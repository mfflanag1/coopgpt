"""Exact falsification of own-report-independent virtual-capacity Banzhaf prices.
Not a valid rule unless coverage/budget are proved; this records counterexamples.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
helper=ROOT/'paper5/truthful_cooperation/verification/2026-10-04-stage-scaling/verify_thresholds.py'
spec=importlib.util.spec_from_file_location('threshold_exact',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def payments(c,sizes,mode):
    groups,totals,T=module.profile_data(c,sizes)
    if T==0:return [Q(0)]*len(c)
    y=[]
    for j,group in enumerate(groups):
        rivals=[l for l in range(len(groups)) if l!=j]
        B=min(totals[l] for l in rivals)
        for i in group:
            if mode=='fill_to_tie':x=max(Q(0),B-(totals[j]-c[i]))
            elif mode=='min_rival_max':x=min(max(c[h] for h in groups[l]) for l in rivals)
            elif mode=='min_rival_mean':x=min(totals[l]/len(groups[l]) for l in rivals)
            else:raise ValueError(mode)
            virtual=list(c);virtual[i]=x
            _,prob=module.payments(tuple(virtual),sizes,False)
            y.append(min(c[i],B)*prob[j])
    return y

records=[]
for mode in ('fill_to_tie','min_rival_max','min_rival_mean'):
    tested=0;found=None;largest=Q(0)
    for sizes in ((1,3),(2,2),(2,3),(2,2,2),(3,3)):
        for c in product(map(Q,(1,2,4)),repeat=sum(sizes)):
            y=payments(c,sizes,mode);g,tot,T=module.profile_data(c,sizes);tested+=1
            largest=max(largest,sum(y)/T)
            for mask in range(1<<len(c)):
                v=module.worth(c,g,mask);pay=sum((y[i] for i in range(len(c)) if mask>>i&1),Q(0))
                if pay<v:
                    found={'sizes':sizes,'capacities':list(map(str,c)),'payments':list(map(str,y)),'coalition_mask':mask,'worth':str(v),'paid':str(pay)};break
            if found:break
        if found:break
    records.append({'candidate':mode,'profiles_tested':tested,'coverage_counterexample':found,'largest_tested_factor':str(largest)})
    print(json.dumps(records[-1]),flush=True)
result={'status':'EXACT_CANDIDATE_FALSIFICATION','records':records,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'probability_helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'scope':'Failures of specified all-profile candidate formulas only; no unrestricted impossibility.'}
Path(__file__).with_name('PHANTOM_PRICE_FAILURES.json').write_text(json.dumps(result,indent=2)+'\n')
