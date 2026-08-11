# Clipped effective bipartition: exact reduction and seven-player obstruction

Date: 2026-08-11

## 1. Status

Let `x=Lmin(v)`, `z=Lmax(v)`, and normalize `T=v(N)=1`.  Write

```text
O(x,z)=sum_i min(x_i,z_i).
```

The target for `n>=6` is

```text
O(x,z)>=n/floor(n^2/4).                              (H)
```

This note proves a canonical fractional-role decomposition of every sparse
Lmax top over-cover and the exact rooted-price dual of its minimum dispersion.
It then records the failure of the stronger scalar inequality those objects
suggested.  A two-generator singleton-normalized exact seven-player game has

```text
theta_+=3/5,       a=5/3,
O=613/782 < 63/80=1/a+1/(7-a).                       (CE7)
```

Thus the clipped effective-bipartition conjecture is false.  The example is
not close to refuting `(H)`: `613/782>7/12` by `941/4692`.

The fractional roles remain a valid incidence theorem, but no argument may
use their two reciprocal masses as a universal overlap floor.  The exact
counterexample has the complete staged Lmin packet, optimal primal and dual
dispersion certificates, positive hinge surplus, and an atomic dispersion
root which is also a ceiling root.  Those premises are jointly insufficient.

## 2. Sparse ceiling data

Let `H_z={i:z_i=M}` be the top Lmax stratum.  A normalized top over-cover is

```text
sum_S lambda_S 1_S=eta 1_N+alpha,                    (OC)
sum_i alpha_i=1,
alpha_i=0                         (i notin H_z),
lambda,eta,alpha>=0,
```

where every supported coalition is `z`-tight.  Its dispersion is

```text
theta=max_i alpha_i.
```

Let `theta_+` be the minimum dispersion over all such certificates.  The
minimum is rational and attained, and a minimizing certificate can be chosen
with at most `n` supported coalitions.  These facts follow from rational LP
duality and conic Caratheodory, as recorded in
`HYBRID_OVERLAP_FACET_PROGRAM.md`.

### The dispersion dual and its rooted-price geometry

The quantity `theta_+` has an exact dual which was missing from the earlier
one-witness formulation.  Let `C_z` be the family of all proper coalitions
tight at `z`.  Then

```text
theta_+=max t                                                (DD)
```

over player prices `y in R^N` and nonnegative top prices `q in R^H_z`
satisfying

```text
y(S)>=0                         (S in C_z),
y(N)<=0,
t+y_i<=q_i                     (i in H_z),
sum_(i in H_z) q_i<=1.                                  (DP)
```

#### Proof

Attach free multipliers `y_i` to the incidence equations in `(OC)`, a free
multiplier `rho` to `sum alpha_i=1`, and nonnegative multipliers `q_i` to
`alpha_i<=theta`.  Minimization over `lambda>=0` gives `y(S)>=0` on every
`z`-tight coalition; minimization over `eta>=0` gives `y(N)<=0`.
Minimization over `alpha_i>=0` gives `y_i<=rho+q_i`, and minimization over
`theta>=0` gives `sum q_i<=1`.  Put `t=-rho`.  The dual objective is `t`,
yielding `(DD)--(DP)`.  Both programs are feasible rational LPs with finite
optimum, so strong rational LP duality gives equality.  QED.

For any optimal primal/dual pair, complementary slackness gives

```text
lambda_S>0  => y(S)=0,
eta>0       => y(N)=0,
alpha_i>0   => t+y_i=q_i,
q_i>0       => alpha_i=theta_+,
theta_+>0   => sum q_i=1.                              (DCS)
```

Thus `q` marks maximally loaded ceiling coordinates, while `y` is a signed
player price which vanishes on every supported over-cover coalition.  This
is the exact rooted-incidence normal paired with the fractional role `u`.
Importantly, `theta_+` depends only on the top block and the incidence
hypergraph of all `z`-tight proper coalitions, not on their worths.  Enlarging
that tight hypergraph can only decrease `theta_+`: it adds primal columns and,
equivalently, constraints to `(DP)`.  Hence `a` is a rational constant on
each complete labelled tight-hypergraph cell.

