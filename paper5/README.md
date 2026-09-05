# Separation program: current results and archival status

Current as of 5 September 2026.

The sharp unrestricted theorem is in [asymptotic_constant_two](asymptotic_constant_two/README.md): `lim n(2-s_n)=2`, with deficit `2/n+O(log(n)/n^2)`. The current assignment paper is [the pairs/triples comparison](assignment_comparison/README.md), which incorporates the two individual assignment notes and their revised prior-art positioning.

`divergence.tex` and its 183-page PDF are retained as a historical manuscript, including the finite `s_5=1/2`, `s_6=2/3` results, equality classification, and PXC development. They are not current submission-ready exposition. In particular, the statement near source line 299 that a bound matching the old G-family construction is open is superseded: later PXC143–146 counterexamples refute that target. The protected ledger's dated override takes precedence over its historical frontier labels. The old PXC151 construction is valid but its coefficient `3+2 sqrt(2)` is not the sharp unrestricted constant.

The fixed-player attainment/rationality proposal in `SHARP_GAP_CHAMBER_REDUCTION.md` remains unproved by its present argument. The mistaken support-cardinality inequality in `SHARP_ASYMPTOTIC_GAP_PROGRAM.md` has been corrected. Neither issue affects the separate reviewed sharp asymptotic proof.

The release script now checks that Python assertions are enabled before starting its legacy stages. Three six-player proof-record wrappers separately use ordinary guards and check complete case coverage. They validate records and file integrity; actual cvc5/Ethos replay is separate. The September 5 review freshly replayed all 30 strict/equality proof objects, but did not rerun the complete historical release.

See [the portfolio audit](../portfolio_review_2026-09-05/REVIEW.md) for precise verification scope, repairs, contribution inventory, and current priority qualifications.
