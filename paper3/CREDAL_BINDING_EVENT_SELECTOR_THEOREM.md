# A dimension-free binding-event theorem for universal credal selection

## Statement

Let `P_` be an atom-vacuous coherent lower probability on a finite state
space `Omega`, and let

```text
K={p in Delta(Omega): p(A)>=P_(A) for every A subseteq Omega}.
```

Let `phi` be the unique increasingly maximal distribution in `K`. Call an
event `A` binding if `phi(A)=P_(A)`. Suppose every pair of binding events
`A,B` satisfies the *binding-event supermodularity* inequalities

```text
P_(A)+P_(B) <= P_(A intersection B)+P_(A union B).       (BES)
```

Then `phi` Lorenz-dominates every distribution in `K`. Equivalently, `phi`
simultaneously maximizes every Schur-concave uncertainty functional on `K`.

Conversely, if `K` has no universal Schur-concave maximizer, then there are
crossing binding events `A,B` for which

```text
P_(A)+P_(B)-P_(A intersection B)-P_(A union B)
 =s_phi(A intersection B)+s_phi(A union B)>0,             (BD)
```

where `s_phi(C)=phi(C)-P_(C)`. Thus failure always exposes a positive broken
diamond among constraints binding at the canonical inc-max distribution.

The theorem is dimension-free. Condition (BES) is imposed only on binding
events at one canonical distribution, not on all event pairs.

## Proof

The established exact-game/coherent-lower-probability correspondence regards
`P_` as a normalized exact game and `K` as its core. Atom-vacuity is exactly
singleton normalization. Consequently its ordinary increasingly maximal
credal distribution is the game's Lmin allocation.

For binding `A,B`, core feasibility and (BES) give

```text
P_(A)+P_(B)
 <= P_(A intersection B)+P_(A union B)
 <= phi(A intersection B)+phi(A union B)
  = phi(A)+phi(B)
  = P_(A)+P_(B).
```

Every inequality is equality, so the intersection and union are also binding.
The binding family is therefore closed under uncrossing.

At every strict payoff boundary of `phi`, leximin optimality supplies a strict
cover of the richer states by proper binding events. Choose a representation
of its player-load vector minimizing

```text
sum_A lambda_A |A|(|Omega|-|A|).
```

If two supported events cross, replacing them by their intersection and union
preserves all state loads and bindingness but decreases this energy by

```text
2 delta |A setminus B| |B setminus A|>0.
```

The minimizing support is therefore laminar. The laminar exact-face theorem
partitions the richer suffix into binding events and makes the suffix itself
binding. This holds at every strict payoff boundary, so `phi` is an exact-
partition allocation. The published exact-partition theorem then makes `phi`
Lorenz-dominating.

A distribution Lorenz-dominates `K` if and only if it maximizes the sums of
the `k` smallest coordinates for every `k`. These partial sums are themselves
Schur-concave, and Lorenz dominance implies optimality for every Schur-concave
functional. This proves the universal-uncertainty formulation.

For the converse, absence of a universal maximizer implies that `phi` is not
Lorenz-dominating and hence cannot be exact partition. At a slack richer
suffix, minimize the same cover energy without assuming (BES). The support
cannot be laminar. A crossing supported pair whose derived intersection and
union were both binding could be uncrossed to lower the energy. At least one
derived event is therefore slack, and modularity of `phi` gives (BD).

## Strictly beyond globally 2-monotone models

Global 2-monotonicity imposes (BES) on every pair of events and is established
base-polyhedral territory. The binding-only theorem is strictly broader.

Normalize by `15` the lower envelope of

```text
(0,4,6,5,0), (5,0,2,7,1), (3,0,0,11,1), (2,2,6,0,5).  (POS)
```

Its unique universal selector is

```text
phi=(1/6,1/6,2/9,2/9,2/9).
```

The only nonempty proper binding event is `{3,4,5}`, so (BES) holds. Yet the
lower probability has 30 global supermodularity violations, with maximum
defect `4/15`. Thus this is not merely the known 2-monotone theorem in new
language.

## A sharp broken-diamond failure

Normalize by `20` the lower envelope of

```text
(2,0,12,6,0), (0,0,0,0,20), (0,2,10,4,4).             (NEG)
```

The inc-max and dec-min distributions are

```text
phi=(1/20,1/20,13/40,1/4,13/40),
psi=(1/10,0,3/10,3/10,3/10).
```

Their increasing cumulative sums cross:

```text
phi: 1/20,1/10,7/20,27/40,1,
psi: 0,1/10,2/5,7/10,1.
```

There is no universal selector. The binding pair `{1,3,5}`, `{3,4,5}` has
intersection `{3,5}` and union `{1,3,4,5}`; each derived event has unnormalized
slack one and their local defect is two. This is the canonical obstruction
predicted by (BD).

## Prior art and novelty boundary

- Globally 2-monotone lower probabilities and their base-polyhedral geometry
  are established. Fujishige's lexicographically optimal-base theorem and the
  continuous inc-max/dec-min theorem of Frank and Murota already imply a
  Lorenz selector on that class.
- Abellan and Moral (2003) compute the maximum-Shannon-entropy point of
  probability-interval credal sets. Vu, Destercke, and Pichon (2026) give a
  current strongly polynomial treatment of upper entropy for all 2-monotone
  lower probabilities.
- Majorization as simultaneous comparison by all Schur-concave uncertainty
  functionals is prior art.

The candidate new contribution is the binding-only, dimension-free extension
beyond global 2-monotonicity, together with the necessary broken-diamond
obstruction. It is derived from the manuscript's exact-face uncrossing theorem
and requires hostile specialist review in imprecise probability and submodular
optimization before any major-breakthrough claim.

## Exact audit

The existing exact verifier now reports the normalized positive and negative
credal distributions, independently recomputes inc-max and dec-min, checks the
Lorenz crossing, and audits the binding-event defects:

```bash
python src/verify_lmin_uncrossing_domain.py \
  --output results/lmin_uncrossing_domain.json
```

The verifier is a bug audit. The proof is the binding-event closure and
minimum-energy uncrossing argument above.
