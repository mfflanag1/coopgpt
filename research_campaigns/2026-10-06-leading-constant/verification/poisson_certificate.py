"""Build exact weighted-profile certificates; independent verifier checks rows."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, hashlib, json
from verify import verify, controls

def compositions(k, parts):
    if parts == 1:
        yield (k,)
    else:
        for n in range(k + 1):
            for rest in compositions(k - n, parts - 1):
                yield (n,) + rest

def construct(k, d, m, alpha):
    alpha = Q(alpha)
    if not (k >= 2 and d >= 1 and m > d and alpha > 0):
        raise ValueError('parameter domain')
    A = (d + 1) * m - d * d
    lam = Q(A) / alpha
    Z = sum((lam**h / factorial(h) for h in range(d + 1)), Q(0))
    p = [lam**h / factorial(h) / Z for h in range(d + 1)]
    rows = []
    mass = Q(0)
    expected_T = Q(0)
    for short in compositions(k, d + 1):
        mu = Q(factorial(k))
        for h, n in enumerate(short):
            mu *= p[h]**n / factorial(n)
        mass += mu
        state = list(short) + [0] * (m - d)
        present = [h for h, n in enumerate(short) if n]
        expected_T += mu * (m + (m - 1) * min(present))
        rows.append({'kind':'budget', 'state':state,
                     'weight':str(mu * (1 + alpha))})
        rows.append({'kind':'cover', 'state':state,
                     'choices':[[h, 1, 0] for h in present],
                     'weight':str(mu * (m - d))})
        rows.append({'kind':'cover', 'state':state,
                     'choices':[[h, m-d+1, 0] if h < d else [h, 0, 1]
                                for h in present], 'weight':str(mu * d)})
        for h in range(d):
            if short[h]:
                rows.append({'kind':'mono','state':state,'h':h,
                             'weight':str(A * mu * short[h])})
    if mass != 1:
        raise ValueError('multinomial mass')
    tail_T = m + (m - 1) * sum((sum(p[r:])**k for r in range(1,d+1)), Q(0))
    if expected_T != tail_T:
        raise ValueError('independent expected-value formulas disagree')
    constant = A + d * (d - 1) * p[d]**k
    coefficient = (1 + alpha) * expected_T
    cert = {'schema':1,'k':k,'m':m,'high':m,
            'claimed_total_factor':str(constant / coefficient),'rows':rows}
    metadata = {'depth':d,'alpha':str(alpha),'lambda':str(lam),
                'p0':str(p[0]),'expected_T':str(expected_T),
                'weaker_theorem_bound':str(Q(A) / coefficient),
                'histograms':sum(1 for _ in compositions(k,d+1))}
    return cert, metadata

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    reports=[]
    cases=[(k,d,m,alpha) for k in (2,3,5) for d,m in ((1,2),(2,3),(2,6),(3,6))
           for alpha in (Q(1),Q(1,3))]
    for index,(k,d,m,alpha) in enumerate(cases):
        cert,meta=construct(k,d,m,alpha)
        result=verify(cert)
        result.update(meta)
        result['corruptions_rejected']=controls(cert)
        name=f'poisson-{index:02}.certificate.json'
        content=(json.dumps(cert,indent=2)+'\n').encode()
        (args.output/name).write_bytes(content)
        result['certificate']=name
        result['certificate_sha256']=hashlib.sha256(content).hexdigest()
        reports.append(result)
    summary={'status':'EXACT_WEIGHTED_PROFILE_CERTIFICATES_PASS','cases':reports,
             'case_count':len(reports),
             'corruptions_rejected':sum(r['corruptions_rejected'] for r in reports),
             'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'verifier_sha256':hashlib.sha256(Path(__file__).with_name('verify.py').read_bytes()).hexdigest(),
             'scope':'Finite exact certificates validate weighted-row construction; full proof gives asymptotics.'}
    (args.output/'VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('PASS',len(reports),'weighted-profile certificates;',summary['corruptions_rejected'],'corruptions rejected')

if __name__=='__main__':main()
