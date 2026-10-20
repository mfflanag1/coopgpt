"""Independent semantic replay; standard library only, no LP solver."""
from collections import defaultdict, Counter
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'finite_diagnostics'
sys.path.insert(0,str(SOURCE))
from check_certificate import check as check_payment_lower


def load(seed):
    data=json.loads((SOURCE/f'case_{seed}_certificate.json').read_text())
    case=data['case'];d=case['d'];A=case['A'];pi=list(map(Q,case['pi']))
    b=[[data['owner_states'][i][p[i]] for i in range(4)] for p in data['profiles']]
    values={}
    for o in data['oracles']:
        cap=tuple(o['cap']);x=list(map(Q,o['x']));p=list(map(Q,o['p']));v=Q(o['value'])
        if min(x)<0 or min(p)<0:raise ValueError('negative oracle')
        if any(sum(A[a][e]*x[e] for e in range(len(pi)))>cap[a] for a in range(d)):raise ValueError('oracle primal')
        if any(sum(A[a][e]*p[a] for a in range(d))<pi[e] for e in range(len(pi))):raise ValueError('oracle dual')
        if sum(pi[e]*x[e] for e in range(len(pi)))!=v or sum(p[a]*cap[a] for a in range(d))!=v:raise ValueError('oracle gap')
        values[cap]=v
    return data,case,b,values


def check_selection(seed,record):
    data,case,b,values=load(seed);d=case['d'];A=case['A'];pi=list(map(Q,case['pi']))
    edges=[v for v in data['certificate'] if v['tag'][0]=='out']
    if not edges:
        if record['status']!='NO COMPARISON SUPPORT':raise ValueError('support status')
        return record['status']
    p={int(k):list(map(Q,v)) for k,v in record['prices'].items()}
    def cap(k):return tuple(sum(b[k][i][a] for i in range(4)) for a in range(d))
    for k,pv in p.items():
        if min(pv)<0 or sum(pv[a]*cap(k)[a] for a in range(d))!=values[cap(k)]:raise ValueError('inefficient selected price')
        if any(sum(A[a][e]*pv[a] for a in range(d))<pi[e] for e in range(len(pi))):raise ValueError('selected price infeasible')
    negative=Q(0)
    for item in edges:
        _,lo,hi,C=item['tag'];delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d))
        defect=sum(p[lo][a]*b[lo][i][a]-p[hi][a]*b[hi][i][a] for i in C for a in range(d))+values[delta]
        negative+=Q(item['weight'])*max(0,-defect)
    if negative!=Q(record['exact_upper']):raise ValueError('negative mass mismatch')
    if seed!=15:
        if negative!=0:raise ValueError('expected zero witness')
        return 'EXACT ZERO WITNESS'
    # Phase-I Farkas dual in resource coordinates, including beta<=original mu.
    g=defaultdict(Q);lower=Q(0)
    for item in record['obstruction']:
        w=Q(item['weight']);tag=item['tag']
        if w<0:raise ValueError('negative Farkas multiplier')
        if tag[0]=='activity':
            _,k,e=tag
            for a in range(d):g[k,a]-=w*A[a][e]
            lower+=w*pi[e]
        else:
            edge=edges[tag[1]];_,lo,hi,C=edge['tag']
            if w>Q(edge['weight']):raise ValueError('phase I multiplier cap')
            delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d))
            lower-=w*values[delta]
            for i in C:
                for a in range(d):g[hi,a]+=w*b[hi][i][a];g[lo,a]-=w*b[lo][i][a]
    for ks,ws in record['efficiency_multipliers'].items():
        k=int(ks);w=Q(ws)
        for a,v in enumerate(cap(k)):g[k,a]+=w*v
        lower-=w*values[cap(k)]
    if any(v<0 for v in g.values()) or lower!=Q(2,139) or negative!=lower:raise ValueError('phase I obstruction')
    return 'EXACT POSITIVE OPTIMUM 2/139'


def check_primal(record,b,values,excluded=frozenset()):
    ids=record['profiles'];K=Q(record['exact_upper']);flat=list(map(Q,record['payments']))
    if len(flat)!=4*len(ids) or min(flat)<0:raise ValueError('payment format')
    y={k:flat[4*j:4*j+4] for j,k in enumerate(ids)}
    prices=None if record['prices'] is None else {int(k):list(map(Q,p)) for k,p in record['prices'].items()}
    cs=[tuple(c) for n in range(1,5) for c in combinations(range(4),n)]
    def cap(k,C):return tuple(sum(b[k][i][a] for i in C) for a in range(4))
    for k in ids:
        if sum(y[k])>K*values[cap(k,range(4))]:raise ValueError('budget')
        for C in cs:
            if sum(y[k][i] for i in C)<values[cap(k,C)]:raise ValueError('coverage')
    edge_tags=set()
    for lo in ids:
        for hi in ids:
            if lo==hi:continue
            for C in cs:
                if len(C)>2:continue
                if any(b[lo][i]!=b[hi][i] for i in range(4) if i not in C):continue
                if any(b[lo][i][a]>b[hi][i][a] for i in C for a in range(4)):continue
                if (lo,hi,C) in excluded:continue
                delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(4));de=values[delta]
                if prices is not None:
                    defect=sum(prices[lo][a]*b[lo][i][a]-prices[hi][a]*b[hi][i][a] for i in C for a in range(4))+de
                    if defect<0:continue
                if sum(y[hi][i]-y[lo][i] for i in C)<de:raise ValueError(('OUT',lo,hi,C))
                edge_tags.add((lo,hi,C))
    if 'comparison_rows' in record and len(edge_tags)!=record['comparison_rows']:raise ValueError('edge count')
    return edge_tags


