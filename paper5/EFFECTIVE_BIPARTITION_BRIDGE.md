# Clipped effective bipartition and the all-dimension overlap bridge

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
Lmax top over-cover and isolates a stronger scalar inequality which would
imply `(H)`.  The stronger inequality is exact on both balanced orientations
of `G(p,k)`, explains the six-player handover from the starved/CFG family,
fails at the five-player extremum, and survives the exact controls described
below.  It is **not proved for all exact games**.

The point of the new formulation is not another label-free relaxation.  The
fractional roles are extracted from the actual sparse Lmax incidence
certificate; the still-missing step must couple them to the complete staged
Lmin packet.

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

## 4. The clipped effective-bipartition conjecture

> **Conjecture (CEB).**  For every singleton-normalized exact game with
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

### Equivalent missing charge lemma

For fixed `a`, `(CEB)` is the linear payoff inequality

```text
a(n-a) O(x,z)>=n.                                    (FRC)
```

The dimension-free task is therefore:

> **Clipped fractional-role coupling lemma.**  Couple the sparse over-cover
> identity `(U2)` to the complete sign-coherent staged Lmin packet and the
> ordered Lmin/Lmax strata to prove `(FRC)`.

Large primitive staged coefficients must be charged against the fractional
capacities `u_i` and `1-u_i`, not against the number of strict gainers or an
integral player partition.

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

These are finite controls, not proof evidence for the unenumerated domain.

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

Thus exactification does not refute `(CEB)`: it moves the dispersion toward
the balanced role mass as overlap falls.  A proof of `(CEB)` must control this
joint movement of `O` and `theta_+`; a fixed one-witness lower bound cannot.

## 8. Exact-cone and algorithmic interface

For a fixed ordered selection branch and a fixed complete Lmax tight
hypergraph, `(DD)` makes `theta_+` and `a` rational constants.  After choosing
one optimal sparse primal over-cover, `u` is rational as well.  The target
`(FRC)` is then a linear inequality in the labelled generator coordinates.
Its validity is decided by the same exact rational branch LP and
affine-Farkas circuit machinery as the common-hinge program.

This gives a finite exact algorithm at fixed `n`:

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

The relative circuit/facet support bounds already proved in
`HYBRID_OVERLAP_FACET_PROGRAM.md` apply after the over-cover ray is fixed.
The fractional role identity `(U2)` adds a distinguished capped incidence
ray; it does not make every relative proof a full exact-cone facet.

## 9. Evidence ledger and next attack

### Human theorems

- clipped fractional-role decomposition `(U1)--(U3)`;
- disjointness of the two ordered carrier packets;
- `(CEB) => (H)`;
- exact specialization to `G(p,k)` and the starved/CFG handover formulas.

### Exact rational evidence

- the archived `n=6`, `n=5`, hostile `n=7/n=8`, and full-branch boundary
  checks in `effective_bipartition_audit.json`.

### Still conjectural

- `(CEB)` and its equivalent charge form `(FRC)` for every exact game with
  `n>=6`;
- a dimension-free construction of the required Farkas charge from the
  complete staged Lmin packet;
- a classification of which projected common-hinge circuits pass to
  indecomposable exact-cone facets.

The highest-value next step is a **price-completed fractional-role coupling
lemma**: express each sign-coherent staged Lmin transport as flow between the
capacities `u` and `1-u`, while using the optimal dispersion prices `(y,q)`
to charge any repeated carrier use and any movement of the ceiling tight
hypergraph.  The resulting global price must be at most `a(n-a)-n`.  The
three atomic/ceiling-root mismatches show that the proof must permit two
distinct labelled roots; equality should force them to coalesce, as they do
in both balanced orientations of `G(p,k)`.

A failed version must be exactified immediately and `theta_+` recomputed.
Boundary `(B2)` proves that a fixed-cap one-witness lemma omitting `(DD)` is
strictly too strong: its relaxed minimizer lowers the overlap only by creating
a tighter dispersion certificate and moving from `a=2` to `a=3`.
