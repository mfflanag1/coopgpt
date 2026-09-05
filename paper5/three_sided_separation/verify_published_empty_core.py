"""Exact independent arithmetic calibration of Atay--Nunez 2019 Example 1."""
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import json

layers = [[[3,1],[2,5]], [[1,4],[5,4]]]
def a(i,j,k):
    return layers[k-1][i-1][j-1]

matchings = []
for q in permutations((1,2)):
    for r in permutations((1,2)):
        edges = [(i,q[i-1],r[i-1]) for i in (1,2)]
        matchings.append({"edges":edges,"value":sum(a(*e) for e in edges)})
best = max(x["value"] for x in matchings)
if best != 7 or sum(x["value"]==best for x in matchings) != 1:
    raise RuntimeError("published optimal matching mismatch")
tests = [(2*a(1,1,1)+a(2,2,2),a(1,1,2)+a(1,2,1)+a(2,1,1)),
         (a(1,1,1)+2*a(2,2,2),a(2,2,1)+a(2,1,2)+a(1,2,2))]
if tests != [(10,4),(11,14)]:
    raise RuntimeError("Lucas-condition transcription mismatch")
certificate = [(1,1,1),(1,2,2),(2,1,2),(2,2,1)]
counts = {(side,i):sum(e[side]==i for e in certificate)
          for side in range(3) for i in (1,2)}
if set(counts.values()) != {2}:
    raise RuntimeError("invalid balanced fractional certificate")
fractional_value = sum(Fraction(a(*e),2) for e in certificate)
if fractional_value != Fraction(17,2) or fractional_value <= best:
    raise RuntimeError("certificate fails to refute core feasibility")
out = {"layers":layers,"perfect_matchings":matchings,"T":best,
       "Lucas_conditions":tests,"fractional_support":certificate,
       "fractional_value":str(fractional_value),"core":"empty"}
Path(__file__).with_name("published_empty_core_results.json").write_text(
    json.dumps(out,indent=2)+"\n")
print("PASS: unique integral optimum 7; Lucas violation 11<14; fractional certificate 17/2")
