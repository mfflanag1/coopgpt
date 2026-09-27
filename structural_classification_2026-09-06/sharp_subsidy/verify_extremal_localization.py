"""Exact real-domain audit of the near-two-fifths localization proof."""
import json,sys

def main():
    if "--smt" not in sys.argv:
        print(json.dumps({"status":"SKIPPED","reason":"optional --smt; conventional proof is EXTREMAL_LOCALIZATION.md"}));return
    import z3
    Q=lambda a,b=1:z3.RealVal(a)/b
    B,h,g,z=z3.Reals('B h g z')
    claims=[]
    # B<=1: the existing quadratic gap is >=1/10 for each active-sector count.
    for q in (1,2,3):claims.append(([h>=3,B>=0,B<=1],h/Q(10)-h*(3+(q-2)*B)/100))
    # B>=1, q=1,2: finite corrections and any excess cycle donors are retained.
    claims.append(([h>=3,g>=0],h*Q(13,100)-Q(1,5)+h*g*Q(119,100)))
    claims.append(([h>=3,g>=0],h*Q(13,200)+Q(4,5)+h*g*Q(119,100)))
    # q=3: z=A(B)+variance>=0. The two min branches bound the parameter increase.
    claims.append(([z>=0,g>=0,z+g<=1],z+Q(6,5)*g-(z+g)*(5+g)/100))
    claims.append(([z>=0,g>=0,z+g>=1],z+Q(6,5)*g-(5+g)/100))
    # Quantitative recovery of the leaf density from A(B).
    A=Q(2,3)*(Q(3,2)-B)*(B-Q(3,5))
    claims.append(([B>=1,B<=Q(3,2)],A-Q(4,15)*(Q(3,2)-B)))
    for assumptions,gap in claims:
        solver=z3.SolverFor('QF_NRA');solver.add(*assumptions,gap<0)
        if solver.check()!=z3.unsat:raise ValueError('localization inequality false/unknown')
    print(json.dumps({'status':'PASS','exact_real_queries':len(claims),'scope':'scalar localization inequalities; conventional proof supplies construction and asymptotic implication'}))
if __name__=='__main__':main()
