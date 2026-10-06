#!/usr/bin/env python3
"""Reproduce this campaign's retained exact claims without SciPy or network."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parent;out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if out==root or root in out.parents:raise ValueError('Choose an output directory outside the source bundle')
manifest=json.loads((root/'verification'/'SOURCE_HASHES.json').read_text())
for relative,wanted in manifest.items():
 actual=hashlib.sha256((root/relative).read_bytes()).hexdigest()
 if actual!=wanted:raise ValueError('source changed: '+relative)
commands=[['binary_lattice/hierarchy_certificate.py','--output',str(out/'hierarchy')],
 ['binary_lattice/verify.py','binary_lattice/integer-1024-4-4.certificate.json','--controls','--output',str(out/'finite-above-two.json')],
 ['binary_lattice/verify.py','binary_lattice/symbolic-eight-row.certificate.json','--controls','--output',str(out/'eight-row.json')],
 ['verify_small_ball.py','--output',str(out/'small-ball.json')],
 ['verify_failed_upper.py','--output',str(out/'failed-upper.json')]]
report=[]
for i,args in enumerate(commands):
 command=[sys.executable,'-B','-O']+args
 r=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=120)
 (out/f'check-{i}.stdout.txt').write_text(r.stdout);(out/f'check-{i}.stderr.txt').write_text(r.stderr)
 report.append({'argv':command,'returncode':r.returncode})
 if r.returncode:raise RuntimeError('Check failed: '+args[0])
(out/'SUMMARY.json').write_text(json.dumps({'status':'ALL_RETAINED_EXACT_CHECKS_PASS','source_hashes_verified':len(manifest),'checks':report,'limitation':'Finite checks do not establish the all-parameter theorem or historical novelty; see the complete proofs and review records.'},indent=2)+'\n')
print('PASS: source hashes and all5 exact check commands; results in',out)
