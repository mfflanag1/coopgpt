# Lmin uncrossing and the local-supermodularity obstruction

## Exact-face theorem

Let `v` be any exact game, let `phi` be any core allocation, and fix a proper
nonempty coalition `H`.  Suppose nonnegative weights on proper coalitions
tight at `phi` give a common positive load on `H` and strictly smaller load on
every player outside `H`.  If the `phi`-tight family is closed under union and
intersection, then `H` is tight at `phi`.

Conversely, if `H` is slack, a minimum-energy representation of the given
load vector contains crossing tight coalitions `A,B` with

```text
v(A)+v(B)-v(A intersection B)-v(A union B)
 = s_phi(A intersection B)+s_phi(A union B) > 0.
```

Thus every failed exact face with a strict tight cover contains a canonical
broken diamond in the Boolean coalition lattice.  This statement needs
neither singleton normalization nor an egalitarian solution.

## Lmin corollary

Let `v` be a singleton-normalized exact game and let `phi=Lmin(v)`.  Call `v`
**Lmin-locally supermodular** if, for every pair `A,B` tight at `phi`,

```text
v(A)+v(B) <= v(A intersection B)+v(A union B).
```

Then `v` is an exact partition game witnessed at `phi`, because Lmin
optimality supplies the strict cover at every payoff boundary.  Hence `phi`
Lorenz-dominates the core by the published exact-partition theorem.

Every failure of exact partition at Lmin therefore has two crossing
Lmin-tight coalitions `A,B` with the strict defect

```text
v(A)+v(B) > v(A intersection B)+v(A union B).
```

More precisely, at any slack richer suffix one can choose the pair in the
support of a minimum-energy representation of a strict richer-side cover.
The result is dimension-free.  It contains both of the following domains:

- laminar Lmin-tight families, where no crossing pair exists;
- convex games, where supermodularity holds for every coalition pair.

The condition is weaker than global convexity: it is imposed only on
coalitions binding at one canonical core allocation.  The finite audit
contains an exact nonconvex game satisfying the condition with two nontrivial
payoff strata.

## Tight-pair closure

If tight `A,B` satisfy the displayed supermodular inequality, both their
intersection and union are tight.  Indeed,

```text
v(A)+v(B)
  <= v(A intersection B)+v(A union B)
  <= phi(A intersection B)+phi(A union B)
   = phi(A)+phi(B)
   = v(A)+v(B).
```

Every inequality is equality.  Thus local supermodularity is exactly the
uncrossing closure needed below.

## Minimum-energy uncrossing proof

Fix the player-load vector `c` of the cover in the exact-face theorem.  In the
Lmin application, the strict richer-side cover lemma gives such weights at
every strict payoff boundary.

Among all nonnegative representations of `c` by nonempty `phi`-tight
coalitions, allowing `N`, choose one minimizing

```text
E(lambda)=sum_S lambda_S |S|(n-|S|).
```

The feasible representation polytope is nonempty and compact after the empty
set is discarded: every nonempty coefficient is bounded by a coordinate of
`c`.  Hence a minimizer exists.

Suppose two positive-support coalitions `A,B` cross.  Put
`delta=min(lambda_A,lambda_B)>0`, subtract `delta` from both, and add `delta`
to their intersection and union.  The incidence identity

```text
1_A + 1_B = 1_(A intersection B) + 1_(A union B)
```

preserves the complete load vector.  Tight-pair closure makes the new sets
tight.  Empty intersections may be discarded.  But the energy falls by

```text
2 delta |A setminus B| |B setminus A| > 0,
```

contradicting minimality.  The minimizing support is therefore laminar.

If it contains `N` with weight `gamma`, remove that term.  Every load was at
least `gamma`; the new rich load is `alpha-gamma>0` because every poorer load
was strictly below `alpha`, and all rich-minus-poor gaps are unchanged.
We now have a strict cover on proper tight coalitions with
laminar support.  The laminar strict-cover theorem forces `H` tight.  Applying
this exact-face theorem to every Lmin payoff boundary proves exact partition.

## Canonical obstruction form

The same argument without assuming local supermodularity gives a converse
certificate.  Minimize the energy over representations of a strict cover.
If `H` is slack, the minimizing support cannot be laminar.  Choose a crossing
positive pair `A,B`.  If their intersection and union were both tight, the
uncrossing move would lower energy.  At least one is therefore slack.  Since
`A,B` are tight and `phi` is modular,

```text
v(A)+v(B)-v(A intersection B)-v(A union B)
 = s_phi(A intersection B)+s_phi(A union B) > 0.
```

Thus every failed boundary produces a strict local failure of convexity
among binding coalitions—not merely a fractional trace or a player-count
pattern.

In the sharp five-player example the two protectors are
`A={1,3,5}` and `B={3,4,5}`.  Both are tight, while their intersection
`{3,5}` and union `{1,3,4,5}` each have slack one.  The local-supermodularity
defect is exactly two.  This also kills the proposed balanced-incidence
extension: the obstruction support has only two columns, so its incidence
matrix is balanced and totally balanced.

## Reproduction

```bash
python src/verify_lmin_uncrossing_domain.py \
  --output results/lmin_uncrossing_domain.json
```

The verifier checks the uncrossing identity and exact energy drop exhaustively
for small coalition pairs, recomputes the sharp five-player defect, confirms
the two-column balanced-incidence limitation, and verifies a nonconvex exact
game inside the positive domain.  It is an audit, not a proof dependency.

## Novelty calibration

Uncrossing, laminarization, supermodular games, exact balancedness, and the
published implication from exact partition to Lorenz dominance are prior
art.  The candidate new contribution is their Lmin-specific combination:
local supermodularity only on the binding coalitions at Lmin forces exact
partition, and every failure has a canonical positive uncrossing defect.
Specialist literature review is required before describing this as new.
