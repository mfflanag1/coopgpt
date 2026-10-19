**Provisional verdict: findings (one consequential inconsistency; otherwise comparisons are mathematically sound and scoped).**

## Findings

**1. Medium — Priority2024 bibliography note contradicts the body text and the source ledger.**
`manuscript.tex:638`: "The source comparison uses the accepted manuscript dated May 22, 2024."
`manuscript.tex:114`: "In the final version of \citet{Priority2024}, Definitions 2 and 4 and Lemmas 2 and 8 …"
`ijgt_SOURCE_PRIORITY.txt:24–41`: the comparison was made on the Version of Record (VU repository); the Vigo accepted manuscript "is a DIFFERENT version" and "is not evidence that the final definitions are unchanged."
The new paragraph correctly asserts final-version content, but the unchanged bibitem sentence states the opposite evidentiary basis. Because the ledger records that the accepted version put *imputation* in the formal definitions while the final puts *core*, the two statements are not interchangeable. Verification: delete or rewrite line 638 to cite the Version of Record (VU URL / DOI) as the inspected text.

**2. Low — Characterization of Priority2024 omits footnote 3 (imputation extension).**
`manuscript.tex:114–116` says the definitions "use a prior core allocation." The ledger (`:29–30`) records that "footnote 3 extends formulas to imputations." The exclusion claim at `:116–117` ("do not supply the sharp subsidy constant for our possibly incompatible floors") remains valid regardless, since Lemmas 2/8 preserve grand worth $T$ and the floor $H/3$ has total $\le T$ (line 529), so a priority game over any $x\ge H/3$ adds no subsidy. But the paragraph's description of the antecedent is narrower than the ledger's reading. Suggested fix: add "(footnote 3 extends the formulas to imputations)" to avoid an inaccurate-by-omission description that a referee familiar with the paper could flag.

**3. Low — Attribution granularity.** `:114–116` attributes "restrict the original core" jointly to Definitions 2/4 and Lemmas 2/8; the ledger (`:30–31`) attributes core restriction to the Lemmas and core-membership of $x$ to the Definitions. Not wrong as a conjunctive sentence, but the parsing is loose.

**Checked and found sound:**
- Bejan–Gómez (`:107–112`): "ordinary minimum is zero" follows from nonempty original core (take $x\in\core$, zero addition); "extended core coincides with the core for balanced games" and the Aug 1, 2008 / §2 pp. 5–6 citation match the ledger (`:8–21`). "Need not itself be efficient or stable" is consistent with $\sum_i l_i\le T$ (line 529).
- Both antecedents are framed as "established antecedents," not excluded as priority; no global novelty is claimed (`:141–145`), consistent with ledger disposition.
- Declarations (`:584–585`, email `:21`) match `AUTHOR_ACTIONS.txt:1–4` (confirmed: no funding, no competing interests, that email).
- Line 141–143 retains the open-priority caveat for Quint/Lucas/Stuart, consistent with ledger gaps.

## Scope limitations
- I did not inspect the Bejan–Gómez or Priority2024 originals; comparison is against the ledger's recorded reading only.
- `AUTHOR_ACTIONS.txt:9–10` lists city/country of residence as still needed; the manuscript title page lacks it. Not a false assertion, but an unresolved admin item outside the related-work scope.
- Bachrach et al. 2009 arXiv ID and Meir et al. Section 2.2 citations are pre-existing and not checked here.
- Model/proof sections stated byte-identical; not reviewed.

## Verdict
**Findings.** Fix Finding 1 before submission (one-line bibliography correction); Finding 2 is a recommended precision edit. No overclaimed priority exclusion detected; new comparisons are mathematically correct under the stated hypotheses.
