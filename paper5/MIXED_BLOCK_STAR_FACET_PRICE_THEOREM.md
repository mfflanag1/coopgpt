# Reviewer packet: mixed block-star and rooted-facet price theorems

Date: 2026-08-11

Status: proved human branch theorems with exact rational controls.  These
results do **not** prove the universal hybrid-overlap conjecture, and no claim
of external validation or literature novelty is made.

## 1. Target and notation

For singleton-normalized exact games put

```text
x=Lmin(v),       z=Lmax(v),       T=v(N),
O(x,z)=sum_i min(x_i,z_i),
c_n=n/floor(n^2/4).
```

The open target is `O>=c_n T` for every `n>=6`.  The results below prove it
for a dimension-free mixed packet class and give a coefficient criterion for
a larger rooted-facet class.

## 2. One-common-hinge mixed block-star theorem

Let

```text
N={r} disjoint-union O disjoint-union B,
|O|=p>=1,       |B|=k>=2,       n=p+k+1.
```

Choose `b_0 in B`, `j in B\{b_0}`, and put
`C_b={r} union (B\{b})`.  Let nonnegative `x,z,w` have common total `T`,
with `w_r=0`, and suppose

```text
x_r=c,
x_b=b                  (b in B\{b_0}),
x_i=a                  (i in O union {b_0}),
0<=a<=b<=c,

z_r=z_b=A              (b in B\{b_0}),
z_(b_0)=B_0,           z(O)=L.
```

Fix the hybrid sign branch in which `B` uses `x` and `{r} union O` uses `z`.
Assume only

```text
x(C_b)<=w(C_b)          (b in B),
z(C_j)<=x(C_j).                                  (1)
```

Then

```text
O(x,z)>=nT/[k(p+1)]>=c_n T.                       (2)
```

### Proof

Summing the `k` witness rows in (1) gives

```text
k c+(k-1)[(k-1)b+a]<=(k-1)w(B)<=(k-1)T.
```

Subtract `(k-1)` times

```text
T=c+(k-1)b+(p+1)a
```

to obtain

```text
c<=p(k-1)a.                                        (3)
```

Put `P=p(k-1)` and `D=k(p+1)`.  Direct expansion gives

```text
(P-1)T-D(c-b)
 =[kP+p+1](b-a)+n(Pa-c)>=0.                        (4)
```

Thus `c-b<=(P-1)T/D`.  Also

```text
T=kA+B_0+L,
(k-1)A+B_0=z(C_j)<=x(C_j)=c+(k-2)b+a.
```

Therefore the fixed-cut objective satisfies

```text
O=A+L+(k-1)b+a
 =T-[(k-1)A+B_0-(k-1)b-a]
 >=T-(c-b)
 >=[D-P+1]T/D=nT/D.
```

Finally `k+(p+1)=n`, hence `D<=floor(n^2/4)`.  QED.

Equality at the universal constant requires the balanced product, equality
in (1), and

```text
b=a,       c=p(k-1)a,       a=T/[k(p+1)].           (5)
```

The premises alone need not make all remaining Lmax levels unique.

## 3. Rooted-facet price theorem

The preceding proof uses the star only to establish (3).  Consider instead a
branch with one root at `c`, `g` players at `b`, and `m` players at `a`, so
`n=1+g+m`.  Suppose a rooted pair lift has root excess `delta>0`, total
deficit weight `Q`, and every deficit lies on an `a`-level loss player.
The pair-floor rooted inequality is

```text
delta c+sum_i q_i v({r,i})<=sum_i q_i x_i=Q a.
```

Since pair values are nonnegative,

```text
c<=P a,             P:=Q/delta.                     (6)
```

If a mixed cross row gives `O>=T-(c-b)`, put `D_P=P+n-1`.  Then

```text
(P-1)T-D_P(c-b)
 =[g(P-1)+D_P](b-a)+n(Pa-c)>=0,                     (7)
```

and hence

```text
O/T>=n/(P+n-1).                                      (8)
```

The universal target follows whenever

```text
P<=floor(n^2/4)-n+1.                                 (9)
```

Thus `P=Q/delta` is the effective facet price: total lower-loss deficit
weight per unit of exceptional-root excess.

### Reserve version

Let the root, `g` middle players, and `m` low players form a subset `U` of
size `n_0=1+g+m`.  Allow all players outside `U` to be nongainers.  If the
full gain set consists of the `g` middle players and one low player, and a
mixed row proves

```text
z(G)-x(G)<=c-b,
```

then (7) applies to `T_U=x(U)<=T`, while
`O=T-[z(G)-x(G)]`.  Consequently

