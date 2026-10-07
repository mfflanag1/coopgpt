**Provisional verdict: no substantive mathematical findings in reviewed scope; one cross-reference cannot be verified from the packet.**

## Findings

**1. (Medium — unverifiable dependency) Lower bounds rest on `lem:weighted-hierarchy` / `eq:weighted-bound`, which are not in the packet.**
`concave.tex` L243, L257–261, L385–388. The supplied `general_and_dag.tex` contains only the DAG analogue (with auxiliary fan owners and a `max{1+α, m/R}` factor), not the scalar multi-glove lemma. Two things are therefore unchecked: (i) that the glove bound has exactly the form `(h+1−h/s)/((1+α)(1+h e^{−k/Z}))` with no `m/R`-type factor; (ii) that in Theorem `ext:thm:dim-gap` the bound depends on the pool count `k` *only* through `e^{−k/Z}`, which is what justifies replacing `k=K_h` by any `D ≥ K_h` (L385–388). The DAG proof is consistent with both (its `k` enters only via `(dag:mean)`), so I expect this to hold, but it is not verifiable here.
*Verification:* supply the lemma statement; confirm the first coalition inequality `Σ_h ν_h x_h ≥ 1` and the transport identity are `k`-independent in the glove version.

**2. (Low — notation) Symbol clash and mixed-direction chain.**
`R` denotes `Σ_i r_i^q` in Lemma `ext:lem:budget` (L53) and `⌈log(h+1)⌉` in L251. Eq. `(ext:eq:endpoint)` (L170) chains `≥ … = … ≤ … ≤`; the needed facts (`m`-term ≥ `ℓ(b_i)` and `ℓ(b_i) ≤ T`, hence uncapped) are both correct, but the display reads as a single inequality chain. Cosmetic; no gap.

## Checked and found correct

- **Boundary-discontinuous supports (L92–128):** supergradient at the relative-interior point `x`; `u·x=f(x)` via homogeneity both directions; `u≥0` via monotonicity; boundary majorization via `y_ε=(1−ε)y+εx` with the cancel-and-divide step valid for `0<ε<1`; admissible set closed, convex, bounded by `u_e ≤ f(x)/x_e`, nonempty. Degenerate case `f(x)=0` forces `u=0`, consistent with `f≡0` on `F_J`.
- **Whole-bundle monotonicity (L153–159):** with `B_i=0`, `x_B` and `ℓ_{x_B}` are `b_i`-independent; `min{ℓ(b_i),T}` nondecreasing including the `∞` transition; `m_i^q` off term fixed. Correct.
- **Coverage (L160–173):** case split on a capped term in `S`; otherwise all on one face so additivity applies. Endpoint inequality uses `b_i ≤ x` ⇒ both `b_i, x−b_i ∈ F_J`. `r ≥ z` follows.
- **Fixed-profile mask union (L21–44, L175–179):** list `{a(B)/T}` of ≤ `2^n` vectors fixed at the profile; union bound is sound since `δ^B` always satisfies the selected-score constraint. Integration gives `(log H+λ+1)/α`; `α ≥ α_j` for `q ≤ 1/j`. `C_{j_n}(2^n) = (log 2+o(1)) n/log n` checks (`α_{j_n}~log n`, `j_n=o(n/log n)`).
- **Lower owner padding (L244–247, L267–272):** zeroing trailing owners preserves all coalition values and unilateral comparisons; `log ν_h=(1+o(1))h log h ≤ (1−ε+o(1))log n`. Parameter checks `s≥2`, `m>h`, `λ≥h`, term monotonicity up to index `h` all hold.
- **Nonconcave max example (L362–368):** with `ε≤1`, singleton values are exactly 1, `T=1+(d−1)ε`; `ε=d^{−2}` gives `(1−o(1))d`.
- **ρ / θ / σ bounds (L331–351, L395–431):** `a/(a+A)` monotonicity, `b_i ≤ ρ_i c`, `Σρ_i ≤ |supp c|`, dual ratio as weighted average of coordinate shares, cone ratio as weighted average over generators with zero-denominator generators having zero numerators, `Σσ_i ≤ r`. Marginal grouping bound `|G|T−(|G|−1)A ≤ T` uses `A ≥ T`. Correct.

## Scope limitations
Only the two supplied files reviewed; `\eqref{prod:*}` references resolved against `general_and_dag.tex`; `lem:weighted-hierarchy`, `eq:weighted-bound`, `BoydSubgradients` not available. No tests or tools executed.

## Verdict
**No findings in reviewed scope** apart from the unverifiable cross-reference (Finding 1) and cosmetic notation (Finding 2).
