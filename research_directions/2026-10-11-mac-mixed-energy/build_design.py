"""Generate deterministic, nonprivate extraction tasks and the prospective run order."""
from pathlib import Path
import json,random
BASE=Path(__file__).resolve().parent

def write(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def main():
 BASE.joinpath('traces').mkdir(exist_ok=True)
 config=dict(model='llama3.2:3b',digest='a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72',
  options=dict(temperature=0,seed=0,num_predict=64,num_ctx=4096), offered_seconds=90,
  rates=[.3,.6,1.2],parallels=[1,2,4],repetitions=2,timeout_s=45,watchdog_s=145,
  pre_idle_s=10,post_idle_s=10,global_budget_s=2700,context=4096,
  output_caps=[64,192,384],slo_by_cap={'64':8,'192':16,'384':30},
  input_rows=[32,96,192],planned_offered=1134,
  warmups=[dict(request_id=f'warm{i+1}',arrival_offset_s=0,prompt=f'Warmup topic {i+1}: Explain in a short paragraph why {topic}.') for i,topic in enumerate(['cubes have flat sides','water moves downhill','queues can grow','memory has finite capacity'])],
  server_settings_common={'OLLAMA_HOST':'http://127.0.0.1:11562','OLLAMA_MAX_LOADED_MODELS':'1','OLLAMA_MAX_QUEUE':'256','OLLAMA_CONTEXT_LENGTH':'4096','OLLAMA_FLASH_ATTENTION':'0','OLLAMA_KV_CACHE_TYPE':'f16','OLLAMA_MULTIUSER_CACHE':'0','OLLAMA_NO_CLOUD':'1','OLLAMA_NOPRUNE':'1','OLLAMA_NOHISTORY':'1','OLLAMA_KEEP_ALIVE':'120s','OLLAMA_DEBUG':'1'})
 write(BASE/'CONFIG.json',config)
 rates=config['rates'];rng=random.Random(20261011);rateorder=rates.copy();rng.shuffle(rateorder)
 permutations={r:random.Random(301+int(r*100)).sample([1,2,4],3) for r in rates}
 plan=[]
 for rep in (1,2):
  jobs=[]
  for block in range(12):
   cells=[(a,b) for a in range(3) for b in range(3)];random.Random(8191*rep+block).shuffle(cells)
   for a,b in cells:
    j=len(jobs);n=config['input_rows'][a];count=[4,12,24][b];seed=20261011+rep*10000+j
    local=random.Random(seed);keep=set(local.sample(range(1,n+1),count));values={i:local.randrange(100,1000) for i in range(1,n+1)}
    rows=[f'R{i:04d} value={values[i]} flag={"KEEP" if i in keep else "DROP"}' for i in range(1,n+1)]
    gold=';'.join(f'R{i:04d}={values[i]}' for i in sorted(keep))
    prompt=f'Task {rep}-{j+1:04d}. Copy every KEEP record below. Return only ID=value pairs separated by semicolons, in increasing ID order. Omit DROP records. Preserve each three-digit value exactly. No explanation.\n'+ '\n'.join(rows)+'\nAnswer:'
    jobs.append(dict(request_id=f'r{j+1:04d}',prompt=prompt,max_output_tokens=config['output_caps'][b],input_rows=n,input_class=['short','medium','long'][a],output_class=['small','medium','large'][b],slo_s=[8,16,30][b],expected=gold))
  for rate in (rateorder if rep==1 else list(reversed(rateorder))):
   n=round(90*rate);trace=[dict(job,arrival_offset_s=i/rate) for i,job in enumerate(jobs[:n])]
   name=f'traces/rep{rep}-rate{rate}.json';write(BASE/name,trace)
   for parallel in (permutations[rate] if rep==1 else list(reversed(permutations[rate]))):
    plan.append(dict(index=len(plan)+1,rate=rate,rep=rep,parallel=parallel,trace_file=name))
 write(BASE/'PLAN.json',plan)
if __name__=='__main__':main()
