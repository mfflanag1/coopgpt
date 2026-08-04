# A sharp five/six threshold for small-poorer Lmin boundaries

## Status

This note records a newly found structural threshold with human proofs on
both sides.  The lower bound now follows from a strict Lmin cover and the
classification of minimal balanced traces on at most three richer players;
the earlier exact-rational 16-query theorem remains only an independent audit.
The new human proof has not yet received external correctness or novelty review.

## Statement

Let `v` be a singleton-normalized exact game, let `phi=Lmin(v)`, and order its
payoff strata from poorest to richest.  At a strict payoff boundary write `L`
for the cumulative poorer side and `H=N\L` for the richer suffix.

The new threshold is:

1. If `|N|<=5` and `|L|<=2`, then `phi(H)=v(H)`.
2. At six players this fails, even for a two-stratum Lmin allocation with
   `|L|=2` and `|H|=4`.

Thus six is the minimum dimension of a slack Lmin richer suffix having only
two poorer players.  More structurally, with exactly two poorer players,
slack is impossible for at most three richer players and possible for every
richer-block size at least four.

The six-player obstruction is the smallest member of a dimension-free
half-plane: for every poorer-block size `m>=2` and richer-block size `h>=4`,
an integral exact game on `m+h` players has a slack tied richest suffix and

```text
Lmin = Lmax = (D repeated m times, 2D repeated h times),
D=(h-2)(h-3).
```

Thus failure of suffix tightness persists throughout `m>=2,h>=4`.  It does
not by itself force Lmin and Lmax to differ.

Combining this family with the through-five lower bound gives an exact
classification on the `m=2` ray: with exactly two poorer players, a slack
tied richest suffix is possible if and only if it has at least four players.

## The six-player exact game

All six vectors below have total ten:

```text
g1 = (0,1,3,3,1,2)
g2 = (1,0,3,2,1,3)
g3 = (1,0,3,3,0,3)
g4 = (1,0,3,3,3,0)
g5 = (4,0,0,0,3,3)
g6 = (1,1,2,2,2,2).
```

Define

```text
v(S) = min_k gk(S).
```

Every generator is a core allocation: it is efficient and dominates the
lower envelope coalition by coalition.  Every coalition attains its worth at
at least one generator.  Hence `v` is exact directly from the definition.
The singleton values are zero.

Put

```text
phi = g6 = (1,1,2,2,2,2).
```

It remains to prove that this core point is Lmin.  The following five worths
are immediate from the generator table:

```text
v(N\{2})       = 9,
v({3,5,6})     = 6,
v({4,5,6})     = 6,
v({1,3,4,5})   = 7,
v({1,3,4,6})   = 7.
```

The point `phi` gives every player at least one.  Conversely, at any core
point with every coordinate at least one, the first displayed constraint and
efficiency force `x2=1`.  Write `y=x-1_N`.  Then `y>=0`, `y2=0`, and
`sum_i y_i=4`.  Put `t=y5+y6`.  The next two constraints give

```text
y3 >= 3-t,    y4 >= 3-t.
```

Adding the last two constraints gives

```text
2(y1+y3+y4)+t >= 6.
```

Since `y1+y3+y4+t=4`, this implies `t<=2`.  Therefore

```text
4 = y1+y3+y4+t >= y1+6-t,
```

so `y1<=t-2<=0`.  Hence `y1=0`, and both players 1 and 2 are pinned at the
first Lmin level one.  The remaining four players have total eight, so their
next common level is at most two; `phi` attains two for all four.  Thus

```text
Lmin(v) = (1,1,2,2,2,2).
```

For the richer suffix `H={3,4,5,6}`, generator `g5` gives

```text
v(H)=6,
phi(H)=8.
```

The richer suffix therefore has slack two despite only two poorer players.

## The human lower bound

At every strict boundary, not only the two-poor case, stagewise Lmin duality
gives a nonnegative cover by coalitions tight at `phi`: every member of the
richer suffix has the same cover load, while every poorer player has strictly
smaller load.  Sum the individual-pinning duals within each poorer payoff
stratum, then combine the stratum covers backwards with successively large
coefficients.  Each earlier cover absorbs the finite unrestricted loads placed
on its stratum by all later stages without destroying deficits already secured
on later poor strata.

