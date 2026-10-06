#!/usr/bin/env python3
"""Exact finite tests of the pairwise probability bound; not its general proof."""
from fractions import Fraction as Q
from math import factorial,prod
from pathlib import Path
import argparse,json,itertools,hashlib


def cdf(weights,t):
 weights=[Q(w) for w in weights if w]
 if not weights:return Q(t>=0)
 n=len(weights);total=Q(0)
 for flags in itertools.product((0,1),repeat=n):
  left=max(Q(0),Q(t)-sum(w*b for w,b in zip(weights,flags)))
  total+=(-1)**sum(flags)*left**n
 return total/(factorial(n)*prod(weights))


def q(rho):
 n=rho.numerator//rho.denominator;theta=rho-n
 if not theta:return Q(1,factorial(n+1))
 return (1-(1-theta)**(n+2))/(theta*factorial(n+2))

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=[]
for rho in (Q(2),Q(5,2),Q(3),Q(13,4)):
 n=int(rho);theta=rho-n
 extremal=[Q(1)]*n+([theta] if theta else [])
 for long in (extremal,[x/2 for x in extremal for _ in (0,1)]):
  for short in ([Q(1)],[Q(1,2)]*2,[Q(1,4),Q(1,4),Q(1,2)]):
   # Reflection of short uniforms: X_long<X_short iff
   # X_long+sum a_i(1-U_i)<sum a_i=1.
   actual=cdf(long+short,Q(1));bound=q(rho)
   if not actual<=bound:raise ValueError('pairwise probability bound fails')
   if long==extremal and len(short)==1 and actual!=bound:raise ValueError('sharp pairwise case fails')
   out.append({'rho':str(rho),'long':list(map(str,long)),'short':list(map(str,short)),'actual':str(actual),'bound':str(bound)})
report={'status':'EXACT_FINITE_PROBABILITY_CHECKS_PASS','cases':out,'limitation':'Finite checks and sharp examples support the formula; the written convexity/vertex proof proves the unrestricted inequality.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(out),'exact probability comparisons')
