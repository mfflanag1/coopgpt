# Stable-core paper: hostile mathematical audit, 2026-09-05

The six-player separation survives this audit. The direct core geometry and external-stability proof are correct. The procedural calculation agrees with the published 2021 definition on its unrestricted TU-game domain. Independent exact calculations establish the three claim formulas for every real parameter on the stated ray, including all finite comparison boundaries. A separate reconstruction of the arrangement produces the reported counts and exact dominators.

One literal statement defect needs correction: the appendix's domination lemma does not explicitly exclude the empty coalition, for which its displayed conditions become vacuously true while domination was defined only for nonempty coalitions. This does not affect the main result or the arrangement proposition, which explicitly uses nonempty coalitions. Two further exposition repairs are recommended below; neither presently supplies a theorem counterexample.

This is an internal mathematical audit, not human specialist review or a priority determination. No outreach, package edit, PDF generation, or broad novelty search was performed.

## Frozen target and evidence

Target package: `/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/`.

Reviewed manuscript SHA256: `7a42759aaa6c06096c66e96e19fdc9f9e4a25b6860d218bc68894b1295557675`.

All anchors below refer to that snapshot. Prior PASS records were not treated as proof, and none of the independent calculations imports package code or package witness data.

Independent artifacts in this directory:

- [independent_audit.py](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/stable_core/independent_audit.py): dynamic exact parameter partition, procedural calculations, quantified real-arithmetic stability/core queries, and interval-lemma sign tests.
- [independent_results.json](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/stable_core/independent_results.json): full cell and boundary traces, maxima, claims, class checks, and solver outcomes.
- [external_stability.smt2](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/stable_core/external_stability.smt2) and [core_segment.smt2](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/stable_core/core_segment.smt2): exact quantified counterexample queries.
- [arrangement_independent.py](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/stable_core/arrangement_independent.py) and [arrangement_independent_results.json](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/stable_core/arrangement_independent_results.json): enumeration in five explicit efficiency coordinates, with all 102 rational domination certificates.
- [original_PES_check.json](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/deep_review/stable_core/original_PES_check.json): actual efficient PES allocation, separately from terminal claims.

Commands:

```text
/private/tmp/coopgt-research-20260904/.venv/bin/python /private/tmp/coopgt-deep-review-20260905/stable_core/independent_audit.py
/private/tmp/coopgt-research-20260904/.venv/bin/python /private/tmp/coopgt-deep-review-20260905/stable_core/arrangement_independent.py
```

Arithmetic is `fractions.Fraction`; the independently constructed quantified queries were solved by Z3 5.1.0. These Z3 outcomes are solver corroboration, not retained formal proof certificates. The conventional direct proof is separately reconstructed below.

## Findings and precise repairs

### F1 — low severity, literal false edge case: empty coalition in appendix lemma

Anchors: [coalition introduction, line 652](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/manuscript.tex:652), [lemma, line 671](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/manuscript.tex:671), and [nonempty dominance definition, line 133](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/manuscript.tex:133).

Take the paper's own game, `S=empty`, and `y=A`. Then `F_S=[A,B]` because `v(empty)=A(empty)=B(empty)=0`. All four displayed families in the lemma are empty, hence true. The asserted equivalence therefore says that `A` is dominated through the empty coalition. Under the paper's definition this is false: the dominating coalition must be nonempty.

Repair: write “For a nonempty coalition S” at line 652, or add `S != empty` in the lemma statement. The arrangement proposition already intersects only over nonempty proper coalitions at line 719, so its proof does not call the defective case. This is a statement-domain defect, not a counterexample to the six-player theorem.

### F2 — minor proof wording: relative halfspaces and empty faces

Anchor: [lines 713–721](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/manuscript.tex:713).

