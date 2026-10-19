**Provisional verdict: findings (two concrete overstatements, both minor-to-moderate and fixable by scope wording).**

Most important concrete finding: the acyclicity manuscript asserts an inference about the Gangam et al. example that it presents as established, but the snapshot gives no evidence the cited page contains the core description the inference needs.

## Findings

**1. Unsupported "entire core is the unit simplex" attribution (Moderate).**
`acyclicity_ijgt/submission/manuscript.tex:115–118`: "Gangam2026, p.1621, give a unit-capacity path whose equitable payoff is $1/r$ on each of its $r$ edges. Its entire core is the unit simplex; therefore each ideal equals one and even the best simultaneous fraction is $1/r$. This last conclusion is an immediate inference from that example."
Evidence of defect: the sentence "Its entire core is the unit simplex" is stated unhedged, as if read from p.1621, while only the final sentence is flagged as the author's inference. No ledger entry in either `SOURCE_PRIORITY.txt` records inspection of Gangam et al. at all — it appears in neither the acyclicity ledger's "NEW DIRECT SOURCE COMPARISONS", "REMAINING FULL-ORIGINAL GAPS", nor the truthful ledger. So the snapshot contains no evidence that the cited page was inspected or that the core-description premise is the authors' rather than the manuscript's.
Minimal correction: attribute explicitly what is read vs. derived, e.g. "give a unit-capacity path with equitable payoff $1/r$ per edge (p.1621); for that instance the core is the unit simplex, from which each ideal equals one and the best simultaneous fraction is $1/r$ — both the core description and this conclusion are our inferences from the stated example."
Verification: check p.1621 for whether a core characterization is given there; if not, re-scope as above.

**2. Ledger/manuscript mismatch on ABV final-version status (Minor–Moderate).**
`truthful_production_et/source/manuscript.tex:144–150`: "Their inspected author version defines... Its Theorem 1 proves own-resource monotonicity..." — correctly version-scoped. But line 723–724 bibliography says "Comparison uses the author manuscript at hal.science/hal-01400498v1", and the ledger (`truthful_production_et/SOURCE_PRIORITY.txt:63–70`) states "no version equivalence or final numbering has been verified" and that whether the final changed hypotheses/conclusions "is also unverified." The manuscript's Online Resource 1 claim of "a strictly concave counterexample to a universal extension of that evidence, with a version-specific comparison" (lines 150–153) is consistent, but the main-text phrase "Its Theorem 1" without the version qualifier adjacent could read as a final-version theorem number.
Minimal correction: write "Theorem 1 of that author version". No substantive claim change needed.

**3. Checked, no defect found (for the record).** Quint/Lucas/Stuart/Marchi/Cao/Owen gaps are disclosed in-manuscript (`acyclicity...:143–146`; `static_subsidies...:142–146`; `truthful...:12–50`, 160–162) with explicit "no theorem below relies on such an uninspected statement" and no nonoverlap inference. The Nuñez–Rafels, Atay–Núñez, Bejan–Gómez, Priority2024, Meir/Bachrach, and arXiv:2502.08248v1 comparisons each carry version, section, and page specifics matching the ledgers, and each disclaims novelty of the benchmark/framework. I found no invented theorem numbers and no claimed priority clearance.

## Scope limitations

- No originals were available to me; I cannot confirm that any cited section/page actually contains the described content, including items the ledgers call "inspected."
- `SOURCE_RECEIPT.json`, `qa/` files, Online Resource 1/2, and the compendium are referenced but absent; their consistency is unverified.
- I did not audit internal proof correctness, and I did not evaluate whether Theorem statements are implied by inaccessible originals — that remains genuinely undetermined, as the ledgers state.
- Line references are to this snapshot's numbering.

## Verdict

Findings: two attribution/scope defects (items 1 and 2), both repairable by wording. No evidence in the reviewed scope of overstated non-overlap against inaccessible originals.
