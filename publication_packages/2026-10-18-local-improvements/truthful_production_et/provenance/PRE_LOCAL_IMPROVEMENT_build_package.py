from pathlib import Path
import hashlib, json, zipfile, shutil, subprocess, tempfile, re, difflib
R=Path(__file__).resolve().parent
ACCEPTED=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt/paper5/truthful_cooperation/author_update_2026-10-17')
PRIOR=ACCEPTED.parent/'submission_prep_2026-10-17'
def digest(b): return hashlib.sha256(b).hexdigest()
def zip_bytes(path,entries):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(entries.items()):
   info=zipfile.ZipInfo(n,(2026,10,18,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,b)
def sums(entries): return ''.join(f'{digest(v)}  {k}\n' for k,v in sorted(entries.items())).encode()
source_names=['manuscript.tex','supplement.tex']
source={n:(R/'source'/n).read_bytes() for n in source_names}
zip_bytes(R/'submission/LATEX_SOURCES.zip',source)
entries={}
with zipfile.ZipFile(PRIOR/'ESM_2.zip') as z:
 for n in z.namelist():
  if not n.endswith('/'): entries['historical_checks/'+n]=z.read(n)
for n,b in source.items(): entries['current_sources/'+n]=b
entries['research_record/manuscript_2026-10-07.tex']=(PRIOR/'research_record/manuscript_2026-10-07.tex').read_bytes()
entries['README.txt']='''ONLINE RESOURCE 2 — Sharp subsidies for truthful production and network cooperation
Economic Theory submission candidate; NOT SUBMITTED
Author: Maxwell Flanagan; no affiliation
Correspondence: maxwell.flanagan@gmail.com
Location: New York City, United States
Original AI assistance: OpenAI Codex (historical model version not recorded).
Subsequent internal review: Anthropic Claude. The author personally reviewed
the manuscripts, proofs, code and results. No external submission is authorized.

current_sources/ contains the exact main/supplement sources of the final ET
candidate PDFs. historical_checks/verification/ preserves all 40 files from
the accepted October17 ESM_2.zip byte-for-byte. Those source snapshots, dated
logs and identity placeholders are historical verification inputs and are NOT
the sources of the current PDFs. Their checks remain applicable because the
scientific blocks of the final candidate are unchanged; only contact/declaration/AI-disclosure
wording, an explicit ABV author-version attribution and associated layout changed. research_record/ provides the original
October7 source referenced by Online Resource1, not another submission version.

Python3.10.14 standard-library checks previously passed five central jobs, five
portfolio jobs and the architecture transcription check. They were not rerun
for this wording update. See historical_checks/verification/README_CURRENT.txt
for commands from that directory in a disposable copy. Historical runners may
write adjacent result files. Exact finite checks are corroboration, not formal
verification or a proof of asymptotic claims. No external dataset is required.

This archive contains no retrieved third-party full-text articles. The source
and verification files are provided locally for review; no public deposit or
reuse license is inferred or selected by this preparation.
'''.encode()
manifest={n:{'sha256':digest(b),'bytes':len(b),'role':('current typeset source' if n.startswith('current_sources/') else 'historical fixed verification or lineage' if n.startswith(('historical_checks/','research_record/')) else 'metadata')} for n,b in sorted(entries.items())}
entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
entries['SHA256SUMS']=sums(entries)
zip_bytes(R/'submission/ESM_2.zip',entries)
shutil.copy2(R/'admin/COVER_LETTER_DRAFT.txt',R/'submission/cover_letter.txt')
# Clean extracted-source build and PDF text comparisons. This is typesetting QA,
# not a fresh mathematical verification campaign.
qa={'source_zip_test':None,'esm2_test':None,'source_builds':{},'historical_payload_files':40}
for fn,k in [('LATEX_SOURCES.zip','source_zip_test'),('ESM_2.zip','esm2_test')]:
 with zipfile.ZipFile(R/'submission'/fn) as z: qa[k]=z.testzip()
with tempfile.TemporaryDirectory(prefix='truthful-et-build-') as td:
 td=Path(td)
 with zipfile.ZipFile(R/'submission/LATEX_SOURCES.zip') as z:z.extractall(td)
 for n,pdf in [('manuscript','manuscript.pdf'),('supplement','ESM_1.pdf')]:
  proc=subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error',n+'.tex'],cwd=td,capture_output=True,text=True)
  (R/'qa'/('clean-build-'+n+'.txt')).write_text(proc.stdout+proc.stderr)
  assert proc.returncode==0
  extracted=subprocess.check_output(['pdftotext',str(td/(n+'.pdf')),'-'],text=True)
  supplied=subprocess.check_output(['pdftotext',str(R/'submission'/pdf),'-'],text=True)
  assert extracted==supplied
  (R/'qa'/(n+'.txt')).write_text(supplied)
  info=subprocess.check_output(['pdfinfo',str(R/'submission'/pdf)],text=True)
  qa['source_builds'][n]={'exit_code':0,'pdf_text_exact':True,'pages':int(re.search(r'Pages:\s+(\d+)',info).group(1)),'sha256':digest((R/'submission'/pdf).read_bytes())}
qa['esm2_current_sources_exact']=all(entries['current_sources/'+n]==source[n] for n in source)
with zipfile.ZipFile(PRIOR/'ESM_2.zip') as z:qa['historical_payload_exact']=all(entries['historical_checks/'+n]==z.read(n) for n in z.namelist())
assert qa['historical_payload_exact']
(R/'qa/CLEAN_BUILD_AND_PACKAGE.json').write_text(json.dumps(qa,indent=2)+'\n')
# Current release integrity evidence is written before sealing the package.
PRE=Path('/Users/maxf/Documents/ECON/artifacts/submission_packages_2026-10-17_author_completed/truthful_production_et')
previous=json.loads((R/'qa/OCT18_FROZEN_PREDECESSOR_HASHES.json').read_text())
pre_exact=all((PRE/n).is_file() and digest((PRE/n).read_bytes())==v for n,v in previous.items())
assert pre_exact
parity={'checked_at':'2026-10-18','esm2_manifest_payloads':len(manifest),'esm2_all_manifest_hashes_match':all(digest(entries[n])==v['sha256'] for n,v in manifest.items()),'esm2_historical_payloads_preserved':40,'current_sources_exact':qa['esm2_current_sources_exact'],'prior_full_proof_campaign_rerun':False,'scope':'Current exact-source, preserved historical payload and frozen predecessor checks'}
assert parity['esm2_all_manifest_hashes_match']
(R/'qa/ARCHIVE_PARITY.json').write_text(json.dumps(parity,indent=2)+'\n')
release={'date':'2026-10-18','single_source_change':'Its Theorem 1 proves -> Theorem 1 of that author version proves','scientific_change':False,'mathematical_source_check':'SCIENCE_PRESERVATION.json proves full-source equality after reversing the sole approved phrase','frozen_predecessor_files_verified':len(previous),'frozen_predecessor_exact':pre_exact,'supplement_pdf_exact_to_predecessor':(R/'submission/ESM_1.pdf').read_bytes()==(PRE/'submission/ESM_1.pdf').read_bytes(),'brief_pdf_exact_to_predecessor':(R/'admin/specialist_brief.pdf').read_bytes()==(PRE/'admin/specialist_brief.pdf').read_bytes(),'clean_source_builds':qa['source_builds'],'historical_payload_exact':qa['historical_payload_exact'],'new_source_gaps_closed':[],'retained_gaps':['Cao full original','Owen1975 full original','ABV publisher-final'],'source_gap_evidence':'OCT18_SOURCE_EVIDENCE.json','fresh_mathematical_simulation_or_proof_campaign':False,'external_action_authorized':False,'exact_new_file_approval':False,'layout':'VISUAL_QA.txt','no_retrieved_article_or_fulltext_extract_in_submission_files':True}
assert release['supplement_pdf_exact_to_predecessor'] and release['brief_pdf_exact_to_predecessor']
(R/'qa/OCT18_RELEASE_QA.json').write_text(json.dumps(release,indent=2)+'\n')
# Freeze submitted-role files separately from coordinator/admin material.
submission={p.name:p.read_bytes() for p in (R/'submission').iterdir() if p.is_file()}
submission['FILE_ROLES.txt']=(R/'admin/UPLOAD_MAP.txt').read_bytes()
submission['SHA256SUMS']=sums(submission)
zip_bytes(R/'SUBMISSION_FILES.zip',submission)
# Exclude TeX scratch files and captures. Keep inspectable audit JSON/text.
allfiles={}
for p in R.rglob('*'):
 rel=p.relative_to(R).as_posix()
 if not p.is_file() or rel in {'FINAL_LOCAL_PACKAGE.zip','PACKAGE_MANIFEST.json','SHA256SUMS'} or rel.startswith('qa/build/') or '__pycache__' in p.parts or p.suffix=='.png':continue
 allfiles[rel]=p.read_bytes()
manifest={n:{'sha256':digest(b),'bytes':len(b)} for n,b in sorted(allfiles.items())}
(R/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
allfiles['PACKAGE_MANIFEST.json']=(R/'PACKAGE_MANIFEST.json').read_bytes()
(R/'SHA256SUMS').write_bytes(sums(allfiles))
allfiles['SHA256SUMS']=(R/'SHA256SUMS').read_bytes()
zip_bytes(R/'FINAL_LOCAL_PACKAGE.zip',allfiles)
with zipfile.ZipFile(R/'FINAL_LOCAL_PACKAGE.zip') as z:assert z.testzip() is None
print(json.dumps({'files':len(allfiles),'final_zip_sha256':digest((R/'FINAL_LOCAL_PACKAGE.zip').read_bytes()),'submission_zip_sha256':digest((R/'SUBMISSION_FILES.zip').read_bytes()),'qa':qa},indent=2))
