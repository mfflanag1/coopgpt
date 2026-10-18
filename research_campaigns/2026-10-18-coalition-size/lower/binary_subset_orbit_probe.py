"""Bounded multi-orbit arbitrary-payment scout on all binary PG(3,2) profiles.

All16 fully eligible owners are fixed; counts0/1 on15 resource rows, with a
free nonnegative common zero-owner payment. The full GL action is generated
explicitly and orbit equivalence is computed by finite generator closure.
Finite numerical discovery only unless its rational certificate is replayed.
"""
from collections import deque
from fractions import Fraction as F
from pathlib import Path
import argparse, json, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from pure_unit_transition_probe import production


def geometry(bits):
    d = (1 << bits) - 1
    edges = [(a-1, b-1, (a ^ b)-1) for a in range(1, d+1)
             for b in range(a+1, d+1) if b < (a ^ b)]
    generator_images = []
    for j in range(bits-1):
        images = [1 << t for t in range(bits)]
        images[j], images[j+1] = images[j+1], images[j]
        generator_images.append(images)
    images = [1 << t for t in range(bits)]
    images[0] ^= 2
    generator_images.append(images)
    generators = []
    for images in generator_images:
        g = []
        for x in range(1, d+1):
            y = 0
            for t, image in enumerate(images):
                if x & (1 << t):
                    y ^= image
            g.append(y-1)
        assert sorted(g) == list(range(d))
        assert {tuple(sorted(g[j] for j in e)) for e in edges} == set(edges)
        generators.append(g)
    return d, edges, generators


def orbits(bits):
    d, edges, generators = geometry(bits)
    states = 1 << d
    maskmaps = []
    for g in generators:
        pm = np.zeros(states, dtype=np.int32)
        for mask in range(1, states):
            low = mask & -mask
            pm[mask] = int(pm[mask ^ low]) | (1 << g[low.bit_length()-1])
        maskmaps.append(pm)
    profile_ids = np.full(states, -1, dtype=np.int32)
    profile_reps = []
    for root in range(states):
        if profile_ids[root] >= 0:
            continue
        oid = len(profile_reps)
        profile_reps.append(root)
        todo = deque([root]); profile_ids[root] = oid
        while todo:
            mask = todo.popleft()
            for pm in maskmaps:
                nxt = int(pm[mask])
                if profile_ids[nxt] < 0:
                    profile_ids[nxt] = oid; todo.append(nxt)
    pair_ids = np.full(states*d, -1, dtype=np.int32)
    payment_ids, payment_reps, transitions = {}, [], []
    orbit_count = 0
    for root in range(states*d):
        if pair_ids[root] >= 0:
            continue
        mask, point = divmod(root, d)
        oid = orbit_count; orbit_count += 1
        if mask & (1 << point):
            payment_ids[oid] = len(payment_reps)
            payment_reps.append((mask, point))
        else:
            transitions.append((mask, point))
        todo = deque([root]); pair_ids[root] = oid
        while todo:
            pair = todo.popleft(); a, j = divmod(pair, d)
            for g, pm in zip(generators, maskmaps):
                nxt = int(pm[a])*d + g[j]
                if pair_ids[nxt] < 0:
                    pair_ids[nxt] = oid; todo.append(nxt)
    basezero = len(payment_reps)
    def qmap(mask):
        return [payment_ids[int(pair_ids[mask*d+j])] if mask & (1 << j) else -1
                for j in range(d)] + [basezero + int(profile_ids[mask])]
    return d, edges, generators, profile_reps, transitions, qmap, basezero+len(profile_reps)


