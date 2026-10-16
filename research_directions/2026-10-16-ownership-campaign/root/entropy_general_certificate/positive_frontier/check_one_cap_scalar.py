"""Exact Fraction replay of the new scalar correction and its attainer."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,random

def require(ok,message):
    if not ok:raise RuntimeError(message)

def run():
    rng=random.Random(2026101702);checks=0;equalities=0
    for _ in range(2000):
        alpha=F(rng.randrange(1,20),10);B=F(rng.randrange(0,30),10)
        p=F(rng.randrange(1,30),10);mu=p*F(rng.randrange(10),10)
        lam=F(rng.randrange(1,10),10);b=1-lam
        upper=B*(p-mu)*b/(b+alpha*p)
        z=B*F(rng.randrange(101),100)
        g=(B-z)/alpha*F(rng.randrange(101),100)
        actual=min((p-mu)*z,b*g-mu*z)
        require(actual<=upper,'Rational scalar majorization failed')
        checks+=1
        zstar=b*B/(b+alpha*p);gstar=p*B/(b+alpha*p)
        require(zstar+alpha*gstar==B,'Attainer constraint failed')
        require(min((p-mu)*zstar,b*gstar-mu*zstar)==upper,'Exact attainer failed')
        equalities+=1
    source=Path(__file__).with_name('ONE_CAP_POSITIVE_DUAL_COUPLING.txt')
    return {'status':'PASS','arithmetic':'Exact fractions.Fraction; finite scalar checks supplement the full analytic proof',
            'rational_inequality_checks':checks,'rational_attainer_equalities':equalities,
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