This observation repairs an algorithmic gap.  It is not enough to retain one
optimal over-cover and treat its cap as exogenous.  A lower-envelope
exactification may create another `z`-tight coalition and lower `theta_+`.
The dispersion dual, or an equivalent enumeration of the complete tight
hypergraph, is required to certify that the cap used in `(CEB)` is optimal.

For nonuniform `z`, put

```text
a_max=1/theta_+,
m=floor(n/2),
a=min(a_max,m).                                       (A)
```

Then `0<a<=m<n`.  If `z` is uniform, `x=z` and `(H)` is immediate, so the
nonuniform case is the only live one.

## 3. The fractional-role theorem

### Theorem (clipped fractional-role decomposition)

Choose a dispersion-minimizing certificate `(OC)` and define

```text
u=a alpha.                                             (U)
```

Then

```text
0<=u_i<=1,                 sum_i u_i=a,                (U1)
```

and the scaled incidence identity is

```text
a sum_S lambda_S 1_S+(1_N-u)=(1+a eta)1_N.            (U2)
```

Let

```text
epsilon=sum_S lambda_S[x(S)-z(S)]
       =alpha.x-M>=0.                                  (E)
```

The two fractional roles split the totals by

```text
u.x=a(M+epsilon),             u.z=aM,
(1-u).x=1-a(M+epsilon),       (1-u).z=1-aM.            (U3)
```

Thus the `u` role carries aggregate `x-z` surplus `a epsilon`, while its
complement carries exactly the opposite deficit.  The role masses sum to
`n`, even when neither role is integral.

#### Proof

Since `a<=a_max=1/theta_+`, every coordinate satisfies

```text
u_i=a alpha_i<=a theta_+<=1.
```

Nonnegativity and `sum alpha_i=1` give `(U1)`.  Multiply `(OC)` by `a` and
add `1_N-u` to both sides to obtain `(U2)`.

Every supported coalition is `z`-tight, so

```text
sum_S lambda_S z(S)-eta z(N)=M.
```

Evaluating the incidence identity at `x` and subtracting its evaluation at
`z` gives `(E)`, including nonnegativity because `x` is a core point.  Since
`alpha` is supported on the top stratum, `alpha.z=M`; hence

```text
u.z=aM,                   u.x=a alpha.x=a(M+epsilon).
```

Subtract these quantities from the common total one to get the complementary
identities in `(U3)`.  QED.

### Interpretation

The vector `u` is the correct replacement for an integral gain/loss
partition.  It assigns every player a fraction of the Lmax-side carrier role,
with `1-u_i` assigned to the complementary Lmin-side role.  The clipping in
`(A)` is legitimate: if the minimum-dispersion certificate has
`a_max>floor(n/2)`, increasing the allowed cap from `theta_+` to `1/m`
rescales the same probability `alpha` into a valid role vector of mass `m`.

This explains the three degenerate six-player equality pairs with a strict
`2|4` gain/loss split.  Their over-cover load `u` gives a virtual `3|3`
split, exactly the product needed for the sharp constant.  A theorem based
on the strict sign counts instead predicts the false lower bound `3/4`; the
actual overlap is `2/3`.

## 4. The refuted clipped effective-bipartition conjecture

> **False conjecture (CEB).**  For every singleton-normalized exact game with
> `n>=6`, the clipped mass `(A)` satisfies
>
> ```text
> O(x,z)>=1/a+1/(n-a)=n/[a(n-a)].                     (CEB)
> ```

This is dispersion-dependent and stronger than `(H)` whenever
`a<floor(n/2)`.

### Proposition (CEB implies the sharp all-n theorem)

If `(CEB)` holds, then `(H)` holds.  Together with the `G(p,k)` lower-bound
family, it determines `s(n)` exactly for every `n>=6`.

#### Proof

On `(0,n/2]`, the product `a(n-a)` is increasing.  Since
`a<=m=floor(n/2)`,

```text
a(n-a)<=m(n-m)=floor(n^2/4).
```

Therefore `(CEB)` gives

