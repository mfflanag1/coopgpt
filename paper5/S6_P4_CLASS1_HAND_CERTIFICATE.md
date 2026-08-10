# Class-1 universal-order hand certificate

## 1. Scope and status

Packet class 1 is the singleton orbit

```text
P4={1,4},   P5={1,5}.
```

Its no-new-order relay is not complete, but the universal split

```text
W: x3<=x4        S: x3>x4
```

closes it.  This note replaces the shared-encoder relay result by a frozen
exact-rational certificate.  The checker imports neither a solver nor the
production encoder.  This is a checkable finite proof object, not an external
review, a novelty finding, or yet a concise conceptual lemma.

## 2. Difference cone and packet sandwich

Write

```text
di = xi-zi > 0       (i=0,1,2,3),
delta4 = z4-x4 > 0,  delta5 = z5-x5 > 0.
```

Efficiency and the two opposite-allocation packet comparisons give

```text
d0+d1+d2+d3 = delta4+delta5,
d1 <= delta4 <= d0+d2+d3,
d1 <= delta5 <= d0+d2+d3.                         (1.1)
```

For a cut `C`, `x(C)-z(C)` is therefore a five-variable rational linear form.
Fourier--Motzkin elimination implemented with `fractions.Fraction` recomputes
the feasible negative-cut list at every relay stage.  This census is independent
of the payoff/witness certificate rows and does not call an LP or SMT solver.

## 3. Relay anatomy

On `W`, the Lmax exchange

```text
h10=e0-e1
```

has exactly seven blockers:

```text
{1,3}, {1,4}, {1,2,4}, {1,3,4},
{1,5}, {1,2,5}, {1,3,5}.
```

After any one of them, the Lmin exchange

```text
h16=-e1-e2+e4+e5
```

has no blocker.  This gives seven terminal leaves.

On `S`, the Lmin exchange

```text
h17=-e1-e3+e4+e5
```

has exactly four blockers:

```text
{1,3,4}, {0,1,3,4}, {1,3,5}, {0,1,3,5}.
```

At each child, `h16` has exactly the two corresponding blockers obtained by
replacing player 3 by player 2, with and without player 0.  Six terminal leaves
then close with

```text
h18=-e2-e3+e4+e5,
```

while the two paths containing player 0 at both levels close with `h10`.
Thus the strict branch has eight terminal leaves and the complete tree has
fifteen.

## 4. Exhaustive activation logic

For `hab=-ea-eb+e4+e5`, the Lmin activation premise is

```text
(xa>x4 and xb>x4 and x5>=x4)
or
(xa>x5 and xb>x5 and x4>=x5).                    (1.2)
```

Failure of (1.2) expands into nine pairs of failed atoms.  The ninth pair
contains both strict failures `x5<x4` and `x4<x5` and is contradictory.  For
each of the other eight pairs, the certificate uses the weaker non-strict
relations and proves either `D<=1/3` or, in three strict-root cases,
`x4-x3<=0`; the latter is strict on `S`.  There are eighteen such two-branch
activation sites, hence 144 rational cases plus eighteen direct contradictions.
The three `h10` sites each have the single failure `z1<=z0`.  The checker
therefore audits all

```text
144 + 18 + 3 = 165
```

activation-failure cases.  This explicit DNF coverage is necessary: neither
alternative of (1.2) is individually forced at the generic relay states.

## 5. Exact census and certificate compression

The twenty-one difference-cone censuses contain 104 feasible opposite-cut
candidates.  Nineteen are the relay edges displayed above and the other 85 are
excluded by exact payoff/witness identities.  The activation and blocker rows
deduplicate as follows:

```text
65 blocker identities + 60 activation identities = 125 identities,
85 blocker uses       + 147 activation uses       = 232 uses.
```

Among the 85 blocker uses, 37 use only the `q1` comparison, twelve use only
the opposite-allocation comparison, and 36 use both.  Across all uses, 223
identities target `D-1/3`, six target the strict sign `x0-z0<0`, and three
target the strict branch sign `x4-x3<0`.

The checker rebuilds every named premise at each use site, verifies all
multipliers and affine identities with exact rational arithmetic, recomputes
the structural census, and rejects mutations of a coefficient, use site,
candidate set, use map, activation atom, or strict-target semantics.

## 6. Reproduction and review boundary

Run

```bash
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class1_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class1_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class1_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class1_hand_certificate_audit.json
```

The frozen inputs are

```text
coopgames/verifiers/s6/strict_exchange_p4_class1_hand_certificate_rows.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class1_hand_certificates.py
```

A reviewer should independently derive (1.1), the twenty-one candidate sets,
the fifteen-leaf relay, and the complete failure expansion of (1.2).  A `PASS`
status alone does not establish that every genuine game-theoretic counterexample
enters the encoded packet relaxation.  That human-to-machine implication
remains the campaign's most important external-review gate.
