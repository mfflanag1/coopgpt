#!/usr/bin/env python3
"""Exact audit of the PXC142 saturation-lock obstruction.

PXC140's concavity reduction is valid, but its proposed product estimate is
not: this verifier constructs an exact singleton-normalized n=6 game in the
strict-spectral branch with tau_*=1 and certifies e_0>O-c_6T by an exact
primal--dual chord calculation.  The main hybrid-overlap inequality survives.

All load-bearing optimization checks below are rational.  SciPy was used only
to discover the displayed certificates; it is not imported here.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(HERE.parent), str(HERE.parent / "search_archive")]

from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from unrestricted_pxc91c_exact_search import (  # noqa: E402
    coalition_minimum_with_witness,
    selector_pair,
    selectors,
)
from verify_pxc138_diagonal_release_curve import sharp_data  # noqa: E402
from verify_pxc139_strict_spectral_single_dual_no_go import (  # noqa: E402
    DEFINING as PXC139_DEFINING,
    N,
    TOTAL as PXC139_TOTAL,
)


TOTAL = F(4)
EPSILON = F(34, 35)
X = (F(39, 70), F(1, 2), F(1, 35), F(169, 140), F(169, 140), F(1, 2))
Z = (F(104, 105), F(14, 15), F(1, 35), F(104, 105), F(104, 105), F(1, 15))


def blended_game():
    sharp_values, _sharp_x, _sharp_z = sharp_data()
    p139_values, _p139_x, _p139_z = selector_pair(PXC139_DEFINING, N, PXC139_TOTAL)
    p139_scaled = tuple(q / 2 for q in p139_values)
    return tuple((1 - EPSILON) * a + EPSILON * b
                 for a, b in zip(sharp_values, p139_scaled))


def release_lp(values, x, z, t):
    """Return the rational minimization form for T+Psi_t.

    Variables are pi_i, F_ri, u^x_i, u^z_i.  The objective is minus the
    overlap payoff, so Psi_t=-opt-T.
    """
    n = len(x); full = (1 << n) - 1; width = n + n*n + 2*n
    ip = lambda i: i
    iff = lambda r, i: n + r*n + i
    iux = lambda i: n + n*n + i
    iuz = lambda i: n + n*n + n + i
    objective = [F(0)] * width
    for i in range(n):
        objective[iux(i)] = objective[iuz(i)] = F(-1)
    aeq, beq = [], []
    row = [F(0)] * width
    for i in range(n): row[ip(i)] = F(1)
    aeq.append(row); beq.append(F(1))
    for r in range(n):
        row = [F(0)] * width; row[ip(r)] = F(-1)
        for i in range(n): row[iff(r, i)] = F(1)
        aeq.append(row); beq.append(F(0))
    for i in range(n):
        row = [F(0)] * width; row[ip(i)] = F(-1)
        for r in range(n): row[iff(r, i)] = F(1)
        aeq.append(row); beq.append(F(0))
    aub, bub = [], []
    for r in range(n):
        for coalition in range(1, full):
            row = [F(0)] * width; row[ip(r)] = values[coalition]
            for i in range(n):
                if coalition >> i & 1: row[iff(r, i)] = -TOTAL
            aub.append(row); bub.append(F(0))
    for i in range(n):
        row = [F(0)] * width; row[iux(i)] = F(1)
        aub.append(row); bub.append(x[i])
        row = [F(0)] * width; row[iux(i)] = F(1); row[ip(i)] = -TOTAL
        aub.append(row); bub.append(F(0))
        row = [F(0)] * width; row[iuz(i)] = F(1)
        aub.append(row); bub.append(z[i])
        row = [F(0)] * width; row[iuz(i)] = F(1); row[ip(i)] = -TOTAL
        aub.append(row); bub.append(F(0))
    lower = [F(0)] * width; upper = [None] * width
    for i in range(n): upper[iff(i, i)] = F(t) * x[i] * z[i] / TOTAL**2
    return objective, aeq, beq, aub, bub, lower, upper


T_QUARTER_PRIMAL = {
    0:F(261907,1855560),1:F(468683,3684800),2:F(187,26320),3:F(169,560),
    4:F(169,560),5:F(62857517,519556800),6:F(169,19600),7:F(107257,16236150),
    8:F(261907,259778400),9:F(291296849,4546122000),10:F(24362531,757687000),
    11:F(7450633,259778400),12:F(15502847,1547616000),13:F(7,960),
    14:F(468683,515872000),15:F(35114917,773808000),16:F(483613,12090750),
    17:F(18260483,773808000),18:F(6919,3684800),19:F(3179,1842400),
    20:F(1,78400),21:F(1,26320),22:F(3179,921200),24:F(169,2240),
    25:F(2873,39200),26:F(169,78400),28:F(11661,78400),29:F(169,78400),
    30:F(480406711,36368976000),31:F(323611891,36368976000),32:F(169,78400),
    33:F(2331159903,12122992000),34:F(2197,117600),35:F(2420297459,36368976000),
    36:F(2325728129,72737952000),37:F(1068577789,36368976000),
    38:F(62857517,72737952000),40:F(1068577789,18184488000),42:F(39,70),
    43:F(1,2),44:F(187,6580),45:F(169,140),46:F(169,140),
    47:F(62857517,129889200),48:F(261907,463890),49:F(468683,921200),
    50:F(187,6580),51:F(104,105),52:F(104,105),53:F(1,15),
}


T_ZERO_DUAL = {
    ("eq",0):F(-41124579,12927718),("eq",1):F(-51350040,6463859),
    ("eq",2):F(-84441000,6463859),("eq",3):F(-1995560,380227),
    ("eq",4):F(-51350040,6463859),("eq",5):F(-84441000,6463859),
    ("eq",6):F(-223508355,25855436),("eq",7):F(33090960,6463859),
    ("eq",8):F(1995560,380227),("eq",9):F(51350040,6463859),
    ("eq",11):F(777805,760454),("ub",10):F(-777805,3041816),
    ("ub",24):F(-498890,380227),("ub",26):F(-21628355,51710872),
    ("ub",32):F(-12837510,6463859),("ub",72):F(-777805,3041816),
    ("ub",91):F(-8272740,6463859),("ub",95):F(-79404605,51710872),
    ("ub",120):F(-89477395,51710872),("ub",151):F(-52959235,51710872),
    ("ub",167):F(-777805,3041816),("ub",180):F(-208390,6463859),
    ("ub",241):F(-52959235,51710872),("ub",242):F(-208390,6463859),
    ("ub",244):F(-4356380,6463859),("ub",272):F(-498890,380227),
    ("ub",277):F(-8272740,6463859),("ub",295):F(-16753870,6463859),
    ("ub",306):F(-4356380,6463859),("ub",335):F(-87810275,103421744),
    ("ub",337):F(-18108195,103421744),("ub",366):F(-91144515,103421744),
    ("ub",373):F(-1),("ub",375):F(-1),("ub",377):F(-1),("ub",379):F(-1),
    ("ub",381):F(-1),("ub",383):F(-1),("ub",384):F(-1),("ub",386):F(-1),
    ("ub",389):F(-1),("ub",390):F(-1),("ub",392):F(-1),("ub",394):F(-1),
    ("lo",23):F(-52959235,12927718),("lo",27):F(-777805,760454),
    ("lo",29):F(-777805,760454),("lo",39):F(-777805,760454),
    ("lo",41):F(-33090960,6463859),("hi",6):F(-84441000,6463859),
    ("hi",13):F(-147253645,12927718),("hi",20):F(-50516480,6463859),
    ("hi",34):F(-147253645,12927718),
}


def replay_quarter_primal(values):
    objective, aeq, beq, aub, bub, lower, upper = release_lp(values, X, Z, F(1,4))
    point = [T_QUARTER_PRIMAL.get(i, F(0)) for i in range(len(objective))]
    if any(sum(a*b for a,b in zip(row,point)) != rhs for row,rhs in zip(aeq,beq)):
        raise AssertionError("quarter primal equality")
    if any(sum(a*b for a,b in zip(row,point)) > rhs for row,rhs in zip(aub,bub)):
        raise AssertionError("quarter primal inequality")
    if any(point[i] < lower[i] or (upper[i] is not None and point[i] > upper[i])
           for i in range(len(point))):
        raise AssertionError("quarter primal bound")
    optimum_upper = sum(a*b for a,b in zip(objective,point))
    return -optimum_upper - TOTAL


def replay_zero_dual(values):
    objective, aeq, beq, aub, bub, lower, upper = release_lp(values, X, Z, F(0))
    width = len(objective); normal = [F(0)] * width; dual_objective = F(0)
    for (kind,index), multiplier in T_ZERO_DUAL.items():
        if kind == "eq": row, rhs = aeq[index], beq[index]
        elif kind == "ub": row, rhs = aub[index], bub[index]
        elif kind == "lo":
            row = [F(0)] * width; row[index] = F(-1); rhs = -lower[index]
        elif kind == "hi":
            row = [F(0)] * width; row[index] = F(1); rhs = upper[index]
        else: raise AssertionError(kind)
        if kind != "eq" and multiplier > 0:
            raise AssertionError(("dual sign",kind,index,multiplier))
        for j in range(width): normal[j] += multiplier * row[j]
        dual_objective += multiplier * rhs
    if normal != objective:
        raise AssertionError("zero dual stationarity")
    return -dual_objective - TOTAL


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values = blended_game()
    x, z = selectors(values, N)
    if (x,z) != (X,Z): raise AssertionError(("selectors",x,z))
    witnesses = []
    for coalition in range(1 << N):
        minimum, witness = coalition_minimum_with_witness(
            {s:values[s] for s in range(1,(1<<N)-1) if values[s]}, N, TOTAL, coalition)
        if minimum != values[coalition]: raise AssertionError(("not exact",coalition))
        witnesses.append(witness)
    if any(values[1<<i] for i in range(N)): raise AssertionError("not singleton normalized")

    overlap = sum(min(a,b) for a,b in zip(X,Z))
    target = F(2,3) * TOTAL
    spectral = spectral_decomposition("PXC142",values,X,Z)
    bstar = F(spectral["sharpened_spectral_bound_ratio"]) * TOTAL
    if not (bstar - target == F(-1,210) and overlap-target == F(7,15)):
        raise AssertionError(("strict spectral data",bstar,target,overlap))

    # Complement-tight equal-coordinate lock.  Every core allocation has
    # y_2<=q.  A stationary center equal to q is therefore supported only on
    # rows with w^r_2=q; positive pi_2 then forces F_22=pi_2*q/T=q^2/T^2.
    player=2; complement=((1<<N)-1)^(1<<player); q=X[player]
    if not (q==Z[player]>0 and values[complement]==TOTAL-q):
        raise AssertionError("lock hypotheses")
    tau = F(1)

    phi_quarter = replay_quarter_primal(values)
    phi_zero = replay_zero_dual(values)
    chord = 4*(phi_quarter-phi_zero)
    if not (phi_quarter==F(61849,19740) and
            phi_zero==F(7970384113,2714820780) and
            chord==F(1678344132,2126609611)>overlap-target):
        raise AssertionError(("chord",phi_zero,phi_quarter,chord,overlap-target))

    payload={
        "claim":"PXC142 complement-tight saturation lock and strict-spectral product no-go",
        "construction":{"epsilon":str(EPSILON),"n":N,"total":str(TOTAL),
                        "source_games":["sharp total-four control","PXC139 scaled by 1/2"]},
        "selectors":{"x":list(map(str,X)),"z":list(map(str,Z))},
        "exact_game":{"all_coalition_minima_replayed":len(witnesses),
                      "singleton_values":[str(values[1<<i]) for i in range(N)]},
        "spectral":{"B_star":str(bstar),"target":str(target),
                    "strict_margin":str(bstar-target)},
        "overlap":{"O":str(overlap),"available":str(overlap-target)},
        "saturation_lock":{"player":player,"q":str(q),
                           "complement_value":str(values[complement]),"tau_star":str(tau)},
        "release_chord":{"t":"1/4","Psi_0_upper":str(phi_zero),
                         "Psi_quarter_lower":str(phi_quarter),
                         "e0_lower_bound":str(chord),
                         "excess_over_available":str(chord-(overlap-target))},
        "conclusion":"tau_* e0 > O-c_6T; the PXC140 product estimate is false",
        "main_inequality_status":"not refuted: O exceeds c_6T by 7/15",
    }
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output: args.output.write_text(rendered)
    print(rendered,end="")


if __name__=="__main__": main()
