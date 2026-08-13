# Protected results ledger for the hybrid-overlap program

Status: working theorem/dependency ledger on `codex/hybrid-overlap-facets`.
Baseline: immutable tag `paper5-arxiv-review-v1`.
Current continuation baseline: commit `7a3a409`.

This file prevents a new attack from silently replacing, weakening, or
forgetting an established part of the program.  A row marked **proved** may
be used subject to its stated hypotheses and scope.  Exact audits remain
falsification/reproducibility evidence unless the human argument is named.
Novelty and external validation are not asserted here.

## Headline results that must survive every rewrite

This short index is deliberately redundant with the detailed tables below.
It is the pre-merge checklist for the campaign's largest established gains;
none may be deleted, weakened, or promoted beyond its stated evidence class
without an explicit note in this ledger.

1. **Dimension thresholds and exact finite values.**  Singleton-normalized
   exact games have `Lmin=Lmax` through four players and can diverge at five;
   `s(5)=1/2` and `s(6)=2/3`.  The five-player exact-partition boundary,
   starvation/configuration theorems, and the six-player equality profiles
   are part of these results, not disposable census commentary.
2. **The global separation picture.**  The universal normalized separation
   bound is `rho<=2`, the proved family approaches `2`, and hence
   `sup_n s(n)=2`.  The explicit sharp-candidate family `G(p,k)`, its shared
   hinge/factorization, and its fixed-dimensional equality controls must stay
   visible even though the matching all-`n` upper bound remains open.
3. **Carrier and balanced-collection thresholds.**  The eta-dual vertices are
   normalized minimal balanced collections containing the target coalition.
   The exact carrier inequality holds through six and fails from seven on;
   the exact seven-player outside-pair theorem survives, while total
   balancedness alone has a sharp nonexact seven-player outside-pair
   counterexample.  These are companion-paper results and must not be
   conflated with the hybrid-overlap conjecture.
4. **Hybrid packet/dual infrastructure.**  The complete staged Lmin packet,
   sparse labelled Lmax over-cover, spectral-anchor bound, null-player descent,
   interpolation floor, carrier/separator alternative, strict-complement
   payment, common-carrier contraction, and canonical block expansion are
   proved reusable components.  Their conjunction is not yet the missing
   universal selection/gluing theorem.
5. **Facet and algorithmic theory.**  The interval-packing min-max theorem,
   mixed-colour packet/projection frameworks, complement-star, rooted-star,
   clone-expanded, complete-graph rooted-pair, and rooted pair-lift facet
   classes, plus fixed-cell/fixed-stratum decision procedures, are protected
   contributions.  None is presently a classification of every exact-cone
   facet.
6. **Weighted quotient breakthroughs and obstructions.**  Weighted selectors
   coincide through three roles and can diverge sharply at four.  The
   normalized `(m,1,1,1)` family rules out an atomic-size-independent `3/4`
   shortcut.  Nevertheless objective A is complete: connected
   positive-Lorenz continuation and weighted common-face rigidity force every
   divergent selector pair onto one common-two-flat edge, which satisfies the
   complete atomic overlap target under the unit-singleton hypothesis;
   the proof is human for `n>=10` and computer-assisted on six finite rows at
   `n=6..9`.  The face-normalized cost theorem retains its exact adjacent-gap
   formula and unique six-player equality weight pattern `(2,2,1,1)` up to
   orientation.
7. **Hostile controls.**  The five-player large-core separation, `PART`/`ZP`
   families, six-player residual facet atlas, seven-player effective-
   bipartition and full-root-block-budget counterexamples, and both
   seven-player balanced equality orientations remain mandatory tests for
   every proposed general lemma.

The unresolved headline is equally protected: no dimension-free proof of the
conjectured fixed-`n` upper formula has yet been obtained.  Objective A, the
atomic weighted four-role quotient theorem, is now complete.  The live gap is
the carrier-selection/gluing theorem in objective B, followed by full
equality and facet identification in objective C.

## Protected mathematical inputs

