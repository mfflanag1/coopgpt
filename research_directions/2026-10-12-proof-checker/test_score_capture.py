"""Synthetic saved-response checks; no study files, model, or network required."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import call, patch

import contract
import score_capture


def fixtures():
    """Distinct proof IDs make accidental cross-case answer binding observable."""
    cases, controls, primary, inventory = [], [], {}, {}
    for index in range(24):
        key = f'case{index}'
        first, second = f'D{index}A', f'D{index}B'
        parts = [dict(id='a1', support=[[first]], contradict=[]),
                 dict(id='a2', support=[[second]], contradict=[])]
        case = dict(request_id=key, label='supported',
                    passages=[dict(id=first), dict(id=second)], components=parts,
                    acceptable_evidence=[[first, second]], relevant_evidence=[first, second])
        cases.append(case)
        candidate = dict(verdict='supported', evidence=[first, second])
        primary[key] = ' \n' + json.dumps(candidate, indent=2) + '\n '
        inventory[key] = json.dumps({part['id']: {side: part[side] for side in ('support', 'contradict')}
                                     for part in parts})
        if index < 12:
            for expected in (True, False):
                controls.append(dict(request_id=f'c_{key}_{expected}', pair_id='pair_'+key,
                                     case_id=key, error_group='false_insufficient', expected_accept=expected,
                                     candidate=copy.deepcopy(candidate) if expected else
                                     dict(verdict='insufficient', evidence=[])))
    return cases, controls, primary, inventory


def trace(request_id, text):
    split = len(text)//2
    return dict(response='IGNORE_TOP_LEVEL', requests=[dict(
        request_id=request_id, request_prompt='IGNORE_PROMPT', response='IGNORE_ROW',
        final=dict(response='IGNORE_CACHED_FINAL'),
        chunks=[dict(data=dict(response=text[:split], thinking='IGNORE_THINKING')),
                dict(data=dict(thinking='IGNORE_THINKING_ONLY')),
                dict(data=dict(response=text[split:], done=True)),
                dict(data=dict(done=True, eval_count=12))])])


class ScoreCaptureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.folder = self.root/'collection'
        self.folder.mkdir()
        self.cases, self.controls, self.primary, self.inventory = fixtures()

    def save(self, identifier, value):
        path = self.folder/(identifier+'.json')
        path.write_text(json.dumps(value))
        return path

    def save_answers(self):
        for prefix, values in (('p_', self.primary), ('i_', self.inventory)):
            for key, text in values.items():
                self.save(prefix+key, trace(prefix+key, text))

    def score(self):
        # Filesystem/provenance validation is tested separately by contract tests.
        # This test supplies in-memory inputs to exercise actual scoring integration.
        with patch.object(score_capture, 'validate_inputs', return_value=(self.cases, self.controls)):
            return score_capture.main(self.root/'synthetic_base', self.root)

    def test_exact_chunk_text_preserves_whitespace_and_ignores_thinking_and_cached_fields(self):
        text = ' \n malformed JSON { "verdict": "broken" } \t\n'
        path = self.save('p_case0', trace('p_case0', text))
        self.assertEqual(score_capture.response_text(path, 'p_case0'), text)

    def test_missing_file_is_none_but_recorded_empty_response_is_empty_string(self):
        self.assertIsNone(score_capture.response_text(self.folder/'missing.json', 'missing'))
        path = self.save('i_case0', trace('i_case0', ''))
        self.assertEqual(score_capture.response_text(path, 'i_case0'), '')

    def test_malformed_raw_containers_raise_without_coercion(self):
        valid = trace('p_case0', 'unchanged')
        malformed = [None, [], {}, {'requests': {}}, {'requests': []},
                     {'requests': [None]}, {'requests': valid['requests']*2}]
        for chunks in (None, 'not chunks', [None], [{}], [{'data': None}],
                       [{'data': {'response': None}}], [{'data': {'response': 7}}],
                       [{'data': {'response': False}}]):
            malformed.append({'requests': [{'request_id': 'p_case0', 'chunks': chunks}]})
        for index, value in enumerate(malformed):
            with self.subTest(index=index):
                path = self.save('p_case0', value)
                with self.assertRaises(ValueError):
                    score_capture.response_text(path, 'p_case0')

    def test_invalid_raw_json_raises(self):
        path = self.folder/'p_case0.json'
        path.write_text('{broken')
        with self.assertRaises(ValueError):
            score_capture.response_text(path, 'p_case0')

    def test_wrong_or_missing_request_id_raises(self):
        for identifier in ('i_case0', 'p_case1', None):
            with self.subTest(identifier=identifier):
                value = trace(identifier, 'text')
                if identifier is None:
                    del value['requests'][0]['request_id']
                path = self.save('p_case0', value)
                with self.assertRaisesRegex(ValueError, 'request ID'):
                    score_capture.response_text(path, 'p_case0')

    def test_exactly_48_bare_case_bindings_and_no_control_warmup_or_summary_reads(self):
        self.save_answers()
        for filename in ('WARMUP', 'SUMMARY', self.controls[0]['request_id']):
            (self.folder/(filename+'.json')).write_text('INVALID AND MUST NOT BE READ')
        sentinel = {'input_complete': True}
        with patch.object(score_capture, 'validate_inputs', return_value=(self.cases, self.controls)) as validated, \
             patch.object(score_capture, 'response_text', wraps=score_capture.response_text) as read, \
             patch.object(score_capture, 'summarize', return_value=sentinel) as summarized, \
             patch.object(contract, 'inventory_job', side_effect=AssertionError('inference job built')), \
             patch.object(contract, 'primary_job', side_effect=AssertionError('inference job built')), \
             patch('socket.socket', side_effect=AssertionError('network use')), \
             patch('subprocess.Popen', side_effect=AssertionError('process launch')):
            result = score_capture.main(self.root/'synthetic_base', self.root)
        self.assertIs(result, sentinel)
        validated.assert_called_once_with(self.root/'synthetic_base')
        summarized.assert_called_once_with(self.cases, self.controls, self.primary, self.inventory)
        expected = [call(self.folder/(prefix+case['request_id']+'.json'), prefix+case['request_id'])
                    for prefix in ('p_', 'i_') for case in self.cases]
        self.assertEqual(read.call_args_list, expected)
        self.assertEqual(read.call_count, 48)

    def test_missing_answers_are_omitted_from_maps_but_empty_answers_are_preserved(self):
        self.save_answers()
        (self.folder/'p_case0.json').unlink()
        (self.folder/'i_case1.json').unlink()
        self.save('i_case2', trace('i_case2', ''))
        expected_primary = dict(self.primary); del expected_primary['case0']
        expected_inventory = dict(self.inventory); del expected_inventory['case1']
        expected_inventory['case2'] = ''
        with patch.object(score_capture, 'validate_inputs', return_value=(self.cases, self.controls)), \
             patch.object(score_capture, 'summarize', return_value={}) as summarized:
            score_capture.main(self.root/'synthetic_base', self.root)
        summarized.assert_called_once_with(self.cases, self.controls, expected_primary, expected_inventory)

    def test_actual_summary_uses_matching_inventories_and_offline_controls(self):
        self.save_answers()
        result = self.score()
        self.assertTrue(result['input_complete'])
        self.assertTrue(result['engineering_gate_passed'])
        self.assertEqual(result['baseline_correct'], 24)
        self.assertEqual(result['automatic_correct'], 24)
        self.assertEqual(result['inventory_quality_correct'], 24)
        self.assertEqual(result['constructed_valid_retained'], 12)
        self.assertEqual(result['constructed_invalid_rejected'], 12)
        self.assertEqual(result['format_variant_checks'], 96)
        self.assertEqual(result['format_variant_failures'], 0)
        self.assertEqual({row['case_id'] for row in result['natural']}, set(self.primary))
        self.assertEqual(len(list(self.folder.glob('*.json'))), 48)

    def test_actual_summary_detects_cross_case_inventory_content(self):
        self.save_answers()
        keys = list(self.inventory)
        for index, key in enumerate(keys):
            shifted = self.inventory[keys[(index+1) % len(keys)]]
            self.save('i_'+key, trace('i_'+key, shifted))
        result = self.score()
        self.assertTrue(result['input_complete'])
        self.assertEqual(result['baseline_correct'], 24)
        self.assertEqual(result['inventory_usable'], 0)
        self.assertEqual(result['automatic_correct'], 0)
        self.assertFalse(result['engineering_gate_passed'])

    def test_actual_summary_marks_missing_inventory_incomplete_without_subset_pass(self):
        self.save_answers()
        (self.folder/'i_case0.json').unlink()
        result = self.score()
        self.assertFalse(result['input_complete'])
        self.assertFalse(result['engineering_gate_passed'])
        self.assertEqual(result['baseline_correct'], 24)
        self.assertEqual(result['inventory_usable'], 23)
        self.assertEqual(result['automatic_correct'], 23)
        self.assertEqual(len(result['natural']), 24)
        self.assertEqual(len(result['controlled']), 24)


if __name__ == '__main__':
    unittest.main()
