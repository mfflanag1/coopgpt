"""Reseal source-access administration only; preserve all scientific/upload bytes."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent
h=lambda b:hashlib.sha256(b).hexdigest()
snapshot=json.loads((R/'qa/SOURCE_FOLLOWUP_PREDECESSOR_HASHES.json').read_text())
P=Path(snapshot['predecessor'])
previous=snapshot['files']
allowed={'SOURCE_PRIORITY.txt','PACKAGE_INDEX.json','READINESS.txt','README.txt','PACKAGE_MANIFEST.json','SHA256SUMS','FINAL_LOCAL_PACKAGE.zip'}
assert R!=P
assert all((P/n).is_file() and h((P/n).read_bytes())==v for n,v in previous.items())
assert all((R/n).is_file() and h((R/n).read_bytes())==v for n,v in previous.items() if n not in allowed)
protected={n:v for n,v in previous.items() if n.startswith(('source/','submission/')) or n.endswith('.pdf') or n=='SUBMISSION_FILES.zip'}
assert all(h((R/n).read_bytes())==v for n,v in protected.items())
with zipfile.ZipFile(R/'submission/LATEX_SOURCES.zip') as z:
 assert z.testzip() is None
 assert all(z.read(n)==(R/'source'/n).read_bytes() for n in z.namelist())
with zipfile.ZipFile(R/'submission/ESM_2.zip') as z:
 assert z.testzip() is None
 for n in ['manuscript.tex','supplement.tex']:assert z.read('current_sources/'+n)==(R/'source'/n).read_bytes()
 nested=json.loads(z.read('MANIFEST.json'))
 assert all(h(z.read(n))==v['sha256'] for n,v in nested.items())
 historical=sum(n.startswith('historical_checks/') for n in nested)
with zipfile.ZipFile(R/'SUBMISSION_FILES.zip') as z:
 assert z.testzip() is None
 assert all(z.read(p.name)==p.read_bytes() for p in (R/'submission').iterdir() if p.is_file())
 assert z.read('FILE_ROLES.txt')==(R/'admin/UPLOAD_MAP.txt').read_bytes()
qa={
 'date':'2026-10-18','scope':'Source/admin follow-up only; no recompilation, simulation or proof campaign.',
 'predecessor':str(P),'predecessor_files_verified':len(previous),'predecessor_all_hashes_unchanged':True,
 'allowed_changed_existing_files':sorted(allowed),'all_other_predecessor_files_exact':True,
 'protected_scientific_and_upload_files':protected,'protected_files_exact':True,
 'submission_zip_preserved_sha256':h((R/'SUBMISSION_FILES.zip').read_bytes()),
 'source_zip_members_match_current_source':True,'esm2_current_sources_exact':True,
 'esm2_all_nested_manifest_hashes_match':True,'esm2_historical_payloads':historical,
 'prior_qa_reused':['qa/CLEAN_BUILD_AND_PACKAGE.json','qa/PDF_CHECKS.json','qa/VISUAL_QA.txt','qa/SCIENCE_PRESERVATION.json'],
 'new_evidence':'qa/OCT18_FOLLOWUP_SOURCES.json','source_gaps_closed':[],
 'no_third_party_source_pdf_or_fulltext_extract_added':True,
 'fresh_build_or_scientific_review':False,'external_action':False}
(R/'qa/SOURCE_FOLLOWUP_PRESERVATION.json').write_text(json.dumps(qa,indent=2)+'\n')
def sums(entries):return ''.join(f'{h(b)}  {n}\n' for n,b in sorted(entries.items())).encode()
files={}
for p in R.rglob('*'):
 n=p.relative_to(R).as_posix()
 if not p.is_file() or n in {'FINAL_LOCAL_PACKAGE.zip','PACKAGE_MANIFEST.json','SHA256SUMS'} or n.startswith('qa/build/') or '__pycache__' in p.parts or p.suffix=='.png':continue
 files[n]=p.read_bytes()
manifest={n:{'sha256':h(b),'bytes':len(b)} for n,b in sorted(files.items())}
(R/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files['PACKAGE_MANIFEST.json']=(R/'PACKAGE_MANIFEST.json').read_bytes()
(R/'SHA256SUMS').write_bytes(sums(files))
files['SHA256SUMS']=(R/'SHA256SUMS').read_bytes()
with zipfile.ZipFile(R/'FINAL_LOCAL_PACKAGE.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in sorted(files.items()):
  info=zipfile.ZipInfo(n,(2026,10,18,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,b)
with zipfile.ZipFile(R/'FINAL_LOCAL_PACKAGE.zip') as z:
 assert z.testzip() is None
 assert set(z.namelist())==set(files)
 assert all(z.read(n)==b for n,b in files.items())
 assert all(h(z.read(n))==v['sha256'] for n,v in manifest.items())
for line in (R/'SHA256SUMS').read_text().splitlines():
 digest,n=line.split('  ',1)
 assert digest==h((R/n).read_bytes())
assert all(h((P/n).read_bytes())==v for n,v in previous.items())
assert all(h((R/n).read_bytes())==v for n,v in protected.items())
print(json.dumps({'manifest_payload_files':len(manifest),'archive_members':len(files),'all_manifest_hashes_and_archive_bytes_match':True,'frozen_predecessor_files':len(previous),'protected_files':len(protected),'esm2_historical_payloads':historical,'final_zip_sha256':h((R/'FINAL_LOCAL_PACKAGE.zip').read_bytes()),'submission_zip_sha256':h((R/'SUBMISSION_FILES.zip').read_bytes()),'main_pdf_sha256':h((R/'submission/manuscript.pdf').read_bytes()),'source_zip_sha256':h((R/'submission/LATEX_SOURCES.zip').read_bytes()),'source_gaps_closed':[]},indent=2))
