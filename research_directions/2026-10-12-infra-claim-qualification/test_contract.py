import copy,json,unittest
from pathlib import Path
import contract as c

class ContractTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.cases=c.validate_sources(Path(__file__).resolve().parent)
 def job(self,label='supported'):return copy.deepcopy(next(x for x in self.cases if x['label']==label))
 def answer(self,job):return {'verdict':job['label'],'evidence':job['acceptable_evidence'][0] if job['acceptable_evidence'] else []}
 def rows(self):return [dict(request_id=j['request_id'],label=j['label'],**c.score(json.dumps(self.answer(j)),j)) for j in self.cases]
 def test_all_gold_witnesses_score_and_gate(self):
  for j in self.cases:
   for proof in j['acceptable_evidence'] or [[]]:self.assertTrue(c.score(json.dumps(dict(verdict=j['label'],evidence=proof)),j)['quality_pass'])
  self.assertTrue(c.gate(self.rows()))
 def test_strict_json_failures(self):
  for text in ['{}','{"verdict":"supported","evidence":[],"x":1}','{"verdict":"supported","verdict":"insufficient","evidence":[]}','{"verdict":true,"evidence":[]}','{"verdict":"SUPPORTED","evidence":[]}','{"verdict":"supported","evidence":[1]}','{"verdict":"supported","evidence":["D1","D1"]}','{"verdict":"supported","evidence":["D1","D2","D3","D4"]}','{"verdict":NaN,"evidence":[]}','[]','['*1100+'0'+']'*1100]:
   with self.subTest(text=text[:80]):self.assertFalse(c.score(text,self.job())['schema_valid'])
 def test_unknown_or_irrelevant_citation_fails(self):
  j=self.job();p=self.answer(j);p['evidence']=['UNKNOWN'];self.assertFalse(c.score(json.dumps(p),j)['quality_pass'])
  wrong=next(x['id'] for x in j['passages'] if x['id'] not in j['relevant_evidence']);p['evidence']=list(j['acceptable_evidence'][0])+[wrong];self.assertFalse(c.score(json.dumps(p),j)['quality_pass'])
 def test_incomplete_multiblock_proof_fails(self):
  j=next(x for x in self.cases if x['acceptable_evidence'] and all(len(p)>1 for p in x['acceptable_evidence']))
  p=self.answer(j);p['evidence']=p['evidence'][:-1];self.assertFalse(c.score(json.dumps(p),j)['evidence_correct'])
 def test_key_and_citation_order_irrelevant(self):
  j=self.job();p=self.answer(j);p['evidence']=list(reversed(p['evidence']));self.assertTrue(c.score(json.dumps({'evidence':p['evidence'],'verdict':p['verdict']}),j)['quality_pass'])
 def test_insufficient_requires_empty_list(self):
  j=self.job('insufficient');self.assertTrue(c.score(json.dumps(self.answer(j)),j)['quality_pass']);self.assertFalse(c.score('{"verdict":"insufficient","evidence":["D1"]}',j)['quality_pass'])
 def test_wrong_label_with_correct_evidence_fails(self):
  j=self.job();p=self.answer(j);p['verdict']='contradicted';r=c.score(json.dumps(p),j);self.assertTrue(r['evidence_correct']);self.assertFalse(r['quality_pass'])
 def test_gold_metadata_never_in_wire(self):
  j=self.job();before=c.wire_job(j)
  for key in ['label','acceptable_evidence','relevant_evidence','rationale','source_id','reasoning']:j[key]='SECRET_CANARY'
  self.assertEqual(before,c.wire_job(j));self.assertNotIn('SECRET_CANARY',str(before));self.assertIs(before['think'],False)
 def test_gate_rejects_missing_duplicate_and_fake_flags(self):
  for change in ['missing','duplicate','intflag','inconsistent']:
   r=self.rows()
   if change=='missing':r.pop()
   elif change=='duplicate':r[1]=r[0]
   elif change=='intflag':r[0]['quality_pass']=1
   else:r[0]['quality_pass']=False
   self.assertFalse(c.gate(r))
 def test_gate_two_evidence_failures_separate_labels_allowed(self):
  r=self.rows()
  for label in ['supported','contradicted']:
   row=next(x for x in r if x['label']==label);row.update(evidence_correct=False,quality_pass=False)
  self.assertTrue(c.gate(r))
 def test_gate_one_insufficient_failure_blocks(self):
  r=self.rows();row=next(x for x in r if x['label']=='insufficient');row.update(evidence_correct=False,quality_pass=False);self.assertFalse(c.gate(r))
 def test_gate_false_support_blocks_even_23_correct(self):
  r=self.rows();row=next(x for x in r if x['label']=='contradicted');row.update(verdict_correct=False,quality_pass=False);row['prediction']['verdict']='supported';self.assertFalse(c.gate(r))
 def test_gate_cannot_hide_weak_label(self):
  r=self.rows()
  for row in [x for x in r if x['label']=='supported'][:2]:row.update(evidence_correct=False,quality_pass=False)
  self.assertFalse(c.gate(r))
if __name__=='__main__':unittest.main()
