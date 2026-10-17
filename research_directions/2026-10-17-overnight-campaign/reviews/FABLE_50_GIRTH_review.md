**Provisional verdict: no findings in reviewed scope.** The star-support reduction, the closed-neighborhood identity (7), the counting giving ρ ≥ (d+1)/2, and the half-integral-dual upper bound (5) all check out line by line; the only items I flag are minor rigor/scope points, none affecting the claim.

## Findings

**1. (Low) Checker's "degree_upper_profiles" test is not independent of the half-integrality lemma.** `P4_SIGNED_CHECK_HIGH_GIRTH.py:55–58` computes F as the minimum over covers with p ∈ {0,½,1}. That equals F_G only if the lemma (note §3, lines 111–119) holds; otherwise the enumeration overestimates F, which would make `H <= (Δ+1)/2·F` *easier* to pass. The lemma itself is classical and the supplied proof is correct (truncation preserves covers; tight edges cannot touch 0/1 vertices; bipartite free tight components admit ±ε perturbation; odd tight cycles force ½ and propagate). Verification: compute F by an exact rational simplex/`fractions`-based LP in the checker and assert it equals the half-integral enumeration.

**2. (Low) Implicit measurability assumption, overstated tool.** §1 line 64 speaks of "each measurable holding," but (1) never states that a_i(·), b_i(·) are μ-measurable; the integral in (1) needs it. Also, (7) only interchanges a *finite* sum with an integral of nonnegative functions, so linearity/monotonicity suffices; Tonelli (line 86) is unnecessary and would require σ-finiteness if a product measure were actually involved. Suggest stating measurability in the theorem and replacing the Tonelli citation.

**3. (Informational) External comparison claims are unverifiable from the packet.** Lines 46–49 and 175 assert "full-OUT has funding factor 2" and "3/2 for TCWM." Nothing in the snapshot supports these; they do not affect the theorem but should be cited. The note correctly refrains from treating (3) as a lower bound on arbitrary incentive mechanisms (lines 46–49, 170–177).

## Verified steps (for the record)

- **Star forcing (§1):** H({i})=0 ⇒ f_i=0 and min(a_i,b_i)=0 a.e.; H({i,j})=0 for nonedges ⇒ opposite supports span K_{|A|,|B|}; C4-free ⇒ min(|A|,|B|)≤1. Correct; finitely many null sets, so a common null set is fine.
- **Identity (7):** For a star layer centered at v with leaf set B⊆N(v): value(N[v]) = grand; for w∈N(v), N[w]∩B={w}∩B by triangle-freeness, so value(N[w]) = value({v,w}); for w∉N[v], v∉N[w], value 0. Holds per layer regardless of which endpoint is called "center" in the singleton–singleton case, so measurability of that choice is not actually needed. Integrate: (7) exact.
- **Counting:** F(N[v])=1, F(e)=1, F(V)=n/2 (d-regular), so nρ ≥ n/2 + nd/2. Correct. Zero-capacity/zero-worth coalitions cause no division issues.
- **Upper (5):** F ≤ H_star via l_v ≤ min(c_v, N_v). Upper via V0/Vh/V1 partition; N(V0)⊆V1 and |N(u)∩V0| ≤ Δ give 2H_star ≤ Σ_{Vh}c + (Δ+1)Σ_{V1}c ≤ (Δ+1)F, using Δ≥1. Coalitionwise transfer (line 102) is valid because H_star(c_S) is literally the restriction of the same layers. At the unit profile H_star(N[v])/F = (d+1)/2, so sharpness is exact.
- **Families:** Projective incidence counts (q+1 points per line, unique common line ⇒ no C4) and the 2-adic uniqueness argument for the circulant (|differences| < 2^{d−1}, m = 2^{d+1}) are correct. Checker's girth tests (`verify_high_girth`, lines 16–19) test all vertex pairs, which covers both sides of the bipartition.

## Scope limitations

I did not run the checker; I only read it. Historical priority (line 2) is not assessed. The companion JSON output was not in the packet.

## Verdict

**No findings in reviewed scope** (two low-severity rigor/independence notes, no errors in the claimed (d+1)/2 lower bound, identity, upper bound, or graph families).
