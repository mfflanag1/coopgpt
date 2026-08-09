"""Does the R4 / merge route reach (R)?

(R) needs a LOWER bound on  max_{y in Core(v)} (2 y_p + y_q).
The merge lemma (PART round, M1) contracts B = {x,y,z} to one player r and
leaves the game exact:  w'(A) = v(A) for A in {p,q};  w'(A u {r}) = v(A u B) - v(B).
The projection pi(y) = (y_p, y_q, y(B) - v(B)) maps Core(v) INTO Core(w').

STRUCTURAL WORRY, before any computation: the objective 2y_p + y_q is unchanged
by pi, and Core(w') CONTAINS pi(Core(v)), so
      max over Core(w')  >=  max over Core(v).
That is an UPPER bound on the quantity we must bound BELOW -- the wrong
direction.  The route survives only if the projection is ONTO, i.e.
pi(Core(v)) = Core(w'), in which case the two maxima coincide.  This script
decides that empirically.
"""
import sys, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L, z3
n = 5; FULL = 31; PROPER = [S for S in range(1, FULL)]

def maxlin(nn, w, coef):
    x = [z3.Real(f"x{i}") for i in range(nn)]
    o = z3.Optimize()
    o.add(z3.Sum(x) == L.to_z3(w[(1 << nn) - 1]))
    for S in range(1, (1 << nn) - 1):
        o.add(z3.Sum([x[i] for i in range(nn) if S >> i & 1]) >= L.to_z3(w[S]))
    for i in range(nn):
        o.add(x[i] >= 0)
    h = o.maximize(z3.Sum([L.to_z3(coef[i]) * x[i] for i in range(nn)]))
    assert o.check() == z3.sat
    return L.rat(o.upper(h))

rng = random.Random(17)
tested = eq = 0
gaps = []
while tested < 120:
    total = rng.randint(5, 16)
    gens = []
    for _ in range(rng.randint(2, 5)):
        cuts = sorted(rng.randrange(total + 1) for _ in range(n - 1))
        gens.append(tuple(F(b - a) for a, b in zip([0] + cuts, cuts + [total])))
    if any(min(g[i] for g in gens) != 0 for i in range(n)):
        continue
    w, sh = L.normalize(n, L.envelope(n, gens))
    T = w[FULL]
    if T <= 0:
        continue
    tested += 1
    p, q = 0, 1
    B = [2, 3, 4]
    Bm = sum(1 << i for i in B)
    vB = w[Bm]
    # merged 3-player game on (p, q, r)
    w2 = [F(0)] * 8
    for A in range(8):
        pm = (1 if A & 1 else 0) * (1 << p) | (1 if A & 2 else 0) * (1 << q)
        if A & 4:
            w2[A] = w[pm | Bm] - vB
        else:
            w2[A] = w[pm] if pm else F(0)
    top = maxlin(n, w, [2, 1, 0, 0, 0])
    tom = maxlin(3, w2, [2, 1, 0])
    if top == tom:
        eq += 1
    else:
        gaps.append((tom - top, T))
print(f"games tested: {tested}")
print(f"  max over Core(v) equals max over Core(merged) : {eq}/{tested}")
if gaps:
    worst = max(gaps)
    print(f"  when they differ, merged is LARGER by up to {worst[0]} (T={worst[1]})")
    print("  => the projection is NOT onto; the merge gives an UPPER bound on a")
    print("     quantity that must be bounded BELOW.  Route is the wrong direction.")
else:
    print("  => projection appears onto on this sample; route may be viable.")
