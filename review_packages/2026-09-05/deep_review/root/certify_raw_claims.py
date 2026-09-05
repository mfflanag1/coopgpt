"""Independent encodings from the manuscripts; cvc5 proofs checked by Ethos.

Z3 is used only as an SMT-LIB expression printer, never as the solving backend.
No paper verification module is imported. The conventional interface arguments
and all-parameter proofs remain separate from these bounded proof objects.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
import os
import re
import subprocess
import time
import z3 as smt

OUT = Path(__file__).resolve().parent / 'certificates'
TOOLS = Path(os.environ.get('COOPGT_PROOF_TOOLS', '/Users/maxf/projects/economics-research/game-theory/experimental-runs/additive-efx-counting-runs/parkability/certification-20260801-v2/tools'))
CVC = TOOLS / 'cvc5-1.3.3/cvc5-macOS-arm64-static/bin/cvc5'
ETHOS = TOOLS / 'ethos-0.2.3/ethos'
SIG = TOOLS / 'cvc5-1.3.3-source/proofs/eo/cpc'
records = []


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def conjunction(*terms):
    return smt.BoolVal(True) if not terms else terms[0] if len(terms)==1 else smt.And(*terms)


def disjunction(*terms):
    return smt.BoolVal(False) if not terms else terms[0] if len(terms)==1 else smt.Or(*terms)


def q(x):
    x = F(x)
    return smt.Q(x.numerator, x.denominator)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def certify(name, constraints, expected='unsat', scope=''):
    OUT.mkdir(parents=True, exist_ok=True)
    formula = OUT / (name + '.smt2')
    printer = smt.Solver()
    printer.add(*constraints)
    formula.write_text('(set-logic QF_LRA)\n' + printer.sexpr() + '\n(check-sat)\n')
    command = [str(CVC), '--strict-parsing', '--tlimit=120000']
    if expected == 'unsat':
        command += ['--produce-proofs', '--proof-pedantic=1', '--no-proof-allow-trust', '--dump-proofs']
    command.append(str(formula))
    start = time.monotonic()
    run = subprocess.run(command, capture_output=True, text=True, timeout=150)
    lines = run.stdout.splitlines()
    require(run.returncode == 0 and lines and lines[0] == expected,
            f'{name}: cvc5 verdict {run.returncode}: {run.stdout[:1000]} {run.stderr[:300]}')
    result = dict(name=name, scope=scope, status=expected, command=command,
                  formula_sha256=digest(formula), assertions=len(constraints),
                  seconds=round(time.monotonic()-start, 3))
    if expected == 'unsat':
        proof = OUT / (name + '.cpc')
        require(lines[1].strip() == '(' and lines[-1].strip() == ')', 'unexpected proof framing')
        body = '\n'.join(lines[2:-1]) + '\n'
        require(not any(marker in body.lower() for marker in ('trust', 'hole', 'warning')),
                'untrusted proof marker')
        require(re.match(r'^\(step @p\d+ false :rule ', body.splitlines()[-1]) is not None,
                'proof does not end in an explicit false conclusion')
        proof.write_text(body)
        wrapper = OUT / (name + '.check.cpc')
        wrapper.write_text(f'(include "{SIG / "Cpc.eo"}")\n(include "{SIG / "expert/CpcExpert.eo"}")\n' + body)
        check = subprocess.run([str(ETHOS), str(wrapper)], capture_output=True, text=True, timeout=150)
        require(check.returncode == 0 and check.stdout.strip() == 'correct',
                f'{name}: Ethos did not validate: {check.stdout[:200]} {check.stderr[:200]}')
        result.update(ethos='correct', proof_sha256=digest(proof), proof_bytes=proof.stat().st_size)
    records.append(result)
    (OUT / 'results.json').write_text(json.dumps({'complete':False,'records':records},indent=2)+'\n')
    print(f'PASS {name}: {expected}' + (' / Ethos correct' if expected=='unsat' else ''), flush=True)


def sums(point):
    values = [F(0)] * (1 << len(point))
    for mask in range(1, len(values)):
        bit = mask & -mask
        values[mask] = values[mask ^ bit] + point[bit.bit_length()-1]
    return values


def stable():
    a = list(map(F, (1,1,0,1,3,0)))
    b = list(map(F, (2,0,1,0,1,2)))
    d = [v-u for u,v in zip(a,b)]
    sa,sb = sums(a),sums(b)
    v = [min(x,y) for x,y in zip(sa,sb)]
    y = list(smt.Reals('s0 s1 s2 s3 s4 s5'))
    imputation = [sum(y)==6] + [y[i]>=q(min(a[i],b[i])) for i in range(6)]
    badcore = []
    nondomination = []
    pair_only = []
    for mask in range(1,63):
        ids=[i for i in range(6) if mask>>i&1]
        badcore.append(sum(y[i] for i in ids)<q(v[mask]))
        delta=sb[mask]-sa[mask]
        if delta>0:
            dominates=conjunction(*[y[i]<q(a[i]) for i in ids])
        elif delta<0:
            dominates=conjunction(*[y[i]<q(b[i]) for i in ids])
        else:
            positive=[i for i in ids if d[i]>0]
            negative=[i for i in ids if d[i]<0]
            tests=[y[i]<q(a[i]) for i in ids if d[i]==0]
            tests += [y[i]<q(b[i]) for i in positive]
            tests += [y[j]<q(a[j]) for j in negative]
            tests += [(y[i]-q(a[i]))/q(d[i]) < (y[j]-q(a[j]))/q(d[j])
                      for i in positive for j in negative]
            dominates=conjunction(*tests)
        nondomination.append(smt.Not(dominates))
        if len(ids)==2:
            pair_only.append(smt.Not(dominates))
    certify('stable_all_coalitions', imputation+nondomination+[disjunction(*badcore)],
            scope='All real six-player imputations: no outside-core point escapes every nonempty coalition dominator on the segment.')
    certify('stable_pairs_only_control', imputation+pair_only+[disjunction(*badcore)], 'sat',
            'Removing domination through non-pair coalitions admits an outside-core point.')


def fib(index):
    a,b=0,1
    for _ in range(index):
        a,b=b,a+b
    return a


def asymptotic(m,r):
    den=fib(m+1)
    donor=[F(fib(m-i),den) for i in range(m)]
    u=[F(r-m)]+donor+[1-a for a in donor]+[F(0)]*r
    v=[F(0)]*(2*m+1)+[F(1)]*r
    su,sv=sums(u),sums(v)
    worth=[min(x,y) for x,y in zip(su,sv)]
    y=[smt.Real(f'f{i}') for i in range(len(u))]
    core=[sum(y)==r]
    for mask in range(1,(1<<len(u))-1):
        core.append(sum(y[i] for i in range(len(u)) if mask>>i&1)>=q(worth[mask]))
    t=1-y[-1]
    on_segment=[y[i]==q(v[i])+t*q(u[i]-v[i]) for i in range(len(u))]
    prefix=f'asym_m{m}_r{r}'
    certify(prefix+'_whole_core',core+[smt.Not(conjunction(*on_segment))],
            scope=f'All proper raw coalition constraints, n={len(u)}: every entire-core point lies on the stated segment.')
    for tag,parameter,floor in [('leximin',F(den,den+1),True),('minimax',F(1,r-m+1),False)]:
        point=[parameter*a+(1-parameter)*b for a,b in zip(u,v)]
        ps=sums(point)
        require(ps[-1]==r and all(x>=a for x,a in zip(ps,worth)), 'candidate not in raw core')
        level=min(point) if floor else max(point)
        caps=[yi>=q(level) if floor else yi<=q(level) for yi in y]
        certify(prefix+'_'+tag,core+caps+[disjunction(*[yi!=q(pi) for yi,pi in zip(y,point)])],
                scope='Feasible predicted point is the sole first-stage optimum; no alternative feasible point at its floor/ceiling.')


def triples(L,R):
    names=[]; colors={}; edges={}
    def player(name,color):
        require(name not in colors,'duplicate player')
        colors[name]=color%3;names.append(name)
        return name
    def edge(players,weight):
        key=tuple(sorted(players))
        require(len(key)==3 and len(set(key))==3 and {colors[p] for p in key}=={0,1,2},'invalid colored triple')
        require(key not in edges or edges[key]==weight,'conflicting triple')
        edges[key]=weight
    G=[player(f'G{i}',i) for i in range(3)]
    U={};V={};D={}
    for ell in range(L+1):
        for i in range(3):
            U[ell,i]=player(f'U{ell}_{i}',i+(ell%2))
            V[ell,i]=player(f'V{ell}_{i}',i+(1-ell%2))
            D[ell,i]=player(f'D{ell}_{i}',i+2)
    copied=[]
    for ell in range(L+1):
        for i in range(3):
            value=2 if ell==0 else 1
            edge([U[ell,i],V[ell,i],D[ell,i]],value)
            edge([U[ell,i],V[ell,i],G[(i+2)%3]],value)
            if ell==0:
                edge([U[ell,i],G[(i+1)%3],G[(i+2)%3]],1)
            else:
                j,k=[a for a in range(3) if a!=i]
                edge([U[ell,i],V[ell-1,j],V[ell-1,k]],2)
                edge([V[ell,i],U[ell-1,j],U[ell-1,k]],3 if ell==1 else 1)
    for rep in range(R):
        for i in range(3):
            cu=player(f'CU{rep}_{i}',colors[U[L,i]])
            cv=player(f'CV{rep}_{i}',colors[V[L,i]])
            cd=player(f'CD{rep}_{i}',i+2)
            copied.append((i,cu,cv,cd))
            for team in ([cu,cv,cd],[cu,cv,G[(i+2)%3]],[cu,V[L,i],G[(i+2)%3]],[cv,U[L,i],G[(i+2)%3]]):
                edge(team,1)
    total=6+3*L+3*R
    matching=[(U[ell,i],V[ell,i],D[ell,i]) for ell in range(L+1) for i in range(3)]
    matching += [(cu,cv,cd) for i,cu,cv,cd in copied]
    used=[p for team in matching for p in team]
    require(len(used)==len(set(used)), 'matching is not disjoint')
    require(sum(edges[tuple(sorted(team))] for team in matching)==total, 'matching lower bound does not equal T')
    y={name:smt.Real(name) for name in names}
    core=[yi>=0 for yi in y.values()]+[sum(y.values())==total]
    core += [sum(y[p] for p in team)>=value for team,value in edges.items()]
    theta=[y[U[0,i]]-1 for i in range(3)]
    expected={p:smt.RealVal(0) for p in names}
    x={p:F(0) for p in names};z=dict(x);t=F(1,2**L+2)
    for ell in range(L+1):
        for i in range(3):
            expected[U[ell,i]]=theta[i]+(1 if ell==0 else 0)
            expected[V[ell,i]]=1-theta[i]
            x[U[ell,i]]=F(2**ell)*t+(1 if ell==0 else 0)
            x[V[ell,i]]=1-F(2**ell)*t
            z[U[ell,i]]=F(1 if ell==0 else 0);z[V[ell,i]]=F(1)
        if ell<L:
            theta=[sum(theta[j] for j in range(3) if j!=i) for i in range(3)]
    for i,cu,cv,cd in copied:
        expected[cu]=theta[i];expected[cv]=1-theta[i]
        x[cu]=2**L*t;x[cv]=1-2**L*t;z[cv]=F(1)
    for point in (x,z):
        require(sum(point.values())==total and min(point.values())>=0,'candidate total')
        require(all(sum(point[p] for p in team)>=value for team,value in edges.items()),'candidate not a covering allocation')
    nonzero=[p for p in names if p.startswith(('U','V','CU','CV'))]
    prefix=f'triple_L{L}_R{R}'
    certify(prefix+'_whole_core',core+[disjunction(*[y[p]!=expected[p] for p in names])],
            scope=f'n={len(names)}, {len(edges)} positive triples: raw entire core forces all recurrence and dummy equations.')
    for tag,point,caps in [('leximin',x,[y[p]>=q(2*t) for p in nonzero]),('minimax',z,[yi<=1 for yi in y.values()])]:
        certify(prefix+'_'+tag,core+caps+[disjunction(*[y[p]!=q(point[p]) for p in names])],
                scope='Exact positive-floor/minimax face uniqueness; fixed-zero dummies are established by the whole-core query.')
    distance=sum(abs(x[p]-z[p]) for p in names)/total
    formula=F(2*((R+2)*2**L-1),(2**L+2)*(L+R+2))
    require(distance==formula,'triple distance formula mismatch')


if __name__=='__main__':
    stable()
    for m,r in ((2,3),(2,5),(3,4)):
        asymptotic(m,r)
    for L,R in ((1,0),(2,1)):
        triples(L,R)
    final={'complete':True,'records':records,'scope':'Fixed instances only, not a machine proof of the all-parameter theorems.',
           'binaries':{str(p):digest(p) for p in (CVC,ETHOS,SIG/'Cpc.eo',SIG/'expert/CpcExpert.eo')},
           'trust_interface':'Ethos checks the emitted CPC premises and explicit final false step. Their semantic equivalence to SMT assertions is inspected through the encoder, not independently mechanically bound. Z3 is only the expression printer. Fixed-instance proof objects do not formalize the all-parameter theorems.',
           'generator_sha256':digest(Path(__file__))}
    (OUT/'results.json').write_text(json.dumps(final,indent=2)+'\n')
    print('PASS independent raw encodings and trust-disabled proof checks',flush=True)
