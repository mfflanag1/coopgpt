# Six-player equality classification and first-crossing reduction

Date: 2026-08-09

## Status

This checkpoint gives a complete **solver-level** classification of equality
in the six-player full-staged generator normal form.  It also gives exact
rational realizations of every surviving type and independently checked CPC
proofs of rigidity and anchor geometry within those types.

It is not yet stated as an unconditional theorem about all exact games.  The
3,348 support-type exclusions in the equality-with-triple census and the
3,350 strict-failure exclusions remain exact QF_LRA solver verdicts rather
than a human reduction or checked proof object for every row.  The normal-form
and hand-net dependencies also still require hostile specialist review.

## 1. Conditional finite classification

Assume the following audited dependencies:

1. the certificate-preserving `n+2`-generator normal form in
   `CORE_CLOSURE_REDUCTION.md`;
2. the 37,277 stratum/table universe and the sound hand exclusions recorded in
   `triage32.json`;
3. the full per-player, per-stage Lmin and Lmax Farkas encoding in
   `core_closure_pipeline.py`; and
4. the exact interpretation of the QF_LRA verdicts in the accepted census
   artifacts.

Then the finite system has no point with

```text
||Lmin-Lmax||_1 > 2/3,
```

and equality is feasible in exactly two stratum/table types, up to player
permutation:

| survivor | Lmin strata | Lmax strata | table | forced Lmin | forced Lmax |
|---:|---|---|---|---|---|
| 1408 | `(4,2)` | `(2,4)` | `((2,2),(0,2))` | `(1,1,1,1,4,4)/12` | `(0,0,1,1,1,1)/4` |
| 2236 | `(5,1)` | `(2,4)` | `((2,3),(0,1))` | `(1,1,1,1,1,4)/9` | `(1,1,4,4,4,4)/18` |

The finite decision is the disjoint equality split

```text
equality with a tight triple of Lmax-top players:       2 SAT / 3348 UNSAT
equality without such a tight triple:                   0 SAT / 3350 UNSAT
```

so every equality case lies in the first line and only indices 1408 and 2236
survive.  The strict census is

```text
distance > 2/3:                                         0 SAT / 3350 UNSAT.
```

These are exhaustive finite verdicts, not archive sampling.  They are still
solver evidence until their UNSAT content is replaced by structural
inequalities or exhaustive checked proof objects.

## 2. Exact realizability and staged recomputation

For each SAT row, `audit_core_closure_reconstruction.py` discards the solver's
optimality claim and uses only its displayed rational generators.  It:

1. chooses a smallest displayed zero-cover subfamily;
2. forms the finite lower-envelope game;
3. verifies singleton normalization and exactness coalition by coalition;
4. recomputes Lmin and Lmax with two independently formulated exact rational
   staged LP implementations; and
5. emits one rational pinning certificate for every player at every stage.

Both recomputations return the displayed pairs and overlap `2/3`.  Thus each
surviving type is genuinely realized by a singleton-normalized exact game; the
SAT rows are not artifacts of a relaxed optimality encoding.

The two CPC queries `equality_noncanonical_index1408` and
`equality_noncanonical_index2236` assert equality while requiring at least one
payoff coordinate to differ from the displayed pair.  Z3 and cvc5 return
UNSAT, cvc5 emits a trust-free exact CPC proof, and Ethos returns `correct`.
Consequently payoff rigidity within both surviving full-staged types has an
independently checked proof object.  This does not independently certify that
the other 3,348 types are equality-infeasible.

## 3. A human barrier for the starved equality type

The starved type at index 1408 admits a short proof that does not use its CPC
rigidity object.  Write

```text
x=(a,a,a,a,b,b),       z=(c,c,d,d,d,d),
```

with table `((2,2),(0,2))`.  Label the cells in order as two `(a,c)`
players, two `(a,d)` players, and two `(b,d)` players.  The dimension-free
cross-stratum lemmas give `c<=a` and `d<=b`; equality of totals then forces
`a<d`.  Put

