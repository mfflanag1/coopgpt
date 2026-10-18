#!/usr/bin/env python3
"""Seal exact proof-input and reproducibility-artifact snapshots; local only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform

HERE=Path(__file__).resolve().parent
CAMP=HERE.parents[1]
INPUTS=(
    'CAMPAIGN_CONTRACT.txt',
    'lower/PROJECTIVE_SQUARE_ROOT_LOWER.txt',
    'root/PROJECTIVE_BOUNDED_COALITION_TAIL.txt',
    'lower/GENERAL_ARITY_CIRCUIT_LOWER.txt',
    'root/GENERAL_ARITY_TAIL_AND_DIMENSION_COROLLARY.txt',
)


def record(path,base):
    data=path.read_bytes()
    return {'path':str(path.relative_to(base)),'bytes':len(data),
            'sha256':hashlib.sha256(data).hexdigest()}


def main():
    output=HERE/'MANIFEST.json'
    build=json.loads((HERE/'BUILD_RESULT.json').read_text())
    replay=json.loads((HERE/'VERIFICATION_RESULT.json').read_text())
    assert build['status']==replay['status']=='PASS'
    assert replay['all_group_action_multiplicities_reconstructed']
    for name,digest in replay['input_hashes'].items():
        assert record(HERE/name,HERE)['sha256']==digest
    manifest={
        'task_started_utc':'2026-10-18T22:47:08Z',
        'sealed_utc':datetime.now(timezone.utc).isoformat(),
        'python':platform.python_version(),
        'dependencies':'Python standard library only',
        'source_inputs_at_seal':[record(CAMP/name,CAMP) for name in INPUTS],
        'owned_artifacts':[record(p,HERE) for p in sorted(HERE.iterdir())
                           if p.is_file() and p!=output],
        'result':{'group_actions':replay['group_actions'],'actual_profiles':replay['profiles_with_exact_primal_dual_value_checked'],
                  'weighted_rows':replay['rows_checked'],'cancelled_payment_coordinates':replay['payment_coordinates_cancelled'],
                  'K_coefficient':replay['K_coefficient'],'rhs':replay['rhs'],'status':'PASS'},
        'scope':'exact certificate engineering for accepted theorem; not a new bound',
        'external_calls_or_data':False,
    }
    output.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':str(output),'inputs':len(INPUTS),
                     'artifacts':len(manifest['owned_artifacts']),'result':manifest['result']},sort_keys=True))


if __name__=='__main__':
    main()
