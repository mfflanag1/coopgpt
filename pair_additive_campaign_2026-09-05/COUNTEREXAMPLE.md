# A nine-player pair-additive counterexample to the one-third guarantee

September 5, 2026. Evidence: conventional proof and solver-free rational verification; independent solver corroboration is recorded separately. Priority is unestablished. This refutes the extension of the player-additive one-third guarantee; it does not refute every positive dimension-independent guarantee.

Name the sectors (a,b,c), (d,e,f), (g,h,i). Set

    A = [[0,0,0], [2,0,1], [0,1,0]],
    B = [[0,0,1], [1,0,0], [0,0,0]],
    C = [[0,1,0], [3,0,0], [2,0,0]],

and give each full triple surplus A_ij+B_ik+C_jk. All pair entries are nonnegative integers at most 3; triple weights range from 0 to 4. Smaller coalitions have no productive teams.

The matching (a,f,i), (b,d,h), (c,e,g) has respective weights 1,3,4 and total 8. The allocation

    x = (1/3,4/3,5/6; 5/6,5/6,1/3; 7/3,5/6,1/3)

is nonnegative, totals 8, and covers every triple. This proves both optimal integral matching value T=8 and nonempty full core. Every core allocation therefore satisfies

    a+f+i=1,  b+d+h=3,  c+e+g=4.                 (1)

Here letters denote the corresponding payoff coordinates. The 27 triple-cover checks are reproduced by verify_rational.py. Team-cover inequalities imply all coalition inequalities by summing over a coalition's disjoint optimal teams.

## Full leximin allocation

The first equation in (1) bounds the minimum payoff by 1/3. Allocation x attains this bound, so the first leximin face fixes a=f=i=1/3.

The triple (b,f,g) has weight 4. Subtract its inequality from the last two equalities in (1) to obtain

    c+d+e+h <= 3+f = 10/3.                      (2)

Thus the next unfixed minimum cannot exceed 5/6. Allocation x attains 5/6 on all four coordinates c,d,e,h. Equality in their sum forces each to equal 5/6; (1) then forces b=4/3 and g=7/3. The second optimal face is a singleton, so x is the full leximin allocation, without ambiguity about subsequent levels.

## Individual maximum and failure

Equation b+d+h=3 and nonnegativity imply H_d<=3. The allocation

    y = (0,0,0; 3,1,1; 3,0,0)

is nonnegative, totals 8, and covers every triple. Therefore H_d=3 and

    x_d/H_d = (5/6)/3 = 5/18 < 1/3.

Consequently c_pair<=5/18. The unknown question is whether c_pair remains strictly positive as sector size increases.

## Opposing full selector

The full lexicographic minimum of descending sorted payoffs is

    z = (0,3/2,1; 1,3/2,1; 3/2,1/2,0).

Indeed, (1) gives f<=1, while b+f+g>=4 gives b+g>=3. The maximum payoff is therefore at least 3/2, achieved by z. At this ceiling, b=g=3/2, f=1 and a=i=0. The weight-3 triple (a,e,g) forces e>=3/2; hence e=3/2 and c=1. The weight-1 triple (a,d,i) forces d>=1, and (1) gives d+h=3/2. Minimizing the next unfixed descending level chooses d=1,h=1/2, uniquely. Feasibility of z is checked against all 27 triples.

The exact normalized distance is ||x-z||_1/8=11/24. This example provides no improvement on the existing lower bound d_pair>=4/3 from the player-additive family. Individual protection and selector disagreement remain separate targets.

## Mechanism and next gate

A low-total matched team fixes the first fairness level. One crossing triple then limits the sum of four later coordinates spread across two other matched teams. The player's ideal payoff can escape that restriction by changing the first team's allocation. This is an explicit finite mechanism; whether it can be repeated with increasing attenuation while preserving nonnegative pair-additivity and the full core is unresolved.

The witness was obtained by a fixed-seed bounded discovery screen followed by four bounded reduction passes. It is not claimed to minimize player count, matrix-entry mass, or the payoff fraction globally. No new paper or field-level breakthrough is claimed.
