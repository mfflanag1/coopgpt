#!/usr/bin/env python3
from pathlib import Path
from fractions import Fraction as F
import runpy,contextlib,io,json
with contextlib.redirect_stdout(io.StringIO()):
 ns=runpy.run_path(str(Path(__file__).with_name('CONE_CHECK_LORENTZ_PHI.py')))
Q,c,phi=ns['Q'],ns['c'],ns['phi']
z=F(17,19);N=200
lo=2*sum((z**(2*k+1)/F(2*k+1) for k in range(N)),F(0))
hi=lo+2*z**(2*N+1)/(F(2*N+1)*(1-z*z))
# The factor is decreasing in L=log18 because4phi-13<0.
assert 4*phi-13<0
bound_low=24*phi*hi/(4*phi+24*hi-13)
bound_high=24*phi*lo/(4*phi+24*lo-13)
assert F(1786,1000)<bound_low<=bound_high<F(1787,1000)
# Exact endpoint odds and affine-elimination identities.
a,bb=F(1,7),F(3,4)
assert bb*(1-a)/(a*(1-bb))==18
assert 2*a/(1+a)==F(1,4)
for LL in [lo,hi,F(3)]:
 lam=6*LL/(phi+6*LL-F(13,4))
 assert lam*phi==6*LL-lam*(6*LL-F(13,4))
 assert lam*phi==24*phi*LL/(4*phi+24*LL-13)
out={'status':'PASS','arithmetic':'Fraction atanh-series bounds and Q(sqrt5)',
 'series_terms':N,'lower_bound':'24 phi log18/(4phi+24log18-13) > 1.786',
 'scope':'Restricted constant-reserve regular radial class in exposure dimension at least2; not all mechanisms.'}
Path(__file__).with_name('CONE_RADIAL_BARRIER_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
