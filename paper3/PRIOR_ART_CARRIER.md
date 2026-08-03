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
- Arin and Iñarra (2001), [*Egalitarian solutions in the core*](https://doi.org/10.1007/s001820100073).
- Arin and Feltkamp (2012), [*Coalitional games: Monotonicity and core*](https://doi.org/10.1016/j.ejor.2011.07.025).
- Young (1985), [*Monotonic solutions of cooperative games*](https://doi.org/10.1007/BF01769885).
- Housman and Clark (1998), *Note: Core and monotonic allocation methods*,
  *International Journal of Game Theory* 27:611--616.

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

3. **The selector has standard antecedents and must be named accordingly.**
   Arin and Iñarra (2001) introduced the Lmin solution, the core allocation
   that lexicographically maximizes sorted payoffs.  If
   `m_i=v({i})` and `v^0(T)=v(T)-sum_{i in T}m_i`, then the present selector is
   exactly `m+Lmin(v^0)`.  It should therefore be called the *normalized Lmin*
   solution, not presented as a new egalitarian selector.  In every theorem
   below with zero singleton values, including the five-player
   proper-coalition counterexample, it coincides directly with ordinary Lmin.

   Dietzenbacher (2021) explicitly compares Lmin and Lmax.  Lmin is already
   known to fail aggregate monotonicity on the broader egalitarian-stable
   domain, while Lmax is coalitionally monotonic there.  Dietzenbacher's
   displayed failure is not an exact-game proper-coalition pair, and the paper
   leaves important questions about the exact-game domain open.  Arin and
   Feltkamp study monotonic core solutions on veto-balanced games.  These
   sources are directly relevant context but do not state the carrier
   inequality used here.

   Arin, Kuipers, and Vermeulen (2003), [*Some characterizations of
   egalitarian solutions on classes of TU-games*](https://doi.org/10.1016/S0165-4896(03)00051-9),
   is also close in language but not in result: it characterizes the ordinary
   lexicographically maximal core allocation on large-core games and uses
   monotonicity in the worth of the grand coalition. Dietzenbacher's result is
   closer in axiom---its Lmax solution is coalitionally monotone---but its
   selector lexicographically minimizes maximal payoffs, whereas normalized
   Lmin lexicographically maximizes payoffs after canonical singleton
   normalization. Moreover PES-stable games form a proper subdomain of
   balanced games and are not identified with the class of exact games.

4. **No matching prior theorem was located** for the quantities gamma_S and
   eta_S, their inequality for every exact core, the complete six/seven
   threshold, or the displayed triangular seven-player family.  The Lmin
   selector itself is established prior art; the narrower claim supported by
   the search is that no prior treatment was located of its proper-coalition
   monotonicity on the full exact-game class. This is evidence of novelty, not
   proof of novelty.

5. **Required external follow-up.** Before submission, a game-theory expert
   should search MathSciNet, zbMATH, and citation chains from the six sources
   above; the six-player census should also be cross-checked against the
   published minimal-balanced catalogs if the underlying data can be obtained.

6. **The new monotone-path separation appears distinct from the closest
   results.** The post-audit seven-player example has
   `eta_S(phi) < gamma_S(phi)` and binding exact-bump capacity
   `d*_v(S) > phi(S)-v(S)`, yet its complete admissible bump path is monotone
   for every member of `S`. Thus the quantitative carrier inequality is not
   necessary for monotonicity of this selector. The sources above establish
   monotonicity of other egalitarian selectors on other domains; they do not
   appear to give this internal separation between a carrier certificate and
   the behavior it was meant to prove. A defensible claim is therefore: "We
   are not aware of a prior exact-game example combining a failed quantitative
   carrier inequality, a binding exact coalition bump, and an explicitly
   certified monotone leximin-above-floors path." This statement still
   requires MathSciNet/zbMATH and expert citation-chain review.

7. **The five-player proper-coalition counterexample changes the main
   monotonicity conclusion.**  The game pair raises one proper coalition in
   an exact game while two members of that coalition lose under the
   normalized Lmin selection.  Since both games have zero singleton values,
   this is directly an ordinary-Lmin counterexample.  Dietzenbacher's positive
   coalitional-monotonicity theorem is not contradicted: it concerns the Lmax
   selector on the PES-stable domain.  The same paper already shows that Lmin
   fails aggregate monotonicity on that broader domain, but its example does
   not establish the present exact-game proper-coalition result.
   Arin--Kuipers--Vermeulen likewise concern Lmax on large-core games.  More
   broadly, Young (1985) is foundational for
   monotonic solution concepts, and Housman--Clark (1998) prove that no core
   allocation method is coalitionally monotonic on the full balanced-game
   domain for four or more players.  That impossibility does not by itself
   imply failure on the exact-game subclass or identify this selector.  The
   focused searches located no earlier counterexample for the present
   selector on exact games.  The defensible formulation is: "We are not aware
   of an earlier exact-game counterexample to proper-coalition monotonicity of
   the Lmin solution."  An expert database and
   citation-chain search remains required before claiming priority.  The
   A later exact symbolic bridge now proves that five is the minimum possible
   dimension: on singleton-normalized exact games through four players, every
   richer-player suffix at a strict Lmin payoff gap is tight, so Lmin
   Lorenz-dominates the core and equals Lmax/PES.  Combining this with Biswas
   et al. (1999) and Dietzenbacher (2021) yields coalitional monotonicity
   through four players.  Focused searches for `exact games + Lmin + Lmax`,
   `Lmin solution + exact games + four players`, and `leximin stable allocation
   + exact game` located no matching statement.  This new bridge postdates the
   external hostile audit and still requires a specialist novelty check.

## Defensible current novelty statement

> We derive a target-conditioned eta-dual correspondence with minimal balanced
> collections and use exact rational certificates to prove a quantitative
> carrier inequality through six players. A triangular three-generator exact
> family disproves the inequality from seven players onward. We are not aware
> of an earlier statement of this inequality or its sharp dimension threshold.
> Separately, an exact five-player lower-envelope pair disproves
> proper-coalition monotonicity of Lmin (equivalently normalized Lmin here,
> because the witness has zero singleton values), and an exact symbolic
> four-player bridge proves that this failure is dimension-minimal.

Do not replace “we are not aware” by “first” until the external search is
completed.