```text
O>=n/[a(n-a)]>=n/floor(n^2/4).
```

The identity `||x-z||_1=2(1-O)` gives the equivalent sharp divergence bound.
The displayed `G(p,k)` family attains it at the balanced integer split.  QED.

### The failed charge lemma

For fixed `a`, `(CEB)` is the linear payoff inequality

```text
a(n-a) O(x,z)>=n.                                    (FRC)
```

The proposed dimension-free task was:

> **Clipped fractional-role coupling lemma.**  Couple the sparse over-cover
> identity `(U2)` to the complete sign-coherent staged Lmin packet and the
> ordered Lmin/Lmax strata to prove `(FRC)`.

Large primitive staged coefficients must be charged against the fractional
capacities `u_i` and `1-u_i`, not against the number of strict gainers or an
integral player partition.  The exact example `(CE7)` proves that even this
fully labelled charge is too strong: `(FRC)` fails for the actual selections
and their actual optimal dispersion certificate.

## 5. Why the bipartition geometry is natural

Put

```text
A={i:z_i>x_i},                    d_i=z_i-x_i>0  (i in A).
```

The sign-coherent staged transport theorem gives every gaining player two
carrier packets supported on losing players:

```text
L_i subseteq {j:x_j>z_j and x_j<=x_i},
U_i subseteq {j:x_j>z_j and z_j>=z_i}.                (TU)
```

### Lemma (opposite carrier packets are disjoint)

For every `i in A`, `L_i intersect U_i` is empty.

#### Proof

If a losing player `j` belonged to both packets, then

```text
x_j<=x_i<z_i<=z_j<x_j,
```

an impossibility.  QED.

For `G(p,k)`, the two carrier roles form the complete bipartite geometry with
effective sizes `k` and `p+1`.  The normalized over-cover load makes this
precise.  With `theta_+=1/k`,

```text
u_0=1,
u_b=(k-1)/k                (b in B),
u_o=0                      (o in O).
```

Thus `sum u=k` and `sum(1-u)=p+1`: every shared gainer is split fractionally
between the two roles.  The raw gain/loss partition is not the invariant.

The lemma does not bound repeated use of a carrier across different targets.
That remaining fractional congestion problem is exactly what `(FRC)` must
solve.

## 6. Exact behavior on the two structural families

### The sharp family `G(p,k)`

Here `n=p+1+k`, `theta_+=1/k`, and

```text
O=1/k+1/(p+1)=n/[k(n-k)].                             (G1)
```

If `k<=floor(n/2)`, then `a=k` and `(CEB)` is equality.  If
`k>floor(n/2)`, clipping gives `a=floor(n/2)` and

```text
k(n-k)<=floor(n^2/4),
```

so `(G1)` is at least the clipped bound.  Equality occurs at the balanced
integer orientations, including both `(p,k)=(2,4)` and `(3,3)` for `n=7`.

### The starved/CFG family

The starved family has

```text
O_CFG=(n-2)/[2(n-3)].                                  (C1)
```

Its three-player top cap supplies an effective role of mass three.  For
`n>=6`, the clipped candidate is no stronger than

```text
1/3+1/(n-3)=n/[3(n-3)].                               (C2)
```

The exact difference is

```text
O_CFG-n/[3(n-3)]=(n-6)/[6(n-3)].                      (C3)
```

Hence this mechanism is sharp at `n=6` and has strict slack thereafter.  At
`n=5`, however,

```text
O_CFG=3/4<5/6,
```

so `(CEB)` fails.  This reproduces the actual five/six handover rather than
forcing a false uniform statement across the exceptional dimension.

## 7. Exact falsification controls and boundaries

### Exact seven-player refutation

Let

```text
g=(12/17,4/17,0,1/17,0,0,0),
h=(0,0,6/23,0,6/23,10/23,1/23),
v(S)=min(g(S),h(S)).                                  (V7)
```

Both generators have total one, lie in `Core(v)`, and one of them attains
every coalition worth.  Hence `v` is exact directly from the definition;
the disjoint supports also give `v({i})=0` for every player.  Exact staged
incidence certificates give

