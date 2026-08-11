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

Consequently, the weaker condition `R_x+R_z>=0` already implies

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
nonnegative residual sum proves (18), and clearing positive denominators gives
(19).  Equality in (18) requires `l=0`, a tight comparison, and
`R_x+R_z=0`.  QED.

### Gain-packet interval reduction

The residual criterion has a one-dimensional form.  Put

```text
delta_i=z_i-x_i>=0 on G,       L_H=x(H)-z(H)>=0,
U_s={(p-s)x(G)-g x(P)+(p-s)[z(H)-hb]+gsb}/g.        (20)
```

Multiplication by `m-s` gives the exact reductions

```text
z(H union J)-x(H union J)=delta(J)-L_H,
(m-s)(R_x+R_z)=g[U_s-delta(J)].                      (21)
```

Therefore a cardinality-`s` gainer packet closes the direct branch whenever

```text
L_H<=delta(J)<=U_s.                                  (22)
```

All multistratum dependence has collapsed into the scalar packet weights
`delta_i` and the explicit interval `[L_H,U_s]`.  This does not prove that
such a packet exists, but it converts the direct side of the missing
selection theorem into a cardinality-constrained interval-hitting problem.

### Cross-ordered sufficient condition

The residual hypotheses have a simple purely ordinal sufficient condition.
Suppose

```text
s<=p,
max x(P)<=min x(G),
max z(G)<=min z(H),
J consists of s lowest-z players of G.               (23)
```

Since `s<=p`, `0<B<=1`.  Every payoff in `G` is at least the average payoff
on `P`, so

```text
R_x >=[s+(1-B)(g-s)-Bp] average(x(P))=0.
```

The Lmax order implies `average(z(H))>=b>=average(z(G))`, while the choice of
`J` gives `average(z(J))<=average(z(G))`.  Hence both brackets in `R_z` have
the required signs and `R_z>=0`.  Thus (23) implies the master bound without
assuming that Lmax has only two levels.

When `x=a` on `P union G`, `x=c` on `H`, `z=l` on `P`, and `z=b` on
`G union H`, both residuals vanish identically.  Thus the two-stratum
specialization is

