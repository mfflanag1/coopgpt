from pathlib import Path
import shutil
r=Path('/private/tmp/coopgpt-ownership-20261016');a=r/'audits';s=Path('/Users/maxf/.local/state/claude-reviews/coopgpt-ownership-20261016-0ad718e4be4a/20261016-203935-c4c4f583')
for f in ['review.md','request.json','status.json','execution.json']:shutil.copy2(s/f,a/('JOINT_RESPONSE_OBSTRUCTION_AND_LOWER_FABLE_'+f))
(a/'ROOT_REVIEW_ADJUDICATION_40.txt').write_text('''ROOT ADJUDICATION 40 -- EXACT JOINT-RESPONSE OBSTRUCTION AND DIFFUSE LIFT
17 October 2026. Accepted internally after independent root and Fable checks.

Accept JOINT_SIGNED_RESPONSE_OBSTRUCTION: the proposed joint signed-response
inequality with charge Lambda(z_A+z_G) is false. Three actual owners with
hardware1, local1 and local2/5 yield exact ratio(11exp(2/5)-8)/7>6/5>Lambda.
A gain to G can offset losses in A's local signed response yet be hidden by
G's outer cap; the two separate own deviations therefore cannot be charged
as though both used the single-deviation signed theorem. This is a precisely
scoped obstruction to that inequality, not a mechanism impossibility theorem.

Accept JOINT_RESPONSE_DIFFUSE_LOWER: unbounded fixed-owner instances yield
liminf [W-C-cK*epsilon*(L-log L)]/epsilon >= c[J-2e-K log2],
J=(11/5)exp(2/5)-8/5+(3/5)Lambda, approximately -0.777825046106238.
This improves the prior sharp pair lower, and preserves all-small-real-epsilon
coverage, actual whole-bundle deviations and growing branch/owner counts.
Root rederived the three deviations, exact cap patterns and inherited core
expansion; Fable 203935 checked the module identities and found no error.
The global upper residual remains -c[2+K log2], so no residual limit or exact
next coefficient is asserted.

Review followups were implemented and checked:
1. The source now explicitly states that after G's deviation, A's local
   payment is [w exp(w)+1-w]epsilon>epsilon. This is permitted: W constrains
   the FULL profile only, and the actual own-report envelope has no epsilon
   restriction on hypothetical counterreports. A remains uncapped because
   its cap distance is asymptotic to1/L, much larger than epsilon.
2. The exact Fraction checker now constructs all three rational profiles,
   symbolically replays baseline payments in q, verifies the two deletion
   profiles have primitive coefficient1/2, and checks signed losses and ratio
   identity before its five exact Taylor comparisons. Root read and replayed
   this enhanced checker under -I -O. The source and checker versions reviewed
   by Fable remain preserved as reviewed_203935_ files.
3. Root replayed the updated 110-digit lower-family checker. Its numerical
   profiles corroborate the analytic continuum construction and are not the
   proof. Large multiplicities are represented algebraically, not enumerated.

Fable executed no code. Internal review is not external specialist review.
No historical novelty or unrestricted-mechanism lower bound is claimed.
''')
print('Adjudication40 and review records saved.')