```text
u=a-c,       v=d-a,       w=b-d.
```

Then `u,w>=0`, `v=u+w`, and

```text
||x-z||_1=4v,       1=6c+8v-4w.                       (10)
```

Suppose `v>1/6`.  Since `c>=0`, (10) implies

```text
w >= 2v-1/4 > v/2.                                    (11)
```

Consider the efficiency-preserving direction

```text
h=(0,0,1,1,-1,-1).
```

For a coalition `S`, let `p,r,n` count its players from the `(a,d)`, `(b,d)`,
and `(a,c)` cells.  If `x(S)<=z(S)`, then

```text
pv-un-wr >= 0.                                         (12)
```

But `h(S)=p-r`.  If `p-r<0`, either `p=0<r`, which makes (12) negative, or
`p=1,r=2`, which makes it at most `v-2w<0` by (11).  Hence every coalition
tight at `x` has `h(S)>=0`.  All nontight constraints retain positive slack,
so `x+epsilon h` remains in the core for sufficiently small positive
`epsilon`.  It leaves two minimum coordinates at `a`, raises the other two,
and keeps the rich pair above them.  Its sorted payoff vector therefore
lexicographically improves on `x`, contradicting `x=Lmin`.

Thus this entire stratum/table type satisfies `||x-z||_1<=2/3` by hand.  At
equality, the same argument rules out `w>v/2`; (10) and `c>=0` give the reverse
inequality.  Therefore

```text
v=1/6,   w=u=1/12,   c=0,
```

which forces the canonical index-1408 pair.  This is both a human strict
barrier and a human rigidity proof for one of the two equality profiles.

## 4. A human barrier for the positive type

The positive type at index 2236 also admits a structural proof.  Write

```text
x=(a,a,a,a,a,b),       z=(c,c,d,d,d,d),
```

with table `((2,3),(0,1))`.  Label the cells as two players `N` of type
`(a,c)`, three players `P` of type `(a,d)`, and the player `r` of type
`(b,d)`.  Again `c<=a`, `d<=b`, and equality of totals forces `a<d`.  Put

```text
u=a-c,       v=d-a,       w=b-d.
```

Then `u,w>=0`, `v>0`,

```text
3v=2u+w,                  ||x-z||_1=6v,                 (13)
c=(1-10v+2w)/6,           d=(1+5v-w)/6.                (14)
```

Exactness at the singleton `{r}` supplies a core point `q` with `q_r=0`.
Call a coalition *eligible* if

```text
x(S)>=z(S) and q(S)>=z(S).                              (15)
```

Every coalition tight at `z` is eligible.  Consider the following eight
efficiency-preserving directions (coordinates are ordered as the two `N`, the
three `P`, and `r`):

```text
e_1-e_i                                      (i in P),
(1,1,-1_i,-1_j,0)                            ({i,j} subset P),
(2,1,-1,-1,-1,0),  (1,2,-1,-1,-1,0).        (16)
```

Here omitted coordinates are zero.  Each direction is nonpositive on the
four-player Lmax-top block and is strictly negative somewhere on that block.
The following exchange lemma is the key point.

### Exchange lemma

If `w<2v`, at least one direction in (16) is nonnegative on every eligible
coalition.

### Proof

For a coalition containing `n` players of `N`, `p` players of `P`, and
possibly `r`, the first inequality in (15) is

```text
nu + 1_{r in S} w - pv >= 0.                            (17)
```

If `w<v`, take either of the last two directions in (16).  A negative
coalition with no `N` player contains a `P` player, and (17) would require
`w>=v`.  A negative coalition containing only the coefficient-one `N` player
has at least two `P` players, but even after adding `r` its left side in (17)
is at most `u+w-2v=(w-v)/2<0`.  With only the coefficient-two `N` player it
needs all three `P` players, giving at most
`u+w-3v=(w-3v)/2<0`; with both `N` players it cannot be negative.  Thus this
direction has no negative eligible coalition.

