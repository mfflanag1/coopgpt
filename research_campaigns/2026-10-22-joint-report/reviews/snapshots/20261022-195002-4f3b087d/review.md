**Provisional verdict: no findings in reviewed scope** (conditional on the inherited q-ary inputs, which were out of scope). The power-r KKT/convexity certificate, multiplier signs, eventual threshold, and additive-owner reduction all check out algebraically; I found no breakdown near r=1 or for r>2.

## Findings

No correctness findings. Verification record of what was checked:

**Primal feasibility (lines 51–56).** With D=d+h, p=h/D, z=1/D: retained own row 2p+(d−h)z=(2h+d−h)/D=1; off row p+dz=1; total 2p+(Q−1)dz=C_Q. Independent of r. ✓

**Stationarity / multiplier derivation (lines 58–76).** Lagrangian stationarity is x_i^{r−1} = (λ-weighted incidence) − τ + ν_i. Veto/focal (marginal 1): p^{r−1}=λ−τ. Neighbor (marginal a0): z^{r−1}=λa0−τ. Subtracting gives λ(1−a0)=p^{r−1}−z^{r−1}, matching line 60. Outside: ν=τ−λb. ✓ Sign chain: ν>0 ⇔ λ(1−b)>p^{r−1} ⇔ p^{r−1}(a0−b)>z^{r−1}(1−b) ⇔ h^{r−1}(a0−b)>1−b, using (p/z)^{r−1}=h^{r−1}. ✓ τ>0 follows from ν>0, λ>0, b>0. ✓

**Eventual threshold (lines 40–48).** (A): a0−b ≥ δ−1/m with m>h≥8Q(Q−1)=2/δ, so a0−b>δ/2 strictly. (B)·(A) gives h^{r−1}(a0−b)>1>1−b since b>0. For r≥2, h^{r−1}≥h=2/δ at j=1 ✓; for 1<r<2, threshold j grows like (8Q(Q−1))^{1/(r−1)−1}, finite for each fixed r. No r-dependence enters the constant. ✓

**Direct convexity certificate (lines 79–89).** ∇Φ(q)_i=q_i^{r−1}; the decomposition a−τ1+ν_vec reproduces p^{r−1}, z^{r−1}, 0 on the three coordinate classes. For feasible y: a·y≥λ (rows with λα_R>0 have demand 1, Σα_R=1), −τΣy≥−τC_Q needs τ≥0 ✓, ν·y≥0 needs ν≥0 ✓. Equality at q (tight rows, tight budget, ν·q=0). Strict convexity of x^r on [0,∞) for r>1 gives uniqueness; gradient exists at 0 for all r>1. ✓ p=h/(d+h)=1/(2Q+5). ✓

**Additive reduction (lines 91–112).** C_Q=(2Q²+2Q−2)/(2Q+5) matches both forms (Q=3 → 2). C(1+A)−A=C_Q ✓. Singleton forces y_A≥A; mixed coalitions reduce to old cover + y_A≥A; excess strictly reducible. 1+A=(C_Q−1)/(C−1), C_Q−1=(2Q²−7)/(2Q+5), hence n·p/(1+A)=n(C−1)/(2Q²−7). ✓ Constant independent of r and j.

## Scope limitations

- Not verified (inherited, declared out of scope): existence of the row mixture α with the stated marginals (focal 1, neighbors a0=(d−h)/[(Q−1)d], all outside exactly b=1−β); "every off-focal row has ≥d neighbors"; a0=1−μ_old; δ=1/[4Q(Q−1)] being the source's actual margin for general Q (only Q=3 is consistent with the quadratic note's a0=9/20, b0=49/120); 0<b<1; exact production realization of deletions.
- Low-severity note: the power note relies on explicit δ, whereas the quadratic note cites only inequality (I). If the source proved (I) without a uniform δ, line 23's δ needs a citation to the source's actual margin. Suggested verification: confirm FINAL_ENVELOPE_OBSTRUCTION.txt Part II defines β0=μ_old+δ with this δ for all Q≥3.
- C=1 case deferred to the all-core-selector result, per instructions.

## Verdict

**No findings in reviewed scope.** The r-generalization preserves the identical primal vector; all r-dependence is confined to the eventual condition (B), which is correctly handled as a fixed-r, growing-j statement.
