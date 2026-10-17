"""Extra descriptive availability and meter-granularity summaries; no inference."""
from pathlib import Path
import datetime,duckdb,json,math
BASE=Path('/private/tmp/coopgpt-overnight-20261017');RAW=Path('/private/tmp/coopgpt-m100-raw-20261017')
c=duckdb.connect(str(RAW/'inspection.duckdb'),read_only=True)
def q(sql):
 cur=c.execute(sql);cols=[x[0] for x in cur.description];return[dict(zip(cols,x))for x in cur.fetchall()]
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Derived descriptive availability within retrieved release, not inferred sensor downtime.'}
report['timeline']=q("SELECT 'psu_sum' AS metric,t,count(*) AS nodes FROM psu GROUP BY t UNION ALL SELECT metric,t,count(*) AS nodes FROM clean WHERE metric='total_power' GROUP BY metric,t ORDER BY metric,t")
report['global_gaps']=q('''WITH times AS(SELECT DISTINCT metric,t FROM clean),gs AS(SELECT metric,t,t-lag(t)OVER(PARTITION BY metric ORDER BY t)AS gap FROM times)
SELECT metric,t-gap AS from_ms,t AS to_ms,gap FROM gs WHERE gap>60000 ORDER BY gap DESC LIMIT20'''.replace('LIMIT20','LIMIT 20'))
report['granularity']={}
for metric in ['ps0_input_power','ps1_input_power','total_power']:
 vals=[x[0]for x in c.execute('SELECT DISTINCT v FROM clean WHERE metric=? ORDER BY v',[metric]).fetchall()]
 report['granularity'][metric]={'distinct_values':len(vals),'gcd_w':math.gcd(*vals),'gcd_adjacent_differences_w':math.gcd(*[b-a for a,b in zip(vals,vals[1:])]),'interpretation':'Observed integer-value granularity only, not sensor accuracy.'}
report['delta_histogram']=q('SELECT delta_w,count(*) AS n FROM triples GROUP BY delta_w ORDER BY delta_w')
report['psu_key_count']=c.execute('SELECT count(*) FROM psu').fetchone()[0]
report['within_observed_range_20s_grid']=[]
for metric in ['ps0_input_power','ps1_input_power','total_power']:
 lo,hi,nn,ct=c.execute('SELECT min(t),max(t),count(distinct node),count(*) FROM clean WHERE metric=?',[metric]).fetchone();grid=(hi-lo)//20000+1
 report['within_observed_range_20s_grid'].append({'metric':metric,'half_open_start_ms':lo,'half_open_stop_ms':hi+20000,'nodes':nn,'grid_times':grid,'observed_cells':ct,'node_time_grid_cells':nn*grid,'observed_fraction':ct/(nn*grid),'assumption':'Explicit phase-zero20s grid across global observed extent. Unobserved archive keys are not automatically sensor downtime.'})
report['monthly_members_complete']='See full archive header enumeration in M100_RANGE_INTAKE.json;3target metric members each uniquely found. Full tar hash not validated.'
(BASE/'checks/M100_PANEL_SUPPLEMENT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in('timeline','delta_histogram')},indent=2))
