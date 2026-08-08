"""Final tally across every artefact of task #22.  Produces summary.json and
the tables quoted in REPORT.txt / PROOF.txt.

usage: python3 summarize.py
"""
from __future__ import annotations
import glob
import json
import sys
from fractions import Fraction as F

HERE = sys.path[0]


def load(pat):
    out = []
    for fn in sorted(glob.glob(f"{HERE}/{pat}")):
        d = json.load(open(fn))
        out += d if isinstance(d, list) else d.get("results", [])
    return out


def key(x):
    return (str(x["lmin"]), str(x["lmax"]), str(x["tbl"]))


def main():
    s = {}
    ar = json.load(open(f"{HERE}/arith22_1_2.json"))["results"]
    s["configurations_total"] = len(ar)
    s["impossible_by_L1"] = sum(1 for x in ar if x["lmax"][-1] == 1)
    s["closed_by_arithmetic"] = sum(1 for x in ar if x["verdict"] == "closed")
    s["open_after_arithmetic"] = sum(1 for x in ar if x["verdict"] == "open")

    b1 = load("batch_1_2_*.json")
    s["pass1_run"] = len(b1)
    s["pass1_infeasible"] = sum(1 for x in b1 if x.get("feasible") is False)
    s["pass1_feasible"] = sum(1 for x in b1 if x.get("feasible"))
    s["pass1_errors"] = sum(1 for x in b1 if x.get("error"))

    b2 = load("batch2_1_2_*.json")
    s["pass2_run"] = len(b2)
    s["pass2_infeasible"] = sum(1 for x in b2 if x.get("feasible") is False)
    s["pass2_feasible"] = sum(1 for x in b2 if x.get("feasible"))
    s["pass2_errors"] = sum(1 for x in b2 if x.get("error"))

    # final verdict per configuration: pass2 overrides pass1
    fin = {key(x): x for x in b1}
    fin.update({key(x): x for x in b2})
    # the two-stratum classification comes from run2strat (FULL ladders); the
    # pass-1 controls used the weaker single-stage set and misclassify.
    r2 = load("run2strat_*.json")
    s["two_stratum_lmin_checked"] = len(r2)
    s["two_stratum_lmin_infeasible"] = sum(1 for v in r2
                                           if v.get("feasible") is False)
    s["two_stratum_impossible_cfg"] = sorted(
        f"{v['lmin']}x{v['lmax']}{v['tbl']}" for v in r2
        if v.get("control_positive_feasible") is False)
    s["two_stratum_bounded_cfg"] = sorted(
        f"{v['lmin']}x{v['lmax']}{v['tbl']}" for v in r2
        if v.get("control_positive_feasible") is True)
    s["final_still_feasible"] = sorted(
        [list(k) for k, v in fin.items() if v.get("feasible")])
    s["n_final_still_feasible"] = len(s["final_still_feasible"])

    try:
        au = json.load(open(f"{HERE}/audit22.json"))
        s["audited_witnesses"] = len(au)
        s["realizable_counterexamples"] = sum(
            1 for a in au if a["verdict"] == "REALIZABLE-COUNTEREXAMPLE")
        s["not_realizable"] = sum(1 for a in au
                                  if a["verdict"] == "NOT-REALIZABLE")
        s["not_a_game"] = sum(1 for a in au if a["verdict"] == "NOT-A-GAME")
    except FileNotFoundError:
        pass
    for name, fn in [("lemmas", "lemmas.json"), ("l1l2_filter", "l2filter.json"),
                     ("positive_control", "poscontrol.json")]:
        try:
            d = json.load(open(f"{HERE}/{fn}"))
            s[name] = {k: v for k, v in d.items() if k != "detail"}
        except FileNotFoundError:
            pass
    try:
        r41 = load("run41_*.json")
        s["regime41_target_third_run"] = len(r41)
        s["regime41_target_third_infeasible"] = sum(
            1 for x in r41 if x.get("feasible") is False)
        s["regime41_target_third_feasible"] = [
            [x["lmin"], x["lmax"], x["tbl"]] for x in r41 if x.get("feasible")]
    except Exception:
        pass
    try:
        s["completeness_control"] = [
            {"lmin": x["lmin"], "lmax": x["lmax"], "target": x["target"],
             "observed": x["observed_ratio"], "feasible": x["feasible"],
             "audit": (x.get("audit") or {}).get("verdict"),
             "true_ratio": (x.get("audit") or {}).get("true_ratio")}
            for x in json.load(open(f"{HERE}/completeness.json"))]
    except FileNotFoundError:
        pass
    print(json.dumps(s, indent=1))
    json.dump(s, open(f"{HERE}/summary.json", "w"), indent=1)


if __name__ == "__main__":
    main()
