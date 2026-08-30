# PXC149 prior-art audit — 2026-08-30

Status: preliminary primary-source audit, not a specialist novelty opinion.

## Sources checked

- Schmeidler's exactness definition and its concavification restatement are
  summarized in Lehrer et al., *A note on the concavification of a
  cooperative game*, Definition 7 and Proposition 1:
  <https://www.math.tau.ac.il/~lehrer/Papers/Note-concav-cooperative-4.pdf>.
- Studený and Kratochvíl, *Facets of the cone of exact games*, characterize
  exact-cone inequalities by minimal/indecomposable semi-balanced systems:
  <https://arxiv.org/abs/2103.02414>.
- Kroupa and Studený, *Facets of the Cone of Totally Balanced Games*, give
  the analogous irreducible min-balanced-system framework and summarize
  exact-balancedness literature:
  <https://arxiv.org/abs/1812.00576>.

## Findings

1. The existence of a separate core allocation attaining each singleton is
   exactly the classical definition of exactness.  PXC149 must not present
   the `b=0` and `c=0` witnesses themselves as new.
2. The weighted elimination used for the `X_b` bound is naturally a
   balanced/semi-balanced incidence certificate.  The manuscript should
   describe it that way, rather than name a new general duality principle.
3. The checked sources provide broad exact-cone and balanced-system
   machinery, but this audit did not locate the specific block-symmetric
   inequalities

   ```text
   X_b <= m(uv-1)/((u-1)(v-1)),
   X_c <= 2m + m(uv-1)/((u-1)(v-1)),
   ```

   the family `J_{m,k}`, its four-orbit minimax dual, or its closed selector
   ratio.
4. Non-location is not evidence of novelty.  The likely candidate
   contribution is the selector-specific application and sharp family, not
   exactness witnesses or balanced-system duality.

## Required external check

A cooperative-game specialist should check exact-balancedness, min-semi-
balanced, large-core, one-bound-core, and Lorenz/egalitarian-core literature
for equivalent inequalities or constructions.  Until that review is
received, label PXC149 as internally proved and independently reproduced,
with novelty unresolved.