The set `D_S` was defined as a set of imputations. It is therefore `I intersect C_S`, where `C_S` is an intersection of open halfspaces in E. Consequently `I \ D_S` is a finite union of sets `I intersect H^-`, not literally a union of whole ambient closed halfspaces. A finite union of nonempty ambient halfspaces is unbounded in positive dimension, whereas `I \ D_S` can be compact. The intended relative interpretation makes the subsequent polytope argument correct.

State the empty-face branch explicitly: if `F_S=empty`, let `D_S=empty`; its nondomination requirement contributes all of I and can be omitted. This removes any need to regard an empty dominated set as an unnamed intersection of open halfspaces. It is a two-sentence proof repair, not a failure of the finite certificate.

### F3 — compressed all-t proof should expose a finite trace certificate

Anchor: [lines 547–557](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/manuscript.tex:547).

“Induction over these strata” does not display the inequalities that show that no other coalition changes a player's fixing time. The cited exact verifier supplies those obligations, and the independent reconstruction below confirms them. Therefore this is not an uncovered parameter regime or a false formula. For a conventionally readable proof, add the admissible-collection table below and a brief statement explaining affine gap certification, or label the all-parameter result explicitly as using its finite exact certificate. The direct fixed-game theorem already has a sufficiently short complete proof.

## Obligation ledger

| Obligation | Manuscript anchor | Verdict and kind of evidence |
|---|---|---|
| TU domain, nonempty stable core, strict gains | 124–152 | Correct; arbitrary singleton values retained. |
| Procedure, progress, termination, terminal collection | 156–185 | Correct; original source matched and invariants reconstructed. |
| Claims oversum excludes PES stability | 187–199 | Correct elementary proof. |
| Finite lower envelope implies exactness | 209–233 | Correct for arbitrary signed generators of equal sum. |
| Monotonicity and superadditivity | 215–232, 307–308 | Correct; nonnegativity needed for monotonicity, not for superadditivity. |
| Additive translations and dominance | 265–284 | Correct without sign restriction. |
| Classical coordinate permutation | 286–301 | Algebraically correct; precise journal antecedent remains uninspected. |
| Core is exactly the displayed segment | 322–351 | Correct direct proof; independent quantified off-segment query UNSAT. |
| First- and second-round fixed-game trace | 357–395 | All maxima, coalitions, and claims independently reproduced. |
| Five complete pair projections | 399–432 | Correct, including individual-rationality bounds. |
| External stability | 434–479 | Correct strict constructive proof; independent all-coalition query UNSAT. |
| Six-player minimum | 481–492 | Valid consequence of matched low-dimensional source theorem and reconstructed large-core implication. |
| Unperturbed endpoint is PES stable | 501–511 | Correct two-round trace; grand coalition included. |
| All-real additive ray | 517–570 | Correct; 37 open cells and 37 boundaries independently certified. |
| Tight-face classification | 652–657 | Correct, including empty faces and coincident endpoints. |
| Interval domination formula | 670–696 | Correct for nonempty S; F1 is a literal empty-S defect. |
| Arrangement vertex equivalence | 698–732 | Correct after explicit relative-set conventions; degeneracies do not defeat rank argument. |
| Reported 21-plane counts | 734–744 | Independently reproduced in E, with all 102 dominators. |
| Five-player exact prior-work calculation | 239–257 | Correct; one-round data freshly matched to Mauri primary text. |

## Reconstruction of the load-bearing mathematics

### 1. Definitions, procedural invariants, and source interface

The game is on all subsets of a nonempty finite player set with `v(empty)=0`. The imputation floor is the actual singleton worth, not zero by convention. The manuscript's explicit nonemptiness requirement at lines 140–142 correctly blocks vacuous stability when the imputation set is empty.

The printed witness has singleton vector `(1,0,0,0,1,0)`. Subtracting these singleton worths gives exactly the unperturbed game w. This is not an innocuous normalization for PES: w is PES stable and v is not. Thus this example does not establish a separation inside the zero-normalized subclass. It does establish the stated unrestricted claim, because the primary definition permits arbitrary singleton values.

