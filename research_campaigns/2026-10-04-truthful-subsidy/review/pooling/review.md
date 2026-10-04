**Provisional verdict: no findings in reviewed scope.** I found no invalid step or counterexample in Theorem 1 or Theorem 2. All checks were by hand; nothing was executed.

## Findings

No correctness defects. Steps I re-derived (POOLING_THEOREM.txt):

- **(a), L29–33:** The bottleneck factor makes P(T)=0, so Σp_j=1. Since c(S∩N_j) ≥ v(S) for every j, y(S) ≥ v(S) for every coalition. The T=0 case is trivially covered.
- **(b), L38–47:** The truncated g vanishes for t ≥ min_{l≠j}A_l, so ∫₀^{x+a} g equals the displayed ∫₀^T. Both x/(x+a) and the integral are nonnegative and nondecreasing in x. The boundaries (a=0, x=a=0, another pool at zero) are consistent with y=0.
- **(c), L49–56:** In both cases H_i ≤ T − v(N∖{i}) ≤ c_i·T/A_j; the A_j>B case reduces to c_i ≤ A_j. Then p_j ≥ T/(kA_j), using A_l ≥ T. Only an upper bound on the original-core H is used, so nothing is recomputed after subsidy.
- **(d), L58–64:** Σ_j A_j p_j ≤ T + (k−1)T/2. The limit A=(1,M,…,M) confirms (k+1)/2 is a non-attained supremum for this formula.
- **Closed form, L66–70:** p_L=B/(2A), p_R=1−B/(2A) and total 3B/2−B²/(2A) are correct.
- **Theorem 2 upper bound, L83–91:** z is monotone, covers coalitions through the bottleneck pool, satisfies z ≥ H, and totals 2T. The mix gives floor exactly αH and subsidy ≤ α, and stays inside the totals-only class.
- **Theorem 2 lower bound, L93–106:** The quantifiers are sound. Monotonicity is used in the one-owner-per-pool instance, giving M·p(M,1) ≥ r. Covering is used in the {1, M−1 | 1} instance. The two are linked only by partition-independence of p and q. The renaming at L95 is legitimate because the argument is symmetric, with no symmetry assumed of the mechanism.

**Low — wording, L72 and L81.** The lower bound gives β ≥ 1/2 even at α=0. Within this class there is therefore no tradeoff for α ≤ 1/2: fairness up to H/2 is free. "Sharp tradeoff" is accurate only for α ∈ [1/2,1]. Suggest stating this explicitly.

**Low — do not promote, L104–106 and L109–110.** The 1/2 lower bound is an artefact of the class restriction. The CALIBRATION five-profile rule is ownership-dependent and achieves 1/8 on its domain, and the text disclaims promotion correctly. I re-derived the 1/8 bound (three coalitions {2,3}, {2,4}, {1,3,4}) and it is valid for any rule whose domain includes those 2×2 profiles.

**Low — scope, L8–9 and L25.** The k=3 result covers only a series of three parallel bundles. It does not cover depth-3 DAGs with mixed path lengths or non-series structure. The text says "subclass"; keep that qualifier in any summary.

**Info — contract fit.** For the live two-hop cell, Theorem 1 delivers an H/2 floor (stronger than the contract's H/3) with β ≤ 1/2, on all real profiles and any number of parallel arcs. The exact minimax constant remains in [1/8, 1/2], as stated at L109–111.

## Suggested verification

- Run an exact-rational randomized check of (a)–(d) for k=2,3 with multi-owner pools, including profiles with zero capacities and tied bottlenecks.
- Run a symbolic check of the y^α floor and subsidy identity.

## Scope limitations

- `verify_calibration.py` was not supplied, so its claimed checks (75/20/4) are unverified.
- No source or novelty audit was done.
- Coordinated reports, false names, overreports and positive costs were not assessed; the document does not claim them.

## Verdict

No findings in reviewed scope. Both theorems stand as stated, with the restricted-class and series-pool qualifiers retained.
