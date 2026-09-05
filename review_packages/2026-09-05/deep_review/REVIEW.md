# Deep pre-outreach correctness review

5 September 2026. Reviewed release base: `bfa87464`. Scope: the consolidated stable-core, asymptotic and assignment papers. Earlier PXC conjectures and superseded portfolio claims are not endorsed by this review. No outreach was sent.

**Verdict: no error was found in the three central results after independent reconstruction and adversarial checking. Confidence in their correctness as stated is high.** The review did find a literal domain defect in a secondary lemma, imprecise appendix wording, and a reproducibility defect affecting all three runners. These have been repaired. Neither successful testing nor this internal assessment establishes novelty, significance, or absolute correctness.

Three fresh reviewers examined the papers separately without accepting historical PASS records as evidence. They reconstructed proof obligations, checked boundary cases and source hypotheses, and wrote new encodings. A coordinating review examined the shared verification lifecycle and added a different solver with independently checked finite proof objects. The detailed reports retain the reviewed input hashes and pre-repair line anchors; their artifact links have been relocated for delivery.

## Findings and disposition

| Finding | Consequence | Disposition |
|---|---|---|
| Empty coalition was not explicitly excluded from the appendix domination lemma | Its inequalities become vacuously true at the empty coalition, contradicting the definition of domination | Restricted the introduction and lemma to nonempty coalitions. The main stability proof and arrangement computation already use nonempty coalitions. |
| Appendix called relative halfspace intersections ambient halfspaces and compressed the empty-face case | Literal wording obscured the compact-polytope argument | Wrote `D_S=I intersect C_S`, described complements relative to I, and explicitly set D_S empty for an empty tight face. |
| Scientific dependencies imported before RUNNING was written | A command could exit with an import error while an old result file still said PASS | Moved scientific imports behind lifecycle initialization in all three runners. Ten missing-dependency probes now persist FAIL; six direct probes observe RUNNING before the first import. |
| Additive-ray proof compressed its computational contribution | Readers could mistake a certified affine calculation for a fully displayed hand calculation | Identified the finite exact certificate, endpoint/slope checks and separate boundary checks. The independent review supplies the full admissible-collection table. |
| New proof-checking harness initially relied on Ethos reporting `correct` | An empty signature-only file also receives that response | Added an explicit final-false gate. Added an explicit disjoint matching certificate for the triple value. The audited current proof files contain final contradictions. |

The last finding concerns this review's new harness, not a defect in the previously released papers. The harness initially also encountered ordinary serialization errors, which were corrected before any result was accepted. No failed or timed-out attempt is counted as a passed mathematical query.

## Mathematical conclusions

**Stable core.** The direct proof genuinely handles every imputation: five pair projections force all but one discrepancy, and strict domination by one of two triples eliminates either sign. The entire core is proved to be the segment, rather than assumed from its generators. The new all-coalition encoding agrees with this proof; a pairs-only negative control admits an outside-core point.

The published procedural definition was checked separately from its terminal claims. For the six-player witness the final efficient PES allocation is `(3/2, 1/2, 1, 1/2, 3/2, 1)`. Coalition `{5,6}` receives `5/2`, below its worth `3`. Thus the counterexample is not an artifact of confusing intermediate claims with the final solution. The domain allows nonzero singleton values. The six-player minimum uses the verified statement and normalization reduction of the published low-dimensional stable-core theorem; its long proof was not independently rebuilt. See [the full stable-core review](stable_core/REVIEW.md).

**Asymptotic separation.** The overlap argument, compact-convex full-selector uniqueness, complementary-coalition equalities identifying the entire core, Fibonacci elimination, all-n admissibility and asymptotic squeeze all survive reconstruction. In particular the claimed first-order limit `n(2-s_n) -> 2` is supported; an exact finite-n optimum or second-order coefficient is not established. Hypothesis-removal controls demonstrate why nonnegativity, convexity and the whole-core argument cannot be dropped. See [the full asymptotic review](asymptotic/DEEP_AUDIT.md) and [proof obligations](asymptotic/PROOF_OBLIGATIONS.md).

