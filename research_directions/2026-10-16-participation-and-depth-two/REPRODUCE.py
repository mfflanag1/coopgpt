"""Portable exact corroboration. Discovery optimizers are not used."""
from pathlib import Path
import subprocess,sys,json,hashlib
base=Path(__file__).resolve().parent
baseline=base/'application/baseline'
jobs=[
 ('participation-certificates',baseline/'verify_floor_certificates.py',sorted(baseline.glob('floor-*.json.gz'))),
 ('domain-guards',baseline/'check_domain_guards.py',[]),
 ('continuous-rule',base/'application/continuous/verify_continuous_rule.py',[]),
 ('residual-and-nested',base/'forest/verify_residual.py',[]),
 ('public-values',base/'application/weighted/verify_public_values.py',[]),
]
outdir=base/'checks';outdir.mkdir(exist_ok=True)
rows=[]
for name,script,args in jobs:
    command=[sys.executable,'-B','-O',str(script)]+[str(p) for p in args]
    result=subprocess.run(command,cwd=script.parent,text=True,capture_output=True)
    (outdir/(name+'.txt')).write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(name+' failed; inspect checks/'+name+'.txt')
    rows.append({'name':name,'status':'pass','script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((outdir/(name+'.txt')).read_bytes()).hexdigest()})
    print(name+': PASS',flush=True)
(base/'REPRODUCTION_RESULT.json').write_text(json.dumps({'status':'pass','python':sys.version,'optimized_python':True,'jobs':rows},indent=2)+'\n')