It remains to take `v<=w<2v`.  Define an **atom**

```text
A_i={r,i},       i in P.
```

By (17), a negative eligible coalition with no `N` player is necessarily an
atom, and atom eligibility says `q_i>=2d`.  A negative eligible coalition for
a two-player direction in (16), if it is not an atom, is necessarily

```text
B_{k,ij}={k,r,i,j},       k in N, {i,j} subset P,        (18)
```

and its `q` inequality is `q_k+q_i+q_j>=c+3d`.  The same
description holds for an asymmetric three-player direction, with `k` equal
to its coefficient-one `N` player.

There are four cases.

1. If all three atoms are eligible, `q(P)>=6d>1`, because (14) and
   `w<2v` give `d>1/6`.
2. If exactly two atoms are eligible, use the one-player direction targeting
   the remaining `P` player.  Any blocker omits one eligible atom when it
   contains two `P` players and omits both when it contains only one.  Adding
   the omitted atom inequalities to its `q` inequality gives respectively
   `q(N union P)>=(c+3d)+2d=c+5d>1` or
   `q(N union P)>=(c+2d)+4d=c+6d>1`.  At the endpoint `w=v`, the only extra
   blocker omits `r` and both atoms and gives `c+d+4d=c+5d>1`.
3. If exactly one atom `A_i` is eligible, the two-player direction on
   `P\{i}` must have a blocker `B_{k,P\{i}}`.  The atom and blocker are
   disjoint, so their inequalities give `q(N union P)>=c+5d>1`.
4. Suppose no atom is eligible.  The two asymmetric directions have blockers
   `B_{1,I}` and `B_{0,J}` for two-element subsets `I,J` of `P`.  If `I!=J`,
   adding their inequalities gives `q_{I intersect J}>=2d`, an atom.  Hence
   `I=J={i,j}`.  Apply the two-player directions to `{i,k}` and `{j,k}`, where
   `k` is the remaining `P` player.  If their blockers use different `N`
   players, adding those two inequalities and the two asymmetric-blocker
   inequalities gives `q_i+q_j>=4d`, hence an atom.  If they use the same
   `N` player, add those two inequalities to the asymmetric blocker using the
   other `N` player.  The left side is at most `2`, whereas the right side is
   `3c+9d=3/2+3d>2`, again impossible.

In every case the assumption that all eight directions are blocked is
impossible.  This proves the lemma.  QED.

If `w<2v`, take the direction supplied by the lemma.  Every `z`-tight core
constraint has nonnegative directional derivative; every other constraint
has positive slack.  For sufficiently small positive `epsilon`, therefore,
`z+epsilon h` is in the core.  Its old top coordinates do not increase, at
least one decreases, and the two lower coordinates remain below the old top
level.  This lexicographically improves the decreasingly sorted vector,
contradicting `z=Lmax`.  Thus

```text
w>=2v.                                                   (19)
```

Combine (19) with the Lmin side.  If `w>2v`, then for each `i in P` the direction
`e_i-e_r` is nonnegative on every `x`-tight coalition, by the same count in
(17), and improves the Lmin vector.  Hence Lmin optimality forces `w<=2v`, so

```text
w=2v.                                                    (20)
```

At (20), the only coalition eligible to block `e_i-e_r` is
`(P\{i}) union {r}`.  Lmin optimality therefore forces all three such triples
to be tight at `x`.  Their `x` and `z` sums agree and equal `3d`, so they are
common tight triples.  Evaluating them at the exactness witness `q_r=0` and
summing gives

```text
2q(P)>=9d,       hence d<=2/9.                           (21)
```

But (14) and (20) give `d=(1+3v)/6`; (21) yields `v<=1/9` and therefore

```text
||x-z||_1=6v<=2/3.
```

Equality forces

