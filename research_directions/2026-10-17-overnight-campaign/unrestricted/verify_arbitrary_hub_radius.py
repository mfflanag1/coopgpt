from itertools import product, combinations
if not __debug__:raise RuntimeError('Assertions must remain enabled.')

def F(forms,vec):return min(sum(a*b for a,b in zip(w,vec)) for w in forms)
def aggregate(profile,S,d):return tuple(sum(profile[i][j] for i in S) for j in range(d))
def leq(a,b):return all(x<=y for x,y in zip(a,b))
counts={'profiles':0,'coalitions':0,'own_comparisons':0}
for forms,hub,choices in [
    ([(1,0),(0,1)],[(1,1)]*4,[(0,0),(0,1),(1,0),(1,1),(2,0),(0,2),(2,2)]),
    ([(2,1),(1,3)],[(1,0),(0,1),(1,1),(2,1)],[(0,0),(0,1),(1,0),(1,1),(2,0),(0,2),(2,2)]),
    ([(1,1,0),(0,1,1),(1,0,2)],[(1,0,0),(0,1,0),(0,0,1),(1,1,1),(0,0,0)],[(0,0,0),(1,0,0),(0,1,0),(0,0,1),(1,1,1),(2,0,1)]),
]:
    n=len(hub);d=len(hub[0]);N=tuple(range(n))
    for radius in (0,1,2):
        cache={}
        def rule(profile):
            P=tuple(i for i in N if not leq(profile[i],hub[i]))
            if P not in cache:
                L=tuple(i for i in N if i not in P);s=radius-len(P)
                J=min(combinations(L,s),key=lambda S:(F(forms,aggregate(hub,[i for i in L if i not in S],d)),S))
                O=tuple(i for i in L if i not in J)
                ctot=aggregate(hub,O,d)
                w=min(forms,key=lambda w:(sum(a*b for a,b in zip(w,ctot)),tuple(w)))
                c={i:sum(a*b for a,b in zip(w,hub[i])) for i in O}
                cache[P]=(L,J,c)
            L,J,c=cache[P]
            T=F(forms,aggregate(profile,N,d));R=F(forms,aggregate(profile,L,d))
            y=tuple(T if i in P else R if i in J else c[i] for i in N)
            assert all(x>=0 for x in y) and sum(y)<=(radius+1)*T
            return y
        profiles={}
        for k in range(radius+1):
            for changed in combinations(N,k):
                for bundles in product(choices,repeat=k):
                    p=list(hub)
                    for i,b in zip(changed,bundles):p[i]=b
                    p=tuple(p)
                    profiles[p]=rule(p)
        for p,y in profiles.items():
            counts['profiles']+=1
            for mask in range(1<<n):
                S=[i for i in N if mask>>i&1]
                assert sum(y[i] for i in S)>=F(forms,aggregate(p,S,d))
                counts['coalitions']+=1
            for i in N:
                for b in choices:
                    pp=list(p);pp[i]=b;pp=tuple(pp)
                    if pp in profiles and leq(p[i],b):
                        assert y[i]<=profiles[pp][i],(forms,hub,radius,p,pp,i,y,profiles[pp])
                        counts['own_comparisons']+=1
print('PASS',counts)
