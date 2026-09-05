# CoopGPT: correctness review and contribution inventory

Review date: 5 September 2026. Source checkout: `codex/coopgt-recovery-20260904`, starting at `842dd6cdae6f135eacb217812d72f38b873c3d37`.

The research has produced several substantial theorem candidates. The current central asymptotic, assignment, stable-core, and carrier results survive this fresh review. The archive as a whole is **not uniformly correct or ready to circulate**: it contains a false normalization claim, incomplete verification wrappers, abandoned conjectures still described as open, and a proposed attainment argument whose proof is incomplete. Those distinctions matter more than the number of recorded PASS messages.

This review repairs the identified local errors and records the remaining limits. It is an internal mathematical and computational audit, not external peer review, a proof-assistant formalization, or a guarantee of novelty. No journal publication, arXiv posting, or identified independent specialist endorsement was established by the recovered record. Historical references to publishing often mean a Git push or a prepared release archive.

## What was traced

All available history pages were retrieved for **CoopGT** (417 unique turns, task `019fb8b2-bedb-78d0-8595-74a4c0d9befc`) and **Disprove cooperative game theory monotonicity conjecture** (157 turns, task `019f9f19-e54f-7642-9fa5-7e22191525a1`). Their 574-turn index is preserved in [history_index.json](history_index.json). The index contains selected, explicitly truncated final excerpts; historical assertions were treated as leads, not proof. The current recovery work, commit history, manuscript sources, and verification artifacts supplied the remaining provenance.

Every available historical page was retrieved and the substantive trajectory was tracked. This does not mean every old tool-output byte or every auxiliary lemma in the 405-page manuscript collection was independently reverified. Unrelated spectral, gravity, graph-conjecture, and EFX projects elsewhere in the repository are outside CoopGPT's cooperative-game portfolio.

## The physical manuscripts

There are **10 current manuscript files, totaling 405 pages**. Versions, arXiv copies, and intermediate releases are not additional papers. In particular, the two four-page assignment notes are incorporated into the eight-page comparison; papers 3 and 5 also retain large amounts of archival material.

| Artifact and current title | Pages | What it contributes; current disposition |
|---|---:|---|
| [Paper 1: Coalitional monotonicity and the core: minimal impossibility, an exact-games escape, and the boundary of surplus-distributor solutions](../paper/main.tex) | 31 | Minimal family obstructions, exact-game feasibility results, and counterexamples to proposed selectors. Mixed research portfolio; does not solve existence of a coalitionally monotone core selector on all exact games. Several background impossibilities and candidate-rule precedents require careful attribution. |
| [Paper 2: Core stability does not imply egalitarian stability: a sharp six-player counterexample](../paper2/main.tex) | 12 | A stable core that fails procedural egalitarian stability, sharp at six players using the published small-player positive result. Clear standalone candidate tied to an explicit literature question. |
| [Paper 3: The normalized Lmin core selection on exact games](../paper3/wrapper.tex) | 120 | Archive of the four/five monotonicity threshold, the six/seven carrier threshold, boundary geometry, credal results, and failed approaches. Several extractable results; not a focused 120-page submission. Normalization wording corrected in this review. |
| [Paper 4: Balanced transport at the egalitarian core: a complete boundary phase diagram](../paper4/threshold.tex) | 27 | Normal-cone and balanced-transport framework, sharp poorer/richer boundary phase diagram, sparse witnesses and related quantitative statements. The coherent structural paper extracted from paper 3. |
| [Paper 5: Maximal divergence of the leximin and leximax core selections in exact games](../paper5/divergence.tex) | 183 | Finite extremal values, six-player equality classification and certificates, constructions, and a long PXC research history. Valuable archive with stale open-problem language; should be rewritten around the later sharp result. |
| [Paper 6: Boundary partitions at the leximin core: a two-parameter characterization](../paper6/partition.tex) | 12 | Exact feasibility of partition types `(p,q)`: `p,q>=1` and `p+q>=4`. Main hand proof survives review. Natural companion to paper 4; auxiliary frontier census not rerun here. |
| [Sharp asymptotic separation of opposing egalitarian core selections](../paper5/asymptotic_constant_two/sharp_asymptotic_separation.tex) | 4 | Exact first-order deficit constant 2 for unrestricted exact games. Completed all-parameter theorem; the strongest completed extremal result in the portfolio. |
| [Sharp disagreement between egalitarian core selections in assignment games](../paper5/assignment_separation/sharp_assignment_separation.tex) | 4 | Sharp finite pairwise distance bound and individual protection. Superseded as the preferred presentation by the comparison below; the half guarantee has prior-art implications. |
| [Three-way assignment can separate fair core selections maximally](../paper5/three_sided_separation/three_sided_separation.tex) | 4 | Explicit sparse, bounded-value three-sector games approaching maximal selector disagreement. Incorporated into the comparison below. |
| [Fair core selections: a sharp boundary between pairs and triples](../paper5/assignment_comparison/pairs_and_triples.tex) | 8 | Current consolidated assignment paper: finite graph bound, triple construction, additive benchmark, and priority qualifications. Best single entry point for this branch. A local maximum/witness wording error is corrected in this review. |

