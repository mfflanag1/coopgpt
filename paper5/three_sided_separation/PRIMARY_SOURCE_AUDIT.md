# Three-sided assignment games: bounded primary-source audit

Audit date: 2026-09-04. This is a literature and definition audit, not an
external correctness review or a certificate of novelty.

## Exact object being compared

The campaign concerns the standard transferable-utility, three-sided
assignment game: arbitrary nonnegative triple weights; a coalition's worth
is its maximum **integral** disjoint-triple matching weight. The payoff
selection domain is the **entire nonempty core**, with all players included
in the full sorted-payoff leximin and descending-lexicographic-minimum
selections. It is not a selected face, an extended/abstract core, an Owen
set, a fractional worth game, or an assortment-restricted subclass.

The parent campaign now reports a conventional construction theorem with
supremum normalized selector distance 2, already with weights in
{0,1,2,3}, and a separate family with exponentially small leximin/core-maximum
coordinate ratio but zero selector distance. These statements were supplied
by the proof lanes; this file audits their literature position only.

## Directly relevant sources

**Quint (1991), The core of an m-sided assignment game**, Games and Economic
Behavior 3(4), 487–503, November 1991.
[Publisher/DOI](https://doi.org/10.1016/0899-8256(91)90017-9),
[author's publication list](https://www.thomasquintmath.com/publications).
The publisher abstract verifies the multisided extension, possible empty
cores, and a sufficient balanced subclass. The original full text was not
available in this audit. Consequently, no claim is made to have ruled out
every result or construction in that paper. Its nonempty-core subclass must
not silently replace the unrestricted three-sided model.

**Atay and Núñez (2019), A note on the relationship between the core and
stable sets in three-sided markets**, Mathematical Social Sciences 98,
10–14; online 7 January 2019.
[Author PDF](https://ataatay.github.io/webpage/Atay_Nu%CC%81n%CC%83ez_2019_MSS.pdf),
[DOI](https://doi.org/10.1016/j.mathsocsci.2018.12.002).
The 2018 working-paper title was *Core stability and core-like solutions for
three-sided assignment games*. Pages 11 and 13 were visually checked.
Section 2 gives the integral model, whole-core inequalities, and Lucas's
balancedness test; Example 1 is empty-core. Its extended compatible-subgame
core union differs from the entire core. The inspected text treats stable
sets, not full sorted-payoff selector distances.

**Lucas (1995), Core theory for multiple-sided assignment games**,
Duke Mathematical Journal **81**(1), 55–65.
[DOI](https://doi.org/10.1215/S0012-7094-95-08106-X).
Atay–Núñez prints volume 87; publisher-deposited Crossref metadata instead
confirms volume 81. The original publisher download returned an HTML block,
so the original full text was not inspected. Attribute the two conditions
to Lucas **as reproduced in Atay–Núñez**, rather than implying direct access
to Lucas's proof. Metadata is saved in `lucas_crossref.json`.

**Martínez-de-Albéniz, Rafels and Ybern (2020), Assortative multisided
assignment games: The extreme core points**, Games and Economic Behavior
120, 144–153, March 2020.
[DOI](https://doi.org/10.1016/j.geb.2020.01.001),
[university postprint](https://diposit.ub.edu/bitstreams/187fcb85-db7e-4ed2-950e-c293fcd99b76/download),
[university metadata](https://diposit.ub.edu/items/9c47c698-7a2a-4160-bd7f-f5be0fdde1ea).
The postprint was downloaded and its mathematical statements inspected.
The subclass requires supermodularity and coordinatewise monotonicity.
Theorem 2.1 supplies an optimal diagonal, a core description using adjacent
index triples, and within-sector payoff order. Theorem 3.1 describes every
extreme core point by paths. For m sectors and q agents per sector the
maximum vertex count is m(m!)^(q−1). Additive/valuation arrays have only m
vertices when the least diagonal value is positive. This is useful prior
structure for the additive calibration family, not an unrestricted-game
bound on fairness selectors. Neither the full sorted-payoff divergence
theorem nor exponential coordinate-sacrifice theorem was found here.

## Nearby results that do not settle this claim

**Atay and Núñez (2019), Multi-sided assignment games on m-partite graphs**,
Annals of Operations Research 279, 271–290.
[Publisher](https://doi.org/10.1007/s10479-019-03256-5),
[author PDF](https://ataatay.github.io/webpage/Atay_Nu%CC%81n%CC%83ez_2019_ANOR.pdf).
This graph-based model builds coalition values from underlying pair
weights. Cycle-free quotient graphs give strong balancedness and a core
description through underlying two-sided cores. Those hypotheses are a
substantive restriction; this cannot be used as a representation of arbitrary
nonnegative triple arrays.

**Tejada and Núñez (2012), The nucleolus and the core-center of multi-sided
Böhm-Bawerk assignment markets**, Mathematical Methods of Operations
Research 75, 199–220; online 24 March 2012.
[Publisher](https://doi.org/10.1007/s00186-012-0381-x),
[institutional PDF](https://www.research-collection.ethz.ch/server/api/core/bitstreams/4531c43d-aa5c-45b8-a007-4e6fc2c32e2b/content).
This source treats a specific homogeneous-goods subclass and reduces its
nucleolus and mass center of the core to a game on sectors. Its lexicographic
center orders **coalition excesses**, not player payoff coordinates. The
fact that two of its selected solutions may differ is not our quantitative
claim about leximin and leximax-min.

**De Loera and Onn (2006), All Linear and Integer Programs Are Slim 3-Way
Transportation Programs**, SIAM Journal on Optimization 17, 806–821.
[Publisher](https://doi.org/10.1137/040610623),
[2004 precursor author PDF](https://www.math.ucdavis.edu/~deloera/RECENT_WORK/ipcouniversality.pdf).
The universality theorem represents rational polytopes by three-way
**line-sum** transportation polytopes, with specified 2-margins. These are
not the matching-dual payoff cores used here. An additional realization
theorem would be required to transfer that universality, and still more
would be required to preserve full payoff selectors and normalized L1
distance. No such transfer was located in this audit.

**Vazirani's fair-assignment work and Gangam et al.**
[Vazirani](https://arxiv.org/abs/2402.11437),
[Gangam–Garg–Shahkar–Vazirani](https://arxiv.org/abs/2403.06037).
These are relevant motivations for payoff fairness. The former concerns
ordinary bipartite assignment games; the latter studies max-flow, MST and
b-matching games, with Owen-set selections. Their stated domains do not
include the unrestricted three-sided whole-core theorem.

## Reproduction of the published empty-core calibration

Use one-based indices, with layers indexed by k:

    A[:,:,1] = [[3,1],[2,5]],  A[:,:,2] = [[1,4],[5,4]].

Independent arithmetic: perfect-matching totals are 7,6,6,6, so the
diagonal is uniquely optimal. Lucas's tests read 10>=4 and 11>=14.
Triples 111,122,212,221 cover every player twice, with total weight 17;
the core inequalities require 2T>=17, contradicting 2T=14. Half-weight
on these four triples gives a fractional matching of value 17/2.

`verify_published_empty_core.py` independently enumerates these matchings,
checks the two inequalities, and checks the four-triple certificate using
only exact integer/rational arithmetic.

## Search boundary and novelty verdict

Queries included combinations of "three-sided assignment", "multi-sided
assignment", "multisided assignment" with "leximin", "leximax",
"lexicographic", "Lorenz", "egalitarian", "fairness", "exponential",
"coordinate", "recurrence", "representation", and "polytope". Searches
targeting the new claims specifically found no prior whole-core result with
normalized distance approaching 2 under bounded integer triple weights, and
no matching theorem about exponential loss relative to a player's core
maximum. Retrieved lexicographic results mainly concern excess-based
nucleoli or specified-player orders, which are different objectives.

The safe conclusion is **no matching prior theorem located in this bounded
audit**. It is not a proof of novelty. Remaining priority work includes the
full Quint and Lucas articles, citation-chain review, and specialist review.
No external messages were sent. The two new claims must remain separate:
coordinate sacrifice with coincident selectors does not prove global
selector divergence; the second construction must supply that conclusion.
