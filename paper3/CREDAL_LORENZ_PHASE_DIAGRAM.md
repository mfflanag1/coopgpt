# The finite-state credal Lorenz phase diagram

## Theorem

The following two universal thresholds are sharp.

1. Every coherent lower probability on at most three states has a unique
   Lorenz-dominating distribution in its induced credal set. Four states can
   fail.
2. If every singleton lower probability is zero, the guarantee extends
   through four states. Five states can fail.

The second threshold is the cooperative-game structural theorem transported
through the established exact-game/coherent-lower-probability correspondence.
The first threshold has a separate base-polyhedral explanation.

## Why three states always work

Let `P_` be a coherent lower probability on `Omega`, with `|Omega|<=3`. Put

```text
ell_i=P_({i}),             u_i=1-P_(Omega\{i}).
```

Every nonempty proper event is either a singleton or the complement of one.
Consequently the entire credal set is the box slice

```text
M(P_)={p: sum_i p_i=1, ell_i<=p_i<=u_i for every i}.   (B)
```

This is a polymatroid base. To see it directly, set `w_i=u_i-ell_i` and
`R=1-sum_i ell_i`, and define

```text
f(A)=ell(A)+min{w(A),R}.                                (F)
```

The truncation of the nonnegative modular function `w(A)` is submodular, so
`f` is submodular. Coherence exactifies every singleton and its complement;
this implies `w_i<=R` and `w(Omega\{i})>=R`. The base inequalities
`p(A)<=f(A)`, together with `p(Omega)=1`, are therefore equivalent to (B):
singleton inequalities give the upper bounds, and complement inequalities
give the lower bounds. Thus (B) is a base polytope.

Equivalently, this point is obtained by water filling:

```text
p_i^*=min{u_i,max{ell_i,lambda}},
```

where `lambda` is chosen so that the coordinates sum to one.

Here is a direct Lorenz proof. If `x` is feasible and differs from `p*`,
efficiency supplies indices `i,j` with `x_i<p_i*` and `x_j>p_j*`. The first
inequality implies `p_i*<=lambda` (otherwise `p_i*=ell_i` and `x_i` would
violate its lower bound); the second implies `p_j*>=lambda` (otherwise
`p_j*=u_j` and `x_j` would violate its upper bound). Hence

```text
x_i < p_i* <= lambda <= p_j* < x_j.
```

Transfer mass from `j` to `i` until one of the two discrepancies is removed.
This stays inside the coordinate box and is a Pigou--Dalton equalizing
transfer. Repetition reaches `p*`, so `p*` Lorenz-dominates `x`. The displayed
water-filling formula uniquely specifies `p*`; equivalently, uniqueness also
follows from strict concavity of Shannon entropy on the convex credal set.
This is the elementary box-slice form of Fujishige's lexicographically
optimal-base theorem.

This proof is structural and contains no finite enumeration. The reason the
argument stops at four states is exact: two-state events are then no longer
singletons or complements of singletons, so genuinely coupled inequalities
can appear.

## Sharp four-state failure

On four states, take the coherent lower envelope of

```text
g1=(23,7,9,9)/48,             g2=(13,13,2,20)/48.       (G4)
```

Both generators are probabilities, belong to the induced credal set, and
eventwise attain the lower envelope. The ordinary increasingly maximal point
and decreasingly minimal point are

```text
phi=(18,8,8,14)/48=(3/8,1/6,1/6,7/24),
psi=(16,10,6,16)/48=(1/3,5/24,1/8,1/3).                (S4)
```

For a direct feasibility check, all nontrivial envelope constraints reduce,
in units of `1/48`, to the following coordinate and pair intervals (triple
constraints are the complementary coordinate upper bounds):

```text
p1 [13,23]   p2 [7,13]   p3 [2,9]    p4 [9,20]
p12 [26,30]  p13 [15,32] p14 [32,33]
p23 [15,16]  p24 [16,33] p34 [18,22].                  (I4)
```

Substitution of `(18,8,8,14)` and `(16,10,6,16)` into (I4) verifies both
points without an optimization oracle.

There are short hand certificates. The two envelope inequalities

```text
p1+p2>=13/24,                 p1+p4>=2/3                (C4)
```

and efficiency imply `p2+p3<=1/3`. Thus the largest possible minimum is
`1/6`; equality pins `p2=p3=1/6`, after which the first inequality in (C4)
gives `p4<=7/24`. The next leximin stage therefore pins `p4=7/24`, and
efficiency gives `p1=3/8`, yielding `phi`.

For decreasing minimization, the second inequality in (C4) makes the smallest
possible maximum at least `1/3`. At equality it pins `p1=p4=1/3`; the first
inequality then pins the next decreasing stage at `p2=5/24`, giving `psi`.
Direct substitution in the event envelope proves both displayed points are
feasible.

Their increasing cumulative sums are

```text
phi: 1/6, 1/3, 5/8, 1,
psi: 1/8, 1/3, 2/3, 1.
```

