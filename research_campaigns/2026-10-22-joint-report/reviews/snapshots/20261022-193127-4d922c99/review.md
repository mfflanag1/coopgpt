**Provisional verdict: no findings in reviewed scope.** The frozen joint threshold theorem (Sections 1–5 of `theory/composition_threshold_mechanism.txt`) checks out step by step; every attack vector in the task was tried and none invalidates a claim. The most important thing to confirm was the budget step with two different rows, and it is sound.

## Findings

No correctness findings. Attack-by-attack record (for the audit trail):

**Own-report monotonicity, arbitrary vectors (§2, lines 30–38).** Summand is `min{b_ir, tau(B)·b_ir/(b_ir+C_r)}`. `tau` is a min over a fixed family of maxes of `B_r = b_ir + C_r`, hence nondecreasing in the vector `b_i` under the product order. The ratio depends on one coordinate and is nondecreasing in it (including the 0→1 jump when `C_r=0`). Product of two nonnegative product-order-monotone functions is monotone; min and sum preserve it. So `a_i ≤ b_i` coordinatewise gives `x_i(a_i,b_-i) ≤ x_i(b_i,b_-i)` directly, without needing a coordinate-chaining argument. Verified.

**Zero-coordinate convention (lines 23, 33–34).** `B_r=0` iff `b_ir=0` and `C_r=0`; both conventions then assign 0, and `min{0,·}=0` agrees. No discontinuity in the wrong direction. Verified.

**Coverage via bottleneck row (§3, lines 42–49).** For `r ∈ D` attaining `tau`, `B_r ≤ tau` so `tau/B_r ≥ 1` (or `b_ir=0`), hence the summand equals `b_ir`. Dropping nonnegative `r ∉ D` terms gives `Σ_{i∈S} x_i ≥ Σ_{r∈D} (Σ_{i∈S} b_i)_r ≥ F(Σ_{i∈S} b_i)` since `D ∈ R`. Empty `S` trivial. Verified.

**Budget via a different min-sum row (§4, lines 55–69).** Identity `Σ_i x_i = Σ_r min{B_r, tau}` holds termwise (`B_r·min{1,tau/B_r}`). With `E` sum-minimizing, `tau ≤ max_{r∈E} B_r ≤ Σ_{r∈E} B_r = F(B)`; then `Σ_r min{B_r,tau} ≤ Σ_{r∈E} B_r + (d−|E|)tau ≤ (1 + d − k_min)F(B)`. Nothing requires `E = D`. Zero-output case (`F=0 ⇔ tau=0`) correct. Verified.

**Rate `d−k_min+1` and §5 specialization (lines 79–81).** For all k-subsets, `tau = B_(k)`, the k smallest contribute themselves (sum `F`), the rest contribute `tau ≤ F`. Total `F + (d−k)tau ≤ (d−k+1)F`. `k=d` efficient, `k=d−1` factor two. Verified.

**Sharpness (lines 89–92).** Example (k−1 zeros, d−k+1 ones): `F=tau=1`, total `d−k+1`. Correctly scoped to this rule and to the all-k-subsets family; no all-mechanism lower bound asserted. Sharpness for general `R` is not claimed, which is appropriate.

**Comparison with frozen general bound (§6, lines 96–107).** `d−k_min+1 ≤ d` always; improvement over `min{d, n√(2/(n+1)), 1+2√d}` claimed only conditionally. Arithmetic for `d=n=4^h`, `k_min=2^h`: `n−√n+1` exceeds `n√(2/(n+1))` for `n≥4` (e.g. `n=4`: 3 vs ≈2.53), so "weaker" is correct. The no-gate-bypass statement follows.

## Scope limitations

- `composition_threshold_check.py` (§7) is not in the packet; no claim about its behavior is assessed.
- The "recursive four-block technology `f_h`" is referenced but not defined here; that it is a unit-coefficient form with `k_min=2^h` is taken from the file, not verified.
- The claim that the rule is "independent" of prior literature was not assessed and no novelty is inferred, per task.
- The theorem addresses only the unit-coefficient subclass of the contract's technology class; it does not bear on arbitrary row-coefficient forms (the file states this correctly, lines 111–114).

## Verdict

**No findings in reviewed scope.** Monotonicity for arbitrary vector underreports, the zero convention, coalition coverage via the bottleneck row, the budget bound via a possibly different min-sum row, the `d−k_min+1` factor, and its rule-specific sharpness are all correctly proven; comparison with the frozen general bound is logically accurate and appropriately modest.
