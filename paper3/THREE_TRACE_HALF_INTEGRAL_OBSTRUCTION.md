# A three-trace half-integral obstruction family

## Result

Let the players be two poorer players `a,b` and a richer block

```text
H = {c} disjoint-union A disjoint-union B,
|A|=u>=2, |B|=w>=2.
```

There is a singleton-normalized exact game with

```text
Lmin = Lmax = (1,1,2,...,2),
v(H)=2|H|-1 < 2|H|=Lmin(H),
```

whose only proper coalitions tight at Lmin are

```text
{c} union A,
{c} union B,
{b} union A union B.
```

Their rich traces have the unique fractional exact cover

```text
(1/2,1/2,1/2).
```

The smallest member has seven players and five rich players.  Its active
trace system has only three columns, so it cannot contain the four-column
four-co-singleton packet under row/column deletion or contraction.  Thus the
four-co-singleton obstruction is unique at four rich players but is not a
universal trace minor of higher-dimensional failures.

All vertices of the defining polytope are half-integral.  Multiplying the
game and displayed allocations by two therefore gives an integral exact game
with the same tight-coalition and trace geometry.

This is a candidate new theorem.  Correctness, terminology, and novelty still
require hostile specialist review.

## Construction

Put `h=1+u+w` and define the compact polytope `P` by

```text
x >= 0,
x(N) = 2+2h,
x({c} union A) >= 2(u+1),
x({c} union B) >= 2(w+1),
x({b} union A union B) >= 2h-1.
```

For every coalition `S`, set

```text
v(S)=min{x(S):x in P}.
```

Every singleton has value zero.  Indeed, the feasible point with
`a=b=c=0`, `x(A)=2u+2`, and `x(B)=2w+2` can zero any prescribed member of
`A` or `B` because both blocks have size at least two.  A second feasible
point is

```text
z_a=0, z_b=3, z_c=3,
z(A)=2u-1, z(B)=2w-1.
```

Thus `v` is singleton-normalized.  The three displayed inequalities and
efficiency show `core(v) subseteq P`; the definition of `v` gives the reverse
inclusion.  Hence `core(v)=P`.  Every coalition minimum is attained on the
compact polytope, so the game is exact directly from the definition.

At a vertex, at most one coordinate in each of the exchangeable blocks `A`
and `B` is positive; otherwise a small transfer between two equal-type
coordinates preserves every defining equation.  After zero coordinates are
removed, the remaining coefficient columns are among the five player types
`a,b,c,A,B`.  Every nonsingular square subdeterminant of their
total-plus-three-coalition incidence matrix has absolute value one or two.
The integer right-hand sides therefore make every vertex half-integral.

## Human Lmin proof

Let

```text
phi=(1,1,2,...,2).
```

It lies in `P` and makes all three defining inequalities tight.  Adding those
inequalities gives

```text
2 x(H)+x_b >= 4h+1.
```

Using `x(N)=2+2h` yields

```text
2x_a+x_b <= 3.
```

Therefore no core point can give every player more than one.  If every player
gets at least one, equality forces `x_a=x_b=1`.  The richer block then has
fixed total `2h`, so its next common level is at most two, attained by `phi`.
Thus `phi=Lmin(v)`.

The point `z` above has `z(H)=2h-1`, while the same inequality implies
`x_a+x_b<=3` and hence `x(H)>=2h-1`.  Therefore

```text
v(H)=2h-1,
```

and the richer suffix has slack exactly one.

## Human Lmax proof

The tight coalition `{c} union A` has `u+1` members and worth `2(u+1)`, so
every core point has a coordinate at least two.  The point `phi` attains this
ceiling.  On the face where every coordinate is at most two, tightness of the
first two defining coalitions forces every member of `H` to equal two.
Efficiency leaves `x_a+x_b=2`; the third constraint forces `x_b>=1`.
Leximax minimization then equalizes the two remaining coordinates at one.
Thus `Lmax(v)=phi`.

## Exact trace classification at `phi`

Because every coordinate of `phi` is positive, the nonnegativity constraints
are inactive there.  If a proper coalition `S` is tight, LP duality gives

```text
1_S = mu 1_N
      + lambda_1 1_({c} union A)
      + lambda_2 1_({c} union B)
      + lambda_3 1_({b} union A union B),
lambda_j>=0.
```

The `a` coordinate makes `mu` either zero or one.  The latter gives only the
grand coalition.  With `mu=0`, comparing the `b,c,A,B` coordinates of the
zero-one vector leaves exactly the three unit choices for `lambda`.  Hence
the displayed coalitions are the only proper tight coalitions.

Their traces are

```text
{c} union A,  {c} union B,  A union B.
```

The cover equations at `c`, at a member of `A`, and at a member of `B` are

```text
beta_1+beta_2=1,
beta_1+beta_3=1,
beta_2+beta_3=1.
```

Thus the unique exact cover is `(1/2,1/2,1/2)`.  Only the third lifted
coalition carries the gaining poor player `b`, so its poor loads are
`r_a=0,r_b=1/2`; at the exact `H`-face point `z`, the balanced-trace transport
inequality is attained at equality.

The saturated exact-balanced identity is

```text
1_({c} union A) + 1_({c} union B)
+ 1_({b} union A union B) + 1_{a} - 1_H = 1_N.
```

The three nontrivial positive coalitions are tight, while singleton `a` and
the negative suffix `H` both have slack one.  Hence the failure is funded by
an external poorer-player sacrifice, but its active trace circuit is distinct
from both the five-player circuit and the co-singleton family.

## Consequence for the research program

The hoped-for theorem that every higher-dimensional two-poorer failure
contains the four-co-singleton packet is false.  The correct next problem is
to classify support-minimal active trace circuits.  At least two infinite classes
now exist:

1. the co-singleton class `J-I`, beginning with four rich players;
2. this three-trace half-integral class, beginning with five rich players.

The second class has a constant three-coalition tight support while both rich
blocks may grow.

## Reproduction

From `coopgames/` run

```bash
python src/verify_three_trace_half_integral_family.py \
  --max-block 4 \
  --output results/three_trace_half_integral_family.json
```

The verifier enumerates the defining polytope's vertices in exact rational
arithmetic, constructs the lower-envelope game, checks exactness and the full
proper-tight-coalition list, verifies the unique half-cover, and independently
replays generic exact staged Lmin and Lmax on the seven-player base case.
