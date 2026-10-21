#!/usr/bin/env python3
"""Offline structural byte audit; no data reader, network, or package dependency.

Default: validate the five supplied inputs and print the report to stdout.
--check: run arithmetic/reader-plan tests and print a compact summary.
--output FILE: explicitly request a JSON write (input files cannot be targets).

Tests establish arithmetic and reader-plan properties, never a universal
compression or information-theoretic lower bound. This script opens only the
allowlisted text/JSON inputs. It never opens a tar, Parquet, or raw range file.
"""

import argparse
from collections import Counter
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys


START = datetime(2020, 6, 1, tzinfo=timezone.utc)
END = datetime(2020, 6, 15, tzinfo=timezone.utc)
CORE = ("timestamp", "value", "node")
COLUMNS = {
    "state": ("timestamp", "value", "description", "host_group", "nagiosdrained", "node", "state_type"),
    "ps0_input_power": CORE,
    "ps1_input_power": CORE,
}
EXPECTED = {"state": (96, 712903), "ps0_input_power": (442, 51066428), "ps1_input_power": (477, 55846138)}
INPUTS = ("june_metadata_report.json", "june_candidate_summary.json", "BYTE_TOTALS.json", "JUNE_CANDIDATE_GATE.txt", "acquisition_ledger.jsonl")


def require(condition, message):
    # Do not use Python assert for validation: -O must not disable these gates.
    if not condition:
        raise ValueError(message)


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, "invalid integer: " + label)
    return value


