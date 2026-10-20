"""Exact semantic checks for local erasure, coverage replacement and terminal prices.
Only standard-library arithmetic; stored files are read-only. Run this file to
write local_normalization_checks.json beside it. No owner multiplier is split.
"""
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent.parent

def dot(x,y): return sum((a*b for a,b in zip(x,y)),Q(0))

def check(data,label):
    case=data['case']; A=case['A']; pi=list(map(Q,case['pi'])); d=len(A)
    states=data['owner_states']; n=len(states)
    b=[[tuple(map(Q,states[i][p[i]])) for i in range(n)] for p in data['profiles']]
    N=len(b)
    def cap(p,C): return tuple(sum((b[p][i][r] for i in C),Q(0)) for r in range(d))
    totals=[cap(p,range(n)) for p in range(N)]
    values={}; efficient={}
    for o in data['oracles']:
        c=tuple(map(Q,o['cap'])); x=list(map(Q,o['x'])); price=list(map(Q,o['p'])); v=Q(o['value'])
        assert all(z>=0 for z in x+price)
        assert all(dot(A[r],x)<=c[r] for r in range(d))
        assert all(sum(A[r][j]*price[r] for r in range(d))>=pi[j] for j in range(len(pi)))
        assert dot(pi,x)==dot(c,price)==v
        values[c]=v; efficient[c]=price
    assert all(all(z>=0 for z in owner) for profile in b for owner in profile)
    def delta(l,h,C): return tuple(cap(h,C)[r]-cap(l,C)[r] for r in range(d))
    lam=defaultdict(Q); mu=defaultdict(Q); nu=[Q(0)]*N
    for item in data['certificate']:
        tag=item['tag']; weight=Q(item['weight']); assert weight>=0
        if not weight: continue
        if tag[0]=='budget': nu[tag[1]]+=weight
        elif tag[0]=='cover': lam[(tag[1],tuple(tag[2]))]+=weight
        elif tag[0]=='out': mu[(tag[1],tag[2],tuple(tag[3]))]+=weight
        else: raise ValueError(tag)
    def audit(coverage,edges):
        g=[[Q(0)]*n for _ in b]; L=Q(0)
        for (p,C),weight in coverage.items():
            assert C and len(C)==len(set(C)) and weight>0
            L+=weight*values[cap(p,C)]
            for i in C: g[p][i]+=weight
        for (l,h,C),weight in edges.items():
            assert C and len(C)<=2 and len(C)==len(set(C)) and weight>0
            assert all(b[l][i]==b[h][i] for i in range(n) if i not in C)
            assert all(b[h][i][r]>=b[l][i][r] for i in C for r in range(d))
            L+=weight*values[delta(l,h,C)]
            for i in C: g[l][i]-=weight; g[h][i]+=weight
        assert all(g[p][i]<=nu[p] for p in range(N) for i in range(n))
        D=sum(nu[p]*values[totals[p]] for p in range(N))
        # Independent coordinate resource identity, including all owner slacks.
        left=[sum(nu[p]*totals[p][r] for p in range(N))
              -sum(w*delta(l,h,C)[r] for (l,h,C),w in edges.items()) for r in range(d)]
        right=[sum(w*cap(p,C)[r] for (p,C),w in coverage.items())
               +sum((nu[p]-g[p][i])*b[p][i][r] for p in range(N) for i in range(n)) for r in range(d)]
        assert left==right
        return L,D,g
    L,D,g0=audit(lam,mu)
    if 'exact_lower' in data: assert L/D==Q(data['exact_lower'])
    lam1=defaultdict(Q); mu1=defaultdict(Q)
    erased_cov=erased_comp=0; empty_coverage=empty_comparisons=0
    for (p,C),weight in lam.items():
        C1=tuple(i for i in C if any(b[p][i]))
        erased_cov+=len(C)-len(C1)
        assert cap(p,C1)==cap(p,C)
        if C1: lam1[(p,C1)]+=weight
        else: empty_coverage+=1; assert values[cap(p,C)]==0
    for (l,h,C),weight in mu.items():
        C1=tuple(i for i in C if any(b[l][i]) or any(b[h][i]))
        erased_comp+=len(C)-len(C1)
        assert delta(l,h,C1)==delta(l,h,C)
        if C1: mu1[(l,h,C1)]+=weight
        else: empty_comparisons+=1; assert values[delta(l,h,C)]==0
    L1,D1,g1=audit(lam1,mu1); assert (L1,D1)==(L,D)
    assert all(g1[p][i]==g0[p][i] if any(b[p][i]) else g1[p][i]<=0
               for p in range(N) for i in range(n))
    lam2=defaultdict(Q,lam1); mu2=defaultdict(Q); replaced=0; replaced_rhs=Q(0)
    lineage=[]
    for (l,h,C),weight in mu1.items():
        if not any(cap(l,C)):
            assert delta(l,h,C)==cap(h,C)
            lam2[(h,C)]+=weight; replaced+=1; replaced_rhs+=weight*values[delta(l,h,C)]
            lineage.append(dict(source=[l,h,list(C)],target=['cover',h,list(C)],whole_weight=str(weight)))
        else: mu2[(l,h,C)]+=weight
    L2,D2,g2=audit(lam2,mu2); assert (L2,D2)==(L,D)
    assert all(any(cap(l,C)) for l,h,C in mu2)
    terminal_original=all(not nu[l] for l,h,C in mu)
    terminal_normalized=all(not nu[l] for l,h,C in mu2)
    if terminal_original: assert terminal_normalized
    price_result=None
    if terminal_normalized:
        # Positive constant feasible production price, computed from columns.
        t=max([Q(1)]+[pi[j]/sum(A[r][j] for r in range(d)) for j in range(len(pi)) if pi[j]>0])
        w=[t]*d; selected={}; outgoing=defaultdict(list)
        for l,h,C in mu2:
            assert sum(totals[h])>sum(totals[l]), 'retained non-self comparison must strictly restore'
            outgoing[l].append((h,C))
        scales=[]
        for p in sorted(range(N),key=lambda q:sum(totals[q]),reverse=True):
            if nu[p]>0:
                assert not outgoing[p]; selected[p]=efficient[totals[p]]
            else:
                scale=Q(1)
                for h,C in outgoing[p]:
                    denom=dot(w,cap(p,C)); assert denom>0
                    scale=max(scale,(dot(selected[h],cap(h,C))-values[delta(p,h,C)])/denom)
                selected[p]=[scale*z for z in w]; scales.append(scale)
        for p,price in selected.items():
            assert all(z>=0 for z in price)
            assert all(sum(A[r][j]*price[r] for r in range(d))>=pi[j] for j in range(len(pi)))
            if nu[p]: assert dot(price,totals[p])==values[totals[p]]
        defects=[dot(selected[l],cap(l,C))-dot(selected[h],cap(h,C))+values[delta(l,h,C)] for l,h,C in mu2]
        assert all(a>=0 for a in defects)
        E=sum(nu[p]*(dot(selected[p],totals[p])-values[totals[p]]) for p in range(N)); assert E==0
        # Check the complete signed accounting identity, not only E and signs.
        signed=sum(weight*(dot(selected[l],cap(l,C))-dot(selected[h],cap(h,C))+values[delta(l,h,C)]) for (l,h,C),weight in mu2.items())
        covslack=sum(weight*(dot(selected[p],cap(p,C))-values[cap(p,C)]) for (p,C),weight in lam2.items())
        sigslack=sum((nu[p]-g2[p][i])*dot(selected[p],b[p][i]) for p in range(N) for i in range(n))
        assert L-D==E+signed-covslack-sigslack
        price_result=dict(profiles_checked=N,supported_comparisons_checked=len(mu2),E=str(E),
                          minimum_a=str(min(defects)) if defects else None,
                          maximum_nonbudget_scale=str(max(scales,default=Q(1))),
                          signed_identity_checked=True,all_prices_feasible=True)
    return dict(case=label,profiles=N,oracles_checked=len(values),L=str(L),D=str(D),
                original_coverage_rows=len(lam),original_comparison_rows=len(mu),
                normalized_coverage_rows=len(lam2),normalized_comparison_rows=len(mu2),
                erased_coverage_members=erased_cov,erased_comparison_members=erased_comp,
                discarded_empty_coverage_rows=empty_coverage,discarded_empty_comparison_rows=empty_comparisons,
                replaced_comparisons=replaced,replaced_full_OUT_contribution=str(replaced_rhs),
                replacement_lineage=lineage,whole_coalition_weights_preserved=True,
                exact_L_D_preserved=True,all_dual_balances_and_resource_identities_checked=True,
                no_zero_low_comparisons_remain=True,
                terminal_budget_support_original=terminal_original,
                terminal_budget_support_normalized=terminal_normalized,price_construction=price_result)


