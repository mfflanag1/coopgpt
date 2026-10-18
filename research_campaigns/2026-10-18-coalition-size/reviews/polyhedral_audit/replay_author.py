"""Exact small certificates for the supplied-partition theorem.

No floating solver or report grid. Coverage is optimized jointly over reports
and feasible production. Every LP maximum has a checked rational dual.
Partition covering is by complete hyperplane-arrangement construction.
"""
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

def dot(a, b):
    return sum((x*y for x,y in zip(a,b)), Q(0))

def solve(matrix, rhs):
    n=len(rhs)
    a=[[Q(v) for v in row]+[Q(rhs[i])] for i,row in enumerate(matrix)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if a[i][j]),None)
        if pivot is None:
            return None
        a[j],a[pivot]=a[pivot],a[j]
        value=a[j][j]
        a[j]=[v/value for v in a[j]]
        for i in range(n):
            if i!=j and a[i][j]:
                factor=a[i][j]
                a[i]=[x-factor*y for x,y in zip(a[i],a[j])]
    return tuple(row[-1] for row in a)

def rank(matrix):
    if not matrix:
        return 0
    a=[[Q(v) for v in row] for row in matrix]
    pivot=0
    for j in range(len(a[0])):
        found=next((i for i in range(pivot,len(a)) if a[i][j]),None)
        if found is None:
            continue
        a[pivot],a[found]=a[found],a[pivot]
        value=a[pivot][j]
        a[pivot]=[v/value for v in a[pivot]]
        for i in range(len(a)):
            if i!=pivot and a[i][j]:
                factor=a[i][j]
                a[i]=[x-factor*y for x,y in zip(a[i],a[pivot])]
        pivot+=1
        if pivot==len(a):
            break
    return pivot

@lru_cache(maxsize=None)
def vertices(H, g):
    dimension=len(H[0])
    found=set()
    for basis in combinations(range(len(H)),dimension):
        point=solve([H[i] for i in basis],[g[i] for i in basis])
        if point is not None and all(dot(row,point)<=bound for row,bound in zip(H,g)):
            found.add(point)
    return tuple(sorted(found))

def lp_max(H, g, objective):
    """Bounded nonempty LP; return a verified rational primal/dual certificate."""
    H=tuple(tuple(Q(v) for v in row) for row in H)
    g=tuple(Q(v) for v in g)
    objective=tuple(Q(v) for v in objective)
    candidates=vertices(H,g)
    assert candidates, "Fixture LP must be bounded and nonempty"
    primal=max(candidates,key=lambda p:dot(objective,p))
    optimum=dot(objective,primal)
    active=[i for i,(row,bound) in enumerate(zip(H,g)) if dot(row,primal)==bound]
    dual=None
    for basis in combinations(active,len(objective)):
        weights=solve([[H[i][j] for i in basis] for j in range(len(objective))],objective)
        if weights is not None and all(w>=0 for w in weights):
            dual=[Q(0)]*len(H)
            for i,w in zip(basis,weights):
                dual[i]=w
            break
    assert dual is not None, "No exact normal-cone certificate found"
    assert all(dot(row,primal)<=bound for row,bound in zip(H,g))
    assert all(v>=0 for v in dual)
    assert tuple(sum(dual[i]*H[i][j] for i in range(len(H))) for j in range(len(objective)))==objective
    assert dot(dual,g)==optimum
    return dict(primal=primal,dual=tuple(dual),optimum=optimum)

def box_constraints(upper):
    m=len(upper)
    H=[];g=[]
    for j,value in enumerate(upper):
        row=[Q(0)]*m;row[j]=1
        H.append(tuple(row));g.append(Q(value))
        row=[Q(0)]*m;row[j]=-1
        H.append(tuple(row));g.append(Q(0))
    return H,g

