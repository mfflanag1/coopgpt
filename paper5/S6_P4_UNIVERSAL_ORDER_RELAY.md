# Universal payoff-order relay for all eleven P4 packet classes

Date: 2026-08-10

## Result

Every one of the eleven exact blocker-packet classes closes under the same
root payoff-order split

```text
x_3 <= x_4        or        x_3 > x_4.             (U.1)
```

Ten classes then close under the ordinary forced-exchange relay rule.  On the
weak branch of class 10 alone, one additional exhaustive split is needed:

```text
x_1 <= x_2        or        x_1 > x_2.             (U.2)
```

Thus all 32 feasible labelled packets have finite order-refined relay trees.
This removes the previous distinction between five complete no-new-order
trees and six classes with open leaves: those leaves reflected unresolved
payoff order, not a different blocker mechanism.

## Exact machine anatomy

| class | orbit | weak `x3<=x4` | strict `x3>x4` | extra split |
|---:|---:|---:|---:|---|
| 1 | 1 | 7 leaves, depth 1 | 8 leaves, depth 2 | none |
| 2 | 2 | 1 leaf, depth 1 | 10 leaves, depth 4 | none |
| 3 | 4 | linearly infeasible | 2 leaves, depth 1 | none |
| 4 | 4 | linearly infeasible | 3 leaves, depth 1 | none |
| 5 | 1 | 19 leaves, depth 4 | 32 leaves, depth 5 | none |
| 6 | 4 | 22 leaves, depth 3 | 7 leaves, depth 4 | none |
| 7 | 4 | linearly infeasible | 4 leaves, depth 3 | none |
| 8 | 2 | 1 leaf, depth 0 | 1 leaf, depth 0 | none |
| 9 | 4 | 2 leaves, depth 2 | 3 leaves, depth 3 | none |
| 10 | 2 | two closed and two open before (U.2) | 4 leaves, depth 3 | (U.2): 1 and 4 leaves |
| 11 | 4 | 1 leaf, depth 2 | 1 leaf, depth 2 | none |

Every order region used for classes 1, 2, 5, 6, 8, 9, 10, and 11 is SAT
before its relay implications are applied.  The weak regions of classes 3, 4,
and 7 are already linearly infeasible.  The class-10 weak region genuinely
retains two open leaves before (U.2), so the nested split is not cosmetic.

## Mathematical interpretation

The universal comparison `x_3` versus `x_4` is the missing order coordinate
for the entire packet table.  It is not merely a convenient split found
separately in classes 9 and 10: imposing it at the root closes classes 1, 2,
5, and 6 as well.  These four were exactly the classes whose ordinary relay
trees still had open leaves after classes 9 and 10 were humanized.

This is a meaningful structural compression of the finite `P4` lemma.  It
does **not** yet make all eleven rows hand-checkable.  Classes 1, 3, 4, 7, 8,
9, 10, and 11 have separate exact hand proof objects, covering 25 labelled
packets.  Classes 2, 5, and 6, covering the other seven, still rely on the
shared parent encoding for their order-refined relay trees.  Their trees are
now precise hand-proof targets rather than unexplained UNSAT residue.

## Reproduction and review boundary

Run with the Z3-enabled Python environment:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_universal_order_relays.py \
  --output /tmp/strict_exchange_p4_universal_order_relays.json
cmp /tmp/strict_exchange_p4_universal_order_relays.json \
  coopgames/verifiers/s6/strict_exchange_p4_universal_order_relays.json
```

The audit freezes every order region, chosen direction, blocker coalition,
closed leaf, and the unique nested exception.  It shares the parent packet
encoder and relay implementation.  External review should therefore treat it
as a structural decomposition and roadmap, not as independent evidence for
the theorem or for the human-to-machine implication.
