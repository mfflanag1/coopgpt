# An actual market whose every optimal subsidy obstruction contains cycles

Date: 2026-09-07. Exact finite theorem. This is a statement about the unrestricted original-core subsidy LP on a specified market, not failure of a sufficient certificate template. The global bounds remain 1/3 <= S_3 <= 2/5. Novelty and external review remain unconfirmed.

## Theorem

There is an admissible m=11 three-sector nonnegative pair-additive market with T=1 and nonempty entire original core, whose optimal grand matching is uniquely the diagonal matching, and whose exact frozen-ideal subsidy is 76/303. In every optimal team-form subsidy dual, six specified disjoint teams have multiplier exactly 1. Their incidence graph relative to the unique diagonal matching is connected and has cycle rank 2.

Consequently there is no optimal subsidy dual supported on an incidence forest for this market. This remains true when fractional team multipliers are allowed and when one is free to choose an optimal grand matching. It does not exclude a theorem that changes the original market, increases its obstruction, and controls the resulting change in original ideals.

The team-form dual uses nonnegative multipliers lambda_t for original full-team constraints and mu_i for the frozen floors, with sum_{t containing i} lambda_t + mu_i <= 1. Arbitrary coalition duals can be expanded into team constraints, but graph-support claims here refer specifically to this team-form representation.

## Explicit pair matrices

Use labels 0,...,10. Every number in the following tables is divided by 5252. The first table lists the three diagonal entries, ordered AB, AC, BC.

| Label | AB | AC | BC |
|---|---:|---:|---:|
| 0 | 108 | 234 | 144 |
| 1 | 252 | 144 | 90 |
| 2 | 144 | 198 | 198 |
| 3 | 90 | 108 | 108 |
| 4 | 154 | 144 | 148 |
| 5 | 108 | 234 | 144 |
| 6 | 153 | 153 | 144 |
| 7 | 189 | 144 | 153 |
| 8 | 144 | 144 | 198 |
| 9 | 198 | 144 | 198 |
| 10 | 198 | 144 | 198 |

The only other positive entries are the three pairs of each displayed P-team:

| Team (A,B,C labels) | AB | AC | BC |
|---|---:|---:|---:|
| (1,0,2) | 252 | 288 | 252 |
| (3,4,1) | 158 | 144 | 234 |
| (0,5,3) | 252 | 198 | 108 |
| (6,3,7) | 153 | 297 | 153 |
| (8,9,5) | 288 | 234 | 306 |
| (7,10,8) | 333 | 198 | 342 |

All other entries are zero. The exact original ideals, 33 coordinate-attaining core witnesses and their upper duals, and a protected allocation with matching subsidy dual are retained under CYCLIC_FRONTIER_6_2_0 in CYCLIC_FRONTIER_CERTIFICATES.json. The independent full-market checker proves T=1, nonempty core, all ideal equalities, and s_3=76/303. CYCLIC_FRONTIER.md gives the certificate equations.

## Unique optimal grand matching

Average the 33 retained original-core witnesses to obtain an original core point x. Every coordinate of x is strictly positive. Of all full teams, the only ones tight at x are the 11 diagonals and (1,0,2), (7,10,8). This equality set is checked with exact rational arithmetic over every potentially nonzero team. Zero-worth teams cannot be tight because x is strictly positive.

Any grand matching attaining T=1 must cover every player and use only x-tight teams. Indeed the difference between x(N) and its matching worth is the sum of its team slacks and the payoffs of unmatched players; all terms are nonnegative. Strict positivity excludes unmatched players.

For every diagonal label j there is a sector player at j that belongs to no other x-tight team. One list of such sectors, for j=0,...,10, is

    A, B, A, A, A, A, A, B, A, A, A.

Each of those players must therefore be covered by its diagonal team. All 11 diagonals are forced, proving uniqueness. The same argument also rules out an alternative fractional perfect optimum.

## Every optimal subsidy dual contains all six P-teams

Let y be the retained optimal protected allocation. It has strictly positive coordinates and exactly 12 tight full-team constraints. For any feasible team-form dual (lambda,mu), the primal-dual difference decomposes as

    sum_i y_i - [sum_t lambda_t w_t + sum_i mu_i H_i/3]
      = sum_t lambda_t [sum_{i in t} y_i - w_t]
        + sum_i mu_i [y_i - H_i/3]
        + sum_i y_i [1 - sum_{t containing i} lambda_t - mu_i].

Every summand is nonnegative. For any optimal dual, equality therefore forces: lambda_t=0 on non-tight teams; mu_i=0 wherever y_i>H_i/3; and every player capacity to be tight because y_i>0.

Apply these necessary conditions in the following order. Each indicated player has a strict floor slack and, among tight teams not already excluded by earlier steps, occurs in exactly the listed team.

| Strict-floor player | Uniquely available team |
|---|---|
| A_0 | (0,5,3) |
| A_1 | (1,0,2) |
| B_9 | (8,9,5) |
| B_10 | (7,10,8) |
| C_1 | (3,4,1) |
| C_7 | (6,3,7) |

At each step mu_i=0 and capacity equality imply that team's multiplier is 1. Every other team sharing any of its players then has multiplier zero by capacity feasibility. This excludes the intersecting tight teams before the next step. The exact verifier checks each singleton choice and strict inequality; it does not assume the conclusion from the stored dual.

Thus all six P-teams have multiplier 1 in every optimal dual, not merely in the exhibited one. Their connected label-team incidence graph has 18 edges and 17 vertices, hence cycle rank 18-17+1=2. Every optimal team-form dual contains this cyclic subgraph. Additional positive teams cannot eliminate its cycles.

## Implication for the sharp-bound campaign

A forest-supported optimum is not available without loss even in an 11-label market with a nonempty original core and a unique grand matching. The broken-ring theorem shows that deleting a pair can also enlarge claims substantially. Together these results reject two simple ways of avoiding cycles: restricting optimal dual support to a forest in the same market, and charging a market-changing cycle opening only to the removed value.

The sharp one-third inequality still might follow from a direct cyclic argument or a more careful transformation. The present subsidy, 76/303, is below one-third and does not improve the global lower bound.

## Verification

Run `python3 -O verify_cyclic_necessity.py`. It first verifies the full original ideals and primal-dual subsidy certificate, then checks strict positivity, the exact tight-team set for the average core witness, the unique-diagonal forcing players, and all six optimal-dual forcing steps. A union-find calculation confirms cycle rank 2. A false forcing step is rejected. The default full build includes this check.

The proof uses standard LP complementary slackness. No novelty is claimed for that ingredient or for graph cycle counting. The proposed contribution requiring priority review is the explicit market-level necessity result with these frozen-ideal and strict-team hypotheses.
