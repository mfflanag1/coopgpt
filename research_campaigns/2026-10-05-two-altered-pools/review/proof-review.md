**Provisional verdict: no findings in reviewed scope.** I rederived every identity and inequality in TWO_POOL_THEOREM.txt by hand; none fails. The most delicate step (Lemma 3, edge C, r=2) is correct with exact equality, and the budget case split is exhaustive.

## Findings

No errors found. Verification record (so the reviewer's checks are auditable):

- **Ratio identity (L21, L47).** From the definitions, `delta_s - z_s = (r²−r−2rs+s)/r²` and `b_{s+1} = (r−1)(r−1−s)/r²`. Dividing gives exactly `(1/(r−1))·[1 − s²/((r−s)(r−s−1))]_+`. Denominator positive for s ≤ r−2. Hence `0 ≤ q_s ≤ 1/(r−1)`, `a_{r−1}=0` (`delta−z = −(r−1)²/r²`).
- **Lemma 2.** `F(x)=T_x(2−(x+1)/r)` in region 1 and `x+(r−x)T_x/r` in region 2 both reduce correctly; the two agree at `delta_x=z_x`; `delta_x−z_x` is strictly decreasing in x so there is a single transition; both derivative formulas are ≤ 2. (i) holds in both regions ((r−g)/r ≥ 1/r since g ≤ r−1).
- **Lemma 3.** A: new−old = `(1−q_s)c_s/2 ≥ 0`. B: new−old = `(e−e')c_g ≥ 0`, valid when a_h=0 (e'=0). C: `(1−e')b_{g+1} ≥ ½(r−1)a_g ≥ a_g ≥ (1−e)a_g` needs r ≥ 3; r=2 gives `a_0=b_1=1/4, e=e'=1/2`, exact equality. D: old `(1−e)c_g ≤ c_g` = new. Case boundaries (s ≤ r−2, h ≤ r−2, g ≤ r−2, h=r−1) partition all low→1 edges in the two-altered family; tie at r−1 and one-to-zero edges are included. Zero products only zero the advanced pool's weight and never appear in a denominator.
- **Budget.** Case 1: `d/(r−1)^d` decreasing for d ≥ 2, and `2r ≤ (r−1)²` iff r ≥ 4. Case 2: slack `T_g(g+1)/r ≥ 2/r ≥ 1/(r−1)` for r ≥ 2. Case 3: `F_1 = 2(2r−1)(r−1)/r²` (a_1>0 for r≥3 since r²−3r+1>0), difference `(2r−1)(r−2)/r²`, and `2r²−5r+2 ≤ 2r²−2r`. Case 4: 13/8 ≤ 2 and 125/72 ≤ 2 recomputed. The four cases exhaust all integer (r,g,h), r≥2, 0≤g<h<r.
- **Coverage (Lemma 1).** Lowering reports lowers every `c(S∩N_j)` hence every `v(S)`; R^j unchanged; convexity closes. Correct.
- **Both change directions** (ahead pool advancing, behind pool advancing, including arrival at a tie) are handled; the family is closed under these moves.

## Scope limitations

- The `H_i/k` floor claim depends on `H_i ≤ M_i` via "every original efficient core allocation has x_i ≤ M_i"; the definition of H_i is not in the packet, so I cannot confirm the floor beyond the inequality `x_i ≤ M_i` (which is valid).
- The one-pool covering proof and `sum_pool M_i ≤ T` are imported from FINITE_FAMILY_ESCAPE.txt; I checked those as stated there, not the earlier source.
- No finite exact checks were run by me; all verification is by-hand algebra on the supplied text.
- The result is correctly scoped as a finite binary-profile assignment (reports in {1/r,1}, ≤2 altered pools); it says nothing about real-valued reports, ≥3 altered pools, or a minimax lower bound, and the file states this.

## Verdict

**No findings in reviewed scope.** The product-weight formula is an exact extension on the full labeled ≤2-altered-pool family: boundary preserved, coverage, all own-report edges monotone, total ≤ 2T, fairness top-up ≤ 3T, for all k≥2, r≥2 (r=2,3 included).
