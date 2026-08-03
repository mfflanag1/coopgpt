# Focused prior-art audit: quantitative carrier theorem

Search date: 2026-08-03.

## Scope searched

The search covered exact TU games, exact-core polyhedra, minimal balanced
collections, leximin/Lmin/Lmax core selections, egalitarian solutions, and
coalitional monotonicity. The closest sources located were:

- Schmeidler (1972), *Cores of exact games, I*.
- Studený and Kratochvíl (2022), [*Facets of the cone of exact games*](https://doi.org/10.1007/s00186-022-00770-4).
- Laplace Mermoud, Grabisch, and Sudhölter (2025), [*Minimal balanced collections and their applications to core stability and other topics of game theory*](https://arxiv.org/abs/2507.05898).
- Mirás Calvo, Quinteiro Sandomingo, and Sánchez Rodríguez (2020), [*The boundary of the core of a balanced game: face games*](https://doi.org/10.1007/s00182-019-00703-2).
- Dietzenbacher (2021), [*Monotonicity and egalitarianism*](https://doi.org/10.1016/j.geb.2021.03.006).
- Arin and Feltkamp (2012), [*Coalitional games: Monotonicity and core*](https://doi.org/10.1016/j.ejor.2011.07.025).

## Findings and claim discipline

1. **Generating minimal balanced collections is prior art.** Laplace Mermoud,
   Grabisch, and Sudhölter implement Peleg's algorithm and report complete
   catalogs through seven players (200,214 labeled collections at six players
   and 132,422,036 at seven). The paper must not present general minimal-
   balanced enumeration as new. The new use here is the eta-dual slice
   containing a prescribed target, followed by exact-cone objective
   certification.

2. **The polyhedral exact-game cone is prior art.** Studený and Kratochvíl
   characterize its facets using indecomposable minimal semi-balanced systems.
   The global-witness cone used in the computation should be presented as a
   convenient exact representation for this problem, not as a new general
   description of exact games.

3. **The nearby monotonicity literature uses different selectors and
   domains.** Dietzenbacher studies the Lmax selector on the PES-stable domain;
   Arin and Feltkamp study monotonic core solutions on veto-balanced games.
   These papers are directly relevant context but do not state the carrier
   inequality used here.

4. **No matching prior theorem was located** for the quantities gamma_S and
   eta_S, their inequality for every exact core, the complete six/seven
   threshold, or the displayed triangular seven-player family. Searches also
   found no treatment of the leximin-above-singleton-floors selector on the
   full class of exact games. This is evidence of novelty, not proof of
   novelty.

5. **Required external follow-up.** Before submission, a game-theory expert
   should search MathSciNet, zbMATH, and citation chains from the six sources
   above; the six-player census should also be cross-checked against the
   published minimal-balanced catalogs if the underlying data can be obtained.

## Defensible current novelty statement

> We derive a target-conditioned eta-dual correspondence with minimal balanced
> collections and use exact rational certificates to prove a quantitative
> carrier inequality through six players. A triangular three-generator exact
> family disproves the inequality from seven players onward. We are not aware
> of an earlier statement of this inequality or its sharp dimension threshold.

Do not replace “we are not aware” by “first” until the external search is
completed.
