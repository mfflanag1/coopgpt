# Assignment package: independent first-principles mathematical review

Date: 5 September 2026. Scope: only the supplied assignment package. The package was read without modifying it. All checks and replay outputs are in this scratch directory. Earlier PASS statements were treated as unproven. No outreach, PDF generation, or broad novelty search was performed.

## Assessment

**No counterexample, central mathematical error, or missing substantive hypothesis was found.** I independently reconstructed the graph bound, sharp examples and player-count cases, the raw three-sided entire core, both full selectors, the asymptotic and finite-dimension conclusions, the additive benchmark, and the unshifted control. The proofs survive their difficult cases: fixed zeros, nonbipartite tight edges, alternate optimal matchings with different positive-edge counts, asymmetric recurrence roots, L=1, R=0, m=1, S=0, and unequal sector sizes introduced by padding.

The computational evidence is stronger than a replay: a fresh sorted-rank/permutation formulation checked 792 positive nonempty graph cores among 842 inputs; 14 fresh raw triple cases and eight additive cases were independently certified. These checks support the proofs but do not formalize them.

There are **no blocking mathematical findings**. The small clarifications below would improve an external reviewer's reading; none changes a result.

1. The definition of the two full selectors at manuscript lines 52–60 presumes the usual existence/uniqueness fact for compact convex feasible sets. It is valid here. A one-sentence convexity justification would make the paper self-contained at this point.
2. In the covering allocation at lines 244–246, explicitly say that both G and D receive zero. The manuscript has introduced G as “global players” before subsequently calling them dummies. The later proof removes any mathematical ambiguity.
3. The source-based algorithmic deduction at lines 424–438 should be read in the source's rational-input domain, including the initial allocation. If “arbitrary core point” is intended to include irrational coordinates for rational weights, add a density/continuity sentence or rely on the elementary proof already supplied. The elementary theorem has no rationality restriction.
4. The third-difference calculation excludes pair-additive representations of the actual array, including ordinary dummy lifts, and is invariant under permutations. It does not exclude every nonlinear or coordinate-changing game representation; the caveat at lines 410–411 correctly limits that inference. Preserve it.

## Proof obligations

All manuscript anchors below refer to [the exact reviewed manuscript](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex).

### O1. Integral worth and the team-inequality description of the entire core — valid

**Anchors:** lines 39–50, especially [equation (1)](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:43).

For each coalition S, sum the team inequalities over an optimal integral matching inside S. Disjointness and nonnegativity imply p(S) is at least that matching's weight. Conversely, a core allocation satisfies every team inequality because that team is a feasible matching in its own coalition; singleton constraints give nonnegativity. Efficiency uses the integral grand-coalition value T. This proves exactly the displayed core, without confusing the fractional matching optimum with T. It works for arbitrary finite hypergraphs with nonnegative weights; nonemptiness is separately needed. Removing or inserting zero-weight teams changes neither worth nor the constraints, because their inequalities follow from nonnegativity.

### O2. Full selectors and fixed zeros — valid, standard auxiliary fact implicit

**Anchors:** [lines 52–60](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:52), 139–141, 292–309.

C is a nonempty compact convex subset of the simplex. Successively maximize the minimum over the coordinates not yet fixed. At the optimal floor at least one such coordinate is fixed at that floor throughout the optimal face: otherwise, average one feasible improvement witness per coordinate to raise them all. Freeze precisely those forced coordinates and continue. The procedure fixes every label in finitely many stages, giving the unique full ascending leximin vector. Reverse inequalities for descending lexicographic minimization. Thus sorted vectors do not create an unresolved labeling ambiguity.

Appending fixed zeros prepends identical entries to the ascending order and appends identical entries to the descending order. It cannot affect the remaining full selector. A first-stage maximin point with zeros would not suffice, as the package's negative control correctly shows.

### O3. Matched-edge equality and fixed unmatched vertices — valid

**Anchors:** [lines 118–120](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:118), 130–131.

