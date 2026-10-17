**Provisional verdict: no findings of load-bearing error in reviewed scope.** Most important observation: every step audited (minimal-face supports, nonexposed-face separation `K ∩ W = H`, surrogate exactness, extreme-point rank bound, lemma interface) checks out; the only items are low-severity wording/implicit-step issues.

## Findings

**1. Low — `composition/CONE_GAIN_ONLY_THEOREM.txt:142-143` — "span of the d coordinate columns" should read "row space of the d×n coordinate matrix."**
The vectors `(θ(b_1),…,θ(b_n))` for linear θ lie in the row space (dimension ≤ rank ≤ d), not the column span (a subspace of V). The conclusion D ≤ d+1 (indeed ≤ k+1) is correct; only the phrasing is off. Verification: none needed beyond rereading; optionally tighten the bound to `1+2√(k+1)` noted as analysis-only.

**2. Low — `root/LOW_RANK_CAPPED_SAMPLING_LEMMA.txt:22-24` — trace ≤ rank step is correct but implicit.**
Eigenvalues may be complex; the step requires `trace = Σ Re λ ≤ #{λ≠0}·ρ(V) ≤ rank(V)`, using ρ(V) ≤ 1 from column sums ≤ 1 and algebraic multiplicity of 0 ≥ nullity (which the file does state). Correct; suggest one clause making the real-part bound explicit. (Root already audited; I only re-verified the interface used in §7.)

**3. Low — `composition/CONE_GAIN_ONLY_THEOREM.txt:36-39` — boundary-extension argument is redundant, not wrong.**
A supergradient of `F|_{H_x}` at `x ∈ relint(H_x)` already satisfies the inequality on all of `H_x` by definition. The dilation argument is harmless.

## Steps validated (load-bearing)

- **§2 supports:** `x ∈ relint(H_x)`; supergradient exists; constant term forced to 0 by homogeneity along the ray (`t·c ≤ c ∀t>0 ⇒ c=0`). Extended price additive by face heredity. ✔
- **§3 coverage:** cap case gives `T − Σ_{h∉A} f_h ≥ F(b(A))` by superadditivity; finite-price case uses `b(A) ∈ H_{C_B}` and `F(C_B)−F(C_B−b_i) ≥ ℓ(b_i)`. ✔
- **§3 individual OUT:** open: `F(C_B)−F(C_B−d) ≥ F(d)`, `C_B−b_i` unchanged. Closed: `ℓ_{C_B}` depends only on `C_B` (excludes `b_i`); cap rises by `F(C)−F(C−d) ≥ F(d)`; three face cases exhaustive (`d ∈ H` when both in H; low-outside ⇒ high-outside; high-outside pays cap). ✔
- **§4:** `-(1-q)g'(q)` identity, `g(q) ≥ (1-q)^n G`, integration by parts reproduces `B_n(a)` exactly (I recomputed; the `−(1−a)g(a) ≤ −(1−a)^{n+1}G` term is needed and is used). `B_n(√(2/(n+1))) = n√(2/(n+1))`. ✔
- **§5:** `H` convex/subadditive, `P` compact via strictly positive functional (exists for closed pointed `K`), extreme points have ≤ k support, `Φ ≤ (m−1)Ψ` at extreme points, Jensen at `α=1`. `m_i − f_i = H(b_i)+H(C−b_i)`, `ΣH(b_i)=G`. ✔
- **§6:** `K ∩ W = H` for any face (not only exposed); 0 ∉ conv of projections; ψ vanishes on W so `Σ_{i∈B} a_i(B) = w(B)`; capped surrogates match extended-price excesses exactly, including B=∅ and zero bundles. ✔
- **§7:** own-bit identity, `min{v/G,1} ≤ 2v/(G+v) ≤ 2v/colsum`, `∫q/(1−q) = −a−log(1−a)`, series bound `≤ a²/(2(1−a))`, `a=1/(1+√(d+1))` gives `1+2√(d+1)`. ✔
- Efficiency at G=0 and nonnegativity (all payments ≥ f_i ≥ 0). ✔

## Scope limitations

- `CONE_APPLICATIONS_AND_LIMITS.txt` and `CONE_CHECKS.json` not in packet; no tests run.
- §8 lineality reduction checked only for internal consistency (`F(l)=F(−l)=0`), not for the implicit claim that `K/L` is closed (true, but unstated).
- Suggested numerical verification: a cone with a nonexposed extreme ray (e.g., cone over conv(disc ∪ square) in R³) with a closed owner on that ray, confirming ψ-separation and OUT in the "only-high-outside" case.

**Verdict: no findings (of substance) in reviewed scope.**
