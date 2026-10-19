## Provisional verdict
**No directly matching theorem found in the reviewed scope; no proof of non-implication.** Marchi & Oviedo contain no subsidy, no individual core-maximum (H_i), and no ratio bound; their only optimization statements (Theorem 1, Lemma 2, Proposition 1) concern core non-emptiness via LP integrality on a *different* polytope, so they cannot yield the H_i/3 constant as an immediate corollary.

## Findings

**F1 (informational — primary). Distinct player set: payoffs are indexed by (m−1)-tuples, not agents.**
Evidence: p.618, "A player (team) or agent of the second species of type j is an (m−1)-tuple of agents, one of each type without an agent of type j" (lines 66–71); core vector "w = (w_{i_j})_{i_j∈N}" (line 114); the m=3 example's core variables are all pair-indexed, e.g. `w_(12,13) + w_(11,13) + w_(11,12) = 1` (lines 162–170). There is no payoff coordinate per individual sector agent, hence no definable H_i = max_{x∈core} x_i in their model. Any reduction would require constructing an agent-level game, which the paper never does.

**F2 (informational). Primal constraint geometry differs (line sums vs plane sums).**
Evidence: (P), p.619 lines 182–191: `Σ_{i1} p_{i1,…,im} ≤ 1 for all i2,…,im`, etc. — one summation index, all others fixed (a multi-index *transportation* / line-sum polytope); restated at lines 401–427. The manuscript's dual polytope is `p_i = Σ_{e∋i} λ_e ≤ 1` (snapshot lines 191–194), i.e. for sector 1, `Σ_{i2,i3} λ_{j,i2,i3} ≤ 1` — a plane sum, the axial 3-index assignment polytope. These are not the same LP, so Theorem 1 (lines 206–208) and Proposition 1 (line 383, restricted further to n_i = 2) do not transfer.

**F3 (informational). No pair-additivity, no non-empty-core hypothesis, no subsidy.**
Their c_{i1…im} are arbitrary nonnegative constants (lines 90–91); the manuscript's v(e)=A+B+C (snapshot eq. (2.1)) drives Lemmas `range`/`comparison`, which have no analogue here. Marchi–Oviedo's emphasis is the opposite direction — empty cores (abstract line 20; p.622 example, lines 275–321).

**F4 (evidence quality). OCR/typographic ambiguity.**
"A full assignment is an assignment with k = min{n_1,…,n_m}" (p.618, line 84) is inconsistent with the m=3, n_j=2 example, whose maximal matching has k=4 (lines 154–157). Treat as corrupt; do not cite. Index subscripts are heavily garbled throughout (lines 69–71, 162–170, 432–444), so fine-grained claims about their notation need the publisher PDF.

## Scope limitations
Only the supplied 9-page extraction and the manuscript snapshot were read; no external search, no PDF re-render, no execution. I cannot exclude an indirect reduction via some unstated composition, nor assess Quint (1991), Lucas (1995), or Stuart (1997).

## Recommendation
No manuscript change is required; Marchi–Oviedo is not a necessary citation. Safe ledger wording:

> Marchi & Oviedo, EJOR 98 (1997) 617–625, inspected in full (author-hosted text extraction, 2026-10-18). Model: m types, players are (m−1)-tuples (p.618); primal (P) uses single-index line sums (p.619). Theorem 1 characterizes core non-emptiness by LP integrality; Lemma 2 and Proposition 1 are auxiliary. No subsidy, no individual core maxima, no ratio constant. No directly matching or subsuming statement located; no general non-implication established. OCR garbling noted (the "k = min{n_j}" line, p.618, conflicts with the paper's own m=3, n_j=2 example); page-level claims should be re-checked against the publisher PDF before submission.
