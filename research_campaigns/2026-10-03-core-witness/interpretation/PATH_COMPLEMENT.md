# Independent first-pass interpretation: path lower bounds and diagonal complements

3 October 2026. Read-only canonical-repository investigation. No optimization, no solver invocation, no held-out CW-05/CW-06 inspection. Exact arithmetic below was evaluated from the retained CW-01 and CW-04 matrices using Python's standard-library Fraction. This note is a conventional proof plus exact arithmetic application, not a literature-novelty claim or a global sharp-bound theorem.

## Parametric statement

Consider any three-sector market in the frozen class with a nonempty original core and an optimal diagonal matching. Let d_j be diagonal team j's worth. At every original core point x,

    x_Aj + x_Bj + x_Cj = d_j.

For sector s and labels a,b, let t(s;a,b) be the full team whose sector-s player has label b and whose other two players have label a. Define

    c_s(a,b) = worth(t(s;a,b)) - d_a.

The full-team cover and diagonal equality at a imply the pointwise comparison

    x_s,b - x_s,a >= c_s(a,b).                         (1)

For any directed path a_0,...,a_k=b in this same-sector comparison graph, let its weight be the sum of its c_s(a_{j-1},a_j). Nonnegativity at a_0 gives

    x_s,b >= path_weight.                            (2)

Let L_s(b) be the maximum of zero and the weights of all such paths ending at b, allowing arbitrary starting labels. All directed cycles have weight at most zero, because summing (1) around a cycle is valid at a core point. Removing a nonpositive cycle can only increase a path's weight; therefore simple paths suffice, and L_s(b) is finite. Equations (1)-(2) imply x_s,b >= L_s(b) simultaneously throughout the original core.

Consequently, for any target sector t and label b,

    H_t,b <= d_b - sum_{s != t} L_s(b).               (3)

Proof: apply the diagonal equality at b to any original core point, subtract the two pointwise lower bounds for the other sectors, then maximize x_t,b over the original core. This does not assume that any two ideals are attained together. An implementation can use a selected finite collection of paths instead of the entire path envelope, and can add any other independently proved pointwise within-sector comparison to the graph.

The distinction is essential: equation (3) subtracts payoffs that are forced in every original core allocation, not the separate maxima H of the other sectors. It makes no assertion that H_Ab+H_Bb+H_Cb <= d_b.

## What is old, and what the diagnostic adds

The full-team-to-difference rewriting, path addition, and diagonal tightness are established ingredients explicitly retained in sharp_subsidy/SECTOR_MINIMUM_CORE.md. Nonnegativity and taking a coordinate maximum are elementary. Equation (3) is their explicit cross-sector consequence, omitted from the current ideal-difference diagnostic. It is a proposed strengthening of that coded relaxation, not a claimed new theorem in the literature.

The entire inequality also admits an ordinary linear-combination/deletion interpretation. It must not be marketed as a new generic duality or deletion-packing mechanism. Its useful content here is a short, semantic explanation and exact separation of named relaxed points: a comparison forces an absolute payoff floor, and another sector's attainable maximum must pay for that floor on the same tight diagonal.

## CW-04: four comparisons eliminate the displayed false obstruction

All quantities in the following calculation are multiplied by 2361. The recorded matching is

    (0,1,3), (1,2,4), (2,0,5), (6,7,0),
    (8,9,1), (10,11,2), (3,3,6).

Its total worth is W=2150, the grand worth is T=2361, and the diagonal caps on the fifteen unmatched players sum to 3100. Every displayed relaxed unmatched h equals its diagonal cap. Thus the displayed relaxed objective is

    (2150 + 3100/3 - 2361)/2361 = 2467/7083 > 1/3.

The following four full teams yield comparison weights:

| Sector path edge | Full team | Team worth | Source diagonal | Difference |
| --- | --- | ---: | ---: | ---: |
| C: 3 -> 6 | (3,3,6) | 171 | 88 | 83 |
| C: 6 -> 0 | (6,6,0) | 186 | 180 | 6 |
| C: 0 -> 5 | (0,0,5) | 182 | 211 | -29 |
| B: 1 -> 9 | (1,9,1) | 217 | 211 | 6 |

Therefore every original core allocation satisfies

    x_C6 >= x_C3 + 83 >= 83,
    x_C0 >= x_C6 + 6 >= 89,
    x_C5 >= x_C0 - 29 >= 60,
    x_B9 >= x_B1 + 6 >= 6.

The diagonal values d_6=180, d_5=211, d_9=211 then imply

    H_B6 <= 97,
    H_A5 <= 151, H_B5 <= 151,
    H_A9 <= 205, H_C9 <= 205.