Delete zero-weight edges from an optimal matching. The remaining positive edges still total T. Their lower bounds sum to T, while all other payoffs are nonnegative and the total is T. Therefore every selected edge is tight and every vertex outside those positive edges is zero in every core allocation. This also covers endpoints of zero-weight edges in the originally chosen matching. The argument is valid for each optimal matching, even when optimal matchings have different numbers k of positive edges.

### O4. Graph half-domination, including general graphs — valid

**Anchors:** [Lemma 1 proof, lines 126–148](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:126).

Fix y in C and an increasing coordinate a with delta=y_a-x_a>0. Changes on selected matching edges are opposite; all other changes are zero. Hence A={d>=delta} and B={d<=-delta} have equal cardinalities, paired by the matching. If a tight graph edge has an endpoint in B, its other endpoint must be in A: otherwise d_u+d_v<0 contradicts feasibility of y. This rules out a B–B tight edge as well as a B–outside edge, so h=1_A-1_B harms no tight inequality in a nonbipartite graph either.

For decreasing vertices, x_i>=delta. Choosing epsilon below delta, every relevant positive edge-slack divided by at most two, and the gap between the smallest affected increasing payoff and the smallest decreasing payoff gives an actual feasible step. If min_B x>min_A x, this step strictly improves the first changed rank in the ascending sorted vector. Lower unaffected payoffs, including fixed zeros, remain an identical prefix. Leximin therefore forces delta<=min_B x<=min_A x<=x_a. Thus y_a<=2x_a.

For every coordinate, min(x_i,y_i)>=y_i/2. Summing gives overlap at least T/2 and normalized distance at most one. No bipartition or rationality assumption was used. A single positive edge has x=(T/2,T/2), H=(T,T), proving the fraction sharp.

### O5. The strengthened finite graph bound for every minimax point — valid

**Anchors:** [lines 157–182](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:157).

For each matched pair, let q_i be the absolute displacement, D=sum q_i, M=max z>0. The decreasing endpoint has x>=q_i by z>=0; the increasing endpoint has x>=q_i by O4. Its z is consequently at least 2q_i, so q_i<=M/2. Hence s_i>=2q_i and D<=kM/2.

There must be a z-maximum endpoint a with x_a>=M. If all z-maximum endpoints decreased toward x, the finite gap below M at all other endpoints permits a sufficiently short convex move lowering the maximum, contrary to minimax. The selected pair containing a has x_a=M+q_p, and its partner has x>=q_p. Its pair sum therefore obeys s_p>=M+2q_p. Summing gives T>=M+2D>=2D(1+1/k), or 2D/T<=k/(k+1). This argument requires only first-stage minimax optimality of z and covers D=0. It does not assert the finite improvement against arbitrary core points; the package correctly includes a counterexample to that stronger false statement.

### O6. k=1, finite-n sharpness, and every-player accounting — valid

**Anchors:** [lines 184–206](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:184).

When k=1 all remaining vertices are fixed zero. The two nonzero-capable payoffs range over a closed interval with constant sum T. Their minimum is T minus their maximum, so the split nearest equality uniquely optimizes both selectors. Consequently n=2 and n=3 have maximum distance zero. There is no positive-T pair game with n=0 or n=1; the theorem appropriately supplies no extremum there.

For k>=2, the identical-row matrix with columns (1,...,1,2) has integral optimum k+1. Every edge occurs in an optimal perfect matching, so every edge is tight on the entire core. Thus all row payoffs equal t, column payoffs equal c_j-t, and 0<=t<=1. Since k>=2 there is a column of weight one: the minimum is min(t,1-t), uniquely optimized at 1/2. The maximum is 2-t, uniquely minimized at 1. All 2k labels change by 1/2 and rho=k/(k+1). An isolate gives the odd-n examples. Monotonicity of k/(k+1) and k<=floor(n/2) completes the exact formula. The restriction k>=2 is necessary in the attainment construction and is stated.

### O7. Three-sided coloring, weights, counts, and integral certificate — valid

**Anchors:** [lines 211–249](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:211).

