"""Repair only rational-rounding residue; replay result independently afterward."""
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, json

def repair(path):
    raw=path.read_bytes();p=json.loads(raw);d=p['d'];n=p['n'];stride=d+1;K=p['factor_index']
    combo={int(k):Q(v) for k,v in p['combo_nonzero'].items()};repairs=0
    for k,a in enumerate(p['states']):
        counts=a+[n-sum(a)]
        for j,c in enumerate(counts):
            if c==0 and combo.get(k*stride+j,Q(0))<0:raise RuntimeError('unrepairable absent payment')
        t=max([Q(0)]+[-combo.get(k*stride+j,Q(0))/c for j,c in enumerate(counts) if c])
        if t>0:
            for j,c in enumerate(counts):combo[k*stride+j]=combo.get(k*stride+j,Q(0))+t*c
            combo[K]-=t*Q(p['oracles'][k]['value'])
            p['certificate'].append({'multiplier':str(t),'row':['budget',k]});repairs+=1
    p['combo_nonzero']={str(k):str(v) for k,v in combo.items() if v}
    p['exact_lower']=str(Q(p['rhs'])/combo[K]);p['exact_dual_valid']=True
    p['rounding_repairs']=repairs;p['repair_input_sha256']=hashlib.sha256(raw).hexdigest()
    p['dual_support']=len(p['certificate'])
    target=path.with_name(path.stem+'_repaired.json');target.write_text(json.dumps(p,indent=2)+'\n')
    return {'file':target.name,'repairs':repairs,'lower':p['exact_lower'],'decimal_lower':float(Q(p['exact_lower']))}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('paths',nargs='+');args=ap.parse_args()
    for p in args.paths:print(json.dumps(repair(Path(p))))
