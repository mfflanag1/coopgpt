# Exact-balanced slack budgets and the four/five threshold

## Status

This is a research note, not yet part of the manuscript theorem chain.  Every
identity below has a short human proof.  The conceptual ingredients have prior
art:

- Arin--Iñarra (2001): the egalitarian-core transfer-blocking property used to
  obtain tight coalitions separating richer from poorer players;
- Csóka--Herings--Kóczy (2011): exact balancedness characterizes exact games;
- Lohmann--Borm--Herings (2012): the structure of minimal exact-balanced
  collections.

The candidate new contribution is the **protector-completion bridge** between
these theories and its use to explain the sharp Lmin threshold.  No claim of
novelty is made until the relevant citation chains have been checked by an
expert.

## 1. Slack-budget law

Let `v` be an exact game, let `phi` be a core allocation, and write

```text
s_phi(S) = phi(S) - v(S) >= 0.
```

An exact-balanced weight vector `rho` satisfies

```text
sum_S rho_S 1_S = 1_N,
```

with every coefficient positive except possibly one.  Exact balancedness of
`v` gives

```text
sum_S rho_S v(S) <= v(N).
```

Efficiency gives `sum_S rho_S phi(S)=phi(N)=v(N)`.  Subtraction proves:

> **Slack-budget law.**  For every exact-balanced weight vector,
>
> ```text
> sum_S rho_S s_phi(S) >= 0.                            (SB)
> ```

If `H` is the unique coalition with negative coefficient, this becomes

```text
(-rho_H) s_phi(H)
    <= sum_(S != H) rho_S s_phi(S).                    (SB-H)
```

Thus slack of a negatively weighted target coalition must be funded by slack
of the positively weighted coalitions.  In particular, if all positive
coalitions are tight at `phi`, then `H` is tight as well.

This is an immediate quantitative reading of exact balancedness, not a new
characterization of exact games.

## 2. Boundary-cover inequality

Assume singleton normalization `v({i})=0`.  Fix `H subsetneq N`, put
`L=N\H`, and let `T` be any collection of coalitions tight at `phi`.  Give
these coalitions weights `lambda_T>=0` and define their player coverages

```text
c_j = sum_(T containing j) lambda_T.
```

Suppose constants `alpha>beta>=0` satisfy

```text
c_h <= alpha  for h in H,
c_i <= beta   for i in L.
```

Complete the coverage with singleton weights

```text
delta_h = alpha-c_h,
delta_i = beta-c_i.
```

After adding an arbitrary common grand-coalition weight if `beta=0`, the
incidence identity

```text
sum_T lambda_T 1_T
 + sum_j delta_j 1_{j}
 - (alpha-beta) 1_H
 = beta 1_N
```

is an exact-balanced collection after positive rescaling.  Applying (SB-H),
using tightness of every `T` and singleton slack
`s_phi({j})=phi_j`, gives:

> **Boundary-cover inequality.**
>
> ```text
> (alpha-beta) s_phi(H)
>   <= sum_(h in H) (alpha-c_h) phi_h
>      + sum_(i in L) (beta-c_i) phi_i.                (BC)
> ```

There is also a direct core-witness proof.  Exactness of `H` gives a core
point `z` with `z(H)=v(H)`.  For `d=z-phi`,

```text
d(H)=-s_phi(H),  d(L)=s_phi(H),  d_j>=-phi_j,
d(T)>=0 for every phi-tight T.
```

Weight the last inequalities by `lambda`, compare the coverage vector with
`alpha 1_H + beta 1_L`, and use the coordinate lower bounds.  Rearrangement
is exactly (BC).

### Exact completion

If the cover is uniform on both sides,

```text
c_h=alpha  (h in H),
c_i=beta   (i in L),
alpha>beta,
```

then the right side of (BC) is zero, so `H` must be tight.  This is the
normal-cone/exact-balanced certificate behind exact-partition tightness.

### Canonical boundary defect

Fix any family `T` of coalitions tight at `phi`, normalize
`alpha-beta=1`, and minimize the right side of (BC) over the nonnegative
coalition weights and `beta`, subject to

