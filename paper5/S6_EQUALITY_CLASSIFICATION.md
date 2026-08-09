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

## 3. Readable rigidity algebra

The checked `equality_no_common_triple` formulas prove one additional fact in
each surviving type: some triple of Lmax-top players is tight at **both**
selections.  Once this statement is supplied, the canonical payoff values no
longer look like unexplained solver output.

For index 1408 write

```text
x=(a,a,a,a,b,b),       z=(c,c,d,d,d,d),
```

with table `((2,2),(0,2))`.  The dimension-free cross-stratum lemmas give
`c<=a` and `d<=b`.  A common top triple contains either one or two `b` players;
its equality with the Lmax sum `3d` also forces `a<=d`.  Equality in distance
therefore gives

```text
b-c=1/3.
```

Together with `4a+2b=1` and `2c+4d=1`, this yields

```text
a=1/12-c/2,   b=c+1/3,   d=1/4-c/2.
```

If the common triple contained one `b`, then `2a+b=3d` would give `c=1/6`
and hence `c=d`, contradicting the strict Lmax strata.  It therefore contains
both `b` players, and `a+2b=3d` gives `c=0`.  The first canonical pair follows.

For index 2236 write

```text
x=(a,a,a,a,a,b),       z=(c,c,d,d,d,d),
```

with table `((2,3),(0,1))`.  Again `c<=a`, `d<=b`, and common-triple equality
forces `a<=d`.  The distance and total equations reduce to

```text
2a+c=5/18.
```

A top triple of three `a` players would give `a=d`; the Lmax total would then
make the left side above equal `1/2`, a contradiction.  Thus the common triple
contains the unique `b` player.  Combining `2a+b=3d` with the two total
equations gives

```text
a=1/9,   b=4/9,   c=1/18,   d=2/9.
```

This short algebra independently explains the values once common-triple
existence is accepted.  The common-triple existence itself currently has a
checked finite proof object for each surviving type, not a dimension-free
human proof.

## 4. Equality anchor geometry is exact

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

## 5. A first-crossing structural reduction

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

## 6. Exact remaining gap

The highest-value next theorem is now sharply localized:

> Prove a tangent/normal-cone inequality at the two canonical equality
> profiles showing that no exact-game direction can increase the distance.

Together with the first-crossing argument, that would replace the global
strict census by a human local barrier theorem.  A weaker computer-assisted
completion would require checked proof objects for the 3,348 equality-type
exclusions and the relevant strict refinement neighborhood.  Merely adding
more sampled games or more unsat cores would not close either gap.

## 7. Reproduction

From the repository root:

```bash
python3 coopgames/verifiers/s6/verify_two_packet_staged_certificates.py
python3 coopgames/verifiers/s6/verify_frozen_certificates.py
python3 coopgames/verifiers/s6/verify_equality_checkpoint.py

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
