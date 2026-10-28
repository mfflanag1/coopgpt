## Provisional verdict: findings

**Most important:** `HISTORY_PLAN.json` assigns the group `canonical-working-snapshot` an author date of **2026-10-18** and cites "README.md; PAPERS.md" as its evidence/content (lines 59–64). But the sync README line 7 states the repository README's publication links were updated to point at the later local-improvements versions, and `handoffs/README.md` line 3 says that navigation was "added 28 October 2026." If today's README/PAPERS navigation text lands in the 18 October group, that is exactly the misleading provenance the plan forbids.

## Findings

**1. High — `provenance/sync-2026-10-28/HISTORY_PLAN.json:59-64`.** README.md/PAPERS.md appear in an 18 October-dated group while carrying text written today. Evidence: sync README line 5 ("New synchronization documentation is dated 28 October in both fields") vs. plan group `canonical-working-snapshot`. *Verify:* `git log --follow -1 --format=%ad README.md PAPERS.md` after import; confirm the 18 Oct commit contains only the 16–18 Oct snapshot bodies, with today's navigation/version-pointer edits isolated in the 28 Oct commit.

**2. High — `HISTORY_PLAN.json` (whole file).** The plan contains **no entry for the 28 October commit(s)** and no per-group path manifests — only path counts. `handoffs/README.md` (written today) is unassigned, while group `handoff-25` (author 25 Oct, 19 paths) plausibly covers `handoffs/`. *Verify:* add an explicit 28 Oct group listing `provenance/sync-2026-10-28/*`, `handoffs/README.md`, `README.md`, `PAPERS.md`; cross-check each group's paths against `IMPORTED_FILES.json`.

**3. Medium — `handoffs/README.md:14`.** "The old canonical coalition PDFs omit the graph theorem" is unsupported in the packet. `READINESS_REPORT.txt:20-21` only states the graph theorem is present in Section 6 of the current manuscript and that the 18 Oct canonical PDFs are *excluded* from the portable packet — not that they lack the theorem. *Verify:* cite a dated diff/section listing, or soften to "are superseded and not included."

**4. Medium — `handoffs/README.md:14` vs `publication_packages/2026-10-18-local-improvements/FINAL_HANDOFF.txt:19-27`.** The current P1/P7/P8 editions (12/10/13 pages) are precisely the three packages whose original-source comparisons are **still outstanding** (Quint/Lucas/Stuart, Cao/Owen, ABV publisher-final). Pointing public links at them while labeling the predecessors "source-checked" inverts the verification status without caveat. Also, the P1/P7/P8 → Acyclicity/Static-Subsidies/Truthful-Production mapping is never stated, and "thirteen-page" collides with Cross-Moment. *Verify:* name the papers and add "newer exposition; priority comparison incomplete."

**5. Medium — `READINESS_REPORT.txt:6,13-19`.** "byte-identical main manuscript" sits beside "exported fresh PDFs with three pdfTeX passes," so the 25 Oct PDF is a new render labeled "scientific version 24 October." State explicitly that byte-identity applies to sources, not to the historical canonical PDF bytes.

**6. Low — directory labels.** `2026-10-20-power-state-gate` (author 21 Oct) and `2026-10-18-local-improvements` (author 19 Oct) keep dates the sync README calls corrected; the correction lives only in prose. Add an in-directory DATE_NOTE. Also, "finished on 21 October" rests on `end_utc=04:11Z` = 00:11 EDT.

**7. Low — `READINESS_REPORT.txt:12-16`.** 133 manifest entries vs. 78 copied canonical inputs vs. 2 changed files are unreconciled.

The noon-EDT rule is applied consistently: every group's assigned day equals the latest-EDT day of its cited completion timestamp.

## Scope limitations
`IMPORTED_FILES.json`, `LOCAL_ONLY_FILES.json`, repo `README.md`, `PAPERS.md`, cited campaign status files and git history were not supplied; hashes, exclusions, and actual commit/date assignment are unverified. No tools run.
