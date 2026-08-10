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

and followed citations in the primary sources above.  Searches were also run
against exact-cone facets, exact partition games, large cores, antiduality,
assignment/matching-game leximin/leximax work, and recent monotonicity papers.

## Claim discipline for the manuscript

The defensible statement is:

> We are not aware of a prior quantitative fixed-dimensional separation bound
> between `Lmin` and `Lmax` on exact games.  A targeted search of the principal
> egalitarian-core and exact-game sources found no equivalent of the sharp
> six-player theorem.  Novelty remains subject to specialist review.

Avoid “first,” “new,” or “previously unknown” without qualification.  A
specialist reviewer should specifically check whether antiduality, base-
polyhedron dec-min theory, or coherent-lower-probability results imply an
equivalent inequality under different terminology.
