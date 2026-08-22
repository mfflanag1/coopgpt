# Independent hostile mathematical and prior-art review — PXC101–PXC108

Review target: commit 7dcf839da0af52b9f8f19257366ea0cf6ad597ec, with the
subsequent repair branch separately identified below.  Verifier outputs were
used only as regression/calibration evidence; the general symbolic arguments
were checked independently.

## Bottom line

I found no counterexample to PXC101–PXC107.  PXC101–PXC104 and PXC107 are
mathematically sound within their stated two-top, fixed-complete-Cx scope.
PXC105 and PXC106 appear correct, but at the reviewed commit their
dimension-continuous exactness arguments had submission-blocking proof-
completeness gaps: the asserted lower-envelope minimizers were not displayed
or constructed, and the all-n block lift did not prove its mass budget.
Those gaps are repaired on branch codex/pxc107-canonical-circuits by explicit
PXC105 endpoint minimizers and a uniform PXC106 construction.

PXC107 proves an exact common-direction/cycle alternative, but its original
chosen-witness graph is not canonical.  PXC108 repairs that issue with an
invariant edge relation, proves rank/support bounds, and identifies the
correct oriented-matroid interface.  The whole dependency cycle is not one
oriented-matroid circuit and is not automatically an indecomposable
semi-balanced system or an exact-cone facet.

## Findings by severity

### Critical

None found.

### Major

1. **PXC105 at 7dcf839 lacked an explicit attainment proof.**  Formula
   PXC105d asserted the full lower envelope for sixteen traces and referred to
   endpoint minimizers and interpolation without displaying the thirty-two
   feasible points.  Since exactness, the complete-Cx claim, the tight menu,
   and the selector formulas all depend on that projection, this was a real
   proof-completeness gap even though the formulas are correct.  The repair
   prints all endpoint allocations, checks every defining row, and uses affine
   interpolation on the closed parameter interval.

2. **PXC106 at 7dcf839 did not prove the all-dimension projection.**  Saying
   that omitted block/top coordinates attain the displayed maximum did not
   establish simultaneous feasibility or that the required mass never
   exceeds the total for arbitrary p,q,A.  The assertion that a player is
   non-null because it occurs in a load-bearing row was also not logically
   sufficient.  The repair gives a uniform feasible minimizer, a complete
   mass bound by trace cases, and explicit positive marginal coalitions.

3. **Any “canonical circuit representation” reading of PXC107 would
   overclaim.**  PXC107 chooses a descent and blocker at each vertex, so the
   resulting graph and cycle depend on choices.  What is proved there is
   existence of a finite directed cycle.  PXC108 fixes this by defining an
   invariant edge whenever any exact staged descent cuts any row of another
   cover, and by taking the set of shortest directed cycles.  Even then,
   canonical means the graph and shortest-cycle set are invariant; it does
   not mean the shortest cycle is unique.

### Minor

1. PXC101–PXC102 called the all-n family genuine rather than null-padded
   without printing marginal coalitions.  The claim is true.  The repair now
   gives positive marginals for a,b,j, every added outsider, and both tops.

2. PXC107 should state explicitly that a common direction cannot represent
   incompatible stages for different covers.  A nonzero direction has a
   unique earliest changed z-stratum, so membership in two staged descent
   unions automatically refers to that same stage.

3. The eta-zero uniqueness argument should mention zero-valued outsider
   singletons.  They cannot receive positive weight when ambient load eta is
   zero because their outsider incidence is positive.  Thus the tight top
   pair remains the only qualifying positive-support eta-zero cover.

4. “Chordless” must be read in the directed sense: a nonconsecutive chord, or
   a reverse edge on a cycle longer than two, produces a shorter directed
   cycle.  It is not an assertion about the underlying undirected graph.

### Presentational

1. Separate three layers: the symbolic theorem, exact finite calibrations, and
   scoped discovery censuses.  The n=6 menu searches omit some combination of
   active common-Cx rows, zero normals, mixed top decorations, or exact-game
   realizability and must not be called a global n=6 classification.

2. Use “represented cover circuit” only for the augmented columns of one
   extreme cover plus the normalization target.  Call the global object a
   circuit–covector incidence cycle, not a circuit.

3. Novelty language should say “candidate new selector-specific coupling.”
   Circuit/covector terminology, complementary slackness, exact covers,
   minimal exact-balanced collections, and semi-balanced exact-cone facets
   are prior art.

## Theorem-by-theorem verdict

