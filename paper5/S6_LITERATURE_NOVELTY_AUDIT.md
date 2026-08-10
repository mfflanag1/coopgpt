# Literature and novelty audit for the six-player bound

Date: 2026-08-10

## Scope and conclusion

This is a targeted primary-source audit, not a definitive novelty opinion.
The search located the established definitions, axiomatizations, continuity,
antiduality, large-core results, exact-partition theory, and exact-cone facet
theory surrounding `Lmin`, `Lmax`, and exact games.  It did **not** locate a
published quantitative bound on

```text
||Lmin(v)-Lmax(v)||_1 / v(N),
```

a sharp six-player value `2/3`, the two equality payoff profiles, or the
singleton-exactness exchange-blocker theorem used here.

That negative search result supports presenting the theorem to specialists as
a candidate new result.  It does not establish novelty: terminology differs
across the egalitarian-core, Lorenz-stable, imprecise-probability, polymatroid,
and discrete-convexity literatures, and an expert may know an equivalent
result under another formulation.

## Primary sources checked

1. **Arin and Iñarra (2001), “Egalitarian solutions in the core.”**
   Introduces the Lorenz stable set, the leximin stable allocation, and the
   egalitarian core.  This is the source lineage for `Lmin`, not for a
   quantitative separation from `Lmax`.
   DOI: <https://doi.org/10.1007/s001820100073>.

2. **Arin, Kuipers, and Vermeulen (2003), “Some characterizations of
   egalitarian solutions on classes of TU-games.”**  Defines the `Lmax` and
   `Lmin` core solutions on balanced games and develops their characterizing
   properties.  The paper is also the appropriate prior-art source for the
   selectors' existence/single-valuedness machinery.
   DOI: <https://doi.org/10.1016/S0165-4896(03)00051-9>.

3. **Arin, Kuipers, and Vermeulen (2008), “An axiomatic approach to
   egalitarianism in TU-games.”**  Gives continuity arguments for `Lmax` and
   `Lmin` and places both among Lorenz core selections.
   DOI: <https://doi.org/10.1007/s00182-008-0133-6>.

4. **Dietzenbacher (2021), “Monotonicity and egalitarianism.”**  Studies
   `Lmin` and `Lmax` on balanced and PES-stable games, characterizes `Lmax` on
   the latter domain, and records their relation to large-core games.  It
   explicitly treats the two selectors as distinct but does not supply the
   fixed-dimensional distance problem considered here.
   DOI: <https://doi.org/10.1016/j.geb.2021.03.006>.

5. **Dietzenbacher and Yanovskaya (2020), “Antiduality in exact partition
   games.”**  Records that `Lmin` and `Lmax` are antidual on balanced games and
   develops exact-partition characterizations of the Dutta--Ray solution.
   DOI: <https://doi.org/10.1016/j.mathsocsci.2020.04.006>.

6. **Biswas, Parthasarathy, Potters, and Voorneveld (1999), “Large cores and
   exactness.”**  Establishes the relevant relationship between exact and
   large-core games, including the small-player boundary used in the companion
   rigidity argument.
   DOI: <https://doi.org/10.1006/game.1998.0686>.

7. **Llerena and Mauri (2017), “On the existence of the Dutta--Ray's
   egalitarian solution.”**  Introduces exact partition games and proves the
   Lorenz-dominant core conclusion on that domain.  This supports the
   four-player coincidence result but does not cover all exact games at six
   players.
   DOI: <https://doi.org/10.1016/j.mathsocsci.2017.07.002>.

8. **Studený and Kratochvíl (2022), “Facets of the cone of exact games.”**
   Characterizes the exact cone through indecomposable semi-balanced systems
   and facet-defining inequalities.  This is the main adjacent structural
   reference for exactness; no egalitarian-selector distance theorem was
   found in it.
   DOI: <https://doi.org/10.1007/s00186-022-00770-4>;
   preprint: <https://arxiv.org/abs/2103.02414>.

