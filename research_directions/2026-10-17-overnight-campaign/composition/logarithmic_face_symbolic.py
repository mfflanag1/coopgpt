#!/usr/bin/env python3
"""Polynomial exact symbolic representation of the general full-OUT payments.

Rational input -> rational hinge lists plus named constant c and log/min syntax.
Decimal evaluation is a display/check aid, NOT an exact rounded payment rule.
"""
from fractions import Fraction as Q
from decimal import Decimal,localcontext
import argparse,json
from pathlib import Path

def require(ok,msg):
    if not ok:raise ValueError(msg)
def envelope(lines):
    lines=sorted(set((Q(a),Q(b)) for a,b in lines));require(lines,'no forms')
    require(all(a>=0 and b>=0 for a,b in lines),'negative coefficient')
    cuts={Q(0),Q(1)}
    for i,(a,b) in enumerate(lines):
        for x,y in lines[i+1:]:
            if b!=y:
                s=(x-a)/(b-y)
                if 0<s<1:cuts.add(s)
    cuts=sorted(cuts);segments=[]
    for lo,hi in zip(cuts,cuts[1:]):
        mid=(lo+hi)/2;line=min(lines,key=lambda p:(p[0]+p[1]*mid,p))
        if segments and segments[-1][2:]==line:segments[-1]=(segments[-1][0],hi,*line)
        else:segments.append((lo,hi,*line))
    alpha=segments[0][2];beta=segments[-1][3];hinges=[]
    for prev,nxt in zip(segments,segments[1:]):
        s=prev[1];delta=prev[3]-nxt[3]
        require(delta>0 and prev[2]+prev[3]*s==nxt[2]+nxt[3]*s,'concave seam')
        hinges.append((s,delta))
    return {'alpha':alpha,'beta':beta,'hinges':hinges,'segments':segments}

def symbolic(forms,owners):
    forms=[tuple(map(Q,a)) for a in forms];owners=[tuple(map(Q,b)) for b in owners]
    require(forms and forms[0],'nonempty forms and resource dimension')
    d=len(forms[0]);require(all(len(a)==d and all(x>=0 for x in a) for a in forms),'invalid forms')
    require(all(len(b)==d and all(x>=0 for x in b) for b in owners),'invalid reports')
    C=[sum(b[j] for b in owners) for j in range(d)];faces=[]
    for j in range(d):
        if C[j]==0:faces.append(None);continue
        lines=[(a[j]*C[j],sum(a[l]*C[l] for l in range(d) if l!=j)) for a in forms]
        faces.append(envelope(lines))
    return {'constant':'c is unique root in (1/2,1) of c*(2-exp(-1/c))=1',
            't0':'1/c-1','psi':'z=min(s,t0); (1-c)*z-c*(1-z)*log(1-z)',
            'face_formula':'H_j=alpha+beta*c+sum(delta*psi(s))',
            'payment_formula':'y_i=sum_j b_ij/C_j*H_j over C_j>0',
            'aggregate':C,'faces':faces,'owner_coefficients':[[b[j]/C[j] if C[j] else Q(0) for j in range(d)] for b in owners]}

def decimal_constant(precision=80):
    with localcontext() as ctx:
        ctx.prec=precision+15;lo=Decimal('0.5');hi=Decimal(1)
        for _ in range(4*(precision+15)):
            mid=(lo+hi)/2;f=mid*(2-(-1/mid).exp())-1
            if f<0:lo=mid
            else:hi=mid
        return +(lo+hi)/2

def decimal_value(packet,precision=80):
    """Numerical display only; returned values do not define the exact mechanism."""
    with localcontext() as ctx:
        ctx.prec=precision
        c=decimal_constant(precision);t0=1/c-1
        def dec(x):x=Q(x);return Decimal(x.numerator)/Decimal(x.denominator)
        values=[]
        for face in packet['faces']:
            if face is None:values.append(Decimal(0));continue
            v=dec(face['alpha'])+dec(face['beta'])*c
            for s,delta in face['hinges']:
                z=min(dec(s),t0);psi=(1-c)*z-c*(1-z)*(1-z).ln();v+=dec(delta)*psi
            values.append(v)
        payments=[sum((dec(a)*v for a,v in zip(row,values)),Decimal(0)) for row in packet['owner_coefficients']]
        return {'constant':c,'cutoff':t0,'face_values':values,'payments':payments,'numerical_only':True}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('--display-digits',type=int)
    args=parser.parse_args();data=json.loads(args.input.read_text());result=symbolic(data['forms'],data['owners'])
    if args.display_digits:result['display']=decimal_value(result,args.display_digits)
    print(json.dumps(result,default=str,indent=2))
if __name__=='__main__':main()
