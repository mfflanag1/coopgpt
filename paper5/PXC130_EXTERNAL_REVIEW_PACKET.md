# Hostile external review — PXC130--PXC131 slack transport and completion no-go

Checkpoint date: 2026-08-24. Review PXC130--PXC131 in `paper5/divergence.tex` and
its mechanism interpretation in `paper5/MECHANISM_PRICE_PROGRAM.md`.

## Claim under review

Let `v` be an exact TU game, let `E` be a nonempty proper coalition, and let
`w^E` be a core allocation attaining `v(E)`. Suppose

```text
sum_S lambda_S 1_S = rho 1_N + beta 1_E,
lambda_S >= 0, rho >= 0, beta > 0.
```

Writing `sigma_y(S)=y(S)-v(S)`, PXC130 claims that every core allocation `y`
satisfies

```text
sum_S lambda_S v(S) <= rho v(N)+beta v(E),
sum_S lambda_S sigma_y(S) >= beta sigma_y(E).
```

The proof evaluates the incidence identity at `w^E`, uses
`w^E(S)>=v(S)`, evaluates it again at `y`, and subtracts. No
indecomposability or facet hypothesis is used.

For `E={r}`, singleton normalization gives the forced-zero packet price

```text
sum_S lambda_S sigma_y(S) >= beta y_r.
```

For a partition `B_1|...|B_m` of `N\T`, the identity

```text
sum_s 1_(T union B_s) = 1_N + (m-1)1_T
```

gives the partition-star transport. When `T={r,h}` and all these rows are
`z`-tight, equal-top cover normalization gives

```text
Phi_R = [x(T)-z(T)]/2.
```

The manuscript concludes only that alternative partition-star covers expose
the same exceptional-pair comparison budget. It explicitly does **not** add
their facet inequalities as independent reciprocal currency and does not
claim a proof of the hybrid-overlap inequality.

PXC131 adds an LP-dual criterion. For a nonsingleton `E`, let `K_-E` retain
every core inequality except `E`. An active packet supported away from `E`
exists iff `min_(K_-E)y(E)=v(E)`. The manuscript then proves exact
irredundancy controls: deleting PXC101's `rj` row lowers its minimum from
`6` to `3`, while deleting either PXC104 cross blocker lowers `18` to `16`.
This refutes the shortcut that exactness automatically supplies a useful
nontrivial completion of every blocker.

## Exact controls

Primary audit:

```bash
python3 verifiers/divergence/verify_pxc130_exceptional_slack_transport.py \
  --output /tmp/pxc130.json
cmp verifiers/divergence/pxc130_exceptional_slack_transport.json \
  /tmp/pxc130.json
```

Focused independent and blocker-completion reproductions:

```bash
python3 verifiers/divergence/verify_pxc130_exceptional_slack_transport_independent.py \
  --output /tmp/pxc130-independent.json
cmp verifiers/divergence/pxc130_exceptional_slack_transport_independent.json \
  /tmp/pxc130-independent.json
python3 verifiers/divergence/verify_pxc131_blocker_completion_no_go.py \
  --output /tmp/pxc131.json
cmp verifiers/divergence/pxc131_blocker_completion_no_go.json \
  /tmp/pxc131.json
python3 verifiers/divergence/verify_pxc131_blocker_completion_no_go_independent.py \
  --output /tmp/pxc131-independent.json
cmp verifiers/divergence/pxc131_blocker_completion_no_go_independent.json \
  /tmp/pxc131-independent.json
```

The controls check:

- six-player PXC101--PXC102 anchor: pair slack `1`, normalized cover
  currency `1/2`;
- both PXC104 cross covers: pair slack `5/3`, currency `5/6`;
- PXC118's additional two-block cover: the same `5/6` currency;
- the relabelled six-player catalogue-type-41 identity
  `2*025+2*125+3*345+0135+0145=4*N+5*{5}`;
