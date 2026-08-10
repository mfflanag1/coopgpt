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

All three arguments use a short core segment.  A segment between two core
points remains in the core.

**No unique Lmax top (`a21`).**  Suppose `i` were the unique maximum of `z`.
Then `z_i>0`, since the six nonnegative coordinates sum to one.  Along the
segment from `z` to `q^i`, coordinate `i` decreases toward zero.  For a small
positive step it remains separated from every old lower coordinate, so the
first entry of the decreasing rearrangement falls.  This contradicts the
leximax-minimality of `z`.  Therefore at least two coordinates share the
maximum.  The production formula writes this as a disjunction over tied top
pairs; the independent bound-two encoder writes the logically equivalent
negation of a unique top.

**Lmax-top cross anchor (`a22`).**  If every player in the top stratum of `z`
satisfied `x_i<z_i`, then a short segment from `z` toward `x` would decrease
every old top coordinate.  Before any lower stratum could cross it, the first
entry of the decreasing rearrangement would fall.  Hence some `z`-top player
has `x_i>=z_i`.

**Lmin-bottom cross anchor (`a23`).**  Dually, if every player in the bottom
stratum of `x` satisfied `z_i>x_i`, a short segment from `x` toward `z` would
increase every old bottom coordinate before a higher stratum could cross it.
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
choose a common positive `epsilon` smaller than all ratios

```text
(y(S)-v(S))/(-h(S)).
```

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

## 7. Exhaustion and soundness conclusion

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

## 8. What an external reviewer can still falsify

A fatal objection must identify one of the following:

1. a false anchor in Section 3, including a tied-stratum or boundary failure;
2. a retained direction accepted by the machine test that does not produce a
   genuine sorted-lexicographic improvement;
3. a missing constraint in the short-step argument of Section 6;
4. a reversed inequality in (Bx) or (Bz);
5. a coalition with `h(S)<0` omitted from a machine disjunction; or
6. an assertion in a frozen formula not accounted for above.

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
