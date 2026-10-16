#!/usr/bin/env python3
"""Reproduce scalar diagnostics for the analytic universal gain proof."""
from math import exp
from pathlib import Path
import json

def require(condition, message='validation failed'):
    if not condition:
        raise AssertionError(message)

def run():
    c=.5/exp(1);rows=[]
    for rho in [2.001,2.1,2.2,2.5,3,3.5,4,5,8,16,64]:
        q=.5*exp(1-rho);delta=c-q*(rho-1)
        g=q*(2*exp((rho-2)/2)-rho) if rho<=4 else q*(exp(1)*(rho-2)-rho)
        require(rho*g<=2*delta+1e-12, 'validation failed')
        worst=0.
        for k in range(101):
            x=k/100;u=max(0.,min(x,(x+rho-3)/2))
            value=q*(exp(u)*(x+rho-1-2*u)-(x+rho-1))
            require(value<=x*g+1e-12, 'validation failed')
            worst=max(worst,value-x*g)
        rows.append({'rho':rho,'rho_g1_over_delta':rho*g/delta,'largest_convex_chord_residual':worst})
    result={'status':'PASS - finite scalar floating corroboration only','scalar_checks':1111,'records':rows,'scope':'Complete analytic proof in UNIVERSAL_TOTAL_INCREASE_LEMMA.txt'}
    Path(__file__).with_name('universal-total-increase-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
