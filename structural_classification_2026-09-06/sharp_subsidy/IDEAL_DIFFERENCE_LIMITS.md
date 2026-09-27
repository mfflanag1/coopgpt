# Ideal differences do not replace coordinate-attaining core witnesses

Date: 2026-09-07. Exact counterexample to an enriched necessary-condition relaxation, together with valid general ideal inequalities. The original sharp constant remains between 1/3 and 2/5. This does not refute the one-third conjecture. Novelty and external review remain unconfirmed.

## General inequalities derived from the full core

Let d_j be the worth of diagonal team j, and define the incident diagonal pair budget

    u_{s,j} = sum of the two diagonal pair values incident to sector s at label j.

At any original core point x, let ell_s be the minimum payoff in sector s. The diagonal opposite-pair inequality from SECTOR_MINIMUM_CORE.md and diagonal tightness give

    0 <= x_{s,j}-ell_s <= u_{s,j}.

Thus, for any labels a,b, the original ideals satisfy

    H_{s,a}-H_{s,b} <= u_{s,a}.                         (1)

To prove this, choose a core point attaining H_{s,a}, use x_{s,b}>=ell_s, and then use H_{s,b}>=x_{s,b}. The analogous pointwise inequality holds throughout the core. If u_{s,j}=0, the corresponding payoff equals the sector minimum at every core point.

There is also a bound induced by a whole P-team, beyond its pair-completion constraints. Write the team as (s at a, t at b, u at c), where (s,t,u) is a permutation of the three sectors, and let its worth be v_e. Its core constraint and the tight diagonal at b imply

    x_{u,c}-x_{u,b} >= v_e-d_b+x_{s,b}-x_{s,a}
                        >= v_e-d_b-u_{s,a}.

Taking a core point attaining H_{u,b} gives the valid ideal inequality

    H_{u,c}-H_{u,b} >= v_e-d_b-u_{s,a}.                 (2)

There are six such inequalities per P-team. These arguments do not assume coordinate maxima are attained simultaneously. They are valid with repeated labels as well.

## The tested relaxation

Attempt to replace the separate coordinate-attaining core witnesses by a vector h subject to:

- nonnegativity, h_{s,j}<=d_j, and h_i<=T-w(P) for players outside P;
- an actual feasible original core point x with h_i>=x_i;
- all within-sector difference inequalities coming from a full-team constraint with two repeated diagonal labels and the associated diagonal equality;
- all global range bounds (1);
- all P-team-induced bounds (2).

Every true ideal vector satisfies these necessary conditions. The first discovery variant omitted (1) and (2); it failed to establish the target. The enriched variant includes both, and also fails. The exact example below retires this replacement as a sufficient route to the sharp inequality. It does not reject using the inequalities alongside the full coordinate-attaining witnesses.

## An eight-label exact counterexample

Use m=8 and

    P = {(1,0,2), (3,4,1), (0,5,6), (6,3,7)}.

The diagonal pair entries, ordered AB,AC,BC, are

| Label | AB | AC | BC |
|---|---:|---:|---:|
| 0 | 2 | 1 | 1 |
| 1 | 1 | 2 | 1 |
| 2 | 1 | 2 | 1 |
| 3 | 2 | 1 | 1 |
| 4 | 2 | 1 | 1 |
| 5 | 2 | 1 | 1 |
| 6 | 1 | 2 | 1 |
| 7 | 1 | 2 | 1 |

The off-diagonal pairs of the four P-teams are respectively

    (AB,AC,BC) = (2,3,2), (3,2,2), (3,2,2), (2,3,2).

All other pair entries are zero. Every diagonal has worth 4 and every P-team worth 7. An exact original-core witness has the following sector vectors:

    A: (3,3,0,3,0,0,3,0),
    B: (1,0,1,1,3,3,0,1),
    C: (0,1,3,0,1,1,1,3).

Full-team coverage and total 32 are verified exactly. The diagonal matching attains 32; hence T=32 and the original core is nonempty. Also w(P)=28, T-w(P)=4, and there are 12 players outside P.

Set the hypothetical vector h_i=4 for every player. It dominates even the true ideals, not just the displayed core witness. It satisfies all the listed necessary conditions, including every repeated-label completion comparison, all 192 instances of (1), and all 24 instances of (2). In particular each P-used player has incident diagonal budget 3, so the right side of (2) is 7-4-3=0. The exact verifier checks all supported repeated-label team comparisons, rather than sampling them.

Nevertheless this vector gives

    w(P) + (1/3) sum_{i outside P} h_i - T
       = 28 + 48/3 - 32 = 12 = (3/8)T > T/3.

This is a false obstruction: h is not the original ideal vector.

## The actual market has zero subsidy

The true original ideals are 4 on all 12 players used by P and 1 on all 12 players outside P. For each coordinate, the retained data contain a core point attaining that value and a dual proving its upper bound. The independent checker reconstructs every original full-team inequality and checks both directions exactly.

The following protected allocation is in the original core. Divide each displayed integer by 3:

    A: (7,7,1,7,1,1,7,1),
    B: (4,1,1,4,10,10,1,1),
    C: (1,4,10,1,1,1,4,10).

Its total is 32, it covers every original coalition, and it pays each player at least one-third of that player's true original ideal. Consequently s_3=0. Summing the diagonal team constraints proves that no total below 32 is feasible. The actual P obstruction is 28+12/3-32=0.

The problem with the relaxation is thus the loss of individual attainability under cross-sector constraints. Pairwise ideal-difference comparisons can all hold for a vector whose unmatched coordinates cannot reach those values anywhere in the original core.

## Verification and next action

Run `python3 -O verify_ideal_difference.py`. It verifies the entire original ideal vector using rational primal and dual witnesses, checks the protected allocation and a matching subsidy dual, and then checks the hypothetical vector against every stated necessary condition. It rejects a damaged ideal claim. Accepted data are in IDEAL_DIFFERENCE_COUNTEREXAMPLE.json; no solver is imported by the verifier.

The two discovery variants and their raw outputs are archived in discovery/ideal_difference_archive.zip. Larger floating relaxation values are not claimed as actual subsidies or accepted sharp bounds.

Retain constraints (1) and (2) as valid tools, but keep the original coordinate-attaining core witnesses or an equivalent exact elimination in the next unicyclic argument. The next load-bearing task is a boundary inequality that preserves the cross-sector P-team coupling. Repeating either tested difference-only replacement is not a route to completion of the active goal.
