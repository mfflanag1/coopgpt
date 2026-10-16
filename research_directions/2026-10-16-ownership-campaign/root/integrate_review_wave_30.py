from pathlib import Path
import shutil
r=Path('/private/tmp/coopgpt-ownership-20261016');a=r/'audits';s=Path('/Users/maxf/.local/state/claude-reviews/coopgpt-ownership-20261016-0ad718e4be4a')
for name,run in {'NEGATIVE_CONVEX_REGIONAL_FABLE':'20261016-195942-ae132b26','TWO_CAP_AND_SUBSET_FABLE':'20261016-200006-07ce474b','EFFECTIVE_MASS_AND_INDIVIDUAL_FABLE':'20261016-200648-112b4ea9','GLOBAL_NEGATIVE_CONVEX_FABLE':'20261016-200649-bf8fc4e5'}.items():
 for f in ['review.md','request.json','status.json','execution.json']:shutil.copy2(s/run/f,a/(name+'_'+f))
notes={30:'''ROOT ADJUDICATION30 -- ONE GLOBAL NEGATIVE-GAP CONVEX PROGRAM
17 October2026. Accepted internally with explicit ER/LB hypotheses.

Accept NEGATIVE_GAP_CONVEX_LOCAL_EXTENSION and GLOBAL_NEGATIVE_LOCAL_CONVEXITY.
The physical hardware bottleneck, exact actual hardware/grid restoration (ER),
and opposing local supply (LB) remain required. Under them a negative full-gap
owner's exact envelope is one globally strictly convex minimization over the
branch-price box. No effective-grid or cap-count restriction is needed. Positive
gaps retain at most four concave programs in the stated low-effective-grid regime.

Root independently derived the Hessian, weighted slope estimate and cap-boundary
jump. Pivot independently audited the regional theorem/dependencies. Fable195942
and200649 found no invalidating step. The outer primitive is globally
N_i=a_i+(d_i-a_i)exp(1-S/H)/2 on the hardware-short side, including negative gaps;
this resolves the review's omitted-source concern. ER for both gap signs is
explicitly accepted in adjudication25. The fixed branch C budget is the original
primitive's scalar max, not an additional unsupported premise.
The loss is strictly convex on each cap region; crossing a cap produces an upward
derivative jump. Line restrictions therefore prove global strict convexity. The
explicit subgradient has the reviewed supergradient-to-subgradient sign. Compactness
gives attainment and unique prices; physical reports above caps can be redundant.

Root replayed the90-digit global checker under-I-O: 80 profiles,1200 cross-cap
Jensen checks,8400 subgradient supports,80 simultaneous jumps,7280 actual-payment
identities. These are corroboration, not the proof. Fable executed no code.
No claim of polynomial bit complexity, exact finite-precision implementation,
unrestricted pool-switch optimization, or historical novelty follows.
''',31:'''ROOT ADJUDICATION31 -- TWO-CAP DIFFUSE SEPARATION AND SUBSET DEFICIT
17 October2026. Accepted internally after root and Fable200006.

Accept TWO_CAPPED_ACCOUNTS_DIFFUSE_GAP: among full profiles with at least two
outer accounts at or above the cap, the diffuse actual-envelope supremum is
 C+(cK/2)epsilon log(1/epsilon)+O(epsilon).
The coefficient is matched by an actual fixed-owner family with both counts growing.
Root rederived the quadratic raw-budget penalty, logarithmic optimization and lower.
The lower now explicitly takes L>=6, so rho>=3, no post-deletion switch and positive
Delta. This is a structural profile class, not an optimal-mechanism lower bound.

Accept SUBSET_HARDWARE_DEFICIT_COUPLING for every actual owner subset:
 U_J >=(1-c)a_J-2(H-M)-K sqrt(c M delta),delta=CM-Z.
For the negative-gap set, (1-c)v-cZminus<=2(1-M)+K sqrt(c M delta).
The accompanying continuum role-support rows are valid. Root independently rederived
both branch orientations and Cauchy summation; five exact constant checks replayed.
The coefficient stability dependency was accepted in adjudication15; its stale pending
header does not invalidate it. Fable did not execute scripts. The numerical LP failure
above8/5 is a relaxation diagnostic, not a realizable lower bound.
''',32:'''ROOT ADJUDICATION32 -- EFFECTIVE ENTROPY MASS AND SAME-OWNER PAYMENT COUPLING
17 October2026. Accepted internally; newer net-charge upper has separate review.

Accept EFFECTIVE_HARDWARE_ENTROPY_MASS after root rederivation and Fable200648.
With A the actual hardware-role payment on full hardware-short branches,
Gminus<=1-A and v_branch<=log[(A_branch+2V)/(2V)]. Retention and weighted entropy
therefore imply the global diffuse residual limsup <=c[K-2-Klog2]. This improves
the earlier upper without limiting owner or branch counts. The post-switch bound
now explicitly invokes retention(4), as the reviewer requested. The retention and
one-cap lower dependencies were accepted in adjudication27. This does not determine
the exact residual coefficient or an optimal mechanism.

Accept INDIVIDUAL_PAYMENT_GAP_COUPLING after root branch proof and Fable200648:
 z_i<=(1-c)a_i+C(H-M)+cM+K sqrt(cMdelta).
At H=1 this gives z_i+(1-c)g_i<=2-M+K sqrt(cMdelta) on positive gaps. On the entire
saturation face H=M,Z=CM the actual envelope obeys
 sum E_i <=[1+exp(-1+3C/8)]F <(8/5)F.
The positive exponential comparison and negative4/5 saving hold for arbitrary
actual underreports, with no restoration assumption: they are accepted in the
original positive dual/negative-gap theorem and the general13/8 reduction. The
review's omitted-premise concern is resolved by those checked dependencies.
Root independently ran all11 rational scalar checks under-I-O. No owner-count
multiple of the per-owner error is introduced. The separate profilewise-neighborhood
note is a further corollary and not part of this frozen review packet.
'''}
for n,t in notes.items():(a/f'ROOT_REVIEW_ADJUDICATION_{n}.txt').write_text(t)
(r/'root/FREE_SOURCE_ATTRIBUTE_FOLLOWUP_20261017.txt').write_text('''FREE ORIGINAL-SOURCE FOLLOW-UP,17 OCTOBER2026

Ozen,Slikker,Sosic, On the core of m-attribute games, Production and Operations
Management31(4),1770-1787,2022, DOI10.1111/poms.13643.
Freely accessible original publisher PDF in the university repository:
https://research.tue.nl/files/203986677/Production_Oper_Manag_2021_zen_On_the_core_of_attribute_games.pdf
The inspected model assigns vector endowments to owners and evaluates a continuous
function on coalition totals. Theorem1 characterizes core nonemptiness across
embedded games using homogeneity and supporting prices on relevant faces. These
are static allocation statements. The contribution being investigated here must
therefore be all-profile own-capacity incentives with explicit external funding,
not the general idea of aggregating multidimensional resources or using supporting
prices for core allocations. This scoped comparison is not novelty clearance.

Cao, Cooperative Functions, SSRN3330596, posted2019,revised25March2021:
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3330596
The freely offered58-page preprint was located via the above original's references.
Its public landing page was read, but its PDF did not load reliably through the
available browser/web tools. No technical theorem comparison is claimed from the
abstract. Its relationship to the published2026 Superadditive Market Games must
also be checked, rather than assuming the versions are identical. No purchase,
login bypass or external contact was attempted.
''')
print('Copied four reviews; adjudications30-32 and primary-source note written.')