The following verifies that the paper's shortened procedure still means the published one.

At any round, fixed players receive the same previously fixed claim in every coalition containing them. Among coalitions containing an unfixed player choose one with the globally largest residual equal share. Every unfixed member of that coalition achieves its individual maximum; every fixed member automatically achieves its fixed maximum; and the coalition is efficient by its residual-share formula. Hence at least one new player is fixed. There are at most n rounds.

A coalition that was previously admissible has all its members fixed, preserves its efficient sum, and therefore remains admissible. This proves nested admissible collections and that accumulating their union, as the manuscript does, equals taking the current union, as the source does.

When a coalition first becomes fully fixed, each newly fixed player's claim is at least that coalition's provisional share. The fixed claim sum is therefore at least its worth. Once fully fixed, that inequality persists. At the terminal round every player's claim is at least their provisional share in every coalition; consequently terminal claims lie in the upper core. Every player belongs to a coalition made tight when the player was fixed, so the claims form an aspiration.

If the grand coalition is terminally admissible, all its provisional shares equal final claims and their sum is `v(N)`. This proves the manuscript's oversum lemma directly. Conversely, if the final claim sum equals `v(N)`, coordinatewise domination of the provisional grand-coalition shares and equality of sums force equality in every coordinate; thus N is admissible. No identification of claims with an efficient PES allocation outside the stable domain is needed.

A stronger independent check used the full efficient PES definition. The witness's maximal terminal admissible coalitions are `135`, `1256`, `1456`; their intersection, the strong claimant set, is `{1,5}`. Keeping these two claims and applying the constrained equal-awards cap `lambda=1` to the other four players gives

`PES(v)=(3/2,1/2,1,1/2,3/2,1)`.

It is efficient, but coalition `56` receives `5/2 < 3=v(56)`. This directly verifies failure of actual PES core selection and removes the possible claims-versus-solution ambiguity.

### 2. Exactness and class membership

For any finite common-sum set Q, every generator q satisfies `q(N)=tau=v(N)` and `q(S)>=v(S)`. Hence each generator is a core point. For each S, one generator attains the finite minimum and therefore attains its core constraint. This proves exactness, including the empty and grand coalitions. The argument never assumes that the core equals the convex hull of Q.

Nonnegative generators are increasing set functions. If `S subset T`, choose a generator minimizing T: `v(S)<=q(S)<=q(T)=v(T)`. For disjoint S,T every q satisfies `q(S union T)>=v(S)+v(T)`, so their minimum does too. Superadditivity in fact holds without nonnegativity. The paper states a sufficient hypothesis rather than an incorrect necessity.

The actual generators are nonnegative and both sum to six. The independent script checked all 729 ordered inclusion comparisons and all 729 ordered disjoint-coalition comparisons, including empty coalitions. These checks corroborate the general proof; they do not substitute for it.

### 3. Additive translation

For `v=w+c`, translating a vector by c translates efficiency, each singleton bound, and every coalition inequality by exactly the relevant `c(S)`. Thus imputations and cores translate, attaining core points translate, and each strict coordinate comparison in a domination witness is unchanged. The affordability inequality also translates exactly. This proves exactness and stable-core equivalence in both directions, including the nonempty-core convention.

Superadditivity is invariant because `c(S union T)=c(S)+c(T)` for disjoint coalitions. Arbitrary signed additive shifts need not preserve monotonicity; the paper does not need such a claim. Its shifts have nonnegative coordinates for every allowed ray parameter.

The coordinate order `(5,2,4,6,1,3)` applied to U and V gives the two printed orthogonal generators exactly. The classical attribution is not load-bearing for correctness because the perturbed geometry and stability have complete direct proofs.

### 4. The core segment

The pair worths are `v(12)=2`, `v(34)=1`, `v(56)=3`; they sum to the grand worth. Any core allocation satisfies these lower bounds and efficiency, so all three are equalities. Singleton rationality then gives

