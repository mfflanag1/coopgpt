# Complete classification of three-column trace obstructions

## Prior-art boundary

The bare trace system below is classical minimal-balanced-collection
geometry: the three pair patterns form a blown-up three-cycle and have the
familiar balancing weights `(1/2,1/2,1/2)`. Minimal balanced collections,
unique balancing weights, and minimal exact-balanced collections are prior
art; see Lohmann, Borm, and Herings (2012), *Minimal exact balancedness*, and
Laplace Mermoud, Grabisch, and Sudhölter (2025), *Minimal balanced collections
and their applications to core stability and other topics of game theory*.

The candidate contribution is the combined Lmin statement: underloaded
transport forces the poorer-player labels, exact singleton faces force the
sharp atom bounds `|A|,|B|>=2`, and the converse construction realizes every
admissible atom triple as an exact game with the asserted Lmin/Lmax behavior.
That combined novelty has not yet been externally established.

## Classification theorem

At a slack Lmin boundary with exactly two poorer players, choose an
underloaded lifted extreme packet supplied by balanced-trace transport.  If
its support has exactly three tight coalitions, then, up to permuting the
coalitions and relabeling the rich players, necessarily

```text
H = C disjoint-union A disjoint-union B,
R1 = C union A,
R2 = C union B,
R3 = A union B,
beta = (1/2,1/2,1/2).
```

All three atoms are nonempty.  If `a` is the losing and `b` the gaining poor
player in the exact-face displacement, no supported coalition contains `a`
and exactly one contains `b`; take it to be the coalition over `R3`.
Exactness then forces

```text
|A|>=2, |B|>=2,
```

while `|C|` can be arbitrary positive.  Conversely, every such triple of
atom sizes is realized by the exact family below.  Hence the complete
support-three tier begins with five rich and seven total players.

### Human proof of uniqueness

Let the three positive cover weights be `beta_1,beta_2,beta_3`.  Every rich
player has a nonempty column-membership pattern `I subseteq {1,2,3}` and its
cover equation is

```text
sum_(j in I) beta_j = 1.
```

If a singleton pattern occurs, its weight is one.  Rank two on the remaining
columns requires both residual singleton patterns, making both weights one;
otherwise the residual system is nonextreme.
If the triple pattern occurs, positivity makes every proper subset sum
strictly less than one, so the incidence matrix has rank one.  Therefore a
fractional rank-three vertex can use only pair patterns.  Rank three forces
all three pair patterns, whose equations uniquely give
`beta_1=beta_2=beta_3=1/2`.

For the lifted poor labels, write `r_a,r_b` for packet loads and `s>0` for
the suffix slack.  The packet inequality, together with
`Delta_a+Delta_b=s`, is

```text
s(r_b-1)+Delta_a(r_a-r_b)>=0.
```

Since `r_b<1` and `Delta_a<0`, it forces `r_a<r_b<1`.  Both loads are
half-integers, so `r_a=0` and `r_b=1/2`.
Consequently no column carries `a` and exactly one carries `b`.

Suppose the `b`-column is `R3=A union B`.  If `A={d}`, selecting the lifted
coalitions over `R1` and `R3` gives rich load `1_H+e_d` and poor load `e_b`.
This is a safe rooted tight cover, forbidden by exactness of singleton `d`.
Thus `|A|>=2`; the symmetric selection `R2,R3` gives `|B|>=2`.  This proves
the necessary half of the classification without dimension enumeration.

## Realization theorem

Let the players be two poorer players `a,b` and a richer block

```text
H = C disjoint-union A disjoint-union B,
|C|=t>=1, |A|=u>=2, |B|=w>=2.
```

There is a singleton-normalized exact game with

```text
Lmin = Lmax = (1,1,2,...,2),
v(H)=2|H|-1 < 2|H|=Lmin(H),
```

whose only proper coalitions tight at Lmin are

```text
 C union A,
 C union B,
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

Put `h=t+u+w` and define the compact polytope `P` by

```text
x >= 0,
x(N) = 2+2h,
x(C union A) >= 2(t+u),
x(C union B) >= 2(t+w),
x({b} union A union B) >= 1+2(u+w).
```

For every coalition `S`, set

```text
v(S)=min{x(S):x in P}.
```

Every singleton has value zero.  For `t=1`, the feasible point with
`a=b=x(C)=0`, `x(A)=2u+2`, and `x(B)=2w+2` zeros the sole member of `C`.
For `t>=2`, use `a=b=0`, `x(C)=2t`, `x(A)=2u+1`, and `x(B)=2w+1`.
Because every nonsingleton block has at least two members, its displayed
total can be placed away from any prescribed member.  A second feasible
point is

```text
z_a=0, z_b=3, z(C)=2t+1,
z(A)=2u-1, z(B)=2w-1.
```

Thus `v` is singleton-normalized.  The three displayed inequalities and
the feasible vector `phi=(1,1,2,...,2)` show that their lower bounds are the
corresponding coalition worths.  They and efficiency imply
`core(v) subseteq P`; the definition of `v` gives the reverse
inclusion.  Hence `core(v)=P`.  Every coalition minimum is attained on the
compact polytope, so the game is exact directly from the definition.

At a vertex, at most one coordinate in each of the exchangeable blocks
`C,A,B` is positive; otherwise a small transfer between two equal-type
coordinates preserves every defining equation.  After zero coordinates are
removed, the remaining coefficient columns are among the five player types
`a,b,C,A,B`.  Every nonsingular square subdeterminant of their
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

The tight coalition `C union A` has `t+u` members and worth `2(t+u)`, so
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
      + lambda_1 1_(C union A)
      + lambda_2 1_(C union B)
      + lambda_3 1_({b} union A union B),
lambda_j>=0.
```

The `a` coordinate makes `mu` either zero or one.  The latter gives only the
grand coalition.  With `mu=0`, comparing the `b,C,A,B` coordinates of the
zero-one vector leaves exactly the three unit choices for `lambda`.  Hence
the displayed coalitions are the only proper tight coalitions.

Their traces are

```text
C union A,  C union B,  A union B.
```

The cover equations at a member of `C`, at a member of `A`, and at a member
of `B` are

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
1_(C union A) + 1_(C union B)
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
2. this completely classified three-column half-integral tier, beginning
   with five rich players.

The second class has a constant three-coalition tight support while all three
rich atoms may grow subject to the sharp two adjacent lower bounds.

## Reproduction

From `coopgames/` run

```bash
python src/verify_three_trace_half_integral_family.py \
  --max-central-block 2 \
  --max-block 4 \
  --output results/three_trace_half_integral_family.json
```

The verifier first enumerates all seven nonempty three-column row types and
checks the abstract classification and poor-label conclusion.  It then
enumerates each defining polytope's vertices in exact rational arithmetic,
constructs the lower-envelope game, checks exactness and the full proper-
tight-coalition list, verifies the unique half-cover, and independently
replays generic exact staged Lmin and Lmax on the seven-player base case.
