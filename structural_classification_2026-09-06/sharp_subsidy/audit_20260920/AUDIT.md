# Independent audit and bounded strengthening attempt

2026-09-20. Original model preserved. No purchases or outreach.

## Current result and evidence tier

The global conventional proof S3 <=39999/100000 survives the two focused
cross-model audits and coordinator reconstruction, after explicit treatment of
the all-leaf case and hypothesis clarifications. This is not proof-assistant
certification or an external specialist verdict. Global sharpness remains open.
The bounded attempt improves the three-label affine lemma from coefficient
17/18 to the optimal13/18 at intercept1/18. An exact obstruction shows that
this local-coefficient route alone cannot prove the global1/3 target through
the retained aggregate inequalities. It is not a market counterexample.

## Audit coverage and adjudication

1. Cloning, compatibility, weighted counting: completed snapshot review
20260920-100442-c54229b5. Reviewer rederived Sections2,3,5 and found an omitted
I=empty case plus implicit hypotheses. Coordinator verified the topology:
all labels degree1 in a connected nontrivial component forces exactly one
P-team and three distinct labels; h=2. The old local lemma at the smallest
label gives10/27, below the claimed global bound. The proof now states this
case and restricts the master inequality to I nonempty. Nonnegative payoffs
follow from zero singleton values; k>=1 follows from nontrivial connectedness.
Optimal diagonal matching is now explicit in the local lemma. These repairs
clarify proof scope; they do not alter the model or the claimed upper bound.

Coordinator separately checked clone tightness in both directions: replacing
one same-sector copy in its tight diagonal yields the payoff inequality;
reversing the replacement gives equality. Sparsification preserves diagonal
worth and expands the core; component restriction maps a global core point
into a local core, so local ideals dominate global ideals in the required
upper-bound direction. No product-core assertion is used. Repeated incidences
are assigned distinct diagonal copies. Weighted-count edge identity includes
parallel edges and cycle rank; proper threshold subsets have one boundary
incidence per component at least. Integrating yields exactly the stated bound.

2. Donor-slack: completed snapshot review20260920-100543-e2d29c2a, no defect
reported in scoped implication. Coordinator checked all four packing mass
types in MIXED_DONOR_UPPER.md and the base capacity argument in SURPLUS_UPPER.md.
A non-row-sector internal donor player receives only beta-z diagonal mass
and at most alpha P mass; leaf pair completions cannot touch it. Thus its
load is at most1-z. The x_s<1-a prerequisite prevents degree-two extra-transfer
rows; x_s>1/5+a gives common positive leaf headroom. Both are derived in the
proof and exact SMT gates, now highlighted in prose. Averaging the leaf-row
maximizers preserves the original core. The donor budget minimum1/5 and
Delta_s/Gamma>=1/4 give C_player>=Q/20; exact slack gives Q/T<=60g.

Reviewer limitations were respected: it spot-checked localization and did not
execute scripts. Coordinator read the finite and localization arguments,
including new-active-sector cases q=1,2,3, h=2, and the min(1,eta) split.
The full build covers their scalar queries and coefficient examples, not an
exhaustive proof of all combinatorial markets. Conventional arguments supply
that generalization. No scoped no-findings verdict is treated as a blanket proof.

3. Local certificate and strengthening: full-team LP calibration reproduced
max(J-(17/18)d0)=1/18 with exact primal and dual. Two formulations, within the
predeclared20-minute search ceiling: test the coefficient17/27 required to
remove the scalar barrier at fixed intercept; obtain exact violation. The
witness forces coefficient>=13/18; a second LP supplies a matching certificate.
The independent standard-library verifier reconstructs all27 teams per each
of6 witnesses, checks every player load and aggregate pair coefficient, checks
sharpness with rational arithmetic, and rejects three damaged inputs under
python -O. See AFFINE_REFINEMENT.md and AFFINE_CERTIFICATE.json.

