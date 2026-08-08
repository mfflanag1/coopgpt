"""d5: which hypotheses do the work?

For a fixed shape (gap pattern + c*), run the lab with the full condition set and
with each condition group removed in turn.  A group whose removal turns UNSAT
into SAT is ESSENTIAL to the proof of that half of C-C.

This doubles as a drop-the-hypothesis control: paper4's Remark mono:rem:exact
says the LEFT inclusion fails for inexact bumps, so removing exv2 must make the
left target SAT.  If it does not, the encoding is not faithful.

usage: d5_ablate.py <n> <gaps as 1,3> <cstar> <targets, comma sep> [--timeout=S]
"""
import sys, time, json
import z3
import d2_lab as lab

n = int(sys.argv[1])
gaps = tuple(int(x) for x in sys.argv[2].split(","))
cstar = int(sys.argv[3])
targets = sys.argv[4].split(",")
tmo = 600000
for a in sys.argv[5:]:
    if a.startswith("--timeout="):
        tmo = int(float(a.split("=")[1]) * 1000)

FULL = lab.ALLGROUPS
KEEP = {"core", "hstar"}                    # definitional, never dropped
print("shape gaps=%s c*=%d   full set = %s" % (gaps, cstar, FULL), flush=True)
out = {}
for target in targets:
    print("\n--- target %s" % target, flush=True)
    rows = []
    trials = [("FULL", FULL)] + [("-" + g, [x for x in FULL if x != g])
                                 for g in FULL if g not in KEEP]
    for label, groups in trials:
        t0 = time.time()
        s, H = lab.build(n, gaps, cstar, target, groups)
        s.set("timeout", tmo)
        r = s.check()
        extra = ""
        if r == z3.sat:
            m = s.model()
            Sm = [T for T in H["isS"] if z3.is_true(m.eval(H["isS"][T]))]
            extra = "  S=%s" % Sm
        rows.append((label, str(r)))
        print("  %-8s %-8s%s   (%.0fs)" % (label, r, extra, time.time() - t0),
              flush=True)
    out[target] = rows
    ess = [l[1:] for l, r in rows if l != "FULL" and r == "sat"]
    print("  ESSENTIAL for %s: %s" % (target, ess or "(none singly essential)"),
          flush=True)
json.dump(out, open("ablate_%s_%s_%d.json" % (n, "".join(map(str, gaps)), cstar), "w"),
          indent=1)
