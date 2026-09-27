# Sharp local affine refinement and exact aggregate barrier

2026-09-20. Conventional local theorem with rational certificates. Global sharpness and novelty unestablished.

For a three-label nonnegative pair-additive market with an optimal diagonal
matching, nonempty original core, T=d0+d1+d2, and P=(1,2,0),

    J <= T/18 + (13/18)d0.

This improves the earlier coefficient17/18. It changes no original-core ideal.
The coefficient13/18 is optimal when the intercept1/18 is fixed, even on the
sparse diagonal/P support. Sector and label permutations permit any designated
label to take the role0.

Proof: the following deletion rows have integer multiplicities divided by18.
Each excludes its named player and loads every other player at most1/3.

| Excluded | Teams and multiplicities /18 |
| --- | --- |
| A0 | 6(111), 6(222) |
| A2 | 1(000), 2(011), 1(022), 1(111), 5(120) |
| B0 | 6(111), 6(222) |
| B1 | 3(000), 1(101), 3(120), 1(121), 1(122), 2(202), 1(222) |
| C1 | 2(110), 4(120), 2(222) |
| C2 | 2(111), 4(120), 2(220) |

Aggregate pair coverage dominates P once, diagonal labels1,2 by17/18,
and diagonal label0 by2/9. Evaluate each row at its separate original
core maximizer. Summing gives

    2T - sum_U H_i/3 >= W + (17/18)T - (13/18)d0,

which proves the theorem. All other pair entries are nonnegative, so the bound
also holds with additional pairs. No LP solver status is needed to check this
coefficient proof.

Sharpness certificate: T=1, (d0,d1,d2)=(1/8,7/16,7/16).
The certificate supplies all nonzero pair weights and six nonnegative core
witnesses, each of total1. All162 full-team inequalities are checked exactly.
A total-one nonnegative team cover proves the diagonal matching optimal;
the verifier additionally enumerates all36 perfect matchings. They give J>=7/48. The proved bound gives J<=7/48, so equality holds. Any
inequality J<=T/18+b d0 valid on this class must have b>=13/18.
The failed target b=17/27 is exceeded by 5/432 in J-b d0 relative to1/18.

## What this does and does not fix globally

Replace the old affine lemma throughout Section5 of CORE_COMPATIBILITY_UPPER.md.
On the idealized scalar face p=z=tau=0 the three bounds become

    F0 = 2/3 - 5q/3 + v,
    F1 = 1/18 + 14q/9 - 8v/9,
    F2 = 1/18 + 41q/18 - 7v/3.

The exact point q=11/41, v=11/82, R=29/82 attains all three bounds.
Conversely the nonnegative combination of F0,F1,F2 with weights
260/533,261/533,12/533 cancels q,v and gives29/82. Thus the scalar
relaxation optimum is exactly29/82, greater than1/3 by5/246.
For the old coefficient the corresponding exact optimum was37/94.
The point satisfies 0<=v<=q, q<=1, as well as the unreduced mass constraints:
B3=v, M3=3v, Bn=3q/2, W3=v, W=1-q+v, and Bn+B3=2q.
This is an obstruction to those aggregate inequalities, NOT an actual market
counterexample, and NOT a bound showing that every cloning method must fail.

More generally for a local bound J<=aT+b d0 the same face has
F1=a+2(a+b)q-(3a+b)v and F2=a+(2a+3b)q-3(a+b)v.
Their intersection has v=q/2; to reach R=1/3 at q=2/7 would require
24a+9b<=7. With a=1/18 this requires b<=17/27, contradicted by the
sharp local witness b>=13/18. Therefore optimizing this local coefficient
alone cannot yield the sharp global conjecture through these aggregate bounds.
Positive actual witness slack z adds a further obstacle, not a remedy.

This completes the two-formulation bounded attempt: test17/27, then certify
the forced value13/18. Stop this fixed-intercept coefficient route. Other intercepts, non-affine
envelopes, additional joint constraints coupling original witness payoffs across
components, or a different decomposition remain possible; success is unresolved. The global bound remains
39999/100000. No decimal optimization or new graph-family search is claimed.
