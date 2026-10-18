#!/usr/bin/env python3
"""Independent stdlib exact replay of sparse all-subset PG certificates."""
from collections import deque, defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse, hashlib, json


def check(path):
    data=json.loads(Path(path).read_text())
    d,n,s,K=(data[k] for k in ("d","n","s","factor_index"))
    edges={tuple(sorted(e)) for e in data["edges"]}
    assert all(len(set(e))==3 and all(0<=j<d for j in e) for e in edges)
    gens=data["generators"]
    for g in gens:
        assert sorted(g)==list(range(d))
        assert {tuple(sorted(g[j] for j in e)) for e in edges}==edges
    masks={int(mask): q for mask,q in data["qmaps"].items()}
    entries=defaultdict(list)
    for mask,q in masks.items():
        assert 0<=mask<(1<<d) and len(q)==d+1 and mask.bit_count()<=n
        for j in range(d):
            if mask&(1<<j):
                assert 0<=q[j]<K
                entries[q[j]].append((mask,j))
            else:
                assert q[j]==-1
        assert 0<=q[d]<K
        entries[q[d]].append((mask,-1))
    cache={}
    def image_mask(mask,gid):
        key=(mask,gid)
        if key not in cache:
            out=0; todo=mask
            while todo:
                low=todo&-todo; todo^=low
                out|=1<<gens[gid][low.bit_length()-1]
            cache[key]=out
        return cache[key]
    # Independently compute only the group orbits needed by claimed equalities.
    orbit_of={}; orbit_id=0; orbit_for_variable={}
    for var,points in sorted(entries.items()):
        start=points[0]
        if start not in orbit_of:
            orbit_of[start]=orbit_id;todo=deque([start])
            while todo:
                mask,j=todo.popleft()
                for gid,g in enumerate(gens):
                    nxt=(image_mask(mask,gid),g[j] if j>=0 else -1)
                    if nxt not in orbit_of:
                        orbit_of[nxt]=orbit_id;todo.append(nxt)
            orbit_id+=1
        oid=orbit_of[start]
        assert all(orbit_of.get(point)==oid for point in points), "false orbit equality"
        assert oid not in orbit_for_variable, "same orbit split inconsistently"
        orbit_for_variable[oid]=var
    def production(mask):
        oracle=data["oracles"][str(mask)]
        value=F(oracle["value"]); x=list(map(F,oracle["primal"])); y=list(map(F,oracle["dual"]))
        ordered_edges=[tuple(e) for e in data["edges"]]
        assert len(x)==len(ordered_edges) and len(y)==d
        assert all(v>=0 for v in x+y)
        assert all(sum(x[t] for t,e in enumerate(ordered_edges) if j in e)<=((mask>>j)&1)
                   for j in range(d))
        assert all(sum(y[j] for j in e)>=1 for e in ordered_edges)
        assert sum(x)==value==sum(y[j] for j in range(d) if mask&(1<<j))
        return value
    combo=defaultdict(F);right=F(0);largest_coalition=0;checked_budgets=set()
    for item in data["certificate"]:
        weight=F(item["weight"]);assert weight>=0
        tag=item["row"];kind=tag[0];old=tag[1];q=masks[old]
        row=defaultdict(F);rhs=F(0)
        if kind=="budget":
            if old not in checked_budgets:
                production(old);checked_budgets.add(old)
            for j in range(d):
                if old&(1<<j):row[q[j]]+=1
            row[q[d]]+=n-old.bit_count()
            row[K]-=F(data["oracles"][str(old)]["value"])
        elif kind=="coverage":
            edge=tuple(sorted(tag[2]));assert edge in edges
            assert all(old&(1<<j) for j in edge)
            for j in edge:row[q[j]]-=1
            rhs=F(-1)
        elif kind=="tcwm":
            new,i,count=tag[2:];r=masks[new]
            assert not old&(1<<i) and new==old|(1<<i)
            assert len(count)==d+1 and all(type(c)is int and c>=0 for c in count)
            assert all(count[j]<=((old>>j)&1) for j in range(d))
            assert count[d]<=n-old.bit_count()-1
            size=1+sum(count);assert size<=s;largest_coalition=max(largest_coalition,size)
            row[q[d]]+=1;row[r[i]]-=1
            for j,c in enumerate(count):
                if c:
                    assert q[j]>=0 and r[j]>=0
                    row[q[j]]+=c;row[r[j]]-=c
        else:
            raise AssertionError(kind)
        for var,c in row.items():combo[var]+=weight*c
        right+=weight*rhs
    assert combo[K]<0 and all(c>=0 for var,c in combo.items() if var!=K)
    lower=right/combo[K]
    if data.get("exact_lower") is not None:assert lower==F(data["exact_lower"])
    if "combo" in data:assert {int(v):F(c) for v,c in data["combo"].items()}=={v:c for v,c in combo.items() if c}
    if "rhs" in data:assert right==F(data["rhs"])
    return {"status":"PASS","exact_lower":str(lower),"certificate_rows":len(data["certificate"]),
            "largest_protected_coalition":largest_coalition,"claimed_s":s,
            "profile_orbit_entries_checked":len(orbit_of),"budget_oracles_checked":len(checked_budgets),
            "sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest()}


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("path");a=p.parse_args()
    print(json.dumps(check(a.path),sort_keys=True))
