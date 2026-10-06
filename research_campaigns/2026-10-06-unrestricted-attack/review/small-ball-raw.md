## Result: the candidate survives audit — complete checked argument, no counterexample

I checked every step by hand (no code-execution tool was available to me; all numbers below are hand arithmetic and are labelled as such). The pairwise inequality is correct for every ρ ≥ 2, including ρ = 2, arbitrary and unequal owner counts, and zero capacities; the induced budget Q(k) is a valid all-profile bound; and Q(k) < U(k) holds for every k ≥ 2 by an analytic pointwise-domination argument that does not require solving for the crossing point. The improvement is an additive O(1) term (≈ 2 at moderate k by hand estimate; ≈ 1.5 + o(1) heuristically as k → ∞); the asymptotic order log k / log log k is unchanged. No field-level claim.

### Established ingredients (not new) vs. proposed application

**Established:**
- (W) Convolution of symmetric unimodal laws on ℝ is symmetric unimodal (Wintner's theorem; the standard textbook treatment is Dharmadhikari–Joag-Dev 1988, which I did not fetch). I could not extract the verbatim theorem statement from the free pages I fetched: the [numdam page](https://www.numdam.org/item/PS_2013__17__605_0) lists "Wintner's theorem" only as a keyword but its own abstract states the k=1 case we need ("the convolution of two symmetric densities which are k-monotone on (0,∞) is again (symmetric) k-monotone provided 0<k≤1"; 1-monotone = nonincreasing); [arXiv 0708.2341](https://arxiv.org/pdf/0708.2341) references the discrete analogue; [arXiv 2009.13848](https://arxiv.org/abs/2009.13848) was surfaced by search as citing Wintner's Theorem XIII but the PDF text was not extractable. **To remove the citation dependence I give an elementary proof of the special case actually needed (uniform summands) in Step 1 below.**
- Jensen's inequality for convex functions; maximum of a convex function over a polytope at a vertex; vertices of {a∈[0,1]^m : Σa_i = ρ} have at most one fractional coordinate; m! > (m/e)^m (from e^m > m^m/m!); P(U_1+…+U_n ≤ u) = u^n/n! on [0,1].

**Proposed application (the candidate's content):** using the actual law of the short-pool sum X_s (rather than X_s ≤ 1) via convexity of F_j on [0,1], showing the singleton short pool is extremal, then maximizing E[(1−X_j)_+] over the capacity polytope.

### Step-by-step check (manuscript `manuscript.tex` lines 233–252 define the baseline; candidate file lines 7–24)

Setup: a_i = d_i/T ∈ [0,1]; fixed shortest pool s with Σ_{i∈N_s} a_i = 1; pool j ≠ s with Σ_{i∈N_j} a_i = ρ ≥ 2 (so N_j has ≥ 2 owners of positive weight; X_j has a density). X_s, X_j independent (disjoint owners).

**Step 1 (convexity of F_j on [0,1]) — correct; here is a self-contained proof.** Lemma: if Z has a continuous law symmetric about c with F_Z convex on (−∞,c] and concave on [c,∞), and W ~ Unif[0,a] independent, then Z+W is symmetric about c+a/2 with F_{Z+W} convex on (−∞, c+a/2]. Proof: F_{Z+W}(x) = (1/a)∫_{x−a}^{x} F_Z, so convexity on an interval ⇔ g(x) = F_Z(x) − F_Z(x−a) nondecreasing there. For x ≤ c both arguments lie in the convex region, so g is nondecreasing (increment of a convex function over a sliding window of fixed length). For c < x ≤ c+a/2, symmetry gives F_Z(x) = 1 − F_Z(2c−x), so g(x) = 1 − F_Z(2c−x) − F_Z(x−a) with both 2c−x and x−a in (−∞,c] and x−a ≤ 2c−x; as x increases, the window [x−a,·] lies to the left of the window ending at 2c−x, and one-sided derivatives of the convex F_Z satisfy F_Z'((x−a)±) ≤ F_Z'((2c−x)∓), so g is nondecreasing. Symmetry of Z+W is immediate. Induction over the summands a_iU_i (each uniform on [0,a_i], symmetric unimodal; drop a_i = 0) gives F_j convex on (−∞, ρ/2] ⊇ [0,1] because ρ ≥ 2. This is exactly Wintner's theorem specialised; the candidate's citation is correct.

**Step 2 (Jensen) — correct.** For every realisation, Σ_{i∈N_s} a_i = 1, U_i ∈ [0,1], so F_j(Σ a_iU_i) ≤ Σ a_i F_j(U_i) (zero weights contribute nothing). Since X_j is continuous and independent of X_s, P(X_j < X_s) = E[F_j(X_s)] ≤ Σ a_i E[F_j(U_i)] = E[F_j(U)] = ∫_0^1 P(X_j ≤ u)du = E[(1−X_j)_+]. Owner count of the short pool is arbitrary.

**Step 3 (vertex maximisation) — correct.** For fixed u, a ↦ (1−Σa_iu_i)_+ is convex; expectation preserves convexity; the feasible set {a∈[0,1]^m : Σa_i = ρ} is a compact polytope whose vertices have ≤ 1 fractional coordinate (two fractional coordinates can be perturbed by ±ε). Since m ≥ n+1 when θ>0 (and m ≥ n when θ=0), the vertex (n ones, one θ, zeros) exists. Owner count m of pool j is arbitrary; zeros are allowed. No owner is split; this bounds a fixed pool's probability by a distributional comparison.

**Step 4 (formula) — correct.** E[(1−S_n)_+] = ∫_0^1 u^n/n! du = 1/(n+1)!. For θ∈(0,1), condition on V: E[(t−S_n)_+] = t^{n+1}/(n+1)! for t = 1−θV ∈ [0,1], and ∫_0^1 (1−θv)^{n+1}dv = [1−(1−θ)^{n+2}]/(θ(n+2)), giving q(n+θ) = [1−(1−θ)^{n+2}]/(θ(n+2)!). Limits θ→0 and θ→1 give 1/(n+1)! and 1/(n+2)!, so q is continuous; q(ρ) = E[(1−S_n−θV)_+] is pointwise decreasing in θ, hence strictly decreasing in ρ. Equality: singleton short pool and pool j = (1,…,1,θ) attains P(X_j<X_s) = q(ρ) exactly, so the *pairwise* bound is sharp.

**Edge cases requested:** ρ = 2: n=2, θ=0, q = 1/6, F_j convex on [0,1] = [0,ρ/2] (e.g. a=(1,1): F_j(x)=x²/2) ✓; baseline (e/2)² ≈ 1.85 is vacuous there. Unequal owner counts: handled in Steps 2–3 with no restriction. Zeros: dropped harmlessly in Steps 1–3; manuscript guarantees each pool has some positive capacity.

### Budget and analytic comparison to baseline

For j ≠ s, p_j = P(X_j < X_ℓ ∀ℓ≠j) ≤ P(X_j<X_s) ≤ q(ρ_j). With ρ_W ≥ 1 and at most k−1 pools having ρ_j > 1, for s ≥ 2: P(ρ_W > s) = Σ_{ρ_j>s} p_j ≤ (k−1)q(s) (q decreasing), and ≤ 1. Hence E ρ_W = ∫_0^∞ P(ρ_W>s)ds ≤ 2 + ∫_2^∞ min{1,(k−1)q(s)}ds = Q(k). ✓ (With the floor, total factor ≤ 1+Q(k).)

**q(s) < (e/s)^s for all s ≥ 2 (rigorous):** with n = ⌊s⌋, q(s) ≤ q(n) = 1/(n+1)! < (e/(n+1))^{n+1} ≤ (e/s)^s, the last because (e/s)^s = exp(s − s log s) has derivative −log s < 0 for s > 1 (the manuscript's "for s ≥ e" is more conservative than necessary). Quantitatively, by Stirling's lower bound, q(s) ≤ (e/s)^s / √(2π(⌊s⌋+1)); heuristically the true ratio is ≈ 1/((s+1)√(2πs)) (inference, not proved).

**Q(k) < U(k) for every k ≥ 2 (rigorous):** for s ∈ [2,e], min{1,(k−1)q(s)} ≤ 1; for s ≥ e, (k−1)q(s) < k(e/s)^s, so min{1,(k−1)q(s)} ≤ min{1,k(e/s)^s}. Therefore Q(k) ≤ ∫_0^e 1 ds + ∫_e^∞ min{1,k(e/s)^s}ds = R_k + ∫_{R_k}^∞ k(e/s)^s ds ≤ R_k + 1/log R_k = U(k), where the last two steps are exactly the manuscript's (lines 246–252; k(e/s)^s ≥ 1 on [e,R_k] since R_k > e and the function decreases). Strictness holds because on (R_k,∞) the integrand inequality is strict. This sidesteps the integer-rounding issue the candidate flagged: I did **not** prove Q_int(k) < U(k) in general (Q_int can exceed Q by up to ~1), only Q(k) < U(k).

Useful identity (checked): ∫_n^{n+1} q(s)ds = H_{n+2}/(n+2)!, so ∫_2^∞ q = Σ_{m≥4} H_m/m! ≈ 0.10983.

**Hand-computed illustrations (not machine-verified):** Q(2) ≈ 2.11 vs U(2) ≈ 4.17; Q(7) ≈ 2.66 vs U(7) ≈ 4.97; Q(100) ≈ 4.38 (s* ≈ 3.825) vs U(100) ≈ 6.48; Q(10⁴) ≈ 6.67 (s* ≈ 6.211) vs U(10⁴) ≈ 8.75. Heuristic asymptotics (inference): s* ≈ R_k − 1 − log(2πR_k)/(2 log R_k), so U − Q ≈ 1.5 + o(1) with the o(1) positive and ≈ 0.5–1 at moderate k; order log k/log log k unchanged.

### Limitations and unresolved items
- No counterexample found; the proof is complete for the stated claims. I filled one gap: the candidate asserts Step 1 by citation only; I supplied an elementary proof since I could not extract Wintner's verbatim statement from free pages.
- Pairwise bound unused for ρ ∈ [1,2) (convexity holds only on [0,ρ/2]); the "2 +" floor is crude, and the union bound/min truncation make Q(k) non-sharp even though q(ρ) is sharp pairwise.
- Q_int(k) < U(k) not proved; asymptotic gain ≈ 1.5 is heuristic; all numerics are hand arithmetic.
- No novelty or field-level significance is claimed; this is a quantitative constant improvement within the existing mechanism.

Sources: [numdam — Convolution property and exponential bounds for symmetric monotone densities](https://www.numdam.org/item/PS_2013__17__605_0); [arXiv 0708.2341](https://arxiv.org/pdf/0708.2341); [arXiv 2009.13848](https://arxiv.org/abs/2009.13848); [Wintner lectures 1937–38 (catalogue entry)](https://ci.nii.ac.jp/ncid/BD02288186).
