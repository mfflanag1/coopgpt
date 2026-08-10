# Human-to-machine soundness proof for the six-player strict bound

Date: 2026-08-10

This note isolates the only implication that the CPC proofs do not check:

```text
genuine exact-game counterexample
        ==> a satisfying assignment of one frozen strict SMT formula.
```

The implication is proved below assertion family by assertion family.  It is
deliberately one-way.  The SMT assignment need not define a game, its witness
vectors need not satisfy a common set of core inequalities, and the coalition
chosen for one exchange need not be chosen for another.  Those omissions
weaken the machine system.  Therefore UNSAT of the weakened system is enough.

## 1. Mathematical input

Let `v` be a singleton-normalized exact game on `N={0,...,5}` with `v(N)>0`.
Write

```text
x = Lmin(v),     z = Lmax(v),     T = v(N).
```

Scale the game and every allocation by `1/T`.  The core is then contained in
the efficiency hyperplane `y(N)=1`.  Singleton normalization and the singleton
core inequalities give `y_i>=v({i})=0` for every core allocation.

Exactness says that for every coalition `S` there is a core allocation that
attains `v(S)`.  Only the six singleton instances are used: choose `q^i` in
the core with

```text
q^i_i = v({i}) = 0.                                      (W)
```

Thus each of `x,z,q^0,...,q^5` is nonnegative and efficient.  No other
coordinate or coalition relation on a witness is placed directly in the SMT
formula.

## 2. Relabeling and the first 21 assertions

Put

```text
P={i:x_i>z_i},   M={i:z_i>x_i},   E={i:x_i=z_i}.
```

If `x!=z`, efficiency makes `P` and `M` nonempty.  Hence the cardinalities
`(p,m,e)` are one of the fifteen triples with `p,m>=1` and `p+m+e=6`.
Relabel players so that `P`, then `M`, then `E` occupy consecutive indices.
Relabeling a game permutes its core; because both sorted lexicographic
objectives are anonymous, it also permutes `Lmin` and `Lmax`.  Nothing is lost
by this canonical labeling.

Equal totals imply

```text
||x-z||_1 = 2 sum_{i in P}(x_i-z_i).                    (D)
```

Consequently a counterexample to the upper bound satisfies the strict
distance assertion.  In every frozen formula this material is exactly:

| assertions | mathematical content |
|---|---|
| `a0-a1` | `x(N)=z(N)=1` |
| `a2-a13` | nonnegativity of `x,z` |
| `a14-a19` | the six strict/equality signs defining `P,M,E` |
| `a20` | the right side of (D) is strictly greater than `2/3` |

Strictness is important: the formulas prove exclusion of distance `>2/3`;
the explicit family supplies attainment separately.

## 3. The three selection anchors (`a21-a23`)

All three arguments use a core segment.  A segment between two core points
remains in the core.  To remove the informal phrase “small step,” use the
order-crossing radius `Delta(y,h)` defined in Section 5 and choose

```text
0 < epsilon < min{1,Delta(y,h)}.                         (E0)
```

The direction in each argument is the endpoint difference.  Formula (E0)
keeps the point on the core segment and preserves every strict order between
distinct old payoff strata.  It is positive because `Delta` is either
strictly positive or `+infinity`.

**No unique Lmax top (`a21`).**  Suppose `i` were the unique maximum of `z`.
Then `z_i>0`, since the six nonnegative coordinates sum to one.  Along the
segment from `z` to `q^i`, use `h=q^i-z`.  At the unique top level,
`h_i=-z_i<0`; there is no other coordinate in that level.  Formula (E0) and
the Lmax half of the order-preservation lemma therefore make the first entry
of the decreasing rearrangement fall.  This contradicts the
leximax-minimality of `z`.  Therefore at least two coordinates share the
maximum.  The production formula writes this as a disjunction over tied top
pairs; the independent bound-two encoder writes the logically equivalent
negation of a unique top.

**Lmax-top cross anchor (`a22`).**  If every player in the top stratum of `z`
satisfied `x_i<z_i`, then a short segment from `z` toward `x` would decrease
every old top coordinate.  More explicitly, put `h=x-z` and use (E0).  Every
coefficient at the highest affected old level is negative, so the Lmax
criterion makes the decreasing rearrangement lexicographically smaller.
Hence some `z`-top player has `x_i>=z_i`.

**Lmin-bottom cross anchor (`a23`).**  Dually, if every player in the bottom
stratum of `x` satisfied `z_i>x_i`, a short segment from `x` toward `z` would
increase every old bottom coordinate.  With `h=z-x` and (E0), every
coefficient at the lowest affected old level is positive, so the Lmin
criterion makes the increasing rearrangement lexicographically larger.
Hence some `x`-bottom player has `z_i<=x_i`.

