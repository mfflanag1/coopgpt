# Exact-balanced slack budgets and the four/five threshold

## Status

The principal results are now integrated into the manuscript theorem chain.
Every identity below has a short human proof.  The conceptual ingredients have
prior art:

- Arin--Iñarra (2001): the egalitarian-core transfer-blocking property used to
  obtain tight coalitions separating richer from poorer players;
- Csóka--Herings--Kóczy (2011): exact balancedness characterizes exact games;
- Lohmann--Borm--Herings (2012): the structure of minimal exact-balanced
  collections.

The candidate new contribution is the **protector-completion and
balanced-trace transport bridge** between these theories and its use to explain
the sharp Lmin thresholds.  No claim of novelty is made until the relevant
citation chains have been checked by an expert.

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

## 2.1 Dimension-free balanced-trace transport

The progressive Lmin duals yield more than individual protector coalitions.
At any strict payoff boundary, sum the individual-pinning duals within each
poorer payoff stratum.  The sum is regular on every later player and has a
unit deficit on every member of its own stratum.  Combining these stratum
covers backwards with successively large coefficients absorbs the finite,
unrestricted loads placed on earlier strata.  The result is a tight-coalition
cover with load one on every rich player and load strictly below one on every
poor player.

If the richer suffix `H` is slack, exactness supplies a core point `z` tight
on `H`.  Put `Delta=z-phi` and `s=phi(H)-v(H)`.  Then

```text
Delta(H)=-s,  Delta(L)=s.
```

Summing the tight cover inequalities at `z` shows that the poor displacement
has both signs.  Projecting the cover to its nonempty traces on `H` gives a
balanced collection.  Decompose it into normalized minimal balanced packets
and lift each packet back to deterministic original tight coalitions.  Every
lifted packet with poor load vector `r` satisfies

```text
-s + r dot Delta_L >= 0,
```

while the convex average of these carrier vectors is strictly below one in
every poor coordinate.  This is the dimension-free **balanced-trace transport
obstruction**: a slack Lmin suffix is possible only if a minimal balanced
rich-side circuit can transport its entire slack through opposing poor-side
gains and losses.  The theorem uses standard minimal balanced collections;
the claimed new content is their forced appearance as traces of Lmin dual
covers in exact games.

### Integral traces and odd-cycle necessity

Let `A_phi(H)` be the hypergraph of nonempty traces on `H` of proper
coalitions tight at `phi`, and let

```text
Q_phi(H) = {beta>=0 : sum_R beta_R 1_R = 1_H}.
```

If an exact `H`-face witness has at most one gaining poorer coordinate and
`Q_phi(H)` is integral, then `H` must be tight.  Decompose the strict cover
into integral exact covers, hence set partitions.  In each lifted partition
packet the load on the unique gaining poor player is an integer; the packet
transport inequality forces it to be at least one.  Averaging contradicts
strict undercoverage.

With exactly two poorer players, the opposing-sign conclusion makes the
unique-gainer hypothesis automatic.  Therefore every slack two-poorer
boundary has a nonintegral active trace polytope.  By Berge's classical
balanced-matrix theorem, its incidence matrix must contain an odd-order
square submatrix with exactly two ones in each row and column.  The full proof
is in `paper3/INTEGRAL_TRACE_OBSTRUCTION.md`.

Equivalently, trace-integral slack forces every exact suffix witness to have
at least two gaining and at least one losing poorer coordinate.  It therefore
requires at least three poorer players in every dimension.

The graph-like case can be eliminated completely. If every active trace on
`H` has size at most two, each extreme exact cover is a disjoint union of
singleton blocks, isolated edges, and half-weight odd cycles. A packet with
gaining-poor load below one must put that poor player on exactly one
half-weight cycle edge and put the losing poor player on none. Alternating
rounding of that odd cycle gives a tight-coalition combination with load
`1_H+e_d+e_b`. Exactifying the duplicated rich singleton `d` contradicts
efficiency because `phi_d>phi_a`. Therefore every two-poorer slack boundary
has a proper tight coalition whose rich trace has size at least three. This is
the dimension-free **rank-two trace exclusion** proved in
`paper3/RANK_TWO_TRACE_EXCLUSION.md`.

When `|H|=4`, one can go further. Up to relabeling, the four-row exact-cover
polytope has five fractional vertex types. Four have a safe root rounding:
their supported tight coalitions can be selected with rich load `1_H+e_d`,
zero-one poor loads, and at least one poor player loaded. Exactifying `d`
contradicts efficiency. The unique survivor is the co-singleton vertex with
weight `1/3` on each `H\{h}`. Hence every slack `2|4` boundary activates all
four co-singletons, exactly as in the sharp family. The human classification
is in `paper3/H4_FIRST_OBSTRUCTION_CLASSIFICATION.md`.

For the internal-sacrifice family, all co-singletons `H\{x}` are active
traces.  Weighting them by `1/(h-1)` gives a fractional exact cover; its
support matrix `J-I` is nonsingular, so the point is a fractional vertex.
Any
three selected player rows and corresponding co-singleton columns give

```text
0 1 1
1 0 1
1 1 0.
```

Thus the `2|3` versus `2|4` threshold is the first realizability transition
for an odd active-trace cycle: the three-rich triangle is killed by exact
singleton faces, while the co-singleton cycle survives from four rich players
onward.

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
same pair constraints give the closed formula

```text
Lmax_i = (m-1)/2          for i in {3,4,r},
Lmax_i = (m-1)/(2(m-2))  otherwise.
```

