# The Lmin-tight-skeleton retraction

## Theorem

Let `v` be a singleton-normalized exact game, let `phi=Lmin(v)`, and let

```text
T_phi = {S: empty != S proper-subset N and v(S)=phi(S)}
```

be the proper coalitions tight at `phi`.  Form the compact polytope

```text
K_phi = {x >= 0:
         x(N)=v(N),
         x(S)>=phi(S) for every S in T_phi}
```

and define the lower-envelope game

```text
R_phi(v)(A) = min{x(A): x in K_phi}.
```

Then:

1. `R_phi(v)` is singleton-normalized and exact, and its core is exactly
   `K_phi`.
2. `R_phi(v)(A)<=v(A)` for every coalition, with equality at `N`, at every
   singleton, and exactly at the proper coalitions in `T_phi` when compared
   with `phi`.
3. `Lmin(R_phi(v))=phi`.  Thus deleting every constraint slack at Lmin does
   not move Lmin after the remaining tight skeleton is exactified.
4. Every Lmin-tight/slack coalition is preserved:

   ```text
   R_phi(v)(A)=phi(A)  iff  v(A)=phi(A).
   ```

   In particular, every cumulative richer suffix has exactly the same
   exact-partition status in `v` and `R_phi(v)`.
5. The operation is idempotent: applying it again gives the same game.
6. If the original data are rational, a common positive scaling makes the
   retracted game integral.

The result is dimension-free and support-independent.  It says that all
Lmin boundary behavior of a normalized exact game can be represented by an
exact game determined solely by the incidence hypergraph and right-hand
sides of the coalitions tight at Lmin.  The characteristic-function values
of all slack coalitions can be discarded.

## Certificate-only converse

The retraction also gives a realization theorem without starting from a
game.  Fix a nonnegative payoff vector `phi`, a family `T` of proper nonempty
coalitions, and form

```text
K(T,phi) = {x>=0: x(N)=phi(N), x(S)>=phi(S) for S in T}.
```

This labeled hypergraph is the Lmin-tight skeleton of a
singleton-normalized exact game if the following finite certificates hold:

1. every coordinate has minimum zero on `K(T,phi)`;
2. at every strict boundary of the payoff partition, nonnegative weights on
   `T` give a common positive load on the richer suffix and strictly smaller
   load on every poorer player;
3. if the tight set must be exactly `T`, every omitted proper coalition `A`
   has `min_K x(A)<phi(A)`.

Indeed, the lower envelope of `K(T,phi)` is then singleton-normalized and
exact, the weighted covers give the progressive gates proving
`Lmin=phi`, and condition 3 prevents additional tight coalitions.  Conversely,
the complete tight family of every singleton-normalized exact game satisfies
all three conditions: exact singleton faces give condition 1, the strict
richer-side cover lemma gives condition 2, and completeness gives condition
3.  Thus realizability of an Lmin tight skeleton is characterized entirely by
linear certificates, with no unspecified characteristic-function values.

## Proof

Exactness and singleton normalization of `v` imply

```text
Core(v) subseteq K_phi.
```

Indeed, every core allocation is efficient and nonnegative, and it satisfies
all tight-coalition inequalities.  Hence, using exactness of `v`,

```text
R_phi(v)(A) <= min{x(A):x in Core(v)} = v(A)
```

for every `A`.  If `A` is in `T_phi`, its defining inequality and the
feasible point `phi` give

```text
R_phi(v)(A)=phi(A)=v(A).
```

For a singleton, the preceding upper bound and nonnegativity give value zero.
Efficiency gives equality at `N`.  Conversely, if a proper `A` is not tight
in `v`, then

```text
R_phi(v)(A) <= v(A) < phi(A),
```

so no new tight coalition is created.

By definition, every point of `K_phi` satisfies all coalition inequalities
of its lower envelope, and therefore lies in `Core(R_phi(v))`.  Conversely,
a core point of the new game is efficient, is nonnegative because every new
singleton value is zero, and satisfies the inequalities
`x(S)>=R_phi(v)(S)=phi(S)` for `S in T_phi`.  It therefore lies in `K_phi`.
Thus the two sets are equal.  Every coalition minimum is attained on the
compact polytope, proving exactness.

It remains to prove that enlarging the core has not moved Lmin.  Write the
payoff strata of `phi` as

```text
B_1,...,B_k, with common levels c_1<...<c_k.
```

For each `j<k`, put `L_j=B_1 union ... union B_j` and
`H_j=N setminus L_j`.  The strict richer-side cover lemma supplies
nonnegative weights on coalitions in `T_phi` whose incidence load is a common
number `alpha_j>0` on every player in `H_j` and is `d_i<alpha_j` on every
`i in L_j`.  Summing the corresponding defining inequalities of `K_phi` and
using efficiency gives the supporting inequality

```text
sum_(i in L_j) (alpha_j-d_i)(x_i-phi_i) <= 0.       (Gate_j)
```

All coefficients are strictly positive.  At the first progressive leximin
stage, `Gate_1` prevents every member of `B_1` from rising weakly above
`c_1` with one strict rise; since `phi` is feasible, the first level is
`c_1` and the whole block `B_1` is pinned.  Inductively, after the earlier
blocks are fixed, `Gate_j` reduces to a strictly positive weighted sum over
`B_j`; it pins that entire block at `c_j`.  Efficiency pins the final block.
Hence `phi` is Lmin of the enlarged core.

The exact equality of tight sets makes the defining skeleton unchanged after
one application, proving idempotence.  For rational input, `K_phi` is a
rational polytope, so all finitely many coalition minima are rational; clear
their denominators.

## Why this is more than another obstruction family

The theorem replaces ad hoc lower-envelope construction by a canonical
retraction valid for every dimension and every payoff partition.  In
particular:

- every counterexample to exact partition at Lmin has an exact representative
  whose core uses only the original Lmin-tight inequalities;
- the representative preserves the complete tight/slack pattern, not merely
  one suffix or one numerical solution;
- all boundary arguments may therefore be carried out on labeled tight
  hypergraphs without loss of generality;
- candidate skeletons can be realized or rejected using only coordinate-zero,
  nested-cover, and omitted-coalition LP certificates;
- the three-column and four-co-singleton constructions become two instances
  of the same support-independent mechanism.

The strict-cover ingredient is a quantitative consequence of the published
property-I/egalitarian-core optimality structure and is not claimed as a new
characterization of Lmin.  Sending a balanced game to the unique exact game
with the same core is also known as the lower envelope or exact cover; this
paper does not claim that construction.  The candidate contribution is the
exact, idempotent
combination preserving Lmin and the entire exact-partition tightness pattern.
Its novelty requires specialist literature review.

## Reproduction

From `coopgames/` run:

```bash
python src/verify_lmin_tight_skeleton_retraction.py \
  --output results/lmin_tight_skeleton_retraction.json
```

The audit reconstructs the skeleton game independently for three unrelated
exact families: the three-stratum five-player family, the four-co-singleton
six-player family, and the three-column seven-player family.  It recomputes
Lmin exactly, checks the full coalitionwise tight/slack pattern, verifies
pointwise domination by the original game, and repeats the retraction to
check idempotence.  The finite audit is not a proof dependency.