The curves cross. A Lorenz-dominating point would have to be `phi`, the unique
increasingly maximal point, but `phi` does not dominate `psi`. Thus four is
sharp.

## Why atom-vacuity buys exactly one state

For atom-vacuous coherent lower probabilities, the corresponding exact game
is singleton-normalized. The manuscript's structural circuit theorem proves
that through four players its Lmin point is exact partition and therefore
Lorenz-dominating. The five-state lower envelope documented in
`COHERENT_LOWER_PROBABILITY_THRESHOLD.md` has crossing inc-max and dec-min
points, proving sharpness.

The two rows therefore form a phase diagram:

```text
class                                      guaranteed       first failure
arbitrary coherent lower probabilities    |Omega| <= 3     |Omega| = 4
atom-vacuous coherent lower probabilities |Omega| <= 4     |Omega| = 5
```

## Universal uncertainty interpretation

For a probability vector `p`, let

```text
L_k(p)=sum of the k smallest coordinates of p,   1<=k<|Omega|.
```

Each `L_k` is a nonnegative Schur-concave functional, invariant under state
relabeling and zero at a point mass. These are therefore uncertainty measures
under the monotonicity-under-random-relabeling convention of Friedland,
Gheorghiu, and Gour (2013). More generally, a distribution `p*` Lorenz-
dominates every point of a credal set `K` if and only if it simultaneously
maximizes every Schur-concave functional on `K`. The forward implication is
the definition of Schur concavity. Conversely, simultaneous maximization of
the particular family `L_1,...,L_{n-1}` is exactly the system of Lorenz
inequalities.

Consequently the phase diagram is also a sharp phase diagram for a
*universal maximum-uncertainty representative*:

```text
class                                      universal representative  first failure
arbitrary coherent lower probabilities    |Omega| <= 3              |Omega| = 4
atom-vacuous coherent lower probabilities |Omega| <= 4              |Omega| = 5
```

At the four-state witness, maximizing `L_1=min_i p_i` forces
`p_1>=3/8`, whereas maximizing `L_3=1-max_i p_i` forces
`max_i p_i=1/3`; their maximizing sets are disjoint. At the atom-vacuous
five-state witness, `L_1` is uniquely maximized by `phi`, whose maximum
coordinate is `1/3`, while `L_4` is maximized at value `3/4` by `psi`, whose
maximum coordinate is `1/4`. Thus failure is already witnessed by two
elementary uncertainty indices, not merely by an abstract separating
functional.

This does not say that a maximum-entropy distribution fails to exist. Shannon
entropy is strictly concave, so every nonempty compact convex credal set has a
unique Shannon maximizer. The sharp statement is simultaneous optimality for
*all* Schur-concave uncertainty measures. Majorization as a universal
uncertainty order is prior art; the candidate new contribution is the sharp
credal-set threshold.

## Verification and scope

The four-state arithmetic is replayed exactly by

```text
src/verify_credal_lorenz_phase_diagram.py
results/credal_lorenz_phase_diagram.json
```

The verifier is a bug-detecting audit. The proof is the box-slice
base-polyhedron argument, the two hand certificates, and the existing human
four/five structural theorem.

The exact-game/credal correspondence and Fujishige's base theorem are prior
art. The candidate contribution is the combined sharp `3/4` and `4/5` phase
diagram. It requires hostile specialist novelty review before any claim of a
major field breakthrough.

There is an adjacent established `3/4` transition. De Bock and de Cooman
(2015) prove that the geometry of *extreme coherent lower previsions* changes
sharply between three states and four or more. Quaeghebeur and de Cooman
(2008) study extreme coherent lower probabilities directly. Neither full text
contains `Lorenz`, `lexic`, or `majoriz`, and neither states the selector
threshold here. The parallel transition supports the structural framing but
does not prove novelty.

Primary adjacent sources:

- J. De Bock and G. de Cooman (2015), *Extreme Lower Previsions*, Journal of
  Mathematical Analysis and Applications 421:1042--1080,
  <https://doi.org/10.1016/j.jmaa.2014.07.067>.
- E. Quaeghebeur and G. de Cooman (2008), *Extreme Lower Probabilities*,
  Fuzzy Sets and Systems 159:2163--2175,
  <https://doi.org/10.1016/j.fss.2007.11.020>.
- S. Friedland, V. Gheorghiu, and G. Gour (2013), *Universal Uncertainty
  Relations*, Physical Review Letters 111:230401,
  <https://doi.org/10.1103/PhysRevLett.111.230401>.
- D. Skulj (2022), *Normal Cones Corresponding to Credal Sets of Lower
  Probabilities*, arXiv:2201.10161, <https://arxiv.org/abs/2201.10161>.
- F. Cuzzolin (2022), *The Intersection Probability: Betting with Probability
  Intervals*, arXiv:2201.01729, <https://arxiv.org/abs/2201.01729>. This is a
  distinct proposed representative for interval credal sets, not a universal
  Schur-concave maximizer.