9. **Frank and Murota (2022), “Decreasing Minimization on
   Base-Polyhedra: Relation Between Discrete and Continuous Cases.”**
   Relates the continuous lexicographically optimal base to decreasingly
   minimal integral points, principal/canonical partitions, and proximity
   between the continuous and discrete problems.  Its object is one dec-min
   selector on a base-polyhedron (or its integral points), not the distance
   between the two opposing Lorenz core selectors considered here.
   Preprint: <https://arxiv.org/abs/2202.06561>.

10. **Frank and Murota (2019), “Discrete Decreasing Minimization, Part I.”**
    Characterizes dec-min elements of integral base-polyhedra/M-convex sets
    by exchange and canonical-chain structure.  This is relevant background
    for a possible exchange reformulation, but it does not by itself identify
    a general exact-game core with a base-polyhedron or turn `Lmin` and
    `Lmax` into the two selectors in the present theorem.
    Preprint: <https://arxiv.org/abs/1808.07600>.

11. **Kroupa and Studený (2019), “Facets of the Cone of Totally Balanced
    Games.”**  Characterizes those facets by irreducible min-balanced
    systems.  Together with the exact-cone paper, this locates the adjacent
    set-system/facet language but does not analyze egalitarian selection
    geometry within an individual core.
    DOI: <https://doi.org/10.1007/s00186-019-00672-y>;
    preprint: <https://arxiv.org/abs/1812.00576>.

12. **Gong, Dietzenbacher, and Peters (2022), “Reduced two-bound core
    games.”**  A two-bound core is exactly a box--efficiency-hyperplane
    section, `C(v)=[l*,u*]∩X(v)`.  The paper proves that its egalitarian
    core is a singleton and gives the explicit clipped-level (water-filling)
    formula.  Since both selectors considered here belong to the Lorenz-
    stable/egalitarian core, they coincide on this special class.  This is a
    useful positive transfer, but not a theorem about arbitrary exact-game
    cores; the paper treats two-bound cores as a restricted domain and notes
    that all balanced games are two-bound only through three players.
    DOI: <https://doi.org/10.1007/s00186-022-00800-1>.

13. **Gong and Dietzenbacher (2026), “Core bound reduced games and
    consistency.”**  Introduces lower/upper exact-core-bound reductions and
    constrained lower/upper equality values on all balanced games.  These
    values are coordinatewise clipping rules built from individual exact
    core bounds, not the two Lorenz core selectors.  Crucially, the paper's
    three-player example shows that either constrained equality value may
    lie outside the core.  Thus its bilateral core-bound consistency theorem
    cannot be substituted for the present within-core exchange theorem.
    DOI: <https://doi.org/10.1007/s00182-026-00986-2>.

14. **Gong and Li (2025), “Reduced game and constrained egalitarianism.”**
    Characterizes two values obtained by equalizing subject to singleton
    worths or marginal contributions.  The constraints use coordinate
    benchmarks rather than all coalition inequalities, so the values are
    not `Lmin` and `Lmax` on a general exact core and no selector-distance
    result is stated.
    DOI: <https://doi.org/10.1016/j.orl.2024.107231>.

## Adjacent-language transfer audit

The closest apparent transfers separate into five distinct levels:

1. **Base-polyhedron decreasing minimization.**  This literature gives
   exchange and canonical-partition structure for one lexicographically
   optimal base and, in the integral setting, its dec-min points.  The present
   theorem concerns the separation of two opposing Lorenz selections in the
   core of an arbitrary exact game.  No checked source states that every such
   core has the required base-polyhedron representation, or that both
   selectors become a known dec-min/increasing pair under one.  Establishing
   such a representation would be a substantive theorem, not a terminological
   substitution.  In particular, a core has the standard base-polyhedron
   representation when the game is convex/supermodular; exactness alone is
   coalitionwise attainability and does not impose that lattice inequality.
   The exact-cone facet description therefore does not itself supply the
   missing submodular rank function.

2. **Exact-cone and totally-balanced-cone facets.**  Semi-balanced and
   min-balanced systems describe inequalities cutting out classes of games in
   game-value space.  The fixed-six theorem instead controls the relative
   positions of two selected points inside each core.  A facet classification
   may help derive the blocker theorem, but the checked classifications do
   not state that implication.

