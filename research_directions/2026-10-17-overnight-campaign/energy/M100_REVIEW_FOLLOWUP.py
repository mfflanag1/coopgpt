"""Focused independent-review checks against existing derived tables only."""
import duckdb,json,datetime
from pathlib import Path
B=Path('/private/tmp/coopgpt-overnight-20261017');c=duckdb.connect('/private/tmp/coopgpt-m100-raw-20261017/inspection.duckdb',read_only=True)
def q(sql):
 cur=c.execute(sql);cols=[x[0]for x in cur.description];return[dict(zip(cols,x))for x in cur.fetchall()]
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Focused QA; no new acquisition or physical fault inference.'}
r['canonical_node_ids']=q('''SELECT count(distinct node) AS string_ids,count(distinct try_cast(node AS INTEGER)) AS integer_ids,
min(try_cast(node AS INTEGER)) AS min_id,max(try_cast(node AS INTEGER)) AS max_id,
count(*) FILTER(WHERE node<>try_cast(node AS INTEGER)::VARCHAR) AS noncanonical_rows FROM raw''')[0]
r['missing_total_at_complete_psu']=q('''WITH fullps AS(SELECT t FROM psu GROUP BY t HAVING count(*)=980),nodes AS(SELECT DISTINCT node FROM psu)
SELECT n.node,count(*) AS missing_times FROM fullps f CROSS JOIN nodes n LEFT JOIN clean x ON x.metric='total_power' AND x.node=n.node AND x.t=f.t
WHERE x.node IS NULL GROUP BY n.node ORDER BY missing_times DESC,try_cast(n.node AS INTEGER) LIMIT 30''')
r['complete_total_gap_histogram']=q('''WITH ft AS(SELECT t FROM clean WHERE metric='total_power'GROUP BY t HAVING count(*)=980),g AS(SELECT t,t-lag(t)OVER(ORDER BY t)AS gap_ms FROM ft)
SELECT gap_ms,count(*) AS n FROM g WHERE gap_ms IS NOT NULL GROUP BY gap_ms ORDER BY gap_ms''')
r['missing_total_after_complete_times_when_psu_complete']=q('''WITH ft AS(SELECT t FROM clean WHERE metric='total_power'GROUP BY t HAVING count(*)=980),fp AS(SELECT t FROM psu GROUP BY t HAVING count(*)=980),nexts AS(SELECT ft.t+20000 AS t FROM ft JOIN fp ON fp.t=ft.t+20000),nodes AS(SELECT DISTINCT node FROM psu)
SELECT n.node,count(*) AS missing_times FROM nexts f CROSS JOIN nodes n LEFT JOIN clean x ON x.metric='total_power' AND x.node=n.node AND x.t=f.t
WHERE x.node IS NULL GROUP BY n.node ORDER BY missing_times DESC,try_cast(n.node AS INTEGER) LIMIT 30''')
r['examined_adjacent_complete_psu_times']=q('''WITH ft AS(SELECT t FROM clean WHERE metric='total_power'GROUP BY t HAVING count(*)=980),fp AS(SELECT t FROM psu GROUP BY t HAVING count(*)=980)
SELECT count(*) AS n FROM ft JOIN fp ON fp.t=ft.t+20000''')[0]['n']
r['per_node_meter_count_difference']=q('''WITH p AS(SELECT node,count(*)AS n FROM psu GROUP BY node),t AS(SELECT node,count(*)AS n FROM clean WHERE metric='total_power'GROUP BY node)
SELECT p.node,p.n AS psu_cells,t.n AS total_cells,p.n-t.n AS missing_total_given_psu FROM p JOIN t USING(node)ORDER BY missing_total_given_psu DESC,try_cast(p.node AS INTEGER)LIMIT 20''')
(B/'checks/M100_REVIEW_FOLLOWUP.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
