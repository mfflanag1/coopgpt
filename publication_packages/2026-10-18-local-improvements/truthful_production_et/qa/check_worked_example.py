"""Exact four-mask evaluation of the printed capped-rule illustration.

Standard library only; no optimization solver or sampled integration.
Run with Python 3. Writes only stdout; optional --output PATH records JSON.
Polynomials use ascending Fraction coefficients in the deletion probability q.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse,json

def add(a,b):
    c=[F(0)]*max(len(a),len(b))
    for k,x in enumerate(a): c[k]+=x
    for k,x in enumerate(b): c[k]+=x
    return c

def scale(a,x): return [v*x for v in a]
def mul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return c

def integrate(a,upper):
    return sum((v*upper**(k+1)/F(k+1) for k,v in enumerate(a)),F(0))

def fmt(a): return [str(v) for v in a]

V=((F(1),F(0)),(F(0),F(1))) # This tuple fixes tie priority.
q=[F(0),F(1)]
on=[F(1),F(-1)]
def dot(a,b): return sum((x*y for x,y in zip(a,b)),F(0))
def total(b,mask): return tuple(sum((b[i][d]*mask[i] for i in range(2)),F(0)) for d in range(2))
def value(b,mask): return min(dot(w,total(b,mask)) for w in V)
def form(b,mask): return min(range(len(V)),key=lambda k:dot(V[k],total(b,mask)))
def prob(mask):
    p=[F(1)]
    for bit in mask:p=mul(p,on if bit else q)
    return p

def evaluate(b):
    T=value(b,(1,1)); rows=[]; payments=[]; detail=[]
    for mask in product((0,1),repeat=2):
        w=form(b,mask)
        rows.append({'mask':list(mask),'scores':[str(dot(v,total(b,mask))) for v in V],'selected_form':w+1,'capped_contributions':[str(min(dot(V[w],bi),T)) for bi in b]})
    for i in range(2):
        p=[F(0)];m=[F(0)];z=[F(0)]
        for other in (0,1):
            off=[0,0];off[1-i]=other
            masked_on=off.copy();masked_on[i]=1
            weight=prob((other,))
            w=form(b,off)
            p=add(p,scale(weight,min(dot(V[w],b[i]),T)))
            m=add(m,scale(weight,value(b,masked_on)-value(b,off)))
        for mask in product((0,1),repeat=2):
            w=form(b,mask)
            z=add(z,scale(prob(mask),min(dot(V[w],b[i]),T)))
        r=add(mul(q,p),mul(on,m))
        payment=F(2)*integrate(r,F(1,2));payments.append(payment)
        detail.append({'owner':i+1,'p_coefficients':fmt(p),'m_coefficients':fmt(m),'r_coefficients':fmt(r),'z_coefficients':fmt(z),'payment':str(payment)})
    coalitions=[]
    for mask in product((0,1),repeat=2):
        v=value(b,mask); pay=sum((payments[i]*mask[i] for i in range(2)),F(0))
        assert pay>=v
        coalitions.append({'mask':list(mask),'value':str(v),'payment':str(pay),'slack':str(pay-v)})
    assert all(x>=0 for x in payments)
    assert payments==[F(5,6)*T,F(3,4)*T]
    assert sum(payments)==F(19,12)*T
    assert sum(payments)-T==F(7,12)*T
    assert detail[0]['p_coefficients']==fmt([T,F(0)])
    assert detail[1]['p_coefficients']==fmt([T,-T])
    assert all(d['m_coefficients']==fmt([T,-T]) for d in detail)
    assert detail[0]['r_coefficients']==fmt([T,-T,T])
    assert detail[1]['r_coefficients']==fmt([T,-T,F(0)])
    return {'bundles':[[str(x) for x in bi] for bi in b],'T':str(T),'masks':rows,'polynomials':detail,'payments':[str(x) for x in payments],'total':str(sum(payments)),'subsidy':str(sum(payments)-T),'coalitions':coalitions}

high=((F(3),F(0)),(F(0),F(2)))
low=((F(1),F(0)),(F(0),F(2)))
H=evaluate(high);L=evaluate(low)
assert high[1]==low[1] and all(x<=y for x,y in zip(low[0],high[0]))
assert F(L['payments'][0])<=F(H['payments'][0])
assert H['masks'][1]['selected_form']==1 # owner 1 excluded, owner 2 included.
assert dot(V[0],high[0])==3 and H['masks'][1]['capped_contributions'][0]=='2'
assert all(a['masks'][0]['selected_form']==1 for a in [H,L])
# The standard two-owner Shapley allocation is an efficient alternative here.
for a,b in [(H,high),(L,low)]:
    shapley=[(value(b,tuple(int(h==i) for h in range(2)))+value(b,(1,1))-value(b,tuple(int(h!=i) for h in range(2))))/2 for i in range(2)]
    assert sum(shapley)==F(a['T'])
    a['efficient_shapley_alternative']=[str(x) for x in shapley]
result={'scope':'Two specified report profiles and the existing capped mechanism with j=2; illustration, not a universal proof or subsidy lower bound.','forms_in_priority_order':[[str(x) for x in v] for v in V],'profiles':{'full':H,'underreport':L},'checks':{'exact_rational_arithmetic':True,'all_four_masks_per_profile':True,'fixed_forms_owners_priority':True,'all_four_coalitions_per_profile':True,'cap_binding_at_full_report':True,'one_owner_underreport_payment_nonincrease':True,'efficient_alternative_exists':True},'new_theorem_or_source_priority_claim':False}
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
text=json.dumps(result,indent=2)+'\n'
if args.output:args.output.write_text(text)
print(text)
