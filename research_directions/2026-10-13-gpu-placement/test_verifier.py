import copy,json,unittest
from verifier import strict_loads,validate_manifest,verify_plan

def fixture():
 m={'schema_version':1,'nodes':[{'id':'n1','owner':'o1','cpu_units':8,'ram_mib':16384,'gpus':[{'id':'g1','family':'A','vram_mib':16384},{'id':'g2','family':'A','vram_mib':16384}]},{'id':'n2','owner':'o2','cpu_units':8,'ram_mib':16384,'gpus':[{'id':'g3','family':'B','vram_mib':32768}]}],'jobs':[{'id':'j1','priority':7,'cpu_units':4,'ram_mib':8192,'gpu_count':1,'min_vram_mib':16384,'allowed_families':['A','B'],'allowed_owners':['o1','o2']},{'id':'j2','priority':6,'cpu_units':4,'ram_mib':8192,'gpu_count':1,'min_vram_mib':16384,'allowed_families':['A'],'allowed_owners':['o1']}]}
 p={'schema_version':1,'placements':[{'job':'j1','node':'n1','gpus':['g1']},{'job':'j2','node':'n1','gpus':['g2']}],'deferred':[]}
 return m,p
_MISSING=object()
class VerifierTests(unittest.TestCase):
 def setUp(self):self.m,self.p=fixture()
 def bad(self,p=_MISSING):
  r=verify_plan(self.m,self.p if p is _MISSING else p);self.assertEqual(set(r),{'valid','errors','priority','admitted'});self.assertFalse(r['valid']);self.assertTrue(r['errors']);self.assertIsNone(r['priority']);self.assertIsNone(r['admitted'])
 def test_valid_exact_boundary(self):self.assertEqual(verify_plan(self.m,self.p),dict(valid=True,errors=[],priority=13,admitted=2))
 def test_order_irrelevant(self):self.p['placements'].reverse();self.assertTrue(verify_plan(self.m,self.p)['valid'])
 def test_no_mutation(self):
  before=copy.deepcopy((self.m,self.p));verify_plan(self.m,self.p);self.assertEqual((self.m,self.p),before)
 def test_defer_all_feasible_not_infeasible_proof(self):self.assertEqual(verify_plan(self.m,dict(schema_version=1,placements=[],deferred=['j1','j2'])),dict(valid=True,errors=[],priority=0,admitted=0))
 def test_no_jobs(self):self.m['jobs']=[];self.assertTrue(verify_plan(self.m,dict(schema_version=1,placements=[],deferred=[]))['valid'])
 def test_missing_job(self):self.p['placements'].pop();self.bad()
 def test_duplicate_job(self):self.p['placements'][1]['job']='j1';self.bad()
 def test_duplicate_deferred(self):self.bad(dict(schema_version=1,placements=[],deferred=['j1','j2','j2']))
 def test_placed_and_deferred(self):self.p['deferred']=['j1'];self.bad()
 def test_reused_gpu(self):self.p['placements'][1]['gpus']=['g1'];self.bad()
 def test_unknown_entities(self):
  for key in ['job','node']:
   p=copy.deepcopy(self.p);p['placements'][0][key]='missing';self.bad(p)
  p=copy.deepcopy(self.p);p['placements'][0]['gpus']=['missing'];self.bad(p)
 def test_wrong_node_gpu(self):self.p['placements'][0]['gpus']=['g3'];self.bad()
 def test_owner_denied(self):self.m['jobs'][0]['allowed_owners']=['o2'];self.bad()
 def test_family_denied(self):self.m['jobs'][0]['allowed_families']=['B'];self.bad()
 def test_gpu_vram_per_device_not_pool(self):self.m['jobs'][0]['min_vram_mib']=32768;self.bad()
 def test_partial_gang(self):self.m['jobs'][0]['gpu_count']=2;self.bad()
 def test_duplicate_gpu_within_gang(self):self.m['jobs'][0]['gpu_count']=2;self.p['placements'][0]['gpus']=['g1','g1'];self.bad()
 def test_mixed_family_gang(self):
  self.m['nodes'][0]['gpus'][1]['family']='B';self.m['jobs'][0]['gpu_count']=2;self.p['placements']=[dict(job='j1',node='n1',gpus=['g1','g2'])];self.p['deferred']=['j2'];self.bad()
 def test_valid_same_family_gang(self):
  self.m['jobs'][0]['gpu_count']=2;self.p['placements']=[dict(job='j1',node='n1',gpus=['g1','g2'])];self.p['deferred']=['j2'];self.assertTrue(verify_plan(self.m,self.p)['valid'])
 def test_cpu_overcommit(self):self.m['nodes'][0]['cpu_units']=7;self.bad()
 def test_host_ram_overcommit(self):self.m['nodes'][0]['ram_mib']=16383;self.bad()
 def test_extra_score_rejected(self):self.p['priority']=999999;self.bad()
 def test_malformed_plan(self):
  for p in [None,[],1,True,{},dict(schema_version=True,placements=[],deferred=[]),dict(schema_version=1,placements=[None],deferred=[]),dict(schema_version=1,placements=[],deferred=[{}])]:self.bad(p)
 def test_bool_float_bad_manifest(self):
  for x in [True,1.0,-1,'8',None]:
   m=copy.deepcopy(self.m);m['nodes'][0]['cpu_units']=x
   with self.assertRaises(ValueError):validate_manifest(m)
 def test_invalid_nested_manifest(self):
  for path,x in [('nodes',None),('nodes',[None]),('jobs',[None]),('jobs','oops')]:
   m=copy.deepcopy(self.m);m[path]=x
   with self.assertRaises(ValueError):validate_manifest(m)
 def test_duplicate_gpu_global(self):
  self.m['nodes'][1]['gpus'][0]['id']='g1'
  with self.assertRaises(ValueError):validate_manifest(self.m)
 def test_duplicate_node_job(self):
  for field in ['nodes','jobs']:
   m=copy.deepcopy(self.m);m[field].append(copy.deepcopy(m[field][0]))
   with self.assertRaises(ValueError):validate_manifest(m)
 def test_absent_allowed_owner_and_family_valid(self):self.m['jobs'][0].update(allowed_owners=['absent'],allowed_families=['absent']);self.assertIsNone(validate_manifest(self.m))
 def test_duplicate_allowed_policy_rejected(self):
  self.m['jobs'][0]['allowed_owners']=['o1','o1']
  with self.assertRaises(ValueError):validate_manifest(self.m)
 def test_extra_field_rejected(self):
  self.m['jobs'][0]['command']='not-executed'
  with self.assertRaises(ValueError):validate_manifest(self.m)
 def test_invalid_ids(self):
  for x in ['', 'a b','1a','a'*33,7,True]:
   m=copy.deepcopy(self.m);m['nodes'][0]['owner']=x
   with self.assertRaises(ValueError):validate_manifest(m)
 def test_nested_unhashable_ids_fail_closed(self):
  self.p['placements'][0]['job']={};self.bad()
 def test_size_limits(self):
  m=copy.deepcopy(self.m);m['jobs']=[dict(m['jobs'][0],id='j'+str(i)) for i in range(9)]
  with self.assertRaises(ValueError):validate_manifest(m)
  m=copy.deepcopy(self.m);m['nodes'][0]['gpus']=[dict(id='x'+str(i),family='A',vram_mib=1) for i in range(8)]
  with self.assertRaises(ValueError):validate_manifest(m)
 def test_strict_json(self):
  for text in ['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}','{"x":-Infinity}','notjson']:
   with self.assertRaises(ValueError):strict_loads(text)
  self.assertEqual(strict_loads('{"x":1}'),{'x':1})
if __name__=='__main__':unittest.main()
