# Defect-to-uncertainty stability for coherent lower probabilities

## The geometric theorem

Let `K` be a nonempty compact set of probability distributions on `n` states
and let `phi` belong to `K`. Order the distinct coordinate strata of `phi`
from richest to poorest. For every strict stratum boundary, let `H_j` be the
cumulative richer suffix and put

```text
s_j = phi(H_j) - min{p(H_j):p in K},
epsilon = max_j s_j,
```

with `epsilon=0` when `phi` has only one stratum. If

```text
L_k(p) = sum of the k smallest coordinates of p,
```

then every `p in K` satisfies

```text
L_k(p) <= L_k(phi) + epsilon       for k=1,...,n-1.       (LR)
```

Equivalently, `phi` is an additive-`epsilon` simultaneous maximizer of every
Lorenz coordinate on `K`.

Moreover, for every `p in K` there is a probability distribution `q` such
that `phi` Lorenz-dominates `q` and

```text
||p-q||_1 <= 2 epsilon.                                  (AM)
```

Consequently, if `F` is Schur-concave and `M`-Lipschitz in `l1` on the
probability simplex, then

```text
F(p) <= F(phi) + 2 M epsilon,                            (UR)
```

simultaneously for every `p in K` and every such `F`.

## Proof

Write `U_p(r)` for the sum of the `r` largest coordinates of `p`, with
`U_p(0)=0`. At a richer-stratum boundary of size `r_j`,

```text
U_p(r_j) >= p(H_j)
           >= min_{x in K} x(H_j)
            = U_phi(r_j)-s_j.
```

Adjoin the endpoints `r=0,n` with zero slack.
The integer graph of `U_p` is concave because its successive increments are
the decreasingly ordered coordinates of `p`. Between consecutive stratum
boundaries, the graph of `U_phi` is affine because all intervening
coordinates of `phi` are equal. Concavity therefore interpolates the
boundary inequalities and gives

```text
U_p(r) >= U_phi(r)-epsilon       for every r.
```

Since `L_k(p)=1-U_p(n-k)`, this is exactly `(LR)`.

Put

```text
eta(p)=max_r [U_phi(r)-U_p(r)]_+ <= epsilon.
```

The established `l1` approximate-majorization formula says that the least
`l1` distance from `p` to a distribution conventionally majorizing `phi` is
`2 eta(p)`. Equivalently, there is `q` within `2 eta(p)` that is
Lorenz-dominated by `phi`. This is `(AM)`. It can also be seen directly by
moving `eta(p)` mass from the lower tail of the increasing rearrangement of
`p` to its largest coordinate. The amount removed from the first `k`
coordinates is `min{eta(p),L_k(p)}`, which is at least every positive deficit
`L_k(p)-L_k(phi)`.

Schur-concavity gives `F(q)<=F(phi)`, and Lipschitz continuity gives

```text
F(p) <= F(q)+M||p-q||_1 <= F(phi)+2M epsilon.
```

This proves `(UR)`.

## Credal and uncrossing corollary

Let `P_` be an atom-vacuous coherent lower probability, let `K` be its
credal set, and let `phi` be its increasingly maximal distribution. Then

```text
s_j = phi(H_j)-P_(H_j).
```

At each strict boundary, the Lmin optimality certificate supplies a rational
strict cover by binding events. Scale it to an integer multiset and uncross
it to laminar support. If the uncrossing steps use multiplicities `delta_t`,
the final partition multiplicity is `m_j`, and

```text
D_phi(A,B)=P_(A)+P_(B)-P_(A intersection B)-P_(A union B),
```

the exact uncrossing-defect budget gives

```text
s_j <= (1/m_j) sum_t delta_t D_phi(A_t,B_t).              (DB)
```

Thus the maximum right side of `(DB)` over the payoff boundaries can replace
`epsilon` in `(LR)`, `(AM)`, and `(UR)`. Zero cumulative defect recovers the
exact universal-selector theorem. Small cumulative defect gives a robust,
dimension-free approximate selector.

## Sharpness and an essential limitation

For the five-state sharp obstruction, the normalized inc-max and dec-min are

```text
phi=(1/20,1/20,13/40,1/4,13/40),
psi=(1/10,0,3/10,3/10,3/10).
```

The maximum richer-suffix slack is `epsilon=1/20`. At `k=3`,

```text
L_3(psi)-L_3(phi)=2/5-7/20=1/20,
```

so `(LR)` is sharp. The closest steepening of `psi` that is
Lorenz-dominated by `phi` is at `l1` distance `1/10=2 epsilon`, so `(AM)` is
also sharp.

The defect bound must use a boundary cover and an uncrossing path, not the
largest raw defect among all binding pairs. The atom-vacuous lower envelope
of

```text
(1/10,1/10,2/5,2/5,0),
(3/10,3/10,0,0,2/5),
(0,2/5,1/5,1/5,1/5),
(2/5,0,1/5,1/5,1/5)
```

has the uniform universal selector, hence `epsilon=0`, but the binding pair
`{1,2,3},{1,2,4}` has positive defect `2/5`. This diamond is inert because
there is no strict payoff boundary for it to finance.

## Prior art and novelty boundary

Approximate majorization in `l1`, including steepest/flattest distributions
and the exact distance formula, is established by Horodecki, Oppenheim, and
Sparaciari (2018). Majorization as simultaneous comparison of Schur-concave
uncertainty measures is also established prior art.

The candidate contribution is the bridge from canonical richer-suffix face
slacks to approximate majorization, followed by the bridge from local
binding-event uncrossing defects to those slacks. It turns the exact-partition
selector theorem into a sharp quantitative stability theorem. This needs
hostile review by specialists in approximate majorization, imprecise
probability, and cooperative games.

## Exact audit

```bash
python src/verify_credal_defect_stability.py \
  --output results/credal_defect_stability.json
```

The audit recomputes both lexicographic selectors, the suffix slacks, the
sharp Lorenz regret and `l1` radius, and the inert positive-defect example.
It also checks the interpolation and steepening inequalities on 51,989
ordered pairs of rational probability vectors through five states. It is not
a proof dependency.
