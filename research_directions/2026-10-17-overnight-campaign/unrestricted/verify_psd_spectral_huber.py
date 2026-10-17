"""Exact rational 2x2 spectral-Huber own-monotonicity obstruction."""
from fractions import Fraction as F


def add(A,B): return tuple(a+b for a,b in zip(A,B))
def scale(c,A): return tuple(c*a for a in A)
def det(A): return A[0]*A[2]-A[1]*A[1]
def trace(A): return A[0]+A[2]
def inner(A,B): return A[0]*B[0]+2*A[1]*B[1]+A[2]*B[2]
def psd(A): return A[0]>=0 and A[2]>=0 and det(A)>=0
def price(C,a,b):
    assert 0<a<b
    assert trace(C)==a+b and det(C)==a*b
    return (1+a/(2*b)-C[0]/b,-C[1]/b,1+a/(2*b)-C[2]/b)


def main():
    X=(F(1,20),F(1,5),F(4,5))
    Y=(F(1,5),-F(1,5),F(1,5))
    H=(F(1),F(6),F(36))
    D=scale(F(1,145),H)
    assert psd(X) and psd(Y) and psd(D)
    assert det(X)==det(Y)==det(D)==0
    C=add(X,Y)
    assert C==(F(1,4),F(0),F(1))
    P=price(C,F(1,4),F(1))
    assert P==(F(7,8),F(0),F(1,8)) and psd(P) and trace(P)==1
    Xp,Cp=add(X,D),add(C,D)
    assert Xp==(F(33,580),F(7,29),F(152,145)) and psd(Xp)
    assert Cp==(F(149,580),F(6,145),F(181,145)) and psd(Cp)
    Pp=price(Cp,F(37,145),F(5,4))
    assert Pp==(F(26,29),-F(24,725),F(3,29))
    assert psd(Pp) and trace(Pp)==1
    old,new=inner(P,X),inner(Pp,Xp)
    assert old==F(23,160) and new==F(6033,42050)
    assert new-old==-F(187,672800)
    assert old<F(1,4) and new<F(37,145)
    # Huber spectral branches: P-small eigenvalue=a/(2b), P-large=1-P-small.
    for p,a,b in [(P,F(1,4),F(1)),(Pp,F(37,145),F(5,4))]:
        psmall=a/(2*b)
        assert det(p)==psmall*(1-psmall)
        assert 0<psmall<F(1,2)
    K=(F(5,4),-F(1,5),F(1,32))
    assert det(K)==-F(3,3200)
    assert inner(K,H)==-F(1,40)
    # Extra eigendirections belong only to the other owner: both remain singular.
    ap,bp=F(37,145),F(5,4)
    low_projector=((bp-Cp[0])/(bp-ap),-Cp[1]/(bp-ap),(bp-Cp[2])/(bp-ap))
    new_low_mass=inner(low_projector,Xp)
    assert new_low_mass==F(3224,83665)
    old_low_product=F(1,4)*X[0]
    for reciprocal_sum,loss in [(F(1,5),-F(10909,970514000)),
                                (F(1,10),-F(561313,3882056000))]:
        extended_old=old-old_low_product*reciprocal_sum/2
        extended_new=new-ap*new_low_mass*reciprocal_sum/2
        assert extended_new-extended_old==loss
        assert 1-F(1,8)-F(1,4)*reciprocal_sum/2>F(1,2)
        assert 1-ap/(2*bp)-ap*reciprocal_sum/2>F(1,2)
    print('PASS: all exact PSD/eigenvalue/price identities; own payment change -187/672800; '
          'negative derivative -1/40; both focal caps inactive; singular-owner lifts in every m>=3.')


if __name__=='__main__': main()
