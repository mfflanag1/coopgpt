# Sharp frozen-ideal subsidy — active

[Current universal upper bound](CORE_COMPATIBILITY_UPPER.md) and [lower-bound construction](SHARP_SUBSIDY.md): **1/3 <= S_3 <= 39999/100000**. The sharp constant remains unresolved. The new label-tree family has exact subsidy 2q and original worth 3(2q+1). Its all-parameter proof and integer certificates are included. Worldwide novelty and external review remain unconfirmed.

The [September 20 audit](audit_20260920/AUDIT.md) completed a bounded proof review and strengthening attempt: the local affine coefficient is sharp at 13/18 with intercept 1/18, and the specified aggregate relaxation stops at 29/82. That obstruction is not a market counterexample. Historical next-step statements below record the campaign trajectory; they do not represent newly running goals.

Run `bash build.sh` for standard-library exact verification. To include the optional original-family SMT checks, run `COOPGT_PYTHON=/path/to/python-with-numpy-scipy-z3 bash build.sh --smt`. The tree certificates do not require a solver.

The primary next step is to prove the fractional-packing inequality in SHARP_SUBSIDY.md or find a certified counterexample. An LP formulation, finite checks, and these bounds are not completion of the sharp-constant goal.

[New exact reductions](REDUCTIONS.md) show that it suffices to analyze connected sparse markets supported on two matchings, using replication to handle fractional obstructions. An independent exact verifier also proves zero subsidy for all two-player-per-sector markets. An exact heterogeneous counterexample rejects a proposed stronger tree-induction bound. None of these results closes the sharp-constant gap.

[Leaf and deletion results](LEAF_AND_DELETION.md) prove that an obstruction exceeding one-third must have at least four leaf labels after reduction. Exact deletion certificates handle five specified matching configurations for all nonnegative pair coefficients. A uniform construction for the remaining leaf-rich class is still missing.

[Uniform deletion theorem](UNIFORM_TEMPLATE.md) now supplies a closed-form construction under an explicit count condition, covering chains of every length and the three-branch star. A separate exact certificate handles the first two-junction tree outside that condition. The multiple-junction extension and the full sharp constant remain unresolved.

The earlier upper-bound milestone was 2/5, improving 5/12; it is superseded by the 39999/100000 bound above. It uses surplus at degree-two and degree-three labels, with an all-size proof, 127,618 independently checked rational packing entries, and six optional exact real-arithmetic budget checks. Earlier proofs remain in SURPLUS_UPPER.md and UNIVERSAL_UPPER.md. The sharp one-third conjecture is still open.

[Pair-budget counterexample](PAIR_BUDGET_NO_GO.md) rules out two cycle-removal shortcuts: zero diagonal pair budget and zero change in grand worth after deleting one pair matrix can both coexist with positive frozen-ideal subsidy. Its nine-player example has exactly T=6, all H_i=2, and s_3=1.

[Grafted stress-pattern theorem](GRAFTED_STRESS_BOUND.md) certifies that the fixed obstruction in the near-worst 23-label count example is at most 0.318841253 across all admissible pair weights. An exact primal attains 22/69. This exposes slack in the universal template on that pattern; it does not bound other packings or close the global gap.

[Variable P-weight direction](VARIABLE_P_DIRECTION.md) supplies exact one-third certificates for two-, four-, and eight-junction patterns using only same-sector transfers. The 4,177 rational entries show that cross-sector transfers are unnecessary for these examples. A transportation lemma isolates the unresolved general choice of row marginals; no new global bound follows yet.

[Local-rule no-go theorem](LOCAL_RULE_NO_GO.md) exactly excludes the single-baseline incidence formula at 16 junctions: its coverage parameter is below 1. Exact extraction also calibrates all transportation inequalities on 102 retained deletion rows. The next weight-selection mechanism must go beyond this particular local formula.

[Free-source priority audit](FREE_SOURCE_AUDIT_20260907.md) adds specific comparisons with almost-core optimization, an August 2026 matching preprint, and coordinate-maximization/subsidy models. It also records the exact equivalence to ordinary cost of stability after auxiliary singleton strengthening. The potential contribution is the restricted assignment-market theorem, not the generic optimization framework; priority-game and earlier original-source gaps remain open.

[Tree-cut transportation](CUT_TRANSPORT.md) proves exact rooted-incidence identities and constructs one-third certificates for 2, 8, and 16 junctions using rational max flow. A sector-imbalanced chain exactly rejects these fixed cut weights as a universal rule. The 20,073 certificate entries pass independent verification; the global bounds are unchanged.

