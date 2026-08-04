# External-review prompt: structural proof of the sharp four/five threshold

Please conduct a hostile mathematical review of the new human proof replacing
the computer-assisted four-player Lmin--Lmax bridge.

## Primary files

- `coopgames/paper3/sections_leximin.tex`: the paper proof, beginning at the
  lemma labelled `lem:lx-protector` and continuing through
  `lem:lx-richer-suffix` and `thm:lx-proper-minimum-dimension`.
- `coopgames/paper3/N4_LMIN_LMAX_HUMAN_PROOF.md`: expanded standalone proof.
- `coopgames/paper3/N4_LMIN_LMAX_REVIEW_PACKET.md`: dependencies, prior-art
  boundary, exact reproduction commands, and explicit review questions.
- `coopgames/paper3/wrapper.pdf`: rendered paper.

## Independent audit material

- `coopgames/src/verify_n4_exact_lmin_pes_bridge.py`
- `coopgames/src/verify_n4_exact_lmin_pes_bridge_primal.py`
- `coopgames/src/verify_n4_exact_lmin_pes_bridge_witnesses.py`
- `coopgames/src/verify_n4_exact_lmin_pes_artifacts.py`
- `coopgames/src/verify_n5_exact_leximin_monotonicity_counterexample.py`
- `coopgames/src/verify_n5_exact_lmin_lmax_large_core.py`

The finite encodings corroborate the theorem but are not intended to repair a
gap in the human proof.  Please assess the proof on its own terms before
consulting their outputs.

## Load-bearing questions

1. Does the protector property used here match the published Arin--Iñarra
   transfer-blocking characterization of the egalitarian core, and does it
   apply to Lmin with these ordering conventions?
2. In the redundant LP derivation, are the stationarity signs correct, giving
   `w_h-w_i=1+mu_i>0`, including on degenerate stage faces?
3. Does positive coverage difference plus complementary slackness reproduce
   the published tight-coalition property under the manuscript's conventions?
4. Is the dimension-free fractional protector-packing inequality (FP) valid
   for arbitrary nonnegative weights with vertex loads at most one?  Do the
   two displayed packing constructions exhaust every protector hypergraph on
   at most three poorer players?
5. In the ordered `2|2` case, do complement tightness, the forced cross pair,
   and the exact singleton witness yield the stated strict efficiency
   contradiction?
6. In the tied `2|2` case, are the two protector disjunctions exhaustive?  If
   all four cross pairs are tight, do they force the displayed exact-singleton
   point and a genuine max-min-improving core segment?
7. Does the final reduction cover every strict payoff boundary for `|N|<=4`
   without silently enumerating or excluding a stratum type?
8. Treating the protector property as known, is (FP), the through-four
   inclusion, or their combination with exact singleton witnesses already
   present in the exact-partition, Lmin/Lmax, egalitarian-stability,
   hypergraph-packing, or Lorenz-core literature?

## Requested verdict

Please return:

- `verified`, `verified with qualifications`, or `not verified`;
- every gap or ambiguous inference with exact file and line references;
- whether each issue is fatal, repairable, or expository;
- a separate novelty/prior-art assessment that does not conflate correctness
  with originality;
- confirmation of which reproduction commands were actually run.

Do not treat solver agreement, unsatisfiable cores, or the previous favorable
review of the finite theorem as evidence that the new human proof is valid.
