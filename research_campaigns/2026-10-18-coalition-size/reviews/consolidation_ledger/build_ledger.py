"""Build a source-linked consolidation snapshot; does not rerun mathematics."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

CAMP = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
entries = []

def add(id, group, title, claim, domain, limits, sources, reviews, status, brief):
    entries.append(dict(id=id, group=group, title=title, exact_claim=claim,
        domain_and_quantifiers=domain, does_not_establish=limits,
        source_paths=sources, review_paths=reviews, audit_status=status,
        handoff_summary=brief))

add('M1','1_main_unrestricted_lower','Projective square-root lower',
 'For every integer s>=1, K3(s)>=sqrt(s/6). For M>=1, Q_M=product_{m=2}^M 2m/(2m-1)=4^M/[2 binom(2M,M)], and the witness forces K>=1+2(M-1)Q_M/(3M) using protected size 2M-1. Current interval: Omega(sqrt(s))<=K3(s)<=K3_OUT(s)<=3s^2.',
 'Every arbitrary nonnegative payment rule on the witness full real report boxes, with every coalition covered at every profile and TCWM for all actual coalitions of size<=s. No formula, anonymity, continuity or dummy-zero assumption. Witness: n=2M+1 fully eligible owners, d=2^(M+1)-1 rows, unit-profit arity exactly3. Lower transfers to full OUT. The 3s^2 upper is imported baseline work.',
 ['No general upper improvement or matching unrestricted optimum.', 'No polynomial-row construction; resource dimension is exponential.', 'For an asymmetric rule, a costly profile lies somewhere in the finite symmetry orbit, not necessarily at the named representative.', 'No historical-priority clearance or formal proof-assistant verification.'],
 ['lower/PROJECTIVE_SQUARE_ROOT_LOWER.txt','inputs/energy/BOUNDED_COALITION_SPARSE_PRODUCTION.txt'],
 ['reviews/PROJECTIVE_ROOT_ACCEPTANCE.txt','reviews/growing_projective_audit.txt'],
 'Root accepted after independent native derivations, author/independent/root exact replays, and opposite-model proof reviews. Opposite reviews did not execute code. The weaker cube-root proof is superseded.',
 'The one main unrestricted contribution: improve the lower exponent from1/4 to1/2; the upper remains3s^2.')

add('M2','1_main_unrestricted_lower','Tail, general arity and joint-count corollaries',
 'For k=r-1>=2, a_m=min(s-1,k(m-1)), P=product_{m=2}^M a_m/(a_m+1), every witness gives K>=1+[k(M-1)/(k+1)]P. For s>=2 its maximum over ladder length is at M=s,s+1. With h=ceil(s/k), alpha=(s-1)/s and Q_{k,h}=product_{m=2}^h km/[k(m-1)+1], B_{k,s}=1+k(s-1)Q_{k,h}alpha^(s-h)/[(k+1)h]. Hence K_r(s)=Omega_r(s^((r-2)/(r-1))). At k=2, B_s/sqrt(s)->sqrt(2pi)/(3sqrt(e)); B_6=493/243. For at-most counts, K_r^{<=}(n,d,s)=Omega_r(min{s,n,log(d+1)}^((r-2)/(r-1))).',
 'Fixed r>=3; arbitrary mechanisms with the same all-real contract as M1. The k,M witness has n=1+kM, d=2^(1+(k-1)M)-1. The at-most-count claim uses admissible M satisfying both counts, not padding to exact counts. The arity3 s6 exhibit has13 fully eligible owners and127 rows.',
 ['Tail optimizes this particular certificate, not the true optimum.', 'General-r result is a corollary of the same construction, not a second arity3 advance.', 'The logarithmic row dependence cannot be dropped.', 'No distinct paper count is assigned to constants, small examples or count corollaries.'],
 ['root/PROJECTIVE_BOUNDED_COALITION_TAIL.txt','lower/GENERAL_ARITY_CIRCUIT_LOWER.txt','root/GENERAL_ARITY_TAIL_AND_DIMENSION_COROLLARY.txt'],
 ['reviews/projective_bounded_tail_audit.txt','reviews/GENERAL_ARITY_ROOT_AUDIT.txt','lower/GENERAL_ARITY_TAIL_REVIEW.txt'],
 'Parent general-arity theorem accepted by root/opposite review. Tail and joint-count algebra have separate native audits and exact replays. Combined-corollary source retains a stale pending line despite PASS audit and later root acceptance record.',
 'Group the tail constant, general-r exponent, s6 example and count bounds with M1; they do not add unrestricted arity3 contributions.')

add('M3','1_main_unrestricted_lower','Pure-owner realization',
 'The same projective lower and tail B_s hold with one fixed pure unit owner per projective row. For general r, n=d=2^(1+(r-2)M)-1; the resulting count dependence is Omega_r(min{s,log(n+1),log(d+1)}^((r-2)/(r-1))).',
 'One fixed actual owner per resource, scalar binding report in[0,1], all real report profiles. Symmetrization uses the JOINT resource/owner GL action. At arity3 and M=s, n=d=2^(s+1)-1.',
 ['Cannot combine pure ownership with the fully eligible construction\'s O(s) owner count.', 'Profilewise cap/veto at displayed profiles is not a globally indispensable owner.', 'No new exponent or polynomial-dimension claim.'],
 ['root/PROJECTIVE_PURE_OWNER_REALIZATION.txt','root/GENERAL_ARITY_TAIL_AND_DIMENSION_COROLLARY.txt'],
 ['lower/PURE_OWNER_REVIEW.txt','reviews/PROJECTIVE_ROOT_ACCEPTANCE.txt','reviews/UNIT_WORTH_IDEAL_ROOT_DISPOSITION.txt'],
 'Independent domain-transfer review and root checks accepted; later opposite-model reviews cover the joint action and pure lower. Original main opposite snapshot predates this refinement.',
 'A second ownership realization of the same theorem, with exponential owners as well as rows.')

add('R1','2_restricted_sharpness_and_barriers','Fixed signed linear worth rules',
 'For fixed integers r>=3,s>=2, every admissible family y_i^(n)(b)=sum_S alpha_{n,i,S} F(b_S) with report-INDEPENDENT finite real coefficients has liminf_{n->infinity} kappa_n>=s^(r-1)/r on the single technology F=min_r.',
 'For each n the same fully eligible unit box[0,1]^r for every actual owner; coefficients may depend on n, labels, technology and box. Nonnegative payments, all-coalition coverage and TCWM for every size1..s. Signed coefficients, dummy payments and nonanonymous inputs are allowed.',
 ['Not an arbitrary-mechanism lower.', 'Does not cover report-adaptive coefficients or nonlinear worth rules.', 'Coefficient positivity is for the nonredundant min_r basis, not every technology/representation.'],
 ['constructive/FIXED_LINEAR_WORTH_RULE_QUADRATIC_BARRIER.txt','constructive/SIGNED_FIXED_MARGINAL_POSITIVITY.txt'],
 ['reviews/FIXED_LINEAR_ROOT_DISPOSITION.txt','reviews/priority_projective/FIXED_LINEAR_PRIORITY_ADDENDUM.txt'],
 'Root and opposite-model proof review accepted after scope repairs; exact isolator replay is supporting finite evidence, not verification of the limiting argument. Source opening still says candidate.',
 'Quadratic arity3 obstruction for all fixed signed worth-linear formulas; keep distinct from the square-root unrestricted lower.')

add('R2','2_restricted_sharpness_and_barriers','Globally shared adaptive positive mixtures',
 'For fixed r,s>=2, any family y_i(b)=integral m_i(p;b) dmu_b(p), with a finite nonnegative measure common to all owners at each profile, and one uniform finite factor across all finite arity<=r institutions, needs K>=s^(r-1)/r. The same lower holds for common report-adaptive nonnegative uniform-cardinality weights.',
 'Arbitrary profile/technology/label dependence of the one shared measure or cardinality vector is allowed. Actual owner roster, including zero reporters, is fixed per institution. The cardinality proof fixes a finite local test list and D at least the number of other local owners before population N grows; it uses selected-cycle error, not vanishing total error.',
 ['Not a lower on every fixed min_r adaptive rule.', 'Owner-specific, active-component-specific and report-sensitive subset weights are outside.', 'Public connectivity alone does not evade the construction, but active-component adaptation may.', 'Does not exclude arbitrary report-adaptive mechanisms.'],
 ['constructive/ADAPTIVE_GLOBAL_MIXTURE_RIGIDITY_BARRIER.txt','constructive/ADAPTIVE_CARDINALITY_RIGIDITY_EXTENSION.txt'],
 ['reviews/ADAPTIVE_GLOBAL_MIXTURE_ROOT_DISPOSITION.txt','reviews/CARDINALITY_AND_DUAL_NORMAL_FORM_ROOT_DISPOSITION.txt','reviews/cardinality_rigidity_audit/CARDINALITY_AUDIT.txt'],
 'Root/native/opposite reviews accepted the stated steps. Opposite packet omitted the cardinality extension itself; root checked its explicit owner-count hypothesis. Earlier pending-extension wording is stale.',
 'Shared global adaptation remains quadratically costly at arity3; owner-specific adaptation remains open.')

add('R3','2_restricted_sharpness_and_barriers','Minimum-norm and total-penalty selector failures',
 'On the exact seven-owner two-branch arity3 fixture, minimizing (1/2)sum y_i^2+psi(sum y_i) over nonnegative coalition covers, for any finite convex nondecreasing psi even chosen by profile, violates size3 TCWM by at least1/40. Every fixed positive quadratic total penalty lambda also fails pair TCWM for sufficiently many cap owners; the exact pre-zero pair threshold is lambda>1/[R(R+3)]. Unweighted Lp selectors fail TCWM for1<p<=2, while p>2 has unbounded owner-independent funding.',
 'The named optimization architectures and fixture domains; every coalition coverage constraint is retained. The s2 statement concerns lambda>0 independent of owner count, not the unpenalized case.',
 ['Does not reject unpenalized quadratic selection at s2.', 'Does not rule out arbitrary weighting/objectives or arbitrary mechanisms.', 'A correct O(s) objective-derived budget alone supplies no incentive proof.'],
 ['root/MINIMUM_NORM_COVER_OBSTRUCTION.txt'],
 ['reviews/minimum_norm_independent_audit.txt','reviews/SCOPED_RESULTS_REVIEW_DISPOSITION.txt'],
 'Accepted after independent actual-subset/KKT checks and opposite-model review. Opposite reviewer caught the s2 overstatement; source body repaired, opening pending line stale.',
 'Architecture counterexamples, with the size2 versus size3 distinction retained.')

add('R4','2_restricted_sharpness_and_barriers','Three-statistic convex cover selectors',
 'The fixed four-owner arity3 restoration defeats positive quadratic cover weights that identify owners only by (V,f_i,g_i), including arbitrary profile-adaptive common weight functions, nondecreasing total penalties and feasible total caps: protected pair payment falls from2/3 to at most3/5. A branch chain yields funding at least(M+2)/3 for the stated common strictly-convex nondecreasing scalar-feature costs if all pair-TCWM comparisons hold.',
 'V=F(B), f_i=F(b_i), g_i=max_{0<=a<=B-b_i}[F(a+b_i)-F(a)]-f_i. Equal feature triples must have equal common costs/weights at a profile. Nonsmooth common-cost chain and owner-specific smooth appendices have distinct hypotheses, including zero slope at0 where stated.',
 ['Not an exclusion of arbitrary scalar summaries, owner-label or bundle-direction-specific objectives.', 'The chain lower is conditional on satisfying every specified pair comparison.', 'Not an unrestricted funding lower.'],
 ['constructive/SCALAR_IMPORTANCE_QP_FAMILY_OBSTRUCTION.txt'],
 ['reviews/SCALAR_SUMMARY_SELECTOR_ROOT_DISPOSITION.txt'],
 'Root and opposite-model proof review accepted; weak original vector checks were strengthened to actual potential maxima and complete QP KKT certificates and replayed by root.',
 'The exact (V,f,g) feature restriction is essential; do not summarize as failure of all convex selection.')

add('R5','2_restricted_sharpness_and_barriers','Worth-only Pareto-minimal selection',
 'For n=M+2 common-unit-box owners on the M-branch arity3 cap technology, every worth-only rule that always selects a Pareto-minimal nonnegative cover and satisfies pair TCWM needs K>=n/3. Without minimality, the symmetrized chain rule obeys removable reserve 2t+q-1>=1/3-K/M.',
 'Worth-only means dependence on the entire coalition-worth vector, not full bundle directions; fixed technology/labels/box may be used. The averaging proof uses convexity only of the special chain games\' minimal sets.',
 ['Not an arbitrary-mechanism lower.', 'The quantitative removable-reserve statement is for the symmetrized rule, not every asymmetric output.', 'Does not show all Pareto-minimal sets are convex.'],
 ['constructive/WORTH_ONLY_PARETO_MINIMAL_COVER_BARRIER.txt'],
 ['reviews/PARETO_COVER_ROOT_DISPOSITION.txt'],
 'Root and opposite-model reviews accepted after narrowing the asymmetric reserve wording.',
 'A uniformly bounded worth-only rule must sometimes choose a nonminimal cover.')

add('R6','2_restricted_sharpness_and_barriers','Aggregate-only common prices',
 'For rules y_i(b)=p(sum b)*b_i on common fully eligible unit cubes, singleton TCWM implies all-size TCWM on endpoint pairs with aggregate capacities<=1. Projective witnesses then force K=Omega(sqrt(n)) at arity3, and Omega_r(n^((r-2)/(r-1))) for fixed r>=3, already under singleton incentives.',
 'The same finite resource price depends only on aggregate supply and institution, not its partition among actual owners. Fixed-roster auxiliary profiles are admissible in the common unit cube. Counts grow along the parent construction.',
 ['Not a lower on full-profile-dependent prices or typed rights.', 'No fixed-row impossibility or additional unrestricted exponent.', 'Auxiliary profiles do not merge actual strategic owners.'],
 ['root/AGGREGATE_COMMON_PRICE_OBSTRUCTION.txt','constructive/AGGREGATE_COMMON_PRICE_INDEPENDENT_CHECK.txt'],
 ['reviews/AGGREGATE_PRICE_ROOT_DISPOSITION.txt'],
 'Root, independent native check and opposite-model corollary review accepted; source opening pending line is stale. Opposite corollary review did not redo all parent proofs.',
 'A parent-theorem architecture corollary: aggregate supply alone loses essential ownership information.')

add('R7','2_restricted_sharpness_and_barriers','Sharp binary unit-worth ideal',
 'Across finite linear3-uniform unit-profit/unit-coefficient hypergraphs with one pure binary unit owner per row, on the ENTIRE downward ideal F(S)<=1, worst optimal TCWM and full-OUT factors both equal B_s from M2 (B_1=1).',
 'All coalitions covered; all comparable binary endpoints in the ideal and all actual protected coalitions tested, including inactive/passive owners. Matching lower is over sufficiently large projective institutions.',
 ['Not an upper rule on the all-real report box.', 'No conclusion for higher-worth, nonbinary or nonlinear-hypergraph profiles.', 'No certificate confined to this ideal, even branching, improves the square-root growth; other domains remain open.'],
 ['lower/branching_pilot/UNIT_WORTH_LINEAR_DOMAIN_THEOREM.txt'],
 ['reviews/UNIT_WORTH_IDEAL_ROOT_DISPOSITION.txt'],
 'Root and opposite-model proof reviews accepted after explicit basis/all-coalition scope repairs; root exact replay recorded. Source header/closing pending lines are stale.',
 'Matching sharpness only on a restricted binary ideal; never pair this upper with M1 as a solved unrestricted frontier.')

add('R8','2_restricted_sharpness_and_barriers','Complete-fiber projection and sharpness',
 'For fixed binary subspace W of size R, F_V(lift S)=R F_Q(S) for every complete-fiber binary profile with W rows absent. Restricting to quotient worth<=1 gives worst optimal funding1 when s<R and B(s/R) when s>=R, with matching lower over sufficiently large quotients; uniformly O(sqrt(max(1,s/R))).',
 'Fixed actual pure owners, fixed W, complete-fiber report profiles. Protected coalitions may contain arbitrary partial selections of unchanged fiber members, but a changed fiber costs R actual restoring members. B(t) is the continuous-parameter recurrence in the source, not unqualified integer B_s.',
 ['No partial-fiber report, arbitrary-real, varying-W or higher-quotient-worth upper theorem.', 'Matching value is not claimed for every fixed small quotient.', 'Projection identity extends above quotient worth1, but the payment upper does not.'],
 ['lower/branching_pilot/FULL_FIBER_PROJECTION_BARRIER.txt'],
 ['reviews/FULL_FIBER_ROOT_DISPOSITION.txt','reviews/full_fiber_audit/FULL_FIBER_INDEPENDENT_AUDIT.txt'],
 'Accepted scoped native/root audit. Independent check plus hardened copy replay passed. Original checker omitted explicit qx/qprice sign assertions and had coarse s metadata; all saved oracle entries verified nonnegative. Original source/output sealed.',
 'Whole-fiber cloning scales coalition cost with production; its restricted upper does not control partial-fiber reports.')

add('R9','2_restricted_sharpness_and_barriers','Activation and row-compression route barriers',
 'For a nonempty vertex-transitive private production hypergraph of rank<=k, a restoring hitting set has size c>=g/k. Under the stated fixed-cap zero-to-productive one-orbit ladder, this bounds its multiplier exponent by(k-1)/k. In a fixed-cap binary projective single-activation ladder with a bounded seed and active-private transitivity, initially dormant highs are linearly independent, forcing exponential rows.',
 'Specified certificate architectures, including dormant zero production, one private payment orbit and actual restoring-member counts. Sequential compression also assumes displayed star support and linear projective stabilizers.',
 ['Not an upper mechanism or universal lower-certificate ceiling.', 'Batch activation, multiple orbits, changing caps, higher-worth and nonbinary profiles remain possible.', 'No universal impossibility of polynomial-row lower bounds.'],
 ['lower/HOMOGENEOUS_ACTIVATION_BARRIER.txt','lower/LINEAR_SEQUENTIAL_COMPRESSION_BARRIER.txt','lower/STATE.txt'],
 ['reviews/GENERAL_ARITY_ROOT_AUDIT.txt'],
 'Activation lemma root/opposite reviewed with scope repairs. Sequential-compression proof has native-lane derivation and exact supporting scouts; no separate final opposite disposition found in inspected records.',
 'These close particular amplification/compression routes, not the remaining unrestricted gap.')

add('R10','2_restricted_sharpness_and_barriers','Positive affine arity reductions and baseline obstruction',
 'The stage/bridge construction yields arity<=3 G(c,M)=B(M)+F_M(c), preserving shared original rows and actual owners. Its two owner-local maps give G(Tb_C)=B(b_C)+F(b_C). Subtracting owner baseline transfers full OUT for the positive-linear map; the constant map transfers TCWM. Ordinary kappa funding yields only(kappa-1)B+kappa F. A single min_r admits an arity(r-1) gadget with B=sum c_i/[r(r-2)], attaining seed baseline1/(r-2).',
 'Exact value/coalition identities on the map image; fixed finite positive packing, original owner roster. The seed optimality is within coalition-affine embeddings. Projective witness baselines of the displayed general gadgets grow exponentially.',
 ['Not a bounded multiplicative or gain-only reduction; no improved arity3 bound follows.', 'TCWM alone does not support baseline subtraction for the linear map.', 'The suggested shared-resource extension of the optimal single-min gadget is FALSE: recorded F=0 but G-B=1.', 'Incentive-pullback counterexamples in the audit are not uniformly funded gadget mechanisms.'],
 ['constructive/arity_reduction/GENERAL_POSITIVE_TERNARY_AFFINE_GADGET.txt','constructive/arity_reduction/OPTIMAL_SINGLE_MINIMUM_BASELINE_GADGET.txt','constructive/arity_reduction/PROJECTIVE_CERTIFICATE_BASELINE.txt'],
 ['reviews/AFFINE_ARITY_ROOT_DISPOSITION.txt','lower/arity_reduction_audit/AUDIT.txt'],
 'Root/native/opposite review accepted scoped identities and obstructions. Later projective-baseline calculation had separate native audit, not the earlier opposite packet. Invalid shared-resource extension remains rejected.',
 'Exact affine value reductions survive; their additive baseline prevents the desired funding transfer.')

add('R11','2_restricted_sharpness_and_barriers','Constructive and price-charge stopping boundary',
 'No subquadratic general upper survived. The all-real mixed-owner capped-graph rule has coverage and size-s TCWM with factor<=1+2s^2 and an exact family asymptotic to2s^2/e. The verified local price-defect bound defect<=zeta_high(C), with sum zeta<=(r-1)F, does not control the global dual; fixed repairs u+beta*zeta fail singleton TCWM for every beta>=0.',
 'The capped-graph result is for F(P,c)=min(P,G(c)) with graph packing G, not arbitrary arity3. Price-charge statements concern the specified optimal-primal/dual decomposition and actual coalition coordinates.',
 ['No capped-graph full-OUT assertion.', 'No O(s) or o(s^2) estimate from summing local charges; outgoing low-profile terms remain.', 'Changed-owner-only charging is false; passive coalition members matter.', 'The balanced counterexample\'s ratio is below1 and supplies no new lower bound.'],
 ['constructive/STATE.txt','constructive/CAPPED_GRAPH_MARGINAL_NEAR_MISS.txt','constructive/CAPPED_GRAPH_REMAINING_COMPENSATION_GAP.txt','reviews/regularity_and_dual_frontier/PRICE_CHARGE_FRONTIER.txt'],
 ['reviews/REGULARIZATION_AND_PRICE_ROOT_DISPOSITION.txt'],
 'Constructive lane sealed with analytic near-miss and author exact checks; no standalone opposite acceptance of that rule found. Price-charge obstructions have root/opposite review and root exact replay.',
 'Retain explicit failed obligations, but do not promote the quadratic near-miss or local charge into a general upper result.')

add('T1','3_certificate_and_regularity_tools','Finite/all-profile feasibility dual',
 'For a fixed finite profile set, nonnegative coverage multipliers lambda, comparison multipliers mu shared by every member of the protected coalition, and budget multipliers nu obey owner/profile balance g=coverage+incoming-outgoing<=nu. Feasibility at K is equivalent to L<=KD for every such dual, where L=sum lambda F(b_C)+sum mu OUT(delta) and D=sum nu F(B). For one fixed institution the all-real optimum equals the supremum of finite-profile optima and is attained, with K<=n.',
 'Actual multirow owner payments; TCWM uses zero comparison RHS and full OUT uses F(delta). Tychonoff compactness uses bounded payment coordinates, no regularity requirement. A common optimal price can make any one specified budget profile efficient.',
 ['Routine LP/Farkas and compactness do not themselves meet the research gate.', 'Not an independent per-owner scalar flow representation.', 'Pooling capacities does not bound the sum of separate budget-profile values.', 'The finite-price-cover ell-factor rule does not bound ell by s.'],
 ['reviews/cross_profile_duality/FINITE_AND_ALL_PROFILE_DUAL.txt','reviews/cross_profile_duality/ATTACK_AND_GATE.txt'],
 ['reviews/CROSS_PROFILE_DUALITY_ROOT_AUDIT.txt'],
 'Root independently rederived signs, compactness and common-price pruning, and executed exact checks. Classical methodology accepted; no new general funding estimate.',
 'Correct classical dual and compactness reduction; preserve shared coalition multipliers and original payment coordinates.')

add('T2','3_certificate_and_regularity_tools','Dual normal forms and endpoint incidence cone',
 'With every legal comparison among a chosen finite profile set available, each protected coalition can have a source-sink forest of at most|Q|-1 comparison edges, preserving balances and not decreasing OUT objective. For endpoints changing D, d=|D|<=s, the exact compressed comparison cone is M>=0, w_i=M for i in D, 0<=w_i<=M otherwise, sum_{i outside D}w_i<=(s-d)M. It gives O(n|Q|^2) comparison variables. Zero-production profiles can be pruned.',
 'Finite profile sets, fixed actual coalition labels and owners. Shortcuts retain the SAME coalition. Endpoint OUT value depends on changed bundles, not which passive members join.',
 ['No unlabeled/cross-coalition cycle cancellation: the exact pair/min3 5/4 example has12 independent actual comparison columns despite an unlabeled cycle.', 'No polynomial all-coalition coverage or all-profile algorithm.', 'Individual zero reporters at positive-production profiles cannot be pruned.', 'No subquadratic ratio bound.'],
 ['reviews/cardinality_rigidity_audit/DUAL_CYCLE_LEMMAS.txt'],
 ['reviews/CARDINALITY_AND_DUAL_NORMAL_FORM_ROOT_DISPOSITION.txt'],
 'Root accepted; opposite review checked specified normal-form sections, not the exact rank example and not code. Rank example has separate exact native/root evidence.',
 'Useful finite certificate compression keeps coalition coupling; erasing labels is invalid.')

add('T3','3_certificate_and_regularity_tools','Arbitrary-rule regularization',
 'For one fixed finite owner institution, unrestricted, Borel and facewise-C-infinity funding infima coincide. For every arbitrary finite-K rule and alpha in(0,1), one positive translation-invariant integration functional gives alpha^(-1)I[phi(t)y(T(t)b)] with exact coverage/TCWM or OUT and funding K/alpha.',
 'Finite boxes, monotone positively1-homogeneous packing F; one fixed functional/kernel for every owner/profile and same multiplier array at comparison endpoints. Uses choice/Hahn-Banach/compactness, not countable additivity.',
 ['No exact-factor smooth attainment, cross-zero-face continuity, computational construction or funding improvement.', 'Smoothing may leave restricted mechanism architectures.', 'Fixed finite convex mixtures preserve inequalities but need not smooth; fresh profilewise randomization is different.'],
 ['root/MULTIPLICATIVE_REGULARIZATION_TOOL.txt','reviews/regularity_and_dual_frontier/BANACH_REGULARIZATION_CANDIDATE.txt'],
 ['reviews/REGULARIZATION_AND_PRICE_ROOT_DISPOSITION.txt','reviews/regularity_and_dual_frontier/REGULARIZATION_AND_DYADIC_AUDIT.txt'],
 'Root/native/opposite reviews accepted after explicit monotonicity/homogeneity and alpha^-1 rescaling clarification. Classical invariant-extension primary source recorded. Older handoff still labels this pending.',
 'Measurability ceases to separate unrestricted infimal funding, but exact attainment and architecture preservation remain separate.')

add('T4','3_certificate_and_regularity_tools','Dyadic-grid completeness',
 'For one fixed finite institution, K_allreal=sup_m K_m=lim_m K_m for nested dyadic report grids; both each finite optimum and the all-real optimum are attained. With rational technology AND rational finite endowments, strict rational lower-factor refutation is an exact semidecision.',
 'Nonnegative payments, every coalition covered and all legal actual-owner TCWM/full-OUT comparisons. One common ultrafilter handles every profile/owner; rounding preserves outsiders and restoration order.',
 ['No finite grid need attain the supremum.', 'No finite upper-verification procedure, convergence rate or polynomial complexity.', 'No measurable or computable mechanism supplied by the ultralimit.'],
 ['root/DYADIC_GRID_COMPLETENESS.txt'],
 ['reviews/REGULARIZATION_AND_PRICE_ROOT_DISPOSITION.txt','reviews/regularity_and_dual_frontier/REGULARIZATION_AND_DYADIC_AUDIT.txt'],
 'Root/native/opposite reviews accepted with rational-endowment and attainment clarifications.',
 'Complete strict-lower refutation search for a fixed rational institution, not finite certification of an unrestricted upper.')

add('T5','3_certificate_and_regularity_tools','Homogenization and local-rule limitation',
 'For fixed owners, technology and zero/nonzero eligibility pattern, positive finite endowment magnitudes have the same optimum. A negative-infinity translation-invariant mean replaces any finite-K box rule by an exact-K homogeneous rule on the eligible orthant. Homogeneous facewise-smooth rules have the same infimum. Static coverage/budget plus Euler and local incentive jets pass at K1 via frozen optimal prices; at every productive point and every kappa>1 there is a genuine smooth linear local admissible rule on a sufficiently small neighborhood.',
 'The arbitrary-rule TCWM/full-OUT contract, one mean across every profile and owner. Orthant smoothing uses local bounds on compact log-kernel supports; contractions commute with common dilation. Zero eligibility remains zero.',
 ['Homogeneous replacement need not agree with the input rule on its original box.', 'No exact smooth attainment, global gluing, cross-face continuity or general funding improvement.', 'At exact K1, tangent budget tests can reject a C1 jet at min(A,B)\'s kink; static jets omit those tests.', 'Local neighborhoods need not be downward report boxes.'],
 ['root/HOMOGENIZATION_AND_LOCAL_JET_LIMIT.txt'],
 ['reviews/homogenization_audit/HOMOGENIZATION_INDEPENDENT_AUDIT.txt'],
 'Independent native audit scoped PASS after source incorporated kink and local-germ qualifications. Root integration/opposite-model final disposition was not found at this ledger snapshot; do not infer it from the regularization review of the predecessor.',
 'Exact homogeneous existence reduction and a precise limit of independent local tests; latest audit is native PASS, not yet a recorded final opposite disposition.')

add('T6','3_certificate_and_regularity_tools','Local incentive separation with admission',
 'At a supplied Jacobian, TCWM is exactly the restoring-owner derivative plus up to s-1 most negative other owner derivatives>=0 for each eligible coordinate. Full OUT additionally has finite activity-input-to-owner assignment tests. For fixed arity, these tests are polynomial in the explicit Jacobian/technology size. For facewise-smooth rules, those derivative tests plus directed zero-face admission are equivalent to all finite comparisons.',
 'Actual owners, including passive/zero-report members, remain in each sort. Assignment tests are a separation device, not owner splitting. Smooth extension/limits handle endowment upper boundaries.',
 ['No integrability construction, all-coalition coverage oracle or all-profile polynomial algorithm.', 'Within-face derivatives alone do not imply zero-face admission.', 'No general funding bound.'],
 ['root/LOCAL_INCENTIVE_SEPARATION.txt'],
 ['reviews/local_incentive_audit/AUDIT.txt'],
 'Independent native audit PASS with exact local/endpoint checks; root source proof checked. No separate final opposite disposition for this complete local theorem found in inspected records.',
 'An exact local oracle for a supplied integrable rule, with seam admission still required.')

add('T7','3_certificate_and_regularity_tools','Fixed-partition continuous piecewise-affine certificates',
 'On a supplied verified finite rational polyhedral cover of a fixed rational report box, continuity, nonnegativity, all-coalition coverage, funding and TCWM/full OUT of continuous piecewise-affine payments have necessary and sufficient finite rational conditions. Coverage uses cellwise LP duals; funding uses cell vertices by concavity; local Jacobian conditions integrate by continuity. Best funding within that fixed partition class is an attained finite LP optimum when feasible.',
 'Fixed actual multirow owners and all real reports inside the box. Full-dimensional cell cover and overlap agreement must themselves be verified. Exponential all-coalition coverage can remain.',
 ['Not completeness or approximation for arbitrary mechanisms.', 'No guarantee a supplied partition is sufficiently fine.', 'No polynomial overall algorithm or improved general funding bound.', 'Coverage cannot be checked only at vertices; the saved triangle example fails in its interior.'],
 ['constructive/polyhedral_certification/POLYHEDRAL_CERTIFICATE_THEOREM.txt','constructive/polyhedral_certification/STATE.txt'],
 ['reviews/local_incentive_audit/AUDIT.txt'],
 'Author theorem/checker packet complete and frozen; its own independent review explicitly pending at snapshot. Cited local audit validates a dependency, not this entire new theorem.',
 'Pending-review finite certificate language within a continuous fixed-partition class; keep out of the accepted unrestricted results.')

add('T8','3_certificate_and_regularity_tools','Explicit original-variable projective certificate lift',
 'General-k positive tail weights cancel seed/transition/terminal payment variables exactly after adding explicit restorer and omitted-payment nonnegativity rows. At M2,k2,s2, GL(3,2)168 times S5 of size120 yields20,160 actions,34,440 distinct weighted legal rows over5,880 profiles; every payment coefficient cancels and the result is K>=4/3.',
 'Original fixed-owner/profile payment coordinates, duplicate group rows retained with legitimate multiplicities. The seed/terminal branch uses all-coalition coverage even when its size exceeds protected s. No dummy-zero assumption.',
 ['Reproducibility for the accepted theorem, not a new bound.', 'Finite replay is not formal verification of all general-k geometry.', 'Budget support is an orbit, not one prescribed asymmetric profile.'],
 ['reviews/projective_dual_lift/EXPLICIT_CERTIFICATE_AND_LIFT.txt'],
 ['reviews/PROJECTIVE_ROOT_ACCEPTANCE.txt'],
 'Independent builder and separate serialized-row verifier executed with exact arithmetic; projective parent accepted. General-k scalar cancellation checked2,520 parameter triples, distinct from geometric proof.',
 'Concrete finite certificate evidence for the same main theorem; do not count it as another research contribution.')

add('A1','4_application_feasibility','Conditional institution and sealed metadata gate',
 'Application status is INSTITUTION-UNVERIFIED. Summit payload access stops at authentication: dataset bytes0, actual timezone/schema/coverage unresolved. M100 May metadata permits a selective May12 schema/alignment candidate at92,759,641 cumulative bytes, but no data pages were fetched. Actual sealed intake:468,255 dataset bytes in334 range requests; power/state pages0. May state envelope20.38 days cannot support two14-day windows.',
 'Three independently controlled interests at one delivery point require documented firm entitlements, binding owned partial withdrawals, feasible joint outside operation, fixed operator access, dispatch/liability and actual sponsor commitment. None is established. Summit Jan1-14/Jan15-28 remains unfrozen; April is inspected calibration. Any later May payload plan must classify all May as training before outcomes.',
 ['Public node partitions do not establish economic owners/rights.', 'Footer timestamps do not prove a matched simultaneous panel.', 'No reliability, pooling, AI workload, sponsor-value or net-benefit finding.', 'M100 is not a silent Summit replacement; no holdout is frozen and no further acquisition is authorized by this ledger.'],
 ['application/FINAL_FEASIBILITY_GATE.txt','application/THREE_INTEREST_CONTRACT.txt','application/NEXT_PREREGISTRATION_DECISION.txt','application/MISSING_EVIDENCE.json'],
 ['reviews/CALIBRATION_REVIEW_DISPOSITION.txt'],
 'Bounded gate closed and byte/source records sealed. Root checked the algebraic application witness; economic/data feasibility remains unresolved, which is an allowed terminal outcome. The ledger does not rerun intake.',
 'Precise conditional contract and bounded metadata evidence only; no empirical application or real sponsor/owner validation.')

add('A2','4_application_feasibility','Illustrative reserve witness and finite uniform 5/4 corollary',
 'A three-owner non-veto cone example has efficient coalition-covering subgradient payments at both profiles but owner1 payment falls from1 to3/2-25/(2sqrt545)<1 upon a cone-feasible owned restoration. Separately, three fixed owners each owning L=(1/2,1/2),R=(1/2,-1/2) on their64 subset profiles force uniform K>=5/4 for pair TCWM, hence OUT, by the existing min2 lower.',
 'Stipulated Gaussian-cone algebra F(t,x)=t-||x|| and one-factor F=t-|x| respectively; actual economic rights would need separate evidence. The 5/4 claim covers every rule on that fixed finite domain, without anonymity or dummy-zero assumptions.',
 ['The first example alone proves no subsidy necessity or optimal individual-versus-coalition separation.', 'The 5/4 result is a worst-profile total-funding lower, not a deficit at full reports, an observed-facility estimate or gain-only premium.', 'Neither result supplies real owners, outside rights, sponsor benefit or empirical Gaussian validity.', 'The 5/4 theorem is a routine prior-result corollary, not a new lower exponent.'],
 ['application/THREE_OWNER_ALGEBRAIC_WITNESS.txt','root/THREE_PORTFOLIO_UNIFORM_SUBSIDY_COROLLARY.txt'],
 ['reviews/CALIBRATION_REVIEW_DISPOSITION.txt','reviews/three_portfolio_corollary_audit.txt','reviews/SCOPED_RESULTS_REVIEW_DISPOSITION.txt'],
 'Root/native/opposite audits accepted the exact algebra with corrected coverage wording. Independent36-row rational certificate replayed by root. Three-portfolio source closing pending-opposite line is stale.',
 'Keep the allocation failure distinct from the finite uniform subsidy lower, and both distinct from empirical necessity.')

add('P1','5_unresolved_priority','Bounded original-source comparison; priority open',
 'No inspected original theorem was found to subsume the precise all-profile arbitrary-payment sparse-packing rate K_r(s)=Omega_r(s^((r-2)/(r-1))). The strong coalition-sum monotonicity principle, static subsidy questions, projective constructions, additive flow methods and coordinated withdrawal concepts have established antecedents.',
 'Only the originals and exact assumptions recorded in the fifteen-entry source map and later follow-ups were checked. Closest quantitative profit-sharing results impose incumbent-by-incumbent monotonicity, which the saved all-real min2 full-OUT example separates from TCWM. Additivity/flow results have different universal-function, balance and domain requirements.',
 ['Absence of a subsuming inspected theorem is not novelty clearance or exhaustive search.', 'Do not dismiss all related literature as scalar: Sprumont2005 explicitly advertises a published bundle extension whose exact text remains unverified.', 'No field-level breakthrough, specialist endorsement or publication-ready priority claim.', 'Nearby data-center co-investment and AI withdrawal sources provide context, not application evidence.'],
 ['reviews/priority_projective/PRIORITY_AUDIT.txt','reviews/priority_projective/SOURCE_THEOREM_MAP.txt','reviews/priority_projective/FIXED_LINEAR_PRIORITY_ADDENDUM.txt','sources/MOULIN_SPRUMONT_PRIMARY_CHECK.txt','sources/PROJECTIVE_STATIC_STABILITY_COMPARISON.txt','sources/SPRumont_PUBLISHED_ACCESS_FOLLOWUP.txt','sources/AI_ENERGY_COINVESTMENT_COMPARISON.txt'],
 ['reviews/PRIORITY_DELEGATION_DISPOSITION.txt'],
 'Bounded primary-source audit complete; priority unresolved. Earlier delegated flow/source comparison was rejected as delivered, with verified components retained and central original rechecked by root. No new source search performed for this ledger.',
 'Use narrow assumption-by-assumption related work; exact published bundle theorem and later citation chaining remain unresolved.')

conflicts = [
 dict(id='C1',kind='historical_baseline',paths=['CAMPAIGN_CONTRACT.txt','root/PROGRESS_LOG.txt','reviews/PROJECTIVE_ROOT_ACCEPTANCE.txt'],finding='Frozen contract and early progress entry retain the opening Omega(s^(1/4)) interval/no-improvement state; later accepted main interval is Omega(sqrt(s)) through3s^2.',disposition='Treat first two as historical snapshots, not current mathematical status.'),
 dict(id='C2',kind='stale_pending_status',paths=['root/GENERAL_ARITY_TAIL_AND_DIMENSION_COROLLARY.txt','lower/GENERAL_ARITY_TAIL_REVIEW.txt','reviews/GENERAL_ARITY_ROOT_AUDIT.txt'],finding='Combined tail source says its final independent check is pending; independent PASS and later root acknowledgement already exist.',disposition='Use accepted native/root scope; do not credit a broader opposite snapshot than actually recorded.'),
 dict(id='C3',kind='stale_pending_status',paths=['lower/branching_pilot/UNIT_WORTH_LINEAR_DOMAIN_THEOREM.txt','reviews/UNIT_WORTH_IDEAL_ROOT_DISPOSITION.txt'],finding='Source header and closing line still say pending independent review despite root/opposite acceptance disposition.',disposition='Preserve source; ledger reports accepted restricted-domain theorem.'),
 dict(id='C4',kind='stale_status_and_scope',paths=['lower/branching_pilot/FULL_FIBER_PROJECTION_BARRIER.txt','reviews/FULL_FIBER_ROOT_DISPOSITION.txt','reviews/full_fiber_audit/FULL_FIBER_INDEPENDENT_AUDIT.txt'],finding='Sealed source says matching lower/audit pending and writes bare O(sqrt(s/R)); later disposition accepts worst-case matching over growing quotients and gives factor1 for s<R, B(s/R) otherwise.',disposition='Use O(sqrt(max(1,s/R))) uniformly and do not assert matching for every fixed small quotient. Preserve sealed original.'),
 dict(id='C5',kind='stale_pending_status',paths=['root/MINIMUM_NORM_COVER_OBSTRUCTION.txt','root/AGGREGATE_COMMON_PRICE_OBSTRUCTION.txt','constructive/FIXED_LINEAR_WORTH_RULE_QUADRATIC_BARRIER.txt','root/THREE_PORTFOLIO_UNIFORM_SUBSIDY_COROLLARY.txt','reviews/SCOPED_RESULTS_REVIEW_DISPOSITION.txt','reviews/AGGREGATE_PRICE_ROOT_DISPOSITION.txt','reviews/FIXED_LINEAR_ROOT_DISPOSITION.txt'],finding='Opening/closing pending lines remain in these sources although later completed reviews accept the scoped results.',disposition='Later explicit dispositions govern current status; original snapshots remain provenance.'),
 dict(id='C6',kind='stale_pending_status',paths=['reviews/ADAPTIVE_GLOBAL_MIXTURE_ROOT_DISPOSITION.txt','reviews/CARDINALITY_AND_DUAL_NORMAL_FORM_ROOT_DISPOSITION.txt','reviews/regularity_and_dual_frontier/FINAL_GATE.txt','reviews/REGULARIZATION_AND_PRICE_ROOT_DISPOSITION.txt'],finding='Older disposition still calls cardinality pending; older regularity handoff calls arbitrary-rule smoothing a candidate awaiting opposite review. Later dispositions resolve both.',disposition='Do not propagate old pending language or erase review-packet limitations.'),
 dict(id='C7',kind='historical_priority_snapshot',paths=['reviews/priority_projective/PRIORITY_AUDIT.txt','lower/GENERAL_ARITY_CIRCUIT_LOWER.txt','reviews/GENERAL_ARITY_ROOT_AUDIT.txt'],finding='Priority audit describes general-arity mathematical review as pending at its input snapshot; mathematical acceptance later completed.',disposition='Update mathematical status in handoff while retaining unresolved historical priority.'),
 dict(id='C8',kind='pending_new_packets',paths=['root/HOMOGENIZATION_AND_LOCAL_JET_LIMIT.txt','reviews/homogenization_audit/HOMOGENIZATION_INDEPENDENT_AUDIT.txt','constructive/polyhedral_certification/STATE.txt'],finding='Homogenization has native PASS but no later root/opposite disposition found; fixed-partition polyhedral theorem is author-complete with its own independent audit pending.',disposition='Do not inherit acceptance of dependencies as acceptance of these whole packets; root should refresh status at final seal.'),
 dict(id='C9',kind='resolved_scope_not_formula_conflict',paths=['root/PROJECTIVE_BOUNDED_COALITION_TAIL.txt','lower/branching_pilot/UNIT_WORTH_LINEAR_DOMAIN_THEOREM.txt','root/PROJECTIVE_PURE_OWNER_REALIZATION.txt','root/MIN_HUBER_CALIBRATION.txt'],finding='h=floor((s+1)/2) and h=ceil(s/2) agree for integer s. B_s is a general lower and also a restricted binary-ideal exact optimum. Pure-owner and fully eligible counts differ. Single-min3 factor2 TCWM does not contradict general arity3 s6 lower493/243.',disposition='No numerical disagreement found among these formulas; retain the distinct domains and counts.'),
 dict(id='C10',kind='checker_hardening_only',paths=['lower/branching_pilot/FULL_FIBER_PROJECTION_BARRIER.txt','reviews/full_fiber_audit/FULL_FIBER_INDEPENDENT_AUDIT.txt','reviews/full_fiber_audit/REPLAY_COMMANDS.txt'],finding='Original full-fiber checker omitted explicit primal/dual sign guards and used coarse protected-size metadata. Hardened owned copy verifies signs and accurate per-R ranges; all saved witnesses remain valid.',disposition='No mathematical invalidation; reference hardened replay without editing sealed original.'),
]

groups = [
 ('1_main_unrestricted_lower','1. ONE MAIN UNRESTRICTED LOWER CONTRIBUTION AND ITS COROLLARIES'),
 ('2_restricted_sharpness_and_barriers','2. RESTRICTED SHARPNESS AND ARCHITECTURE / ROUTE BARRIERS'),
 ('3_certificate_and_regularity_tools','3. GENERAL CERTIFICATE / REGULARITY TOOLS'),
 ('4_application_feasibility','4. APPLICATION FEASIBILITY EVIDENCE'),
 ('5_unresolved_priority','5. UNRESOLVED PRIORITY'),
]

def main():
    stamp = datetime.now(timezone.utc).isoformat()
    all_refs = sorted({p for e in entries for p in e['source_paths']+e['review_paths']}
                      | {p for c in conflicts for p in c['paths']})
    missing = [p for p in all_refs if not (CAMP/p).is_file()]
    if missing:
        raise RuntimeError(f'Missing cited artifacts: {missing}')
    packet = dict(schema_version=1, created_utc=stamp, campaign_root=str(CAMP),
        purpose='Consolidation snapshot; no new proof, source search or external priority claim.',
        contribution_counting='One main unrestricted projective lower-bound contribution; corollaries, barriers, tools, applications and certificate engineering are not counted as separate papers.',
        current_frontier='Omega(sqrt(s)) <= K3(s) <= K3_OUT(s) <= 3s^2',
        contract=dict(owners='Fixed actual multirow owners and eligibility within each institution.',
            reports='All nonnegative real binding underreports in fixed finite boxes unless an entry explicitly restricts the domain.',
            coverage='Every coalition, at every feasible report; coverage coalition size is not capped by s.',
            incentives='TCWM or full OUT for all protected actual coalitions of size<=s, including unchanged members.',
            payments='Nonnegative; no dummy-zero axiom; total funding is relative to F(total report).'),
        verification_scope='Read theorem statements and current dispositions; source-status reconciliation only. This consolidation did not rerun mathematical checkers. Previously executed checks are attributed to their recorded reviewers/authors. Frozen hashes identify the inspected snapshot.',
        groups=[dict(id=g,title=t) for g,t in groups],entries=entries,
        conflicts_and_scope_alerts=conflicts,
        open_frontier=['No subquadratic unrestricted upper.', 'No exponent above1/2 for arity3.', 'No polynomial-row square-root construction from the recorded routes.', 'No real reserve institution/sponsor or frozen holdout.', 'Historical priority and exact published bundle-extension comparison remain unresolved.'])
    (OUT/'CLAIM_LEDGER.json').write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n')
    lines=['CAMPAIGN CLAIM LEDGER — CONSOLIDATION SNAPSHOT',stamp,
      'One main unrestricted contribution; no separate-paper count for its corollaries, barriers or tools.',
      'Current frontier: Omega(sqrt(s)) <= K3(s) <= K3_OUT(s) <= 3s^2.',
      'All paths below are relative to CAMP. JSON carries exact quantifiers, exclusions and audit limitations.',
      'This ledger reads existing evidence; it does not rerun checks or perform a priority search.','']
    for group,title in groups:
        lines += [title]
        for e in entries:
            if e['group'] != group:
                continue
            lines += [f"{e['id']} — {e['title']}",e['handoff_summary'],
                'Claim: '+e['exact_claim'],
                'Limit: '+e['does_not_establish'][0],
                'Source: '+'; '.join(e['source_paths']),
                'Review: '+'; '.join(e['review_paths']),
                'Status: '+e['audit_status'],'']
    lines += ['CONFLICT / STATUS ALERTS (SOURCES NOT MODIFIED)']
    for c in conflicts:
        lines += [c['id']+' — '+c['finding'],c['disposition'],'Paths: '+'; '.join(c['paths']),'']
    lines += ['HANDOFF GUARDS',
      '- The binary unit-worth and complete-fiber matching uppers are restricted-domain theorems, not all-real mechanisms.',
      '- A finite exact certificate supports its proof; numerical or finite replay is not proof of an unbounded theorem.',
      '- Native/opposite review and code execution are distinct evidence. Do not attribute execution to reviewers who only read.',
      '- Main lower is accepted internally; priority remains open. The application remains institution-unverified.',
      '- Refresh new-packet status and source hashes at final root seal.']
    (OUT/'CLAIM_LEDGER.txt').write_text('\n'.join(lines)+'\n')
    def digest(p):
        data=p.read_bytes()
        return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    manifest=dict(created_utc=stamp,ownership='reviews/consolidation_ledger/ only',
        sources=[digest(CAMP/p) for p in all_refs],
        outputs=[digest(OUT/p) for p in ['build_ledger.py','CLAIM_LEDGER.json','CLAIM_LEDGER.txt']],
        validation=dict(entry_count=len(entries),group_count=len(groups),alert_count=len(conflicts),
            cited_paths_exist=True,source_files_modified=False,mathematical_checkers_rerun=False,
            new_external_search=False))
    (OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'entries':len(entries),'groups':len(groups),'alerts':len(conflicts),
        'cited_files':len(all_refs),'created_utc':stamp,'outputs':[str(OUT/p) for p in ['CLAIM_LEDGER.json','CLAIM_LEDGER.txt','MANIFEST.json']]}))

if __name__ == '__main__':
    main()
