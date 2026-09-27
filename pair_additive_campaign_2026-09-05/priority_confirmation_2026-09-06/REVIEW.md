# Priority assessment of the vanishing-protection theorem

6 September 2026. Follow-up to the user's request to confirm novelty. Scope: the latest pair-additive theorem, not a new priority verdict on every earlier CoopGT paper.

**Verdict: no earlier result establishing the exact theorem was identified in the sources reviewed. It remains a credible, specific novelty candidate; historical priority is not confirmed.** This follow-up strengthens the comparison with older models and representation results. It does not justify replacing “to our knowledge” with an unconditional first-result claim.

## Exact claim that survives

The [proved family](../cycle5/root/VANISHING_FAMILY.md) has, for every integer q≥1:

- Three fixed sectors, each with 3q+1 players; all full triples are available, and only full triples produce value.
- Triple values A_ij+B_ik+C_jk, with pair entries in the fixed integer alphabet {0,1,2} and triple values at most 5.
- Integral matching worth 6q+1 and a full payoff core containing a strictly positive allocation.
- One labeled player's full ascending-leximin payoff equal to 1/[3(q+1)], fixed throughout the first optimal face, and its ideal over the same entire core equal to 1.

Consequently c_pair=0. The candidate contribution is this simultaneous restricted realization. Merely bounding real weights would be weaker: rescaling each instance preserves payoff-to-ideal ratios. The fixed integer alphabet avoids that normalization explanation.

## What the additional review established

### Older strict chains do not directly contain this family

Stuart's [author chapter](https://columbia.edu/~hws7/Stuart%202001%20CG%20and%20Bus%20Strategy.pdf) gives the supplier–firm–buyer formula and discusses coordinate core intervals. The original final [Atay–Solymosi 2018 article](https://ataatay.github.io/webpage/Atay_Solymosi_2018_EL.pdf), Definition 3 and equations 1–2, specifies the signed two-pair chain with negative triple totals replaced by zero. Its bargaining-set results do not state this sorted-leximin theorem.

Our deduction: if M_ij=max{r_i+s_j,0}, any 2×2 slice with both diagonal entries positive must have diagonal sum no larger than off-diagonal sum. The new family's AB, AC and BC slices include respectively [[2,1],[0,1]], [[3,1],[1,1]] and [[1,0],[0,1]]. Each violates that condition. Thus no ordering of its three sectors, relabeling within sectors, or alternative two-pair decomposition makes the actual tensor a strict chain. This excludes direct application of the read chain model, including its zero-truncation convention. It does not exclude auxiliary-player or transformed-core representations. See the [classical comparison](classical_chain/CLASSICAL_CHAIN_REVIEW.md).

### General representation theorems do not supply the missing implication

De Loera–Onn's [transportation universality manuscript](https://www.math.ucdavis.edu/~deloera/RECENT_WORK/ipcouniversality.pdf), Theorems 1–3, concerns primal transportation coordinates. Its constructions use margins, forbidden entries or auxiliary coordinates; the three-way line-sum dual has pair-indexed prices. No inspected theorem identifies the required entire labeled player-payoff core while preserving full leximin, coordinate ideals and the pair-value restrictions.

