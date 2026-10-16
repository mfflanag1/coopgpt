**Provisional verdict: no invalid steps found in the reviewed proof/verifier logic; the certificate data itself (certificate.json) is not in the packet, so the numerical claim (968 rectangles < 13/8) is unverified here.**

Most important point: every inequality the 13/8 reduction needs that was previously derived under `P<=H` has been correctly re-derived or replaced with a `pi`-based version; I could not find a step that silently reuses a raw-`P` bound.

## Findings

**1. (Low) Redundant/duplicate row — harmless.** `GENERAL_THIRTEEN_EIGHTHS.txt:93,99` and `verify_certificate.py:70,74`: row 2 (`-CU*M+Z<=0`) is implied by row 13 (`-CU*M+Z<=-dl`, `dl>=0`). No soundness effect (weak duality with nonnegative weights tolerates redundant valid rows), but the text's "13 rows" count includes one that adds nothing.

**2. (Low) Verifier strictness vs. soundness.** `verify_certificate.py:84,87` require stored `residual`/`upper` to equal the recomputed Fractions exactly. This is fine for integrity, but note that the *only* load-bearing check is line 88 (`upper < 13/8`); the equality checks are consistency, not evidence. Worth stating in the note so an auditor does not read "residual replay" as an extra proof step.

**3. (Informational) Direction checks that I verified by hand and found correct:**
- Signed Taylor directions: `T_25(x) <= exp(-x) <= T_24(x)` for `x>=0` (remainder sign `(-x)^{n+1}`), used consistently at lines 31–35, 59–60, 67.
- `lambda <= lambdahi` (line 83): needs `q>=qlo` and `1+1/u-1/S >= 1+1/u-1/lo >= 0`; holds since `S>=lo>=1`, `u<1`.
- `mu <= muhi`: needs `K<KU=EU-1` (`e<EU`), `eta<=qhi/lo`, `A>=Alo>0` (checked line 62).
- Saving `b>=blo`: `S+delta <= hi+dh`, so `exp(1-S-delta) >= exp(-(hi-1+dh)) >= T_25`.
- `L` is decreasing in its argument (derivative in `s=sqrt(1-v)` is `2e^{s-1}s/(1+s)^2>=0`), `z_i g_i<=1/4`, `K^2<3` ⇒ `L>L(3/4)=4/(3√e)>4/5 ⇔ e<25/9` (line 39).
- Empty-cell condition `lo > Pi+CU-dl` (line 53): from `S<=Pi+Z=Pi+CM-delta<=Pi+CU-dl` with `M<=1`. Correct.
- Deficit rows `CL*M-Z<=dh`, `-CU*M+Z<=-dl`: outer enclosures of `delta=CM-Z`, valid because `M>=0`.
- Coordinate caps `(1,Cbar,1,Cbar,p*Cbar)` and nonnegativity of all five variables (needed for the residual-cap step of weak duality): `v<=1` from `v+zminus<=1`; `t<=p(Z-zminus)<=p*Cbar`.
- High-pi regime: `pi>=51/40 ⇒ P>=pi>1=H`, so GRID_CAP_RANGE_BOUND's hypothesis `P>=H` holds; bound is increasing in `m` and decreasing in `pi>=1` (derivative ∝ `-(pi+const)+1<0`), so checking `(M,pi)=(1,51/40)` suffices.
- Moments (2): each of `v+Z-M<=1`, `v+Z<=3/2`, `v+zminus<=1`, `zminus<=Z`, `M<=Z<=CM` depends only on hardware/local roles and the set J (where `p_i+z_i<1` forces `pi_i=p_i`), not on `P`. `S>=1` needs `P+M>H`, which the regime ordering guarantees.

## Scope limitations
- `certificate.json` (weights, `u` values, residuals) and `verification.json` outputs are not inspectable; I cannot confirm the 968 bounds or the 1.6205 maximum.
- Not in packet: subset hardware-role lemma (`(4/3)M+v-zminus<=4/3`), JOINT_ROLE_TRADEOFF (`L<=min(M,1/2)`), NEGATIVE_GAP_SAVINGS, power-bottleneck `C²` theorem, PD3 support inequality. These were stated as previously reviewed; I did not re-derive them.
- I did not execute the script.

## Verdict
**No findings** of invalid steps in the reviewed proof text and verifier logic (one redundant row, one presentational note). **Insufficient evidence** for the numerical certificate itself, which lives in files outside the packet.
