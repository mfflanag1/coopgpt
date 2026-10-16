from pathlib import Path
BASE=Path(__file__).parent
s=(BASE.parent/'RATIONAL_PARAMETER_FAMILY_THEOREM.txt').read_text()
def rep(a,b):
 global s
 if a not in s:raise RuntimeError('missing '+a[:80])
 s=s.replace(a,b)
rep('EXACT TRUTHFUL PARAMETER INTERVAL FOR THE RATIONAL TILT FAMILY','OPTIMAL SEPARABLE CONCENTRATION TILT FOR THE FIXED WATER-PRODUCT ARCHITECTURE')
start=s.index('For every parameter a>0')
end=s.index('\n1. DEFINITION.',start)
s=s[:start]+'''Consider the water-product architecture defined below, with separable
prefactor h(s,t)=1/2+f(t)-f(s), where f is zero on[0,2/3]. Among ALL such
rules that are universally truthful for fixed actual owners, the optimal
funding factor is
  Gamma=1+(-17rho^2+24rho-8)(1+rho)^3/
           [216rho(1-rho)(2rho-1)],                    (OS_gamma)
where rho is the unique root in(2/3,1) of
  68rho^5-235rho^4+308rho^3-199rho^2+64rho-8=0.
Numerically rho is about0.6745420332091702 and Gamma about1.128751298487466.
The lower bound requires no continuity, differentiability or monotonicity
assumption on f. It follows from one finite four-owner report comparison.
A convex, continuously differentiable piecewise-algebraic shape achieves the
bound, while giving nonnegative payments and covering every coalition for
all finite fixed-owner instances and every real report profile. The upper
and lower bounds therefore meet for this architecture.
This does not prove a lower bound against arbitrary truthful mechanisms.
The broader9/8 lower bound and historical novelty remain separate questions.
''' +s[end:]
rep('f(u)=0 for0<=u<=2/3,\n  f(u)=f_a(u)=(1/10)v^2/[a+(1-a)v], v=3u-2, for2/3<u<=1,','''q0=2/3,
  C(u)=u^2/[8(1-u)(2u-1)]-1/2 forq0<=u<1.
Let tau be the unique real root of
  53tau^3-91tau^2+55tau-12=0,
and let kappa=C'(tau). Define the achieving shape
  f(u)=0 for0<=u<=q0,
  f(u)=C(u) forq0<=u<=tau,
  f(u)=1/10-kappa(1-u) fortau<=u<=1,''')