def arrangement(upper,cuts):
    """All full-dimensional cells of a complete finite hyperplane arrangement."""
    cells=[]
    for signs in product((-1,1),repeat=len(cuts)):
        H,g=box_constraints(upper)
        for sign,(normal,offset) in zip(signs,cuts):
            H.append(tuple(Q(sign)*v for v in normal));g.append(Q(sign)*offset)
        H=tuple(H);g=tuple(g);vs=vertices(H,g)
        if not vs:
            continue
        differences=[[x-y for x,y in zip(v,vs[0])] for v in vs[1:]]
        if rank(differences)!=len(upper):
            continue
        center=tuple(sum(v[j] for v in vs)/len(vs) for j in range(len(upper)))
        assert all(dot(row,center)<bound for row,bound in zip(H,g) if any(row))
        cells.append(dict(H=H,g=g,vertices=vs,center=center,signs=signs))
    # Covering follows from the complete sign enumeration and closure/density
    # argument in the companion note, not from testing random points.
    return cells

def aggregate_matrix(coordinates,coalition,resources):
    return tuple(tuple(Q(owner in coalition and resource==a) for owner,resource in coordinates)
                 for a in range(resources))

def production_value(A,profits,capacity):
    activities=len(profits)
    H=[tuple(Q(v) for v in row) for row in A]
    g=[Q(v) for v in capacity]
    for e in range(activities):
        row=[Q(0)]*activities;row[e]=-1
        H.append(tuple(row));g.append(Q(0))
    return lp_max(H,g,profits)

def coverage_lp(cell,coefficients,intercepts,coordinates,A,profits,coalition):
    m=len(coordinates);activities=len(profits);resources=len(A)
    S=aggregate_matrix(coordinates,coalition,resources)
    H=[tuple(row)+(Q(0),)*activities for row in cell['H']]
    g=list(cell['g'])
    for row_a in range(resources):
        H.append(tuple(-v for v in S[row_a])+tuple(Q(v) for v in A[row_a]))
        g.append(Q(0))
    for e in range(activities):
        row=[Q(0)]*(m+activities);row[m+e]=-1
        H.append(tuple(row));g.append(Q(0))
    aC=tuple(sum(coefficients[i][j] for i in coalition) for j in range(m))
    hC=sum(intercepts[i] for i in coalition)
    cert=lp_max(H,g,tuple(-v for v in aC)+tuple(Q(v) for v in profits))
    cert['shortfall']=cert['optimum']-hC
    # Recover precisely the coverage witnesses in theorem (5).
    u=cert['dual'][:len(cell['H'])]
    p=cert['dual'][len(cell['H']):len(cell['H'])+resources]
    assert all(sum(cell['H'][l][j]*u[l] for l in range(len(u)))
               -sum(S[a][j]*p[a] for a in range(resources))==-aC[j]
               for j in range(m))
    assert all(sum(A[a][e]*p[a] for a in range(resources))>=profits[e]
               for e in range(activities))
    assert dot(cell['g'],u)-hC==cert['shortfall']
    cert['coverage_u']=u;cert['coverage_p']=p
    cert['coalition']=tuple(coalition)
    return cert

def local_incentives(coefficients,coordinates,A,profits,s):
    n=len(coefficients);s=min(s,n)
    tcwm=[];outside=[]
    def negative_sum(scores,excluded,limit):
        values=sorted(v for i,v in enumerate(scores) if i not in excluded and v<0)
        return sum(values[:limit],Q(0))
    for column,(owner,resource) in enumerate(coordinates):
        scores=[coefficients[i][column] for i in range(n)]
        value=scores[owner]+negative_sum(scores,{owner},s-1)
        tcwm.append(dict(coordinate=(owner,resource),margin=value))
    lookup={pair:j for j,pair in enumerate(coordinates)}
    for e,profit in enumerate(profits):
        support=[a for a in range(len(A)) if A[a][e]>0]
        eligible=[[i for i in range(n) if (i,a) in lookup] for a in support]
        for assignment in product(*eligible):
            restoring=set(assignment)
            if len(restoring)>s:
                continue
            scores=[sum(A[a][e]*coefficients[i][lookup[(owner,a)]]
                        for a,owner in zip(support,assignment)) for i in range(n)]
            value=sum(scores[i] for i in restoring)+negative_sum(scores,restoring,s-len(restoring))-profit
            outside.append(dict(activity=e,assignment=assignment,margin=value))
    return dict(tcwm_pass=all(x['margin']>=0 for x in tcwm),
                out_pass=all(x['margin']>=0 for x in tcwm+outside),
                coordinate_tests=tcwm,assignment_tests=outside)

