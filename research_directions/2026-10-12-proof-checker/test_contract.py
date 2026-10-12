import unittest,json,copy,hashlib
import contract as c

def fixtures():
 cases=[];controls=[]
 for label in c.LABELS:
  for i in range(8):
   parts=[dict(id='a1',claim='A',label='supported',support=[['D1']],contradict=[]),dict(id='a2',claim='B',label=label,support=[['D2']] if label=='supported' else [],contradict=[['D2']] if label=='contradicted' else [])]
   whole,proofs,ids=c.aggregate_gold(parts);cases.append(dict(request_id=label+str(i),claim='A and B',label=whole,passages=[dict(id=x,text=x+'text') for x in ['D1','D2','D3']],components=parts,acceptable_evidence=proofs,relevant_evidence=ids))
 for label in c.LABELS:
  chosen=sorted([j for j in cases if j['label']==label],key=lambda j:hashlib.sha256(('order:'+j['request_id']).encode()).hexdigest())[:4]
  for i,j in enumerate(chosen):
   good=dict(verdict=label,evidence=[] if label=='insufficient' else j['acceptable_evidence'][0])
   if label=='insufficient':group='unsupported_decisive';bad=dict(verdict='supported' if i<2 else 'contradicted',evidence=['D1'])
   elif i<2:group='false_insufficient';bad=dict(verdict='insufficient',evidence=[])
   else:group='citation';bad=dict(verdict=label,evidence=['D1'])
   for accept,obj in [(True,good),(False,bad)]:
    pair='pair_'+j['request_id'];key='c_'+hashlib.sha256(('coop-proof-control:'+pair+':'+str(accept)).encode()).hexdigest()[:20]
    controls.append(dict(request_id=key,case_id=j['request_id'],candidate=obj,expected_accept=accept,pair_id=pair,error_group=group))
 controls.sort(key=lambda r:hashlib.sha256(('control-order:'+r['request_id']).encode()).hexdigest())
 primary={j['request_id']:json.dumps(dict(verdict=j['label'],evidence=[] if j['label']=='insufficient' else j['acceptable_evidence'][0])) for j in cases}
 inventories={j['request_id']:json.dumps({p['id']:{side:p[side] for side in ['support','contradict']} for p in j['components']}) for j in cases}
 return cases,controls,primary,inventories