The precise bottleneck is no longer an unknown best local coefficient:
coefficient13/18 is sharp, whereas this aggregate route would need at most17/27.
The resulting scalar relaxation has matching exact primal and dual value29/82.
Its feasible point is not certified realizable by a market. No claim that every
cloning strategy fails, and no change to the global bound, follows from it.

## Reproduction and provenance

A clean temporary environment restored numpy, scipy and z3-solver after the
old scratch environment had disappeared. The original nineteen-file manifest
was checked against all canonical files before integration, with no mismatch.
BASELINE_MANIFEST.json preserves it. The original full build passed in an
isolated copy. After integration, the required full build includes the new
verifier; see BUILD.log and the final manifest for its completion record.

The proof, exact certificate and stdlib verifier are authoritative. module_probe.py
is optional SciPy discovery/reproduction, not trusted by the independent check.
The new certificate check command is:

    python3 -O audit_20260920/verify_affine_refinement.py

The full command is:

    COOPGT_PYTHON=<python-with-numpy-scipy-z3> bash build.sh --smt

Review reports and their original request hashes are retained in reviews/.
The reviewed old proof preceded the small explicit-case edits above. The new
local lemma has a separate focused review; its final adjudication is recorded
below after the report is collected. No paper submission or human outreach.

## Source integrity and novelty

SOURCE_CHECK.md records the free-original comparisons and exact source locations.
The subsidy LP/dual, generic priority-floor constructions, equal-treatment
reasoning, and threshold counting techniques are established ingredients.
The 2026 sectorwise attainment theorem has supermodularity and local-monotonicity
hypotheses, not general validity for our model. Original Quint/Lucas/Stuart
comparisons remain unavailable/unresolved; no purchase was made. The proposed
contribution is the particular protected-subsidy bound and its proof, with this
local refinement as supporting mathematics. Novelty is not confirmed, and a
field-level breakthrough is not established.

## Completion requirements

- Independent focused audit of cloning/counting/donor-slack: collected and
  findings independently checked; explicit-case repair applied.
- Original hypotheses and original ideals: retained throughout.
- Bounded strengthening attempt: two formulations completed; sharp local
  improvement and exact limitation of that route documented.
- Reproducible evidence: exact certificate and solver-free verifier supplied;
  final integrated build and new-claim review completed; see adjudication below.
- Free source comparisons and established/proposed distinction: documented;
  unavailable originals and novelty uncertainty explicit.

## Final focused review and adjudication

Review20260920-101645-842b9596 completed and independently rederived the new
packing proof, sharpness witness, and scalar barrier without an algebraic defect.
It flagged (a) implicit diagonal-optimality verification and (b) a metadata-only
negative control. Finding(a) was already logically covered: diagonal worth1
plus a nonnegative full-team cover of total1 proves optimality by weak duality.
For a more direct independent check the verifier now enumerates all36 perfect
matchings and checks their maximum is1. With nonnegative weights, any partial
matching extends to a perfect matching, so this also covers ordinary grand worth.
No uniqueness assumption was added.

Finding(b) was valid. The canonical metadata check is now outside the generalized
checker; the changed coefficient17/27 must fail specifically at pair domination,
not metadata. All three damaged controls have required failure gates. The revised
verifier passed under python -O with162 team inequalities, 36 assignments and6
packing rows. The reviewed snapshot predates these narrow verification changes;
coordinator inspected and executed the final changes independently. No new theorem
assumption or stronger conclusion was introduced after review.

The bounded mathematical search is closed after its two formulations. This
only rules out reducing b at a fixed a=1/18 in the displayed relaxation; other
intercepts, non-affine envelopes and additional joint constraints remain open.
The final integrated full build completed with exit code 0 after these verifier
changes (session 63349). Its final check reports 162 team inequalities, 36
matchings, 6 deletion rows and 3 rejected damaged controls. MANIFEST.json records
final hashes. All requirements of this bounded audit/attempt are met; the
unresolved global conjecture and novelty claims are not promoted to results.
