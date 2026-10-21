"""Independent stdlib arithmetic/graph audit of the activation mass certificate.

Full off-row feasibility is proved from the closed-neighborhood implication
in the accompanying audit; this checker never pretends to enumerate all rows.
No imports from search/reconstruction code and no numerical optimizer.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json


def check(path):
    raw=path.read_bytes(); data=json.loads(raw)
    n=104; star={0,1,52,103}; rank=55
    edges={tuple(sorted((j,(j+s)%n))) for j in range(n) for s in [1,52]}
    assert len(edges)==156
    neighbors={b if a==0 else a for a,b in edges if 0 in (a,b)}
    assert neighbors==star-{0}
    # Translation by1 generates a transitive graph automorphism group.
    assert {tuple(sorted(((a+1)%n,(b+1)%n))) for a,b in edges}==edges
    assert {(0+j)%n for j in range(n)}==set(range(n))
    support=data['support']; assert len(support)==101
    weights=[]; sets=[]; marg=[F(0)]*n
    for entry in support:
        a=entry['independent_set']; weight=F(entry['weight'])
        assert len(a)==len(set(a))==49 and all(type(j) is int and 0<=j<n for j in a)
        independent=set(a)
        assert not any(u in independent and v in independent for u,v in edges)
        assert len(independent & star)==1 and weight>0
        sets.append(independent); weights.append(weight)
        for j in independent:marg[j]+=weight
    assert sum(weights)==1
    assert marg==[F(1,4) if j in star else F(12,25) for j in range(n)]
    v=[1-x for x in marg]; t=F(2929,100)
    assert sum(v)==55 and sum(x*x for x in v)==t
    rows=[set(range(n))-s for s in sets]
    assert all(len(a)==55 and len(a&star)==3 for a in rows)
    assert all(sum(v[j] for j in a)==t for a in rows)
    q=[x/t for x in v]; lam=[w/t for w in weights]
    assert [sum((lam[r] for r,a in enumerate(rows) if j in a),F(0)) for j in range(n)]==q
    L=sum(lam); assert L==F(100,2929) and sum(x*x for x in q)==L
    assert q[0]==F(75,2929)
    # Full projection certificate using104 translated copies of one row.
    orbit=[{(j+s)%n for j in rows[0]} for s in range(n)]
    full=[sum(F(1,rank*rank) for a in orbit if j in a) for j in range(n)]
    assert full==[F(1,55)]*n
    rho=sum(x*x for x in full); assert rho==F(104,3025)
    assert all(sum(full[j] for j in a)==1 for a in orbit)
    H=rho*n*v[0]**2; assert H==F(6084,3025)>2
    # Finite union product: all row tuples, K=4, with factored multipliers.
    K=4; alpha=rho/(rho+(K-1)*L); beta=L/(rho+(K-1)*L)
    assert alpha+3*beta==1 and alpha*L/rho==beta
    product_q=[alpha*x for x in q]+[beta*x for x in full]*3
    product_rho=rho/K; product_L=alpha*L
    assert sum(x*x for x in product_q)==product_L==F(2600,303029)
    product_focal=product_q[0]; assert product_focal==F(1950,303029)
    E=K*n*product_focal**2; gap=E-2*product_rho
    assert gap==F(10084108268,277775388894025)>0
    # Common veto: J copies of the416-owner product, plus one veto owner.
    J=30000; veto_full=J*product_rho/(1+J*product_rho)
    gamma=1/(1+(J-1)*product_rho+product_L)
    veto_relaxed=1-gamma
    assert gamma*((J-1)*product_rho+product_L)==veto_relaxed
    focal_final=gamma*product_focal
    exact_diagonal_lower=veto_full**2+J*K*n*focal_final**2
    conservative_margin=(J*gap-1)/(1+J*product_rho)**2
    assert conservative_margin>0 and exact_diagonal_lower>=1+conservative_margin
    return {'certified':True,'source_sha256':hashlib.sha256(raw).hexdigest(),
            'support_count':len(support),'source':str(path),'H':str(H),
            'rho':str(rho),'L':str(L),'base_focal':str(q[0]),'t':str(t),
            'all_off_rows':'analytical: independent set containing0 meets its closed star only at0',
            'union_copies':K,'product_rho':str(product_rho),'product_L':str(product_L),
            'product_focal':str(product_focal),'product_E_minus_2rho':str(gap),
            'veto_copies':J,'final_owners':J*K*n+1,'production_resources':2*(J*K*n+1),
            'veto_full':str(veto_full),'final_focal':str(focal_final),
            'conservative_diagonal_margin':str(conservative_margin),
            'exact_diagonal_lower':str(exact_diagonal_lower),
            'scope':'Diagonal conjecture counterexample after stated closure/star realization; no arbitrary-mechanism or total-funding lower bound.'}


if __name__=='__main__':
    root=Path(__file__).resolve().parent.parent
    result=check(root/'proofs/activation_mass_certificate.txt')
    (root/'checks/mass_geometry_main_verify.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