At an even current level, U has color i and the preceding odd-level V players with indices j,k have colors j,k. At an odd current level, U has color i+1 and the preceding even-level V players have colors j+1,k+1. The reverse recurrence triples have the complementary argument. Local/global and copied cross-triples also contain exactly three distinct colors. All positive teams are distinct by their player labels. Counts are 6(L+1)+3+6L+12R=12(L+R)+9 teams, 9(L+R+1)+3 players, and 3(L+R)+4 per sector.

The local D-triples are disjoint and total 6+3L+3R. The specified z allocation covers every team: the forward recurrence covers with two V payoffs; the reverse root recurrence has 1+1+1=3; later reverse recurrences cover with the current V payoff; the copy equalities cover with a V. Total payoffs equal the matching weight T. Therefore weak covering/matching comparison proves the integral optimum and a nonempty entire core; it does not assume fractional integrality in general triple markets.

### O8. Entire sparse triple core, including asymmetric roots — valid in both directions

**Anchors:** [Lemma 2, lines 253–282](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:253).

Equality in the local matching forces every G to zero and each local triple to its designated total. Replacing D by the zero G forces D=0. Root anchor teams impose U_0>=1. Write U_0=1+q_0,V_0=1-q_0 and U_l=q_l,V_l=1-q_l thereafter. Forward recurrence constraints give q_li>=q_(l-1)j+q_(l-1)k. At l=1 the reverse weight three exactly cancels the two root offsets; at later levels reverse weight one gives the same opposite inequality. Copied cross-teams give both q'_ri>=q_Li and q'_ri<=q_Li. Nonnegativity gives every q between zero and one.

Conversely, these unrestricted three root variables, recurrence identities, bounds and copied identities satisfy each raw inequality, nonnegativity and efficiency. Therefore they describe the entire core, rather than a symmetric subcore, an optimal dual face at a wrongly chosen fractional value, or only a collection of candidate allocations. A small positive uniform root vector has a full neighborhood inside the bounds, so the resulting core really has dimension three.

### O9. Shifted triple full minimax selector — valid and unique already at its first stage

**Anchors:** [lines 286–290](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:286).

Root U payoffs are at least one, and z has maximum one. Every point with maximum at most one must set each U_0 to one, so q_0=0. O8 then fixes every coordinate. There is no unexamined later descending-lexicographic stage.

### O10. Shifted triple full leximin selector and uniqueness — valid, including L=1 and R=0

**Anchors:** [lines 292–310](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:292).

Exactly G,D are fixed zero: q_0=t(1,1,1), 0<t<2^-L, gives all remaining players positive. For a common positive floor eta, sum q_1>=3eta and sum q_L<=3(1-eta), with sums respectively 2 sum q_0 and 2^L sum q_0. Thus eta<=2/(2^L+2). Uniform roots t=1/(2^L+2) attain it at every required coordinate: the smallest nonroot U is 2t; the smallest V is the top V, equal to 2t; roots and copies satisfy the same floor.

At equality the two sum bounds leave no slack, so each of the three q_1 coordinates equals eta. The matrix J-I is invertible (eigenvalues 2,-1,-1), forcing uniform q_0. The first positive-floor face is a singleton, proving the full selector without assuming symmetry. For L=1 the same argument is simply q_1>=eta and q_1<=1-eta with eta=1/2; it remains unique. Copies and R=0 do not affect this reasoning.

### O11. Distance, individual failure, and sharp supremum two — valid

**Anchors:** [lines 312–325](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:312).

There are three pairs per level, each contributing 2·2^l t, and three copied pairs per replication contributing 2·2^L t. This gives the displayed numerator and, after division by T, exactly rho(L,R). In particular rho(4,16)=287/198>4/3. With R=L^2, the factors 2^L/(2^L+2) and (R+2)/(L+R+2) tend to one, yielding rho→2. Nonnegative allocations of the same total never have distance above 2T.

Top V is at most one by the entire-core form, reaches one at z, and equals 2/(2^L+2) at x. This separately proves the lack of a positive dimension-independent individual guarantee. It does not rely on large distance implying individual loss.

### O12. All-n padding and the logarithmic deficit — valid

**Anchors:** [Proposition 1, lines 327–346](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:327).

