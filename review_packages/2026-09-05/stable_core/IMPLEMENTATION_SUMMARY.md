# Package implementation summary — 2026-09-05

Source commit: `21443c59ac75f5a399f9787014aa4ccb6c0c1dc8` in the recovered CoopGT repository. Original files were read only. All changes are confined to this package copy.

## Manuscript

- Created a single self-contained `manuscript.tex`, with no external TeX input dependencies.
- Retained the complete core-segment derivation, two-round procedural trace, pair-domination lemma, direct six-player external-stability proof, sharpness result, additive-invariance lemma, and all three ray formulas/proof.
- Placed the direct stability theorem before the ray, so the ray's stability claim follows an already-proved result.
- Preserved Mauri2017's exact-game precedent, now with freshly verified printedpp40–41. The historical core geometry and pair/triple mechanism remain attributed to older work.
- Kept only the segment arrangement cross-check in a clearly secondary appendix. Removed the general polyhedral-core algorithm and its novelty-adjacent narrative.
- Made stable-core nonemptiness explicit, matching the primary definition. This repairs an ambiguity that could otherwise admit vacuous external stability when the imputation set is empty.
- Added modern context and a truthful pending-specialist-review statement. Removed unsupported assertions that all current claims had already received author/human review.

## Verification

- Standard entrypoint: `python3 verification/run_checks.py`.
- Fresh procedural checker uses `fractions.Fraction`, full coalition tables, published positive/negative controls, and Mauri's prior example. It also verifies the permutation/additive relation of the regression witness over all coalitions.
- Reused the independently structured segment arrangement verifier, preserving exhaustive coverage and exact domination construction. Package copy now rejects incomplete coalition coverage, malformed player sets, and duplicate JSON keys; no silent zero-filling is accepted.
- Reused the symbolic ray proof, replacing every optimization-sensitive `assert` with an unconditional guard. Added explicit procedural progress/termination checks and a machine-readable report of every parameter cut.
- Made result persistence fail closed: the entrypoint replaces any prior PASS with RUNNING before data parsing, and saves FAIL on exceptions. A separate copied-package probe started from a fake PASS and truncated JSON; it exited1 and replaced the old result with FAIL (`audit/stale_result_negative_control.json`).
- Added negative controls for missing zero coalitions in both parsers, duplicate JSON keys, duplicate coalition aliases, wrong stored claims, and guard failure under optimized Python. The main runner scans its verification source to reject any remaining `assert` node.
- Trimmed data to the main six-player witness and its exactly mapped regression normalization. Earlier ancillary five-player search witnesses are not packaged as new contributions.

## Results and limits

Normal Python run passed on Python3.14.3. Optimized-mode run was also exercised to check that validation cannot disappear under `-O`. The symbolic ray covers37 comparison cells plus every finite boundary. Each arrangement replay checks20,349 bases,8,264 nonsingular bases,230 distinct intersections,104 imputation vertices,2 core endpoints, and102 dominated outside-core vertices.

Written references and labels were checked for unresolved/duplicate labels, with none found; there are no TeX input dependencies. PDF compilation/rendering is deliberately left to the parent consolidation task. Full human specialist correctness and priority review remains **PENDING**.

The current program certifies the explicit games and ray; it does not reprove the published universal five-player large-core theorem. The primary 2011 theorem statement and hypotheses were inspected directly. A full modern citation closure and the final subscription-only2025 population article remain specialist-review limits.
