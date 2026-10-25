**Provisional verdict: no blocking errors found in reviewed scope; two items warrant a pre-outcome amendment.**

Most important finding: the calibration gate's "six units plus aggregate" screen is not seven checks. The aggregate book (20,0) is a positive multiple of unit 1 (100,0), so the aggregate standardized loss series is *identical* to unit 1's; units 4 and 5 are sign-mirrors of 1 and 2. The protocol should state this before outcomes so the gate isn't later read as stronger evidence than it is.

## Findings

**1. Medium — redundant calibration gate (PROTOCOL_V1.txt:14, 21).** Standardized loss = (q·Δy)/sqrt(qᵀΣq) is invariant to positive scaling of q, so aggregate ≡ unit 1. The 500-draw block bootstrap "for aggregate" is therefore a unit‑1 bootstrap. Effective distinct checks: 2y upper tail (1, aggregate), 2y lower tail (4), 10y upper/lower (2, 5), two curve tails (3, 6). Verification: confirm aggregate and unit‑1 ratios print identically; amend wording to "six unit series (aggregate duplicates unit 1)".

**2. Low — rolling-covariance estimator underspecified (PROTOCOL_V1.txt:9).** The static baseline specifies ddof=1 and demeaning; the primary 252‑day rolling model specifies neither. Demeaning vs. zero-mean (second-moment) estimators differ materially in trending months (e.g., 2022) and interact with the zero mean forecast used for scoring. Fix before running to avoid a post-outcome degree of freedom.

**3. Low — formulations checked, consistent.**
- κ = φ(z)/0.025 with z = Φ⁻¹(0.975) is the correct centered-Gaussian 97.5% ES multiplier (~2.338); bp conversion ×100 and no √252 scaling match the one-day DV01 units.
- Euler k_i = κ·q_iᵀΣq(N)/‖q(N)‖_Σ sums to r and is core-feasible by Cauchy–Schwarz whenever q(N)≠0; the gate's "Euler must be feasible" is thus a numerical check only, which is fine.
- k = b − y gives k(N) = r and k(S) ≤ c(S) ⇔ y(S) ≥ b(S) − c(S); singleton constraints force y ≥ 0, so d ∈ [0,1] and the /(2T) normalization is a true reassigned-fraction.
- Cap Σ max(−k_i,0) ≤ L is convex/polyhedral; Euler itself yields negative charges for units 4–6 (q_iᵀΣq(N) < 0 under positive 2y/10y correlation), so L/T = 0 is likely infeasible — protocol correctly requires reporting infeasibility rather than a substitute.
- Diagnostic (−80,20) for unit 6 does give aggregate (0,0); Euler undefined there, correctly scoped out.

**4. Low — hindsight remarks.** The 2019–2021 / 2022–2025 block split aligns with the publicly known 2022 hiking cycle; this is reporting stratification, not tuning, but should be labelled as macro‑informed. The "positions chosen before reading outcomes" claim is unverifiable from the packet. Differences spanning up to 7 calendar days are scored as one-day Gaussian losses (small variance misspecification, acknowledged implicitly).

**5. Budget baseline.** Contract line 23 and protocol gate 22 correctly state no λ, sponsor surplus, or funding evidence exists; no claim exceeds available data.

## Scope limitations
Cannot verify the SHA256, data coverage (84 months), the referenced "zero-aggregate √3 theorem", or Tasche/SR16‑3 characterizations. No code reviewed; lexicographic implementation correctness (fixed-coordinate identification) remains an execution risk flagged by gate 19 but unauditable here.

## Verdict
**Findings** — amend items 1–2 (wording of calibration gate; rolling estimator spec) before running. No material economic incoherence, outcome-definition error, or leakage beyond already-explicit external-validity limits.
