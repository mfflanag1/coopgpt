# Bounded source audit: min-of-k capacity pool mechanism (route C)

None of the five sources I inspected states or implies a stage-scaling result for the frozen model, in either direction. This is a bounded audit, not a novelty confirmation, and it found one real correction to the earlier ledger.

**How each source was read.** Sources 2, 3 and 4 were read directly as PDF page images. Source 1 (Huang et al.) was read only through the fetch tool's model-extracted quotations of the arXiv HTML, so its wording should be re-checked before quoting. Source 5 could not be retrieved in full text.

## Closest source comparisons

### 1. Huang, Mei, Yang, Cao — Mechanism Design in Max-Flows (arXiv:2502.08248v1, 12 Feb 2025)
https://arxiv.org/abs/2502.08248 · https://arxiv.org/html/2502.08248v1

- **Hypotheses (as extracted):**
  - One edge per player, capacities c ∈ ℝ₊₊ (strictly positive), v(S) is the max-flow using edges in S.
  - Reports satisfy ĉ(e) ≤ c(e), i.e. underreports only; "no cost is incurred when a player's edge is used."
  - The mechanism definition includes efficiency, Σφᵢ(ĉ) = v̂(N).
  - Example 1 gives a four-player game where a core-selecting mechanism is manipulable.
  - Proposition 1: the Shapley mechanism is DSIC and SIR.
  - Definition 2 / Theorem 1: the minimal-cut mechanism is DSIC, SIR, SP, MP and CM.
- **Relation to the frozen model:**
  - Inference from the definitions: the k-pool game is their max-flow game on a series of k parallel-edge bundles. The paper does not single out this family, and the extraction found no mention of glove games.
  - Their budget is exactly v̂(N), so β = 0 by construction.
  - No subsidy, approximate core, cost of stability or H-type floor appears in the extraction.
  - Their stated future work is computing the MC mechanism, multi-edge owners and private costs; it does not include subsidised coalition coverage.
- **Stage scaling:** neither implied nor preempted. The qualitative conflict between core selection and truthfulness is theirs; it carries no rate in k.
- **Gaps:** I did not obtain a numbered theorem for "no core-selection mechanism is truthful" beyond Example 1 and the abstract. Zero-capacity boundary profiles are outside their formal domain. Only v1 was seen; no citing-paper trace was done.

### 2. Moretti and Norde — Some new results on generalized additive games (Cahier du LAMSADE 395, Feb 2020), §4.1
https://www.lamsade.dauphine.fr/fileadmin/mediatheque/lamsade/documents/cahier_395.pdf_1.pdf

- **Hypotheses (read directly, p. 10):**
  - "Given a partition {L,R} of the set of players N and a weight vector w ∈ ℝ₊ᴺ … v(S) = min{Σ_{i∈S∩L} wᵢ, Σ_{j∈S∩R} wⱼ}", with non-integer weights allowed.
  - Total balancedness is shown by giving the short side its weights, in every subgame.
  - Weighted glove games need not admit a PMAS (the 2+2 standard glove game has none, citing Sprumont).
  - Theorem 4.3: for positive w, the game is supermodular iff one side is a single player whose weight is at least the other side's total.
- **Correction to the earlier ledger:** this section is strictly two-sided. It is an original source for the k = 2 real-capacity model and its bottleneck core vector only, not for the k-pool technology. The mechanism-frontier ledger entry 1 ("defines exactly this real-capacity model") should be scoped to two pools.
- **Other relevant content:**
  - The representing map 𝓜 in eq. (13) "depends on the weight vector w", and no universal map exists. So their fixed-𝓜 theorems (3.3–3.7, for every w) do not cover the glove family across profiles.
  - Monotonicity here means in coalition membership (PMAS), not in a player's own capacity.
  - There is no strategic reporting or subsidy.
- **Stage scaling:** none.

### 3. Immorlica, Mahdian, Mirrokni — Limitations of cross-monotonic cost-sharing schemes (SODA 2005; author PDF), §3.5
https://immorlica.com/pubs/costshare.pdf

- **Hypotheses (read directly, pp. 11–12):**
  - Definition 3.3: a profit-sharing scheme ξ(i,S) has ξ(i,S) = 0 for i ∉ S.
  - It is α-budget-balanced (α ≥ 1) if v(S) ≤ Σ_{i∈S} ξ(i,S) ≤ α·v(S) for every S.
  - It is cross-monotone if ξ(i,S) ≤ ξ(i,S∪T).
  - Theorem 3.6: "There is no o(n)-budget-balanced profit-sharing scheme for the maximum flow game", where the proof assumes cross-monotonicity.
  - The witness is the graph s→u→t with n−1 parallel edges per stage, which is exactly a two-pool unit glove game; the expected ratio is at least (n−1)/2.
- **Why it matters:** this is the closest prior theorem on a multiplicative subsidy with a monotonicity requirement in exactly the two-pool technology. It is not cited in either supplied ledger.
- **Why it does not transfer:** its monotonicity is in the set of present agents and constrains other agents' shares. The frozen model requires only own-report monotonicity. The Ω(n) bound is therefore consistent with the contract's two-pool β ≤ 1/(2e).
- **My inference, not a source theorem:** restricted to 0/1 profiles, the proof appears to use only pair coverage, cross-monotonicity and nonnegativity. If so, adding Huang-style cross-monotonicity (CM) to the frozen requirements would force β to grow linearly in owner count already at k = 2. This needs coordinator verification before use.
- **Stage scaling:** none. The growth is in owner count at two stages, under a different axiom. It does not preempt a k-dependent bound.

