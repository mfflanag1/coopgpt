from fractions import Fraction as Q
if not __debug__:
    raise RuntimeError('Assertions must remain enabled.')
checks=0
for m in range(2,101):
    for k in range(2,201):
        kap=Q(k*(2*m-1)+(m-1)**2,(2*m-1)*(m-1)+k*m)
        h=Q(2*m-1-kap*m,m-1)
        assert kap*(2*m-1)==k*h+(m-1)
        assert 0<kap<Q(2*m-1,m)<2
        assert h>0
        checks+=1
for m in range(2,101):
    k=m**3
    kap=Q(k*(2*m-1)+(m-1)**2,(2*m-1)*(m-1)+k*m)
    assert 2-kap<=Q(3,m)
    checks+=1
print('PASS',checks,'exact lower-algebra checks; upper proved analytically')
