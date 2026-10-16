**Provisional verdict: no findings in reviewed scope (both statements rederive correctly from the displayed definitions); only low-severity wording/scope notes.** Most important concrete check: the exact owner-removal identity (3) and the certificate's monotonicity premises are correct as stated.

## Findings

**1. Low — MARGINAL_FLOOR_STABILITY.txt:17–28, identity (3).** Rederived: with short total 1, M=1, opponents' actual long total is 1+u−d when every opponent is uncapped; M₋ᵢ=min(1−s,1+u−d) gives μ=max{s,d−u}. If opponents' actual long ≥1, then ρ−d ≥ min(ρ−d,1)... i.e. capped opposing total ≥1 so d−u≤0 and μ=s. Correct. The identity silently uses that caps are at the branch short total T and that q=½e^{-u}, δ_branch=c−qu — these primitive definitions are not in the packet (scope limitation, not an error). δ_branch≥0 holds automatically since ½ue^{-u}≤1/(2e).

**2. Low — lines 38–44, short-case ratio.** Verified: q=ct, c−qu=c(1−t+t log t), ratio derivative sign (t−1)[(t+1)log t−2t+2], inner derivative log t−1+1/t≥0, endpoint value (e−1)². (e−1)²/(2e) is increasing in e, so using ehi in the checker is the correct direction. Note the case u≥1 uses q≤c; u=1 gives δ=0 and q−c=0, so no division issue.

**3. Low — lines 49–55 and checker.** 1−c−q>0 justifies d→1. Taylor truncations: degree 13 (odd) is a lower bound and degree 12 an upper bound for e^{-x}, x>0 — correct via Lagrange remainder. Interval directions (F decreasing → Fhi at lo; δ decreasing on [0,1] → δ_lo at hi) are correct. Sanity check of worst box lo≈0.1772: F≈0.2527, δ(hi)≈0.1092, ratio≈0.584 — matches JSON. Active-box count 474 is consistent with the root of F near u≈0.6939 (3j/2048<0.6939 ⇒ j≤473). `require` raises RuntimeError, so -O does not disable checks.

**4. Low — lines 77–81, aggregation.** Branch scaling z≥(1−c)μ−(4/5)√(Tδ) and Cauchy–Schwarz with ΣT_j=M, Σδ_j=δ are correct; marginals add since M and M₋ᵢ are both branch sums.

**5. Low — OPTIMAL_PRIMITIVE_ZERO_LOSS_OBSTRUCTION.txt:9–19.** Rederived: λ=1−R satisfies the water equation uniquely below 1 (cap 1 active); P=1−R; with t=1/(1+R), ½+C(t)=1/(8R(1−R)), so p=1/(8R), residual payment pR=1/8 exactly. 3/4→71/96 and 1/4→25/96 check. 25/37<17/25<τ follows from T(17/25)=−211/15625<0 (verified) and T′>0. Nested numbers 15/8 and the e^{1/96} factor check; dominant account 1+25/96 remains capped.

**6. Low (wording) — line 22–23.** "The optimal architecture's flat own-payment segment" reads as a property of every optimal shape; the lower bound only forces f(ρ)≤C(ρ) pointwise, so an alternative Γ-achieving shape with f<C on (12/25,1/2) is not excluded. The obstruction is proved for the constructed shape; suggest "the constructed optimal shape's".

**7. Low (ambiguity) — lines 43–51.** In the r-fold replication, "same aggregate losses" requires the residual owner to underreport in every branch (or the loss scales by the number of deviated branches); either way D_i=0 and outgoing loss>0, so the conclusion stands.

## Scope limitations
- The exponential primitive's payment formula, coalition-coverage property, and outer-layer account/cap conventions (used in §7 and the nested consequence) are not in the packet; I took them as stated.
- "Independent Codex algebra audit passed" (line 3) and the −I −O replay are unverified here.
- I did not re-execute the checker; monotonicity premises and one worst box were verified by hand.

## Verdict
No findings in reviewed scope. Both scalar inequalities, the marginal identity, the exact interval certificate's direction-of-bound logic, the Cauchy aggregation, the zero-own-loss computation, and the nested strict-gain example are valid given the stated primitive definitions. Items 6–7 are presentation caveats only.
