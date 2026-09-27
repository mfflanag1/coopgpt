# CoopGT research direction review — 2026-09-04

Update after executing the recommended campaign: the sharp asymptotic constant is now proved internally to be 2, with two independent constructions and an all-n theorem. See `coopgames/paper5/asymptotic_constant_two/README.md`. The assessment below records the earlier frontier and motivation; its open first-order constant is now resolved. External significance and novelty assessment remain pending.

Reviewed the recovered conversation, central manuscript proofs, campaign and no-go ledgers, core-closure reduction, chamber-reduction candidate, and primary literature. Three independent review agents examined construction correctness, campaign trajectory, and universal geometry. This is a targeted mathematical and strategic review, not a replay of every archived computational certificate or an external specialist verdict. Reviewed checkpoint: 059605a05a90981abe25c577f96ca60eaf231864.

## Opinion

Continue the project, but change the allocation of effort. PXC151 is credible mathematical progress within the selected problem. The history contains a clear period of local entrapment in increasingly elaborate reformulations; PXC151 is a successful escape. The latest recommendation to determine the sharp asymptotic constant is sensible, but prescribing 3+2 sqrt(2) as the expected answer is not supported by a global extremal argument.

Field-level importance remains unestablished. This project defines and advances a natural extremal question, but a difficult constant in a self-selected metric is not automatically a central problem for cooperative game theory. A reusable structural theorem, connection to natural game classes, or expert confirmation of a recognized gap would make the significance case stronger.

## What deserves to survive

1. PXC151 has a short, conventional proof. Its three efficient nonnegative generators establish exactness immediately; the floor face is a singleton; a normalized sparse minimax dual and two further row families pin the entire other selector. Independent algebraic review found no substantive gap in the stated parameter range. See coopgames/paper5/divergence.tex:11420.
2. It improves the construction's asymptotic deficit coefficient from 8 to 3+2 sqrt(2), with O=2m+r+2 and T=2mr+m+r+1. This changes the constant, not the previously known construction's rate. Global optimality remains open.
3. The n+2-generator exactification is an especially useful general reduction. Both selected allocations and one zero-coordinate witness per player suffice for a lower-envelope realization preserving the selector pair. It supports unrestricted adversarial synthesis without a guessed bounded-role representation. See coopgames/paper5/CORE_CLOSURE_REDUCTION.md:95.
4. PXC147–150 produced useful scoped no-go results: their tight-row obstructions led directly to abandoning the old pair-menu floor mechanism and discovering PXC151. Negative results were productive when they changed the construction.

## Evidence of local entrapment

- PXC119–140 repeatedly developed pricing, packet, transport and stationary-flow machinery around an unresolved quantitative overlap inequality. MECHANISM_PRICE_PROGRAM.md:751–773 explicitly records a point where the reformulation still requires essentially the original bound. PXC143 subsequently falsified the n>=6 target at n=7.
- Release replays, independent encodings and detailed atlases give confidence in statements. Their volume does not establish importance or make an unproved all-dimensional implication more likely. The new conceptual work should receive most of the research effort; full legacy replay belongs at coherent release boundaries.
- The 183-page manuscript has not been reorganized around its strongest contribution: PXC151 is absent from the abstract, and divergence.tex:299 still calls an upper bound matching the old benchmark open even though later constructions refute it.
- The r=2 'handover' pastes an older family into the index set. This is disclosed and valid as a convention, but it should not be counted as a separate extension theorem.
- A modest-n construction gate can reject a genuinely superior asymptotic family whose crossover occurs later. Derive its symbolic leading coefficient and crossover before retiring it solely for losing at one small n.

## Reconstructed universal geometry

The missing PXC152 release artifacts should be rebuilt, but the reported mathematical bound can be independently established with a short argument. In fact there is a slightly stronger generic bound.

Let n>=2, T>0, and K be a nonempty compact convex subset of {y>=0: sum y_i=T}. Let x maximize the minimum coordinate and z minimize the maximum coordinate on K; full lexicographic selectors satisfy these conditions. Define a=min x_i, M=max z_i and O=sum min(x_i,z_i). Then

    O >= T/(n-1), hence ||x-z||_1/T <= 2-2/(n-1).

Proof. If x=z the claim is immediate. Otherwise a<M, since a>=M together with equal totals would force both points to be uniform. Some index i with z_i=M has x_i>=M: otherwise a sufficiently short move from z toward x lowers every top coordinate and hence lowers the maximum. Similarly some index j with x_j=a has z_j<=a: otherwise a short move from x toward z raises every bottom coordinate and hence raises the minimum. These indices are distinct because x_i>=M>a=x_j. Therefore

    O >= M+z_j,
    T <= (n-1)M+z_j <= (n-1)(M+z_j) <= (n-1)O.

This proves the claim. It uses neither coalition inequalities nor exactness nor later lexicographic stages. Combined with the existing all-n construction bounds it establishes deficit order Theta(1/n); the asymptotic lower constant remains 2. This mathematical reconstruction does not establish completion of the lost PXC152 release run.

## A concrete barrier to the last campaign direction