For n>=30, k=floor((n-12)/9)>=2, L=ceil(log_2 k)>=1 and L<=k, so R=k-L>=0. The unpadded game has 9k+12 players; zero to eight extra players can be assigned arbitrarily to sectors. The old grand coalition still has worth T, and efficiency/nonnegativity force every new player to zero. Thus both full selectors and T are unchanged. Allowing unequal sector sizes is explicitly part of the proposition.

Writing a=2^L and k=L+R, subtraction gives 2-rho=2La/((a+2)(k+2))+4/(a+2)+2/((a+2)(k+2)). Since a>=k, the displayed bound follows term by term. It bounds 2-S_n because S_n is at least the constructed rho and at most two. The O(log n/n) statement is then immediate.

### O13. Complete equal-size additive benchmark — valid, including signed coefficient representations

**Anchors:** [Proposition 2, lines 351–377](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:351).

Subtract sector coefficient minima to get offsets b_si>=0 and total minimum S. Nonnegativity of the complete array gives S>=0 even if an original coefficient representation has negative entries. Every perfect matching uses every player once and has total T; every team belongs to one. Every team inequality is consequently tight in the core. Subtracting equalities for teams differing in one sector proves p_si=b_si+t_s. Each sector has a zero offset, giving t_s>=0; the team equalities give sum t_s=S. Conversely these constraints make every team tight and give total T=sum b+mS.

The minimum payoff is min_s t_s, so t_s=S/3 is the unique first-stage maximin solution; for S=0 the whole core is a singleton. H_si=b_si+S<=3x_si. Also ||x-y||_1=m sum|t_s-S/3|<=4mS/3<=4T/3. This is an all-core-point bound, stronger than a bound only against the other selector.

For m>=2, the specified sharp family has nonzero offsets in one player of each of two sectors, transferable shift S=1 and T=m+2. A ceiling of one forces t_1=t_2=0 and t_3=1, uniquely. Its distance is 4m/[3(m+2)] and tends to 4/3. An offset-zero coordinate with S>0 attains individual ratio 1/3 exactly. The m>=2 restriction on the distance example is essential and present; the general theorem also covers m=1.

### O14. Unshifted individual-loss control — valid

**Anchors:** [lines 380–389](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:380).

After the stated modifications all pair totals are one, no root anchors remain, and both recurrence inequalities still force q_l=(J-I)^l q_0 with bounds [0,1]. A floor eta yields sum q_0>=3eta and 2^L sum q_0<=3(1-eta), so eta<=1/(2^L+1). A ceiling M yields sum q_0>=3(1-M) from root V and 2^L sum q_0<=3M from top U, so M>=2^L/(2^L+1). Equality forces each root coordinate to 1/(2^L+1), fixing both full selectors. The feasible root-zero vector gives H_topV=1, so the individual ratio tends to zero while rho=0. This also works for L=0 as an auxiliary check.

### O15. Source-class exclusions — valid within the stated scope

**Anchors:** [lines 392–411](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:392).

The identified cube has only entries 111=2,110=2,100=1 nonzero. The third mixed difference is 1. Every sum of pair functions has third mixed difference zero by direct cancellation; permutations merely relocate the witness.

For L>=2, (J-I)^2=J+I has strictly positive entries, and multiplication by J-I preserves positivity. A top V reaching one therefore forces q_0=0, since all roots are nonnegative. A root U in the same sector can exceed one at a small positive uniform root vector. Thus sectorwise simultaneous attainment of all maxima fails in every sector, irrespective of permutations. The primary Theorem 3.2 indeed requires equal sector sizes, supermodularity and local monotonicity and concludes simultaneous maxima within a sector. The contrapositive is applicable to this equal-size family. It excludes the conjunction of hypotheses, rather than proving absence of supermodularity alone.

### O16. Pairwise equality, exact games and source-based half corollary — mathematically supported

**Anchors:** [lines 414–438](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/manuscript.tex:414).

