"""Independent optimization route for finite diameter checks, floating only.
Selector solver reused from preceding gate and explicitly distinguished from proof.
"""
from pathlib import Path
from fractions import Fraction
import json
import numpy as np
from scipy.optimize import linprog
from selector_lp import core,selector
P=Path(__file__).parent

def main():
    cases=json.loads((P/'exact_checks.json').read_text())['cases'];out=[];lps=0
    for case in cases:
        A=np.array([[float(Fraction(v)) for v in row] for row in case['exposures']]);n=len(A)
        M,v,T,b=core(A);norms=np.linalg.norm(M@A,axis=1)
        r={'name':case['name'],'n':n}
        if n<=8:
            radius=-1
            for mask in range(2**(n-1)):
                signs=np.array([1]+[1 if (mask>>j)&1 else -1 for j in range(n-1)])
                fit=linprog(-signs,A_ub=M,b_ub=norms,A_eq=np.ones((1,n)),b_eq=[0],bounds=list(zip(-b,b)),method='highs');lps+=1
                if not fit.success:raise RuntimeError(fit.message)
                radius=max(radius,-fit.fun)
            measured=2*radius/T;expected=np.sqrt(float(Fraction(case['normalized_diameter_squared'])))
            if abs(measured-expected)>1e-8:raise RuntimeError('diameter mismatch')
            r.update(diameter_lp=measured,diameter_formula=expected,diameter_absolute_error=abs(measured-expected))
        if n<=6 or case.get('spectrum_gate') and case.get('owner_gate'):
            x,_,ex=selector(M,v,T,'ascending');z,_,ez=selector(M,v,T,'descending')
            rho=float(np.abs(x-z).sum()/T);G=sum(np.outer(a,a)/bi for a,bi in zip(A,b));bound=2*np.sqrt(np.linalg.eigvalsh(G)[-1]/T)
            if rho>bound+1e-8:raise RuntimeError('spectral bound failure')
            r.update(selector_rho=rho,spectral_bound=bound,selector_residual=max(ex,ez),x=x.tolist(),z=z.tolist())
            if case.get('full_selectors_exact') and max(np.max(np.abs(x-1)),np.max(np.abs(z-1)))>1e-8:raise RuntimeError('coincidence calibration failed')
        out.append(r)
    payload={'evidence':'Floating LP checks, not proof; exhaustive sign objectives for finite books n<=8.','diameter_lp_count':lps,'cases':out,'all_checks_passed':True}
    (P/'lp_checks.json').write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps({'diameter_lp_count':lps,'cases':len(out),'all_checks_passed':True}))
if __name__=='__main__':main()
