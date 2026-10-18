"""Bounded pure-unit relaxation with an explicitly verified resource group.

Numerical discovery only. Unlike the first probe, this file does not claim an
exact lower unless its quotient certificate is independently replayed. The
unsymmetrized checker does not apply to this output.
"""
from fractions import Fraction as Q
from itertools import permutations,product
from pathlib import Path
import argparse,json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from pure_unit_transition_probe import case,production,need

def automorphisms(d,edges):
    E={tuple(sorted(e)) for e in edges}
    return [g for g in permutations(range(d)) if {tuple(sorted(g[j] for j in e)) for e in E}==E]

def permute(a,g):
    b=[0]*len(a)
    for j,v in enumerate(a):b[g[j]]=v
    return tuple(b)

def solve(label,edges,L,s,seconds):
    start=time.monotonic();d=1+max(map(max,edges));n=d*L+1;G=automorphisms(d,edges)
    visited=set();reps=[]
    for a in product(range(L+1),repeat=d):
        if a in visited:continue
        reps.append(a);visited.update(permute(a,g) for g in G)
    del visited
    keyids={};mapping={};profiles=[];profileids={}
    def qmap(a):
        if a in mapping:return mapping[a]
        images=[permute(a,g) for g in G];canon=min(images)
        gs=[g for g,ag in zip(G,images) if ag==canon]
        keys=[(canon,min(g[j] for g in gs)) for j in range(d)]+[(canon,d)]
        ix=[]
        for key in keys:
            if key not in keyids:keyids[key]=len(keyids)
            ix.append(keyids[key])
        mapping[a]=ix
        if a not in profileids:profileids[a]=len(profiles);profiles.append(a)
        return ix
    for a in reps:qmap(a)
    transitions=[]
    for a in reps:
        for i in range(d):
            if a[i]<L:
                b=list(a);b[i]+=1;b=tuple(b);qmap(b);transitions.append((a,b,i))
    K=len(keyids);N=K+1;records=[];coeff=[];rhs=[];seen=set();oracles={}
    def add(c,b,tag):
        key=json.dumps(tag)
        if key in seen:return False
        seen.add(key);records.append(tag);coeff.append(c);rhs.append(b);return True
    def merge(pairs):
        c={}
        for j,v in pairs:c[j]=c.get(j,Q(0))+v
        return {j:v for j,v in c.items() if v}
    for a in reps:
        v,x,p=production(a,edges);oracles[a]=(v,x,p);q=qmap(a);pid=profileids[a]
        c=merge([(q[j],Q(t)) for j,t in enumerate(list(a)+[n-sum(a)])]);c[K]=-v
        add(c,Q(0),['budget',pid])
        for e in edges:
            if all(a[j] for j in e):add(merge([(q[j],Q(-1)) for j in e]),Q(-1),['coverage',pid,list(e)])
    for a,b,i in transitions:
        q,r=qmap(a),qmap(b)
        add(merge([(q[d],Q(1)),(r[i],Q(-1))]),Q(0),['tcwm',profileids[a],profileids[b],i,[0]*(d+1)])
    hist=[];solution=None
    for it in range(60):
        remain=seconds-(time.monotonic()-start)
        if remain<=0:break
        rr=[];cc=[];dd=[]
        for row,c in enumerate(coeff):
            for j,v in c.items():rr.append(row);cc.append(j);dd.append(float(v))
        A=coo_matrix((dd,(rr,cc)),shape=(len(rhs),N)).tocsr();obj=np.zeros(N);obj[K]=1
        z=linprog(obj,A_ub=A,b_ub=list(map(float,rhs)),bounds=(0,None),method='highs',options={'time_limit':remain})
        if not z.success:hist.append({'iteration':it,'success':False,'message':z.message});break
        solution=z;added=0;maxv=0.
        for a,b,i in transitions:
            q,r=qmap(a),qmap(b);loss=[z.x[q[j]]-z.x[r[j]] for j in range(d+1)]
            mult=list(a)+[n-sum(a)-1];count=[0]*(d+1);remaining=s-1
            for j in sorted(range(d+1),key=lambda j:loss[j],reverse=True):
                if loss[j]<=0 or remaining<=0:break
                count[j]=min(remaining,mult[j]);remaining-=count[j]
            violation=z.x[q[d]]-z.x[r[i]]+sum(c*l for c,l in zip(count,loss));maxv=max(maxv,violation)
            if violation>1e-8:
                pairs=[(q[d],Q(1)),(r[i],Q(-1))]
                for j,t in enumerate(count):pairs.extend([(q[j],Q(t)),(r[j],Q(-t))])
                added+=add(merge(pairs),Q(0),['tcwm',profileids[a],profileids[b],i,count])
        h={'iteration':it,'factor':float(z.fun),'cuts':added,'max_violation':maxv,'elapsed':time.monotonic()-start};hist.append(h);print(json.dumps({'name':label,**h}),flush=True)
        if not added:break
    info={'name':label,'d':d,'n':n,'s':s,'levels':L,'resource_group_order':len(G),'representative_count':len(reps),'variables':N,'history':hist,'elapsed':time.monotonic()-start,'scope':'numerical finite symmetric relaxation, no upper theorem'}
    if solution is not None:
        z=solution;info['float_lower_candidate']=float(z.fun)
        cert=[];combo={};right=Q(0)
        for j,v in enumerate(z.ineqlin.marginals):
            if v>=-1e-9:continue
            m=Q(round(-float(v)*10**9),10**9)
            if not m:continue
            cert.append({'multiplier':str(m),'row':records[j]})
            for t,c in coeff[j].items():combo[t]=combo.get(t,Q(0))+m*c
            right+=m*rhs[j]
        # Each price variable belongs to exactly one representative profile;
        # its budget coefficient is the number of actual owners in its orbit.
        for a in reps:
            q=qmap(a);c=merge([(q[j],Q(t)) for j,t in enumerate(list(a)+[n-sum(a)])])
            m=max([Q(0)]+[-combo.get(j,Q(0))/count for j,count in c.items() if count])
            if m>0:
                for j,count in c.items():combo[j]=combo.get(j,Q(0))+m*count
                combo[K]=combo.get(K,Q(0))-m*oracles[a][0]
                cert.append({'multiplier':str(m),'row':['budget',profileids[a]]})
        good=combo.get(K,Q(0))<0 and all(v>=0 for j,v in combo.items() if j!=K)
        info.update(exact_combo_valid=good,exact_lower=str(right/combo[K]) if good else None,certificate_rows=len(cert))
        out={**info,'edges':edges,'automorphisms':G,'profiles':profiles,'qmap':[mapping[a] for a in profiles],
             'factor_index':K,'representatives':[profileids[a] for a in reps],
             'oracles':{str(profileids[a]):{'value':str(v),'primal':list(map(str,x)),'dual':list(map(str,p))} for a,(v,x,p) in oracles.items()},
             'certificate':cert,'combo_nonzero':{str(j):str(v) for j,v in combo.items() if v},'rhs':str(right)}
        Path(__file__).with_name(label+'.json').write_text(json.dumps(out,indent=2)+'\n')
    return info

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('case');ap.add_argument('--levels',type=int,default=4);ap.add_argument('--s',type=int,default=24);ap.add_argument('--seconds',type=int,default=120);args=ap.parse_args()
    name=f'sym_{args.case}_L{args.levels}_S{args.s}'
    print(json.dumps(solve(name,case(args.case),args.levels,args.s,args.seconds)),flush=True)