```text
x=(227/782,48/391,48/391,1/34,48/391,13/46,1/34),
z=(91,12,90,12,90,91,5)/391.                         (XZ7)
```

The solver-free selection proof has the dependency map

```text
v=min(g,h)
  -> x-tight support {37,49,55,85}
  -> Lmin blocks (3,6)|(1,2,4)|(5)|(0)
  -> z-tight support {37,42,49,66,72,97,103,109,115,121}
  -> Lmax blocks (0,5)|(2,4)|(1,3)|(6)
  -> fourteen sign-correct staged incidence identities
  -> x=Lmin(v), z=Lmax(v).                            (SEL7)
```

For example, the first Lmin relation is

```text
1_55+e_3+e_6=1_N,
```

with either player forced, while the first Lmax relation for player `0` is

```text
1_37+(1/2)1_42+1_49+(1/2)1_66+(1/2)1_72
  -e_0-(3/2)e_5=1_N.
```

Every supported coalition is tight at the asserted point.  Dotting these
relations with a core displacement proves the appropriate stage pinning; the
remaining twelve identities are recorded literally in the verifier and are
also replayed by a separately formulated exact feasibility LP.

The minimum-dispersion primal certificate has

```text
eta=2/5,  alpha=(2/5,0,0,0,0,3/5,0),
lambda_37=2/5, lambda_42=1/5, lambda_49=2/5,
lambda_66=1/5, lambda_72=1/5.                        (P7)
```

The dual certificate `(DD)` is

```text
t=3/5,
y=(-3,-1,1,-1,1,2,1)/5,
q=e_5.                                                (D7)
```

The two witnesses prove `theta_+=3/5` exactly.  Therefore `a=5/3`, but

```text
O(x,z)=613/782,
1/a+1/(7-a)=63/80,
O-63/80=-113/31280.                                  (R7)
```

This refutes `(CEB)`.  The counterexample is unusually decisive about the
premise: the dual price is atomic at player `5`, and player `5` is also a
ceiling root because `x_5>z_5=max z`.  Root coalescence does not repair the
false inequality.  Its positive hinge surplus is `9/170`; the already proved
sharpened spectral bound is `234/391>7/12`, so the main target survives by a
different mechanism.

Reproduce exactness, all fourteen solver-free staged identities, fourteen
independently formulated exact staged LP checks, both dispersion witnesses,
and the strict rational comparison with

```bash
python3 verifiers/divergence/verify_n7_effective_bipartition_counterexample.py \
  --output verifiers/divergence/n7_effective_bipartition_counterexample.json
```

### Earlier finite controls

The exact audit

```bash
python3 verifiers/divergence/audit_effective_bipartition.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --n5-dir verifiers/s5close \
  --output verifiers/divergence/effective_bipartition_audit.json
```

reports:

1. `374/374` archived six-player pairs satisfy clipped `(CEB)`, with minimum
   margin zero.
2. The **unclipped** statement is false on exactly two archived pairs,
   `602[119]` and `602[158]`: `a_max=4`, predicted overlap `3/4`, actual
   overlap `7/10`.  Clipping to `a=3` repairs both.
3. Among `124` distinct archived five-player pairs, `12` violate `(CEB)`;
   the worst margin is `-1/12`, attained by overlap `3/4` against `5/6`.
4. Five hostile fixed branches, the coefficient-seven eight-player branch,
   both sharp seven-player orientations, and the nonuniform-generator
   seven-player control all pass.  The two sharp orientations attain equality.

These were finite controls, not proof evidence for the unenumerated domain;
`(V7)--(R7)` is the exact out-of-bank counterexample they did not detect.

The independent primal/dual audit

```bash
python3 verifiers/divergence/audit_overcover_dispersion_dual.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/overcover_dispersion_dual_audit.json
```

checks `(DD)--(DCS)` on all `374` nonuniform archived six-player records.
It finds `373` distinct `(v,z)` pairs, no strong-duality or complementarity
failure, and primal coalition support at most four in this bank.  Every
record happens to admit an optimal dual with an atomic price `q=e_r`, but in
three records no such atomic price root is a ceiling root with `x_r>=M`.
The optimized seven-player spectral obstruction has the same separation.
Thus the tempting identification of the dispersion root with the
maximum-overlap root is false; a general proof must transport charge between
those two labelled roles or earn strict slack when they differ.  The archive
counts and the atomic-root observation are finite discovery evidence only.