```text
c_h <= beta+1  for h in H,
c_i <= beta    for i in L.
```

Call the resulting exact linear-program value `Delta_(phi,T)(H)`.  Then

```text
0 <= s_phi(H) <= Delta_(phi,T)(H) <= phi(H).           (BD)
```

The last inequality uses the feasible zero cover.  Thus a zero-defect cover
forces the boundary tight in every dimension.  If such a cover exists for
every richer suffix of Lmin, the game is exact partition at Lmin and the
published Lorenz consequence applies.  This packages the dimension-free
research problem into a precise covering invariant: classify when egalitarian
transfer blockers have zero defect, and classify the positive-defect equality
cases when they do not.

## 3. The existing fractional-packing lemma is a specialization

Suppose `r` is uniquely richest at Lmin, with `phi_r=gamma`, and choose for
every poorer player `i` a tight protector

```text
T_i = {r} union Q_i,   empty != Q_i subseteq L\{i}.
```

Give these protectors weights `lambda_i`, put

```text
Lambda = sum_i lambda_i,
c_j = sum_(i: j in Q_i) lambda_i <= 1,
```

and apply (BC) to `H={r}`, `alpha=Lambda`, `beta=1`.  Since
`s_phi({r})=phi_r=gamma`, this gives exactly

```text
gamma (Lambda-1) <= sum_j (1-c_j) phi_j,               (FP)
```

the fractional protector-packing obstruction in the manuscript.  In
exact-balanced language, the corresponding incidence identity is

```text
sum_i lambda_i 1_{T_i}
 + sum_j (1-c_j) 1_{j}
 - (Lambda-1) 1_{r}
 = 1_N.
```

The proof through four players therefore combines a published Lmin
transfer-blocking theorem with a published exactness characterization; the
new content is the completion argument and its sharp low-dimensional use.

## 4. The unique-richest threshold and infinite obstruction family

The fractional packing inequality gives a direct structural explanation for
one sharp branch of the four/five threshold.  With at most three poorer
players, either two disjoint protector parts leave at most one uncovered
payoff—strictly smaller than the unique richest payoff—or the three
two-element protector parts admit a half-integral perfect cover.  In either
case (FP) is impossible.

At five players a four-generator exact lower-envelope game attains (FP) at
equality.  More strongly, it is the first member of a family for every
`n=m+1>=5`.  With poorer set `P={1,...,m}` and richest player `r=m+1`, take

```text
g1 = (m-1)(e4+er)
g2 = (m-1)(e3+e4)
g3 = e1+e2+e3+(m-4)e5+(m-1)er
g4 = sum_{i in P} ei + (m-2)er.
```

Every generator has total `2m-2`, so the lower envelope is exact.  Its Lmin
point is `phi=g4`, proved by the four values
`v(N\{1})=v(N\{2})=2m-3` and
`v({3,r})=v({4,r})=m-1`, while `v({r})=0<m-2=phi_r`.  The
exact-balanced circuit

```text
1_{3r}+1_{4r}+sum_{i in P\{3,4}}1_i-1_r=1_N
```

has slack budget `0+0+(m-2)-(m-2)=0`.  The fourth poorer player supplies the
second uncovered unit that cannot exist at four players, and each additional
poorer player adds one unit to both sides.  This is the sacrifice-budget
explanation of both the sharp threshold and its persistence.  The complete
human proof and exact replay are in `paper3/N4_N5_STRUCTURAL_THRESHOLD.md`.

## 5. The five-player monotonicity escape saturates the slack budget

For the base five-player game,

```text
phi = (1,1,13/2,5,13/2),
H = {3,5},
s_phi(H) = 13-12 = 1.
```

The only tight nontrivial proper coalitions are

```text
T_1 = {1,3,5},  v(T_1)=14,
T_4 = {3,4,5},  v(T_4)=18.
```

Their incidence vectors satisfy the exact-balanced identity

```text
1_{135} + 1_{345} + 1_{2} - 1_{35} = 1_N.             (E5)
```

