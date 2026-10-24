I've exhausted the bounded set of legitimate free routes; the remaining attempts all hit access blocks rather than content. Writing up the result now — no further fetches.

## Result: bounded free-only follow-up on Uhan 2014 and Arin 2013

**Bottom line:** Neither full original was obtained. For Arin, a legitimate free *working-version* copy was located at a concrete URL but is behind a bot-verification interstitial this tool cannot pass; it would not close the final-version delta anyway. For Uhan, every indexed open-access pointer is dead or redirects into archives this tool cannot reach. No definition/theorem comparison beyond what is already in the supplied files was possible, so no priority conclusion changes.

### Arin, "Monotonic core solutions: beyond Young's theorem" (IJGT 42:325–337, 2013)

**Located (evidence, not read):**
- OpenAlex and Semantic Scholar both mark the DOI green-OA via `http://hdl.handle.net/10810/6373` (ADDI, UPV/EHU), version = **submittedVersion**, i.e. the Ikerlanak working paper, not the published text. (https://api.openalex.org/works/doi:10.1007/s00182-013-0368-8; https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s00182-013-0368-8)
- Search index exposes the exact bitstream: **https://addi.ehu.es/bitstream/10810/6373/1/IL4410.pdf** — Ikerlanak IL 44/10, dated 2010-07, author "Arin Aguirre, Francisco Javier". Also the ADDI record https://addi.ehu.es/handle/10810/6373 and a UPV/EHU research-portal record for the 2013 article (https://ekoizpen-zientifikoa.ehu.eus/documentos/652b29fcebee473633a38d5d).

**Access gap (exact):**
- ADDI root returns a "Verificación de seguridad" interstitial; every ADDI path (handle on `.es`/`.eus`, bitstream with/without `?sequence=1&isAllowed=y`, `/discover`, DSpace REST, OAI-PMH GetRecord) returned HTTP 404 to this tool. This is a tool-side block, not evidence the file is missing.
- ekoizpen-zientifikoa.ehu.eus: ECONNRESET twice.
- IDEAS/EconPapers record pages (`ehu/ikerla/6373`, `201044`, RePEc-handle path, refs.cgi): 404/empty. Google Scholar: "did not match any articles" (unreliable from this tool). BASE and Semantic Scholar HTML: Anubis bot-block.
- Springer page: subscription preview (already recorded in the addendum; not re-tested).

**Comparison status:** The ADDI copy is a **2010 working version**. Even if retrieved, it cannot settle the "final 2013 version delta" named in CONTRIBUTION_AND_PRIORITY.txt line 93–94 and PRIORITY_ADDENDUM.txt lines 12, 70–74. Whether IL 44/10 is textually identical to the already-read TCER E-24 is **unverified**. The addendum's credited basis (E-24, pp. 4–7, incident-coalition definition, Theorem 3) remains the only verified comparison. No new subsumption claim can be made or ruled out.

### Uhan, "The complexity of egalitarian mechanisms for linear programming games" (ORL 42(1):76–81, 2014)

**Correct DOI (Crossref):** 10.1016/j.orl.2013.12.003 (PII S016763771300165X). Note: my first probe used a wrong guessed DOI (10.1016/j.orl.2013.11.001, a different ORL paper); disregarded.

**Indexed OA pointers, all dead for this tool:**
- Semantic Scholar lists GREEN OA at `http://www.optimization-online.org/DB_FILE/2011/07/3106.pdf`; that path now resolves to the abstract-only landing page https://optimization-online.org/2011/07/3106/ (published 2011-07-18, updated 2014-01-02, no file link). The new-style upload path and the author listing pages (`/author/uhan/`, `/page/2/`) expose no PDF.
- OpenAlex lists only the publisher DOI and CiteSeerX `10.1.1.416.2322` (is_oa false). CiteSeerX now 301-redirects into web.archive.org, which this tool cannot fetch; Wayback captures of the legacy DB_FILE/DB_HTML paths likewise unreachable.
- Author homepage (https://nelson.uhan.me/) and USNA faculty page: DOI link only, no PDF. MIT thesis (dspace.mit.edu/handle/1721.1/45607, 2008) predates and does not cover this result per its abstract.
- Purdue e-Pubs, CORE, scholar.archive.org, OpenAIRE, OUCI: 403/anti-scrape/409.
- Phrase searches ("most cost-efficient subset problem") found no mirror.

**Comparison status:** Unchanged from the addendum (lines 38–48): model distinguished at introduction/definition level (valuation bids, chosen served set, cost-recovering prices; subsets chosen by average marginal cost) vs. the draft's resource reports/production payments. Algorithm 3.1, Corollary 3.4 and the hardness proof remain **unread**; no theorem-level clearance is claimed. Nothing read suggests Uhan states a funding-ratio or monotonicity-repair bound, but this is an inference from abstract/intro only.

### Limitations
- Zero full-text reads this round; everything above is metadata/index evidence plus documented failures. Absence of a reachable copy is **not** novelty evidence.
- Remaining realistic free route for Arin: open `https://addi.ehu.es/bitstream/10810/6373/1/IL4410.pdf` in a normal browser (passes the interstitial) — but it yields only the 2010 working version. The final-version delta still requires the Springer text via access the author already holds.
- For Uhan, a browser session to the Wayback capture of `optimization-online.org/DB_FILE/2011/07/3106.pdf` is the most plausible free route; untested here because the tool cannot reach web.archive.org.
- No files were edited, no purchases, no outreach.

Sources: [Optimization Online 3106](https://optimization-online.org/2011/07/3106/) · [Semantic Scholar – Uhan](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.orl.2013.12.003?fields=title,openAccessPdf,externalIds,year) · [OpenAlex – Uhan](https://api.openalex.org/works/doi:10.1016/j.orl.2013.12.003) · [Crossref query](https://api.crossref.org/works?query.bibliographic=complexity+egalitarian+mechanisms+linear+programming+games+Uhan&rows=3) · [Uhan homepage](https://nelson.uhan.me/) · [MIT thesis](https://dspace.mit.edu/handle/1721.1/45607) · [OpenAlex – Arin](https://api.openalex.org/works/doi:10.1007/s00182-013-0368-8) · [Semantic Scholar – Arin](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s00182-013-0368-8?fields=title,openAccessPdf,externalIds,year) · [ADDI record (blocked)](https://addi.ehu.es/handle/10810/6373) · [ADDI bitstream IL4410.pdf (blocked)](https://addi.ehu.es/bitstream/10810/6373/1/IL4410.pdf) · [UPV/EHU portal record](https://ekoizpen-zientifikoa.ehu.eus/documentos/652b29fcebee473633a38d5d?lang=en) · [IDEAS ikerla/6373](https://ideas.repec.org/p/ehu/ikerla/6373.html) · [Springer article page](https://link.springer.com/article/10.1007/s00182-013-0368-8)