These proofs allow tied strata and zero boundary coordinates.  The only place
strict positivity is needed is the allegedly unique top coordinate, where it
follows from nonnegativity and efficiency.

## 4. Singleton witnesses (`a24-a71`)

For each `i`, the eight assertions in the block beginning at `a(24+8i)` say:

```text
q^i(N)=1,     q^i_i=0,     q^i_j>=0 for every j.
```

The actual exactness witness (W) satisfies this block.  The machine does not
assert that `q^i` lies in a common core.  Its only later use is through
inequalities that every actual core witness must satisfy.  This is a genuine
relaxation, not an omitted premise in the soundness direction.

## 5. Infinitesimal lexicographic improvement

Let `h` be a retained integer direction with `h(N)=0`.

The following elementary lemma makes every use of “sufficiently small” in
this note finite and explicit.

**Order-preservation lemma.**  For a point `y` and a direction `h`, put

```text
Delta(y,h) = min {(y_j-y_i)/(h_i-h_j):
                  y_i<y_j and h_i>h_j},
```

with the minimum of the empty set interpreted as `+infinity`.  Every
`0<epsilon<Delta(y,h)` preserves every strict order between distinct old
payoff strata:

```text
y_i<y_j  ==>  y_i+epsilon h_i < y_j+epsilon h_j.
```

Indeed, only a pair with `h_i>h_j` can close its old positive gap, and the
displayed ratio is exactly its crossing time.  There are finitely many pairs,
so `Delta(y,h)>0` whenever it is finite.

Now let `alpha` be the lowest old payoff level containing a nonzero entry of
`h`.  If every player at level `alpha` has `h_i>=0` and at least one has
`h_i>0`, then for every `0<epsilon<Delta(y,h)` the increasing rearrangement
of `y+epsilon h` agrees with that of `y` below the `alpha` block; inside that
block, its initial zero-direction entries agree and its next entry strictly
increases.  It is therefore lexicographically larger.  This proves the Lmin
criterion.  Taking the highest affected level, reversing all inequalities,
and requiring one negative and no positive coefficient proves the Lmax
criterion.  The conclusion does not depend on coefficients being unit-sized.

For Lmin, call `h` admissible at `x` when the lowest payoff level touched by
`h` has no negative coefficient and has at least one positive coefficient.
Equivalently, there is a positive pivot `r` such that every affected player
has `x_j>=x_r` and every negative-coefficient player has `x_j>x_r`.
For a sufficiently small positive `epsilon`, no adjacent payoff strata cross;
the first changed block in the increasing rearrangement is therefore the
old level of `r`, where at least one coordinate rises and none falls.  Thus
`x+epsilon h` is lexicographically better.

For Lmax the order dual is used: there is a negative pivot at the highest
affected level, every affected player is weakly below it, and every positive-
coefficient player is strictly below it.  The first changed block in the
decreasing rearrangement falls.

These are sufficient tests, not a claim to recognize every improving
direction.  The production pivot predicate and a separately written
first-affected-level predicate agree on all 4,683 labeled weak orders, all
1,610 efficiency-preserving bound-two directions, and both sides: 15,079,260
comparisons with no mismatch.  The two coefficient-two cases are also rebuilt
by an encoder that writes the first-affected-level test directly.

## 6. Tight-blocker lemma and each implication after `a72`

Write the normalized core as

```text
C(v)={y:y(N)=1 and y(S)>=v(S) for every proper S}.
```

Suppose `h` passes the relevant sufficient improvement test at a selected
point `y`.  If every coalition tight at `y` had `h(S)>=0`, then all tight
inequalities would remain satisfied along `y+epsilon h`.  There are finitely
many nontight coalitions.  Each with `h(S)<0` has positive slack, so one can
define the single radius

```text
epsilon_* = min({1,Delta(y,h)} union
                {(y(S)-v(S))/(-h(S)):
                 S proper, y(S)>v(S), h(S)<0}).          (E1)
```

The ratio set may be empty, but the set in (E1) always contains `1`; every
other finite member is strictly positive, so `epsilon_*>0`.  Choose
`0<epsilon<epsilon_*`.  Coalitions with `h(S)>=0` cannot become violated,
tight coalitions are safe by the supposition, and the slack ratios protect all
remaining coalitions.  The same epsilon lies below `Delta(y,h)`, so it also
preserves the payoff-stratum order needed for lex improvement.  Thus one
explicit positive radius handles both requirements.

Efficiency is preserved because `h(N)=0`.  Singleton nonnegativity is already
among the coalition inequalities because `v({i})=0`.  Hence a short improving
step would remain in the core, contradicting selection optimality.  Therefore
there is a nonempty proper coalition `S` such that

