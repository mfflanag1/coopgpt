"""Exact prices via a supplied maximal-SFM oracle; the test oracle is exponential.

Assumptions: public normalized monotone submodular rational rank, nonnegative
rational capacities, and an exact inclusion-maximal minimizer callback.
The algorithm reduces evaluation to <=2m-1 maximal-SFM calls on active rows.
It does not validate submodularity or certify an arbitrary callback.
"""
from fractions import Fraction as Q
from functools import lru_cache

def rational(x):
    if not isinstance(x,(int,Q)):
        raise TypeError('Use exact int/Fraction inputs, not floating approximations')
    return Q(x)

def ratio_cdf(z):
    if z is None:return Q(1)
    return z/2 if z<=1 else 1-Q(1,2)/z

def polymatroid_prices(common, capacities, rank, maximal_sfm):
    """Return exact accepted two-block prices and their principal chain.

    rank(mask) uses original resource indices. maximal_sfm(a,c,r) must return
    the largest minimizer of a*r(mask)-sum(c[j] for j in mask), using its LOCAL
    active indices. Owner payments are dot(original bundle, returned prices).
    """
    P=rational(common);c=tuple(map(rational,capacities));m=len(c)
    if P<0 or any(x<0 for x in c):raise ValueError('Nonnegative capacities required')
    zero={'value':Q(0),'prices':(Q(0),)*(m+1),'chain':[],'breakpoints':[],
          'weights':[],'maximal_sfm_calls':0,'active_private_rows':[]}
    active=tuple(j for j,x in enumerate(c)if x>0)
    if not P or not active:return zero
    cc=tuple(c[j]for j in active);n=len(active);full=(1<<n)-1
    @lru_cache(None)
    def rr(mask):
        original=sum(1<<active[j]for j in range(n)if mask>>j&1)
        return rational(rank(original))
    if rr(0)!=0:raise ValueError('Normalized rank required')
    if rr(full)==0:return zero
    loops=sum(1<<j for j in range(n)if rr(1<<j)==0)
    def mass(mask):return sum((cc[j]for j in range(n)if mask>>j&1),Q(0))
    def intercept(mask):return mass(full^mask)
    pending=[(full,loops)];edges=[];calls=0
    while pending:
        A,B=pending.pop()
        if B&~A or A==B or rr(A)<=rr(B):raise ValueError('Invalid rank/oracle nesting')
        z=mass(A^B)/(P*(rr(A)-rr(B)))
        M=maximal_sfm(z*P,cc,rr);calls+=1
        if not isinstance(M,int)or M<0 or M&~full:raise ValueError('Invalid oracle mask')
        endpoint=z*P*rr(A)+intercept(A)
        if endpoint!=z*P*rr(B)+intercept(B):raise AssertionError('Intersection mismatch')
        got=z*P*rr(M)+intercept(M)
        if got>endpoint:raise ValueError('Oracle did not minimize against endpoints')
        if got==endpoint:
            if M!=A:raise ValueError('Oracle returned a non-maximal tied minimizer')
            edges.append((z,A,B))
        else:
            if B&~M or M&~A or M in(A,B)or not rr(B)<rr(M)<rr(A):
                raise ValueError('Oracle violates maximal parametric nesting')
            pending.extend(((M,B),(A,M)))
    edges.sort();chain=[full];cuts=[]
    for z,A,B in edges:
        if A!=chain[-1]or(cuts and z<=cuts[-1]):raise AssertionError('Bad chain order')
        cuts.append(z);chain.append(B)
    if chain[-1]!=loops or calls>2*n-1:raise AssertionError('Bad endpoint/count')
    boundaries=[Q(0),*cuts,None]
    weights=[ratio_cdf(b)-ratio_cdf(a)for a,b in zip(boundaries,boundaries[1:])]
    if any(w<=0 for w in weights)or sum(weights,Q(0))!=1:raise AssertionError('Bad weights')
    prices=[sum((w*rr(S)for w,S in zip(weights,chain)),Q(0))]+[Q(0)]*m
    for local,original in enumerate(active):
        prices[original+1]=sum((w for w,S in zip(weights,chain)if not S>>local&1),Q(0))
    value=min(P*rr(S)+intercept(S)for S in chain)
    original_chain=[sum(1<<active[j]for j in range(n)if S>>j&1)for S in chain]
    return {'value':value,'prices':tuple(prices),'chain':original_chain,'breakpoints':cuts,
            'weights':weights,'maximal_sfm_calls':calls,'active_private_rows':list(active)}

def exhaustive_maximal_sfm(a,c,rank):
    """Verification backend only: enumerates2^m subsets, NOT polynomial."""
    vals=[a*rank(S)-sum((c[j]for j in range(len(c))if S>>j&1),Q(0))for S in range(1<<len(c))]
    best=min(vals);mask=0
    for S,v in enumerate(vals):
        if v==best:mask|=S
    if vals[mask]!=best:raise ValueError('Input rank is not submodular or oracle defect')
    return mask

def ordinary_to_maximal_sfm(a,c,rank,ordinary_sfm):
    """At most m+1 exact ordinary-SFM calls; callback returns any minimizer mask."""
    n=len(c)
    def f(S):return a*rank(S)-sum((c[j]for j in range(n)if S>>j&1),Q(0))
    optimum=f(ordinary_sfm(n,f));answer=0
    for j in range(n):
        other=[k for k in range(n)if k!=j]
        def lift(T):return(1<<j)|sum(1<<k for q,k in enumerate(other)if T>>q&1)
        T=ordinary_sfm(n-1,lambda T:f(lift(T)))
        if f(lift(T))==optimum:answer|=1<<j
    if f(answer)!=optimum:raise ValueError('Ordinary oracle or submodularity defect')
    return answer
