from pathlib import Path
import shutil, hashlib, json
r=Path('/private/tmp/coopgpt-ownership-20261016'); a=r/'audits'
s=Path('/Users/maxf/.local/state/claude-reviews/coopgpt-ownership-20261016-0ad718e4be4a')
reviews={'MONOPOLY_AND_ACTUAL_FAMILY_FABLE':'20261016-194003-127b8798','SHARP_LOCAL_ENTROPY_FABLE':'20261016-194408-f3dde325','DIRECTIONAL_AND_HIGH_TOTAL_FABLE':'20261016-195044-421e6301','RETENTION_AND_ONE_CAP_FABLE':'20261016-195213-6f5c5bc5','CONVEX_AND_FOUR_PROGRAM_FABLE':'20261016-195405-0e32165c'}
for name,run in reviews.items():
 for source in ['review.md','request.json','status.json','execution.json']:
  shutil.copy2(s/run/source,a/(name+'_'+source))
notes={26:'''ROOT ADJUDICATION 26 -- SOLE-HARDWARE STRUCTURE AND THE OLD MOMENT FAMILY
17 October2026. Accepted internally; no specialist review or priority claim.

Accept MONOPOLY_HARDWARE_COORDINATE_RESTORATION and
AGGREGATE_OBSTRUCTION_EXACT_ENVELOPE after root analytic reconstruction and
Fable194003. The sole actual hardware owner's hardware and grid restore exactly;
local reports cannot generally be restored. The dominance subclass has E=N and
sharp funding C for this rule. This is a profile-class theorem, not general C^2.
The old PD5 obstructive family's actual envelope is exactly the stated piecewise
formula and is below5/4. Root had separately matched the family to the PD5
moment obstruction; Fable did not inspect that omitted source. Thus the old
coarse-certificate failure is not an actual-envelope lower bound.
Own-coordinate monotonicity and coverage are accepted dependencies; root checked
the simultaneous coordinate composition by chaining their global inequalities.
No numerical tests were executed by Fable. Agent checks passed normal/-O;
root rederived the stationary point and boundary formulas.
''',27:'''ROOT ADJUDICATION 27 -- SHARP LOCAL ENTROPY AND DIFFUSE RESIDUAL INTERVAL
17 October2026. Accepted internally; no claim of exact order-epsilon coefficient.

Accept SHARP_LOCAL_ONLY_ENTROPY, INCOMING_RETENTION_PENALTY and
DIFFUSE_ONE_CAPPED_GRID_LOWER after root reconstruction and Fable194408/195213.
Let W be the unrestricted hardware-bottleneck actual-envelope supremum with
max_i z_i/H<=epsilon; L=log(1/epsilon),c=1/(2e),K=e-1,C=1+c. Then
 -c[e+1+K log2] <= liminf [W-C-cK epsilon(L-log L)]/epsilon
 <= limsup [W-C-cK epsilon(L-log L)]/epsilon <= c(K-2).
These are an interval of coefficients, not equality or proof that the limit exists.
Both counts grow in the actual fixed-owner lower. It is stronger than the earlier
restricted common-cap witness's coefficient. The construction uses two distinct
actual deviations for two different envelope recipients, legitimately summed.

The new local inequality charges retention: for a removed original long resource,
I<=v[(K-1)V+D]. Summation with entropy weights retains the own-payment loss D;
the negative outer payment comparison charges (g+1)D, not just D. Root independently
rederived the retention switch case, scalar stationary equation and expansions.
Fable's beta citation finding was valid and repaired: the uniform bound follows
from SHARP_LOCAL_ONLY_ENTROPY (5)-(6), eventually max(K epsilon L,e epsilon)
<=K epsilon(1+L), rather than the older global estimate with an extra epsilon.
Fable's positive-part concern in the switch lemma is harmless because both
coefficients q,q_new<=1/2; this fact is now explicit in the proof.

Root independently evaluated the full actual-owner one-cap construction at90-digit
precision for three shrinking epsilon values, 164 to8708 owners, with11 checks each.
These finite diagnostics corroborate the analytic family, not prove asymptotics.
Fable ran no code. The accepted global restoration/outgoing dependencies have
already been reviewed in adjudications13,18,25 and remain unchanged.
''',28:'''ROOT ADJUDICATION 28 -- DIRECTIONAL MASS AND HIGH CAPPED TOTAL
17 October2026. Accepted sufficient-profile theorems, not unrestricted C^2.

Accept DIRECTIONAL_LOCAL_MASS_FUNDING and HIGH_CAPPED_TOTAL_FUNDING after root
reconstruction and Fable195044. At a normalized hardware bottleneck:
 (i) positive-gap local-payment mass delta_plus<=1/100 implies sum E<7/5;
 (ii) capped total S>=3 implies sum E<=1+11/(4e^2)<7/5.
Both allow arbitrary mixed owners, cap overflow and growing owner/branch counts.
No restoration or class-preserving restriction is imposed on feasible deviations.

The sharp K=e-1 incoming estimate is essential for (i). Fable correctly asked
for dependency status because an old proof header said pending. Adjudication18
already accepts that estimate after independent analytic and exact checks; this
resolves the dependency, rather than assuming it away. The high-S bound (ii)
even survives dropping negative savings, as the review notes.
The narrow rational margin in the high-S support is now displayed with a finite
Taylor sum plus geometric tail: exp(1069/825)<183/50<11/3. Root independently
replayed the10 high-S and11 directional exact Fraction checks under-I-O.
Review was by hand from frozen files; Fable did not run these scripts.
''',29:'''ROOT ADJUDICATION 29 -- EXACT POSITIVE-GAP CONVEX PROGRAMS AND CAP COUNT
17 October2026. Positive-gap result accepted; negative extension separately reviewed.

Accept JOINT_RESPONSE_CONVEX_LOCAL_FRONTIER and CONVEX_LOCAL_FOUR_PROGRAM_BOUND,
conditional on their explicit physical hardware bottleneck, exact actual hardware/
grid restoration (ER), and redundant opponent local-supply hypotheses (LB).
The ER sufficient condition is already accepted in adjudication25; no-hardware
owners also satisfy ER directly. These hypotheses are not removed by this audit.

Root and Fable195405 rederived exact logarithmic coordinates, jointly attainable
opponent affine responses and own concave response. Per actual cap pattern, the
positive-gap objective is concave over a convex domain; its open logarithmic
boundary cannot contain the maximum, so attainment is valid. A cosmetic description
of the domain as closed was not needed. Local notation is being clarified to avoid
confusing branch local caps with outer capped accounts.

The sharp sum of opponent coordinate maxima is at most
 D M, D=1+(1/2)exp(-1/e)<3/2.
Using the simpler3M/2 and effective grid pi<=51/40 gives at most2 crossing opponents
and at most4 cap patterns, independently of owner and branch counts. All4 patterns
are attainable in a growing fixed-owner family; this is not a computational lower
bound. The exact programs retain joint responses; independent minima remain invalid.
This is a real-arithmetic representation, not a polynomial-bit or finite-precision
truthful implementation. Fable ran no scripts; exactness rests on analytic recovery.
'''}
for n,t in notes.items(): (a/f'ROOT_REVIEW_ADJUDICATION_{n}.txt').write_text(t)
manifest={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in a.glob('ROOT_REVIEW_ADJUDICATION_*.txt')}
(a/'ADJUDICATION_HASHES_0004.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Copied five complete reviews; wrote adjudications26-29.')