def check_candidate(name,cells,coordinates,A,profits,coefficients,intercepts,kappa):
    n=len(coefficients[0]);m=len(coordinates);resources=len(A)
    nonnegative=[];funding=[];coverage=[];continuity=[];local=[]
    for t,cell in enumerate(cells):
        for vertex in cell['vertices']:
            values=[dot(coefficients[t][i],vertex)+intercepts[t][i] for i in range(n)]
            nonnegative.append(min(values))
            S=aggregate_matrix(coordinates,set(range(n)),resources)
            capacity=tuple(dot(row,vertex) for row in S)
            cert=production_value(A,profits,capacity)
            excess=sum(values)-kappa*cert['optimum']
            funding.append(dict(cell=t,vertex=vertex,value=cert['optimum'],
                                excess=excess,production_certificate=cert))
            if cert['optimum']==0 and excess<=0 and all(y>=0 for y in values):
                assert all(y==0 for y in values)
        for size in range(1,n+1):
            for coalition in combinations(range(n),size):
                cert=coverage_lp(cell,coefficients[t],intercepts[t],coordinates,A,profits,coalition)
                cert['cell']=t
                coverage.append(cert)
        local.append({str(s):local_incentives(coefficients[t],coordinates,A,profits,s)
                      for s in range(1,n+1)})
    for t,u in combinations(range(len(cells)),2):
        intersection=vertices(cells[t]['H']+cells[u]['H'],cells[t]['g']+cells[u]['g'])
        for vertex in intersection:
            for owner in range(n):
                difference=dot(coefficients[t][owner],vertex)+intercepts[t][owner]-dot(coefficients[u][owner],vertex)-intercepts[u][owner]
                continuity.append(dict(cells=(t,u),vertex=vertex,owner=owner,difference=difference))
    summary=dict(
        name=name,cells=len(cells),cell_vertices=sum(len(c['vertices']) for c in cells),
        coverage_LPs=len(coverage),funding_LPs=len(funding),
        nonnegative_pass=all(v>=0 for v in nonnegative),
        continuity_pass=all(c['difference']==0 for c in continuity),
        coverage_pass=all(c['shortfall']<=0 for c in coverage),
        funding_pass=all(c['excess']<=0 for c in funding),
        local_tcwm_pass=all(result[str(n)]['tcwm_pass'] for result in local),
        local_out_pass=all(result[str(n)]['out_pass'] for result in local),
    )
    summary['full_certificate_pass']=all(summary[key] for key in (
        'nonnegative_pass','continuity_pass','coverage_pass','funding_pass','local_out_pass'))
    inputs=dict(owners=n,coordinates=coordinates,A=A,profits=profits,kappa=kappa,
                cells=[dict(H=cell['H'],g=cell['g'],coefficients=coefficients[t],
                            intercepts=intercepts[t]) for t,cell in enumerate(cells)])
    return dict(summary=summary,inputs=inputs,coverage=coverage,funding=funding,
                continuity=continuity,local=local)