The positive protectors have zero slack, player 2 has singleton slack one,
and the negative richer suffix has slack one.  Hence (SB) is attained at
equality:

```text
0 + 0 + 1 - 1 = 0.
```

Equivalently, in (BC) take `alpha=2`, `beta=1`.  The protectors cover each
rich player twice and the poorer players with loads `(1,0,1)`.  The only
coverage deficit is player 2, whose payoff is one, so

```text
(2-1) * s_phi({3,5}) = 1 = phi_2.
```

This is the structural escape: the fifth player supplies exactly the unit of
positive singleton slack needed to fund the slack richer suffix.  Through four
players the protector completions used in the human proof either have an
insufficient positive slack budget (contradicting exact balancedness) or fall
into the all-cross-pairs configuration, where a direct Lmin-improving segment
finishes the argument.

The exact verifier also minimizes the boundary-defect LP rather than merely
checking the displayed cover.  Its optimum is one.  Since (BD) supplies the
matching lower bound from `s_phi(H)=1`, the five-player cover is globally
optimal within this boundary-cover relaxation.

## 6. A second sharp threshold found from this framework

The first attempt to generalize the four-player proof suggested that every
Lmin boundary with at most two cumulative poorer players might be tight in
every exact game.  That dimension-free conjecture is false, but the failure is
sharp:

```text
|N| <= 5 and |L| <= 2  =>  the richer suffix H is tight;
|N|  = 6 and |L|  = 2  =>  a slack richer suffix exists.
```

The five-player lower bound is currently an exact symbolic theorem: all 16
ordered-stratum boundary queries are unsatisfiable.  The six-player upper
bound is stronger evidence—a fixed lower envelope of six common-total integer
allocations has

```text
Lmin = (1,1,2,2,2,2),
v({3,4,5,6}) = 6 < 8 = Lmin({3,4,5,6}).
```

Exactness follows immediately from the lower-envelope representation, and a
short four-inequality argument proves the displayed Lmin by hand.  Full paths,
proof, and reproduction commands are in
`paper3/N5_N6_SMALL_POORER_THRESHOLD.md`.

This discovery rules out the strongest dimension-free version of the
small-poorer conjecture, while identifying a new sharp five/six obstruction
threshold.  It also shows that the boundary-cover LP is a bound rather than a
universal zero-defect mechanism: many tight five-player suffixes do not admit
a zero-defect cover once the target suffix itself is excluded.

## 7. What would make this a larger theorem

The bridge becomes substantially broader if one can prove any of the
following without dimension enumeration:

1. a short human incidence/exact-balancedness proof of the five-player
   small-poorer lower bound, replacing its 16 symbolic queries;
2. a structural classification of minimal positive-defect patterns containing
   both the five-player equality (E5) and the six-player `2|4` construction;
3. a domain theorem showing that a broad established class (for example a
   nontrivial subclass of totally balanced or large-core games) always has
   zero-defect completions and is therefore exact partition;
4. a lift or converse construction realizing the six-player obstruction, and
   every irreducible positive slack budget, in a controlled infinite family.

Those would turn the present sharp finite theorem into a general theory of how
exact-balanced slack is transported across egalitarian payoff boundaries.

## Primary literature checked

- I. Arin and E. Iñarra (2001), *Egalitarian solutions in the core*.
- P. Csóka, P. J.-J. Herings, and L. Á. Kóczy (2011), *Balancedness
  conditions for exact games*, Mathematical Methods of Operations Research
  74, 41--52.
- E. Lohmann, P. Borm, and P. J.-J. Herings (2012), *Minimal exact
  balancedness*, Mathematical Social Sciences 64, 127--135.
- M. Studený and V. Kratochvíl (2022), *Facets of the cone of exact games*,
  Mathematical Methods of Operations Research 95, 35--80.
- M. Llerena and J. Mauri (2017), *On the existence of the Dutta--Ray's
  egalitarian solution*, Mathematical Social Sciences 89, 92--99.

The focused searches found no source explicitly linking egalitarian-core
transfer blockers to exact-balanced slack budgets.  This is not a definitive
MathSciNet/zbMATH novelty opinion.
