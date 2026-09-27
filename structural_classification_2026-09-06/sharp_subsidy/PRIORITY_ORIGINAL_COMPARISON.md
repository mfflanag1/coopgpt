# Priority-games original: completed accepted-manuscript comparison

Audit date: 2026-09-07. Global bounds remain 1/3 <= S_3 <= 2/5. Novelty remains unconfirmed.

## Version and retrieval

Iago Núñez Lugilde, Arantza Estévez-Fernández and Estela Sánchez-Rodríguez, *Priority coalitional games and claims problems*, Mathematical Methods of Operations Research 100 (2024), 669–701, DOI https://doi.org/10.1007/s00186-024-00876-x.

The [free Vigo original](https://www.investigo.biblioteca.uvigo.es/xmlui/bitstream/11093/11185/4/2024_coalitional_games.pdf) was retrieved successfully through the public repository link. The cover labels it an accepted manuscript, not the Version of Record; its title page is dated May 22, 2024. Retained PDF: 689430 bytes. Manifest records SHA-256 hashes, source and resolved repository URLs. Python retrieval failed on local certificate validation; the system HTTPS client succeeded without disabling verification.

## Specific comparison with the original

Definition 2 and Lemma 2 (PDF page 7; manuscript page 6) distinguish arbitrary imputation references from core references. For reference x and priority group Q, the weak-priority game is max(v(S),x(S intersect Q)) on proper coalitions, retaining grand value v(N). Core membership of x guarantees balancedness; it is not necessary to define the transformation. Definitions 3–4 and Lemma 8 add upper bounds for outsiders in the strong-priority construction (PDF pages 10–11). Theorems 3 and 10 concern claims games and references.

The published preview's footnote 3 phrases the definition using a core reference while explicitly allowing extension to imputations. The inspected accepted manuscript instead places x in I(v) in Definition 2. Do not silently equate these versions. The required model/intervention comparison is complete for this author original; post-acceptance textual changes and the entire published proofs have not been compared.

## Exact connection to the present optimization

The following is our bookkeeping application of the inspected definition, not a novelty claim.

Write l_i=H_i/3 for the frozen original floors. For each player i choose a nonnegative imputation a^(i) of the ORIGINAL game satisfying a^(i)_i=l_i and sum a^(i)=T. Such an imputation exists: 0<=l_i<=T, singleton original worths are zero, and there is another player to receive the remainder. No core membership is asserted.

Form the weak-priority transformation with reference a^(i) and group {i}, then take their pointwise maximum over i. Call the resulting auxiliary game h. It has h(N)=T and, for proper nonempty S,

    h(S)=max(v(S), max_{i in S} l_i).

Its ordinary cost-of-stability subsidy is exactly s_3(M). Indeed, a nonnegative vector covering h covers v and, from singleton constraints, every l_i. Conversely original coalition coverage and all singleton floors imply y(S)>=v(S) and y(S)>=l_i for every i in S, hence cover h. Total T+s is identical on both sides. This is a comparison device: original v and H remain frozen in the actual problem.

This h differs as a characteristic function from max(v(S),sum_{i in S}l_i) in the earlier audit, but has exactly the same nonnegative covering polyhedron. It shows that the floor intervention can be assembled from existing weak-priority transformations. The individual reference imputations need not be core points, so the source's balancedness theorem supplies no zero-subsidy conclusion. Generic floor constraints, priority transformations and cost-of-stability optimization are established ingredients. A contribution would have to lie in the restricted assignment-market bounds and constructions.

## Remaining obligations and no-go record

No claim of a sharp frozen-ideal assignment constant was established by this comparison. It does not constitute an exhaustive literature search or external proof review. Quint, Lucas and Stuart's 1997 full-original comparisons remain unresolved. Stuart's later author chapter was already audited elsewhere in this project and was not counted again as new evidence. The research goal remains active.

The previous VU HTTP403 and browser-reader failures are retrieval history, not evidence of permanent inaccessibility. The Vigo accepted original is now available locally. Do not repeat those failed endpoints as if the source were still entirely missing.