def run():
    A=((Q(1),),(Q(1),));profits=(Q(1),)
    mixed=((0,0),(0,1),(1,0),(1,1))
    mixed_cells=arrangement((1,1,1,1),[((1,-1,1,-1),0)])
    assert len(mixed_cells)==2
    universal=[]
    for cell in mixed_cells:
        gradient=(1,0,1,0) if cell['center'][0]+cell['center'][2]<cell['center'][1]+cell['center'][3] else (0,1,0,1)
        universal.append((tuple(map(Q,gradient)),tuple(map(Q,gradient))))
    universal_result=check_candidate('universal y_i=F(total), mixed owners',mixed_cells,mixed,A,profits,
                                     universal,[(Q(0),Q(0))]*2,Q(2))
    assert all(universal_result['summary'][key] for key in (
        'nonnegative_pass','continuity_pass','coverage_pass','funding_pass','local_tcwm_pass','local_out_pass'))

    pure=((0,0),(1,1))
    continuous_cells=arrangement((1,1),[((1,-1),0),((1,-2),0)])
    assert len(continuous_cells)==3
    continuous=[]
    for cell in continuous_cells:
        b1,b2=cell['center']
        if b1<b2:
            continuous.append(((Q(1),Q(0)),(Q(0),Q(0))))
        elif b1<2*b2:
            continuous.append(((Q(-1),Q(2)),(Q(1),Q(-1))))
        else:
            continuous.append(((Q(0),Q(0)),(Q(0),Q(1))))
    continuous_result=check_candidate('continuous switching core selector',continuous_cells,pure,A,profits,
                                      continuous,[(Q(0),Q(0))]*3,Q(1))
    assert all(continuous_result['summary'][key] for key in (
        'nonnegative_pass','continuity_pass','coverage_pass','funding_pass'))
    assert not continuous_result['summary']['local_tcwm_pass']
    assert not continuous_result['summary']['local_out_pass']
    assert 2*Q(1,2)-Q(3,4)==Q(1,4)
    assert 2*Q(1,2)-Q(1)==0

    jump_cells=arrangement((1,1),[((1,-1),0)])
    jump=[]
    for cell in jump_cells:
        b1,b2=cell['center']
        jump.append(((Q(1),Q(0)),(Q(0),Q(0))) if b1<b2
                    else ((Q(0),Q(0)),(Q(0),Q(1))))
    jump_result=check_candidate('discontinuous switching core selector',jump_cells,pure,A,profits,
                                jump,[(Q(0),Q(0))]*2,Q(1))
    assert all(jump_result['summary'][key] for key in (
        'nonnegative_pass','coverage_pass','funding_pass','local_tcwm_pass','local_out_pass'))
    assert not jump_result['summary']['continuity_pass']

    triangle=arrangement((1,1),[((1,1),1)])
    lower=next(c for c in triangle if sum(c['center'])<1)
    zero=((Q(0),Q(0)),(Q(0),Q(0)))
    probe=coverage_lp(lower,zero,(Q(0),Q(0)),pure,A,profits,(0,1))
    assert all(min(vertex)==0 for vertex in lower['vertices'])
    assert probe['shortfall']==Q(1,2)
    assert probe['primal']==(Q(1,2),Q(1,2),Q(1,2))

    return dict(
        status='PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        scope='Exact all-real certificates on supplied finite partitions, not a grid test or general funding improvement.',
        partition_validation='Complete hyperplane arrangements with exact full-dimension filtering; closures cover the box by the finite arrangement density argument.',
        candidates=[universal_result,continuous_result,jump_result],
        coverage_vertex_trap=probe,
        finite_incentive_violations=[
            dict(rule='continuous',coalition=(0,),low=(Q(3,4),Q(1,2)),
                 high=(Q(1),Q(1,2)),low_payment=Q(1,4),high_payment=Q(0)),
            dict(rule='discontinuous',coalition=(0,),low=(Q(1,4),Q(1,2)),
                 high=(Q(3,4),Q(1,2)),low_payment=Q(1,4),high_payment=Q(0)),
        ],
    )

def encode(value):
    if isinstance(value,Q):
        return str(value)
    raise TypeError(type(value).__name__)

if __name__=='__main__':
    result=run()
    source=Path(__file__)
    result['checker_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    source.with_suffix('.json').write_text(json.dumps(result,default=encode,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],candidates=[x['summary'] for x in result['candidates']],
                         coverage_vertex_trap=str(result['coverage_vertex_trap']['shortfall'])),indent=2))

