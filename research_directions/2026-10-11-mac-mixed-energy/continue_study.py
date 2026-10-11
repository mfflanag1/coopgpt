"""Complete only a never-attempted suffix after the frozen campaign's time budget."""
import argparse,datetime,hashlib,json,time
from pathlib import Path
import runstudy,power_capture

def same(a,b):return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)

def eligible_prefix(source,previous):
 config=json.loads((source/'CONFIG.json').read_text());plan=json.loads((source/'PLAN.json').read_text())
 prior=json.loads((previous/'CAMPAIGN.json').read_text())
 if prior['status']!='budget_stopped':raise ValueError('Only time-budget stopping permits continuation')
 for name,expected in [('CONFIG.json',config),('PLAN.json',plan)]:
  if not same(json.loads((previous/name).read_text()),expected):raise ValueError('Prior design mismatch')
 windows=prior['windows'];n=len(windows)
 if not 0<n<len(plan):raise ValueError('Expected a nonempty incomplete prefix')
 if sorted(p.name for p in previous.glob('window-*'))!=[f'window-{i:02d}' for i in range(1,n+1)]:raise ValueError('Unexpected attempted window directories')
 for item,record in zip(plan,windows):
  if record['status']!='completed' or any(not same(record.get(k),v) for k,v in item.items()):raise ValueError('A previous attempted window was not completed as planned')
  if not same(json.loads((previous/f"window-{item['index']:02d}/RUN.json").read_text()),record):raise ValueError('Campaign/RUN disagreement')
  if not (previous/f"window-{item['index']:02d}/REQUESTS.json").exists():raise ValueError('Completed window missing capture')
 stop=json.loads((previous/'POWER_STOP.json').read_text())
 if 'power_stop_error' in prior or not same(prior.get('power_stop'),stop) or stop.get('stop_confirmed') is not True or type(stop.get('returncode')) is not int or stop['returncode']!=0:raise ValueError('Prior sampler did not stop normally')
 return config,plan,n

def main(previous,out):
 source=Path(__file__).resolve().parent;runstudy.check_lock()
 config,plan,n=eligible_prefix(source,previous)
 amendment=source/'CONTINUATION_PROTOCOL.txt'
 if not amendment.exists():raise ValueError('Prospective continuation record missing')
 out.mkdir(parents=True,exist_ok=False)
 claim=dict(created_utc=runstudy.utc(),output_directory=str(out),source_freeze_sha256=hashlib.sha256((source/'FREEZE.json').read_bytes()).hexdigest())
 with (previous/'CONTINUATION_CLAIM.json').open('x') as handle:
  handle.write(json.dumps(claim,sort_keys=True)+'\n')
 for name,value in [('CONFIG.json',config),('PLAN.json',plan)]:runstudy.write(out/name,value)
 c=dict(status='starting',started_utc=runstudy.utc(),windows=[],continuation_of=previous.name,
        amendment=amendment.name,amendment_sha256=hashlib.sha256(amendment.read_bytes()).hexdigest(),
        source_freeze_sha256=hashlib.sha256((source/'FREEZE.json').read_bytes()).hexdigest(),completed_prefix=list(range(1,n+1)),
        original_campaign_sha256=hashlib.sha256((previous/'CAMPAIGN.json').read_bytes()).hexdigest(),
        original_power_sha256=hashlib.sha256((previous/'POWER.txt.gz').read_bytes()).hexdigest(),
        continuation_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        full_planned_offered=config['planned_offered'],planned_offered=sum(len(json.loads((source/p['trace_file']).read_text())) for p in plan[n:]))
 meter=None
 try:
  meter=power_capture.launch(out);c['power_launch']=meter;c['status']='running';deadline=time.monotonic()+900
  for item in plan[n:]:
   if time.monotonic()>deadline-360:c['status']='budget_stopped';break
   print(json.dumps(dict(item,status='starting')),flush=True)
   try:r=runstudy.window(item,config,out)
   except BaseException:
    path=out/f"window-{item['index']:02d}/RUN.json"
    if path.exists():c['windows'].append(json.loads(path.read_text()))
    raise
   c['windows'].append(r);runstudy.write(out/'CAMPAIGN.json',c)
   print(json.dumps(dict(item,status='completed')),flush=True)
  else:c['status']='completed'
 except BaseException as error:c['status']='aborted';c['error']=type(error).__name__+': '+str(error);raise
 finally:
  if meter is not None:
   try:c['power_stop']=power_capture.stop_and_archive(meter,out)
   except BaseException as error:c['power_stop_error']=type(error).__name__+': '+str(error)
  c['finished_utc']=runstudy.utc();runstudy.write(out/'CAMPAIGN.json',c)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('previous',type=Path);p.add_argument('output',type=Path);a=p.parse_args();main(a.previous.resolve(),a.output.resolve())
