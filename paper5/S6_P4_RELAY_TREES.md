# Forced-exchange relay trees in the six-player `(4,2,0)` case

Date: 2026-08-10

## 1. What the relay audit asks

Fix one of the eleven exact blocker packets in
`S6_P4_PACKET_CLASSIFICATION.md` and its frozen subset-minimal residual core.
At a current branch:

1. test which unused core directions are forced lex-improving;
2. among them choose one with the fewest feasible blocker alternatives;
3. discard every blocker alternative inconsistent with the current branch;
4. branch on the remaining concrete blockers; and
5. close a leaf when a forced improving direction has no blocker.

If no unused direction is forced, the leaf is explicitly left open.  A closed
tree is therefore a finite explanation of the parent UNSAT formula: every
branch is a sequence of necessary optimality blockers, ending when optimality
cannot supply the next blocker.  It is not an independent proof object, and a
SAT or open branch is not an exact game.

## 2. Five complete relay classes

The deterministic audit gives the following anatomy.  `Closed/open` counts
terminal leaves; depth zero means the first forced direction has no blocker.

| class | packet orbit size | core directions | closed/open | maximum depth | complete relay | separate hand proof |
|---:|---:|---:|---:|---:|---|---|
| 1 | 1 | 4 | `2/6` | 1 | no | no |
| 2 | 2 | 6 | `6/3` | 4 | no | no |
| 3 | 4 | 2 | `2/0` | 1 | yes | yes |
| 4 | 4 | 3 | `3/0` | 1 | yes | no |
| 5 | 1 | 7 | `30/3` | 4 | no | no |
| 6 | 4 | 7 | `29/4` | 4 | no | no |
| 7 | 4 | 4 | `4/0` | 3 | yes | no |
| 8 | 2 | 1 | `1/0` | 0 | yes | yes |
| 9 | 4 | 4 | `0/1` | 0 | no | no |
| 10 | 2 | 4 | `0/1` | 0 | no | no |
| 11 | 4 | 3 | `1/0` | 2 | yes | no |

Thus classes `3,4,7,8,11` have complete forced relays.  Their orbit sizes sum
to eighteen of the 32 feasible labelled packets.  Classes 3 and 8, covering
six packets, have already been converted into the explicit hand inequalities
in `S6_P4_PACKET_CLASSIFICATION.md`.  The other twelve packets in the closed
relay set have machine-checked trees that now specify exactly which blocker
lemmas remain to be humanized.

## 3. Two especially small targets

### Class 4: a three-leaf star

The first forced direction is

```text
-e_1-e_3+e_4+e_5       (Lmin).
```

Only three of its twenty negative cuts survive:

```text
{1,2,3,4},   {1,3,5},   {0,1,3,5}.
```

The first blocker forces `e_2-e_1` to improve Lmax, with no feasible blocker.
Either of the other two forces `-e_2-e_3+e_4+e_5` to improve Lmin, again with
no feasible blocker.  The whole four-packet orbit is therefore a depth-one,
three-leaf relay.  Converting the three no-blocker leaves into displayed
inequalities is the highest-value next hand target.

### Class 11: a unique three-exchange chain

There is no branching:

```text
Lmax: -e_1+e_2+e_3-e_5
  unique blocker {0,1,2,5}
Lmax: -e_1+e_2
  unique blocker {0,1,3}
Lmin: -e_1+e_2
  no feasible blocker.
```

This chain covers four labelled packets.  It is longer than class 4 but has a
single terminal obligation and is the cleanest candidate for a named
max-to-min exchange-relay lemma.

Class 7 is also complete but has four leaves and depth three.  It should be
attempted after classes 4 and 11.

## 4. What remains unresolved

The relay method stalls immediately in classes 9 and 10 because none of the
directions in the chosen subset-minimal core is forced before an additional
order split.  Classes 1, 2, 5, and 6 have many closed branches but retain,
respectively, 6, 3, 3, and 4 open leaves.  These are precise structural
residues, not counterexamples.

The relay audit does not replace the trust-disabled CPC proof of the weaker
parent formula and does not validate the human-to-machine map.  Its purpose is
to turn the residual finite proof into a short list of concrete exchange and
blocker lemmas suitable for external review.

## 5. Reproduction

Run from the repository root with the Z3-enabled Python environment:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_relay_trees.py \
  --output /tmp/strict_exchange_p4_relay_trees.json
cmp /tmp/strict_exchange_p4_relay_trees.json \
  coopgames/verifiers/s6/strict_exchange_p4_relay_trees.json
```

The frozen JSON records every chosen direction, its side and role orbit, the
number of eligible negative cuts, every surviving blocker coalition, every
closed or open leaf, and the exact packet/core provenance.
