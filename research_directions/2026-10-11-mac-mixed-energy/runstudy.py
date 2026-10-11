#!/usr/bin/env python3
"""Collect the frozen mixed-task study with bounded same-device power telemetry."""
import argparse,datetime,hashlib,json,os,re,signal,socket,subprocess,threading,time,urllib.request
from pathlib import Path
from client import run_trace
import power_capture
BASE=Path(__file__).resolve().parent
URL='http://127.0.0.1:11562';ORIGINAL='http://127.0.0.1:11434';BINARY='/opt/homebrew/bin/ollama'

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(path,obj):
 temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_text(json.dumps(obj,separators=(',',':'),sort_keys=True)+'\n');temporary.replace(path)
def api(path,body=None,base=URL,timeout=5):
 request=urllib.request.Request(base+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(request,timeout=timeout) as response:return json.load(response)
def original_idle():
 try:return not api('/api/ps',base=ORIGINAL)['models']
 except Exception:return None
def state():
 def call(args):
  p=subprocess.run(args,capture_output=True,text=True,timeout=5);return p.stdout.strip() or p.stderr.strip()
 return dict(utc=utc(),power=re.sub(r'\(id=\d+\)','(id=REDACTED)',call(['/usr/bin/pmset','-g','batt'])),thermal=call(['/usr/bin/pmset','-g','therm']),load_average=list(os.getloadavg()))
def parallel_values(log):
 return sorted({int(x) for p in [r'n_seq_max\s*=\s*(\d+)',r'\bParallel[=:]\s*(\d+)',r'--parallel\s+(\d+)'] for x in re.findall(p,log)})
def check_lock():
 freeze=json.loads((BASE/'FREEZE.json').read_text())
 for name,digest in freeze['sha256'].items():
  if hashlib.sha256((BASE/name).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen input changed: '+name)
 lock=json.loads((BASE/'MODEL_LOCK.json').read_text())
 manifest=Path.home()/'.ollama/models/manifests/registry.ollama.ai/library/llama3.2/3b'
 if hashlib.sha256(manifest.read_bytes()).hexdigest()!=lock['manifest_sha256']:raise ValueError('Model manifest changed')
 if hashlib.sha256(Path(BINARY).resolve().read_bytes()).hexdigest()!=lock['binary_sha256']:raise ValueError('Binary changed')
def loaded_ok(value,config):
 models=value.get('models',[])
 return len(models)==1 and models[0]['digest']==config['digest'] and models[0].get('context_length')==config['context'] and models[0].get('size_vram',0)>0

def window(item,config,out):
 path=out/f'window-{item["index"]:02d}';path.mkdir();proc=None;watchdog=None
 meta=dict(item,status='starting',model=config['model'],options=config['options'],before=state(),original_endpoint_idle_before=original_idle(),phases=[])
 def phase(name,stamp=None):
  meta['phases'].append(dict(name=name,utc=stamp or utc()));write(path/'RUN.json',meta)
 def kill_owned(sig=signal.SIGTERM):
  if proc is not None:
   try:os.killpg(proc.pid,sig)
   except ProcessLookupError:pass
 def stop_server():
  if proc is None:return
  if proc.poll() is None:
   try:
    api('/api/generate',dict(model=config['model'],keep_alive=0),timeout=15)
    deadline=time.monotonic()+15
    while True:
     meta['loaded_after_unload']=api('/api/ps')
     if not meta['loaded_after_unload']['models']:break
     if time.monotonic()>deadline:raise RuntimeError('Model unload timeout')
     time.sleep(.1)
   except Exception as error:meta['cleanup_error']=type(error).__name__+': '+str(error)
   kill_owned()
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
  kill_owned()
  deadline=time.monotonic()+3
  while True:
   try:os.killpg(proc.pid,0)
   except ProcessLookupError:break
   if time.monotonic()>=deadline:
    kill_owned(signal.SIGKILL);break
   time.sleep(.1)
  meta['dedicated_server_returncode']=proc.returncode
 write(path/'RUN.json',meta)
 try:
  if meta['original_endpoint_idle_before'] is not True:raise RuntimeError('Original endpoint is not verified idle')
  if "'AC Power'" not in meta['before']['power']:raise RuntimeError('AC power absent')
  with socket.socket() as probe:
   probe.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);probe.bind(('127.0.0.1',11562))
  settings=dict(config['server_settings_common'],OLLAMA_NUM_PARALLEL=str(item['parallel']))
  meta['server_settings']=settings
  env={k:v for k,v in os.environ.items() if k in ('PATH','HOME','TMPDIR','LANG','LC_ALL')};env.update(settings)
  with (path/'SERVER.log').open('w') as log:proc=subprocess.Popen([BINARY,'serve'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  meta['dedicated_server_pid']=proc.pid
  deadline=time.monotonic()+30
  while True:
   if proc.poll() is not None:raise RuntimeError('Server exited before readiness')
   try:meta['version']=api('/api/version');break
   except Exception:
    if time.monotonic()>deadline:raise RuntimeError('Server readiness timeout')
    time.sleep(.1)
  if meta['version']['version']!='0.20.0':raise ValueError('Wrong server version')
  meta['model_tag']=next(x for x in api('/api/tags')['models'] if x['name']==config['model'])
  if meta['model_tag']['digest']!=config['digest']:raise ValueError('Wrong model digest')
  warm=run_trace(URL,config['warmups'],config['model'],config['options'],timeout_s=config['timeout_s'],hard_timeout_s=55,checkpoint=lambda value:write(path/'WARMUP.json',value));write(path/'WARMUP.json',warm)
  if len(warm['requests'])!=4 or not all(r['completed'] for r in warm['requests']):raise RuntimeError('Warmup failed')
  meta['loaded_before']=api('/api/ps')
  if not loaded_ok(meta['loaded_before'],config):raise ValueError('GPU model/context unverified')
  meta['runtime_parallel_values']=parallel_values((path/'SERVER.log').read_text())
  if meta['runtime_parallel_values']!=[item['parallel']]:raise ValueError('Actual server parallelism unverified')
  phase('loaded_idle_start');time.sleep(config['pre_idle_s'])
  trace=json.loads((BASE/item['trace_file']).read_text())
  phase('workload_start');workstart=time.monotonic()
  def abort_watchdog():
   meta['watchdog_fired']=True;kill_owned();time.sleep(3);kill_owned(signal.SIGKILL)
  watchdog=threading.Timer(config['watchdog_s'],abort_watchdog);watchdog.daemon=True;watchdog.start()
  result=run_trace(URL,trace,config['model'],config['options'],timeout_s=config['timeout_s'],hard_timeout_s=155,checkpoint=lambda value:write(path/'REQUESTS.json',value));write(path/'REQUESTS.json',result)
  meta['phases'][-1]['utc']=result['started_utc']
  remaining=config['offered_seconds']-(time.monotonic()-workstart)
  if remaining>0:time.sleep(remaining)
  phase('workload_drained')
  watchdog.cancel();watchdog.join()
  if meta.get('watchdog_fired'):raise RuntimeError('Workload watchdog fired')
  meta['loaded_after']=api('/api/ps')
  if not loaded_ok(meta['loaded_after'],config):raise RuntimeError('Loaded model changed after workload')
  stop_server();phase('server_quiescent');time.sleep(config['post_idle_s']);phase('episode_end')
  meta['after']=state();meta['original_endpoint_idle_after']=original_idle()
  if meta.get('cleanup_error') or meta.get('loaded_after_unload',{}).get('models')!=[]:raise RuntimeError('Cleanup not verified')
  meta['status']='completed'
 except BaseException as error:
  meta['status']='aborted';meta['error']=type(error).__name__+': '+str(error);raise
 finally:
  if watchdog is not None:watchdog.cancel()
  if proc is not None:stop_server()
  logfile=path/'SERVER.log'
  if logfile.exists():logfile.write_text(logfile.read_text().replace(str(Path.home()),'USER_HOME'))
  write(path/'RUN.json',meta)
 return meta

def main(out):
 check_lock();out.mkdir(parents=True,exist_ok=False)
 config=json.loads((BASE/'CONFIG.json').read_text());plan=json.loads((BASE/'PLAN.json').read_text())
 write(out/'PLAN.json',plan);write(out/'CONFIG.json',config)
 campaign=dict(status='starting',started_utc=utc(),planned_offered=config['planned_offered'],windows=[])
 meter=None
 try:
  meter=power_capture.launch(out);campaign['power_launch']=meter
  deadline=time.monotonic()+config['global_budget_s'];campaign['status']='running'
  for item in plan:
   if time.monotonic()>deadline-360:
    campaign['status']='budget_stopped';break
   print(json.dumps(dict(item,status='starting')),flush=True)
   try:meta=window(item,config,out)
   except BaseException:
    path=out/f'window-{item["index"]:02d}/RUN.json'
    if path.exists():campaign['windows'].append(json.loads(path.read_text()))
    raise
   campaign['windows'].append(meta);write(out/'CAMPAIGN.json',campaign)
   print(json.dumps(dict(item,status='completed')),flush=True)
  else:campaign['status']='completed'
 except BaseException as error:
  campaign['status']='aborted';campaign['error']=type(error).__name__+': '+str(error);raise
 finally:
  if meter is not None:
   try:campaign['power_stop']=power_capture.stop_and_archive(meter,out)
   except BaseException as error:campaign['power_stop_error']=type(error).__name__+': '+str(error)
  campaign['finished_utc']=utc();write(out/'CAMPAIGN.json',campaign)
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
 main(parser.parse_args().output)