start=s.index('For all a>0, f is continuously differentiable')
end=s.index('Therefore2/5<=h',start)
s=s[:start]+'''Section2 proves that this f is convex, continuously differentiable and
nondecreasing, with f(q0)=0,f(1)=1/10 and0<=f'<=5/16<1/2. Thus0<=f<=1/10.
''' +s[end:]
start=s.index('Uniformly for4/45<=a<=2/3')
end=s.index('\nUnder a short increase',start)
s=s[:start]+'''Here are the shape facts used in the incentive proof. Put
  chi(u)=(3u-2)/[u(1-u)(2u-1)]
        =2/u+1/(1-u)-2/(2u-1).
Then C'(u)=(1/2+C(u))chi(u). On[q0,1), chi>=0 and
  chi'(u)=-2/u^2+1/(1-u)^2+4/(2u-1)^2>0,
because1/(1-u)^2>=9 and2/u^2<=9/2. Consequently C is increasing and
strictly convex, C(q0)=C'(q0)=0. Its tangent reaches(1,1/10) exactly when
  (1-u)C'(u)+C(u)-1/10=0,
whose numerator after multiplication by20(1-u)(2u-1)^2 is
  T(u)=53u^3-91u^2+55u-12.
The derivative T'=159u^2-182u+55 is everywhere positive (discriminant-1856).
Moreover
  T(17/25)=-211/15625<0,
  T(683/1000)=936311/10^9>0.
Thus17/25<tau<683/1000, and the definition glues C1 to the tangent line.
The derivative is nondecreasing up to tau and constant thereafter, so f is
convex. Exact endpoint comparisons give
  1/4<C'(17/25)=10625/41472<13/50,
  C'(683/1000)=1045843750/3365276121<5/16.
Hence1/4<kappa<5/16. In particular
  f'(u)u(1-u)<=1/9,
  f'(u)u(1-u)<=5/72,                                 (OS_bounds)
and f'(u)<=13/50 when2/3<=u<=17/25. Below2/3 the derivative is zero.
Convexity and the endpoint values also imply
  f(t)<=(3/10)(t-2/3), hence1/2+f(t)<=(3/10)(1+t)
for2/3<=t<=1.                                       (OS_secant)

The critical pure-long incentive inequality is
  f'(t)/(1/2+f(t))<=chi(t), 2/3<t<1.                  (OS_critical)
It holds with equality while f=C. At tau the two sides agree. Afterwards
the left side is kappa/[1/2+1/10-kappa(1-t)], which decreases, while chi
increases. Thus it holds on the tangent segment as well. At1 the original
undivided form f'(t)t(1-t)<=(1/2+f(t))(3t-2)/(2t-1) follows by continuity.
''' +s[end:]
s=s.replace('(PF_bounds)','(OS_bounds)').replace('(PF_secant)','(OS_secant)').replace('(PF_long)','(OS_long)')
rep('At s=1, H>=(2/5)(2-3R)/(2-R)>=2/15>1/16, so(OS_long) holds.\nAt s=1-R with R<=1/3, H>=(2/5)(1-2R)/(1-R)>=1/5>1/16.','At s=1, H>=(2/5)(2-3R)/(2-R)>=2/15>5/72, so(OS_long) holds.\nAt s=1-R with R<=1/3, H>=(2/5)(1-2R)/(1-R)>=1/5>5/72.')
start=s.index('only to prove, with v=3t-2,')
end=s.index('If L is inactive instead,',start)
s=s[:start]+'''only to prove
  f'(t)t(1-t)<=(1/2+f(t))(3t-2)/(2t-1).
This is exactly(OS_critical), already proved for the constructed shape.
It completes every active nonmaximum-long case.
''' +s[end:]
start=s.index('Here e=0 and x<=min(s,1-s). If s>2/3,')
end=s.index('\nSuppose s<=2/3.',start)
s=s[:start]+'''Here e=0 and x<=min(s,1-s). If s>2/3, the water identities imply
P(1+beta*x)<=1/s in either auxiliary-cap orientation. In the inactive case
use lambda>=s and P<=1; in the active case use P<=lambda/s. Also
  h'_+x<=(1-s)/9+f'(s)s(1-s).
For2/3<s<=17/25, use h<=3/5,1/s<=3/2, and f'(s)<=13/50, giving
  (RT_hard)>=1-9/10-1/27-13/225=7/1350>0.
For s>=17/25, retain1/s<=25/17 and use f'<=5/16, giving
  (RT_hard)>=1-15/17-1/27-5/72=41/3672>0.
The global1/16 derivative-product bound used for the rational parameter
family is false for this optimal shape; these two estimates replace it.
''' +s[end:]
rep("-1/2+s f'(s)(1-s)<=-7/16<0","-1/2+s f'(s)(1-s)<=-31/72<0")
start=s.index('For s<=2/3 and L>2/3, divide')
end=s.index('\nFinally suppose both L',start)
s=s[:start]+'''For s<=2/3 and L>2/3, divide the right side by L-s. With L fixed its
maximum over s<=2/3 is at s=2/3. Convexity gives
  f(L)(L+2/3)/(L-2/3)<=(3/10)(L+2/3)<=1/2.
For L<=2/3 the right side vanishes. For s>2/3 and L>s, write its quotient as
  Q(L)=(L+s)[f(L)-f(s)]/(L-s)-K L/(L-s),
  K=s(1-s)f'(s)>=0.
The nonnegative secant slope[f(L)-f(s)]/(L-s) is nondecreasing in L by
convexity, so its product with L+s is nondecreasing. The second term also
increases, with derivative K s/(L-s)^2. Hence Q(L)<=Q(1), and it suffices to
check
  Q(1)=(1+s)[1/10-f(s)]/(1-s)-s f'(s)<=1/2.            (OS_balance)
If s>=tau, the tangent formula gives Q(1)=kappa<1/2. If q0<s<=tau, f=C,
and after multiplication by the positive denominator40(1-s)^2(2s-1)^2,
the numerator of1/2-Q(1) is
  N(s)=-4-24s+173s^2-316s^3+186s^4.
Writing s=2/3+x gives exactly
  N(s)=(52/9)x+37x^2+180x^3+186x^4>=0.
At L=s the undivided right side of(RT_balance) is nonpositive. This proves
all cases, including the C1 junction at tau and the endpoints.
''' +s[end:]
rep("-1+2s f'(s)(1-s)<=-7/8<0","-1+2s f'(s)(1-s)<=-31/36<0")
rep("x s f'(s)<=s(1-s)f'(s)<=1/16, so its derivative is at least27/80.","x s f'(s)<=s(1-s)f'(s)<=5/72, so its derivative is at least119/360.")
rep('The extra concentration thresholds are also linear after clearing\npositive denominators.', 'The extra concentration thresholds2/3 and tau are also linear after\nclearing positive denominators, with fixed real coefficients.')
s=s.replace('g_a(s)','g(s)').replace('max g_a','max g')
rep('This funding argument works uniformly for the entire truthful interval.','This funding argument uses only the already-proved incentives of this rule.')
start=s.index('10. SHARP FUNDING, FAMILY OPTIMUM, AND COMPUTATION.')
s=s[:start]+'''10. EXACT SHARP FUNDING OF THE CONSTRUCTED RULE.
For s<=1/2, g=1/8; for1/2<=s<=2/3, g=F increases, with
  g(2/3)=125/972>1/8.
On2/3<=s<=tau the ceiling shape gives
  g_C(s)=(-17s^2+24s-8)(1+s)^3/[216s(1-s)(2s-1)],
  g_C'(s)=(1+s)^2 J(s)/[216s^2(1-s)^2(2s-1)^2],
  J(s)=68s^5-235s^4+308s^3-199s^2+64s-8.
At s=2/3+x,
  J=4/243-(164/81)x-(221/27)x^2-(148/9)x^3-(25/3)x^4+68x^5.
For0<=x<=1/3, its derivative is negative: the positive term340x^4 is
at most(340/9)x^2, leaving
  J'<=-164/81-(442/27)x-(104/9)x^2-(100/3)x^3<0.
Also J(2/3)=4/243>0 and J(1)=-2<0. There is exactly one root rho in(2/3,1).
The exact value J(27/40)=-25331/25600000<0 shows
  rho<27/40<17/25<tau.
Thus g_C attains its unique maximum at rho before the shape switches.

On tau<=s<=1, set A=4/5+2kappa. The funding curve is
  g_lin(s)=(A-2kappa s)(1+s)^3/(54s).
Its derivative has the sign of
  A(2s-1)-6kappa s^2.
This quadratic has negative leading coefficient and discriminant
  4A(A-6kappa)=4A(4/5-4kappa)<0,
since kappa>1/4>1/5. It is strictly negative everywhere, so the tangent
segment's funding curve decreases. Consequently the unique global maximum
is g_C(rho), proving the upper bound(OS_gamma).

For any s>=1/2, take four pure owners with short reports(s,1-s,0,0) and long
reports(0,0,1,1). Then t=1/2,lambda=(1+s)/3,P=lambda^3/s and the excess is
exactly(1-2f(s))F(s). At s=rho, f=C, so this profile attains Gamma exactly.
All four owners are fixed and have positive capacity. Rational profiles
approach the same factor, but the all-real theorem includes the exact
algebraic attainer.

11. MATCHING ALL-SHAPE LOWER BOUND WITHOUT REGULARITY ASSUMPTIONS.
Let an arbitrary real-valued f vanish on[0,2/3] and use the SAME fixed
water-product architecture, with h(s,t)=1/2+f(t)-f(s). Suppose the resulting
rule is own-report monotone on every fixed-owner instance. No continuity,
measurability, differentiability, monotonicity or convexity of f is assumed.
Fix four pure owners with short reports(1/2,1/2,0,0) and long reports(0,0,1,R).
For0<R<=1/2 the water level is1-R, the auxiliary cap is inactive, and the
residual owner's payment is
  Y(R)=[1/2+f(1/(1+R))]R(1-R).
At R=1/2, both concentration arguments are at most2/3, so Y(1/2)=1/8.
Truthfulness under the SAME residual owner's finite underreport implies
  Y(R)<=1/8.
Setting t=1/(1+R) proves the exact pointwise ceiling
  f(t)<=t^2/[8(1-t)(2t-1)]-1/2=C(t), 2/3<=t<1.        (OS_ceiling)
This finite comparison also justifies the differential ceiling when f is
smooth, but no integration or regularity premise is needed.

Now evaluate the same architecture at the four-owner concentration profile
from Section10, with s=rho. Its funding ratio is
  1+(1-2f(rho))F(rho)>=1+(1-2C(rho))F(rho)=Gamma.
Thus every universally truthful rule in this architecture has worst-case
funding factor at least Gamma. In particular this holds for those that are
nonnegative and cover every coalition. The constructed rule achieves Gamma,
so the all-shape architecture optimum is exact. This lower bound does not
apply to mechanisms outside this architecture or shapes that do not vanish
on[0,2/3]. It uses four fixed owners and no identity changes.

12. EXACT COMPUTATION AND SCOPE.
The two constants tau and rho are specified by cubic and quintic equations
with unique isolated roots. The rule itself uses only tau and
kappa=C'(tau), so rational reports produce payments in the fixed algebraic
number field Q(tau), of degree at most3; they need not be rational numbers.
Comparisons to tau can be made with exact algebraic arithmetic or certified
root intervals, including equality by the defining polynomial. Sorting caps
and water filling require O(n log n) comparisons and O(n) arithmetic steps;
bit complexity additionally depends on input/output precision or exact
algebraic encodings. An exact implementation must preserve these comparisons
and must not silently replace tau by a floating constant near a tie.

The theorem concerns the two-input cooperative production game and its
report-independent positive sums. It does not automatically replace a
primitive inside a nested network that requires extra role-payment bounds.
It establishes an exact optimization within a specific water-product and
separable-tilt architecture, not unrestricted mechanism optimality or
historical novelty. The manuscript should make that distinction explicit.
'''
(BASE/'OPTIMAL_SEPARABLE_TILT_THEOREM.txt').write_text(s)
print('wrote',len(s.splitlines()),'lines')
