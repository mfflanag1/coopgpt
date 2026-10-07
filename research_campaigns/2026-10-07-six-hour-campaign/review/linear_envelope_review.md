**Provisional verdict: no findings in reviewed scope (minor clarifications only).** The most important point is definitional: the proof assumes the selected minimum cut W is always one of the K inclusion‑minimal structural cuts; the document's wording ("selected random minimum cut") should state this explicitly, since (2) and (6) decompose Pr(e ∈ W) over structural cuts only.

## Findings

**1. Low — LINEAR_ENVELOPE_BOUND.txt lines 10–11, 57, 68: selection domain not stated.**
Evidence: z_e uses "the selected random minimum cut"; line 68 writes z_e(c^t)=Σ_{C∋e} t·Pr(W^{c^t}=C) over structural cuts. If the mechanism minimizes over *all* s‑t edge cuts, a non‑minimal cut can tie a minimal one when zero‑D edges exist, and the decomposition needs a per‑outcome choice of a minimal sub‑cut containing e. The chain (5) survives (score(C′) ≤ score(W) for C′ ⊆ W), so the bound still holds, but the written argument assumes W ∈ structural cuts. Verification: add one sentence fixing the candidate set to the K structural cuts, or add the sub‑cut selection remark.

**2. Low — linear_envelope.py lines 37–39: untested external dependency.**
The script loads `2026-10-06-monotone-envelope/verification/verify.py` (not in packet). Semantics of `effective`, `cutsets`, `weighted_sum` (bitmask cuts, structural‑only) are assumed. Verification: confirm `cutsets` returns only inclusion‑minimal cuts and that `effective` implements min(c_e, maxflow(s,a), maxflow(b,t)).

**3. Informational — the script checks components, not y directly.**
It exactly checks (3), (4), (5) and the identity Σ_e bound_e = K·T, but never evaluates z_e(c^t) or the supremum y_e. That is acceptable (the sup is proved analytically), but the claim "exact … flow checks" should not be read as a numerical test of (1).

## Steps verified (all pass on my reading)

- (3): reflection U_i→1−U_i for negative coefficients gives event Σ|w_i|V_i ≤ N with N=Σ(b_i−a_i)_+, W=A−B+2N; A>B ⇒ 0≤N<W/2. Convex lower‑half CDF ⇒ F(N) ≤ N/W. N/(A−B+2N) ≤ B/(A+B) ⇔ N(A−B) ≤ B(A−B) ⇔ N ≤ B ✓ (N ≤ Σb_i). Cases A≤B, A=B, identical vectors, B=0, N=0, single weight (linear CDF, chord tight) all handled.
- Unimodality lemma: derivative [f(x+r)−f(x−r)]/2r ≤ 0 for x≥0 uses |x+r| ≥ |x−r| ✓; induction base (one uniform) is even/nonincreasing ✓.
- (4): upper bound by c^t ≤ c; lower bound by scaling a D_h‑attaining flow (e‑coordinate ≤ xD_e = t); equality at h=e ✓. Restriction to t ≤ D_e: for D_e ≤ t ≤ c_e feasible sets coincide ✓.
- (5)/(6): event inclusion is weak, so ties are harmless; A is fixed from c, structural, d_A=T; overlap handled by (3) on the same U_h ✓.
- Order of operations: (2) bounds z_e(c^t) uniformly in t by original‑profile quantities, so summing y_e at profile c is legitimate (consistent with the ledger's warning) ✓. Σ_e D_e Σ_{C∋e}1/d_C = K requires d_C ≥ T > 0 ✓.
- T=0 ⇒ D=0 ⇒ y=0; D_e=0 ⇒ D_e(c^t)=0 for t ≤ c_e ⇒ y_e=0 ✓.
- (7): y_e ≤ D_e (z_e(c^t) ≤ t ≤ D_e; for t ≥ D_e equals z_e(c) ≤ D_e) and Σ_{e∈A}D_e=T ✓.
- Calibration: on a K‑edge path the bound gives K·T vs actual T — loose but not claimed sharp.

## Scope limitations

Static review only; no execution; `verify.py` dependency absent; cannot confirm the asserted script run. Novelty and the "L ≤ K" context claim not assessed.

## Verdict

**No findings in reviewed scope.** The K·T envelope bound and refinement (7) are correctly derived; only a one‑line clarification of the cut‑selection domain is recommended.