`y=(1+t,1-t,s,1-s,3-u,u)`, with `0<=t,s<=1` and `0<=u<=2`.

Specifically the floors are `(1,0,0,0,1,0)`, so the last pair gives `y5=3-u>=1`, not the incorrect upper range three that zero-normalization would have given.

The core constraints for `23` and `14` become `s>=t` and `t>=s`. The constraints for `135` and `246` become `u<=2t` and `u>=2t`. Thus all core points equal `A+t(B-A)`. Conversely both endpoints are core points and the core is convex. The endpoint values t=0,1 are included.

The independent solver query asserts all 63 coalitional lower bounds and efficiency, and asks for a point not representable as `A+r(B-A)` with `0<=r<=1`. Its result is UNSAT. It does not assume the paper's tight-pair reduction.

### 5. Pair domination and the strict triple step

For each of `12,34,56,23,14`, the two endpoint projections coincide with the endpoints of the subgame imputation segment. They sweep the whole segment because they depend affinely and nontrivially on t. In particular `56` ranges from `(3,0)` to `(1,2)`, which uses the correct singleton floor one for player 5.

If `epsilon=v(P)-y(P)>0`, adding `epsilon/2` to each pair member preserves individual rationality and gives exactly the pair worth. Any two-player efficient individually rational vector automatically lies between the two subgame endpoints, so some core parameter produces precisely this vector. Both gains are strictly positive. No hypothesis of an interior initial imputation is used.

An undominated imputation must therefore satisfy all five pair inequalities. The first three sum to efficiency and become equalities. The last two force the same t for coordinates 1–4, leaving only

`y=(1+t,1-t,t,1-t,3-u,u)`.

If `u>2t`, the midpoint `r=(t+u/2)/2` lies strictly between t and u/2, hence in `[0,1]`. Players 1 and 3 gain because `r>t`; player 5 gains because `2r<u`. Coalition 135 is exactly affordable at every core parameter.

If `u<2t`, the same midpoint lies strictly between u/2 and t. Players 2 and 4 gain because `r<t`; player 6 gains because `2r>u`. Coalition 246 is exactly affordable. Even if t or u is at an allowed endpoint, a nonzero discrepancy supplies a nonempty strict interval. The only remaining case `u=2t` is precisely the core segment.

Internal stability is immediate: if two core points x,y had `x_i>y_i` on a nonempty coalition S, then `x(S)>y(S)>=v(S)`, contradicting affordability. The proof therefore establishes vNM stability with its full strict-gain definition.

The independent quantified solver query asks for an efficient individually rational y violating some core inequality for which there exists no core parameter and no nonempty proper affordable coalition with strict gains for every member. Result: UNSAT. The query includes all coalitions, not just the seven used in the direct proof, and has no pre-coded interval elimination formula.

### 6. Fixed-game procedural trace

Independent exact enumeration of all coalitions gives the first-round maxima

`(3/2,5/4,4/3,5/4,3/2,3/2)`.

Only `15` and `56` are admissible, so players `156` fix at `3/2`. The second-round admissible collection is exactly

`12,14,15,135,56,1256,1456`.

Players `234` fix at `(1/2,1,1/2)`. The resulting claim vector has sum `13/2` versus grand worth six. Every coalition and every individual maximum in the manuscript matches; there is no early-stopping, omitted-fixed-coalition, or tied-maximum discrepancy.

### 7. Sharp six-player minimum

The source's low-dimensional theorem applies to games with a nonempty stable core and at most five players, using the same actual singleton floors and strict-improvement dominance. Although the working paper assumes nonnegative games without loss of generality, its footnote explicitly supplies an additive translation. Stable cores and large cores are both translation-invariant; no transfer of PES stability through that normalization is needed. First infer largeness back in the original game, then apply the large-core implication there. Thus the manuscript's unrestricted sharpness conclusion is valid.

