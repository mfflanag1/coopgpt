# A structural proof of the four/five Lmin threshold

## Statement

Let `v` be an exact game, normalize `v({i})=0`, and write
`phi=Lmin(v)`.  If `|N|<=4`, every cumulative richer payoff suffix of
`phi` is tight.  Thus `v` is an exact partition game at `phi`.

The proof below replaces exhaustive machine enumeration by a human-scale,
mechanism-driven case analysis.  Section 4 still separates a few possible
tight protectors and complement patterns; it does not enumerate games or the
full tight-set lattice.  Its key input is the published transfer-blocking characterization
of the egalitarian core due to Arin--Iñarra: whenever one player receives
strictly more than another, a tight coalition contains the former and omits
the latter.  We call such a coalition a **protector coalition** descriptively.
The new step is to combine that known property with exact-game singleton
witnesses.  This explains the sharp threshold: through
four players every possible boundary reduces to one of three small geometric
configurations, whereas the known five-player example escapes them in a
`3|2` configuration.

Throughout, `C=Core(v)`, `V=v(N)`, and a coalition is *tight* when
`phi(S)=v(S)`.  Exactness means

```text
v(S) = min { x(S) : x in C }
```

for every coalition `S`.  In particular, for every player `i` there is a
point `z^i in C` with `z^i_i=0`.

## 1. Published transfer-blocking property

Let `B` be a payoff stratum of `phi`, at level `alpha`, let `P` be the union
of the poorer strata, and let `R` be the union of the richer strata.  For
every `i in B` and `h in R`, there is a tight coalition `T` such that

```text
h in T,   i not in T.                                  (P)
```

This is the Arin--Iñarra characterization of membership in the egalitarian
core, applied to Lmin.  For a self-contained check of conventions, it also
follows from the following LP-dual argument.  The face is defined by final
payoff strata, not by potentially finer algorithmic pinning substeps; tied
players that pin at different degenerate substeps therefore cause no issue.
Consider the stratum face

```text
F = {x in C : x_p=phi_p (p in P), x_l>=alpha (l not in P)}.
```

The maximum of `x_i` on `F` is `alpha`.  Otherwise, the segment from `phi`
to a point with `x_i>alpha`, taken sufficiently close to `phi`, would keep
all richer coordinates strictly above `alpha`, keep every current coordinate
at least `alpha`, and raise at least one current coordinate.  This would
lexicographically improve `phi`.

Apply LP duality to `max x_i` on `F`.  Let `lambda_S>=0` be the multipliers
of `v(S)-x(S)<=0`, let `mu_l>=0` be the multipliers of
`alpha-x_l<=0`, and put

```text
w_q = sum_{S containing q} lambda_S.
```

Stationarity at a nonprevious coordinate `q` is

```text
-1[q=i] - w_q - mu_q + nu = 0.
```

Previous coordinates have free equality multipliers, so their stationarity
equations impose no restriction on the coverage comparison below.

Since `phi_h>alpha`, complementary slackness gives `mu_h=0`.  Hence

```text
w_h - w_i = 1 + mu_i > 0.
```

Some positive-multiplier coalition therefore contains `h` and omits `i`.
Complementary slackness makes that coalition tight, proving (P).

## 2. A dimension-free fractional-packing obstruction

Suppose `r` is the unique richest player, with `phi_r=gamma`, and put
`L=N\{r}` and `q_i=phi_i` for `i in L`.  Thus

```text
0 <= q_i < gamma.
```

For every `i in L`, the protector lemma gives a tight coalition

```text
T_i = {r} union Q_i,
empty != Q_i subseteq L\{i}.
```

The set `Q_i` is nonempty because the singleton `{r}` is slack:
`phi_r=gamma>0=v({r})`.

Use exactness of `{r}` to take `z in C` with `z_r=0`.  For arbitrary
nonnegative weights `lambda_i`, define the load of a poorer player `j` by

```text
c_j = sum { lambda_i : j in Q_i },
Lambda = sum_i lambda_i.
```

If every load is at most one, then nonnegativity of `z` and tightness of the
protectors give

```text
gamma + q(L) = z(L)
             >= sum_j c_j z_j
              = sum_i lambda_i z(Q_i)
             >= gamma Lambda + sum_j c_j q_j.
```

Consequently every fractional packing of the protector sets must satisfy the
dimension-free inequality

```text
gamma (Lambda-1) <= sum_j (1-c_j) q_j.                 (FP)
```

This is a general necessary condition, not a finite enumeration.  It says
that a high-weight packing of protectors is incompatible with the exact
singleton witness unless enough low-payoff mass remains uncovered.

It immediately excludes a unique richest player when `|L|<=3`:

- For `|L|=1`, no nonempty `Q_i subseteq L\{i}` exists.
- For `|L|=2`, put weight one on both singleton protectors.  Then
  `Lambda=2` and every load is one, so (FP) says `gamma<=0`.
- Let `|L|=3`.  If some `Q_i={j}`, put weight one on `Q_i` and on
  `Q_j`.  These sets are disjoint, so this is a fractional packing with
  `Lambda=2`.  It leaves at most one player uncovered; hence (FP) says
  `gamma<=q_u<gamma` (or `gamma<=0` if none is uncovered).  If no
  `Q_i` is a singleton, then `Q_i=L\{i}` for all `i`.  Weighting all
  three sets by `1/2` gives `Lambda=3/2` and unit load everywhere, so
  (FP) says `gamma/2<=0`.

Thus an Lmin allocation of a normalized exact game on at most four players
cannot have a singleton richest stratum.

## 3. A first singleton stratum has a tight complement

