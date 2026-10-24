## Result: prior-art scout on financing complementary assets under fragmented control / bundled guarantees

### 1. Source manifest and honest access status

| # | Source | What I actually read | Free link | Version caveat |
|---|---|---|---|---|
| S1 | Hart & Moore (1990), "Property Rights and the Nature of the Firm," *JPE* 98(6):1119–58 | **Original, published scan**, pp. 1123–1156 (pp. 1119–22 not rendered) | [DASH bitstream](https://dash.harvard.edu/server/api/core/bitstreams/7312037c-4b76-6bd4-e053-0100007fdf3b/content) (also [DASH PDF](https://dash.harvard.edu/bitstream/1/3448675/2/Hart_PropertyRights.pdf), [MIT WP 495](https://dspace.mit.edu/handle/1721.1/64099)) | JPE version confirmed by running heads |
| S2 | Hart & Moore (1994), "A Theory of Debt Based on the Inalienability of Human Capital," *QJE* 109(4):841–79 | **Not read this session** (MIT DSpace returned HTTP 429 three times; QJE paywalled) | [MIT WP 592 record](https://dspace.mit.edu/handle/1721.1/64271) → `/bitstreams/821f9877-3834-485c-8bab-074392470958/download` | Mechanism below is from my background knowledge, flagged |
| S3 | Bolton & Scharfstein (1996), "Optimal Debt Structure and the Number of Creditors," *JPE* 104(1):1–25 | **Not read** (Scharfstein Harvard PDF, HBS "Read Now", CEPR chapter all 403; SSRN no download) | [Harvard Scholar page](https://scholar.harvard.edu/davidscharfstein/publications/optimal-debt-structure-and-number-creditors); [JPE DOI](https://www.journals.uchicago.edu/doi/10.1086/262015) | Described via two secondary originals I did read: Bris & Welch NBER w8652 pp. 1, 5–7; Berglöf–Roland–von Thadden pp. 6–7 |
| S4 | Berglöf, Roland & von Thadden, "The Design of Corporate Debt Structure and Bankruptcy," WP Aug 2009; published *RFS* 23(7):2648–79 (2010) | **Original WP, pp. 1–22** (Props 1–6) | [Berkeley PDF](https://eml.berkeley.edu//~groland/pubs/bankruptaugust09.pdf); [Mannheim final w/ appendix](https://www.vwl.uni-mannheim.de/media/Lehrstuehle/vwl/von_Thadden/research/bankruptfinal-withApp.pdf) | RFS version not read; numbering may differ |
| S5 | Banal-Estañol, Ottaviani & Winton, "The Flip Side of Financial Synergies: Coinsurance vs. Risk Contamination," IGIER WP 475 (May 2013); *RFS* 26(12):3142–81 | **Original WP, pp. 1–18** (Props 1–3, Predictions 1–4) | [IGIER PDF](https://repec.unibocconi.it/igier/igi/wp/2013/475.pdf) | RFS version not read |
| S6 | Hansmann & Kraakman (2000), "The Essential Role of Organizational Law," 110 *Yale L.J.* 387 | **Original, pp. 387–410** (Parts I–V.A) | [Yale LJ PDF](https://www.yalelawjournal.org/pdf/386_hxm176pg.pdf) | pp. 411–440 not read |

Adjacent, not counted among the six: Leland (2007) *JF* 62(2) — only the author's [June 2007 slides](https://www.nhh.no/globalassets/departments/business-and-management-science/karl-borch-lecture-series/2007/080607.pdf) read (all 23); SSRN WP 345380 403'd. Squire (2011) 78 *U. Chi. L. Rev.* 605 — abstract only ([Chicago Unbound](https://chicagounbound.uchicago.edu/uclrev/vol78/iss2/3), [Fordham](https://ir.lawnet.fordham.edu/faculty_scholarship/66)); both PDFs 403'd. Bris & Welch (2001) [NBER w8652](https://www.nber.org/system/files/working_papers/w8652/w8652.pdf) read pp. 1–8, used only to characterize S3.

### 2. Exact mechanisms and results (theorem facts)

**S1 Hart–Moore 1990** (control = residual right to exclude; Shapley split of date-1 surplus, eq. (4) p. 1129; investment is in human capital only, Assumption 3 p. 1127).
- Def. "strictly complementary" (p. 1135): $v^i(S,A\setminus\{a_m\}) \equiv v^i(S,A\setminus\{a_n\}) \equiv v^i(S,A\setminus\{a_m,a_n\})$ for $i\in S$.
- **Prop 8** (p. 1135): strictly complementary assets should be owned/controlled together. **Prop 3** (p. 1132): each asset controlled by a coalition or its complement. **Prop 4** (p. 1132): no two agents should have veto power over one asset. **Prop 6** (p. 1133): indispensable agent should own. **Prop 9 + Corollary** (p. 1137): a dispensable agent with no investment — in particular an *outside party* — should have no control rights if stochastic control is possible. **Prop 10** (p. 1138): economically independent → independent control.
- Many-owners result (pp. 1148–49, eq. (9)): with $N{-}1$ users each needing the pipeline $a_1$, control shares/votes only reallocate a fixed budget $\sum_i p_i = N/2$. **This is the formal reason "more owners" adds no mathematics: ownership counts only redistribute marginal-incentive weights under a conservation constraint (eqs. (6), (9)).**
- Explicit exclusions: contingent control / secured debt ("option-to-own contracts") ruled out for simplicity, fn. 10 p. 1129; "payoff uncertainty, risk aversion, and wealth constraints" ignored, so financing/ownership-by-financiers "plays no part," p. 1152.

**S2 Hart–Moore 1994** (not read this session; abstract per MIT record: inability to commit human capital caps what can be owed at any date; repayment schedule depends on return maturity, asset durability and specificity). Background-knowledge mechanism, unverified here: single creditor's only threat is liquidation, so repayment is bounded by liquidation value; more durable/less specific assets → more debt capacity. No multiple-creditor or complementary-asset result.

**S3 Bolton–Scharfstein 1996** (secondary only): two creditors make ex-post renegotiation inefficient → lower payoff to manager in default → deters strategic default, at the cost of inefficient liquidation under liquidity default; optimal number of creditors trades these off (BRvT p. 6; Bris–Welch pp. 1, 5). Bris–Welch pilot (p. 7–8, n=63 SDNY cases): secured-creditor concentration helped secured recoveries — opposite empirical sign to BS96. I could **not** verify the asset-complementarity parameter in BS96 from any original text.

**S4 Berglöf–Roland–von Thadden 2009** (closest formal object to "fragmented lender control"). Model §2 (pp. 8–11): date-0 investment $I$; date-1 verifiable assets $A$, non-verifiable cash $Y\in\{0,Y_H\}$ w.p. $q$; continuation $V$; liquidating $B\le A$ scales continuation **linearly** to $(1-B/A)V$ (p. 9). Contract $(I_i,R_i,D_i,B_i)$: individual foreclosure right $D_i\le A$, collective claims $B_1+B_2\le A$ (p. 10).
- **Prop 1** (p. 14, eq. 8): $\frac{D}{B}D_1 + D - \frac{D^2}{B} \le B_1 \le \frac{D}{B}D_1 - D + B$ ⇒ no asymmetric default in equilibrium.
- Debt-capacity bound (eqs. 22–23, p. 18): $\max (1-q\theta)B + q\theta D \le (1+q)A$; exact iff $\underline V \ge 2A$.
- **Prop 2** (p. 20): financing feasible iff $\varphi(\min(2,t_0))\le A$; debt capacity $>A$ iff $\min(2,t_0)A<\overline V$; can be as low as $A$ "despite the double liquidation threat."
- **Prop 3** (p. 21): $B^*<D^*$ (undersecured). **Prop 4** (p. 21): two creditors strictly preferred to one. **Prop 5** (p. 22, eq. 31): strategic default w.p.>0 if $f(\underline V)(\underline V-A)((1-q)EV+q\underline V)<(1-q)(EV-A)$. **Prop 6**: APR deviation if $I<q\underline V+(1-q)A$.

**S5 Banal-Estañol–Ottaviani–Winton 2013.** Two ex-ante identical projects, $I=1$, binary returns $r_L<1<r_H$ w.p. $1-p,p$, independent; debt only; recovery $\gamma$; separate = two nonrecourse loans, joint = one loan with recourse to both (p. 10). Footnote 9 (p. 10): no coordination failures among syndicate lenders assumed.
- **Prop 1** (p. 13): separate feasible iff $r_i^*=\frac{1-\gamma(1-p)r_L}{p}\le r_H$ (1); joint feasible iff (2) $r_m^*=\frac{1-\gamma(1-p)^2 r_L}{1-(1-p)^2}\le\frac{r_H+r_L}{2}$ or (3).
- **Prop 2** (p. 14): if (2) holds, joint optimal with coinsurance gain $CI=p(1-p)(1-\gamma)r_L$; if not, separate optimal, **risk-contamination loss $RC=p(1-p)(1-\gamma)r_H$**.
- **Prop 3** (p. 15): if (2) fails, joint financing *reduces* borrowing capacity. Predictions 1–4 (pp. 16–18): lower $\gamma$, lower $p$, mean-preserving spread (if $p>\bar p$), negative skewness all favor separation. Correlation (p. 6): perfectly negative → joint eliminates default; rising correlation → separate; perfectly positive → equivalent. Explicit distinction from Leland 2007 (p. 8): debt-only, fixed scale, so separation can be optimal even with no leverage re-optimization.

**S6 Hansmann–Kraakman 2000.** Affirmative partitioning = firm creditors' priority + liquidation protection (pp. 393–95); benefits = monitoring economies / creditor specialization (hotel–oil example pp. 399–400; project-finance fn. 22 pp. 401–02), going-concern protection against hold-up by owners' creditors (pp. 403–04); **costs** = more bankruptcy events as pools shrink and loss of "diversification as a bankruptcy-prevention device" (p. 400), debtor opportunism/asset-draining (pp. 400–01); cannot be replicated by contract because subordination of all present/future personal creditors is uncontractible and unmonitorable (pp. 406–09). Leland slides (9, 20–21): separation value = always-negative "LL effect" of merger + signed leverage effect; separation favored by high/different volatilities, high correlation, different default costs. Squire (abstract): intra-group cross-guarantees among correlated affiliates are a "one-way bet" that dilutes non-guaranteed creditors.

### 3. Comparison with the proposed date-0/1/2 financing-and-control model

| Proposed ingredient | Already settled by | Status |
|---|---|---|
| Complementary assets should sit under common control | S1 Prop 8; Table 1 p. 1146 | Theorem (under efficient ex-post bargaining, human-capital investment) |
| Lender (no investment, dispensable) holding control rights | S1 Prop 9/Corollary: harmful dilution | Theorem — but S1 excludes wealth constraints (p. 1152) and option-to-own/secured debt (fn. 10); the lender-rights question is *outside* S1 by construction |
| Fragmented creditor rights raise pledgeable income | S4 Props 2, 4; bound $(1+q)A$ | Theorem, but with **linear** liquidation technology and one divisible asset |
| Bundling (joint recourse) spreads distress / lowers borrowing capacity | S5 Props 2(b), 3(b) | Theorem, with additive independent returns; harm falls on borrower via endogenous competitive rate — satisfies the campaign's "explicit channel" no-go |
| Separate incorporation as monitoring/going-concern device; guarantees undo it | S6 pp. 399–404; Squire (abstract) | Legal-economic argument, not a theorem |
| "Many owners" per se | S1 eqs. (6), (9) | Conservation constraint: count alone adds nothing |

### 4. Decisive classical-reduction / falsification gates

**Gate A (reduction to S4).** Write the proposed model's liquidation technology. If the loss from creditor $i$ foreclosing on its asset is proportional to its share (continuation $(1-B/A)V$ as on S4 p. 9), then every result about "lender rights over complementary assets raising financeable cash flow" is S4 Props 1–4 with relabelled assets → stop. The model survives only if the technology is S1-strictly-complementary (any single foreclosure zeroes continuation) **and** that changes a sign in S4.

**Gate B (reduction to S5).** If "bundled guarantees" is modelled as recourse to pooled cash flows, contagion is S5 Prop 2(b) and capacity loss is Prop 3(b); the sufficient-statistic is whether $r_m^*\le (r_H+r_L)/2$ (condition (2)) → stop. The model survives only if the bundling instrument is a *trigger without pooling* (cross-default/acceleration) that S5 does not contain.

**Gate C (S1 Prop 9 check).** If the lender has no date-0 investment and date-1 bargaining is efficient, S1 already says lender control rights only dilute. Any positive role must come from non-verifiable cash / wealth constraints (S2/S4-type), and the model must state that friction explicitly.

### 5. At most two unresolved distinctions to test (conjectured gaps, not theorems)

**D1 — Complementarity × fragmented foreclosure (S1 def. p. 1135 inside S4).** Replace S4's linear $(1-B/A)V$ with strictly complementary assets $a_1,a_2$ pledged to creditors 1,2: foreclosure by either alone yields continuation $0$ and fragment salvage $L_i<A_i$. Compute the two-creditor optimal contract. Falsification: if debt capacity equals the single-creditor capacity (individual threats collapse to the collective threat), then "fragmented control over complementary assets" is classical (one-creditor S2/S4). If it is strictly higher or strictly lower with a sign depending on $L_i$, that is a bounded structural lemma. I have not found this computation in any of the six sources; S4 explicitly assumes constant returns to scale in liquidation (p. 9, fn. 5).

**D2 — Cross-default trigger vs joint recourse (S5 + S4 hybrid).** In S5's binary setup compare three regimes: separate nonrecourse; joint recourse; separate + cross-default (loan 1 accelerates on loan 2's default with no access to project 2's cash). In the $(r_H,r_L)$ state the third regime produces pure contamination with no coinsurance, so it is dominated *unless* it buys something — the only candidate channel in the literature is strategic-default deterrence via a stronger collective threat (S3/S4). Falsification: if separate+cross-default is never strictly optimal for any $(p,\gamma,r_L,r_H,q,V)$, "bundled rights spread distress" is S5 Prop 2(b) and nothing more. If strictly optimal somewhere, that is the isolated problem. Not settled by anything I read; S5 fn. 9 assumes away intra-loan coordination, and S4 has one project.

### 6. Limitations
- Three key originals were not read this session: S2 (MIT 429 ×3), S3 (all free copies 403), Leland 2007 paper and Squire 2011 (403); S3's mechanism is stated from two secondary originals and should be verified against the JPE text (especially whether an asset-complementarity parameter exists there) before any claim depends on it.
- S4/S5 were read as working papers; proposition numbers in the RFS versions may differ.
- No claims are made here about any CoreWeave agreement, rights chain, or valuation; nothing above is a legal opinion.
- No acceptance checks were run; no files were written.
