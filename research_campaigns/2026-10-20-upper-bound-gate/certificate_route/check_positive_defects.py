from fractions import Fraction as Q
import json


def check(m):
    assert m >= 2 and m % 2 == 0
    eps = Q(1, 4*m)
    H = [Q(0)]
    for k in range(1, m+1):
        H.append(H[-1] + Q(1,k))
    v = [2 + Q(t,2*m) for t in range(1,m+1)]
    totals = [(V, V+eps, 3*V) if t%2 else (V+eps, V, 3*V)
              for t,V in enumerate(v,1)]
    bundles = [(A-1,B-2,K) for A,B,K in totals]
    u = [V-(1 if t%2 else 2) for t,V in enumerate(v,1)]
    nu = [max(Q(1),H[k]-H[m-1-k]) for k in range(m)]
    div = [Q(0)]*m
    pos = neg = full_out_rhs = weight_oe = tcwm_pos = Q(0)
    all_pairs = 0
    for i in range(m):
        for j in range(i+1,m):
            mu=Q(1,j-i)
            div[i]-=mu
            div[j]+=mu
            assert -mu <= nu[i] and mu <= nu[j]
            delta=tuple(b-a for a,b in zip(bundles[i],bundles[j]))
            assert all(x>0 for x in delta)
            rhs=min(delta)
            expected_rhs=v[j]-v[i]-(eps if (j-i)%2 else 0)
            assert rhs==expected_rhs
            defect=u[i]-u[j]+rhs
            odd_i=(i+1)%2==1
            odd_j=(j+1)%2==1
            expected=(1-eps if odd_i else -1-eps) if odd_i != odd_j else Q(0)
            assert defect==expected
            pos+=mu*max(0,defect)
            neg+=mu*max(0,-defect)
            tcwm_pos+=mu*max(0,u[i]-u[j])
            full_out_rhs+=mu*rhs
            if odd_i and not odd_j:
                weight_oe+=mu
                assert u[i]-u[j]>=Q(1,2)
            all_pairs+=1
    assert div==[H[k]-H[m-1-k] for k in range(m)]
    div[0]+=1 # coverage of actual productive grand coalition R,A,B
    assert all(g<=n for g,n in zip(div,nu))
    assert nu[0]>=1 # each of the two fixed outside suppliers
    D=sum(n*V for n,V in zip(nu,v))
    L=v[0]+full_out_rhs
    Hodd=H[m]-H[m//2]/2
    assert weight_oe==((m+1)*Hodd-Q(m,2))/2
    assert pos==(1-eps)*weight_oe
    assert neg==(1+eps)*((m-1)*Hodd-Q(m,2))/2
    assert pos-neg==Q(3,4)*Hodd+Q(1,8)
    assert D<=Q(5,2)*(2*m-1)
    assert tcwm_pos>=weight_oe/2
    # Efficient owner R-only payments Y_R=F(total)=V cover all coalitions
    # on these selected profiles: coalitions without R have zero K.
    # OUT holds because each rhs <= V_j-V_i. Thus L<=D independently.
    assert L<=D
    # Full optimal-price slack identity: coverage price slack is zero.
    sigma_u=Q(0)
    for k in range(m):
        priceA=(k+1)%2==1
        ua=Q(1) if priceA else Q(0)
        ub=Q(0) if priceA else Q(2)
        sigma_u+=(nu[k]-div[k])*u[k]
        sigma_u+=(nu[k]-(1 if k==0 else 0))*(ua+ub)
    assert L-D==pos-neg-sigma_u
    return {'profiles':m,'actual_owners':3+all_pairs,'arity':3,'protection_size':2,
            'D_exact':str(D),'L_exact':str(L),'positive_OUT_defect_exact':str(pos),
            'negative_OUT_defect_magnitude_exact':str(neg),
            'positive_OUT_defect_over_D':float(pos/D),
            'positive_TCWM_defect_over_D':float(tcwm_pos/D),
            'signed_OUT_defect_exact':str(pos-neg),
            'rerouting_invariant_lower_bound_over_D':float(weight_oe/(2*D)),
            'all_checks_passed':True}

if __name__=='__main__':
    print(json.dumps({'evidence':'exact rational checks supplementing the all-size proof',
                      'results':[check(m) for m in [2,4,8,16,32,64,128,256]]},indent=2))