### 4. Bachrach, Elkind, Malizia, Meir, Pasechnik, Rosenschein, Rothe, Zuckerman — Bounds on the Cost of Stabilizing a Cooperative Game (JAIR 63 (2018) 987–1023)
https://www.jair.org/index.php/jair/article/download/11270/26463/20899 · conference version https://arxiv.org/abs/0907.4385

- **Hypotheses (read directly, pp. 987–994 and 1014):**
  - Definitions 1–2: a fixed game G; CoS⁺(G) = inf{p(N) − v(N) : p stable}; CoS^×(G) = inf{p(N)/v(N)}.
  - Observation 5: monotone games have CoS^× ≤ n, and this is tight.
  - Theorem 7: superadditive games have CoS^× ≤ √n, asymptotically tight.
  - Table 1 also lists anonymous superadditive 2n/(n+1) (Theorem 9) and weighted voting games 2 (Theorem 10) for profit sharing, and 1/(ln n + 1) (Proposition 29) for subadditive cost sharing.
- **Relation to the frozen model:**
  - The β normalisation matches CoS^× − 1.
  - These are pointwise, fixed-game quantities with no private information. Every v_c is balanced, so CoS⁺(v_c) = 0 at every profile; this is immediate from the definition, not stated in the paper for glove games.
  - A positive β in the frozen model comes only from requiring one own-report-monotone rule across profiles, plus the H/k floor.
  - The √n and logarithmic bounds are in the number of players, for games with empty cores. They do not transfer to k-dependence.
- **Stage scaling:** none.

### 5. Brânzei, Solymosi, Tijs — Type monotonic allocation schemes for multi-glove games (CentER DP 2003-34; TOP 15 (2007) 78–88)
https://research.tilburguniversity.edu/files/790105/monotoni.pdf · https://repository.tilburguniversity.edu/bitstreams/c47188cf-99af-4b8f-a640-7e4f6258c492/download

- **Access failed:** both free links returned HTTP 403. I saw only bibliographic data and search-snippet abstract text.
- **From the snippets only (not verified):** the paper introduces type monotonic allocation schemes for multi-glove games, weight-system rules that generate them, and extendability of each core element to such a scheme.
- **Uncertain equivalence:** this is the most likely original for the k-type complement technology. I could not check whether endowments are real or integer, whether each agent holds exactly one type, or how type monotonicity relates to own-capacity monotonicity. No theorem from it may be asserted.
- **Stage scaling:** unknown. Nothing in the snippets suggests subsidy or reporting.

I am not adding a sixth. The Resnick et al., Goko et al., Gangam et al. and Kurz entries in the supplied ledgers were not re-inspected in this pass.

## Where the frozen model's ingredients stand in these sources

| Ingredient | Status in inspected sources |
|---|---|
| k-pool complement technology (v = min over k pools) | Not sourced in free text I could read: source 2 is two-sided, source 5 is inaccessible. It is a special case of source 1's max-flow model only by my inference. |
| Fixed single-pool owners | Matches source 1 (one edge per player) and source 2 (partition), the latter for two sides only. |
| Capacity underreports, no costs | Source 1 only. |
| Coverage of every coalition with outside money | Fixed-game concept in source 4; per-set with cross-monotonicity in source 3. Neither combines it with capacity reports. |
| H_i/k floor and (1+β)T budget | Not found in any inspected source. This is non-detection in five documents, not evidence of absence. |

## Limitations and unresolved questions

- **Not retrieved:** Kalai–Zemel (1982) on flow games, Young (1985) and Housman–Clark (1998) on core versus coalitional monotonicity, Postlewaite (1979) on endowment withholding, Sprumont (1990) on PMAS, and Meir et al. on subsidies under restricted cooperation (https://www.cs.huji.ac.il/~jeff/papers/coopmas11meir.pdf appeared in search but was not opened). These are leads from memory or search only; no assertion rests on them.
- **Search coverage:** one search for follow-ups to Huang et al. returned no relevant subsidy or approximate-core successor. That is not evidence of absence.
- **Not searched:** resource-monotonic allocation under Leontief preferences and continuous or additive cost-sharing (Moulin–Shenker style).
- **Open checks for the coordinator:**
  - Whether the multi-glove paper covers real, one-type-per-agent endowments.
  - Whether my cross-monotonicity inference under source 3 holds.
  - Whether later versions or citing papers of 2502.08248 add subsidies.

No purchases, CAPTCHA, outreach, delegation or file edits occurred.

Sources:
- https://arxiv.org/abs/2502.08248
- https://arxiv.org/html/2502.08248v1
- https://www.lamsade.dauphine.fr/fileadmin/mediatheque/lamsade/documents/cahier_395.pdf_1.pdf
- https://immorlica.com/pubs/costshare.pdf
- https://www.jair.org/index.php/jair/article/download/11270/26463/20899
- https://arxiv.org/abs/0907.4385
- https://ideas.repec.org/p/tiu/tiutis/2fed3103-b346-4023-a36d-fcb58a2cdc45.html
- https://research.tilburguniversity.edu/en/publications/type-monotonic-allocation-schemes-for-multi-glove-games-2
