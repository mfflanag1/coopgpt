# Specialist review packet: sharp cost of one-third core-maximum protection

**Status:** internally proved; human review and historical novelty unconfirmed. This packet has not been sent.

## Question and answer

Three equal finite sectors, nonnegative pair-additive full triples only, integral coalition matching worth, positive grand worth T and nonempty original entire core C. Freeze H_i=max_C x_i. How much extra grand-coalition budget is needed to retain every original coalition inequality while paying every player at least H_i/3?

The proposed theorem gives s/T<1/3 for every finite market and sharp supremum S3=1/3. A retained all-parameter family attains s/T=2q/[3(2q+1)]. For each integral partial matching with k unmatched players per sector, its obstruction is at most 2(k-1)T/[3(2k-1)] for k>=1, and this bound is sharp across markets for each k>=2. This finite-k bound is not asserted for arbitrary fractional residual mass.

## Read in this order

1. [Complete proof](SHARP_ONE_THIRD.md), Sections 1–5: the direct fractional upper bound. The decisive pair is V<=5T-B and V<=3T+B-C_2/k; averaging proves the sharp constant.
2. Sections 6–8: the sharp integral correction, complete lower construction and nonnegative slack identities.
3. [Review adjudication](../reviews/sharp_theorem/ADJUDICATION.md) and [reproduction](REPRODUCE.md): executed checks, review scope and negative controls.
4. [Source comparison](SOURCE_COMPARISON.md): established ingredients, closest antecedents and unresolved originals.

## Questions for a specialist

- Is the attaining-witness transfer in (2), followed by the six-permutation aggregation, valid without simultaneous maxima or sparsity? We explicitly retain repeated labels and multiplicities.
- Does the weighted residual argument (7) cover all real fractional packings, including zero residual coordinates and k=0 separately? Is compact dual attainment enough for the finite-market strict inequality?
- Is the retained all-q chain witness proof exhaustive for every full triple?
- Is this aggregate inequality or sharp constant already implied by work on multisided assignment games, payoff floors or priority games, especially the unread Quint/Lucas/Stuart originals? The underlying model and fairness question are not claimed new.

The proposed new element is the combination of compatibility inequalities yielding the sharp bound. The subsidy LP, tightness, core extrema, half-optimal-core question and earlier project lower family receive separate credit. No change of coalition model or post-subsidy recomputation of ideals is allowed.
