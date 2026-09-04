# A three-generator extension of PXC151 reaching asymptotic coefficient 2

Conventional all-parameter proof checked independently. Full-coalition rational verification passes four parameter tuples and all 16 exclusion queries. This extends the multiplicity of the intermediate role; it does not require a growing number of distinct payoff roles. External correctness and novelty review remain pending.

Let integers k>=1, m>=max(2,2k-2), r>=3. Set

    q=(k+1)m-k+2,
    A=km-k+1,
    B=q-1=A+m,
    y=r(q-1)-A,
    T=rq+m+1,
    n=m+k+r+3.

Players are U^m; b_1,...,b_k; c; d; E^r; g. Three efficient nonnegative generators:

    X=(1^m; (m-1)^k; y; 1; 1^r; 1),
    V=(0^m; 0^k; 0; 0; q^r; m+1),
    W=(0^m; (m+1)^k; T-k(m+1); 0; 0^r; 0).

Define v(S)=min(X(S),V(S),W(S)). This is exact, and the zero sets of V,W cover all players, so singleton-normalized. Positivity: q>m+1, A>0, y=rB-A>(r-1)B>=2B, and W_c=y+(m+r+2-2k)>=y+r since m>=2k-2.

## Global identities shared by the full core

For every ell in U union {d}, and every i in {1,...,k}, all three generators give coalition {b_i,ell,g} the same value m+1. The complementary coalition likewise has the common value T-m-1=rq. Hence every core allocation w satisfies

    w_bi+w_ell+w_g=m+1.

Thus there exist t,p such that all U,d coordinates equal t, all b_i coordinates equal p, and w_g=m+1-p-t.

The following two coalition families have easy generator minima:

    v({b_1,...,b_k,c,d} union E)=rq,
    v({c,g} union (E minus {e_j}))=rq-A.

For the first, X and V attain rq; W has T. For the second X and V attain rq-A; W's value exceeds it by exactly m-2k+2>=0.

The first family, taking complements and substituting the global equalities, gives

    p>=(m-1)t.

Write delta=p-(m-1)t>=0. Define

    H=m t+(k-1)p=A t+(k-1)delta,
    L=(m+1)t+k p=B t+k delta.

The second family and efficiency give

    w_ej+L<=q,
    w_c+sum_E w_e=rq-H.

Finally, with a=A/B in (0,1),

    a L-H=[(m-k+1)/B]delta>=0,

and the coefficient is strictly positive in the parameter domain.

## Unique maximin (hence full leximin)

For every ell in U union {d}, v(N minus {ell})=T-1, so w_ell<=1 throughout the core. X has all coordinates >=1, so the optimum floor is 1. On its optimal face t=1. Since w_g>=1 and w_g=m+1-p-t=m-p, we obtain p<=m-1. Combined with p>=(m-1)t, this gives p=m-1, g=1. Therefore L=B=q-1, and each E coordinate <=1. The floor makes all E coordinates exactly 1, and efficiency fixes c=y. The first-stage maximin face is the singleton {X}.

## Unique minimax (hence full leximax-min)

Let M be any core allocation's largest coordinate. From e_j<=q-L and efficiency,

    w_c>=rq-H-r(q-L)=rL-H>=(r/a-1)H.

Thus H<=a M/(r-a). On the other hand,

    rq=H+w_c+sum_E w_e<=H+(r+1)M
      <=[a/(r-a)+(r+1)]M.

Therefore

    M>=q(r-a)/(r+1-a)=q y/(y+q-1)=:M0.

Set lambda=q/(y+q-1), and Z=lambda X+(1-lambda)V. This is in the core and has coordinates

    Z=(lambda^m; [lambda(m-1)]^k; M0; lambda; M0^r; m+1-m lambda).

It has ceiling M0. Indeed y>m-1 and y>1 make its c,E coordinates exceed its b,U,d coordinates. Its g coordinate is also below M0, because

    M0-(m+1-m lambda)
      =(q-m-1)(y-1)/(y+q-1)>0.

Hence the lower bound is attained. Every equality case in the bound must have all c,E coordinates equal M0 and H=aL. The strict coefficient in aL-H then forces delta=0. Efficiency uniquely fixes t=lambda, p=(m-1)lambda, and g=m+1-m lambda. Thus the first-stage minimax face is the singleton {Z}.

## Exact overlap and asymptotics

Since 0<lambda<1, M0>1, and g_Z>1,

    O=sum_i min(X_i,Z_i)
      =lambda[(m+1)+k(m-1)+y]+r+1
      =lambda[(q-1)+y]+r+1
      =q+r+1.

Consequently

    rho=2-2(q+r+1)/(rq+m+1).

For fixed k and m/r->alpha>0,

    n(2-rho)->2(alpha+1)((k+1)alpha+1)/((k+1)alpha).

The optimal alpha=1/sqrt(k+1) gives

    C_k=2(1+1/sqrt(k+1))^2.

For k=1 this recovers PXC151 and C_1=3+2sqrt(2). For every k>=2 it is strictly smaller. Letting k grow produces coefficient 2.

A polynomial subsequence is k=s^2, m=2s^2, r=2s^3 for s>=2. Then

    n=2s^3+3s^2+3,
    q=2s^4+s^2+2,
    O=2s^4+2s^3+s^2+3,
    T=4s^7+2s^5+4s^3+2s^2+1,

so n(2-rho)=2nO/T ->2. Coupled with the independently established universal O>=T/(n-1), this proves c_*=2.

In fact the full sequence can be covered: for sufficiently large n choose k=floor(n^(2/3)/4), m=2k, r=n-3k-3. Then n is exact, r~n, q~2k^2, k=o(n), and n/q->0, whence n*2(q+r+1)/(rq+m+1)->2. Thus the full limit n(2-s_n)=2 exists, using the universal lower bound proved in the companion manuscript.

## Exact verification and negative control

`verify_integer_family.py` independently constructs all proper nonempty coalition inequalities from the three raw integer vectors for (m,k,r)=(2,1,3),(2,2,3),(3,2,4),(4,3,3). It excludes floors above one, other points on the optimal floor face, ceilings below the formula, and other points on the optimal ceiling face. All 16 rational Z3 queries return UNSAT; UNKNOWN is a failure. Candidate feasibility follows algebraically from generator membership and convexity.

The domain condition is substantive. At (m,k,r)=(3,3,3), which violates m>=2k-2, X=(1,1,1,2,2,2,23,1,1,1,1,1). Reducing its c coordinate to 22 and raising one E coordinate to 2 gives another core point with a lexicographically larger sorted payoff vector. The script verifies this explicit point against every coalition and requires the improvement. Thus extrapolating the formula outside its domain fails.

Finite rational checks corroborate the conventional proof and guard against implementation mistakes; they are not an all-parameter proof.
