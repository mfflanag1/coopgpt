"""Exercise original and proposed record wrappers in ordinary and -O Python."""
from pathlib import Path
import copy
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
WORK=ROOT/'worktree'
PYTHON=sys.executable
WRAPPERS=[
 dict(name='verify_strict_exchange_bound_certificates.py',audit='strict_exchange_direction_cores.json',cert='certificates',stem='strict_exchange_p1_n1_t4'),
 dict(name='verify_equality_exchange_classification_certificates.py',audit='equality_exchange_direction_cores.json',cert='certificates',stem='equality_exchange_p1_n1_t4'),
 dict(name='verify_strict_exchange_orbit_core_certificates.py',audit='strict_exchange_large_case_orbit_cores.json',cert='orbit_core_certificates',stem='strict_exchange_orbit_core_p3_n2_t1'),
]

def require(ok,msg):
 if not ok: raise RuntimeError(msg)

def run(config,proposed,optimized):
 script=config['name'] if proposed else 'old_'+config['name']
 command=[PYTHON]+(['-O'] if optimized else [])+[str(WORK/script)]
 result=subprocess.run(command,cwd=WORK,text=True,capture_output=True,timeout=120)
 try: payload=json.loads(result.stdout)
 except json.JSONDecodeError: payload={}
 accepted=result.returncode==0 and payload.get('status')=='PASS'
 return dict(version='proposed' if proposed else 'original',optimized=optimized,returncode=result.returncode,accepted=accepted,checked_rows=len(payload.get('checked',[])) if accepted else None,error_tail='\n'.join(result.stderr.splitlines()[-2:]))

def changed_json(path,change):
 data=json.loads(path.read_text()); change(data)
 return (json.dumps(data,indent=2,sort_keys=True)+'\n').encode()


def controls(config):
 audit=WORK/config['audit'];record=WORK/config['cert']/(config['stem']+'.json')
 orbit='orbit_core' in config['name']
 yield 'audit_status',audit,changed_json(audit,lambda d:d.__setitem__('status','FAIL'))
 yield 'record_ethos_status',record,changed_json(record,lambda d:d['cpc_proof']['ethos'].__setitem__('status','incorrect'))
 yield 'missing_row',audit,changed_json(audit,lambda d:d['rows'].pop())
 yield 'empty_rows',audit,changed_json(audit,lambda d:d.__setitem__('rows',[]))
 yield 'duplicate_row',audit,changed_json(audit,lambda d:d['rows'].__setitem__(-1,copy.deepcopy(d['rows'][0])))
 count='selected_labeled_direction_count' if orbit else 'case_count'
 yield 'declared_count',audit,changed_json(audit,lambda d:d.__setitem__(count,d[count]-1))
 rowcount='selected_labeled_direction_count' if orbit else 'retained_direction_count'
 yield 'row_count',audit,changed_json(audit,lambda d:d['rows'][0].__setitem__(rowcount,d['rows'][0][rowcount]+1))
 yield 'proof_byte_count',record,changed_json(record,lambda d:d['cpc_proof'].__setitem__('proof_bytes',d['cpc_proof']['proof_bytes']+1))
 formula=WORK/config['cert']/(config['stem']+'.smt2')
 yield 'modified_formula',formula,formula.read_bytes()+b'\n; control: formula bytes changed\n'
 proof=WORK/config['cert']/(config['stem']+'.cpc')
 yield 'modified_CPC',proof,proof.read_bytes()+b'\n; control: proof bytes changed\n'
 if orbit:
  yield 'missing_orbit_ablations',audit,changed_json(audit,lambda d:d['rows'][0].__setitem__('single_orbit_ablations',[]))
  yield 'incorrect_selected_orbits',audit,changed_json(audit,lambda d:d['rows'][0].__setitem__('selected_orbits',[]))
 else:
  yield 'retained_menu_missing',audit,changed_json(audit,lambda d:d['rows'][0].__setitem__('retained_menu',[]))


def main():
 results=[]
 for config in WRAPPERS:
  baseline=[run(config,p,o) for p in (False,True) for o in (False,True)]
  require(all(r['accepted'] for r in baseline),'baseline failed '+config['name'])
  trials=[]
  for label,path,replacement in controls(config):
   original=path.read_bytes()
   try:
    path.write_bytes(replacement)
    outcomes=[run(config,p,o) for p in (False,True) for o in (False,True)]
   finally:path.write_bytes(original)
   require(all(not r['accepted'] for r in outcomes if r['version']=='proposed'),label+' passed proposed guard')
   trials.append(dict(control=label,file=str(path.relative_to(WORK)),outcomes=outcomes))
   print(config['name'],label,'original accepted:',[r['optimized'] for r in outcomes if r['version']=='original' and r['accepted']],'proposed rejected both modes',flush=True)
  results.append(dict(wrapper=config['name'],baseline=baseline,controls=trials))
  (ROOT/'wrapper_control_results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
 print('PASS every valid baseline and every proposed negative control in normal/-O modes',flush=True)

if __name__=='__main__':main()
