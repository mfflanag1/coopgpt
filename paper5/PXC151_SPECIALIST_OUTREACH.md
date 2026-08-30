# PXC151 external-specialist outreach

Prepared: 2026-08-30

Status: outreach package only. No person listed below has been contacted,
agreed to review, or endorsed PXC151. The mathematical version to inspect is
frozen at commit
`8d5947ff7ed80535bbcc0b7fa13d2e44bfcbe564` on branch
`codex/hmr-four-generator-no-go`.

Public commit:
<https://github.com/mfflanag1/counterexample-hunt/commit/8d5947ff7ed80535bbcc0b7fa13d2e44bfcbe564>

## Expertise coverage sought

The most useful review is split between two independent readers.

1. **Egalitarian selectors and exact-partition games.** The reader should know
   the Arin--Iñarra--Kuipers--Vermeulen or Dietzenbacher line and should audit
   the meanings of `Lmin`, `Lmax`, Lorenz dominance, and the `r=2` structural
   handover. Bas Dietzenbacher is a plausible reader from the public
   authorship record: his current Maastricht profile identifies cooperative
   game theory and egalitarian allocation as active expertise.
   <https://www.maastrichtuniversity.nl/bj-dietzenbacher>
2. **Exact-cone and semi-balanced-system geometry.** The reader should audit
   lower-envelope exactness and the sparse incidence/minimax certificate in
   the terminology of the exact-game cone. Milan Studený or Václav
   Kratochvíl are plausible readers because they authored *Facets of the cone
   of exact games* and maintain the relevant catalogue/software.
   <https://utia.cas.cz/en/people/?pid=185>
   <https://mtr.utia.cas.cz/cs/people/kratochvil>

An optional third reader can test whether a general majorization theorem
already subsumes the construction. Martijn Schoot Uiterkamp is a plausible
adjacent reader because his work characterizes simultaneous optimization and
least-majorized points on (bi-)submodular polyhedra.
<https://www.tilburguniversity.edu/staff/m-h-h-schootuiterkamp>

These names are expertise matches, not a ranking, contact record, or claim of
availability. A reviewer with equivalent publication-level expertise is
equally suitable.

## Files to send

Ask the reader to inspect the frozen commit, not the moving branch head, and
start with:

```text
coopgames/paper5/PXC151_QUADRATIC_TWO_BLOCK_REVIEW_PACKET.md
coopgames/paper5/PXC151_PRIOR_ART_AUDIT_20260830.md
coopgames/paper5/divergence.tex                  (PXC151a--PXC151i)
coopgames/verifiers/divergence/verify_pxc151_quadratic_two_block_breakthrough.py
coopgames/verifiers/divergence/verify_pxc151_quadratic_two_block_breakthrough_independent.py
```

The verifier outputs are audit aids, not proofs. The reviewer should check the
conventional all-parameter argument independently before consulting them.

## Short request

```text
Subject: Narrow external review request — exact cooperative-game selector family

I am seeking a hostile, narrowly scoped review of a candidate theorem about
two opposing egalitarian core selections on singleton-normalized exact TU
games. At the frozen commit below, PXC151 gives a three-generator exact family
K_{m,r}, m>=2 and r>=3, with closed Lmin and Lmax, and proves an infinite
improvement over the paper's previous balanced-family benchmark. Along
m/r -> a it obtains n(2-rho) -> 2a+3+1/a, minimized at 3+2sqrt(2)<8.

Frozen commit:
https://github.com/mfflanag1/counterexample-hunt/commit/8d5947ff7ed80535bbcc0b7fa13d2e44bfcbe564

Please begin with:
coopgames/paper5/PXC151_QUADRATIC_TWO_BLOCK_REVIEW_PACKET.md

Would you independently check the conventional symbolic proof and report
critical, major, minor, and presentational findings? Please treat the verifier
outputs only as regression evidence. Separately, please state whether you know
or can locate an equivalent exact-game family, selector-separation theorem, or
asymptotic coefficient under exact-partition, Lorenz/egalitarian,
semi-balanced, majorization, or coherent-lower-probability terminology.

Please distinguish three verdicts:
(1) correctness of PXC151a--PXC151i;
(2) novelty within the search scope you actually covered; and
(3) significance of beating one construction benchmark without a matching
global upper bound.

The r=2 boundary is deliberately defined as the older PXC146 H_m family. It is
a discrete mechanism handover, not an algebraic continuation; please say
whether that wording and calibration are mathematically acceptable.
```

## Required verdict record

```text
Reviewer name and affiliation:
Relevant expertise:
Date:
Exact commit SHA inspected:

Correctness: correct / correct after listed repairs / indeterminate / false
Critical or major findings:
Minor or presentational findings:

Prior-art databases, citation networks, and terminology searched:
Equivalent prior result: yes / none located in stated scope / indeterminate
Closest result and why it does or does not imply PXC151:

Significance: construction theorem / broader structural theorem / requires a
matching upper bound or other named step
Permissible manuscript wording:
```

Until at least one selector/domain specialist returns this record, the only
permissible project description remains: “internally proved infinite
benchmark improvement; external correctness and prior-art assessment
pending.” Exact-cone review is a valuable independent second gate, but cannot
substitute for the selector/domain review.
