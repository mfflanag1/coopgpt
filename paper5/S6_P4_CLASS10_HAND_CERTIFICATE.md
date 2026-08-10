# Class-10 two-order-split hand certificate

Date: 2026-08-10

## 1. Status and boundary

Packet class 10 has two labelled packets.  Its no-new-order relay stalls at
the root, but the exhaustive regions

```text
W_L: x_3<=x_4 and x_1<=x_2,
W_R: x_3<=x_4 and x_1>x_2,
S:   x_3>x_4
```

close in one, four, and four leaves.  The exact proof object and solver-free
checker make this a complete hand-checkable finite packet lemma.  They do not
validate the parent theorem's human-to-machine interface and are not
independent evidence for literature novelty.

## 2. Packet sandwich

Here the packet coalitions are

```text
P4={1,2,4},        P5={1,2,5}.
```

Write `d_i=x_i-z_i` for `i=0,1,2,3` and
`delta_m=z_m-x_m` for `m=4,5`.  The two opposite comparisons, their
complements, and efficiency give

```text
d_1+d_2 <= delta_4 <= d_0+d_3,
d_1+d_2 <= delta_5 <= d_0+d_3.                  (10.1)
```

Thus the packet cone has only five free difference coordinates after
eliminating `delta_5`.  Exact Fourier--Motzkin elimination recomputes every
candidate list below directly from (10.1), positivity, and the blockers
already selected on the branch.

## 3. Nine-leaf relay

Set

```text
C0={3,4}, C5={3,5}, C3={1,3}, C2={0,1,3},
D4={1,2,3,4},      D5={1,2,3,5}.
```

On `W_L`, Lmax exchange `e_0+e_2-e_4-e_5` has the unique blocker `C0`;
then Lmin exchange `-e_1-e_3+e_4+e_5` has no blocker.

On `W_R`, the same Lmax exchange has blockers `C0` and `C5`.  Either forces
Lmax exchange `-e_1+e_2`, whose blockers are exactly `C3` and `C2`.
The terminal Lmin exchange `-e_1+e_2` then has no blocker.

On `S`, Lmin exchange `-e_1-e_3+e_4+e_5` has blockers `D4` and `D5`.
They force `e_0+e_2-e_4-e_5`, with the respective unique blockers `C5`
and `C0`.  The same two-step `-e_1+e_2` Lmax/Lmin relay then closes both
children.  This is the complete nine-leaf tree frozen by the independent
order-split audit.

## 4. Exact structural census

There are eighteen distinct relay stages.  Before applying the `q^1`
comparison, their exact difference-cone candidate counts are

| motif | stages | candidates per stage |
|---|---:|---|
| weak roots | 2 | 4 |
| weak-left terminal | 1 | 2 |
| weak-right middle | 2 | 9 |
| weak-right terminals | 4 | 9 |
| strict root | 1 | 4 |
| strict second level | 2 | 2 |
| strict middle | 2 | 8 |
| strict terminals | 4 | 8 |

The frozen audit records every coalition, not only these counts.  Removing
any recorded candidate from the expected table is rejected by a mutation
control.

## 5. Certificate compression and source localization

The exhaustive relay requires 105 blocker exclusions and seventeen
activation checks.  Exact duplicate rows reduce these to

```text
95 blocker identities + 13 activation identities = 108 identities.
```

All 122 uses are mapped explicitly to a stage, and each affine premise is
rebuilt at that use site.  Of the 105 blocker uses, 103 are excluded using
the `q^1` comparison alone.  Only two `W_L` cuts use the opposite-allocation
comparison alone: `{3,5}` at the root and `{1,2,3,5}` at the terminal leaf.
No row needs both sources.

Every one of the nine terminal leaves closes directly at `D<=1/3`; class 10
does not need the auxiliary `x_1=1/3` anchor used for class 9.  Of all 122
uses, 116 target `D-1/3`.  Six strict-branch exclusions target `d_0`, which
is strictly positive by the original P-sign premise.

## 6. Reproduction and review boundary

Run from the repository root:

```bash
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class10_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class10_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class10_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class10_hand_certificate_audit.json
```

The checker uses pure `Fraction` arithmetic and exact Fourier--Motzkin
elimination.  It imports no solver and no production encoder.  It rejects
coefficient, use-site, candidate-deletion, use-map-deletion, and
strict-target mutations.

External review should still rederive (10.1), the eighteen candidate sets,
all activation-negation orientations, and the deduction from the displayed
relay to the encoded blocker alternatives.  A `PASS` result alone is not a
substitute for that human audit.
