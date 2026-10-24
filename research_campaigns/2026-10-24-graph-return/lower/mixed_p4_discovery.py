#!/usr/bin/env python3
"""Predetermined mixed-owner P4 diagrams; floating discovery, rational export.

Only the independently reconstructed Fraction certificate is proof evidence.
No prices, payment symmetry, homogeneity, or marginal floors are imposed.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse, json, time
import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = Path(__file__).resolve().parent
N = 4
P = 256
KCOL = N * P


def value(x):
    return min(x[0] + x[2], x[1] + x[3], x[1] + x[2])


def reports(R):
    out = []
    for p in range(P):
        row = []
        for i in range(N):
            b = [0] * 4
            if p & (1 << (2*i)): b[i] = R
            if p & (1 << (2*i+1)): b[(i+1) % 4] = 1
            row.append(tuple(b))
        out.append(row)
    return out


def data(R):
    b = reports(R)
    def cap(p, S):
        return tuple(sum(b[p][i][v] for i in range(N) if S >> i & 1) for v in range(4))
    rows, rhs, tags = [], [], []
    def add(row, right, tag):
        rows.append({k: F(v) for k,v in row.items() if v})
        rhs.append(F(right)); tags.append(tag)
    for p in range(P):
        add({**{4*p+i: 1 for i in range(N)}, KCOL: -value(cap(p,15))}, 0, ['budget',p])
        for S in range(1,16):
            add({4*p+i: -1 for i in range(N) if S >> i & 1}, -value(cap(p,S)), ['cover',p,S])
    # All comparable profile pairs and ALL eligible supersets of changed owners.
    for low in range(P):
        free = 255 ^ low
        bits = free
        while bits:
            high = low | bits
            changed = sum(1 << i for i in range(N) if bits & (3 << (2*i)))
            delta = tuple(sum(b[high][i][v]-b[low][i][v] for i in range(N)) for v in range(4))
            for S in range(1,16):
                if S & changed != changed: continue
                row = {}
                for i in range(N):
                    if S >> i & 1:
                        row[4*low+i] = 1
                        row[4*high+i] = -1
                add(row, -value(delta), ['out',low,high,S])
            bits = (bits - 1) & free
    return b, rows, rhs, tags


def row_digest(row, rhs, tag):
    payload = [tag, [[k,str(v)] for k,v in sorted(row.items())], str(rhs)]
    return sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest()


def solve(R, limit):
    t0=time.monotonic()
    b, rows, rhs, tags = data(R)
    rr=[];cc=[];vv=[]
    for j,row in enumerate(rows):
        for c,v in row.items():rr.append(j);cc.append(c);vv.append(float(v))
    A=coo_matrix((vv,(rr,cc)),shape=(len(rows),KCOL+1)).tocsr()
    objective=np.zeros(KCOL+1);objective[-1]=1
    ans=linprog(objective,A_ub=A,b_ub=np.array(list(map(float,rhs))),
                bounds=(0,None),method='highs-ds',
                options={'presolve':False,'time_limit':limit})
    result={'R':R,'profiles':P,'owners':N,'resources':4,'variables':KCOL+1,
            'rows':len(rows),'row_types':dict(Counter(x[0] for x in tags)),
            'status':int(ans.status),'message':ans.message,
            'elapsed_seconds':time.monotonic()-t0,
            'scipy':scipy.__version__,'numpy':np.__version__,
            'solver_is_discovery_only':True}
    if ans.success:
        result['float_optimum']=float(ans.fun)
        rat=lambda x:F(float(x)).limit_denominator(10**9)
        primal=list(map(rat,ans.x))
        weights=[rat(max(0,-v)) for v in ans.ineqlin.marginals]
        combo=defaultdict(F); right=F(0)
        for row,r,w in zip(rows,rhs,weights):
            if not w:continue
            for c,v in row.items():combo[c]+=w*v
            right+=w*r
        repairs=[]
        for p in range(P):
            w=max(F(0),max(-combo[4*p+i] for i in range(N)))
            if w:
                weights[16*p]+=w
                for c,v in rows[16*p].items():combo[c]+=w*v
                repairs.append([p,str(w)])
        assert combo[KCOL]<0 and all(v>=0 for c,v in combo.items() if c!=KCOL)
        lower=right/combo[KCOL]
        primal_ok=min(primal)>=0 and all(sum(v*primal[c] for c,v in row.items())<=r for row,r in zip(rows,rhs))
        result.update(exact_lower=str(lower),exact_primal_feasible=primal_ok,
                      rational_primal_objective=str(primal[-1]),
                      exact_optimum=primal_ok and lower==primal[-1],
                      certificate_support=sum(bool(w) for w in weights),
                      budget_repairs=repairs)
        packet={'family':'four-cyclic-mixed-owners-binary-independent-coordinates',
                'R':R,'owner_full_bundles':b[-1],
                'profiles':list(range(P)), 'payment_variable_count':KCOL,
                'row_types':result['row_types'],
                'semantic_row_digest':sha256(''.join(sorted(row_digest(a,r,t) for a,r,t in zip(rows,rhs,tags))).encode()).hexdigest(),
                'certificate':[{'tag':t,'weight':str(w)} for t,w in zip(tags,weights) if w],
                'primal':list(map(str,primal)),
                'exact_lower':str(lower),'budget_repairs':repairs,
                'result':result}
        (HERE/f'cyclic_R{R}_certificate.json').write_text(json.dumps(packet,indent=2)+'\n')
    (HERE/f'cyclic_R{R}_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--R',type=int,nargs='+',default=[1,2,4,16])
    parser.add_argument('--seconds',type=int,default=120)
    args=parser.parse_args()
    for R in args.R: solve(R,args.seconds)
