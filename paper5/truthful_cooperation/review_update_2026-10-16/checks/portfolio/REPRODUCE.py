"""Run the curated exact verifiers; no dependencies beyond standard Python."""
from pathlib import Path
import subprocess,sys,json,hashlib

base=Path(__file__).resolve().parent
jobs=[('verify_owner_sqrt.py','OWNER_SQRT_CHECKS.json'),
      ('verify_finite_mask_v2.py','FINITE_MASK_V2_CHECKS.json'),
      ('verify_vcap_mask.py','VCAP_MASK_CHECKS.json'),
      ('verify_dimension_sqrt.py','DIMENSION_SQRT_CHECKS.json'),
      ('verify_compressed_dimension.py','COMPRESSED_DIMENSION_CHECKS.json')]
rows=[]
for script,result in jobs:
    run=subprocess.run([sys.executable,'-B','-O',str(base/script)],text=True,capture_output=True)
    if run.returncode:
        raise RuntimeError(f'{script} failed: {run.stdout}\n{run.stderr}')
    report=json.loads((base/result).read_text())
    if report.get('status')!='pass':
        raise RuntimeError(f'{result}: status is not pass')
    rows.append({'script':script,'result':result,'status':'pass',
                 'script_sha256':hashlib.sha256((base/script).read_bytes()).hexdigest(),
                 'result_sha256':hashlib.sha256((base/result).read_bytes()).hexdigest()})
    print(f'{script}: PASS',flush=True)
out={'status':'pass','python':sys.version,'optimized_checks':True,'results':rows}
(base/'REPRODUCTION_RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
