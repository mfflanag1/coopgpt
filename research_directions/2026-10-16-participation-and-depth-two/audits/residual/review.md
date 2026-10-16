**Provisional verdict: no findings in reviewed scope.** All stated coverage, budget, derivative, non-veto and all-profile claims check out against the supplied primitive; the only notable item is a vacuous line in the verifier (low severity, not a correctness defect).

## Findings

**1. Low — `forest/verify_residual.py:32`: vacuous check.**
`if mask==3: require(Q(2)==v, ...)` compares the constant 2 with itself; it never evaluates `y_I + y_A`. The comment says the IA equality is "by cancellation", which is correct symbolically (`(1+q/2)+(1−q/2)=2`), but the script does not corroborate it. Suggested fix: assert `add(y[0],y[1])` has lower bound exactly `2` via exact cancellation, e.g. check `y[0][0]+y[1][1]==2 and y[0][1]+y[1][0]==2`, or simply drop the special case and note the identity is symbolic. Counts toward `checks` either way.

**2. Low — scope of code corroboration.** The script hard-codes the reduced payment formulas (`1+q/2`, `1−q/2`, `q`; Candidate B's `1+(1−β)/2+q(x+β/2)`) rather than implementing the two-input rule and composing it. It therefore certifies the note's algebra and strict inequalities, not that the mechanism as implemented produces those numbers. The algebra itself is verified below, so this is a limitation, not an error.

## Verified statements (hand-checked)

- **Model:** `F = M + min(p,R) = min(H, p+M)`: local activities dominate (same unit profit, no shared power), so `w_j = min(h_j,l_j)` then `sum x_j ≤ min(p, R)`. Correct, also coalitionwise.
- **Coverage:** `(H_i−z_i)_+` sums to ≥ `H_S−z_S`; lemma coverage gives `t(S) ≥ min(a_S,p_S)`; chain to `min(H_S, M(S)+p_S)` uses `z_S ≥ M(S)`. Correct for any owner set/branch count.
- **Budget:** `z_i^h ≤ H_i` (short: `(1−p)h_ij`; long: `p·min(h_ij,T) ≤ h_ij/2`), so `Σa_i ≤ H−Z_h`. Per-branch `min(h_j,l_j) − Z_{h,j} ≤ h_j/2`: short case uses `p ≤ 1/2`; long case uses `ρe^{1−ρ}` decreasing on `[1,∞)` and `ρ ≤ η`, then `η(1+e^{1−η}) ≥ 2` (equality at 1, derivative `1+(1−η)e^{1−η} ≥ 1−1/e > 0`). Case split `p ≤ R` / `p ≥ R` yields `(3/2)C ≈ 1.77591`. Correct.
- **Candidate A example:** branch 1 short hardware `T=1`, `ρ=1+x`, `q=½e^{−x}`; `z=(qx, 1−q, q)`; residuals `(1−qx, q, 0)`, `T_res=1+q(1−x)<2`, `ρ_res=1`, `p_res=½`; `t_I=1+q/2−qx`; `y_I=1+¼e^{−x}` strictly decreasing. Coalition values `{I:1,A:0,B:0,IA:2,IB:1,AB:1,N:2}` and non-veto all confirmed. Deviation is a single own-coordinate decrease, within the primitive's domain.
- **Candidate B:** `z_I^h=0`, `a_A=1−β+βq`, residual total `<2` for all `β∈(0,1]`, `ρ_res=1`; `y_I` and `dy_I/dx = q(1−x−β/2)` correct; negative on `(1−β/2,1)` for every `β>0`.
- **Code:** alternating-series enclosure parity (odd k → lower) correct on `[0,1]`; test points `1−β/3 < 1−β/4` both lie in the negative-derivative window; `e>8/3 ⇒ (3/2)C<57/32<2` valid.

## Scope limitations

- Only the three supplied files; no execution. Lemma in `MIXED_PRIMITIVE.txt` taken as given.
- "No conjectural envelope claim" — none is made; the note correctly disclaims adaptive/other-mechanism repairs. No novelty assessment made.

## Verdict
**No findings in reviewed scope** (one low-severity vacuous check in the verifier).