def solve(bits, s, seconds):
    start = time.monotonic()
    d, edges, gens, reps, transitions, qmap, K = orbits(bits)
    n = d+1; N = K+1
    print(json.dumps({"stage": "orbits", "profiles": len(reps),
                      "transitions": len(transitions), "variables": N,
                      "elapsed": time.monotonic()-start}), flush=True)
    records, coefficients, rhs, seen, oracles = [], [], [], set(), {}
    def merge(pairs):
        c = {}
        for var, val in pairs:
            if val:
                assert var >= 0
                c[var] = c.get(var,F(0)) + val
        return {j:v for j,v in c.items() if v}
    def add(c, b, tag):
        key = json.dumps(tag)
        if key in seen:
            return False
        seen.add(key); records.append(tag); coefficients.append(c); rhs.append(b)
        return True
    for mask in reps:
        a = [(mask >> j)&1 for j in range(d)]
        value, primal, dual = production(a, edges)
        oracles[mask] = (value, primal, dual)
        q = qmap(mask)
        c = merge([(q[j],F(a[j])) for j in range(d)] + [(q[d],F(n-mask.bit_count()))])
        c[K] = -value
        add(c,F(0),["budget",mask])
        for e in edges:
            if all(a[j] for j in e):
                add(merge([(q[j],F(-1)) for j in e]),F(-1),["coverage",mask,list(e)])
    for mask, i in transitions:
        new = mask | (1 << i); q, r = qmap(mask), qmap(new)
        add(merge([(q[d],F(1)),(r[i],F(-1))]),F(0),["tcwm",mask,new,i,[0]*(d+1)])
    history, solution = [], None
    for iteration in range(100):
        remaining = seconds-(time.monotonic()-start)
        if remaining <= 0:
            break
        rr,cc,vv = [],[],[]
        for row,c in enumerate(coefficients):
            for col,value in c.items():
                rr.append(row); cc.append(col); vv.append(float(value))
        A=coo_matrix((vv,(rr,cc)),shape=(len(rhs),N)).tocsr()
        obj=np.zeros(N); obj[K]=1
        z=linprog(obj,A_ub=A,b_ub=list(map(float,rhs)),bounds=(0,None),method="highs",
                  options={"time_limit":remaining})
        if not z.success:
            history.append({"iteration":iteration,"message":z.message}); break
        solution=z; cuts=0; maximum=0
        for mask,i in transitions:
            new=mask|(1<<i);q,r=qmap(mask),qmap(new)
            losses=[(z.x[q[j]]-z.x[r[j]],j,1) for j in range(d) if mask&(1<<j)]
            losses.append((z.x[q[d]]-z.x[r[d]],d,n-mask.bit_count()-1))
            count=[0]*(d+1); slots=s-1
            for loss,j,multiplicity in sorted(losses,reverse=True):
                if slots<=0 or loss<=0:
                    break
                count[j]=min(slots,multiplicity);slots-=count[j]
            violation=z.x[q[d]]-z.x[r[i]]+sum(t*(z.x[q[j]]-z.x[r[j]])
                                                         for j,t in enumerate(count) if t)
            maximum=max(maximum,violation)
            if violation>1e-8:
                pairs=[(q[d],F(1)),(r[i],F(-1))]
                for j,t in enumerate(count):
                    if t:
                        pairs.extend([(q[j],F(t)),(r[j],F(-t))])
                cuts+=add(merge(pairs),F(0),["tcwm",mask,new,i,count])
        step={"iteration":iteration,"factor":float(z.fun),"cuts":cuts,
              "max_violation":maximum,"elapsed":time.monotonic()-start}
        print(json.dumps(step),flush=True);history.append(step)
        if not cuts:
            break
    info={"bits":bits,"d":d,"n":n,"s":s,"representatives":len(reps),
          "transition_representatives":len(transitions),"variables":N,"history":history,
          "scope":"finite necessary relaxation only; no upper or growth claim"}
    if solution is None:
        return info
    cert=[];combo={};right=F(0)
    for row,multiplier in enumerate(solution.ineqlin.marginals):
        weight=F(round(max(0,-float(multiplier))*10**10),10**10)
        if not weight:
            continue
        cert.append({"weight":str(weight),"row":records[row]})
        for var,value in coefficients[row].items():
            combo[var]=combo.get(var,F(0))+weight*value
        right+=weight*rhs[row]
    for mask in reps:
        q=qmap(mask)
        c=merge([(q[j],F(1)) for j in range(d) if mask&(1<<j)]
                +[(q[d],F(n-mask.bit_count()))])
        weight=max([F(0)]+[-combo.get(j,F(0))/value for j,value in c.items()])
        if weight>0:
            for var,value in c.items():
                combo[var]=combo.get(var,F(0))+weight*value
            combo[K]=combo.get(K,F(0))-weight*oracles[mask][0]
            cert.append({"weight":str(weight),"row":["budget",mask]})
    valid=combo.get(K,F(0))<0 and all(value>=0 for var,value in combo.items() if var!=K)
    info.update(float_candidate=float(solution.fun),exact_combo_valid=valid,
                exact_lower=str(right/combo[K]) if valid else None,certificate_rows=len(cert))
    used=set()
    for record in cert:
        row=record["row"];used.add(row[1])
        if row[0]=="tcwm":used.add(row[2])
    out={**info,"edges":edges,"generators":gens,"profile_reps":reps,"factor_index":K,
         "qmaps":{str(mask):qmap(mask) for mask in used},
         "oracles":{str(mask):{"value":str(v),"primal":list(map(str,p)),"dual":list(map(str,y))}
                    for mask,(v,p,y) in oracles.items()},
         "certificate":cert,"combo":{str(j):str(v) for j,v in combo.items() if v},"rhs":str(right)}
    Path(__file__).with_name(f"BINARY_SUBSET_B{bits}_S{s}.json").write_text(json.dumps(out,indent=2)+"\n")
    return info


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--bits",type=int,default=4)
    p.add_argument("--s",type=int,default=15);p.add_argument("--seconds",type=int,default=180)
    a=p.parse_args();assert 2<=a.bits<=4,"bounded all-subset scout"
    print(json.dumps(solve(a.bits,a.s,a.seconds)),flush=True)
