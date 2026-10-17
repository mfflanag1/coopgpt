"""Exact constructor check; the general proof is in BOOLEAN_PROFILE_REALIZATION_LEMMA.txt."""
from fractions import Fraction as Q
if not __debug__:raise RuntimeError('Assertions required; run without -O.')
n=4;N=(1<<n)-1
# Each clause requires coalition A and some of its members' high reports H.
# The common veto owner 0 makes every nonzero subgame core explicitly available.
clauses=[(0b0011,0b0010),(0b1101,0b0100),(0b1011,0b1001)]
def worth(u,s):
    return Q(int(any(a&s==a and h&u==h for a,h in clauses)))
forms=[]
for u in range(1<<n):
    for a in range(1,1<<n):
        value=worth(u,a)
        base=[Q(0) if a>>i&1 else Q(1) for i in range(n)]
        if value:
            assert a&1
            base[0]=value
        control=[Q(int(not(u>>i&1))) for i in range(n)]
        for s in range(1<<n):
            assert sum(base[i] for i in range(n) if s>>i&1)>=worth(u,s)
        forms.append(base+control)
checks=0
for v in range(1<<n):
    for s in range(1<<n):
        x=[Q(int(s>>i&1)) for i in range(n)]+[Q(int((s&v)>>i&1)) for i in range(n)]
        observed=min(sum(a*b for a,b in zip(p,x)) for p in forms)
        assert observed==worth(v,s)
        assert worth(v,s)==worth(v&s,s)
        for u in range(1<<n):
            if u&v==u:assert worth(u,s)<=worth(v,s)
        checks+=1
print({'owners':n,'resources':2*n,'forms':len(forms),'profile_coalition_checks':checks,'status':'PASS'})
