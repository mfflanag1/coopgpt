# CoopGPT paper index

Updated 6 October 2026. Eight focused manuscript candidates are listed below.
Completed manuscript means the exposition and PDF exist; it does not imply
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

[Current PDF](paper5/sharp_subsidy/output/pdf/manuscript.pdf) · [Source, audit, and verification package](paper5/sharp_subsidy/README.md)

High level: external money can restore a one-third guarantee of each participant's
best original stable payoff. The worst-case required subsidy is one third of
original surplus as a supremum; no finite market attains that ratio.

Technical: for strict three-sector nonnegative pair-additive markets with positive
integral worth and nonempty original entire core, S3=1/3. The direct fractional
proof combines six comparisons of individual maxima with residual budgets at
separate attaining core points. It also proves the sharp integral-obstruction
bound 2(k-1)T/[3(2k-1)] for k unmatched players per sector. A family with pair
values in {0,1,2} supplies sharpness, with full coordinate-attainment witnesses.

Status: ten-page self-contained manuscript, freshly audited by the coordinator
and Fable 5.1; notation, explanatory steps, and attribution disclosures repaired.
Portable exact checks include 3,603,804 full-team inequalities. Human specialist
validation and historical novelty remain pending. The prior
[theorem package](research_campaigns/2026-10-03-core-witness/sharp_result/SHARP_ONE_THIRD.md)
is its research archive, not an additional paper. This result supersedes the
former 1/3<=S3<=39999/100000 frontier.

### 8. Subsidies for truthful cooperation: sharp proportional bounds and nonlinear escape

**New theorem supplement:** [Unrestricted hierarchy result](research_campaigns/2026-10-06-unrestricted-attack/HIERARCHY_THEOREM.txt) and [review packet](research_campaigns/2026-10-06-unrestricted-attack/REVIEW_PACKET.txt). The preserved PDF below predates this result.

[Current PDF](paper5/truthful_cooperation/output/pdf/manuscript.pdf) · [Specialist brief](paper5/truthful_cooperation/output/pdf/specialist_brief.pdf) · [Source and verification package](paper5/truthful_cooperation/README.md)

High level: how much extra money is needed to keep every coalition satisfied
while preventing owners from gaining by hiding capacity? Proportional payments
need a growing budget; nonlinear payments avoid that obstruction on the exact
family used to prove it.

Technical: fixed-owner weighted multi-glove games admit an all-profile capped
continuous-Banzhaf rule with total factor O(log k/log log k). Every universal
constant must be at least 2. The floor-free capped-proportional minimax factor
is (1+o(1)) log k/log log k. Nonlinear rules have factor 2 on up to two altered
binary pools and factor 2m+3 on [1/r,1] with at most m altered equal-size pools.
The original H/k floor adds at most one. The new supplement now proves unrestricted growth of order log k/log log k,
with coefficient bounds1/2 and1, using growing owner and pool counts. It
supersedes the PDF's open-question statement; the PDF has not yet been revised.

Status: complete review manuscript consolidating the October 4–5 AGT results,
with exact portable checks and a fresh Fable 5.1 proof review. The established
game and Banzhaf functional are credited; novelty and human specialist
significance review remain unresolved. Outreach is prepared and unsent.
These extensions are one paper candidate, not multiple additional papers.

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