[Zero-subsidy ring theorem](RING_ZERO_SUBSIDY.md) excludes the uniform cyclic junction family for all sizes. [Next phase](NEXT_PHASE.md) prioritizes a structural one-third proof, challenged by heterogeneous and multiple-cycle markets. The sharp goal remains active.

[Heterogeneous cyclic pattern bounds](CYCLIC_PATTERN_BOUNDS.md) certify six selected obstructions below one-third across all admissible pair weights, including K3,3, prism, and cube incidence supports. Each has an explicit market with exactly certified full subsidy. These finite-pattern results leave the universal sharp bound unresolved.

[Harmonic-rule rejection](HARMONIC_SECTOR_NO_GO.md) proves t<0.967618 on a 25-label tree even with separate sector parameters and flexible diagonal transfers. An exact 1,605-entry unrestricted certificate reaches t=1 on the same tree. This retires the harmonic mixture rule while leaving the general transportation route open.

[Tree slack identity](TREE_SLACK_IDENTITY.md) proves a size-independent budget of three for coverage surplus, diagonal/order losses, and unused sector capacity in any same-sector tree certificate at t=1. It gives the model ceiling t<=1+1/m and necessary equality conditions. Exact checks cover 315 rows and 25,855 entries; universal feasibility is still open.

[Integral assignment barrier](TREE_INTEGRAL_BARRIER.md) rules out sector-balanced binary P weights with maximal root-monotone diagonals on every incidence tree having at least four degree-two labels. Fractional transfers do not repair this restriction. A fractional control works on the same 11-label chain; exact row enumeration and reduced SMT checks corroborate the proof.

[Convex-hull barrier](TREE_CONVEX_HULL_BARRIER.md) extends the integrality restriction to arbitrary averages of integral deletion matchings on the sector-balanced E=0 face. Twelve rows of the fractional chain control violate an explicit valid hull inequality by 2/3 each. [Quint source lead](FREE_SOURCE_LEAD_QUINT.md) records the UCLA report number; the original text remains unavailable.

[Constructive low-hub-count theorem](ONE_HUB_THEOREM.md) proves the one-third obstruction bound for every incidence tree with at most one degree-three label, without a leaf-balance assumption. A convex existence argument reduces exact construction to six rational variables and at most 1,330 three-plane solves. Ten certificates contain 27,514 verified entries; six cases lie outside the old uniform criterion. Any obstruction above one-third must therefore have a cyclic component or an acyclic component with at least two degree-three labels.

[Leaf-dilation lifting theorem](LEAF_DILATION_THEOREM.md) expands a stationary, sector-balanced seed to an all-size family. The exact 366-entry seed yields one-third certificates for a two-hub family with m=18k-7 for every k>=1; four lifted checks cover 26,627 entries. This does not cover arbitrary two-hub trees. The note also proves contraction of degree-two links within the leaf-only E=0 certificate model.

[Two-hub block reduction](TWO_HUB_BLOCK_REDUCTION.md) classifies the two central-port cases and their admissible leaf-count data. A sufficient compressed model has at most 390 variables, independently of sector size. Six full rational certificates, including both port cases and nonuniform counts, contain 35,221 verified entries. Arbitrary count feasibility and composition across hubs remain unresolved.

[Common-denominator barrier](COMMON_DENOMINATOR_BARRIER.md) rules out a single affine normalization of aggregate block weights and leaf flows across all independently growing count arrays, including positive baselines. Exact Farkas certificates with 8 and 13 constraints corroborate the narrower coefficientwise search. Five hundred numerical pointwise cases remained feasible; no universal feasibility or improved global bound follows. Two failed affine variants retire that route.

[Root-mass balance](ROOT_MASS_BALANCE.md) proves R>=g+2 in the leaf-only E=0 tree model. Equality forces all transfer supply to leaves and exactly one unit of total hub slack. Both two-hub seeds attain R=4 with 857 independently checked entries; 500 equality-constrained numerical count cases remain discovery evidence. This supplies a concrete composition invariant, not a universal existence theorem.

[Hub rebalancing theorem](HUB_REBALANCING.md) proves that a specific one-hub certificate cannot be extended by freezing surviving old P weights. The enlarged support satisfies a sharp cut W<=17, while the old weights give 35/2. A 73-constraint exact proof and three fully checked controls (914 entries) distinguish this joining-rule failure from certificate nonexistence. A viable induction must rebalance existing weights.

