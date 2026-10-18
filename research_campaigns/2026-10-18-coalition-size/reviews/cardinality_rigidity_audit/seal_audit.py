#!/usr/bin/env python3
"""Record exact source/artifact snapshots for the bounded independent audit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE=Path(__file__).resolve().parent
CAMP=HERE.parents[1]
INPUTS=(
    'CAMPAIGN_CONTRACT.txt',
    'constructive/ADAPTIVE_CARDINALITY_RIGIDITY_EXTENSION.txt',
    'constructive/ADAPTIVE_GLOBAL_MIXTURE_RIGIDITY_BARRIER.txt',
    'reviews/cross_profile_duality/FINITE_AND_ALL_PROFILE_DUAL.txt',
    'reviews/cross_profile_duality/ATTACK_AND_GATE.txt',
)


def record(path,base):
    data=path.read_bytes()
    return {'path':str(path.relative_to(base)),'bytes':len(data),
            'sha256':hashlib.sha256(data).hexdigest()}


def main():
    output=HERE/'AUDIT_MANIFEST.json'
    checks={}
    for name in ('audit_cardinality.json','audit_dual_cycles.json'):
        data=json.loads((HERE/name).read_text())
        assert data['status']=='PASS'
        checks[name]={'status':data['status'],'sha256':record(HERE/name,HERE)['sha256']}
    result={
        'task_started_utc':'2026-10-18T22:35:36Z',
        'sealed_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'independent architecture proof audit and finite-dual reductions; no funding exponent improvement',
        'inputs_at_seal':[record(CAMP/name,CAMP) for name in INPUTS],
        'owned_artifacts':[record(path,HERE) for path in sorted(HERE.iterdir())
                           if path.is_file() and path != output],
        'executed_checks':checks,
        'external_data_retrieved':False,
        'external_review_status':'root coordinates opposite-model review; none launched recursively',
    }
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'manifest':str(output),'inputs':len(result['inputs_at_seal']),
                      'artifacts':len(result['owned_artifacts']),'status':'sealed'}))


if __name__=='__main__':
    main()