The large-core implication can be reconstructed without treating its source theorem as a black box. Terminal claims gamma are in the upper core. Largeness provides a core point z with `z<=gamma`. Every player belongs to a terminal tight coalition S with `gamma(S)=v(S)`. On each such S, `z(S)>=v(S)=gamma(S)` while `z<=gamma`; hence every coordinate gap on S is zero. These coalitions cover N, so z=gamma. Its grand sum is therefore v(N), giving PES stability.

Residual limitation: I verified the precise statement, definitions, and normalization reduction of the long low-dimensional theorem; I did not independently reconstruct every case in its approximately fourteen-page appendix proof. Sharpness retains that ordinary published-theorem dependency. The upper example, unlike the lower bound, is fully reconstructed here.

### 8. The complete additive ray

All games on `t>=0` have translated stable cores and nonnegative generators. The claim formulas have the following exact admissible traces on the three open parameter intervals:

| Parameter interval | Round 1 | Round 2 | Round 3 |
|---|---|---|---|
| `(0,2/3)` | `56` | `56,135` | `12,14,56,135,1256,1456` |
| `(2/3,1)` | `56` | `15,56` | `12,14,15,56,135,1256,1456` |
| `(1,infinity)` | `15` | `15,56,135` | `12,14,15,56,135,1256,1456` |

These imply exactly the stated new-player strata `56|13|24`, `56|1|234`, `15|36|24`. All admissible collections in the table, not just the claim vectors, were constant across the independently derived open cells. No interior isolated tie changes the strata.

The independent parameter calculation starts with no proposed strata or breakpoints. At each state it forms every coalition's affine provisional shares, subdivides at all roots of individual share comparisons and at roots of fully fixed coalition feasibility, chooses the exact admissible collection on each resulting open cell, and recurses with that collection's fixed players. Every selected maximum is checked against every coalition on the entire cell closure, using both endpoint values for finite cells or the left value and slope for the unbounded final cell. Affine nonidentities have no untested interior equality after this subdivision. Each finite boundary is separately run through the exact numerical procedure from its initial state.

This yields 37 open cells, 37 finite boundary points, and 24,934 generated affine comparisons. The claim formulas agree as affine identities on each open cell and exactly at every boundary. The last cell is `(9,infinity)`, certified by slope signs rather than finite sampling.

At t=0 the trace is `56|1234` and N belongs to the second-round collection. At t=2/3 the second round additionally admits `15`, with claims `(1,2/3,1,2/3,4/3,4/3)`. At t=1 the first round simultaneously admits `15` and `56`, with strata `156|234`; claims are exactly the main witness's claims. Both adjacent formulas agree at their shared endpoints.

Summing the independently checked vectors and subtracting `4+2t` gives `t`, `1-t/2`, and `1/2` in the respective regimes. The second expression is positive throughout `[2/3,1]`; the first is positive for t>0; the third is always positive. The endpoint t=0 is separately stable. Thus the all-real “if and only if” is established, not extrapolated from a finite grid.

### 9. Segment domination formula and all empty/degenerate branches

A coalitional slack along a core segment is an affine nonnegative function of r. Its zero set is empty, the first endpoint, the second endpoint, or the whole segment. Affordability plus core feasibility forces any dominating core point into that zero set. This remains correct if A=B; some listed alternatives then describe the same singleton.

For a fully tight nonempty S, define `q_i=(y_i-A_i)/d_i` when `d_i!=0`. Positive directions impose `r>q_i`; negative directions impose `r<q_j`; zero directions require `y_k<A_k`. With r in `[0,1]`, the necessary and sufficient conditions are `q_i<1`, `q_j>0`, and all cross inequalities `q_i<q_j`. A strict interval exists because all inequalities are strict and there are finitely many. Multiplication by a negative direction reverses the sign, yielding exactly `h_ij(y)>0`, as printed.

