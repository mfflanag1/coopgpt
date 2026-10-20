**Provisional verdict: no invalidating findings in reviewed scope.** I independently rederived both claims and found no error. Most important concrete observation: the two-terminal lemma's load-bearing steps are correct but §3 silently uses two unstated facts (existence of the shared `w`, nonemptiness of `T`), both of which I verified do follow from the stated hypotheses.

## Findings

**1. (Info/low) layer_followup.txt:58, 61 — unstated but true intermediate steps.**
The existence of nonnegative `w` with `gamma_(a,i)=-w_i`, `gamma_(z,i)=+w_i` is asserted. It follows from (i) `sum_p gamma_(p,i)=0` (each edge contributes ±mu per member), (ii) (BT) at interiors, (iii) `z` a sink ⇒ `gamma_(z,i)>=0`. Similarly "T is nonempty" and `M>0` need: self-rows removed ⇒ every positive edge has some strict coordinate increase, and every edge lies on an a→z path (concatenate backward/forward paths in a DAG with unique source/sink) ⇒ `b_i(z)-b_i(a)` dominates each edge's increment. Suggested verification: add these two lines; no repair needed.

**2. Coordinate-cut conservation, endpoint-row legality, telescoping — all check out.** Lower-side summation gives `sum_(crossing, j in C_e) mu_e = w_j` for *every* owner j, hence `w_j<=w_i` (1)–(2); so `w_i=M` on T (3), and total-crossing-weight `=M` with each j∈T attaining `M` forces `T⊆C_e` on positive crossing edges (4). Direct rows are legal: changed owners `T⊆C_e`; `C_e\T` unchanged hence weakly increasing; non-members unchanged since `T⊆C_e`. Telescoping (5) is `sum_(p,i) gamma_(p,i) b_i(p)` under (BT); (6) is superadditivity + homogeneity. `gamma` is preserved pointwise, so `g=lambda`-incidence`+gamma`, `sigma`, `nu`, `D` are genuinely unchanged — the comparison-only vs. full-`g` distinction (line 16, lines 38–40) is handled correctly.

**3. (Scope) layer_followup.txt:50 — `L<=rD` is not verifiable here.** The "retained rank-r one-layer theorem" and `r` are external; the componentwise claim additionally relies on profile-disjointness of components (true) and on "isolated profiles use efficient static prices" (asserted only). Treat only the contraction normalization as established by this packet.

**4. Both failed-normalization examples: scopes accurate.** §5: `F=1` on all `p_k`, balances, `g<=nu` (q>=2), `L=1`, `D=q`, RC residual `(q,q,q)` all reproduce; (7)'s `>=qm` follows from per-label unit flow + every comparison containing R + `nu_sink >= incoming R weight` + `f=1`. Correctly labelled not a lower bound (ratio is 1/q). §6: all four shortcuts change 3 owners; dual feasible with `L=8`, `D=12` (<1 ratio) — correctly labelled a local legality obstruction only.

**5. (Low) layer_followup.py:72–91 vs. .txt:220.** `branched_cut_check` models only two coordinates; the K row of "R1 owns A,K" never appears, so the text's "one changed owner owns two resource rows" is not exercised by the code. Also `all_checks_passed=True` and `original_L/D` are literals, not computed; RC is checked only as a residual, not against `lambda b + sigma b` (I verified that decomposition by hand: it holds).

**6. Capped fractional counterexample is correct.** Static cap: usage `<= Gamma_a W` for any retained-activity plan, and `sum_C min(b_ia,Gamma_a V) >= min(sum_C b_ia, Gamma_a V) >= ` plan usage; discarding zero-profit columns is value-neutral; `V=0` handled. Example: `V=2`, cap 2, reports unchanged; all 16 worths invariant; for `x,y>=1` the D-anchor cancels and `phi = E[(U_P-yU_Y)_+] = 1/(6y)`; `1/3 → 5/18`, loss `1/18`, with `F(delta)=0`. Hence `y_i(h)-y_i(l)=phi` difference exactly for any `H(v_b)`.

**7. (Scope, correctly disclosed) CAPPED...STOP.txt:37–39.** The rejection covers only `c*phi_i(btilde)+H_i(v_b)`. A correction reading the aggregate capacity vector escapes it: `c_low=(1,2,1)` vs `c_high=(1,5/2,1)`. Also "the known individually monotone, covering fractional rule" (line 5) is an external attribution not checkable here.

## Scope limitations
Snapshot only; no execution. Unverified external dependencies: the rank-r one-layer theorem, OLD R1, and the covering/monotonicity of `phi`. check_capped_fractional.py hardcodes `phi` (lines 33–34); the integral is proof-only — suggest symbolic/Monte-Carlo confirmation and an assertion that `x,y>=1` (where the formula is valid).

## Verdict
No findings invalidating either claim in reviewed scope; items 1, 3, 5, 7 are presentation/scope gaps, not errors. No general upper-bound improvement is claimed or implied by these two results.
