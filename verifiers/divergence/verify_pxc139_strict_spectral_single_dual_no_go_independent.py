#!/usr/bin/env python3
"""Standalone exact audit of the PXC139 strict-spectral route falsifier.

No project game, selector, LP, spectral, or stationary implementation is
imported.  The script enumerates the seven-row core vertices, reconstructs
all 64 coalition minima, proves both selector stages by explicit
inequalities, recomputes B_* by its finite top-block formula, and replays the
two primal plus one dual certificates.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


N, T = 6, F(8)
ROWS = {15: F(4), 29: F(6), 30: F(6), 37: F(2), 38: F(2), 52: F(2), 59: F(8)}
X = (F(1), F(1), F(0), F(5, 2), F(5, 2), F(1))
Z = (F(2), F(2), F(0), F(2), F(2), F(0))


def csum(point, mask):
    return sum(point[i] for i in range(N) if mask >> i & 1)


def solve_square(matrix, rhs):
    aug = [list(map(F, row)) + [F(value)] for row, value in zip(matrix, rhs)]
    for col in range(N):
        pivot = next((row for row in range(col, N) if aug[row][col]), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [value / scale for value in aug[col]]
        for row in range(N):
            if row == col or not aug[row][col]:
                continue
            scale = aug[row][col]
            aug[row] = [a - scale * b for a, b in zip(aug[row], aug[col])]
    return tuple(row[-1] for row in aug)


def reconstruct_game():
    inequalities = []
    for i in range(N):
        inequalities.append((tuple(F(int(i == j)) for j in range(N)), F(0)))
    for mask, bound in ROWS.items():
        inequalities.append((tuple(F(int(mask >> j & 1)) for j in range(N)), bound))
    vertices = set()
    total_row = (F(1),) * N
    for active in itertools.combinations(range(len(inequalities)), N - 1):
        point = solve_square(
            [total_row] + [inequalities[index][0] for index in active],
            [T] + [inequalities[index][1] for index in active],
        )
        if point is not None and all(
            sum(a*b for a, b in zip(normal, point)) >= bound
            for normal, bound in inequalities
        ):
            vertices.add(point)
    expected = {
        tuple(map(F, row)) for row in (
            (0, 0, 0, 4, 2, 2), (0, 0, 0, 6, 0, 2),
            (2, 2, 0, 0, 4, 0), (2, 2, 0, 2, 2, 0),
        )
    }
    if vertices != expected:
        raise AssertionError(("vertex reconstruction", vertices))
    values = tuple(min(csum(point, mask) for point in vertices) for mask in range(1 << N))
    if any(values[1 << i] for i in range(N)):
        raise AssertionError("not singleton normalized")
    return vertices, values


def selector_and_spectral_proof(values):
    # Row 59 has worth T and omits only player 2, so every core point has y2=0.
    if values[59] != T:
        raise AssertionError("fixed-zero row")
    # Rows 29 and 30 give y1+y5<=2 and y0+y5<=2.  If every nonfixed
    # coordinate is at least m, then m<=1.  Equality fixes 0,1,5 at one;
    # efficiency leaves y3+y4=5 and the next floor equalizes them.
    if min(X[i] for i in range(N) if i != 2) != 1:
        raise AssertionError("Lmin floor")
    if X[0]+X[5] != 2 or X[1]+X[5] != 2 or X[3]+X[4] != 5:
        raise AssertionError("Lmin pinning")
    # Row 29 contains only three nonfixed coordinates, has value six, and
    # forces the ceiling to at least two.  At ceiling two, rows 29 and 30
    # pin 0,1,3,4; efficiency pins player 5 to zero.
    if max(Z) != 2 or csum(Z, 29) != 6 or csum(Z, 30) != 6:
        raise AssertionError("Lmax pinning")
    for point in (X, Z):
        if sum(point) != T or min(point) < 0:
            raise AssertionError("selector feasibility")
        if any(csum(point, mask) < value for mask, value in ROWS.items()):
            raise AssertionError("selector outside core")

    # The z-tight row 26={1,3,4}, scaled by 1/3, is the top certificate:
    # theta=1/3, eta=0, alpha_1=alpha_3=alpha_4=1/3.
    if values[26] != 6 or csum(Z, 26) != 6:
        raise AssertionError("spectral anchor")
    theta = F(1, 3)
    minimum, maximum = min(X), max(Z)
    surplus = (X[1]+X[3]+X[4])/3 - maximum
    required = (maximum + surplus - minimum) / theta
    candidates = []
    for chosen in itertools.combinations(range(N), 4):
        if sum(X[i]-minimum for i in chosen) < required:
            continue
        candidates.append(sum(min(X[i], maximum) for i in chosen))
    if required != 6 or min(candidates) != 5:
        raise AssertionError("spectral minimum")
    return F(5), F(6)


def primals():
    pi0=tuple(map(F,(F(2,17),F(2,17),0,F(23,68),F(5,17),F(9,68))))
    f0=[[F(0)]*N for _ in range(N)]
    for (r,i),v in {(0,3):F(1,17),(0,4):F(1,34),(0,5):F(1,34),
                    (1,3):F(1,17),(1,4):F(1,34),(1,5):F(1,34),
                    (3,0):F(23,272),(3,1):F(23,272),(3,4):F(23,136),
                    (4,3):F(15,68),(4,5):F(5,68),
                    (5,0):F(9,272),(5,1):F(9,272),(5,4):F(9,136)}.items(): f0[r][i]=v
    ux0=tuple(map(F,(F(16,17),F(16,17),0,F(5,2),F(40,17),1)))
    uz0=tuple(map(F,(F(16,17),F(16,17),0,2,2,0)))
    pi1=tuple(map(F,(F(265,2176),F(265,2176),0,F(3599,10880),F(809,2720),F(279,2176))))
    f1=(tuple(map(F,(F(1,640),F(1,640),0,F(1257,21760),F(1393,43520),F(1257,43520)))),
        tuple(map(F,(F(1,640),F(1,640),0,F(1257,21760),F(1393,43520),F(1257,43520)))),
        (F(0),)*N,
        tuple(map(F,(F(3599,43520),F(3599,43520),0,0,F(3599,21760),0))),
        tuple(map(F,(F(1,256),F(1,256),0,F(1171,5440),F(1,256),F(1533,21760)))),
        tuple(map(F,(F(279,8704),F(279,8704),0,0,F(279,4352),0))))
    ux1=tuple(map(F,(F(265,272),F(265,272),0,F(5,2),F(809,340),1)))
    uz1=tuple(map(F,(F(265,272),F(265,272),0,2,2,0)))
    return (pi0,tuple(map(tuple,f0)),ux0,uz0),(pi1,f1,ux1,uz1)


def replay_primal(values, cert, t):
    pi,flow,ux,uz=cert; diag=tuple(X[i]*Z[i]/T**2 for i in range(N))
    assert sum(pi)==1
    for r in range(N):
        assert min(flow[r])>=0 and sum(flow[r])==pi[r] and flow[r][r]<=t*diag[r]
        for mask in range(1,(1<<N)-1): assert T*csum(flow[r],mask)>=pi[r]*values[mask]
    for i in range(N):
        assert sum(flow[r][i] for r in range(N))==pi[i]
        assert 0<=ux[i]<=min(X[i],T*pi[i]) and 0<=uz[i]<=min(Z[i],T*pi[i])
    return sum(ux)+sum(uz)-T


def replay_dual(values):
    theta=F(104,17);alpha=tuple(map(F,(0,0,1,1,0,1)));beta=tuple(map(F,(0,0,1,1,1,1)))
    p=tuple(map(F,(1,1,0,0,1,0)));q=tuple(map(F,(1,1,0,0,0,0)))
    A=tuple(F(k,17) for k in (176,32,0,288,176,288));B=tuple(F(k,17) for k in (0,0,0,176,144,176))
    lam={(0,11):F(4,17),(0,29):F(22,17),(0,33):F(26,17),(0,59):F(18,17),
         (1,11):F(4,17),(1,26):F(22,17),(1,34):F(26,17),
         (3,30):F(18,17),(3,59):F(18,17),(3,61):F(18,17),
         (4,25):F(22,17),(4,26):F(22,17),(4,48):F(44,17),
         (5,29):F(18,17),(5,30):F(18,17),(5,59):F(18,17)}
    for i in range(N):
        assert alpha[i]+p[i]>=1 and beta[i]+q[i]>=1
        assert theta-A[i]-B[i]+sum(w*values[s] for (r,s),w in lam.items() if r==i)-T*(p[i]+q[i])>=0
    defects=[]
    for r in range(N):
        loads=[]
        for i in range(N):
            load=T*sum(w for (rr,s),w in lam.items() if rr==r and s>>i&1);loads.append(load)
            if i!=r: assert A[r]+B[i]>=load
        defects.append(loads[r]-A[r]-B[r])
    D=theta+sum(alpha[i]*X[i]+beta[i]*Z[i] for i in range(N))
    diag=tuple(X[i]*Z[i]/T**2 for i in range(N));E=sum(diag[i]*max(F(0),defects[i]) for i in range(N))
    return D,tuple(defects),E


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path);args=parser.parse_args()
    vertices,values=reconstruct_game();bstar,actual_top=selector_and_spectral_proof(values)
    p0,p1=primals();psi=replay_primal(values,p0,F(0));released=replay_primal(values,p1,F(1,20))
    D,defects,E=replay_dual(values);target=F(16,3);O=F(6)
    assert bstar==5<target<psi==F(191,34)<O and actual_top==6
    assert D==T+psi and D+E/F(20)==T+released and E==F(54,17)>O-target
    payload={"claim":"standalone exact PXC139 replay","core_vertices":[list(map(str,p)) for p in sorted(vertices)],
             "all_64_values_reconstructed":True,"selectors_proved_by_hand":{"x":list(map(str,X)),"z":list(map(str,Z))},
             "spectral_bound":str(bstar),"actual_top_bound":str(actual_top),"target":str(target),
             "stationary_value":str(psi),"released_t_1_20":str(released),"dual_objective":str(D),
             "minimum_optimal_face_exposure":str(E),"available_overlap_above_target":str(O-target),
             "dual_defects":list(map(str,defects)),"strict_route_refuted":True,
             "main_inequality_survives":str(psi-target)}
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output:args.output.write_text(rendered)
    print(rendered,end="")


if __name__=="__main__":main()