| Result | Status and scope | Primary repository evidence |
|---|---|---|
| Global asymptotic divergence | **Proved.** For the normalized separation `rho=||Lmin-Lmax||_1/T`, one always has `rho<=2`, the explicit exact family approaches `2`, and therefore `sup_n s(n)=2`.  This is an asymptotic theorem, not the conjectured sharp formula for every fixed `n`. | `paper5/divergence.tex`, global bound and family sections |
| Four/five selector threshold | **Proved.** Every singleton-normalized exact game on at most four players has `Lmin=Lmax`; exact five-player games can differ.  This is an unweighted player theorem, not weighted-role coincidence. | `paper4/threshold.tex`; `paper5/divergence.tex` |
| Five-player exact-partition boundary | **Proved.** Four-player exact games have the exact-partition/Lorenz-greatest bridge used for selector coincidence; every five-player selector failure has a slack suffix, and the attempted exact-partition failure mechanism is impossible at `n=5`.  Preserve the precise suffix quantifiers from the paper. | `paper4/threshold.tex`; commit `3004fe8`; `verifiers/cc/` |
| Five-player sharp separation | **Proved at fixed n.** `s(5)=1/2`; the Lmin `(4,1)` stratum regime has the stronger `1/3` bound, and the starved player is Lmin-poor.  The fixed-dimensional proof is computer-assisted with separately formulated Lmin-optimality components. | `paper5/divergence.tex`; commit `15ff9f4`; `verifiers/s5close/` |
| Five-player certificate and configuration theorems | **Proved at fixed n.** The one-coalition certificate theorem and the extremal/starvation configuration arguments are reusable structural inputs, not merely implementation details of the census. | `paper5/divergence.tex`; `verifiers/a3check/`; `verifiers/o2/`; commits `329ff1f`, `48780d9` |
| PART/ZP structural families | **Proved constructions and boundary results in their stated parameter ranges.** Closed-form `PART(p,q)` realizations and the seven-player `ZP(2,2)` realization refute earlier restrictive conjectures; these controls must remain in any general theorem audit. | `paper4/threshold.tex`; `paper5/divergence.tex`; `verifiers/part/`; commits `df58ef4`, `fd59dce` |
| Six-player sharp bound and equality work | **Proved at fixed n.** `s(6)=2/3`, with exact equality profiles, a complete counterexample-to-SMT implication, exact infeasibility certificates, and compressed human exchange schemas.  Its packet/orbit calculations must not be promoted to an all-n theorem. | `paper5/divergence.tex`; `paper5/S6_*`; `verifiers/s6/`; `verifiers/s6_direct/` |
| Sharp family `G(p,k)` | **Proved construction.** Supplies the conjectured all-n lower examples and the equality controls the upper theorem must recover. | `paper5/divergence.tex` |
| Large-core separation control | **Proved exact example.** A five-player exact game with a large core has `Lmin!=Lmax`; therefore the large-core/PES characterization of `Lmax` cannot by itself prove selector coincidence. | `paper5/divergence.tex`, introduction and archived exact verifier |
| Sparse Lmax over-cover | **Proved dual certificate framework.** Normalization and top-stratum labels are essential. | `paper5/LMAX_OVERCOVER_COUPLING.md`; `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md` |
| Spectral-anchor overlap theorem | **Proved dimension-free conditional lower bound.** A sparse Lmax over-cover and its optimized dispersion parameter yield the exact labelled-to-spectral overlap floor `B_theta`.  It is an effective bound, not a proof that one scalar anchor reaches the all-n target. | `paper5/LMAX_OVERCOVER_COUPLING.md`, `(SA)`; `audit_lmax_overcover.py` |
| Complete staged Lmin packet | **Proved selection/certificate framework.** Later gluing must use the complete staged packet, not a first-floor surrogate. | `paper5/divergence.tex`; `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md` |
| Zero-floor null-player descent | **Proved dimension-free induction reduction.** If the Lmin floor is zero, exactness makes one player null; deletion preserves the core product, both selectors, total, and overlap.  Thus a minimal-dimensional counterexample to the target has positive Lmin floor. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(NPD0)--(NPDC)`; `verify_null_player_hybrid_descent.py` |
| Sharp-family shared hinge and factorization | **Proved dimension-free for `G(p,k)`.** The common hinge geometry and overlap factorization explain the lower family structurally and are mandatory equality controls for any general gluing theorem. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, shared-hinge section; `verify_balanced_family_shared_hinge.py` |
| Dispersion and staged-transport theorems | **Proved within their stated packet hypotheses.** The paired dispersion budget, projected staged-circuit theorem, first-floor Hall alternative, and sign-coherent staged lifts give exact transport structure.  Their individual unit-box/target-count strengthenings fail at seven players. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, Sections 5--6; adjacent exact audits |
| Direct/interpolation/null/root-price/common-repair reduction | **Proved components plus exact finite handover audit.** The finite census is not the missing general selection theorem. | `verifiers/divergence/audit_direct_ceiling_common_hinge_trichotomy.py` and adjacent JSON; research note |
| Ceiling-root interpolation floor | **Proved dimension-free.** The scalar floor `O/T>=t-u+u/t` closes all parameters outside an explicit positive-floor wedge.  Archived hard controls lie inside that wedge, so facet/packet charge is still required. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`; `verify_ceiling_root_interpolation.py` |
| Labelled rooted packing/cover duality | **Proved exact LP duality.** Facet price belongs to a labelled normal plus its Lmin-tight labels; it is not gauge invariant. | `verifiers/divergence/audit_labelled_facet_cover_duality.py`; research note |
| Carrier cycle or separator | **Proved structural alternative.** A carrier cycle is a sign-coherent tight-face object; the alternative alone has no quantitative target price. | commits `00ea31b`, `21b2d23`; research note |
| Strict complement payment | **Proved.** A z-tight coalition splitting an x-carrier gives strict payment on it and its complement.  One separator need not pay enough. | commit `5ac2ab8`; `audit_carrier_separator_payment.py` |
| Strict-loss proper-packet support | **Proved.** If a nongainer carrier cycle has positive selector loss, then every gainer is omitted by some Lmin-tight coalition containing the cycle.  Carrier monotonicity proves this proper-packet existence; residual normalization remains open, as does the tied-loss analogue. | `paper5/divergence.tex`; `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`; `audit_carrier_separator_payment.py` |
| Carrier-cycle cardinality theorem | **Proved dimension-free.** Any direct block containing a carrier cycle has atomic multiplicity at least two.  Once its gainer packet is proper, its direct cardinality base automatically reaches the target for every `n>=6`; the unique cardinality equality parameters are `(n,p,g,h,s)=(6,2,2,2,1)`. | `paper5/divergence.tex`, `(CCC)`; `verify_carrier_cycle_cardinality.py` |
| Comparison--residual cancellation | **Proved exact identity.** In the direct master identity, the weighted comparison payment plus both order residuals equals `B(U_s-L_H)`.  The budget grows by total gainer gain divided by `g` when `s` increases, so the best proper packet has size `g-1` and its labels are irrelevant.  The remaining carrier choice is the scalar nongainer-block budget `U_(g-1)>=L_H`, not triangular labelled residual matching. | `paper5/divergence.tex`, `(CB1)--(CB3)`; `verify_two_stratum_direct_gluing.py`; `audit_carrier_separator_payment.py` |
| Root-block aggregate reduction and failure | **Exact identity; universal sign disproved.** For the full nongainer maximum-overlap root block, the budget is `[g(g+h)U-gpR-[g+h(p+1)]D]/[g(g+h)]`.  All 65 role-irreducible six-player controls have nonnegative numerator, but an exact role-irreducible seven-player lower envelope has numerator `-8` and scalar margin `-1`.  Its overlap is safely `76/85`, and a labelled tight-support enlargement closes with margin `17/30`; only the full-root-block shortcut fails.  The repair row is selected by primitive first-floor circuit `1_59+e_2+e_6=1_N`, a relative selection-cell circuit rather than a new full-cone facet. | `paper5/divergence.tex`, `(RBB)--(RBB-C)`; `verify_n7_root_block_budget_counterexample.py`; exact JSON |
| Root-exclusion transport | **Proved dimension-free support lemma.** For every gainer, positive-loss sources in any sign-coherent Lmin transport lie among nonroot nongainers, never in the nongainer maximum-overlap root block.  Each eligible source satisfies `M-z_i >= (M-x_j)+(x_i-z_i)`.  The lemma localizes the budget but does not bound joint transport congestion. | `paper5/divergence.tex`, `(RET)`; staged-transport theorem |
| Cardinality-ranked carrier support | **Proved exact identity.** For fixed gainer set and fixed candidate-block size, `U_(g-1)-L_H` is affine in `z(H)` with positive coefficient `n/(g+h)` and all other terms constant.  Hence Lmax sum ranks all equal-size admissible staged Lmin supports exactly.  This reduces optimization but does not prove that an admissible block crosses the target threshold. | `paper5/divergence.tex`, `(CRS)`; `verify_cardinality_ranked_support.py` |
| Target-reserve quota and seven-player facet boundary | **Proved dimension-free identity plus exact fixed example.** Retaining cardinality slack gives `R_tau(P)=(1-tau)T-D-gnz(P)/[(n-p)(p+1)]>=0`; when the cardinality base already reaches the target, as `(CCC)` guarantees on the carrier-cycle arm, this is no stronger than strict quota and is strictly weaker for positive base surplus.  Without that base hypothesis the tests need not be ordered.  In a three-generator exact game, all six carrier-cycle supports miss the strict quota, but the first-floor row `P={2}` has base `5/6` and target reserve `11/3`, so it closes `7/12`.  A third tied root simultaneously has margin `1` and exposes an indecomposable rooted pair-lift facet tight at the game.  Its price is `4`, its multistage penalty is zero, and the rooted theorem independently gives `7/10>7/12`.  Its canonical support is distinct from the five `n=6` residual-atlas orbits but uses the proved pair-lift mechanism; no novelty claim is made.  Universal selection remains open. | `paper5/divergence.tex`, `(EDQ5)`, `(QFH1)--(QFH4)`; `verify_excluded_block_deficit_quota.py`; `verify_n7_quota_reserve_facet_boundary.py`; exact JSON |
| Rooted complement averaging and charged properization boundary | **Proved dimension-free identities plus exact finite obstruction.** For a root-containing `x`-tight packing, excluded-block Lmax mass and cardinality equal root-excess mass plus uncovered-player deficit mass, and core feasibility gives the rooted tangent inequality `(RCA1)--(RCA3)`.  On a fixed complement cardinality this yields the exact average target-reserve formula `(RCA4)`.  The exact price and reserve changes under row replacement are `(PXC1)--(PXC2)`; the pair-free co-singleton specialization is `(PXC3)`.  Exactness proves `(PXC4)`: two tight sets covering `N` have a tight intersection, so co-singleton intersection universally removes the comparison/selection obstruction.  The ordered-cut rewrite `(PXC5)--(PXC8)` gives the Lmax-side certificate.  The omitted-gainer identity `(PXC9)--(PXC11)` gives the complementary Lmin-side certificate and proves that its entire error is exactly `c_p[z(I)-x(I)]`; there is no third residual currency.  The root-block-only certificate closes all 150 archived carrier-row intersections (142 positive, eight zero).  The comparison certificate is exact and nonnegative on 148; the other two rows have comparison payment `1/2` and are closed by the root certificate.  On the fixed seven-player repair the root-only bound is `-59/60`, the ordered-cut bound is `53/12`, and the comparison bound equals the exact reserve `289/60`.  Universal selection or separator payment of this two-colour max-certificate remains open. | `paper5/divergence.tex`, `(RCA1)--(RCA4)`, `(PXC1)--(PXC11)`; `audit_marked_packing_target_reserve.py`; exact JSON |
| Carrier price selection and direct frontier | **Exact identities, finite theorem, scope counterexample, and corrected live conjecture.** Identities `(PXC12)--(PXC16)` reduce the sufficient two-colour max-certificate selection to `min(Z_all,X_all)<=K_tau` and make each fixed-cardinality certificate price a maximum-weight row problem.  Tight-co-singleton exchange laws `(PXC18)--(PXC19)` give the exact one-player change in both certificate prices; `(PXC20)--(PXC21)` turn certificate-price stability into explicit player payments and a decomposable balanced-partition packet, not the distinct indecomposable complement-star facet family.  The weaker exact direct price `(PXC22)--(PXC23)` is `Y_I=c_p z(P)<=min(Z_I,X_I)`; a direct row closes iff `Y_all<=K_tau`, so this—not the stronger hybrid inequality—is the correct direct-versus-separator frontier.  Formula `(PXC23)` is a pure retained-Lmax-mass support function on the complete Lmin-tight menu.  Its exchange and stability laws `(PXC24)--(PXC25)` produce pure retained Lmax payment before the coefficient midpoint.  Joint uncrossing `(PXC26)` shows that all available tight co-singletons generate a Boolean deletion cube, and `(PXC27)` reduces its direct-price optimum to a one-dimensional order-statistic scan.  Endpoint identity `(PXC28)` says `u_j=T-v(N\{j})=max_{y in core(v)}y_j` and a co-singleton is `x`-tight exactly when `x_j=u_j`; every missing cube direction therefore carries positive upper slack and an exact endpoint witness.  The minimax/Farkas alternative `(PXC29)--(PXC30)` proves that any shortage set either has one common endpoint witness or yields a sparse exact-core separator with positive aggregate slack; its coalitions are not automatically Lmax-tight.  On the common-witness arm, `(PXC31)--(PXC33)` give an exact endpoint-fixed mixed-packet projection, linear support bound, and multi-exception incidence system, but do not prove the target or full-cone indecomposability.  The ceiling inequalities `(PXC34)--(PXC36)` directly couple the endpoint witness/separator to the sparse Lmax over-cover; the priced separator requires alpha-dominance, and failure of that alignment remains the rooted/mixed-packet interface.  On the full n=6 menus, minimum hybrid deletion is globally price-optimal on 386/415 strict cycles, while `p=1 -> p=2` strictly improves 29; all 29 are exact co-singleton exchanges deleting a player with `x_j=z_j=0`.  The verifier checks all 157 available exchange/cube seeds and 314 vertices/layers; all archived cubes have dimension one.  It also checks 497 retained noncarrier nongainer endpoint occurrences, of which 157 are pinned and 340 have positive slack.  Every archived shortage set is a singleton, so all 340 have a common endpoint witness and the positive-separator arm has no nontrivial finite test.  The endpoint/Lmax coupling holds on all 340: 276 shortages are alpha-dominant and the other 64 strictly improve the old dispersion ceiling, but only two coupling bounds are tight and none is stronger than its dispersion corollary in this archive.  The direct and hybrid global prices coincide on all 415 archived cycles, so the strategic weakening is structural rather than a finite-data repair.  All 830 minimum rows close.  A new exact n=7 lower envelope has `(PXC11,PXC6)=(13/24,-1/12)` and `(X_star,Z_star)=(35/8,5)`, exhibiting the Lmin-colour handover.  Equality corollary `(PXC17)` says a carrier max-certificate closes at `K_tau=0` iff `z(P)=0`.  Fixed-cell support-function facets are not automatically full exact-cone facets. | `paper5/divergence.tex`, `(PXC12)--(PXC36)`; `audit_strict_carrier_minimum_deletion.py`; exact JSON |
| Multi-endpoint positive-gap control | **Exact sharp sign/price control, not a new facet.** The seven-player dummy extension of the two-player simplex has incompatible endpoint faces with `epsilon_R=1/2`.  Its sparse Lmax load and endpoint separator weights are both `(1/2,1/2)`, `q_R=1`, and `(PXC36)` is tight at `M=1/2`.  The explicit `(PXC30)` packet uses `gamma=1/2` and half weight on each dummy singleton.  It is decomposable and is not a carrier hard case. | `audit_strict_carrier_minimum_deletion.py`; `n7_multi_endpoint_separator_control` in exact JSON |
| Endpoint ceiling plus scalar interpolation | **Universal closure route refuted by exact archive audit.** Minimizing `(CRI)` over the ceiling interval allowed by `(PXC35)` reaches the target on only 28/340 full-menu shortage rows; even the actual-ceiling `(CRI)` closes only 165/340.  The endpoint/Lmax coupling remains proved, but scalar ceiling optimization cannot replace labelled direct-price or mixed-packet gluing. | `audit_strict_carrier_minimum_deletion.py`; exact JSON counters |
| Canonical direct-optimal price handover | **Proved dimension-free reduction plus finite scope audit.** At a global direct-price minimizer through the coefficient midpoint, every retained nongainer below the exact exchange threshold has a non-tight co-singleton `(PXC37)`; the complementary retained block obeys the high-mass inequality `(PXC38)`, yielding the explicit target-reserve lower bound `(PXC39)`.  Thus the canonical cheap set goes to the endpoint separator and a negative high-mass bound is the exact labelled residual still owed.  All 920 archived full-menu direct-optimal rows through the midpoint have empty cheap set; `(PXC39)` closes 682 rows and at least one optimum on 296/415 cycles.  The remaining 238 rows span 119 cycles and require labelled packet currency. | `paper5/divergence.tex`, `(PXC37)--(PXC39)`; `audit_strict_carrier_minimum_deletion.py`; exact JSON |
| Direct-optimal labelled currency | **Exact dimension-free identity plus finite stage localization.** `(PXC40)` decomposes the direct reserve into the high-mass base `(PXC39)` plus nonnegative retained Lmax excess `Lambda_I`.  All 238 archived negative-base rows have profile `(g,h,p,r)=(2,2,1,1)` and zero ordered-cut error, so this is exactly the PXC6 colour.  The currency player is Lmax-top in 236; the two off-top rows have zero excluded Lmax mass and hence zero direct price.  First-stage visibility for every positive-price residual is finite evidence, not yet a universal theorem. | `paper5/divergence.tex`, `(PXC40)`; exact JSON and off-top details |
| Carrier-preorder closure of top currency | **Proved dimension-free module theorem plus finite payment audit.** The full carrier relation is a preorder `(PXC41)`; each strong class is an Lmin tight-face module with constant Lmin payoff.  A top nongainer currency player is a maximum-overlap root, and if it joins the cycle component the existing Lmax-separator/weighted-contraction alternative applies to the enlarged class.  Of 236 archived top-currency occurrences, 222 join: 90 contract to four weighted roles and 132 have a strict separator payment lying in `[-B_I,Lambda_I]`.  The 14 remaining occurrences are one-way carrier satellites.  Only the module theorem is dimension-free; the separator interval is finite evidence. | `paper5/divergence.tex`, `(PXC41)`; exact JSON counters and outside-SCC details |
| Locked-satellite quotient | **Proved dimension-free normal-form reduction; target open.** A one-way top satellite over a common carrier component either has an Lmax splitter or contracts to `(PXC42)`: a weighted top role `*` and unit top satellite `j` with equal Lmax levels, `x_*/|E|>=x_j>=M`, and every quotient Lmin-tight coalition containing `j` also containing `*`.  Four of 14 archived satellites close by a splitter; ten give the five-role weights `(2,1,1,1,1)`.  This lies beyond the four-role theorem and is the current quotient bottleneck. | `paper5/divergence.tex`, `(PXC42)`; exact JSON counters/details |
| Locked-block atomic cutoff | **Proved dimension-free.** The contracted carrier module plus its top satellite contribute `W=|E|+1` copies of overlap `M>=T/n`; `(PXC43)` closes automatically for `W>=4` in even dimension and `W>=5` in odd dimension.  Any surviving locked satellite has module size at most two (even) or three (odd), though arbitrarily many outside roles may remain. | `paper5/divergence.tex`, `(PXC43)` |
| Locked-satellite marked-row dichotomy | **Proved dimension-free sign/support theorem plus complete finite closure.** One-way carrier lock supplies an Lmin-tight row containing the module and omitting the satellite; its reverse comparison payment is nonnegative.  Every Lmax-tight locked-block splitter has nonnegative forward payment, and a splitter containing the satellite but omitting the module pays strictly.  Zero payment in either colour is exactly a common hinge `(PXC44)`.  A top-only zero marked row itself yields a normalized common top over-cover `(PXC45)`.  Of the ten archived `(2,1,1,1,1)` quotient occurrences, eight have a positive mixed-colour payment in `[-B_I,Lambda_I]`; the last two are one record whose top-only marked hinge `22={1,2,4}` gives `theta=1/3` and spectral bound `43/2>46/3`.  Universal affordability or target pricing remains open. | `paper5/divergence.tex`, `(PXC44)--(PXC45)`; exact JSON counters and row details |
| Marked-hinge deficiency transfer | **Proved dimension-free polar-price theorem.** For a common hinge `A`, the common-support deficiency dual satisfies `-y(A\H)>=|A cap H|epsilon_star` and `y(H\A)>=|H\A|epsilon_star` `(PXC46)`.  Thus failure of a common top over-cover forces signed labelled price transfer across every hinge meeting and omitting the Lmax top.  The exact replay checks 2,065 common rows; 21 rows in positive-deficiency records exercise the nonzero arm, with a sharp equality control at `601[71]`, coalition `23`.  Only 11/21 admit an optimal over-cover row with the same top trace; the four-row `602[17]` control refutes a universal one-row nested shear.  The positive-root-excess aggregate conversion is classified by `(PXC47)`; the tied arm remains open. | `paper5/divergence.tex`, `(PXC46)`; `audit_marked_hinge_deficiency_transfer.py`; exact JSON |
| Aggregate marked-hinge rooted facets | **Conditional dimension-free construction; complete finite positive-excess classification.** Adjoining the marked hinge to the full sparse deficiency over-cover and applying the existing rooted-pair shear at positive root excess gives `(PXC47)`.  Of 21 positive-deficiency transfer rows, 11 have positive excess and all 11 are support-minimal indecomposable exact-cone facets, independently replayed in Z3.  Their three orbits (multiplicities `4,3,4`) are saturated or clone-expanded rooted stars; two occur in the prior five-orbit atlas and the third is the saturated `(1,2,2)` branch star with canonical support `(1,3,13,49)`.  All 11 are scalar-affordable at `n=6` (`Q/delta` is 1 or 2 versus `K=4`), but payoff-stratum alignment is separate.  All ten tied rows close through earlier finite arms.  Universal aligned target pricing and a proof that tied geometry forces an earlier arm remain open. | `paper5/divergence.tex`, `(PXC47)`; `audit_marked_hinge_deficiency_transfer.py`; `verify_marked_hinge_mixed_facets_z3.py`; exact JSON |
| Tied aggregate carrier theorem | **Proved dimension-free.** Rooted packing/cover duality gives `(PXC48)`.  At tie, cover mass one forces every positive cover label into every rooted tagged trace, so a tied root is equivalent to a nonempty aggregate-carrier intersection `(PXC48')`; no genuinely fractional unit-cover branch exists.  All 31 nonzero tied archive roots exhibit this.  The support-relative carrier is promoted by the full-menu trichotomy `(PXC49)`; pricing remains separate. | `paper5/divergence.tex`, `(PXC48)--(PXC48')`; exact JSON witnesses |
| Full-menu marked carrier trichotomy | **Proved dimension-free structural theorem.** Enlarge a common marked hinge by the full Lmax-tight menu.  Either a top hinge root has positive aggregate load and yields a sparse mixed packet, or tied root covers generate an Lmax-top carrier cycle inside the hinge; an Lmin-tight splitter then gives strict reverse payment, while absence of a splitter makes a common module covered by exact weighted contraction `(PXC49)`.  The ten tied archive rows split exactly as 3 positive packets, 2 strict splitters, and 5 common modules.  Payment magnitude and payoff-stratum alignment remain open. | `paper5/divergence.tex`, `(PXC49)`; exact JSON alternatives |
| Mixed-packet comparison budget | **Proved dimension-free exact identity plus hostile alignment audit.** A positive full-menu rooted packet obeys `Gamma + sum q_i(x_i-z_i)=delta(x_r-z_r)` and, at a maximum-overlap root, `Gamma=D+delta*l_r-E` with `max sigma_C>=Gamma/(1+delta)` `(PXC50)--(PXC51)`.  Thus `E<=delta*l_r` is the precise sufficient comparison-charge condition.  Positive root excess does not force it even after lexicographically minimizing `E` on the entire maximum-root-load face and across eligible roots: of 21 marked positive-deficiency rows, 6 lack an eligible hinge-top root, 7 are tied, and 8 have positive eligible excess; only 3/8 optima have zero alignment defect and 4/8 cover total gain.  The neutral n=7 control further has `delta=1`, `Gamma=0`, Lmin-only bound `8/15<7/12`, but full mixed bound `5/6`; hence genuinely coloured gluing can be necessary. | `paper5/divergence.tex`, `(PXC50)--(PXC51)`; `audit_marked_hinge_deficiency_transfer.py`; `audit_pxc51_handover_controls.py`; exact JSON controls |
| Common carrier contraction | **Proved.** A common x/z tight-face carrier module contracts to one weighted role while preserving exactness, weighted selectors, total, and overlap. | commits `5ac2ab8`, `fc28a1a`; research note |
| Canonical block expansion | **Proved.** A nonnegative exact weighted role game expands to a singleton-normalized exact atomic game when every unit-weight role has zero singleton worth.  Weighted selectors and overlap are preserved. | commit `fc28a1a`; research note |
| Common-module role induction | **Proved structural reduction.** Formulate the target for weighted games by number of roles while holding total atomic weight fixed.  A common selector module contracts to fewer roles without changing the target data, so strong induction discharges the contraction arm; the base through four roles is now complete.  A role-minimal counterexample is therefore common-module-free. | `paper5/divergence.tex`, Proposition `common-module-induction`; `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`; `audit_carrier_separator_payment.py` |
| Weighted coincidence through three roles | **Proved dimension-free.** The core is a box intersected with efficiency and the clipped weighted equalizer Lorenz-dominates all feasible repeated vectors. | commit `36c13c6`; `verify_weighted_three_role_coincidence.py` |
| Elementary/laminar four-role coincidence reductions | **Proved.** Weighted selectors coincide when one role total is core-constant or when at most one complementary pair slab is nonredundant.  Equal weights also suffice only when all role singleton worths vanish.  Any hard quotient has four variable roles and at least two crossing pair slabs. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, elementary four-role reductions |
| Two-active-crossing-partitions lemma | **Proved local structural reduction.** If the weighted selectors differ, each selector itself lies on endpoints of at least two independent pair-sum slabs.  Otherwise its active relaxation is laminar and its Lorenz-greatest water-filling point forces global selector coincidence.  Hence the residue is a transition between two-flat edges, not a locally laminar optimum. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, two-active-crossing-partitions lemma |
| Four-role pair-coordinate distance identity | **Proved exact reformulation.** The three complementary pair sums turn the core into a box cut by four diagonal coordinate slabs, and selector displacement satisfies `||x-z||_1=max(sum |delta_j|,2 max |delta_j|)`.  This reduces the residue to a clipped-edge transition bound but does not supply that bound by itself. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(FEC1)--(FEC4)` |
| Four-role minimal edge-transition classification | **Proved and closed.** Up to pair-coordinate symmetries there are four noncommon minimal edge incidences.  Weighted common-face rigidity closes types I and II.  Connected positive-Lorenz continuation confines the entire selector path to one pair-box edge and rules out opposite-endpoint types III and IV. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(FEC1)--(FEC10)`; `paper5/divergence.tex`, common-face rigidity and edge-confinement theorems |
| Weighted common-face rigidity | **Proved dimension-free structural theorem.** On a fixed complementary pair endpoint, the four roles split into two fixed-total pairs.  Their distances from weighted equality are two Lorenz dispersion coordinates.  Convexity puts all undominated points in one dispersion orthant, where only one remaining pair strip can carry a non-singleton Pareto frontier.  Thus two distinct undominated points share a second pair endpoint.  This is purely human geometry for positive integer role weights and does not use singleton normalization. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(FEC6)--(FEC9)`; `paper5/divergence.tex`, Theorem `common-face-rigidity` |
| Connected Lorenz continuation and edge confinement | **Proved dimension-free structural bridge.** Positive scalarizations of the repeated-payoff Lorenz sums have compact convex argmax fibers; their graph over a coefficient segment is connected.  Every point is Lorenz-undominated and hence lies on the pair-box one-skeleton.  Common-face rigidity forbids turning between incident edges, so weighted Lmin and weighted Lmax coincide or share two pair endpoints. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(FEC10)` and edge-confinement theorem; `paper5/divergence.tex`, Theorem `four-role-confinement` |
| Four-role weighted divergence | **Proved sharp role threshold.** Weighted coincidence fails at four roles, including in every sufficiently large atomic dimension. | commits `569dd84`, `c5e71f8`; exact verifiers and JSON |
| Normalized constant-overlap four-role family | **Proved.** For weights `(m,1,1,1)`, `m>=5`, an exact zero-singleton role game has weighted selections `(5,1,5,1)` and `(3,3,3,3)`, hence `O/T=2/3`.  It refutes a universal `3/4` quotient bound but satisfies the atomic conjecture. | commit `7a3a409`; `verify_weighted_four_role_normalized_obstruction.py` |
| Balanced weighted seesaw face | **Proved atomic-weight-aware quotient theorem.** If both weighted selectors lie on two balanced common crossing flats, the face is `q(t)=(t,W-t,t,W-t)` and its exact selector formula plus the integer harmonic/product bound proves the full atomic target.  This includes the common face of the normalized `2/3` family and has strict target slack for `n>=6`.  The two flats are exact-partition face equalities, so no new full-cone facet is asserted. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(BWS1)--(BWS8)`; `verify_weighted_balanced_seesaw.py` |
| Face-normalized endowed common-two-flat theorem | **Proved atomic-weight-aware quotient theorem under its explicit face hypothesis.** The selectors are the middle order statistics of the `2 by 2` crossing matrix; diagonal middle gaps are impossible; and every adjacent gap has the sharp cost formula `(EWS5)`.  If every unit-weight role has zero effective endowment on that line, integer weights prove the full target for `n>=6`.  Equality occurs only at `(2,2,1,1)` up to orientation, whose canonical expansion is six-player survivor 1408.  Role-level zero singleton worth does **not** automatically imply the face hypothesis. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(EWS1)--(EWS18)`; `paper5/divergence.tex`, Theorem `endowed-seesaw`; `verify_weighted_endowed_seesaw.py`; common-face scope control |
| Common-face hub payment | **Proved exactness inequality.** If the two tight pair coalitions defining a common line share hub `h` and omit opposite role `o`, singleton exactness gives `q_h-w(h)<=q_o-w(o)` throughout the face.  A normalized unit hub therefore has effective endowment `e_h<=e_o`.  This does not charge either arm role and did not by itself close the unrestricted common-two-flat theorem. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(EWS20)--(EWS21)`; `paper5/divergence.tex` |
| Unrestricted common-face large-`n` theorem | **Proved atomic-weight-aware reduction.** With no zero-effective-endowment assumptions, the exact adjacent unit-gap cost is `S_0=2+p/q+(p+q+b)/r`.  Integer inequalities prove the full target for every `n>=10`; only six ordered weight patterns at `n=6,7,8,9` require off-face exactness.  The six relaxed rows are not asserted realizable. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(EWS22)--(EWS26)`; `verify_weighted_endowed_seesaw.py` |
| Finite unit-hub closure | **Proved human inequality.** Every one of the six relaxed subtarget rows has `p=q=1`; if the unit low role is the common hub, exactness gives `e_p<=e_r` and restores the safe sharp cost `2(2r+b+1)/(r-1)`.  At this intermediate human stage only arm/opposite orientations remained; the later quantified audit closes them. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(EWS27)--(EWS28)`; `verify_weighted_endowed_seesaw.py` |
| Weighted fairness selector encoding | **Proved convex characterization.** Weighted Lmin is max--min fair and weighted Lmax is min--max fair in role per-capita coordinates.  This gives a stratum-free quantified LRA encoding on the four-role interval/pair-slab core and retains unit-singleton exactness witnesses.  A separately formulated rational audit compares 236 staged selectors and 944 role implications. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(EWS29)`; `verify_common_two_finite_z3.py`; `verify_weighted_fairness_selector.py` |
| Atomic weighted four-role quotient theorem (objective A) | **Proved for all `n>=6`, computer-assisted only on a finite quantitative residue.** Edge confinement makes the common-two branch exhaustive.  The human adjacent-gap theorem closes `n>=10` and all but six ordered rows at `n=6..9`; a stratum-free quantified-LRA relaxation checks all `6*12*16=1,152` cells for those rows and returns unsat with zero unknowns.  Hence every exact nonnegative weighted four-role game satisfying the unit-role singleton hypothesis reaches the atomic target. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(FEC6)--(FEC10)`, `(EWS22)--(EWS31)`; `paper5/divergence.tex`, Theorem `atomic-four-role`; exact verifiers and JSON |
| Complete strict carrier support | **Proved support theorem.** Normalized coefficient supply collapses to zero/nonzero support; coefficient magnitude is not invariant currency. | research note, complete strict-carrier-support section |
| Interval-packing min-max | **Proved exact combinatorial theorem** with its stated fixed-stratum algorithm and integrality boundary.  It is not a full all-cell gluing theorem. | research note, interval-packing sections |
| Mixed-colour packet and mixed-witness projection | **Proved projection frameworks.** They allow genuinely mixed x/z support; relative-cell validity does not automatically imply a full exact-cone facet. | `verify_mixed_packet_gluing.py`; `verify_mixed_witness_projection.py` and Z3 replay |
| First genuinely noncommon mixed packet | **Proved branch certificate.** The explicit two-colour packet closes its optimized hostile branch; an alternative rooted-pair shear gives an active indecomposable exact-cone facet and reaches the exact `3/4` one-witness minimum.  This is a branch theorem, not universal gluing. | `paper5/EFFECTIVE_BIPARTITION_BRIDGE.md`; `mixed_packet_gluing.json`; `mixed_witness_projection*.json` |
| Complement-star facets | **Proved dimension-free class** with exact indecomposability/facet criterion in its stated parameter range. | commit `cd5e947`; `verify_complement_star_facets.py` |
| Rectangular and saturated rooted-star facets | **Proved class criteria.** These enumerate their distinguished classes, not every exact-cone facet. | `verify_rooted_star_matrix_facets.py`; research note |
| Nonroot clone expansion of rooted-star facets | **Proved preservation theorem.** It applies to the stated nonroot clone expansion, not arbitrary marked shears. | commit `d3b4987`; `verify_clone_expanded_rooted_star_facets.py` |
| Complete-graph rooted-pair facets | **Proved dimension-free non-star class.** This is a sharp warning that clone-saturated stars do not exhaust the facet atoms. | `verify_complete_graph_rooted_pair_facets.py`; independent K4 Z3 control |
| Rooted pair-lift facet theorem | **Proved dimension-free interface.** Extreme rooted packings shear to min-semi-balanced systems of support at most `n`; the published indecomposability test decides when the resulting inequality is a full exact-cone facet.  The simultaneous `G(p,k)` lift is an indecomposable facet for every stated `p,k`. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`; `paper5/EFFECTIVE_BIPARTITION_BRIDGE.md`; pair-lift LP/Z3 audits |
| Relative common-hinge facet decision | **Proved exact finite decision procedure** on a fixed labelled selection cell.  It does not by itself certify a full-cone facet after cell gluing. | research note, `(CHF)` section |
| Exact fixed-stratum/fixed-n algorithms | **Proved decidability/enumeration interfaces** for the stated cells and candidate classes.  No polynomial full exact-cone enumeration claim is licensed. | research note, fixed-stratum and cellwise-pullback sections |
| Effective fractional-role decomposition | **Proved exact reduction.** The clipped fractional-role/dispersion dual and disjoint carrier packets remain valid.  The stronger effective-bipartition overlap floor they motivated is false by an exact seven-player counterexample. | `paper5/EFFECTIVE_BIPARTITION_BRIDGE.md`; `verify_n7_effective_bipartition_counterexample.py` |
| Six-player positive-residual facet atlas | **Exact finite theorem/audit.** Thirteen facets in five support orbits cover the live archived residuals; it is not an all-n class exhaustion. | `audit_n6_positive_residual_facet_atlas.py`; independent Z3 verifier |
| Seven-player hostile and equality controls | **Exact falsification controls.** Every new general lemma must pass the fixed hostile cases and both balanced equality orientations `(2,4)` and `(3,3)`. | research note and adjacent n=7 verifiers |
| Excluded-block deficit quota | **Proved dimension-free identity and fixed-cell decision criterion.** For a staged support `H=L\P`, `U_(g-1)-L_H=[pT-nz(P)]/(n-p)-(p+1)D/g`; hence the direct arm closes iff the excluded nongainers meet the exact below-mean Lmax deficit quota. This does not prove universal existence and is not a full-cone facet theorem. | `verify_excluded_block_deficit_quota.py`; `(EDQ)--(EDQ3)` |
| Carrier-direct equality boundary | **Proved arm-specific equality theorem.** A target-reaching direct packet containing a carrier cycle is strict except possibly at `n=6`, `(p,g,h,s)=(2,2,2,2,1)`; equality there requires `z(P)=0` and total gainer gain `D=T/3`. Rooted seven-player equality remains outside this arm. | `(CCC)`, `(EDQ)`, `verify_excluded_block_deficit_quota.py` |

