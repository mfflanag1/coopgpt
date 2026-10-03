# Opposite-model literature QA

3 October 2026. Reviewer: **native Astra**, the in-process Codex agent conducting this source inspection, not a new CLI review run. Reviewed delegate: completed Fable research run `20261003-132011-54f36e1c`; its request records engine `fable`, model `claude-fable-5-1`. No purchases, outreach, recursive delegation, or canonical edits.

**Verdict: useful partial research, with a material coverage failure; no novelty clearance.** The principal Meir and Atay–Núñez comparisons are supported, subject to the qualification below. Preserve the delegate's partial-read and abstract-only labels. Do not count the half-optimal-core search as successful, or describe the candidate as cleared against Quint and the other unread originals.

## Verified findings

1. **Meir–Rosenschein–Malizia is a real framework antecedent, with a domain qualification.** The [author PDF](https://www.cs.huji.ac.il/~jeff/papers/coopmas11meir.pdf), §2 pp. 3–4, defines preimputations x with total v(N), then defines `CoS(x,G)` as the least grand-coalition subsidy permitting a stable payoff coordinatewise above x. Fable's comparison is sound as an antecedent, but our floor `l=H/3` may sum to less than T and is not automatically such a preimputation. Our own bookkeeping extension is

       s(l,G) = min_{x>=l, sum x=T} CoS(x,G),  when sum l<=T.

   Any stable y>=l with total at least T dominates some x in that displayed feasible set; the converse is immediate. This is our comparison, not a theorem quoted from the paper. Its relative cost uses `(T+subsidy)/T`, not `subsidy/T`. Section 2's definitions concern positive monotone games; the inspected √n and coalition-size bounds in Theorem 2/Proposition 1 explicitly concern superadditive games. Neither establishes the candidate's frozen-ideal sharp ratio.

2. **Atay–Núñez confirms the model distinction and the Quint lead.** In the [author original](https://ataatay.github.io/webpage/Atay_Nu%CC%81n%CC%83ez_2019_ANOR.pdf), printed p. 273 expressly attributes pair-additive m-tuple values and zero worth for smaller coalitions to **a model in Quint (1991)**. Its own §2, pp. 274–275, instead permits productive connected sub-tuples, including pairs. Thus Fable's basic comparison is correct. The stronger wording “the frozen model is Quint's” should remain qualified: this is a later author's description; the exact original hypotheses and results have not been compared. Proposition 2, p. 284, provides simultaneous sector maxima for a cycle-free quotient graph. Example 5, pp. 288–289, demonstrates failure of same-sector joint attainment with a nonempty core in their cyclic model. These are genuine prior structural ingredients, not a subsidy-bound comparison or novelty clearance.

3. **Marchi–Oviedo remains a full-original gap; one misleading free link was identified.** The [publisher abstract](https://www.sciencedirect.com/science/article/pii/S0377221796001762) is available in indexed search and expressly distinguishes its model from Quint's. It does not specify enough structure to settle relevance. [Oviedo's publications page](https://sites.google.com/view/jorgeoviedo/publicaciones) lists the 1997 paper with a [PDF link](https://drive.google.com/file/d/1VSzLH_jjQfOELIv206q_A0vf2CKTXi4f/view). The public download succeeds, but its title page identifies **Jorge Oviedo, “The core of a repeated n-person cooperative game,” EJOR 127 (2000), 519–524**, a different paper. Do not mark the requested original retrieved. I did not purchase or request it.

## Coverage failure and retained gaps

- Fable's “half-optimal core unidentified” statement is contradicted by the supplied canonical `structural_classification_2026-09-06/simultaneous_protection/SOURCE_STATUS.md`: it names Núñez–Rafels, *Bargained stable allocations in assignment markets*, links [free Working Paper 153](https://www.bse.eu/sites/default/files/working_paper_pdfs/153.pdf), and records its inspection of Definition 6 and relevant pages. This is a task-execution failure, not an unavailable-source finding. The coordinator is independently reopening that original; I have not duplicated that paper inspection here.
- The same ledger already says the 2026 extrema full text was recovered. Fable's successful retrieval is useful reproduction, but should not be reported as the first resolution of that historical gap. I did not verify its detailed 2026 theorem table; the coordinator owns that check.
- `PRIORITY_ORIGINAL_COMPARISON.md` already records successful local retrieval and an accepted-manuscript comparison of the 2024 priority-games paper. Fable correctly says that prior comparison stands unrefreshed. Its newly failed endpoints do not undo the earlier retrieval. I read the local comparison, not that original again.
- Quint, Lucas, Stuart, Marchi–Oviedo, later unread Vazirani theorem sections, and the abstract-only matching/guarantee leads remain incompletely compared. No implication audit of those sources occurred in this QA. The coordinator is separately reading the new stable-payoff-guarantees preprint.

## Exact read scope and provenance

Read all of Fable's `result.md` and the two requested local source ledgers. Independently retrieved and read targeted passages of Meir: §2 definitions, §2.2, relative-cost definition, Theorem 2 and Proposition 1 statements; Atay–Núñez: introductory comparison p. 273, §2 definitions/equations, Proposition 2 and proof, and Example 5. These were targeted text-extraction reads, not fresh complete-paper reads. Read the indexed Marchi–Oviedo publisher abstract and the author publications entry. Downloaded the linked PDF and checked its title/abstract, which exposed the mismatch; no conclusion about the actual Marchi–Oviedo full text follows.

Fable result SHA-256: `6a629321884108f7d71a08d3e84ef42beb24f0f1d34a599366d640f5c217a35f`.

Wrongly linked PDF: `/private/tmp/coopgpt-witness-20261003/oviedo_2000_mislabeled_link.pdf`, 104,186 bytes, SHA-256 `55a6aa4c70aaab728e728128f4751ff9de6264c7684730187d1d60cd172a3d46`. Its misleading original download name was corrected after title verification.

Recommended adjudication: retain verified entries as partial research; record the missed supplied half-optimal source as a material completeness failure. This note supplies evidence for coordinator adjudication; it does not mutate the routing ledger or certify the candidate's novelty.
