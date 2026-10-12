"""Bounded sequential development/confirmation gate; no energy or scheduling claims."""
import argparse,datetime,hashlib,json,re,threading,time
from pathlib import Path
from client import run_trace
from clock_bridge import paired_stamp,bridge_diagnostics,duration_bounds_s
from design import wire_job,score
from server_control import OwnedServer
BASE=Path(__file__).resolve().parent

def write(path,obj):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n');tmp.replace(path)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check_freeze():
 x=json.loads((BASE/'FREEZE.json').read_text())
 for n,h in x['sha256'].items():
  if hashlib.sha256((BASE/n).read_bytes()).hexdigest()!=h:raise ValueError('Frozen source mismatch: '+n)
 return hashlib.sha256((BASE/'FREEZE.json').read_bytes()).hexdigest()
def stage(config,jobs,candidate,out,deadline):
 if time.monotonic()>deadline-300:raise RuntimeError('Calibration budget stopped before stage setup')
 out.mkdir();result=dict(candidate=candidate,planned=len(jobs),status='starting',requests=[],started_utc=utc());write(out/'STAGE.json',result)
 stamps=[]
 try:
  with OwnedServer(out,config) as server:
   warm=dict(request_id='warm',arrival_offset_s=0,prompt='Return the word ready.',max_output_tokens=32)
   wr=run_trace('http://127.0.0.1:11562',[warm],config['model'],config['options'],timeout_s=30,hard_timeout_s=35,checkpoint=lambda x:write(out/'WARMUP.json',x));write(out/'WARMUP.json',wr)
   if not wr['requests'][0]['completed']:raise RuntimeError('Warmup API failed')
   server.verify_loaded();stamps.append(paired_stamp())
   for job in jobs:
    if time.monotonic()>deadline-300:raise RuntimeError('Calibration budget stopped before next request')
    server.check_host('before_'+job['request_id'])
    before=paired_stamp();triggered=threading.Event()
    def stop():triggered.set();server.stop_owned()
    timer=threading.Timer(100,stop);timer.daemon=True;timer.start()
    path=out/(job['request_id']+'.json')
    try:
     raw=run_trace('http://127.0.0.1:11562',[wire_job(job,candidate)],config['model'],config['options'],timeout_s=90,hard_timeout_s=95,checkpoint=lambda x:write(path,x));write(path,raw)
    finally:timer.cancel();timer.join()
    after=paired_stamp()
    server.check_host('after_'+job['request_id'])
    if triggered.is_set():raise RuntimeError('Owned-server watchdog fired')
    stamps.extend([before,raw['started_stamp'],raw['finished_stamp'],after])
    row=raw['requests'][0]
    entry=dict(request_id=job['request_id'],input_rows=job['input_rows'],keep_count=job['keep_count'],api_completed=row['completed'],quality_pass=None,observed_context_margin=None,raw_file=path.name,collector_duration=duration_bounds_s(raw['started_stamp'],raw['finished_stamp']),phase_duration=duration_bounds_s(before,after))
    result['requests'].append(entry);write(out/'STAGE.json',result)
    if not row['completed']:raise RuntimeError('Transport or terminal failure; abort without candidate fallback')
    if raw['epoch_monotonic_ns']!=raw['started_stamp']['monotonic_after_ns'] or not (0<=row['dispatch_offset_s']<=row['first_content_offset_s']<=row['terminal_offset_s']<=raw['elapsed_seconds']+1e-6):raise RuntimeError('Monotonic request ordering failed')
    margin=config['context']-row['final']['prompt_eval_count']-job['max_output_tokens'];entry['observed_context_margin']=margin
    if margin<128:raise RuntimeError('Observed prompt/output context allowance has insufficient margin')
    text=''.join(c['data'].get('response','') for c in row['chunks'])
    entry['quality_pass']=score(text,job);entry['output_tokens']=row['final']['eval_count'];entry['done_reason']=row['final'].get('done_reason');entry['completion_s']=row['terminal_offset_s']-row['arrival_offset_s']
    write(out/'STAGE.json',result)
    print(json.dumps(dict(stage=out.name,request=job['request_id'],quality_pass=entry['quality_pass'])),flush=True)
    time.sleep(.2)
   server.verify_loaded();stamps.append(paired_stamp());result['clock_diagnostics']=bridge_diagnostics(stamps);result['clock_stamps']=stamps
   if not result['clock_diagnostics']['valid']:raise RuntimeError('Observed clock bridge failed; no promotion')
   log=(out/'SERVER.log').read_text()
   if re.search(r'truncat(?:e|ed|ing).*input|input.*truncat',log,re.I):raise RuntimeError('Input truncation diagnostic')
  result['status']='completed';result['quality_count']=sum(x['quality_pass'] for x in result['requests']);result['gate_passed']=len(result['requests'])==len(jobs) and result['quality_count']==len(jobs)
 except BaseException as e:
  result['status']='aborted';result['error']=type(e).__name__+': '+str(e);result['gate_passed']=False;raise
 finally:
  result['finished_utc']=utc();write(out/'STAGE.json',result)
 return result

def run_gate(run_stage):
 """Pure decision tree: no B fallback after A reaches confirmation."""
 stages=[]
 for candidate in ('A','B'):
  dev=run_stage('development',candidate);stages.append(dev)
  if dev['status']!='completed':raise RuntimeError('Invalid development stage')
  if dev['gate_passed']:
   confirm=run_stage('confirmation',candidate);stages.append(confirm)
   if confirm['status']!='completed':raise RuntimeError('Invalid confirmation stage')
   return dict(selected=candidate,qualified=confirm['gate_passed'],stages=stages)
 return dict(selected=None,qualified=False,stages=stages)

def main(out):
 freeze=check_freeze();out.mkdir(parents=True,exist_ok=False)
 config=json.loads((BASE/'CONFIG.json').read_text())
 for name in ('model','options','context','lock'):
  if name not in config:raise ValueError('Missing required config: '+name)
 for name,wanted in {'budget_s':1800,'request_timeout_s':90,'max_output_caps':[192,512,1024],'candidate_order':['A','B']}.items():
  if config.get(name)!=wanted:raise ValueError('Unsupported config: '+name)
 campaign=dict(started_utc=utc(),source_freeze_sha256=freeze,status='starting',qualified=False)
 write(out/'CAMPAIGN.json',campaign);deadline=time.monotonic()+1800
 try:
  def collect(part,candidate):
   jobs=json.loads((BASE/(part+'.json')).read_text())
   return stage(config,jobs,candidate,out/(part+'-'+candidate),deadline)
  campaign.update(run_gate(collect));campaign['status']='completed'
 except BaseException as e:
  campaign['status']='aborted';campaign['error']=type(e).__name__+': '+str(e);raise
 finally:
  campaign['finished_utc']=utc();write(out/'CAMPAIGN.json',campaign)
 return campaign
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();main(a.output.resolve())
