# A structural proof of the four/five Lmin threshold

## Statement

Let `v` be an exact game, normalize `v({i})=0`, and write
`phi=Lmin(v)`.  If `|N|<=4`, every cumulative richer payoff suffix of
`phi` is tight.  Thus `v` is an exact partition game at `phi`.

The proof below does not enumerate payoff compositions, tight-set patterns,
or games.  Its key object is a **protector coalition** forced by the dual of
one ordinary linear program.  It also explains the sharp threshold: through
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

## 1. Protector lemma

Let `B` be a payoff stratum of `phi`, at level `alpha`, let `P` be the union
of the poorer strata, and let `R` be the union of the richer strata.  For
every `i in B` and `h in R`, there is a tight coalition `T` such that

```text
h in T,   i not in T.                                  (P)
```

To see this, consider the Maschler-stage face

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

Since `phi_h>alpha`, complementary slackness gives `mu_h=0`.  Hence

```text
w_h - w_i = 1 + mu_i > 0.
```

Some positive-multiplier coalition therefore contains `h` and omits `i`.
Complementary slackness makes that coalition tight, proving (P).

## 2. A unique richest player is impossible through four players

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

Use exactness of `{r}` to take `z in C` with `z_r=0`, and set
`a_i=z_i-q_i`.  Efficiency gives

```text
a(L)=gamma.                                             (1)
```

The tight protector inequality gives

```text
a(Q_i) >= gamma                                         (2)
```

for every `i`.  Also `z_i>=0`, so

```text
a_i >= -q_i > -gamma.                                  (3)
```

Equations (1)--(3) are impossible when `|L|<=3`:

- For `|L|=1`, no nonempty `Q_i subseteq L\{i}` exists.
- For `|L|=2`, the two protectors give `a_1>=gamma` and
  `a_2>=gamma`, contradicting (1).
- Let `|L|=3`.  If some `Q_i={j}` is a singleton, then
  `a_j>=gamma`.  The protector for `j` supplies a disjoint nonempty
  `Q_j` with `a(Q_j)>=gamma`.  If these sets cover `L`, then
  `a(L)>=2gamma`; otherwise the remaining coordinate is greater than
  `-gamma` by (3), so again `a(L)>gamma`.  If no `Q_i` is a singleton,
  then every `Q_i=L\{i}`.  From (1)--(2), every `a_i<=0`, contradicting
  `a(L)=gamma>0`.

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
four-player singleton-witness contradictions.  This is a structural account
of how the sharp example escapes the proof, not a claim that every
higher-dimensional slack boundary must have the same `3|2` shape.

The previously published exact-partition-to-Lorenz implication then gives
`Lmin=Lmax=PES` through four players, while the existing five-player pair
proves sharp failure.

## Audit boundary

The genuinely new ingredient in this proof is the protector-coalition use of
stagewise Lmin duality together with exact singleton witnesses.  It does not
claim that the exact-partition condition or its Lorenz consequence is new.
The existing two exact-rational encodings remain useful as independent checks
of the theorem and of all sign conventions, but they are no longer the proof
of the four-player classification if the argument above survives review.
