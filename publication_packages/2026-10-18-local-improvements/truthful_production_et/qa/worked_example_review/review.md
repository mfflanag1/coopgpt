## Provisional verdict: no findings in reviewed scope

I re-derived the example from the mechanism definitions (§"The mechanism", eqs. prod:p–prod:payment) and reproduce every printed number. No concrete error found in the new paragraph (manuscript.tex:295–324 / qa/WORKED_EXAMPLE_INSERTION.tex:1–30).

## Independent derivation (all four masks per profile)

Full profile `b1=(3,0)`, `b2=(0,2)`, `T=min(3,2)=2`; scores `Σ_i B_i(w·b_i)`, first-argmin priority on `V=((1,0),(0,1))`:

| mask (B1,B2) | score w¹ / w² | selected | a₁ | a₂ |
|---|---|---|---|---|
| (0,0) | 0 / 0 → tie | w¹ | min(3,2)=2 | 0 |
| (0,1) | 0 / 2 | w¹ | **2 (raw 3 capped)** | 0 |
| (1,0) | 3 / 0 | w² | 0 | min(2,2)=2 |
| (1,1) | 3 / 2 | w² | 0 | 2 |

So `p₁=T` (both B₁=0 masks select w¹), `p₂=(1-q)T` (T only when owner 1 present), `m₁=(1-q)[f(3,2)-f(0,2)]=(1-q)T`, `m₂=(1-q)[f(3,2)-f(3,0)]=(1-q)T`. Hence `r₁=qT+(1-q)²T=T(1-q+q²)`, `r₂=(1-q)T`.
`M₁=2∫₀^{1/2}(1-q+q²)dq·T = 2T(1/2-1/8+1/24)=5T/6`; `M₂=2T(1/2-1/8)=3T/4`. Total `19T/12`, subsidy `7T/12`. Table values (5/3, 3/2, 19/6, 7/6) and (5/6, 3/4, 19/12, 7/12) follow for T=2, 1.

Underreport profile `b1=(1,0)`, T=1: masks (0,0),(0,1) select w¹ with `a₁=min(1,1)=T`; (1,0) selects w²; (1,1) scores 1 vs 2 → w¹. Same `p`, `m`, `r` in units of T, so the T-scaling in the paragraph is legitimate for *these two* profiles (correctly hedged as "at either displayed profile").

**Cross-checks that strengthen the example:** it satisfies the proof's own identities, `qΣpᵢ = Z−g` (`qT(2−q)=T−T(1−q)²`) and `Σmᵢ=−g'` with `g=T(1−q)²`, `Z=T`; and `R=Z−g−(1−q)g'` holds exactly. Also `r_i ≥ z_i` (e.g. `1−q+q²−q=(1−q)²`), and `C₂(2)≈8.55 ≫ 19/12`.

**Other scoped claims verified:** cap genuinely binds (mask (0,1) raw 3 > T=2; it also binds at (0,0), which is not an error); singleton values are `min(3,0)=0`, `min(0,2)=0`, payments nonnegative, grand coverage `19T/12 ≥ T`; owner 1's payment strictly falls (5/6 < 5/3) with owner 2's report fixed and `(1,0) ≤ (3,0)` componentwise; two-owner Shapley `[f(b_i)+T−f(b_{-i})]/2` gives (1,1) and (1/2,1/2), is efficient, own-monotone and covers singletons by superadditivity of a min of nonnegative forms — so the "not a necessary subsidy" disclaimer is correct and the paragraph makes no sharpness/lower-bound claim. No hidden owner/form/priority/domain change: `V`, priority order, owner 2's report and the full `(R₊²)²` domain are unchanged.

Minor (non-error) wording note: the Shapley formula is stated inside the *proof* of Proposition prod:uncapped, not its statement; "discussed in Proposition~\ref{prod:uncapped}" is a forward reference.

## Scope limitations
- All "DIFF AGAINST HEAD" blocks are empty, so I cannot confirm that manuscript.tex changed *only* by this paragraph.
- `qa/WORKED_EXAMPLE_DIFF.patch` is listed in the packet but not supplied.
- I did not execute `check_worked_example.py`; I read it as evidence (its logic — first-argmin ties, `prob` bit weights, conditional `p`/`m` construction, exact Fraction integration — matches my hand derivation, and its asserted targets are the printed values).
- No source-priority, build, or all-profile claims reviewed.

## Verdict
No findings in reviewed scope.
