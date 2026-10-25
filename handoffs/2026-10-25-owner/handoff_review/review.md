**Provisional verdict: findings (minor); no material overclaim found in reviewed scope.** Most important: SYNTHESIS.txt reuses the labels "P4" and "P6" for both paper catalogue entries and path graphs, which a first-time reader cannot disambiguate.

## Findings

**1. Low–Medium — Label collision P4/P6 (paper vs. path graph).** SYNTHESIS.txt lines 74, 87, 119 use P4/P5/P6 as paper IDs; lines 189 ("fail on P6"), 214–215 ("The P4 advance does not close that class") use P4/P6 as path graphs (ROOT_TRACKS `p4_tree`, `weighted_graphs.remaining_work`). Line 215 is especially confusing: a reader of §2 will read "P4 advance" as the balanced-transport paper. Suggest writing "path P4 / path P6" or "unit-profit four-resource path" wherever the graph is meant (as line 185 already does).

**2. Low — Supersession of the sub-two envelope target by a coalition result.** Line 138–139 states the weighted-graph TCWM 3/2 "supersedes the old sub-two EXISTENCE target" for the depth-two *individual own-report* envelope (ROOT_TRACKS `ownership_depth_two` status says the same). Coalition TCWM ⇒ individual monotonicity only matters if the depth-two technology F=min(H,P+Σ min(H_j,L_j)) lies in the weighted fractional resource-graph class; neither file states this membership. Add the one-line justification or mark the supersession as recorded-but-unverified here.

**3. Low — Unverified figures/dates not grounded in supplied inventories.**
- Line 143: "66 root adjudications" — SOURCE_INDEX.json not supplied; highest adjudication number cited in ROOT_TRACKS is 63.
- Line 100: P9 manuscript "is the 24 October scientific source" — PAPERS.json/RECENT_TRACKS date only the packet (25 Oct); no 24 Oct source date recorded.
- Line 237: "preregistered usefulness threshold" — `ai_serving_history` says "five-point gate", not preregistered.
- Line 323: Yves Sprumont as alternative reader — absent from all inventories.
These are not contradictions but should carry a source pointer or be softened.

**4. Low — Irreversible-reserve bullet slightly compresses the contract.** Line 201 "The original full-OUT problem has factor 1" vs. inventory "y=(F,0) has optimal unrestricted factor 1" on the same box. Stating the specific rule (F,0) and that the obstruction is to irreversible reserves (line 202 does this) would prevent reading "factor 1" as a general full-OUT statement.

**Checked and consistent:** individual vs coalition (lines 49–57, 152–153, 126); total vs gain (46–47, 185 "total factor", 216–217, 226–227); architecture vs unrestricted lower bounds (180–181, 199–202, 204–208; math-reset bullet 193–194 could add "true all-profile K=1" from `math_reset_coverage_obstruction`); N-PORT counts 1,791/393/29 and explicit non-error-rate caveat (272–274); unsent vs submitted (106–111, 322–327; September drafts null sent_at; packet "remains unsent"); nine catalogue entries not nine publications (67–69); envelope candidate not auto-numbered, no PDF export (91–96); P4/P5 binding uncertainty (87); P7 stale PAPERS.md paragraph (88–89); 323/200, 8/5 relaxation obstruction, withdrawn C² (134–137); arity frontier and B_6=493/243 (158–159); Mac 100/2,400 (250).

## Scope limitations
Only SYNTHESIS.txt and the four JSON inventories were reviewed; INVENTORY.json, PAPERS_READABLE.txt, SOURCE_INDEX.json, and all cited source/review files were not supplied. No proofs, replays, or path existence were verified; inventories are treated as recorded evidence only.

## Verdict
Findings — four minor consistency/labelling items; no concrete overclaim of submission, publication, novelty, unrestricted lower bound, or arbitrary-graph coverage detected in the reviewed scope.
