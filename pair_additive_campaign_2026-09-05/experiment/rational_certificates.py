"""Produce and verify plain rational LP certificates without a symbolic solver."""
from fractions import Fraction as F
from itertools import product
import json
import numpy as np
from scipy.optimize import linprog
from pilot import ROOT, require

def fraction(x):
    return F(float(x)).limit_denominator(10**7)

def dot(a,b):
    return sum((x*y for x,y in zip(a,b)),F(0))

def make_core(record):
    n=9; rows=[]; eq=[dict(label='efficiency',a=[F(1)]*n,b=F(record['T']))]
    for i in range(n):
        a=[F(0)]*n;a[i]=F(-1)
        rows.append(dict(label=f'nonnegative_{i}',a=a,b=F(0)))
    for i,j,k in product(range(3),repeat=3):
        a=[F(0)]*n
        for h in (i,3+j,6+k):a[h]=F(-1)
        rows.append(dict(label=f'triple_{i+1}_{j+1}_{k+1}',a=a,b=-F(record['weights'][i][j][k])))
    return rows,eq

def certify(rows,eq,c,label):
    A=[r['a'] for r in rows];b=[r['b'] for r in rows]
    E=[r['a'] for r in eq];e=[r['b'] for r in eq]
    result=linprog(np.array(c,dtype=float),A_ub=np.array(A,dtype=float),b_ub=np.array(b,dtype=float),A_eq=np.array(E,dtype=float),b_eq=np.array(e,dtype=float),bounds=[(None,None)]*len(c),method='highs')
    require(result.success,'LP discovery failed '+label)
    point=list(map(fraction,result.x));alpha=list(map(fraction,result.ineqlin.marginals));beta=list(map(fraction,result.eqlin.marginals))
    require(all(a<=0 for a in alpha),'wrong dual signs')
    require(all(dot(a,point)<=v for a,v in zip(A,b)),'rational primal inequality failure '+label)
    require(all(dot(a,point)==v for a,v in zip(E,e)),'rational primal equality failure '+label)
    require(all(sum(alpha[r]*A[r][j] for r in range(len(A)))+sum(beta[r]*E[r][j] for r in range(len(E)))==c[j] for j in range(len(c))),'rational dual coefficient failure '+label)
    objective=dot(c,point)
    require(dot(alpha,b)+dot(beta,e)==objective,'rational dual objective failure '+label)
    return dict(label=label,primal=point,objective=objective,objective_coefficients=c,extra_inequality_rows=rows[36:],extra_equalities=eq[1:],inequality_multipliers=[dict(row=rows[i]['label'],multiplier=v) for i,v in enumerate(alpha) if v],equality_multipliers=[dict(row=eq[i]['label'],multiplier=v) for i,v in enumerate(beta) if v],verified=True)

def main():
    record=json.loads((ROOT/'reduced_counterexample.json').read_text());rows,eq=make_core(record)
    certificates=[]
    for i,h in enumerate(map(F,record['core_maxima'])):
        c=[F(0)]*9;c[i]=-1
        cert=certify(rows,eq,c,f'H_{i}')
        require(cert['objective']==-h,'coordinate ideal mismatch')
        certificates.append(cert)
    for key,upward in [('Lmin',True),('Lmax',False)]:
        fixed={}
        for stage in record[key+'_stages']:
            value=F(stage['level']);free=[i for i in range(9) if i not in fixed]
            prefix=eq+[dict(label=f'fixed_{i}',a=[F(int(i==j)) for j in range(9)],b=v) for i,v in fixed.items()]
            extended=[dict(label=r['label'],a=r['a']+[F(0)],b=r['b']) for r in rows]
            extended_eq=[dict(label=r['label'],a=r['a']+[F(0)],b=r['b']) for r in prefix]
            for i in free:
                a=[F(0)]*10;a[i]=-1 if upward else 1;a[-1]=1 if upward else -1
                extended.append(dict(label=f'level_cap_{i}',a=a,b=F(0)))
            c=[F(0)]*10;c[-1]=-1 if upward else 1
            cert=certify(extended,extended_eq,c,f'{key}_level_{value}')
            require(cert['objective']==(-value if upward else value),'level mismatch')
            certificates.append(cert)
            face=list(rows)
            for i in free:
                a=[F(0)]*9;a[i]=-1 if upward else 1
                face.append(dict(label=f'face_cap_{i}',a=a,b=-value if upward else value))
            for i in stage['players']:
                c=[F(0)]*9;c[i]=-1 if upward else 1
                cert=certify(face,prefix,c,f'{key}_pinned_{i}_at_{value}')
                require(cert['objective']==(-value if upward else value),'pinned bound mismatch')
                certificates.append(cert)
            fixed.update({i:value for i in stage['players']})
    active={}
    for key in ('Lmin','Lmax'):
        point=list(map(F,record[key]))
        active[key]=[r['label'] for r in rows if dot(r['a'],point)==r['b']]
    output=dict(scope='36 raw nonnegativity/triple inequalities plus integral total8; exact rational primal/dual coefficient identities; full selectors with every pinned coordinate and every H_i',certificates=certificates,active_constraints=active,core_rows=rows,efficiency=eq)
    (ROOT/'rational_certificates.json').write_text(json.dumps(output,indent=2,default=str)+'\n')
    print('PASS',len(certificates),'rational LP dual certificates; no symbolic solver used in certificate checks',flush=True)

if __name__=='__main__':main()
