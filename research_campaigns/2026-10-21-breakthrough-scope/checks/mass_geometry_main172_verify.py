"""Independent stdlib exact replay of the172-owner base and finite veto step.

No search or reconstruction modules are imported. The complete off-row
feasibility proof is the closed-neighborhood implication in the main proof;
the enormous row universe is not numerically enumerated here.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json


def verify(path):
    raw=path.read_bytes(); data=json.loads(raw)
    n=172; k=89; star={0,1,86,171}
    edges={tuple(sorted((j,(j+s)%n))) for j in range(n) for s in (1,86)}
    assert len(edges)==258
    assert {b if a==0 else a for a,b in edges if 0 in (a,b)}==star-{0}
    assert {tuple(sorted(((a+1)%n,(b+1)%n))) for a,b in edges}==edges
    assert set(range(n))=={j%n for j in range(n)}
    marginal=[F(0)]*n; rows=[]; weights=[]
    assert len(data['support'])==168
    for entry in data['support']:
        values=entry['independent_set']; s=set(values); weight=F(entry['weight'])
        assert len(s)==len(values)==83 and all(type(j) is int and 0<=j<n for j in values)
        assert not any(a in s and b in s for a,b in edges)
        assert len(s&star)==1 and weight>0
        weights.append(weight); rows.append(set(range(n))-s)
        for j in s:marginal[j]+=weight
    assert sum(weights)==1
    assert marginal==[F(1,4) if j in star else F(41,84) for j in range(n)]
    w=[1-x for x in marginal]; t=F(3887,84)
    assert sum(w)==89 and sum(x*x for x in w)==t
    assert all(len(a)==89 and len(a&star)==3 for a in rows)
    assert all(sum(w[j] for j in a)==t for a in rows)
    q=[x/t for x in w]; lam=[x/t for x in weights]
    assert q==[F(63,3887) if j in star else F(43,3887) for j in range(n)]
    assert [sum((lam[r] for r,a in enumerate(rows) if j in a),F(0)) for j in range(n)]==q
    ell=sum(lam); assert ell==sum(x*x for x in q)==F(84,3887)
    # Full cover certificate: translated rows, with possible duplicates counted.
    orbit=[{(j+s)%n for j in rows[0]} for s in range(n)]
    full=[sum(F(1,k*k) for a in orbit if j in a) for j in range(n)]
    assert full==[F(1,89)]*n and all(sum(full[j] for j in a)==1 for a in orbit)
    rho=sum(x*x for x in full); assert rho==F(172,7921)
    p=q[0]; H=rho*n*(p/ell)**2; E=n*p*p; delta=E-2*rho
    assert H==F(16641,7921)>2 and E/rho==F(31438449,15108769)>2
    assert delta==F(209996692,119676559249)>0 and ell<=rho
    J=570; D=1+(J-1)*rho+ell; gamma=1/D
    assert gamma*((J-1)*rho+ell)==1-gamma
    veto=J*rho/(1+J*rho); focal=gamma*p
    exact_lower=veto*veto+J*n*focal*focal
    margin=(J*delta-1)/(1+J*rho)**2
    assert J*delta-1==F(21555191,119676559249)>0
    assert margin==F(170738667911,169637232162345649)>0
    assert exact_lower>=1+margin
    return {'certified':True,'source':str(path),'source_sha256':hashlib.sha256(raw).hexdigest(),
            'support_count':len(rows),'graph_edges':len(edges),'all_marginals_exact':True,
            'all_support_independent_and_star_one':True,'full_orbit_KKT_exact':True,
            'local_KKT_exact':True,'t':str(t),'rho':str(rho),'dual_mass':str(ell),
            'focal_base':str(p),'H':str(H),'E':str(E),'E_over_rho':str(E/rho),
            'E_minus_2rho':str(delta),'veto_copies':J,'owners':J*n+1,'resources':2*(J*n+1),
            'veto_full':str(veto),'focal_final':str(focal),'exact_diagonal_lower':str(exact_lower),
            'conservative_margin':str(margin),
            'off_row_coverage':'Analytical: every independent83-set containing focal excludes its3 neighbors.',
            'scope':'Actual diagonal counterexample via the main proof closure/realization; no funding-sum or arbitrary-mechanism claim.'}


if __name__=='__main__':
    root=Path(__file__).resolve().parent.parent
    result=verify(root/'proofs/activation_mass_certificate_172.txt')
    (root/'checks/mass_geometry_main172_verify.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