[Joint transfer-cut requirement](COMPOUND_TRANSFER_CUTS.md) gives the exact fixed-weight flow criterion and an m=27 rational counterexample to hub balance plus singleton/full cuts. Its two-block cut fails by 285781/607050 despite R=4 and hub loads 7/2 each. A different exact certificate on the same tree has 1,995 verified entries and passes all 96 cuts. Composition must preserve joint transfer capacity; max-flow itself is an established ingredient.

[Broken-ring theorem](BROKEN_RING_THEOREM.md): lowering one pair value from 2 to 0 in the zero-subsidy ring preserves T=12b but produces H_i=3 and exact subsidy 4b-2 for all b>=2. This proves nonmonotonicity across original markets and gives a cyclic family approaching one-third. The global bounds remain unchanged.

[Exact cyclic frontier](CYCLIC_FRONTIER.md) validates 21 retained unicyclic fixed-P optima, proves that degree and sector leaf counts do not determine that optimum, and checks six full-ideal markets independently. A stronger submatching exposes why a fixed-P bound is insufficient to bound every obstruction of the witness market. Global bounds are unchanged.

[Cycles are necessary in an optimal obstruction](CYCLIC_OPTIMA_REQUIRED.md): an exact m=11 market has a unique diagonal grand matching, and every optimal team-form subsidy dual contains a two-cycle support. This rules out a forest-only optimal-certificate restriction on the original market, including fractional duals. Its exact subsidy is 76/303, below one-third.

[Sector-minimum core representation](SECTOR_MINIMUM_CORE.md) replaces unrestricted third-player constraints by three auxiliary variables and local completions, with an all-size equivalence proof covering repeated-label teams. Its completion difference bounds also hold for the original ideal vector. The independent checker uses symbolic coefficient identities and rational witnesses; no new global subsidy bound is claimed.

[Limits of ideal-difference constraints](IDEAL_DIFFERENCE_LIMITS.md): valid global-range and P-induced bounds still admit a false 3/8 obstruction on an exactly certified zero-subsidy market. This rejects replacing original coordinate-attaining witnesses by the tested necessary inequalities; it is not a counterexample to the sharp one-third conjecture.

[Attainment frontier](COATTAINABILITY_FRONTIER.md) connects a published supermodular safe class to zero subsidy and proves that the lower-bound family requires exactly 3(q+1) separate core allocations to attain all unmatched ideals. The [free-original follow-up](FREE_SOURCE_ATTAINMENT_AUDIT.md) closes the Bejan-Gomez definition comparison; no novelty or global sharpness is established.

[Repeated-label unicyclic audit](REPEATED_UNICYCLE_AUDIT.md) exhaustively covers the 216 labeled patterns at m=4 with two P-teams and a repeated label. Two symmetry representatives each have exact fixed-P obstruction supremum 1/6. This finite calibration does not settle all-unicyclic supports or the full subsidy.

[Priority-games original comparison](PRIORITY_ORIGINAL_COMPARISON.md) retrieves the free accepted manuscript and identifies the frozen-floor covering problem as ordinary cost of stability for a maximum of weak-priority transformations. This strengthens attribution of the generic intervention to established ingredients; novelty of the structural bounds remains unconfirmed.

[Cycle-boundary limitation](CYCLE_BOUNDARY_LIMIT.md) exactly rejects preserving the fixed-P optimum after zeroing an arbitrary prescribed cycle pair, even with all other weights reoptimized. The six-label gap is at least 4/801; adaptive edge selection remains unresolved.

[Adaptive cycle-boundary limitation](ADAPTIVE_BOUNDARY_LIMIT.md) strengthens the prescribed-edge counterexample: a six-label support has F(P)=2/9, but zeroing any of its three cycle pairs gives F<=58/267 even after all other weights are reoptimized. Retire both zero-pair boundary variants; the global one-third question remains open.

[Finite-size upper correction](FINITE_UPPER_CORRECTION.md) sharpens each reduced integral obstruction to J/T<=2/5-1/(60h) and proves every finite original market has subsidy ratio strictly below 2/5, via rational replication. This does not improve the supremum bound. Fourteen rational certificates and six real-domain budget checks corroborate the conventional proof; external review remains outstanding.

[Near-ceiling localization](EXTREMAL_LOCALIZATION.md) proves that reduced obstructions approaching 2/5 must have balanced sector leaf counts, negligible degree-two density and negligible cycle rank relative to h. This necessary condition narrows the unresolved region; it is not an existence result, cycle-removal theorem or improved supremum bound.
