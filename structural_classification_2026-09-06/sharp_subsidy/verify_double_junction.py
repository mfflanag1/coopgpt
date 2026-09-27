"""Exact verification of the first configuration outside the uniform criterion."""
import json
from pathlib import Path
from verify_deletion import check,require


def run():
 d=json.loads(Path(__file__).with_name('DOUBLE_JUNCTION_DELETION.json').read_text())
 require(d['m']==11 and d['P']==[[0,1,2],[3,0,4],[5,6,0],[1,7,8],[9,10,1]],'wrong configuration')
 count=check(d)
 bad=dict(d);bad['packings']=[]
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('negative control accepted')
 print(json.dumps({'status':'PASS','m':11,'partial_matching_teams':5,'rational_entries':count,'negative_controls':1,'scope':'fixed two-junction configuration, all nonnegative pair coefficients'}))


if __name__=='__main__':run()