The formula is attained by the core point
`a*g4+(1-a)*g2`, where `a=(m-1)/(2(m-2))`; pair forcing followed by averaging
proves it is the unique Lmax.  Thus this is an Lmin--Lmax separation in every
dimension from five onward, matching the equality theorem through four.
The exact-balanced circuit

```text
1_{3r}+1_{4r}+sum_{i in P\{3,4}}1_i-1_r=1_N
```

has slack budget `0+0+(m-2)-(m-2)=0`.  The fourth poorer player supplies the
second uncovered unit that cannot exist at four players, and each additional
poorer player adds one unit to both sides.  This is the sacrifice-budget
explanation of both the sharp threshold and its persistence.  The complete
human proof and exact replay are in `paper3/N4_N5_STRUCTURAL_THRESHOLD.md`.

The same mechanism is not confined to a unique richest player.  For every
richest-block size `h>=1` and poorer-block size `m>=h+3`, an integral scaling
and uniform rich-block amplification of the four generators has

```text
Lmin = h on P and m-2 on R,       v(R)=0,
Lmax = h(m-1)/(h+1) on R union {3,4},
       h^2(m-1)/((h+1)(m-2)) elsewhere.
```

The proof uses the same two complement constraints, two rich-block
constraints, and one convex combination.  The exact distance is
`4h(m-h-2)/(h+1)`.  For fixed `h`, the normalized distance tends to
`2/(h+1)`.  In particular, the `h=1` family has normalized distance
`(m-3)/(m-1) -> 1`.  These games are indecomposable: a connected set of
positive pair worths contains the first five poorer/rich players, and explicit
higher-coalition interactions attach every additional poorer player.

This is the substantive asymptotic claim.  Null-player padding gives
dimensional existence but keeps the five-player normalized gap at `1/3`.
A direct sum of `h` five-player copies likewise gives `h` tied richest
players at normalized gap `1/3`; it can even beat the present family's
`2/(h+1)` limit for large `h`, but it is decomposable.  Accordingly the
rich-block axis is secondary, and no uniform separation claim is made as
`h -> infinity`.  The remaining novelty question is whether an
indecomposable exact family with the growing `h=1` separation is known.

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

The five-player lower bound now has a structural human proof.  Stagewise Lmin
duality produces a tight-coalition cover that is regular on the richer side
and strictly undercovers both poor players.  On at most three rich players,
minimal balanced traces are partitions plus the unique three-pair triangle.
An exact suffix witness eliminates the partitions; the forced triangle and an
exact rich-singleton witness then contradict efficiency.  The earlier 16
ordered-stratum queries remain an independent audit.  The six-player upper
bound is a fixed lower envelope of six common-total integer allocations with

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

The second escape mechanism is now also dimension-free.  For every `m>=2`
and `h>=4`, there is an integral exact game with `m` poorer players and `h`
tied richer players for which

```text
Lmin = Lmax = (D repeated m times, 2D repeated h times),
D=(h-2)(h-3),
v(H) = 2D(h-1) < 2Dh = Lmin(H).
```

Its saturated circuit is internal:

```text
1_{H\{4}} + 1_{4} - 1_H = 0.
```

The tight coalition `H\{4}` and the slack rich singleton fund the suffix
slack without using either poorer player.  This contrasts with the external
sacrifice circuit of the unique-richest/rich-block family.  It also proves
that exact partition at Lmin is not necessary for Lmin--Lmax equality.

The five-player external-sacrifice geometry admits a different universal
extension.  For every `m>=3,h>=2`, a common-total integral lower envelope has

```text
Lmin = 1 on m-1 poorer players, 2 on one poorer player, 3 on H,
v(H) = 3h-1 < 3h = Lmin(H).
```

It also has a closed-form distinct Lmax: with `epsilon=1/(h+1)`, the payoffs
are `2-epsilon` on the first poorer player, `epsilon` on the second,
`3-epsilon` on the intermediate poorer player and every rich player, and one
on every additional poorer player.  The exact L1 distance is `4h/(h+1)`.

The construction uses four base rows plus one row for each additional poorer
singleton.  Two rich-plus-poor faces successively pin the first two Lmin
levels, and efficiency equalizes the richer suffix.  The family is
indecomposable: a positive-pair bridge connects all players when `m>=4`, and
a strict higher-order interaction attaches the only pair-isolated player at
`m=3`.  Its full symbolic proof is in
`paper3/COMPLETE_BOUNDARY_SHAPE_CLASSIFICATION.md`.

Combining this family with the external unique-richest family, the internal
two-poorer family, and the two human impossibility arguments gives a complete
classification of arbitrary strict Lmin boundary cardinalities:

```text
m_min(h) = 4  for h=1,
m_min(h) = 3  for h=2 or h=3,
m_min(h) = 2  for h>=4.
```

Here `m_min(h)` is the minimum number of cumulative poorer players compatible
with a slack richer suffix of size `h`.  No two-stratum hypothesis is needed.
The excluded region follows from the opposing-sign transport condition, the
unique-richest packing theorem, and the two-poorer packet theorem.  Every
admitted pair is realized by one of the three explicit dimension-free
families.  Thus the original four/five threshold is the first corner of a
global boundary-cardinality phase transition, not an isolated finite fact.

The bridge becomes substantially broader if one can prove any of the
following without dimension enumeration:

1. a structural classification of minimal positive-defect patterns refining
   the now-complete cardinality phase diagram into circuit types;
2. a domain theorem showing that a broad established class (for example a
   nontrivial subclass of totally balanced or large-core games) always has
   zero-defect completions and is therefore exact partition;
3. a converse realization theorem for irreducible positive slack budgets,
   beyond the three universal families used in the phase diagram.

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
