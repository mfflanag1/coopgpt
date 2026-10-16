from pathlib import Path
p=Path('/private/tmp/coopgpt-ownership-20261016/PROOF_MAP.txt');s=p.read_text()
s=s.replace('16 October2026,23:45UTC.','17 October2026,00:39UTC.')
a=s.index('B. GENERAL MIXED-OWNER FUNDING:');b=s.index('\nC. SHARP ASYMPTOTIC',a)
s=s[:a]+'''B. GENERAL MIXED-OWNER FUNDING: CURRENT MAIN THEOREM
 root/entropy_general_certificate/GENERAL_323_200_ENTROPY_CERTIFICATE.txt
 root/entropy_general_certificate/verify_certificate.py
 root/entropy_general_certificate/certificate.json
Adjudication35: sum E_i<=323F/200 for every profile in the stated two-stage
pooling model, arbitrary actual mixed owners and unbounded finite counts.
Continuous32,768-rectangle rational weak-duality certificate, independently
replayed by root and Codex. External high-grid and physical-power regimes are
analytic. Not an efficient exact evaluator or a mechanism-optimality theorem.
This supersedes13/8 and27/16 for the SAME envelope. Earlier asymmetric171/100
is a DIFFERENT rule; historical range-rule claims must not be assigned to E.
New dependencies: subset entropy and eta4 spill, adjudication34. All selected
positive-dual parameters constrain the same actual sum of positive excesses.
A newer8/5 certificate attempt is LIVE and NOT established. In particular,
S>=2 does NOT automatically imply C^2; the unsupported statement in a draft
one-cap note was withdrawn. Its valid S<2 inequality is unaffected.
''' +s[b:]
s=s.replace(' SHARP_LOCAL_ONLY_ENTROPY.txt is a newer sharper response/upper-term candidate;\nits review is separate. General order-eps coefficient remains open.', ''' NET_HARDWARE_RESPONSE_CHARGE.txt: accepted general residual limsup
 <=-c[2+Klog2], adjudication33. SHARED_RESPONSE_BRANCH_DIFFUSE_LOWER.txt:
 accepted residual liminf >=approximately-0.785643710331513, adjudication36.
 A sharper mixed-response lower is in independent review; do not promote it
 before adjudication. The existence/exact value of a residual limit is open.
 TWO_CAPPED_ACCOUNTS_DIFFUSE_GAP.txt: exactly half the leading coefficient
 cK/2 on profiles with at least two full outer caps, adjudication31.''')
s=s.replace('being separately checked; coarse-bound failure is not a mechanism lower bound.', 'accepted under adjudication26; coarse-bound failure is not a mechanism lower bound.')
pos=s.index('\nG. OTHER ACCEPTED STRUCTURAL')
s=s[:pos]+'''
 certificates/nonlinear_funding/CONVEX_LOCAL_FOUR_PROGRAM_BOUND.txt
 certificates/nonlinear_funding/GLOBAL_NEGATIVE_LOCAL_CONVEXITY.txt
Adjudications29--30: under physical hardware bottleneck, actual hardware/grid
restoration and opposing-local-supply hypotheses, positive gaps use at most
four concave programs in the stated low-effective-grid regime. Negative gaps
use one globally strictly convex nonsmooth program, without grid/cap-count
restriction. These are conditional exact reductions, not polynomial bit-
complexity results or an unrestricted finite-precision truthful implementation.
 certificates/nonlinear_funding/MONOPOLY_HARDWARE_COORDINATE_RESTORATION.txt
Adjudication26: sole-hardware-owner restoration and exact dominance-class C.

F2. NEW LOCAL/OWNER COMPATIBILITY INEQUALITIES
 mixed/outer_scalar/review_13_8/SUBSET_ENTROPY_DEFICIT_COUPLING.txt
 mixed/outer_scalar/review_13_8/ENTROPY_DEFICIT_WEIGHT_FOUR.txt
 mixed/outer_scalar/review_13_8/PARAMETRIC_ENTROPY_DEFICIT_SPILL.txt
 mixed/outer_scalar/review_13_8/TWO_PARAMETER_ENTROPY_SPILL.txt
Adjudications34,37: actual-owner subset entropy and general real-parameter
spill/deficit inequalities. Exact clipping, convexity and directed rational
constants, not numerical profile fitting. The entropy perspective is sharp
on the stated r in[c,1/2] face only.
 mixed/outer_scalar/review_13_8/NEGATIVE_GAP_CONCENTRATION_CHORD.txt
Adjudication34: negative saving retains sum_i z_i g_i^2, with a valid aggregate
v^2 Zminus relaxation. Supports sharper general certification.
 ownership/outer_frontier/hardware_bound/extension/SIGNED_OTHER_LOCAL_LOSS_FOUR_OVER_E.txt
Adjudication37: signed OTHER local-only loss<=4z_i/e, hardware retained. A sharp
constantLambda theorem is now in independent review. Neither statement controls
the sum of positive losses or capped outer losses without extra accounting.
 root/entropy_general_certificate/positive_frontier/
New sharp inverse-entropy individual gap ceiling and one-capped-positive dual
coupling: root/Codex/Fable algebra reviews PASS; final adjudication pending.
''' +s[pos:]
p.write_text(s)
print('Current proof map updated, with live claims separated.')
