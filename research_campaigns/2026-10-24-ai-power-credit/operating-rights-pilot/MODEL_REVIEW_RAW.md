**Provisional verdict: no incorrect equality found in reviewed scope; two hidden hypotheses and one unverified structural claim.**

Most important: the equivalence at MODEL_COMPARISON.txt:20–21 is correct *only because* `c` is assumed to vanish from every constraint and from every party's failure-state cash position. That assumption is asserted, not derived, and the note's own hedge (line 22) does not list the specific case most likely to break it.

## Findings

**1. Hidden hypothesis — who pays `c` in the failure state (Medium).** Lines 20–21: replacing `a*Delta` by `a*Z*(Delta-c)` is a pure objective substitution. Equation (2) as written has no vendor failure-state liquidity/limited-liability constraint, so the substitution is valid within the stated program. But the vendor's failure payoff becomes `a*Z*(Delta-c) - f`; if the paper's Appendix derivation of (2) relies on vendor failure-state resources (e.g., to fund `f`), a cash cost `c` paid at the time of use can enter the constraint set even though it is "paid only if access is successfully used." Line 22 excludes "costs paid upfront… or affecting budget/IC constraints," which is circular: whether `c` affects a constraint is exactly what needs stating. *Verification:* state explicitly that `c` is paid by the vendor from the realized `Delta` (netting, not a separate outlay), or cite the appendix step showing no vendor failure-state resource constraint.

**2. `P_V = P_M + Delta` is not carried through (Low–Medium).** Line 17 lists `P_V = P_M + Delta` and two inequalities in `P_V` as maintained assumptions. Under `Delta_eff`, either `P_V` is unchanged (then `P_V ≠ P_M + Delta_eff`, breaking a stated identity) or `P_V` is redefined (then `p*R + q*P_V > I_0` may fail). Line 22 hedges generically about "social-efficiency assumptions" but does not name this. Not an error in the reduced-program equivalence, since (2) does not contain `P_V`; it is an incomplete hypothesis list. *Verification:* add one sentence stating which branch is taken.

**3. "Compact feasible set" unverified (Low).** Line 21 relies on compactness. The constraints at lines 12–14 bound `t` above (`mbar`) and `f` above (via constraint 2 and `t ≤ mbar`), but no lower bound on `t` appears. Compactness is irrelevant to the maximization because `mu ≥ 1` makes the objective increasing in `t`, so the claim is harmless but as stated unsupported. *Verification:* either cite `t ≥ 0` from the paper or drop "compact."

**4. Payoff formula — checked, correct.** On the binding face `t + p*w = q*f - Gamma`, objective = `(mu-1)*t - Gamma + q*a*Delta_eff`. Constraint 1 must bind: with `t = mbar`, `w = R-k`, `f = 0`, slackness would require `Gamma < 0`, contradicting `G_0 > 0`. With `Delta ≥ c`, `a = 1` is weakly optimal and `q*Delta_eff` is correct in both `Delta_eff > 0` and `= 0` cases. Line 21 holds independently of the paper's Proposition 1.

**5. Joint-rights section (lines 24–27) — logically sound, no overclaim.** The nonimplication examples are valid; the equivalence statement at line 25 is conditional on "encode every relevant condition" and hence tautological but correctly flagged as such. Line 26 correctly disclaims any issuer mapping.

**6. Novelty.** No novelty claim is made (lines 2, 19, 22, 30); nothing to flag.

## Scope limitations
- Cannot verify line 5 (source inspection, page 12) or line 8 (access "enters the objective, not the reduced financing constraints"); finding 1 depends on this.
- Did not inspect the paper's binding-constraint proof; finding 4 is my own re-derivation from the supplied program.
- No files beyond the single snapshot; no execution.

## Verdict
**Findings** — no incorrect equality in the parameter-substitution step; hidden hypotheses on the payer/timing of `c` (1) and on `P_V` (2) should be made explicit before the reduction is cited.
