#!/usr/bin/env python3
"""Bounded independent checks; temporary inputs are copies, no acquisition."""
from datetime import datetime, timezone
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import tempfile

HERE=Path(__file__).resolve().parent
CAMP=HERE.parents[1]


def pay(b):
    x,z=b
    return x,z+(x if x>=Q(1,2) else 0)


def main():
    grid=[Q(0),Q(1,4),Q(2,5),Q(49,100),Q(1,2),Q(51,100),Q(3,4),Q(1)]
    profiles=list(product(grid,repeat=2));coals=[(0,),(1,),(0,1)]
    coverage=0;comparisons=0
    for b in profiles:
        y=pay(b)
        assert all(v>=0 for v in y) and sum(y)<=2*sum(b)
        for c in coals:
            assert sum(y[i] for i in c)>=sum(b[i] for i in c);coverage+=1
    for lo in profiles:
        for hi in profiles:
            for c in coals:
                if any(hi[i]!=lo[i] for i in range(2) if i not in c):continue
                if any(hi[i]<lo[i] for i in c):continue
                assert sum(pay(hi)[i]-pay(lo)[i] for i in c)>=sum(hi[i]-lo[i] for i in c)
                comparisons+=1
    lo=(Q(2,5),Q(1));hi=(Q(1,2),Q(1))
    norm=lambda b:tuple(v*sum(b)/sum(pay(b)) for v in pay(b))
    assert norm(lo)[0]==Q(2,5) and norm(hi)[0]==Q(3,8)
    assert norm(hi)[0]-norm(lo)[0]==-Q(1,40)
    assert norm(hi)[0]<hi[0]  # normalized singleton coverage also fails

    app=CAMP/'application'; script=app/'verify_portable_metadata.py'
    sealed=json.loads((CAMP/'checks/portable_runner_validation/metadata_integrity_PASS.json').read_text())
    verify=runpy.run_path(str(script))['verify']
    result={'normalization':{'status':'PASS','profiles':len(profiles),'coverage_checks':coverage,
                            'full_OUT_checks':comparisons,'before':'2/5','after':'3/8','drop':'-1/40',
                            'note':'Finite checks supplement the direct all-real proof; no priority assertion.'}}
    with tempfile.TemporaryDirectory(prefix='copied_inputs_',dir=HERE) as td:
        root=Path(td)
        for name,expected in sealed['inputs_sha256'].items():
            src=app/name;assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
            dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        baseline=verify(root)
        assert {k:v for k,v in baseline.items() if k!='checked_utc'}=={k:v for k,v in sealed.items() if k!='checked_utc'}
        damaged=root/'m100_may_metadata/range_0_512.bin';old=damaged.read_bytes()
        damaged.write_bytes(bytes([old[0]^1])+old[1:])
        try:verify(root)
        except ValueError as exc: corruption_error=str(exc)
        else:raise AssertionError('Byte corruption was accepted')
        damaged.write_bytes(old)
        hp=root/'m100_may_metadata/report.json';fp=root/'m100_may_footers/report.json'
        oldh,oldf=hp.read_bytes(),fp.read_bytes()
        h,f=json.loads(oldh),json.loads(oldf)
        original=f['members'][0]['name'];replacement='audit_only_name_absent_from_tar'
        assert all(e['name']!=replacement for e in h['entries'])
        next(e for e in h['selected_members'] if e['name']==original)['name']=replacement
        f['members'][0]['name']=replacement
        hp.write_text(json.dumps(h));fp.write_text(json.dumps(f))
        try:
            verify(root);false_name_accepted=True;false_name_error=None
        except (ValueError,KeyError,StopIteration) as exc:
            false_name_accepted=False;false_name_error=str(exc)
        result['metadata']={'baseline':'PASS','copied_selected_inputs':len(sealed['inputs_sha256']),
                            'dataset_bytes':baseline['dataset_body_bytes'],
                            'request_count':baseline['dataset_range_requests'],
                            'corrupt_byte_rejected':corruption_error,
                            'nonexistent_selected_tar_name_accepted':false_name_accepted,
                            'nonexistent_name_error':false_name_error,
                            'scope':'Temporary copy only; no network, acquisition, Parquet decoding, footer statistics, original docs or sparse wrappers.'}
    result.update(timestamp_utc=datetime.now(timezone.utc).isoformat(),
                  script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                  audit_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