The empty-sign branches work: if P is empty, choose r=0 whenever all negative upper bounds are positive; if M is empty, choose r=1 whenever all positive lower bounds are below one; if both are empty, only the zero-direction coordinate inequalities remain. For a genuinely fully tight coalition `sum d(S)=0`, a nonzero direction within S actually forces both signs to occur, but the interval calculation is valid more generally. Endpoint-only domination is precisely strict improvement in each coordinate at that endpoint. An empty tight face permits no dominator at all. The empty-coalition branch is excluded as required by F1.

For corroboration, quantified real arithmetic compared the original parameter-existence formula with the printed inequality formula for all 27 three-coordinate direction patterns in `{-2,0,3}^3`, including all-zero and one-sided patterns. Every symmetric-difference query was UNSAT. These are checks of representative sign cases, not a finite substitute for the preceding algebraic proof.

### 10. Finite arrangement proof, including degeneracies

After the relative-set correction in F2, each nondomination condition is a finite union of weak halfspace inequalities inside I. Finite distributivity gives U as a finite union of closed polytopes cut out by the stated hyperplanes and singleton floors. The imputation set is compact because efficiency and the finite lower bounds imply an upper bound `y_i <= v(N)-sum_{j!=i}v(j)` for each coordinate. The core being nonempty ensures I is nonempty.

Empty pieces can be discarded. If U has an outside-segment point, at least one nonempty polytope piece P is not contained in the segment. If every vertex of P lay in the segment, convexity would contain all of P; hence an outside-segment vertex exists.

This argument does not assume P has full dimension. At any vertex of a polytope described by inequalities in the `(n-1)`-dimensional efficiency space, the active normals span that whole tangent space: otherwise a nonzero direction orthogonal to all active normals would permit sufficiently small displacements of both signs while preserving all finitely many inactive strict slacks, contradicting extremality. Thus `(n-1)` independent active hyperplanes determine the vertex even for a line, face, or singleton piece. Duplicated or coincident hyperplanes do not matter because only an independent subfamily is selected. For the one-player efficiency space the argument is zero-dimensional and the core equals the sole imputation; no outside vertex exists.

If A=B, the direction terms disappear; the domination regions reduce to endpoint coordinate comparisons and the same finite-polytope argument works. If n=2, some ambient hyperplane restrictions to E may coincide or be improper; discard empty or whole-E restrictions and retain genuine hyperplanes. Singleton floors still define a bounded I. The six-player application has no improper restriction and this convention does not alter its count.

A grand-coalition domination cannot occur between efficient vectors with all strict coordinate gains, so restricting the union to proper coalitions loses nothing. The empty coalition contributes nothing by the dominance definition. Hence the vertex equivalence, correctly scoped, survives the boundary audit.

### 11. Independent arrangement enumeration and code assessment

The fresh enumeration restricts every plane to `y6=6-y1-y2-y3-y4-y5` before normalization and deduplication. It therefore verifies distinctness in E, not merely distinctness of ambient equations. It finds exactly 21 planes, 20,349 candidate bases, 8,264 nonsingular bases, 230 distinct intersections, 104 imputations, and only A,B as core arrangement vertices.

Each of the remaining 102 vertices receives a rational dominator generated from the five-pair/two-triple construction above. Every generated point is rechecked against all core inequalities, affordability, and each strict gain. This differs from the package's interval-based dominator constructor. The resulting count corroborates both the numerical assertion and the direct domination mechanism.

The inspected package's mathematical implementations correspond to the relevant obligations:

