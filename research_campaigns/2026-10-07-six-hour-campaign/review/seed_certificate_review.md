**Provisional verdict: no correctness findings in reviewed scope** (proof review only; checker not executed). Most important observation: the checker's strict-face test is not the theorem's margin LP (4) but a vertex-average criterion; I verified it is equivalent, but the theorem text does not document this substitution.

## Findings

**F1 (Low, documentation) — Strict feasibility via vertex averaging, not LP (4).**
`seed_certificate.py:163-173` certifies C_σ ≠ ∅ by averaging all vertices of the relaxed polytope P_σ and checking each strict form is positive there. This is sound and complete: a linear form attains its max on P_σ at a vertex, so C_σ ≠ ∅ ⇒ every strict form has a positive vertex ⇒ the average (all others ≥ 0) is strictly positive; conversely the average is itself a witness. The reuse shortcuts (`:192-198`) are also correct: when the new hyperplane does not cut P_parent, P_child = P_parent; when `low==0` or `high==0`, {form=0} is a supporting face whose vertices are exactly the parent vertices with value 0. The theorem (§3) should state that any strict witness suffices and that the LP is one option. Verification: add a comment/paragraph; no code change needed.

**F2 (Low, consistency) — η range mismatch.** SEED_CERTIFICATION §1/§7 only require η>0; UNIFORM_SAMPLING_THEOREM §1 requires 0<η≤1 for sample bound (1). The Las Vegas acceptance-probability argument (§7) silently inherits η≤1. Fixtures use η=2 (`:395`) — fine for the seed-agnostic checker but outside the probabilistic regime. Verification: add η≤1 to §7 hypotheses.

**Verified steps (proof):**
- Hyperplane families suffice: all-coalition pairwise comparisons fix the first-argmin for every U (full preorder on V fixed); cap branch compares w^{v*}·b_i against L_{I,t*}, both in the second family. Δ_{i,S} uses two fixed coalition forms. No θ-dependent surfaces.
- Closure lemma (5) and the convex-combination argument are correct; counterexample t-formula gives G(b_t) < G(x)/2 − G(x)/2 = 0 and b_t ∈ C_σ (`:323-327` implements it and re-checks membership and actual slack).
- T=0: frozen coalition forms equal true minima on closures by continuity; cap branch w·b_i ≤ T persists on closure, so frozen payments vanish. `:306-307` tests exactly this.
- Homogeneity, face partition, linear-objective-on-closure ⇔ on-face equivalence, incremental face bound Σ2^k C(h,k), and geometric Las Vegas analysis (expected trials ≤ 1/(1−δ), finite seed space 2^{nN}, positive-probability event contains an atom since π_k>0) all check.
- Posterior-sampler compatibility: θ_{|S|} is a per-mask constant; the arrangement needs no extra hyperplanes.

**Hand-checked fixture claims:** θ=(3/8,5/16,11/56) matches I_{n−k+1,k}/I_{n−k,k} with b0=1/2, n=2. The 11-hyperplane count (`:386`) for n=2,d=2,V={(1,0),(0,1)} reproduces by hand after canonicalization/dedup. The three calibration arrangements (`:374-380`) yield 3, 3, 1 faces as asserted. For the accepted seed, a spot check at b=((1,0),(0,1)) gives ΣP=T exactly (tight, nonnegative); the η=0 and Cbar=3/2 negative controls fail as claimed at that profile and at ((1,1),(1,1)).

## Scope limitations
- No execution; fixture outputs, `COUNTS`, and `required_cushion` diagnostics unverified beyond the hand checks above.
- Did not re-audit the uniform theorem's constants or the dual-vertex enumeration preprocessing.
- Vertex enumeration via all active sets is exponential; correctness only, no performance claim reviewed.

## Verdict
**No findings** affecting soundness, completeness, or Las Vegas termination in the reviewed scope; two low-severity documentation/consistency items (F1, F2).
