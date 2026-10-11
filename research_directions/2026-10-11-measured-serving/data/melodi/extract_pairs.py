#!/usr/bin/env python3
"""Extract unique exact-prompt pairs; no fitting, selection, or replay.
Derived numeric data: CC BY-SA 4.0, Husom et al. (2024); see PROVENANCE.json.
Raw prompts/responses are hashed and not redistributed in the output.
"""
import argparse, csv, hashlib, json, statistics
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

FILES = {
 'laptop2': ('alpaca_gemma_7b_laptop2.csv', '93901dc3fdf03bc06e69535186caf1d2fc6cbe53c6d82481f65953d32f175950'),
 'workstation': ('alpaca_gemma_7b_workstation.csv', 'ee627119afe11b9e1c116a4b70d5a56efef3ebf3ab1f83a344585cd80c5bb9b8'),
}
def sha(x): return hashlib.sha256(x).hexdigest()
def dec(x): return Decimal(x)
def dt(x): return datetime.fromisoformat(x)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=Path(__file__).resolve().parent.parent);p.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
 sources={}; indexes={}; audit={}
 for name,(file,digest) in FILES.items():
  path=a.source_dir/file
  actual=sha(path.read_bytes())
  if actual!=digest:raise ValueError(f'Unexpected source checksum: {file} {actual}')
  with path.open(newline='') as f: rows=list(csv.DictReader(f))
  counts=Counter(r['prompt'] for r in rows)
  indexes[name]={r['prompt']:(idx,r) for idx,r in enumerate(rows) if counts[r['prompt']]==1}
  sources[name]=rows
  chrono=sorted(rows,key=lambda r:dt(r['start_time']))
  gaps=[(dt(y['start_time'])-dt(x['end_time'])).total_seconds() for x,y in zip(chrono,chrono[1:])]
  audit[name]={
   'source_rows':len(rows),'unique_prompts':len(counts),'duplicated_prompt_values':sum(v>1 for v in counts.values()),
   'temporal_overlaps':sum(g<0 for g in gaps),'minimum_between_request_gap_seconds':min(gaps),'median_between_request_gap_seconds':statistics.median(gaps),
   'warm_load_fraction_le_1pct':sum(dec(r['load_duration'])<=dec(r['total_duration'])/100 for r in rows),
   'load_over_100ms_count':sum(dec(r['load_duration'])>100000000 for r in rows),
   'median_api_seconds':statistics.median(float(dec(r['total_duration'])/10**9) for r in rows),
   'median_gpu_watts_using_api_duration_plus_default_1sec_buffer_DIAGNOSTIC_ONLY':statistics.median(float(dec(r['energy_consumption_llm_gpu'])*3600000/(dec(r['total_duration'])/10**9+1)) for r in rows),
   'source_sha256':actual,
  }
 paired=[]
 common=set(indexes['laptop2'])&set(indexes['workstation'])
 for prompt in sorted(common,key=lambda k:indexes['laptop2'][k][0]):
  row={'prompt_sha256':sha(prompt.encode()),'same_prompt_tokens':int(indexes['laptop2'][prompt][1]['prompt_token_length']==indexes['workstation'][prompt][1]['prompt_token_length']), 'same_response_text':int(indexes['laptop2'][prompt][1]['response']==indexes['workstation'][prompt][1]['response']), 'same_response_tokens':int(indexes['laptop2'][prompt][1]['response_token_length']==indexes['workstation'][prompt][1]['response_token_length'])}
  for name in FILES:
   idx,r=indexes[name][prompt]
   row[name+'_source_row_zero_based']=idx
   row[name+'_model_label']=r['model_name']
   row[name+'_response_sha256']=sha(r['response'].encode())
   for k in ['start_time','end_time','prompt_token_length','response_token_length']:
    row[name+'_'+k]=r[k]
   for k in ['total_duration','load_duration','prompt_duration','response_duration']:
    row[name+'_'+k+'_seconds']=str(dec(r[k])/10**9)
   row[name+'_clock_duration_seconds']=str((dt(r['end_time'])-dt(r['start_time'])).total_seconds())
   for k in ['gpu','cpu','total']:
    row[name+'_energy_'+k+'_kwh']=r['energy_consumption_llm_'+k]
   row[name+'_load_fraction']=str(dec(r['load_duration'])/dec(r['total_duration']))
  paired.append(row)
 with (a.output_dir/'PAIRED_MEASUREMENTS.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
 audit['paired']={'exact_unique_prompt_pairs':len(paired),'same_prompt_token_count':sum(r['same_prompt_tokens'] for r in paired),'same_response_text':sum(r['same_response_text'] for r in paired),'same_response_token_count':sum(r['same_response_tokens'] for r in paired),'no_replay_or_predictor_fitting':True,'no_pair_filtering_after_matching':True}
 (a.output_dir/'COMPATIBILITY_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
 print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