**Assignment.** The half-domination proof works for general graphs with nonempty core, including fixed zeros and nonbipartite tight edges. The strengthened finite bound applies to every minimax point and the examples attain the stated player-count extrema. The triple construction has a certified integral matching value, a nonempty entire core with unrestricted asymmetric roots, and unique full selectors. The additive benchmark and padding argument also survive. No replacement of the entire core by a symmetric slice or generating hull was found. The rational-input scope of the earlier algorithmic deduction is retained; the elementary proof supplies the real-valued theorem. See [the full assignment review](assignment/PROOF_REVIEW.md).

## New completed evidence

| Check | Actual completed scope |
|---|---|
| Stable additive ray | 37 open parameter cells, 37 finite boundaries, 24,934 affine comparisons; unbounded interval checked by slopes |
| Stable arrangement | 20,349 candidate bases, 230 distinct intersections, 104 imputations, 102 exact outside-core dominators |
| General asymptotic realization | All 66,066 binary matrices through order four; 543 positive inverse-vector cases; 20 representative complete raw-core checks |
| Generic overlap and uniqueness falsification | Overlap n=2..10; sorted-midpoint uniqueness n=2..5; every completed query UNSAT |
| Additional Fibonacci checks | Four additional raw coalition cases; exact determinants through m=40; logarithm endpoints through L=128; integer representations through n=10^60 |
| Independent graph selectors | 842 graph inputs: 792 positive nonempty cores, 47 correctly empty cores, three zero-value controls; separate sorted-rank optimization and violation queries |
| Assignment extensions | 14 raw triple cases up to 192 players; eight additive cases; 9,995 arithmetic padding counts |
| Verification fault injection | 16 bad solver outcomes rejected; 24 lifecycle, scientific-failure and help controls passed |
| Different solver and proof checker | 16 cvc5 UNSAT results with trust disabled and Ethos-checked CPC proofs; one pairs-only SAT control |
| Revised artifacts | Fresh scientific replays for all three runners; clean extraction/replay of all three revised ZIPs; stable-core TeX build and 11-page visual inspection |

Matrix counts are not counts of distinct raw games; padding counts are arithmetic checks, not thousands of raw-core solver runs. The universal overlap search toward n=32 timed out; only the completed n<=10 cases are claimed. The mathematical all-parameter arguments remain essential.

## Certificate and reproducibility boundaries

[The independently reviewed encoder](root/certify_raw_claims.py) imports no package scientific code. Z3 prints expressions; cvc5 is the solving backend. The retained [proof record](root/certificates/results.json) records formulas, proofs and tool hashes. The three fixed asymptotic instances and two triple instances are bounded corroborations, not formalizations of their parameterized families.

Ethos checks a contradiction from emitted CPC premises. Their semantic identity with the saved SMT assertions is not independently mechanically certified. One complete triple premise list was manually inspected, and all 16 assumption counts and final contradictions were checked. Python exact feasibility checks and conventional arguments supply the stated interfaces and reverse core inclusions. The encoder, parser, signatures and checker remain trusted components. This is stronger evidence than replaying one solver, but is not end-to-end proof-assistant certification. See [the interface review](assignment/CERTIFICATE_INTERFACE_REVIEW.md).

The repaired runners invalidate prior success after standard-library startup, argument parsing and output initialization. They cannot promise a persisted status when the interpreter cannot start, the entry file cannot parse, or the destination is unwritable; an abrupt kill can leave RUNNING. The [runner report](runner_fixes/RUNNER_FIX_REPORT.md) and before/after records preserve the precise guarantee.

Detailed reports are preserved as reviews of the frozen pre-repair inputs. Their scientific evidence is unchanged. Historical per-lane manifests record those original snapshots; the enclosing release manifest identifies delivered bytes. Independent scripts use their own directories for outputs. Run them from a scratch copy with their documented dependencies. The proof generator requires local cvc5/Ethos/signature paths, configurable with `COOPGT_PROOF_TOOLS`; tool binaries and third-party papers are not redistributed.

## Residual uncertainty and recommendation

There is no currently identified theorem defect requiring a research redesign. The remaining material uncertainty is external: priority, specialist interpretation, and whether the results are important enough for the intended venues. Some original legacy texts and the final 2025 population-monotonicity article remain incompletely accessible, as the source ledgers disclose. The stable-core lower bound also retains an ordinary published-theorem dependency.

Keep the three focused papers and their qualified claims. Do not revive superseded PXC targets or expand the program on the strength of this internal audit. The repaired packages are ready for specialist correctness and priority assessment when outreach is authorized. All existing requests remain unsent; no human assessment has been received.