- a nonexact relaxed selector point on which that single packet fails by
  `609/178`, providing a fail-open control;
- 64 ordered two-/three-block incidence identities through four residual
  roles in the standalone implementation;
- all remaining proper core rows after each of the three blocker deletions;
- independent active-set lower envelopes, explicit deleted-row minimizers,
  and explicit dual lower-bound packets.

## Questions for hostile review

1. Is exactness of `v` sufficient to choose one `w^E` attaining an arbitrary
   proper coalition `E`, with no hidden convexity or total-balancedness step?
2. Are both inequality orientations in PXC130b correct?
3. Does the partition-star normalization really give common weight
   `1/[2(m-1)]` and top coefficients `(1/2,1/2)` for every `m>=2`?
4. Does PXC130e require all positive rows and `T` to be `z`-tight, and are
   those hypotheses stated prominently enough?
5. Is the warning against summing two alternative-cover budgets rigorous as
   stated, or does it accidentally rule out a legitimate disjoint refinement?
6. Is the singleton-exceptional specialization already a standard named
   “slack form” or “deficiency form” of exact balancedness?
7. Is the partition-star specialization merely complementary-slackness for a
   known exact-cone facet, and should the terminology be adjusted?
8. Does catalogue type 41 have the displayed coefficient orientation under
   the Studený–Kratochvíl convention?
9. Are there known aggregation or uncrossing theorems for semi-balanced
   systems that could provide the still-missing disjoint label-layer payment?
10. Does this result materially advance the mechanism-to-price program, or is
    its honest significance only to close an invalid reciprocal-facet route?
11. Is the PXC131 equivalence exactly the Farkas/redundancy criterion for the
    deleted core row, including the sign of the efficiency multiplier?
12. Do the three strict deleted-row gaps really preclude every active packet
    supported away from the blocker, rather than only a selected facet class?
13. Is there a standard exact-balancedness theorem that gives a nontrivial
    completion under an additional hypothesis weaker than row redundancy?

## Prior-art baseline and novelty restraint

Review date: 2026-08-24.

- Schmeidler's definition of exact games supplies coalition-attaining core
  allocations; PXC130's first step should be treated as standard exactness.
- Studený and Kratochvíl, *Facets of the cone of exact games*, DOI
  `10.1007/s00186-022-00770-4`, supplies the indecomposable semi-balanced
  facet correspondence. A primary-text check on 2026-08-24 found that its
  Lemma 7 states the exact-game inequalities over every exceptional set and
  Lemma 8 identifies the vertices with min-balanced or exceptional
  min-semi-balanced systems. PXC130b should therefore be presented as a
  slack-form rewrite of that established exactness machinery, not a new cone
  theorem; neither “slack transport” nor “redundancy” appeared as a named
  term in the searchable text. PXC130 does not claim the correspondence or
  the partition-star facets as new.
- Lohmann, Borm and Herings, *Minimal exact balancedness*, DOI
  `10.1016/j.mathsocsci.2012.01.002`, is the relevant balanced-collection
  background.
- Ordinary LP complementary slackness and weighted core-slack identities are
  clear conceptual neighbors. A specialist should determine whether PXC130b
  already appears verbatim under another name.

The only proposed contribution is the use of this elementary transport as a
common accounting interface for the staged-selector carrier/blocker program,
plus the resulting warning that reciprocal alternative-cover facets do not
automatically provide independent payment. No novelty claim should be made
before specialist review.

## Significance if correct

PXC130--PXC131 is a useful dimension-free bridge and route no-go, not the
desired overlap theorem. It
turns every selected semi-balanced/exactness packet into explicit permitted
currency and proves that the reciprocal partition-star facets alone cannot
finish the job. The live theorem remains packet **selection plus congestion**:
one must produce enough such packets from the PXC128 carrier measure and
staged blockers, then assign their transported slacks to disjoint threshold
layers totaling `D_H`.
