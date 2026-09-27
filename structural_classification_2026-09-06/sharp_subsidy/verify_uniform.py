"""Uses the independent coefficient checker, not the construction formula."""
import json
from pathlib import Path
from verify_deletion import check,require


def run():
 rows=json.loads(Path(__file__).with_name('UNIFORM_TEMPLATE_CERTIFICATES.json').read_text())
 expected={(2*q+1,tuple((s,q+s,s-1 if s else 2*q)for s in range(q)))for q in range(1,13)}
 expected.add((7,((0,1,2),(3,0,4),(5,6,0))))
 actual={(r['m'],tuple(tuple(t)for t in r['P']))for r in rows}
 require(len(rows)==len(expected)and actual==expected,'missing or repeated configurations')
 entries=sum(check(r)for r in rows)
 bad=dict(rows[-1]);bad['packings']=[]
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('negative control accepted')
 print(json.dumps({'status':'PASS','independent_pair_domination_checks':True,'configurations':len(rows),'rational_packing_entries':entries,'negative_controls':1}))


if __name__=='__main__':run()
