from pathlib import Path
import shutil
r=Path('/private/tmp/coopgpt-ownership-20261016');a=r/'audits';s=Path('/Users/maxf/.local/state/claude-reviews/coopgpt-ownership-20261016-0ad718e4be4a')
for name,run in {'ENTROPY_WEIGHT_FOUR_FABLE':'20261016-201647-75bc3d81','GENERAL_323_200_AND_PARAMETRIC_FABLE':'20261016-202317-281d944e','SHARED_LOWER_AND_SIGNED_LOSS_FABLE':'20261016-202332-4306e46c'}.items():
 for f in ['review.md','request.json','status.json','execution.json']:shutil.copy2(s/run/f,a/(name+'_'+f))
notes={34:'''ROOT ADJUDICATION34 -- SUBSET ENTROPY AND PARAMETRIC SPILL
17 October2026. Accepted internally, original exponential primitive only.

Accept SUBSET_ENTROPY_DEFICIT_COUPLING and ENTROPY_DEFICIT_WEIGHT_FOUR after
root analytic rederivation, exact scalar replay, and Fable201647. The negative
set is strictly d_i<a_i; zero-gap owners are excluded. Perspective sharpness
is restricted to r in[c,1/2], with no assertion of attainment below c. The
proof now makes both restrictions explicit. Mechanism identities follow from
the established primitive definition; the exact clipping loss is h-rho*T.

Accept PARAMETRIC_ENTROPY_DEFICIT_SPILL and NEGATIVE_GAP_CONCENTRATION_CHORD
after root rederivation and Fable202317. The former proves all real eta>=2,
not just the sampled supporting rows. Root checked the two scalar regimes,
AM-GM, optimized eta boundary and directed finite constants. The latter uses
concavity of L on[0,3/4] and the chord slope4/15; the aggregate v^2 Zminus
is an upper moment relaxation, not an attainability assertion. These two
lemmas are NOT dependencies of the323/200 theorem. Fable executed no code.
No historical novelty or optimal general funding constant is claimed.
''',35:'''ROOT ADJUDICATION35 -- GENERAL323/200 ORIGINAL ENVELOPE FUNDING
17 October2026. Accepted internally after independent proof and exact replay.

Accept root/entropy_general_certificate/GENERAL_323_200_ENTROPY_CERTIFICATE.txt:
 sum_i E_i <=323F/200 for fixed actual owners, all nonnegative real reports,
 arbitrary mixed ownership and unbounded finite owner/branch counts.
This strengthens13/8 for the same all-profile truthful coalition-covering
actual own-report envelope. It does not replace the mechanism or its domain.

Root read the proof and standalone verifier, independently replayed all32,768
continuous rectangles with Fraction arithmetic under-I-O, and confirmed
30,896 valid duals plus1,872 geometric exclusions. Maximum rational low-grid
bound displays1.6141096740946201; external high-grid bound1.5990301209303297;
power bound1.4017137520598988. Explicit output target is323/200.
Certificate SHA256 bf348e6090f778bb4fb018f3eb92bce5508b6f25aa65ecd77e2ce38168969ab2.
Verifier SHA256 448d4ffe43f8f34f1445661d520c3c5550a859b0a706549b181d7dc9e7dd16f4.
Sparse independently audited all interval signs and replayed the same hashes.

Fable202317 found no invalid row or logic error but correctly declined whole-
theorem certification without the5MB artifact and all earlier source lemmas.
Root resolves those omissions with the actual replay and accepted dependency
chain: POSITIVE_GAP_DUAL_AGGREGATION explicitly proves PD1/PD2 for EVERY fixed
u on the SAME actual sum Y; effective overflow was separately accepted and
rechecked. JOINT_ROLE_TRADEOFF and SUBSET_HARDWARE_DEFICIT_COUPLING imply all
role/Young rows; the13/8 predecessor's exhaustive physical/outer regimes and
negative theorem remain unchanged. Entropy/eta4 inputs are adjudication34.
Y>=0 follows from E_i>=N_i=a_i+q0(d_i-a_i)>a_i on the strict positive set.
The verifier accepts several possible target values by design; this frozen
artifact and replay explicitly use323/200, so no weaker-target PASS is used.

This is a computer-assisted rational weak-duality proof over a continuous
moment relaxation, not a finite report grid or optimizer-status argument.
No efficient exact evaluator, optimality, C^2 bound, external specialist review,
or historical-priority clearance follows. Fable inspected but ran no code.
''',36:'''ROOT ADJUDICATION36 -- SHARED RESPONSE LOWER AND SIGNED3/2 LOSS
17 October2026. Accepted internally; sharper signed/lower candidates separate.

Accept SHARED_RESPONSE_BRANCH_DIFFUSE_LOWER after root analytic checking,
110-digit direct primitive replay under-I-O, and Fable202332. The same actual
G owns both response coordinates and has total local payment exactly epsilon.
A and G deviations are separate; G's cap hides A-induced local gains. The
family has both active owner and productive branch counts growing and yields
residual liminf at least c[Fresp-2e-Klog2], approximately-0.785643710331513.
It strengthens the previous independent-pair lower; no exact residual limit
or unrestricted mechanism lower bound is claimed. The accepted core and exact
outer primitive identities were rechecked from the prior source dependencies.
Finite Decimal values corroborate identities only; the asymptotic proof gives
the all-small-real-epsilon result.

Accept SIGNED_OTHER_LOCAL_LOSS_THREE_HALVES after root scalar/cap inspection,
exact Fraction replay, and Fable202332. For local-only bundle underreports,
positive-part of the SIGNED other-local-payment loss is at most1.5*z_i.
Hardware stays fixed; counts and other ownership are arbitrary. The accepted
SHORT_STAGE_NONLINEAR_THREE_HALVES source resolves the omitted short-stage
dependency. This is not a bound on summed positive losses or capped outer
losses: the shared construction's capped loss J*epsilon exceeds1.5*epsilon,
while its signed local loss does not. The proof explicitly preserves that
scope. No mathematical error identified; Fable executed no scripts.
'''}
for n,t in notes.items():(a/f'ROOT_REVIEW_ADJUDICATION_{n}.txt').write_text(t)
print('Copied three review records and wrote adjudications34--36.')
