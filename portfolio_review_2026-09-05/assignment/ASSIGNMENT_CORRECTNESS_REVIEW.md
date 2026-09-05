# Fresh hostile correctness review: assignment portfolio

5 September2026. Scope: current assignment_separation, three_sided_separation and assignment_comparison manuscripts and their exact-verification code. Originals were read and hashed, then copies were used for all executions. No original file was edited. This is a new review from current files, not a reuse of prior review conclusions.

## Verdict

No counterexample or load-bearing mathematical defect found in the central pairwise finite theorem, three-sided construction, additive corollary, or consolidated boundary statement. The entire-core characterizations and full-selector arguments survive a fresh independent encoding. This is strong internal correctness evidence, not external verification, formal proof-assistant certification, or priority certification.

One minor local wording defect occurs in the consolidated subclass-exclusion paragraph: it says the root U maximum above1 is "attained at a small positive feasible q0." The small positive witness proves H_U>1; it generally does not attain H_U. For L=2, the suggested uniform q0=1/8 gives root payoff9/8, while q0=(1/2,0,0) is feasible and gives that root payoff3/2. Replace with "has maximum greater than one, as witnessed by a small positive feasible q0." The exclusion proof only needs H_U>1, so the conclusion and central theorem are unaffected.

## What was checked mathematically

- Common model: unit-capacity integral matching games, positive T, entire nonnegative efficient core, full ascending leximin and full descending lexicographic minimum. Arbitrary graph cores are explicitly required nonempty; bipartite cores are automatically nonempty. All fixed zeros count toward n.
- Graph half domination: the global positive/negative threshold sets are bijected by any fixed positive optimal matching; tight edges cannot lose payoff under the threshold transfer. Full lexicographic optimality, rather than an arbitrary first maximin point, supplies the bound. No bipartition is needed. Zero-weight matching edges can be deleted; efficiency then fixes all remaining unmatched players to zero.
- Finite graph distance: the proof controls every minimax allocation, not just a selected face representative. The maximum-coordinate witness produces the extra term M in T>=2D+M. The k=1 interval case and all odd/even n lower examples are correctly separated.
- Exact TU games: singleton exactness is stronger than merely using the entire core. The extremal examples are nonexact, so they do not contradict the separate exact-assignment equality result. Exact rational computation is a different use of "exact."
- Triple construction: valid sector coloring at every parity; no duplicated specified teams; n=9(L+R)+12, equal sector size3(L+R)+4 and positive-team count12(L+R)+9. A disjoint integral matching and a feasible cover with the same T=3(L+R+2) establish the actual integral optimum and core nonemptiness.
- Entire triple core: zero globals follow from matching efficiency, zero local dummies from alternative pair triples, shifted roots from anchor inequalities, and recurrence/copy identities from paired opposite inequalities. The converse holds for arbitrary asymmetric roots, not only the selected symmetric point.
- Full selectors: all non-dummy coordinates can simultaneously be positive. The first nonfixed leximin floor is bounded by the level1/topV sum inequalities and has a unique optimal face. Minimax also has a unique optimal face from the root lower bounds. Therefore the displayed points are full selectors, not merely first-stage choices.
- Triple distance and asymptotics: the pair-change sum, n counts, exact rho formula, L>=1 and R>=0 domain, R=L^2 limit and all-n padding bound check. No sharp finite-n formula or sharp deficit rate is claimed.
- Additive equal-sector corollary: the complete core is the shift simplex after subtracting sector minima. It yields the individual1/3 guarantee and distance at most4/3 to every core point. The attaining selector family now correctly includes m>=2. Its supremum is asymptotic; constant-value examples attain farthest-core distance4/3 while the two selectors coincide.
- Subclass exclusions: the displayed third mixed difference is1, so it excludes pair-additive representations on these player coordinates. Positivity of (J-I)^L for L>=2 proves the sector-maxima incompatibility, conditional on the accurately cited source theorem. It does not prove priority against every representation or alternative model.

## Fresh computational evidence

1. Recomputed all255 nonzero2x2 matrices with weights0..3, then re-ran the structural checker: individual core maxima, every minimax-point violation query, targeted cases, exactness examples, k=2,...,6 attaining families and negative controls passed.
2. Independently verified those510 full selector claims using a new explicit sorting-network SMT encoding. Coalition values were reconstructed independently for all4-player coalitions; no progressive-floor helper was imported. Every strict lex-improvement query was UNSAT. A first-stage-only fake was correctly rejected by a SAT improvement witness.
3. Independently rebuilt six raw triple games from the manuscript, with (L,R)=(1,0),(1,3),(2,1),(3,2),(4,0),(4,16), reaching192 players. Checked both inclusions in the claimed entire-core parameterization, dummy support, better-floor infeasibility, optimal-floor uniqueness, better-ceiling infeasibility, minimax uniqueness and coordinate maxima. These checks use direct SAT queries, not the shared staged selector implementation. The first three cases additionally exclude an integral matching heavier than T by binary integer constraints; all six carry equal matching/cover certificates.
4. Checked the finite-n padding inequality at987 counts, including every n=30,...,1000 and large powers-of-two boundaries up to roughly10^19.
5. Replayed all256 binary2x2x2 arrays, the sourced empty-core example, additive calibrations and12 fixed-seed3x3x3 arrays. There were237 positive nonempty-core binary cases, all with selector distance0; eight of the12 sampled3x3x3 cases had nonempty cores. All checks passed.
6. Replayed the consolidated extension checks: six graph cases and eight additive cases, including empty-core, zero-shift, nonbipartite, signed-coefficient and whole-minimax-face controls.

Evidence files: review_input_hashes.json, hostile_checks.py, hostile_check_results.json, assignment_replay.log, assignment_structural_replay.log, three_calibration_replay.log and extension_replay.log, plus regenerated JSON within the scratch package copies.

## Verifier soundness and limits

The modern assignment scripts use explicit RuntimeError guards and reject solver UNKNOWN, so Python -O does not remove their proof gates. Their progressive-stage selector is sound: after fixed coordinates are retained, the next optimal level is monotone and therefore enforces previous free-coordinate caps automatically. A pinned coordinate must exist on each compact convex optimal face. Nevertheless several "independent" replays share Z3 and closely related selector code; they are not independent solver implementations. The fresh sorting and unique-face queries above reduce this shared-algorithm risk while still trusting Z3's arithmetic engine.

The strict/equality historical CPC record wrappers are a different matter and are reviewed in the accompanying wrapper-patch report. Their validation flaws do not occur in these modern assignment verifiers and do not by themselves refute any theorem. All-parameter correctness ultimately rests on the conventional proofs.

## Contribution classification

- Principal candidates: exact finite graph selector-distance bound and explicit sparse bounded-value three-sided construction approaching absolute maximal disagreement; their combined structural boundary is coherent.
- Short corollaries or supporting deductions: bipartite half domination from known algorithm invariants, extension of the geometric proof to general nonempty-core graphs, and additive shift-simplex quantitative bounds.
- Established background: entire-core covering descriptions, optimal-matching complementarity, full sorted selection concepts, and feasible matched-halfsplit Lorenz optimality/exact-assignment agreement.
- Unresolved externally: novelty, priority relative to inaccessible originals, field-level significance, prevalence and perturbation robustness. The construction proves a worst-case allocation disagreement, not inefficiency or empirical unfairness.
