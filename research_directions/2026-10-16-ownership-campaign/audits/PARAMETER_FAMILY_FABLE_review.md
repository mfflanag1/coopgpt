**Provisional verdict: no findings in reviewed scope.** Every changed inequality I rederived checks out; the most delicate step (the nonmaximum-long polynomial `C(a,v)`, line 157) is exactly correct and its constant coefficient `a(45a−4)` is where the lower endpoint is forced.

## Findings

No invalid steps or counterexamples found. Items below are confirmations of the critical steps plus two exposition-level remarks.

**Verified by independent rederivation (file `RATIONAL_PARAMETER_FAMILY_THEOREM.txt`):**

- L53–55: `f'`, `f''=9a²/(5D³)`, `f'(1)=(3/10)(1+a)≤1/2` iff `a≤2/3`. Correct.
- L98–110 (PF_bounds 1/16): `B(a,v)` expression, sign of `∂_aB ∝ v²−a(2−v)(1−v)`, closed form `(2−v)²(v+2)/120` at `a_*`, `147/2560` at `v=1/4`, `a_*(1/4)=1/21<4/45`, and `P4(v)=16−56v−95v²+1176v³+984v⁴` from `24v(8+41v)(v+2)(1−v)≤(4+41v)²`. All correct; both interval bounds (`≥1`, `=10941/2000`) correct.
- L138–158 (PF_long): `H'` sign `N=−f'(s)w(w−2R)+2Rh`, `N'=−f''w(w−2R)−2wf'≤0` (the `2Rh'=−2Rf'` term cancels into `−2wf'`), endpoint values `2/15`, `1/5`, reduction to `3v/(2v+1)`, and all five coefficients of `C(a,v)` recomputed from `9D(5D+v²)−[2a+(1−a)v](2+3v−3v²−2v³)`. Exact match; discriminant `−2376` correct. At `a=4/45` the inequality is tight to first order in `v`, consistent with Section 11.
- L188, L209: margins `1/2160` and `2/45` arithmetic correct (`1/10−43/432=1/2160`). Thin but exact.
- L239–248: difference identity `f(L)−f(s)=(3/(10b))(L−s)[1−a²/(D_LD_s)]`, derivative factor `3bs+2−3a`, and `Q(1)` numerator `5a²+(6a−4a²)v+(3−3a−a²)v²` equals `5D²−v(2−3a)[2a+(1−2a)v]`. Correct; `2−3a≥0` is genuinely used only here, matching Section 12.
- L255–259: both-active expression and slope `−7/8` correct; reduction at `λ=s` to the inactive case is legitimate because that expression was shown nonnegative for all `λ≤L`.
- L332–334: funding derivative sign is algebraically identical to PF_long (via `1−t=Rt`), so the Section 3 reuse is not circular.
- L340: `32(1+s)³−27(2s+1)²=(2s−1)²(8s+5)` correct.
- L361–368: `f_{a0}`, `g_{a0}`, `J(s)` fully expanded and match; `J(2/3)=16/27`, `J(1)=−114`, `J'(2/3)=−40`, `J''` discriminant `−198625680`. Rough evaluation gives `J(0.679)≈0` and `g≈0.1288`, consistent with stated decimals (not certified to 16 digits here).
- L391: `Y_a'(1/2−u)/u→1−4/(45a)` via `t−2/3≈4u/9`, `f''(2/3⁺)=9/(5a)`. Correct.
- L409–410: limiting derivative equals `(L−s)[1/2−Q(L)]`, so negativity for `L→1` follows from `Q(1)>1/2`. Correct; cell assumptions (k=0, L active, aux inactive, owner strict maximum) hold for small δ.

**Exposition-level remarks (not errors):**

1. L16–18 "if and only if … all actual mixed owners": both necessity profiles use pure owners (zero accounts) and the unrestricted domain. Under fixed eligibility restrictions excluding them, necessity is not asserted. If "mixed" means strictly positive accounts, a one-line perturbation remark (strict negativity of the derivative persists) would close the gap. Omitted hypothesis statement, not a mathematical gap.
2. L110 "including v=0,1 by continuity": the case `v≥1/4` already covers `v=1`; fine.

## Scope limitations

- Water-cell identities, dominant-cap lemma, and (RT_F) accepted as supplied dependencies; I rechecked the β formulas from the water equation but not the concentration envelope.
- No numeric tool execution; decimal `1.1288005100532479` verified only to ~4 significant digits.
- Cell-finiteness/continuity gluing (Section 7) taken as inherited from the accepted proof.

## Verdict

**No findings in reviewed scope.** The claim "truthful iff `4/45≤a≤2/3` within this family, best factor ≈1.12880051" is supported by the supplied proof.
