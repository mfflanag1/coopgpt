# Class-9 order-split hand-proof checkpoint

Date: 2026-08-10

## 1. Status and boundary

Packet class 9 is no longer an unstructured UNSAT row.  Its four labelled
packets close after the single exhaustive split

```text
x_3 <= x_4        or        x_3 > x_4.
```

The frozen machine relay has five leaves and depth at most three.  This note
records the structural reduction and the exact-certificate discovery
checkpoint.  It is **not yet a complete hand proof**: the discovered
coefficients still need to be deduplicated, frozen in a source table, and
checked by a solver-free verifier that imports no production encoder.

## 2. Packet inequalities

Here `A={0,2}`, `B={2}`, so the two packet coalitions are

```text
P4={0,1,2,4},       P5={1,2,5}.
```

Write `d_i=x_i-z_i` for `i=0,1,2,3` and
`delta_m=z_m-x_m` for `m=4,5`.  The opposite comparisons and their
complements are

```text
d_0+d_1+d_2 <= delta_4 <= d_0+d_3,
d_1+d_2     <= delta_5 <= d_3.                     (9.1)
```

Thus `d_3>=d_1+d_2`.  The two `q=q^1` comparisons are

```text
q_0+q_2+q_4 >= x_0+x_1+x_2+x_4,
q_2+q_5     >= x_1+x_2+x_5.                       (9.2)
```

Their complementary forms are retained separately; collapsing them into an
aggregate inequality loses blocker membership information.

## 3. Five-leaf relay

Use the branch names

```text
C0={3,4},       C1={1,2,3,4},
C2={0,1,3},     C3={1,3}.                          (9.3)
```

On the weak order branch `W: x_3<=x_4`, the forced relay is

```text
Lmax  e_0-e_1+e_2-e_4
  C0 -> Lmin -e_1-e_3+e_4+e_5 -> contradiction,
  C1 -> Lmax -e_1+e_2
          C2 -> Lmin -e_1+e_2 -> contradiction.    (9.4)
```

On the strict order branch `S: x_3>x_4`, the relay is

```text
Lmin -e_1-e_3+e_4+e_5
  C1 -> Lmax e_0-e_1+e_2-e_4
          C3 -> Lmin -e_1+e_2 -> contradiction,
          C1 -> Lmax -e_1+e_2
                  C3 or C2 -> Lmin -e_1+e_2
                                  -> contradiction. (9.5)
```

The root activation in (9.5) is immediate from `x_3>x_4` and
`x_1>x_4,x_5`.  Every other activation has an exact weighted identity whose
negation forces `D<=1/3`.

## 4. Exact difference-cone censuses

Eliminate `delta_5` using efficiency.  Positivity, (9.1), and the branch's
opposite comparisons give the following complete candidate sets before the
`q` source is applied:

| stage | eligible cuts | opposite-source candidates |
|---|---:|---|
| `W` root | 20 | `{1}`, `{1,3}`, `C0`, `{1,3,4}`, `{1,3,5}`, `{0,1,3,4}`, `C1` |
| `W,C0` terminal | 20 | none |
| `W,C1` | 16 | `{1}`, `{0,1}`, `{1,3}`, `C2`, `{0,1,5}`, `{1,3,4}`, `{1,3,5}`, `{0,1,3,4}`, `{0,1,3,5}` |
| `W,C1,C2` terminal | 16 | `{1,4}`, `{1,5}`, `{0,1,4}`, `{0,1,5}`, `{1,3,4}`, `{1,4,5}`, `{0,1,4,5}`, `{1,3,4,5}`, `{0,1,3,4,5}` |
| `S` root | 20 | `{1,3,4}`, `C1` |
| `S,C1` | 20 | `{1}`, `C3`, `{1,3,5}`, `{0,1,3,4}`, `C1` |
| `S,C1,C3` terminal | 16 | `{1,4}`, `{1,5}`, `{0,1,4}`, `{1,3,4}`, `{1,4,5}`, `{0,1,4,5}`, `{1,3,4,5}`, `{0,1,3,4,5}` |
| `S,C1,C1` | 16 | `{1}`, `{0,1}`, `C3`, `C2`, `{0,1,5}`, `{1,3,5}`, `{0,1,3,4}`, `{0,1,3,5}` |
| either long strict terminal | 16 | the same eight terminal candidates as `S,C1,C3` |

Direct exact rational cone feasibility reproduces the table.  After the
`q` comparison is imposed, the survivors are exactly those displayed in
(9.4)--(9.5).  There are 56 candidate-stage exclusions, but only 43 distinct
weighted identities after identical rows are shared across stages.

## 5. Terminal anchor lemma

The terminal leaves admit a common conceptual explanation.  Every terminal
direction is the Lmin exchange `-e_1+e_2`; hence every negative cut contains
player 1 and excludes player 2.  For each of the four terminal branch profiles,
the branch comparisons imply

```text
x_1 > 1/3.                                           (9.6)
```

There is one exact `D-1/3` identity for the negation `x_1<=1/3` in each
profile.  Conversely, combining a hypothetical terminal `q(C)>=x(C)` with
the packet and branch comparisons gives

```text
x_1 <= 1/3.                                          (9.7)
```

for every opposite-source candidate in the table.  The 33 candidate-stage
instances of (9.7) reduce to 27 distinct rational identities.  Thus the
terminal closure is an anchor-threshold contradiction, not 33 unrelated
UNSAT leaves.

## 6. Exact-certificate discovery audit

An independently assembled affine system found and exactified:

- 56 blocker-filter rows: 33 target `x_1-1/3`, 20 target `D-1/3`, and three
  strict-sign contradictions targeting `d_0`;
- eleven activation rows, reducing to seven distinct identities;
- four branch-anchor rows proving (9.6).

Every numerical LP output was rationalized and then rejected unless its
weighted affine sum was literally equal, coefficient by coefficient, to the
claimed target.  This is discovery evidence only: it does not replace the
pending source-table audit, nonnegative-multiplier check, exhaustive-use map,
mutation controls, or external review.

## 7. Next exact checkpoint

1. Freeze the 43 distinct blocker identities, seven activation identities,
   and four anchor identities with an explicit use map for all 56 exclusions
   and eleven activations.
2. Implement a pure-`Fraction` verifier with an exact Fourier--Motzkin
   reconstruction of every difference-cone row.
3. Add coefficient, use-map, strict-target, and candidate-deletion mutation
   controls.
4. Only after those checks pass, promote class 9 to a sixth
   hand-checkable packet lemma and update the manuscript counts.

Until then, the authoritative theorem evidence remains the parent CPC proof;
the class-9 order tree and this note are explanatory reductions.