class ProofTests(unittest.TestCase):
 def setUp(self):self.cases,self.controls,self.primary,self.inventories=fixtures();self.job=self.cases[0]
 def s(self):return c.summarize(self.cases,self.controls,self.primary,self.inventories)
 def change_inv(self,key,edit):
  obj=json.loads(self.inventories[key]);edit(obj);self.inventories[key]=json.dumps(obj)
 def test_perfect(self):
  s=self.s();self.assertTrue(s['engineering_gate_passed']);self.assertEqual(s['inventory_quality_correct'],24);self.assertEqual(s['inventory_component_correct'],48);self.assertEqual(s['format_variant_checks'],96);self.assertFalse(s['native_sensitivity_observed'])
 def test_false_insufficient_is_caught(self):
  self.primary['supported0']='{"verdict":"insufficient","evidence":[]}'
  s=self.s();self.assertEqual((s['baseline_correct'],s['automatic_correct'],s['semantic_errors_caught']),(23,23,1));self.assertTrue(s['engineering_gate_passed'])
 def test_false_insufficient_shared_error_is_accepted_and_blocks(self):
  self.primary['supported0']='{"verdict":"insufficient","evidence":[]}'
  self.change_inv('supported0',lambda o:o['a2'].update(support=[]));s=self.s();self.assertEqual(s['automatic_errors'],1);self.assertFalse(s['engineering_gate_passed']);self.assertEqual(s['inventory_quality_correct'],23)
 def test_missing_component_citation_is_rejected(self):
  self.primary['supported0']='{"verdict":"supported","evidence":["D1"]}';self.assertEqual(self.s()['semantic_errors_caught'],1)
 def test_contradiction_of_one_component_refutes_conjunction(self):
  j=next(j for j in self.cases if j['request_id']=='contradicted0');i=json.loads(self.inventories[j['request_id']]);i['a1']['support']=[]
  d=c.decide(self.primary[j['request_id']],json.dumps(i),j);self.assertTrue(d['accept'])
 def test_both_sides_for_atom_is_conflict_referral(self):
  self.change_inv('supported0',lambda o:o['a1'].update(contradict=[['D3']]));s=self.s();self.assertEqual(s['inventory_usable'],23);self.assertFalse(s['engineering_gate_passed']);self.assertEqual(s['referrals'],1)
 def test_unknown_id_unusable_not_proof(self):
  self.change_inv('supported0',lambda o:o['a1'].update(support=[['D9']]));s=self.s();self.assertEqual(s['inventory_schema_valid'],24);self.assertEqual(s['inventory_usable'],23);self.assertFalse(s['engineering_gate_passed'])
 def test_empty_outer_bad(self):self.assertFalse(c.parse_inventory('{}',self.job)['schema_valid'])
 def test_duplicate_key_bad(self):self.assertFalse(c.parse_inventory('{"a1":{},"a1":{},"a2":{}}',self.job)['schema_valid'])
 def test_duplicate_set_permutation_bad(self):
  obj=json.loads(self.inventories['supported0']);obj['a1']['support']=[['D1','D2'],['D2','D1']];self.assertFalse(c.parse_inventory(json.dumps(obj),self.job)['schema_valid'])
 def test_schema_limits(self):
  for bad in [[[]],[['D1','D1']],[['D1','D2','D3','D4']],[[1]]]:
   obj=json.loads(self.inventories['supported0']);obj['a1']['support']=bad;self.assertFalse(c.parse_inventory(json.dumps(obj),self.job)['schema_valid'])
 def test_no_primary_or_gold_in_inventory_wire(self):
  j=copy.deepcopy(self.job);wire=c.inventory_job(j);j['label']='SECRET';j['acceptable_evidence']='SECRET';j['relevant_evidence']='SECRET'
  for p in j['components']:p.update(label='SECRET',support='SECRET',contradict='SECRET',rationale='SECRET')
  self.assertEqual(c.inventory_job(j),wire);self.assertNotIn('SECRET',wire['prompt'])
 def test_decision_does_not_require_gold_or_components(self):
  bare={'passages':self.job['passages']};d=c.decide(self.primary['supported0'],self.inventories['supported0'],bare);self.assertTrue(d['accept'])
 def test_alternative_valid_proof_is_accepted(self):
  i=json.loads(self.inventories['supported0']);i['a1']['support'].append(['D3']);d=c.decide('{"verdict":"supported","evidence":["D3","D2"]}',json.dumps(i),self.job);self.assertTrue(d['accept'])
 def test_omitted_alternative_causes_false_rejection(self):
  j=copy.deepcopy(self.job);j['components'][0]['support'].append(['D3']);j['label'],j['acceptable_evidence'],j['relevant_evidence']=c.aggregate_gold(j['components']);p='{"verdict":"supported","evidence":["D3","D2"]}';self.assertTrue(c.score(p,j)['quality_pass']);self.assertFalse(c.decide(p,self.inventories['supported0'],j)['accept']);q=c.inventory_quality(self.inventories['supported0'],j);self.assertTrue(q['quality_pass']);self.assertFalse(q['all_alternatives_recovered'])
 def test_irrelevant_added_citation_reject(self):self.assertFalse(c.decide('{"verdict":"supported","evidence":["D1","D2","D3"]}',self.inventories['supported0'],self.job)['accept'])
 def test_insufficient_requires_empty_evidence(self):
  j=next(x for x in self.cases if x['label']=='insufficient');self.assertFalse(c.decide('{"verdict":"insufficient","evidence":["D1"]}',self.inventories[j['request_id']],j)['accept'])
 def test_malformed_primary_format_referral(self):
  self.primary['supported0']='bad';s=self.s();self.assertEqual(s['format_referrals'],1);self.assertEqual(s['semantic_errors_caught'],0);self.assertEqual(s['referrals'],1)
 def test_bad_inventory_not_semantic_catch(self):
  self.primary['supported0']='{"verdict":"insufficient","evidence":[]}';self.inventories['supported0']='bad';s=self.s();self.assertEqual(s['semantic_errors_caught'],0);self.assertFalse(s['engineering_gate_passed'])
 def test_missing_or_extra_raw_map_blocks(self):
  self.primary.pop('supported0');self.assertFalse(self.s()['input_complete']);self.primary['EXTRA']='{}';self.assertFalse(self.s()['input_complete'])
 def test_reject_all_not_success(self):
  self.inventories={k:'bad' for k in self.inventories};s=self.s();self.assertFalse(s['engineering_gate_passed']);self.assertEqual(s['automatic_correct'],0)
 def test_source_grounding_semantic_error_separate(self):
  self.change_inv('supported0',lambda o:o['a1'].update(support=[['D3']]));s=self.s();self.assertEqual(s['inventory_component_correct'],47);self.assertEqual(s['inventory_quality_correct'],23)
 def test_control_contract(self):c.validate_controls(self.cases,self.controls)
 def test_control_selection_tamper_rejected(self):
  selected={r['case_id'] for r in self.controls};old=next(r['case_id'] for r in self.controls if r['case_id'].startswith('supported'));new=next(j['request_id'] for j in self.cases if j['label']=='supported' and j['request_id'] not in selected)
  for r in self.controls:
   if r['case_id']==old:r['case_id']=new
  with self.assertRaisesRegex(ValueError,'prospective'):c.validate_controls(self.cases,self.controls)
 def test_control_wrong_citation_still_different_construction_rejected(self):
  r=next(r for r in self.controls if r['error_group']=='citation' and not r['expected_accept']);r['candidate']['evidence']=[]
  with self.assertRaisesRegex(ValueError,'prospective'):c.validate_controls(self.cases,self.controls)
 def test_control_order_tamper_rejected(self):
  self.controls.reverse()
  with self.assertRaisesRegex(ValueError,'prospective'):c.validate_controls(self.cases,self.controls)
 def test_false_insufficient_controls_present(self):
  bad=[x for x in self.controls if x['error_group']=='false_insufficient' and not x['expected_accept']];self.assertEqual(len(bad),4);self.assertTrue(all(x['candidate']=={'verdict':'insufficient','evidence':[]} for x in bad))
 def test_inventory_has_no_claimed_overall_verdict(self):
  obj=json.loads(self.inventories['supported0']);obj['verdict']='supported';self.assertFalse(c.parse_inventory(json.dumps(obj),self.job)['schema_valid'])
 def test_json_invariance_is_deterministic_only(self):
  a='{"verdict":"supported","evidence":["D1","D2"]}';z=' { "evidence" : [ "D2", "D1" ], "verdict" : "supported" } '
  self.assertEqual(c.decide(a,self.inventories['supported0'],self.job)['accept'],c.decide(z,self.inventories['supported0'],self.job)['accept'])
if __name__=='__main__':unittest.main()
