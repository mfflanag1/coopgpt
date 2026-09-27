# Original-source priority followup — 6 September 2026

## Result

**Neither targeted original-text gap is closed.** Eight new focused searches and distinct author/university routes found no readable original of Quint (1991)/CAM88-24 or the distinct 2023 SSRN4369524 manuscript. This supports a documented search statement, not confirmation of novelty.

The exact claim being checked is the theorem in the campaign's cycle5/root/VANISHING_FAMILY.md: fixed three sectors, complete strict triple production, nonnegative pair matrices with entries in {0,1,2}, nonempty full core with a strictly positive allocation, and full sorted ascending leximin satisfying x_i/H_i=1/[3(q+1)] for n=9q+3. This implies c_pair=0. This audit did not modify or search for mathematics.

## Source and claim table

| Source | Original coverage actually obtained | What can safely be said | Deductive anticipation of the target |
|---|---|---|---|
| Thomas Quint, “The core of an m-sided assignment game,” GEB 3(4), 487–503 (1991), DOI 10.1016/0899-8256(91)90017-9; UCLA CAM88-24 (1988) | Bibliographic entry and publisher abstract from prior audit; new official-author publication list. **No original theorem, proof, or example text.** | The original studies multisided assignment cores and supplies a nonempty-core subclass, according to its abstract. Exact subclass hypotheses and examples remain unread. | **Unresolved.** We cannot exclude an example, representation, or corollary in unread text. Nonemptiness alone would not establish the target ideal-ratio claim. |
| Martínez-de-Albéniz, Rafels, Ybern, “Extreme Core Points in Multisided Assignment Problems,” SSRN4369524 (2023), DOI 10.2139/ssrn.4369524 | Crossref identity and indexed SSRN abstract from prior audit. **No original theorem, proof, or example text.** New author pages yielded no manuscript link. | The abstract concerns conditions for computing extreme-core allocations through a finite family of cooperative games. Its precise conditions and representation are still unread. | **Unresolved.** A general computation/geometry result is not automatically an explicit vanishing construction, but a suitable representation theorem could make it a corollary. This possibility cannot be dismissed from the abstract. |
| Same authors, “Assortative multisided assignment games: The extreme core points,” GEB120, 144–153 (2020), DOI 10.1016/j.geb.2020.01.001 | Prior cycle recovered complete accepted-author and working-paper texts and read definitions, Theorems2.1/3.1, discussion/examples. This followup located the same institutional item through Rafels's profile. | This is a **different paper** from SSRN4369524. It addresses ordered supermodular/monotone assignment arrays and describes extreme cores. | The inspected original statements do not assert the target ratio theorem. The 2020 scope cannot be used to assume the unread 2023 paper has identical restrictions. No new all-parameter applicability proof is claimed by this retrieval-only followup. |

Primary links: [Quint publisher record](https://www.sciencedirect.com/science/article/abs/pii/0899825691900179), [UCLA CAM index](https://ww3.math.ucla.edu/cam-reports-1986-2000/), [2023 SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4369524), [2020 UB accepted-author record](https://diposit.ub.edu/items/9c47c698-7a2a-4160-bd7f-f5be0fdde1ea).

## Newly attempted routes and exact read coverage

1. **Quint official author route.** The [UNR faculty profile](https://www.unr.edu/math/thomas-quint) links to [his current publication list](https://www.thomasquintmath.com/publications). Read the complete rendered publication list (87 lines). The target1991 entry has no download link; only another unrelated paper is linked. Read his [home page](https://www.thomasquintmath.com/), which adds no target text. An indexed author CV at CiteSeer could not be fetched (web400 timeout). No unobserved PDF path was guessed.

2. **Rafels official institution route.** Read the [UB group members page](https://www.ub.edu/gametheory/members/), which links his author page. The web parser failed to decode that page. A public HTTP read succeeded after ordinary sandbox DNS failure and approved network retrieval. The URL redirected to [his public SIRA profile](https://sira.ub.edu/static/fitxes/EconomiaIEmpresa.html?id=crafels.ub.edu&lang=ca). This is an empty rendering shell; its explicitly linked public JavaScript specifies its public data file. Read that data file successfully, with no authentication or challenge bypass. Its three selected recent publication records include the2020 paper and its existing repository handle, not the2023 target.

3. **Longer institutional author profile.** The SIRA data explicitly links [Rafels's longer public profile](https://webgrec.ub.edu/webpages/personal/ang/000584_crafels.ub.edu.html), retrieved successfully as ISO-8859-1 HTML. Inspected all publication links and occurrences of multisided/extreme-core/targetID. It lists the2020 paper and2021 weak-assortative conference presentations, but no2023 target or SSRN link. This profile is visibly historical; absence there provides little evidence about a2023 manuscript.

4. **Search coverage.** Four target-title/author/Quint-author-site searches followed by four distinct repository/exact-title/dissertation searches; exact strings and raw returned results are in web_retrievals.json. No fresh original target text emerged. A [Stanford matching bibliography](https://stanford.edu/~alroth/matchbib.html) identifies additional historical reports but supplies no target original. The UB group's peer-reviewed-papers page produced web400 timeout; it was not treated as read.

Previously failed UCLA inferred PDF, ScienceDirect PDF, SSRN download guess, and publisher metadata-only routes were not repeated. The already known UB working-paper-page timeout was not retried. This round used alternate author paths instead.

## Public wording and confidence

Recommended: **“We prove that no positive size-independent coordinate-ideal protection guarantee exists for full leximin in complete strict three-sided assignment markets with nonnegative pair-additive values, even with pair entries in {0,1,2}. We have not identified an earlier result establishing this exact theorem in the sources reviewed. Historical full-text checks and external specialist priority review remain incomplete.”**

For a manuscript priority claim, “To our knowledge” is a qualified attribution convention, not a verification certificate. Do not say “novelty confirmed,” “first ever,” or “the literature rules out prior work.”

Confidence is high about the distinction between the2020 and2023 titles and about what was actually retrieved. Confidence in an unconditional novelty claim is **insufficient**: neither targeted original's theorem/example content was obtained. The remaining material gaps are exact originals, not merely missing citations. This audit does not downgrade the separately verified mathematics, and it does not certify field-level significance.

## Reproducibility

- web_retrievals.json: all eight new search strings and raw web-tool responses, plus official-profile reads.
- author_direct_retrieval.json: successful author-page public HTTP response metadata; the preceding sandbox attempt failed DNS with “[Errno8] nodename nor servname provided, or not known.”
- public_assets_retrieval.json: exact public URLs, statuses, redirects, content types, byte counts, and SHA256 hashes for linked author-page assets and data.
- rafels_author.html and public_*.txt: raw retrieved bodies.
- fetch_author.py / fetch_public_assets.py: retrieval scripts. No secrets or authentication used.
- Prior coverage and failed routes remain in /private/tmp/coopgt-pairadd-cycle5/literature_historical/HISTORICAL_AUDIT.md and its retrieval records.

