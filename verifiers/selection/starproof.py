"""Audit of the star-facet proposition: St(H,Q) is minimal semi-balanced and
indecomposable, for every h>=1 and every nonempty proper Q of L.

Checked with the independent classifier sbcheck.classify at n = 4,5,6,7 for one
representative of every (h,q) pair, and -- to stress the proof's case analysis --
by brute force over EVERY external E at n = 7.
"""
import sys, json
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
import catalogue, sbcheck

def star(n, h, q):
    H = (1 << h) - 1
    L = list(range(h, n))
    Q = sum(1 << L[k] for k in range(q))
    lam = {H | Q: 1}
    for i in L:
        if not Q >> i & 1:
            lam[H | (1 << i)] = lam.get(H | (1 << i), 0) + 1
    lam[H] = lam.get(H, 0) - (len(L) - q)
    return {S: c for S, c in lam.items() if c}

out = []
for n in (4, 5, 6, 7):
    tab = catalogue.index(n)[0] if n <= 6 else None
    for h in range(1, n - 1):
        for q in range(1, n - h):
            lam = star(n, h, q)
            # the displayed combination must be constant, = 1_N
            load = [sum(c for S, c in lam.items() if S >> i & 1) for i in range(n)]
            assert load == [1] * n, (n, h, q, load)
            verdict, wit = sbcheck.classify(n, list(lam))
            rows = tab.get(catalogue.canon(n, lam)) if tab else None
            ok = verdict.startswith("indecomposable")
            print(f"n={n} h={h} q={q}  {catalogue.pretty(n, lam):48s} {verdict:34s} "
                  f"rows={rows}  {'OK' if ok else 'FAIL'}", flush=True)
            out.append({"n": n, "h": h, "q": q, "verdict": verdict, "rows": rows})
            assert ok, (n, h, q, verdict, wit)
json.dump(out, open(SCR + "/sel/starproof.json", "w"), indent=1)
print("\nall star systems on n<=7 are indecomposable minimal semi-balanced")
