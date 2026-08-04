# A sharp four/five Lorenz threshold for coherent lower probabilities

## Setup

Let `Omega` be finite. A coherent lower probability is a set function
`P_` admitting a nonempty credal set

```text
M(P_) = {p in Delta(Omega): p(A) >= P_(A) for every A subseteq Omega}
```

and satisfying the exact lower-envelope identity

```text
P_(A) = min {p(A): p in M(P_)}.                         (1)
```

Equivalently, after the normalization `P_(Omega)=1`, this is an exact
cooperative game and `M(P_)` is its core. This equivalence is established
prior art; it is not a contribution claimed here.

Write `ell_i=P_({i})` and `R=1-sum_i ell_i`.

## Atom-removal theorem

If `R=0`, then `M(P_)={ell}`. If `R>0`, define

```text
Q_(A) = [P_(A)-sum_(i in A) ell_i]/R.                  (2)
```

Then `Q_` is an atom-vacuous coherent lower probability and

```text
q |--> ell + R q                                      (3)
```

is an affine bijection from `M(Q_)` onto `M(P_)`.

### Proof

Disjoint superadditivity of an exact game gives
`1=P_(Omega)>=sum_i P_({i})`, hence `R>=0`. Every `p in M(P_)` satisfies
`p_i>=ell_i`. When `R=0`, efficiency forces equality in every coordinate.

Suppose `R>0`. For a probability vector `q`, put `p=ell+Rq`. For every
event `A`,

```text
p(A)>=P_(A)  iff  ell(A)+R q(A)>=ell(A)+R Q_(A)
                iff  q(A)>=Q_(A).
```

Also `p(Omega)=1` iff `q(Omega)=1`. Thus (3) maps the two credal sets
bijectionally. Taking minima in the displayed equivalence proves that `Q_`
satisfies (1), while (2) gives `Q_({i})=0`. Disjoint superadditivity gives
`P_(A)>=sum_(i in A)ell_i`, so `Q_` is nonnegative as required.

This also identifies the intrinsic residual or surplus coordinates

```text
q_i=(p_i-ell_i)/R.                                    (4)
```

## Sharp threshold theorem

Every coherent lower probability on at most four states has a unique credal
distribution whose residual vector (4) Lorenz-dominates every other residual
vector. The bound is sharp: on five states this can fail even when every
singleton lower probability is zero.

### Through four states

For `R=0` the claim is immediate. For `R>0`, the atom-removal theorem reduces
the claim to a singleton-normalized exact game on at most four players. The
structural circuit theorem in the manuscript proves that its Lmin allocation
has every cumulative richer suffix tight, hence has the exact-partition
property. The published exact-partition theorem then makes this allocation
the Lorenz-dominating core point. Applying (3) proves the residual statement.

The substantive new input is the human four-player structural theorem. The
exact-game/coherent-lower-probability equivalence and the implication from
exact partition to Lorenz dominance are prior art.

### Five-state sharpness witness

On `Omega={1,2,3,4,5}`, take the lower envelope of the four distributions

```text
g1=(0,0,0,3,3)/6,       g2=(0,0,3,3,0)/6,
g3=(1,1,1,0,3)/6,       g4=(1,1,1,1,2)/6.             (5)
```

That is, set `P_(A)=min_k gk(A)`. Each generator lies in the induced credal
set and one attains every displayed minimum, so (1) holds directly. All
singleton lower probabilities are zero.

The unique increasingly maximal (leximin) point is

```text
phi=(1/6,1/6,1/6,1/6,1/3),                            (6)
```

whereas the unique decreasingly minimal point is

```text
psi=(1/8,1/8,1/4,1/4,1/4).                            (7)
```

These selections have short hand certificates. The envelope values give

```text
p(Omega\{1})>=5/6,       p(Omega\{2})>=5/6,
p({3,5})>=1/2,           p({4,5})>=1/2.                (7a)
```

The first pair says `p1,p2<=1/6`, so no feasible distribution can have
minimum coordinate above `1/6`. The point `phi=g4` attains that minimum.
If every coordinate is at least `1/6`, the first pair pins `p1=p2=1/6`;
efficiency and the second pair then give `p3,p4<=1/6`, pinning (6)
completely. Thus `phi` is uniquely leximin.

The second pair in (7a) implies that every feasible distribution has a
coordinate at least `1/4`. The point

```text
psi=(1/4)g2+(3/4)g4
```

is feasible and has maximum `1/4`. At any feasible point with every
coordinate at most `1/4`, both second-pair inequalities force
`p3=p4=p5=1/4`. The remaining mass `p1+p2=1/4` is decreasingly minimized by
the unique equal split `p1=p2=1/8`, proving (7) without computation.

Their cumulative increasing-order sums are

```text
phi:  1/6, 1/3, 1/2, 2/3, 1,
psi:  1/8, 1/4, 1/2, 3/4, 1.                          (8)
```

Thus their Lorenz curves cross. A Lorenz-dominating point in a compact
fixed-sum set must be its unique increasingly maximal point, hence would have
to equal `phi`; but `phi` does not dominate `psi` by (8). No
Lorenz-dominating credal distribution exists.

The exact verifier reconstructs (5), recomputes (6)--(7), checks exactness,
and audits (8):

```text
src/verify_credal_four_five_threshold.py
results/credal_four_five_threshold.json
```

The verifier is a reproducibility and bug-detection device. The proof of the
threshold is the affine reduction plus the structural four-player theorem.

## Calibrated significance

The candidate cross-field contribution is the sharp state-space threshold:
automatic residual Lorenz dominance through four states, with first failure
at five. It is not a new characterization of coherent lower probabilities,
not a new exact-partition implication, and not yet established as absent from
the imprecise-probability literature. Specialist novelty review is required.

The contrast with supermodular lower probabilities is important. Their
credal sets are base-polyhedral, where increasingly maximal and decreasingly
minimal selections coincide in every dimension. The theorem above concerns
arbitrary coherent lower probabilities: four states force the coincidence
without supermodularity, while five states permit its first failure.

## Primary literature used for positioning

- M. Studený and V. Kratochvíl (2017), *Linear Core-Based Criterion for
  Testing Extreme Exact Games*, PMLR 62:313--324,
  <https://proceedings.mlr.press/v62/studen%C3%BD17a.html>.
- S. Fujishige (1980), *Lexicographically Optimal Base of a Polymatroid with
  Respect to a Weight Vector*, Mathematics of Operations Research 5:186--196,
  <https://doi.org/10.1287/moor.5.2.186>.
- A. Frank and K. Murota (2022), *Decreasing Minimization on
  Base-Polyhedra: Relation Between Discrete and Continuous Cases*,
  <https://arxiv.org/abs/2202.06561>.
- E. Miranda and I. Montes (2023), *Centroids of the Core of Exact
  Capacities: A Comparative Study*, Annals of Operations Research 321:409--449,
  <https://doi.org/10.1007/s10479-022-05097-1>.
