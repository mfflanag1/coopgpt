#!/usr/bin/env python3
"""Recheck repaired local validator on isolated copied selected inputs."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import runpy
import tempfile

HERE=Path(__file__).resolve().parent
CAMP=HERE.parents[1]


def main():
    app=CAMP/'application';script=app/'verify_portable_metadata.py'
    sealed=json.loads((CAMP/'checks/portable_runner_validation/metadata_integrity_v2_PASS.json').read_text())
    verify=runpy.run_path(str(script))['verify']
    source_bytes={name:(app/name).read_bytes() for name in sealed['inputs_sha256']}
    assert all(hashlib.sha256(data).hexdigest()==sealed['inputs_sha256'][name] for name,data in source_bytes.items())
    outcomes={}
    with tempfile.TemporaryDirectory(prefix='v2_copied_inputs_',dir=HERE) as td:
        root=Path(td)
        def reset():
            for name,data in source_bytes.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        def json_read(name):return json.loads((root/name).read_text())
        def json_write(name,value):(root/name).write_text(json.dumps(value))
        hp='m100_may_metadata/report.json';fp='m100_may_footers/report.json'
        def challenge(name,change,expected):
            reset();change()
            try:verify(root)
            except ValueError as exc:
                assert expected in str(exc),(name,str(exc),expected)
                outcomes[name]={'status':'REJECTED','reason':str(exc)}
            else:raise AssertionError('Corrupt fixture accepted: '+name)
        reset();baseline=verify(root)
        assert {k:v for k,v in baseline.items() if k!='checked_utc'}=={k:v for k,v in sealed.items() if k!='checked_utc'}
        def forged_name():
            h,f=json_read(hp),json_read(fp);old=f['members'][0]['name'];fake='audit_only_name_absent_from_tar'
            assert all(e['name']!=fake for e in h['entries'])
            next(e for e in h['selected_members'] if e['name']==old)['name']=fake
            f['members'][0]['name']=fake;json_write(hp,h);json_write(fp,f)
        challenge('original_forged_selected_and_footer_name',forged_name,'Selected member not bound')
        def selected_offset():
            h=json_read(hp);h['selected_members'][0]['offset']+=512;json_write(hp,h)
        challenge('selected_offset_mismatch',selected_offset,'Selected member not bound')
        def selected_duplicate():
            h=json_read(hp);h['selected_members'].append(dict(h['selected_members'][0]));json_write(hp,h)
        challenge('duplicate_selected_name',selected_duplicate,'Duplicate selected member')
        def omitted_header():
            h=json_read(hp);h['entries'].pop(1);json_write(hp,h)
        challenge('omitted_interior_tar_entry',omitted_header,'Tar traversal offset disagreement')
        def end_offset():
            h=json_read(hp);h['next_offset']+=512;json_write(hp,h)
        challenge('wrong_reported_end_offset',end_offset,'Tar end position disagreement')
        def end_nonzero():
            h=json_read(hp);start=h['next_offset'];path=f'm100_may_metadata/range_{start}_512.bin'
            assert (root/path).read_bytes()==bytes(512)
            body=b'1'+bytes(511);(root/path).write_bytes(body)
            log='m100_may_metadata/requests.jsonl';rows=[json.loads(s) for s in (root/log).read_text().splitlines()]
            target=[r for r in rows if r.get('start')==start and r.get('length')==512]
            assert len(target)==1;target[0]['sha256']=hashlib.sha256(body).hexdigest()
            (root/log).write_text(''.join(json.dumps(r)+'\n' for r in rows))
        challenge('nonzero_end_marker_with_matching_body_hash',end_nonzero,'First tar end marker is not zero')
        def missing_footer():
            f=json_read(fp);f['members'].pop();json_write(fp,f)
        challenge('omitted_footer_record_leaves_ranges',missing_footer,'Unaccounted footer ranges')
        def duplicate_footer():
            f=json_read(fp);f['members'].append(dict(f['members'][0]));json_write(fp,f)
        challenge('duplicate_footer_member',duplicate_footer,'Duplicate footer member')
        def footer_size():
            f=json_read(fp);f['members'][0]['member_size']+=1;json_write(fp,f)
        challenge('footer_member_size_mismatch',footer_size,'Footer member-size disagreement')
        def archive_size():
            log='m100_may_metadata/requests.jsonl';rows=[json.loads(s) for s in (root/log).read_text().splitlines()]
            target=next(r for r in rows if r['kind'].startswith('dataset_'))
            prefix,size=target['content_range'].rsplit('/',1);target['content_range']=prefix+'/'+str(int(size)+1)
            (root/log).write_text(''.join(json.dumps(r)+'\n' for r in rows))
        challenge('one_range_archive_size_disagrees',archive_size,'Remote archive-size metadata disagreement')
        reset();assert verify(root)['status']=='PASS'
    # Verify originals remain unchanged after all copied-input challenges.
    assert all((app/name).read_bytes()==data for name,data in source_bytes.items())
    out={'status':'PASS','timestamp_utc':datetime.now(timezone.utc).isoformat(),
         'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
         'baseline_saved_output_matches_except_timestamp':True,
         'copied_selected_inputs':len(source_bytes),'dataset_requests':334,'dataset_bytes':468255,
         'negative_fixtures_rejected':len(outcomes),'fixtures':outcomes,
         'sealed_originals_unchanged':True,
         'scope':'Local byte/placement consistency only; no acquisition, footer-statistics decoding, outcome values, original documents or sparse wrappers.'}
    Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