def tiny_fixture():
    # Owner 0 holds both rows; owner 1 is zero locally at profiles 0,1 but
    # nonzero at profile 2. The first comparison has positive full-OUT worth.
    states=[[[0,0],[1,1],[2,2]],[[0,0],[1,0]]]
    caps=[(0,0),(1,1),(3,2),(2,1)]
    oracles=[]
    for a,b in caps:
        v=min(a,b); p=[1,0] if a<=b else [0,1]
        oracles.append(dict(cap=[a,b],value=str(v),x=[str(v)],p=list(map(str,p))))
    return dict(case=dict(A=[[1],[1]],pi=['1']),owner_states=states,
                profiles=[[0,0],[1,0],[2,1]],oracles=oracles,
                certificate=[dict(tag=['out',0,1,[0,1]],weight='1'),
                             dict(tag=['out',1,2,[0,1]],weight='2'),
                             dict(tag=['cover',1,[0,1]],weight='1'),
                             dict(tag=['budget',2],weight='2')])


def main():
    paths=sorted((ROOT/'finite_diagnostics').glob('case_*_certificate.json'),key=lambda p:int(p.name.split('_')[1]))
    assert len(paths)==56, len(paths)
    results=[check(json.loads(path.read_text()),path.name) for path in paths]
    tiny=check(tiny_fixture(),'explicit_local_nonzero_OUT_fixture')
    assert tiny['erased_coverage_members']>0 and tiny['erased_comparison_members']>0
    assert tiny['replaced_comparisons']>0 and Q(tiny['replaced_full_OUT_contribution'])>0
    assert tiny['normalized_comparison_rows']>0 and tiny['price_construction'] is not None
    summary=dict(stored_certificates_checked=len(results),
        original_terminal_budget_cases=sum(r['terminal_budget_support_original'] for r in results),
        normalized_terminal_budget_cases=sum(r['terminal_budget_support_normalized'] for r in results),
        backward_price_constructions_checked=sum(r['price_construction'] is not None for r in results),
        total_erased_coverage_members=sum(r['erased_coverage_members'] for r in results),
        total_erased_comparison_members=sum(r['erased_comparison_members'] for r in results),
        total_replaced_comparisons=sum(r['replaced_comparisons'] for r in results),
        all_exact_checks_passed=True)
    output=dict(summary=summary,stored_cases=results,explicit_fixture=tiny,
        scope='Finite semantic checks supplement the general proof; no funding-factor conclusion is inferred.')
    (Path(__file__).resolve().parent/'local_normalization_checks.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(dict(summary=summary, explicit_fixture=dict(explicit_fixture_L=tiny['L'],explicit_fixture_D=tiny['D'],
        erased_coverage_members=tiny['erased_coverage_members'],erased_comparison_members=tiny['erased_comparison_members'],
        replaced_full_OUT_contribution=tiny['replaced_full_OUT_contribution'])),indent=2))

if __name__=='__main__': main()
