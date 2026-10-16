from pathlib import Path
BASE=Path(__file__).parent
s=(BASE.parent/'quarter_shape'/'QUARTER_RATIONAL_TILT_THEOREM.txt').read_text()
def rep(a,b):
 global s
 if a not in s:raise RuntimeError('missing '+a[:80])
 s=s.replace(a,b)
rep('THE QUARTER-PARAMETER RATIONAL TILT: SHARP FUNDING FACTOR ABOUT 1.129174349','EXACT TRUTHFUL PARAMETER INTERVAL FOR THE RATIONAL TILT FAMILY')
start=s.index('The mechanism below is nonnegative, covers every actual coalition')
end=s.index('\n1. DEFINITION.',start)
s=s[:start]+'''For every parameter a>0 define f_a below and use the same water-product
rule. The rule covers every coalition and is nonnegative for every a>0.
It is own-report monotone for all actual mixed owners and all profiles IF
AND ONLY IF
  4/45<=a<=2/3.                                        (PF_interval)
For a in this interval, its exact sharp funding factor is
  gamma(a)=1+max_{0<s<=1}[(1-2f_a(s))F(s)],
  F(s)=1/8 for s<=1/2, F(s)=(1+s)^3/(54s) for s>=1/2.   (PF_gamma)
The function gamma(a) is strictly increasing on the truthful interval.
Its unique optimum within this one-parameter family is a0=4/45, with
  gamma0=1+(-27s_*^2+77s_*-38)(1+s_*)^3/[54s_*(41s_*-26)],
where s_* is the unique root in(2/3,1) of
  -3321s^4+9122s^3-10019s^2+5092s-988=0.                (PF_optimum)
Numerically s_* is about0.6790666428875705 and gamma0 about1.1288005100532479.
The algebraic definitions are exact; decimal certification is supplementary.
The four-owner concentration profile attains each factor. These are exact
claims about this specified family, not a globally optimal truthful mechanism,
a lower bound for all possible rules, or a historical priority claim.
''' +s[end:]
rep('f(u)=2(3u-2)^2/[5(9u-5)] for2/3<u<=1,','f(u)=f_a(u)=(1/10)v^2/[a+(1-a)v], v=3u-2, for2/3<u<=1,')
start=s.index('On[0,1], f is continuously differentiable')
end=s.index('Therefore2/5<=h',start)
s=s[:start]+'''For all a>0, f is continuously differentiable, nondecreasing and convex,
with f(2/3)=0 and f(1)=1/10. Thus0<=f<=1/10. In the incentive proof assume
4/45<=a<=2/3. Writing D_a(v)=a+(1-a)v,
  f'(u)=(3/10)v[2a+(1-a)v]/D_a(v)^2,
  f''(u)=9a^2/[5D_a(v)^3] foru>2/3,
  f'(1)=(3/10)(1+a)<=1/2.
Hence0<=f'<=1/2 throughout the truthful interval.
''' +s[end:]
start=s.index('For u>q put v=3u-2')
end=s.index('\nUnder a short increase',start)
s=s[:start]+'''Uniformly for4/45<=a<=2/3, the following shape bounds hold:
  f'(u)u(1-u)<=1/9,
  f'(u)u(1-u)<=1/16.                                  (PF_bounds)
The first follows from f'<=1/2 and u(1-u)<=2/9 when u>2/3; both sides of
the derivative expression vanish below that threshold. To prove1/16 put
v=3u-2 in(0,1), D=a+(1-a)v. The expression is
  B(a,v)=v[2a+(1-a)v](v+2)(1-v)/(30D^2).
For fixed v, its a-derivative has the sign of
  v^2-a(2-v)(1-v).
Its unconstrained maximum over positive a is therefore at
  a_*(v)=v^2/[(2-v)(1-v)],
and that maximum equals(2-v)^2(v+2)/120. For v>=1/4 this last expression
is decreasing and at most147/2560<1/16. For v<=1/4, a_*(v)<=1/21<4/45;
therefore B(a,v)<=B(4/45,v), since B decreases past its maximizer. At4/45,
the inequality B<=1/16 is equivalent to
  P4(v)=16-56v-95v^2+1176v^3+984v^4>=0.
For0<=v<=1/5, P4>=16-56/5-95/25=1. For1/5<=v<=1/4,
  P4>=16-56/4-95/16+1176/125=10941/2000>0.
This proves the uniform bound, including v=0,1 by continuity.
Convexity and the endpoint values also give
  f(t)<=(3/10)(t-2/3), hence1/2+f(t)<=(3/10)(1+t)
for2/3<=t<=1.                                       (PF_secant)
''' +s[end:]
s=s.replace('(RT_bounds)','(PF_bounds)').replace('(RT_secant)','(PF_secant)')
start=s.index('If L is active, d<=R, lambda>=1-R')
end=s.index('If L is inactive instead,',start)
s=s[:start]+'''If L is active, d<=R and R=L(1-t)/t<1/2. Its constant term is at least
  1-R/lambda-f'(t)t(1-t)/h.
It is therefore enough to show
  H(s):=h(s,t)(1-R/lambda)>=f'(t)t(1-t).                (PF_long)
For fixed t,R, the water level is1-R when s<=1-R, and(1+s-R)/2 otherwise.
On the first range H decreases in s, so its minimum is at s=1-R.
On the active-auxiliary range put w=1+s-R. The derivative of H has the sign
of N=-f'(s)w(w-2R)+2Rh. Differentiating on smooth cells gives
  N'=-f''(s)w(w-2R)-2w f'(s)<=0,
since w-2R>=2-4R>=0. N is continuous at s=2/3; hence H can have an
interior maximum but no strict interior minimum. Its minimum over all s
is attained at one of s=1-R and s=1. This minimization is an algebraic
upper-domain comparison; it does not change the actual owner's reports.

At s=1, H>=(2/5)(2-3R)/(2-R)>=2/15>1/16, so(PF_long) holds.
At s=1-R with R<=1/3, H>=(2/5)(1-2R)/(1-R)>=1/5>1/16.
For R>=1/3, f(1-R)=0 and
  H=(1/2+f(t))(1-2R)/(1-R).
Because L<=1, R<=(1-t)/t; the ratio in H decreases with R. Thus it remains
only to prove, with v=3t-2,
  f'(t)t(1-t)<=(1/2+f(t))*3v/(2v+1).                  (PF_critical)
After multiplying positive denominators, this is exactly C(a,v)>=0, where
  C(a,v)=a(45a-4)+(-90a^2+86a-2)v
          +(45a^2-72a+42)v^2+(12-8a)v^3+2(1-a)v^4.   (PF_polynomial)
All coefficients are nonnegative on4/45<=a<=2/3. The constant is
nonnegative by the lower parameter bound. The concave coefficient of v
has endpoint values74/15 and46/3, so is positive throughout. The coefficient
of v^2 has negative discriminant -2376 and positive leading coefficient.
The last two coefficients are nonnegative because a<=2/3<1. This proves
(PF_critical), hence every active nonmaximum-long case.
''' +s[end:]
start=s.index('For s<=2/3 and L>2/3, divide')
end=s.index('\nFinally suppose both L',start)
s=s[:start]+'''For s<=2/3 and L>2/3, divide the right side by L-s. With L fixed its
maximum over s<=2/3 is at s=2/3. Writing v=3L-2 and D=a+(1-a)v, this is
  f(L)(L+2/3)/(L-2/3)=v(v+4)/(10D)<=1/2,
since the inequality is equivalent to(v-1)(v+5a)<=0 on[0,1]. If L<=2/3
the right side vanishes. For s>2/3 and L>s put b=1-a>0 and
D_s=a+b(3s-2),D_L=a+b(3L-2). The exact difference identity is
  f(L)-f(s)=[3/(10b)](L-s)[1-a^2/(D_L D_s)].
The right side of(RT_balance), divided by L-s, becomes
  Q(L)=[3/(10b)](L+s)[1-a^2/(D_L D_s)]
        -K L/(L-s), K=s(1-s)f'(s)>=0.
The first term has derivative
  [3/(10b)][1+a^2(3bs+2-3a)/(D_L^2 D_s)]>0;
the second has derivative K s/(L-s)^2>=0. Here2-3a>=0 is essential.
Thus Q(L)<=Q(1). With v=3s-2 and D=a+(1-a)v, simplification gives
  Q(1)=(1+s)[f(1)-f(s)]/(1-s)-s f'(s)
      =1/2-v(2-3a)[2a+(1-2a)v]/(10D^2)<=1/2.         (PF_balance_margin)
The bracket2a+(1-2a)v=2a(1-v)+v is positive. This formula applies for s<1;
at s=1 there is no L>s to check. At L=s the undivided right side is
nonpositive. This proves(RT_balance), including all endpoints.
''' +s[end:]
start=s.index('In this reduction\n')
end=s.index('\n10. SHARP MAXIMUM',start)
s=s[:start]+'''After this reduction the excess is exactly the payment to a pure residual
long owner of capacity R in a profile with one other long owner of capacity1
and short maximum s. To see this without altering any incentive domain,
observe that every residual cap is below the water level, so splitting or
combining their mass changes neither P nor the scalar excess. The formula
for a pure residual owner's payment is pR, which equals the excess because
D-1=R. A finite pure-short profile with total1 and maximum s always exists.

Hold that comparison profile's short reports and unit long cap fixed, and
increase the residual owner's R from its present value to1/2. The long-own
monotonicity already proved in Section3 applies, including any auxiliary
water-level crossing, and proves the scalar excess cannot decrease. This
argument only uses an already established derivative inequality and is not
circular: the incentive proof used no funding assertion. Equivalently, on
an active-auxiliary cell the derivative of the excess has sign
  h(1+s-3R)-R(1+s-R)f'(t)t^2,
which is exactly the pure residual-owner inequality(PF_long).

At R=1/2, t=2/3, so f(t)=0. If s<=1/2, the auxiliary cap is inactive and
the excess is1/8. If s>=1/2, it is
  [1-2f(s)](s+1/2)^2/(16s)<=[1-2f(s)]F(s)=g_a(s).
The comparison follows from
  32(1+s)^3-27(2s+1)^2=(2s-1)^2(8s+5)>=0.
Since max g_a>=1/8, every dominant-long profile has excess at most max g_a.
This funding argument works uniformly for the entire truthful interval.
''' +s[end:]
start=s.index('10. SHARP MAXIMUM, ATTAINMENT, AND COMPUTATION.')
s=s[:start]+'''10. SHARP FUNDING, FAMILY OPTIMUM, AND COMPUTATION.
For s<=1/2, g_a=1/8; for1/2<=s<=2/3, g_a=F increases, with
  g_a(2/3)=125/972>1/8.
Moreover g_a'(2/3+)=F'(2/3)>0 since f_a'(2/3)=0, while
  g_a(1)=(4/5)F(1)=16/135<125/972.
Thus every g_a attains its maximum at an interior point of(2/3,1).

For any s>=1/2, take two pure short owners of reports s,1-s and two pure
long owners each of report1. Then t=1/2,lambda=(1+s)/3, P=lambda^3/s,
and the excess is exactly g_a(s). This proves sharpness of(PF_gamma) for
every permitted a with four fixed owners. Because
  partial f_a(s)/partial a=-v^2(1-v)/(10[a+(1-a)v]^2)<0
on2/3<s<1, g_a strictly increases with a there. Evaluating the larger-a
curve at an interior maximizer of the smaller-a curve proves that gamma(a)
is strictly increasing. Its unique minimum on the truthful interval is at
  a0=4/45.
At this endpoint,
  f_a0(s)=3(3s-2)^2/[2(41s-26)],
  g_a0(s)=(-27s^2+77s-38)(1+s)^3/[54s(41s-26)],
  g_a0'(s)=(1+s)^2 J(s)/[54s^2(41s-26)^2],
  J(s)=-3321s^4+9122s^3-10019s^2+5092s-988.
Here J(2/3)=16/27>0,J(1)=-114<0,J'(2/3)=-40. Also
  J''(s)=-39852s^2+54732s-20038<0
for every real s, because its leading coefficient is negative and its
discriminant is -198625680<0. Thus J' is decreasing and negative on[2/3,1],
so J has exactly one root s_* there. The funding curve has its unique global
maximum at s_*, proving(PF_optimum). Rational bisection of J and monotone
endpoint bounds on1-2f and F certify the stated decimal factor.

For rational a and reports, all operations in f,h, water filling,P and
payments are rational. Sorting caps gives O(n log n) comparisons and O(n)
arithmetic operations; bit complexity also counts input and output lengths.
The exact algebraic extremizer is included in the real-report theorem;
rational capacities approach its sharp value. This is a two-input theorem.
Replacing a primitive inside a nested network may require role-payment
properties not established by this funding theorem.

11. NECESSITY OF THE LOWER PARAMETER ENDPOINT.
Suppose0<a<4/45. Use four fixed pure owners: short reports(1/2,1/2,0,0)
and long reports(0,0,1,R), where R=1/2-u with u>0 small. The residual long
owner has zero short report, and the auxiliary cap is inactive. Its payment is
  Y_a(R)=[1/2+f_a(1/(1+R))]R(1-R).
It has derivative
  Y_a'(R)=[1/2+f_a(t)](1-2R)-R(1-R)f_a'(t)t^2,
  t=1/(1+R).
Since f_a(2/3)=f_a'(2/3)=0 and f_a''(2/3+)=9/(5a), Taylor expansion from
the right (or direct differentiation of the rational expression) gives
  lim_{u->0+} Y_a'(1/2-u)/u=1-4/(45a)<0.
Thus Y_a'<0 on an open interval just below1/2. Choosing two capacities
R_low<R_high within this interval gives Y_a(R_low)>Y_a(R_high): the same
actual owner profits by a coordinatewise underreport. No appeal to finite
sampling is needed. If a is rational the capacities can be chosen rational;
for arbitrary real a the theorem's real report domain permits the same
argument. The threshold is the first coefficient of(PF_polynomial), so the
sufficiency and obstruction meet exactly.

12. NECESSITY OF THE UPPER PARAMETER ENDPOINT.
Suppose a>2/3. The algebraic identity(PF_balance_margin) still holds for
any a>0. Fix any s in(2/3,1). Then2-3a<0 and2a(1-v)+v>0, so Q(1)>1/2.
Take four fixed pure owners with short reports(s,1-s,0,0) and long reports
(0,0,L,1-L), with s<L<1 sufficiently close to1. At full aggregate balance,
P=1 and the pools have common total1. A small decrease of the first short
owner's report makes that pool strictly short, with k=0, one active long
cap L and an inactive auxiliary cap. The owner's derivative from below,
multiplied by L, tends at balance to
  (L-s)/2-[f_a(L)-f_a(s)](L+s)+L s(1-s)f_a'(s).
As L->1, this tends to(1-s)[1/2-Q(1)]<0. Hence it is negative for L close
enough to1. By continuity of the derivative on a sufficiently small
one-sided neighborhood, a small underreport strictly increases the same
owner's payment. Pool orientation agrees at balance, so this is a genuine
whole-rule incentive failure. This proves necessity of a<=2/3.

Sections3--7 prove sufficiency; Sections11--12 prove necessity. The exact
interval(PF_interval) and its best factor(PF_optimum) are therefore proved.
The broader 9/8 lower bound, restrictions of other rule classes, and current
historical novelty remain separate questions.
'''
(BASE/'RATIONAL_PARAMETER_FAMILY_THEOREM.txt').write_text(s)
print('wrote',len(s.splitlines()),'lines')
