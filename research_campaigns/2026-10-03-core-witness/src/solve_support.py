"""Numerical discovery for fixed-P synthesis; only the independent checker accepts."""
import argparse, json, time
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def pairs(t):
    a,b,c=t
    return ((0,a,b),(1,a,c),(2,b,c))


def build(m,P):
    if type(m) is not int or m<1: raise ValueError('m')
    if any(len(t)!=3 or any(type(j) is not int or not 0<=j<m for j in t) for t in P): raise ValueError('P indices')
    if any(len({t[s] for t in P})!=len(P) for s in range(3)): raise ValueError('P overlap')
    edges=sorted({e for t in list(P)+[(j,j,j) for j in range(m)] for e in pairs(t)})
    index={e:k for k,e in enumerate(edges)};off=len(edges);used={s*m+j for t in P for s,j in enumerate(t)}
    U=sorted(set(range(3*m))-used);targets=U or [-1];n=off+len(targets)*3*m
    teams=[(t,[index[e] for e in pairs(t) if e in index]) for t in product(range(m),repeat=3)]
    teams=[(t,es) for t,es in teams if es]
    rr=[];cc=[];vv=[]
    for k in range(len(targets)):
        for tpos,(t,es) in enumerate(teams):
            row=k*len(teams)+tpos
            for j in es: rr.append(row);cc.append(j);vv.append(1)
            for s,j in enumerate(t):rr.append(row);cc.append(off+k*3*m+s*m+j);vv.append(-1)
    A=coo_matrix((vv,(rr,cc)),shape=(len(targets)*len(teams),n)).tocsr()
    er=[];ec=[]
    for s in range(3):
        for j in range(m):er.append(0);ec.append(index[(s,j,j)])
    for k in range(len(targets)):
        for j in range(3*m):er.append(k+1);ec.append(off+k*3*m+j)
    E=coo_matrix((np.ones(len(er)),(er,ec)),shape=(len(targets)+1,n)).tocsr()
    c=np.zeros(n)
    for t in P:
        for e in pairs(t):c[index[e]]+=3
    for k,i in enumerate(targets):
        if i>=0:c[off+k*3*m+i]=1
    return edges,U,targets,teams,A,E,c


def rational_primal(values,A,E,cap):
    vals=[Q(float(v)).limit_denominator(cap) for v in values]
    # Discovery-side filter only. Independent checker rebuilds raw constraints.
    if min(vals)<0 or max(vals)>1: return None
    for row in range(E.shape[0]):
        if sum(vals[j]*int(v) for j,v in zip(E.indices[E.indptr[row]:E.indptr[row+1]],E.data[E.indptr[row]:E.indptr[row+1]])) != 1:return None
    for row in range(A.shape[0]):
        if sum(vals[j]*int(v) for j,v in zip(A.indices[A.indptr[row]:A.indptr[row+1]],A.data[A.indptr[row]:A.indptr[row+1]])) > 0:return None
    return vals


def solve(m,P,seconds=120):
    edges,U,targets,teams,A,E,c=build(m,P);off=len(edges);n=len(c);start=time.monotonic()
    result=linprog(-c,A_ub=A,b_ub=np.zeros(A.shape[0]),A_eq=E,b_eq=np.ones(E.shape[0]),bounds=(0,1),method='highs',options={'time_limit':seconds})
    info={'m':m,'P':P,'variables':n,'cover_rows':A.shape[0],'elapsed_seconds':time.monotonic()-start,'solver_status':result.status,'message':result.message}
    if not result.success:return {'status':'UNRESOLVED','discovery':info}
    info['floating_objective']=-result.fun/3-1
    primal=None
    for cap in (1000,10000,1000000,100000000):
        primal=rational_primal(result.x,A,E,cap)
        if primal is not None:break
    if primal is None:return {'status':'RATIONAL_RECOVERY_FAILED','discovery':info,'raw_primal':result.x.tolist()}
    # Use exact rational approximations to multipliers. Residual correction remains rigorous.
    masses=[max(Q(0),Q(float(-v)).limit_denominator(1000000)) for v in result.ineqlin.marginals]
    nus=[Q(float(-v)).limit_denominator(1000000) for v in result.eqlin.marginals]
    residual=list(map(lambda v:Q(int(v)),c))
    for row,mass in enumerate(masses):
        if mass:
            for pos in range(A.indptr[row],A.indptr[row+1]):residual[A.indices[pos]]-=mass*int(A.data[pos])
    for row,nu in enumerate(nus):
        for pos in range(E.indptr[row],E.indptr[row+1]):residual[E.indices[pos]]-=nu*int(E.data[pos])
    upper=(sum(nus)+sum(max(Q(0),v) for v in residual))/3-1
    matrices=[[['0']*m for _ in range(m)] for _ in range(3)]
    for (s,a,b),v in zip(edges,primal):matrices[s][a][b]=str(v)
    witnesses=[[str(v) for v in primal[off+k*3*m:off+(k+1)*3*m]] for k in range(len(targets))]
    lam=[]
    for row,mass in enumerate(masses):
        if mass:
            k,tpos=divmod(row,len(teams));lam.append([targets[k],*teams[tpos][0],str(mass)])
    J=sum(Q(int(v))*x for v,x in zip(c,primal))/3-1
    return {'schema':'core-witness-v1','m':m,'P':[list(t) for t in P],'unmatched':U,'support':[list(e) for e in edges],'matrices':matrices,'witness_targets':targets,'witnesses':witnesses,'primal_J':str(J),'dual':{'lambda':lam,'normalization':str(nus[0]),'totals':list(map(str,nus[1:])),'upper':str(upper)},'discovery':info,'acceptance':'UNVERIFIED until independent checker passes'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('output');ap.add_argument('--seconds',type=int,default=120);args=ap.parse_args()
    data=json.loads(Path(args.input).read_text());out=solve(data['m'],data['P'],args.seconds);Path(args.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out.get('status','CANDIDATE'),'primal_J':out.get('primal_J'),'upper':out.get('dual',{}).get('upper'),'discovery':out['discovery']}))
if __name__=='__main__':main()
