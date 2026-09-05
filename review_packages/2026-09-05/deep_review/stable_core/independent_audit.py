"""Independent mathematical checks. Imports no package verifier or witness data.
Run: /private/tmp/coopgt-research-20260904/.venv/bin/python independent_audit.py
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import json, hashlib, z3
OUT=Path(__file__).parent
U=(0,1,0,1,2,0); V=(1,0,1,0,0,2)
A=(1,1,0,1,3,0); B=(2,0,1,0,1,2)
coalitions=[s for k in range(1,7) for s in combinations(range(6),k)]
def val(s): return min(sum(A[i] for i in s),sum(B[i] for i in s))
def label(s): return ''.join(str(i+1) for i in s)
def req(x,msg):
    if not x: raise RuntimeError(msg)
def af(a=0,b=0): return (F(a),F(b)) # intercept, slope
zero=af()
def add(*forms): return tuple(sum(f[k] for f in forms) for k in range(2))
def sub(f,g): return tuple(f[k]-g[k] for k in range(2))
def div(f,k): return tuple(x/k for x in f)
def at(f,t): return f[0]+t*f[1]
worth={s:af(min(sum(U[i] for i in s),sum(V[i] for i in s)),len(set(s)&{0,4})) for s in coalitions}

def round_forms(fixed,ws=worth,ss=coalitions,n=6):
    chi={}
    for s in ss:
        free=set(s)-fixed.keys()
        residual=sub(ws[s],add(zero,*(fixed[i] for i in s if i in fixed)))
        share=div(residual,len(free)) if free else None
        chi[s]={i:fixed[i] if i in fixed else share for i in s}
    return chi

def choose_round(chi,t,ws=worth,n=6):
    maxima={i:max((cs[i] for s,cs in chi.items() if i in s),key=lambda f:at(f,t)) for i in range(n)}
    admiss=[s for s,cs in chi.items() if at(sub(add(zero,*cs.values()),ws[s]),t)==0 and all(at(cs[i],t)==at(maxima[i],t) for i in s)]
    return maxima,admiss

def point_trace(t,ws=worth,ss=coalitions,n=6):
    fixed={}; hist=[]
    for _ in range(n):
        chi=round_forms(fixed,ws,ss,n)
        maxima,admiss=choose_round(chi,t,ws,n)
        new=sorted(set().union(*map(set,admiss))-fixed.keys())
        req(new,'point procedure stalled')
        hist.append({'maxima':[str(at(maxima[i],t)) for i in range(n)],'admissible':list(map(label,admiss)),'new':label(new)})
        fixed.update({i:af(at(maxima[i],t)) for i in new})
        if len(fixed)==n: return tuple(fixed[i][0] for i in range(n)),hist
    raise RuntimeError('too many rounds')

# Independent parametric branching: discover every comparison root dynamically,
# without assuming the manuscript's strata or its three claim chambers.
cuts={F(0)}; cells=[]; comparisons=0

def walk(lo,hi,fixed,hist):
    global comparisons
    if len(fixed)==6:
        cells.append((lo,hi,tuple(fixed[i] for i in range(6)),hist)); return
    chi=round_forms(fixed)
    local={lo};
    if hi is not None: local.add(hi)
    forms=[]
    for i in range(6):
        candidate=set(cs[i] for s,cs in chi.items() if i in s)
        forms.extend(sub(f,g) for f,g in combinations(candidate,2))
    # Fully fixed coalition feasibility can change at isolated parameter points.
    forms.extend(sub(add(zero,*cs.values()),worth[s]) for s,cs in chi.items())
    for f in forms:
        comparisons+=1
        if f[1]:
            r=-f[0]/f[1]
            if r>lo and (hi is None or r<hi): local.add(r); cuts.add(r)
    points=sorted(local)
    ranges=list(zip(points,points[1:]))
    if hi is None: ranges.append((points[-1],None))
    for left,right in ranges:
        sample=left+1 if right is None else (left+right)/2
        maxima,admiss=choose_round(chi,sample)
        # Independently ensure a selected maximum dominates each rival throughout
        # the cell closure. Zero of a nonzero affine gap cannot be inside.
        for s,cs in chi.items():
            for i,f in cs.items():
                gap=sub(maxima[i],f)
                req(at(gap,left)>=0 and (gap[1]>=0 if right is None else at(gap,right)>=0),'max not valid on cell')
        new=sorted(set().union(*map(set,admiss))-fixed.keys())
        req(new,'interval procedure stalled')
        walk(left,right,{**fixed,**{i:maxima[i] for i in new}},hist+[{'new':label(new),'admissible':list(map(label,admiss))}])

walk(F(0),None,{},[])
expected=[(af(F(1,2),F(3,4)),af(F(1,2),F(1,4)),af(F(1,2),F(3,4)),af(F(1,2),F(1,4)),af(1,F(1,2)),af(1,F(1,2))),
          (af(0,F(3,2)),af(1,F(-1,2)),af(1),af(1,F(-1,2)),af(1,F(1,2)),af(1,F(1,2))),
          (af(F(1,2),1),af(F(1,2)),af(1),af(F(1,2)),af(F(1,2),1),af(F(3,2)))]
def chamber(t): return 0 if t<=F(2,3) else (1 if t<=1 else 2)
for lo,hi,g,hist in cells:
    t=lo+1 if hi is None else (lo+hi)/2
    req(g==expected[chamber(t)],f'ray formula mismatch {lo} {hi}')
    req([h['new'] for h in hist]==[['56','13','24'],['56','1','234'],['15','36','24']][chamber(t)],'unexpected open-cell strata')
boundary_records=[]
for t in sorted(cuts):
    g,h=point_trace(t)
    req(g==tuple(at(f,t) for f in expected[chamber(t)]),f'boundary claim mismatch {t}')
    req(('123456' in h[-1]['admissible'])==(t==0),'boundary PES wrong')
    if t not in (0,F(2,3),1):
        req([a['new'] for a in h]==[['56','13','24'],['56','1','234'],['15','36','24']][chamber(t)],f'isolated strata exception {t}')
    boundary_records.append({'t':str(t),'claims':list(map(str,g)),'trace':h})

# Full coalition exactness/class membership, recomputed directly from printed A,B.
req(sum(A)==sum(B)==6,'sums')
req(all(val(s)>=0 for s in coalitions),'nonnegative')
monotonic_checks=0; super_checks=0
for s in [()]+coalitions:
    for q in [()]+coalitions:
        if set(s)<=set(q): req(val(s)<=val(q),'monotonicity'); monotonic_checks+=1
        if not set(s)&set(q): req(val(tuple(set(s)|set(q)))>=val(s)+val(q),'superadditive'); super_checks+=1

# Direct quantified formulation: no imported h_ij formula, arrangement, or pair proof.
y=z3.Reals('y1 y2 y3 y4 y5 y6'); r=z3.Real('r')
core=[sum(y[i] for i in s)>=val(s) for s in coalitions]
I=[sum(y)==6]+[y[i]>=min(A[i],B[i]) for i in range(6)]
x=[A[i]+r*(B[i]-A[i]) for i in range(6)]
dom=z3.Exists([r],z3.And(r>=0,r<=1,z3.Or(*[z3.And(sum(x[i] for i in s)<=val(s),*[x[i]>y[i] for i in s]) for s in coalitions[:-1]])))
solver=z3.Solver(); solver.set(timeout=60000)
solver.add(*I,z3.Not(z3.And(*core)),z3.Not(dom))
status=solver.check(); req(status==z3.unsat,f'global stability quantified status {status}')
(OUT/'external_stability.smt2').write_text(solver.sexpr())
# Core containment reverse checked without asserted pair parametrization.
segment=z3.Exists([r],z3.And(r>=0,r<=1,*[y[i]==x[i] for i in range(6)]))
sc=z3.Solver(); sc.set(timeout=60000); sc.add(*I,*core,z3.Not(segment))
req(sc.check()==z3.unsat,'core has off-segment point')
(OUT/'core_segment.smt2').write_text(sc.sexpr())

# General interval elimination lemma: exercise all sign patterns with exact QE,
# and separately empty P/M, zero directions, and endpoint ties.
lemma_checks=0
for d in product((-2,0,3),repeat=3):
    zz=z3.Reals('z1 z2 z3'); tt=z3.Real('tt')
    direct=z3.Exists(tt,z3.And(tt>=0,tt<=1,*[tt*d[i]>zz[i] for i in range(3)]))
    rhs=z3.And(*([zz[i]<0 for i in range(3) if d[i]==0]+[zz[i]<d[i] for i in range(3) if d[i]>0]+[zz[i]<0 for i in range(3) if d[i]<0]+[d[j]*zz[i]-d[i]*zz[j]>0 for i in range(3) for j in range(3) if d[i]>0>d[j]]))
    sl=z3.Solver(); sl.set(timeout=10000); sl.add(z3.Xor(direct,rhs))
    req(sl.check()==z3.unsat,f'interval sign failure {d}'); lemma_checks+=1

# Mauri printed data, computed through same definition with independent generic input.
ss5=[s for k in range(1,6) for s in combinations(range(5),k)]
aa=(1,-1,-1,0,0); bb=(0,1,0,-1,-1)
w5={s:af(min(sum(aa[i] for i in s),sum(bb[i] for i in s))) for s in ss5}
g5,h5=point_trace(F(0),w5,ss5,5)
req(g5==(0,0,0,0,0) and h5[0]['admissible']==['1','12','13','124','125'],'Mauri calculation')
result={'method':'independent Fraction dynamic ray partition; direct quantified LRA stability and core queries; no package imports',
        'z3_version':z3.get_version_string(),'core_off_segment_query':'UNSAT','outside_undominated_query':'UNSAT',
        'ray':{'open_cells':len(cells),'finite_boundaries':len(cuts),'affine_comparisons_considered':comparisons,'all_claim_formulas':'verified','all_strata_including_isolated_interior_ties':'verified','boundaries':boundary_records,'cells':[{'lo':str(lo),'hi':str(hi),'claims':[[str(z) for z in f] for f in g],'trace':h} for lo,hi,g,h in cells]},
        'monotonic_comparisons':monotonic_checks,'disjoint_superadditive_comparisons':super_checks,'general_domination_sign_pattern_checks':lemma_checks,
        'mauri':{'claims':list(map(str,g5)),'trace':h5}}
(OUT/'independent_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('ray','mauri')},indent=2))
print('Ray:',len(cells),'open cells;',len(cuts),'finite boundaries;',comparisons,'comparisons')