```text
a=1/9,   b=4/9,   c=1/18,   d=2/9,
```

the canonical index-2236 pair.  Thus both solver-surviving equality types now
have human strict barriers and human rigidity proofs.  The script
`audit_positive_5_1_barrier.py` separately checks the eight-direction
coalition enumeration and the boundary arithmetic.

There is an additional rigidity fact useful for the refined tangent problem.
At equality, (21) is an equality throughout: `q(P)=1`, both `N` coordinates
of `q` vanish, and `q(P\{i})=2/3` for every `i`.  Hence the singleton-`r`
witness is unique:

```text
q=(0,0,1/3,1/3,1/3,0).                                  (22)
```

With the canonical `x,z,q`, an exact coalition check leaves only the three
triples `(P\{i}) union {r}` as eligible negative blockers for any direction
in (16).  For the Lmin direction `e_i-e_r`, exactly its corresponding triple
survives.  This gives the following genuine neighborhood reduction.

### Positive critical-residue theorem

There is a neighborhood of the canonical index-2236 payoff pair such that,
for every singleton-normalized exact game whose two selections lie in that
neighborhood (with players labeled by the three canonical populated cells):

1. all three triples `(P\{i}) union {r}` are tight at Lmin; and
2. at least two of them are also tight at Lmax.

### Proof

For the first claim, suppose a triple corresponding to `i` were not tight at
`x`.  At the canonical pair, every other coalition on which `e_i-e_r` is
negative has the strict wrong sign `z(S)<x(S)`.  That remains true in a small
neighborhood.  Hence `e_i-e_r` would be nonnegative on every `x`-tight
constraint, and a short step would improve Lmin, a contradiction.

For the second claim, choose an exactness witness `q^m_r=0` along any sequence
of such games converging to the canonical pair.  Compactness gives a convergent
subsequence.  The first claim makes all three triple values converge to
`2/3`; evaluating them at the witness shows that its limit satisfies
`q(P\{i})>=2/3` for every `i`.  The equality argument leading to (22) makes
the limit uniquely `q`.  Therefore every coalition outside the three triples
which is negative for a direction in (16) retains either the strict wrong
`x-z` sign or the strict wrong `q-z` sign.  It cannot be `z`-tight.  Lmax
optimality requires every direction in (16) to have a negative tight blocker.
The three one-player directions have blocker sets `{T_2,T_3}`,
`{T_2,T_4}`, and `{T_3,T_4}`; hitting all three requires at least two
triples.  A compactness contradiction upgrades the sequential statement to a
single neighborhood.  QED.

Thus the positive refined-tangent problem has a three-constraint critical
residue, not a 62-coalition local residue.  This is a reduction of the next
problem, not yet a proof that arbitrary simultaneous splits are non-outward.

### The three-triple residue is not the missing theorem

The exact audit `audit_positive_critical_relaxation.py` prevents one tempting
overreach.  It exhibits rational displayed generators satisfying all six
singleton zero-coordinate conditions, all three Lmin-triple inequalities,
and in fact all three common-triple equalities, with displayed pair

```text
x~=(2/135,29/270,7/30,1/6,7/30,11/45),
z~=(1/270,1/270,47/135,38/135,47/135,2/135)
```

and

```text
||x~-z~||_1=31/45>2/3.                                  (23)
```

This relaxation is arbitrarily local.  Interpolate `x~`, `z~`, and each of
its six indexed singleton witnesses componentwise with the canonical pair and
the canonical witnesses from the accepted index-2236 model.  Every simplex,
zero-coordinate, triple-dominance, and common-triple condition is affine and
holds at both endpoints.  The cross-cell signs agree, so for `0<lambda<=1`
the displayed distance is exactly

```text
2/3 + lambda/45.                                         (24)
```

Thus even the complete three-triple critical residue permits a first-order
outward ray if staged selection optimality is discarded.

Closing the eight displayed generators produces a singleton-normalized exact
game.  Two independently formulated exact rational LP implementations then
recompute

