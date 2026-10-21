"""Exact one-variable veto optimization within the proved even-L family.

Uses Fraction only. The accompanying proof establishes unimodality in J and
the stopping bound, making the reported minimum exhaustive within this family.
This optimizes the selected-coordinate certificate, not the true envelope.
"""
from fractions import Fraction as F
from pathlib import Path
import json


TARGET=F(101,100)


def parameters(L):
    assert L>=4 and L%2==0
    d=2*L*L+9*L-18; k=L+3; n=2*L
    rho=F(n,k*k); ell=F(4*(L-2),d); p=F(3*(L-2),d)
    delta=rho-ell; R=n*p*p/rho
    assert delta==F(2*(L-6)**2,k*k*d) and 0<=delta<F(1,4)
    r=p*k; assert r*r==R and r<F(3,2)*(1-delta)
    return n,k,rho,ell,p,delta,R


def diagonal(L,J,conservative=False):
    n,k,rho,ell,p,delta,R=parameters(L)
    c=J*rho
    return c*c/(1+c)**2+R*c/(1+c-(0 if conservative else delta))**2


def derivative(L,J):
    n,k,rho,ell,p,delta,R=parameters(L)
    c=J*rho; a=1-delta
    return 2*c/(1+c)**3+R*(a-c)/(a+c)**3


def optimize_J(L):
    n,k,rho,ell,p,delta,R=parameters(L)
    if R<=2:return None
    # Actual critical c is below the conservative one R/(R-2).
    upper=R/(R-2)/rho
    hi=upper.numerator//upper.denominator+2; lo=0
    assert derivative(L,lo)>0 and derivative(L,hi)<0
    while hi-lo>1:
        mid=(hi+lo)//2
        if derivative(L,mid)>0:lo=mid
        else:hi=mid
    best=max([lo,hi],key=lambda J:diagonal(L,J))
    return best


def summary(L,J):
    n,k,rho,ell,p,delta,R=parameters(L)
    value=diagonal(L,J); conservative=diagonal(L,J,True)
    return {'L':L,'base_owners':n,'veto_copies':J,'final_owners':J*n+1,
            'rho':str(rho),'R':str(R),'delta':str(delta),'c':str(J*rho),
            'exact_diagonal_certificate':str(value),'exact_decimal':float(value),
            'conservative_certificate':str(conservative),'conservative_decimal':float(conservative),
            'strictly_above_1_percent':value>TARGET}


def run():
    # D_exact(c)<D_(9/4)(c), and D_(9/4)(c)<=D_(9/4)(5)<1.01 for c<=5.
    assert (F(25)+F(9,4)*5)/36<TARGET
    best=None; feasible=[]; considered=[]; L=4
    while True:
        if best is not None and 5*(L+3)**2>=best['final_owners']-1:
            break
        n,k,rho,ell,p,delta,R=parameters(L)
        effective_R=R/(1-delta)**2
        # Uniform upper envelope avoids irrelevant one-variable optimization.
        can_reach=(effective_R>2 and effective_R**2/(4*(effective_R-1))>TARGET)
        if can_reach:
            optimum=optimize_J(L)
            if optimum is not None and diagonal(L,optimum)>TARGET:
                lo=0; hi=optimum
                while hi-lo>1:
                    mid=(hi+lo)//2
                    if diagonal(L,mid)>TARGET:hi=mid
                    else:lo=mid
                assert diagonal(L,hi)>TARGET and diagonal(L,hi-1)<=TARGET
                entry=summary(L,hi);entry['maximum_J']=optimum
                entry['maximum_certificate']=str(diagonal(L,optimum))
                feasible.append(entry)
                if best is None or entry['final_owners']<best['final_owners']:best=entry
        considered.append(L);L+=2
    assert best is not None
    elegant=[summary(l,5*l+30) for l in [550,560,576,600,640,1000]]
    return {'target':str(TARGET),'scope':'Selected witness certificate only; not a global upper bound on the true own-report envelope.',
            'minimum_owners_within_even_L_family':best,'first_feasible_L':feasible[0]['L'],
            'checked_even_L_range':[4,considered[-1]],'stopping_L':L,
            'stopping_bound':'Every >1% certificate requires c>5, hence N-1>5(L+3)^2.',
            'feasible_minimum_J_entries':feasible,'elegant_candidates':elegant}


if __name__=='__main__':
    result=run();Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['minimum_owners_within_even_L_family','first_feasible_L','checked_even_L_range','stopping_L','elegant_candidates']},indent=2))
