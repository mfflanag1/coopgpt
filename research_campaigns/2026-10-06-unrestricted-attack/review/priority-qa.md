**Static review — no tools used, no files opened, no searches run. Everything below is based solely on the supplied text (result.md, manuscript.tex, HIERARCHY_LOWER_CANDIDATE.txt, SOURCE_COMPARISONS.txt). I cannot verify any URL, theorem number, or page reference in external sources; those are flagged as unverified.**

## 1. Independent check of the hierarchy proof (what result.md calls "checks out")

I re-derived the candidate proof from the supplied text; result.md's conclusion that it is internally sound is correct.

- **Symmetrization.** Averaging over pool and within-pool permutations: coverage is preserved because `avg_σ y(σS)(σc) ≥ avg_σ v_{σc}(σS) = v_c(S)`; the budget is preserved linearly; own-monotonicity is preserved because each term `y_{σ(i)}(σc)` is monotone in the coordinate `c_i`. Correct.
- **Values.** Type-h total is `hm + (m−h)`; `T = m` at the base because `n_0 ≥ 1`, and `T = m` at every destination `S_h` because `n_0 ≥ 2` covers the `h = 0` case. Correct.
- **Eq. (1).** The changed owner becomes one of `(h+1)(n_{h+1}+1)` symmetric high owners at `S_h`; budget gives `(h+1)(n_{h+1}+1) z_{h+1}(S_h) ≤ Bm`; own-monotonicity gives `x_h(S) ≤ z_{h+1}(S_h)`. Only the changing owner's payment is transported. Correct.
- **Eqs. (2)–(3).** `C0` is feasible since every pool has `m−h ≥ m−d ≥ 1` low owners; worth 1. `C1` needs `m−h ≥ m−d+1`, i.e. `h ≤ d−1`, satisfied for `h<d`; worth `min(m−d+1, m) = m−d+1`. Correct.
- **Eq. (4).** Weights `(m−d)` and `d` give coefficient `(m−d)+d(m−d+1) = A` on every `h<d` term and exactly `n_d[(m−d)x_d + d z_d]`, the full type-d pool payment, on the last term. Correct.
- **Elementary family.** `A = d(d+2)`, `n_h/(n_{h+1}+1) < 1/L`, `A·H_d/L ≤ Ad/(2Ad) = 1/2`, so `B > A/(m·3/2) = (d+2)/3`. Correct.
- **Sharper family.** `q_d ≥ 2` for `d ≥ 2`, so `m = dq_d > d`. `A/m = d+1−d/q_d = (1−o(1))d`; bracket `≤ 1 + H_d/(1+log d)² ≤ 1 + 1/(1+log d)`; `log L = (2+o(1))log d`; `log k_d = (2+o(1)) d log d`. With `d = ⌊(1/2−ε) log k/log log k⌋`, `log k_d ≈ (1−2ε) log k < log k`, so `k_d ≤ k`. Padding with type-d pools only lowers the `h=d−1` ratio. Coefficient `1/2` follows. Correct.
- **Upper coefficient 1.** Theorem `thm:upper` gives `R_k + 1/log R_k` with `R_k ~ log k/log log k`. Correct.

Consistency with the manuscript's feasibility theorems: the hierarchy family has every pool altered (in normalized form all low owners sit at `1/m`), so it lies outside both `𝒟_1` (one altered pool) and the bounded-`m`-altered-pools domain of `thm:continuous`. No contradiction; result.md could have said so explicitly.

## 2. Findings on result.md's prior-art analysis

**F1 (precision defect — Huang et al. reduction direction).** result.md states "a weighted multi-glove game is the max-flow game on serial layers of parallel edges" (correct: flow = min over layers of capacity sums) and then concludes "Huang et al.'s impossibility is prior art for the exact-B=1 endpoint." The specialization runs the wrong way for that inference: a multi-glove lower bound transfers *to* max-flow games, but a max-flow counterexample only applies to multi-glove games if the counterexample network is itself a serial-parallel layer network. result.md does not state the structure of Huang et al.'s core-selection counterexample. Either (a) confirm the example is serial-parallel, or (b) restate: Huang et al. are prior art for the B=1 endpoint *in the broader max-flow model*, while the multi-glove-specific B=1 impossibility is already implied by the manuscript's own `thm:unrestricted`. Unverifiable here; must be fixed in the write-up.

