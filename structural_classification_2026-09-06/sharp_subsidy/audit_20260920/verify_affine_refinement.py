"""Independent rational check; no solver and no compressed core formulation."""
from fractions import Fraction as F
from pathlib import Path
from itertools import product, permutations
from collections import defaultdict
import json

def require(ok,msg):
    if not ok: raise ValueError(msg)

def check(d):
    teams=list(product(range(3),repeat=3));P=(1,2,0);U=[0,2,3,4,7,8]
    def pairs(t):
        a,b,c=t
        return [(0,a,b),(1,a,c),(2,b,c)]
    edges=sorted({e for t in [(j,j,j) for j in range(3)]+[P] for e in pairs(t)})
    require(d['P']==list(P) and d['U']==U,'scope')
    require(d['edges']==list(map(list,edges)),'edges')
    a,b=F(d['a']),F(d['b'])
    require(a>=0 and b>=0,'bound coefficient signs')
    masses=list(map(F,d['packing']))
    require(len(masses)==162 and min(masses)>=0,'packing dimension/sign')
    cover=defaultdict(F)
    for k,i in enumerate(U):
        loads=[F(0)]*9
        for r,t in enumerate(teams):
            mass=masses[k*27+r]
            for s,j in enumerate(t):loads[s*3+j]+=mass
            for e in pairs(t):cover[e]+=mass
        require(loads[i]==0 and max(loads)<=F(1,3),'deletion capacity')
    target=defaultdict(F)
    for e in pairs(P):target[e]+=1
    for j in range(3):
        for e in pairs((j,j,j)):target[e]+=1-a-(b if j==0 else 0)
    require(all(cover[e]>=v for e,v in target.items()),'pair domination')
    primal=list(map(F,d['sharp_witness']));off=len(edges)
    require(len(primal)==off+54 and min(primal)>=0,'primal sign/dimension')
    weights=dict(zip(edges,primal[:off]))
    def worth(t):return sum(weights.get(e,F(0)) for e in pairs(t))
    ds=[worth((j,j,j)) for j in range(3)]
    require(ds==[F(1,8),F(7,16),F(7,16)],'diagonal values')
    matchings=[sum(worth((j,p[j],q[j])) for j in range(3))
               for p in permutations(range(3)) for q in permutations(range(3))]
    require(len(matchings)==36 and max(matchings)==sum(ds)==1,'diagonal optimality')
    attained=[]
    for k,i in enumerate(U):
        x=primal[off+9*k:off+9*(k+1)]
        require(sum(x)==1,'witness total')
        for t in teams:require(sum(x[3*s+j] for s,j in enumerate(t))>=worth(t),'full-team cover')
        attained.append(x[i])
    J=worth(P)+sum(attained)/3-1
    require(J==F(7,48) and J==a+b*ds[0],'sharpness equality')
    require((J-a)/ds[0]==b and b>F(17,27),'coefficient barrier')
    q=F(11,41);v=F(11,82);R=F(29,82)
    bounds=[F(2,3)-F(5,3)*q+v,a+F(14,9)*q-F(8,9)*v,a+F(41,18)*q-F(7,3)*v]
    require(bounds==[R]*3 and R-F(1,3)==F(5,246),'aggregate witness')
    w0,w1,w2=F(260,533),F(261,533),F(12,533)
    require(min(w0,w1,w2)>0 and w0+w1+w2==1,'combination weights')
    require(-F(5,3)*w0+F(14,9)*w1+F(41,18)*w2==0,'q cancellation')
    require(w0-F(8,9)*w1-F(7,3)*w2==0,'v cancellation')
    require(F(2,3)*w0+a*(w1+w2)==R,'aggregate upper')
    return {'status':'PASS','local_bound':'J <= T/18 + (13/18)d0','sharp_coefficient':'13/18','full_team_checks':162,'matching_checks':36,'deletion_rows':6,'scalar_relaxation_optimum':'29/82','market_counterexample_to_global_one_third':False}

def main():
    d=json.loads(Path(__file__).with_name('AFFINE_CERTIFICATE.json').read_text())
    require((F(d['a']),F(d['b']))==(F(1,18),F(13,18)),'canonical claim')
    result=check(d)
    import copy
    damaged=[]
    bad=copy.deepcopy(d);bad['packing']=['0']*162;damaged.append((bad,'pair domination'))
    bad=copy.deepcopy(d);bad['sharp_witness'][-1]='-1';damaged.append((bad,'primal sign/dimension'))
    bad=copy.deepcopy(d);bad['b']='17/27';damaged.append((bad,'pair domination'))
    for bad,expected in damaged:
        try:check(bad)
        except ValueError as error:
            require(str(error)==expected,'negative control failed at wrong gate: '+str(error))
            continue
        raise ValueError('negative control accepted')
    result['negative_controls']=len(damaged)
    print(json.dumps(result))
if __name__=='__main__':main()
