from fractions import Fraction as Q
if not __debug__:
    raise RuntimeError('Run without -O; assertions are the verifier.')
checks=0
for m in range(2,12):
    for den in range(1,13):
        for num in range(den,2*den):
            beta=Q(num,den)
            if m*(2-beta)<=1:
                continue
            u=(2*m-1-beta*m)/(m-1)
            assert u>0 and u<=1
            assert m*u + m*(1-u)+(m-1)*(1-u)==beta*m
            for k in range(2,20):
                assert (k*u+m-1)/(2*m-1)>0
                checks+=1
# Coalition values underlying the two forcing inequality families.
for k,m in ((2,2),(3,2),(2,3),(3,3),(2,4),(4,2)):
    n=k*m
    for distinguished in range(k):
        caps=[(1 if s==distinguished or j else m) for s in range(k) for j in range(m)]
        assert min(sum(caps[s*m:(s+1)*m]) for s in range(k))==m
        all_short_plus_high=[s*m+j for s in range(k) for j in range(m)
                             if s==distinguished or j==0]
        value=min(sum(caps[t] for t in all_short_plus_high if t//m==s) for s in range(k))
        assert value==m
        for mask in range(1<<n):
            selected=[t for t in range(n) if mask>>t&1]
            if all(sum(t//m==s for t in selected)==1 for s in range(k)) and all(t//m==distinguished or t%m>0 for t in selected):
                assert min(sum(caps[t] for t in selected if t//m==s) for s in range(k))==1
                checks+=1
print('PASS',checks,'exact arithmetic/coalition checks')