Assume the richer suffix `H` is slack.  Exactness gives a core point `z` tight
on `H`.  Its displacement `Delta=z-phi` satisfies

```text
Delta(H)=-s,  Delta_a+Delta_b=s>0.
```

After normalizing the cover's rich load to one and discarding empty rich
traces, summing its tight inequalities at `z` gives

```text
-s + c_a Delta_a + c_b Delta_b >= 0,  c_a,c_b<1.
```

Together with `Delta_a+Delta_b=s`, this rules out two nonnegative poor
displacements.  Their sum is positive, so they have opposite signs; write
`Delta_a<0<Delta_b`.

This is the general balanced-trace transport theorem: project the strict
tight-coalition cover onto its traces on `H`, decompose it into normalized
minimal balanced packets, and lift those packets back to original tight
coalitions.  For at most three rich players, every packet is a set partition
except for the unique three-pair triangle

```text
1/2 * ({c,d}, {c,e}, {d,e}).
```

If a packet loads the poor players by `r_a,r_b`, summing its tight coalition
inequalities at `z` gives

```text
-s + r_a Delta_a + r_b Delta_b >= 0.
```

Partition packets have integer poor loads, so each must load the gaining
player `b` at least once.  This contradicts strict undercoverage when
`|H|<=2`.  For `|H|=3`, some triangle packet must load `b` less than once.
Its half-integral loads force `b` onto exactly one triangle edge and `a` onto
none.  After relabeling, the tight coalitions are

```text
{c,d},  {c,e},  {b,d,e}.
```

Exactness of singleton `d` supplies a core point with `x_d=0`.  The first and
third tight inequalities then give

```text
x_c >= phi_c+phi_d,
x_b+x_e >= phi_b+phi_d+phi_e,
```

which exceeds the grand total by `phi_d-phi_a>0`.  This proves the lower
bound without payoff-stratum enumeration.  The old 16 exact-rational queries
remain a definition-level audit, not proof evidence on which the theorem
depends.

## Reproduction

The first command replays the superseded finite lower-bound audit; the second
checks the fixed sharpness example.  Neither command substitutes for checking
the human balanced-trace proof above.

From `coopgames/` run:

```bash
python src/verify_n5_small_poorer_suffix.py \
  --output results/n5_small_poorer_suffix.json
python src/verify_n6_two_poorer_suffix_counterexample.py \
  --output results/n6_two_poorer_suffix_counterexample.json
```

The second verifier checks the fixed generator certificate, recomputes all 62
exact coalition-face minima with exact LPs, recomputes Lmin with the separate
exact staged implementation, and checks the worths used in the human proof.

Discovery-only falsification scripts are:

```text
src/hunt_small_poorer_boundary.py
src/hunt_structured_two_poorer_boundary.py
```

Their no-hit results are not proof evidence and should not be cited as such.

The dimension-free continuation is reproduced by

```bash
python src/verify_two_poorer_rich_family.py \
  --max-poorer-block 5 --max-rich-block 10 --exact-replay-m2-h4 \
  --output results/two_poorer_rich_family.json
```

Its manuscript proof uses an explicit common-total generator family, a
symbolic Lmin argument, and a two-line Lmax argument.  The finite parameter
grid is only an audit of the universal formulas.

## Significance and limits

This is a structural advance over the four/five exact-partition result: it
identifies a different obstruction geometry and shows sharply that two poorer
players cease to force suffix tightness at six, then continues that obstruction
throughout the half-plane with at least two poorer and at least four richer
players.  The family is integral and human-checkable.

This removes the principal finite-enumeration limitation: the sharp `2|3`
versus `2|4` threshold now has a dimension-structural explanation through
balanced trace packets.  The subsequent universal three-poorer family closes
the former `h=2,3` strips and, together with the unique-richest and internal
families, yields the complete boundary-cardinality phase diagram recorded in
`paper3/COMPLETE_BOUNDARY_SHAPE_CLASSIFICATION.md`.  A focused literature
review has not yet established novelty, and both the transport proof and the
complete classification need hostile external review.
