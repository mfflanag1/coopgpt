"""Prospective synthetic calibration and confirmation tasks; no model calls."""
import json,random,re
from pathlib import Path
BASE=Path(__file__).resolve().parent
SCHEMA={'type':'object','properties':{'records':{'type':'array','items':{'type':'object','properties':{'id':{'type':'string','pattern':'^R[0-9]{4}$'},'value':{'type':'string','pattern':'^[0-9]{3}$'}},'required':['id','value'],'additionalProperties':False}}},'required':['records'],'additionalProperties':False}
CAPS={4:192,12:512,24:1024}
INSTRUCTION='Select every record whose flag is KEEP, and omit every record whose flag is DROP. Copy both the ID and its three-digit value exactly. Return one JSON object with a records array, sorted by ID. Each item has string fields id and value. Do not add commentary or any other field.\n'
EXAMPLE='Example only, not part of the input:\nR9001 value=271 flag=KEEP\nR9002 value=583 flag=DROP\nR9003 value=946 flag=KEEP\nThe example answer would be {"records":[{"id":"R9001","value":"271"},{"id":"R9003","value":"946"}]}. These example IDs do not occur in the actual input.\n'
def tasks(seed,per_cell,label):
 rng=random.Random(seed);jobs=[]
 for repeat in range(per_cell):
  cells=[(n,k) for n in (32,96,192) for k in (4,12,24)];rng.shuffle(cells)
  for n,k in cells:
   keep=set(rng.sample(range(1,n+1),k));rows=[dict(id=f'R{i:04d}',value=str(rng.randrange(100,1000)),flag='KEEP' if i in keep else 'DROP') for i in range(1,n+1)]
   jobs.append(dict(request_id=f'{label}-{len(jobs)+1:03d}',input_rows=n,keep_count=k,max_output_tokens=CAPS[k],rows=rows,expected={'records':[{a:r[a] for a in ('id','value')} for r in rows if r['flag']=='KEEP']}))
 return jobs
def wire_job(job,candidate):
 if candidate not in ('A','B'):raise ValueError('unknown candidate')
 prompt=INSTRUCTION+(EXAMPLE if candidate=='B' else '')+'Output schema: '+json.dumps(SCHEMA,separators=(',',':'))+'\nInput records:\n'+'\n'.join(f"{r['id']} value={r['value']} flag={r['flag']}" for r in job['rows'])+'\nJSON answer:'
 return dict(request_id=job['request_id'],arrival_offset_s=0,prompt=prompt,max_output_tokens=job['max_output_tokens'],format=SCHEMA)
def strict_object(pairs):
 obj={}
 for k,v in pairs:
  if k in obj:raise ValueError('duplicate JSON key')
  obj[k]=v
 return obj
def score(text,job):
 try:
  obj=json.loads(text,object_pairs_hook=strict_object,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
  if type(obj)!=dict or set(obj)!= {'records'} or type(obj['records'])!=list:return False
  for r in obj['records']:
   if type(r)!=dict or set(r)!={'id','value'} or type(r['id'])!=str or type(r['value'])!=str:return False
   if not re.fullmatch(r'R[0-9]{4}',r['id']) or not re.fullmatch(r'[0-9]{3}',r['value']):return False
  return obj==job['expected']
 except (ValueError,TypeError):return False

def main():
 for name,seed,n,label in [('development.json',202610111,1,'dev'),('confirmation.json',202610112,3,'confirm')]:
  (BASE/name).write_text(json.dumps(tasks(seed,n,label),indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