Convexity and simultaneous full lexicographic optimality cannot improve the asymptotic coefficient above 2. Even adding zero-coordinate attainment is insufficient.

Normalize T=1. For n>=4 choose

    0<a<(n-3)/((n-1)(n-2)),
    x=(1-(n-1)a,a,...,a),
    z=(1/(n-1),0,1/(n-1),...,1/(n-1)),
    K=conv{x,z,e_1,e_3}.

Here e_i is the ith unit vector. Every coordinate has minimum zero on K. Coordinate 2 equals a only at x, so x is the unique maximin point and consequently the leximin point. At z, coordinates 1 and 3 sum to 2/(n-1). At every other displayed vertex they sum to strictly more: at x their sum is 1-(n-2)a, and at each unit vector it is 1. Consequently every non-z point has a coordinate exceeding 1/(n-1), making z uniquely minimax and thus the full leximax-min point.

The overlap is

    O=1/(n-1)+(n-2)a.

For example a=n^(-3) gives n(2-rho)=2nO -> 2. This is an abstract convex-set control, not a claimed exact-game core. It satisfies both selector requirements and all coordinate-zero attainments; what it lacks is an established realization by coalition-sum inequalities.

Therefore a stronger exact-game theorem must use the special coalition-normal geometry, or an equivalent condition for preservation of selectors under coalition closure. A proof using only generic nested faces, convexity and coordinate-zero witnesses cannot suffice. This is a sharper research obstruction than simply asking for more coupled KKT machinery.

## Technical repairs to keep separate from research advances

- SHARP_ASYMPTOTIC_GAP_PROGRAM.md:56 incorrectly states O>=a*|supp z|. PXC151 itself has x_i=a=1 and 0<z_i<1 on U. The intended final bound O>=a*T/M is valid by min(x_i,z_i)>=(a/M)z_i; remove the false support-cardinality step.
- SHARP_GAP_CHAMBER_REDUCTION.md is explicitly a candidate with unresolved boundary and forced-stratum obligations. Its conclusion is plausible, but the prose proof is incomplete. With variable dual multipliers and variable RHS, objective equality is not automatically linear; substitute fixed dual basic solutions first. Exact strata can merge on boundaries, and uniqueness alone does not prove closedness. A fixed-matrix lexicographic LP using sums of the k smallest coordinates offers a cleaner repair. Even when repaired, fixed-n piecewise affine structure gives no uniform compression theorem.

## Recommended next campaign

1. Consolidate a short theorem-first manuscript: the original near-disjointness phenomenon, PXC151's improved family, the elementary universal bound, and the precise gap 2<=c_*<=3+2 sqrt(2). Move the historical mechanism catalog and large finite audits to supplements. Seek specialist judgment now on both correctness and importance; do not wait for a claimed final breakthrough.
2. Make coalition closure the first structural test. Begin from the explicit abstract near-extremizer above, form the game v(S)=min_{y in K} y(S), and determine exactly which new feasible allocations in its core alter the two selectors. Seek a quantitative obstruction or a way to realize comparable separation by genuine exact cores. Zero attainments and exactness of this lower-envelope game are immediate; selector preservation is the difficult issue.
3. Use the n+2 normal form for a separate adversarial route. Search selector certificates and coalition incidence patterns with asymmetric witnesses and growing role counts. Derive symbolic scaling before large numerical searches. A better infinite coefficient is evidence to change the candidate answer.
4. Promote a route only for a stronger universal constant, a better infinite family, a quantitative coalition-closure theorem, or a demonstrably useful uniform extremal reduction. Two phases yielding only restatements of the missing inequality trigger a representation change.
5. If the constant remains resistant, pursue a theorem relating disagreement between fairness priorities to a structural failure of Lorenz domination, or establish the phenomenon in a natural combinatorial-game class. Those connections may have more field-wide value than another small numerical improvement.

## Primary-source context checked

- Vazirani, Fair Core Imputations for the Assignment Game, latest listed arXiv version v6 (2025): https://arxiv.org/abs/2402.11437. Provides fairness solution concepts and strongly polynomial algorithms. This confirms an active substantive neighboring question; it does not establish novelty of the project's separation bound.
- Gangam et al., Equitable Core Imputations for Max-Flow, MST and b-Matching Games, latest listed v3 (2025): https://arxiv.org/abs/2403.06037. Their algorithmic guarantees concern Owen sets for these games; transferring conclusions to whole exact cores requires proof.
- Schoot Uiterkamp, A Characterization of Simultaneous Optimization, Majorization, and (Bi-)Submodular Polyhedra: https://doi.org/10.1287/moor.2023.0054 and https://arxiv.org/abs/2201.06596. Connects simultaneous fairness optimization to polyhedral structure, a useful model for a broadly reusable structural result.
- Studeny and Kratochvil, Facets of the cone of exact games (2022): https://arxiv.org/abs/2103.02414. Supplies established semi-balanced facet theory; it does not by itself imply selector-chamber extremizers lie on exact-cone extreme rays.

This source check did not establish an equivalent published separation theorem. That is not a novelty certification. The recommended significance claim is currently 'a credible extremal contribution with a promising structural research question,' pending external review.
