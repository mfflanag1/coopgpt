**Provisional verdict: findings — material corrections, no fatal defect found in the checked arithmetic.** Most important: the outreach draft presumes a packet state that does not exist yet (no current compiled PDF), and the brief introduces an unsourced "s^{1/4}" baseline that reads as a literature claim.

## Findings

**1. Blocker (process) — email vs. packet state.** `MARINA_REVIEW_REQUEST.txt:30` says the packet "includes the manuscript." `packet/README.txt:11–15` says the only PDFs are stale 18 Oct exports, excluded, with fresh export pending permission, and "Do not describe this as a current PDF packet." Either obtain export and send a current PDF, or revise the email to state the manuscript is supplied as standalone LaTeX source. Also `README.txt:29,35` point to "the enclosing handoff" for replay outputs and the readiness disposition — dangling references for an external recipient; include or strip.

**2. High — overclaim risk in brief.** `specialist_brief.tex:15–16`: "raises the recorded unrestricted arity-three lower from order s^{1/4} to order s^{1/2}." Nothing in the manuscript, matrix, or email defines where s^{1/4} was "recorded." A specialist will read this as the prior literature state, contradicting `README.txt:40` ("Novelty remains unconfirmed"). Replace with "raises this project's earlier internal certificate" or delete.

**3. Medium — missing hypotheses in email.** `MARINA_REVIEW_REQUEST.txt:18` uses `s` without defining it (bound on protected-coalition size, with coverage for *every* coalition); line 13 "each allowed coalition" is ambiguous about whether coverage is also size-limited. Line 17 presents the dimension bounds as "sharp" while hedging only the sqrt(s) claim, though `REVIEW_SCOPE.txt:15–19` lists the OUT dimension lower as unverified analytic work. Hedge symmetrically.

**4. Medium — funding normalization.** The email says "factor" (lines 18, 20) without stating it multiplies *total* payment (supplement = (κ−1)F). Manuscript (`manuscript.tex:198–203`), brief (§1), and matrix (line 33) are consistent; the email should carry one sentence of the same normalization so a first-pass reader does not misread 1+1/√2 as a supplement.

**5. Low — reproduction instruction mismatch.** `specialist_brief.tex:196–197` names one graph checker; `README.txt:23–26` names two and advises a scratch copy. Align.

**6. Low — presentation.** `PRIORITY_MATRIX.txt` has run-together tokens (line 2, 24, 28, 102: "funding1+1/sqrt(2)", "every0<alpha<1"). Fix before external send.

**Coalition-sum vs. group strategyproofness:** no conflation found. `PRIORITY_MATRIX.txt:151–158` and `manuscript.tex:224–229` explicitly distinguish them; the Immorlica implication direction (line 63–66) is stated correctly.

**Bounded job:** the scope is large (≈15 correctness items + P1–P5). The email promises "first pass or referral" but names no entry point. Recommend naming Section 5 plus brief §3 (one page) as a self-contained first target.

**Arithmetic spot-checks that passed:** `eq:central-bound` induction (difference = M), B₆ = 493/243, the tail asymptotic, `cor:tail` maximizer argument, `eq:coefficient` derivation and sign, P6 obstruction flow feasibility, and the (4,1,1,1) ratio in `graph:scope`.

## Scope limitations
No files executed; "625 profiles" and "34,440 inequalities" counts unverifiable here. Did not audit the OUT dimension lower (Lemmas `dim:price-reduction`–`dim:pair-obstruction`), the graph holding-cube cell inequalities, or third-party sources. Cannot verify recipient suitability or address.

## Verdict
Findings: one process blocker (#1), one material text correction (#2), several minor alignments. Packet is otherwise coherent on contract, normalization, and version boundaries; no mathematical gap identified in the checked portions.