**F2 (unverified external claims).** The following are asserted with specific locators I cannot check statically: Huang et al. §§1.1, 2.2, Prop. 1, Thm. 1, §4.2 MC-not-in-core statement, and the characterization of their "CM" axiom; Immorlica–Mahdian–Mirrokni Definition 3.3 / Theorem 3.6, pp. 10–12, and the claim that their proof "carries the payoffs of already-present edges"; Moretti–Norde Def. 3.1/Thm. 3.2; Brânzei–Solymosi–Tijs Def. 1, Thms. 2 and 5. The logical separation arguments given (other-owner vs own-report monotonicity; zero-capacity encoding only controls the entering edge's own payoff) are valid *if* the cited definitions are as described. The ledger's observation that the manuscript's upper is bounded at `k=2` while IMM's obstruction is already linear on two layers is a sound sanity check that the hypotheses differ.

**F3 (correct distinctions).** The three-way separation — own-report monotonicity / other-owner population monotonicity (PMAS, cross-monotonic, type-monotonic) / fixed-game stability (cost of stability) — is stated correctly and matches the manuscript's model section. No reduction from any listed source to the hierarchy theorem is claimed, and none is apparent to me from the supplied descriptions.

**F4 (Brânzei–Solymosi–Tijs omission).** Flagging this as a citation defect is appropriate given the "multi-glove" + "type monotonic" terminology; the stated reason it does not subsume (population counts vary in unweighted games; remaining owners are controlled, not the changing owner) is a valid missing-hypothesis argument. Its existence/locator is unverified here.

**F5 (minor inconsistencies / omissions).**
- The ledger (item 4) and result.md cite Bachrach et al. arXiv:0907.4385 (2009), but manuscript.tex cites the JAIR 2018 "Bounds on the Cost of Stabilizing…" paper. These are different papers; the manuscript bibliography and the ledger should be aligned.
- result.md does not state explicitly that the lower bound needs owners-per-pool `m ≈ d log d ≈ log k`, so the regime of *fixed* pool size `r` remains open. "Both grow" is mentioned, but the open fixed-`r` question should be listed among what the theorem does not settle.
- The criteria require recording the time bound; result.md records access limitations (Tilburg 403) but not time spent.
- Manuscript line references (24, 40–42, 62–67, …) are approximately consistent with the supplied file but I did not verify them exactly.

**F6 (manuscript-revision list).** The listed defects are correct: the abstract, introduction, §4 closing remark, and "What remains open" all state the unrestricted bound is only 2 and divergence is unresolved; `cor:minimax` explicitly says it is "not the unrestricted optimum." All must change if the hierarchy theorem is promoted, and the theorem must be stated in the manuscript proper.

## 3. Priority assessment (static)

- **Established prior art (per supplied descriptions, unverified externally):** the weighted multi-glove game and total balancedness (Moretti–Norde); truthful efficient core selection failure in max-flow games (Huang et al., subject to F1); cross-monotonic approximate profit sharing with a linear max-flow obstruction under *population* monotonicity (IMM); PMAS/type-monotonic schemes for multi-glove games (Brânzei–Solymosi–Tijs); fixed-game stabilization by subsidy (Bachrach et al.).
- **Priority-unconfirmed:** the specific theorem — nonnegative coalition-covering payments, monotone only in each owner's own capacity, have worst-case factor `Θ(log k/log log k)` with lower coefficient `1/2` and upper `1`, when pools and owners both grow. No supplied source states it or reduces to it. Search silence is not novelty evidence; result.md says so correctly.

## 4. Verdict

**Revise (minor).** The mathematical audit of the hierarchy proof is correct and complete; the model distinctions are correct; the overall priority conclusion is appropriately hedged. Required edits before acceptance: (i) fix the direction-of-reduction statement about Huang et al. (F1); (ii) mark external theorem/page locators as inspected-but-unverified-by-this-review, since this review cannot confirm them (F2); (iii) add the fixed-`r` open regime, the Bachrach citation mismatch, and the time-bound record (F5). No finding here challenges the claimed `Θ(log k/log log k)` lower bound itself.