if __name__=='__main__':
    records=json.loads((ROOT/'results.json').read_text())
    statuses=Counter(check_selection(r['seed'],r) for r in records)
    lower=check_payment_lower(SOURCE/'case_15_certificate.json')
    data,case,b,values=load(15);primal=json.loads((ROOT/'payment_primal.json').read_text())
    full=check_primal(primal['full_lattice'],b,values);five=check_primal(primal['five_profiles'],b,values)
    if Q(primal['full_lattice']['exact_upper'])!=Q(lower['lower']) or Q(primal['five_profiles']['exact_upper'])!=Q(lower['lower']):raise ValueError('optimality gap')
    region_supports=[check_primal(r,b,values) for r in primal['nonnegative_price_regions']]
    # One fixed cover has precisely one incentive shortfall. This checks the
    # sharper universal inequality L-D <= (7/12) mu_star via its test vector.
    ids=[37,101,133,149,165]
    fixed_w={k:[Q(0),Q(0),Q(0),Q(5,2)] for k in ids}
    fixed_w[149]=[Q(1,3),Q(1,3),Q(7,12),Q(19,12)]
    star=(133,149,(1,3));shortfalls={}
    for lo,hi,C in five:
        delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(4))
        gap=values[delta]-sum(fixed_w[hi][i]-fixed_w[lo][i] for i in C)
        if gap>0:shortfalls[lo,hi,C]=gap
    if shortfalls!={star:Q(7,12)}:raise ValueError('one-edge shortfall')
    if fixed_w[149][1]-fixed_w[133][1]!=Q(1,3):raise ValueError('singleton increment')
    deleted_record=dict(profiles=ids,exact_upper='1',payments=[str(v) for k in ids for v in fixed_w[k]],prices=None,comparison_rows=15)
    deleted_support=check_primal(deleted_record,b,values,excluded=frozenset([star]))
    mu_lower=(Q(lower['lower'])-1)/Q(7,12)
    star_weight=sum(Q(item['weight']) for item in data['certificate'] if item['tag']==['out',133,149,[1,3]])
    if mu_lower!=Q(6,139) or star_weight!=mu_lower or mu_lower/3!=Q(2,139):raise ValueError('sharp quantitative bound')
    # Extra rational points check the explicit two-case witness and pattern
    # inclusion. Continuous completeness is the affine sign-table proof.
    def low(t):return [t,Q(5,2)-t,Q(0),max(t,1-2*t,Q(0))]
    point_checks=0
    for t,s in product((Q(0),Q(5,4),Q(5,2)),(Q(0),Q(1,3),Q(2,3),Q(5,4),Q(5,2))):
        prices={37:low(t),133:low(s),101:[Q(5,2),0,0,Q(5,2)],149:[Q(1,3),Q(13,6),0,Q(1,3)],165:[0,Q(5,2),0,1]}
        w={37:[0,0,0,Q(5,2)],101:[0,0,0,Q(5,2)],165:[0,0,0,Q(5,2)],149:[Q(1,3),Q(1,3),Q(7,12),Q(19,12)],133:[0,0,0,Q(5,2)] if s==0 else [0,0,Q(5,2),0]}
        ids=[37,101,133,149,165]
        rec=dict(profiles=ids,exact_upper='1',payments=[str(v) for k in ids for v in w[k]],prices={str(k):list(map(str,p)) for k,p in prices.items()})
        support=check_primal(rec,b,values)
        if not any(support<=maximal for maximal in region_supports):raise ValueError('pattern inclusion')
        point_checks+=1
    print(json.dumps(dict(status='EXACT PASS',stored_supports=dict(statuses),payment_optimum=lower['lower'],full_lattice_profiles=256,full_lattice_coverage_rows=3840,full_lattice_comparison_rows=len(full),five_profile_coverage_rows=75,five_profile_comparison_rows=len(five),phase_I_optimum='2/139',price_region_upper_bounds=[r['exact_upper'] for r in primal['nonnegative_price_regions']],additional_rational_sign_points=point_checks,one_edge_obstruction=dict(edge=['out',133,149,[1,3]],unique_test_vector_shortfall='7/12',other_comparisons_satisfied=len(deleted_support),singleton_increment='1/3',deleted_edge_optimum='1',normalized_optimal_edge_weight_lower=str(mu_lower),attained_edge_weight=str(star_weight),sharp_negative_mass_over_all_optimal_duals_and_prices=str(mu_lower/3)),scope='The fixed-five-profile universal bound L-D <= (7/12) mu_star follows by multiplying the exactly verified testing inequalities. Every-profile price efficiency, including nu=0 profiles, is required for the unavoidable price defect.'),indent=2))
