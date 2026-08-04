# Tight deficit completion: a general obstruction invariant

## The theorem

Let `v` be exact, let `phi` be any core allocation, and split the players as
`N=H disjoint-union L`. Give `phi`-tight coalitions nonnegative weights
`lambda_T` whose incidence load is a common value `alpha` on `H` and is
`c_i<=beta<alpha` at each `i in L`.

Define the outside deficit vector

```text
d_i=beta-c_i >= 0.                                    (D)
```

Let nonnegative weights `nu_Q` on coalitions `Q subseteq L` complete this
vector exactly:

```text
sum_Q nu_Q 1_Q = d.
```

Then

```text
(alpha-beta) s_phi(H) <= sum_Q nu_Q s_phi(Q).         (DC)
```

No singleton normalization or egalitarian hypothesis is needed once the
strict tight cover is supplied.

## Proof

The cover and completion satisfy

```text
sum_T lambda_T 1_T + sum_Q nu_Q 1_Q
  - (alpha-beta)1_H = beta 1_N.                       (I)
```

If `beta>0`, divide by `beta`; if `beta=0`, add the grand coalition with any
positive coefficient before rescaling. This is an exact-balanced vector with
`H` as its only negative coalition. The tight `T` terms and the grand
coalition have zero slack, so the exact-balanced slack law applied to `(I)`
is precisely `(DC)`.

## The completion-cost invariant

For `d>=0` on `L`, define the finite covering LP

```text
kappa_phi,L(d) = min sum_Q nu_Q s_phi(Q)
subject to      sum_Q nu_Q 1_Q=d,  nu_Q>=0,
                empty != Q subseteq L.
```

Singleton coalitions make it feasible, and nonnegative slack makes its value
finite and nonnegative. The theorem gives

```text
(alpha-beta)s_phi(H) <= kappa_phi,L(d).               (K)
```

Moreover `kappa_phi,L(d)=0` exactly when `d` lies in the incidence cone of
coalitions contained in `L` that are tight at `phi`. Thus:

> A strict tight cover whose outside deficit can itself be completed by tight
> poorer-side coalitions forces the target `H` tight.

This is a dimension-free domain criterion. A slack boundary is certified by
a strictly positive completion cost, turning obstruction classification into
the study of positive-cost rays of a canonical tight-set covering cone.

There is an equivalent value formulation. Define

```text
omega_v,L(d) = max sum_Q nu_Q v(Q)
subject to     sum_Q nu_Q 1_Q=d, nu_Q>=0.
```

Because `phi` is modular,

```text
kappa_phi,L(d)=d dot phi_L-omega_v,L(d).              (G)
```

Thus the invariant is the gap between the `phi`-price of the deficit vector
and the maximum game worth obtainable from a fractional exact cover of that
vector. In a singleton-normalized game, singleton completion has cost
`d dot phi_L`; coalition completion is never worse and is strictly better
whenever an optimal completion has positive total coalition worth.

## Two obstruction families are equality cases

### Five-player two-column obstruction

Give the two tight protectors unit weight. Their loads are two on the failed
richer pair, one on the two arms, and zero on the exterior singleton. Take
`alpha=2,beta=1`. The deficit is the incidence vector of that exterior
singleton, so `(K)` becomes

```text
s_phi(H) <= s_phi(R).
```

Both slacks equal one. This is the exterior-budget theorem and its sharp
five-player equality case.

### Seven-player three-trace obstruction

Give the three traces weight one half. Their richer load is one; on the two
poorer players their loads are zero and one half. Take
`alpha=1,beta=1/2`. The deficit is one half of the losing poorer singleton.
The target slack and singleton slack are both one, so

```text
(1/2)s_phi(H) = (1/2)s_phi({a}) = 1/2.
```

Thus the support-two and support-three families are not unrelated examples:
they are saturated rays of the same completion-cost inequality.

## Relation to existing results

The earlier boundary-cover inequality completes deficits only with singleton
coalitions and charges their full payoff under normalization. The present
form permits arbitrary poorer-side coalitions and charges their actual core
slacks, so it can be strictly sharper. The two-column exterior bound is the
smallest illustration.

The incidence identity is a semi-balanced system with exceptional coalition
`H` in the terminology of Studený and Kratochvíl (2022), *Facets of the cone
of exact games*. Its exact-game inequality is therefore firmly prior art, as
is the earlier exact-balanced formulation of Lohmann, Borm, and Herings
(2012). The candidate new contribution is only the Lmin-selected restriction
to poorer-side completions, the resulting minimum-cost functional and
zero-cost cone criterion, and the identification of distinct obstruction
families as saturated rays. Focused searches found no such restricted
functional, but specialist review is required before making a novelty claim.

## Reproduction

```bash
PYTHONPATH=src python src/verify_tight_deficit_completion.py \
  --output results/tight_deficit_completion.json
```

The verifier reconstructs both exact games, recomputes Lmin, checks the
incidence completions, and verifies both rational equality cases. It is not a
proof dependency.
