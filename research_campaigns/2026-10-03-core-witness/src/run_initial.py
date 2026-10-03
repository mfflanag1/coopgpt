import sys,json,time,hashlib,datetime
from pathlib import Path
c=Path(__file__).resolve().parents[1];sys.path.insert(0,str(c/'src'))
from solve_support import solve
from check_certificate import check
from relaxation import solve as rsolve,check as rcheck
reg=json.loads((c/'registry/supports.json').read_text());digest=hashlib.sha256((c/'registry/supports.json').read_bytes()).hexdigest()
if digest!='84c0f4f9212721939aca5e4d1dd253fb734aa447507121e5893dcaeb32ff6ef7':raise ValueError('registry hash changed')
out=c/'paired';out.mkdir(exist_ok=True);results=[];start=time.monotonic()
for row in reg['supports']:
 if row['held_out']:continue
 name=row['id'];path=out/(name+'_full.json')
 if path.exists() or (out/(name+'_relaxed.json')).exists():raise ValueError('refusing repeat initial attempt')
 print(json.dumps({'phase':'start','id':name,'m':row['m'],'r':len(row['P'])}),flush=True)
 meta={'registry_sha256':digest,'source_hashes':{n:hashlib.sha256((c/'src'/n).read_bytes()).hexdigest() for n in ['solve_support.py','check_certificate.py','relaxation.py']},'support_id':name,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'attempt':1,'solver_limit_seconds':1800,'held_out':False}
 full=solve(row['m'],row['P'],1800);full['provenance']=meta;path.write_text(json.dumps(full,indent=2)+'\n')
 if 'schema' not in full:
  result={'id':name,'full_status':full['status'],'relaxed_status':'not run after full failure'};results.append(result);print(json.dumps(result),flush=True);continue
 fresult=check(full)
 if __import__('fractions').Fraction(fresult['lower'])>__import__('fractions').Fraction(1,3):
  results.append({'id':name,'full':fresult,'branch':'STOP_FOR_COUNTEREXAMPLE_AUDIT'});break
 relaxed=rsolve(row['m'],row['P'],1800);relaxed['provenance']=meta;(out/(name+'_relaxed.json')).write_text(json.dumps(relaxed,indent=2)+'\n')
 rresult=rcheck(relaxed) if 'schema' in relaxed else {'status':relaxed['status']}
 result={'id':name,'full':fresult,'relaxed':rresult,'full_solve_seconds':full['discovery']['elapsed_seconds'],'relaxed_solve_seconds':relaxed['discovery']['elapsed_seconds']};results.append(result);print(json.dumps(result),flush=True)
(out/'INITIAL_RESULTS.json').write_text(json.dumps({'status':'INITIAL_FOUR_COMPLETED' if len(results)==4 else 'STOPPED','registry_sha256':digest,'elapsed_seconds':time.monotonic()-start,'results':results,'scope':'full bounds are fixed-support; relaxed points are feasible lower bounds only; heldouts remain unopened'},indent=2)+'\n')