The equality assertions can be independently justified. Averaging endpoints within each chosen matched pair is a doubly stochastic averaging operation; if that equal-pair vector is feasible, it Lorenz-dominates every core point and both selectors choose it. Exactness implies every singleton can reach its standalone value zero. For an edge joining distinct selected pairs, minimizing each endpoint in turn gives w_uv<=min(s_u,s_v), so pairwise equal splits cover it. Edges to fixed-zero unmatched vertices must have weight zero by exactness of the matched singleton. Hence exact assignment games have feasible pairwise equal splits and coincident selectors. In the sharp pair and shifted triple families a stated singleton has core minimum one but worth zero, proving nonexactness.

The source-based half estimate follows by integrating speed at most one until a coordinate becomes permanently fixed; the active/bin floor invariant gives its final payoff at least the freezing clock, and permanent components subsequently do not move. Initially fixed coordinates are separate. Direction reversals and temporary returns to Bin do not break the absolute total-displacement bound. The elementary proof O4 supplies real-weight generality independently of the source.

## Verification review

### Existing implementation semantics

- [exact_assignment.py:28](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/verification/exact_assignment.py:28) and [exact_three.py:26](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/verification/exact_three.py:26) demand exact SAT and rational/integer objective values. Unbounded or infinitesimal optima fail conversion; UNKNOWN and UNSAT fail immediately. Their selector routines at lines 37–51 and 35–49 implement O2 correctly. Omitting old common-floor inequalities from the next stage is safe because the previous optimal face remains feasible, so the next optimum is monotone and restores at least those bounds.
- These two implementations are essentially the same algorithm, **not independent corroboration of each other's logic**. README lines 49–51 accurately disclose this. [verify_independent.py:22](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/verification/verify_independent.py:22) supplies the separate sorted-improvement formulation for all 255 bounded pair matrices.
- [verify_independent.py:131](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/verification/verify_independent.py:131) verifies the fixed-zero set and the singleton positive-floor and minimax faces, which suffices for full triple selectors. Lines 141–164 check both entire-core inclusions without restricting roots to be equal. The older second-generator check alone proves only one inclusion, but the independent file supplies the other.
- [verify_extensions.py:13](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/verification/verify_extensions.py:13) computes integral graph worth recursively, includes every coalition, checks individual maxima, and queries all minimax points. The original six graph cases are targeted examples, not an exhaustive general-graph census. The README says this accurately.
- [verify_assignment_theorem.py:11](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/assignment/verification/verify_assignment_theorem.py:11) uses the smallest positive-edge count among optimal bipartite matchings, which checks the strongest applicable bound. Its all-minimax query is limited to n<=8 and the README labels that scope.
- Zero triple teams are omitted in large raw checks only where nonnegativity makes their inequalities redundant. The matching/cover certificates precede selector calculations. For small triple arrays, the dynamic program considers leaving a first-sector player unmatched as well as every feasible team; it computes the integral value, not a relaxation.
- All inspected SAT/UNSAT proof gates have the correct polarity and reject UNKNOWN. No Python assert is used for acceptance; runner children execute under -O. Some feasibility solvers lack their own timeout but the enclosing child-stage timeout bounds them and fails the run on timeout.
- The 987 original padding checks validate integer counts and rational formulas; they are not 987 distinct raw-core SMT padding constructions. README calls them “player-padding counts,” accurately. The manuscript's full padding argument is needed.
- No in-package independently checked proof certificate or different solver kernel protects every Optimize answer. Exact rational arithmetic and exact status handling are not a guarantee against solver implementation bugs. The package acknowledges this. The parent review is separately assessing another backend and runner startup/stale-output behavior; this review does not duplicate those findings.

### Fresh evidence produced in this review

