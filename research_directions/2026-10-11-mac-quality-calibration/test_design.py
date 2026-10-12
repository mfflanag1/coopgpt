import copy,json,unittest
from design import tasks,wire_job,score,SCHEMA
class DesignTests(unittest.TestCase):
 def setUp(self):self.jobs=tasks(12,1,'test');self.job=self.jobs[0]
 def test_all_cells_once(self):self.assertEqual({(j['input_rows'],j['keep_count']) for j in self.jobs},{(n,k) for n in (32,96,192) for k in (4,12,24)})
 def test_gold_from_raw(self):
  for j in self.jobs:
   self.assertEqual(len(j['expected']['records']),j['keep_count'])
   self.assertEqual(j['expected']['records'],[{k:r[k] for k in ('id','value')} for r in j['rows'] if r['flag']=='KEEP'])
   self.assertTrue(score(json.dumps(j['expected']),j))
 def test_no_gold_in_wire_or_schema(self):
  for c in ('A','B'):
   w=wire_job(self.job,c);self.assertEqual(set(w),{'request_id','arrival_offset_s','prompt','max_output_tokens','format'});self.assertNotIn('expected',w['prompt']);self.assertEqual(w['format'],SCHEMA)
  self.assertNotIn('enum',json.dumps(SCHEMA));self.assertNotIn('minItems',json.dumps(SCHEMA));self.assertNotIn('maxItems',json.dumps(SCHEMA))
 def test_fresh_tasks(self):self.assertFalse({json.dumps(j['rows']) for j in tasks(202610111,1,'dev')}&{json.dumps(j['rows']) for j in tasks(202610112,3,'confirm')})
 def test_json_whitespace_key_order_only(self):
  o={'records':[{'value':r['value'],'id':r['id']} for r in self.job['expected']['records']]};self.assertTrue(score(json.dumps(o,indent=2),self.job))
 def test_wrong_selection_type_and_order_fail(self):
  base=self.job['expected']
  variants=[]
  for kind in ('missing','extra','wrong','reordered','number','key'):
   v=copy.deepcopy(base)
   if kind=='missing':v['records'].pop()
   if kind=='extra':v['records'].append(v['records'][0])
   if kind=='wrong':v['records'][0]['value']='000'
   if kind=='reordered':v['records'].reverse()
   if kind=='number':v['records'][0]['value']=int(v['records'][0]['value'])
   if kind=='key':v['records'][0]['extra']='x'
   variants.append(v)
  for v in variants:self.assertFalse(score(json.dumps(v),self.job))
 def test_duplicates_and_trailing_and_markdown_fail(self):
  t=json.dumps(self.job['expected'])
  for v in [t+' junk','```json\n'+t+'\n```','{"records":[],"records":'+json.dumps(self.job['expected']['records'])+'}',t.replace('"records"','"other"')]:self.assertFalse(score(v,self.job))
if __name__=='__main__':unittest.main()
