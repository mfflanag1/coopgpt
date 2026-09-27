# Review: C4_VANISHING.md (with SOURCE_FAMILY_PROOF.md and source_family.py as supporting evidence)

I re-derived every step of the C4 argument by hand from the packet, independently of the prose. I did not run any code.

## Findings

No correctness defects found. The items below are informational / low severity.

### 1. (Info) Selective lemma — verified for every mixed full team
Evidence: C4_VANISHING.md lines 15–20. With `w'(a,b,c,d)=A(a,b)+C(b,c)+B(a,d)+D_c·1_{c=d}` and cover `(z_a,z_b,z_c,D_d)`:
- `c=d`: `B(a,d)=B(a,c)`, so `z_a+z_b+z_c+D_c ≥ [A+B(a,c)+C]+D_c = w'`. Exact, no slack needed.
- `c≠d`: `z_a+z_b+z_c+D_d ≥ A+C+B(a,c)+D_d ≥ A+C+B(a,d)`, using `B(a,c)≥0` and `D_d ≥ max_a B(a,d)`. Holds for all `(a,b)`, not just diagonal-block ones.
Applied with `D=2` on `{O_s,L_s}`, `D=0` on `{L_0,R_s}`: `B`'s nonzero entries are `B(O_s,O_s)=B(O_s,L_s)=2`, so these are exactly the column maxima and the hypothesis is met (including the zero columns). Nothing in the lemma requires `D_j>0`.

### 2. (Info) Exact integral worth and shift — verified
`ΣD = 2·2q = 4q`; diagonal full matching value `= T0+ΣD = 6q+1+4q = 10q+1` (line 44). The lifted cover has the same total, so the integral worth is exactly `T=10q+1`. Shift (lines 22–25): each team sum changes by `−t/3·3 + t = 0`; total changes by `−3m·(t/3)+m·t = 0`; nonnegativity needs `z_i ≥ t/3 = τ/4`, satisfied since `min z = τ`. With `t=3τ/4=1/[4(q+1)]`, every coordinate of `p` is `≥ t` (old: `τ−τ/4 = t`; new: `D_d+t ≥ t`).

### 3. (Info) Partial matching values, disjointness, unmatched set — verified
- `N_s=(a_{O_s},b_{R_s},c_{L_s},d_{L_s})`: `A(O_s,R_s)=2`, `C(R_s,L_s)=1`, `B(O_s,L_s)=2`, `D_{L_s}=2` → 7. ✓
- `E_s=(a_{L_{s-1}},b_{L_{s-1}},c_{O_s},d_{O_s})`: `A=0` (A has only O-rows), `C(L_{s-1},O_s)=1`, `B=0`, `D_{O_s}=2` → 3. ✓
- Sector-wise labels: a `{O_s}∪{L_0..L_{q-1}}`, b `{R_s}∪{L_0..L_{q-1}}`, c `{L_1..L_q}∪{O_s}`, d `{L_1..L_q}∪{O_s}` — all disjoint. ✓
- Complements: a `{L_q,R_s}`, b `{L_q,O_s}`, c `{L_0,R_s}`, d `{L_0,R_s}` → `|U|=4(q+1)`, matches line 54–55, contains `c_{L_0}`. ✓
- Value `10q = T−1`, hence `Σ_U v ≤ 1` for every core point. ✓
Consistency check: in `p`, every U-coordinate equals exactly `t` (`a_{L_q},b_{L_q},c_{L_0},a_{R_s},b_{O_s},c_{R_s}` all have `z=τ`; `d_{L_0},d_{R_s}` have `D=0`), so `Σ_U p = 1` — tight, as required.

### 4. (Info) First-face pinning and ideal — verified
Max-min over the core is `≤ 1/|U| = t` and attained by `p`, so the first leximin level is `t`; every leximin-optimal point has all coordinates `≥ t`, and `Σ_U ≤ 1 = |U|t` forces each U-coordinate `= t`. The target is pinned at `t` regardless of later refinements. Ideal: team `(L_0,L_0,L_0,L_0)` has value `0+1+0+0=1`, tight at every core point (diagonal matching optimal), so `H_{c,L_0} ≤ 1`; the unshifted lift of `y` has `y_{c,L_0}=1`. Hence `H=1`, ratio `1/[4(q+1)] → 0`.

### 5. (Info) Source three-sector core covers — independently re-checked
Since the C4 result inherits from `z=u` and `y` being old core points, I redid the case split in SOURCE_FAMILY_PROOF.md lines 56–88: `a∈L/R` rows have zero A and B, leaving the four positive C pairs (sums `1−τ, 1−τ, 1+(3s−1)τ, 1−τ`, plus `u_a=τ`); `a=O_s` with both A,B positive gives the four listed cases (`4, 4+3τ, 5−3τ, 5` vs `w=4,4,4,5`), and with at most one positive `w≤3 ≤ u_{a_{O_s}} = 3+4τ+(3(q−s))τ ≥ 3+4τ`. All hold; totals `(q+1)+q+4q = 6q+1`. The C4 document's dependence is sound.

### 6. (Low) No C4-specific machine verifier is included
`source_family.py` verifies only the three-sector market (products over `range(m)^3`, weights `[5,1]*q`, `|U|=3q+3`). There is no four-sector enumerator in the packet. This does not affect the symbolic proof, but the claim "finite evaluations… corroborate" (implicitly carried over) has no C4 artifact here. Suggested verification: an analogous exhaustive `range(m)^4` cover check for `q=1,2` on `(p, (y,D))`, plus the 2q-team partial matching and `|U|=4q+4`.

### 7. (Low) Selective-vs-uniform distinction is consistent, but the no-go theorem is not in the packet
The construction's dependence on selectivity is real: `D_{L_0}=0` is needed to keep `H_{c,L_0}=1` via the value-1 diagonal team; `D_{R_s}=0` is needed for the shortfall to stay 1 (the `d_{R_s}` are unmatched, so any positive `D_{R_s}` inflates `T` without inflating the partial matching). I cannot check the statement or hypothesis of the "uniform positive bonus no-go" (line 68) since it is not supplied, so the claim of non-conflict is unverified here.

## Scope limitations
- Only the three supplied files were reviewed. The uniform-bonus no-go theorem, the "5/44" finite bound, the priority audit, and any formal definition of `c(C4)` beyond line 7–11 are not in the packet.
- I did not execute `source_family.py`; its logic was read and matches the source proof, but pass/fail is not attested.
- The C4 model assumptions (only full teams produce, arbitrary nonnegative edge matrices, "strict" = every allowed edge nonzero somewhere) are taken as stated in lines 7 and 66; a diagonal `cd` matrix with zeros is admissible under those stated rules, but if the intended C4 class imposes extra conditions (e.g., all edge entries positive, or genericity), that would be a model question outside this snapshot.
- Novelty/priority is not assessed and cannot be inferred from correctness.

## Verdict
**No findings in reviewed scope** (informational notes only). Every step audited — selective lemma for all mixed full teams, exact integral worth `10q+1`, floor shift preserving efficiency and team sums, partial matching disjointness/values/unmatched set with `|U|=4(q+1)`, whole-first-face pinning at `t=1/[4(q+1)]`, and `H_{c,L_0}=1` — checks out symbolically for all `q≥1`. No counterexample or hidden model change found within the stated definitions; the only unverifiable items are external (no-go theorem, absence of a C4 numerical verifier).
