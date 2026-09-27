"""Standard-library certificate: integral worth, positive floor, target pinning, ideal."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def check(r):
    m,k=r['m'],r['k'];n=m*k;T=F(r['T']);tau=F(r['floor']);target=r['target']
    require(k==4 and isinstance(m,int) and m>=1,'Not a four-sector market')
    require(len(r['edges'])==len(r['matrices'])==4,'Matrix/edge count')
    require(set(map(tuple,r['edges']))=={(0,1),(1,2),(2,3),(0,3)},'Not the stated four-cycle')
    require(all(len(A)==m and all(len(row)==m and all(type(v)is int and v in (0,1,2)for v in row)for row in A)for A in r['matrices']),'Matrix shape or alphabet')
    require(0<=target<n and T>0,'Target or positive worth')
    def w(t):return sum(A[t[a]][t[b]]for (a,b),A in zip(r['edges'],r['matrices']))
    teams=list(product(range(m),repeat=k))
    matching=r['optimal_matching']
    require(len(matching)==m and all(sorted(t[v]for t in matching)==list(range(m))for v in range(k)),'Not perfect matching')
    require(sum(w(t)for t in matching)==T,'Matching worth')
    def covers(point):
        require(len(point)==n and min(point)>=0 and sum(point)==T,'Efficiency or nonnegativity')
        for t in teams:require(sum(point[v*m+t[v]]for v in range(k))>=w(t),'Uncovered team')
    x=list(map(F,r['x']));y=list(map(F,r['ideal_witness']));covers(x);covers(y)
    require(min(x)==tau>0,'Positive floor')
    loads=[F(0)]*n;dual_w=F(0)
    for row in r['residual_dual']:
        t=row['team'];weight=F(row['weight'])
        require(tuple(t)in teams and weight>0,'Invalid dual term')
        for v in range(k):loads[v*m+t[v]]+=weight
        dual_w+=weight*w(t)
    d=[1-v for v in loads];require(min(d)>=0 and d[target]>0,'Dual loads or target deficit')
    require(T-dual_w==tau*sum(d),'Dual objective identity')
    # For every core p: sum(d_i p_i)+sum(lambda_t*(p(t)-w(t)))=T-lambda.w.
    # All terms are nonnegative. Thus p>=tau forces p_i=tau whenever d_i>0.
    target_team=next(t for t in matching if t[target//m]==target%m)
    H=w(target_team)
    require(y[target]==H and x[target]==tau,'Ideal attainment or target payoff')
    require(tau/H==F(r['ratio'])<F(1,k),'Protection ratio')
    return {'status':'PASS','team_cover_checks':2*len(teams),'target':target,'ratio':str(tau/H),'ideal':str(H),'dual_terms':len(r['residual_dual'])}

if __name__=='__main__':
    print(json.dumps(check(json.loads((Path(__file__).parent/'FOUR_CYCLE_CERTIFICATE.json').read_text()))))
