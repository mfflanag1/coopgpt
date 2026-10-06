#!/usr/bin/env python3
"""Replay exact weighted-profile certificates from hash-checked sources."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,tempfile,shutil
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=Path('validation/sharp_replay'))
    args=ap.parse_args();src=Path(__file__).resolve().parent/'sharp'
    manifest=json.loads((src/'SOURCE_HASHES.json').read_text())
    require(set(manifest)=={'poisson_certificate.py','verify.py'},'Manifest scope')
    for name,wanted in manifest.items():
        require(hashlib.sha256((src/name).read_bytes()).hexdigest()==wanted,'Source mismatch: '+name)
    out=args.output.resolve()
    require(out!=src and src not in out.parents,'Choose output outside source directory')
    with tempfile.TemporaryDirectory(prefix='coopgt-sharp-') as tmp:
        scratch=Path(tmp)/'result'
        proc=subprocess.run([sys.executable,'-B','-O',str(src/'poisson_certificate.py'),
                             '--output',str(scratch)],capture_output=True,text=True,timeout=120)
        require(proc.returncode==0,'Certificate replay failed: '+proc.stderr)
        result=json.loads((scratch/'VERIFICATION.json').read_text())
        require(result['status']=='EXACT_WEIGHTED_PROFILE_CERTIFICATES_PASS','Verification status')
        require(result['case_count']==24 and result['corruptions_rejected']==168,'Verification coverage')
        require(result['generator_sha256']==manifest['poisson_certificate.py'],'Generator provenance')
        require(result['verifier_sha256']==manifest['verify.py'],'Verifier provenance')
        shutil.copytree(scratch,out,dirs_exist_ok=True)
        (out/'stdout.txt').write_text(proc.stdout);(out/'stderr.txt').write_text(proc.stderr)
    print('PASS:24 exact weighted-profile certificates and168 corruption rejections; '+str(out))
if __name__=='__main__':main()
