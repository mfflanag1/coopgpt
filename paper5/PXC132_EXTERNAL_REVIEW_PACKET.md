# Hostile external review — PXC132--PXC135 packet support and transport

Checkpoint date: 2026-08-24. Review PXC132--PXC135 in
paper5/divergence.tex, the matching section of
paper5/MECHANISM_PRICE_PROGRAM.md, and all primary/independent verifiers
listed below. This packet makes no novelty claim.

## Claimed theorem

Let Z(z) be the proper coalitions tight at z. Suppose an efficiency-zero
staged direction d and blocker Q in Z(z) satisfy

    d(Q)<0,        d(S)=0 for every S in Z(z) different from Q.

Consider a reduced exceptional packet

    sum_(S in P) lambda_S 1_S = rho 1 + beta 1_E,
    sum_(S in P) lambda_S v(S) = rho T + beta v(E),
    lambda_S,beta>0, rho>=0,

where reduced means E is absent from the positive support. PXC132 claims
that Q in P subset Z(z) is impossible.

The proof assumes the contrary. Evaluating the incidence identity at z and
comparing it with the active worth equality makes E itself z-tight.
Reducedness gives E different from Q. Dotting with d then leaves only
lambda_Q d(Q)=0, contradicting strict negativity.

## Consequences and scope

- The theorem applies in every dimension to the complete typed z-tight
  menus of the PXC101 and PXC125 common-direction families.
- It says an active mixed packet containing their blocker must import at
  least one positive row not tight at z.
- It does not prove that such a packet exists, that its imported slack is
  large enough, or that packets can be aggregated without congestion.
- PXC104 is a necessary negative control: its reciprocal blocker has an
  entirely z-tight active cross-cover packet because another z-tight menu
  row supplies the additional derivative.

## Reproduction

From the repository root:

    python3 verifiers/divergence/verify_pxc132_forced_zero_packet_escape.py \
      --output /tmp/pxc132.json
    cmp verifiers/divergence/pxc132_forced_zero_packet_escape.json \
      /tmp/pxc132.json

    python3 \
      verifiers/divergence/verify_pxc132_forced_zero_packet_escape_independent.py \
      --output /tmp/pxc132-independent.json
    cmp verifiers/divergence/pxc132_forced_zero_packet_escape_independent.json \
      /tmp/pxc132-independent.json

The primary audit checks the all-dimensional derivative patterns and then
uses all 7,006 labelled permutations of the published six-player
indecomposable min-semi-balanced catalogue as finite calibration. The
standalone audit imports no project game, LP, selector, cover, or catalogue
code. The catalogue counts are not used to prove the theorem.

## Prior-art baseline checked on 2026-08-24

- Studený and Kratochvíl, “Facets of the cone of exact games,”
  DOI 10.1007/s00186-022-00770-4, supplies the min-semi-balanced
  exceptional-set/facet framework used for the finite calibration.
- Björner, Las Vergnas, Sturmfels, White, and Ziegler, Oriented Matroids,
  second edition (Cambridge, 1999), is the natural general source for
  circuit/cocircuit support orthogonality.
- PXC132 should currently be treated as an elementary complementary-
  slackness/orthogonality observation specialized to the selector packet,
  not as a new exact-cone or oriented-matroid theorem. The targeted search
  found no named cooperative-game statement about a unique-negative staged
  blocker, but only a specialist review can determine whether this
  specialization is already standard under another name.
- PXC133 is an algebraic slack-conservation rewrite of the same incidence
  identity. It should not be presented as a new facet theorem; the only
  potentially useful content is its warning against spending exactness
  slack already present at the comparison allocation.
- PXC134 is the standard fractional-matching/vertex-cover LP dual combined
  with the project's layer-cake identity. No novelty is claimed for that
  optimization theorem. The research-specific question is whether exactness
  and staged selector certificates force a target-reaching admissible edge
  graph; PXC134 expressly does not answer it.
