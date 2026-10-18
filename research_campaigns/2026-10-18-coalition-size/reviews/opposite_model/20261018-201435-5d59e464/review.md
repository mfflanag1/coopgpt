## Provisional verdict
**No findings in reviewed scope** for all three results: I found no fatal gap or missing hypothesis in the three frozen proofs as written. The most important concrete item is only a definitional imprecision in the polyhedral certificate's FULL-OUT test (line 112, "eligible actual owner f(a)"), which must mean *row-wise* eligibility `(f(a),a)` is a retained coordinate; otherwise `J_t[i;f(a),a]` is undefined for removed coordinates.

## Findings

**1. Minor / definitional — POLYHEDRAL_CERTIFICATE_THEOREM.txt:111–116.** Line 112 defines `z_i(e,f)=sum_a A_(a,e) J_t[i;f(a),a]`, but line 112's quantifier says only "eligible actual owner f(a)". The dependency (LOCAL_INCENTIVE_SEPARATION.txt:43–45) requires `(f(a),a) in J`. Under the loose reading the term is undefined for owners with `bar_b_(f(a),a)=0` (those coordinates were deleted at line 15–17); under an over-broad reading the synthesis LP gains spurious constraints (conservative, not unsound). *Verification:* restate line 112 as "assignments f with (f(a),a) a retained coordinate", and check the shipped checker's assignment enumerator matches.

**2. Minor / dependency-conditional — POLYHEDRAL_CERTIFICATE_THEOREM.txt:118–124, 133.** Necessity and sufficiency of (7)/(7)+(8) are imported verbatim; I read them as supplied and did not re-derive them. The downstream use is otherwise self-consistent: the derivative bound is applied with a cell-constant Jacobian, so it is valid on lower-dimensional faces of a cell as well as its interior, and the interval-subdivision argument (126–131) is correct (each open subinterval lies in one closed cell's intersection interval).

Checks I did re-derive and found correct:
- Coverage dual (5): dual of (4) with `u>=0` on `H_t b<=g_t`, `p>=0` on `Ax-S_C b<=0`, `b` free gives exactly `H_t^T u - S_C^T p = -a_C`, `A^T p>=pi`, `g_t^T u<=h_C`; sign chain at line 69 is valid, and boundedness/attainment hold because zero-profit columns are removed with `A,pi>=0`.
- Vertex funding equivalence (79–88) via affineness + concavity + `kappa>=0`; zero-output vanishing (95–97) follows.
- Chamber barrier: zero-`a` slice is a full box (needs all endowments positive, `r>=2` — both hypothesized), forcing `h=0` and cross-resource coefficients `0`; simplex relative-interior variation forces `l^a_(i,j)` constant in `j`; `n=1` and `E=T_a` edges are handled. `r=1` genuinely falsifies the conclusion, and the hypothesis excludes it.
- CEA: coverage via bottleneck `t_i^h=b_(i,h)`; Lemma (5) case split is valid without water-level monotonicity; bottleneck-interval telescoping gives `>= min_a D_a`; cover (7)–(9) verified to satisfy the CEA equations (`sum_i min(b_(i,a),L_a)=T_h=E`, `L_a>=0`), with `S_a=∅` admissible; the §6 non-affineness example recomputes to `7/10, 1, 1`.

## Scope limitations
No tools: I could not run the 7 synthesis fixtures, 14 CEA regions, 98 coverage duals, or 90,396 ternary comparisons; those remain unverified evidence. Novelty/priority and the unrestricted-infimum questions are out of scope, as the files themselves state (POLYHEDRAL:200–205; BARRIER:62–65; CEA:143–148).

## Verdict per result
1. Polyhedral certification — no findings beyond the line-112 wording.
2. Production-chamber factor-`n` barrier — no findings; hypotheses (`r>=2`, all-positive endowments, continuity, chamber-affineness) are necessary and stated.
3. CEA factor-`r` full OUT and cover — no findings.
