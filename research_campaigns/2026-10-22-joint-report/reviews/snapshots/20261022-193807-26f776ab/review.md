**Provisional verdict: no findings in reviewed scope.** I re-derived every displayed inequality and the three worked examples; all check out. The most important point to record is a scope limitation, not an error: the budget factor β is proven only for finite min-linear representations (Section 2 and the Lipschitz step in Section 3 both use a coefficient row), not for the contract's general concave technology, and the documents say so explicitly.

## Findings

**No correctness findings.** Verified steps:

- `composition_weighted_threshold_comparison.txt:36-44` — coverage: for a sum-minimizing row, `a_r B_r ≤ a·B = F(B)` and `a_r ≤ w_r`, so each Y-term ≥ `a_r b_ir`; summing over S gives `a·(Σ_S b_i) ≥ F(Σ_S b_i)`. B_r=0 forces b_ir=0. Correct; same for τ with a bottleneck-minimizing row.
- `:46-53` — budget: `min{z,T} ≤ cz+(1−c)T` with `c_r=a_r/w_r ∈[0,1]` and the row chosen so `a·B=F(B)` yields `(1+d_eff−Σ a_r/w_r)F(B) ≤ (1+d_eff−κ)F(B)`. The separate `d_eff F(B)` bound is immediate. β ≥ 1 since κ ≤ d_eff.
- `:30-34` — own-monotonicity: F and `b_ir/B_r` are both nondecreasing in the own vector (0/0:=0 is consistent: 0 → 1 when b_ir becomes positive with others zero).
- `:72-84` — U ≤ Y: with `g(t)=F(C−t e_r)` concave on `[0,B_r]`, `g(0)−g(sB_r) ≤ s(g(0)−g(B_r))`; `C−B_r e_r ≥ 0` because the r-th coordinate is untouched before its removal; `F(C)−F(C−B_re_r) ≤ min{w_rB_r, F(B)}` via monotonicity/nonnegativity and the row at `C−B_re_r`. Telescoping gives U_i. Correct.
- `:87-89` example: F=3/2, τ=1, X^τ=(1,1,0,1), U=(1/2,1/2,0,3/2). Verified; neither dominates.
- `composition_threshold_group_scope.txt:9-18` — factoring `min{w_r, q/B_r}` out of the coalition sum is valid for B_r>0; the zero convention matches both sides. Monotonicity in A follows. Example `:33-37`: with b_1=(2,0), b_2 moving (0,1)→(1,1), B=(3,1), F=1, U=(0,1), total drops 2→1 at output 1; threshold total 2 at both. Verified.
- `composition_dense_regularization_obstruction.txt` — κ=(2M+1)/(M+1), β_M=1+1/(M+1); τ_M(t,1)=M+1 on `1≤t≤(M+1)/M`; adjusted payment M+1−Mt strictly decreasing; grand-marginal identity `[F_M(B)−F_M(B−b_i)]−MΣb_ir=G(B)−G(B−b_i)`; leftover term `M/(M+1)(B_1+B_2)` unbounded relative to G at B=(t,1). All verified.
- Section 4 span argument: e_r−e_s differences (possible for 1≤k<d) span the zero-sum subspace; nonzero coordinate sum completes R^d; unique activity at (1 on S, 2 off S) holds. Correct.

**Counterexample attempts (none succeeded):** rows {(2,0),(0,2),(½,½)} (κ=½<1) at B=(1,1) gives ΣY=2=βF — tight, not violated. Sum-of-two-smallest, d=3, B=(1,1,0) gives ΣU=2=2F — tight.

## Scope limitations

- `inputs/manuscript.tex` (source of the grand-marginal rule and the generic `min{d, n√(2/(n+1)), 1+2√d}` factor) and `composition_weighted_threshold_check.py` are not in the packet; their contents and the claimed checker results are unverified.
- β is representation-dependent (acknowledged at `:23-26`); no technology invariant is established or claimed.
- The theorem covers finite min-linear F only; the Lipschitz step needs a row, so extension to general concave homogeneous f is not supplied.
- Nothing here bears on the unrestricted rate or the 90-minute gate; the documents correctly disclaim this.

## Verdict

No findings in reviewed scope. The weighted β bound, the U ≤ Y comparison, and the coalition-total monotonicity are correctly proven for finite min-linear forms; the dense-regularization obstruction is an exact counterexample as stated.
