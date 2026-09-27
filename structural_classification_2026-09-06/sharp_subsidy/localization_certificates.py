"""Construct and independently check near-ceiling localization samples."""
from pathlib import Path
from fractions import Fraction as F
import json,sys
from mixed_donor_template import construct
from localization_parameter import parameter
from verify_mixed_donor import check

def main():
 root=Path(__file__).parent
 old=json.loads((root/'MIXED_DONOR_CERTIFICATES.json').read_text())
 if '--generate' in sys.argv:
  rows=[]
  for v in old:
   d=construct(v['m'],v['P'],t=parameter(v['m'],v['P']));d['case']=v['case'];rows.append(d)
  (root/'LOCALIZATION_CERTIFICATES.json').write_text(json.dumps(rows)+'\n')
 rows=json.loads((root/'LOCALIZATION_CERTIFICATES.json').read_text())
 if [(r['case'],r['m'],r['P'])for r in rows]!=[(r['case'],r['m'],r['P'])for r in old]:raise ValueError('inventory')
 count=sum(check(d,localization=True)for d in rows)
 if not any(F(d['parameter'])>F(4,5)for d in rows):raise ValueError('no improved branch')
 bad=dict(rows[0],packings=[])
 try:check(bad,localization=True)
 except ValueError:pass
 else:raise ValueError('empty packing accepted')
 print(json.dumps({'status':'PASS','cases':len(rows),'packing_entries':count,'negative_controls':1,'scope':'sample coefficient domination for localization parameter'}))
if __name__=='__main__':main()
