#!/usr/bin/env python3
"""Independent exact audit of the PXC121 zero-demand closures."""
from __future__ import annotations

import json
import argparse
from pathlib import Path
from fractions import Fraction as F
import z3


def q(value: F):
    return z3.Q(value.numerator, value.denominator)


def target(n):
    return F(n, (n*n)//4)


def common_unsat(k, branch):
    M, Q, J, K = z3.Reals(f"M_{k}_{branch} Q_{k}_{branch} J_{k}_{branch} K_{k}_{branch}")
    T = 2*M + 2*Q + J + (k-1)*K
    u = (Q+J+(k-1)*K)/(k+1)
    p = (T-(k+2)*u)/2
    mu = u if branch == "u" else J
    B = 2*M + 2*u + mu + (k-1)*K
    s=z3.Solver()
    s.add(T==1, M>=Q, Q>=J, J>=K, K>=0)
    s.add(Q+(k-1)*K>=M)
    s.add((k+2)*Q+(k-1)*K >= (2*k+1)*J)
    s.add(p>=M)
    s.add(u<=J if branch=="u" else J<=u)
    s.add(B < q(target(k+4)))
    return str(s.check())


def reciprocal_unsat(m):
    A=z3.Real(f"A_{m}")
    u=(A+m)/(m+1)
    T=16+A+m
    B=12+2*u+m
    s=z3.Solver()
    s.add(A>=4,A<=6)
    s.add(B < q(target(m+4))*T)
    return str(s.check())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    common=[]
    for k in range(2,129):
        for branch in ("u","J"):
            status=common_unsat(k,branch)
            assert status=="unsat",(k,branch,status)
            common.append((k,branch,status))
    reciprocal=[]
    for m in range(2,129):
        status=reciprocal_unsat(m)
        assert status=="unsat",(m,status)
        reciprocal.append((m,status))
    payload={
      "claim":"independent exact-LRA audit of PXC101/PXC106 spectral closure",
      "z3_version":z3.get_version_string(),
      "common_cells":len(common),
      "common_k_range":[2,128],
      "reciprocal_cells":len(reciprocal),
      "reciprocal_m_range":[2,128],
      "all_status":"unsat",
      "scope":"finite exact audit of the conventional all-k inequalities; not the dimension-free proof and not PXC120",
    }
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered,end="")


if __name__=="__main__":main()
