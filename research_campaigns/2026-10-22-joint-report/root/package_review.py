"""Build a focused first-party review bundle; sends nothing externally."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
import json

R=Path(__file__).resolve().parents[1]
paths=[
'THEOREM_REVIEW_BRIEF.txt','REVIEW_PACKET_CONTENTS.txt',
'root/CONSOLIDATION_PLAN.txt',
'CONTRACT.txt',
'inputs/previous_full_envelope_proof.txt',
'inputs/previous_report.txt',
'theory/selection_cap_two_analysis.txt',
'theory/selection_power_regularizer_extension.txt',
'theory/selection_efficient_core_envelope_barrier.txt',
'theory/selection_seed_barrier_below_two.txt',
'theory/composition_cap_audit.txt',
'theory/selection_cap_two_check.py','theory/selection_cap_two_check.json',
'root/power_certificate_check.py','root/power_certificate_check.json',
'theory/selection_seed_barrier_check.py','theory/selection_seed_barrier_check.json',
'reviews/ROOT_VERIFICATION.txt','reviews/FINAL_POWER_AND_RESUME_AUDIT.txt',
'sources/root_primary_comparisons.txt','theory/dual_priority_comparison.txt',
'theory/dual_priority_addendum.txt',
]
focused_replay='''FOCUSED THEOREM REPLAY
From the extracted packet root, using Python3 and only its standard library:
 python3 theory/selection_cap_two_check.py
 python3 root/power_certificate_check.py
 python3 theory/selection_seed_barrier_check.py
The first two check scalar optimality certificates conditional on the
written row-mixture proof. The third checks the efficient-core/low-seed
pool argument. They do not enumerate the huge row family or prove novelty.
The full campaign has additional replays; they are not required here.
'''
contents={name:(R/name).read_bytes() for name in paths}
contents['REPRODUCE.txt']=focused_replay.encode()
manifest={'scope':'Focused first-party theorem packet. No outreach performed. Full campaign provenance and other checks remain outside this bundle.',
          'files':[{'path':name,'sha256':sha256(data).hexdigest(),'bytes':len(data)} for name,data in sorted(contents.items())]}
manifest_bytes=(json.dumps(manifest,indent=2)+'\n').encode()
(R/'REVIEW_PACKET_MANIFEST.json').write_bytes(manifest_bytes)
contents['PACKET_MANIFEST.json']=manifest_bytes
out=R/'FIXED_CAP_REVIEW_PACKET.zip'
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(contents.items()): z.writestr(name,data)
with ZipFile(out) as z:
    assert z.testzip() is None
    m=json.loads(z.read('PACKET_MANIFEST.json'))
    for x in m['files']:
        assert sha256(z.read(x['path'])).hexdigest()==x['sha256']
print(json.dumps({'file':str(out),'entries':len(contents),'bytes':out.stat().st_size,
                  'sha256':sha256(out.read_bytes()).hexdigest(),'integrity':'PASS'}))
