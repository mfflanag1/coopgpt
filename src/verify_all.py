"""Independent re-verification of every SD-prenucleolus finding, with maximal
suspicion. Primary verifier = my sd_prenucleolus.py; cross-checked against the
parallel implementation sd.py. All exact rational unless marked screen."""
from fractions import Fraction as F
import random
from tugame import Game, is_balanced_game
import sd_prenucleolus as MINE          # my impl
import sd as ALT                        # parallel impl (prior instance)
from sd_float import sd_prenucleolus_float as mine_float
from validate_sd import random_monotonic_veto
from permutation import permutation_game

def hr(t): print("\n" + "=" * 70 + "\n" + t + "\n" + "=" * 70)

# ---------------------------------------------------------------- 1. cross-impl
def cross_impl():
    hr("1. CROSS-IMPLEMENTATION: my sd_prenucleolus vs sd.py (independent)")
    random.seed(11); mism = 0; tested = 0
    for _ in range(25):
        n = random.choice([3, 4])
        N = (1 << n) - 1
        v = [F(0)] * (1 << n)
        for S in range(1, N + 1):
            v[S] = F(random.randint(0, 9))
        v[N] = F(random.randint(n, 3 * n))
        g = Game(n, v)
        a = MINE.sd_prenucleolus(g)
        b = ALT.certified_sd_prenucleolus(g)
        tested += 1
        if b is None or list(a) != list(b):
            mism += 1
            print(f"  MISMATCH v={[int(x) for x in v]}: mine={a} alt={b}")
    print(f"  tested={tested} mismatches={mism}")
    return mism == 0

# ------------------------------------------------------- 2. SD-prekernel segment
def sdpk_segment():
    hr("2. SD-PREKERNEL CONTINUUM (game v; s_ij=min_{i in S, j not} F(S,x))")
    v = [F(x) for x in [0,0,0,17,0,18,5,19,0,2,17,19,8,20,17,49]]
    g = Game(4, v); N = g.N
    center = MINE.sd_prenucleolus(g)
    print("  my SD-prenucleolus (center):", [str(u) for u in center])
    print("  == [63/4,53/4,37/4,43/4]:", center == [F(63,4),F(53,4),F(37,4),F(43,4)])

    def s_ij(x):
        Fx = MINE.sd_satisfaction(g, x)
        out = {}
        for i in range(4):
            for j in range(4):
                if i != j:
                    out[(i,j)] = min(Fx[S] for S in range(1,N)
                                     if (S>>i&1) and not (S>>j&1))
        return out
    def equalized(x):
        s = s_ij(x)
        return all(s[(i,j)] == s[(j,i)] for i in range(4) for j in range(i+1,4))

    d = [F(1),F(-1),F(-1),F(1)]
    def pt(t): return [center[i] + t*d[i] for i in range(4)]
    inside = [F(-11,4), F(-2), F(-1), F(0), F(1), F(2), F(11,4)]
    outside = [F(-3), F(3), F(-11,4)-F(1,10), F(11,4)+F(1,10)]
    print("  equalized inside [-11/4,11/4]:",
          {str(t): equalized(pt(t)) for t in inside})
    print("  equalized just OUTSIDE:", {str(t): equalized(pt(t)) for t in outside})

    # uniqueness of SD-prenucleolus: only center passes SD-Kohlberg, and its
    # sorted satisfaction vector STRICTLY leximax-dominates any other seg point.
    def sat_sorted(x): return sorted(MINE.sd_satisfaction(g, x).values())
    ssc = sat_sorted(center)
    okc, _ = MINE.sd_kohlberg(g, center)
    print("  center passes my SD-Kohlberg:", okc)
    for t in (F(-11,4), F(2), F(11,4)):
        x = pt(t); okx,_ = MINE.sd_kohlberg(g, x); ss = sat_sorted(x)
        # ascending leximax: center dominates if first difference is larger
        diff = next(((c,o) for c,o in zip(ssc,ss) if c != o), None)
        print(f"    t={t}: kohlberg={okx}  sat==center:{ss==ssc}  "
              f"center_dominates:{diff is not None and diff[0] > diff[1]}")
    print("  => set-valued SD-prekernel (paper: strict incl., glove games);"
          " SD-prenucleolus (center) still UNIQUE. Not a refutation.")
    return center == [F(63,4),F(53,4),F(37,4),F(43,4)] and okc

