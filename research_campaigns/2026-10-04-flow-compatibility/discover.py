"""Eight fixed preregistered capacity games, stopping at first obstruction.
SciPy discovery; exact rational certificates checked here and independently.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from scipy.optimize import linprog


def require(ok, why):
    if not ok:
        raise ValueError(why)


ROOT = Path(__file__).resolve().parent
REGISTRY = json.loads((ROOT/'INSTANCES.json').read_text())
CASES = [(c['id'],c['edges']) for c in REGISTRY['cases']]


def rat(x):
    return F(float(x)).limit_denominator(100000)


def run_case(case_id, edges):
    start = time.monotonic()
    m = len(edges)
    inner = sorted({u for e in edges for u in e[:2]} - {'s','t'})
    cuts = []
    for mask in range(1 << len(inner)):
        side = {'s'} | {v for j,v in enumerate(inner) if mask >> j & 1}
        cuts.append([j for j,(u,v,c) in enumerate(edges) if u in side and v not in side])
    values = [min(sum(edges[j][2] for j in cut if mask >> j & 1) for cut in cuts)
              for mask in range(1 << m)]
    total = values[-1]
    require(total > 0, 'Nonpositive grand flow')
    coal = np.array([[int(mask >> j & 1) for j in range(m)] for mask in range(1 << m)],dtype=float)
    def solve(c, floor, equalities):
        left = 300 - (time.monotonic()-start)
        require(left > 0, 'Instance deadline')
        return linprog(c, A_ub=-coal, b_ub=-np.array(values,dtype=float),
            A_eq=np.array([a for a,b in equalities],dtype=float) if equalities else None,
            b_eq=np.array([float(b) for a,b in equalities]) if equalities else None,
            bounds=[(float(x),None) for x in floor], method='highs',
            options={'time_limit':min(60,left)})
    def certificate(res, c, floor, efficient):
        require(res.success, 'LP not optimal: '+res.message)
        x = list(map(rat,res.x))
        w = [(mask,-rat(z)) for mask,z in enumerate(res.ineqlin.marginals) if abs(z)>1e-9]
        nu = rat(res.eqlin.marginals[0]) if efficient else F(0)
        mu = [F(c[j])-nu-sum((q for mask,q in w if mask >> j & 1),F(0)) for j in range(m)]
        require(all(x[j] >= floor[j] for j in range(m)), 'Rational lower bound failure')
        require(not efficient or sum(x)==total, 'Rational efficiency failure')
        require(all(sum((x[j] for j in range(m) if mask>>j&1),F(0))>=v for mask,v in enumerate(values)), 'Rational cover failure')
        require(all(q>=0 for mask,q in w) and min(mu)>=0, 'Rational dual sign failure')
        pobj = sum((F(a)*b for a,b in zip(c,x)),F(0))
        dobj = sum((values[mask]*q for mask,q in w),F(0))+nu*total+sum((a*b for a,b in zip(mu,floor)),F(0))
        require(pobj==dobj,'Rational duality gap')
        return {'x':list(map(str,x)),'weights':[[mask,str(q)] for mask,q in w],
                'efficiency_price':str(nu),'lower_prices':list(map(str,mu)),
                'objective':str(pobj)}
    ideals=[]
    h=[]
    for i in range(m):
        c=[-int(i==j) for j in range(m)]
        cert=certificate(solve(c,[F(0)]*m,[([1]*m,total)]),c,[F(0)]*m,True)
        ideals.append(cert)
        h.append(-F(cert['objective']))
    floor=[q/3 for q in h]
    protected=certificate(solve([1]*m,floor,[]),[1]*m,floor,False)
    joint={}
    for role in ('source','sink'):
        ids=[j for j,(u,v,c) in enumerate(edges) if (u=='s' if role=='source' else v=='t')]
        c=[-int(j in ids) for j in range(m)]
        cert=certificate(solve(c,[F(0)]*m,[([1]*m,total)]),c,[F(0)]*m,True)
        best=-F(cert['objective'])
        target=sum((h[j] for j in ids),F(0))
        require(best<=target,'Endpoint support exceeds ideals')
        joint[role]={'status':'EXACT_FEASIBLE' if best==target else 'EXACT_OBSTRUCTION',
          'indices':ids,'max_sum':str(best),'sum_ideals':str(target),
          'gap':str(target-best),'certificate':cert}
    subsidy=F(protected['objective'])-total
    return {'id':case_id,'edges':edges,'T':total,'coalitions':len(values),
            'H':list(map(str,h)),'ideal_certificates':ideals,'protected_certificate':protected,
            'subsidy':str(subsidy),'ratio':str(subsidy/total),'joint_attainment':joint,
            'elapsed_seconds':time.monotonic()-start}


if __name__=='__main__':
    cases=[]
    for pair in CASES:
        case=run_case(*pair)
        cases.append(case)
        report={'status':'PASS','cases':cases,
          'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'registry_sha256':hashlib.sha256((ROOT/'INSTANCES.json').read_bytes()).hexdigest(),
          'solver_retries':0,'scope':'Fixed games, all coalitions, exact rational primal-dual certificates.'}
        (ROOT/'DISCOVERY.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:case[k] for k in ('id','T','H','subsidy','joint_attainment')}),flush=True)
        if any(z['status']=='EXACT_OBSTRUCTION' for z in case['joint_attainment'].values()):
            break
