"""Independent full-subset lower-hull comparison; finite tests are not the proof."""
from pathlib import Path
import importlib.util,json,random
from fractions import Fraction as Q
from itertools import combinations
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('oracle_prices',B/'POLYMATROID_ORACLE_PRICES.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
R=random.Random(171026);counts={'profiles':0,'restoration_holding_boxes':0,'ordinary_oracle_comparisons':0,'maximal_oracle_calls':0,'all_pair_reference_checks':0}
def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def forms(rank,P,c):return[(P*rank[S],sum((v for j,v in enumerate(c)if not S>>j&1),Q(0)),S)for S in range(len(rank))]
def reference(rank,P,c,all_pairs=False):
    ff=forms(rank,P,c);value=min(a+b for a,b,S in ff)
    if not value:return value,(Q(0),)*(len(c)+1)
    if all_pairs:
        cuts={Q(0)}
        for(a,b,S),(aa,bb,T)in combinations(ff,2):
            if a!=aa and(z:=(bb-b)/(a-aa))>0:cuts.add(z)
        cuts=sorted(cuts)+[None]
        prices=[Q(0)]*(len(c)+1)
        for lo,hi in zip(cuts,cuts[1:]):
            z=lo+1 if hi is None else(lo+hi)/2;best=min(a*z+b for a,b,S in ff);chosen=0
            for a,b,S in ff:
                if a*z+b==best:chosen|=S
            weight=mod.ratio_cdf(hi)-mod.ratio_cdf(lo)
            gradient=[rank[chosen]]+[Q(not chosen>>j&1)for j in range(len(c))]
            prices=[x+weight*y for x,y in zip(prices,gradient)]
    else:
        # Enumerate every subset, then build the ordinary lower hull of all lines.
        best={}
        for a,b,S in ff:
            if a not in best or b<best[a][0]:best[a]=(b,S)
        hull=[]
        for a in sorted(best,reverse=True):
            b,S=best[a];start=None
            while hull:
                aa,bb,SS,oldstart=hull[-1];start=(b-bb)/(aa-a)
                if oldstart is None or start>oldstart:break
                hull.pop()
            if not hull:start=None
            hull.append((a,b,S,start))
        prices=[Q(0)]*(len(c)+1)
        for index,(a,b,S,start)in enumerate(hull):
            stop=hull[index+1][3]if index+1<len(hull)else None
            if stop is not None and stop<=0:continue
            lo=max(Q(0),start)if start is not None else Q(0)
            weight=mod.ratio_cdf(stop)-mod.ratio_cdf(lo)
            gradient=[rank[S]]+[Q(not S>>j&1)for j in range(len(c))]
            prices=[x+weight*y for x,y in zip(prices,gradient)]
    for j,v in enumerate((P,*c)):
        if not v:prices[j]=Q(0)
    return value,tuple(prices)

def ordinary(n,f):return min(range(1<<n),key=lambda S:(f(S),S))
for m in range(1,9):
 for tech in range(4):
    active=R.randrange(1<<m);cap=R.randrange(m+1)
    features=[R.randrange(1<<m)&active for _ in range(5)];weights=[Q(R.randrange(1,6),R.randrange(1,5))for _ in features]
    rank=[Q(min(cap,(S&active).bit_count()))+sum((w for f,w in zip(features,weights)if S&f),Q(0))for S in range(1<<m)]
    for trial in range(6):
      C=tuple(Q(R.randrange(0,10),R.randrange(1,5))for _ in range(m+1))
      got=mod.polymatroid_prices(C[0],C[1:],rank.__getitem__,mod.exhaustive_maximal_sfm)
      expected=reference(rank,C[0],C[1:]);assert(got['value'],got['prices'])==expected,(m,tech,C,got,expected)
      if m<=4 and trial==0:
          assert expected==reference(rank,C[0],C[1:],all_pairs=True);counts['all_pair_reference_checks']+=1
      assert dot(C,got['prices'])<=Q(3,2)*got['value']
      counts['profiles']+=1;counts['maximal_oracle_calls']+=got['maximal_sfm_calls']
      if m<=4 and trial<2:
          via=lambda a,c,r:mod.ordinary_to_maximal_sfm(a,c,r,ordinary)
          second=mod.polymatroid_prices(C[0],C[1:],rank.__getitem__,via)
          assert second['prices']==got['prices'];counts['ordinary_oracle_comparisons']+=1
      if got['value']and trial<2:
          for j in range(m+1):
              D=list(C);delta=Q(1,3);D[j]+=delta
              high=mod.polymatroid_prices(D[0],D[1:],rank.__getitem__,mod.exhaustive_maximal_sfm)
              loss=sum((v*max(Q(0),a-b)for v,a,b in zip(C,got['prices'],high['prices'])),Q(0))
              assert delta*high['prices'][j]>=loss
              counts['restoration_holding_boxes']+=1
# A tied, all-at-once principal breakpoint; zero rows; true public loops.
for rank,C in [([Q(0),Q(1),Q(1),Q(2)],(Q(1),Q(1),Q(1))),([Q(0),Q(0),Q(1),Q(1)],(Q(1),Q(4),Q(2))),([Q(0),Q(1),Q(1),Q(1)],(Q(1),Q(0),Q(2)))]:
    got=mod.polymatroid_prices(C[0],C[1:],rank.__getitem__,mod.exhaustive_maximal_sfm)
    assert(got['value'],got['prices'])==reference(rank,C[0],C[1:],all_pairs=True);counts['profiles']+=1
out={'status':'PASS',**counts,'algorithm':'At most2m-1exact maximal-SFM calls on mactive private rows; zero faces may use0.','test_backend':'Exhaustive subset enumeration: intentionally exponential, not a polynomial implementation.','reference':'Independent complete-subset lower hull, with all-pair breakpoint cross-checks on small instances.','scope':'Finite implementation evidence only; all-profile incentives follow from identical prices and the accepted analytic theorem; no fullOUT claim.'}
(B/'POLYMATROID_ORACLE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