```text
y(S)=v(S),     h(S)<0.                                  (B)
```

If `y=x`, core membership of `z` and every `q^i` gives

```text
z(S)>=x(S),     q^i(S)>=x(S) for i=0,...,5.             (Bx)
```

If `y=z`, it gives

```text
x(S)>=z(S),     q^i(S)>=z(S) for i=0,...,5.             (Bz)
```

For each retained direction, the SMT consequent is the disjunction of (Bx)
or (Bz) over **every** nonempty proper coalition with `h(S)<0`.  The genuine
tight coalition from (B) is one of those alternatives.  Thus every actual
counterexample satisfies every retained implication.

The consequent does not assert tightness, does not introduce `v(S)`, and may
choose a different coalition independently for each direction.  Each change
only enlarges the machine-feasible set.  It cannot create a false UNSAT proof.

## 7. Two coefficient-two implication rows without SMT syntax

These examples expose the complete mathematical content of one retained row
in each bound-two sign case.  They are not representative spot checks used to
infer the other rows; the semantic audit reconstructs every row.  Their
purpose is to make the external review start from coalition arithmetic.

### Case `(p,m,e)=(2,3,1)`, assertion `a72`

Here `P={0,1}`, `M={2,3,4}`, `E={5}` and the Lmin direction is

```text
h=(-2,-1,1,1,1,0).
```

Its activation condition is exactly

```text
min(x_2,x_3,x_4) < min(x_0,x_1).                      (A231)
```

Indeed, the lowest affected level then contains a positive recipient and no
negative donor, and the converse is immediate.  Write
`R=S intersect {2,3,4}`.  The complete set of negative proper cuts is

```text
S intersect {0,1} = {1}:    |R|=0;
S intersect {0,1} = {0}:    |R|=0 or 1;
S intersect {0,1} = {0,1}:  |R|=0, 1, or 2,
```

with player 5 independently absent or present.  Thus there are
`2 + 8 + 14 = 24` alternatives, and no others, because these conditions are
just `h(S)=-2 1[0 in S]-1[1 in S]+|R|<0`.

For each of these 24 coalitions the consequent has exactly the seven
comparisons

```text
z(S)>=x(S),   q^0(S)>=x(S), ..., q^5(S)>=x(S).         (B231)
```

Therefore `a72` says `(A231) ==> OR_S (B231)`, with `S` ranging over precisely
the displayed family.

### Case `(p,m,e)=(3,3,0)`, assertion `a74`

Here `P={0,1,2}`, `M={3,4,5}` and consider the Lmin direction

```text
h=(-2,0,-2,1,1,2).
```

Its activation condition is

```text
min(x_3,x_4,x_5) < min(x_0,x_2).                      (A330)
```

Player 1 is unaffected.  Let `D=S intersect {0,2}` and let

```text
w(S)=1[3 in S]+1[4 in S]+2 1[5 in S].
```

The negative-cut condition is exactly `w(S)<2|D|`.  Hence `D` must be
nonempty.  If `|D|=1`, then `w(S)<2`, giving three recipient subsets; there
are two choices of donor and two independent choices for player 1, for 12
cuts.  If `|D|=2`, every recipient subset except `{3,4,5}` has weight below
four; with player 1 optional this gives 14 cuts.  These 26 coalitions are the
complete negative-cut family.

For each such `S`, the consequent is

```text
z(S)>=x(S),   q^0(S)>=x(S), ..., q^5(S)>=x(S).         (B330)
```

Thus `a74` is `(A330) ==> OR_S (B330)` over exactly those 26 cuts.  The
coefficient two affects which coalitions are negative, but not the
first-affected-level proof of lexicographic improvement.

An external reviewer can now check both examples by comparing the displayed
cut parametrizations with the corresponding rows of
`strict_exchange_formula_interface.json`; no solver result is needed.

## 8. Exhaustion and soundness conclusion

Given a genuine strict counterexample:

1. normalize it;
2. relabel it into its unique sign-count case;
3. assign the actual `x,z` and six actual singleton exactness witnesses;
4. satisfy `a0-a71` by Sections 1--4; and
5. for every implication whose antecedent fires, use Section 6 to select its
   genuine negative tight blocker.

This constructs a satisfying assignment of the corresponding frozen formula.
Since all fifteen formulas are UNSAT, no genuine counterexample exists.

The literal formula audit confirms that this list is exhaustive: each frozen
formula declares exactly 48 reals (`x,z,q^0,...,q^5`), contains exactly 72
base assertions in the ranges above, and then contains exactly its recorded
retained implications.  There are no game-value variables and no hidden
premises.  Run:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py \
  --output /tmp/strict_exchange_formula_interface.json
