from fractions import Fraction as Q
if not __debug__:raise RuntimeError('Run without -O.')
A=[(1,1,0),(1,0,1)];low=[Q(2,3),Q(1,3),Q(1,3)];high=[Q(1,2)]*3
for t,x in [(0,low),(1,high)]:
    for s in range(1,8):
        c1=Q(int(s&1>0));c2=Q(int(s&2>0));c3=Q(int(s&4>0));z=t*c1
        v=min(c1,c2+c3)+min(z,c1,c2,c3)/2
        assert sum(x[i] for i in range(3) if s>>i&1)>=v
    if t==0:
        assert low==[sum(Q(1,3)*row[i] for row in A) for i in range(3)]
        assert all(sum(Q(row[i])*low[i] for i in range(3))==1 for row in A)
    else:assert sum(high)==Q(3,2) and sum(y*y for y in high)==Q(3,4)
assert low[0]>high[0]
print({'low_projection':list(map(str,low)),'high_projection':list(map(str,high)),'status':'PASS'})
