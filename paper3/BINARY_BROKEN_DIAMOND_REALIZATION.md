# Binary broken-diamond realization and the structural four/five threshold

This note records the integer-level specialization `a=2,b=1`.  The complete
two-column normal form, exterior-slack budget, and arbitrary-level converse
are in `paper3/TWO_COLUMN_LMIN_OBSTRUCTION.md`.

## Universal realization theorem

Partition the player set into four nonempty blocks

```text
N = C disjoint-union X disjoint-union Y disjoint-union R
```

with `|C|+|R|>=3`. Put `A=C union X`, `B=C union Y`, assign payoff two on
`C` and one outside `C`, and call this vector `phi`. Define

```text
K = {x>=0: x(N)=phi(N), x(A)>=phi(A), x(B)>=phi(B)},
v(S)=min{x(S):x in K}.
```

Then `v` is singleton-normalized and exact, `Core(v)=K`, and
`Lmin(v)=phi`. The crossing coalitions `A,B` are tight, while

```text
s_phi(C)         = min(2|C|,|R|),
s_phi(A union B) = min(|X|,|Y|).
```

Both are positive. Thus every four-cell Venn shape satisfying the sharp
capacity condition `|C|+|R|>=3` has a dimension-free exact realization as a
broken tight diamond at Lmin.

## Proof

The point `phi` lies in `K`, so both displayed inequalities are attained.
Every coalition minimum is attained on the compact polytope. The usual two
inclusions show that the lower-envelope game has core exactly `K`, and is
therefore exact.

Every coordinate has minimum zero. For a player in `X`, move its unit to
`C`; this preserves the `A` inequality and strengthens the `B` inequality.
The argument for `Y` is symmetric, and for a player in `R` moving its unit to
`C` strengthens both constraints. For a player in `C`, if `|C|>=2`, move its
two units to another member of `C`. If `|C|=1`, the hypothesis gives
`|R|>=2`: zero `C`, add two units to each of `X` and `Y`, and remove two units
in total from `R`. Hence the lower envelope is singleton-normalized.

The two tight coalitions with unit weight load every member of `C` twice,
every member of `X union Y` once, and every member of `R` zero times. This is
a strict richer-side cover. Its supporting gate fixes all level-one players
at the first progressive leximin stage. Efficiency leaves total `2|C|` on
`C`, whose max-min allocation is two per player. Thus `Lmin(v)=phi`.

Writing `c=|C|`, `x=|X|`, `y=|Y|`, `r=|R|`, aggregate minimization gives

```text
v(C)=max(0,2c-r),
v(C union X union Y)=2c+max(x,y),
```

which proves the slack formulas.

## Sharp necessity and the four/five threshold

The four Venn regions of a crossing pair are `C=A intersection B`,
`X=A setminus B`, `Y=B setminus A`, and `R=N setminus(A union B)`.

A broken tight diamond in an exact game must have `R` nonempty. If
`A union B=N`, the exact-balanced vector

```text
+1_A +1_B -1_(A intersection B) = 1_N
```

and tightness of `A,B` force their intersection tight; the union is already
the tight grand coalition.

The only remaining four-player Venn shape has one player in each block. It
cannot orient the intersection above the exterior in a singleton-normalized
exact game. Let `C={h}`, `R={r}`, and suppose `phi_h>phi_r`. Exactness of
`{h}` gives a core point `z` with `z_h=0`. For `d=z-phi`, tightness of `A`
and `B` gives `d(X)>=phi_h` and `d(Y)>=phi_h`. Efficiency gives
`d_r<=-phi_h`, so `z_r<=phi_r-phi_h<0`, contradicting `z_r>=0`.

Therefore a payoff-oriented broken tight diamond needs at least five players.
The universal family attains five in both possible ways:

```text
(|C|,|X|,|Y|,|R|)=(2,1,1,1) or (1,1,1,2).
```

This is a structural explanation of the four/five threshold: three players
are required to make a crossing, a fourth exterior player is required by
exact balancedness, and singleton exactness requires one additional unit of
intersection-or-exterior capacity to orient the diamond across a strict
payoff boundary.

## Reproduction

```bash
python src/verify_binary_broken_diamond_realization.py \
  --output results/binary_broken_diamond_realization.json
```

The verifier reconstructs the lower-envelope core over a parameter grid,
recomputes Lmin exactly in the smallest cases, and checks both slack formulas.
The computation is not a proof dependency.

## Novelty calibration

Lower envelopes, exact balancedness, and Boolean-lattice Venn decompositions
are established. The candidate contribution is the sharp realization and
capacity theorem tying broken tight diamonds to Lmin and explaining why their
first payoff-oriented exact realization has five players. Specialist review
is required.
