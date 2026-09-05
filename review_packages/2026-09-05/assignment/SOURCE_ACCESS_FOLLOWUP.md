# Santamaria Riba thesis: assignment priority comparison

**Historical retrieval layer:** the later deep priority review supersedes current-access and novelty assessments here. See `PRIORITY_REVIEW.md` in each package and `priority_review/REVIEW.md` at release root. Full final2025 population text and the 2008 segment paper are now inspected.


**5 September 2026.** Inspected the substantive theoretical, implementation, validation, experiment and conclusion sections of Lluc Santamaria Riba's *Implementation and Experimental Analysis of Leximin Fair Core Imputations for the Assignment Game*.

**Source:** [immutable primary TeX](https://github.com/Lluc24/leximin-docs/blob/3e201fa6064532fa24375d3cb70442240aa55572/memory/final-milestone/thesis.tex), repository commit dated 23 June 2026. Verified local 110,103-byte blob: `152a1ba66799e5b59ba37321732fa0637467c612`; SHA-256: `5ce4d4b0d3223528187be323432f3147bab38d5f76fc86c641badf298824365d`. README says June 2026; TeX cover line 131 says 01/07/2026. Neither establishes an official award date. These are source-line anchors; the compiled PDF was not inspected.

**Conclusion:** The thesis contributes an implementation and computational study of Vazirani's existing leximin algorithm. It does not state/prove the coordinate-ideal half guarantee, sharp normalized pair distance `k/(k+1)`, or a pair/triple comparison. This conclusion rests on the substantive scope below, not keyword absence alone.

- **Lines 347–397, background:** bipartite assignment cores and essential-player leximin. Omitting nonessential players agrees with our all-player convention because their payoffs are fixed at zero.
- **Lines 565–658, algorithm:** unit-rate rotations, clock and freezing reproduce prior algorithmic ingredients. The `W_max/2` theorem at line 651 concerns clock termination time, not half of an individual core maximum. Keep the package's half-guarantee attribution to Vazirani.
- **Lines 662–785 and 1058–1120:** modular Python implementation with rational combinatorial operations, degeneracy handling, and a progressive-LP reference computing the same full leximin point. These are existing implementation contributions; no first-implementation claim is appropriate for our verifiers.
- **Lines 1009 and 1519–1536:** reported 1,320 benchmark instances; reference agreement uses tolerance `10^-6`. Line 1530 identifies the experimental metrics as runtime and memory, not payoff-ideal ratios or cross-selector distance.
- **Lines 1789–1818, conclusions:** outputs are implementation, tests, trace and benchmarking. **Leximax implementation remains future work at line 1812.** No three-sided extension is supplied.

Replace the old thesis access gap with “primary TeX inspected; PDF uninspected.” Preserve Quint/Lucas access gaps and specialist-review status **PENDING**. This narrows one source-specific uncertainty; it neither certifies novelty nor independently validates the thesis code. No packages were edited or contacts made.