- [verify_claims.py:26](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/verification/verify_claims.py:26) includes already-fixed coalitions, explicit sum feasibility, simultaneous maxima, and a progress guard.
- [verify_additive_ray.py:117](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/verification/verify_additive_ray.py:117) uses affine closure inequalities; [line 164](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/verification/verify_additive_ray.py:164) partitions comparison roots; [line 243](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/verification/verify_additive_ray.py:243) separately checks finite boundaries. Nonzero affine gaps cannot vanish at isolated interior points of a certified cell. Fully fixed coalitions cannot acquire an unrecorded interior feasibility zero: their claims exceed worth throughout a valid state, and a nonzero affine nonnegative slack cannot vanish in the interior. The independent calculation nevertheless adds such roots explicitly.
- [verify_stability.py:211](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/verification/verify_stability.py:211) certifies its asserted affine core line by tight complement sums and exact rank, then bounds the parameter. Its rejection of coincident endpoints is appropriate to its stated nondegenerate six-player application, even though the theoretical appendix permits a degenerate segment.
- [verify_stability.py:298](/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05/stable_core/verification/verify_stability.py:298) correctly separates empty faces, endpoint faces, and whole-segment faces. In the whole-segment case an endpoint with finitely many strict gains always extends to a one-sided interval of strict gains, so requiring a positive-width parameter interval does not omit an endpoint-only dominator there.

I did not count the alternate permutation/additive replay as an independent theorem. The transformation is mathematically redundant evidence once the invariance is proved. I also did not rerun the shipped wrapper and accept its overall PASS as evidence. Runner startup and stale-result behavior are assigned to the parent review and are outside this mathematical finding list.

## Primary-source checks and residual source limits

The [author-uploaded published Dietzenbacher 2021 text](https://www.researchgate.net/publication/350699095_Monotonicity_and_egalitarianism) was freshly inspected: pp.195 and 197–199 define all-TU domain, procedure, claims, final PES, and PES stability; p.203 Theorem 3.5 supplies the large-core inclusion. Its definitions match the manuscript, including nonzero singleton values.

The [Estévez-Fernández author working paper](https://papers.tinbergen.nl/11086.pdf) was freshly inspected: printed p.4 has the same imputation and upper-core definitions; p.5 gives the nonnegative WLOG reduction in footnote 2; p.9 defines nonempty stable core and states Theorem 4.1 for at most five players. Its long appendix proof is an acknowledged external theorem dependency.

The [Mauri Masdeu institutional thesis](https://repositori.urv.cat/repositori/getDocument/TDX%3A2707?ds=Memoria&mime=application%2Fpdf), *Essays on egalitarianism-based solution concepts for cooperative TU-games*, Example 5, printed pp.40–41, was freshly read. Its two five-player vectors, five maximizing coalitions, and zero maximum-average output match the manuscript. The agreement needed here is solely the one-round computation, not a general equivalence of two different solution procedures.

The precise Shellshear–Sudhölter 2009 journal example was not retrieved in this audit; the institutional thesis endpoint returned a security-check page. The manuscript's historical locator therefore remains a source-access limitation. It does not affect the reconstructed theorem. The 2017 PES full article was not separately retrieved; the published 2021 article prints the complete operative definition and directly states the selector/stability equivalence. No post-2021 novelty or priority conclusion was inferred from this limited access.

## Final assessment

No counterexample to the main six-player theorem, the all-t ray theorem, or the correctly scoped arrangement proposition was found. The principal result has a sound elementary proof and now has independent exact corroboration using different encodings. The actual efficient PES allocation also violates a displayed core inequality, which decisively resolves the procedural-interpretation concern for this witness.

Correct the appendix's empty-coalition quantifier and make the relative-halfspace/empty-face conventions explicit before sharing the draft. Adding the ray trace table would improve the written proof substantially. These are narrow mathematical presentation repairs; they do not change generators, claims, breakpoints, stable-core geometry, or player count.

Confidence is high in the main separation and ray. The exact lower bound uses the verified statement of a published low-dimensional theorem whose full long proof was not independently rebuilt. The solver checks are not proof-assistant formalizations, the historical journal locator remains uninspected, and priority remains unassessed. These are the exact residual limitations of this audit.
