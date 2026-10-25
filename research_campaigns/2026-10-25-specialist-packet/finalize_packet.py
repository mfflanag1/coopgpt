from pathlib import Path
import json, hashlib, shutil, difflib, html, re, zipfile
from pypdf import PdfReader

P=Path(__file__).resolve().parent
C=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt/paper5/coalition_withholding')
R=Path('/Users/maxf/.local/state/claude-reviews/2026-10-25-specialist-packet-b391e230fa79/20261025-121932-6c417691')
packet=P/'packet'
ver=P/'verification'
reviews=P/'reviews'
reviews.mkdir(exist_ok=True)
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def write_json(f,x): f.write_text(json.dumps(x,indent=2)+'\n')
inputs=json.loads((ver/'CANONICAL_INPUT_HASHES.json').read_text())
assert all(sha(C/f)==h for f,h in inputs.items()), 'Canonical source changed during packaging'
assert (packet/'manuscript.tex').read_bytes()==(C/'manuscript.tex').read_bytes()
changed=[f for f,h in inputs.items() if sha(packet/f)!=h]
assert sorted(changed)==['review/PRIORITY_MATRIX.txt','specialist_brief.tex'], changed
for f in changed:
    diff=''.join(difflib.unified_diff((C/f).read_text().splitlines(keepends=True),(packet/f).read_text().splitlines(keepends=True),fromfile='canonical/'+f,tofile='packet/'+f))
    (reviews/(Path(f).name+'.patch')).write_text(diff)

export=json.loads((ver/'PDF_EXPORT.json').read_text())
for entry in export['files']:
    f=packet/entry['file']
    assert sha(f)==entry['pdf_sha256']
    assert sha(f.with_suffix('.tex'))==entry['source_sha256']
    reader=PdfReader(f)
    entry['pages']=len(reader.pages)
    txt='\n'.join(p.extract_text() for p in reader.pages)
    assert '??' not in txt
    if f.stem=='manuscript':
        assert len(reader.pages)==33
        assert '24 October 2026' in txt and 'Protected-leaf path rule' in txt
    else:
        assert len(reader.pages)==4
        assert '25 October 2026' in txt
        assert 'recorded unrestricted' not in txt
export['status']='PASS'
export['visual_review_record']='VISUAL_QA.json'
write_json(ver/'PDF_EXPORT.json',export)
write_json(ver/'VISUAL_QA.json',{
    'status':'PASS',
    'method':'All 37 pages rendered at 100 dpi and inspected by Codex in ten four-page contact sheets; brief page 2 and manuscript page 19 additionally inspected as individual images.',
    'manuscript_pages':33,'brief_pages':4,
    'checks':['No clipped equations or text','No overlapping text or tables','Page numbers and table of contents present','Graph theorem present in Section 6','Correct scientific and packet dates','No undefined-reference markers in extracted text'],
    'limitations':'Layout and export verification only; not mathematical proof or novelty certification.',
    'render_directory':'Local handoff verification/rendered; images omitted from portable ZIP to avoid duplication.'
})
compiler=json.loads((ver/'COMPILER_CHECK.json').read_text())
compiler['pdf_exported']=True
compiler['export_approval']='Explicit user reply: Yes, export current PDFs'
compiler['export_engine']='pdfTeX 1.40.29; three passes per standalone source'
compiler['export_result']='PDF_EXPORT.json'
write_json(ver/'COMPILER_CHECK.json',compiler)

for f in ['review.md','request.json','status.json']:
    shutil.copy2(R/f,reviews/f)