## Adjacent campaign results that must not be lost

These results belong primarily to the normalized-Lmin/coalitional-monotonicity
paper rather than to the hybrid `Lmin`--`Lmax` bound.  They are recorded here
because they supplied several of this program's carrier, exactness, and
dimension-threshold ideas.  They must not be silently absorbed into stronger
claims about the current overlap conjecture.

| Result | Status and scope | Primary repository evidence |
|---|---|---|
| Normalized-Lmin monotonicity boundary | **Proved.** Singleton bumps are monotone; grand-coalition resource monotonicity fails; and proper nonsingleton coalitional monotonicity fails for an exact five-player zero-singleton game, in the minimum possible dimension, with the exact bump path computed. | `paper3/sections_leximin.tex`; `verify_n5_exact_leximin_monotonicity_counterexample.py` |
| Large-core/exact-partition separation at five | **Proved.** The five-player monotonicity pair has large cores and constant `Lmax`, while `Lmin` changes; the base core has neither an exact-partition allocation nor a Lorenz-dominating element.  This makes the through-four boundary sharp. | `paper3/sections_leximin.tex`, large-core separation proposition; large-core verifier |
| Quantitative carrier dimension threshold for exact games | **Proved, computer-assisted at the finite threshold.** The carrier inequality holds for every exact game through six players and fails for an explicit exact game at every `n>=7` by null padding.  The seven-player seed has a hand-certified exact lower envelope and Lmin point. | `paper3/sections_leximin.tex`, complete dimension threshold; `verify_n7_exact_carrier_counterexample*.py`; n6 eta-dual census and replay |
| Seven-player exact outside-pair theorem | **Proved, computer-assisted.** Although the unrestricted exact carrier inequality first fails at seven players, it still holds there whenever the outside set has size at most two; outside size three is minimal for an exact seven-player obstruction. | `paper3/sections_leximin.tex`, seven-player outside-pair theorem and outside-triple obstruction; exact census/replay artifacts |
| Totally-balanced outside-pair threshold | **Proved as a sharp fixed-dimensional result.** For `n=6`, `|S|=4`, `|P|=2`, all 619 undominated eta-dual vertex orbits satisfy the carrier bound under total balancedness.  An explicit integer totally balanced, nonexact seven-player game with `|S|=5`, `|P|=2` has `(gamma,eta)=(1,0)`, so this strengthening is dimension-sharp.  It does not refute the exact seven-player outside-pair theorem. | `results/total_balanced_outside_pair_checkpoint.md`; `paper3/N7_TOTAL_BALANCED_OUTSIDE_PAIR_COUNTEREXAMPLE.md`; `verify_n7_total_balanced_outside_pair_counterexample.py` |
| Eta-dual/minimal-balanced-collection correspondence | **Proved.** After dominated columns are removed, eta-dual vertices are precisely normalized minimal balanced collections containing the target coalition, with support at most `n`.  This is the principal bridge from the carrier problem to exact-cone combinatorics. | `paper3/sections_leximin.tex`, eta-dual vertex lemma |

