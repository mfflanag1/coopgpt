# Three-sided assignment priority audit: follow-up

Audit date: **2026-09-05**. This addendum records new retrieval evidence and a
bounded assessment of priority. It does not certify novelty or replace specialist
review. Original Quint (1991) and Lucas (1995) full texts remain uninspected.

## Assessment

No inspected primary source states the sharp supremum of normalized L1 distance
between full sorted-payoff leximin and full leximax-min over nonempty entire
three-sided assignment cores, or the bounded-integer recurrence family proving
that supremum is two. No inspected representation theorem makes that conclusion
an immediate corollary without additional mathematical work.

This is stronger evidence than a keyword search alone: the known pair-additive
and ordered-supermodular subclasses can be separated from our family by explicit
structural obstructions below. It is still a bounded negative finding. Two
foundational original articles remain inaccessible, and no author has reviewed
our claims.

## Original-paper retrieval: what is and is not closed

**Thomas Quint (1991), The core of an m-sided assignment game**, Games and Economic
Behavior 3(4), 487–503, DOI
[10.1016/0899-8256(91)90017-9](https://doi.org/10.1016/0899-8256(91)90017-9).
The [author's publication list](https://www.thomasquintmath.com/publications)
contains the correct entry without a full-text link. The
[publisher abstract](https://www.sciencedirect.com/science/article/abs/pii/0899825691900179)
states the multisided extension, possible empty cores, and a sufficient balanced
subclass. [RePEc](https://ideas.repec.org/a/eee/gamebe/v3y1991i4p487-503.html)
explicitly restricts full text to ScienceDirect subscribers. Public publisher
retrieval returned HTTP 403. OpenAlex record W2045968762 reports closed access,
no OA URL, and no indexed repository full text. These facts establish the access
limit, not absence of a theorem in the paper.

**William F. Lucas (1995), Core theory for multiple-sided assignment games**,
Duke Mathematical Journal 81(1), 55–65, DOI
[10.1215/S0012-7094-95-08106-X](https://doi.org/10.1215/S0012-7094-95-08106-X).
The legitimate [Project Euclid record](https://projecteuclid.org/euclid.dmj/1077245461)
was identified via OpenAlex W2012117153, but returned a short blocking HTML page.
OpenAlex reports closed access and no indexed repository full text. A further
library route is *A Celebration of John F. Nash Jr.* (Duke University Press,
1996), ISBN 9780822317821. Its [Google Books contents](https://books.google.com/books/about/A_Celebration_of_John_F_Nash_Jr.html?id=iCH9EGj3YkEC)
list Lucas's chapter at page 77. The public preview HTML was retrieved, but no
readable chapter text was exposed; the linked accessible-text preview returned
HTTP 403. This is a retrieval lead, not an inspected reprint. The journal volume
is 81; the volume-87 citation in Atay's thesis and Atay–Núñez is inconsistent with
publisher metadata.

The preserved `quint_openalex.json`, `lucas_openalex.json`, and
`original_retrieval_log.json` make these limits reviewable. No purchase,
authentication workaround, paywall bypass, or external message was attempted.

## Citation-chain clarification of Quint and Lucas

Ata Atay's 2017 doctoral thesis, *Essays on multi-sided assignment markets*, is
available from the [University of Barcelona](https://diposit.ub.edu/server/api/core/bitstreams/1f199fe6-c683-45fd-add3-f32aecd56e10/content).
Printed page 18, Proposition 2.13, explicitly attributes the two 2x2x2
balancedness inequalities to Lucas, assuming an optimal main diagonal. Printed
page 19, Lemma 2.14, attributes to Quint a sufficient condition for pair-additive
arrays: pair weights satisfy a common convex-combination bound by diagonal pair
weights. Pages 19–20 distinguish Stuart's chain-additive class and Sherstyuk's
supermodular class. These are directly inspected statements in a later research
source; they do not substitute for inspection of the original Quint/Lucas proofs.
The previously inspected 2020 assortative paper also says Quint and Stuart give
nonemptiness results rather than a full core characterization for those models.

The thesis's rendered summation index in Lemma 2.14 appears to exclude the last
sector despite its prose referring to all pairs. Avoid copying that index as if
it were checked against Quint's original article.

## A relevant 2026 primary paper absent from the first audit

F. Javier Martínez-de-Albéniz, Carlos Rafels, and Neus Ybern,
*Maximum and minimum core payoffs for supermodular multisided assignment markets
with local monotonicity*, Discrete Applied Mathematics 379 (2026), 605–612,
DOI [10.1016/j.dam.2025.10.006](https://doi.org/10.1016/j.dam.2025.10.006),
[open publisher PDF at UPC](https://upcommons.upc.edu/server/api/core/bitstreams/fcec9d22-f4b5-4826-a5d4-d7e585b218cb/content).
Online publication was 14 October 2025; the issue date is 30 January 2026.
The whole eight-page paper was downloaded and relevant statements inspected.

Theorem 3.1 (p. 608) supplies a core allocation under supermodularity and local monotonicity (4).
Theorem 3.2 (p. 609) applies to an n-square multisided supermodular assignment
market satisfying (4). It gives explicit formulas for every coordinate maximum
and minimum. Precisely the consequence used below is: for each sector k there
exists a core allocation attaining every agent's coordinate maximum in sector k,
and another attaining every coordinate minimum in that sector. The allocations
may depend on k. Remark 3.2
and Examples 3.2–3.3 (p. 610) explain nonuniqueness of such sector-optimal
allocations and the need for local monotonicity. These are coordinate extrema
under substantive array restrictions, not full sorted-payoff selectors.

## Direct separation from known array classes (our deductions)

These deductions concern the proved shifted recurrence family; they are not
claims attributed to the sources.

1. **The array is not pair-additive.** In the subarray with sector coordinates
   A=(G0,U[0,0]), B=(G1,V[0,0]), C=(G2,D[0,0]), the nonzero entries, using binary
   indices, are w111=2, w110=2, w100=1. Every other corner is zero. The third
   mixed difference is therefore

       w111-w110-w101-w011+w100+w010+w001-w000 = 1.

   For every representation wabc=fab+gac+hbc, that difference is zero by
   cancellation. Thus neither arbitrary pair weights nor a chain/tree of
   pair weights can generate this array. Permuting sector labels or player
   labels does not remove the obstruction. In particular, our family is outside
   the pair-additive classes discussed in Quint, Stuart, and the related graph
   models.

2. **For L>=2 the core fails sectorwise simultaneous maximization.** Its entire
   core has q0>=0 and qL=(J-I)^L q0. Because (J-I)^2=J+I, every entry of
   (J-I)^L is strictly positive for L>=2. Any top V coordinate achieves its
   maximum 1 only if q0=0. Every sector also contains a root U coordinate
   1+q0_i whose core maximum exceeds 1: a sufficiently small positive uniform
   q0 is feasible. Hence no allocation simultaneously maximizes all coordinates
   of any sector. Theorem 3.2's consequence therefore fails for this family,
   ruling out representation of its array as supermodular with local
   monotonicity under any relabeling within or between sectors.

These obstructions explain why the new construction is not obtained merely by
substituting parameters into the inspected sufficient subclasses. They do not
exclude every possible indirect implication of old work.

## Representation and universality audit

**De Loera–Onn.** The inspected author version,
[All Rational Polytopes are Transportation Polytopes and all Polytopal Integer
Sets are Contingency Tables](https://www.math.ucdavis.edu/~deloera/RECENT_WORK/ipcouniversality.pdf),
Theorem 1 (PDF p. 2), represents rational polytopes by slim r-by-c-by-3
transportation polytopes with fixed line sums (2-margins). Its representation
is a bijective coordinate-erasing projection, and also preserves integer
points. This precedes the 2006 SIAM article listed in the original audit.

Our inference: three further steps would be required for the current claim.
First, those are primal feasible polytopes with specified 2-margins, whereas
our payoff core is an optimal dual face for a matching problem with unit
individual capacities. Second, any conversion must produce the entire core of
a standard integral three-sided assignment game, with the required matching
certificate. Third, added coordinates and normalization must preserve the two
full sorted-payoff selectors and their normalized L1 separation. A polytope
isomorphism or projection alone gives none of those selector invariances. We
located no primary source supplying all these steps.

**Streekstra–Trudeau (2022).**
[Stable source connection and assignment problems as multi-period shortest path
problems](https://www.sdu.dk/-/media/files/om_sdu/institutter/ivoe/disc_papers/disc_2022/dpe8_2022.pdf),
SDU Discussion Papers on Economics 8/2022, manuscript dated 15 July 2022.
Theorems 2–3 (printed pp. 10–11) represent all zero-normalized totally balanced
value games as multi-period shortest-path cost-saving games. Theorem 6
(p. 21) represents strict multisided assignment games satisfying the Stuart
condition in that shortest-path class; Corollary 3 proves total balancedness.
These implications run into the shortest-path model, not from arbitrary
polytopes or games into three-sided assignment games. Combining them does not
supply the missing reverse implication or selector preservation.

**Generalized three-sided markets.** Atay's thesis, Chapters 3–4, studies
additional singleton and pair values, reduced/derived games, and graph-based
composition. Such models contain or extend the strict class, but an extension
of a game class is not a universality theorem for the strict subclass. Likewise,
core selections for coalitional excesses or externally fixed player orders are
not full sorted-payoff leximin/leximax-min.

## Recommended claim and remaining review request

Use: “We prove the sharp supremum is two for nonempty entire cores of standard
three-sided assignment games, already with weights in {0,1,2,3}. The result is
not a consequence of the inspected pair-additive and ordered-supermodular
subclass descriptions. No matching prior theorem was located in our dated,
bounded search.”

Do not use: “first,” “previously unknown,” “field-level breakthrough,” or
“complete novelty verification.” The next external review should explicitly
request comparison against Quint (1991), Lucas (1995), and any
selector-preserving realization theorem for three-sided assignment cores. The
full texts of those first two papers are still the concrete access gap.

## Exact exclusion checks

`verify_priority_exclusions.py` reads the durable raw family generator and checks
the eight displayed cube entries, the nonzero third difference, positivity of
(J-I)^L, and a raw feasible core witness with every root U greater than one.
All checks passed for L=2,3,4,8; results are in
`priority_exclusion_checks.json`. The finite checks support the conventional
all-parameter deductions above and do not replace them.