Suppose the unique poorest player is `a`, with `phi_a=alpha`.  Then
`x_a<=alpha` for every `x in C`: otherwise a sufficiently short segment from
`phi` toward a point with `x_a>alpha` raises the minimum payoff.  Exactness
therefore gives

```text
v(N\{a}) = min_{x in C} x(N\{a})
          = V - max_{x in C} x_a
          = V-alpha
          = phi(N\{a}).                                (4)
```

So the first richer suffix is tight in every dimension whenever the poorest
stratum is a singleton.

## 4. The only remaining four-player geometry: a `2|2` boundary

Let the two poorer players be `a,b` and the two richer players be `c,d`.
Write their payoffs in nondecreasing order.

### 4.1 Distinct poorer levels

Let

```text
phi_a=alpha < phi_b=beta < phi_c=gamma <= phi_d=delta.
```

By (4), `N\{a}` is tight.  Suppose, for contradiction, that `{c,d}` is
slack.  Then `N\{b}` cannot be tight: if both complements were tight, every
core point would satisfy `x_a<=alpha` and `x_b<=beta`, so exactness would give
`v({c,d})=gamma+delta`.

Apply the protector lemma to player `b` and richer player `c`.  A protector
contains `c` and omits `b`.  Of the four possibilities

```text
{c}, {a,c}, {c,d}, {a,c,d}=N\{b},
```

the first is slack because `gamma>0`, and the last two are slack by the
preceding paragraph.  Hence `{a,c}` is tight.

Now take the exact singleton witness `z^c`, with `z^c_c=0`.  Tightness of
`N\{a}` and `{a,c}` gives

```text
z^c_b + z^c_d >= beta+gamma+delta,
z^c_a           >= alpha+gamma.
```

Adding yields `z^c(N)>=V+gamma`, contradicting efficiency.

### 4.2 Tied poorer level

Let

```text
phi_a=phi_b=alpha < phi_c=gamma <= phi_d=delta.
```

Again suppose `{c,d}` is slack.  Applying the protector lemma to each poorer
player and each richer player gives

```text
N\{a} tight  or  ({b,c} and {b,d} tight),
N\{b} tight  or  ({a,c} and {a,d} tight).              (5)
```

Indeed, for example, a protector containing `c` and omitting `a` can only be
`{c}`, `{b,c}`, `{c,d}`, or `N\{a}`; the singleton and the alleged slack
suffix are unavailable.

If both complements in (5) are tight, exactness makes `{c,d}` tight, a
contradiction.  If exactly one complement is tight, say `N\{a}`, then the
other disjunction makes `{a,c}` tight.  At the exact singleton witness
`z^c_c=0`,

```text
z^c_b+z^c_d >= alpha+gamma+delta,
z^c_a       >= alpha+gamma,
```

again giving `z^c(N)>=V+gamma`.  The opposite case is symmetric.

It remains that neither complement is tight.  Then all four cross pairs are
tight.  Since

```text
v({a,c})+v({b,d})=(alpha+gamma)+(alpha+delta)=V,
```

the two corresponding core inequalities must be equalities at every core
point; the same is true of `{a,d}` and `{b,c}`.  At the exact singleton
witness `z^c`, these equalities force

```text
z^c=(alpha+gamma, alpha+gamma, 0, delta-gamma).
```

For a sufficiently small `t>0`, the core point
`(1-t)phi+t z^c` raises both poorest coordinates above `alpha` while both
richer coordinates remain above them.  This contradicts max-min optimality.

Thus the richer pair is tight in both `2|2` geometries.

## 5. Completion and the sharp threshold

Consider any strict payoff boundary of `phi` when `|N|<=4`.  Its richer side
cannot be a singleton by Section 2.  Hence its poorer side has size at most
two.  A one-player poorer side is covered by Section 3.  If the poorer side
has size two, the only remaining possibility is the four-player `2|2`
geometry of Section 4.  Every richer suffix is therefore tight.

This proves the exact-partition classification without finite enumeration.
At five players, new boundary geometries appear.  The base game in the paper
has payoff strata `2+1+2`; its failed boundary is exactly

```text
L={1,2,4},  H={3,5},  |L|=3,  |H|=2.
```

The protector argument therefore explains both why four players are forced
into the exact-partition class and why the first known obstruction appears at
five.  Concretely, at the base Lmin point the only tight nontrivial proper
coalitions are

```text
{3,4,5}, with value 18, and {1,3,5}, with value 14.
```

The first protects the initial block `{1,2}` and the second protects player
`4`, while the richer pair `{3,5}` retains one unit of slack.  The third poor
player lets these protectors overlap without triggering either of the
four-player singleton-witness contradictions.  In particular, (FP) is a
unique-richest obstruction and does not apply to this failed boundary: an
exact singleton witness can zero one of the two rich players, but not the
entire rich side.  This is a structural account
of how the sharp example escapes the proof, not a claim that every
higher-dimensional slack boundary must have the same `3|2` shape.

The previously published exact-partition-to-Lorenz implication then gives
`Lmin=Lmax=PES` through four players, while the existing five-player pair
proves sharp failure.

## Audit boundary

The protector property itself is prior art: it is the transfer-blocking
characterization of the egalitarian core in Arin--Iñarra (2001).  The proposed
new contribution is its use together with exact singleton witnesses, including
the dimension-free fractional-packing obstruction (FP), to prove the sharp
low-dimensional inclusion ``exact through four implies exact partition at
Lmin.''  Neither the novelty of (FP) nor that of the classification has yet
been established by a definitive literature review.  The argument does not
claim that the exact-partition condition or its Lorenz consequence is new.
The existing two exact-rational encodings remain useful as independent checks
of the theorem and of all sign conventions, but they are no longer the proof
of the four-player classification if the argument above survives review.