- PXC135 is a synthesis of the already displayed PXC129 carrier dichotomy
  with PXC134 and canonical opposite-rank pairing. No separate novelty claim
  is made for this synthesis before specialist review.

## Hostile questions

1. Does activity plus positive-row z-tightness really force z(E)=v(E) with
   no hidden sign assumption?
2. Is reducedness the correct way to exclude cancellation of the same row
   on both sides, and should the theorem instead state the cancelled normal
   form explicitly?
3. Does the dot-product contradiction require d(S)=0 on every other
   z-tight row, or can it be weakened to a signed inequality?
4. Are the PXC101 and PXC125 typed menus complete in every stated parameter
   chamber, including boundary coarsenings?
5. Is PXC104 genuinely a fail-open reciprocal control rather than a
   contradiction to the theorem's hypotheses?
6. Is the result already standard as an oriented-matroid cocircuit,
   complementary-slackness, or semi-balanced-support observation?
7. Does the manuscript distinguish clearly between the conventional
   dimension-free theorem and the finite six-player catalogue calibration?
8. Does this route restriction materially advance the hybrid-overlap
   program, or should it be demoted to a remark?

## Honest status

PXC132 is a short support no-go. It rules out a tempting all-active-facet
proof in the common-direction branch and identifies the precise resource
that must enter next: non-z-tight row slack or disjoint staged-label
currency. It does not prove the hybrid-overlap inequality.

## PXC133 conservation claim

For every packet, not only active ones, PXC133 defines

    g = rho T + beta v(E) - sum lambda_S v(S)

and claims

    sum lambda_S sigma_y(S) = beta sigma_y(E) + g

for every efficient core allocation y. Exactness gives g nonnegative.
Subtracting the identities at x and z gives

    sum lambda_S [x(S)-z(S)] = beta [x(E)-z(E)].

The review should check the consequence drawn from this: raw core slack at
x is not overlap currency until the same packet's slack at z is subtracted.
In the positive-demand PXC125 control the active packet has raw x-slack
22/5, z-slack 4, and comparison shear 2/5, which is below D_H=2/3.

The primary audit also recomputes the full spectral decomposition. It finds

    PXC101: B*=B_H=O=15, packet shear 1;
    PXC104: B*=B_H=O=56/3, packet shear 10/3;
    PXC125: B*=B_H=16, O=23, packet shear 2/5.

Hence packet comparison shear is not automatically either `B_H-B*` or
`O-B_H`. The first two shears are surplus in zero-demand controls; PXC125's
positive demand is paid by a separate label-layer theorem. Reviewers should
reject any language that identifies these quantities before an explicit
demand-aware embedding has been proved.

Additional reproduction:

    python3 \
      verifiers/divergence/verify_pxc133_two_allocation_packet_conservation.py \
      --output /tmp/pxc133.json
    cmp verifiers/divergence/pxc133_two_allocation_packet_conservation.json \
      /tmp/pxc133.json

    python3 \
      verifiers/divergence/verify_pxc133_two_allocation_packet_conservation_independent.py \
      --output /tmp/pxc133-independent.json
    cmp \
      verifiers/divergence/pxc133_two_allocation_packet_conservation_independent.json \
      /tmp/pxc133-independent.json

Additional hostile questions:

9. Is PXC133a exactly a constant-gap identity, including for nonactive
   packets?
10. Is it legitimate to conclude that only PXC133b, rather than the raw
    positive-support slack at x, can be assigned as x-versus-z label
    currency?
11. Do the PXC101 and PXC125 calculations correctly separate exactness
    slack already present at z from comparison shear?
12. Is this conservation observation standard in exact-game facet theory
    under a named slack or complementary-slackness formulation?
13. Do the spectral controls decisively rule out interpreting packet shear
    itself as top-selection or label currency, rather than merely showing
    that one proposed normalization was poor?

