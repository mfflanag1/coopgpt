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

## Third pass, 2026-08-05: zbMATH Open and the catalogue

Both items previously listed as unreachable turned out to be reachable.

### zbMATH Open

zbMATH has been open access since 2021 and exposes a JSON API at
`api.zbmath.org/v1/document/_search`.  Review texts are licence-restricted but
titles, authors, years and MSC codes are returned.  The informative queries
were the empty ones:

| query | hits |
|---|---|
| `ab: "exact games" & ab: "four players"` | 0 |
| `ab: "Lorenz" & ab: "core" & ab: "exact game"` | 0 |
| `ti: leximin & ti: core` | 0 |
| `ab: "lexicographically" & ab: "core" & ab: "egalitarian"` | 4, all already known |
| `ab: "exact partition games"` | 4, all already known |
| `ab: "egalitarian core"` | 7 |
| `ab: "large core" & ab: "exact"` | 5, headed by Biswas et al. (1999) |

Nothing states the richer-side one-packet selection theorem or the staircase.
Two confirmations and one addition:

- `Antiduality in exact partition games` is indexed as Dietzenbacher and
  Yanovskaya (2020), confirming the manuscript bibliography.
- Biswas et al. (1999) is confirmed as the source of the four-player
  large-core bound.
- New adjacent reference: Arin and Inarra, *Egalitarian sets for TU-games*,
  Int Game Theory Rev 4 (2002) 183-199, a set-valued follow-up to their 2001
  paper.  It concerns egalitarian solution concepts and the egalitarian core,
  not leximin failure classification.  No collision.

MathSciNet remains subscription-gated and was not consulted.

### The Studeny-Kratochvil catalogue

The catalogue is public at
`gogo.utia.cas.cz/indecomposable-min-semi-balanced-catalogue/`, with CSV data
per player count.  It is purely combinatorial: permutational types of
indecomposable min-semi-balanced systems, in one-to-one correspondence with
facets of the exact cone.  It contains no leximin or egalitarian content, so
there is no priority collision with the selection theorem.  Counts: 280
systems in 16 permutational types on five players, 53 types on six.

The check was turned into a positive result rather than only a negative one.
The smallest failure, the `(m,h)=(4,1)` family member on five players, has
tight proper coalitions `ce, de, cde, acde, bcde` at its Lmin point, and each
admissible packet coalition yields a system (P) that is, up to permutation and
overall sign, one of the catalogued types.  Different packet coalitions give
different types, which is the concrete form of the multi-class remark in the
manuscript.  This is now Remark 5 of `paper4/threshold.tex`.

One caution for anyone extending this: the catalogue labels permutational
types by arithmetic expressions encoding set cardinalities, not by numeric
index, and the CSV row order is not a published numbering.  Cite the systems
explicitly, not row numbers.  Note also that the CSV includes a column for
the grand coalition; forgetting to drop it corrupts the sign split that
identifies the exceptional coalition.
