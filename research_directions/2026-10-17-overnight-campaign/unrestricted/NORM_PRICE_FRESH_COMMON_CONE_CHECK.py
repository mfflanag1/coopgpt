from fractions import Fraction as Q
from itertools import product

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def scale(t,a):return tuple(t*x for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cone(a):return a[0]>=max(abs(a[1]),abs(a[2]))
def value(a):return a[0]-max(abs(a[1]),abs(a[2]))
def allowed(a):return cone(a) and cone(sub((Q(4),Q(0),Q(0)),a))

def main():
    checks=0
    for den in range(2,101):
      for num in range(1,den):
        s=Q(num,den);h=(1-s)/4
        U=(h,h,h);O=(h,-h,-h);D1=(s/2,s/2,s/2)
        Cd=(Q(1,2),s/2,s/2);C0=(2*h,Q(0),Q(0))
        assert add(U,O)==C0 and add(add(U,D1),O)==Cd
        A=((1+s)/4,(1+s)/4,-(3*s-1)/4)
        D2=(Q(1,2),Q(1,2),s/2)
        B=((3+s)/4,(3+s)/4,(1-s)/4)
        Ca=(Q(1),(1+s)/2,Q(0))
        assert add(A,O)==(Q(1,2),s/2,-s/2)
        assert add(A,D2)==B and add(B,O)==Ca
        assert all(allowed(v) for v in (U,O,add(U,D1),A,B))
        assert cone(D1) and cone(D2)
        # Saturate the necessary scalar bounds, retaining exact arithmetic.
        ad=Q(1);cd=(1-s)/(1+s);bd=(cd-ad)/2
        assert dot((ad,bd,bd),add(U,D1))==h
        low=dot((ad,bd,-bd),A)
        assert low==(1-s)*(1+3*s)/(4*(1+s))
        ab=4*low/(3+s);a=Q(1);b=ab-a
        assert dot((a,b,Q(0)),B)==low
        ratio=dot((a,b,Q(0)),Ca)/value(Ca)
        assert ratio==4*(1+s)/(3+s)
        if s==Q(1,2):assert ratio==Q(12,7)
        assert 2-ratio==2*(1-s)/(3+s)
        checks+=1
    slack_checks=0
    for s in [Q(1,5),Q(1,2),Q(4,5)]:
      for e0,ed,ec,ea,ep in product([Q(0),Q(1,7),Q(3,2)],repeat=5):
        a0=1+e0;ad=1+ed;cd=(1-s)*a0/(1+s)+ec;bd=(cd-ad)/2
        low=(1+s)*ad/4+s*bd
        assert (1+s)*cd/4>=(1-s)*a0/4
        assert low>=(1-s)*(1+3*s)/(4*(1+s))
        a=1+ea;ab=4*low/(3+s)+ep;b=ab-a;r=(1+s)/2
        assert (3+s)*ab/4>=low
        assert a+r*b>=(1-s)/2*(4*(1+s)/(3+s))
        assert all(v>=0 for v in [(1-s)/4,s/2,1-r,r])
        slack_checks+=1
    rays=((1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1))
    assert add(rays[0],rays[3])==add(rays[1],rays[2])
    orthant=0
    for z in product(range(7),repeat=4):
        C=tuple(sum(z[j]*rays[j][k] for j in range(4)) for k in range(3))
        assert value(C)==2*(min(z[0],z[3])+min(z[1],z[2]))
        orthant+=1
    for z,p,q in [((1,1,1,0),(1,Q(-1,2),Q(-1,2)),(0,1,1,2)),
                  ((Q(3,2),Q(1,2),Q(1,2),Q(1,2)),(1,Q(-1,3),Q(-1,3)),(Q(1,3),1,1,Q(5,3)))]:
        C=tuple(sum(z[j]*rays[j][k] for j in range(4)) for k in range(3))
        assert C==(3,1,1)
        assert tuple(dot(p,r) for r in rays)==q
        assert q[0]+q[3]==q[1]+q[2]
    print(f'PASS: {checks} exact two-owner restoration certificates; {slack_checks} rational-slack inequality chains; {orthant} generator identities; exact12/7 example; asymptotic2 gap formula; pointwise descent but representation dependence.')

if __name__=='__main__':main()