| Result | Correctness | Significance | Novelty verdict |
|---|---|---|---|
| PXC101 | Correct after direct symbolic check of chamber, selectors, tight menus, cover segment, and common descent | Strong infinite rational family of exact non-null counterexamples | Family/mechanism may be new; lower-envelope and complementary-slackness ingredients are standard |
| PXC102 | Correct all-n specialization of PXC101 | Establishes genuine failure in every n at least 6, not null padding | Consequence of PXC101 rather than separate conceptual novelty |
| PXC103 | Correct necessary-and-sufficient criterion for the common-direction forced-zero branch only | Clean structural characterization | Best viewed as selector-specific complementary slackness; no established exact name found |
| PXC104 | Correct exact six-player cross-cover example; cover triangle and all reduced selectors exhaust | Important falsifier of the claim that every universal failure has one common forced-zero blocker | Cross-cover dependency mechanism may be new in this exact selector setting |
| PXC105 | Statement correct; proof incomplete at 7dcf839 and complete after explicit-minimizer repair | Shows PXC104 lies in a positive-dimensional chamber | Parametric robustness, not a new general theory |
| PXC106 | Statement correct; all-n proof incomplete at 7dcf839 and complete after uniform-minimizer repair | Strongest construction result: genuine cross-cover failures in every n at least 6 | Likely novel family if PXC104 mechanism is novel |
| PXC107 | Correct common/cycle existence dichotomy | Useful conceptual compression; finite-cycle step is elementary after cover collapse | Chosen graph is not canonical; novelty lies in the selector-specific coupling, not graph theory |
| PXC108 | Correct invariant strengthening, support/rank bounds, recognition algorithm, and per-cover circuit interpretation | Best structural/algorithmic theorem in this segment | Potentially new, but requires external specialist confirmation; not an exact-cone facet theorem |

## Independent symbolic checks

- Positive cover weights and the normalized identity force every supported
  row derivative to zero on a top/earlier-stratum-fixed tangent.
- If a descent is nonnegative on the union of cover supports, applying every
  cover identity forces zero on that union; the same direction and its unique
  earliest changed stratum are therefore feasible for every lift.
- Full-game Lmax optimality then supplies a z-tight blocker.  It cannot be an
  active common-Cx row or active nonnegativity normal because those were
  retained, so in the common branch it lies outside the cover union.
- In the no-common branch every vertex has invariant positive outdegree and no
  loop, hence a directed cycle.  A shortest directed cycle is induced.
- For eta positive, extremality of the cover equations plus normalization
  forces full column rank of the outsider incidence on its support.  Full
  outsider rank pins every later stratum; a failing positive-ambient support
  has size at most n-3.
- Appending the ambient column and negative normalization target to one
  extreme cover gives a minimally dependent signed set because the active
  columns are independent and every coefficient in the unique target
  representation is nonzero.

## Prior-art verdict

The closest sources establish related ingredients, not the complete
selector-dependent mechanism:

- Reijnierse and Derks (1998) study coalition collections with one-point core
  and exact covers.  Their object has no ordered Lmax stages, fixed Cx, or
  pair of selected core points.
- Lohmann, Borm, and Herings (2012) characterize minimal exact-balanced
  collections, including the single exceptional negative coefficient and
  three generation types.  The positive augmented top-cover circuit here has
  not been shown equivalent to one of those types.
- Studený and Kratochvíl (2022) identify indecomposable semi-balanced systems
  with facets of the exact-game cone.  PXC108 changes with Cx and payoff
  strata while the exact-game cone does not, so no facet conclusion follows.
- Björner, Las Vergnas, Sturmfels, White, and Ziegler (1999) supply the
  standard circuit, covector, cocircuit, and oriented-matroid programming
  language.

I found no source naming precisely the “one later-stage blocker has zero
weight in every qualifying top cover” mechanism or the cyclic dependency in
which each cover contains a blocker for another cover's descent.  That is not
proof of novelty.  A cooperative-game specialist and an oriented-matroid
specialist should separately search terminology around exact covers,
basis-exchange/pivot graphs, complementary-slackness cycles, and
semi-balanced-system decompositions.

Primary references:

- https://doi.org/10.1007/s001820050084
- https://doi.org/10.1016/j.mathsocsci.2012.01.002
- https://doi.org/10.1007/s00186-022-00770-4
- https://doi.org/10.1017/CBO9780511586507

## Overall assessment

The mathematics is advanced research-level polyhedral cooperative game
theory: exact lower-envelope constructions, staged lexicographic selectors,
Farkas/tangent certificates, finite cover polytopes, and realizable
oriented-matroid language.  After the PXC105/PXC106 repairs, this is a
credible specialized structural contribution.  It is not yet a major field
breakthrough.  Such a claim would require a complete six-player
exact-realizability classification, a dimension-free restriction on cycle
types, or a genuine projection theorem producing new exact-cone facets.
