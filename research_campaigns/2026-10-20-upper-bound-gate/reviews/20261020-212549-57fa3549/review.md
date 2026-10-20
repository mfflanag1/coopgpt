## Provisional verdict
**Findings (all minor/precision; no error invalidating the lemma).** I re-derived the section‑5 identity from the dual balance in `inputs/FINITE_AND_ALL_PROFILE_DUAL.txt` and obtained exactly
`L-D = E + Σμ_e a_e − Σλ c_(p,S) − Σσ u_(p,i)`, with `E=Σν_p[p_p·B_p−F(B_p)] ≥ 0` by weak duality — the budget‑excess sign is correct (excess *hurts*, so `E=0` is what the price lemma buys). Sections 2–4 survive my checks; I found no counterexample. The most important gap is a scope/precision one in the §4 construction (zero‑μ edges), plus an unverified claim of reach for the terminal‑budget hypothesis.

## Findings

1. **§4 proof, lines 82–85 — "every outgoing comparison" overstates §3 (Low, fixable in one line).** §3 (lines 53–54) guarantees `b_C(l)≠0` only for *retained positive‑μ* edges. If the DAG retains μ_e=0 edges, `w·b_C(l)` can be 0 with positive numerator `p_h·b_C(h)−F(δ_e)`, so `t_l` is undefined. Fix: delete all μ_e=0 rows first (changes no g, L, D) and define the DAG on supp(μ). The conclusion (lines 69–71) already quantifies over positive‑μ edges, so no result changes. *Verification:* check whether §1's "comparison graph" is defined on supp(μ) or on all admissible rows in Q.

2. **§1 line 15 — DAG property assumed, not proved (Low).** It is true: δ_e=0 with componentwise monotone members and fixed outsiders forces l=h, so every nontrivial edge strictly increases Σ_a B_p,a, precluding cycles. Since the reverse topological induction in §4 rests entirely on this, the one‑line argument should be stated rather than inherited.

3. **§2 lines 21–24 — empty‑coalition comparison case unstated (Low).** If all members are zero at both endpoints the coalition empties; this can only happen when l=h (changed owners ⊆ C), i.e. a trivial self‑row already excluded. Worth saying, since the §3 step tacitly needs retained C nonempty.

4. **§5 lines 92–94 — identity is full‑OUT specific (Low).** The derivation substitutes `d_e=F(δ_e)`. Under TCWM (`d_e=0`) an extra `−Σμ_e F(δ_e) ≤ 0` term appears; harmless (it weakens L−D), but §3's TCWM remark (lines 56–58) sits next to an identity that does not hold verbatim for TCWM.

5. **§4 lines 61–63 — reach of "terminal budget support" is unevidenced (Evidence gap, not an error).** No certificate family satisfying the hypothesis is exhibited, and no argument shows whether the known ratio>1 / √(s/6) lower certificates have budget profiles that are tails of positive‑μ edges. Without that, the lemma may be vacuous on the certificates that matter. *Verification:* inspect the stored lower‑bound certificates for outgoing positive‑μ edges at ν>0 profiles.

6. **Standing hypothesis, §3 line 40 — "nonnegativity of resources" should be stated as `b_i(p) ≥ 0` per owner (Low).** §3 and the "g ≤ 0" sharpening both need per‑owner nonnegativity (not just nonnegative aggregates); it is forced by finiteness of singleton coverage rows `F(b_i(p))`, but CONTRACT's "arbitrary real report boxes" invites the opposite reading.

## Scope limitations
Snapshot only: no execution, no access to the five‑profile obstruction file, `budget_price_relaxation`, `signed_followup`, or `ATTACK_AND_GATE.txt`. Claims about consistency with those (§5 lines 106–110, §6) are unverified. Novelty/history unchecked (file disclaims it).

## Verdict
Findings as above; the lemma's stated content (local erasure, simultaneous zero‑low replacement, unchanged L/D and g≤ν, reverse‑topological shared prices, E≥0 sign) is **mathematically valid in reviewed scope**, with items 1–4, 6 as precision repairs and item 5 as the substantive missing evidence. The note's disclaimer of any improved funding bound is accurate.
