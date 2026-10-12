import copy,hashlib,json,unittest
import contract as c

def fixture():
 cases=[];controls=[]
 for label in c.LABELS:
  for i in range(8):
   key=label+str(i);cases.append(dict(request_id=key,label=label,claim='Claim '+key,passages=[{'id':'D1','text':'Premise'},{'id':'D2','text':'Unrelated'}],acceptable_evidence=[] if label=='insufficient' else [['D1']],relevant_evidence=[] if label=='insufficient' else ['D1']))
 for j in cases:
  i=int(j['request_id'][-1]);label=j['label']
  if i>=4:continue
  good={'verdict':label,'evidence':[] if label=='insufficient' else ['D1']}
  bad=copy.deepcopy(good)
  if label=='insufficient':group='missing_premise';bad={'verdict':'supported' if i<2 else 'contradicted','evidence':['D1']}
  elif i<2:group='wrong_verdict';bad['verdict']='contradicted' if label=='supported' else 'supported'
  else:group='citation';bad['evidence']=['D2']
  for valid,answer in [(True,good),(False,bad)]:controls.append(dict(request_id='c_'+hashlib.sha256((j['request_id']+str(valid)).encode()).hexdigest()[:20],case_id=j['request_id'],candidate=answer,expected_accept=valid,pair_id=j['request_id'],error_group=group))
 return cases,controls

def outputs(cases,controls):
 primary={j['request_id']:json.dumps({'verdict':j['label'],'evidence':[] if j['label']=='insufficient' else ['D1']}) for j in cases}
 checker={'n_'+j['request_id']:'{"accept":true}' for j in cases}
 checker.update({x['request_id']:json.dumps({'accept':x['expected_accept']}) for x in controls})
 return primary,checker

