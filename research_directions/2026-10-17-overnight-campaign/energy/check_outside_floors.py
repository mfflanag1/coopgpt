"""Exact finite replay of proportional payments, full floors, and coalition OUT."""
from fractions import Fraction as Q
import json
from pathlib import Path


def payment(e, h, eo, ho):
    E, H = e + eo, h + ho
    T = min(E, H)
    return Q(T) * (Q(e, E) + Q(h, H)) if T else Q(0)


def demand(condition, message):
    if not condition:
        raise RuntimeError(message)


profiles = deviations = 0
for e in range(5):
    for h in range(5):
        for eo in range(5):
            for ho in range(5):
                y = payment(e, h, eo, ho)
                F = min(e + eo, h + ho)
                demand(y >= F - min(eo, ho), "full-owner marginal floor")
                demand(y >= min(e, h), "coalition coverage")
                demand(y + payment(eo, ho, e, h) == 2 * F, "budget")
                for re in range(e + 1):
                    for rh in range(h + 1):
                        demand(y >= payment(re, rh, eo, ho) + min(e - re, h - rh),
                               "coalition outside-production deviation")
                        deviations += 1
                profiles += 1
result = {"status": "PASS", "arithmetic": "Fraction exact",
          "profiles": profiles, "coalition_outside_deviations": deviations,
          "scope": "Finite exact replay; all-real proof is in OUTSIDE_FLOOR_CONTRACT.txt and root OUT note."}
Path(__file__).with_name("outside_floor_checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
