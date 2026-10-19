"""Finite-instance LP diagnostics, followed by exact rational certificate checks.

SciPy locates candidate optima numerically. Fraction arithmetic independently
checks all primal constraints and dual coefficient identities; neither step
extends the paper's universal statements or resolves historical priority.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import scipy
from scipy.optimize import linprog

root = Path(__file__).resolve().parents[1]
if root.name == 'acyclicity_ijgt':
    labels = ('L0','O1','L1','R1')
    A = {('O1','O1'):2, ('O1','R1'):2}
    B = {('O1','O1'):2, ('O1','L1'):2}
    C = {('L0','L0'):1, ('L1','L1'):1, ('R1','R1'):1,
         ('R1','L1'):1, ('L0','O1'):1}
    target = lambda a,j: (F(4) if j=='O1' else F(1,2)) if a==0 else F(1)
else:
    assert root.name == 'static_subsidies_ijgt'
    labels = (0,1,2)
    A = {(j,j):1 for j in labels}
    B = A.copy()
    C = A.copy()
    A[0,1], B[0,2], C[1,2] = 2,1,2
    target = lambda a,j: F(3)
players = list(product(range(3), labels))
teams = list(product(labels, repeat=3))
def worth(t):
    a,b,c = t
    return A.get((a,b),0)+B.get((a,c),0)+C.get((b,c),0)
T = sum(worth((j,j,j)) for j in labels)
incidence = [[int(t[a]==j) for a,j in players] for t in teams]
values = list(map(worth,teams))
def rat(x):
    return F(str(float(x))).limit_denominator(1000000)
certificates = []
for i,(a,j) in enumerate(players):
    objective = [-int(k==i) for k in range(len(players))]
    result = linprog(objective, A_ub=[[-v for v in row] for row in incidence],
                     b_ub=[-v for v in values], A_eq=[[1]*len(players)],
                     b_eq=[T], bounds=(0,None), method='highs')
    assert result.success, result.message
    H = target(a,j)
    assert abs(-result.fun-float(H)) < 1e-9
    x = list(map(rat,result.x))
    lam = [-rat(v) for v in result.ineqlin.marginals]
    mu = -rat(result.eqlin.marginals[0])
    residual = list(map(rat,result.lower.marginals))
    assert min(x)>=0 and sum(x)==T and x[i]==H
    assert all(sum(c*v for c,v in zip(row,x))>=w for row,w in zip(incidence,values))
    assert min(lam)>=0 and min(residual)>=0
    # mu*1 - incidence^T*lambda - residual = unit_i.
    # For any nonnegative core point, this yields x_i <= mu*T-lambda*worth.
    assert all(mu-sum(lam[e]*incidence[e][k] for e in range(len(teams)))
               -residual[k] == int(k==i) for k in range(len(players)))
    assert mu*T-sum(l*w for l,w in zip(lam,values)) == H
    certificates.append({'player':{'sector':a+1,'label':j}, 'maximum':str(H),
        'numerical_status':int(result.status), 'exact_primal':list(map(str,x)),
        'dual_mu':str(mu),
        'dual_lambda_nonzero':[{'team':list(t),'weight':str(l)}
                               for t,l in zip(teams,lam) if l],
        'dual_residual':list(map(str,residual)), 'exact_primal_and_dual_checks':'PASS'})
report = {'result':'PASS', 'scope':'Finite worked-example upper bounds only; numerical LP diagnostic followed by exact rational primal/dual checks. No universal proof or priority claim.',
          'solver':'scipy.optimize.linprog(method=highs)', 'scipy_version':scipy.__version__,
          'source_sha256':hashlib.sha256((root/'submission/manuscript.tex').read_bytes()).hexdigest(),
          'players':len(players), 'all_full_team_inequalities':len(teams), 'T':T,
          'coordinate_maximizations':len(players), 'all_exact_certificates_verified':True,
          'certificate_identity':'mu*1 - incidence^T*lambda - residual = unit_i; lambda,residual >= 0; upper bound mu*T-lambda*worth = H_i',
          'unchanged_analytic_upper_bound':'Simplex necessity and weak-player equalities' if root.name.startswith('acyc') else 'Diagonal tightness',
          'certificates':certificates}
print(json.dumps(report,indent=2))
