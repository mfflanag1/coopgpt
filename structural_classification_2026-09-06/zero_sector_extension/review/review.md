# Review: ZERO_SECTOR_TRANSFER.md (with SOURCE_FAMILY_PROOF.md as supporting evidence)

I re-derived every step of the extension argument by hand and re-verified the source family proof it depends on. Details below.

## Findings

### F1 (Low) — `tau > 0` asserted without hypothesis in the general theorem
**ZERO_SECTOR_TRANSFER.md:29** writes `tau = max_(z in C) min_i z_i > 0` as if it were a fact of the general setting. Nothing in the standing hypotheses (lines 7) implies positivity; a market with a permanently-zero-ideal old player has `tau = 0`. The derivation of `t <= k*tau/K` (line 29) and of the first-face description (line 33) does **not** need `tau > 0`, but the claim "this attains the upper bound and is a positive full-core point" (line 31) does. For the triangle application `tau = 1/[3(q+1)] > 0` from the source proof, so nothing downstream breaks.
*Verification:* state `tau > 0` as a hypothesis of the "positive full-core point" sentence, or note that when `tau = 0` the extension forces `R = 0` (since `R/k <= z_i = 0` for the zero-ideal player) and everything degenerates consistently.

### F2 (Low) — Wording in the uniformity argument
**ZERO_SECTOR_TRANSFER.md:13** says each team cover "is tight at a core point." The argument requires tightness at **every** extended core point (which holds: all extended payoffs are nonnegative, the matching is perfect, and its worth equals the extended grand worth `T`). The math is right; the phrasing understates what is being used. The swap argument itself is correct: for teams `t1` (label `j`) and `t2` (label `h`) in new sector `a`, the two tight equations for `t1` before and after the swap differ only in `q^a_j` vs `q^a_h`, giving equality. `m = 1` is trivially covered.

### F3 (Informational) — Convention dependency is correctly flagged but cannot be verified from the packet
**ZERO_SECTOR_TRANSFER.md:3, 47** condition the conclusion `c(G) = 0` on the allowed-graph model permitting zero matrices on permitted edges. The document is explicit that this fails under a positivity requirement. The packet does not contain the goal's model definition, so I cannot confirm the convention; the conditional statement is honest. See scope limitations.

No correctness errors found. Items I specifically checked and found sound:

- **Grand worth stays `T`** (line 9): projection of extended matchings to old matchings; old optimal matching can be taken perfect (nonnegative values, equal sizes) and completed with any bijections to new-sector labels. ✔
- **Entire-core affine description** (lines 15–21): necessity — `z_i = p_i + R/k` gives `z(team) = p(team) + R >= w(team)`, `sum z = sum p + mR = T`, `z >= 0`; coalitional inequalities follow by summing team covers plus nonnegativity, so `z ∈ C`, and `p_i >= 0` is exactly `z_i >= R/k`. Sufficiency — reverse construction is nonnegative, efficient, covers every extended team, hence every coalition (worth = integral matching of full teams). This is the full coalitional core, not a subset. ✔
- **Ideal preservation** (line 25): `p_i <= z_i <= H_i`; `q = 0, p = z` attains. Works for zero ideals too (`H_i^ext = 0`). ✔
- **First face** (lines 29–33): `q_a >= t`, `R >= ell*t`, `z_i >= t + R/k >= Kt/k` ⇒ `t <= k*tau/K`. Attainment with `q_a = t*`, `z >= tau`: `p_i >= tau - ell*tau/K = t*`. Face characterization: `R <= k(tau - t*) = ell*t*` combined with `R >= ell*t*` forces every `q_a = t*`, and then `z_i >= t* + ell*t*/k = tau`. ✔
- **Ratio scaling** (line 35): old target fixed at `tau` on `F` ⇒ extended payoff `tau - ell*tau/K = k*tau/K` on the whole new first face; leximin lies in the first face; ideal unchanged ⇒ ratio scales by exactly `k/K`. ✔
- **Triangle application** (lines 39–47): with only the three triangle matrices nonzero, the pair-additive `K`-team value equals `A + B + C` of the projection, matching the extension hypothesis. `K(3q+1)` players, entries in `{0,1,2}`, `T = 6q+1`, `t* = 3*tau/K = 1/[K(q+1)]`, ideal 1, positive full-core point. The four-vertex enumeration (paw, diamond, K4 contain triangles; P4, K1,3, C4 do not) is correct. ✔
- **Not dummy-player invariance** (line 51): correctly distinguished — new players receive `t* > 0` on the first face and change the productive team structure.

**Source family (SOURCE_FAMILY_PROOF.md), re-verified:** nonzero-entry count `8q+1`; diagonal values 1/1/4 totaling `6q+1`; both `u` and `y` sum to team values; all `u` coordinates `>= tau` (extremes at `b_{L_q}`, `c_{L_0}`, `c_{O_1}`); every mixed-triple case in both tables (including the observation that `A`/`B` rows are nonzero only for `O_s` labels, and `C_{O_s,L_s} = C_{R_s,O_s} = 0`); partial matching `N_s, E_s` is disjoint with value `6q`; `|U| = 3q+3`; inequality (1) forces `U`-coordinates to `tau` on the first face; `H_{c_{L_0}} = 1` from tightness of the diagonal `L_0` team plus witness `y`. No errors found.

## Scope limitations

- The definitions of `c(G)`, "protection constant," the allowed-graph model, and the "all-tree theorem" giving `1/4` for P4 and K1,3 (line 47) are not in the packet. I checked internal consistency, not those external claims.
- Whether the goal's model treats a zero matrix on a permitted edge as within scope (F3) cannot be determined from the supplied files.
- No tests or computations were executed; all verification is by hand derivation on the supplied text.
- Novelty/priority is not assessed, per instructions and per the document's own disclaimer.

## Verdict

**No substantive findings in reviewed scope.** The uniformity-by-permutation argument, the exact affine description of the entire extended core, exact ideal preservation for old players, the whole-first-face mapping `q_a = t*`, `z ∈ F`, and the `k/K` ratio scaling are all correct under the stated hypotheses (equal sizes, nonnegative values, pair-additive extension with zero new matrices), including the edge cases `m = 1`, zero ideals, and integral worth. The only remarks are a missing `tau > 0` hypothesis for the positivity clause (F1), a wording imprecision (F2), and the acknowledged, unverifiable dependence on the zero-matrix convention (F3). The triangle-containing-graph vanishing conclusion follows from the (independently re-verified) source family, conditional on that convention.