## PXC134 endpoint-congested transport

For a predeclared family of residual pairs `i -> j` with
`max(x_j,z_j)<min(x_i,z_i)`, PXC134 maximizes the clipped interval lengths
over nonnegative edge weights having outgoing weight at most one and
incoming weight at most one per player. It claims that this value is at most
`O-B_H`, by integrating the endpoint constraints across threshold layers,
and that its exact dual is the fractional bipartite source/sink cover
`p_i+q_j>=ell_ij`.

For the complete clipped graph the canonical opposite-rank edges attain
`O-B_H`; this follows because they use every player at most once in each
orientation. A three-residual chain control has restricted value `1` but
complete-graph value `3/2=O-B_H`, and detects the invalid stronger choice of
merging a player's two orientation capacities.

The theorem is only an aggregation interface. It does not claim that every
PXC114 blocker or cover pair generates a graph attaining `D_H`. The named
controls are PXC125 (two rungs, value `7`), PXC127 (common-cut graph, value
`37/5`), and the zero-demand PXC101/PXC104/PXC90 boundaries.

Additional reproduction:

    python3 verifiers/divergence/verify_pxc134_endpoint_congested_transport.py \
      --output /tmp/pxc134.json
    cmp verifiers/divergence/pxc134_endpoint_congested_transport.json \
      /tmp/pxc134.json
    python3 \
      verifiers/divergence/verify_pxc134_endpoint_congested_transport_independent.py \
      --output /tmp/pxc134-independent.json
    cmp verifiers/divergence/pxc134_endpoint_congested_transport_independent.json \
      /tmp/pxc134-independent.json

Additional hostile questions:

14. Does the layer proof correctly use one shared endpoint capacity across
    all thresholds in each orientation, rather than silently assigning a
    fresh player at each layer?
15. Is it correct to keep a player's source and sink capacities separate
    because their active threshold intervals are disjoint, and does the chain
    control detect an accidental merger?
16. Is the dual exactly the bipartite fractional matching dual, with no
    missing blossom constraints or integrality claim?
17. Are the blocker/Farkas-induced allowed edges defined independently of
    the desired overlap conclusion, or would a future existence theorem be
    tautological?

## PXC135 mechanism-labelled canonical saturation

PXC135 combines PXC129 and PXC134. For every positive canonical rank
carrier, it selects a retained common separator when one exists. Otherwise
PXC129 labels the carrier by either a separating positive cover row or the
staged-Lmax blocker forced when that cover gives both endpoints identical
incidence. The canonical carriers use each player at most once in each
orientation, so their simultaneous PXC134 value is exactly `O-B_H`.

This claims only qualitative attribution of the existing label currency. It
does not claim `O-B_H>=D_H`, and it does not spend the packet shears from
PXC133. The exact remaining question is whether the singleton witnesses and
Farkas identities attached to these labels exclude a PXC134 dual
source/sink cover of total below `D_H`.

Additional reproduction:

    python3 \
      verifiers/divergence/verify_pxc135_mechanism_labelled_canonical_transport.py \
      --output /tmp/pxc135.json
    cmp verifiers/divergence/pxc135_mechanism_labelled_canonical_transport.json \
      /tmp/pxc135.json
    python3 \
      verifiers/divergence/verify_pxc135_mechanism_labelled_canonical_transport_independent.py \
      --output /tmp/pxc135-independent.json
    cmp \
      verifiers/divergence/pxc135_mechanism_labelled_canonical_transport_independent.json \
      /tmp/pxc135-independent.json

Additional hostile questions:

18. Does PXC129 genuinely provide a label for every positive canonical
    carrier after the common-row case is removed, for one fixed cover at a
    time?
19. Does the canonical rank construction use every player at most once in
    each orientation even when a player appears once in both roles?
20. Is PXC135 careful to claim only attribution of `O-B_H`, rather than the
    still-open quantitative lower bound by `D_H`?