## The distinct contribution families

### 1. Stable core versus egalitarian stability

Paper 2 supplies a six-player core segment, a direct von Neumann–Morgenstern external-stability argument, and a procedural egalitarian allocation outside that core. The fresh review checked the proof, not only the witness output. The additive-shift mechanism explains why core geometry and core stability can remain unchanged while procedural egalitarian stability changes. The manuscript also gives a polyhedral arrangement approach to the general core-stability decision problem; this should not be advertised as the first algorithm without a separate priority review.

The original campaign claimed both an exact-game and a stable-core counterexample were new. That was corrected during the earlier work: **Mauri's 2017 thesis already contains an exact game without egalitarian stability**. The stable-core six-player construction is the meaningful remaining candidate contribution. Dietzenbacher's published *Monotonicity and Egalitarianism* explicitly asks the two questions and establishes the relevant small-player positive results. [Published article](https://doi.org/10.1016/j.geb.2021.03.006), [Mauri thesis record](https://repositori.urv.cat/estatic/TDX0011/es_TDX2707.html).

### 2. Sharp unrestricted separation

For singleton-normalized exact games with positive total `T`, write `rho=||Lmin-Lmax||_1/T` and let `s_n` be its supremum over `n` players. The new short note proves

\[
\lim_{n\to\infty}n(2-s_n)=2,
\qquad 2-s_n=\frac2n+O\!\left(\frac{\log n}{n^2}\right).
\]

The universal side is stronger than a game-specific statement: overlap is at least `T/(n-1)` for opposing maximin/minimax points in a compact convex nonnegative constant-sum set. The constructive side gives exact games whose **entire cores** are explicitly characterized Fibonacci segments. The proof works for all sufficiently large player counts, not just a favorable subsequence. The old PXC151 coefficient `3+2 sqrt(2)` remains a valid construction coefficient, but is superseded as a proposed sharp constant.

The finite program contains `s_5=1/2`, `s_6=2/3`, and two six-player equality profiles up to relabeling. This review freshly replayed the six-player interface and proofs; it did not repeat the complete five-player census. Those finite results and the asymptotic theorem belong in one focused extremal paper, with the PXC archive retained as supporting material.

### 3. A sharp boundary between pairwise and three-way assignment

For matching games on graphs with nonempty cores, the full leximin allocation gives each player at least half their maximum attainable core payoff. If a positive optimal matching has `k` edges, its normalized distance from any minimax allocation is at most `k/(k+1)`. The sharp maximum over `n>=4` players is `floor(n/2)/(floor(n/2)+1)`; for two or three players the selector distance is zero.

For genuine three-sector unit-capacity assignment, the construction instead approaches distance **2**, the absolute upper bound. It has `n=9(L+R)+12` players, only `12(L+R)+9` positive teams, team values in `{1,2,3}`, an integral optimum equal to the covering optimum, and an explicitly characterized entire core. The all-parameter proof establishes the full selectors. This is a worst-case disagreement between efficient allocations; it does not establish welfare loss, typical-market behavior, or empirical unfairness.

For the additive equal-sector subclass, the core is a shift simplex, giving an individual one-third guarantee and a sharp selector-distance supremum of `4/3`. This benchmark helps explain the role of interaction structure, but is a shorter supporting result.

Priority matters: the **bipartite half guarantee follows from invariants of Vazirani's earlier algorithm** and must not be promoted as an independently new headline. The finite quantitative distance theorem, graph extension, and bounded sparse triple construction remain candidates requiring specialist priority review. The comparison's existing priority matrix also explains exclusions from particular three-sided subclasses; these exclusions do not prove novelty against all earlier work. [Vazirani, version 6](https://arxiv.org/html/2402.11437v6), [current priority matrix](../paper5/assignment_comparison/PRIORITY_MATRIX.md).

### 4. The sharp carrier threshold: six versus seven

At any core reference `psi` and for every proper nonsingleton target coalition `S`, the carrier slack margin `gamma_S(psi)` is bounded above by the greatest feasible gain `eta_S(psi)` that weakly improves every player in `S`, for **every exact game through six players**. A seven-player exact game violates this inequality even at normalized Lmin.

The rank argument reduces the difficult six-player case to three positive residual weights. The seven-player failure has a short coalition-incidence identity and a rational staged Lmin calculation. Both arguments survived independent review. The written proof still cites an earlier five-player computation; [the carrier audit](asymptotic/CARRIER_AUDIT.md) supplies a dummy-player reduction that removes that computational dependency for exact games. The separate total-balancedness strengthening has not thereby been verified.

This is a real structural threshold, distinct from coalitional monotonicity, which can already fail at five. It could be extracted into a compact paper or combined with the monotonicity threshold if the motivation is made clear.

### 5. Normalized Lmin and monotonicity

The project proves positive behavior through four players and sharp five-player failures for the normalized Lmin rule on exact games, including proper-coalition and grand-coalition changes; singleton bumps have their own positive theorem. Fresh independently coded checks reproduce the main five-player witnesses. The through-four theoretical bridge was inspected; its entire historical certificate release was not rerun.

Failure of this particular selection **does not settle whether some other coalitionally monotone core selector exists on all exact games**. Likewise, feasibility for every three-game family through five players is a finite consistency result, not a global selection theorem. Paper 1's surplus-distributor and permutation examples are useful counterexamples to proposed rules, but each needs a precise prior-art comparison before being called a new contribution.

### 6. Boundary geometry and partition structure

Paper 4 characterizes a slack richer suffix at Lmin. With `m` poorer and `h` richer players, it is possible exactly when `m>=m_min(h)`, where `m_min(1)=4`, `m_min(2)=m_min(3)=3`, and `m_min(h)=2` for `h>=4`. The normal-cone/balanced-transport proof explains the mechanism and gives sparse certificates. The review checked the principal proof structure and exact family examples; it is not a fresh audit of every one-packet or projective-plane auxiliary statement in the archive.

Paper 6's partition condition `p,q>=1`, `p+q>=4` and its two construction families also survive review. The claimed general framework builds on earlier exact-partition/Lorenz results; the phase diagram and quantitative refinements are the candidate additions. The two papers naturally form one research line.

### 7. Credal and supporting results

Paper 3 contains a credal-set translation: a three/four threshold for compatibility of fairness criteria, Lorenz/entropy consequences, and quantitative defect estimates. This review inventoried those statements but did not independently reverify that late appendix. They may support a separate imprecise-probability paper after a dedicated source and proof audit. They should not be counted as a finished externally validated paper today.

Other useful outputs include exact rational selectors, full-core closure and generator compression, mutation controls, SMT interfaces, and independently checkable CPC certificates. The `n+2` generator observation preserves a chosen selector pair, **not necessarily the whole original core**, and proves neither fixed-player attainment nor uniform constant-size compression. PXC91's completion monotonicity, PXC92's staged tangent criterion, and PXC98's explicit six-player obstruction remain useful scoped results; the latter's claimed universal five-player minimality was not re-enumerated here.

## Errors found, repairs, and unresolved statements

| Finding | Consequence and treatment |
|---|---|
| Paper 3 identifies normalized Lmin with ordinary Dutta–Ray on every convex game. | False with unequal singleton floors. For `v(1)=10,v(2)=0,v(12)=12`, normalized Lmin is `(11,1)` but ordinary Lmin/Dutta–Ray is `(10,2)`. Restricted the claim to singleton-normalized games and explained translation. The sharp small-player theorem already uses normalization correctly and is unaffected. |
| Paper 4's auxiliary exact-bump-window proof chooses a proper coalition that becomes the grand coalition when only one outsider remains. | Added that missing case: nonnegative outsider payoff gives `x(S)<=v(N)`, hence the same bound `alpha_ex(S)<=g(S)`. The claimed inequality and main phase theorem remain valid. |
| Three six-player certificate wrappers accept deleted/empty/duplicate case rows; assertions also disappear under `-O`. | Real validation defects, including empty-case PASS under ordinary Python. Replaced removable assertions with explicit guards; enforce complete case sets, declared/actual/derived counts, hashes, statuses, direction menus, and complete recorded ablations. These are record-integrity checks; the wrapper does not itself rerun Ethos. |
| Two seven-player carrier scripts lack optimization guards despite a broad historical harness claim. | Added early rejection of `-O`, `-OO`, and `PYTHONOPTIMIZE`. Normal scientific outputs are unchanged. |
| The legacy paper-5 release mixes many assertion-based scripts. | Added an interpreter preflight that rejects optimized Python before any release stage. This is not a migration of every historical verifier to optimization-safe checks. |
| The asymptotic program asserts `O>=mu*|supp(z)|`. | False; positive coordinates may be below `mu`. Replaced it with the valid coordinatewise inequality `min(x_i,z_i)>=(mu/M)z_i`, yielding the intended weaker bound `O>=mu*T/M`. The new sharp theorem did not depend on the false support argument. |
| A proposed fixed-`n` selector-chamber proof claims linearity/closedness too quickly. | Joint primal/dual terms can be bilinear; strict non-forcing strata do not automatically give a closed weak-polyhedral graph. Marked fixed-`n` attainment and rationality **unproved by this note**. No counterexample to attainment is claimed. |
| Paper 5's old matching upper-bound target and universal gluing frontier are still described as open in places, including `divergence.tex` near line 299. | Later counterexamples refute that target. Added a current-status override and an archival README. The 183-page frozen manuscript/release is retained as history and is not certified as current exposition. |
| The comparison says a maximum is attained at a small positive root witness. | The point witnesses a value greater than one; it need not maximize it. Corrected the sentence. The subclass exclusion remains valid. |
| Paper 6's README still says the prior-art pass is pending. | Updated to reflect its August 9 citation pass. This does not assert confirmed novelty. |

The three affected PDFs were rebuilt: paper 3 (120 pages, changed text on page 4), paper 4 (27 pages, corrected proof and resulting text flow on pages 19–24), and the comparison (8 pages, changed text on page 7). Changed pages were rendered and visually inspected; other-page extracted text and all page counts match the originals. The frozen paper-5 PDF was not silently rewritten.

## Fresh evidence and its limits

| Area | Fresh verification in this review |
|---|---|
| Six-player extremal theorem | 1,332 semantic-interface queries; explicit negative mutation control; all 15 strict and 15 equality formulas freshly UNSAT in cvc5; all 30 saved CPC proofs freshly accepted as `correct` by Ethos. The human counterexample-to-formula map was separately read and checked. |
| Unrestricted sharp theorem | Conventional upper/lower proof review; 33 exact calibration cases and three negative controls, including full-core closure, Fibonacci segments, and the three-generator family. Archived outputs reproduced. |
| Pairwise assignment | All 255 nonzero `2x2` matrices with weights `0..3`; 510 independent explicit-sort lexicographic improvement queries; individual maximum, minimax-face, attainment, and mutation controls. |
| Triple assignment | Six independently reconstructed raw games up to 192 players; both whole-core inclusions; uniqueness of floor and ceiling optima; matching/cover certificates; 987 player-count padding checks. Replayed all binary `2x2x2` cases, fixed-seed `3x3x3` cases, and additive/graph extension checks. |
| Early papers | 37 new independently coded exact checks for central examples and families, plus bounded hand-proof review. See [early-paper audit](early/EARLY_PAPER_REVIEW_2026-09-05.md) for scope. |
| Carrier theorem | Rank/duality/exceptional-orbit hand argument; three fresh exact replays; both witness scripts reproduce outputs after guards and reject eight optimized-mode invocations. |
| Harness repairs | Valid normal and optimized record-wrapper runs plus corrupted statuses, hashes, bytes, counts, case coverage, menus, and ablation records. Mutation tests demonstrate the original false PASS behavior and its removal. |

The evidence directory retains review reports, executed scripts, hashes, JSON outputs, and build records. Some executed scripts retain their original absolute scratch paths as provenance; these are audit records, not a portable one-command release.

Limits: the complete historical 66-stage release was not rerun; neither were all five-player arrangement cells, the 1,489-case carrier census, every PXC branch, the complete credal theory, or every auxiliary frontier result. The assertion inventory finds 273 Python files containing 1,873 assertions; that is an archive inventory, not a finding that all are unsafe proof gates. Modern explicit checks and guarded assertion scripts differ from unguarded legacy scripts. No claim is made that all 405 manuscript pages have been exhaustively certified.

## What the history says about research direction

| Period | Research transition | Assessment |
|---|---|---|
| July 22–25 | Selector counterexamples, exact-game escape, then stable-core example; first three drafts | Several real findings, initially overbroad novelty claims. |
| July 31–August 4 | Prior-art correction; five-player Lmin failure, six/seven carrier threshold, boundary/credal work | Productive extraction of sharp statements from a failed global monotonicity strategy. |
| August 6–10 | Papers 5 and 6; finite separation and six-player certificates | Strong finite results and substantial reproducibility infrastructure. |
| August 12–24 | Large PXC sequence of packet, gluing, transport, and spectral reformulations | Much of this was a local-maximum phase: formulations multiplied while the same universal bottleneck remained unresolved. Scoped obstructions have value, but PXC count is not theorem or paper count. |
| Late August | PXC141–146 refute the old target; PXC151 improves construction coefficient | Productive falsification. The previous matching upper-bound target should have been retired consistently across prose. |
| August 30–September 5 | Recovery, sharp constant 2, pair/triple assignment, consolidated comparison and priority downgrade | A material move beyond the old mechanism search. The asymptotic constant is settled; assignment adds a recognizable economic model. |

PXC152 is mentioned in recovered messages, but no corresponding released artifact was located. Its historical claim is not an independently recovered contribution. The newer compact convex-set theorem provides a written and reviewed replacement. The historical fixed-player attainment claim is also excluded from the established-results list.

My assessment is that the project is now on a better track, but “field-level breakthrough” remains unestablished. The strongest evidence is a small number of sharp, explainable theorems, not the volume of the archive or repeated internal approval. The next useful work is consolidation and external mathematical engagement:

1. Prepare the stable-core six-player paper around the exact published question, with the Mauri precedent explicit.
2. Use the eight-page pairs/triples comparison as the assignment submission candidate; have a specialist check priority, especially the sharp finite bound and triple construction.
3. Rewrite the extremal paper around the constant-2 theorem plus the finite five/six-player results. Move the 183-page exploration history out of the main argument.
4. Treat boundary phase/partitions and the carrier threshold as the next structural package or two focused notes. Audit credal results separately before promoting another paper.

After those packages are stable, the strongest new research direction is to explain **when and how often** the triple pathology occurs: a structural condition yielding quantitative protection, and robustness under perturbation, would add more economic content than another isolated mechanism atlas. This is a recommendation, not a claim that those results already exist. The global exact-game selector-existence question remains a separate open research objective.

## Supporting audit files

- [Early papers](early/EARLY_PAPER_REVIEW_2026-09-05.md)
- [Unrestricted asymptotic and supporting lemmas](asymptotic/UNRESTRICTED_ASYMPTOTIC_AUDIT.md)
- [Carrier threshold](asymptotic/CARRIER_AUDIT.md)
- [Assignment theorem and code review](assignment/ASSIGNMENT_CORRECTNESS_REVIEW.md)
- [Verifier repair review](wrapper/WRAPPER_REVIEW.md)
- [Complete retrieved historical index](history_index.json)
- [Integration and evidence manifest](integration_manifest.json)
