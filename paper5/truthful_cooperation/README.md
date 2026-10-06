# Subsidies for truthful cooperation

**Sharp unrestricted bounds in weighted multi-glove games** — Maxwell Flanagan, 6 October 2026.

The [current manuscript source](manuscript.tex) and [current specialist brief](specialist_brief.tex)
now incorporate the unrestricted hierarchy theorem and its complete proof:
the minimax total-payment factor is **(1+o(1)) log k/log log k**.
The new profile-averaged hierarchy closes the leading-constant gap at 1.
Historical novelty and human specialist assessment remain open.

- [Current portable source and verification packet](truthful_cooperation_review.zip).
- [Source comparisons](SOURCE_COMPARISON.txt), [reviewer recommendations](REVIEWERS.txt), and [unsent outreach drafts](OUTREACH_DRAFTS.txt).
- [Sharp-theorem audit](review/SHARP_RESOLUTION.txt) and [earlier integration audit](review/INTEGRATION_RESOLUTION.txt) and [current validation](validation/INTEGRATION_VALIDATION.json).
- [Leading-constant campaign and sharp proof](../../research_campaigns/2026-10-06-leading-constant/CONTRACT.txt).

The existing [manuscript PDF](output/pdf/manuscript.pdf) and
[brief PDF](output/pdf/specialist_brief.pdf) are **historical pre-hierarchy snapshots**.
They are not the current review packet and must not be sent as the revised result.
The existing LaTeX sources compile in the native editor, including the already-open
brief. No separate PDF was compiled or new editor tab opened for this revision.
Export refreshed PDFs from the native editor before sending PDF attachments.

The paper also retains the all-profile capped continuous-Banzhaf upper bound,
a strict finite-k probability refinement, the sharp proportional-class leading
constant, and restricted-domain nonlinear constructions. Model and functional
precedents are explicitly credited. All are parts of one manuscript candidate.

Run with Python 3.9 or later (standard library only):

```sh
python3 -B -O verification/run_sharp.py
python3 -B -O verification/run_hierarchy.py
python3 -B -O verification/run_all.py
```

The first verifies 24 exact weighted-profile duals and 168 corruptions.
The second checks source hashes, 14 exact single-base hierarchy certificates (including padding
and 98 rejected corruptions), and 24 exact pairwise probabilities in fresh temporary
directories. The third replays the six earlier verifiers and compares canonical
report hashes. Use `--output /tmp/coopgt-checks` to choose an output location.
Finite checks support the full written proofs; they do not certify novelty or a
universal theorem by themselves. The packet contains sources and executable certificates,
without third-party articles, stale PDFs, contacts or private review transcripts.
External outreach remains unsent.
