"""Bounded public range intake; raw third-party data remain outside the handoff."""
from pathlib import Path
import datetime, hashlib, json, re, tarfile, time, urllib.request
BASE=Path('/private/tmp/coopgpt-overnight-20261017')
OUT=Path('/private/tmp/coopgpt-m100-raw-20261017');OUT.mkdir(exist_ok=True)
URL='https://zenodo.org/records/7588815/files/20-04.tar?download=1'
TOTAL=210769920; LIMIT=100_000_000; REQUEST_LIMIT=250
TARGETS={'total_power','ps0_input_power','ps1_input_power'}
used=0; requests=0; last=0.; cache=b''; cache_at=-1
entries=[]; fetched=[]
def fetch(start,length):
 global used,requests,last
 if length<=0:return b''
 if used+length>LIMIT or requests>=REQUEST_LIMIT:raise RuntimeError('Intake budget reached')
 delay=0.7-(time.monotonic()-last)
 if delay>0:time.sleep(delay)
 end=start+length-1
 req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}','User-Agent':'CoopGPT-public-data-schema-check/1.0'})
 with urllib.request.urlopen(req,timeout=30) as r:
  if r.status!=206:raise RuntimeError(f'Range not honored: {r.status}')
  if r.headers.get('Content-Range')!=f'bytes {start}-{end}/{TOTAL}':raise RuntimeError('Unexpected Content-Range')
  b=r.read(length+1)
  if len(b)!=length:raise RuntimeError('Wrong range body length')
 used+=len(b);requests+=1;last=time.monotonic();return b

def small(start,length):
 global cache,cache_at
 if cache_at<=start and start+length<=cache_at+len(cache):return cache[start-cache_at:start-cache_at+length]
 cache_at=start;cache=fetch(start,min(max(16384,length),TOTAL-start));return cache[:length]

status='COMPLETE'; error=None; offset=0; pending_name=None
try:
 while offset+512<=TOTAL:
  header=small(offset,512)
  if not any(header):
   remaining=TOTAL-offset
   if remaining>4096:raise RuntimeError('Unexpectedly long archive end padding')
   padding=fetch(offset,remaining)
   if len(padding)<1024 or any(padding):raise RuntimeError('Invalid tar end padding')
   break
  ti=tarfile.TarInfo.frombuf(header,'utf-8','surrogateescape')
  data_at=offset+512
  if ti.type==tarfile.GNUTYPE_LONGNAME:
   pending_name=small(data_at,ti.size).rstrip(b'\x00').decode('utf-8')
  elif ti.type in (tarfile.XHDTYPE,tarfile.XGLTYPE):
   raise RuntimeError('PAX archive needs explicit parser; stop rather than guessing paths')
  else:
   name=pending_name or ti.name;pending_name=None
   row={'name':name,'size':ti.size,'offset':data_at,'type':ti.type.decode('ascii','replace')};entries.append(row)
   m=re.search(r'/plugin=ipmi_pub/metric=([^/]+)/',name)
   if ti.isfile() and m and m.group(1) in TARGETS and name.endswith('.parquet'):
    if ti.size>30_000_000:raise RuntimeError('Target member exceeds30MB individual budget')
    data=fetch(data_at,ti.size)
    p=OUT/(m.group(1)+'__'+Path(name).name);p.write_bytes(data)
    fetched.append({**row,'local_raw_path':str(p),'sha256':hashlib.sha256(data).hexdigest()})
    print('Fetched',m.group(1),ti.size,'bytes',flush=True)
  offset=data_at+((ti.size+511)//512)*512
except Exception as exc:
 status='STOPPED';error=type(exc).__name__+': '+str(exc)
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':status,'error':error,'source':URL,'archive_bytes':TOTAL,'downloaded_bytes':used,'requests':requests,'budget_bytes':LIMIT,'next_offset':offset,'entries':entries,'selected_members':fetched,'scope':'Observed public archive intake only; no empirical pooling or reliability inference.'}
(BASE/'checks/M100_RANGE_INTAKE.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('entries','selected_members')},indent=2))
