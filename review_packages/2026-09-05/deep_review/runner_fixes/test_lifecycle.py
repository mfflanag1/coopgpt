"""Exercise startup dependency failures and real scientific rejection after fixes."""
from pathlib import Path
import json, os, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/'test_results'
RESULTS.mkdir(exist_ok=True)
PROBES=Path(tempfile.mkdtemp(prefix='probes-',dir=ROOT))
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
def require(ok,message):
    if not ok: raise RuntimeError(message)
def setup(name,label):
    dst=PROBES/label/name/'verification'
    shutil.copytree(ROOT/name/'verification',dst,ignore=shutil.ignore_patterns('results','__pycache__'))
    output=dst/'results'/('verification_summary.json' if name=='assignment' else 'verification.json')
    output.parent.mkdir()
    output.write_text(json.dumps({'status':'PASS','old_marker':'seeded-old-result'})+'\n')
    if name=='stable_core':(output.parent/'verification.log').write_text('PASS old log\n')
    return dst,output

def run_probe(name,label,flags=(),fault=None,mutate=None,expected=None,command_builder=None):
    dst,output=setup(name,label)
    if mutate:mutate(dst)
    command=[sys.executable,*flags,str(dst/'run_checks.py')]
    if command_builder:command=command_builder(dst,output,flags)
    proc=subprocess.run(command,capture_output=True,text=True,timeout=120,env=ENV)
    record=json.loads(output.read_text())
    require(proc.returncode!=0,label+' accepted injected failure')
    require(record.get('status')=='FAIL' and not record.get('old_marker'),label+' left stale success')
    error=str(record.get('error'))
    require(expected is None or expected in error,label+' unexpected error: '+error)
    require('PASS' not in proc.stdout,label+' printed scientific success')
    row={'package':name,'label':label,'flags':list(flags),'fault':fault,'exit_code':proc.returncode,'record_after':record,'stderr_tail':proc.stderr.splitlines()[-3:]}
    if name=='stable_core':
        log=(output.parent/'verification.log').read_text();require(log.startswith('FAIL:') and 'old log' not in log,label+' stale log');row['log_after']=log
    if name=='assignment' and (output.parent/'exact_assignment.log').exists():
        row['first_stage_log_tail']=(output.parent/'exact_assignment.log').read_text().splitlines()[-3:]
    return row

rows=[]
for name in ('stable_core','asymptotic','assignment'):
    for opt in (False,True):
        flags=['-O'] if opt else []
        if name=='stable_core':
            mutation=lambda dst:(dst/'verify_claims.py').rename(dst/'verify_claims.disabled')
            expected='verify_claims'; fault='missing local verify_claims'
        else:
            flags+=['-S'];mutation=None;expected='z3';fault='site loading disabled; third-party z3 absent'
        rows.append(run_probe(name,f'original_startup_{name}_{int(opt)}',flags,fault,mutation,expected))
(RESULTS/'startup_failure_after.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS 6 original startup failure regressions, normal and -O',flush=True)

rows=[]
for opt in (False,True):
    flags=['-O'] if opt else []
    rows.append(run_probe('assignment',f'verification_io_{int(opt)}',flags,'missing local verification_io',lambda dst:(dst/'verification_io.py').rename(dst/'verification_io.disabled'),'verification_io'))
    rows.append(run_probe('stable_core',f'data_module_{int(opt)}',flags,'missing local data',lambda dst:(dst/'data.py').rename(dst/'data.disabled'),'data'))
(RESULTS/'extra_local_import_failures.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS 4 additional local-dependency failures',flush=True)

# Intercept exactly the first scientific import, observe on-disk RUNNING, then fail.
HOOK=r'''
from pathlib import Path
import importlib.abc, json, runpy, sys
runner, output, dependency = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0,str(runner.parent))
class Probe(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname == dependency:
            record=json.loads(output.read_text())
            if record.get('status')!='RUNNING' or record.get('old_marker'):
                raise RuntimeError('scientific import occurred before RUNNING')
            raise ModuleNotFoundError('RUNNING observed before import: '+dependency)
sys.meta_path.insert(0,Probe())
sys.argv=[str(runner)]
runpy.run_path(str(runner),run_name='__main__')
'''
rows=[]
for name,dep in [('stable_core','data'),('asymptotic','z3'),('assignment','z3')]:
    for opt in (False,True):
        flags=['-O'] if opt else []
        builder=lambda dst,output,flags,dep=dep:[sys.executable,*flags,'-c',HOOK,str(dst/'run_checks.py'),str(output),dep]
        rows.append(run_probe(name,f'observe_running_{name}_{int(opt)}',flags,'import hook observes persisted RUNNING',None,'RUNNING observed before import:',builder))
(RESULTS/'running_before_import.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS 6 direct observations of RUNNING before first scientific import',flush=True)

def wrong_stable_claim(dst):
    p=dst/'supplement_data.json';data=json.loads(p.read_text());data['stable_witness_1']['egalitarian_claims'][0]='999';p.write_text(json.dumps(data))
def wrong_asymptotic_selector(dst):
    p=dst/'run_checks.py';s=p.read_text();old='tmin, tmax = F(denominator, denominator + 1), F(1, r - m + 1)';require(old in s,'missing mutation target');p.write_text(s.replace(old,'tmin, tmax = F(3, 4), F(1, r - m + 1)'))
def false_assignment_bound(dst):
    p=dst/'exact_assignment.py';s=p.read_text();old="require(rho <= 2-F(2, len(players)-1), 'generic bound failed')";require(old in s,'missing assignment target');p.write_text(s.replace(old,"require(rho <= -F(1), 'generic bound failed')"))
rows=[]
for name,mutation,expected in [('stable_core',wrong_stable_claim,'stored claims wrong'),('asymptotic',wrong_asymptotic_selector,'wrong maximin value'),('assignment',false_assignment_bound,'exact_assignment.py failed')]:
    for opt in (False,True):
        flags=['-O'] if opt else []
        rows.append(run_probe(name,f'science_{name}_{int(opt)}',flags,'false mathematical expectation must be rejected',mutation,expected))
(RESULTS/'scientific_exception_controls.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS 6 genuine scientific rejection controls, normal and -O',flush=True)

rows=[]
for opt in (False,True):
    dst,output=setup('asymptotic',f'help_{int(opt)}')
    flags=['-O'] if opt else []
    proc=subprocess.run([sys.executable,*flags,'-S',str(dst/'run_checks.py'),'--help'],capture_output=True,text=True,timeout=20,env=ENV)
    require(proc.returncode==0 and '--output' in proc.stdout,'--help needs scientific dependencies')
    record=json.loads(output.read_text());require(record.get('old_marker')=='seeded-old-result','help started scientific run')
    rows.append({'optimization':opt,'exit_code':proc.returncode,'help_available_without_z3':True,'existing_result_unchanged':True})
(RESULTS/'help_behavior.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS help without z3; help does not invalidate scientific result',flush=True)
(RESULTS/'control_summary.json').write_text(json.dumps({'status':'PASS','original_startup_failures':6,'extra_local_import_failures':4,'running_observations':6,'scientific_exception_controls':6,'help_controls':2},indent=2)+'\n')