### Boundary with the one-witness reduction

The candidate is stronger than the common-hinge universal floor.  In
`harvest6_601.json`, record `13` has

```text
theta_+=1/2,      a=2,
O=13/17>3/4.                                           (B1)
```

Both maximum-overlap-root common-hinge relaxations have exact minimum `2/3`,
so they do not prove the record-specific `3/4` candidate.  With the complete
labelled supports and all singleton witnesses, the full branch minimum is
again `2/3`; its lower-envelope exactified minimizer recomputes

```text
theta_+=1/3,      a=3,
O=2/3=1/3+1/3.                                         (B2)
```

Thus this particular exactification does not refute `(CEB)`: it moves the
dispersion toward the balanced role mass as overlap falls.  It remains a
valid warning about treating the cap as fixed, but the independent game
`(V7)` now refutes `(CEB)` outright without such movement.

## 8. Exact-cone and algorithmic interface

For a fixed ordered selection branch and a fixed complete Lmax tight
hypergraph, `(DD)` makes `theta_+` and `a` rational constants.  After choosing
one optimal sparse primal over-cover, `u` is rational as well.  The target
`(FRC)` is then a linear inequality in the labelled generator coordinates.
Its validity is decided by the same exact rational branch LP and
affine-Farkas circuit machinery as the common-hinge program.

This gives a finite exact diagnostic algorithm at fixed `n` for deciding the
now-refuted inequality on every labelled branch:

1. enumerate the Lmax top block and complete tight-coalition hypergraph;
2. solve the primal/dual incidence pair `(OC)` and `(DD)` and compute
   `a=min(1/theta_+,floor(n/2))`;
3. reduce one optimal primal over-cover to sparse support and enumerate
   complete rooted staged Lmin circuit selections and ordered
   Lmax strata;
4. test `(FRC)` on every feasible lower-envelope branch;
5. extract either an exact rational counterexample or a target-containing
   positive circuit;
6. project any coalition coefficient system and apply the
   Studeny--Kratochvil indecomposable semi-balanced test before calling it a
   facet of the full exact-game cone.

The seven-player witness shows that this algorithm can return a substantive
target-containing separating model, not merely an infeasible or boundary
branch.  It is not an algorithm for proving `(H)`.

The relative circuit/facet support bounds already proved in
`HYBRID_OVERLAP_FACET_PROGRAM.md` apply after the over-cover ray is fixed.
The fractional role identity `(U2)` adds a distinguished capped incidence
ray; it does not make every relative proof a full exact-cone facet.

## 9. Evidence ledger and next attack

### Human theorems

- clipped fractional-role decomposition `(U1)--(U3)`;
- disjointness of the two ordered carrier packets;
- `(CEB) => (H)`;
- exact specialization to `G(p,k)` and the starved/CFG handover formulas;
- the dispersion dual `(DD)--(DCS)` and its tight-hypergraph monotonicity;
- the threshold label-currency and carrier-interval theorems in
  `HYBRID_OVERLAP_FACET_PROGRAM.md`;
- the normalized coefficient-supply collapse and complete strict carrier
  support theorem;
- the canonical rank-pairing theorem recovering all label currency from
  clipped high--low rectangles;
- the exact rooted-hinge witness-projection theorem and its `n-1` support
  bound for two-colour fractional hinge packings;
- the singleton-slack completion theorem: each rooted packing vertex lifts
  to a min-semi-balanced system, purely so with exceptional singleton root
  exactly when its root advantage is positive; the published
  indecomposability test is then the exact full-cone facet filter;
- the positive-root nonfacet theorem: `(RDB)` forces a nonroot deficit, and
  its singleton together with the exceptional root singleton gives an
  explicit two-singleton decomposition, so no canonical rooted completion
  can be an exact-cone facet at `x_r>0`;
