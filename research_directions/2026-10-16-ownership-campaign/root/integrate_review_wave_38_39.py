from pathlib import Path
import shutil
r=Path('/private/tmp/coopgpt-ownership-20261016');a=r/'audits';base=Path('/Users/maxf/.local/state/claude-reviews/coopgpt-ownership-20261016-0ad718e4be4a')
for run,label in [('20261016-203321-c24a56a6','SHARP_SIGNED_AND_OWNER_CEILING'),('20261016-203630-ff207e8b','SHARP_PAIR_AND_ROW_DIRECTIONS')]:
    for f in ['review.md','request.json','status.json','execution.json']:
        shutil.copy2(base/run/f,a/(label+'_FABLE_'+f))
(a/'ROOT_REVIEW_ADJUDICATION_38.txt').write_text('''ROOT ADJUDICATION 38 -- SHARP SIGNED RESPONSE, INVERSE ENTROPY AND ONE CAP
17 October 2026. Accepted internally; no universal 8/5 theorem implied.

Accept SHARP_SIGNED_OTHER_LOCAL_LOSS: fixed own hardware and arbitrary local-only
whole-bundle withholding cause signed other-local loss at most Lambda*z_i,
where v_* exp(v_*)=1/2 and Lambda=(1-v_*)^2/v_*. The constant is attained.
Root rederived the short-stage endpoint argument and long-stage switch ratio;
independent Codex audits checked both parts, and Fable 203321 found no error.
The short role has sharp constant one; summing gives the role-sensitive charge
U_local-short+Lambda*V_local-long. Hardware components are not charged again.
Exact scalar comparisons and the actual attainment were checked separately.
This supersedes the earlier signed 3/2 and 4/e upper bounds on the SAME domain.
It does not control positive-loss sums or cap-truncated outer-account losses.

Accept SHARP_DEFICIT_OWNER_GAP_CEILING and ONE_CAP_POSITIVE_DUAL_COUPLING on S<2.
Root and independent Codex reconstructed the branchwise role inequality,
Jensen/inverse-entropy direction, tangent family, actual sharpness family,
and the one-cap scalar intersection. High-precision finite checks corroborate
these analytic proofs; they do not replace the continuum proofs. Fable 203321
found no substantive error. Its E_i caveat is resolved against PROOF_MAP: E_i
is exactly the outer primitive's actual own-report supremum, not a sum with
an additional local payment. Every candidate raw payment is bounded by its
outer short total, itself at most full H=1, so E_i<=1 is valid.

CORRECTION: root discovered that the original one-cap note incorrectly cited
a general S>=2 C^2 result. The cited theorem had an additional orientation
hypothesis. This extraneous claim was withdrawn in the source; its reviewed
version is preserved as reviewed_before_S2_correction_ONE_CAP.txt. The valid
S<2 proof and accepted 323/200 theorem never use this false shortcut. Any
future global certificate must cover S>=2 with independently valid rows.
The independent Codex/Fable reviews did not initially flag this source-scope
sentence; root did. Review success is not proof of infallibility.
''')
(a/'ROOT_REVIEW_ADJUDICATION_39.txt').write_text('''ROOT ADJUDICATION 39 -- SHARP PAIR LOWER AND DIRECTED ROW COEFFICIENTS
17 October 2026. Accepted internally; no universal 8/5 theorem implied.

Accept SHARP_SIGNED_RESPONSE_DIFFUSE_PAIR_LOWER: the existing all-small-epsilon
fixed-owner core together with two sharp signed-response modules yields residual
liminf at least c[2Lambda-2e-K log2]. Root independently reconstructed the
module payments, full S=2 cap pattern, each separate own deviation and the
order-epsilon expansion, and replayed the 110-digit checker under -I -O.
Fable 203630 rechecked the displayed identities and found no error. The full
profile alone must satisfy diffuseness. The construction applies for every
sufficiently small real epsilon, with both owner and branch counts growing.
It bounds this specified envelope from below, not all truthful mechanisms.

Accept the interval directions in root/RATIONAL_CAP_AND_CHORD_ROW_AUDIT.txt
as supporting algebra. Independent Codex and Fable 203630 agree. In particular:
- one-cap T uses p_hi, mu_lo, b_hi=1-lambda_lo, alpha_lo, whereas the base
  positive-dual terms use lambda_hi and mu_hi; opposite directions are deliberate;
- Bsafe is enlarged and multiplied while nonnegative before its M coefficient
  is expanded, so a negative expanded coefficient is harmless;
- v+Zminus<=1 follows by summing z_i+g_i=a_i-p_i on negative uncapped owners;
- first lower the common negative-saving prefactor on the nonnegative grouped
  bracket, then replace v^2 by the bin upper, permitting the same lower
  prefactor in the resulting positive correction;
- the PF row uses the proved IG8 support and only nonnegative grouped products.
Root previously checked these dependencies against accepted PD1, negative-gap
saving and individual-gap sources. Fable did not receive all upstream notes
and did not execute scripts; those limitations are retained in its report.
A complete partition and independent rational weak-duality replay are still
required before any stronger global funding factor may be claimed.
''')
print('Adjudications 38 and 39, and cross-model records saved.')
