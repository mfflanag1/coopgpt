# Positive-Lehman trace obstruction

## Classical matrix identity

A positive Lehman pair consists of square zero--one matrices `A,B` with

```text
A B^T = J + k I,       k>=1.
```

The matrices are regular: write `r` for the row and column sum of `A` and
`s` for that of `B`.  Lehman's theorem makes this identity central to the
cores of nondegenerate minimally nonideal matrices.  None of that classical
structure is claimed as new here.

In the exact-game application, rows of `A` are rich players and columns are
the supported tight-coalition traces.  Every row of `B`, used as a zero--one
selector of those columns, has rich incidence

```text
1_H + k e_d.
```

It is exactly the rooted rounding sought by the exact-face theorem.

## Two-label density theorem

Suppose the packet weights every column of `A` by `1/r`.  Let `U` be the
columns whose lifted coalitions contain the losing poor player and `V` those
containing the gaining poor player.  Transport implies

```text
0 <= |U| < |V| < r.
```

For a column set `Z`, define

```text
Pi_B(Z) = sum_d binom(|row_d(B) intersect Z|,2).
```

The packet is impossible if

```text
s|V| - 2 Pi_B(V) > Pi_B(U).                          (LH-D)
```

Indeed, let `n_1` be the number of dual rows meeting `V` exactly once.
Column regularity and `t<=2 binom(t,2)` for `t>=2` give

```text
n_1 >= s|V| - 2 Pi_B(V).
```

If every such row met `U` at least twice, each would contribute at least one
to `Pi_B(U)`, contradicting (LH-D).  Therefore some dual row meets `V`
once and `U` at most once.  Its Lehman identity is a safe rooted cover, which
exactness forbids.

If any two columns of `B` occur together in at most one row, then
`Pi_B(Z)<=binom(|Z|,2)`, so the simpler sufficient condition is

```text
|V|(s-|V|+1) > binom(|U|,2).                         (LH-L)
```

The density condition is automatic for `|V|<=2`.  With one gaining column
there are no losing columns. With two gaining columns there is at most one
losing column, while nonsingularity makes the two dual columns distinct and
their codegree at most `s-1`.

There is a dimension-free extension to `|V|=3`.  For any three columns of
`B`, suppose no row meets them exactly once.  Their row-load vector then has
values only `0,2,3`.  If `x` rows have load three, the transpose identity
forces every column of `A` outside the chosen triple to meet exactly one of
those `x` rows.  Capacity gives `x>=s-1`; parity of the remaining total
incidence `3(s-x)` forces `x=s`, which would make the three columns identical.
Thus a simple row exists.  Its residual is `(r-3)(1-u)`, and the positive or
negative band excludes all `u<=|U|<=2`.  Consequently every survivor must
have `|V|>=4` and `r>=5`.  See
`THREE_COLUMN_LEHMAN_SEPARATION.md`.

At the first open value `|V|=4`, an odd-multiplier parity lemma still forces a
simple row.  In the thin case `k=1`, any survivor is consequently restricted
to `r>=6`, `|U|=3`, and `|U intersect V|<=1`.  The local transport law reduces
each label-free trace to one of six explicit `(V-load,U-load)` tiles.  See
`FOUR_COLUMN_RESIDUAL_NORMAL_FORM.md`.  This is a normal form, not yet an
exclusion of all six tiles.

The triple-intersection property sharpens this normal form.  All dual rows
with `u=3` have pairwise disjoint primal row supports, so there are at most
`s-1` of them.  Every `w=1` row lies in this packing and anchors at least
`r-5` label-free traces of the forced type `(1,3),(3,0)`.  See
`FOUR_LABEL_SIMPLE_ROW_PACKING.md`.  The next obstruction is therefore a
global companion-congestion bound rather than another local load census.
Before that packing step, a divisibility argument shows that all rows with
`u>=2` are exactly one canonical column of `B`; this majority-column rigidity
rules out every dual-cubic (`s=3`) core and forces `s>=4`.

The natural stronger conjecture is that every positive Lehman pair has the
two-label property without a density hypothesis: whenever
`|U|<|V|<r`, some dual row meets `V` once and `U` at most once. This has been
checked only on small classical examples and is not used as a theorem.

## Two-sided convex dual-row criterion

