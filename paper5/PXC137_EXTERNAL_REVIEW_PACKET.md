# External review packet — PXC137 product midpoint / forced diagonal

Date: 2026-08-24

Status: internal proof and exact primary/standalone audits complete; no cooperative-game specialist review yet.

## Claim being reviewed

Let `x,z` be any two efficient core allocations of an exact
singleton-normalized TU game with total `T`. PXC136 defines a stationary
singleton-witness flow by

```text
row(F)=col(F)=pi,  F>=0,  F_rr=0,
T F_r(S)>=pi_r v(S).
```

PXC137 drops only the zero-diagonal equations and proves that the relaxed
bridge equals overlap exactly. The explicit feasible point is

```text
pi_r=(x_r+z_r)/(2T),
F_ri=(x_r z_i+z_r x_i)/(2T^2),
y=T*pi=(x+z)/2.
```

For every root and coalition,

```text
T F_r(S)-pi_r v(S)
 = [x_r(z(S)-v(S))+z_r(x(S)-v(S))]/(2T) >= 0.
```

Since `y` is in the coordinate box between `x,z`, its bridge objective is
exactly `O=sum_i min(x_i,z_i)`. The only violated original equation is
`F_rr=0`, because the product has diagonal `x_r z_r/T^2`.

The fixed-midpoint zero-diagonal repair is therefore exactly the matrix
system `(PXC137c)`. Common-tight rows have zero available slack, linking the
repair to the frozen PXC112 common tangent and PXC114 common/reciprocal
obstruction mechanisms.

For a feasible PXC136 dual put

```text
L_r(i)=sum_(S contains i) lambda_rS,
Delta_r=T L_r(r)-A_r-B_r.
```

The diagonal-relaxed dual adds precisely `Delta_r<=0`. Product weighting of
the root and off-diagonal arc inequalities gives

```text
D >= T+O-sum_r (x_r z_r/T^2)[Delta_r]_+ .       (PXC137d)
```

PXC138, added after this packet was first drafted, proves that the weighted
defect of one optimal zero-diagonal dual is not the total stationary price.
On the sharp control its minimum is `9/17`, whereas the true loss is `1/51`,
a factor of 27.  That control has `B_star=c_nT`, so it does not refute a
theorem under the strict hypothesis `B_star<c_nT`; it makes strict spectral
failure load-bearing.  The exact open formulation bounds the integral of
the decreasing diagonal shadow-price curve by `O-c_nT`.  Neither PXC137 nor
PXC138 proves that final bound.

## Exact reproduction

From the repository root:

```bash
python3 verifiers/divergence/verify_pxc137_product_diagonal_obstruction.py \
  --output /tmp/pxc137.json
cmp verifiers/divergence/pxc137_product_diagonal_obstruction.json \
  /tmp/pxc137.json

python3 \
  verifiers/divergence/verify_pxc137_product_diagonal_obstruction_independent.py \
  --output /tmp/pxc137-independent.json
cmp verifiers/divergence/pxc137_product_diagonal_obstruction_independent.json \
  /tmp/pxc137-independent.json
```

The primary audit checks all 373 distinct archived six-player selector
triples and the named PXC101/PXC104/PXC118/PXC125/PXC90 controls. The
standalone audit imports no project game, selector, LP, or PXC136/PXC137
implementation; it checks independently generated exact lower envelopes in
dimensions 3 through 10 using `Fraction` arithmetic.

## Dated prior-art check

Search date: 2026-08-24.

The ingredients are individually standard. Exact games are represented by
core minima/tightness structures in the exact-game and coherent-lower-
probability literature; see the [linear extremity criterion for exact games](https://doi.org/10.1016/j.ijar.2018.06.007)
and the [survey of centroids of exact capacities](https://doi.org/10.1007/s10479-022-05097-1).
Matrices with prescribed margins and prescribed zero entries are classical
transportation polytopes; see Barvinok's [survey](https://arxiv.org/abs/1010.5706).
Zero-diagonal symmetric contingency tables are also standard objects; see
McKay--McLeod's [enumeration paper](https://arxiv.org/abs/1108.4496).

I did not locate a source coupling two selected core allocations by the
specific symmetric product occupation measure, identifying exact
root-labelled coalition slack as above, or interpreting the leximin/leximax
overlap loss as the price of imposing singleton-witness zero diagonals. This
is only a negative search result, not a novelty determination. The outer-
product coupling itself is elementary and should not be presented as novel;
only its exact-game selector use could be.

## Hostile questions

1. Is the product row-slack identity correctly normalized by `2T`?
2. Does dropping `F_rr=0` introduce any other primal or dual freedom omitted
   from the statement?
3. Does the repair system `(PXC137c)` give an actual iff for retaining the
   fixed midpoint, including nonnegativity and every proper coalition row?
4. Are the signs in the missing diagonal dual inequality and `(PXC137d)`
   correct?
5. Is calling the stationary loss a “forced-diagonal price” mathematically
   informative, or is there a standard Markov occupation-measure theorem
   that makes this terminology misleading?
6. Can the PXC114 common-direction blocker or reciprocal cross-cover facets
   bound the integrated diagonal shadow-price curve without using overlap
   as an unexplained charge?
7. Is the product occupation construction already known in exact-game,
   balancedness, Markov-chain, or transportation-polytope literature under a
   standard name?

Please distinguish correctness, significance, and novelty. Do not treat the
finite verifier outputs as proofs of the all-dimensional statements.
