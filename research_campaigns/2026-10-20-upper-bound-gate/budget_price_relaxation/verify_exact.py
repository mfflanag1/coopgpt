"""Independent standard-library verification of budget-supported price witnesses."""
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/'finite_diagnostics'
spec=importlib.util.spec_from_file_location('frozen_certificate_checker',SRC/'check_certificate.py')
frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)

def verify(seed,prices=None,scale=Q(1)):
    path=SRC/f'case_{seed}_certificate.json'
    original=frozen.check(path)
    data=json.loads(path.read_text());case=data['case'];A=case['A'];pi=list(map(Q,case['pi']));d=case['d']
    if prices is None:prices=json.loads((ROOT/f'case_{seed}.json').read_text())['prices']
    p={int(k):list(map(Q,v)) for k,v in prices.items()}
    b=[[data['owner_states'][i][s[i]] for i in range(4)] for s in data['profiles']]
    values={tuple(o['cap']):Q(o['value']) for o in data['oracles']}
    def cap(k,C):return tuple(sum(b[k][i][a] for i in C) for a in range(d))
    def val(k,C):return values[cap(k,C)]
    def charge(k,C):return sum(p[k][a]*b[k][i][a] for i in C for a in range(d))
    nu=defaultdict(Q);sigma=defaultdict(Q);L=D=coverage=positive=negative=Q(0);edges=[];slacks=[]
    for item in data['certificate']:
        tag=item['tag'];w=Q(item['weight'])*scale
        if tag[0]=='budget':
            k=tag[1];nu[k]+=w;D+=w*val(k,range(4))
            for i in range(4):sigma[k,i]+=w
        elif tag[0]=='cover':
            _,k,C=tag;v=val(k,C);slack=charge(k,C)-v
            assert slack>=0
            L+=w*v;coverage+=w*slack
            if slack:slacks.append(dict(profile=k,coalition=C,slack=str(slack),weighted_slack=str(w*slack)))
            for i in C:sigma[k,i]-=w
        else:
            _,lo,hi,C=tag;delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d));v=values[delta]
            defect=charge(lo,C)-charge(hi,C)+v
            assert defect>=0,(seed,tag,defect)
            L+=w*v;positive+=w*max(defect,0);negative+=w*max(-defect,0)
            edges.append(dict(lo=lo,hi=hi,coalition=C,defect=str(defect),weighted_defect=str(w*defect)))
            for i in C:sigma[lo,i]+=w;sigma[hi,i]-=w
    excess={}
    for k,pk in p.items():
        assert min(pk)>=0
        assert all(sum(A[a][j]*pk[a] for a in range(d))>=pi[j] for j in range(len(pi)))
        ex=charge(k,range(4))-val(k,range(4));assert ex>=0
        if nu[k]>0:assert ex==0,(seed,k,ex)
        if ex:excess[k]=ex
    assert all(w>=0 for w in sigma.values())
    sigma_price=sum(w*charge(k,[i]) for (k,i),w in sigma.items())
    budget_excess=sum(nu[k]*v for k,v in excess.items())
    assert budget_excess==0 and negative==0
    assert L-D==positive-negative-coverage-sigma_price+budget_excess
    return dict(seed=seed,status='EXACT PASS',lower=original['lower'],profiles=len(p),comparison_rows=len(edges),budget_profiles=sum(v>0 for v in nu.values()),L=str(L),D=str(D),positive_defect=str(positive),negative_defect=str(negative),coverage_slack=str(coverage),sigma_price=str(sigma_price),budget_excess=str(budget_excess),profile_excess={str(k):str(v) for k,v in excess.items()},edges=edges,coverage_slacks=slacks)

def root_inflation_family():
    """Exact rational fixtures; RESULT section 6 proves the all-real bound."""
    out=[]
    for t in [Q(1,2),Q(1,3),Q(1,10),Q(1,100),Q(1,1000),Q(2,3),Q(9,10)]:
        R=(Q(3),Q(0),Q(0));cl=(t,2*t,3*t);ch=(Q(1),Q(2),Q(3))
        Bl=tuple(a+b for a,b in zip(R,cl));Bh=tuple(a+b for a,b in zip(R,ch))
        delta=tuple(a-b for a,b in zip(ch,cl));pl=(Q(0),(1+t)/(2*t),Q(0));ph=(Q(0),Q(1),Q(0))
        dot=lambda a,b:sum(x*y for x,y in zip(a,b))
        assert min(Bl)==2*t and min(Bh)==2 and min(cl)==t and min(delta)==1-t
        assert Bh[1]<Bh[0] and Bh[1]<Bh[2] # unique bottleneck; proof gives unique efficient price
        assert min(pl)>=0 and sum(pl)>=1 and sum(ph)==1
        assert dot(ph,Bh)==min(Bh) and dot(ph,ch)==2
        assert dot(pl,cl)==1+t and dot(pl,Bl)==1+t
        defect=dot(pl,cl)-dot(ph,ch)+min(delta);assert defect==0
        # g(low,R)=g(low,C)=g(high,R)=0, g(high,C)=1.
        g=(Q(0),Q(1)-Q(1),Q(0),Q(1));nu=(Q(0),Q(0),Q(1),Q(1))
        assert all(x<=y for x,y in zip(g,nu))
        L=min(cl)+min(delta);D=min(Bh);assert L==1 and D==2
        coverage_slack=dot(pl,cl)-min(cl);sigma_price=dot(ph,R)
        budget_excess=dot(ph,Bh)-min(Bh)
        assert L-D==defect-coverage_slack-sigma_price+budget_excess
        assert dot(pl,Bl)/min(Bl)==(1+t)/(2*t)
        out.append(dict(t=str(t),minimum_low_cost=str(1+t),low_value=str(2*t),minimum_cost_ratio=str((1+t)/(2*t)),defect=str(defect),L=str(L),D=str(D)))
    return dict(status='EXACT PASS',attribution='Root derivation, independently checked by upper_gate_price_lift',scope='Rational fixture checks; universal proof in RESULT.txt section 6',fixtures=out)

if __name__=='__main__':
    results=[verify(s) for s in range(10,66)]
    root_prices={'37':['0','5/2','0','1'],'101':['5/2','0','0','5/2'],'133':['0','5/2','1/6','5/6'],'149':['1/3','13/6','0','1/3'],'165':['0','5/2','0','1']}
    root_check=verify(15,root_prices,Q(139,6))
    assert root_check['positive_defect']=='5/2' and root_check['coverage_slack']=='23/12'
    assert root_check['profile_excess']=={'133':'1/3'}
    assert Q(root_check['L'])-Q(root_check['D'])==Q(7,12)
    (ROOT/'seed15_root_witness.json').write_text(json.dumps(dict(prices=root_prices,verification=root_check),indent=2)+'\n')
    inflation=root_inflation_family()
    (ROOT/'root_inflation_family.json').write_text(json.dumps(inflation,indent=2)+'\n')
    summary=dict(status='EXACT PASS',cases=len(results),with_comparisons=sum(bool(v['comparison_rows']) for v in results),without_comparisons=sum(not v['comparison_rows'] for v in results),all_price_defects_nonnegative=True,all_budget_supported_efficiency=True,full_signed_identity_checked=True,root_inflation_family=inflation,results=results,seed15_root_witness=root_check)
    (ROOT/'EXACT_VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('results','seed15_root_witness','root_inflation_family')},indent=2))
    print('Root inflation-family rational fixtures: EXACT PASS')
