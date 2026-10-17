**Provisional verdict: no substantive findings in reviewed scope.** The proof's every step uses only `F >= min(P,G)` (never the old equality), and the derivative/coverage/funding chains check out by hand. Most important observation: correctness of the combined Θ(M^(1/4)) statement rests on the lower bound's bounded-report domain being a sub-case of the upper's all-nonnegative-profile guarantee — this is consistent, but the lower's own §4 still states the stale O(M^(1/3)) gap.

## Findings

**1. (Low — documentation) Stale rate claim in lower file.** `UNRESTRICTED_COMMON_CAP_QUARTER_POWER_LOWER.txt:91-94` says "remaining general rate gap is now Ω(M^(1/4)) versus O(M^(1/3))". The upper (line 11-12) supersedes this. If both are frozen as the combined claim, the lower should carry a pointer, or the pair reads inconsistently. Verification: text edit only.

**2. (Low — informational) Combined statement quantifier is correct but narrow.** Upper gives a single mechanism working for *every* fixed mixed-owner model (line 5-6); lower exhibits *one* model (R pure power owners bounded 1/R, pure branch owners bounded 1). So inf-over-mechanisms of sup-over-owner-models is Θ(M^(1/4)) for this common-cap family. It says nothing about any single fixed owner model's rate, nor rank-3 LPs generally. The file already disclaims this (lines 125-130); I flag it only so the root does not promote it further.

## Steps verified by hand (no discrepancies)

- (4): `g_j <= min(a_j,b_j)` ⇒ `F >= min(P,G)`; `r >= C/M`. Funding §5 uses only this direction: `r<=1 ⇒ G>=P ⇒ F=P` (valid since also `F<=P`); `r>1 ⇒ F>=G`.
- Coverage `r>C`: `G<P/C` ⇒ no branch capped ⇒ `g_j=min(a_j,b_j)` ⇒ `g_j/a_j+g_j/b_j>=1`. `max_{x>1}(1-1/x)/sqrt(x)=2/(3√3)` at `x=3` — correct, so `h+f>=1`; weak LP duality gives coalition coverage. Case `r<=C`: `h=1` since `C>=1`, coalition output `<= s_P`.
- a_j restoration (8): `Z'` formula correct; `g_j'=1 ⇒ g_j=a_j ⇒ Z'=1+s_bj/b_j>=G'`; `f'r'Z >= -2rf'G'` uses `Z<=2G`, `r'<=0`; `f-2rf'` is 0 on the √ branch, 1 on the constant branch.
- P restoration (9): `G'=t/C`, `G>=Pt/C ⇒ r'>=0`, `Pr'<=r`; `s_P h'r' >= Ph'r' >= rh'`; `h+rh'` is 1 or 0. ✓
- Parameter: `C^4=16M/27 ⇒ C^2=4√M/(3√3)`, so second entry is exactly `1+C`; integer `C` gives `C+2`. ✓
- Zero faces: `G→0`: total `(C+2)G`; `P→0`: `f·2G = 4√(PG)/(3√(3C)) → 0`. ✓
- Implementation: `rad=4P/(27CG)` equals `f^2` on the √ branch; `h=min(1,CG/P)`; zero conventions match. `zero_two` squaring + sign check is sound.

## Scope limitations

- Did not execute the checker; `sign_two` interval guard and its "independently checked" status taken on the packet's word.
- Lower-bound proof only spot-checked ((4)–(6), product identity, asymptotic constant); not a full re-audit.
- Cannot confirm novelty or priority.

## Verdict

**No findings in reviewed scope** beyond the minor documentation inconsistency. The quarter-power upper is internally sound; together with the lower it establishes Θ(M^(1/4)) for the uniform-over-fixed-owner-model TCWM funding rate on this common-cap family, and nothing broader.