disposition="""READINESS REVIEW DISPOSITION — 25 October 2026
Scope: manuscript/brief/request fidelity, evidence boundaries, and packet readiness.
Independent reviewer: Claude Fable 5.1; raw review and source hashes retained.
This is not a new full proof audit or a historical-priority clearance.

1. Packet state and portable verification
Accepted as a clarity/completeness issue, not a proof defect. The earlier email
said 'manuscript' without explicitly saying PDF; standalone source was available.
User explicitly authorized export. Current 33-page manuscript and 4-page brief
are now generated from the packet sources, checked, and included. Fresh replay,
export and readiness records are included in verification_20261025/ and review/.
The old canonical 18 October PDF exports are excluded.

2. Internal baseline mistaken for literature
Accepted. Removed the brief's comparison to a 'recorded' s^(1/4) lower.
It now states only the proposed unrestricted square-root lower. No claim about
the best published lower is made. Two 'new' descriptors were also neutralized.

3. Contract and claim wording
Accepted the undefined-s and ambiguous coverage concerns. The email defines s
as protected coalition size, retains every-coalition coverage, and describes
the draft's bounds as proposed. Rejected the review's characterization of the
dimension-lower argument as simply 'unverified analytic work': prior internal
proof audits exist, and REVIEW_SCOPE identifies questions for human scrutiny.
Those audits still do not amount to independent human certification.

4. Funding normalization
Accepted. The email specifies K as TOTAL payments/output and (K-1) as the
supplement coefficient. The manuscript, brief and matrix already used this
normalization consistently.

5. Replay alignment
Accepted. Brief and README now name both graph checkers, recommend copying them
together into scratch, and warn of adjacent JSON writes. Finite diagnostics
remain expressly distinct from all-profile proof claims.

6. Presentation and bounded entry point
Accepted. Repaired run-together tokens in the priority matrix. The email gives
brief Section 3 and manuscript Section 5 as the initial lower-bound target.

Verification of repairs:
- Editorial diffs are retained beside this disposition.
- The manuscript and all mathematical source fragments are unchanged.
- All 78 source files at the canonical location remain unchanged.
- Fresh exact replays passed; graph diagnostic and recursion check passed.
- Built-in compilation passed; authorized PDF export and visual QA passed.
- Reviewer spot-checks are recorded only as limited internal checks. The reviewer
  did not execute code, inspect third-party originals or audit the full analytic
  dimension reduction or every graph cell. No broader clearance is inferred.

The raw review/request refer to their pre-repair snapshots. Current packet hashes
are in SHA256SUMS; the original review does not pretend to hash-bind the repairs.
Root verified these editorial repairs and the separate export/replay evidence.

Disposition: editorial findings resolved; packet ready for a human first look.
Human correctness and priority assessment remains outstanding. No message sent.
"""
(reviews/'READINESS_DISPOSITION.txt').write_text(disposition)
shutil.copy2(reviews/'READINESS_DISPOSITION.txt',packet/'review'/'READINESS_20261025.txt')
shutil.copy2(reviews/'review.md',packet/'review'/'READINESS_20261025_RAW.md')
shutil.copy2(P/'REVIEW_SCOPE.txt',packet/'review'/'REVIEW_SCOPE_20261025.txt')
for f in ['specialist_brief.tex.patch','PRIORITY_MATRIX.txt.patch']:
    shutil.copy2(reviews/f,packet/'review'/f)
write_json(packet/'review'/'READINESS_20261025_PROVENANCE.json',{
    'reviewer':'Claude Fable 5.1',
    'scope':'Pre-repair packet readiness; limited arithmetic spot-checks, not full proof or literature review',
    'raw_review_sha256':sha(reviews/'review.md'),
    'raw_request_sha256':sha(reviews/'request.json'),
    'repair_disposition':'READINESS_20261025.txt'
})
dest=packet/'verification_20261025'
dest.mkdir(exist_ok=True)
for f in ['CANONICAL_INPUT_HASHES.json','SOURCE_INTEGRITY.json','COMPILER_CHECK.json','PDF_EXPORT.json','VISUAL_QA.json']:
    shutil.copy2(ver/f,dest/f)
