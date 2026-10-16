from pathlib import Path
BASE=Path(__file__).parent
s=(BASE.parent/'stronger_shape'/'STRONGER_RATIONAL_TILT_THEOREM.txt').read_text()
def rep(a,b):
 global s
 if a not in s:raise RuntimeError('missing '+a[:80])
 s=s.replace(a,b)
rep('A STRONGER RATIONAL TILT WITH SHARP FUNDING FACTOR ABOUT 1.129754606','THE QUARTER-PARAMETER RATIONAL TILT: SHARP FUNDING FACTOR ABOUT 1.129174349')
rep('gamma=1+(-18s_*^2+39s_*-13)(1+s_*)^3/[270s_*(3s_*-1)]','gamma=1+(-36s_*^2+93s_*-41)(1+s_*)^3/[270s_*(9s_*-5)]')
rep('-162s^4+306s^3-255s^2+104s-13=0.','-972s^4+2394s^3-2421s^2+1148s-205=0.')
rep('1.129754606127951','1.1291743487400028')
rep('f(u)=(3u-2)^2/[5(3u-1)] for2/3<u<=1,','f(u)=2(3u-2)^2/[5(9u-5)] for2/3<u<=1,')
rep("f'(u)=3/5-3/[5(3u-1)^2] for u>2/3.\nIn fact f'(1)=9/20", "f'(u)=(2/5)[1-1/(9u-5)^2] for u>2/3.\nIn fact f'(1)=3/8")
start=s.index('For u>q put v=3u-2')
end=s.index('\nUnder a short increase',start)
s=s[:start]+'''For u>q put v=3u-2 in(0,1]. Then
  f(u)=2v^2/[5(1+3v)],
  f'(u)=6v(2+3v)/[5(1+3v)^2], f''(u)=36/[5(9u-5)^3]>0.
The following bounds will be used:
  f'(u)u(1-u)<=1/9,
  f'(u)u(1-u)<=(8/15)v(1-v), v=3u-2,
  f'(s)s(1-s)<=1/16.                                   (RT_bounds)
The first follows from f'<=1/2 and u(1-u)<=2/9. For the second,
  f'(u)u(1-u)=2v(2+3v)(v+2)(1-v)/[15(1+3v)^2],
and each of(2+3v)/(1+3v) and(v+2)/(1+3v) is at most2.
For the third, the desired inequality is equivalent to
  P4(v)=96v^4+160v^3+7v^2-38v+15>=0.
Its second derivative1152v^2+960v+14 is at least14 on[0,1]. At v0=1/4,
P4(v0)=141/16 and P4'(v0)=3/2. Strong convexity therefore gives
  P4(v)>=141/16+(3/2)(v-1/4)+7(v-1/4)^2
        >=141/16-(3/2)^2/28=489/56>0.
These derivative bounds are zero below q. Convexity and the endpoint
values f(q)=0,f(1)=1/10 also give the useful secant bound
  f(t)<=(3/10)(t-2/3), hence1/2+f(t)<=(3/10)(1+t)
for2/3<=t<=1.                                       (RT_secant)
''' + s[end:]
start=s.index('If L is active, d<=R and\n')
end=s.index('If L is inactive instead,',start)
s=s[:start]+'''If L is active, d<=R, lambda>=1-R, and R=L(1-t)/t<1/2. The constant
term is bounded below by
  1-R/lambda-f'(t)t(1-t)/h
  >=(1-2R)/(1-R)-f'(t)t(1-t)/h.
Because L<=1, R<=(1-t)/t. The first term decreases in R, and is at least
  (3t-2)/(2t-1)=3v/(2v+1), v=3t-2.
The second shape bound in(RT_bounds), together with
(1-v)(2v+1)<=9/8 and h>=2/5, gives
  f'(t)t(1-t)(2v+1)<=3v/5<3hv.
Thus the lower bound is positive. This argument retains the actual water
level and residual cap mass rather than dropping their relation.
''' + s[end:]
rep("h'_+x<=(1-s)/9+f'(s)s(1-s)<=1/27+1/20=47/540.\nThus(RT_hard)>=1-(3/5)(3/2)-47/540=7/540>0.","h'_+x<=(1-s)/9+f'(s)s(1-s)<=1/27+1/16=43/432.\nThus(RT_hard)>=1-(3/5)(3/2)-43/432=1/2160>0.")
start=s.index('Suppose s<=2/3.')
end=s.index('\n6. MAXIMUM SHORT OWNER',start)
s=s[:start]+'''Suppose s<=2/3. If t<=2/3 both tilt and its derivative vanish, and the
reviewed half-prefactor derivative proof applies. Otherwise t>2/3. The
largest actual long cap L is active: with inactive auxiliary cap this
follows from D>1, and with active auxiliary cap, inactivity of L would give
t<=L<=lambda<s<=2/3, a contradiction. It is the only active actual cap,
so P and the water level can be retained exactly.

With inactive auxiliary cap, lambda=1-R and P=lambda/L. Since x<=1/2,
L=tD>=t, and beta=1/lambda-k, one obtains
  P(1+beta*x)<=(lambda+x)/L
               =(1+x)/L-(1-t)/t<=1+1/(2t).
Here h=1/2+f(t). The secant bound(RT_secant) gives
  hP(1+beta*x)<=(3/10)(1+t)(1+1/(2t))<=9/10,
because t+1/(2t)<=3/2 for1/2<=t<=1.
With active auxiliary cap, lambda=(1+s-R)/2<s, P=lambda^2/(sL),
and x<=1-s. Therefore lambda+x<=1 and
  P(1+beta*x)<=lambda(lambda+x)/(sL)<=1/L<=1/t<3/2,
so again hP(1+beta*x)<=9/10. In both orientations, s<=2/3 implies
h'_+=1_{k=1}f'(t)t(1-t)<=1/9, and x<=1/2. Consequently
  (RT_hard)>=1-9/10-1/18=2/45>0.
This uses exact product slack, avoiding the insufficient coarse tilt-cost
bound near t=2/3. Every nonmaximum-short case is safe.
''' + s[end:]
rep("-1/2+s f'(s)(1-s)<=-9/20<0","-1/2+s f'(s)(1-s)<=-7/16<0")
start=s.index('For s<=2/3 and L>2/3, divide')
end=s.index('\nFinally suppose both L',start)
s=s[:start]+'''For s<=2/3 and L>2/3, divide the right side by L-s. With L fixed its
maximum over s<=2/3 is at s=2/3. Writing v=3L-2, that maximum is
  f(L)(L+2/3)/(L-2/3)=2v(v+4)/[5(1+3v)]<=1/2,
since the inequality is equivalent to(v-1)(4v+5)<=0 on[0,1]. If L<=2/3
the right side vanishes. For s>2/3 and L>s, use the exact difference
  f(L)-f(s)=(2/5)(L-s)[1-1/((9L-5)(9s-5))].
The right side of(RT_balance), divided by L-s, is
  Q(L)=(2/5)(L+s)[1-1/((9L-5)(9s-5))]
        -K L/(L-s), K=s(1-s)f'(s)>=0.
The first term has derivative
  (2/5)[1+(9s+5)/((9L-5)^2(9s-5))]>0;
the second has derivative K s/(L-s)^2>=0. Hence Q(L)<=Q(1). With
v=3s-2, direct simplification gives
  Q(1)=(1+s)[f(1)-f(s)]/(1-s)-s f'(s)
      =1/2-v(1+v)/(1+3v)^2<=1/2.                     (RT_balance_margin)
This formula applies for s<1; at s=1 there is no L>s to check.
At L=s the undivided right side is nonpositive. This proves(RT_balance),
including all endpoints.
''' + s[end:]
rep("-1+2s f'(s)(1-s)<=-9/10<0","-1+2s f'(s)(1-s)<=-7/8<0")
rep("x s f'(s)<=s(1-s)f'(s)<=1/20, so its derivative is at least7/20.","x s f'(s)<=s(1-s)f'(s)<=1/16, so its derivative is at least27/80.")
start=s.index('In this reduction\n')
end=s.index('\n10. SHARP MAXIMUM',start)
s=s[:start]+'''In this reduction
  f(t)=2(1-2R)^2/[5(1+R)(4-5R)].
If s<=1-R the auxiliary cap is inactive and E=h R(1-R). Put u=1/2-R.
For0<=R<=1/2, (1+R)(4-5R)=4-R-5R^2>=9/4. Dropping -f(s) gives
  E<=[1/2+(32/45)u^2](1/4-u^2)<=1/8.
If s>=1-R the auxiliary cap is active and
  E2(s,R)=h(s,1/(1+R))*R*(1+s-R)^2/(4s).
For fixed s its derivative in R has the sign of
  K=h(1+s-3R)
       -(6/5)(1-2R)(5-4R)R(1+s-R)/[(1+R)^2(4-5R)^2].
This follows from the exact derivative
  h_R=-(6/5)(1-2R)(5-4R)/[(1+R)^2(4-5R)^2].
Use h>=2/5, s>=1-R and1+s-R<=2-R. The polynomial
R(2-R)(5-4R)=10R-13R^2+4R^3 increases on[0,1/2], because its derivative
is12(R-1/2)(R-5/3)>=0, so its maximum is9/4. Also the squared denominator
is at least81/16. Therefore
  K>=(1-2R)[4/5-(6/5)(9/4)/(81/16)]
    =(4/15)(1-2R)>=0.
The allowed interval1-s<=R<=1/2 is preserved while increasing R.
Thus E2 is at most its value at R=1/2:
  [1-2f(s)](s+1/2)^2/(16s)<=[1-2f(s)]F(s)=g(s).
The last comparison follows from
  32(1+s)^3-27(2s+1)^2=(2s-1)^2(8s+5)>=0;
here s>=1/2 and1-2f(s)>0. Since max g>=1/8, all dominant-long cases are
bounded by max g as well.
''' + s[end:]
start=s.index('For s<=1/2, g=1/8;')
end=s.index('\nFor any s>=1/2',start)
s=s[:start]+'''For s<=1/2, g=1/8; for1/2<=s<=2/3, g=F increases. For s>=2/3,
  g(s)=(-36s^2+93s-41)(1+s)^3/[270s(9s-5)],
  g'(s)=(1+s)^2 J(s)/[270s^2(9s-5)^2],
  J(s)=-972s^4+2394s^3-2421s^2+1148s-205.
Here J(2/3)=5/3>0,J(1)=-56<0,J'(2/3)=-40. Also
  J''(s)=-11664s^2+14364s-4842<0
for every real s, because its leading coefficient is negative and its
discriminant is -19583856<0. Thus J' is decreasing and negative on[2/3,1],
so J has exactly one root s_* there. The funding curve g has its unique
global maximum at s_*, proving(RT_gamma). Rational bisection of J together
with monotone bounds on1-2f and F gives rigorous decimal enclosures.
''' + s[end:]
start=s.index('11. RELATION TO THE PRECEDING RATIONAL RULE.')
s=s[:start]+'''11. RELATION TO THE PRECEDING RATIONAL RULE.
This shape is f_a with a=1/4 in
  f_a(s)=(1/10)v^2/[a+(1-a)v], v=3s-2>0,
and zero otherwise. It exceeds the preceding a=1/2 and a=2/3 shapes
strictly on2/3<s<1, with equality at the endpoints. Hence its funding
curve is smaller there, and its sharp factor is strictly smaller than
both preceding factors. The proof above is not based on this comparison:
it independently checks all mixed-owner incentive cases, including those
where the older coarse inequalities are no longer sufficient.
'''
(BASE/'QUARTER_RATIONAL_TILT_THEOREM.txt').write_text(s)
print('wrote',len(s.splitlines()),'lines')
