#!/usr/bin/env python3
"""Exact constructive dual for the hierarchy lower-bound candidate.
This checks specializations; the all-parameter proof is in the companion note.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,hashlib
from verify import verify,controls


def construct(d,m,L,extra=0):
    if not (type(d)is int and d>=1 and type(m)is int and m>d and type(L)is int and L>=2 and type(extra)is int and extra>=0):
        raise ValueError('parameter domain')
    counts=[2*L**h for h in range(d+1)]+[0]*(m-d)
    counts[d]+=extra
    k=sum(counts);A=(d+1)*m-d*d
    rows=[{'kind':'budget','state':counts,'weight':'1'},
          {'kind':'cover','state':counts,'choices':[[h,1,0] for h in range(d+1)],'weight':str(m-d)},
          {'kind':'cover','state':counts,'choices':[[h,m-d+1,0] for h in range(d)]+[[d,0,1]],'weight':str(d)}]
    factor=Q(1)
    for h in range(d):
        edge_weight=A*counts[h]
        budget_weight=Q(edge_weight,(h+1)*(counts[h+1]+1))
        dest=counts.copy();dest[h]-=1;dest[h+1]+=1
        rows.append({'kind':'mono','state':counts,'h':h,'weight':str(edge_weight)})
        rows.append({'kind':'budget','state':dest,'weight':str(budget_weight)})
        factor+=budget_weight
    cert={'schema':1,'k':k,'m':m,'high':m,'claimed_total_factor':str(Q(A,m)/factor),'rows':rows}
    return cert


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    results=[]
    for d in (1,2,3,5,8,12,20):
        m=2*d;A=d*(d+2);L=2*A*d
        for extra in (0,7):
            cert=construct(d,m,L,extra);result=verify(cert);result['corruptions_rejected']=controls(cert)
            bound=Q(result['factor'])
            if not bound>Q(d+2,3):raise ValueError('elementary symbolic lower failed')
            result.update(d=d,L=L,extra_pools=extra,strict_elementary_lower=str(Q(d+2,3)))
            name=f'hierarchy-d{d}-extra{extra}.certificate.json';target=a.output/name
            target.write_text(json.dumps(cert,indent=2)+'\n')
            result['certificate_sha256']=hashlib.sha256(target.read_bytes()).hexdigest();results.append(result)
            print(json.dumps({'d':d,'extra':extra,'factor_decimal_for_display':float(bound),'certified_greater_than':str(Q(d+2,3)),'rows':len(cert['rows'])}),flush=True)
    (a.output/'VERIFICATION.json').write_text(json.dumps({'status':'EXACT_SPECIALIZATIONS_CHECKED','limitation':'The finite runs validate the dual construction, not the all-d theorem or novelty.','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).with_name('verify.py').read_bytes()).hexdigest(),'cases':results},indent=2)+'\n')
