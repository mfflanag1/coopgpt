#!/usr/bin/env python3
"""Independent exact replay of the PXC140 saturation factor.

This script imports no project Python module.  It composes the already
standalone PXC138/PXC139 artifacts, reconstructs the PXC139 lower envelope
from its four vertices, and independently verifies the new saturation primal
and its positive-left-slope supporting dual.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
DIV = HERE.parent
N, T = 6, F(8)
X = (F(1), F(1), F(0), F(5, 2), F(5, 2), F(1))
Z = (F(2), F(2), F(0), F(2), F(2), F(0))
VERTICES = (
    tuple(map(F, (0, 0, 0, 4, 2, 2))), tuple(map(F, (0, 0, 0, 6, 0, 2))),
    tuple(map(F, (2, 2, 0, 0, 4, 0))), tuple(map(F, (2, 2, 0, 2, 2, 0))),
)


def csum(point, mask):
    return sum(point[i] for i in range(N) if mask >> i & 1)


def values():
    return tuple(min(csum(point, mask) for point in VERTICES) for mask in range(1 << N))


def saturation_primal(v, tau):
    pi=tuple(map(F,(F(19,144),F(19,144),0,F(5,16),F(11,36),F(17,144))))
    flow=(tuple(map(F,(F(7,1296),F(7,1296),0,F(143,2592),F(199,5184),F(143,5184)))),
          tuple(map(F,(F(7,1296),F(7,1296),0,F(143,2592),F(199,5184),F(143,5184)))),
          (F(0),)*N,tuple(map(F,(F(5,64),F(5,64),0,0,F(5,32),0))),
          tuple(map(F,(F(35,2592),F(35,2592),0,F(131,648),F(35,2592),F(163,2592)))),
          tuple(map(F,(F(17,576),F(17,576),0,0,F(17,288),0))))
    ux=tuple(map(F,(1,1,0,F(5,2),F(22,9),F(17,18))))
    uz=tuple(map(F,(F(19,18),F(19,18),0,2,2,0)))
    diag=tuple(X[i]*Z[i]/T**2 for i in range(N));assert sum(pi)==1
    for r in range(N):
        assert min(flow[r])>=0 and sum(flow[r])==pi[r] and flow[r][r]<=tau*diag[r]
        for mask in range(1,(1<<N)-1):assert T*csum(flow[r],mask)>=pi[r]*v[mask]
    for i in range(N):
        assert sum(flow[r][i] for r in range(N))==pi[i]
        assert 0<=ux[i]<=min(X[i],T*pi[i]) and 0<=uz[i]<=min(Z[i],T*pi[i])
    return sum(ux)+sum(uz)-T


def left_dual(v):
    theta=F(90,17);alpha=tuple(map(F,(1,1,1,1,0,0)));beta=tuple(map(F,(0,0,1,1,1,1)))
    p=tuple(map(F,(0,0,0,0,1,1)));q=tuple(map(F,(1,1,0,0,0,0)))
    A=tuple(F(k,17) for k in (100,80,36,148,100,0));B=tuple(F(k,17) for k in (0,0,0,100,20,-36))
    lam={(0,11):F(10,17),(0,29):F(25,34),(0,33):F(11,34),(0,59):F(5,34),
         (1,15):F(10,17),(1,26):F(25,34),(1,34):F(11,34),
         (2,8):F(10,17),(2,24):F(5,34),(2,31):F(9,34),
         (3,15):F(9,34),(3,30):F(7,17),(3,59):F(7,17),(3,61):F(7,17),
         (4,25):F(25,34),(4,26):F(25,34),(4,48):F(8,17),(5,56):F(5,34)}
    for i in range(N):
        assert alpha[i]+p[i]>=1 and beta[i]+q[i]>=1
        assert theta-A[i]-B[i]+sum(w*v[s] for (r,s),w in lam.items() if r==i)-T*(p[i]+q[i])>=0
    defects=[]
    for r in range(N):
        loads=[]
        for i in range(N):
            load=T*sum(w for (rr,s),w in lam.items() if rr==r and s>>i&1);loads.append(load)
            if i!=r:assert A[r]+B[i]>=load
        defects.append(loads[r]-A[r]-B[r])
    D=theta+sum(alpha[i]*X[i]+beta[i]*Z[i] for i in range(N))
    diag=tuple(X[i]*Z[i]/T**2 for i in range(N));E=sum(diag[i]*max(F(0),defects[i]) for i in range(N))
    return D,E,tuple(defects)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path);args=parser.parse_args()
    p138=json.loads((DIV/'pxc138_diagonal_release_curve_independent.json').read_text())
    p139=json.loads((DIV/'pxc139_strict_spectral_single_dual_no_go_independent.json').read_text())
    sharp_tau=F(p138['breakpoint']);sharp_e0=F(p138['dual_exposure']);sharp_price=F(1,51)
    assert sharp_tau*sharp_e0==sharp_price
    tau=F(14,81);v=values();O=saturation_primal(v,tau);Dleft,Eleft,defects=left_dual(v)
    assert O==6 and Dleft+tau*Eleft==T+O and Eleft==F(81,68)>0
    e0=F(p139['minimum_optimal_face_exposure']);price=F(13,34);available=F(p139['available_overlap_above_target'])
    product=tau*e0
    assert price<=product==F(28,51)<available==F(2,3)
    payload={"claim":"independent PXC140 slope-times-saturation replay",
             "sharp":{"tau":str(sharp_tau),"e0":str(sharp_e0),"product":str(sharp_price)},
             "pxc139":{"tau":str(tau),"left_slope":str(Eleft),"left_defects":list(map(str,defects)),
                       "e0":str(e0),"tau_times_e0":str(product),"true_price":str(price),
                       "available":str(available)},
             "scope":"standalone exact saturation certificates plus independently pinned upstream e0 values; general inequality is the concavity proof"}
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output:args.output.write_text(rendered)
    print(rendered,end="")


if __name__=="__main__":main()