```text
Lmin=(13,13,22,13,22,52)/135,
Lmax=(8,8,32,23,32,32)/135,
||Lmin-Lmax||_1=4/9.                                    (25)
```

The Lmin trace has strata `(3,2,1)` and the Lmax trace has strata `(2,1,3)`;
the artifact contains all twelve per-player staged pinning certificates.
Hence exact closure repairs (23) by changing the later lexicographic strata,
not by violating exactness or losing the three triples.  This identifies the
missing structural condition sharply: the refined proof must retain the full
staged pinning packet (or a theorem genuinely equivalent to it).  Neither
singleton exactification nor the critical common triples can replace that
packet, even infinitesimally.

### Exact one-split residue

The critical-residue theorem nevertheless makes the first finite tangent
layer very small.  Among the eleven hand-net survivors obtained by leaving
the positive type coarse or splitting exactly one Lmin/Lmax block,
`audit_positive_one_split_residue.py` finds:

```text
critical triples + r-singleton exactness already UNSAT:   8
still SAT until staged pinning is restored:               3
full-staged verdict on those three:                  0 SAT / 3 UNSAT.
```

The exact staged residue is

| census index | refinement | missing side indicated by minimized navigation core |
|---:|---|---|
| 1414 | Lmax top `4 -> 1+3` | first Lmax ceiling pin |
| 1442 | Lmin bottom `5 -> 3+2` | first Lmin floor pin |
| 2268 | Lmin bottom `5 -> 4+1` | first Lmin floor pin |

The first two columns and both SAT/UNSAT layers are regenerated directly; the
last column is proof-discovery navigation, not independent proof evidence.
This is the first explicit finite obstruction list produced by the local
theory: a human one-split completion now needs only three staged cases rather
than eleven support types or 62 coalition constraints.

This still does **not** reduce simultaneous splits to one split.  The tangent
graph of a piecewise-linear lexicographic selection need not be convex, so a
formal braid-cone decomposition of payoff derivatives would not by itself
show that its summands remain realizable selection derivatives.  The three-row
list is therefore a genuine next lemma, not a surrogate proof of the whole
1,659-type positive refinement neighborhood.

## 5. Equality anchor geometry is exact

Every equality model in either surviving type has a tight coalition consisting
of three Lmax-top players.  Giving that coalition weight `1/3` yields

```text
eta = 0,
alpha_i = 1/3 on the triple and 0 elsewhere,
theta <= 1/3.
```

The two `equality_no_triple` CPC proofs establish the existence statement
throughout each surviving type.  The two `equality_subthird` CPC proofs exclude
any Lmax over-cover with every top weight strictly below `1/3`.  Hence, within
both equality types,

```text
theta = 1/3.
```

The independent exact LP on each reconstructed game finds the same optimum,
with `eta=0` and one tight triple in its support.  This upgrades the earlier
five-game archive observation to a rigid statement on the two solver-surviving
equality types, conditional only on the finite type classification.

## 6. A first-crossing structural reduction

There is a useful route from equality classification back to the strict bound.
Let `u_N` be the unanimity game, normalized by `u_N(N)=1` and
`u_N(S)=0` for proper `S`.  It is exact and both selections are uniform.
The exact-game cone is convex: if `v,w` are exact, add coalition-attaining core
points to show that `v+w` is exact.  Therefore, for any normalized exact `v`,

```text
v_t = (1-t)u_N + t v,       0 <= t <= 1,
```

stays normalized and exact.

For `t<1`, the unanimity component supplies a strict relative-interior core
point for every proper-coalition inequality.  Standard finite-dimensional
parametric-LP/Hoffman continuity, applied stage by stage, then makes Lmin,
Lmax, and their distance continuous along this path.  Thus a strict
counterexample would have a first parameter `t_0<1` with distance exactly
`2/3`.