## Protected false lemmas and forbidden shortcuts

The following must not be silently reintroduced.

- Uniform generators or monotonicity under majorization.
- Cycle-only or full-carrier-closure selection.
- Full nongainer maximum-overlap root-block selection.  The exact seven-player
  `(RBB-CE)` control has RBB numerator `-8`; its successful direct block is
  instead the nongainer part of labelled Lmin-tight coalition `59`.
- Universal singleton excluded-block selection.  On the complete selected
  six-player staged supports, 95 of 420 nongainer carrier cycles require an
  excluded block of size two to meet `(EDQ2)`; the quota increment law, not a
  one-source rule, governs the handover.
- Universal cycle-supported quota closure, even when a first-floor complement
  is available.  In `(QFH1)`, all six tight supports containing carrier cycle
  `(1,5)` miss `(EDQ2)`; the first-floor choice `P={2}` has quota margin
  `-2/7`.  The target-reserve criterion still closes with margin `11/3`, and
  tied root `0` simultaneously supplies a marked facet boundary control.
- Closure by one arbitrary Lmax separator.
- Gauge-invariant rooted-facet affordability.
- Automatic handover from a row of the same price-optimal marked packing.
  The returned optimizer misses a reserve closer at 77 unaffordable roots,
  but four are optimizer-selection swaps: another packing on the same optimal
  price face contains a closer.  The exact six-player audit leaves 73 genuine
  full-face obstructions, all in the co-singleton margin-`-1` class described
  above.
