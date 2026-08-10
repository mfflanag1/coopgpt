# Class-6 asymmetric-packet skeleton

## 1. Scope

Packet class 6 has representative

```text
P4={0,1,4},   P5={0,1,2,5}.
```

Its orbit contains four of the 32 feasible labelled packets.  The frozen
order-refined relay has 29 leaves.  This note now gives complete solver-free
arithmetic for the packet, activation, cut, and terminal-closure layers,
conditional on the frozen relay/use maps.  It is not independent validation of
the human-to-machine interface, external review, or a novelty determination.

## 2. The asymmetric sandwich

Let `di=xi-zi>0` for `i=0,1,2,3` and
`delta_m=zm-xm>0`.  The two opposite packet comparisons are

```text
d0+d1    <= delta4,
d0+d1+d2 <= delta5.
```

Together with efficiency they give

```text
d0+d1 <= delta4 <= d3,
d0+d1+d2 <= delta5 <= d2+d3.                    (6.1)
```

For example
`delta4-d3=(delta4+delta5-sum_i di)+(d0+d1+d2-delta5)`.
Thus the asymmetry forces the strong relation `d0+d1<=d3`.

## 3. The universal root split closes by signs

On `x3<=x4`, the Lmax root is

```text
h11=e0+e3-e4-e5.
```

The chains `z0<x0<=x4<z4` and `z3<x3<=x4<z4` prove its activation.  Of its
twenty negative cuts, a cut containing both rich players has negative
`d(C)` by efficiency.  With one rich player, (6.1) eliminates every cut
except

```text
24, 124.                                         (6.2)
```

In particular the stronger lower bound for `delta5` eliminates all cuts
through player 5.  No witness comparison is needed.

On `x3>x4`, the Lmin root is

```text
h17=-e1-e3+e4+e5.
```

The anchor chain gives `x1>x4,x5`, while `x3>x4>=min(x4,x5)`, proving
activation.  A negative cut without a rich player has positive `d(C)`.  A
negative cut through player 4 contains players 1 and 3, and
`delta4<=d3` makes its `d(C)` strictly positive.  Through player 5, including
player 2 is impossible by `delta5<=d2+d3`.  Hence the exact root list is

```text
135, 0135.                                       (6.3)
```

Equations (6.2)--(6.3) replace both twenty-cut root censuses by two two-cut
lists using only the packet sandwich and strict signs.

## 4. Complete cut accounting

Across the 49 direction nodes there are 924 eligible negative-cut uses.  (The
`h10` and `h15` directions have 16 each; the other five types have 20.)  Exact
Fourier--Motzkin elimination over the five-dimensional difference cone removes
711 and retains 213.  Only ten distinct candidate sets occur across all 49
nodes.  The remaining partition is disjoint and exhaustive:

```text
pure difference exclusions       711
allocation-context exclusions     11
singleton-witness exclusions     155
relay branches                    47
total                            924
```

The 11 intermediate exclusions arise before the target witness comparison:
their candidate opposite comparison is inconsistent with the packet/ancestor
`q^1` context.  Each has a sparse incidence over-cover of support at most five;
eight use unit coefficients and three require coefficient two.  Their strict
allocation lower bounds deduplicate to nine exact rational identities.  A
solver-free checker verifies those identities at all 11 sites and checks that
every named premise is available on the declared path.

The other 202 cuts survive that context layer.  Of these, 47 survive the full
witness comparison and are exactly the frozen relay branches; 155 are excluded
by the target `q^1` comparison.  Applying the zero-anchor incidence theorem to
those 155 exclusions produces an over-cover using at most five of the packet,
ancestor, and target coalitions:

```text
support size       1   2   3   4   5
certificate count 12  82  27  30   4
```

Exactly 150 certificates have only unit coefficients.  The other five use a
coefficient two; no coefficient larger than two is needed.  The exact support
bounds are zero in 12 cases, one in 98, two in 42, and three in three.  Thus
the witness side of every non-root filter is now a short incidence inequality,
not an opaque Farkas certificate.

The allocation half has now also been exactified.  The 155 strict lower bounds
deduplicate to 53 rational identities, each using three to eleven displayed
premises.  A solver-free checker reconstructs every normalization, sign,
anchor-order, packet, ancestor, and target premise as an affine form and
checks the identities over `Q`, including a positive multiplier on a strict
premise.  At the use level their anatomy is

```text
anchor/sign only  57       order-dependent   37
packet-dependent  24       path-dependent    37
```

