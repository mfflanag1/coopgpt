# A sharp five/six threshold for small-poorer Lmin boundaries

## Status

This note records a newly found structural threshold.  The six-player upper
bound has a short human proof.  The five-player lower bound is currently an
exact-rational computer-assisted theorem using the same definition-level
exactness and Lmin KKT encoding that was externally reviewed for the
four-player classification.  The combined result has not yet received an
external novelty or correctness review.

## Statement

Let `v` be a singleton-normalized exact game, let `phi=Lmin(v)`, and order its
payoff strata from poorest to richest.  At a strict payoff boundary write `L`
for the cumulative poorer side and `H=N\L` for the richer suffix.

The new threshold is:

1. If `|N|<=5` and `|L|<=2`, then `phi(H)=v(H)`.
2. At six players this fails, even for a two-stratum Lmin allocation with
   `|L|=2` and `|H|=4`.

Thus six is the minimum dimension of a slack Lmin richer suffix having only
two poorer players.  The lower bound at five is computer-assisted at present.

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

## The five-player lower bound

`src/verify_n5_small_poorer_suffix.py` checks all ordered payoff-stratum
compositions of five players.  At each strict boundary after one or two
cumulative poorer players, it imposes positive richer-suffix slack.

The encoding contains:

- nonnegative singleton-normalized payoffs and coalition slacks;
- a definition-level exact core-face witness for every proper coalition;
- exact stagewise KKT conditions for the common Lmin level;
- exact individual-pinning KKT conditions for every player in each stratum.

All 16 boundary queries are unsatisfiable in Z3's exact linear-rational
arithmetic.  This extends the already externally reviewed through-four
classification only for the restricted `|L|<=2` boundary property.  It does
not claim that every five-player exact game is exact partition—the existing
five-player counterexample has a failed boundary with three poorer players.

## Reproduction

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

It is not yet a major field breakthrough.  The five-player lower bound still
depends on a finite symbolic classification, and a focused literature review
has not established novelty.  The result becomes materially stronger if the
five-player unsatisfiability can be replaced by a short incidence or
exact-balancedness proof, or if the six-player generator pattern extends to a
classification of all minimal positive boundary-defect obstructions.
