"""d19: minimal hypothesis set for a single shape (fast, one z3 call each)."""
import sys, time, itertools, z3
import d2_lab as lab
n = int(sys.argv[1]); target = sys.argv[2]
gaps = tuple(int(x) for x in sys.argv[3].split(",")); cstar = int(sys.argv[4])
sets = sys.argv[5].split(";")
for gs in sets:
    g = gs.split(",")
    t0 = time.time()
    s, H = lab.build(n, gaps, cstar, target, g)
    s.set("timeout", 600000)
    r = s.check()
    extra = ""
    if r == z3.sat:
        m = s.model()
        extra = "  S=%s" % [T for T in H["isS"] if z3.is_true(m.eval(H["isS"][T]))]
    print("  %-45s %-7s%s  (%.0fs)" % (gs, r, extra, time.time() - t0), flush=True)
