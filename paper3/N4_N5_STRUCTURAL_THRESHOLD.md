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

## Why five succeeds

Take the lower envelope of

```text
g1 = (0,0,0,3,3)
g2 = (0,0,3,3,0)
g3 = (1,1,1,0,3)
g4 = (1,1,1,1,2).
```

All rows have total six.  Therefore every row is a core allocation of the
lower-envelope game and every coalition attains its worth at a row: the game
is exact directly from the definition.

The four coalition values

```text
v(N\{1}) = v(N\{2}) = 5,
v({3,5}) = v({4,5}) = 3
```

give a complete hand proof that

```text
Lmin(v) = (1,1,1,1,2).
```

Indeed, any core allocation giving everyone at least one must have
`x1=x2=1`.  Writing `y=x-1_N`, efficiency gives
`y3+y4+y5=1`, while the last two constraints give
`y3+y5>=1` and `y4+y5>=1`.  Hence `y3=y4=0`, `y5=1`, so the max-min face is
the displayed point.  But `v({5})=0`, making the unique richest suffix slack
by two.

The exact-balanced circuit is

```text
1_{35} + 1_{45} + 1_{1} + 1_{2} - 1_{5} = 1_N.       (U5-C)
```

The protector slacks are zero, singleton slacks 1 and 2 are one each, and the
negative singleton-5 slack is two.  Thus the slack budget is exactly

```text
0 + 0 + 1 + 1 - 2 = 0,
```

or `(FP)` at equality `2=1+1`.  The fourth poorer player is decisive: two
uncovered poorer singleton payoffs can jointly fund the richest-singleton
slack.  With only three poorer players, the same packing leaves at most one
payoff, which is strictly smaller than `gamma`.

## What is and is not new

The exact-partition condition is established terminology, and its implication
to the Dutta--Ray/Lorenz conclusion is published.  Exact balancedness and the
egalitarian transfer-blocking property are also prior art.  The proposed new
contribution is their combination into the sacrifice-budget inequality and
the sharp human four/five threshold, together with the minimal integral
five-player witness above.

This materially strengthens the mathematical narrative, but a definitive
novelty opinion still requires expert review of the exact-partition,
exact-balancedness, and egalitarian-core citation chains.

## Reproduction

From `coopgames/`:

```bash
python src/verify_n5_unique_richest_boundary.py \
  --output results/n5_unique_richest_boundary.json
```

The verifier checks the fixed generators, recomputes all 30 proper coalition
faces by exact LP, recomputes Lmin by the independent exact staged algorithm,
and checks the incidence/slack circuit.
