#!/usr/bin/env python3
"""Independent exact replay; imports neither candidate builder nor optimizer."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import hashlib,json
ROOT=Path('/private/tmp/coopgpt-ownership-20261016')
SOURCE=ROOT/'root/capped_grid_general/certificate.json'

def require(test,message):
    if not test: raise RuntimeError(message)

def taylor_negative(x,degree):
    require(x>=0,'Taylor domain')
    return sum(((-x)**j / factorial(j) for j in range(degree+1)),Q(0))

def main():
    cert=json.loads(SOURCE.read_text())
    total_s=128; total_delta=8
    pmax=Q(51,40); zmax=Q(148,125); dmax=Q(23,125)
    e_lower=sum((Q(1,factorial(j)) for j in range(9)),Q(0))
    e_upper=e_lower+Q(1,factorial(9))*Q(10,9)
    C_lower=1+1/(2*e_upper); C_upper=1+1/(2*e_lower)
    K_upper=e_upper-1
    require(C_upper<zmax and C_upper-1<dmax,'C interval enclosure')
    require(K_upper**2<3,'negative-saving argument enclosure')
    require(Q(cert['PB'])==pmax and cert['target']=='13/8','target metadata')
    require(cert['S_intervals']==total_s and cert['delta_intervals']==total_delta,'partition metadata')
    require(len(cert['cells'])==total_s*total_delta,'complete rectangle count')
    bounds=[]; empty=0; max_residual=Q(0)
    for index,cell in enumerate(cert['cells']):
        sk,dk=divmod(index,total_delta)
        s0=1+(pmax+zmax-1)*sk/total_s
        s1=1+(pmax+zmax-1)*(sk+1)/total_s
        delta0=dmax*dk/total_delta;delta1=dmax*(dk+1)/total_delta
        require(tuple(Q(cell[k]) for k in ('s_lo','s_hi','d_lo','d_hi'))==(s0,s1,delta0,delta1),'rectangle endpoints')
        impossible=s0>pmax+C_upper-delta0
        if 'empty_reason' in cell:
            require(impossible,'invalid omitted rectangle')
            empty+=1;continue
        u=Q(cell['u']);require(0<u<1,'dual scalar domain')
        q_lower=taylor_negative(1/u-1,25)/2
        q_upper=taylor_negative(1/u-1,24)/2
        a_lower=1-q_upper*(1+1/u)
        a_upper=1-q_lower*(1+1/u)
        require(0<q_lower<=q_upper and 0<a_lower<=a_upper,'positive scalar support coefficients')
        lambda_upper=1-q_lower*(1+1/u-1/s0)
        eta_upper=q_upper/s0
        linear=K_upper*eta_upper
        quadratic=K_upper**2*eta_upper**2/(4*a_lower)
        saving_lower=Q(2,5)*taylor_negative(s1-1+delta1,25)
        require(lambda_upper>0 and saving_lower>0,'positive interval bounds')
        # Columns: physical M, local total Z, negative gap v, negative local Zm, auxiliary t.
        rows=[
            ('M <= Z',(1,-1,0,0,0),0),
            ('Z <= Cupper M',(-C_upper,1,0,0,0),0),
            ('S <= pmax+Z',(0,-1,0,0,0),pmax-s0),
            ('hardware role, power<=M',(-1,1,1,0,0),1),
            ('hardware role, power<=1/2',(0,1,1,0,0),Q(3,2)),
            ('negative owned capacity',(0,0,1,1,0),1),
            ('subset hardware role',(Q(4,3),0,1,-1,0),Q(4,3)),
            ('negative payments subset',(0,-1,0,1,0),0),
            ('linear outgoing branch',(0,-linear,0,linear,1),0),
            ('quadratic outgoing branch',(0,-quadratic-a_upper,0,quadratic,1),a_upper*(pmax-s0)),
            ('M <= hardware',(1,0,0,0,0),1),
            ('delta <= delta1',(C_lower,-1,0,0,0),delta1),
            ('delta >= delta0',(-C_upper,1,0,0,0),-delta0),
        ]
        weights=tuple(map(Q,cell['weights']))
        require(len(weights)==len(rows) and all(y>=0 for y in weights),'nonnegative dual multipliers')
        target=(Q(0),Q(0),lambda_upper-saving_lower,Q(0),Q(1))
        caps=(Q(1),zmax,Q(1),zmax,linear*zmax)
        residual=tuple(max(Q(0),target[j]-sum((weights[k]*Q(rows[k][1][j]) for k in range(len(rows))),Q(0))) for j in range(5))
        bound=1+lambda_upper*(s1-1)
        bound+=sum((weights[k]*Q(rows[k][2]) for k in range(len(rows))),Q(0))
        bound+=sum((residual[j]*caps[j] for j in range(5)),Q(0))
        require(residual==tuple(map(Q,cell['residual'])),'recorded residual mismatch')
        require(bound==Q(cell['upper']),'recorded upper mismatch')
        require(bound<Q(13,8),'interval funding target')
        bounds.append(bound);max_residual=max(max_residual,*residual)
    require(cert['nonempty']==len(bounds) and cert['rectangles']==len(cert['cells']),'count metadata')
    require(Q(cert['max_upper'])==max(bounds),'recorded maximum')
    # Independently rounded exact constants for the analytic pi tail.
    require(taylor_negative(Q(148,125),15)>Q(153,500),'inner tail exp lower')
    require(taylor_negative(Q(153,500),12)<Q(737,1000),'outer tail exp upper')
    require(taylor_negative(Q(11,40),12)<Q(19,25),'grid coefficient exp upper')
    high_grid=1+Q(19,50)*(Q(51,40)+Q(737,2000))
    require(high_grid==Q(162453,100000)<Q(13,8),'high grid rational target')
    result={
      'status':'PASS','arithmetic':'fractions.Fraction, no optimizer imports',
      'rectangles':len(cert['cells']),'certified_nonempty':len(bounds),'proved_empty':empty,
      'max_upper':str(max(bounds)),'max_upper_display':float(max(bounds)),
      'analytic_high_grid_upper':str(high_grid),
      'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