```text
O/T>=n_0/(P+n_0-1).                                  (10)
```

If `T_U=0`, the cross row gives `O=T` directly.  Otherwise the payoff order
and `c<=Pa` force `P>=1`, as required when passing from (7) to (10).

This reaches the `n`-player target when

```text
P<=n_0 floor(n^2/4)/n-n_0+1.                         (11)
```

### Exact multistage penalty

If rooted deficits do not all lie on the `a` floor, define

```text
e_q=max(0,[sum_i q_i(x_i-a)-sum_i q_i v({r,i})]/delta).
```

The rooted pair inequality gives `c<=Pa+e_q`.  Adding `n e_q` to the
left side of (7) therefore gives

```text
O/T>=n/(P+n-1)-n e_q/[(P+n-1)T].                    (12)
```

For a reserve subset, the bound is

```text
O/T>=n_0(T-e_q)/[(P+n_0-1)T].                       (13)
```

In the full structured dimension, the universal target follows whenever

```text
e_q/T<=1-(P+n-1)/floor(n^2/4).                       (14)
```

Equations (12)--(14) are the quantitative interface for the four tested cuts
whose deficits do not all lie on the first Lmin floor.  A multistage theorem
must pay this exact penalty from label, spectral, or reserve currency.

## 4. Exact-cone interpretation

The witness projection of the block-star packet has rooted packing excess
`delta=1/(k-1)` and outside deficit weights one, so

```text
Q=p,             P=Q/delta=p(k-1).
```

Replacing each outside singleton deficit by the rooted pair column is the
pair-spoke shear

```text
sum_(b in B) 1_{C_b}
 +(k-1)sum_(o in O)1_{r,o}
 -[p(k-1)+1]e_r=(k-1)1_N.
```

The existing inverse-matrix theorem proves this system indecomposable for
all `p>=1,k>=2`.  The identification with a facet of the exact-game cone uses
the published Studeny--Kratochvil indecomposable semi-balanced criterion.
The new statement here is the labelled overlap conversion: only one star
hinge must also be Lmax-tight.  The other `k-1` hinges remain Lmin-only.

This does not assert that every mixed labelled Farkas circuit is a full-cone
facet.  Only its projected coalition system, after the pair shear and the
published indecomposability test, receives that name.

## 5. New exact seven-player boundary control

The lower envelope of

```text
g=(2,4,0,16,2,0,0),
h=(0,8,5,0,0,8,3),
k=(1,0,7,8,0,3,5)
```

is singleton-normalized and exact.  All generators have total `24`.  Exact
staged identities give

```text
x=(2,4,4,6,2,4,2),
z=(7/4,9/2,9/2,9/2,7/4,9/2,5/2).
```

Its actual overlap is `22=11T/12`, and player `3` is the unique
maximum-overlap root.  Nevertheless the one-witness relaxation at player
`3`, retaining **every** proper coalition tight at either displayed
selection, has optimum exactly `7/12`.  Its primal minimizer is

```text
x*=(1/12,1/12,1/12,1/2,1/12,1/12,1/12),
z*=(1/32,3/16,3/16,3/16,1/32,3/16,3/16),
w*=(0,1/4,1/4,0,0,1/4,1/4).
```

This is precisely the normalized `G(2,4)` sharp triple.  The verifier checks
fourteen explicit staged identities for the actual selections and a
hard-coded primal/dual identity for the relaxation optimum.  No optimization
call is used for the latter certificate.

## 6. Multistage direct-gluing master theorem

There is a second dimension-free closure mechanism that uses no exactness
witness.  Partition

```text
N=P disjoint-union G disjoint-union H,
|P|=p, |G|=g, |H|=h,
m=p+g, q=g+h, n=p+g+h,
```

where `p,g,h>=1`.  Let `P,H` be nongainers and `G` the gainers:

```text
z_i<=x_i on P union H,       x_i<=z_i on G.
```

Put

```text
l=z(P)/p,                     b=z(G union H)/q,
B=g/(m-s).
```

Let `J` be a subset of `G`, put `s=|J|<g`, and suppose the direct selection
comparison

```text
x(H union J)<=z(H union J)                              (15)
```

is valid.  For example, (15) is automatic when `H union J` is Lmin-tight,
because `z` lies in the core.  Define the two exact order/dispersion residuals

```text
R_x=x(J)+(1-B)x(G\J)-B x(P),
R_z=(1-B)[z(H)-hb]-B[z(J)-sb].                       (16)
```

Then, with no two-stratum assumption on either selection, the master identity
is

