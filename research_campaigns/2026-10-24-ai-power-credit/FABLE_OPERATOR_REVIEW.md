**Provisional verdict: no substantive error in the two exact formulas under the declared hypotheses; one concrete missing hypothesis in the financing-scope paragraph (lines 43–49).**

## Findings

**1. (Medium) Financing scope silently requires all-action feasibility in every state — OPERATOR_MENU_BOUNDARY.txt:44–47.**
`E[Q_robust(state)]` is only defined if `C_a(w) >= 0` for every permitted `a` in every state `w`. The file's own negative-C boundary (lines 39–40) says that if any `C_a < 0` the problem has *no* feasible allocation at all, not a zero receipt. So in a multi-state version, a single state containing one infeasible operator makes the entire contract infeasible, and the expectation is undefined rather than reduced. The model has no default/outside outcome (liquidation value, non-participation payoff) to assign in that case, so the "worst-case expected receipts" formula needs the explicit hypothesis "for all `w` and all `a ∈ A(w)`, `C_a(w) >= 0`", or a stated default action. Verification: construct two states, state 2 with `V=1, b({1})=2` from the file's own counterexample; check that no `q(·,·)` satisfies all constraints.

**2. (Low) Coalition family mismatch — OPERATOR_MENU_BOUNDARY.txt:15–16 vs MODEL_CALIBRATION.txt:33,37.**
The menu file says "all declared owner coalitions"; the LP in L2 (line 37) ranges over "every nonempty S". If the declared family is a proper subset, `tau_a` must be computed over that same family, otherwise the upper bound `x(N,a) >= tau_a` (line 33) is not implied. Harmless if the family is always the full family; should be stated.

**3. (Low) `1+r > 0` not restated — line 47.** Required for the division; L1 states it, the menu file does not.

**4. (Low) `Q_control` is stated under a stronger hypothesis than needed — lines 21, 26–28.** Under creditor control only the chosen action must be feasible, so `Q_control = min(D, max_{a: C_a>=0} C_a)` is well-defined whenever at least one `C_a >= 0`. The current "assume initially all `C_a >= 0`" is sufficient but obscures that the robust and control regimes have different feasibility domains — which is itself the substantive content of the negative-C boundary.

## Checked and found correct
- Upper bound `q(a) <= C_a` from `x(N,a) >= tau_a` and budget identity: correct.
- Attainability: `q(a) = Q_robust`, owner vector = LP optimum plus excess `C_a - Q_robust >= 0` to one owner. Lower-only constraints and `x >= 0` are preserved; budget `x(N,a) = V_a - Q_robust` is exact. Needs `m >= 1`, which is assumed.
- Negative-C claim (lines 39–41): if `tau_a > V_a` then `x(N,a) <= V_a < tau_a` contradicts the LP bound, so infeasible even at `q = 0`. Clamping would indeed be wrong.
- Calibration: `tau = 2`, `C = (10, 6)`, `Q_robust = 6`, `Q_control = min(8,10) = 8`, owner payments `(6, 2)` each `>= 2`; `V_2 = 1` gives `C_2 = -1`, infeasible. All arithmetic checks.
- L2 dual, additive case, core case, and the `m=3` witness (`tau = 3/2`, primal/dual match) check.

## Scope limitations
Reviewed only the two supplied files as static text; no tools, no execution. Did not assess novelty or literature comparison (lines 58–64). Did not review L1, L3, L4 beyond what the menu file depends on. Cannot verify any statement about CoreWeave or CoopGPT.

## Verdict
**Findings** — one concrete missing hypothesis (per-state, per-action feasibility, or a default outcome) in the financing-scope paragraph; the two exact formulas and the negative-C boundary are correct as stated under the declared assumptions.
