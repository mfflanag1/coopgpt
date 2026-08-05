# Focused prior-art audit: simultaneous Lmin covers and one-packet selection

Date: 2026-08-04

## Sources inspected

1. Arin, Kuipers, and Vermeulen (2008), *An axiomatic approach to
   egalitarianism in TU-games*, International Journal of Game Theory 37,
   565--580, DOI `10.1007/s00182-008-0133-6`.
2. Lohmann, Borm, and Herings (2012), *Minimal exact balancedness*,
   Mathematical Social Sciences 64, 127--135.
3. Studeny and Kratochvil (2022), *Facets of the cone of exact games*,
   Mathematical Methods of Operations Research 95, 35--80, DOI
   `10.1007/s00186-022-00770-4`.
4. Llerena and Mauri (2017), *On the existence of the Dutta--Ray's
   egalitarian solution*, Mathematical Social Sciences 89, 92--99.
5. Dietzenbacher and Yanovskaya (2020), *Antiduality in exact partition
   games*, Mathematical Social Sciences 108, 116--121.

## What is definitely prior art

- Arin--Kuipers--Vermeulen define property I and characterize the lexicographic
  egalitarian selections by the ordered payoff partition and all tight
  coalitions.  Their displayed characterization is a tangent-direction
  condition.  It does not, in the inspected statement, display one
  simultaneous weighted cover that is uniform on a cumulative richer suffix
  and strictly underloads every poorer player.
- Lohmann--Borm--Herings characterize exact games through exact-balanced
  collections and minimal exact-balanced collections.
- Studeny--Kratochvil introduce semi-balanced systems, identify
  indecomposable minimal semi-balanced systems with facets of the exact-game
  cone, and in Lemma 13 give a one-to-many correspondence between minimal
  balanced systems on the full player set and purely minimal semi-balanced
  systems by replacing a set with the complement of the exceptional set.
  Therefore it would be wrong to claim that the mere passage from an
  exceptional incidence relation to a balanced system is new.
- Llerena--Mauri introduce exact partition games and establish the behavior of
  the Dutta--Ray solution on that domain.  Dietzenbacher--Yanovskaya establish
  antidual closure and self-antiduality results on the same domain.

## Candidate distinction that survives this audit

The proposed result begins with the Lmin-selected tight family, obtains a
normal vector positive on a specified cumulative poorer side and zero on its
richer complement, and converts that vector into one simultaneous strict
tight cover.  It then projects this cover onto the richer suffix `H`,
decomposes the projection into minimal balanced packets *on `H`*, and uses

```text
F(r)=1+(|L|-1) max_i r_i-sum_i r_i
```

plus Jensen's inequality to select one lifted packet with positive rooted
defect.  Vertex sparsity then bounds the rooted certificate by `|N|` positive
coalitions.  This is not the Studeny--Kratochvil full-player-set complement
construction.  The resulting slack budget also uses the Lmin labeling of the
two sides.

No inspected source states this richer-side projection and positive-defect
selection theorem.  That is evidence of a plausible novelty boundary, not a
definitive novelty opinion.  A specialist should search MathSciNet, zbMATH,
the coherent-lower-probability literature, and citations to the five papers
above before any priority claim.

## Current verdict

- Exact-partition and Lorenz implications: established prior art.
- Semi-balanced incidence inequality: established prior art.
- Full-set semi-balanced/minimal-balanced correspondence: established prior
  art.
- Simultaneous Lmin normal cover: plausible derived novelty, mathematically
  elementary once property I is expressed as a tangent-cone condition.
- Richer-side one-packet positive-defect theorem: plausible substantive
  novelty; not externally verified.
- Complete boundary staircase and parametric realizations: plausible
  substantive novelty; not externally verified.

## Second pass, 2026-08-05 (post-review)

A further focused search was run over: Kohlberg-criterion and nucleolus
balancedness; Studeny--Kratochvil and the exact-game facet literature;
coherent lower probabilities and credal sets; minimal balanced collections;
exact partition games and Dutta--Ray existence; and Arin--Kuipers--Vermeulen
and its citation neighbourhood.  Nothing found states the richer-side
one-packet selection theorem or the boundary staircase.

Three corrections came out of it.

1. `Arin--Kuipers--Vermeulen (2008)` was cited for "property I".  That paper
   (IJGT 37:565--580) is about independence of irrelevant core allocations
   and the equal-share-distance solution.  The Lmax-on-large-core-games
   content is in Arin--Kuipers--Vermeulen (2003), Math Soc Sci 46:327--345.
   The manuscript now cites Arin--Inarra (2001) for transfer blocking, which
   is the property actually used, and AKV (2003) for Lmax.  Note also that
   the protector property is the `H={r}` case of the cover lemma, so the
   argument does not depend on the citation.
2. `Biswas et al. (1999)` was missing entirely, although it supplies the
   four-player large-core bound behind the only stated low-dimensional
   comparison.  Added.
3. `Dietzenbacher (2021)` was cited as a Tilburg thesis; the PES/Lmax and
   egalitarian-stable results are in the GEB paper, 127:194--205.  Corrected.

One calibration, not a correction: the linear-size sparsity bound is the
standard basic-solution support bound and is not claimed as new.  An earlier
draft of this note attributed a matching `n-1` bound to Benedek, Fliege and
Nguyen (Math Program, 2020); that is wrong.  Their improvement bounds the
*number* of balancedness checks in the Kohlberg criterion by `n-1`, not the
size of each collection.  The manuscript now makes the weaker, correct point
without the citation.

Still outstanding: MathSciNet and zbMATH, and a direct inspection of the
Studeny--Kratochvil electronic catalogue of indecomposable min-semi-balanced
systems on at most six variables, which is the most likely place for an
unnoticed collision with the packet classes.