- the pair-floor rooted projection: retaining only
  `w_i>=v({r,i})` from the singleton witness's core constraints sharpens
  root-deficit balance by `sum_i q_i v({r,i})`; this term is exactly the
  exceptional-set transport premium lost by the decomposable lift;
- the rooted pair-lift theorem: the column shear
  `e_i -> 1_{r,i}=e_r+e_i` turns an extreme packing into a
  min-semi-balanced system of support at most `n`, whose exact-game
  inequality is precisely the pair-floor budget and which is a full-cone
  facet exactly when it passes the published indecomposability test;
- the dimension-free sharp-family classification: the simultaneous
  `k`-hinge pair lift is indecomposable for every `p>=1,k>=2`, is active at
  both selections of `G(p,k)`, and supplies a uniform exact-cone facet
  explanation of equality;
- the over-cover/pair-lift coupling theorem: a common sparse Lmax over-cover
  with deleted-root load ceiling `theta_-` normalizes directly to a rooted
  packing with `delta=(alpha_r-theta_-)/(eta+theta_-)` and
  `q_i=(theta_--alpha_i)/(eta+theta_-)`, yielding explicit two-selection
  exact-cone facet charge;
- the rooted-pair gauge quotient: packing weight on `{r,i}` can be transferred
  to its deficit coefficient without changing the merged pair-lift system,
  so rooted-pair columns should be deleted before vertex/facet enumeration;
- the common-support deficiency dual: the minimum over-cover hinge surplus
  equals an explicit player-price maximum and vanishes exactly when a common
  normalized top over-cover exists;
- the noncommon surplus-defect theorem: the Lmax-side scaled pair-lift slack
  is `kappa_r`, the Lmin-side slack is exactly `kappa_r-epsilon`, and common
  tangent balance acquires the exact defect `-epsilon`;
- the best-single-anchor perspective LP, which optimizes
  `(M+epsilon-mu)/theta` jointly over all sparse top over-covers.

### Exact rational evidence

- the archived `n=6`, `n=5`, hostile `n=7/n=8`, and full-branch boundary
  checks in `effective_bipartition_audit.json`;
- the exact seven-player refutation `(V7)--(R7)`, including two formulations
  of the selection certificates and primal/dual dispersion witnesses;
- independent direct-witness and projected cutting-plane agreement on all
  maximum-overlap roots of six hostile and two sharp fixed branches;
- exact-LP and independently formulated Z3 agreement that all eight
  nontrivial rooted cuts in those controls are min-semi-balanced but
  decomposable, including both sharp block-star cuts;
- exact pair-floor root-deficit replay on all eight cuts: seven equalities,
  with only `9/9523` slack in the neutral-endpoint control;
- exact-LP and independent Z3 agreement that six of the eight rooted pair
  lifts are indecomposable exact-cone facets, including both sharp
  seven-player orientations; the other two have `3` and `20`
  decompositions;
- the exact root-specific over-cover audit separates deleted-load
  minimization from common-leader maximization: the coefficient-two root
  `3` has a strict common leader of gap `1/3` despite a tied
  minimum-deleted-load solution; the primitive and both sharp cases also
  have strict common leaders, the neutral control is necessarily tied, and
  three hostile branches admit no normalized common top over-cover.  An
  independently formulated Z3 exact-LRA replay agrees on all eleven optima
  or infeasibilities.  After the gauge quotient, the coefficient-two strict
  certificate is the half-sum of two distinct active indecomposable facets;
  exact-LP and Z3 both return zero decompositions for both supports;
- on all 374 archived six-player records, the returned minimum-dispersion
  certificate is also minimum-surplus, 73 minimum deficiencies are positive,
  and at least one top root absorbs the surplus.  Exact-LP and independently
  formulated Z3 agree on all named-control deficiency and best-anchor
  optima;
- a null-padded exact five-player control gives an exact six-player negative
  control to unrestricted surplus absorption: `epsilon_*=3/112` but both top
  pair lifts have `kappa_r=0`.  Its overlap `25/28` is safely above `2/3`.

### Refuted

