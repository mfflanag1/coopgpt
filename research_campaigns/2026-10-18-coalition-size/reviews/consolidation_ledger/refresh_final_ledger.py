"""Root reconciliation of the earlier frozen claim ledger and later audits.

Does not edit the earlier snapshot, execute mathematics, or infer acceptance
from a filename. Exact completed review dispositions are specified below.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
original = HERE / 'CLAIM_LEDGER.json'
ledger = json.loads(original.read_text())
ledger['created_utc'] = datetime.now(timezone.utc).isoformat()
ledger['schema_version'] = 'root-final-reconciliation-1'
ledger['snapshot_status'] = 'Root reconciliation; campaign timing/completion is controlled by STATUS.json and FINAL_CAMPAIGN_ADJUDICATION.txt.'
ledger['prior_snapshot_sha256'] = hashlib.sha256(original.read_bytes()).hexdigest()
ledger['verification_scope'] = (
    'Root reconciled the frozen source-status ledger with later native/opposite-model audits and root dispositions. '
    'The original consolidation agent wrote a draft before a capacity error; its unfinished turn is not counted as final independent approval. '
    'This script checks links/hashes, not mathematics. Actual exact replays are separately recorded under checks/portable_runner_validation/ '
    'and checks/final_supporting_replay/. Historical and new execution are distinguished.')

updates = {
    'A1': ('Sealed metadata-only gate; no power/state observations or value extrema selected/displayed and no heldout outcome analysis. Whole raw footers may encode unselected summaries. Final independent source/output audit and root clarification preserve the raw ledgers, unfrozen protocol, April calibration and unverified rights/sponsor status.',
           ['reviews/APPLICATION_FINAL_PROVENANCE_DISPOSITION.txt', 'reviews/application_leakage_final_audit/AUDIT.txt']),
    'M1': ('Accepted after independent derivations, completed opposite-model reviews, exact supporting replays and a fresh final adversarial audit of compatibility with the inherited upper. No anonymity, dummy-zero or smaller report domain is assumed; historical novelty unconfirmed.',
           ['reviews/BASELINE_COMPATIBILITY_ROOT_CHECK.txt', 'reviews/final_contract_adversarial_audit/AUDIT.txt']),
    'T5': ('Accepted after native audit, completed opposite review20261018-200840-7083e0cc, root funding/interiority/mean clarifications and independent final clarification audit.',
           ['reviews/LOCAL_AND_HOMOGENIZATION_ROOT_DISPOSITION.txt', 'reviews/homogenization_audit/CLARIFICATION_REAUDIT_2026-10-19.txt']),
    'T6': ('Accepted after native exact checks and completed opposite review20261018-200457-ee9a5855; root made explicit all-subset, face-coordinate, technology and finite-admission hypotheses, independently rechecked.',
           ['reviews/LOCAL_AND_HOMOGENIZATION_ROOT_DISPOSITION.txt', 'reviews/local_incentive_audit/CLARIFICATION_REAUDIT_2026-10-19.txt']),
    'T7': ('Accepted within supplied verified rational continuous piecewise-affine partitions after independent seven-fixture exact synthesis, opposite review20261018-201435-5d59e464, root row-wise-eligibility wording repair and fresh portable replay. No unrestricted PL completeness.',
           ['reviews/POLYHEDRAL_AND_CEA_ROOT_DISPOSITION.txt', 'reviews/polyhedral_audit/AUDIT.txt', 'checks/final_supporting_replay/independent_synthesis.json']),
    'P1': ('Priority remains unconfirmed. Root rejected the delivered source follow-up after direct-original corrections, including presence of main proofs in Ju et al. and the strict proof-supported Pountourakis–Vidali threshold. Checked leads only retained. Thomson2024 full original remains unavailable.',
           ['reviews/priority_projective/FOLLOWUP_RESEARCH_ADJUDICATION.txt', 'reviews/priority_projective/FREE_ORIGINAL_FOLLOWUP.txt', 'reviews/ju_hierarchy_root_check/AUDIT.txt', 'reviews/SOURCE_CONTRACT_ROOT_ADJUDICATION.txt', 'reviews/priority_projective/S15_FINAL_ACCESS_CHECK.txt', 'reviews/PUBLISHED_VERSION_ROOT_DISPOSITION.txt', 'reviews/published_version_delta_audit/AUDIT.txt']),
}
for entry in ledger['entries']:
    if entry['id'] in updates:
        entry['audit_status'], more = updates[entry['id']]
        entry['review_paths'] += [p for p in more if p not in entry['review_paths']]
    if entry['id'] == 'T7':
        entry['handoff_summary'] = 'Accepted finite certificate/synthesis language within a continuous fixed-partition class; no unrestricted funding improvement or representation completeness.'


def add(identifier, group, title, claim, domain, limits, sources, reviews, status):
    ledger['entries'].append({'id': identifier, 'group': group, 'title': title,
        'exact_claim': claim, 'domain_and_quantifiers': domain,
        'does_not_establish': limits, 'source_paths': sources, 'review_paths': reviews,
        'audit_status': status, 'handoff_summary': claim})


add('T9', '3_certificate_and_regularity_tools', 'Coarse production-chamber representation barrier',
    'For one minimum of r>=2 pool totals with n fully eligible owners and positive coordinate endowments, every nonnegative continuous rule affine only on the r production chambers and finitely funded has y_i=c_i F. Coverage implies c_i>=1, so the exact restricted factor is n.',
    'One fixed actual-owner full box; r>=2 is essential. Lower does not need incentives. Matching y_i=F satisfies full OUT for every coalition.',
    ['Not a general mechanism lower.', 'No lower on the number of cells in a finer owner-sensitive partition.', 'Does not apply at r1 or to arbitrary eligibility patterns.'],
    ['root/PRODUCTION_CHAMBER_PARTITION_BARRIER.txt'],
    ['reviews/POLYHEDRAL_AND_CEA_ROOT_DISPOSITION.txt', 'reviews/polyhedral_audit/PRODUCTION_CHAMBER_BARRIER_AUDIT.txt'],
    'Native proof audit and completed opposite review20261018-201435-5d59e464 accepted the precise hypotheses; root agrees.')
add('T10', '3_certificate_and_regularity_tools', 'CEA owner-sensitive PL calibration',
    'For ONE F(T)=min_a T_a technology, sum each owner’s constrained-equal-awards allocations of common estate F(T) over all r pools. Total funding equals rF, every coalition is covered, and full OUT holds for every coalition size at every real report. The rule is continuous homogeneous PL with explicit saturated-owner cells.',
    'Arbitrary fixed actual mixed owners and finite coordinate boxes, including zero endowments, ties and zero output. CEA is a classical primitive; a bottleneck-interval proof supplies the all-real result.',
    ['Not an arbitrary arity-r packing upper.', 'No sharpness or historical-novelty assertion.', 'Not proof that continuous PL rules approximate the unrestricted optimum.'],
    ['constructive/capped_awards_calibration/CEA_MINIMUM_FULL_OUT.txt'],
    ['reviews/POLYHEDRAL_AND_CEA_ROOT_DISPOSITION.txt', 'reviews/cea_calibration_audit/AUDIT.txt', 'checks/final_supporting_replay/check_refined_cells.json'],
    'Native independent all-real region certificates and90,396 endpoint comparisons, author replay, completed opposite proof review and root replay PASS. Counts are for n3/r2; the universal scope comes from the written proof.')
add('R12', '2_restricted_sharpness_and_barriers', 'Finite cost of efficient-price domination',
    'On the same sealed twelve-profile three-owner min3 fixture, the exact unrestricted finite optimum is5/4. Requiring domination of some efficient nonnegative production-dual allocation at each profile raises it to3/2, even with freely chosen profile-dependent prices.',
    'All seven nonempty static coalitions at each selected profile and all108 legal protected comparisons of size<=2, including24 proper comparisons with unchanged members. Matching primals and complete expanded duals cancel actual y and p variables.',
    ['No growing-family obstruction.', 'No all-real upper attainment claim for either finite optimum.', 'No rejection of every O(s) price-plus-reserve rule.', 'The extra domination condition is not without loss.'],
    ['reviews/next_frontier_synthesis/PRICE_BASE_RISK_CHECK.txt', 'reviews/next_frontier_synthesis/check_price_base_fixture.py'],
    ['reviews/price_base_fixture_audit/AUDIT.txt', 'reviews/price_base_fixture_audit/check_independent.json', 'reviews/price_base_fixture_audit/FINAL_SYNTHESIS_CLARIFICATION.txt', 'reviews/PRICE_BASE_AND_SYNTHESIS_ROOT_DISPOSITION.txt'],
    'Native exact audit, completed opposite review20261018-202826-0db0f369 and root disposition accept the finite diagnostic. The six high-profile efficient prices are unique; low prices remain free. No growing extrapolation is accepted.')

add('R13', '2_restricted_sharpness_and_barriers', 'Sharp price domination on the binary unit-worth ideal',
    'On the entire binary unit-worth ideal of a finite linear unit triple technology with pure unit owners, requiring domination of some efficient nonnegative price allocation has worst optimum A1=1 and A_s=1+2s q_s=1+[s/(s-1)](B_s-1) for s>=2, for both TCWM and full OUT. It has the same square-root leading constant as B_s.',
    'Every coalition is covered; every legal binary comparison for each protected actual-owner subset of size<=s is checked, including passive members. Prices may be chosen freely at each profile and are averaged with payments in the lower. The actual funding peak is m=s-1,s for s>=3 and onlym2 for s2.',
    ['Not an all-real upper or unrestricted mechanism frontier.', 'No growing architecture obstruction can exceed this exponent using only this exact restricted ideal.', 'Does not remove the finite cost of price domination on other domains or imply it is without loss.'],
    ['constructive/price_reserve_growing_gate/UNIT_WORTH_PRICE_BASE_FRONTIER.txt'],
    ['reviews/PRICE_RESERVE_GROWING_ROOT_DISPOSITION.txt', 'reviews/price_reserve_growing_audit/AUDIT.txt', 'reviews/price_reserve_growing_audit/FINAL_CLARIFICATION_AUDIT.txt'],
    'Scoped acceptance after independent proof/exact audit, completed opposite review20261018-205024-834f9222, and verified two-sentence clarification. Historical priority unassessed.')
add('R14', '2_restricted_sharpness_and_barriers', 'Global one-layer report systems admit rank funding',
    'For any finite selected profile system whose every distinct-profile comparison goes from one global source set to a disjoint global sink set, source efficient prices and sink rank charges cover all coalitions, satisfy full OUT, dominate efficient prices and cost at most rF.',
    'Arbitrary fixed actual mixed owners, legal real profiles and nonnegative finite arity-r packing technology. All nonzero restorations count, including restored bundles with zero worth. Source/sink roles must be globally consistent across coalition labels.',
    ['Not a rule on the complete real report box.', 'Per-coalition forest/source-sink normal forms do not supply the global hypothesis.', 'Profiles that both receive and emit comparisons leave an uncontrolled outgoing reserve term; no general factor-r upper follows.'],
    ['constructive/price_reserve_growing_gate/ONE_RESTORATION_LAYER_BARRIER.txt'],
    ['reviews/PRICE_RESERVE_GROWING_ROOT_DISPOSITION.txt', 'reviews/price_reserve_growing_audit/AUDIT.txt', 'reviews/price_reserve_growing_audit/FINAL_CLARIFICATION_AUDIT.txt'],
    'Scoped acceptance after independent proof/exact audit, completed opposite review20261018-205024-834f9222 and explicit clarification that nontrivial means nonzero restoration, not positive outside worth.')

for alert in ledger['conflicts_and_scope_alerts']:
    if alert['id'] == 'C8':
        alert['disposition'] = 'Superseded by LOCAL_AND_HOMOGENIZATION_ROOT_DISPOSITION and POLYHEDRAL_AND_CEA_ROOT_DISPOSITION; preserve the original pending snapshots as history.'
ledger['conflicts_and_scope_alerts'].append({
    'id': 'C11', 'kind': 'source_report_rejected',
    'paths': ['reviews/priority_projective/FOLLOWUP_RESEARCH_ADJUDICATION.txt', 'reviews/priority_projective/FREE_ORIGINAL_FOLLOWUP.txt'],
    'finding': 'A delegated report and its QA incorrectly described the hierarchy original as lacking main proofs and overstated a cost-sharing boundary.',
    'disposition': 'Delivered report rejected; direct-original root corrections govern. No global novelty clearance.'})

paths = sorted({p for entry in ledger['entries'] for field in ['source_paths', 'review_paths'] for p in entry[field]})
missing = [p for p in paths if not (CAMP/p).is_file()]
if missing:
    raise SystemExit('Missing source paths: ' + repr(missing))
ledger['files_sha256'] = {p: hashlib.sha256((CAMP/p).read_bytes()).hexdigest() for p in paths}
(HERE/'FINAL_CLAIM_LEDGER.json').write_text(json.dumps(ledger, indent=2, ensure_ascii=False)+'\n')
lines = ['ROOT-RECONCILED CLAIM LEDGER', ledger['created_utc'], ledger['verification_scope'],
         'One main unrestricted lower contribution; constants/corollaries/tools are not separate paper counts.', '']
for group in ledger['groups']:
    lines += [group['title'], '']
    for entry in ledger['entries']:
        if entry['group'] != group['id']:
            continue
        lines += [entry['id']+' — '+entry['title'], 'Claim: '+entry['exact_claim'],
            'Domain: '+entry['domain_and_quantifiers'],
            'Limits: '+' '.join(entry['does_not_establish']),
            'Status: '+entry['audit_status'],
            'Sources: '+'; '.join(entry['source_paths']),
            'Reviews: '+'; '.join(entry['review_paths']), '']
(HERE/'FINAL_CLAIM_LEDGER.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'entries': len(ledger['entries']), 'linked_source_files': len(paths), 'missing': missing}))
