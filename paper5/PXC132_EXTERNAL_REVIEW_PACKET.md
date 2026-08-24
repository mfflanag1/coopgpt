# Hostile external review — PXC132 forced-zero active-packet escape

Checkpoint date: 2026-08-24. Review PXC132 in paper5/divergence.tex,
the matching section of paper5/MECHANISM_PRICE_PROGRAM.md, and the two
PXC132 verifiers. This packet makes no novelty claim.

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
