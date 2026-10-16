**Provisional verdict: no findings in reviewed scope (no concrete failure located; derivation checks out step-by-step as far as the packet allows).** Most important observation: the one constraint whose justification is not cited anywhere, `L = sum V_i <= 1/2` (used for `v+Z<=3/2`, LP row 5), is in fact derivable from included material — see Finding 1.

## Findings

**1. Low — `L<=min(M,1/2)` asserted without reference** (`LOW_GRID…txt` line 40). `L<=M` is immediate (`L_j<=m_j` in both orientations). `L<=H/2` is not immediate but holds: hardware-short branch gives `L_j = (rho e^{1-rho}/2) m <= m/2`; local-power-short branch gives `L_j/h <= (1-e^{1-rho}/2)/rho <= 1/2` since `(rho+1)e^{1-rho}<=2`. This is also the `q→0` limit of `JOINT_ROLE_TRADEOFF` (1) with `B=1`. Row 5 is therefore valid; the manuscript should cite the source. Verification: add the one-line derivation or a pointer.

**2. Info — all other rows of (1) re-derived and confirmed.** `M<=1`, `M<=Z<=CM` (branch totals in `[T,CT]`), `S>=min(P+Z,1)>=1`, `S<=P+Z<=1+Z` (`P<=1`), `v<=sum_i(a_i-U_i)=1-Z+L` (needs `d_i>=U_i`, true since `z_i>=U_i`, `p_i>=0`), `v+zminus=sum_J(a_i-p_i)<=1` (J uncapped since `d_i<a_i<=1`), SH1 on the actual subset J with `a_J=P_J+Z_J+G_-` gives `zminus>=v-(4/3)(1-M)`, exact overflow identity `P+Z-S`. Tied owners: `zplus<=Z-zminus` is correctly only used via monotonic increase of both PD2 terms; `G=S-1+v` is exact. LP rows 1–11 in both scripts match (1)/(6) sign-for-sign.

**3. Info — interval monotonicity directions confirmed.** `lambda=1-q(1+1/u-1/S)` with positive bracket: `q>=qlo` and `1/S<=1/lo` both push upward → `lambda<=lambdahi`. `A<=Ahi`, `A>=Alo>0`, `eta<=qhi/lo`, `mu<=3etahi²/(4Alo)`, `Keta<=(7/4)etahi` (`K<19/11<7/4` from `e<30/11`), `b(S)>=(2/5)T_25(exp(-(hi-1+cbar)))` (odd-degree Taylor is a lower bound for all `x>=0`; `c<cbar` from `e>125/46`). `lambda(S-1)<=lambdahi(hi-1)` needs `la>0`, which the verifier requires (line 35). Saving step: `delta=CM-Z in[0,cM]`, `z_ig_i<=1/4`, `L` decreasing in its argument, `L(3/4)=(4/3)e^{-1/2}>4/5`.

**4. Info — weak-duality certificate structure is sound.** Variables nonnegative; caps `(1,Cbar,1,Cbar,pCbar)` all valid (`zminus<=Z<=CM<Cbar`, `t<=p(Z-zminus)`). Verifier recomputes every coefficient from `(lo,hi,u)` with Fractions, does not trust saved rows, checks adjacency/cover/endpoint, strict `8/5`, and max replay. The line-42 check is tautological given line-40 residual definition (harmless). Coefficient directions in row 10 (`Ahi` on the `Z` coefficient and RHS) are the correct upper relaxation of `A(1+Z-S)` with `S>=lo`.

## Scope limitations
- Cannot execute; `low_grid_certificate.json` is not in the packet (only its SHA-256 and `max_upper`). Leading digits of the reported fraction are consistent with ≈1.5782, but the 128 dual-weight vectors were not inspected.
- PD1/PD2, negative-gap saving, SH1, C²F, and the 27/16 high-grid bound are taken as previously audited; I checked only their hypotheses and usage (`P+M>=1`, actual subset J, arbitrary overflow, `u in(0,1)` free per interval), not their internal proofs.
- Boundary regimes (`H=0`, `P+M=H`, `P=H`) are covered by the stated inclusive theorems; not re-verified.

## Verdict
**No findings** of substance in the reviewed scope. The reduction, moment constraints, tied-owner handling, interval coefficient directions, and weak-duality logic are internally consistent; the only gap is a missing citation for `L<=1/2`, which is provable from included lemmas.
