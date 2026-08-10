# Class-9 order-split hand-proof checkpoint

Date: 2026-08-10

## 1. Status and boundary

Packet class 9 is no longer an unstructured UNSAT row.  Its four labelled
packets close after the single exhaustive split

```text
x_3 <= x_4        or        x_3 > x_4.
```

The frozen machine relay has five leaves and depth at most three.  The
structural reduction is now paired with a frozen, deduplicated exact proof
object and a solver-free verifier that imports no production encoder.  In the
same finite-certificate sense as the class-4, class-7, and class-11 lemmas,
this is a complete hand-checkable proof of the class-9 row.  It remains a
finite packet lemma and does not independently validate the parent theorem's
human-to-machine interface.

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

There is an exact `D-1/3` identity for the negation `x_1<=1/3` in each
profile.  The four profile uses reduce to two distinct identities: one for
the weak branch and one shared by all three strict-branch profiles.
Conversely, combining a hypothetical terminal `q(C)>=x(C)` with
the packet and branch comparisons gives

```text
x_1 <= 1/3.                                          (9.7)
```

for every opposite-source candidate in the table.  The 33 candidate-stage
instances of (9.7) reduce to 27 distinct rational identities.  Thus the
terminal closure is an anchor-threshold contradiction, not 33 unrelated
UNSAT leaves.

## 6. Exact-certificate audit

An independently assembled affine system found and exactified the raw rows.
They are now frozen as a proof object containing:

- 56 blocker-filter uses, reducing to 43 distinct identities: 33 uses target
  `x_1-1/3`, twenty target `D-1/3`, and three strict-sign contradictions
  target `d_0`;
- eleven activation uses, reducing to seven distinct identities;
- four branch-anchor uses proving (9.6), reducing to two identities.

`verify_strict_exchange_p4_class9_hand_certificates.py` reconstructs each
affine premise afresh at every use site and checks every weighted sum with
pure `Fraction` arithmetic.  It also recomputes all ten difference-cone
candidate sets by exact Fourier--Motzkin elimination, checks the exhaustive
use map, and rejects mutations of a coefficient, a use site, a candidate set,
the use map, and the strict-target declaration.  Thus deduplication cannot
silently reuse a row where one of its premises is unavailable.

## 7. Proof boundary and reproduction

Run from the repository root:

```bash
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class9_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class9_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class9_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class9_hand_certificate_audit.json
```

The verifier and its frozen rows are independently formulated only relative
to the class-9 packet inequalities and relay premises displayed above.  They
do not prove that every genuine counterexample satisfies the parent encoded
relaxation.  The authoritative theorem evidence remains the parent CPC proof,
and external review of that semantic interface remains the highest-priority
independent gate.
