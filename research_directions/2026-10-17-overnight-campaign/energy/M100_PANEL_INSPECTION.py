"""Descriptive raw-file gate only: no causal, pooling, or reliability inference."""
from pathlib import Path
import datetime, hashlib, json, math
import duckdb
BASE=Path('/private/tmp/coopgpt-overnight-20261017'); RAW=Path('/private/tmp/coopgpt-m100-raw-20261017')
C=duckdb.connect(str(RAW/'inspection.duckdb'))
C.execute("SET memory_limit='1GB'");C.execute('SET threads=2');C.execute("SET TimeZone='UTC'")
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'duckdb':duckdb.__version__,'scope':'Descriptive existence and quality gate for April2020 public M100 power files; not ownership, reliability or pooling validation.','schema':[]}
def query(q,params=None):
 cur=C.execute(q,params or []); cols=[d[0] for d in cur.description]
 return [dict(zip(cols,x)) for x in cur.fetchall()]
def save():
 (BASE/'checks/M100_PANEL_INSPECTION.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
parts=[]
for p in sorted(RAW.glob('*.parquet')):
 metric=p.name.split('__')[0]
 report['schema'].append({'metric':metric,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'columns':query('DESCRIBE SELECT * FROM read_parquet(?)',[str(p)]),'parquet_metadata':query('SELECT DISTINCT row_group_id,row_group_num_rows FROM parquet_metadata(?)',[str(p)])})
 # Paths are exclusively constructed locally from observed tar member basenames.
 parts.append("SELECT '"+metric+"' AS metric,node,epoch_ms(timestamp)::BIGINT AS t,value::BIGINT AS v FROM read_parquet('"+str(p).replace("'","''")+"')")
C.execute('CREATE OR REPLACE TABLE raw AS '+ ' UNION ALL '.join(parts));save()
report['raw_by_metric']=query('''SELECT metric,count(*) AS rows,count(distinct node) AS nodes,min(t) AS first_ms,max(t) AS last_ms,
count(*) FILTER(WHERE node IS NULL) AS null_node,count(*) FILTER(WHERE t IS NULL) AS null_time,
count(*) FILTER(WHERE v IS NULL) AS null_value,count(*) FILTER(WHERE v<0) AS negative_value,count(*) FILTER(WHERE v=0) AS zero_value,
count(*) FILTER(WHERE try_cast(node AS INTEGER) NOT BETWEEN0 AND979 OR try_cast(node AS INTEGER) IS NULL) AS unmapped_node,
count(*) FILTER(WHERE t%1000<>0) AS subsecond_rows,min(v) AS min_w,max(v) AS max_w,quantile_cont(v,[0.01,0.5,0.99]) AS quantile_w,
count(distinct v) AS distinct_w,count(*) FILTER(WHERE v%100=0) AS multiple100_w FROM raw GROUP BY metric ORDER BY metric'''.replace('BETWEEN0 AND979','BETWEEN 0 AND 979'))
C.execute('''CREATE OR REPLACE TABLE cells AS SELECT metric,node,t,count(*) AS multiplicity,count(v) AS nonnull_count,min(v) AS lo,max(v) AS hi
FROM raw GROUP BY metric,node,t''')
report['keys_by_metric']=query('''SELECT metric,count(*) AS distinct_keys,count(*) FILTER(WHERE multiplicity>1) AS duplicated_keys,
sum(multiplicity-1) AS extra_rows,count(*) FILTER(WHERE lo<>hi) AS conflicting_keys,
count(*) FILTER(WHERE nonnull_count=0) AS all_null_keys,count(*) FILTER(WHERE nonnull_count>0 AND nonnull_count<multiplicity) AS null_mixed_keys,
max(multiplicity) AS max_multiplicity FROM cells GROUP BY metric ORDER BY metric''')
C.execute('''CREATE OR REPLACE TABLE clean AS SELECT metric,node,t,lo AS v FROM cells
WHERE node IS NOT NULL AND t IS NOT NULL AND lo=hi AND lo>=0''')
report['clean_policy']='One nonnegative identical nonnull value per node/metric/time; exact duplicates collapsed. Conflicts and all-null/negative cells excluded; null+one-value cells retained and counted separately. No rounding, imputation, state filtering or upper cutoff.'
report['phase_counts']=query('SELECT metric,(t/1000)::BIGINT%20 AS second_mod20,count(*) AS cells FROM clean GROUP BY metric,second_mod20 ORDER BY metric,second_mod20')
C.execute('''CREATE OR REPLACE TABLE gaps AS SELECT metric,node,t,t-lag(t) OVER(PARTITION BY metric,node ORDER BY t) AS gap_ms FROM clean''')
report['gap_frequencies']=query('SELECT metric,gap_ms,count(*) AS n FROM gaps WHERE gap_ms IS NOT NULL GROUP BY metric,gap_ms ORDER BY metric,n DESC')
report['gap_summary']=query('''SELECT metric,count(*) AS positive_gaps,min(gap_ms) AS min_gap_ms,max(gap_ms) AS max_gap_ms,
quantile_cont(gap_ms,[0.5,0.9,0.99]) AS quantile_gap_ms,count(*) FILTER(WHERE gap_ms=20000) AS exactly20s,
count(*) FILTER(WHERE gap_ms%20000=0) AS multiple20s FROM gaps WHERE gap_ms>0 GROUP BY metric''')
report['per_node']=query('''SELECT metric,node,count(*) AS cells,min(t) AS first_ms,max(t) AS last_ms,min(v) AS min_w,max(v) AS max_w,
quantile_cont(v,0.5) AS median_w,count(*) FILTER(WHERE v=0) AS zeros FROM clean GROUP BY metric,node ORDER BY metric,try_cast(node AS INTEGER)''')
save();print('Raw, key and cadence summaries complete',flush=True)
C.execute('''CREATE OR REPLACE TABLE psu AS SELECT a.node,a.t,a.v+b.v AS v FROM clean a JOIN clean b USING(node,t)
WHERE a.metric='ps0_input_power' AND b.metric='ps1_input_power' ''')
C.execute('''CREATE OR REPLACE TABLE triples AS SELECT a.node,a.t,a.v AS input_w,b.v AS total_w,b.v-a.v AS delta_w
FROM psu a JOIN clean b USING(node,t) WHERE b.metric='total_power' ''')
report['psu_by_node']=query('''SELECT node,count(*) AS cells,min(t) AS first_ms,max(t) AS last_ms,min(v) AS min_w,max(v) AS max_w,
quantile_cont(v,[0.01,0.5,0.99]) AS quantile_w,count(*) FILTER(WHERE v=0) AS zeros FROM psu GROUP BY node ORDER BY try_cast(node AS INTEGER)''')
report['triples']=query('''SELECT count(*) AS n,count(distinct node) AS nodes,min(delta_w) AS min_delta_w,max(delta_w) AS max_delta_w,
avg(delta_w) AS mean_delta_w,quantile_cont(delta_w,0.5) AS median_delta_w,quantile_cont(abs(delta_w),[0.5,0.9,0.99]) AS abs_delta_quantiles,
count(*) FILTER(WHERE delta_w=0) AS equal_values,count(*) FILTER(WHERE input_w=0) AS input_zero,count(*) FILTER(WHERE total_w=0) AS total_zero,
avg(delta_w::DOUBLE/input_w) FILTER(WHERE input_w>0) AS mean_relative_delta FROM triples''')[0]
report['triples_by_node']=query('''SELECT node,count(*) AS n,min(delta_w) AS min_delta_w,max(delta_w) AS max_delta_w,avg(delta_w) AS mean_delta_w,
quantile_cont(delta_w,0.5) AS median_delta_w,count(*) FILTER(WHERE delta_w=0) AS equal_values FROM triples GROUP BY node ORDER BY try_cast(node AS INTEGER)''')
report['simultaneity']={}
for name,source in [('total_power',"SELECT node,t FROM clean WHERE metric='total_power'"),('psu_sum','SELECT node,t FROM psu')]:
 C.execute('CREATE OR REPLACE TEMP TABLE selected AS '+source)
 nodes=C.execute('SELECT count(distinct node) FROM selected').fetchone()[0]
 hist=query('SELECT n_nodes,count(*) AS times FROM(SELECT t,count(*) AS n_nodes FROM selected GROUP BY t)GROUP BY n_nodes ORDER BY n_nodes')
 alltimes=query('SELECT t FROM selected GROUP BY t HAVING count(*)=? ORDER BY t',[nodes])
 pair=query("SELECT t FROM selected WHERE node IN('0','1') GROUP BY t HAVING count(*)=2 ORDER BY t")
 def times_summary(rows):
  ts=[x['t'] for x in rows]; run=best=1 if ts else 0;beststart=ts[0] if ts else None;start=beststart
  for a,b in zip(ts,ts[1:]):
   if b-a==20000:run+=1
   else:run=1;start=b
   if run>best:best=run;beststart=start
  return {'count':len(ts),'first_ms':ts[0] if ts else None,'last_ms':ts[-1] if ts else None,'first_two_ms':ts[:2],'longest_postselected_exact20s_run':{'cells':best,'first_ms':beststart,'last_ms':beststart+(best-1)*20000 if best else None}}
 report['simultaneity'][name]={'nodes':nodes,'node_count_per_time_histogram':hist,'all_observed_nodes':times_summary(alltimes),'preselected_nodes_0_and_1':times_summary(pair)}
report['states']='No Nagios/state slice acquired. Health, occupancy, online status and power-meter equivalence unresolved.'
report['verdict']={'schema':'PASS in retrieved complete members','exact_panel':'EXISTS' if all(x['preselected_nodes_0_and_1']['count']>=2 for x in report['simultaneity'].values()) else 'NOT ESTABLISHED','scientific_sufficiency':'UNASSESSED; no reliability, reserve savings, ownership, delivery or pooling claim'}
save();print(json.dumps({'raw_by_metric':report['raw_by_metric'],'keys_by_metric':report['keys_by_metric'],'gap_summary':report['gap_summary'],'triples':report['triples'],'simultaneity':{k:{a:b for a,b in v.items() if a!='node_count_per_time_histogram'} for k,v in report['simultaneity'].items()}},indent=2))
