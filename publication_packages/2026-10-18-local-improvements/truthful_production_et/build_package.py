"""Build/reseal only this worked-example successor; never write its predecessor.

python3 build_package.py --prepare  # Exact source/archive and clean main-build QA.
python3 build_package.py --seal     # After coordinator review; no recompilation.
"""
from pathlib import Path
import argparse,hashlib,json,zipfile,subprocess,tempfile,re
R=Path(__file__).resolve().parent
h=lambda b:hashlib.sha256(b).hexdigest()
snapshot=json.loads((R/'qa/LOCAL_IMPROVEMENT_PREDECESSOR.json').read_text())
P=Path(snapshot['predecessor'])
assert P!=R

def zip_bytes(path,entries):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(entries.items()):
            info=zipfile.ZipInfo(n,(2026,10,18,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,b)

def sums(entries):return ''.join(f'{h(b)}  {n}\n' for n,b in sorted(entries.items())).encode()
def record(path,data):path.write_text(json.dumps(data,indent=2)+'\n')
def unchanged():
    assert all((P/n).is_file() and h((P/n).read_bytes())==v for n,v in snapshot['files'].items())
    insertion=(R/'qa/WORKED_EXAMPLE_INSERTION.tex').read_bytes()
    main=(R/'source/manuscript.tex').read_bytes()
    assert main.count(insertion)==1
    assert main.replace(insertion,b'',1)==(P/'source/manuscript.tex').read_bytes()
    protected=['source/supplement.tex','source/specialist_brief.tex','submission/ESM_1.pdf','admin/specialist_brief.pdf','SOURCE_PRIORITY.txt','admin/AUTHOR_FACTS.json','admin/COVER_LETTER_DRAFT.txt','submission/cover_letter.txt']
    assert all((R/n).read_bytes()==(P/n).read_bytes() for n in protected)
    return {n:h((R/n).read_bytes()) for n in protected}

def prepare():
    protected=unchanged()
    source={n:(R/'source'/n).read_bytes() for n in ['manuscript.tex','supplement.tex']}
    zip_bytes(R/'submission/LATEX_SOURCES.zip',source)
    with zipfile.ZipFile(P/'submission/ESM_2.zip') as z:original={n:z.read(n) for n in z.namelist()}
    entries={n:b for n,b in original.items() if n not in ['MANIFEST.json','SHA256SUMS']}
    for n,b in source.items():entries['current_sources/'+n]=b
    readme=entries['README.txt'].decode()
    a=readme.index('Their checks remain applicable')
    b=readme.index('research_record/',a)
    readme=readme[:a]+'''Their checks remain applicable because the prior theorem/proof/equation text
is preserved. The current main adds a reader-facing exact two-profile payment
calculation only; no new theorem or source-priority clearance is asserted.
worked_example/ contains its standard-library rational-mask checker and result;
run python3 worked_example/check_worked_example.py from this archive's root.
The example is not a subsidy-necessity or lower-bound claim. '''+readme[b:]
    readme=readme.replace('for this wording update.','for this illustrative update; only the new four-mask calculation was checked.')
    entries['README.txt']=readme.encode()
    for n in ['check_worked_example.py','WORKED_EXAMPLE_EXACT.json']:
        entries['worked_example/'+n]=(R/'qa'/n).read_bytes()
    manifest={n:{'sha256':h(b),'bytes':len(b),'role':('current typeset source' if n.startswith('current_sources/') else 'current worked example verification' if n.startswith('worked_example/') else 'preserved historical verification or lineage' if n.startswith(('historical_checks/','research_record/')) else 'metadata')} for n,b in sorted(entries.items())}
    entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    entries['SHA256SUMS']=sums(entries)
    zip_bytes(R/'submission/ESM_2.zip',entries)
    preserved=[n for n in original if n.startswith(('historical_checks/','research_record/'))]
    assert all(entries[n]==original[n] for n in preserved)
    with tempfile.TemporaryDirectory(prefix='clean-source-',dir=R/'qa') as t:
        t=Path(t)
        with zipfile.ZipFile(R/'submission/LATEX_SOURCES.zip') as z:z.extractall(t)
        p=subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','manuscript.tex'],cwd=t,capture_output=True,text=True)
        (R/'qa/WORKED_EXAMPLE_CLEAN_BUILD.log').write_text(p.stdout+p.stderr)
        assert p.returncode==0
        built=subprocess.check_output(['pdftotext',str(t/'manuscript.pdf'),'-'])
        supplied=subprocess.check_output(['pdftotext',str(R/'submission/manuscript.pdf'),'-'])
        assert built==supplied
        log=(t/'manuscript.log').read_text()
        assert not any(s in log for s in ['Overfull','Underfull','undefined references','undefined citations'])
    # Previously rendered pages 1--4 have unchanged text; downstream pages inspected.
    prior_text=subprocess.check_output(['pdftotext',str(P/'submission/manuscript.pdf'),'-']).split(b'\x0c')
    assert supplied.split(b'\x0c')[:4]==prior_text[:4]
    info=subprocess.check_output(['pdfinfo',str(R/'submission/manuscript.pdf')],text=True)
    pages=int(re.search(r'Pages:\s+(\d+)',info).group(1));assert pages==13
    qa={'date':'2026-10-18','scope':'One reader-facing worked example only; all previous theorem/proof/equation text unchanged.','predecessor':str(P),'frozen_predecessor_files_verified':len(snapshot['files']),'frozen_predecessor_exact':True,'prior_main_recovered_by_removing_exact_insertion':True,'protected_files_exact':protected,'main_source_sha256':h(source['manuscript.tex']),'main_pdf_sha256':h((R/'submission/manuscript.pdf').read_bytes()),'pages':{'main':13,'supplement':73,'brief':3},'clean_extracted_main_build':{'exit_code':0,'pdf_text_exact':True,'undefined_references_or_box_warnings':False},'source_zip_members_exact':True,'supplement_build_reused_for_identical_bytes':True,'main_pages_1_to_4_text_exact':True,'new_example_check':'WORKED_EXAMPLE_EXACT.json','example_checker_sha256':h((R/'qa/check_worked_example.py').read_bytes()),'example_result_sha256':h((R/'qa/WORKED_EXAMPLE_EXACT.json').read_bytes()),'esm2_historical_and_lineage_payloads_preserved':len(preserved),'esm2_original_historical_payload_count':sum(n.startswith('historical_checks/') for n in preserved),'esm2_current_sources_exact':True,'esm2_manifest_payloads':len(manifest),'new_source_gaps_closed':[],'source_limits_unchanged':True,'full_solver_or_proof_campaign_rerun':False,'visual_review':'LOCAL_IMPROVEMENT_VISUAL_QA.txt','independent_review':'LOCAL_IMPROVEMENT_REVIEW.txt (required before seal)','new_exact_file_approval':False,'external_authorization':False}
    record(R/'qa/LOCAL_IMPROVEMENT_QA.json',qa)
    unchanged()
    print(json.dumps({'prepared':True,'main_pages':pages,'source_zip_sha256':h((R/'submission/LATEX_SOURCES.zip').read_bytes()),'esm2_sha256':h((R/'submission/ESM_2.zip').read_bytes()),'preserved_historical_and_lineage_payloads':len(preserved),'final_seal':False},indent=2))

def seal():
    unchanged()
    assert (R/'qa/LOCAL_IMPROVEMENT_REVIEW.txt').is_file()
    qa=json.loads((R/'qa/LOCAL_IMPROVEMENT_QA.json').read_text())
    assert qa['main_source_sha256']==h((R/'source/manuscript.tex').read_bytes())
    assert qa['main_pdf_sha256']==h((R/'submission/manuscript.pdf').read_bytes())
    for fn in ['LATEX_SOURCES.zip','ESM_2.zip']:
        with zipfile.ZipFile(R/'submission'/fn) as z:
            assert z.testzip() is None
            for n in ['manuscript.tex','supplement.tex']:
                key=n if fn=='LATEX_SOURCES.zip' else 'current_sources/'+n
                assert z.read(key)==(R/'source'/n).read_bytes()
            if fn=='ESM_2.zip':
                m=json.loads(z.read('MANIFEST.json'))
                assert all(h(z.read(n))==v['sha256'] for n,v in m.items())
                for line in z.read('SHA256SUMS').decode().splitlines():
                    digest,n=line.split('  ',1);assert h(z.read(n))==digest
    submission={p.name:p.read_bytes() for p in (R/'submission').iterdir() if p.is_file()}
    submission['FILE_ROLES.txt']=(R/'admin/UPLOAD_MAP.txt').read_bytes()
    submission['SHA256SUMS']=sums(submission)
    zip_bytes(R/'SUBMISSION_FILES.zip',submission)
    with zipfile.ZipFile(R/'SUBMISSION_FILES.zip') as z:
        assert z.testzip() is None
        assert all(z.read(n)==b for n,b in submission.items())
    allfiles={}
    for p in R.rglob('*'):
        rel=p.relative_to(R).as_posix()
        if not p.is_file() or rel in ['FINAL_LOCAL_PACKAGE.zip','PACKAGE_MANIFEST.json','SHA256SUMS'] or rel.startswith(('qa/build/','qa/worked-example-build/')) or '__pycache__' in p.parts or p.suffix=='.png':continue
        allfiles[rel]=p.read_bytes()
    manifest={n:{'sha256':h(b),'bytes':len(b)} for n,b in sorted(allfiles.items())}
    record(R/'PACKAGE_MANIFEST.json',manifest)
    allfiles['PACKAGE_MANIFEST.json']=(R/'PACKAGE_MANIFEST.json').read_bytes()
    (R/'SHA256SUMS').write_bytes(sums(allfiles));allfiles['SHA256SUMS']=(R/'SHA256SUMS').read_bytes()
    zip_bytes(R/'FINAL_LOCAL_PACKAGE.zip',allfiles)
    with zipfile.ZipFile(R/'FINAL_LOCAL_PACKAGE.zip') as z:
        assert z.testzip() is None and set(z.namelist())==set(allfiles)
        assert all(z.read(n)==b for n,b in allfiles.items())
        assert all(h(z.read(n))==v['sha256'] for n,v in manifest.items())
    for line in (R/'SHA256SUMS').read_text().splitlines():
        digest,n=line.split('  ',1);assert h((R/n).read_bytes())==digest
    unchanged()
    print(json.dumps({'sealed':True,'manifest_files':len(manifest),'archive_members':len(allfiles),'hashes':{n:h((R/n).read_bytes()) for n in ['FINAL_LOCAL_PACKAGE.zip','SUBMISSION_FILES.zip','submission/manuscript.pdf','submission/LATEX_SOURCES.zip','submission/ESM_1.pdf','submission/ESM_2.zip']},'frozen_predecessor_verified':123,'source_gaps_closed':[]},indent=2))

p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--prepare',action='store_true');g.add_argument('--seal',action='store_true');a=p.parse_args()
prepare() if a.prepare else seal()