cmp /tmp/strict_exchange_formula_interface.json \
  coopgames/verifiers/s6/strict_exchange_formula_interface.json
```

The JSON maps each direction implication to its assertion label, direction,
side, negative-proper-cut count, and seven comparisons per cut.

The layout audit alone does not establish that an assertion with the right
outer shape has the right semantics.  A second script therefore reconstructs
every frozen assertion independently and tests logical equivalence one row at
a time:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_semantic_interface.py \
  --output /tmp/strict_exchange_semantic_interface.json
cmp /tmp/strict_exchange_semantic_interface.json \
  coopgames/verifiers/s6/strict_exchange_semantic_interface.json
```

This reconstruction imports no production encoder, lex predicate, blocker
builder, direction generator, minimizer, exporter, or serializer.  It treats
only the retained menus as theorem data.  It writes the no-unique-top anchor
as the negation of a unique maximum, writes lex improvement by the direct
first-affected-payoff-level criterion, and rebuilds every blocker by iterating
all nonempty proper subsets with negative direction sum.  Across the fifteen
formulas it checks semantic equivalence of all `1,080` base assertions and all
`252` direction implications.  The latter independently reconstruct `4,722`
negative-cut alternatives and `33,054` individual blocker comparisons.  Every
one of the `1,332` local equivalence queries is UNSAT.

This is materially stronger than checking assertion counts or rerunning the
theorem formulas.  It would detect a reversed comparison, a missing negative
cut, a wrong sign case, a changed distance normalization, or a production lex
predicate that differs from the first-affected-level statement.  It still
does not prove the human claims that the three anchors are necessary, that the
first-affected test is genuinely lex-improving, or that optimality supplies a
negative tight blocker.  Those remain the external reviewer's load-bearing
mathematical tasks.

## 9. What an external reviewer can still falsify

A fatal objection must identify one of the following:

1. a false anchor in Section 3, including a tied-stratum or boundary failure;
2. a retained direction accepted by the machine test that does not produce a
   genuine sorted-lexicographic improvement;
3. a missing constraint in the short-step argument of Section 6;
4. a reversed inequality in (Bx) or (Bz);
5. a coalition with `h(S)<0` omitted from a machine disjunction; or
6. an assertion in a frozen formula not accounted for above.

For item 2, it is enough to check the order-preservation lemma and then check
that each encoded pivot predicate is the displayed lowest/highest-affected-
level condition.  For item 3, it is enough to check the finite minimum of
`Delta(y,h)` and the nontight-coalition slack ratios.  These reductions do not
replace review, but they localize the two previously informal epsilon choices
to explicit positive quantities.

Solver reruns do not answer these questions.  The appropriate review is to
prove or refute Sections 2--6 and then inspect several full implication rows,
especially in `(2,3,1)` and `(3,3,0)`, against the assertion manifest.

The separately certified 19-orbit large-case formulas are intentionally
weaker than this uniform map: they delete `a21`, the no-unique-Lmax-top
anchor, and retain only the two cross anchors.  This does not affect the
soundness implication because every genuine counterexample satisfies the
weaker premise list.  Their single-cross-anchor ablations are SAT, so both
remaining cross anchors are load-bearing within that reduced relaxation.
The `(4,2,0)` orbit formula is weaker once more: in each negative-cut
alternative it keeps the opposite-selection comparison and the four
singleton-witness comparisons indexed by `P`, but drops the two indexed by
`M`.  Every genuine counterexample satisfies the retained comparisons, so
this deletion preserves the one-way map.  The six witness variable blocks and
their base simplex/zero constraints remain in the formula.  Removing any one
of the five retained comparison-source families makes this reduced
relaxation SAT; that is an internal irredundancy control, not a claim that the
omitted witnesses are unnecessary in the general blocker lemma.

The separate anchor-localized `(4,2,0)` formula weakens this interface much
further.  The two cross anchors choose an `x`-bottom `a in P` and a `z`-top
`b in P`.  If `a=b`, then any `m in M` gives
`x_m>=x_a>z_a>=z_m>x_m`; hence only the distinct branch exists.  Relabel it
as `a=0,b=1`.  The frozen localized formula replaces both anchor disjunctions
by these extreme-role inequalities, retains only the actual exactness witness
`q^b`, and keeps only the opposite and `q^b` comparisons in every blocker
alternative.  A real counterexample satisfies all of those weaker assertions.
The formula has 18 reals, 39 base assertions, and nineteen direction
implications in ten residual orbits.  Its complete assertion-level account is
`S6_P4_ANCHOR_LOCALIZATION.md`.
