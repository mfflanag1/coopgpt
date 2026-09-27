# Review: final section “The original target is protected even when the bonus shrinks” (`DIAGONAL_SUBDIVISION_NO_GO.md` lines 66–84)

I traced every claim in the new section against the source matrices as defined in `source_family.py` (`construct`), with team order (a,b,c,d), edges ab=A, bc=C, cd=M·I, ad=B, and w′ = A(a,b)+C(b,c)+B(a,d)+M·1_{c=d}.

## Source matrix nonzeros used (from `source_family.py` lines 17–25)

- C(L_s,L_s)=1 for s=0..q
- For s=1..q: A(O_s,O_s)=2, B(O_s,O_s)=2, C(R_s,R_s)=1, A(O_s,R_s)=2, B(O_s,L_s)=2, C(R_s,L_s)=1, C(L_{s-1},O_s)=1
- All other entries zero. Note A and B have nonzero rows only at O_s; C has nonzero rows only at L_s and R_s. Diagonal totals (q+1)·1 + q·4 + q·1 = 6q+1, matching `T` in the verifier.

## Checks of the claimed partial matching (lines 70–79)

Team values:
1. (O_s,R_s,L_s,L_s), s<q: 2+1+2+M = 5+M ✓ (q−1 copies)
2. (O_q,R_q,R_q,L_q): A(O_q,R_q)=2, C(R_q,R_q)=1, B(O_q,L_q)=2, c≠d → 5 ✓
3. (L_{s−1},L_{s−1},O_s,O_s), 1≤s≤q: 0+C(L_{s−1},O_s)=1+B(L_{s−1},O_s)=0+M = 1+M ✓ (q copies)
4. (L_q,L_q,L_q,R_q): 0+1+0+0 = 1 ✓
5. (R_s,O_s,R_s,R_s), s<q: A(R_s,O_s)=0, C(O_s,R_s)=0, B(R_s,R_s)=0, c=d → M ✓ (q−1 copies)

Sum: 5(q−1)+5+q+1 + M[(q−1)+q+(q−1)] = 6q+1+(3q−2)M. With T(M)=6q+1+(3q+1)M this is exactly T(M)−3M ✓. Team count (q−1)+1+q+1+(q−1)=3q=m−1 ✓.

Disjointness / unmatched players, per sector:
- a: O_1..O_q (groups 1,2), L_0..L_q (groups 3,4), R_1..R_{q−1} (group 5) → only R_q missing ✓
- b: R_1..R_q (groups 1,2), L_0..L_q (groups 3,4), O_1..O_{q−1} (group 5) → only O_q missing ✓
- c: L_1..L_{q−1} (1), R_q (2), O_1..O_q (3), L_q (4), R_1..R_{q−1} (5) → only L_0 missing ✓
- d: L_1..L_{q−1} (1), L_q (2), O_1..O_q (3), R_q (4), R_1..R_{q−1} (5) → only L_0 missing ✓

q=1 specialization: groups 1 and 5 empty; teams (O_1,R_1,R_1,L_1)=5, (L_0,L_0,O_1,O_1)=1+M, (L_1,L_1,L_1,R_1)=1; 3 teams, total 7+M = T(M)−3M = (7+4M)−3M ✓; unmatched a_R1, b_O1, c_L0, d_L0 ✓.

## Checks of the derived bounds (lines 80–84)

- H_(c,L0) ≤ 3M: summing the 3q full-team core inequalities gives matched players ≥ T(M)−3M; efficiency (core total = T(M), proved earlier via the diagonal matching + cover p^M for all M>0) gives the four unmatched players ≤ 3M; nonnegativity gives x_{c,L0} ≤ 3M for every core point, hence for the whole-core ideal. Core nonemptiness for every M>0 is supplied by lines 58–60 (p^M), so the ideal is well defined ✓.
- Floor x_(c,L0) ≥ M/4: follows from existence of a core point with all coordinates ≥ M/4 (p^M for 0<M<2, line 60; p for M≥2, lines 19–32) plus the leximin-min argument at line 32 ✓. The interpolation itself is sound: w_M(t)=w_0(t)+M·1_{c=d} is affine in M, p^0 covers at M=0 with total 6q+1 (row maxima: A rows 2q, B rows 2q, C rows 2q+1 — verified against the nonzero list), so the convex combination covers at M with total 6q+1+mM ✓.
- Ratio ≥ (M/4)/(3M)=1/12, M-independent, hence valid for M=M(q)→0 ✓. The auxiliary bound H ≤ 1+M from the diagonal team (0+1+0+M) is also correct ✓.
- The closing scope caveat (different target under shrinking bonus not excluded) is appropriate and consistent with what is proved.

## Findings

None. I found no correctness defect in the reviewed section.

## Scope limitations

- Only lines 66–84 were reviewed for correctness; lines 1–64 were used as context and their internal claims (in particular line 32’s leximin floor argument and line 60’s interpolation) were spot-checked only insofar as the final section depends on them.
- `source_family.py` does not exercise the four-sector market; no code in the packet verifies the 3q-team matching. Verification was by hand from the matrix definitions. Suggested verification: for q∈{1,2,3} and several M (including M<1/2 where 3M<1+M), enumerate all m⁴ teams to confirm T(M)=6q+1+mM, confirm the listed 3q teams are disjoint with the stated values, and solve the core LPs to confirm max x_{c,L0} ≤ 3M and leximin x_{c,L0} ≥ M/4.
- No tools were run; no novelty assessment was made.

## Verdict

No findings in reviewed scope.