def timestamp(value):
    require(isinstance(value, str), "timestamp must be a string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("malformed timestamp") from exc
    require(result.tzinfo is not None and result.utcoffset() == timedelta(0), "timestamp must be UTC-aware")
    return result


def overlaps(lo, hi, start=START, end=END):
    """Closed observed extrema [lo,hi] overlap a half-open target [start,end)."""
    require(start < end and lo <= hi, "reversed or empty timestamp range/window")
    return lo < end and hi >= start


def range_union(ranges, limit=None):
    """Canonical half-open union; exact duplicates/overlap/adjacency cost once."""
    checked = []
    if limit is not None:
        integer(limit, "range limit", 1)
    for pair in ranges:
        require(isinstance(pair, (tuple, list)) and len(pair) == 2, "malformed byte range")
        a, b = pair
        integer(a, "range start")
        integer(b, "range end", 1)
        require(a < b and (limit is None or b <= limit), "empty, reversed, or out-of-bounds byte range")
        checked.append((a, b))
    result = []
    for a, b in sorted(checked):
        if result and a <= result[-1][1]:
            result[-1][1] = max(result[-1][1], b)
        else:
            result.append([a, b])
    return result


def byte_count(ranges):
    return sum(b - a for a, b in range_union(ranges))


def intersection(left, right):
    left, right = range_union(left), range_union(right)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        a, b = left[i]
        c, d = right[j]
        if max(a, c) < min(b, d):
            out.append([max(a, c), min(b, d)])
        if b <= d:
            i += 1
        else:
            j += 1
    return range_union(out)


def difference(left, right):
    """Exact uncached half-open ranges, with no coalesced gaps."""
    right = range_union(right)
    out = []
    for a, b in range_union(left):
        cursor = a
        for c, d in right:
            if d <= cursor:
                continue
            if c >= b:
                break
            if cursor < c:
                out.append([cursor, min(c, b)])
            cursor = max(cursor, d)
            if cursor >= b:
                break
        if cursor < b:
            out.append([cursor, b])
    return range_union(out)


def member_plan(member):
    metric = member["metric"]
    require(metric in COLUMNS, "unexpected metric")
    columns = COLUMNS[metric]
    size = integer(member["size"], "member size", 12)
    offset = integer(member["offset"], "archive offset")
    require([row[0] for row in member["schema"]][1:] == list(columns), "unexpected schema columns")
    require(member["schema"][1][1] == "INT64" and "isAdjustedToUTC=1" in member["schema"][1][3], "unexpected timestamp representation")
    times = {}
    for record in member["timestamp_ranges"]:
        require(isinstance(record, list) and len(record) == 3, "malformed timestamp record")
        group = integer(record[0], "timestamp group")
        lo, hi = timestamp(record[1]), timestamp(record[2])
        require(lo <= hi, "reversed timestamp extrema")
        require(group not in times or times[group] == (lo, hi), "conflicting timestamp duplicates")
        times[group] = (lo, hi)
    require(times and set(times) == set(range(len(times))), "missing/noncontiguous timestamp group")
    selected = {group for group, (lo, hi) in times.items() if overlaps(lo, hi)}
    chunks, group_rows = {}, {}
    for record in member["chunks"]:
        # Supplied safe projection: group id, row count, column path,
        # total_compressed_size, data_page_offset, dictionary_page_offset.
        require(isinstance(record, list) and len(record) == 6, "malformed chunk record")
        group, rows, column, length, data, dictionary = record
        integer(group, "chunk group")
        integer(rows, "structural row count", 1)
        integer(length, "compressed length", 1)
        integer(data, "data-page offset", 4)
        require(group in times and column in columns, "unexpected chunk group or column")
        if dictionary is not None:
            integer(dictionary, "dictionary-page offset", 4)
            require(dictionary < data, "dictionary offset must precede data offset")
        begin = data if dictionary is None else dictionary
        end = begin + length
        range_union([[begin, end]], size - 8)
        require(begin <= data < end, "data offset outside complete chunk")
        key = (group, column)
        value = (rows, begin, end, data, dictionary)
        require(key not in chunks or chunks[key] == value, "conflicting chunk duplicates")
        require(group not in group_rows or group_rows[group] == rows, "inconsistent group row count")
        chunks[key] = value
        group_rows[group] = rows
    require(set(chunks) == {(g, c) for g in times for c in columns}, "missing chunk")
    # Distinct chunks must not claim the same physical bytes. Exact repeated
    # metadata records have already been deduplicated by (group,column).
    all_ranges = sorted((v[1], v[2]) for v in chunks.values())
    require(all(a[1] <= b[0] for a, b in zip(all_ranges, all_ranges[1:])), "overlapping distinct chunks")
    per_column = {}
    for column in columns:
        ranges = range_union([[v[1], v[2]] for (g, c), v in chunks.items() if g in selected and c == column], size)
        full = range_union([[v[1], v[2]] for (_, c), v in chunks.items() if c == column], size)
        per_column[column] = {"selected_chunk_union_bytes": byte_count(ranges), "selected_chunk_union_member_relative": ranges,
                              "all_month_complete_column_bytes": byte_count(full)}
    chosen = range_union([r for col in per_column.values() for r in col["selected_chunk_union_member_relative"]], size)
    all_union = range_union(all_ranges, size)
    return {
        "metric": metric, "member_name": member["name"], "archive_member_start": offset, "member_bytes": size,
        "total_row_groups": len(times), "selected_row_group_ids": sorted(selected), "selected_row_groups": len(selected),
        "selected_groups_with_reported_minimum_inside_candidate": sum(START <= times[g][0] < END for g in selected),
        "selected_groups_with_reported_maximum_at_or_after_candidate_end": sum(times[g][1] >= END for g in selected),
        "selected_group_timestamp_minimum": min(times[g][0] for g in selected).isoformat(),
        "selected_group_timestamp_maximum": max(times[g][1] for g in selected).isoformat(),
        "columns": per_column, "selected_chunk_union_bytes": byte_count(chosen),
        "selected_chunk_union_member_relative": chosen,
        "all_month_chunk_union_bytes": byte_count(all_union), "all_month_chunk_union_member_relative": all_union,
        "unrepresented_member_bytes": size - byte_count(all_union),
    }


def ledger_plan(records, source, totals):
    by_kind, by_count, june_ranges = Counter(), Counter(), []
    for entry in records:
        kind = entry["kind"]
        require(isinstance(kind, str) and (kind == "documentation" or kind.startswith("dataset_")), "unknown ledger class")
        body = integer(entry["body_bytes"], "ledger body bytes")
        by_kind[kind] += body
        by_count[kind] += 1
        if kind.startswith("dataset_") and body:
            start = integer(entry["start"], "ledger range start")
            requested = integer(entry["requested_bytes"], "requested bytes", 1)
            require(entry["status"] == 206 and requested == body, "dataset response not an exact range")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", entry["content_range"])
            require(match is not None, "malformed Content-Range")
            a, last, archive_size = map(int, match.groups())
            require(a == start and last + 1 == start + body and last < archive_size, "inconsistent Content-Range")
            require(int(entry["content_length"]) == body, "inconsistent Content-Length")
            if kind.startswith("dataset_june_"):
                require(archive_size == source["size"] and "20-06.tar" in entry["url"], "wrong June archive")
                june_ranges.append([start, start + body])
    dataset = sum(v for k, v in by_kind.items() if k.startswith("dataset_"))
    require(dataset == totals["new_dataset_bytes"], "ledger dataset total mismatch")
    require(by_kind["documentation"] == totals["new_documentation_bytes"], "ledger documentation total mismatch")
    require(totals["inherited_dataset_bytes"] + dataset == totals["cumulative_dataset_bytes"], "cumulative total mismatch")
    require(totals["cap_bytes"] - totals["cumulative_dataset_bytes"] == totals["remaining_bytes"], "remaining allowance mismatch")
    return {"body_bytes_by_kind": dict(sorted(by_kind.items())), "entries_by_kind": dict(sorted(by_count.items())),
            "june_cached_absolute_union": range_union(june_ranges, source["size"]),
            "june_cached_union_bytes": byte_count(june_ranges), "june_body_bytes": sum(v for k, v in by_kind.items() if k.startswith("dataset_june_")),
            "dataset_body_bytes": dataset, "documentation_body_bytes": by_kind["documentation"], "entries": len(records)}


def build_report(base):
    paths = {name: base / "inputs" / name for name in INPUTS}
    raw = {name: path.read_bytes() for name, path in paths.items()}
    metadata = json.loads(raw["june_metadata_report.json"])
    summary = json.loads(raw["june_candidate_summary.json"])
    totals = json.loads(raw["BYTE_TOTALS.json"])
    ledger = [json.loads(line) for line in raw["acquisition_ledger.jsonl"].splitlines() if line.strip()]
    require(metadata["status"] == "METADATA_ONLY" and metadata["data_pages_read"] == 0 and
            metadata["outcome_statistics_selected"] is False and metadata["node_keys_decoded"] is False, "unexpected metadata boundary")
    require(hashlib.sha256(raw["june_metadata_report.json"]).hexdigest() == summary["source_metadata_sha256"], "metadata provenance hash mismatch")
    require(metadata["source"] == summary["source"], "source identity mismatch")
    require(summary["metadata_only"] is True and summary["outcomes_read"] is False and summary["candidate_selected_as_holdout"] is False, "unexpected candidate status")
    require(summary["candidate"] == "2020-06-01T00:00:00Z through 2020-06-15T00:00:00Z exclusive", "candidate changed")
    require(metadata["cumulative_dataset_bytes"] == totals["cumulative_dataset_bytes"] == 93606385, "inherited spend mismatch")
    require(totals["cap_bytes"] == 100000000 and totals["remaining_bytes"] == summary["remaining_dataset_bytes"] == 6393615, "inherited budget mismatch")
    for value in totals.values():
        if not isinstance(value, str):
            integer(value, "byte total")
    require(len(metadata["members"]) == len(COLUMNS) and {m["metric"] for m in metadata["members"]} == set(COLUMNS), "member set mismatch")
    members = [member_plan(m) for m in metadata["members"]]
    summary_members = {m["metric"]: m for m in summary["members"]}
    require(set(summary_members) == set(COLUMNS), "summary member set mismatch")
    accounting = ledger_plan(ledger, metadata["source"], totals)
    cache = accounting["june_cached_absolute_union"]
    all_selected, all_members = [], []
    for member in members:
        metric, offset, size = member["metric"], member["archive_member_start"], member["member_bytes"]
        expected_count, expected_bytes = EXPECTED[metric]
        s = summary_members[metric]
        require(member["selected_row_groups"] == s["candidate_row_groups"] == expected_count and
                member["selected_chunk_union_bytes"] == s["candidate_chunk_range_bytes"] == expected_bytes, "inherited member arithmetic mismatch")
        require(size == s["member_bytes"] and member["total_row_groups"] == s["row_groups"], "summary member structure mismatch")
        require(offset + size <= metadata["source"]["size"], "member beyond archive")
        absolute = [[offset + a, offset + b] for a, b in member["selected_chunk_union_member_relative"]]
        cached = intersection([[offset, offset + size]], cache)
        member["cached_member_union_member_relative"] = [[a - offset, b - offset] for a, b in cached]
        member["cached_member_bytes"] = byte_count(cached)
        member["selected_chunk_bytes_already_cached"] = byte_count(intersection(absolute, cache))
        member["selected_chunk_uncached_bytes"] = byte_count(difference(absolute, cache))
        member["whole_member_uncached_bytes"] = size - byte_count(cached)
        # No alleged data chunk may overlap known marker/footer bytes.
        all_absolute = [[offset + a, offset + b] for a, b in member["all_month_chunk_union_member_relative"]]
        require(byte_count(intersection(all_absolute, cache)) == 0, "chunk overlaps known metadata/marker bytes")
        all_selected.extend(absolute)
        all_members.append([offset, offset + size])
    require(byte_count(all_members) == sum(m["member_bytes"] for m in members), "overlapping members")
    total = byte_count(all_selected)
    require(total == summary["planned_full_column_row_group_bytes"] == 107625469, "inherited aggregate mismatch")
    remain = totals["remaining_bytes"]
    column_totals = {c: sum(m["columns"].get(c, {}).get("selected_chunk_union_bytes", 0) for m in members) for c in sorted(set(c for cs in COLUMNS.values() for c in cs))}
    optional = sum(v for c, v in column_totals.items() if c not in CORE)
    return {
        "audit_kind": "offline arithmetic and reader-plan validation; not a universal compression lower bound",
        "source": metadata["source"], "input_sha256": {name: hashlib.sha256(content).hexdigest() for name, content in sorted(raw.items())},
        "candidate": {"start_inclusive": START.isoformat(), "end_exclusive": END.isoformat(), "days": 14, "fixed_nodes": 980, "selected_as_holdout": False},
        "safe_inputs_only": True, "new_dataset_bytes_read_by_replay": 0, "outcome_values_or_statistics_read_by_replay": False,
        "range_convention": "[start,end) bytes; member-relative endpoints become absolute by adding archive_member_start; HTTP inclusive end is end-1",
        "reader_class": "Complete compressed column chunks for every group whose reported closed timestamp envelope overlaps the fixed half-open candidate; exact disjoint range reads with no gaps or retries",
        "budget": totals, "ledger": accounting, "members": members, "selected_column_totals": column_totals,
        "plans": {
            "complete_chunks_all_selected_columns": {"bytes": total, "uncached_bytes": byte_count(difference(all_selected, cache)), "exceeds_remaining_by": total - remain, "verdict": "fails current cap within declared reader class"},
            "timestamp_first_complete_selected_chunks": {"first_stage_bytes": column_totals["timestamp"], "first_stage_exceeds_remaining_by": column_totals["timestamp"] - remain,
                "verdict": "first stage alone fails cap; cannot assume later savings", "all_selected_group_minima_inside_candidate": all(m["selected_groups_with_reported_minimum_inside_candidate"] == m["selected_row_groups"] for m in members),
                "pruning_scope": "Reported minima are in candidate for every selected group: trusting those extrema, decoding timestamps cannot eliminate a whole selected group. Page-level alternatives remain separate."},
            "drop_all_extra_state_columns": {"dropped_columns": [c for c in COLUMNS["state"] if c not in CORE], "saved_bytes": optional, "remaining_plan_bytes": total - optional,
                "exceeds_remaining_by": total - optional - remain, "verdict": "fails cap even before deciding whether semantics permit omission"},
            "value_columns_only_diagnostic": {"bytes": column_totals["value"], "verdict": "fails cap; not a usable linked panel without timestamp/node"},
            "whole_month_all_complete_columns": {"bytes": sum(m["all_month_chunk_union_bytes"] for m in members), "verdict": "fails cap; includes all month groups"},
            "whole_members_single_reads": {"bytes": sum(m["member_bytes"] for m in members), "verdict": "fails cap; charges cached metadata again if reread"},
            "whole_members_assembled_with_cache": {"new_bytes": byte_count(difference(all_members, cache)), "verdict": "fails cap even crediting all cached member bytes"},
            "indexed_or_scanned_page_reader": {"bytes": None, "verdict": "unidentified from supplied projection; no feasibility or impossibility established",
                "missing": ["page offsets, compressed sizes, index existence and integrity", "timestamp-to-row/page mapping and cross-column alignment", "dictionary/decode dependencies", "bounded metadata-discovery and request overhead", "exact outcome/date exposure plan"]},
        },
        "limits": ["Only structural counts, offsets, lengths, schemas and timestamp extrema used; no power/state/node value distributions or distinct counts.",
                   "Active-node cardinality and common-node support are not readable here; fixed design count 980 is not observed cardinality.",
                   "Lower costs are necessary union bytes for this complete-chunk reader class, conditional on the supplied metadata; they are not sufficiency guarantees or universal extraction bounds.",
                   "No cost saving is credited for favorable values, node selection, alternate dates, a shorter window, new encodings, remote filtering, or a higher cap.",
                   "Already counted metadata need not be counted twice if reused; new footer checks, page indexes, gaps, retries and repeated bodies count when read. HTTP/TLS headers are excluded under inherited accounting.",
                   "These overlapping groups extend through June 30. If values are later authorized, exposure must be declared for all decoded dates before reading them.",
                   "June is only a fixed metadata-inspected candidate. This arithmetic does not qualify training/holdout completeness, operational state, validity or reliability."],
    }, metadata


def self_test(report, metadata):
    """Meaningful arithmetic tests, including adversarial malformed metadata."""
    checked = []
    def check(condition, label):
        require(condition, "test failed: " + label)
        checked.append(label)
    def rejects(call, label):
        try:
            call()
        except (ValueError, TypeError, KeyError, IndexError):
            checked.append(label)
        else:
            raise ValueError("test failed to reject: " + label)
    check(report["plans"]["complete_chunks_all_selected_columns"]["bytes"] == 107625469, "inherited exact aggregate")
    check(report["budget"]["remaining_bytes"] == 6393615, "inherited exact remainder")
    check(range_union([[10, 20], [0, 5], [5, 10], [3, 7], [10, 20]]) == [[0, 20]], "overlap adjacency duplication union")
    check(difference([[0, 10]], [[2, 4], [6, 20]]) == [[0, 2], [4, 6]], "cached range subtraction")
    check(intersection([[0, 10]], [[2, 4], [6, 20]]) == [[2, 4], [6, 10]], "cached range intersection")
    tick = timedelta(milliseconds=1)
    check(overlaps(START, START), "inclusive window start")
    check(not overlaps(START - tick, START - tick), "strictly before window")
    check(overlaps(START - tick, START), "closed maximum at start")
    check(not overlaps(END, END + tick), "exclusive window end")
    check(overlaps(END - tick, END), "last millisecond and upper overlap")
    check(overlaps(START - tick, END + tick), "envelope straddles whole window")
    for bad in ([[1, 1]], [[2, 1]], [[-1, 2]], [[True, 2]], [[1.0, 2]], [[0, 11]], [[0]], [[0, None]]):
        rejects(lambda b=bad: range_union(b, 10), "malformed byte range rejected: " + repr(bad))
    rejects(lambda: timestamp("2020-06-01"), "naive timestamp rejected")
    rejects(lambda: overlaps(END, START), "reversed extrema rejected")
    for original in metadata["members"]:
        altered = copy.deepcopy(original)
        altered["chunks"] = list(reversed(altered["chunks"])) + altered["chunks"][:3]
        altered["timestamp_ranges"] = list(reversed(altered["timestamp_ranges"])) + altered["timestamp_ranges"][:2]
        check(member_plan(altered) == member_plan(original), original["metric"] + " ordering and exact duplication invariance")
        bad = copy.deepcopy(original)
        bad["chunks"][0][3] = -1
        rejects(lambda b=bad: member_plan(b), original["metric"] + " negative chunk size rejected")
        bad = copy.deepcopy(original)
        bad["chunks"][0][4] = bad["size"]
        rejects(lambda b=bad: member_plan(b), original["metric"] + " out-of-member chunk rejected")
        bad = copy.deepcopy(original)
        bad["chunks"].append(list(bad["chunks"][0]))
        bad["chunks"][-1][3] += 1
        rejects(lambda b=bad: member_plan(b), original["metric"] + " conflicting duplicate rejected")
        bad = copy.deepcopy(original)
        bad["timestamp_ranges"].pop()
        rejects(lambda b=bad: member_plan(b), original["metric"] + " missing timestamp group rejected")
    return {"passed": len(checked), "scope": "arithmetic and reader-plan validation only", "checks": checked}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="test and print summary without writing files")
    parser.add_argument("--output", type=Path, help="explicitly write a JSON report to this file")
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    report, metadata = build_report(base)
    report["validation"] = self_test(report, metadata)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        target = args.output.resolve()
        forbidden = {p.resolve() for p in (base / "inputs").iterdir()} | {Path(__file__).resolve(), (base / "CONTRACT.txt").resolve()}
        require(target not in forbidden and not target.is_dir(), "refusing to overwrite an input or replay")
        target.write_text(rendered, encoding="utf-8")
    if args.check:
        print(json.dumps({"validation": report["validation"], "plans": report["plans"], "selected_column_totals": report["selected_column_totals"]}, indent=2, sort_keys=True))
    elif args.output is None:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        print("AUDIT FAILED CLOSED: " + str(error), file=sys.stderr)
        sys.exit(1)