for d in ['replay-20261025','graph-replay']:
    shutil.copytree(ver/d,dest/d,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
(packet/'README.txt').write_text((packet/'README.txt').read_text().replace('DATED SPECIALIST SOURCE PACKET','DATED SPECIALIST REVIEW PACKET'))

report="""SPECIALIST REVIEW PREPARATION — 25 October 2026

READY FOR A HUMAN FIRST LOOK; HUMAN REVIEW NOT YET OBTAINED

Current documents:
- manuscript.pdf: 33 pages, scientific version 24 October 2026.
- specialist_brief.pdf: 4 pages, packet edition 25 October 2026.
- Corresponding standalone LaTeX sources, editorial fragments, exact checkers,
  priority matrix, focused review scope and scoped internal review records.

Completed:
- Confirmed all 133 entries of the inherited canonical SHA256SUMS manifest.
- Verified reconstruction from the editorial fragments and byte-identical main
  manuscript. All 78 copied canonical input files remain unchanged at source.
- Changed only two copied editorial files: specialist_brief.tex and the priority
  matrix. Their dated diffs are retained. No mathematical proof was changed.
- Both standalone sources passed the built-in compiler. With explicit user
  authorization, exported fresh PDFs with three pdfTeX passes. No undefined
  references, overfull-box warnings or other selected diagnostic issues.
- Rendered and inspected all 37 pages. Graph theorem is present in Section 6.
  The old 18 October canonical PDFs are excluded from this portable packet.
- Six exact replay suites passed, including the 34,440-row original-variable
  certificate. Graph replay: 625 exact algebraic profiles; recursion witness:
  canonical irrational case plus nine rational cases. These are finite
  diagnostics, not proofs for all profiles or sizes.
- Verified 107 unique labels and 94 resolved manuscript references.
- Completed cross-model readiness audit and verified editorial repairs.
  See reviews/READINESS_DISPOSITION.txt. It is not a new full proof certification.
- Prepared a concrete unsent request for Marina Núñez and a separate optional
  request for Yves Sprumont. Public institutional contacts and fields verified.
  Topic fit does not establish willingness or availability.

Portable package:
coalition-review-packet-20261025.zip contains current PDFs, sources, SHA256SUMS,
fresh replay/export records, the priority matrix and review disposition.
Local rendering images and duplicate LaTeX intermediates are omitted.
No third-party article PDFs are redistributed.

Scientific status:
Human review must assess the fixed-owner symmetry and payment ladder, the
arbitrary-rule dimension reduction, graph selector and boundary proof, and
exact original-source priority comparisons. Novelty remains unconfirmed.
The general arity-three sqrt(s/6)-to-3s^2 gap is unchanged. Later laminar and
irreversible-compensation obstructions remain separate research supplements.
Application work remains on hold.

Next step:
User review of the exact message and attachments, followed by explicit approval
for named-recipient outreach. Standing cross-model authorization does not cover
human email. No human outreach, external email draft, submission, publication or
Git action occurred. The canonical sources/repository remain unchanged.
Localhost links work only on this Mac; a reviewer needs the actual attachments.
"""
(P/'READINESS_REPORT.txt').write_text(report)

page=(P/'index.html').read_text()
page=page.replace('coalition-review-sources-20261025.zip','coalition-review-packet-20261025.zip')
page=page.replace('Download the dated source packet','Download the complete review packet')
old='<strong>Source packet prepared; human review has not been obtained.</strong> The canonical PDFs are 18 October exports and omit the 24 October graph addition. They are excluded. Both current LaTeX sources compile. Fresh PDF export awaits your answer to the explicit export question.'
new='<strong>Current PDFs and sources are ready; human review has not been obtained.</strong> The manuscript has 33 pages and the brief has four. Both were freshly exported with your approval and visually checked. The old 18 October exports are excluded; the current manuscript includes the graph theorem.'
assert old in page or new in page
page=page.replace(old,new)
page=page.replace('<a href="packet/manuscript.tex">Main manuscript</a>','<a href="packet/manuscript.pdf">Main manuscript PDF · 33 pages</a><br><a href="packet/manuscript.tex">LaTeX source</a>')
page=page.replace('<a href="packet/specialist_brief.tex">Specialist brief</a>','<a href="packet/specialist_brief.pdf">Specialist brief PDF · 4 pages</a><br><a href="packet/specialist_brief.tex">LaTeX source</a>')
page=page.replace('Corrected the instruction pointing to an outdated PDF; scientific scope unchanged.','Corrected version/replay instructions and an ambiguous internal-baseline comparison; scientific scope unchanged.')
page=re.sub(r'(<section id="request">.*?<pre>).*?(</pre>)',lambda m:m.group(1)+html.escape((P/'MARINA_REVIEW_REQUEST.txt').read_text())+m.group(2),page,flags=re.S)
page=page.replace('Both current standalone LaTeX files passed the desktop compiler; no PDF export is implied by that result.','Both current standalone LaTeX files passed the desktop compiler. The separately authorized export then produced current PDFs; all 37 rendered pages were inspected.')
page=page.replace('A focused cross-model readiness audit is in progress. Its final disposition will be linked before delivery.','A focused cross-model readiness audit is complete. Its editorial findings were checked and repaired. <a href="reviews/READINESS_DISPOSITION.txt">Read the disposition</a>; this was not a new full proof audit.')
page=page.replace('<a href="verification/COMPILER_CHECK.json">Current compilation</a>','<a href="verification/COMPILER_CHECK.json">Current compilation</a> · <a href="verification/PDF_EXPORT.json">PDF hashes and export</a> · <a href="verification/VISUAL_QA.json">Visual checks</a>')
page=page.replace('Fresh PDF export is awaiting your explicit approval under the earlier editor instruction. The source packet is usable now. Human outreach still needs authorization for the named recipient and exact message; no human message or external email draft has been created.','The packet and concrete message are ready for your review. Sending the request to Marina Núñez still needs your explicit authorization; no human message or external email draft has been created.')
assert 'awaits your answer' not in page and 'audit is in progress' not in page
(P/'index.html').write_text(page)

# Manifest and portable ZIP. Include files only, omitting caches and manifests-of-self.
files=sorted(f for f in packet.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='SHA256SUMS')
(packet/'SHA256SUMS').write_text(''.join(f'{sha(f)}  {f.relative_to(packet).as_posix()}\n' for f in files))
zpath=P/'coalition-review-packet-20261025.zip'
with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in files+[packet/'SHA256SUMS']:
        z.write(f,'coalition-review-20261025/'+f.relative_to(packet).as_posix())
with zipfile.ZipFile(zpath) as z:
    assert z.testzip() is None
    for f in files:
        key='coalition-review-20261025/'+f.relative_to(packet).as_posix()
        assert hashlib.sha256(z.read(key)).hexdigest()==sha(f)
write_json(ver/'PACKAGE_CHECK.json',{
    'status':'PASS','file':zpath.name,'files_including_manifest':len(files)+1,
    'bytes':zpath.stat().st_size,'sha256':sha(zpath),
    'all_entries_crc_checked':True,'all_content_hashes_checked':True,
    'canonical_input_hashes_rechecked':len(inputs),
    'mathematical_sources_changed':False,
    'pdfs':[e['file'] for e in export['files']],
    'excludes':'Archived 18 October PDF exports, third-party article PDFs, local renders, duplicate LaTeX intermediates'
})
print(json.dumps({'packet':str(zpath),'bytes':zpath.stat().st_size,'files':len(files)+1,'status':'PASS'},indent=2))

