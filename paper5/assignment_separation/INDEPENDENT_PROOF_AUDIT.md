# Independent hostile audit: simpler sharp bound and exactness corollary

## Verdict

Both proposed proofs are valid. The simpler proof strengthens the sharp bound from full leximin versus full leximax-min to **full leximin versus any allocation minimizing the largest core payoff**. It should replace the maximal-displacement proof in the main presentation. The latter can remain a secondary derivation if useful.

Assume positive total matching value T, take any fixed optimal matching, and retain its k positive-weight edges. Every other player's core payoff is zero; matched pair i has fixed total s_i>0. The leximin half-domination lemma used below was established independently by feasible superlevel shifts of the difference-constraint potentials.

## A. Simpler finite correction

Let x be full leximin and z any global minimax core allocation. Put

    q_i = |z_Li-x_Li| = |z_Ri-x_Ri|,
    D = sum_i q_i,
    M = max_a z_a.

For each pair with q_i>0, call the endpoint whose payoff increases from x to z its increasing endpoint a and its other endpoint b. The half-domination inequality z_a<=2x_a gives x_a>=q_i; nonnegativity of z_b gives x_b=z_b+q_i>=q_i. Thus

    s_i>=2q_i,    z_a=x_a+q_i>=2q_i,    q_i<=M/2.

These statements also hold trivially for q_i=0. Consequently D<=kM/2.

There is a coordinate j for which z_j=M and x_j>=M. Otherwise, every coordinate attaining the maximum at z would be strictly smaller at x; on a sufficiently short segment from z toward x, all those coordinates would decrease below M, while coordinates originally below M would remain below M. That contradicts global minimax optimality of z. This argument uses only finiteness, convexity, and minimax optimality, not later lexicographic stages.

Since T>0, M>0. Hence j is not an unmatched or fixed-zero coordinate: it belongs to a positive matched pair p. Within that pair,

    q_p=x_j-M,
    x_other>=q_p,
    s_p=x_j+x_other>=M+2q_p.

Combining this one strengthened pair inequality with s_i>=2q_i for all other pairs yields

    T>=2D+M>=2D(1+1/k).

Finally ||x-z||_1=2D, proving rho<=k/(k+1). The proof works also when x=z; no separate exception is mathematically necessary. For k=1 the displayed bound is valid but not sharp: the core is a one-dimensional interval of splits of the sole positive pair, and both full leximin and every minimax point choose the unique feasible split closest to equality. Thus x=z.

### Checks against likely failure modes

- A maximum witness cannot escape into a zero matched pair or unmatched agent because M>0.
- The excess M is added only once, on pair p; no double counting occurs.
- q_i=0 causes no issue, including if the witness lies on an unchanged pair.
- Nonunique maximum coordinates and nonunique minimax allocations cause no issue.
- Nonunique optimal matchings cause no issue; all reasoning fixes one matching at the start.
- Full leximin remains essential to the half-domination lemma. The strengthened statement does not automatically extend to an arbitrary first-stage maximin allocation.
- The assumption T>0 is essential to the normalized ratio and the M>0 witness argument. The zero game can be treated separately with both allocations zero.

## B. Exact-assignment corollary

Let the game additionally be exact. The entire left side L has coalition value v(L)=0, so exactness supplies a core allocation a with a(L)=0. Because all core coordinates are nonnegative, every left payoff in a is zero. Matched-pair tightness then gives a_Ri=s_i, and all unmatched coordinates remain zero. Exactness applied to the right side supplies the opposite allocation b with b_Li=s_i and b_Ri=0.

By convexity their midpoint h=(a+b)/2 belongs to the core and has

    h_Li=h_Ri=s_i/2,

with unmatched coordinates zero.

For an arbitrary core allocation y, let P be the permutation swapping the two coordinates of every selected matched pair and fixing unmatched coordinates. Pairwise fixed sums imply

    h=(y+Py)/2.

Therefore h is majorized by y: averaging a vector with one permutation is a doubly stochastic averaging operation. Equivalently, replacing each pair by its arithmetic mean is a finite series of pairwise equalizations.

If h!=y, they cannot have identical sorted vectors: strict convexity gives

    ||h||_2^2 < (||y||_2^2+||Py||_2^2)/2 = ||y||_2^2.

Majorization consequently makes the ascending sorted vector of h strictly lexicographically larger than that of y and its descending sorted vector strictly lexicographically smaller. Hence h is simultaneously the unique full leximin and unique full leximax-min allocation. Their divergence is zero.

### Scope refinement

Full game exactness is stronger than required. Exactness only for the two side coalitions is sufficient; still more generally, it is sufficient that the balanced matched-pair allocation h belong to the core. In that case the same permutation-average proof applies to every core allocation.

This is a striking boundary for the previous research program: standard assignment games permit sharp disagreement approaching one, whereas exact assignment games have no disagreement between the two full selections. The extremal complete matrix with one row of weights 2 and remaining rows of weights 1 is therefore necessarily nonexact for k>=2. Its core's right-side sum is k(1-t), left-side sum is 1+kt; the left-side sum cannot reach its coalition value zero.