All five players are unmatched. Their displayed relaxed values are respectively 180,211,211,211,211, so the total reduction from the diagonal caps is

    83 + 60 + 60 + 6 + 6 = 215.

For the fixed market encoded by CW-04_relaxed.json, this proves the true fixed-P bound

    sum_{i unmatched} H_i <= 2885/2361,
    J(M,P) <= (3*2150+2885-3*2361)/(3*2361)
            = 2252/7083 < 1/3.

The gap below one third is 109/7083. This is a bound on that market's named P obstruction; it is not its exact ideal vector, not its exact subsidy, and not a bound on arbitrary pair coefficients on the support.

The very first comparison already separates the relaxed point: it has h_C6=171/2361 and h_C3=88/2361, so the difference condition is satisfied with equality, but h_B6=180/2361 violates the unavoidable complement cap 97/2361. This shows exactly how separate ideal differences lose the pointwise information needed by an attaining witness.

## CW-01: a second exact separator, with a remaining gap

Now multiply all quantities by 51. The full team (7,6,6) has worth 5 and source diagonal d_6=4. It gives x_A7-x_A6 >=1. The full team (9,7,9) has worth 5 and d_9=4. It gives x_B7-x_B9 >=1. Nonnegativity therefore gives x_A7>=1 and x_B7>=1. Since d_7=5,

    H_C7 <= 3/51,

whereas CW-01_relaxed.json has h_C7=4/51. Both recorded h differences themselves hold with equality: h_A7-h_A6=1/51 and h_B7-h_B9=1/51.

Here W=47/51 and the unmatched diagonal caps sum to 73/51. The two path floors lower the C7 diagonal cap from 5/51 to 3/51, giving only

    J(M,P) <= 47/51 + (71/51)/3 - 1 = 59/153 > 1/3.

Thus these path/complement cuts separate CW-01 but the displayed bound alone does not bring that market's named P obstruction below one third. This limits only the two path cuts displayed here. It does not limit all elementary tools: the subset-Q bound below already brings this diagnostic market below one third.

## A second, explicitly old explanation that should not be promoted

For a subset Q of P and the union L of its diagonal labels, diagonal tightness and the disjoint Q-team covers imply

    sum_{players on L not used by Q} x_i <= sum_{j in L} d_j - w(Q).

This is the old integral deletion/coalition-slack argument. For the first three CW-01 teams, L={0,1,2,3,4,10}, the diagonal worth is 26/51 and w(Q)=24/51. Hence every unused coordinate on those labels has ideal at most 2/51. Eight globally unmatched displayed h coordinates equal 4/51 and violate this bound. Their diagonal caps are each4/51, so these eight cuts reduce the cap sum from73/51 to57/51, and including the C7 cut reduces it to55/51. Thus J(M,P)<=43/153<1/3 (or45/153 without the C7 cut). This is a concrete localization of an old ingredient, not a new research mechanism.

## Scope and follow-up boundary

The paired full records contain primal_J=5/18 (CW-01) and 4/17 (CW-04). Their duals were read for context but not used in this derivation, and their accepted status should come from the independent checker rather than this note. The argument above uses the relaxed records' raw matrices, original core axioms, and exact arithmetic only.

These results supply a parametrically valid necessary relation and two named-point separations. They do not establish literature novelty, solve the sharp one-third problem, or by themselves justify a long continuation. A substantive next argument must extract information beyond simply re-expressing the existing deletion bounds or adding bookkeeping cuts. No held-out support was inspected or solved.

## Input hashes

All source paths are under /Users/maxf/projects/economics-research/game-theory/coopgpt/research_campaigns/2026-10-03-core-witness/.

    b9c68977417081ca248e53d625fef2aaea085c9c42cc79d3d94b7103e932e383  FORMULATION.md
    33bca31622f9804ec070e856c51880e3e423405c82eeeccdee4661b84908ffbb  paired/CW-01_full.json
    7a1fe769777049a6b2d8ec528b94b9b243fcc95b93bcf97d15d34e36dbecfc53  paired/CW-01_relaxed.json
    627c6cd6e49f8fbc332b90a0b5ed577bc6a064aec421650fc2b986a272da7c6d  paired/CW-04_full.json
    d7a527856afe8ed3dfe2ab5879db11f4ca7fe3e599b85d084ffa8509ea8c7d03  paired/CW-04_relaxed.json

## Coordinator verification and review dependency

The raw-market core hypotheses are established by the exact relaxation checker: it verifies the nonnegative total-one core vector against all1728 full triples and the value-one diagonal. Fable5.1 independently reviewed the proof and arithmetic but did not execute that check. The coordinator accepted the scope clarification that the two displayed CW01 path cuts alone are insufficient, while the old subset-Q cuts already give43/153. This is a clarification of the elementary-route conclusion, not a new global bound.
