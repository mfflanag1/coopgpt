"""Execute the frozen synthetic energy-constrained inference-consortium pilot.

All economic comparisons use the same production technology. The public trace
is descriptive context only: this program is not a request-level serving replay.
"""

import argparse
import csv
from fractions import Fraction as Q
from itertools import product
from math import ceil
import json
from pathlib import Path
import time

from model import Technology, standalone_first
from payments import RULES, aggregate, payments


DESIGN_REPORTS = tuple(product((Q(0), Q(1)), (Q(0), Q(1)), (Q(0), Q(1), Q(2))))
EXAMPLE = ((Q(1), Q(0), Q(1)), (Q(0), Q(1), Q(2)), (Q(1), Q(1), Q(1)))
HELD_OUT = {
    "redundant_hardware": ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 2)),
    "fractional_mixed": ((Q(1, 2), 0, Q(1, 2)), (0, 1, 1),
                         (1, Q(1, 2), Q(1, 2)), (0, 0, 1)),
    "balanced": ((1, 0, 2), (0, 1, 1), (1, 0, 2), (0, 1, 1)),
    "stranded_energy": ((0, 0, 2), (0, 0, 1), (0, 0, 1), (0, 0, 0)),
    "zero_energy": ((1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 0)),
    "complementary": ((2, 0, 0), (0, 2, 0), (0, 0, 2), (0, 0, 4)),
}
# Each stress case fixes its physical inventory from its declared TRUE endowment.
# Never infer installed hardware from an underreport during a deviation check.
HELD_OUT_INSTALLED = {
    name: tuple(tuple(ceil(b[k]) for k in range(2)) for b in bundles)
    for name, bundles in HELD_OUT.items()
}


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def exact_json(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(key): exact_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [exact_json(item) for item in value]
    return value


def compact_json(value):
    return json.dumps(exact_json(value), separators=(",", ":"), sort_keys=True)


def new_metrics():
    return dict(profiles=0, positive_value_profiles=0, coalition_deficit_profiles=0,
                withholding_gain_profiles=0, max_coalition_deficit=Q(0),
                coalition_deficit_witness=None, max_withholding_gain=Q(0),
                withholding_gain_witness=None, max_total_payment=Q(0),
                max_subsidy=Q(0), max_payment_ratio=Q(0), max_subsidy_ratio=Q(0),
                payment_ratio_witness=None)


def run(output_dir):
    started = time.perf_counter()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    technology = Technology()
    cache = {}

    def payment(rule, bundles):
        bundles = tuple(tuple(map(Q, b)) for b in bundles)
        key = rule, bundles
        if key not in cache:
            cache[key] = payments(rule, bundles, technology.value,
                                  technology.dual_vertices, weights=(1, 1, 1), j=2)
        return cache[key]

    def assess(profile_id, bundles, lower_reports, metrics):
        bundles = tuple(tuple(map(Q, b)) for b in bundles)
        n = len(bundles)
        total = technology.value(aggregate(bundles))
        coalitions = []
        for mask in range(1 << n):
            members = tuple(i for i in range(n) if mask >> i & 1)
            coalitions.append((members, technology.value(aggregate(bundles, members))))
        deviations = []
        for i, own in enumerate(bundles):
            for low in lower_reports(own):
                low = tuple(map(Q, low))
                if low == own:
                    continue
                check(all(0 <= x <= y for x, y in zip(low, own)),
                      "Invalid componentwise lower report")
                changed = bundles[:i] + (low,) + bundles[i+1:]
                deviations.append((i, low, changed))

        records = {}
        for rule in RULES:
            pay = payment(rule, bundles)
            check(all(p >= 0 for p in pay), "Negative " + rule + " payment")
            total_payment = sum(pay, Q(0))
            subsidy = max(Q(0), total_payment-total)
            deficit = Q(0)
            deficit_witness = None
            for members, coalition_value in coalitions:
                candidate = coalition_value-sum((pay[i] for i in members), Q(0))
                if candidate > deficit:
                    deficit = candidate
                    deficit_witness = dict(profile_id=profile_id, bundles=bundles,
                                           members=members, coalition_value=coalition_value,
                                           coalition_payment=coalition_value-candidate,
                                           payments=pay)
            gain = Q(0)
            gain_witness = None
            for i, low, changed in deviations:
                hidden_payments = payment(rule, changed)
                hidden_payment = hidden_payments[i]
                candidate = hidden_payment-pay[i]
                if candidate > gain:
                    gain = candidate
                    gain_witness = dict(profile_id=profile_id, bundles=bundles,
                                        owner_index=i, lower_report=low,
                                        hidden_bundles=changed,
                                        true_payments=pay, hidden_payments=hidden_payments,
                                        true_payment=pay[i], hidden_payment=hidden_payment,
                                        true_value=total,
                                        hidden_value=technology.value(aggregate(changed)))
            if rule in ("proportional", "dual", "shapley"):
                check(total_payment == total, rule + " efficiency regression")
            if rule in ("dual", "marginal", "sharp_hybrid"):
                check(deficit == 0, rule + " coalition-coverage regression")
            if rule in ("proportional", "shapley", "marginal", "sharp_hybrid"):
                check(gain == 0, rule + " own-report monotonicity regression")
            if rule == "marginal":
                check(total_payment <= min(n, 2)*total,
                      "Sparse grand-marginal budget bound regression")
            if not total:
                check(total_payment == 0, "Nonzero payment at zero production")
            ratio = total_payment/total if total else None
            subsidy_ratio = subsidy/total if total else None
            records[rule] = dict(payments=pay, total_payment=total_payment,
                                 subsidy=subsidy, payment_ratio=ratio,
                                 max_coalition_deficit=deficit,
                                 max_withholding_gain=gain,
                                 deficit_witness=deficit_witness,
                                 withholding_witness=gain_witness)
            m = metrics[rule]
            m["profiles"] += 1
            m["positive_value_profiles"] += int(total > 0)
            m["coalition_deficit_profiles"] += int(deficit > 0)
            m["withholding_gain_profiles"] += int(gain > 0)
            m["max_total_payment"] = max(m["max_total_payment"], total_payment)
            m["max_subsidy"] = max(m["max_subsidy"], subsidy)
            if deficit > m["max_coalition_deficit"]:
                m["max_coalition_deficit"] = deficit
                m["coalition_deficit_witness"] = deficit_witness
            if gain > m["max_withholding_gain"]:
                m["max_withholding_gain"] = gain
                m["withholding_gain_witness"] = gain_witness
            if total and ratio > m["max_payment_ratio"]:
                m["max_payment_ratio"] = ratio
                m["payment_ratio_witness"] = dict(profile_id=profile_id, bundles=bundles,
                                                  value=total, payments=pay)
            if total:
                m["max_subsidy_ratio"] = max(m["max_subsidy_ratio"], subsidy_ratio)
        return total, records, len(coalitions), len(deviations)

    design_metrics = {rule: new_metrics() for rule in RULES}
    design_profiles = tuple(product(DESIGN_REPORTS, repeat=3))
    check(len(design_profiles) == 1728, "Frozen grid size changed")
    # All grid payment vectors are cached before any pairwise comparisons.
    for bundles in design_profiles:
        for rule in RULES:
            payment(rule, bundles)
    design_lower = lambda own: tuple(b for b in DESIGN_REPORTS
                                    if all(x <= y for x, y in zip(b, own)))
    design_coalitions = design_deviations = design_schedules = 0
    example = None
    max_pooling_gain = Q(0)
    max_priority_loss = Q(0)
    pooling_witness = priority_witness = None
    csv_path = output_dir / "PAYMENTS.csv"
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            "profile_id", "bundles_H_L_incremental_kWh", "rule", "value_points",
            "payments", "total_payment", "external_subsidy", "payment_ratio",
            "max_coalition_deficit", "max_unilateral_withholding_gain",
            "synthetic_technology", "trace_replay"))
        writer.writeheader()
        for index, bundles in enumerate(design_profiles):
            profile_id = "design_" + str(index).zfill(4)
            total, records, nc, nd = assess(profile_id, bundles, design_lower, design_metrics)
            design_coalitions += nc
            design_deviations += nd
            certificate = technology.schedule(bundles, installed=((1, 1),)*3)
            design_schedules += 1
            dispatch = standalone_first(technology, bundles)
            check(dispatch["autarky"] <= dispatch["standalone_first"] <= dispatch["joint"],
                  "Dispatch ordering regression")
            check(dispatch["joint"] == total, "Pooled dispatch differs from production value")
            pooling_gain = total-dispatch["autarky"]
            priority_loss = total-dispatch["standalone_first"]
            if pooling_gain > max_pooling_gain:
                max_pooling_gain = pooling_gain
                pooling_witness = dict(profile_id=profile_id, bundles=bundles, dispatch=dispatch)
            if priority_loss > max_priority_loss:
                max_priority_loss = priority_loss
                priority_witness = dict(profile_id=profile_id, bundles=bundles, dispatch=dispatch)
            for rule, rec in records.items():
                writer.writerow(dict(
                    profile_id=profile_id, bundles_H_L_incremental_kWh=compact_json(bundles),
                    rule=rule, value_points=str(total), payments=compact_json(rec["payments"]),
                    total_payment=str(rec["total_payment"]), external_subsidy=str(rec["subsidy"]),
                    payment_ratio="" if rec["payment_ratio"] is None else str(rec["payment_ratio"]),
                    max_coalition_deficit=str(rec["max_coalition_deficit"]),
                    max_unilateral_withholding_gain=str(rec["max_withholding_gain"]),
                    synthetic_technology="true", trace_replay="false"))
            if bundles == EXAMPLE:
                example = dict(profile_id=profile_id, bundles=bundles, value=total,
                               dispatch=dispatch, payment_rules=records, schedule=certificate)
    check(example is not None, "Declared example absent from design grid")

    held_metrics = {rule: new_metrics() for rule in RULES}
    held_cases = {}
    held_coalitions = held_deviations = 0
    stress_lower = lambda own: tuple(product(*(sorted({Q(0), x/2, x}) for x in own)))
    for name, raw in HELD_OUT.items():
        bundles = tuple(tuple(map(Q, b)) for b in raw)
        total, records, nc, nd = assess(name, bundles, stress_lower, held_metrics)
        held_coalitions += nc
        held_deviations += nd
        dispatch = standalone_first(technology, bundles)
        check(dispatch["autarky"] <= dispatch["standalone_first"] <= dispatch["joint"] == total,
              "Held-out dispatch regression")
        held_cases[name] = dict(bundles=bundles, value=total, dispatch=dispatch,
                                payment_rules=records, coalition_checks_per_rule=nc,
                                strict_unilateral_pairs_per_rule=nd,
                                schedule=technology.schedule(bundles, HELD_OUT_INSTALLED[name]))

    elapsed = time.perf_counter()-started
    results = dict(
        status="pass",
        interpretation=("Synthetic exact-rational capacity-sharing stress test. "
                        "No trace-replayed serving, empirical dollar savings, tail-SLA "
                        "guarantee, market participation prediction or novelty claim."),
        technology=dict(resource_units=["H node-hours", "L node-hours", "incremental kWh"],
                        output_unit="synthetic public service-capacity value points",
                        A=((1, 0), (0, 1), (2, 1)), prices=(6, 2),
                        dual_vertices=technology.dual_vertices,
                        proportional_weights=(1, 1, 1), fixed_hybrid_j=2),
        design=dict(profiles=len(design_profiles), owners=3,
                    coalitions_per_rule=design_coalitions,
                    strict_unilateral_report_pairs_per_rule=design_deviations,
                    schedule_certificates=design_schedules,
                    frequency_interpretation="Uniform artificial grid frequencies only",
                    rule_metrics=design_metrics,
                    maximum_pooling_gain=max_pooling_gain, pooling_gain_witness=pooling_witness,
                    maximum_standalone_first_loss=max_priority_loss,
                    standalone_first_loss_witness=priority_witness),
        declared_example=example,
        held_out=dict(profiles=len(HELD_OUT), owners=4, coalitions_per_rule=held_coalitions,
                      strict_unilateral_report_pairs_per_rule=held_deviations,
                      schedule_certificates=len(HELD_OUT), rule_metrics=held_metrics,
                      cases=held_cases),
        computation=dict(unique_production_value_inputs=technology.value_count,
                         payment_vectors_cached=len(cache),
                         exact_arithmetic="fractions.Fraction",
                         runtime_seconds=round(elapsed, 6),
                         runtime_is_nondeterministic=True),
        artifacts=dict(detailed_grid_payments="PAYMENTS.csv", trace_context="TRACE_PROVENANCE.json"))
    result_path = output_dir / "RESULTS.json"
    result_path.write_text(json.dumps(exact_json(results), indent=2, sort_keys=True) + "\n")
    print(json.dumps(exact_json(dict(status="pass", design_profiles=len(design_profiles),
                                   design_rule_metrics=design_metrics,
                                   held_out_profiles=len(HELD_OUT),
                                   computation=results["computation"],
                                   results_file=str(result_path), payments_file=str(csv_path))),
                     indent=2, sort_keys=True))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    run(parser.parse_args().output_dir)
