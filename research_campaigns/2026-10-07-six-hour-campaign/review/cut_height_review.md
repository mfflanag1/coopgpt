**Provisional verdict: no findings in reviewed scope.** I traced every step of Sections 2–4 and the stated corollary; all check out, including with parallel edges. Only minor presentational notes below.

## Findings

**None invalidating.** Minor notes (severity: low / informational):

1. **CUT_HEIGHT.txt:26 — private-witness existence.** Uses both "C is a cut" (so Q_e must use some C-edge) and "C\{e} is not a cut". Correct but compressed; acyclicity guarantees Q_e uses e once. With parallel edges e, e' ∈ C between the same endpoints, Q_e uses e specifically, which is all Section 3 needs.

2. **CUT_HEIGHT.txt:36–45 — interval injection.** Verified: (a) s ∈ S_ij (s ∈ R, τ(s) < τ(b_j)); t ∉ S_ij (t ∉ R, τ(a_i) < τ(t) since a_i precedes t on P — does not require t to be τ-maximal); (b) monotonicity of τ along P makes the three-zone description exact, and the only P-edges leaving S_ij are e_i,…,e_j (edges strictly between are in δ⁺(S_ij) iff R→non-R iff in C); (c) prefix of Q_{e_k} ⊆ R with τ ≤ τ(a_k) < τ(b_j), suffix ⊆ V\R with τ ≥ τ(b_k) > τ(a_i), using i ≤ k ≤ j. Extra δ⁺(S_ij) edges from low-τ non-R vertices are harmless (never on P or Q_{e_k}). D_ij exists since δ⁺(S_ij) is a finite s-t cut. P-intersections are sets of distinct P-edges, so parallel copies cause no collision. Implicit h(C) ≥ 1 holds since C is a cut.

3. **CUT_HEIGHT.txt:13–14 — arithmetic.** r(r+1)/2 ≤ K ⇔ r ≤ (√(8K+1)−1)/2; R_K ≤ √(2K) gives K R_K ≤ √2 K^{3/2}. Correct. Corollary at line 15–17 is the trivial substitution H ≤ K R_K into 2HT; no independent content.

4. **CUT_HEIGHT.txt:52–72 — Fibonacci classification.** Verified: TT-blocking uses "jump ≤ 2" and "S vertices reachable within S" (holds since paths avoiding C stay in R); SS-blocking uses existence of arc f−1→f (always present) and the private-path suffix lying in T; the resulting form S^a(TS)^bT^c is forced and the converse (S-connectivity via +2 jumps, T-to-t via +2 then +1) holds. Minimality via private paths and injectivity (R recovered from C) are sound. Height: path monotone ⇒ leaves each of the b+1 S-runs at most once; backbone achieves b+1. Counts: Σ_{h=1}^r(2r−2h+1)=r², and (2r+1)·r(r+1)/2 − 2·r(r+1)(2r+1)/6 = r(r+1)(2r+1)/6 ✓, ~K^{3/2}/3.

5. **Unused hypothesis (informational).** "Every edge lies on an s-t path" (line 7) is not used in Sections 2–3; results hold without it. Not an error.

6. **Line 29 wording.** The sentence ordering ("Thus C=δ⁺(R). The reverse inclusion also holds…") mislabels which inclusion is which; the argument for both directions is present.

## Scope limitations
- Only CUT_HEIGHT.txt reviewed; the 2HT envelope bound and the K·T marginal budget are taken as given, not verified.
- Literature attribution (Korenblit–Levit) not checked, per instructions.
- No tools run; verification is by hand-trace.

## Verdict
**No findings in reviewed scope.** The private-path characterization C = δ⁺(R), the injection K ≥ h(h+1)/2 (robust to parallel edges), bound (1), and the Fibonacci classification with K = r², H = r(r+1)(2r+1)/6 are all correct as written. The sharpness claim is correctly scoped to the exponent; constants (√2 vs 1/3) are not claimed tight.