1. **Full scratch replay:** [replay.log](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/replay.log); [fresh summary](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/replay_verification/results/verification_summary.json). All eight stages passed, regenerating their output files in the scratch copy.
2. **Independent graphs and triples:** [independent_audit.py](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/independent_audit.py), [results](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/independent_audit_results.json), [log](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/independent_audit.log). No package generator or selector is imported. Graph ranks are represented by a bijective permutation of labels, optimized lexicographically, then independently queried for attainment, absence of strict sorted improvement, labeled uniqueness, half-bound violation, and a distance violation by any minimax point. All graph worths use explicit integral matching dynamic programming and full coalition constraints.

   | Inputs | Total | Positive nonempty | Empty core | Zero T |
   |---|---:|---:|---:|---:|
   | Every 2-vertex weighting in 0–3 | 4 | 3 | 0 | 1 |
   | Every 3-vertex weighting in 0–3 | 64 | 48 | 15 | 1 |
   | Every 4-vertex weighting in 0–2 | 729 | 696 | 32 | 1 |
   | Rational cover-certified 5-vertex cases | 30 | 30 | 0 | 0 |
   | Rational cover-certified 6-vertex cases | 15 | 15 | 0 | 0 |
   | **Total** | **842** | **792** | **47** | **3** |

   The maximum observed rho for n=2,3,4 was respectively 0,0,2/3. Larger targeted rational samples were not designed to attain the bound. The raw triple cases were shifted (L,R)=(1,0),(1,4),(2,0),(2,3),(3,1),(4,16),(5,7),(8,2),(12,0), and unshifted L=0,1,2,4,7 with R=0. Every case passed the independent raw covering/matching, both core inclusions, singleton selector faces and ideal-payoff queries; shifted L>=2 cases also passed sector-exclusion queries. Maximum size was 192 players.
3. **Additive and padding:** [additive_padding_audit.py](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/additive_padding_audit.py), [results](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/additive_padding_results.json). Eight raw complete additive cases include m=1, S=0, signed original coefficients with nonnegative team values, and sharp families m=2,3,4,8. Both core inclusions, the unique leximin floor, ideal-payoff bounds and witnesses, all-core distance bound, and sharp-family unique minimax were checked. A further 9,995 player counts include every n=30,...,10000 and values around powers of two through exponent 200; the deficit identity and inequality held exactly.
4. **Fault injection:** [fault_injection.py](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/fault_injection.py), [results](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/assignment/fault_injection_results.json). Under Python -O, all 16 injected bad outcomes were rejected: Optimize UNKNOWN/UNSAT in both wrappers, unbounded values, infinitesimal unattained optima, inconsistent constraints, UNKNOWN feasibility/violation queries, and wrong SAT/UNSAT polarity. These test the acceptance gates, not immunity to an arbitrarily dishonest solver kernel.

## Limited primary-source recheck

[Vazirani's inspected v6](https://arxiv.org/html/2402.11437v6): re-read Definition 19, clock initialization, component update/fixing discussion, Remark 1, Lemmas 5 and 9, and Theorem 8. They support the algorithmic-deduction ingredients described in O16. Its rational-input convention is explicit. This is a deduction from the source, not a located explicit half-bound theorem. I did not attempt to re-prove the entire source algorithm or certify priority.

[Martínez-de-Albéniz, Rafels and Ybern, Theorem 3.2, printed p.609](https://diposit.ub.edu/server/api/core/bitstreams/82079683-149e-4510-a3a4-5cc1e1c57c65/content): the primary repository PDF's indexed text exposed the theorem, its hypotheses, the simultaneous-sector conclusion, and proof. Direct web opening of both repository PDF URLs failed during this review; this is therefore a theorem-text recheck through primary-source indexing, not a newly downloaded/full-PDF inspection. The exact consequence used at manuscript lines 403–410 is supported. No broader source-class or novelty conclusion was inferred.

## Confidence and residual limitations

**High confidence in the mathematical correctness of the central claims as stated**, based primarily on the reconstructed proofs and secondarily on the fresh exact checks. The finite graph correction, asymmetric whole-core triple derivation, and full-selector uniqueness arguments received the most scrutiny and have no unresolved logical step beyond standard compact-convex selector facts.

This is an AI-assisted internal audit, not an external expert sign-off or proof-assistant formalization. Z3 is shared by the package and these new checks; the new formulations reduce common modeling/algorithm error but not all common solver risk. The recent source theorem was rechecked through primary indexed text only. Original inaccessible legacy papers remain a priority/source-attribution limitation, not a dependency of the elementary central proofs. No conclusion about novelty, empirical relevance, arbitrary perturbation robustness, or models with capacities greater than one is warranted by this review.
