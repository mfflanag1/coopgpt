# The structural four/five threshold: sacrifice budgets at Lmin

## Result

The sharp four/five boundary now has a conceptual human explanation rather
than merely a finite classification.

For a singleton-normalized exact game, suppose Lmin has a unique richest
player `r`, payoff `gamma`, and poorer set `L`.  Egalitarian transfer blocking
supplies, for every poorer player `i`, a tight protector

```text
T_i = {r} union Q_i,
empty != Q_i subseteq L\{i}.
```

Exactness converts any fractional packing of these protectors into the
dimension-free inequality

```text
gamma (Lambda-1) <= sum_j (1-c_j) phi_j.              (FP)
```

The left side is the slack demand of the richest singleton.  The right side
is the payoff budget of poorer players left uncovered by the protector
packing.  This is the sacrifice budget.

## Why four is impossible

There are at most three poorer players.

- With one poorer player, no protector exists.
- With two, the two protectors form a reciprocal singleton pair.  Giving each
  weight one covers both poorer players, so `(FP)` forces `gamma<=0`.
- With three, if some `Q_i={j}`, give weight one to protectors `i` and `j`.
  Their poorer parts are disjoint and leave at most one player `u` uncovered,
  so `(FP)` forces `gamma<=phi_u<gamma`.
- If none of the three poorer parts is a singleton, each is the complementary
  pair `L\{i}`.  Giving every protector weight `1/2` covers all poorer players
  and forces `gamma/2<=0`.

Thus a normalized exact game with at most four players cannot have a
unique-richest Lmin obstruction.

This is one load-bearing branch of the full human proof that every Lmin richer
suffix is tight through four players.  The remaining branches—singleton
poorer side and the `2|2` boundary—are handled by exact witnesses and the
all-cross-pairs Lmin-improving segment in the manuscript.

## Why five succeeds, and why the obstruction persists

More generally, let the poorer players be `P={1,...,m}`, let `r=m+1`, and
write `e_i` for the unit vectors.  For every `m>=4`, take the lower envelope
of the four common-total allocations

```text
g1 = (m-1)(e4+er)
g2 = (m-1)(e3+e4)
g3 = e1+e2+e3+(m-4)e5+(m-1)er
g4 = sum_{i in P} ei + (m-2)er.
```

For `m=4`, the coefficient of `e5=er` in the middle term is zero.  All rows
have total `2m-2`.  Therefore every row is a core allocation of the
lower-envelope game and every coalition attains its worth at a row: the game
is exact directly from the definition.

The four coalition values

```text
v(N\{1}) = v(N\{2}) = 2m-3,
v({3,r}) = v({4,r}) = m-1
```

give a complete hand proof that

```text
Lmin(v) = (1,...,1,m-2).
```

Indeed, any core allocation giving everyone at least one must have
`x1=x2=1`.  Writing `y=x-1_N`, efficiency gives
`sum_i y_i=m-3`, while the last two constraints give
`y3+yr>=m-3` and `y4+yr>=m-3`.  Comparing either inequality with the total,
and then intersecting their equality supports, gives `y_i=0` for every
poorer player and `y_r=m-3`.  Thus the max-min face is the displayed point.
But `v({r})=0`, making the unique richest suffix slack by `m-2`.

The same family has a closed-form Lmax.  Put

```text
a = (m-1)/(2(m-2)),   c = (m-1)/2.
```

Then Lmax equals `c` on players `3,4,r` and `a` on every other player.
Indeed, the two pair constraints force every core point's largest coordinate
to be at least `c`.  The point

```text
z = a g4 + (1-a) g2
```

is in the core and has exactly those coordinates, so it attains the optimal
ceiling.  On that ceiling face the pair constraints force
`x3=x4=xr=c`; the other `m-2` coordinates have a fixed total and their next
leximax ceiling is minimized uniquely by setting all of them to their average
`a`.  Therefore Lmin and Lmax differ for every `n>=5`, while the manuscript's
classification proves equality through four players.