The real overload budget gives a stronger sufficient test that does not
require a zero--one safe selector.  Put `p=|U|`, `ell=|V|`, and for a dual
row `d` write `u_d=|row_d(B) intersect U|` and
`w_d=|row_d(B) intersect V|`.  Define

```text
F_d=(r-p)w_d+p-ell-(r-ell)u_d.                       (LH-R)
```

The packet is impossible under either band

```text
w_d>=1,   0<=F_d<=k(r-ell),                          (LH-C+)
u_d>=1,  -k(r-p)<=F_d<=0.                            (LH-C-)
```

Indeed, interpolate the uniform packet with row `d` using

```text
t=(r-ell)/(r w_d-ell).
```

The resulting rich load is `1_H+t k e_d`, its gaining-poor load is exactly
one, and its losing-poor load is

```text
a_d=[p(w_d-1)+u_d(r-ell)]/(r w_d-ell).
```

The positive band says `a_d<=1` and `t k>=1-a_d`.  The exact-face
overload budget would then give `t k phi_d<=(1-a_d)phi_a`, contradicting
`phi_d>phi_a`.  When `w_d=1,u_d<=1`, this specializes to the earlier safe
dual-row conclusion, but the proof and conclusion are genuinely
real-valued.

For the negative band, interpolate instead with weight
`t_hat=(r-p)/(r u_d-p)`.  The losing load becomes one and the gaining load is

```text
b_d=[ell(u_d-1)+w_d(r-p)]/(r u_d-p).
```

Now `F_d<=0` says `b_d<=1`, while `F_d>=-k(r-p)` says
`t_hat k>=1-b_d`; the overload budget contradicts `phi_d>phi_b`.

Regularity also gives the exact conservation law

```text
sum_d F_d=k(ell-p)>0.                                (LH-S)
```

This scalar law is the sum of the stronger local transport identity

```text
A^T F=k[(r-p)1_V-(r-ell)1_U].                        (LH-T)
```

Every trace column carrying neither poor label therefore contains residuals
whose sum is exactly zero.  See `LEHMAN_RESIDUAL_TRANSPORT.md`.

Since every zero-`V` row has negative residual, some gaining-bearing row has
positive residual.  Thus a surviving packet must have a genuine overshoot
`F_d>k(r-ell)` rather than merely fail an unnamed safe-row search.

In a projective plane of order `q`, one can always choose a point on exactly
one of the `ell<=q` gaining lines.  Its residual is
`F=(q+1-ell)(1-u)`.  The positive band applies when `u<=1`, and the negative
band applies when `u>=2`.  Consequently every finite projective-plane packet
is excluded, in every order and without a Desarguesian assumption.

## Subset residual face budget

The row interpolation extends to any nonempty dual-row set `D`.  Put
`d=|D|`, `U_D=sum_(j in D)u_j`, `W_D=sum_(j in D)w_j`, and
`F(D)=sum_(j in D)F_j`.  Averaging its dual selectors gives rich load
`1_H+(k/d)1_D`.  Interpolating with the uniform packet yields

```text
W_D>=d, F(D)>=0
  => k(r-ell)[phi(D)-v(D)] <= F(D) phi_a,

U_D>=d, F(D)<=0
  => k(r-p)[phi(D)-v(D)] <= -F(D) phi_b.
```

Thus a zero-residual set with the relevant average poor load at least one is
forced tight.  Singleton sets recover the two row bands.  Taking all rows
meeting `V` and padding to `d=s ell` rows recovers the canonical internal-face
bound below.  See `SUBSET_LEHMAN_FACE_BUDGET.md`.

## Canonical internal face without the density hypothesis

There is an unconditional substitute for a single safe row. Put
`T=s|V|`. The Lehman diagonal gives `k+1<=s`, so `T<n` because `|V|<r` and
`rs=n+k`. Take every dual row meeting `V` and add arbitrary zero-`V` rows
until there are exactly `T` rows; call their index set `D`. Averaging these
rows gives

```text
rich load = 1_H + (k/T) 1_D,
gaining-poor load = 1,
losing-poor load = u(D)/T < 1.
```

The exact-face overload budget therefore forces

```text
phi(H)-v(H) < phi(D)-v(D) <= [T-u(D)] phi_a/k.      (LH-F)
```

