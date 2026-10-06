#!/usr/bin/env python3
"""Independent exact checking of actual invariant coalition/report rows.
Uses only the standard library; checks survive -O. The symmetry justification
is in ENCODING.txt. Certifies a lower bound, not an upper mechanism or novelty.
"""
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import argparse,copy,hashlib,json


def check(ok,message):
    if not ok:raise ValueError(message)


def verify(cert):
    k,m,H=(cert[n] for n in ('k','m','high'))
    check(all(type(x)is int and x>=2 for x in (k,m,H)),'parameter domain')
    check(cert.get('schema')==1,'schema')
    total=defaultdict(Fraction);constant=Fraction(0)
    for row in cert['rows']:
        mu=Fraction(row['weight']);check(mu>=0,'negative weight')
        s=tuple(row['state'])
        check(len(s)==m+1 and all(type(n)is int and n>=0 for n in s) and sum(s)==k,'profile histogram')
        hs={h for h,n in enumerate(s) if n}
        T=min((m-h)+H*h for h in hs)
        if row['kind']=='budget':
            total['B']+=mu*T
            for h in hs:
                if m-h:total[s,h,'low']-=mu*s[h]*(m-h)
                if h:total[s,h,'high']-=mu*s[h]*h
        elif row['kind']=='cover':
            triples=row['choices'];check(len(triples)==len(hs),'one choice per present type')
            used=set();caps=[]
            for triple in triples:
                check(len(triple)==3 and all(type(x)is int for x in triple),'integer coalition counts')
                h,a,b=triple
                check(h in hs and h not in used,'coalition type');used.add(h)
                check(0<=a<=m-h and 0<=b<=h,'coalition multiplicities')
                caps.append(a+H*b)
                if a:total[s,h,'low']+=mu*s[h]*a
                if b:total[s,h,'high']+=mu*s[h]*b
            check(used==hs,'all pool types covered')
            constant+=mu*min(caps)
        elif row['kind']=='mono':
            h=row['h'];check(type(h)is int and 0<=h<m and s[h]>0,'report edge')
            dest=list(s);dest[h]-=1;dest[h+1]+=1;dest=tuple(dest)
            # A single original owner raises 1 -> H; every other report is fixed.
            total[s,h,'low']-=mu
            total[dest,h+1,'high']+=mu
        else:raise ValueError('unknown row kind')
    coeff=total.pop('B',Fraction(0));check(coeff>0,'positive budget coefficient')
    check(all(x<=0 for x in total.values()),'uncancelled positive payment coefficient')
    bound=constant/coeff
    check(bound==Fraction(cert['claimed_total_factor']),'claimed bound mismatch')
    return {'status':'EXACT_LOWER_CERTIFIED','factor':str(bound),'subsidy_factor':str(bound-1),
            'k':k,'owners_per_pool':m,'high_report':H,'rows':len(cert['rows']),
            'budget_coefficient':str(coeff),'constant':str(constant),
            'nonnegativity_rows_to_cancel':sum(x<0 for x in total.values())}


def controls(cert):
    mutations=[]
    c=copy.deepcopy(cert);c['rows'][0]['weight']='-1';mutations.append(('negative weight',c))
    c=copy.deepcopy(cert);c['rows'][0]['state'][0]+=1;mutations.append(('profile histogram',c))
    c=copy.deepcopy(cert);c['claimed_total_factor']=str(Fraction(c['claimed_total_factor'])+1);mutations.append(('claimed bound mismatch',c))
    for kind,message in [('cover','coalition multiplicities'),('mono','report edge')]:
        c=copy.deepcopy(cert);r=next((r for r in c['rows'] if r['kind']==kind),None)
        if r is None:continue
        if kind=='cover':r['choices'][0][1]=cert['m']+1
        else:r['h']=cert['m']
        mutations.append((message,c))
    c=copy.deepcopy(cert);c['rows']=[r for r in c['rows'] if r['kind']!='budget']
    mutations.append(('positive budget coefficient',c))
    c=copy.deepcopy(cert);r=next((r for r in c['rows'] if r['kind']=='cover' and any(a or b for h,a,b in r['choices'])),None)
    if r is not None:
        # Dominate every possible negative budget/edge coefficient at one
        # selected owner coordinate, without changing the descriptor schema.
        large=1+sum(abs(Fraction(x['weight'])) for x in c['rows'])*(cert['k']*cert['m']+1)
        r['weight']=str(Fraction(r['weight'])+large)
        mutations.append(('uncancelled positive payment coefficient',c))
    for message,c in mutations:
        try:verify(c)
        except ValueError as e:check(str(e)==message,'wrong rejection: '+str(e))
        else:raise ValueError('corruption accepted')
    return len(mutations)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('certificate',type=Path);parser.add_argument('--controls',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args();cert=json.loads(args.certificate.read_text());result=verify(cert)
    if args.controls:result['corruptions_rejected']=controls(cert)
    result['certificate_sha256']=hashlib.sha256(args.certificate.read_bytes()).hexdigest()
    result['verifier_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text)