- `(CEB)` and its equivalent charge form `(FRC)`;
- the price-completed fractional-role lemma proposed in the previous version;
- identification of an atomic dispersion root with a ceiling root as a
  sufficient repair—the counterexample has the same root;
- the complete carrier-packing route as an independent bridge: after neutral
  endpoints are restored, it is identically equal to label currency;
- an unrestricted surplus-absorbing top-root theorem, by the null-padded
  negative control;
- every single scalar spectral-anchor proof, even after jointly optimizing
  surplus and dispersion: three noncommon hostile controls retain exact
  shortfalls `25/36`, `3/2`, and `1`.

### Still open

- the weaker universal target `(H)`;
- a dimension-free construction of its Farkas charge from the complete
  staged Lmin packet and sparse ceiling data;
- a dimension-free selection/gluing theorem guaranteeing that sparse Lmax
  common hinges expose enough rooted pair-lift facet charge to prove the
  hybrid target; the facet class and its quantitative currency
  `v({r,i})` are now explicit.  The theorem must distinguish strict-common,
  tied-common, and noncommon-support branches; optimizing deleted load alone
  cannot do so.  In the noncommon positive-floor branch it must either prove
  surplus absorption for a suitable root or distribute the unabsorbed
  deficiency across multiple staged/facet rows; one scalar anchor is now
  proved insufficient.

The next live bridge is a **spectral-or-balanced disjunction**.  Positive
hinge surplus already converts to a rigorous sharpened spectral lower bound;
it closes `(V7)` at `234/391>7/12` and every positive-floor six-player
archive record.  The three named seven-player spectral obstructions, however,
are closed by their labelled common-hinge branches instead.  A dimension-free
proof must show that failure of the sharpened spectral target forces enough
zero-surplus/common-hinge structure for the rooted staged packet to prove
`(H)`.  Unlike `(CEB)`, this asks only for the balanced universal constant and
explicitly allows the two existing mechanisms to substitute for one another.

In the threshold formulation, put `a_i=min(x_i,z_i)` and
`b_i=max(x_i,z_i)`.  Every pair with `b_j<a_i` gives the high--low rectangle
`(b_j,a_i]`; it is staged-available because `x_j<x_i`.  Sorting the residual
`a`-values downward and `b`-values upward and pairing equal ranks produces
weight-one rectangles whose occupancy at every threshold is exactly the
smaller of the high--high and low--low populations.  Hence their total length
is all label currency.  Neutral endpoints are essential in general and were
missing from the earlier opposite-sign formulation.

For fixed payoff strata and fixed carrier supports this is now an exact
algorithmic theorem.  The carrier-by-threshold matrix has consecutive-one
columns and is totally unimodular.  The maximum weighted interval packing
equals a minimum threshold cover, has an integral sparse optimum for integer
capacities, and is exactly solvable in polynomial time for rational data.
The dual cover is the sharp Hall-type obstruction for a restricted packet.
Normalized auxiliary coefficients are now proved to be either
unavailable or unbounded: the duplicate forced-player column permits
amplification while preserving normalization.  Consequently their magnitudes
carry no congestion information.  Adding earlier player relations proves
that every strict order-compatible carrier is available.  The canonical
rank pairing then proves that the complete interval optimum equals label
currency identically.  Thus asking it to pay the residual deficit is exactly
the original hybrid-overlap inequality, not a stronger bridge.  The live
input must instead couple sparse Lmax over-cover weights to common tight
coalitions in the staged Lmin packet.

The minimum-cover dual also has a rooted potential form.  After subtracting
the physical threshold coordinate from cumulative cover prices, carrier
constraints say that the potential cannot fall along carrier arcs.  Extreme
covers are certified by tight rooted spanning trees made from carrier arcs
and adjacent-threshold path arcs.  These threshold trees are the candidate
interface to rooted semi-balanced systems for restricted families.  For the
complete family the physical layer-width cover and canonical rank pairing
are matching tautological optima.  There is no residual coefficient, support,
or threshold-tree pattern to encode as the missing facet.  Any facet advance
must come from the common-hinge coalition lift, followed by gluing and the
published indecomposability test.