The exact-balanced circuit is

```text
1_{3r} + 1_{4r} + sum_{i in P\{3,4}} 1_{i} - 1_{r} = 1_N.  (UF-C)
```

The protector slacks are zero, the `m-2` positive poorer-singleton slacks are
one each, and the negative richest-singleton slack is `m-2`.  Thus the slack
budget is exactly

```text
0 + 0 + (m-2) - (m-2) = 0,
```

or `(FP)` at equality.  The fourth poorer player is decisive at the threshold;
each additional poorer player then contributes one unit simultaneously to
the positive sacrifice budget and to the permitted richest-singleton slack.
The five-player witness is the first member of an infinite obstruction family.

## Arbitrarily large richest strata

The construction has a two-parameter amplification.  Let `P` have `m`
players, let `R` have `h` players, and assume `m>=h+3`.  After multiplying by
`h`, replace the old richest coordinate uniformly by the block `R`:

```text
g1 = h(m-1)e4 + (m-1)1_R
g2 = h(m-1)(e3+e4)
g3 = h(e1+e2+e3) + h(m-4)e5 + (m-1)1_R
g4 = h1_P + (m-2)1_R.
```

The resulting integral exact game has

```text
Lmin_i = h      on P,
Lmin_i = m-2    on R,
v(R) = 0.
```

The same complement and rich-block constraints prove this formula in two
Lmin stages.  Its Lmax is `c=h(m-1)/(h+1)` on `R union {3,4}` and
`a=h^2(m-1)/((h+1)(m-2))` elsewhere, attained by the convex combination
`t*g4+(1-t)*g2`, where `t=h(m-1)/((h+1)(m-2))`.

Consequently the richest-stratum obstruction is not tied to a singleton:
both the richest block and the ambient dimension can grow.  The exact
distance formula is

```text
||Lmin-Lmax||_1 = 4h(m-h-2)/(h+1).
```

Every game in the family is indecomposable.  For each fixed `h`, after
normalizing by `v(N)=2h(m-1)`, the distance tends to `2/(h+1)` as `m`
grows.  The strongest axis is `h=1`, where the exact normalized distance is
`(m-3)/(m-1) -> 1`.  Null-player padding preserves only the five-player
value `1/3`, while a direct sum can create a large tied rich block but is
decomposable.  Thus the growing indecomposable separation, not dimensional
existence or the tied-block size by itself, is the content.

## What is and is not new

The exact-partition condition is established terminology, and its implication
to the Dutta--Ray/Lorenz conclusion is published.  Exact balancedness and the
egalitarian transfer-blocking property are also prior art.  The proposed new
contribution is their combination into the sacrifice-budget inequality, the
sharp human four/five threshold, and the four-generator obstruction family in
every dimension at least five.

This materially strengthens the mathematical narrative, but a definitive
novelty opinion still requires expert review of the exact-partition,
exact-balancedness, and egalitarian-core citation chains.

## Reproduction

From `coopgames/`:

```bash
python src/verify_n5_unique_richest_boundary.py \
  --output results/n5_unique_richest_boundary.json
python src/verify_unique_richest_family.py \
  --max-players 12 --exact-lmin-through 7 --exact-lmax-through 6 \
  --output results/unique_richest_family.json
python src/verify_rich_block_family.py \
  --max-rich-block 4 --extra-poorer 4 \
  --exact-replay-through-players 7 \
  --output results/rich_block_family.json
```

The first verifier checks the fixed five-player generators, recomputes all 30
proper coalition faces by exact LP, recomputes Lmin by the independent exact
staged algorithm, and checks the incidence/slack circuit.  The family verifier
checks the parametric identities and closed-form Lmax proof through the
requested dimension and performs independent exact staged Lmin/Lmax replays
through the requested player bound.  The rich-block verifier audits the
dimension-free formulas over a two-parameter exact-rational grid; the human
symbolic proof, not the finite grid, carries the universal quantifiers.
