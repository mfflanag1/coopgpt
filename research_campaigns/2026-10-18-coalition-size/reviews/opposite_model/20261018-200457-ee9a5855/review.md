## Provisional verdict: findings (minor-to-moderate; no counterexample found)

Most important concrete finding: the "exact" equivalences (2) and (3) are only *necessary* under the stated contract unless one adds the unstated hypothesis that **every** set of at most `s` actual owners is a protected coalition. `Neg_{s-1}(z;{j})` / `Neg_{s-|D|}(z;D)` pick the most negative entries over *arbitrary* owners `i ∉ D` (line 26–33, 42), and §2 necessity (line 45–47) needs "for each C containing D … |C| ≤ s" to range over admissible coalitions. The contract says only "Protected coalitions C have |C| ≤ s" plus "fixed eligibility"; if eligibility ever restricts *which* ≤s-subsets are protected, the minimizing coalition in (2)/(3) may be inadmissible and the conditions are strictly stronger than TCWM/OUT. Line 28's undefined "every eligible C" is where this slips through.

## Findings

1. **Missing hypothesis / quantifier (moderate), lines 28–33, 38, 45–47.** As above: state explicitly "all ≤s subsets of actual owners are protected." Verification: re-derive the min over the admissible coalition family; if it is a strict subfamily, exhibit a Jacobian satisfying TCWM but violating (2).

2. **Overloaded term "eligible" (low–moderate), lines 51–56.** In §2 sufficiency "eligible" must mean *"(j,a) ∈ J for some j ∈ C"*, not the contract's static owner–resource eligibility. Under the static reading `q_a = min_{j∈C:(j,a)∈J} ℓ_{(j,a)}` is a min over an empty set for rows with no positive C-report, and the dual cover is undefined. The J-based reading makes the argument go through (such rows have aggregate capacity `c_a = 0`, so the activity is unusable). Fix: define the term.

3. **Load-bearing model hypotheses not invoked (low), lines 36–42, 57–60.** Dual feasibility `sum_a A_{a,e} q_a ≥ π_e` must hold for *all* columns; the document only imposes (3) for positive-profit columns of arity ≤ r. This is valid only because (i) all positive-profit columns have arity ≤ 3, (ii) `A ≥ 0`, `q ≥ 0` covers `π_e ≤ 0`, (iii) no positive-profit resource-free columns (else `F = ∞`). Cite these.

4. **Incorrect justification of finiteness (low), lines 81–82.** The limit in (4) is approached from above as `t ↓ 0`, so finiteness needs a *lower* bound — supplied by "payments nonnegative," not by the funding bound (an upper bound). Conclusion stands; the stated reason does not.

5. **Checks that do hold.** Coordinatewise reduction of TCWM (linearity + nonneg cone), the (3) necessity construction (homogeneity of `F` makes the scaled direction locally feasible), the duality step `sum ℓ d ≥ sum q_a c_a ≥ F(c)`, `D ⊆ C ⇒ |D| ≤ s`, the integration over `t ∈ (ε,1)` with `(1-ε)F(sum d) → F(sum d)`, and the §4 counterexample (at `(0,1)`: `Y_{{1}} = 1 > lim = 0`, so (4) is genuinely independent of coverage/funding) all verify on the snapshot.

## Scope limitations

No tools were run; nothing executed or inspected beyond these two files. Smooth-regularization, novelty, LP-synthesis, code and the global O(s) program were excluded. Facewise smoothness, the smooth extension at endowment upper boundaries, and integrability of the Jacobian are assumed, not evidence here; §5's "independently checked regularization theorem" is not in the packet (insufficient evidence for claims depending on it).
