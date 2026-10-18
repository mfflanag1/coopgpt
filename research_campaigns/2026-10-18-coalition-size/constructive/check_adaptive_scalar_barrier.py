"""Exact rational finite replay of the global adaptive-scalar binomial barrier.
No optimizer, floating-point sign, or sampled report claim is used.
"""
from fractions import Fraction as Q
from pathlib import Path
import json

def witness(s):
 assert s>=2
 claimed_K=Q(s*s,4);L=Q(12);epsilon=Q(1)
 B=claimed_K*(L+epsilon+1)/L
 q=Q(16,15*s)
 assert q>Q(1,s)
 assert 3*B*q*q<Q(1)
 a=Q(s-1,s);b=1-q
 # LHS/RHS at M=s. Repeated multiplication finds the first strict rational
 # contradiction; it is a finite certificate, not a floating-point estimate.
 M=s;ratio=Q(1,3*s)/B/(b**(s-1))
 while ratio<=1:
  ratio*=a/b;M+=1
 assert Q(1,3*s)*a**(M-s)>B*b**(M-1)
 return dict(s=s,claimed_K=str(claimed_K),anchor_L=str(L),hard_epsilon=str(epsilon),B=str(B),rational_probability_lower_bound=str(q),hard_coverage_check=str(3*B*q*q),leaves=M,owners=M+5,strict_rational_contradiction=(ratio.numerator>ratio.denominator),ratio_numerator_bits=ratio.numerator.bit_length(),ratio_denominator_bits=ratio.denominator.bit_length(),contradiction_ratio_decimal=float(ratio))

if __name__=='__main__':
 out={'status':'PASS','scope':'report-adaptive single global beta,p only','witnesses':[witness(s) for s in [2,3,4,8,16,32]]}
 Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({**out,'witnesses':[{k:v for k,v in z.items() if k!='contradiction_ratio'} for z in out['witnesses']]},indent=2))
