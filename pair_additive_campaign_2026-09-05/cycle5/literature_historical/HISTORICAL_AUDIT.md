# Historical priority audit for the strict pair-additive 1/9 witness

Checked September 6, 2026. Scope: original historical sources and their applicability to the canonical 21-player result in cycle4/root/ONE_NINTH_COUNTEREXAMPLE.md. The result concerns the full labeled core of complete, equal-sector, strict triple assignment games with nonnegative pair data; the target is fixed at the positive first leximin floor 1/3 and has whole-core ideal 3.

**Verdict: novelty is not confirmed.** This audit closes the original-author-text gap for the 2020 assortative extreme-core paper and rules out its direct applicability to this example. It does not close the original-text gaps for Quint, Lucas, Stuart, or the separate 2023 extreme-core paper. No inspected statement establishes the campaign's exact sorted-leximin ideal-ratio result, but those access gaps prevent a comprehensive historical priority verdict. Internal correctness checks and priority remain separate.

## Claim table

| Original work | Primary material obtained and exact scope established | Relation to the 1/9 claim |
|---|---|---|
| Quint, *The core of an m-sided assignment game* (CAM88-24, 1988; GEB 1991) | UCLA's [original CAM index](https://ww3.math.ucla.edu/cam-reports-1986-2000/) identifies report 88-24, August 1988, without a PDF link. The [publisher record](https://www.sciencedirect.com/science/article/abs/pii/0899825691900179) describes an m-type extension, possible empty cores, and a balanced subclass. Publisher API returns bibliographic coredata only. | Exact subclass hypotheses and theorem statements remain unread. Do not assert that all nonnegative pair-additive instances are in Quint's balanced class, or that his original paper excludes our ratio. |
| Lucas, *Core theory for multiple-sided assignment games* (1995) | Publisher-deposited [DOI metadata](https://doi.org/10.1215/S0012-7094-95-08106-X) identifies Duke Mathematical Journal **81(1)**. The original download returned an access-interstitial HTML page, not a paper. | Original theorem remains unread. The two inequalities below are a later paper's attribution, not an original-source verification. They concern six-player balancedness, not a seven-per-sector leximin ratio. |
| Stuart, *The supplier–firm–buyer game and its m-sided generalization* (1997) | [Author publication list](https://www.columbia.edu/~hws7/) and [publisher DOI](https://doi.org/10.1016/S0165-4896(96)00830-X) confirm the work. The publisher abstract, also surfaced through its citing-article page, says local additivity suffices for core nonemptiness. Original full text was not obtained; the article API returns coredata only. | Precise original chain assumptions and numbered theorems remain unread. Nonemptiness alone is not a selector protection theorem. Later authors' descriptions must retain their status as later descriptions. |
| Martínez-de-Albéniz–Rafels–Ybern, *Assortative multisided assignment games: The extreme core points* (2020; WP2019) | Complete [UB author manuscript](https://diposit.ub.edu/bitstreams/187fcb85-db7e-4ed2-950e-c293fcd99b76/download) and [UB WP E19/395](https://diposit.ub.edu/bitstreams/ffcefa74-6311-49d1-8e14-1fb8cdadba78/download) obtained. Exact theorem scope is stated below. | A certified reversal of within-sector core-payoff order excludes this witness from the assortative class under every relabeling. The paper's theorem therefore does not directly supply this instance or its ratio. |
| Martínez-de-Albéniz–Rafels–Ybern, *Extreme Core Points in Multisided Assignment Problems* (2023), SSRN4369524 | [Primary SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4369524), 13 pages, posted February 24, 2023, plus DOI metadata and UB's working-paper listing. Abstract describes reduction of extreme-core computation to a suitable finite family of cooperative games. Full text remains unavailable. | Its conditions and representation details remain unread. It must not be excluded by the assumptions of the different 2020 assortative paper. This remains a meaningful unresolved priority gap. |

## Exact statements recovered from the assortative author text

The UB repository labels the 25-page file an accepted version of the 2020 article; its cover is dated October 8, 2019. A separate 23-page institutional working paper was also obtained. This audit does not equate either file with the final publisher typesetting.

For a square market whose worth array is supermodular and coordinatewise nondecreasing, Theorem 2.1 (manuscript pp.8–9) states: the diagonal is optimal; nonnegative allocations are in the core exactly when diagonal equalities and central-strip inequalities hold; every core allocation respects the fixed within-sector agent order. “Central strip” means coordinate-index range at most one. Remark 2.1 distinguishes the assumptions used by the three parts.

Theorem 3.1 (pp.14–18) identifies all extreme core points with vectors obtained by imposing equality along paths that traverse consecutive diagonal coalitions one sector-coordinate at a time. These are statements about the core's geometry under assortative assumptions, not sorted leximin or ideal-payoff fractions. Source: [institutional author text](https://diposit.ub.edu/bitstreams/187fcb85-db7e-4ed2-950e-c293fcd99b76/download).

**Application check, using the already certified campaign witnesses:** in sector a, u_a0=4/3>u_a3=1/3, while y_a0=2<y_a3=3. Thus neither possible fixed ordering of a0 and a3 can hold throughout the core. Theorem 2.1(c) rules out any assortative relabeling of this market. This is a short implication of the retrieved theorem and the existing verified covers, not a new search or a universal representation-exclusion result.

## Lucas: precise later attribution, with the original gap retained

Atay–Núñez (2019), section 2, attributes to Lucas the following six-player criterion. If the two diagonal triples form an optimal matching in a 2×2×2 array a, balancedness is equivalent to

```
2 a111 + a222 >= a112 + a121 + a211
a111 + 2 a222 >= a221 + a212 + a122.
```

This was read from the [later authors' full text](https://ataatay.github.io/webpage/Atay_Nu%CC%81n%CC%83ez_2019_MSS.pdf), not Lucas's original. No theorem number or additional original hypotheses are invented. The later bibliography lists volume 87; publisher-deposited metadata gives volume 81. Only the volume/issue correction is independently established here.

## Two separate extreme-core papers

The earlier campaign summary merged an unread-paper gap with the title of the 2020 assortative article. They must remain distinct:

- The 2020 assortative article has DOI 10.1016/j.geb.2020.01.001; its 2019 working-paper record is SSRN3490554.
- The 2023 paper has DOI 10.2139/ssrn.4369524 and the different title *Extreme Core Points in Multisided Assignment Problems*.

The [2020 institutional record](https://diposit.ub.edu/items/9c47c698-7a2a-4160-bd7f-f5be0fdde1ea), [2019 SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3490554), [2023 SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4369524), and saved DOI metadata establish the distinction. Retrieving the 2020 manuscript does not close the 2023 gap.

## Access and audit coverage

There were 13 focused web queries: the initial 12 historical queries, then one exact-title query after the distinct 2023 paper was clarified. One Crossref title lookup resolved Lucas's original DOI; later Crossref calls were exact-DOI retrievals. All queries, raw browser requests/responses, direct retrieval attempts and artifact hashes are retained in this directory. Secondary search aggregators served only as discovery leads.

The normal network sandbox could not resolve external hosts. Approved public retrieval outside that sandbox obtained the two institutional PDFs and DOI metadata. No credentials, subscription access, or authentication bypass was used.

Remaining exact access failures:

- Quint: the primary CAM index supplies no download; a derived standard CAM filename returned HTTP404. Publisher download yielded a download-error page; the standard article API supplies only bibliographic metadata.
- Lucas: the DOI-deposited original-download URL returned HTTP200 with an Incapsula interstitial. The artifact is correctly stored as HTML, not labeled a PDF.
- Stuart: author page has no linked 1997 manuscript. Publisher page retrieval failed, and the standard API supplies metadata without article text.
- SSRN4369524: the indexed primary abstract was retrieved, but opening the full record returned HTTP403; no original full text was obtained.

Original-author text retrieved means its definitions and relevant theorem statements were read, not that every proof in that paper was independently re-proved. No exhaustive citation-tree audit was performed. The 2026 supermodular/local-monotonicity ideal-payoff paper surfaced as a lead and was passed to the parent campaign's contemporary-literature lane; it was not analyzed here.

**What can be said publicly now:** the campaign has an internally verified finite strict pair-additive counterexample to its proposed 1/6 guarantee, with exact ratio1/9. Historical literature already studies multisided assignment cores, local/pair additivity and extreme-core geometry. The inspected original assortative theorem does not cover this witness. **Novelty and external specialist priority review remain pending.**
