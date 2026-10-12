"""Offline unit/source regressions; imports only isolated official scorer AST."""
import ast
import collections
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import re
import string
import tempfile
import unittest

import design


def source_dir():
    locations=[Path(__file__).resolve().parent/'sources',Path('/tmp/coop-qwen32-build/sources')]
    if os.environ.get('COOP_QA_SOURCE_DIR'):
        locations.insert(0,Path(os.environ['COOP_QA_SOURCE_DIR']))
    for path in locations:
        if (path/'dev-v2.0.json').is_file() and (path/'official_evaluate.py').is_file():
            return path
    raise RuntimeError('Pinned SQuAD source and official scorer are required for offline tests')


def official_functions(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != '710840ce2c2c61716334c056777032f24660b83eb9869a451036e6a24d8103c4':
        raise ValueError('official scorer SHA256 mismatch')
    tree=ast.parse(path.read_text())
    names={'normalize_answer','get_tokens','compute_exact','compute_f1'}
    nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    if {node.name for node in nodes} != names:
        raise ValueError('missing official scoring functions')
    isolated=ast.Module(body=nodes,type_ignores=[])
    namespace={'re':re,'string':string,'collections':collections}
    exec(compile(isolated,str(path),'exec'),namespace)
    return namespace


def simple_job(impossible=False):
    return dict(request_id='fixture',passage='The Red Fox jumps over the dog.',question='Which animal jumps?',
                answers=[] if impossible else [{'text':'Red Fox','answer_start':4}],is_impossible=impossible)


class DesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=source_dir();cls.source=cls.sources/'dev-v2.0.json'
        cls.selected=design.build_dataset(cls.source)
        cls.official=official_functions(cls.sources/'official_evaluate.py')

    def entries(self,part):
        return [dict(request_id=j['request_id'],is_impossible=j['is_impossible'],length_band=j['length_band'],
                     schema_valid=True,exact_match=True) for j in self.selected[part]]

    def test_official_normalization_and_f1_match(self):
        samples=['The, quick fox!','an A THE','Élan—Über the river','  A\tB\nC ','3.14','3,14','theatre','THE','.',"Fox's fox",'']
        rng=random.Random(81)
        words=['the','a','an','FOX','fox','dog','and','1984','éclair','not-a-word','x_y']
        samples += [' '.join(rng.choices(words,k=rng.randrange(0,12))) for _ in range(100)]
        for text in samples:
            self.assertEqual(design.normalize_answer(text),self.official['normalize_answer'](text))
        for a,b in zip(samples,reversed(samples)):
            self.assertAlmostEqual(design.token_f1(a,b),self.official['compute_f1'](a,b),places=14)
        # All selected official gold strings are included, not only toy normalizers.
        for part in design.PER_CELL:
            for job in self.selected[part]:
                for answer in job['answers']:
                    text=answer['text']
                    self.assertEqual(design.normalize_answer(text),self.official['normalize_answer'](text))

    def test_schema_duplicate_types_extra_missing_trailing_nonfinite(self):
        bad=['{"answer":"Red Fox","answer":"Red Fox"}','{"answer":1}','{"answer":true}',
             '{"answer":["Red Fox"]}','{"answer":{"text":"Red Fox"}}','{}',
             '{"answer":"Red Fox","why":"because"}','{"answer":"Red Fox"} tail',
             '{"answer":NaN}','{"answer":Infinity}','["Red Fox"]']
        for text in bad:
            with self.subTest(text=text):
                value=design.score(text,simple_job())
                self.assertFalse(value['schema_valid']);self.assertFalse(value['exact_match'])

    def test_deeply_nested_json_is_schema_failure(self):
        result=design.score('['*1100+'0'+']'*1100,simple_job())
        self.assertFalse(result['schema_valid']);self.assertFalse(result['exact_match'])

    def test_altered_official_scorer_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'official.py'
            path.write_bytes((self.sources/'official_evaluate.py').read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'scorer SHA256'):official_functions(path)

    def test_answerable_normalized_exact_and_partial(self):
        correct=design.score('{"answer":"the red fox!"}',simple_job())
        self.assertTrue(correct['schema_valid']);self.assertTrue(correct['exact_match'])
        self.assertEqual(correct['f1'],1);self.assertFalse(correct['literal_span'])
        partial=design.score('{"answer":"Fox"}',simple_job())
        self.assertFalse(partial['exact_match']);self.assertGreater(partial['f1'],0)
        self.assertFalse(design.score('{"answer":null}',simple_job())['exact_match'])

    def test_unanswerable_requires_literal_null(self):
        job=simple_job(True)
        out=design.score('{"answer":null}',job)
        self.assertTrue(out['exact_match']);self.assertTrue(out['abstained'])
        for value in ('','the','a','...','an!'):
            with self.subTest(value=value):
                out=design.score(json.dumps({'answer':value}),job)
                self.assertTrue(out['schema_valid']);self.assertFalse(out['exact_match'])
                self.assertFalse(out['abstained']);self.assertEqual(out['official_exact_match'],1)

    def test_official_empty_normalized_annotation_filter(self):
        job=simple_job();job['answers'].append({'text':'.','answer_start':len(job['passage'])-1})
        self.assertTrue(design.score('{"answer":"Red Fox"}',job)['exact_match'])
        self.assertFalse(design.score('{"answer":"."}',job)['exact_match'])
        job['answers']=[job['answers'][-1]]
        with self.assertRaisesRegex(ValueError,'nonempty normalized gold'):design.score('{"answer":null}',job)

    def test_bad_gold_offsets_and_answerability_fail_closed(self):
        for change in ('offset','bool_offset','unanswerable_gold','missing_answers'):
            job=simple_job()
            if change=='offset':job['answers'][0]['answer_start']=5
            elif change=='bool_offset':job['answers'][0]['answer_start']=True
            elif change=='unanswerable_gold':job['is_impossible']=True
            else:job['answers']=[]
            with self.subTest(change=change),self.assertRaises(ValueError):design.score('{"answer":"Red Fox"}',job)

    def test_pinned_source_hash(self):
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(),design.SOURCE_SHA256)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'altered.json';path.write_bytes(self.source.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'SHA256'):design.build_dataset(path)

    def test_article_partition_independently_ranked(self):
        original=json.loads(self.source.read_text())
        titles=sorted((a['title'] for a in original['data']),key=lambda t:(hashlib.sha256(('coop-qa-20261012:'+t).encode()).hexdigest(),t))
        self.assertEqual(self.selected['article_partition']['development'],titles[:12])
        self.assertEqual(self.selected['article_partition']['confirmation'],titles[12:])

    def test_exact_cells_and_disjoint_articles_context_ids(self):
        sets={}
        for part,n in [('development',2),('confirmation',6)]:
            jobs=self.selected[part]
            self.assertEqual(len(jobs),6*n)
            cells=collections.Counter((j['length_band'],j['is_impossible']) for j in jobs)
            self.assertEqual(cells,collections.Counter({(b,i):n for b in ('short','medium','long') for i in (False,True)}))
            self.assertEqual(len({j['passage'] for j in jobs}),len(jobs))
            self.assertTrue(all(j['title'] in self.selected['article_partition'][part] for j in jobs))
            sets[part]={k:{j[k] for j in jobs} for k in ('request_id','title','passage')}
        for key in sets['development']:self.assertFalse(sets['development'][key]&sets['confirmation'][key])

    def test_selection_reproducible_and_ranked(self):
        self.assertEqual(self.selected,design.build_dataset(self.source))
        for part in design.PER_CELL:
            ids=[j['qid'] for j in self.selected[part]]
            seed='coop-qa-20261012:'+part+':'
            self.assertEqual(ids,sorted(ids,key=lambda q:(hashlib.sha256((seed+q).encode()).hexdigest(),q)))

    def test_length_boundaries(self):
        for n,wanted in [(599,'short'),(600,'medium'),(1199,'medium'),(1200,'long'),(2400,'long'),(2401,None)]:
            self.assertEqual(design.length_bin('x'*n),wanted)

    def test_wire_uses_only_passage_question_and_public_schema(self):
        job=copy.deepcopy(self.selected['development'][0]);wire=design.wire_job(job)
        changed=copy.deepcopy(job);changed['answers']=[{'text':'SECRET_GOLD_CANARY','answer_start':0}]
        changed['is_impossible']=not job['is_impossible'];changed['label']='SECRET_LABEL';changed['title']='SECRET_TITLE'
        self.assertEqual(wire,design.wire_job(changed))
        self.assertEqual(set(wire),{'request_id','arrival_offset_s','prompt','max_output_tokens','format','think'})
        self.assertFalse(wire['think']);self.assertEqual(wire['max_output_tokens'],256)
        self.assertNotIn('enum',json.dumps(wire['format']));self.assertNotIn('SECRET_GOLD',json.dumps(wire))
        expected=design.INSTRUCTION+'Passage:\n'+job['passage']+'\nQuestion:\n'+job['question']+'\nJSON answer:'
        self.assertEqual(wire['prompt'],expected)

    def test_always_null_is_weak_fifty_percent_floor(self):
        for part in design.PER_CELL:
            baseline=design.always_null_baseline(self.selected[part])
            self.assertEqual(baseline['exact_accuracy'],.5)
            entries=[dict(request_id=j['request_id'],is_impossible=j['is_impossible'],length_band=j['length_band'],
                          schema_valid=True,exact_match=j['is_impossible']) for j in self.selected[part]]
            self.assertFalse(design.gate(entries,part))

    def test_gate_development_single_failure_passes_two_fail(self):
        rows=self.entries('development');self.assertTrue(design.gate(rows,'development'))
        rows[0]['exact_match']=False;self.assertTrue(design.gate(rows,'development'))
        rows[1]['exact_match']=False;self.assertFalse(design.gate(rows,'development'))

    def test_gate_confirmation_total_pass_can_fail_label_or_length(self):
        for kind in ('label','length'):
            rows=self.entries('confirmation')
            indices=[i for i,r in enumerate(rows) if (r['is_impossible'] if kind=='label' else r['length_band']=='short')][:3]
            for i in indices:rows[i]['exact_match']=False
            details=design.gate_details(rows,'confirmation')
            self.assertEqual(details['exact_correct'],33);self.assertFalse(details['passed'])
        rows=self.entries('confirmation')
        # Three failures spread over all lengths and both answerability labels.
        for band,impossible in [('short',False),('medium',True),('long',False)]:
            next(r for r in rows if r['length_band']==band and r['is_impossible']==impossible)['exact_match']=False
        self.assertTrue(design.gate(rows,'confirmation'))

    def test_confirmation_crossed_cell_minimum_blocks_concentrated_errors(self):
        rows=self.entries('confirmation')
        affected=[r for r in rows if r['length_band']=='short' and not r['is_impossible']][:2]
        for row in affected:row['exact_match']=False
        details=design.gate_details(rows,'confirmation')
        self.assertEqual(details['exact_correct'],34)
        self.assertEqual(details['correct_by_label']['answerable'],16)
        self.assertEqual(details['correct_by_length']['short'],10)
        self.assertFalse(details['passed'])
        self.assertEqual(details['minimum_per_cell'],5)
        self.assertIn('crossed length/answerability cell threshold failed',details['errors'])

    def test_gate_requires_all_schema_valid(self):
        rows=self.entries('development');rows[0].update(exact_match=False,schema_valid=False)
        self.assertFalse(design.gate(rows,'development'))

    def test_gate_rejects_duplicates_missing_extra_and_fake_truth_flags(self):
        for change in ('duplicate','missing','extra','intflag','wrongcell','unhashable_id'):
            rows=self.entries('development')
            if change=='duplicate':rows[1]['request_id']=rows[0]['request_id']
            elif change=='missing':rows.pop()
            elif change=='extra':rows.append(copy.deepcopy(rows[0]))
            elif change=='intflag':rows[0]['exact_match']=1
            elif change=='wrongcell':rows[0]['is_impossible']=not rows[0]['is_impossible']
            else:rows[0]['request_id']=[]
            with self.subTest(change=change):self.assertFalse(design.gate(rows,'development'))

if __name__=='__main__':unittest.main()
