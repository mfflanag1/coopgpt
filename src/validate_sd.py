"""Validate the SD-prenucleolus implementation:
 (1) coincides with the serial rule on monotonic veto games (Arin-Katsev Sec 6);
 (2) the LP optimizer agrees with the independent SD-Kohlberg certifier;
 (3) AFM-2012 Example 2 worked value.
"""
import random
from fractions import Fraction as F
from tugame import Game
from serial_rule import serial_rule
from sd_prenucleolus import sd_prenucleolus, sd_kohlberg, sd_satisfaction

def random_monotonic_veto(n, hi=9, rng=random):
    """Player 0 is the veto player: v(S)=0 unless 0 in S; monotonic; v(N)>0."""
    N = (1 << n) - 1
    v = [F(0)] * (1 << n)
    for S in range(1, N + 1):
        if not (S & 1):
            v[S] = F(0)
    # assign nondecreasing-ish values to veto coalitions, then enforce monotonicity
    for S in range(1, N + 1):
        if S & 1:
            v[S] = F(rng.randint(0, hi))
    for S in range(1, N + 1):          # enforce monotonicity by upward closure
        if S & 1:
            for i in range(n):
                if not (S >> i & 1):
                    T = S | (1 << i)
                    if v[T] < v[S]:
                        v[T] = v[S]
    if v[N] == 0:
        v[N] = F(rng.randint(1, hi))
    return Game(n, v)

def run():
    random.seed(7)
    # (3) AFM Example 2
    v = [F(0)] * 16
    v[0b0111] = 8; v[0b1011] = 8; v[0b1101] = 6; v[0b1111] = 12
    g = Game(4, v)
    sd = sd_prenucleolus(g)
    print("AFM Ex2 SD-prenucleolus =", [str(u) for u in sd], "(serial rule (8,2,1,1))")
    assert sd == [F(8), F(2), F(1), F(1)], "AFM example mismatch"
    ok, why = sd_kohlberg(g, sd); assert ok, f"kohlberg rejects AFM: {why}"

    # (1)+(2) random monotonic veto games: SD == serial rule, and self-cert
    mism = 0; certfail = 0; tested = 0
    for n in (3, 4, 5):
        for _ in range(200):
            g = random_monotonic_veto(n)
            sr = serial_rule(g)
            sd = sd_prenucleolus(g)
            tested += 1
            if sd != sr:
                mism += 1
                if mism <= 3:
                    print(f"  MISMATCH n={n}: SD={[str(u) for u in sd]} SR={[str(u) for u in sr]}")
                    print("    v=", {S: str(g.v[S]) for S in range(1, 1 << n) if g.v[S] != 0})
            ok, why = sd_kohlberg(g, sd)
            if not ok:
                certfail += 1
                if certfail <= 3:
                    print(f"  CERTFAIL n={n}: {why}")
    print(f"veto games: tested={tested} serial-rule mismatches={mism} kohlberg-failures={certfail}")

    # extra: random GENERAL balanced-ish games, LP-vs-Kohlberg self consistency
    selffail = 0; n_general = 0
    for _ in range(300):
        n = random.choice([3, 4])
        N = (1 << n) - 1
        v = [F(0)] * (1 << n)
        for S in range(1, N + 1):
            v[S] = F(random.randint(0, 8))
        v[N] = F(random.randint(n, 4 * n))
        g = Game(n, v)
        sd = sd_prenucleolus(g)
        if sd is None:
            continue
        n_general += 1
        ok, why = sd_kohlberg(g, sd)
        if not ok:
            selffail += 1
            if selffail <= 5:
                print(f"  GENERAL selfcert FAIL n={n}: {why}  v="
                      + str({S: str(v[S]) for S in range(1, N + 1)}))
    print(f"general games: tested={n_general} LP-vs-Kohlberg self-cert failures={selffail}")

if __name__ == "__main__":
    run()
