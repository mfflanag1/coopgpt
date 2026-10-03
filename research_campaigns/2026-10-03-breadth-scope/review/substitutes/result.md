**Result: the generic proposition is false.** There is a hand-checkable 5-player counterexample; it is not an arc-player flow game, so it does not refute source-arc joint attainment or C2, which remain UNKNOWN. Nothing was run and no sources were retrieved; everything below is derived by hand from the three supplied files.

## Counterexample (generic proposition only)

N = {1,2,3,4,5}, S = {1,2}. The basic coalitions are {3,4} with value 1, {1,4,5} with value 2, and {2,3,5} with value 2. Define:

- v(N) = 3
- v(A) = 2 if A ≠ N and A ⊇ {1,4,5} or A ⊇ {2,3,5}
- v(A) = 1 if A ⊇ {3,4} and neither of the above holds
- v(A) = 0 otherwise

Two facts make every check short: the three basic coalitions pairwise intersect (in 4, 3 and 5), and {1,4,5} ∪ {2,3,5} = N. The 4-player values are v(1234)=1 and v(1235)=v(1245)=v(1345)=v(2345)=2.

- **Monotone:** immediate from the definition by containment.
- **Superadditive:** if A and B are disjoint, at most one contains a basic coalition, so at most one has positive value. Monotonicity then gives v(A)+v(B) ≤ v(A∪B).
- **Balanced:** x = (1,0,1,0,1) and y = (0,1,0,1,1) are core points. Both sum to 3. Any coalition containing {1,4,5} gets at least 2 (x: 1+0+1; y: 0+1+1). Any coalition containing {2,3,5} gets at least 2 (x: 0+1+1; y: 1+0+1). Any coalition containing {3,4} gets at least 1 (x: 1+0; y: 0+1). All other proper coalitions have value 0.
- **Substitutes hypothesis:** v(R∪12)+v(R) ≤ v(R∪1)+v(R∪2) holds for all eight R ⊆ {3,4,5}, in fact with equality:

| R | v(R∪12) + v(R) | v(R∪1) + v(R∪2) |
|---|---|---|
| ∅, {3}, {4}, {5} | 0 + 0 | 0 + 0 |
| {3,4} | 1 + 1 | 1 + 1 |
| {3,5} | 2 + 0 | 0 + 2 |
| {4,5} | 2 + 0 | 2 + 0 |
| {3,4,5} | 3 + 1 | 2 + 2 |

- **Ideals:** x₁ ≤ T − v(2345) = 1, attained at x, so H₁ = 1. Symmetrically H₂ = 1, attained at y.
- **Joint failure:** adding the core constraints x(34) ≥ 1, x(145) ≥ 2, x(235) ≥ 2 gives 2T − x₁ − x₂ ≥ 5, so x₁+x₂ ≤ 1 < 2 = H₁+H₂ on the whole core.

## What this shows

- **No same-side strengthening helps.** Q ↦ v(R∪Q) is modular for every R here, so any condition on S alone given fixed R (gross substitutes, M♮-concavity) is also insufficient. A sufficient condition has to constrain how S interacts with N∖S.
- **H equal to the marginal does not help.** Here H_i = v(N) − v(N∖i), and v(N) − v(N∖S) = 2 = H₁+H₂, yet attainment fails.
- **The hypothesis does kill one family of obstructions.** Submodularity gives H(Q) ≤ Σ_{i∈Q}(v(N) − v(N∖i)) ≤ v(N) − v(N∖Q), so no single coalition N∖Q can block.
- **What survives is a "2-cover" obstruction.** The family {R₀, 1∪R₁, 2∪R₂} covers each non-S player twice, with v(R₀)+v(1∪R₁)+v(2∪R₂) > 2T − H₁ − H₂. The two S-coalitions overlap in player 5, so superadditivity does not bound their sum by T.

## Why it does not refute C2 or the flow lemma

The example cannot be realised with these five players as single arcs. Since v(145)=2 with all sub-pairs zero, 1→5→4 must be a path, say 1=(s,u), 5=(u,w), 4=(w,t). Since v(34)=1, 3=(s,w). Then v(235)=2 with all sub-pairs zero would need 2, 3, 5 to form an s–t path, but 3 ends at w, 5 starts at u, and 4 is the only arc into t. This rules out this labelling only; it is not a claim that flow games exclude 2-cover obstructions in general.

## Additional condition (noncircular but limited)

If each H_i for i ∈ S is attained at a minimum-cut (dual) allocation, then the U_min lattice argument in `CUT_LATTICE_SIMPLIFICATION.txt` lines 7–18 gives joint attainment. This is checkable one arc at a time and is not the reduced-game restatement.

It does not cover general capacities. In the (3,1)/(2,1) example in `COORDINATOR_EVIDENCE.txt` lines 9–17, H_{a1} = 1 is strictly between 0 and the capacity 3, so it is not cut-attained, yet joint attainment holds there. I am assuming that example is a complete bipartite network with non-binding middle arcs; the file does not say so.

## Unresolved

- Whether source-arc joint attainment holds for arc-player flow games, including DAGs with path length ≤ 3. The precise open step is to exclude or exhibit, in a flow game, a family of coalitions with weights δ where Σδ_A·1_A = μ·1_N − λ on S and Σδ_A·v(A) > μT − λ·H. The 2-cover family above is the simplest shape.
- I made no attempt beyond the labelling argument above to embed the obstruction in a flow network with more arcs.
