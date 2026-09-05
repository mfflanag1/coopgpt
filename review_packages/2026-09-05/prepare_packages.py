"""Build, freeze, and test the three review packages from a clean extraction."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile

BASE=Path(__file__).resolve().parent
PACKAGES=('stable_core','asymptotic','assignment')
PYTHON=sys.executable
LATEXMK=shutil.which('latexmk') or '/Library/TeX/texbin/latexmk'
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def include(path,root):
    relative=path.relative_to(root)
    if any(part in ('__pycache__','.venv','.git','qa') for part in relative.parts):return False
    if path.suffix in ('.aux','.fdb_latexmk','.fls','.synctex','.gz','.log','.bbl','.blg','.out','.toc','.pyc'):return False
    if path.suffix=='.pdf' and relative.as_posix()!='output/pdf/manuscript.pdf':return False
    return path.is_file()

def build(name):
    root=BASE/name
    for required in ('manuscript.tex','README.md','CLAIMS_AND_SOURCES.md','REVIEW_REQUEST.md','PROVENANCE.json','verification/run_checks.py'):
        require((root/required).is_file(),name+': missing '+required)
    (root/'output/pdf').mkdir(parents=True,exist_ok=True)
    (root/'build.sh').write_text('#!/usr/bin/env bash\nset -euo pipefail\ncd "$(dirname "$0")"\nmkdir -p output/pdf\nlatexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf manuscript.tex\n')
    os.chmod(root/'build.sh',0o755)
    (root/'.gitignore').write_text('__pycache__/\n*.pyc\noutput/pdf/*.aux\noutput/pdf/*.fdb_latexmk\noutput/pdf/*.fls\noutput/pdf/*.log\noutput/pdf/*.out\noutput/pdf/*.toc\n')
    command=[LATEXMK,'-pdf','-interaction=nonstopmode','-halt-on-error','-outdir=output/pdf','manuscript.tex']
    result=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=120)
    logs=BASE/'build_records';logs.mkdir(exist_ok=True)
    (logs/(name+'.log')).write_text(result.stdout+result.stderr)
    require(result.returncode==0,name+': TeX build failed')
    log=(root/'output/pdf/manuscript.log').read_text()
    issues=[line for line in log.splitlines() if any(x in line for x in ('Overfull','Underfull','undefined','Rerun to get','There were undefined'))]
    require(not issues,name+': unresolved build issues '+repr(issues))
    return {'package':name,'build':'PASS','pdf_sha256':sha(root/'output/pdf/manuscript.pdf'),'source_sha256':sha(root/'manuscript.tex')}

def freeze_and_replay(name):
    root=BASE/name
    manifest=root/'SHA256SUMS'
    files=[p for p in sorted(root.rglob('*')) if include(p,root) and p.name!='SHA256SUMS']
    manifest.write_text(''.join(f'{sha(p)}  {p.relative_to(root).as_posix()}\n' for p in files))
    archives=BASE/'archives';archives.mkdir(exist_ok=True)
    archive=archives/(name+'_review.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(files+[manifest]):
            name_in_zip=name+'/'+path.relative_to(root).as_posix()
            info=zipfile.ZipInfo(name_in_zip,(2026,9,5,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100755 if path.name=='build.sh' else 0o100644)<<16
            z.writestr(info,path.read_bytes())
    extraction=BASE/'clean_replays'/name
    require(not extraction.exists(),'clean replay destination already exists '+name)
    extraction.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:z.extractall(extraction)
    fresh=extraction/name
    for line in (fresh/'SHA256SUMS').read_text().splitlines():
        expected,relative=line.split('  ',1)
        require(sha(fresh/relative)==expected,'archive checksum mismatch '+relative)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
    start=time.monotonic()
    result=subprocess.run([PYTHON,'verification/run_checks.py'],cwd=fresh,capture_output=True,text=True,env=env,timeout=900)
    records=BASE/'build_records'
    (records/(name+'_clean_replay.log')).write_text(result.stdout+result.stderr)
    require(result.returncode==0,name+': clean extraction replay failed: '+result.stderr[-2000:])
    return {'package':name,'status':'PASS','command':'python verification/run_checks.py','python':PYTHON,'clean_extraction':str(fresh),'seconds':round(time.monotonic()-start,3),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'files':len(files)+1}

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'build'
    if mode=='build':
        with ThreadPoolExecutor(max_workers=3) as executor:records=list(executor.map(build,PACKAGES))
        (BASE/'build_records/builds.json').write_text(json.dumps(records,indent=2)+'\n')
    elif mode=='freeze':
        with ThreadPoolExecutor(max_workers=3) as executor:records=list(executor.map(freeze_and_replay,PACKAGES))
        (BASE/'build_records/clean_replays.json').write_text(json.dumps(records,indent=2)+'\n')
    else:raise RuntimeError('unknown mode')
    print(json.dumps(records,indent=2))
