# CoopGPT paper index

Updated 7 October 2026. Eight focused manuscript candidates are listed below.
The current LaTeX sources are authoritative; some PDF exports are historical. A completed draft does not imply
publication, confirmed novelty, or independent human endorsement. The current
structural paper replaces the earlier chain-cycle manuscript in this list.

## Current focused manuscripts

### 1. Acyclicity and simultaneous protection of individual core maxima

[Current PDF](paper5/graph_core_protection/output/pdf/manuscript.pdf) · [Source and verification package](paper5/graph_core_protection/README.md)

High level: the sector interaction graph determines whether stable allocations
can guarantee everyone a fixed fraction of their own best stable payoff.
Trees permit protection; cycles can defeat even the best choice of allocation.

Technical: under equal sector sizes, nonnegative pair matrices (zero matrices
allowed), productive full teams only, positive integral worth and nonempty
entire core, c(G)=R(G)=1/K for trees and zero for cyclic graphs. The source
triangle has an entire-core simplex of dimension 4q+2 and exact optimal
simultaneous fraction 1/(2q+3). The proofs combine tree cut coordinates,
clipping, a unit partial-matching budget and selective subdivision.

Status: consolidated technical manuscript, incorporating the former chain-cycle,
graph-classification and simultaneous-protection results. Scoped model review
and exact checks are documented in the package. Novelty and specialist review
remain qualified; no field-level breakthrough is established.

### 2. Sharp asymptotic separation of opposing egalitarian core selections

[Current PDF](review_packages/2026-09-05/asymptotic/output/pdf/manuscript.pdf) · [Package](review_packages/2026-09-05/asymptotic/README.md)

High level: two fairness rules can allocate almost all the same surplus to
different people; the paper determines the rate at which maximal disagreement
is approached as the population grows.

Technical: for singleton-normalized exact games with n players and
s_n=sup ||Lmin-Lmax||_1/T, the theorem is
2-s_n=2/n+O(log(n)/n^2), hence n(2-s_n) tends to 2. A universal compact-convex
constant-total overlap inequality matches a whole-core Fibonacci segment
construction for every sufficiently large n. Here Lmax minimizes descending
sorted payoffs; it does not maximize an individual's payoff.

Status: self-contained quantitative manuscript. Segment and Fibonacci ingredients
have prior precedents; the precise opposing-selector comparison is the candidate
contribution. Human specialist review and global priority remain unconfirmed.

### 3. Fair core selections: a sharp boundary between pairs and triples

[Current PDF](review_packages/2026-09-05/assignment/output/pdf/manuscript.pdf) · [Package](review_packages/2026-09-05/assignment/README.md)

High level: changing from pairwise cooperation to three-way cooperation sharply
increases how much two fairness rules can disagree.

Technical: graph matching games with nonempty core have sharp normalized
selector distance floor(n/2)/(floor(n/2)+1) for n>=4. Sparse strict three-sided
markets with bounded team values approach distance 2. Equal-sided complete
additive triples retain a 1/3 ideal guarantee and sharp distance supremum 4/3.
This paper permits arbitrary triple arrays, unlike the pair-additive restriction
in Paper 1 above.

Status: consolidated manuscript. Half-of-ideal guarantees have prior algorithmic
and matching-reduction antecedents. The finite distance comparison and sparse
triple family are the principal proposed contributions; original-source gaps remain.

### 4. Balanced transport at the egalitarian core: a complete boundary phase diagram

[PDF](paper4/threshold.pdf) · [Source](paper4/threshold.tex)

High level: determines exactly when a richer group's coalition constraint can
remain slack at the leximin allocation of an exact game.

Technical: with m poorer and h richer players, slack richer suffixes exist
exactly for m>=m_min(h), where m_min(1)=4, m_min(2)=m_min(3)=3 and
m_min(h)=2 for h>=4. The main proof uses tight-coalition normal-cone geometry,
balanced transport and explicit all-parameter realizing families.

Status: coherent structural manuscript; main theorem survived the portfolio
audit. Some auxiliary finite-certificate claims have narrower replay coverage.
Exact partitions and their Lorenz consequences have prior antecedents.

### 5. Boundary partitions at the leximin core: a two-parameter characterization

[PDF](paper6/partition.pdf) · [Package](paper6/README.md)

High level: identifies when two tight coalitions can divide all players across
a slack fairness boundary, with one richer player in each coalition.

Technical: the numbers p,q of poorer players on the two sides are feasible
exactly when p,q>=1 and p+q>=4. Necessity and sufficiency have closed-form
proofs and explicit constructions, including the (2,2) case that corrected
an earlier conjecture.

Status: completed specialized manuscript, naturally a companion to or section
of Paper 4 above. It should not be counted as an unrelated major research program.

### 6. Stable core without egalitarian stability

[Current PDF](review_packages/2026-09-05/stable_core/output/pdf/manuscript.pdf) · [Package](review_packages/2026-09-05/stable_core/README.md)

High level: stability of the core does not ensure that a procedural egalitarian
rule selects a stable allocation.

Technical: a six-player entire core segment is von Neumann-Morgenstern stable,
but final procedural claims sum to 13/2 against total worth 6. The manuscript
gives a direct stability proof and a three-regime additive ray. Six-player
minimality uses established low-player implications.

Status: focused manuscript, with downgraded novelty claims. Bare existence is a
short synthesis of classical ingredients; the explicit example and complete ray
are narrower worked-result candidates. The exact-game counterexample has earlier
precedent in Mauri's thesis and is not claimed new.

