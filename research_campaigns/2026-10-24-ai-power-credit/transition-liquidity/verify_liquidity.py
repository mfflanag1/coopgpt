#!/usr/bin/env python3
"""Exact finite cross-checks for MODEL_NOTE.txt; not a proof or issuer model."""
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path

def required_grant(events, initial, credit):
    balance = Q(0)
    peak = Q(0)
    for cost, receipt in events:
        balance += cost - receipt
        peak = max(peak, balance)
    return max(Q(0), peak-initial-credit)

def feasible(events, initial, grant, draw):
    cash = initial + grant + draw
    for cost, receipt in events:
        cash += receipt-cost
        if cash < 0:
            return False
    return True

def main():
    # Independent enumeration of permitted draws and contributions, not a
    # restatement of the prefix maximum. Half-unit grid, all event sequences
    # of length 1..3 with costs/receipts in {0, 1/2, 1}.
    vals = [Q(0), Q(1,2), Q(1)]
    grants = [Q(k,2) for k in range(7)]
    cases = 0
    for length in range(1,4):
        for flat in product(vals, repeat=2*length):
            events = list(zip(flat[::2],flat[1::2]))
            for initial, credit in product(vals, repeat=2):
                draws = [Q(k,2) for k in range(int(2*credit)+1)]
                minimum = next(g for g in grants if any(
                    feasible(events,initial,g,q) for q in draws))
                assert minimum == required_grant(events,initial,credit)
                cases += 1

    # Enumerate actual terminal payment splits. P, D, L and K are integers;
    # integral feasibility is enough for this finite grid because the two
    # inequalities admit integral witnesses whenever their data are integral.
    seniority_cases = 0
    for pledgeable, face in product(range(13),repeat=2):
        for liquidation in range(face+1):
            for cost in range(1,9):
                junior_ok = any(new >= cost and new <= max(0,pledgeable-face)
                                for new in range(pledgeable+1))
                outside = face if junior_ok else liquidation
                consent_ok = any(new >= cost and old >= outside
                    for new in range(pledgeable+1)
                    for old in range(pledgeable-new+1))
                assert junior_ok == (cost <= max(0,pledgeable-face))
                assert consent_ok == (pledgeable >= cost+liquidation)
                if consent_ok:
                    witness = (cost, outside, pledgeable-cost-outside)
                    assert min(witness) >= 0 and sum(witness) == pledgeable
                seniority_cases += 1

    examples = {
      "expense_before_receipt": str(required_grant([(Q(6),Q(0)),(Q(0),Q(12))],Q(0),Q(0))),
      "receipt_before_expense": str(required_grant([(Q(0),Q(12)),(Q(6),Q(0))],Q(0),Q(0))),
      "large_bridge_same_surplus": [
          {"cost": n,"surplus":1,
           "grant":str(required_grant([(Q(n),Q(0)),(Q(0),Q(n+1))],Q(0),Q(0)))}
          for n in (1,10,100,10000)],
      "seniority": {"R":12,"P":12,"K":6,"D":10,"L":4,
                    "junior_capacity":2,"consented_split":[6,4,2]},
      "limited_pledgeability": {"R":12,"P":8,"K":6,"D":10,"L":4,
                                "real_surplus":2,"consented_finance_possible":False}
    }
    assert examples["expense_before_receipt"] == "6"
    assert examples["receipt_before_expense"] == "0"
    result={"status":"passed","prefix_cases":cases,
            "seniority_cases":seniority_cases,"arithmetic":"fractions and integers",
            "scope":"finite diagnostic cross-checks; no empirical or universal proof by enumeration",
            "examples":examples}
    out=Path(__file__).with_name("verification_results.json")
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="examples"},indent=2))

if __name__ == "__main__":
    main()

