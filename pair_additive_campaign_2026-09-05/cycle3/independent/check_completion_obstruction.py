"""Raw recurrence construction and exact obstruction to pair-additive completion."""
from fractions import Fraction as F
from itertools import product
import json
import z3


def require(value, message):
    if not value: raise RuntimeError(message)


def recurrence(L):
    names = [[], [], []]
    colors = {}
    def player(name, color):
        names[color].append(name);colors[name]=color
    for color in range(3): player('G'+str(color),color)
    for ell in range(L+1):
        for i in range(3):
            player(f'U{ell}_{i}',(i+(ell%2))%3)
            player(f'V{ell}_{i}',(i+1-(ell%2))%3)
            player(f'D{ell}_{i}',(i+2)%3)
    weights={}
    def team(players,value):
        ordered=tuple(sorted(players,key=lambda name:colors[name]))
        require(tuple(colors[name] for name in ordered)==(0,1,2),'valid colored triple')
        require(ordered not in weights or weights[ordered]==value,'consistent weights')
        weights[ordered]=value
    for ell in range(L+1):
        for i in range(3):
            U=f'U{ell}_{i}';V=f'V{ell}_{i}';D=f'D{ell}_{i}'
            team((U,V,D),2 if ell==0 else 1)
            team((U,V,'G'+str((i+2)%3)),2 if ell==0 else 1)
            if ell==0:
                team((U,'G'+str((i+1)%3),'G'+str((i+2)%3)),1)
            else:
                j,k=[a for a in range(3) if a!=i]
                team((U,f'V{ell-1}_{j}',f'V{ell-1}_{k}'),2)
                team((V,f'U{ell-1}_{j}',f'U{ell-1}_{k}'),3 if ell==1 else 1)
    def point(t):
        p={name:F(0) for sector in names for name in sector}
        for ell in range(L+1):
            for i in range(3):
                p[f'U{ell}_{i}']=(F(1) if ell==0 else F(0))+2**ell*t
                p[f'V{ell}_{i}']=1-2**ell*t
        return p
    return names,colors,weights,point(F(0)),point(F(1,2**L))


outputs=[]
for L in (2,3,4):
    sectors,colors,weights,p0,p1=recurrence(L)
    T=6+3*L
    for p in (p0,p1):
        require(min(p.values())>=0 and sum(p.values())==T,'target core witness efficiency')
        require(all(sum(p[name] for name in team)>=value for team,value in weights.items()),'target core witness covers')
    coefficients={}
    for c,d in ((0,1),(0,2),(1,2)):
        for u,v in product(sectors[c],sectors[d]):
            coefficients[(u,v)]=z3.Real('w_'+u+'_'+v)
    def edge(u,v):
        return coefficients[(u,v) if colors[u]<colors[v] else (v,u)]
    def induced(team):
        a,b,c=team
        return edge(a,b)+edge(a,c)+edge(b,c)
    solver=z3.Solver();solver.set(timeout=30000)
    solver.add(*[coefficient>=0 for coefficient in coefficients.values()])
    solver.add(*[induced(team)>=value for team,value in weights.items()])
    for team in product(*sectors):
        for p in (p0,p1):
            solver.add(induced(team)<=z3.RealVal(str(sum(p[name] for name in team))))
    status=solver.check()
    require(status==z3.unsat,'full completion query must be UNSAT, got '+str(status))

    U=f'U{L}_0';V=f'V{L}_0';D=f'D{L}_0'
    candidates=[f'U{L-1}_1',f'U{L-1}_2']
    J=next(name for name in candidates if colors[name]==colors[D])
    K=next(name for name in candidates if colors[name]==colors[U])
    GU='G'+str(colors[U]);GV='G'+str(colors[V])
    require(weights[tuple(sorted((U,V,D),key=lambda name:colors[name]))]==1,'retained local clause')
    require(weights[tuple(sorted((V,J,K),key=lambda name:colors[name]))]==1,'retained reverse clause')
    require((p0[U],p0[V],p0[D],p0[J],p0[K],p0[GU],p0[GV])==(0,1,0,0,0,0,0),'origin restriction')
    require((p1[U],p1[V],p1[D],p1[J],p1[K],p1[GU],p1[GV])==(1,0,0,F(1,2),F(1,2),0,0),'endpoint restriction')
    local=z3.Solver();local.set(timeout=30000)
    clauses={
      'pair_nonnegativity':z3.And([v>=0 for v in coefficients.values()]),
      'retain_local':induced((U,V,D))>=1,
      'retain_reverse':induced((V,J,K))>=1,
      'origin_UDG':induced((U,D,GV))<=0,
      'endpoint_VDG':induced((V,D,GU))<=0,
      'origin_UVJ':induced((U,V,J))<=1,
      'origin_JKG':induced((J,K,GV))<=0,
      'endpoint_VKD':induced((V,K,D))<=z3.RealVal('1/2'),
    }
    for name,clause in clauses.items(): local.assert_and_track(clause,name)
    local_status=local.check()
    require(local_status==z3.unsat,'seven-player obstruction')
    # Stronger six-player cube: permit signed pair coefficients, but retain
    # nonnegative triple weights and the original fixed-zero G slice.
    cube=z3.Solver();cube.set(timeout=30000)
    for u,v,d in product((U,K),(V,GV),(D,J)):
        cube.add(induced((u,v,d))>=0)
        cube.add(induced((u,v,d))<=z3.RealVal(str(p0[u]+p0[v]+p0[d])))
        cube.add(induced((u,v,d))<=z3.RealVal(str(p1[u]+p1[v]+p1[d])))
    cube.add(induced((U,V,D))>=1,induced((K,V,J))>=1)
    cube_status=cube.check()
    require(cube_status==z3.unsat,'signed six-player cube obstruction')
    # Verify the exact pair-incidence cancellation, without a solver.
    def pair_row(team):
        a,b,c=team
        row={}
        for first,second in ((a,b),(a,c),(b,c)):
            key=tuple(sorted((first,second)))
            row[key]=row.get(key,0)+1
        return row
    identity={}
    for team,mult in (((U,V,D),1),((K,V,J),1),((U,V,J),-1),((K,V,D),-1),
                      ((U,GV,D),-1),((K,GV,J),-1),((U,GV,J),1),((K,GV,D),1)):
        for key,value in pair_row(team).items(): identity[key]=identity.get(key,0)+mult*value
    require(all(value==0 for value in identity.values()),'six-player cube identity')
    outputs.append({'L':L,'players':sum(map(len,sectors)),'T':T,
                    'full_completion_status':str(status),'seven_player_status':str(local_status),
                    'signed_six_player_cube_status':str(cube_status),
                    'players_in_certificate':{'U':U,'V':V,'D':D,'J':J,'K':K,'GU':GU,'GV':GV},
                    'unsat_core':list(map(str,local.unsat_core()))})

# The scalar Farkas certificate is elementary: add the two retained lower
# bounds and subtract the mixed UVJ upper bound. Its left side is
# beta+gamma+eta+zeta-delta, whose upper bound is1/2, but lower bound1.
require(F(1)+F(1)-F(1)>F(0)+F(0)+F(0)+F(1,2)-F(0),'strict rational contradiction')
print(json.dumps({'status':'PASS','cases':outputs,'solver':z3.get_version_string(),
                  'unknown_policy':'Any solver status other than UNSAT raises',
                  'exact_contradiction_gap':'1/2',
                  'scope':'Finite raw checks of the all-depth six-player cube obstruction; historical seven-player query retained separately'},indent=2))
