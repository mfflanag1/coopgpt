#!/usr/bin/env python3
"""Independent, read-only arrival qualification auditor. No driver imports/timing.

Usage: python3 audit_arrivals.py RUN --freeze DRAFT_FREEZE_REPAIRED.json
       --authorization AUTHORIZATION.json --output ARRIVAL_AUDIT.json
       python3 audit_arrivals.py --self-test

Exit 0 means the evidence audit passes, not that a scheduler qualifies. A clean
experiment can fail every timing gate. Missing or malformed evidence fails the
audit; its requests remain in the fixed 2,400-request accounting denominator.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
MODES = ("thread", "process")
LOADS = ("idle", "python_cpu")
TIMES = ("wake_ns", "emitted_ns", "admitted_ns", "received_ns")
METRICS = dict(zip(("wake_jitter", "emission_jitter", "admission_jitter",
                    "receipt_delay"), TIMES))
FROZEN_FILES = {"arrival_qualification.py", "PROTOCOL.txt", "DIAGNOSIS.txt",
                "test_arrival_qualification.py"}


def integer(value):
    return type(value) is int


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("Nonfinite JSON number: " + value)


def decode(text):
    return json.loads(text, object_pairs_hook=strict_pairs,
                      parse_constant=reject_constant)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Evidence:
    def __init__(self):
        self.errors = []
        self.checks = 0

    def require(self, condition, context):
        self.checks += 1
        if not condition:
            self.errors.append(context)
        return bool(condition)

    def equal(self, actual, expected, context):
        # Exact JSON semantics, also distinguishing bool from integer.
        return self.require(type(actual) is type(expected) and actual == expected,
                            context + " differs")

    def read(self, path):
        try:
            return decode(path.read_text())
        except (OSError, ValueError, UnicodeError) as exc:
            self.require(False, str(path) + ": " + str(exc))
            return None


def distribution(values):
    """None is +infinity; it participates in both the rank and denominator."""
    if not values:
        return {"p99_ns": None, "maximum_ns": None}
    ordered = sorted(values, key=lambda x: (x is None, 0 if x is None else x))
    rank = (99 * len(values) + 99) // 100
    return {"p99_ns": ordered[rank - 1], "maximum_ns": ordered[-1]}


def statistics(rows):
    result = {"planned": len(rows)}
    for label, field in METRICS.items():
        deltas = [r[field] - r["planned_ns"]
                  if integer(r.get(field)) and integer(r.get("planned_ns"))
                  else None for r in rows]
        result[label] = distribution(deltas)
    result["admitted"] = sum(integer(r.get("admitted_ns")) for r in rows)
    result["received"] = sum(integer(r.get("received_ns")) for r in rows)
    admission = result["admission_jitter"]
    result["qualification_pass"] = (
        bool(rows) and result["admitted"] == len(rows)
        and result["received"] == len(rows)
        and admission["p99_ns"] is not None
        and admission["p99_ns"] <= 2_000_000
        and admission["maximum_ns"] <= 10_000_000)
    return result


def cpu_checksum(iterations):
    """Exponentiate the reported affine recurrence; do not run a CPU load."""
    modulus = 1 << 32
    mul, add = 1664525, 1013904223
    accum_mul, accum_add = 1, 0
    count = iterations
    while count:
        if count & 1:
            accum_mul = mul * accum_mul % modulus
            accum_add = (mul * accum_add + add) % modulus
        mul, add = mul * mul % modulus, (mul + 1) * add % modulus
        count //= 2
    return (accum_mul + accum_add) % modulus


def validate_freeze(freeze, source, ev):
    ev.require(isinstance(freeze, dict), "Freeze must be an object")
    if not isinstance(freeze, dict):
        return []
    plan = freeze.get("plan", {})
    ev.require(isinstance(plan, dict), "Freeze plan must be an object")
    if not isinstance(plan, dict):
        return []
    for key, value in {"schema": 1, "stage": "arrival-driver-qualification",
                       "lead_ns": 50_000_000, "p99_limit_ns": 2_000_000,
                       "maximum_limit_ns": 10_000_000, "phase_seconds": 80,
                       "startup_seconds": 2, "case_drain_seconds": 1}.items():
        ev.equal(plan.get(key), value, "Frozen " + key)
    cases = plan.get("cases", [])
    ev.require(isinstance(cases, list) and len(cases) == 48,
               "Freeze must have exactly 48 ordered cases")
    if not isinstance(cases, list):
        return []
    seen, groups, shared = set(), Counter(), {}
    horizons = 0
    for case in cases:
        if not ev.require(isinstance(case, dict), "Frozen case must be an object"):
            continue
        mode, load = case.get("mode"), case.get("load")
        rep, rate = case.get("rep"), case.get("rate")
        cid = case.get("case_id")
        valid = (mode in MODES and load in LOADS and integer(rep)
                 and rep in range(3) and integer(rate) and rate in (20, 50, 100, 200))
        ev.require(valid, "Invalid frozen case treatment: " + str(cid))
        if not valid:
            continue
        ev.equal(cid, f"r{rep}-rate{rate}-{load}-{mode}", "Frozen case ID")
        ev.require(cid not in seen, "Duplicate frozen case: " + str(cid))
        seen.add(cid)
        groups[mode, load] += 1
        ev.equal(case.get("seed"), 2410242000 + 10 * rep
                 + (20, 50, 100, 200).index(rate), str(cid) + " seed")
        requests = case.get("requests", [])
        ev.require(isinstance(requests, list) and len(requests) == 50,
                   str(cid) + " must contain 50 planned requests")
        if not isinstance(requests, list):
            continue
        offsets = []
        for rid, row in enumerate(requests):
            if not ev.require(isinstance(row, dict), str(cid) + " request object"):
                continue
            ev.equal(row.get("request_id"), rid, str(cid) + " planned ID/order")
            off = row.get("offset_ns")
            ev.require(integer(off) and off > 0, str(cid) + " positive integer offset")
            if integer(off):
                ev.require(not offsets or off > offsets[-1], str(cid) + " positive gaps")
                offsets.append(off)
        if len(offsets) == 50:
            horizons += offsets[-1] + 50_000_000
        key = rep, rate
        if key in shared:
            ev.equal(requests, shared[key], str(cid) + " common intended offsets")
        else:
            shared[key] = requests
    ev.equal(len(seen), 48, "Unique frozen case count")
    ev.equal(dict(groups), {(m, l): 12 for m in MODES for l in LOADS}, "Frozen groups")
    ev.equal(plan.get("planned_offer_horizons_plus_leads_ns"), horizons,
             "Frozen sum of horizons plus leads")
    ev.require(horizons < 70_000_000_000, "Frozen horizons must remain below 70 seconds")
    hashes = freeze.get("sha256", {})
    ev.require(isinstance(hashes, dict) and set(hashes) == FROZEN_FILES,
               "Freeze must hash all four source/protocol/test files")
    if isinstance(hashes, dict):
        for name in FROZEN_FILES:
            try:
                ev.equal(sha(source / name), hashes.get(name), "Frozen source hash: " + name)
            except OSError as exc:
                ev.require(False, "Frozen source unavailable: " + str(exc))
    return cases


def read_raw(path, ev):
    events = []
    try:
        lines = path.read_text().splitlines()
    except OSError as exc:
        ev.require(False, "RAW missing: " + str(exc))
        return events
    for number, line in enumerate(lines, 1):
        try:
            if not line.strip():
                raise ValueError("blank record")
            events.append(decode(line))
        except ValueError as exc:
            ev.require(False, f"{path}:{number}: {exc}")
    return events


def index_rows(rows, expected_ids, ev, label, complete):
    indexed, order = {}, []
    if not ev.require(isinstance(rows, list), label + " must be an array"):
        return indexed
    for row in rows:
        if not ev.require(isinstance(row, dict), label + " row must be object"):
            continue
        rid = row.get("request_id")
        if not ev.require(integer(rid) and rid in expected_ids, label + " unknown/noninteger ID"):
            continue
        ev.require(rid not in indexed, label + " duplicate ID " + str(rid))
        order.append(rid)
        if rid not in indexed:
            indexed[rid] = row
    target = expected_ids if complete else expected_ids[:len(order)]
    ev.equal(order, target, label + " ID denominator/order")
    return indexed


def check_case(spec, case_plan, events, result, epoch, ev):
    cid = spec["case_id"]
    initial_errors = len(ev.errors)
    expected_ids = list(range(50))
    rows = [dict(r, planned_ns=None, wake_ns=None, emitted_ns=None,
                 admitted_ns=None, received_ns=None) for r in spec["requests"]]
    start = None
    ready = None
    if ev.require(isinstance(case_plan, dict), cid + " missing case PLAN"):
        ev.equal(case_plan.get("spec"), spec, cid + " case PLAN frozen spec")
        start = case_plan.get("case_start_monotonic_ns")
        if ev.require(integer(start), cid + " absolute case start must be integer"):
            for row in rows:
                row["planned_ns"] = start + row["offset_ns"]
            if integer(epoch.get("phase_start_monotonic_ns")):
                ev.require(start >= epoch["phase_start_monotonic_ns"] + 50_000_000,
                           cid + " case start precedes phase lead")
        ready = case_plan.get("ready")
        planned = index_rows(case_plan.get("requests"), expected_ids, ev,
                             cid + " case PLAN", True)
        for row in rows:
            supplied = planned.get(row["request_id"], {})
            for field in ("request_id", "offset_ns", "planned_ns"):
                ev.equal(supplied.get(field), row[field], cid + " frozen absolute " + field)

    if ev.require(isinstance(ready, dict), cid + " missing ready record"):
        ev.equal(ready.get("kind"), "ready", cid + " ready kind")
        pid = ready.get("pid")
        ev.require(integer(pid) and pid > 0, cid + " positive producer PID")
        consumer = epoch.get("consumer_pid")
        ev.require((pid == consumer) if spec["mode"] == "thread" else (pid != consumer),
                   cid + " thread/process producer PID semantics")
        ev.equal(ready.get("switch_interval_seconds"), epoch.get("switch_interval_seconds"),
                 cid + " producer/consumer switch interval")

    offers, finals, receive_times = [], [], []
    final_seen = False
    for event in events:
        if not ev.require(isinstance(event, dict), cid + " RAW event object"):
            continue
        receipt = event.get("received_ns")
        ev.require(integer(receipt), cid + " RAW receipt integer")
        if integer(receipt):
            ev.require(not receive_times or receipt >= receive_times[-1], cid + " RAW receive order")
            receive_times.append(receipt)
        message = event.get("message")
        if not ev.require(isinstance(message, dict), cid + " RAW message object"):
            continue
        kind = message.get("kind")
        ev.require(not final_seen, cid + " RAW record after final producer record")
        if kind == "offer":
            ev.require("received_ns" not in message, cid + " offer must not spoof consumer receipt")
            offers.append(dict(message, received_ns=receipt))
        elif kind == "done":
            finals.append((message, receipt))
            final_seen = True
        else:
            ev.require(False, cid + " unknown RAW message kind")
    offer_index = index_rows(offers, expected_ids, ev, cid + " received offers", False)
    ev.equal(len(offers), 50, cid + " received-offer denominator")
    ev.equal(len(finals), 1, cid + " final producer record count")
    final_index, done_receipt = {}, None
    if len(finals) == 1:
        final, done_receipt = finals[0]
        ev.equal(final.get("failure"), None, cid + " final producer failure")
        final_index = index_rows(final.get("rows"), expected_ids, ev,
                                 cid + " final producer rows", True)

    previous_admission = None
    early_receipts = 0
    for row in rows:
        rid = row["request_id"]
        offer, producer = offer_index.get(rid), final_index.get(rid)
        if producer is not None:
            for field in ("request_id", "offset_ns", "planned_ns"):
                ev.equal(producer.get(field), row[field], cid + f" final[{rid}] " + field)
            for field in TIMES[:-1]:
                row[field] = producer.get(field)
        if offer is not None:
            ev.equal(offer.get("planned_ns"), row["planned_ns"], cid + f" offer[{rid}] planned time")
            row["received_ns"] = offer.get("received_ns")
            for field in ("wake_ns", "emitted_ns"):
                if producer is not None:
                    ev.equal(producer.get(field), offer.get(field), cid + f" raw/final[{rid}] " + field)
                else:
                    row[field] = offer.get(field)
        ev.require(all(integer(row[field]) for field in TIMES), cid + f" request[{rid}] missing timestamp")
        if all(integer(row.get(field)) for field in ("planned_ns",) + TIMES):
            planned, wake, emitted, admitted, received = (row[f] for f in ("planned_ns",) + TIMES)
            ev.require(planned <= wake <= emitted <= admitted, cid + f" request[{rid}] producer time order/early offer")
            ev.require(received >= emitted, cid + f" request[{rid}] receipt before emission")
            # received < admitted is legal: reading may finish before sender records return.
            early_receipts += int(received < admitted)
            if previous_admission is not None:
                ev.require(wake >= previous_admission, cid + f" request[{rid}] sequential producer order")
            previous_admission = admitted
            if integer(done_receipt):
                ev.require(admitted <= done_receipt and received <= done_receipt,
                           cid + f" request[{rid}] timestamps after final receipt")
        for label, field in METRICS.items():
            row[label + "_ns"] = (row[field] - row["planned_ns"]
                                        if integer(row[field]) and integer(row["planned_ns"]) else None)
        row["status"] = "complete" if all(integer(row[f]) for f in TIMES) else "incomplete"

    computed = statistics(rows)
    load = None
    if ev.require(isinstance(result, dict), cid + " missing RESULT"):
        ev.equal(result.get("case_id"), cid, cid + " RESULT ID")
        ev.equal(result.get("spec"), spec, cid + " RESULT frozen spec")
        ev.equal(result.get("failure"), None, cid + " operational failure")
        ev.equal(result.get("producer_ready"), ready, cid + " RESULT ready record")
        ev.equal(result.get("raw_offers_received"), len(offers), cid + " raw received count")
        declared = index_rows(result.get("requests"), expected_ids, ev,
                              cid + " RESULT rows", True)
        for row in rows:
            supplied = declared.get(row["request_id"], {})
            for field in ("request_id", "offset_ns", "planned_ns", "status") + TIMES:
                ev.equal(supplied.get(field), row[field], cid + f" RESULT[{row['request_id']}] " + field)
        ev.equal(result.get("summary"), computed, cid + " independently recomputed statistics")
        load = result.get("consumer_load")
        if ev.require(isinstance(load, dict), cid + " missing consumer load record"):
            iterations = load.get("iterations")
            if spec["load"] == "idle":
                ev.equal(iterations, 0, cid + " idle load iterations")
            else:
                valid = integer(iterations) and iterations > 0 and iterations % 2048 == 0
                ev.require(valid, cid + " CPU work must be positive whole 2048-update batches")
                if valid:
                    ev.equal(load.get("checksum"), cpu_checksum(iterations), cid + " CPU recurrence checksum")
    intact = len(ev.errors) == initial_errors
    return {"case_id": cid, "mode": spec["mode"], "load": spec["load"],
            "rate": spec["rate"], "rep": spec["rep"], "evidence_intact": intact,
            "case_start_monotonic_ns": start, "final_receipt_ns": done_receipt,
            "producer_ready": ready, "consumer_load": load,
            "received_before_admitted_count": early_receipts,
            "statistics": computed, "qualification_pass": intact and computed["qualification_pass"],
            "requests": rows}


def audit_run(run, freeze_path, authorization_path, source):
    ev = Evidence()
    freeze = ev.read(freeze_path)
    specs = validate_freeze(freeze, source, ev)
    authorization = ev.read(authorization_path) if authorization_path else None
    if ev.require(isinstance(authorization, dict), "Reviewed authorization file is required"):
        ev.equal(authorization.get("authorized"), True, "Explicit collection authorization")
        ev.equal(authorization.get("plan"), freeze.get("plan"), "Authorized frozen plan")
        ev.equal(authorization.get("sha256"), freeze.get("sha256"), "Authorized source hashes")
        ev.require(isinstance(authorization.get("host_conditions"), str)
                   and bool(authorization["host_conditions"].strip()), "Declared host conditions")
    plan, epoch, summary = (ev.read(run / name) for name in ("PLAN.json", "EPOCH.json", "SUMMARY.json"))
    ev.equal(plan, freeze.get("plan") if isinstance(freeze, dict) else None, "Run PLAN versus freeze")
    if not isinstance(epoch, dict):
        ev.require(False, "EPOCH object required")
        epoch = {}
    if not isinstance(summary, dict):
        ev.require(False, "SUMMARY object required (hard-killed/incomplete is failure)")
        summary = {}
    for name in ("phase_start_monotonic_ns", "wall_epoch_ns", "consumer_pid"):
        ev.require(integer(epoch.get(name)) and epoch[name] > 0, "EPOCH positive integer " + name)
    for name in ("utc", "platform", "python", "host_conditions"):
        ev.require(isinstance(epoch.get(name), str) and bool(epoch[name].strip()), "EPOCH " + name)
    try:
        ev.require(datetime.fromisoformat(epoch.get("utc", "")).utcoffset().total_seconds() == 0,
                   "EPOCH UTC must be timezone-aware UTC")
    except (ValueError, TypeError, AttributeError):
        ev.require(False, "EPOCH UTC parsing")
    if isinstance(authorization, dict):
        ev.equal(epoch.get("host_conditions"), authorization.get("host_conditions"), "EPOCH authorized conditions")
    switches = [k for k in ("switch_interval_changed", "runner_adjusted_switch_interval") if k in epoch]
    ev.require(bool(switches), "EPOCH switch-interval provenance flag missing")
    for key in switches:
        ev.equal(epoch[key], False, "EPOCH " + key)
    switch = epoch.get("switch_interval_seconds")
    ev.require(type(switch) in (int, float) and switch > 0, "Positive consumer switch interval")
    beginning, end = epoch.get("phase_start_monotonic_ns"), summary.get("phase_end_monotonic_ns")
    elapsed = end - beginning if integer(end) and integer(beginning) else None
    ev.require(integer(elapsed) and 0 <= elapsed <= 81_500_000_000,
               "Phase elapsed must be nonnegative and within 80s plus bounded 1.5s cleanup")
    ev.equal(summary.get("aborted"), None, "Phase operational abort")

    cases, observed, previous_end, missing = [], [], None, []
    for spec in specs:
        cid = spec["case_id"]
        directory = run / cid
        if directory.is_dir():
            observed.append(cid)
        if not (directory / "RESULT.json").is_file():
            missing.append(cid)
        cp, result = ev.read(directory / "PLAN.json"), ev.read(directory / "RESULT.json")
        events = read_raw(directory / "RAW.jsonl", ev)
        audited = check_case(spec, cp, events, result, epoch, ev)
        start, finish = audited["case_start_monotonic_ns"], audited["final_receipt_ns"]
        if integer(start) and integer(previous_end):
            ev.require(start >= previous_end + 50_000_000, cid + " frozen case execution order/lead")
        if integer(finish):
            previous_end = finish
            if integer(end):
                ev.require(finish <= end, cid + " final receipt after phase end")
            if integer(beginning):
                ev.require(finish <= beginning + 80_000_000_000,
                           cid + " case execution exceeds shared 80s deadline")
            last = audited["requests"][-1]["planned_ns"]
            if integer(last):
                ev.require(finish <= last + 1_000_000_000, cid + " exceeds 1s case drain")
        cases.append(audited)
    ev.equal(observed, [s["case_id"] for s in specs], "All 48 case directories")
    extra = [p.name for p in run.iterdir() if p.is_dir() and p.name not in {s["case_id"] for s in specs}]
    ev.require(not extra, "Unexpected run directories: " + repr(extra))
    ev.equal(summary.get("planned_requests"), 2400, "SUMMARY planned denominator")
    ev.equal(summary.get("completed_cases"), 48, "SUMMARY complete-case denominator")
    ev.equal(summary.get("unrun_cases"), missing, "SUMMARY unrun cases versus missing RESULT")
    ev.require(not missing, "No missing planned cases")
    structural = not ev.errors and len(cases) == 48 and all(c["evidence_intact"] for c in cases)
    groups = []
    for mode in MODES:
        for load in LOADS:
            subset = [c for c in cases if (c["mode"], c["load"]) == (mode, load)]
            groups.append({"mode": mode, "load": load, "complete_cases": sum(c["evidence_intact"] for c in subset),
                           "expected_cases": 12, "qualification_pass": structural and len(subset) == 12
                           and all(c["qualification_pass"] for c in subset)})
    ev.equal(summary.get("groups"), groups, "SUMMARY four independent group gates")
    # Any mismatch in the declared group results also closes qualification.
    if ev.errors:
        for group in groups:
            group["qualification_pass"] = False
    paired = []
    lookup = {(c["rep"], c["rate"], c["load"], c["mode"]): c for c in cases}
    for rep in range(3):
        for rate in (20, 50, 100, 200):
            for load in LOADS:
                pair = [lookup.get((rep, rate, load, mode)) for mode in MODES]
                vals = [c["statistics"]["admission_jitter"]["p99_ns"] if c else None for c in pair]
                paired.append({"rep": rep, "rate": rate, "load": load,
                               "thread_p99_ns": vals[0], "process_p99_ns": vals[1],
                               "process_minus_thread_p99_ns": vals[1] - vals[0]
                               if all(integer(x) for x in vals) else None})
    return {"schema": 1, "audit_pass": not ev.errors, "checks": ev.checks,
            "errors": ev.errors, "run_directory": str(run), "freeze_sha256": sha(freeze_path),
            "authorization_sha256": sha(authorization_path) if authorization_path and authorization_path.is_file() else None,
            "checker_sha256": sha(Path(__file__)), "planned_cases": 48, "planned_requests": 2400,
            "phase_start_monotonic_ns": beginning, "phase_end_monotonic_ns": end,
            "phase_elapsed_ns": elapsed, "within_80_second_phase": integer(elapsed) and elapsed <= 80_000_000_000,
            "within_81_5_second_cleanup_bound": integer(elapsed) and elapsed <= 81_500_000_000,
            "all_48_operationally_complete": structural, "groups": groups,
            "scheduler_both_loads": {mode: all(g["qualification_pass"] for g in groups if g["mode"] == mode)
                                     for mode in MODES},
            "missing_case_ids": missing, "received_before_admitted_count": sum(c["received_before_admitted_count"] for c in cases),
            "pairs": paired, "cases": cases,
            "limitations": ["Records and frozen source support reported workload/PID semantics; no independent OS trace was collected.",
                            "The case-start timestamp does not timestamp readiness, schedule send, or cleanup separately.",
                            "Receipt delay here is received_ns minus planned_ns, not a service latency.",
                            "Sequential-host synthetic qualification is not a serving, energy, or pure-GIL causal experiment."]}


def self_test():
    # Pure fabricated records: no Event, clock, pipe, process, thread, or driver.
    import copy
    tests = 0
    def check(value):
        nonlocal tests
        tests += 1
        if not value:
            raise AssertionError("Self-test " + str(tests))
    check(distribution(list(range(50))) == {"p99_ns": 49, "maximum_ns": 49})
    check(distribution([0] * 49 + [None]) == {"p99_ns": None, "maximum_ns": None})
    check(distribution(list(range(100))) == {"p99_ns": 98, "maximum_ns": 99})
    for bad in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
        try:
            decode(bad)
        except ValueError:
            check(True)
        else:
            check(False)
    value = 1
    for n in range(30):
        check(cpu_checksum(n) == value)
        value = (1664525 * value + 1013904223) % (1 << 32)
    spec = {"case_id": "synthetic", "mode": "thread", "load": "idle", "rep": 0,
            "rate": 20, "requests": [{"request_id": i, "offset_ns": (i + 1) * 1000} for i in range(50)]}
    ready = {"kind": "ready", "pid": 123, "switch_interval_seconds": 0.005}
    start = 60_000_001
    plan_rows = [dict(r, planned_ns=start + r["offset_ns"]) for r in spec["requests"]]
    cp = {"spec": spec, "case_start_monotonic_ns": start, "requests": plan_rows, "ready": ready}
    produced = [dict(r, wake_ns=r["planned_ns"] + 1, emitted_ns=r["planned_ns"] + 2,
                     admitted_ns=r["planned_ns"] + 4) for r in plan_rows]
    events = [{"received_ns": r["planned_ns"] + 3,
               "message": {**{k: r[k] for k in ("request_id", "planned_ns", "wake_ns", "emitted_ns")}, "kind": "offer"}}
              for r in produced]
    events.append({"received_ns": produced[-1]["admitted_ns"] + 1,
                   "message": {"kind": "done", "rows": produced, "failure": None}})
    result_rows = [dict(r, received_ns=r["planned_ns"] + 3, status="complete") for r in produced]
    result = {"case_id": "synthetic", "spec": spec, "failure": None, "requests": result_rows,
              "summary": statistics(result_rows), "producer_ready": ready,
              "consumer_load": {"iterations": 0}, "raw_offers_received": 50}
    epoch = {"consumer_pid": 123, "switch_interval_seconds": 0.005, "phase_start_monotonic_ns": 1}
    ev = Evidence()
    clean = check_case(spec, cp, events, result, epoch, ev)
    check(not ev.errors and clean["qualification_pass"] and clean["received_before_admitted_count"] == 50)
    # Consistent late data must fail qualification without failing the audit.
    p, raw, r = copy.deepcopy((cp, events, result))
    for event in raw:
        event["received_ns"] += 3_000_000
        msg = event["message"]
        if msg["kind"] == "offer":
            for field in ("wake_ns", "emitted_ns"):
                msg[field] += 3_000_000
        else:
            for row in msg["rows"]:
                for field in TIMES[:-1]:
                    row[field] += 3_000_000
    for row in r["requests"]:
        for field in TIMES:
            row[field] += 3_000_000
    r["summary"] = statistics(r["requests"])
    e = Evidence()
    late = check_case(spec, p, raw, r, epoch, e)
    check(not e.errors and not late["qualification_pass"])
    check(late["statistics"]["admission_jitter"]["p99_ns"] == 3_000_004)
    # The process/CPU condition must have a distinct producer PID and valid work.
    other_spec, p, raw, r = copy.deepcopy((spec, cp, events, result))
    other_spec.update(mode="process", load="python_cpu")
    p["spec"] = other_spec
    r["spec"] = other_spec
    p["ready"]["pid"] = 456
    r["producer_ready"] = p["ready"]
    r["consumer_load"] = {"iterations": 4096, "checksum": cpu_checksum(4096)}
    e = Evidence()
    check(check_case(other_spec, p, raw, r, epoch, e)["qualification_pass"] and not e.errors)
    r["consumer_load"]["checksum"] ^= 1
    e = Evidence()
    check(not check_case(other_spec, p, raw, r, epoch, e)["qualification_pass"] and bool(e.errors))
    for mutation in ("duplicate", "changed_plan", "missing_final", "reorder", "missing_admission", "receipt_before_emission", "wrong_pid", "changed_result"):
        p, raw, r = copy.deepcopy((cp, events, result))
        if mutation == "duplicate":
            raw.insert(1, copy.deepcopy(raw[0]))
        elif mutation == "changed_plan":
            p["requests"][0]["planned_ns"] += 1
        elif mutation == "missing_final":
            raw.pop()
        elif mutation == "reorder":
            raw[0], raw[1] = raw[1], raw[0]
        elif mutation == "missing_admission":
            raw[-1]["message"]["rows"][0]["admitted_ns"] = None
        elif mutation == "receipt_before_emission":
            raw[0]["received_ns"] = raw[0]["message"]["emitted_ns"] - 1
        elif mutation == "wrong_pid":
            p["ready"]["pid"] = 999
        else:
            r["requests"][0]["admitted_ns"] += 1
        e = Evidence()
        checked = check_case(spec, p, raw, r, epoch, e)
        check(bool(e.errors) and not checked["qualification_pass"])
        check(checked["statistics"]["planned"] == 50)
        if mutation in ("missing_final", "missing_admission"):
            check(checked["statistics"]["admission_jitter"]["p99_ns"] is None)
    return {"synthetic_only": True, "self_test_pass": True, "checks": tests}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("--freeze", type=Path, default=ROOT / "DRAFT_FREEZE_FINAL.json")
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--source-dir", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "ARRIVAL_AUDIT.json")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--validate-freeze", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return 0
    if args.validate_freeze:
        ev = Evidence()
        frozen = ev.read(args.freeze)
        cases = validate_freeze(frozen, args.source_dir, ev)
        print(json.dumps({"freeze_valid": not ev.errors, "cases": len(cases),
                          "checks": ev.checks, "errors": ev.errors}, sort_keys=True))
        return int(bool(ev.errors))
    if args.run is None:
        parser.error("RUN is required unless --self-test or --validate-freeze")
    if args.output.resolve().parent != ROOT or not args.output.name.startswith("ARRIVAL_AUDIT"):
        parser.error("Output must be an ARRIVAL_AUDIT* file in the application directory")
    try:
        report = audit_run(args.run.resolve(), args.freeze.resolve(), args.authorization, args.source_dir)
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        report = {"audit_pass": False, "errors": ["Malformed/incomplete evidence: " + str(exc)],
                  "planned_cases": 48, "planned_requests": 2400}
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({k: report.get(k) for k in ("audit_pass", "checks", "planned_cases", "planned_requests",
          "phase_elapsed_ns", "all_48_operationally_complete", "groups", "errors")}, sort_keys=True))
    return 0 if report["audit_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
