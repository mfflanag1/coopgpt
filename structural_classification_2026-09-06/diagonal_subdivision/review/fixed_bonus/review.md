# Review: DIAGONAL_SUBDIVISION_NO_GO.md §"Family-specific refinement" against source_family.py

## Findings

No correctness defects found in the new section. I traced each claim against the constructor in `source_family.py`; details and two minor precision notes follow.

### Verified claims

**1. Simultaneous diagonal edge optima (line 56).** From `construct(q)` (source_family.py lines 17–25), with m=3q+1, o=3s−2, ell=3s−1, r=3s, prev=left(s−1):

- A: only rows o are nonzero, entries A[o][o]=A[o][r]=2. Row-max sum = 2q; diagonal contributes A[o][o]=2 each → 2q. ✔
- B: only rows o nonzero, B[o][o]=B[o][ell]=2. Row-max sum = 2q; diagonal 2q. ✔
- C (rows indexed by b): rows ell (s=0..q, q+1 rows, C[ell][ell]=1, plus C[prev][o]=1 in some of them) and rows r (q rows, C[r][r]=C[r][ell]=1) have max 1; rows o are empty. Row-max sum = 2q+1; diagonal C[0][0]+ΣC[ell][ell]+ΣC[r][r] = 2q+1. ✔
- M·identity: any perfect matching gets ≤ mM, diagonal gets mM. ✔

Since each a-player, b-player appears in exactly one team of a perfect matching, Σ_teams w′ ≤ Σ_a max A + Σ_a max B + Σ_b max C + mM = 6q+1+mM, attained by (i,i,i,i). So T(M)=6q+1+mM for all M≥0 without the B-range hypothesis. ✔ Consistent with `verify()` line 39 (T=6q+1 at source level).

**2. Row-price cover at M=0 (line 58).** p⁰_a+p⁰_b+0+0 = max_b A(a,·)+max_d B(a,·)+max_c C(b,·) ≥ A(a,b)+B(a,d)+C(b,c) = w′₀(team). Total = 2q+2q+2q+1 = 6q+1 = T(0); nonnegative. ✔

**3. p² at M=2 (line 58).** B entries ∈{0,2}, so B(a,d)−B(a,c)≤2=M holds; source core nonempty (witness u in `construct`, checked by `verify` line 44). Hence the earlier lemma applies, p² ≥ 1/2 coordinatewise, total 6q+1+2m. ✔

**4. Affine interpolation, 0<M<2 (line 60).** With λ=M/2: w′_M(t)=w′₀(t)+M·1_{c=d} = (1−λ)w′₀(t)+λw′₂(t), so (1−λ)p⁰(t)+λp²(t) ≥ w′_M(t). Total = (1−λ)(6q+1)+λ(6q+1+2m) = 6q+1+mM = T(M). Nonnegative; each coordinate ≥ λ·(1/2) = M/4. ✔

**5. Bound M/[4(4+M)] (line 62).** Leximin coordinates ≥ first floor ≥ M/4; every core point is tight on every diagonal team (optimal matching for all M≥0 by item 1), so with nonnegativity H_i ≤ max_j[A(j,j)+B(j,j)+C(j,j)]+M = 4+M (diagonal source teams have worth 1 or 4, from lines 18–28 of the constructor). Ratio ≥ (M/4)/(4+M). Holds for every player including d-players and every q. For M≥2 the earlier lemma gives the same. ✔

**6. Remaining scope (line 64).** Correct: the bound → 0 as M→0, so M(q)→0 is unsettled; the statement claims nothing about other C4 markets.

### Minor notes (low severity, wording only)

- **Line 60, "covers every M-market team because its value and T(M) are affine in M".** The actual reason is that both sides of the cover inequality are affine in λ and the inequality holds at the endpoints λ=0,1 (convex combination). Affinity of T(M) is only needed for efficiency, not for coverage. Suggest rephrasing to avoid a reader inferring that affinity alone implies coverage.
- **Line 64, "the only live parameter regime … is a bonus tending to zero".** Strictly, M=0 exactly (zero-valued cd edge) is also outside the proven bound; the document delegates that case to the earlier "first-face mapping for zero-valued added sectors" (line 52), which is outside this packet. A one-clause cross-reference would close the gap.

## Scope limitations

- I did not execute `source_family.py`; matrix structure was read from the constructor code, and the source-core nonemptiness/optimality facts rely on `verify()` as written.
- The earlier general lemma (lines 17–38) was previously reviewed and is taken as given here; I only checked that its hypothesis (B row range ≤ M) is satisfied where invoked (M≥2).
- Definitions of "first optimal floor", "full leximin", and "whole-core ideal" are taken from the document's usage; I assume the standard meanings (leximin coordinates ≥ max-min floor; H_i = max of x_i over the core).
- No novelty assessment performed, per instructions.

## Verdict

**No findings in reviewed scope.** The family-specific extension to every fixed M>0 is sound: simultaneous edge-wise optimality of the diagonal, the M=0 row-price core point, the affine core interpolation, and the resulting bound M/[4(4+M)] all check against `source_family.py`. Only two minor wording/cross-reference improvements suggested.