class Tests(unittest.TestCase):
 def setUp(self):self.cases,self.controls=fixture();self.primary,self.checker=outputs(self.cases,self.controls)
 def summary(self):return c.summarize(self.cases,self.controls,self.primary,self.checker)
 def test_perfect_native_does_not_identify_sensitivity(self):
  s=self.summary();self.assertTrue(s['engineering_gate_passed']);self.assertFalse(s['native_sensitivity_observed']);self.assertEqual(s['semantic_errors_caught'],0);self.assertEqual(s['automatic_correct'],24)
 def test_one_semantic_error_caught_without_correcting(self):
  self.primary['insufficient0']='{"verdict":"contradicted","evidence":["D1"]}';self.checker['n_insufficient0']='{"accept":false}'
  s=self.summary();self.assertTrue(s['engineering_gate_passed']);self.assertEqual((s['baseline_correct'],s['automatic_correct'],s['semantic_errors_caught'],s['referrals']),(23,23,1,1))
 def test_accepted_error_blocks_even_otherwise_perfect(self):
  self.primary['insufficient0']='{"verdict":"contradicted","evidence":["D1"]}';s=self.summary();self.assertFalse(s['engineering_gate_passed']);self.assertEqual(s['automatic_errors'],1)
 def test_reject_all_is_not_success(self):
  self.checker={k:'{"accept":false}' for k in self.checker};s=self.summary();self.assertFalse(s['engineering_gate_passed']);self.assertEqual((s['automatic_correct'],s['constructed_valid_retained']),(0,0))
 def test_accept_all_fails_control_sensitivity(self):
  self.checker={k:'{"accept":true}' for k in self.checker};s=self.summary();self.assertFalse(s['engineering_gate_passed']);self.assertEqual(s['constructed_invalid_rejected'],0)
 def test_retention_gate_exact_90_percent(self):
  for i in range(3):self.checker['n_supported'+str(i)]='{"accept":false}'
  s=self.summary();self.assertGreaterEqual(s['automatic_correct'],18);self.assertFalse(s['native_gate_passed'])
 def test_retention_boundary_20_correct_18_retained(self):
  for j in self.cases[:4]:self.primary[j['request_id']]='bad';self.checker['n_'+j['request_id']]='{"accept":false}'
  for j in self.cases[4:6]:self.checker['n_'+j['request_id']]='{"accept":false}'
  s=self.summary();self.assertEqual((s['baseline_correct'],s['automatic_correct']),(20,18));self.assertTrue(s['native_gate_passed'])
  self.checker['n_'+self.cases[6]['request_id']]='{"accept":false}';self.assertFalse(self.summary()['native_gate_passed'])
 def test_malformed_checker_acceptance_reported_but_not_automatic(self):
  self.primary['insufficient0']='not JSON';s=self.summary();self.assertEqual(s['checker_accepted_malformed'],1);self.assertEqual(s['automatic_errors'],0);self.assertEqual(s['format_referrals'],1)
 def test_correct_automatic_floor_independent_of_retention(self):
  for j in self.cases[:7]:self.primary[j['request_id']]='bad';self.checker['n_'+j['request_id']]='{"accept":false}'
  s=self.summary();self.assertEqual(s['automatic_correct'],17);self.assertEqual(s['baseline_correct'],17);self.assertFalse(s['native_gate_passed'])
 def test_malformed_primary_is_format_not_semantic_catch(self):
  self.primary['insufficient0']='not JSON';s=self.summary();self.assertTrue(s['engineering_gate_passed']);self.assertEqual(s['format_referrals'],1);self.assertEqual(s['semantic_errors_caught'],0);self.assertFalse(s['native_sensitivity_observed'])
 def test_checker_failure_routes_review_and_blocks_gate(self):
  self.checker['n_supported0']='{"accept":1}';s=self.summary();self.assertFalse(s['engineering_gate_passed']);self.assertEqual(s['referrals'],1)
 def test_control_one_false_reject_allowed_two_not(self):
  good=[r for r in self.controls if r['expected_accept']]
  self.checker[good[0]['request_id']]='{"accept":false}';self.assertTrue(self.summary()['control_gate_passed'])
  self.checker[good[1]['request_id']]='{"accept":false}';self.assertFalse(self.summary()['control_gate_passed'])
 def test_one_bad_control_accepted_blocks(self):
  bad=next(r for r in self.controls if not r['expected_accept']);self.checker[bad['request_id']]='{"accept":true}';self.assertFalse(self.summary()['engineering_gate_passed'])
 def test_checker_parser_strict(self):
  for value in ['{"accept":1}','{"accept":"false"}','{"accept":true,"x":0}','{"accept":true,"accept":false}','{"accept":NaN}','[]','['*1200+'0'+']'*1200]:self.assertFalse(c.parse_check(value)['schema_valid'])
  self.assertEqual(c.parse_check(' {"accept": false} '),{'schema_valid':True,'accept':False})
 def test_complete_denominator_required(self):
  self.checker.pop('n_supported0');self.assertFalse(self.summary()['engineering_gate_passed'])
  self.primary['EXTRA']='{}';self.assertFalse(self.summary()['input_complete'])
 def test_metadata_not_in_wire(self):
  j=copy.deepcopy(self.cases[0]);a=c.primary_job(j);b=c.checker_job(j,'RAW','n_x')
  for k in ['label','rationale','acceptable_evidence','relevant_evidence','source_id']:j[k]='SECRET'
  self.assertEqual(a,c.primary_job(j));self.assertEqual(b,c.checker_job(j,'RAW','n_x'))
 def test_exact_proposal_and_checker_cap(self):
  w=c.checker_job(self.cases[0],' \n{"x":1}\n','n_test');self.assertIn('Proposed answer:\n \n{"x":1}\n\n\nAudit JSON:',w['prompt']);self.assertEqual(w['max_output_tokens'],64);self.assertIs(w['think'],False)
 def test_valid_control_pairs(self):c.valid_controls(self.cases,self.controls)
 def test_fake_valid_control_rejected(self):
  bad=next(r for r in self.controls if not r['expected_accept']);bad['expected_accept']=True
  with self.assertRaises(ValueError):c.valid_controls(self.cases,self.controls)
 def test_schema_only_cannot_discriminate_constructed_controls(self):
  for r in self.controls:
   j=next(j for j in self.cases if j['request_id']==r['case_id']);self.assertTrue(c.score(json.dumps(r['candidate']),j)['schema_valid'])
if __name__=='__main__':unittest.main()
