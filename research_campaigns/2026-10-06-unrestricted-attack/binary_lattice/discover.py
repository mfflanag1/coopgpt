#!/usr/bin/env python3
"""Floating LP discovery on ALL binary-type histograms. Exact checker is separate.
No primal numerical solution proves an all-profile theorem. Saved dual rows may
certify a lower bound even when cutting planes stop early.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as Q
import hashlib,itertools,json,math,time
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def compositions(total, length):
    if length == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for rest in compositions(total-first,length-1):
                yield (first,)+rest


def solve(k,m,high,seconds,max_rounds,strip=False,bmin=0,bmax=None,integer_scale=None):
    started=time.monotonic()
    states=([(a,b,k-a-b)+(0,)*(m-2) for a in range(min(k,2)+1) for b in range(bmin,min(k-a,bmax if bmax is not None else k)+1)] if strip else list(compositions(k,m+1)))
    state_id={s:i for i,s in enumerate(states)}
    ids={};multiplicity={};owner_state={};totals=[];active=[]
    for a,s in enumerate(states):
        hs=[h for h,n in enumerate(s) if n];active.append(hs)
        totals.append(min(m+h*(high-1) for h in hs))
        for h in hs:
            for kind,count in ((0,m-h),(1,h)):
                if count:
                    index=len(ids);ids[a,h,kind]=index
                    multiplicity[index]=s[h]*count;owner_state[index]=a
    B=len(ids);rows=[];descriptions=[];rhs=[];seen=set();budget_indices={}
    def add(coef,value,desc):
        key=json.dumps(desc,separators=(',',':'),sort_keys=True)
        if key in seen:return False
        seen.add(key);rows.append({i:Q(x) for i,x in coef.items() if x});rhs.append(Q(value));descriptions.append(desc)
        return True
    def coalition(a,choices):
        coef={};capacities=[]
        for h,u,v in choices:
            capacities.append(u+high*v)
            if u:coef[ids[a,h,0]]=states[a][h]*u
            if v:coef[ids[a,h,1]]=states[a][h]*v
        return add(coef,min(capacities),{'kind':'cover','state':states[a],'choices':choices})
    for a,s in enumerate(states):
        coef={B:totals[a]}
        for h in active[a]:
            for typ in (0,1):
                if (a,h,typ) in ids:coef[ids[a,h,typ]]=-multiplicity[ids[a,h,typ]]
        budget_indices[a]=len(rows)
        add(coef,0,{'kind':'budget','state':s})
        coalition(a,[(h,m-h,h) for h in active[a]])
        for h in range(m):
            if not s[h]:continue
            dest=list(s);dest[h]-=1;dest[h+1]+=1
            if tuple(dest) not in state_id:continue
            d=state_id[tuple(dest)]
            add({ids[d,h+1,1]:1,ids[a,h,0]:-1},0,{'kind':'mono','state':s,'h':h})
    options={h:[(u,v,u+high*v) for u in range(m-h+1) for v in range(h+1) if u+v] for h in range(m+1)}
    eligible={(h,t):[(u,v) for u,v,cap in options[h] if cap>=t] for h in range(m+1) for t in range(1,m+h*(high-1)+1)}
    trace=[];last=None;last_rows=None;separation_complete=False
    for iteration in range(max_rounds):
        remaining=seconds-(time.monotonic()-started)
        if remaining<=0:break
        rr=[];cc=[];vv=[]
        for r,coef in enumerate(rows):
            for c,x in coef.items():rr.append(r);cc.append(c);vv.append(-float(x))
        matrix=coo_matrix((vv,(rr,cc)),shape=(len(rows),B+1)).tocsr()
        objective=np.zeros(B+1);objective[B]=1
        result=linprog(objective,A_ub=matrix,b_ub=[-float(x) for x in rhs],bounds=(0,None),method='highs',options={'time_limit':max(1,min(remaining,180))})
        if not result.success:
            trace.append({'iteration':iteration,'solver_status':int(result.status),'message':result.message});break
        last=result;last_rows=len(rows);new=0;most_negative=0.;scanned_states=0
        for a,s in enumerate(states):
            for t in range(1,totals[a]+1):
                choices=[];payment=0.
                for h in active[a]:
                    lo=result.x[ids[a,h,0]] if m>h else 0.
                    hi=result.x[ids[a,h,1]] if h else 0.
                    u,v=min(eligible[h,t],key=lambda uv:(uv[0]*lo+uv[1]*hi,uv[0]+high*uv[1],uv))
                    choices.append((h,u,v));payment+=s[h]*(u*lo+v*hi)
                value=min(u+high*v for h,u,v in choices)
                gap=payment-value
                if gap < -1e-8:
                    most_negative=min(most_negative,gap)
                    new+=bool(coalition(a,choices))
            scanned_states+=1
            if time.monotonic()-started>=seconds:break
        item={'iteration':iteration,'factor':float(result.fun),'rows_solved':last_rows,'new_rows':new,'largest_deficit':-most_negative,'seconds':round(time.monotonic()-started,3)}
        trace.append(item);print(json.dumps(item),flush=True)
        if not new:
            separation_complete=(scanned_states==len(states))
            break
    if last is None:
        return {'status':'NO_SOLVED_LP','k':k,'m':m,'high':high,'trace':trace},None
    # Any rounded nonnegative dual can be made exact by extra budget rows.
    weights={r:(Q(round(float(-v)*integer_scale)) if integer_scale else Q(float(-v)).limit_denominator(10**8)) for r,v in enumerate(last.ineqlin.marginals) if -v>1e-10}
    residual=defaultdict(Q);value=Q(0)
    for r,w in weights.items():
        for j,x in rows[r].items():residual[j]+=w*x
        value+=w*rhs[r]
    repairs=defaultdict(Q)
    for j in range(B):
        if residual[j]>0:
            a=owner_state[j];needed=residual[j]/multiplicity[j]
            if integer_scale:needed=Q(math.ceil(needed))
            repairs[a]=max(repairs[a],needed)
    for a,w in repairs.items():
        r=budget_indices[a];weights[r]=weights.get(r,Q(0))+w
        for j,x in rows[r].items():residual[j]+=w*x
    if residual[B]<=0 or any(residual[j]>0 for j in range(B)):
        raise RuntimeError('Exact budget repair failed')
    bound=value/residual[B]
    certificate={'schema':1,'k':k,'m':m,'high':high,'claimed_total_factor':str(bound),
                 'rows':[dict(descriptions[r],weight=str(w)) for r,w in sorted(weights.items()) if w>0]}
    summary={'status':'DISCOVERY_ONLY','k':k,'m':m,'high':high,'states':len(states),'payment_variables':B,
             'state_mode':'strip' if strip else 'all','bmin':bmin,'bmax':bmax,'integer_scale':integer_scale,
             'scipy':scipy.__version__,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'numeric_factor':float(last.fun),'candidate_exact_factor':str(bound),'certificate_rows':len(certificate['rows']),
             'repair_budget_rows':len(repairs),'numerical_separation_complete':separation_complete,'trace':trace,
             'seconds':round(time.monotonic()-started,3),'limitation':'Only separate exact verification can accept the lower certificate. No unrestricted upper follows from a numerical primal.'}
    return summary,certificate

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('k',type=int);parser.add_argument('m',type=int);parser.add_argument('high',type=int)
    parser.add_argument('--strip',action='store_true');parser.add_argument('--bmin',type=int,default=0);parser.add_argument('--bmax',type=int);parser.add_argument('--integer-scale',type=int);parser.add_argument('--seconds',type=int,default=120);parser.add_argument('--rounds',type=int,default=50);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not(args.k>=2 and args.m>=2 and args.high>=2):raise ValueError('k,m,high >=2 required')
    summary,certificate=solve(args.k,args.m,args.high,args.seconds,args.rounds,args.strip,args.bmin,args.bmax,args.integer_scale)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(summary,indent=2)+'\n')
    if certificate:args.output.with_suffix('.certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='trace'}),flush=True)
