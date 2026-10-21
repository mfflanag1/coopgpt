"""Inspect retained Parquet footer structure, never data pages or value statistics.

The explicit projection follows parquet-format 2.9.0 parquet.thrift. This is
a bounded Compact Protocol reader for this audit, not a general Parquet reader.
Unselected fields, including every Statistics struct, are consumed and discarded.
No binary statistic, node dictionary, or measurement value is decoded/emitted.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

PAGE_ENCODING = {1: "int", 2: "int", 3: "int"}
COLUMN_METADATA = {
    1: "int", 2: ("list", "int"), 3: ("list", "text"), 4: "int",
    5: "int", 6: "int", 7: "int", 9: "int", 10: "int", 11: "int",
    13: ("list", PAGE_ENCODING),
}
COLUMN_CHUNK = {3: COLUMN_METADATA, 4: "int", 5: "int", 6: "int", 7: "int"}
ROW_GROUP = {1: ("list", COLUMN_CHUNK), 3: "int"}
FILE_METADATA = {1: "int", 3: "int", 4: ("list", ROW_GROUP), 6: "text"}


class CompactReader:
    def __init__(self, data):
        self.data = memoryview(data)
        self.pos = 0

    def take(self, count):
        if count < 0 or self.pos + count > len(self.data):
            raise ValueError("Truncated or invalid compact field")
        out = self.data[self.pos:self.pos + count]
        self.pos += count
        return out

    def byte(self):
        return self.take(1)[0]

    def unsigned(self):
        value = 0
        for shift in range(0, 70, 7):
            b = self.byte()
            value |= (b & 127) << shift
            if not b & 128:
                if value > (1 << 64) - 1:
                    raise ValueError("Oversized compact integer")
                return value
        raise ValueError("Unterminated compact integer")

    def integer(self):
        value = self.unsigned()
        return (value >> 1) ^ -(value & 1)

    def struct(self, policy=None, depth=0):
        if depth > 50:
            raise ValueError("Excess nesting")
        result = {} if policy is not None else None
        previous = 0
        seen = set()
        while True:
            head = self.byte()
            if head == 0:
                return result
            kind, delta = head & 15, head >> 4
            field = previous + delta if delta else self.integer()
            if field <= 0 or field in seen:
                raise ValueError("Invalid or duplicate field id")
            seen.add(field)
            previous = field
            selected = policy.get(field) if policy is not None else None
            value = self.value(kind, selected, depth + 1)
            if selected is not None:
                result[field] = value

    def value(self, kind, policy, depth, in_collection=False):
        if depth > 50:
            raise ValueError("Excess nesting")
        if policy == "int" and kind not in (3, 4, 5, 6):
            raise ValueError("Expected integer")
        if policy == "text" and kind != 8:
            raise ValueError("Expected binary text")
        if isinstance(policy, dict) and kind != 12:
            raise ValueError("Expected struct")
        if isinstance(policy, tuple) and kind != 9:
            raise ValueError("Expected list")
        if kind in (1, 2):
            if in_collection and self.byte() not in (1, 2):
                raise ValueError("Invalid collection boolean")
            return None
        if kind == 3:
            value = self.byte()
            return value - 256 if value > 127 else value
        if kind in (4, 5, 6):
            value = self.integer()
            return value if policy is not None else None
        if kind == 7:
            self.take(8)
            return None
        if kind == 8:
            body = self.take(self.unsigned())
            return bytes(body).decode("utf-8") if policy == "text" else None
        if kind in (9, 10):
            head = self.byte()
            count, subtype = head >> 4, head & 15
            count = self.unsigned() if count == 15 else count
            if count > 1000000:
                raise ValueError("Excess collection length")
            child = policy[1] if policy is not None else None
            result = [] if policy is not None else None
            for _ in range(count):
                value = self.value(subtype, child, depth + 1, True)
                if result is not None:
                    result.append(value)
            return result
        if kind == 11:
            count = self.unsigned()
            if count > 1000000:
                raise ValueError("Excess map length")
            if count:
                kinds = self.byte()
                for _ in range(count):
                    self.value(kinds >> 4, None, depth + 1, True)
                    self.value(kinds & 15, None, depth + 1, True)
            return None
        if kind == 12:
            return self.struct(policy, depth + 1)
        raise ValueError("Unknown compact type")


def project_footer(data):
    reader = CompactReader(data)
    result = reader.struct(FILE_METADATA)
    if reader.pos != len(data):
        raise ValueError("Trailing footer bytes")
    if not {1, 3, 4, 6} <= result.keys():
        raise ValueError("Missing required audit field")
    return result


def audit(root):
    metadata = json.loads((root / "inputs/june_metadata_report.json").read_text())
    records = []
    for member in metadata["members"]:
        path = root / "inputs" / (member["metric"] + "_footer.bin")
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != member["footer_sha256"]:
            raise ValueError("Footer differs from inherited source hash")
        projected = project_footer(body)
        if len(projected[4]) != len(member["timestamp_ranges"]):
            raise ValueError("Row-group count mismatch")
        original = {(x[0], x[2]): x for x in member["chunks"]}
        if len(original) != len(member["chunks"]):
            raise ValueError("Duplicate inherited chunk keys")
        start = datetime(2020, 6, 1, tzinfo=timezone.utc)
        end = datetime(2020, 6, 15, tzinfo=timezone.utc)
        selected = set()
        for group_id, lo, hi in member["timestamp_ranges"]:
            lo, hi = datetime.fromisoformat(lo), datetime.fromisoformat(hi)
            if lo.tzinfo is None or hi.tzinfo is None or hi < lo:
                raise ValueError("Invalid timestamp extrema")
            if lo < end and hi >= start:
                selected.add(group_id)
        columns = []
        seen = set()
        for group_id, group in enumerate(projected[4]):
            for chunk in group[1]:
                column = chunk[3]
                if len(column[3]) != 1:
                    raise ValueError("Unexpected nested schema")
                name = column[3][0]
                key = (group_id, name)
                if key in seen:
                    raise ValueError("Duplicate projected column key")
                seen.add(key)
                prior = original[(group_id, name)]
                if [group[3], column[7], column[9], column.get(11)] != [prior[1], prior[3], prior[4], prior[5]]:
                    raise ValueError("Structural projection disagrees with inherited DuckDB metadata")
                encodings = column.get(13)
                data_pages = None if encodings is None else sum(e[3] for e in encodings if e[1] in (0, 3))
                if encodings is not None and any(e[3] < 0 for e in encodings):
                    raise ValueError("Negative page count")
                columns.append({
                    "row_group": group_id, "column": name,
                    "candidate_overlap": group_id in selected,
                    "compressed_bytes": column[7], "data_page_count": data_pages,
                    "page_encoding_counts": encodings,
                    "offset_index_present": 4 in chunk or 5 in chunk,
                    "column_index_present": 6 in chunk or 7 in chunk,
                })
        if seen != set(original):
            raise ValueError("Incomplete projected column set")
        counts = Counter(str(c["data_page_count"]) for c in columns)
        records.append({"metric": member["metric"], "created_by": projected[6],
                        "footer_sha256": member["footer_sha256"],
                        "column_chunks": len(columns), "page_count_histogram": dict(counts),
                        "offset_indexes": sum(c["offset_index_present"] for c in columns),
                        "column_indexes": sum(c["column_index_present"] for c in columns),
                        "columns": columns})
    return {"status": "STRUCTURAL FOOTER PROJECTION VERIFIED", "members": records,
            "scope": "Already acquired footer bytes only; outcome statistics skipped, no data pages read. Page counts are writer metadata, not independently observed page headers."}


if __name__ == "__main__":
    print(json.dumps(audit(Path(__file__).resolve().parent), indent=2))
