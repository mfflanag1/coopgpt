"""Exact finite supplement; the integration/cap arguments are in the note."""
from fractions import Fraction as Q
from itertools import combinations
import json
from pathlib import Path

def worth(bundle):
    return min(bundle[0], bundle[1]) + bundle[2]

def total(reports, selected):
    return tuple(sum((reports[i][a] for i in selected), Q(0)) for a in range(3))

low = ((Q(1), Q(0), Q(0)), (Q(0), Q(1), Q(0)),
       (Q(0), Q(1), Q(0)), (Q(0), Q(0), Q(1)))
high = (low[0], (Q(0), Q(3, 2), Q(0)), low[2], low[3])
assert all(high[i] == low[i] for i in (0, 2, 3))
assert all(high[1][a] >= low[1][a] for a in range(3))
rows = []
for size in range(5):
    for coalition in combinations(range(4), size):
        vl = worth(total(low, coalition))
        vh = worth(total(high, coalition))
        assert vl == vh
        rows.append({"coalition": coalition, "both_values": str(vl)})
for reports in (low, high):
    V = worth(total(reports, range(4)))
    assert V == 2
    capped = tuple(tuple(min(v, V) for v in row) for row in reports)
    assert capped == reports

# On x,y>=1, exact polynomial integration is
# int_{u=0}^1 int_{v=0}^{u/y} (u-y*v) dv du = 1/(6*y).
phi_low = Q(1, 6) + Q(1, 6)
phi_high = Q(1, 6) + Q(1, 9)
assert phi_high - phi_low == -Q(1, 18)
delta = tuple(high[1][a] - low[1][a] for a in range(3))
assert worth(delta) == 0
out = {"coalition_worth_rows": rows, "global_output": "2",
       "cap_unchanged": True, "protected_coalition": [1, 2],
       "low_fractional_payment": str(phi_low),
       "high_fractional_payment": str(phi_high),
       "protected_increment": str(phi_high - phi_low),
       "outside_production": str(worth(delta)),
       "scope": "Exact finite check; analytic integral and cap proof are separate."}
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "coalition_worth_rows"}))