```text
O-[1-gp/{q(m-s)}]T
 =[gpn/{q(m-s)}]l
  +[g/(m-s)][z(H union J)-x(H union J)].             (24)
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
(24) specializes to

```text
O-(5/8)T=(21/8)z_0+(1/2)[z(74)-x(74)].               (25)
```

The lower-envelope game has three generators, actual overlap `11T/12`, and
all seven one-witness branch relaxations have minimum `5/8`.  The hand bound
is above the seven-player target `7/12`; the rooted LP values are a hostile
control, not a premise of the theorem.

The arbitrary-Lmax master also recovers the two archived direct hostile
certificates.  For the actual-top-fixed branch it gives `7/10`, with
`R_x=15/4`, `R_z=111/20`, and packet `1/2` in `[1/2,129/10]`.  For the
top-and-bottom-fixed branch it gives `2/3`, with `R_x=1`, `R_z=11`, and
packet `3/2` in `[3/2,15/2]`; here `s=3>p=1`, showing why the exact
residual criterion is strictly stronger than sufficient condition (23).

### Fixed hostile direct/rooted atlas

An exact finite falsification atlas now checks every sign-compatible `P/H`
partition and every proper gainer packet on all seven fixed hostile branch
selections.  The best certificates, preferring an Lmin-tight comparison, are

```text
branch                              direct base   comparison
optimized spectral                    3/5         11, Lmin-tight
actual top fixed                       3/4         47, Lmin-tight
top and bottom fixed                   2/3         59, Lmin-tight
coefficient-two congestion             5/8         44, Lmin-tight
primitive coefficient-seven (n=8)      5/9        244, direct slack 5/39
sharp G(2,4)                            none        rooted equality arm
sharp G(3,3)                            none        rooted equality arm
```

The residual-sum strengthening is essential: the `3/4` actual-top proof has
`R_x=15`, `R_z=-15/2`, while the primitive `5/9` proof has `R_x=-8/9`,
`R_z=116/117`.  In both cases their sum is positive.  Thus every nonsharp
fixed obstruction is now closed directly, whereas exactly the two sharp
orientations require the rooted block-star arm.  This is strong branch-level
falsification evidence for the direct-or-rooted disjunction, not a proof that
the dichotomy holds for all exact games.

The tempting stronger inference “every nonsharp branch is direct” is false.
An exact census over all 374 archived six-player pairs finds 296 with a
target-reaching direct packet, 282 of those with an Lmin-tight comparison,
but 78 with no direct packet at all.  Seventy-six of the 78 lie strictly
above the target; the first has

```text
x=(1,2,1,1,1,1),
z=(3/2,3/2,3/2,5/6,5/6,5/6),
O/T=6/7>2/3.
```

Thus strict slack does not force a direct certificate.  The independently
formulated common-hinge/root audit already closes all 374 archived pairs and
has exact minimum `2/3`.  Taken together, the two censuses support the
direct-or-rooted disjunction while decisively refuting its direct-only
strengthening.  Both statements remain finite evidence, not a six-player
domain proof.

The proved ceiling-root interpolation bound closes 28 of the 78 direct
failures.  The remaining 50 consist of 34 zero-floor rows, 14 strict
positive-floor rows inside the interpolation wedge, and the two equality
rows.  Every direct failure has a ceiling root.  Thus the live packet lemma
only has to handle the zero-floor/positive-wedge residual plus equality; it
need not reprove the 296 direct or 28 interpolation branches.

### Positive-Lmax equality exclusion

The rooted status of the two sharp rows has a dimension-free human
explanation.  If a direct certificate has base `beta`, comparison slack and
residual sum nonnegative, and `z_i>0` for every player, then `l=z(P)/p>0`.
Identity (17) therefore gives the strict inequality

```text
O>beta T.                                             (26)
```

Consequently, if `O=c_n T` and Lmax is strictly positive, no direct packet
with `beta>=c_n` can exist.  The balanced `G(p,k)` extremizers have
`k(p+1)=floor(n^2/4)`, overlap exactly `c_n T`, and strictly positive Lmax
coordinates `p(k-1)/k` and `1/k`.  They are therefore forced onto the rooted
arm.  The indecomposable block-star semi-balanced system from Section 4
supplies that arm at equality.  This separates the mechanisms structurally:
direct gluing can close nonsharp branches, but positive-Lmax equality is
carried by the rooted exact-cone facet.

### `G(p,k)` direct/rooted handover theorem

The entire extremal family exhibits the same mechanism, including strict
nonbalanced members.  Use its standard blocks `{r}`, `O`, and `B`, with
`|O|=p`, `|B|=k`, and take in the master theorem

```text
P=O,        G=B,        H={r},        J=B\{b}.
```

The comparison coalition is the common block-star hinge `C_b`.  From the
closed-form selections, putting

```text
d=[p(k-1)-1]/[k(p+1)],
```

each gainer has gain `pd`, the root has loss `p(k-1)d`, and the packet
`J` has gain exactly `p(k-1)d`.  Thus its comparison is tight, its packet
interval is a singleton, and both residuals vanish.  Formula (18) gives

```text
direct base = n/[(p+1)(k+1)].                        (GPD)
```

It reaches the universal target exactly when

```text
(p+1)(k+1)<=floor(n^2/4).                            (GPC)
```

By contrast, the rooted block-star theorem gives

```text
rooted base = n/[k(p+1)]>=n/floor(n^2/4)             (GPR)
```

for every `p,k`, because `k+(p+1)=n`.  The one-unit shift from `k` to
`k+1` is the complete handover: direct gluing closes sufficiently unbalanced
parameters, while the rooted facet supplies the missing factor near the
balanced split and is sharp when `k(p+1)=floor(n^2/4)`.  For example,
`G(3,2)` has direct base `1/2` but rooted base `3/4>2/3`; `G(2,4)` and
`G(3,3)` have direct bases `7/15` and `7/16` but rooted base `7/12` at
equality.  This is a human dimension-free classification of the two proof
mechanisms on `G(p,k)`, not a classification of all exact games.

The exact-cone interpretation is numerical as well as combinatorial.  The
direct denominator and the rooted facet-price denominator are

```text
D_direct=(p+1)(k+1),
D_root=p(k-1)+n-1=k(p+1),
D_direct-D_root=p+1.
```

The pair-spoke shear of Section 4 is precisely the indecomposable
semi-balanced atom realizing `D_root`; the direct identity retains the
strictly positive low-Lmax payment on the `p` outside players.  Thus the
root-zero exactness witness and its facet replace a visible `p+1` denominator
penalty.  This is the exact-cone reason the common hinge alone is insufficient
near balance.

## 7. Hand payment certificate for the spectral branch

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
 +(3/4)(x_0-x_4)+(1/2)(z_4-z_5)+(z_5-z_1).          (27)
```

Every term is nonnegative by a displayed core/witness comparison,
nonnegativity, or branch order.  At the actual control every coalition
bracket is zero.  Its strict margin `119/1080` consists only of `z_2` and
three payoff-stratum gaps.  This proves by hand that the mixed packet fixes a
baseline above the universal target while ordered label currency pays the
multistage defect.

The new direct atlas also proves `O>=3T/5` on this fixed selection, already
above the target `7T/12`.  Thus the stronger `3T/4` mixed certificate is no
longer needed to close this control; it is retained as a human proof of the
rooted mechanism that the positive-Lmax equality cases require.

The adjacent verifier checks (27) as a coefficient identity and verifies a
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
  rows, a complete direct-packet atlas on seven fixed hostile selections,
  a 374-pair six-player direct census with 78 exact negative controls,
  and exact arbitrary-Lmax replays of both archived direct hostile branches
  for (17), plus fourteen exact staged selection certificates for its fresh
  seven-player control;
- all nine extreme mixed-witness projection cuts have price within their
  dimensional threshold; eight have only nongaining deficits, but only five
  put every deficit on the first Lmin floor.

The nine-cut statement is a finite coefficient audit, not a theorem.  Together
with (17), it isolates the remaining obstacle as a direct-or-rooted selection
lemma: either some Lmin-tight comparison supplies a cardinality-constrained
gain packet satisfying (22), or failure of all such packets must produce an
affordable mixed-colour rooted packet.  Neither alternative has been proved
universally.

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