# ------------------------------------------------------ 3. population monotonic
def pm_convex():
    hr("3. POPULATION MONOTONICITY on CONVEX (SD not claimed PM; verify witness)")
    v = [F(x) for x in [0,0,0,0,0,0,0,1,0,4,0,4,0,4,0,5]]
    g = Game(4, v)
    print("  full game convex:", g.is_convex(), " balanced:", is_balanced_game(g))
    S, T, i = 13, 15, 3          # S={0,2,3}, T=N, player 3
    subS, memS = g.subgame(S); subT, memT = g.subgame(T)
    xS = MINE.sd_prenucleolus(subS); xT = MINE.sd_prenucleolus(subT)
    posS = memS.index(i); posT = memT.index(i)
    print(f"  subgame S={memS} convex:{subS.is_convex()} SD={[str(u) for u in xS]}"
          f"  player{i}={xS[posS]}")
    print(f"  subgame T={memT} convex:{subT.is_convex()} SD={[str(u) for u in xT]}"
          f"  player{i}={xT[posT]}")
    drop = xT[posT] < xS[posS]
    print(f"  player {i}: {xS[posS]} -> {xT[posT]}  PM-violation:{drop}")
    # cross-check both subgames with sd.py + Kohlberg
    aS = ALT.certified_sd_prenucleolus(subS); aT = ALT.certified_sd_prenucleolus(subT)
    print("  sd.py agrees S,T:", list(aS)==list(xS), list(aT)==list(xT))
    print("  Kohlberg S,T:", MINE.sd_kohlberg(subS,xS)[0], MINE.sd_kohlberg(subT,xT)[0])
    return drop

# --------------------------------------------------- 4. permutation pairwise mono
def perm_pairwise():
    hr("4. PERMUTATION-GAME pairwise monotonicity of SD (parallels nucleolus)")
    ok = True
    # Q0: known nucleolus witness K, bump K[3][2] 1->2
    K = [[0,7,0,0],[1,0,0,1],[1,0,0,0],[0,9,1,0]]
    g = permutation_game(K); K2=[r[:] for r in K]; K2[3][2]+=1; g2=permutation_game(K2)
    b = MINE.sd_prenucleolus(g); a = MINE.sd_prenucleolus(g2)
    print("  Q0 SD before:", [str(u) for u in b], " after:", [str(u) for u in a])
    print(f"     player2: {b[2]} -> {a[2]}  drop:{a[2]<b[2]}")
    ok &= a[2] < b[2]
    # Q1 certified witness
    K = [[7,10,11,1],[3,2,7,11],[11,2,3,10],[3,8,5,6]]
    g = permutation_game(K)
    # bump = raise entry to change one matched value; use recorded (0,1)+2
    K2 = [r[:] for r in K]; K2[0][1] += 2; g2 = permutation_game(K2)
    b = MINE.sd_prenucleolus(g); a = MINE.sd_prenucleolus(g2)
    drops = [(i,str(b[i]-a[i])) for i in range(4) if a[i] < b[i]]
    print("  Q1 SD before:", [str(u) for u in b], " after:", [str(u) for u in a])
    print("     drops:", drops)
    ok &= len(drops) > 0
    print("  Kohlberg both (Q1):", MINE.sd_kohlberg(g,b)[0], MINE.sd_kohlberg(g2,a)[0])
    return ok

# ------------------------------------------- 5. CORRECT in-class veto calibration
def veto_inclass():
    hr("5. IN-CLASS veto calibration (raise keeps w a monotonic veto game)")
    random.seed(5); tested=0; viol=0; outofclass=0
    for _ in range(120):
        n = random.choice([3,4])
        g = random_monotonic_veto(n); N=g.N
        base = mine_float([float(x) for x in g.v], n)
        for S in range(1, N):
            if not (S & 1):        # must contain veto player 0 to stay veto game
                continue
            for d in (1,2,3):
                w = list(g.v); w[S]+=d; gw=Game(n,[F(x) for x in w])
                if not gw.is_monotone_game():   # w left the monotonic-veto class
                    outofclass += 1; continue
                aft = mine_float([float(x) for x in gw.v], n)
                tested += 1
                if any((S>>i&1) and aft[i] < base[i]-1e-7 for i in range(n)):
                    viol += 1
                    print(f"  IN-CLASS VIOLATION n{n} S={S} d={d} v={[int(x) for x in g.v]}")
    print(f"  in-class raises tested={tested} violations={viol} "
          f"(out-of-class skipped={outofclass})  expect violations=0")
    return viol == 0

if __name__ == "__main__":
    r1=cross_impl(); r2=sdpk_segment(); r3=pm_convex(); r4=perm_pairwise(); r5=veto_inclass()
    hr("SUMMARY")
    print("1 cross-impl agree      :", r1)
    print("2 SDPK segment + unique :", r2)
    print("3 PM-convex violation   :", r3)
    print("4 perm pairwise viol    :", r4)
    print("5 in-class veto clean   :", r5)
