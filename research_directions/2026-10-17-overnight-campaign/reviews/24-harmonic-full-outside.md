**Provisional verdict: no findings in reviewed scope** (the full-OUT derivative chain, sharp γ_t constant, funding algebra, type-congestion transfer and bucketed bound (13) all check out on independent recomputation). Most important observation: the proof is sound but hinges on two unverifiable named dependencies and an unreviewed checker.

## Findings

**No correctness defects found.** Items independently recomputed:

- **Normalized derivatives (5), lines 34–38.** Q' = Σ w_v² d'_v and Z_P' = Q'Σθ_v + Σ w_v d'_v(1−θ_v) are correct (θ_v' = d'_v(1−θ_v)/P'_v). All d'_v coefficients are nonnegative; the min-over-θ reduction to Σ min(w_v,S₂) is valid.
- **Sharp γ_t (6)–(7), lines 45–53.** φ(q)=q²+m(1−q)²/(t−m)+1−q is convex with minimizer q=(t+m)/(2t) ∈ (½,1); φ there equals (3t+m)/(4t), minimized at m=1. The m<t restriction is justified (all weights exceeding S₂ ≥ 1/t forces Σw>1). Equality witness: S₂=(t+3)/(4t), w₁>S₂ iff t>1, Σmin=(3t+1)/(4t). Correct.
- **Case r<C, lines 64–72.** f−krf_r=0 holds for f=(r/C)^{1/k}. r' decomposition and Z'≥L verified (for a privately-assigned branch the own-share term plus cap-growth term sum exactly to d_jl). Dropping the nonnegative first term of r' and using Z≤kG gives Y'≥A_tZ_P'≥D≥F(d). Valid.
- **Case r>C, lines 74–82.** hZ_P = CGΣθ_v is exact; both G' and θ_v' are ≥0; Z_j' ≥ g_j' = d_{jl*} for the current minimizer. Valid.
- **Funding (12), lines 100–105.** f/r ≤ M^{(k−1)/k}/C via r≥C/M; r=1,C=1 corner is consistent. Substituting (1) yields B_tC+max(B_t,k). Verified.
- **Type transfer and (13), lines 110–122.** Σ_τF_τ(d) ≥ F_true(d) is a genuine relaxation inequality in withdrawn capacities; time-sharing uses K_τ/D ≤ 1 for private rows. K_τ ≤ √(B₂k)M_τ^a+B₂+max(B₂,k) follows from C ≤ 1+√(k/B_t)M^a; Jensen step requires ΣM_τ=M (true with disjoint buckets). B₂=16/7 is correct for γ₂=7/8.

**Low — zero-face handling (lines 87–97).** The argument is correct but terse: it implicitly uses that G(u) and Q(u) are nondecreasing along restoration (so zero values occur only at u=0) and that total payment → 0 continuously as Q→0 or G→0. Both hold (G ≤ MQ/C; B_tQh = B_tCG when r>C). Suggest stating the monotonicity explicitly.

**Low — wording.** Line 39 "decreases it" should read "does not increase it" (D may equal some d'_v).

## Scope limitations

- Could not inspect `harmonic_multi_common_full_outside.py`; the claim that it raises on unresolved algebraic comparisons is unverified.
- Named dependencies accepted without verification: TheoremA's TCWM scalar identities, the three-pool 1+2c full-OUT constant, the one-common full-OUT mechanism (line 106 "recovers" claim unverifiable here), and the within-type prefix (fractional-knapsack) identity's extension to F_τ(d) for arbitrary d (holds by inspection since the identity is pointwise in capacities, but no proof text is supplied for the OUT version).
- No empirical or novelty claims reviewed.

## Verdict

**No findings in reviewed scope.** The mixed-owner derivative lemma, γ_t constant, both joint-direction cases (including persistent ties), actual-technology funding, weighted type time-sharing, and the ρT approximation transfer are each verified algebraically from the packet. Residual risk lies only in the unreviewed checker and the accepted prior constants.
