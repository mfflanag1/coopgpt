from fractions import Fraction as Q
from itertools import product
if not __debug__:raise RuntimeError('Run without -O.')
checks=0
for den in range(2,45):
    for num in range(1,den):
        s=Q(num,den);y=max(s,1-s)
        # Each local coalition choice produces t; outside uniform pools need
        # ceil(t) units. Check every attainable t and both affected choices.
        for a,b in product(range(2),range(3)):
            t=a*s+b
            if not t:continue
            ceil=-(-t.numerator//t.denominator)
            assert b*y+ceil*s>=t
            for a2,b2 in product(range(2),range(3)):
                tt=min(t,a2*s+b2)
                if not tt:continue
                ceil2=-(-tt.numerator//tt.denominator)
                assert (b+b2)*(1-s)/2+ceil2*s>=tt
                checks+=1
        factor=(2*y+3*s)/(2+s)
        assert factor<=Q(5,3)
        assert s<=y and s/2<=s
        for m in range(4,40):
            assert Q(m)/(m-2+2*s)<=2
            checks+=1
print('PASS',checks,'exact breakpoint/budget checks')