The [Demange–Deng 2010 paper](https://www.econstor.eu/bitstream/10419/98563/1/749510048.pdf) supplies classical packing/production and core-integrality principles, not the required fixed-three-sector realization. [Kumabe–Maehara 2020](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p663.pdf), Corollary 3.4, restricts positive uniform convex hypergraph matching games to disjoint hyperedges. That class does not directly contain this overlapping construction. The inspected [Conitzer–Sandholm 2006 gadget](https://www.cs.cmu.edu/~arielpro/mfai_papers/CS06.pdf) uses growing coalitions and values; it does not give the needed fixed-rank representation.

There is also a direct barrier to copying the old flow-path simplex unchanged. A positive rank-three coalition in a game on more than three players excludes a simplex vertex that pays everything to an omitted player. Therefore the positive all-player simplex cannot be the identical labeled full core of such a rank-three matching game. This only rules out that identical-core transfer; projections and auxiliary-coordinate reductions require separate examination. See the [representation audit](representations/REPRESENTATION_AUDIT.md).

### Similar terminology does not establish the same result

The original [Tejada–Rafels working text](https://diposit.ub.edu/bitstreams/92331b85-c564-429d-866c-e063a2d7b3b0/download) characterizes a threat-based bargaining selector. Its inspected example does not supply an all-size vanishing family. Other primary texts found by “leximin” searches optimize over attainable outcomes outside the efficient core, or study stable coalition partitions. Those objects cannot silently replace the full transferable-payoff core. Exact read scopes and the example calculation are in the [terminology audit](root/TERMINOLOGY_AUDIT.md).

## What was already known

These credits from the [preceding audit](../cycle5/NOVELTY_LEDGER.md) remain essential:

- Coordinate protection relative to a player's ideal is explicit in Núñez–Rafels's [2004 working paper](https://www.bse.eu/sites/default/files/working_paper_pdfs/153.pdf), Definition 6.
- A flow-path example in [Gangam–Garg–Shahkar–Vazirani](https://arxiv.org/pdf/2403.06037), §3.1.4, already yields vanishing protection in a broader game class. The ideal-ratio calculation is our deduction from that example.
- Pair-additive modeling, sorted selectors, LP duality and matching-cover budget arguments are established ingredients.

The 2020 assortative and distinct 2026 locally monotone supermodular extrema papers were inspected in the prior cycle. The saved q≥3 tensor obstruction excludes their hypotheses after within-sector relabeling. That does not settle all possible representations, and their restrictions cannot be assigned to the unread 2023 paper merely because the authors overlap.

## Material gaps that prevent confirmation

| Original | Coverage and remaining priority question |
|---|---|
| Quint, *The core of an m-sided assignment game* (1991; CAM88-24 in 1988) | Current author list located, original theorem/example text still unavailable. A relevant construction or core representation remains unexcluded. |
| Lucas, *Core theory for multiple-sided assignment games* (1995) | Original inaccessible. Publisher metadata establishes 81(1); later bibliographies support pages 55–65, not the unsupported 81–108. Original theorem scope remains unread. |
| Stuart, *The supplier–firm–buyer game and its m-sided generalization* (1997) | Later same-author exposition and a full later primary article clarify the three-sector chain. They do not establish everything in the original or its broader extension. |
| Martínez-de-Albéniz–Rafels–Ybern, *Extreme Core Points in Multisided Assignment Problems*, SSRN4369524 (2023) | Identity and abstract checked; theorem text unavailable. Its stated core-computation/representation route could matter. This is distinct from the recovered 2020 assortative paper. |

The [original-source follow-up](old_core/PRIORITY_REPORT.md) records legitimate alternate author and institutional routes. Failed retrievals count as gaps, not as evidence that an antecedent does not exist. Earlier modern-version and bargaining-text gaps also remain as specified in the preceding ledger. No external specialist has reviewed this exact theorem, and no outreach was sent.

## Publication wording and decision

Suggested qualified wording:

> We construct complete strict three-sided assignment markets with nonnegative pair-additive values, using only pair entries in {0,1,2}, whose cores contain strictly positive allocations but for which a player's full leximin payoff divided by its whole-core ideal tends to zero. To our knowledge, this restricted-class vanishing result has not previously been established.

Use that wording with the explicit prior credits above. Do not claim a new fairness criterion, the first vanishing example across all cooperative games, or a confirmed field-level breakthrough. Mathematical correctness, historical priority and importance are separate assessments.

The next action that can materially improve confidence is targeted comparison against the missing original constructions and expert assessment of equivalent representations. More repeated keyword searches without new source access would add little. A useful review question is: does any earlier theorem or example imply this exact statement while preserving the three fixed sectors, strict production, full labeled payoff core, full leximin and fixed integer pair alphabet?

## Audit trail and verification

Four independent routes supplied 33 new focused queries in total (8 terminology, 8 historical author routes, 9 classical including one pagination check, 8 representation), plus primary reads and reference tracing. Query counts describe work performed; they do not measure completeness of the literature.

Reports and raw query/retrieval ledgers are preserved in the four subdirectories. Retrieval errors and read scopes are explicit. Source originals were used where accessible; later bibliographic corroboration is labeled as such.

The unchanged cycle5 build passed with `--full` on a fresh scratch copy, including rational covers and three raw-core SMT exclusions. Before integration, all 257 campaign manifest entries and all 60 cycle5 manifest entries matched. The three chain-scope slices were independently evaluated at q=1 and q=4; their all-q identities follow directly from the construction. See [verification](VERIFICATION.json) and [build output](BUILD.log). These checks support the theorem and source-comparison deductions; they cannot certify absence of prior work.
