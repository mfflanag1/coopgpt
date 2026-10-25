**Provisional verdict: no findings of error in the reviewed scope.** The charging lemma (§1) and disjointness argument (§4) are, as far as hand-checking of the packet allows, correct; the most important observation is that the result depends on two assumptions the file uses but never states explicitly (precise "global one-layer" definition, and that replacement comparisons are also restricted to |C| ≤ s = 2).

## Findings

**F1 (Low — missing explicit assumption) `COVERAGE_PRESERVATION_OBSTRUCTION.txt:44-45`.** The lemma's only non-trivial step is "global one-layer support makes h a head with NO outgoing comparison," giving `nu_h >= incoming_(h,i_j)`. The term "global one-layer" is never defined in the packet. The proof needs exactly: within each piece, every profile that is the head of some comparison has zero outgoing comparisons (a_j itself may be a head, in which case `lambda <= nu_(a_j)` directly). If the intended architecture allows a head to also emit comparisons, the inequality on line 45 fails. Suggested verification: add the one-line definition to §1.

**F2 (Low — unstated hypothesis) `:30-31, :143-145`.** H_s(a) is defined via comparisons with |C| ≤ s, and disjointness (§4) uses that a_g→z changes three owners. This only works if replacement pieces are bound to the same s = 2. With s ≥ 3 the sets A_s(a_g) all contain z and (1) collapses. The RESULT paragraph should say "feasible global one-layer certificates **at the same protection limit s=2**."

**F3 (Informational) `:13-15`.** "Coalition labels … may change" is ambiguous as to whether it includes coverage labels. The lemma needs the retained row to have a coalition containing some owner (any nonempty S_j suffices), so a coverage label change that keeps a nonempty coalition at a_g is still covered; a weakening that removes the row is not — consistent with §6, but worth stating.

## Verified by hand (no execution claimed)
- Balances §3: at a_g all zero; b_g: v_g = −1/2; c_g: w_g = −1; z: (1/2,1/2,1) ≤ nu_z = 1. Admissibility of all four edges at |C| ≤ 2 holds; each d_e = F(delta_e) = 1.
- L = m/2 + 2m = 5m/2, D = 6m, f_(a_g) = 2(3m−3)+3 = 6m−3; (m/2)(6m−3)/(6m) = m/2 − 1/4 ≥ m/4 for m ≥ 1. Matches EXACT_CHECK.json for m=1 (1/4), m=2 (3/4), m=64 (127/4).
- Lemma chain: `lambda ≤ nu_(a_j) + outgoing_(a_j,i_j) ≤ Σ_{q∈A_s(a_j)} nu_q` (grouping edges by head; one-layer gives `nu_h ≥ incoming`), then monotonicity `f_q ≥ f_(a_j)` since admissibility forces h ≥ l on all rows (protected members ≥, outsiders identical). Disjointness prevents double charging within a piece; aggregation over pieces is linear. Valid.
- §4 for arbitrary real legal profiles: any q ≥ a_g, a_h coordinatewise is ≤ z by the boxes and ≥ 2 everywhere, so q = z; z ∉ A_2(a_g). Valid.
- All-profile K = 1 (§2): `min_r b(h) − min_r b(l) ≥ min_r[b(h)−b(l)]` summed over C gives F(delta) because rows are private; coverage exact. Valid.
- §5 upper witness: coverage pieces feasible (1/2 ≤ 1/2), cost (m/2)(6m−3), objective m/2; o→h piece: `-m ≤ nu_o = 0`, `m ≤ nu_h = m`, d_e = 2, objective 2m, cost 2m. Total/D = m/2 + 1/12, L' = L. Valid.

## Scope limitations
- No execution; checker and JSON only hand-cross-checked at three m values.
- Definition of "global one-layer" and the admissibility conventions taken from `FINITE_AND_ALL_PROFILE_DUAL.txt` §1/§3 only.
- Not assessed: novelty, funding lower bounds, or whether the "flexible coverage" architecture can succeed (§6 explicitly leaves this open).

## Verdict
No findings of mathematical error in the reviewed scope; two assumptions (F1, F2) should be made explicit in the statement before the result is relied upon.