At `t_0`, the conditional classification forces one of the two tables above.
Because each profile has a positive gap between its two Lmin levels and its
two Lmax levels, sufficiently nearby ordered strata can split a coarse level
but cannot cross a coarse gap.  The post-crossing table must therefore be a
contiguous refinement of one of the two equality tables.

`audit_equality_refinement_neighborhood.py` enumerates that combinatorial
neighborhood exactly:

```text
all six-player configurations:                         37,277
refinements of at least one equality type:             14,109
hand-net survivors in their union:                      2,163
strict-failure verdicts on those survivors:     0 SAT / 2,163 UNSAT
```

There are only 34 coarse or one-split refinements, 22 of which survive the
hand net.  That smaller number is diagnostically attractive but is **not** yet
a valid proof reduction: a one-parameter perturbation may split several equal
blocks simultaneously.  A tangent-cone lemma showing that every outward
direction is generated by the one-split directions would reduce the strict
proof-object burden to those 22 cases.  No such lemma is claimed here.

## 7. Exact remaining gap

The highest-value next theorem is now sharply localized:

> Prove a **refined** tangent/normal-cone inequality at the two canonical
> equality profiles showing that no simultaneous splitting of their payoff
> strata can increase the distance.

The two coarse stratum/table barriers are now human.  They control movement
that preserves the displayed blocks and force both canonical boundary pairs,
but they do not yet justify projecting an arbitrary simultaneous block split
onto those coarse directions.  A refined tangent theorem, together with the
first-crossing argument, would replace the global strict census by a human
local proof.  A weaker computer-assisted completion would require checked
proof objects for the 3,348 equality-type exclusions and the relevant strict
refinement neighborhood.  Merely adding more sampled games or more unsat
cores would not close either gap.

For the positive profile, the next calculation should begin from (22): all
eight Lmax exchange directions and all three Lmin directions have only the
three common triples as boundary blockers.  The missing statement is a
first-order inequality coupling the full staged pinning packet—not only the
derivatives of those three tight values—to the derivative of
`sum_{i in P}(z_i-x_i)`.  The local relaxation (23)--(25) is a mandatory
negative control for any proposed coupling.  At the one-split level, that
coupling only needs to explain census types 1414, 1442, and 2268.

## 8. Reproduction

From the repository root:

```bash
python3 coopgames/verifiers/s6/verify_two_packet_staged_certificates.py
python3 coopgames/verifiers/s6/verify_frozen_certificates.py
python3 coopgames/verifiers/s6/verify_equality_checkpoint.py
python3 coopgames/verifiers/s6/audit_starved_4_2_barrier.py
python3 coopgames/verifiers/s6/audit_positive_5_1_barrier.py
python3 coopgames/verifiers/s6/audit_positive_critical_relaxation.py \
  --output /tmp/positive-critical-current.json
cmp coopgames/verifiers/s6/positive_critical_relaxation_audit.json \
  /tmp/positive-critical-current.json
python3 coopgames/verifiers/s6/audit_positive_one_split_residue.py \
  --output /tmp/positive-one-split-current.json
cmp coopgames/verifiers/s6/positive_one_split_residue_audit.json \
  /tmp/positive-one-split-current.json

python3 coopgames/verifiers/s6/audit_core_closure_reconstruction.py \
  --census coopgames/verifiers/s6/equality_triple_census.json \
  --output /tmp/equality-reconstruction.json
cmp coopgames/verifiers/s6/core_closure_reconstruction_audit.json \
  /tmp/equality-reconstruction.json

python3 coopgames/verifiers/s6/audit_equality_refinement_neighborhood.py \
  --output /tmp/equality-refinements.json
cmp coopgames/verifiers/s6/equality_refinement_neighborhood_audit.json \
  /tmp/equality-refinements.json
```

The raw shard merger commands and their SHA-256 outputs should be supplied to
reviewers with the checkpoint; raw timing shards remain execution logs rather
than proof objects.