3. **Two-bound cores and exact core bounds.**  On the box--hyperplane class,
   the clipped-level formula collapses the Lorenz-stable set to one point and
   therefore collapses the two selectors.  This is the closest checked
   positive geometric theorem.  General exact cores need not be box--
   hyperplane sections.  The 2026 bound-consistency extension to all balanced
   games does not repair that gap: its clipped coordinate values can fail
   core membership already with three players.

4. **Exact partition and antiduality.**  These results explain coincidence or
   axiomatic relations on special domains.  They do not furnish the
   quantitative `2/3` separation bound on the full six-player exact domain.

5. **Coherent lower probabilities.**  Exact games also occur in this
   language, as the exact-cone source records.  The targeted search found no
   selection-distance result there, but this is the least conclusive portion
   of the audit because the selectors may be named differently.

## Concrete transfer tests

The two closest theories can be tested without relying on terminology.

**Base-polyhedron test.**  Suppose an exact game `v` had its core represented
as the base-polyhedron `B(f)` of a submodular function `f`, in the original
player coordinates.  Exactness and the standard tightness property of a
base-polyhedron give, for every coalition `S`,

```text
v(S) = min{x(S): x in C(v)} = f(N) - f(N\S).
```

The right-hand side is supermodular in `S`; hence `v` would be convex.  The
converse is the standard core/base-polyhedron representation of a convex
game.  Therefore, on exact games, this direct representation is available
exactly on the convex subdomain.  Exact games outside that subdomain cannot
be imported into Frank--Murota by merely renaming their cores.  A more
general affine or extended formulation remains logically possible, but a
reviewer would have to exhibit it and prove that it preserves both sorted
lexicographic selectors and the normalized `L1` metric.

**Two-bound test.**  If `C(v)=[l*,u*]∩X(v)`, the 2022 clipped-level theorem
makes the egalitarian core a singleton.  Since `Lmin` and `Lmax` are both
Lorenz-stable selections, they must be that same point.  Consequently every
archived exact example with `Lmin != Lmax` is, without further computation, a
certificate that the full exact domain cannot be reduced to the two-bound
domain.  By contrast, the 2026 constrained equality values apply on all
balanced games but are not core selections; their published three-player
example explicitly witnesses the failed premise.

This audit therefore found no theorem that presently subsumes the claimed
bound.  The two-bound-core result is an important boundary case, not a
subsuming result.  The remaining high-value novelty question is precise: can
a specialist derive the singleton-exactness blocker or the `2/3` inequality
from a known base-polyhedron, exact-cone, exact-core-bound, or coherent-lower-
probability theorem after an explicit translation?  Until that question is
answered, the
appropriate claim is “no equivalent located in a targeted cross-domain
search,” not “first” or “previously unknown.”

## Searches performed

Searches combined the phrases

```text
"Lmin solution" "Lmax solution"
"Lmin(v)" "Lmax(v)" exact games
distance between egalitarian core solutions
leximin stable allocation leximax exact game
six-player exact cooperative game egalitarian
Lorenz dominance exact games Lmin Lmax
```

and followed citations in the primary sources above.  A date refresh on
2026-08-10 additionally searched `exact core bounds`, `core bound reduced
games`, `two-bound core games`, and constrained-egalitarian reduced-game
terminology, including publications through March 2026.  Searches were also
run
against exact-cone facets, exact partition games, large cores, antiduality,
assignment/matching-game leximin/leximax work, and recent monotonicity papers.
The adjacent-language pass additionally checked continuous and discrete
decreasing minimization on base-polyhedra, M-convex exchange, totally balanced
cone facets, semi-balanced systems, and coherent-lower-probability terminology.

## Claim discipline for the manuscript

The defensible statement is:

> We are not aware of a prior quantitative fixed-dimensional separation bound
> between `Lmin` and `Lmax` on exact games.  A targeted search of the principal
> egalitarian-core and exact-game sources found no equivalent of the sharp
> six-player theorem.  Novelty remains subject to specialist review.

Avoid “first,” “new,” or “previously unknown” without qualification.  A
specialist reviewer should specifically check whether antiduality, two-bound
or exact-core-bound reductions, base-polyhedron dec-min theory, or coherent-
lower-probability results imply an equivalent inequality under different
terminology.
