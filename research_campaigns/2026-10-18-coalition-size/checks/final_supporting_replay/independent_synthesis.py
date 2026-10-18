#!/usr/bin/env python3
"""Independent exact fixed-partition LP audit; imports no author implementation.

Numerical optimization supplies candidates only. Every feasible optimum is
checked against rational primal and dual certificates with exact equality.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np
from scipy.optimize import linprog


class LP:
    def __init__(self):
        self.names=[]; self.ub=[]; self.rhs=[]; self.eq=[]; self.erhs=[]

    def variable(self, name, nonnegative=False):
        k=len(self.names); self.names.append(name)
        if nonnegative:
            self.le({k:-1},0)
        return k

    def le(self, row, rhs):
        self.ub.append({k:Q(v) for k,v in row.items() if v});self.rhs.append(Q(rhs))

    def equal(self, row, rhs=0):
        self.eq.append({k:Q(v) for k,v in row.items() if v});self.erhs.append(Q(rhs))

    def optimize(self, objective):
        def matrix(rows):
            return np.array([[float(row.get(k,0)) for k in range(len(self.names))]
                             for row in rows],dtype=float)
        c=[Q(objective.get(k,0)) for k in range(len(self.names))]
        result=linprog(np.array(c,dtype=float), A_ub=matrix(self.ub),
                       b_ub=np.array(self.rhs,dtype=float), A_eq=matrix(self.eq),
                       b_eq=np.array(self.erhs,dtype=float),
                       bounds=[(None,None)]*len(self.names),method='highs')
        assert result.success, result.message
        rational=lambda x:Q(float(x)).limit_denominator(1000000)
        x=list(map(rational,result.x))
        lam=list(map(rational,result.ineqlin.marginals))
        nu=list(map(rational,result.eqlin.marginals))
        assert all(v<=0 for v in lam)
        value=lambda row:sum(v*x[k] for k,v in row.items())
        assert all(value(row)<=rhs for row,rhs in zip(self.ub,self.rhs))
        assert all(value(row)==rhs for row,rhs in zip(self.eq,self.erhs))
        for k in range(len(self.names)):
            assert sum(lam[j]*row.get(k,0) for j,row in enumerate(self.ub)) + \
                   sum(nu[j]*row.get(k,0) for j,row in enumerate(self.eq)) == c[k]
        primal=sum(v*z for v,z in zip(c,x))
        dual=sum(v*z for v,z in zip(lam,self.rhs))+sum(v*z for v,z in zip(nu,self.erhs))
        assert primal==dual
        sparse=lambda vals:{str(i):str(v) for i,v in enumerate(vals) if v}
        return {'optimum':str(primal),'variables':len(x),'inequalities':len(self.ub),
                'equalities':len(self.eq),'primal':sparse(x),
                'inequality_dual':sparse(lam),'equality_dual':sparse(nu),
                'variable_names':self.names},x


def add(row, k, value):
    row[k]=row.get(k,0)+value


def synthesize(n, active, pure, s):
    coordinates=[(0,0),(1,1)] if pure else [(i,a) for i in range(active) for a in (0,1)]
    m=len(coordinates)
    normal=[1 if a==0 else -1 for i,a in coordinates]
    cubes=list(product((0,1),repeat=m))
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    cells=[]
    for sign in (1,-1):
        H=[];g=[]
        for j in range(m):
            row=[0]*m;row[j]=1;H.append(row);g.append(1)
            row=[0]*m;row[j]=-1;H.append(row);g.append(0)
        H.append([sign*a for a in normal]);g.append(0)
        # Cutting a unit cube by this integer +/-1 form introduces no new
        # vertices in cube edges: a strict sign change cannot occur within
        # an edge whose endpoint values are consecutive integers.
        vertices=[b for b in cubes if sign*dot(normal,b)<=0]
        assert vertices
        cells.append((H,g,vertices))
    tie=[b for b in cubes if dot(normal,b)==0]
    coalitions=[C for size in range(1,n+1) for C in combinations(range(n),size)]
    lp=LP()
    payment={}
    for t in range(2):
        for i in range(n):
            for j in range(m+1):
                payment[t,i,j]=lp.variable(f'a[{t},{i},{j}]')
    K=lp.variable('K',nonnegative=True)
    for v in tie:
        for i in range(n):
            row={}
            for j,bj in enumerate(v+(1,)):
                add(row,payment[0,i,j],bj);add(row,payment[1,i,j],-bj)
            lp.equal(row)
    for t,(H,g,vertices) in enumerate(cells):
        for v in vertices:
            for i in range(n):
                lp.le({payment[t,i,j]:-bj for j,bj in enumerate(v+(1,))},0)
            capacity=[sum(v[j] for j,(i,a) in enumerate(coordinates) if a==resource)
                      for resource in (0,1)]
            row={K:-min(capacity)}
            for i in range(n):
                for j,bj in enumerate(v+(1,)):
                    add(row,payment[t,i,j],bj)
            lp.le(row,0)
        for C in coalitions:
            u=[lp.variable(f'u[{t},{C},{h}]',True) for h in range(len(H))]
            p=[lp.variable(f'p[{t},{C},{a}]',True) for a in (0,1)]
            for j,(owner,resource) in enumerate(coordinates):
                row={u[h]:H[h][j] for h in range(len(H))}
                if owner in C:add(row,p[resource],-1)
                for i in C:add(row,payment[t,i,j],1)
                lp.equal(row)
            lp.le({p[0]:-1,p[1]:-1},-1)
            row={u[h]:g[h] for h in range(len(H))}
            for i in C:add(row,payment[t,i,m],-1)
            lp.le(row,0)
            if len(C)>s:continue
            # Deliberate full coalition expansion, rather than sorting.
            for j,(owner,resource) in enumerate(coordinates):
                if owner in C:
                    lp.le({payment[t,i,j]:-1 for i in C},0)
            for j,(owner0,a0) in enumerate(coordinates):
                if a0!=0 or owner0 not in C:continue
                for k,(owner1,a1) in enumerate(coordinates):
                    if a1!=1 or owner1 not in C:continue
                    row={}
                    for i in C:
                        add(row,payment[t,i,j],-1);add(row,payment[t,i,k],-1)
                    lp.le(row,-1)
    result,x=lp.optimize({K:1})
    expected=Q(1 if pure else active)
    assert Q(result['optimum'])==expected
    result.update({'owners':n,'active_owners':active,'pure':pure,'s':s,
                   'expected_optimum':str(expected),'cell_vertex_counts':[len(c[2]) for c in cells],
                   'coverage_dual_blocks':2*len(coalitions),
                   'coordinates':coordinates,'funding_factor':str(x[K]),
                   'payments':[[[str(x[payment[t,i,j]]) for j in range(m+1)]
                                for i in range(n)] for t in range(2)]})
    return result


def coarse_partition_farkas():
    # Variables (total b1 coefficient, total b2 coefficient, total intercept).
    # Funding at (1,0),(0,1), nonnegativity at origin, coverage at (1,1).
    rows=[(1,0,1),(0,1,1),(0,0,-1),(-1,-1,-1)]
    rhs=[0,0,0,-1]
    assert all(sum(row[j] for row in rows)==0 for j in range(3))
    assert sum(rhs)==-1
    return {'status':'INFEASIBLE','variables':['A1','A2','H'],
            'rows':rows,'rhs':rhs,'nonnegative_multipliers':[1,1,1,1],
            'sum':'0 <= -1',
            'scope':'One affine cell for two pure owners and F=min(b1,b2), at every finite K.'}


def main():
    runs=[]
    for n,active,pure,s in [(2,2,True,1),(2,2,True,2),
                            (2,2,False,1),(2,2,False,2),
                            (3,3,False,1),(3,3,False,3),
                            (3,2,False,3)]:
        runs.append(synthesize(n,active,pure,s))
    out={'status':'PASS','timestamp_utc':datetime.now(timezone.utc).isoformat(),
         'scope':'Independent exact fixed-partition synthesis; no completeness or funding improvement.',
         'synthesis_runs':runs,'coarse_partition_farkas':coarse_partition_farkas(),
         'exact_optimality_certificates':len(runs),
         'coverage_dual_blocks_checked':sum(r['coverage_dual_blocks'] for r in runs)}
    path=Path(__file__).with_suffix('.json')
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'PASS','optima':[r['optimum'] for r in runs],
                      'coverage_dual_blocks_checked':out['coverage_dual_blocks_checked'],
                      'output':str(path)}))


if __name__=='__main__':main()