- Coefficient magnitude as invariant carrier currency; only normalized support
  survives the proved rescaling analysis.
- Common support as a prerequisite for mixed packet validity.
- Automatic promotion of a relative selection-cell circuit to a full
  exact-game-cone facet.
- Weighted coincidence at four roles.
- An atomic-size-independent weighted four-role overlap bound `O/T>=3/4`;
  commit `7a3a409` gives a normalized exact family at `2/3`.
- A universal `O/T>=1/2` bound for abstract endowed two-flat seesaws; the
  exact rational parameter row recorded after `(EWS5)` has ratio
  `3715/12616`.  No exact-game realization of that auxiliary row is asserted.
- Reduction of all weight vectors to `(m,1,1,1)` without proof.
- Invoking four-player rigidity on an endowed weighted quotient merely because
  its role weights are equal; the ordinary theorem requires role-level
  singleton normalization, which `(CBE)` does not require for nonunit roles.
- Inferring zero effective endowment on a common two-flat line from zero
  singleton worth of a unit role.  The singleton minimum may be attained off
  that face.  The exact `(3,1,1,1)` scope control has zero role singletons,
  common two-flat selectors, ambient line endowment `(1,0,0,1)`, and safe
  overlap `11/12`; it refutes the inference, not the atomic target.
- Treating a finite n=6/n=7 census, solver agreement, or an unsat core as a
  dimension-free theorem.

