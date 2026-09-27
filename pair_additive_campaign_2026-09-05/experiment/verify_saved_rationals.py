"""Standard-library-only verification of saved rational LP identities."""
from fractions import Fraction as F
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))

def parsed(row,n):
    a=list(map(F,row['a']))
    require(len(a)<=n,'oversized row')
    return dict(label=row['label'],a=a+[F(0)]*(n-len(a)),b=F(row['b']))

def main():
    data=json.loads((ROOT/'rational_certificates.json').read_text())
    for cert in data['certificates']:
        c=list(map(F,cert['objective_coefficients']));n=len(c)
        rows=[parsed(r,n) for r in data['core_rows']+cert['extra_inequality_rows']]
        eq=[parsed(r,n) for r in data['efficiency']+cert['extra_equalities']]
        alpha={r['row']:F(r['multiplier']) for r in cert['inequality_multipliers']}
        beta={r['row']:F(r['multiplier']) for r in cert['equality_multipliers']}
        require(len({r['label'] for r in rows})==len(rows),'duplicate inequality label')
        require(len({r['label'] for r in eq})==len(eq),'duplicate equality label')
        require(set(alpha)<={r['label'] for r in rows} and set(beta)<={r['label'] for r in eq},'unbound multiplier')
        require(all(a<=0 for a in alpha.values()),'wrong inequality sign')
        point=list(map(F,cert['primal']))
        require(len(point)==n,'wrong point dimension')
        require(all(dot(r['a'],point)<=r['b'] for r in rows),'primal inequality')
        require(all(dot(r['a'],point)==r['b'] for r in eq),'primal equality')
        require(all(sum(alpha.get(r['label'],F(0))*r['a'][j] for r in rows)+sum(beta.get(r['label'],F(0))*r['a'][j] for r in eq)==c[j] for j in range(n)),'dual identity')
        bound=sum(alpha.get(r['label'],F(0))*r['b'] for r in rows)+sum(beta.get(r['label'],F(0))*r['b'] for r in eq)
        require(bound==dot(c,point)==F(cert['objective']),'objective agreement')
    print('PASS',len(data['certificates']),'saved rational primal/dual identities; Python standard library only')

if __name__=='__main__':main()
