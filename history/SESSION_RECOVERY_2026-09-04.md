# CoopGT session recovery

Source task: codex://threads/019fb8b2-bedb-78d0-8595-74a4c0d9befc (CoopGT).
Recovered into the replacement conversation on 2026-09-04.

## Consolidated comparison and revised priority — 2026-09-05

The pairwise and three-sided results are consolidated in `coopgames/paper5/assignment_comparison/pairs_and_triples.tex` and its eight-page PDF. Common definitions use unit capacity, integral matching worth, nonempty entire cores, full selectors and all-player counts. The graph result extends to nonbipartite nonempty-core games; complete additive triples with equal sector sizes have the one-third guarantee and sharp distance supremum 4/3. The unrestricted triple supremum remains 2.

The priority investigation materially changes attribution: the BIPARTITE half-core-maximum guarantee follows as a short corollary of Vazirani v6 Algorithm 1's clock, speed and freezing invariants. It should no longer be positioned as an independent new fairness discovery. The sharp finite graph distance is a potentially new quantitative refinement; the sparse bounded-value triple construction and combined comparison are the strongest candidate contribution. The new `PRIORITY_MATRIX.md` supersedes earlier novelty wording without changing preserved proof checkpoints.

The audit inspected additional primary sources including a 2026 coordinate-extrema theorem. Explicit mixed-difference and sector-maxima obstructions exclude the constructed array from the inspected pair-additive and supermodular/local-monotonicity subclasses. Six graph, eight additive and four source-exclusion checks passed; source and proof audits agree. Original Quint and Lucas full texts remain inaccessible, and no novelty or field-level significance certification is claimed. The specialist-review request is local and unsent. No publication, external messages, purchase or remote push occurred.

## Completed three-sided assignment goal — 2026-09-04

The next structural goal is resolved internally: standard three-sided assignment games with nonempty entire cores have sharp supremum 2 for full leximin versus full leximax-min normalized L1 distance, already with triple weights in {0,1,2,3}. The explicit recurrence family has n=9(L+R)+12, T=3(L+R+2), and rho=2[((R+2)2^L−1)]/[(2^L+2)(L+R+2)]; R=L² gives rho→2. Optimized parameters give an all-n deficit O(log n/n). No positive dimension-independent fraction of a player's maximum core payoff is guaranteed by leximin. A separate coincident-selector family establishes that individual failure alone does not imply large disagreement.

See `coopgames/paper5/three_sided_separation/README.md`, the four-page note, expanded proof, exact verifiers, dated primary-source audit and specialist packet. The entire core, integral matching optimum and full selectors are proved, and independent raw checks pass through 192 players. The complete portable replay and PDF inspection passed. This identifies a structural boundary with the two-sided half-guarantee and supremum 1. Prior checkpoints `99e6e08499b945c97c8533dc526abcc8065ff80b` and `2466be6fe9237e5c9ab64a047de2aa5de05ea01e` are preserved unchanged.

External correctness, novelty and significance remain unverified; the original Quint and Lucas full texts were unavailable in the bounded audit. No external messages, publication or remote push occurred. The recommended next direction is to consolidate the pairwise/three-way comparison and resolve priority; a sharp finite-n three-sided rate is a separate secondary question.

## Completed assignment-game goal - 2026-09-04

The next authorized goal has now been resolved internally as well: for n>=4, the exact maximum normalized L1 distance between full leximin and leximax-min in arbitrary weighted bipartite assignment-game cores is floor(n/2)/(floor(n/2)+1); for n=2,3 it is zero. More strongly, leximin gives every player at least half their payoff in every other core allocation, and the finite bound holds against any minimax core allocation. Identical-row complete markets with weights 1 and 2 attain it. Exact assignment games have coincident selectors, consistent with known pairwise egalitarian results.

See `coopgames/paper5/assignment_separation/README.md`, the four-page manuscript, exact verifiers, dated source audit and specialist packet. Independent conventional proof reviews and the complete portable replay passed. The previous unrestricted exact-game checkpoint `99e6e08499b945c97c8533dc526abcc8065ff80b` remains unchanged. External correctness, novelty and significance review are pending; no external messages or publication have occurred.

## Completed research checkpoint — 2026-09-04

The resumed campaign has now established the full limit n(2-s_n) -> 2, with 2-s_n=2/n+O(log(n)/n^2). A two-generator Fibonacci segment construction and an independent three-generator extension of PXC151 attain the universal constant. The original abstract example's coalition closure is also fully resolved. See `coopgames/paper5/asymptotic_constant_two/README.md`, its four-page manuscript, exact verifiers, and specialist review packet. All 33 finite cases and three negative controls passed. Frozen PXC151 files remain unchanged. External correctness, novelty, and significance review remain pending.

The recovered historical frontier and original next-work list below are retained as provenance; they are superseded by this checkpoint.

## Verified repository state

- Durable worktree: /Users/maxf/projects/economics-research/game-theory/coopgt-recovery
- Recovery branch: codex/coopgt-recovery-20260904
- Base: 059605a05a90981abe25c577f96ca60eaf231864, fetched from origin/codex/sharp-asymptotic-gap.
- Remote PXC151 review branch: 96e9f90ebf8dc6aa9c08694ccb937c5ae176deeb.
- Frozen PXC151 mathematical commit: 8d5947ff7ed80535bbcc0b7fa13d2e44bfcbe564.
- The old /private/tmp/coop-sharp-20260830 checkout no longer exists.
- The restored checkout was clean before this recovery note was added.

## Recovered research frontier

The source conversation reports PXC151's infinite exact-game construction with asymptotic coefficient 3+2 sqrt(2). It reports completion of the 66-stage PXC151 release suite and identical manuscript builds. Those historical checks have not been rerun during recovery. External specialist correctness and prior-art review remained outstanding.

The latest conversation reports a subsequent PXC152 universal minimax overlap bound O(x,z) >= M >= T/n, implying s_n <= 2-2/n and, together with PXC151, 2 <= c_* <= 3+2 sqrt(2). It reports targeted exact checks but ends without a terminal full-release pass or a pushed PXC152 commit. No PXC152 files were found in the restored branch. Treat the mathematical statement as recovered conversation content pending reconstruction and verification, not a recovered release artifact.

The reported supporting argument uses a distribution on the top coordinates of the minimax allocation z. Be precise about quantifiers: for every x there exists a top coordinate r with x_r >= M; the same r need not work for every x.

## Next work

1. Recover or reconstruct the PXC152 proof and exact verifier, audit its hypotheses, and complete its release checkpoint before relying on historical claims of completion.
2. Continue toward c_* = liminf n(2-s_n): sharpen the selector-specific universal constant, find a better infinite family, or prove a useful finite-dimensional extremal reduction.
3. Preserve frozen PXC151 and distinguish conventional proofs, computational evidence, and external review.
4. Respect the campaign's no-go ledger: do not reopen PXC138/PXC140 or PXC147-PXC150 tight skeletons, use padding/direct sums as a construction substitute, or resume generic payoff hill-climbing. Pivot when a proposed lemma merely restates the overlap conjecture.
5. No external messages have been authorized or sent during recovery.

Relevant retained documents: coopgames/paper5/SHARP_ASYMPTOTIC_GAP_PROGRAM.md, SHARP_GAP_CHAMBER_REDUCTION.md, PXC151_GOAL_COMPLETION_AUDIT.md, and PXC151_QUADRATIC_TWO_BLOCK_REVIEW_PACKET.md.
