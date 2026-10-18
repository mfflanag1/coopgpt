#!/usr/bin/env python3
"""Offline date/range feasibility from safe footer metadata; zero value reads."""
from pathlib import Path
import datetime as dt
import json

ROOT = Path(__file__).resolve().parent


def stamp(s):
    return dt.datetime.fromisoformat(s)


def main():
    data = json.loads((ROOT / "m100_may_footers/report.json").read_text())
    earliest = max(min(stamp(r[1]) for r in m["timestamp_ranges"]) for m in data["members"])
    latest = min(max(stamp(r[2]) for r in m["timestamp_ranges"]) for m in data["members"])
    start = earliest.replace(hour=0, minute=0, second=0, microsecond=0)
    if start < earliest:
        start += dt.timedelta(days=1)
    stop = start + dt.timedelta(days=1)
    summaries = []
    required = []
    for m in data["members"]:
        overlap = {r[0] for r in m["timestamp_ranges"] if stamp(r[1]) < stop and stamp(r[2]) >= start}
        wholly = {r[0] for r in m["timestamp_ranges"] if start <= stamp(r[1]) and stamp(r[2]) < stop}
        chunks = [r for r in m["chunks"] if r[0] in overlap]
        # All columns are required for state interpretation, not value alone.
        ranges = []
        for r in chunks:
            offsets = [v for v in (r[5], r[6]) if v is not None and v > 0]
            begin = min(offsets)
            ranges.append((begin, begin + r[4]))
        ranges.sort()
        merged = []
        for begin, end in ranges:
            if merged and begin <= merged[-1][1]:
                merged[-1][1] = max(end, merged[-1][1])
            else:
                merged.append([begin, end])
        byte_total = sum(end - begin for begin, end in merged)
        coalesced = []
        for begin, end in merged:
            if coalesced and begin - coalesced[-1][1] <= 16384:
                coalesced[-1][1] = end
            else:
                coalesced.append([begin, end])
        row = {"metric": m["metric"], "candidate_row_group_ids": sorted(overlap),
               "candidate_row_groups": len(overlap), "wholly_within_day_ids": sorted(wholly),
               "rows_in_candidate_groups": sum(next(r[1] for r in m["chunks"] if r[0] == g) for g in overlap),
               "candidate_chunk_bytes": sum(r[4] for r in chunks),
               "merged_range_bytes": byte_total, "merged_ranges_member_relative_half_open": merged,
               "coalescing_max_gap_bytes": 16384,
               "coalesced_request_count": len(coalesced),
               "coalesced_range_bytes": sum(end-begin for begin,end in coalesced),
               "coalesced_ranges_member_relative_half_open": coalesced,
               "candidate_groups_extend_outside_day": bool(overlap - wholly),
               "largest_timestamp_in_candidate_groups": max(r[2] for r in m["timestamp_ranges"] if r[0] in overlap)}
        summaries.append(row)
        required.append(byte_total)
    projected = data["cumulative_dataset_bytes"] + sum(required)
    report = {"selection_rule": "Earliest full UTC day after the maximum of the three global timestamp minima; no power/state outcomes inspected",
              "candidate_day_start": start.isoformat(), "candidate_day_end_exclusive": stop.isoformat(),
              "common_metadata_envelope_start": earliest.isoformat(), "common_metadata_envelope_end": latest.isoformat(),
              "common_envelope_days": (latest-earliest).total_seconds()/86400,
              "already_downloaded_dataset_bytes": data["cumulative_dataset_bytes"],
              "additional_selected_chunk_bytes": sum(required),
              "projected_cumulative_dataset_bytes": projected,
              "coalesced_projected_cumulative_dataset_bytes": data["cumulative_dataset_bytes"] + sum(m["coalesced_range_bytes"] for m in summaries),
              "coalesced_request_count": sum(m["coalesced_request_count"] for m in summaries),
              "within_100MB_by_metadata": projected <= 100_000_000,
              "members": summaries,
              "verdict": "BYTE-FEASIBLE CANDIDATE ONLY; exact node/time alignment, gaps, state meanings and holdout-safe filtering remain unverified",
              "limitations": ["Timestamp extrema do not certify any particular interior timestamp or common node.",
                              "Different PSU row-group IDs are not matched observations.",
                              "Candidate groups may include later dates; no payload is fetched here and no new holdout is frozen.",
                              "A power/state panel is not established until actual observed key intersection and state semantics pass."]}
    (ROOT / "m100_training_day_plan.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k != "members"}, indent=2))
    for row in summaries:
        print(json.dumps({k:v for k,v in row.items() if k not in ("candidate_row_group_ids", "wholly_within_day_ids", "merged_ranges_member_relative_half_open", "coalesced_ranges_member_relative_half_open")}, indent=2))


if __name__ == "__main__":
    main()