For the strict inequality, evaluate each dual row outside `D` at the core
point exact on `H`. Such a row carries no gaining-poor label, so its rooted
tight-coalition sum forces the corresponding rich displacement to be
positive. Every rich player outside `D` therefore gains, while `H` loses its
total suffix slack. The displacement of `D` is consequently more negative
than that total slack, and core feasibility converts this into the strict
lower bound above.

Thus every positive Lehman packet, including any packet outside the density
theorem, canonically amplifies the suffix slack onto a proper internal rich
face. This is the candidate recursive invariant for lifting
minimally-nonideal contractions.

## Contractions need only preserve one scalar deficit

Suppose a classical minor lift adjoins unit-weight contracted columns whose
disjoint traces partition the rich rows outside a positive Lehman core. Let
`t_a,t_b` count their losing- and gaining-poor labels. The combined tight
packet satisfies

```text
-sigma + (t_a+|U|/r) Delta_a
       + (t_b+|V|/r) Delta_b >= 0.
```

If its total gaining load is below one, then `t_b=0`, `|V|<r`, and substitution
of `Delta_b=sigma-Delta_a` forces

```text
r t_a + |U| < |V|.
```

Hence `t_a=t_b=0` and `|U|<|V|<r`: every contracted column is automatically
poor-label-free in an exact-cover lift. Adding those neutral columns to a safe Lehman dual row gives
the same rooted cover of the original suffix, and adding them to the averaged
dual rows preserves the strict internal-face amplification. The unresolved
minor step is preservation of the scalar gaining-player load below one
together with exact coverage of all residual rich rows; classical noncore
rows may otherwise be overcovered. Separate preservation of two label sets
is not needed once those conditions hold. See
`LEHMAN_MINOR_LIFTING.md` for the standalone statement and
Corollary `cor:lx-deficit-preserving-lehman-minor` for the proof.

Equivalently, the scale-separated formulation in
`SCALE_SEPARATED_MNI_BRIDGE.md` reduces both requirements to preservation of
one weighted objective gap: any noncore excess then costs more than the
available unit margin.

If a classical MNI lift has noncore rows, they can be included in the density
test rather than discarded. Blocker-core rows meet every noncore clutter row
at least once, and the total excess `s|W|-n=s(|W|-r)+k` bounds the number
meeting a fixed support `W` twice. Thus the strengthened sufficient condition

```text
s|V|-2 Pi_B(V) > Pi_B(U) + sum_W [s|W|-n]
```

produces a dual selector exact on every noncore row. See
`NONCORE_LEHMAN_LIFTING.md`.

## Structural significance

This theorem places the earlier arguments in a standard combinatorial
framework:

- an odd trace cycle is the `r=2` thin-Lehman case, and its dual row is the
  alternating rounding;
- a projective plane is a self-dual, column-linear positive Lehman matrix;
  the two-sided residual theorem eliminates this entire family in every
  order, while (LH-L) is only its coarse one-sided density bound;
- the sharp co-singleton support `J-I` instead satisfies the opposite-sign
  identity `(J-I)I=J-I`, so it is not eliminated by the positive theorem.

The other classical branch of the minimally-nonideal theorem, a degenerate
projective plane, is eliminated directly by
`DEGENERATE_MNI_TRACE_EXCLUSION.md`. Its unique nonuniform fractional cover
always yields a safe two-column rooted rounding under the required poor-load
ordering. The explicit objective in `UNIT_GAP_MNI_BRIDGE.md` proves that an
underloaded active trace matrix is nonideal and identifies the scalar
underload with a strict unit set-cover gap.

This is a genuine structural distinction, not a classification yet.  Two
steps remain before one can claim a dimension-free characterization:

1. reduce an arbitrary underloaded active exact-cover packet to a positive
   Lehman core while preserving the scale-separated objective gap (or,
   equivalently in the unscaled formulation, preserving the scalar
   gaining-player deficit and controlling noncore-row excess);
2. rule out the residual polarization required when both convex bands fail
   on a general positive Lehman core.  The first still-open label cardinality
   is now `|V|=4`, where the residual transport identity imposes exact local
   cancellation on every label-free trace.

The classical source is Cornuéjols, Guenin, and Tunçel, *Lehman matrices*,
Journal of Combinatorial Theory B 99 (2009), 531--556,
<https://doi.org/10.1016/j.jctb.2008.06.009>.  The exact-game bridge and the
two-label density argument require specialist novelty review.
