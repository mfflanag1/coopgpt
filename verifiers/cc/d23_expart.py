"""d23: the exact-partition impossibility conjecture (paper4's last monotonicity
conjecture), decided at n = 5.

EXACT PARTITION at phi (paper4 abstract): every cumulative union of the richest
payoff strata is tight, i.e. every richer suffix H_j satisfies phi(H_j) = v(H_j).

CONJECTURE: no monotonicity failure occurs at an exact-partition phi.

Two questions, both run over all 31 nonempty gap patterns with S a variable
one-hot coalition, using the same complete encoding as the C-C decision (Lemma L
is necessary AND sufficient, so a model is a real game and UNSAT is a decision):

  bumpexists : does an exact-partition base admit an ADMISSIBLE EXACT BUMP at
               all (alpha > s_phi(S), v' exact)?  If this is UNSAT everywhere,
               the conjecture is VACUOUS at n = 5 and the honest verdict is
               "no five-player instance to decide", not "theorem".
  exists     : is there a monotonicity failure at an exact-partition phi?

Note a structural simplification that applies here: at exact partition the
Lemma-L certificate at every cut is witnessed by lambda = 1_{H_j}, nu = 1, so
"phi is leximin-maximal" is IMPLIED by "phi in core(v) and every richer suffix
tight" -- the base side of the encoding costs nothing.  (Recorded as Lemma EP
in REPORT3.txt.)

usage: d23_expart.py <target> [groups] [--timeout=SEC]
"""
import sys, itertools, time, json
import z3
import d2_lab as lab

target = sys.argv[1]
groups = ["core", "sup", "exv", "exv2", "cert", "cert2", "worse", "expart"]
tmo = 600000
for a in sys.argv[2:]:
    if a.startswith("--timeout="):
        tmo = int(float(a.split("=")[1]) * 1000)
    else:
        groups = a.split(",")
if target == "bumpexists":
    groups = [g for g in groups if g != "worse"]   # no failure => keep it valid
n = 5
print("n=%d target=%s groups=%s" % (n, target, ",".join(groups)), flush=True)
tally = {"sat": 0, "unsat": 0, "unknown": 0}
sats = []
t0 = time.time()
for r in range(1, n):
    for gaps in itertools.combinations(range(1, n), r):
        s, H = lab.build(n, gaps, gaps[0], target, groups)
        s.set("timeout", tmo)
        res = s.check()
        tally[str(res)] += 1
        flag = ""
        if res == z3.sat:
            m = s.model()
            Sm = [T for T in H["isS"] if z3.is_true(m.eval(H["isS"][T]))]
            flag = "   S=%s" % Sm
            sats.append(dict(gaps=list(gaps), S=Sm))
        print("  gaps=%-14s %-7s%s  (%.0fs)"
              % (str(gaps), res, flag, time.time() - t0), flush=True)
print(json.dumps(tally))
if sats:
    print("SAT shapes:", json.dumps(sats))
else:
    print("ALL %d GAP PATTERNS UNSAT for target '%s' at n=%d" %
          (tally["unsat"], target, n))
