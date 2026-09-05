from verification_io import RESULTS
"""Independent sparse-market generation and exact full-selector verification.

Uses only raw triple inequalities after an explicit integral matching and a
feasible covering allocation independently certify the matching optimum.
"""
from exact_three import *
from pathlib import Path
import json


def market(L, R=0, shifted=False, anchor=True, recurrence=True):
    require(L>=0 and R>=0 and (not shifted or L>=1), 'invalid parameters')
    names=[]; colors=[]; weights={}; matching=[]
    def player(name,color):
        names.append(name); colors.append(color%3)
        return len(names)-1
    def triple(ids,value):
        require(len(set(ids))==3 and len({colors[i] for i in ids})==3, 'invalid market triple')
        key=tuple(sorted(ids))
        require(key not in weights or weights[key]==value, 'conflicting triple weights')
        weights[key]=value
        return key
    G=[player('G'+str(c),c) for c in range(3)]
    U={}; V={}; D={}; S={}
    for level in range(L+1+R):
        template=min(level,L)
        for i in range(3):
            cu=(i+(template%2))%3; cv=(i+1-(template%2))%3
            U[level,i]=player('U_%d_%d'%(level,i),cu)
            V[level,i]=player('V_%d_%d'%(level,i),cv)
            D[level,i]=player('D_%d_%d'%(level,i),i+2)
            s=2 if shifted and level==0 else 1
            S[level,i]=s
            matching.append(triple([U[level,i],V[level,i],D[level,i]],s))
            triple([U[level,i],V[level,i],G[(i+2)%3]],s)
    for level in range(1,L+1):
        if not recurrence:
            continue
        for i in range(3):
            j,k=[a for a in range(3) if a!=i]
            triple([U[level,i],V[level-1,j],V[level-1,k]],2)
            triple([V[level,i],U[level-1,j],U[level-1,k]],3 if shifted and level==1 else 1)
    if shifted and anchor:
        for i in range(3):
            triple([U[0,i]]+[G[c] for c in range(3) if c!=colors[U[0,i]]],1)
    for level in range(L+1,L+1+R):
        for i in range(3):
            triple([U[level,i],V[L,i],G[(i+2)%3]],1)
            triple([V[level,i],U[L,i],G[(i+2)%3]],1)
    certificate=[F(0)]*len(names)
    for (level,i),u in U.items():
        certificate[u]=F(int(shifted and level==0))
        certificate[V[level,i]]=F(1)
    T=sum(weights[e] for e in matching)
    require(sum(certificate)==T, 'cover certificate total mismatch')
    require(all(sum(certificate[i] for i in e)>=w for e,w in weights.items()), 'cover certificate failed')
    covered=[i for e in matching for i in e]
    require(len(covered)==len(set(covered)), 'certificate matching overlaps')
    require(all(certificate[i]==0 for i in range(len(names)) if i not in covered), 'unmatched positive certificate')
    # Any integral matching is bounded by this feasible cover, while the
    # displayed disjoint matching attains its sum. Thus T is exact.
    p=[z3.FreshReal('pay') for _ in names]
    cons=[q>=0 for q in p]+[sum(p)==T]
    cons += [sum(p[i] for i in e)>=w for e,w in weights.items()]
    # Omitted zero triples give only redundant nonnegativity inequalities.
    return names,colors,p,cons,T,U,V,D,G,weights,matching


def verify(L,R,shifted):
    names,colors,p,cons,T,U,V,D,G,weights,matching=market(L,R,shifted)
    solver=z3.Solver(); solver.add(*cons)
    require(solver.check()==z3.sat,'constructed entire core empty')
    x,xst=selector(cons,p,True); z,zst=selector(cons,p,False)
    t=F(1,2**L+(2 if shifted else 1))
    expected_x=[F(0)]*len(p); expected_z=[F(0)]*len(p)
    for (level,i),u in U.items():
        amount=2**min(level,L)*t
        offset=int(shifted and level==0)
        expected_x[u]=offset+amount
        expected_x[V[level,i]]=1-amount
        expected_z[u]=offset if shifted else expected_x[u]
        expected_z[V[level,i]]=1 if shifted else expected_x[V[level,i]]
    require(x==expected_x and z==expected_z,'full selector formula mismatch')
    rho=sum(abs(a-b) for a,b in zip(x,z))/T
    expected_rho=F(2*((R+2)*2**L-1),(2**L+2)*(L+R+2)) if shifted else F(0)
    require(rho==expected_rho,'distance formula mismatch')
    coordinate=None
    if not shifted:
        chosen=V[L,0]
        maximum=optimize(cons,p[chosen],True)
        require(maximum==1 and x[chosen]==F(1,2**L+1),'individual guarantee formula mismatch')
        coordinate=dict(player=names[chosen],core_maximum=str(maximum),Lmin=str(x[chosen]))
    print('PASS raw triple core',dict(L=L,R=R,shifted=shifted,n=len(p),T=T,rho=str(rho)),flush=True)
    return dict(L=L,R=R,shifted=shifted,n=len(p),T=T,positive_triples=len(weights),matching_triples=len(matching),rho=str(rho),coordinate_witness=coordinate,players=names,colors=colors,Lmin=list(map(str,x)),Lmax=list(map(str,z)),Lmin_stages=xst,Lmax_stages=zst)


def controls():
    out=[]
    for label,kwargs in [('without_root_anchor',dict(anchor=False)),('without_recurrence',dict(recurrence=False))]:
        names,colors,p,cons,T,U,V,D,G,weights,matching=market(2,2,True,**kwargs)
        x,_=selector(cons,p,True); z,_=selector(cons,p,False)
        rho=sum(abs(a-b) for a,b in zip(x,z))/T
        if label=='without_root_anchor':
            solver=z3.Solver(); solver.add(*cons,p[U[0,0]]<1)
            require(solver.check()==z3.sat, 'removing anchor did not enlarge core')
            # The selectors happen to remain unchanged. This control targets
            # the claimed entire-core characterization, not selector distance.
            out.append(dict(name=label,rho=str(rho),core_enlargement_witness='SAT U_0_0<1'))
        else:
            require(rho==0, 'removing recurrence should leave coincident selectors')
            out.append(dict(name=label,rho=str(rho)))
    return out


def main():
    cases=[verify(L,0,False) for L in (0,1,2,3,5)]
    cases += [verify(L,R,True) for L,R in ((1,0),(1,2),(2,0),(2,4),(3,9),(5,12))]
    payload=dict(method='Raw sparse entire-core triple inequalities; integral primal matching and dual cover certify T before lexicographic optimization. No reduced recurrence constraints added.',cases=cases,negative_controls=controls())
    (RESULTS/'gadget_exact_results.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print('PASS all independent gadget checks and negative controls',flush=True)


if __name__=='__main__':
    main()
