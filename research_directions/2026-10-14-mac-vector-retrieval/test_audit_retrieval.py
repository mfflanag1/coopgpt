"""Small constructed fixtures only; never load the real SIFT corpus."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

import audit_retrieval as audit


class RetrievalAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.base = [(0,0),(1,0),(0,1),(2,0),(0,2)]
        self.queries = [(0,0),(2,2)]
        self.oracle = audit.integer_oracle(self.base, self.queries, k=2)

    def tearDown(self):
        self.temp.cleanup()

    def vecs(self, name, rows, floating=True):
        path = self.root/name
        path.write_bytes(b''.join(struct.pack('<i',len(row)) + struct.pack('<'+('f' if floating else 'i')*len(row),*row) for row in rows))
        return path

    def output(self, rows=None):
        path = self.root/'distances.u32le'
        rows = self.oracle['distances'] if rows is None else rows
        path.write_bytes(b''.join(struct.pack('<'+'I'*len(row),*row) for row in rows))
        return path

    def query_rows(self):
        rows = []
        for i, distances in enumerate(self.oracle['distances']):
            digest = hashlib.sha256(struct.pack('<'+'I'*len(distances),*distances)).hexdigest()
            top = [{'id':j,'distance':d} for j,d in zip(self.oracle['top_ids'][i],self.oracle['top_distances'][i])]
            rows.append({'query_id':i,'batch_index':i,'status':'passed','passed':True,'compared_distances':5,
                         'mismatch_count':0,'invalid_dot_count':0,'max_abs_error':0,'top10':top,'cpu_top10':copy.deepcopy(top),
                         'top10_exact_match':True,'gpu_distance_sha256':digest,'cpu_distance_sha256':digest,
                         'reconstruction_selection_seconds':.01,'cpu_oracle_validation_seconds':.01})
        return rows

    def profile_fixture(self):
        # Constructed schema fixture, not a SIFT query or collected observation.
        distances=list(range(10000)); top=[{'id':i,'distance':i} for i in range(10)]
        row_bytes=struct.pack('<'+'I'*10000,*distances); row_hash=hashlib.sha256(row_bytes).hexdigest()
        path=self.root/'complete.u32le'; path.write_bytes(row_bytes*100)
        oracle={'distances':[distances]*100,'top_ids':[list(range(10))]*100,'top_distances':[list(range(10))]*100}
        rows=[{'query_id':i,'batch_index':i//16,'status':'passed','passed':True,'compared_distances':10000,
               'mismatch_count':0,'invalid_dot_count':0,'max_abs_error':0,'top10':copy.deepcopy(top),'cpu_top10':copy.deepcopy(top),
               'top10_exact_match':True,'gpu_distance_sha256':row_hash,'cpu_distance_sha256':row_hash,
               'reconstruction_selection_seconds':.001,'cpu_oracle_validation_seconds':.001} for i in range(100)]
        memory={'cap_bytes':67108864,'input_file_staging_bound_bytes':5211600,'input_vector_bytes':1292800,
                'integer_norm_bytes':80800,'distance_matrix_bytes':4000000,'distance_serialization_bytes':4000000,
                'cpu_selection_hash_scratch_bound_bytes':524288,'top10_storage_bound_bytes':64000,
                'base_buffer_payload_bytes':5120000,'base_row_bytes':512,'base_buffer_length_bytes':5120000,
                'base_buffer_allocated_bytes':5120000,'maximum_batch_buffer_allocated_bytes':648192,
                'conservative_explicit_bound_bytes':20941680,'device_allocated_before_base_sample':0,
                'device_allocated_with_base_sample':5120000,'device_allocated_before_retrieve_return_sample':5120000}
        batches=[]
        for i,start in enumerate(range(0,100,16)):
            n=min(16,100-start); t=1.+10*i
            b={'index':i,'query_start':start,'query_count':n,'status':'passed','passed':True,'command_buffer_status':4,
               'preparation_start_s':t,'submit_s':t+1,'gpu_completion_observed_s':t+2,'reconstruction_start_s':t+2,
               'reconstruction_end_s':t+3,'oracle_start_s':t+3,'oracle_end_s':t+4,'resource_release_s':t+4.1,
               'preparation_seconds':1.,'gpu_submit_to_completion_seconds':1.,'reconstruction_selection_seconds':1.,
               'cpu_oracle_validation_seconds':1.,'query_row_bytes':512,'dot_row_bytes':40000,
               'query_buffer_payload_bytes':n*512,'dot_buffer_payload_bytes':n*40000,
               'query_buffer_length_bytes':n*512,'dot_buffer_length_bytes':n*40000,
               'query_buffer_allocated_bytes':n*512,'dot_buffer_allocated_bytes':n*40000,
               'explicit_bound_bytes':15173488+5120000+n*40512,
               'device_allocated_before_buffers_sample':5120000,'device_allocated_with_buffers_sample':5120000+n*40512,
               'device_allocated_after_release_sample':5120000}
            batches.append(b)
        raw={'schema_version':1,'protocol_id':'mac-sift10k-retrieval-v1','batch_size':16,'base_count':10000,
             'query_count':100,'dimensions':128,'top_k':10,'distance_file_bytes':4000000,'distance_file':'distances.u32le',
             'distance_file_sha256':audit.sha(path),'gate_passed':True,'cpu_self_test_passed':True,'inputs_validated':True,
             'input_base_sha256':'b'*64,'input_query_sha256':'q'*64,'device_name':'Fixture Mac','has_unified_memory':True,
             'max_buffer_length':67108864,'recommended_max_working_set_size':100000000,'clock_origin_uptime_ns':1,
             'started_at':'2026-10-14T00:00:00Z','completed_at':'2026-10-14T00:02:00Z',
             'input_read_validate_seconds':.1,'index_prepare_seconds':.1,'distances_write_seconds':.1,
             'processing_through_distance_output_seconds':70.,'queries':rows,'batches':batches,'memory':memory}
        args=(path,{'index':2,'profile_id':'b16','batch_size':16,'folder':'p02_b16'},
              {'protocol_id':'mac-sift10k-retrieval-v1'},oracle,
              {audit.BASE_FILE:{'sha256':'b'*64},audit.QUERY_FILE:{'sha256':'q'*64}},{'Fixture Mac'})
        return raw,args

    def test_strict_parse_and_literal_oracle(self):
        path = self.vecs('base.fvecs',self.base)
        self.assertEqual(audit.read_vecs(path,5,2,True),self.base)
        self.assertEqual(self.oracle['distances'],[[0,1,1,4,4],[8,5,5,4,4]])
        self.assertEqual(self.oracle['top_ids'],[[0,1],[3,4]])
        self.assertEqual(self.oracle['top_distances'],[[0,1],[4,4]])

    def test_truncated_extra_and_wrong_row_count(self):
        path = self.vecs('vectors',self.base)
        original = path.read_bytes()
        for raw in [original[:-1],original+b'\0',original[:-12]]:
            path.write_bytes(raw)
            with self.assertRaises(ValueError): audit.read_vecs(path,5,2,True)

    def test_later_dimension_header_rejected(self):
        path = self.vecs('vectors',self.base)
        raw = bytearray(path.read_bytes()); struct.pack_into('<i',raw,24,1); path.write_bytes(raw)
        with self.assertRaises(ValueError): audit.read_vecs(path,5,2,True)

    def test_nonfinite_fractional_and_out_of_range_rejected(self):
        for bad in [float('nan'),float('inf'),-1,256,.5]:
            path = self.vecs('vectors',[(0,bad)])
            with self.assertRaises(ValueError): audit.read_vecs(path,1,2,True)

    def test_all_distance_values_checked(self):
        path = self.output()
        self.assertTrue(audit.check_distance_file(path,self.oracle)['checks_passed'])
        raw = bytearray(path.read_bytes()); struct.pack_into('<I',raw,36,99); path.write_bytes(raw)
        result = audit.check_distance_file(path,self.oracle)
        self.assertFalse(result['checks_passed']); self.assertEqual(result['mismatch_count'],1)

    def test_query_order_and_truncated_output_rejected(self):
        path = self.output(list(reversed(self.oracle['distances'])))
        self.assertFalse(audit.check_distance_file(path,self.oracle)['checks_passed'])
        path.write_bytes(path.read_bytes()[:-1])
        result = audit.check_distance_file(path,self.oracle)
        self.assertFalse(result['checks_passed']); self.assertIsNone(result['mismatch_count'])

    def test_official_ties_and_boundary_allowed(self):
        result = audit.check_groundtruth([(0,2),(4,3)],self.oracle,5)
        self.assertTrue(result['checks_passed'])
        self.assertEqual(result['canonical_top10_official_id_set_overlap_total'],3)

    def test_official_missing_closer_wrong_order_duplicate_and_bad_id(self):
        for row in [(1,2),(1,0),(0,0),(0,5),(0,-1)]:
            result = audit.check_groundtruth([row,(3,4)],self.oracle,5)
            self.assertFalse(result['checks_passed'])

    def test_json_rejects_duplicate_and_nonfinite(self):
        path = self.root/'bad.json'
        for content in ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}']:
            path.write_text(content)
            with self.assertRaises(ValueError): audit.load(path)

    def test_native_canonical_ties_stricter_than_official(self):
        rows = self.query_rows()
        self.assertEqual(audit.check_queries(rows,self.oracle,1)['errors'],[])
        rows[0]['top10'][1]['id']=2  # Equal distance permitted officially, not by our canonical tie rule.
        self.assertTrue(audit.check_queries(rows,self.oracle,1)['errors'])

    def test_query_coverage_identity_and_failure(self):
        for mutate in [lambda rows: rows.pop(),lambda rows: rows.reverse(),
                       lambda rows: rows[1].update(status='failed',passed=False),
                       lambda rows: rows[1].update(compared_distances=4),
                       lambda rows: rows[1].update(batch_index=0)]:
            rows = self.query_rows(); mutate(rows)
            self.assertTrue(audit.check_queries(rows,self.oracle,1)['errors'])

    def test_query_hash_and_integer_types(self):
        for mutate in [lambda rows: rows[1].update(cpu_distance_sha256='0'*64),
                       lambda rows: rows[0]['top10'][0].update(id=False),
                       lambda rows: rows[0].update(max_abs_error=float('nan'))]:
            rows = self.query_rows(); mutate(rows)
            self.assertTrue(audit.check_queries(rows,self.oracle,1)['errors'])

    def test_frozen_file_mutation_and_unsafe_path(self):
        names = ['PROTOCOL.txt','PLAN.json','DATA_MANIFEST.json','retrieve.swift','run_retrieval.py',
                 'capture_inventory.py','audit_retrieval.py','test_audit_retrieval.py',
                 audit.BASE_FILE,audit.QUERY_FILE,audit.GT_FILE,'siftsmall.tar.gz','SOURCES.txt','MD5SUM.source.txt']
        for name in names:
            path=self.root/name; path.parent.mkdir(exist_ok=True); path.write_text(name)
        freeze={'source_sha256':{name:audit.sha(self.root/name) for name in names}}
        self.assertEqual(audit.frozen_sources(self.root,freeze),[])
        (self.root/'PLAN.json').write_text('changed')
        self.assertIn('Frozen source mismatch: PLAN.json',audit.frozen_sources(self.root,freeze))
        freeze['source_sha256']['../escape']='0'*64
        with self.assertRaises(ValueError): audit.frozen_sources(self.root,freeze)

    def test_complete_profile_and_batch_mutations(self):
        raw,args=self.profile_fixture()
        result=audit.audit_profile(raw,*args)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['compared_distances'],1000000)
        self.assertEqual(result['canonical_top10_positions_matched'],1000)
        for mutate in [lambda r:r['batches'].pop(),
                       lambda r:r['batches'][1].update(query_start=15),
                       lambda r:r['batches'][1].update(preparation_start_s=0),
                       lambda r:r['batches'][0].update(dot_buffer_allocated_bytes=100000000),
                       lambda r:r['memory'].update(conservative_explicit_bound_bytes=1),
                       lambda r:r.update(input_query_sha256='x'*64)]:
            changed=copy.deepcopy(raw); mutate(changed)
            self.assertFalse(audit.audit_profile(changed,*args)['checks_passed'])


if __name__ == '__main__': unittest.main()