```text
O-[1-gp/{q(m-s)}]T
 =[gpn/{q(m-s)}]l
  +B[z(H union J)-x(H union J)]+R_x+R_z.             (17)
```

Consequently, if `R_x>=0` and `R_z>=0`, then

```text
O/T>=1-gp/[(g+h)(p+g-s)].                             (18)
```

This reaches the universal `n`-player target exactly when

```text
floor(n^2/4)gp
 <=[floor(n^2/4)-n](g+h)(p+g-s).                     (19)
```

### Proof

The sign branch gives

```text
T=z(P)+z(G)+z(H)=x(P)+x(G)+x(H),
O=z(P)+x(G)+z(H)=T-z(G)+x(G).
```

Expand the comparison term and use `x(H)=T-x(P)-x(G)`.  Direct cancellation
gives

```text
B[z(H union J)-x(H union J)]+R_x+R_z
 =x(G)+z(H)-BT-(1-B)hb+Bsb.
```

Now substitute `b=(T-pl)/q`, `B=g/(m-s)`, and `q=g+h`.
The coefficient of `l` after adding the first term in (17) becomes `p`, and
the coefficient of `T` becomes `-[1-gp/{q(m-s)}]`.  The result is
`pl+x(G)+z(H)-[1-gp/{q(m-s)}]T`, exactly the left side of (17).

The low term is nonnegative because singleton normalization and core
membership give `z>=0`; the comparison term is nonnegative by (15).  Thus
nonnegative residuals prove (18), and clearing positive denominators gives
(19).  Equality in (18) requires `l=0`, a tight comparison, `R_x=0`, and
`R_z=0`.  QED.

### Cross-ordered sufficient condition

The residual hypotheses have a simple purely ordinal sufficient condition.
Suppose

```text
s<=p,
max x(P)<=min x(G),
max z(G)<=min z(H),
J consists of s lowest-z players of G.               (20)
```

Since `s<=p`, `0<B<=1`.  Every payoff in `G` is at least the average payoff
on `P`, so

```text
R_x >=[s+(1-B)(g-s)-Bp] average(x(P))=0.
```

The Lmax order implies `average(z(H))>=b>=average(z(G))`, while the choice of
`J` gives `average(z(J))<=average(z(G))`.  Hence both brackets in `R_z` have
the required signs and `R_z>=0`.  Thus (20) implies the master bound without
assuming that Lmax has only two levels.

When `x=a` on `P union G`, `x=c` on `H`, `z=l` on `P`, and `z=b` on
`G union H`, both residuals vanish identically.  Thus the two-stratum
specialization is

```text
O-[1-gp/{q(m-s)}]T
 =[gpn/{q(m-s)}]l
  +[g/(m-s)][z(H union J)-x(H union J)].             (21)
```

This theorem supplies the direct-labelled arm of the surviving disjunction.
It does not assert that every staged Lmin packet contains a coalition of the
required form.  When it does, however, no rooted witness, full-cone facet, or
rearrangement of unprotected labels is needed.

A fresh exact seven-player control has

```text
(3,0,0,6,1,2,0),
(1,0,2,0,0,3,6),
(0,5,0,1,5,0,1),
(p,g,h,s)=(3,2,2,1),
x=(3/2,3/2,3/2,9/4,3/2,3/2,9/4),
z=(4/3,2,4/3,2,2,4/3,2),
```

and coalition `74={1,3,6}=H union J` is tight at both selections.  Formula
(21) specializes to

```text
O-(5/8)T=(21/8)z_0+(1/2)[z(74)-x(74)].               (22)
```

The lower-envelope game has three generators, actual overlap `11T/12`, and
all seven one-witness branch relaxations have minimum `5/8`.  The hand bound
is above the seven-player target `7/12`; the rooted LP values are a hostile
control, not a premise of the theorem.

The arbitrary-Lmax master also recovers the two archived direct hostile
certificates.  For the actual-top-fixed branch it gives `7/10`, with
`R_x=15/4` and `R_z=111/20`.  For the top-and-bottom-fixed branch it gives
`2/3`, with `R_x=1` and `R_z=11`; here `s=3>p=1`, showing why the exact
residual criterion is strictly stronger than sufficient condition (20).

## 7. Hand payment certificate for the hardest spectral branch

The optimized label-free seven-player obstruction is the tested cut with a
deficit on a gaining/later-stratum player.  Its root-`3` branch nevertheless
has the following direct hand certificate, after normalizing `T=1` and
writing `w=w^3`:

```text
O-3/4
 =z_2+(1/2)w_2+(1/4)w_5+(1/4)w_6
 +(1/4)[w(26)-x(26)]+(1/4)[w(57)-x(57)]
 +(5/4)[x(52)-z(52)]+(1/2)[x(57)-z(57)]
 +(1/4)[w(75)-z(75)]
 +(3/4)(x_0-x_4)+(1/2)(z_4-z_5)+(z_5-z_1).          (23)
```

Every term is nonnegative by a displayed core/witness comparison,
nonnegativity, or branch order.  At the actual control every coalition
bracket is zero.  Its strict margin `119/1080` consists only of `z_2` and
three payoff-stratum gaps.  This proves by hand that the mixed packet fixes a
baseline above the universal target while ordered label currency pays the
multistage defect.

The adjacent verifier checks (23) as a coefficient identity and verifies a
matching feasible primal at `3/4`; it makes no optimization call.

## 8. Evidence and limitations

Human proof evidence:

- equations (3)--(4), proving the mixed block-star theorem in every
  dimension;
- equations (6)--(8), proving the general rooted-facet price criterion;
- the reserve argument (10);
- the multistage direct-gluing identity (17), valid in every dimension.

Exact audit evidence:

- 56 `(p,k)` parameter rows for the block-star identity;
- 684 rational rows for the general facet-price identity;
- exact lower-envelope, core, staged-selection, primal, dual, and root checks
  for the displayed seven-player control;
- 1,080 exact two-stratum arithmetic rows, 680 nonuniform multistage order
  rows, and exact arbitrary-Lmax replays of both archived direct hostile
  branches for (17), plus fourteen exact staged selection certificates for
  its fresh seven-player control;
- all nine extreme mixed-witness projection cuts have price within their
  dimensional threshold; eight have only nongaining deficits, but only five
  put every deficit on the first Lmin floor.

The nine-cut statement is a finite coefficient audit, not a theorem.  Together
with (17), it isolates the remaining obstacle as a direct-or-rooted selection
lemma: either some Lmin-tight comparison reaches the target with
`R_x,R_z>=0`, or failure of all such comparisons must produce an affordable
mixed-colour rooted packet.  Neither alternative has been proved universally.

The numerical search that exposed the control was used only for discovery
and is not part of the evidence chain.

## 9. Reproduction and review paths

Run from the repository root:

```bash
python3 verifiers/divergence/verify_mixed_block_star_boundary.py \
  --output verifiers/divergence/mixed_block_star_boundary.json

python3 verifiers/divergence/verify_optimized_mixed_currency_certificate.py \
  --output verifiers/divergence/optimized_mixed_currency_certificate.json

python3 verifiers/divergence/verify_two_stratum_direct_gluing.py \
  --output verifiers/divergence/two_stratum_direct_gluing.json

python3 verifiers/divergence/verify_rooted_star_matrix_facets.py \
  --input verifiers/divergence/mixed_witness_projection.json \
  --output /tmp/rooted-star-recheck.json
cmp verifiers/divergence/rooted_star_matrix_facets.json \
  /tmp/rooted-star-recheck.json
```

Primary files:

- `paper5/MIXED_BLOCK_STAR_FACET_PRICE_THEOREM.md` — this packet;
- `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md` — full dependency context;
- `paper5/divergence.tex` and `paper5/divergence.pdf` — manuscript;
- `verifiers/divergence/verify_mixed_block_star_boundary.py` — exact audit;
- `verifiers/divergence/mixed_block_star_boundary.json` — saved output;
- `verifiers/divergence/verify_optimized_mixed_currency_certificate.py` —
  solver-free hand-certificate audit;
- `verifiers/divergence/verify_two_stratum_direct_gluing.py` — exact audit of
  the dimension-free direct-gluing identity and its seven-player control;
- `verifiers/divergence/verify_rooted_star_matrix_facets.py` — existing
  indecomposability audit.

Questions for hostile review:

1. Are the quantifiers and sign-branch assumptions in Section 2 sufficient
   and no stronger than the proof uses?
2. Does identity (7) correctly convert the rooted pair-lift coefficient ratio
   into the overlap bound for rational, nonintegral `P`?
3. Is the reserve argument valid when unstructured nongainers occupy
   arbitrary later Lmin strata?
4. Does the pair-spoke shear justify the stated exact-cone interface without
   conflating the labelled mixed circuit with a full-cone facet?
5. Is an equivalent effective-facet-price or one-common-hinge theorem already
   present in the cooperative-game/exact-cone literature?
6. Can the four non-floor-aligned extreme cuts be handled by a known
   multistage transport or semi-balanced decomposition theorem?
7. Is the multistage identity (17) already known as a labelled tight-set
   gluing lemma, and can its coalition-existence premise be forced from a
   complete staged Lmin packet?