Thus 118 of the 155 reductions use no ancestor or target comparison.  Of the
37 path-dependent uses, 33 use ancestors only and four also use the target's
opposite comparison.  The 53 identities split into 31 path-free and 22
path-dependent rows.  This removes Z3 from the arithmetic layer.  It does not
independently establish that the frozen 155-use map is exhaustive; that map
still comes from the localized relay and remains part of the external-review
boundary.  An independent exact-arithmetic census nevertheless checks that
the 11 context uses, 155 target-witness uses, and 47 branch edges partition all
213 difference-cone candidates; deleting any use or changing a direction is
rejected.

## 5. The same over-cover theorem controls activation

The 49 direction nodes have 124 elementary activation-failure conjunctions.
The anchor chains and the root order remove 84 of them directly.  Of the 40
residual cases, four `h7` failures are already inconsistent with the
opposite-allocation comparisons.  Every one of the other 36 failures has a
zero-anchor incidence over-cover using only the packet and ancestor witness
comparisons:

```text
support size       2   3   4
certificate count 12  10  14
```

Thirty use unit coefficients and six require coefficient two.  Deduplication
leaves 24 labelled support signatures.  Thus blocker filtering and forced
activation are two applications of the same witness-image theorem, rather
than separate solver phenomena.

The allocation half is now exactified too.  The 36 witness lower bounds
deduplicate to 26 rational identities, and the four direct cases share one
contradiction identity.  A solver-free checker reconstructs every failure
atom and named premise, checks the identities and strict semantics over `Q`,
and digest-links them to the 36 detailed incidence supports.  Nineteen uses
need no path comparison and seventeen use an ancestor.  This removes Z3 from
activation arithmetic; the relay-derived coverage map remains encoding-shared.

## 6. Residual relay

The weak root has two symmetric-looking subtrees.  Each passes through the
automatic `h10=e0-e1` Lmax exchange, one of four `h10` blockers, the automatic
Lmin exchange `h15=e0-e1`, and then closes immediately with either `h17` or
the three-for-three Lmax exchange `h7=e0-e1+e2-e5`.  The strict root has only
seven leaves and depth four.  The exact 924-use partition proves every
opposite-cut census and terminal no-blocker closure; the context and target
witness exclusions have solver-free incidence and allocation identities, and
all activation failures have the decomposition above.  Thus no arithmetic
leaf remains machine-only.  What remains encoding-shared is the relay/use-map
selection itself, which is precisely the external-review boundary.

## 7. Audits

```bash
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json
cmp /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_packet_skeleton_audit.json
```

The checker imports no solver or production encoder.  Exact rational
coefficient arithmetic verifies (6.1) and exhaustively partitions both
twenty-cut root lists.  Finite order enumeration checks both activation
chains and rejects weakened-chain and candidate-deletion mutations.  Its read
of the frozen universal relay is separately labelled as an integration audit,
not proof evidence for the lemma or the human-to-machine implication.

The complete cut census and the two encoding-shared over-cover layers are
reproduced separately:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py \
  --output /tmp/strict_exchange_p4_class6_overcovers.json
cmp /tmp/strict_exchange_p4_class6_overcovers.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_overcovers.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_allocation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class6_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_allocation_identity_audit.json
cmp /tmp/strict_exchange_p4_class6_allocation_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_allocation_identity_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_context_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_context_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_context_identities.py \
  --context-details /tmp/strict_exchange_p4_class6_context_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_context_identity_audit.json
cmp /tmp/strict_exchange_p4_class6_context_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_context_identity_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_cut_census.py \
  --output /tmp/strict_exchange_p4_class6_cut_census_audit.json
cmp /tmp/strict_exchange_p4_class6_cut_census_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_cut_census_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_activation_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_activation_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_activation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class6_activation_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_activation_identity_audit.json
cmp /tmp/strict_exchange_p4_class6_activation_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_activation_identity_audit.json
```

The compact artifact freezes the census and a SHA-256 digest of the canonical
155-row certificate list.  `--details` regenerates the complete list for
inspection without storing a large redundant proof artifact.  This second
audit imports Z3 and the localized relay encoder; it is a discovery and
integration audit.  The allocation checker itself imports neither and checks
the stored 53 identities by exact rational arithmetic.  Its linkage to all
155 detailed supports is digest-protected, but the relay-derived use map is
still not independent human-to-machine evidence.  The context audit has the
same status for its 11-use map; its separate checker verifies nine identities
over `Q` and enforces premise availability at every use site.  The cut-census
checker imports no encoder or solver.  It independently recomputes the 711/213
difference-cone split and checks the exhaustive `213 = 11 + 155 + 47`
partition against the frozen integration maps.

The activation audit also imports the localized encoder.  It checks all 49
failure expansions and the `124 -> 84 + 4 + 36` partition, and freezes a
digest for the 36 detailed supports.  Its incidence rows instantiate the
solver-free theorem.  The separate rational checker proves the 26 lower-bound
and one direct identity without an encoder; only their 40-use coverage map is
integration evidence.