### 7. Sharp subsidies for protecting core maxima in three-sided assignment markets

[Current source](paper5/sharp_subsidy/manuscript.tex) · [Historical 3 October PDF](paper5/sharp_subsidy/output/pdf/manuscript.pdf) · [Source, audit, and verification package](paper5/sharp_subsidy/README.md)

High level: external money can restore a one-third guarantee of each participant's
best original stable payoff. The worst-case required subsidy is one third of
original surplus as a supremum; no finite market attains that ratio.

Technical: for strict three-sector nonnegative pair-additive markets with positive
integral worth and nonempty original entire core, S3=1/3. The direct fractional
proof combines six comparisons of individual maxima with residual budgets at
separate attaining core points. It also proves the sharp integral-obstruction
bound 2(k-1)T/[3(2k-1)] for k unmatched players per sector. A family with pair
values in {0,1,2} supplies sharpness, with full coordinate-attainment witnesses.

Status: the complete main theorem is retained, and all surviving static-protection extensions are now consolidated in appendices: general sector bounds, unit/quota flow, transportation-core comparison, endpoint incompatibility, sparse core representation, coattainment, perturbation instability and the finite cyclic-optimum obstruction. [Current consolidation record](review_packages/2026-10-07/consolidation/README.md). The old ten-page PDF predates these additions. Priority and human review remain pending.

### 8. Sharp subsidies for truthful production and network cooperation

[Current manuscript](paper5/truthful_cooperation/manuscript.tex) · [Main PDF](paper5/truthful_cooperation/output/pdf/manuscript.pdf) · [Indexed supplement](paper5/truthful_cooperation/supplement.tex) · [Two-page comparison](paper5/truthful_cooperation/output/pdf/specialist_brief.pdf) · [Review package](paper5/truthful_cooperation/README.md)

High level: preventing gains from hidden resources while protecting every coalition requires an external budget that grows with production complexity. The paper gives the sharp growth rate, including for ordinary simple directed networks.

Technical: over the class of finite nonnegative min-linear technologies with at most K fixed supporting forms, the optimal worst-case all-profile total-payment factor is **(1+o(1)) log K/log log K**. A capped own-excluded/endpoint hybrid proves the upper bound for every fixed technology; weighted report transitions through shared-fan networks give the matching simple-DAG lower with strategic auxiliary owners. The theorem permits arbitrary overlapping whole-owner resource bundles. The worst-case parameter uses at most K forms/cuts; it does not settle rates in owner count or resource dimension.

Further results include an O(n/log n) bound for all finite-valued monotone concave homogeneous production functions, resource-dimension bounds, exact finite sampling and all-profile certification, and the earlier sharp multi-glove hierarchy. Certification can require exponential preprocessing. Appendices consolidate the finite-pool mechanisms, network subclasses, monotone-envelope obstruction and scoped method boundaries; these do not inflate the paper count.

Status: focused nine-page Economic Theory candidate, 63-page indexed supplement and two-page comparison prepared locally on 14 October, with fresh PDFs, scoped independent audits and exact checks. A full-bundle scope error in an auxiliary example is repaired; the central theorem is unchanged. The [author decision sheet](paper5/truthful_cooperation/submission_2026-10-14/DECISION.txt) records remaining declarations and priority limits. The [October 7 campaign](research_campaigns/2026-10-07-six-hour-campaign/INDEX.txt) remains the research archive. Historical novelty, significance and human specialist assessment remain unconfirmed. No submission or outreach was sent.

## Broader archived manuscripts

- [Coalitional monotonicity and the core](paper/main.pdf): counterexamples to
  surplus-distributor and other proposed selectors, minimal family obstructions,
  and bounded exact-game feasibility. It does not resolve existence of a
  universally coalitionally monotone selector on all exact games.
- [Normalized Lmin on exact games](paper3/wrapper.pdf): four/five-player
  monotonicity and six/seven-player carrier thresholds, boundary geometry and
  later credal-set work. A large research archive; it overlaps Papers 4-5 and
  contains material with differing review coverage.
- [Maximal divergence of leximin and leximax](paper5/divergence.pdf): finite
  s_5=1/2 and s_6=2/3 results, equality classifications and the long PXC history.
  Contains superseded frontier language; Paper 2 above is the preferred
  presentation of the sharp asymptotic result.

## Earlier presentations, not extra independent papers

- [Original stable-core manuscript](paper2/main.pdf).
- [Original short asymptotic note](paper5/asymptotic_constant_two/output/pdf/sharp_asymptotic_separation.pdf).
- [Pairwise assignment note](paper5/assignment_separation/output/pdf/sharp_assignment_separation.pdf).
- [Three-sided assignment note](paper5/three_sided_separation/output/pdf/three_sided_separation.pdf).
- [Earlier assignment consolidation](paper5/assignment_comparison/output/pdf/pairs_and_triples.pdf).
- [Earlier chain-cycle manuscript](paper5/chain_cycle_separation/paper/manuscript.pdf),
  now incorporated into Paper 1 above.

The general graph and simultaneous-protection theorem notes are incorporated in Paper 1 and should not be counted as additional papers. Earlier portfolio and priority reviews remain in `portfolio_review_2026-09-05/REVIEW.md` and `review_packages/2026-09-05/priority_review/REVIEW.md`. The September affine coefficient and scalar no-go results remain in the historical sharp-subsidy audit; the scalar 29/82 barrier is not an actual market.