## Active dependency map

The desired all-n upper theorem currently requires all three arrows:

```text
complete staged Lmin packet + sparse labelled Lmax over-cover
                         |
                         v
direct / separator / rooted-facet / common-carrier selection theorem
              |                            |
              |                            v
              |                  atomic-weight-aware quotient bound
              |                            |
              +----------------------------+
                         |
                         v
      hybrid overlap target, equality classification, exact s(n)
                         |
                         v
 semi-balanced-system identification and full-cone facet tests by class
```

The quotient program may use the companion four-player theorem as follows:
the underlying unweighted four-role exact game has an exact-partition,
Lorenz-greatest allocation.  Unequal role multiplicities change both weighted
selectors, so this center is an additional structural witness, not an
automatic coincidence theorem.  Quantifying both weighted selectors relative
to that center is an active human-proof route.

## Current completion boundary

The main dimension-free overlap inequality, its equality characterization,
and a complete carrier/separator selection theorem remain open.  Objective A
is complete: connected edge confinement makes the common-two theorem
exhaustive, including its exact six-player equality boundary.  Objective B's
common-module contraction arm is now closed by strong induction on role
count.  In a role-minimal hard branch every carrier cycle must therefore be
split by an Lmax-tight separator.  The live arrow is the quantitative
separator/direct/marked-facet selection theorem at the current role count.
Comparison--residual cancellation and the target-reserve identity reduce its
direct arm to selecting a cycle-containing staged support satisfying `(EDQ5)`;
strict quota `(EDQ2)` is only a stronger sufficient subarm.  Every six-player
archive cycle has an `(EDQ2)` row, while `(QFH1)` has none but does have an
`(EDQ5)` row and an independently target-priced rooted facet.  Universal
selection of a target-reserve row or the separator/facet alternative remains
open.  On the rigid co-singleton residue, `(PXC5)--(PXC11)` now expose a
paired certificate: retained high-Lmax ordered-cut mass on one side and
omitted-gainer-versus-excluded-Lmin mass on the other.  The root-only
corollary closes all archived rows but fails on the fixed seven-player
control; both full certificates pass its selected repair.  Universal
selection or separator payment of this two-colour max-certificate is still
the live arrow.  The new minimum-deletion audit makes the prospective selector
incidence-theoretic and basis-independent in the archive: every full-menu
minimum row closes on 415 strict n=6 cycles and the fixed strict n=7 control,
while six nonminimum rows fail.  The next proof
obligation is therefore an exchange/Farkas alternative for the
support-minimal two-colour **maximum**, not simultaneous positivity: the new
exact n=7 control has `(PXC11)=13/24` and `(PXC6)=-1/12` on both minimum rows.
Identities `(PXC13)--(PXC16)` now reduce that arrow exactly to the full-family
inequality `min(Z_all,X_all)<=K_tau`; a failure produces strict dual
obstructions in both colours.  Minimum deletion remains a strong finite
subfamily, not the global hypothesis.  Objective C's full
equality and facet identification also remain required.
