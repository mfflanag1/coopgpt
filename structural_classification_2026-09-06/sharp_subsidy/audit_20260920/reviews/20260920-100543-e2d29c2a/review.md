**Provisional verdict: no findings in reviewed scope** — I could not break the Section 6 implication `Q/T ≤ 60g`. The load claim, the averaging step, and all constants check out, with margin. The most important caveat is that the load bound is *contingent* on `x_s < 1−a` (i.e. `L_s ≤ h−1`): if that failed, degree‑two rows would acquire positive headroom `q_i = Lα − β > 0`, would receive extra transfer, and their excluded label would itself be a donor — destroying both "excluded label is a leaf" and `e_i = Δ_s/n_s`. Section 6 asserts this in (6.5) but does not flag it as the load argument's load‑bearing hypothesis.

## Findings

**1. Donor other‑sector load ≤ 1−z_ij — verified (no defect).** MIXED_DONOR §5 defines row *i* (sector *s*) as exactly four mass types. Step 1 gives label‑*d* players `β − z_{i,d}`; step 2 gives `α` to each P‑used player (P is player‑disjoint, so at most once, even when a P‑team repeats a label). Steps 3–4 touch only: the two partners at the excluded leaf `j`; residual players at leaf labels `l` with sector‑*s* used player; and unmatched/used **sector‑s** players (including a donor's sector‑*s* player, load exactly `β−z+α+z = 1`, correctly excluded from the slack in (6.6)). Since donors are internal and `j`, `l` are leaves, non‑*s* donor players get no step‑3/4 mass. Hence load `= β − z + α·[used] ≤ 1 − z`. Verification: re‑enumerate MIXED_DONOR §5 steps 1–4 against the player of each internal label in each sector.

**2. Averaging leaf rows — valid.** `q_i = Lα − (β−δ)` is sector‑constant and positive iff `x_s > 1/5 + a`; degree‑two rows have `q_i = 0` iff `x_s ≤ 1 − a`. Both hold: (6.2) gives `B ≥ 1.48875`, `|x_s − B/3| ≤ √0.003`, so `x_s ∈ [0.4415, 0.5548]`; `n_s/h = B − x_s ≥ 0.93 > 0`. The core is convex, so `y^s` is an original core point, and diagonal tightness gives `Σ_{r≠s} y^s_{r,j} = d_j − y^s_{s,j}` exactly, matching (2.1)'s retained‑payoff term.

**3. Constants — correct, slightly loose.** I re‑derived `Δ_s/h = x_s(B−x_s) − B/5 − a(x_s+B)` and `Γ/h = (4/5)B − 3/5 − (6/5)a + (6/5)c/h` from `2ℓ+n₂=3h`, `n₃ = h(B−1) − 1 + c`, `c = m − 2h + 1`. Jointly optimizing (not the document's decoupled rounding) gives `Δ_s/Γ ≥ 0.273 > 1/4`; `γ_j ≥ 1/5` ⇒ `C_player ≥ Q/20` ⇒ `Q ≤ 60gT`. Section 7's arithmetic (`g ≥ 3/70370`) also reproduces. The `t=4/5` packing is feasible here: `Γ − ΣD_s = h(A(B)+V+(6/5)c/h) + 4B − 6/5 > 0`.

## Scope limitations

- REDUCTIONS.md and SURPLUS_UPPER.md are absent; MIXED_DONOR §5 defers its base capacity proof to the latter. If the actual packing contains teams beyond steps 1–4, finding 1 would need rechecking.
- I did not audit (2.1)–(5.6), the cloning argument, or any LP/SMT/script claim; (6.2)'s derivation was only spot‑checked (q=1,2,3 branches, `min(1,z+g)(5+g)/100 ≤ z+(6/5)g`).
- `Q ≤ 60gT` is conditional on those prerequisites, not independently established.

**Verdict: no findings in reviewed scope.**
