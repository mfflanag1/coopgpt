"""One bounded initial attempt per reserved support, after a hashed statement."""
import json,sys,time,hashlib,datetime
from pathlib import Path
from fractions import Fraction as Q

def main():
 c=Path(sys.argv[1]).resolve();sys.path.insert(0,str(c/'src'))
 from solve_support import solve
 from check_certificate import check
 from relaxation import solve as oldsolve,check as oldcheck
 from residual_relaxation import solve as rpsolve,check as rpcheck
 freeze=json.loads((c/'interpretation/RESIDUAL_SUFFICIENCY_FREEZE.json').read_text())
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 if sha(c/'interpretation/RESIDUAL_SUFFICIENCY_CONJECTURE.md')!=freeze['statement_sha256']:raise ValueError('statement changed')
 if sha(c/'registry/supports.json')!=freeze['registry_sha256']:raise ValueError('registry changed')
 if sha(c/'src/residual_relaxation.py')!=freeze['source_sha256']:raise ValueError('RP source changed')
 reg=json.loads((c/'registry/supports.json').read_text());out=c/'heldout';out.mkdir(exist_ok=True);results=[];start=time.monotonic();status='COMPLETE'
 for row in reg['supports']:
  if not row['held_out']:continue
  name=row['id']
  if any(out.glob(name+'_*')):raise ValueError('refusing repeat heldout attempt')
  meta={'support_id':name,'registry_sha256':freeze['registry_sha256'],'statement_sha256':freeze['statement_sha256'],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'attempt':1,'solver_limit_seconds':1800,'sources':{n:sha(c/'src'/n) for n in ['solve_support.py','check_certificate.py','relaxation.py','residual_relaxation.py']}}
  item={'id':name}
  for tag,sol,verify in [('full',solve,check),('relaxed',oldsolve,oldcheck),('residual',rpsolve,rpcheck)]:
   data=sol(row['m'],row['P'],1800);data['provenance']=meta;(out/(name+'_'+tag+'.json')).write_text(json.dumps(data,indent=2)+'\n')
   item[tag]=verify(data) if 'schema' in data else {'status':data['status']}
   item[tag]['elapsed_seconds']=data['discovery']['elapsed_seconds']
   if tag=='full' and 'lower' in item[tag] and Q(item[tag]['lower'])>Q(1,3):status='STOP_FOR_ACTUAL_WITNESS_AUDIT';break
   if tag=='residual' and item[tag].get('above_one_third'):status='RP_SUFFICIENCY_REFUTED';break
  results.append(item);print(json.dumps(item),flush=True)
  if status!='COMPLETE':break
 summary={'status':status,'results':results,'elapsed_seconds':time.monotonic()-start,'freeze':freeze,'scope':'finite fixed-support bounds and diagnostic feasible points only; RP counterexample is not an actual-market counterexample'}
 (out/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'status':status,'elapsed_seconds':summary['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
