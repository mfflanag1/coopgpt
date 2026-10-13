"""Small independently specified fixtures for provenance, anomalies and paired tables."""
import copy
import csv
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import analyze_traces as audit


class TemporaryCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def table(self, name, header, rows):
        path = self.base / name
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)
        return path


class Integrity(TemporaryCase):
    def metadata(self):
        cache = self.base / 'raw'
        cache.mkdir()
        path = cache / 'source.csv'
        path.write_bytes(b'name,count\na,1\n')
        hashes = audit.file_hashes(path)
        revision = 'a' * 40
        common = {'path': 'source.csv', 'url': audit.SOURCE_RAW_BASE + revision + '/source.csv',
                  'bytes': hashes['bytes'], 'git_blob_sha1': hashes['git_blob_sha1']}
        lock = {'repository': audit.SOURCE_REPOSITORY, 'revision': revision, 'files': [common]}
        record = {'revision': revision, 'files': [dict(common, sha256=hashes['sha256'])],
                  'total_bytes': hashes['bytes']}
        return cache, lock, record

    def test_exact_hashes(self):
        cache, lock, record = self.metadata()
        result = audit.verify_inputs(cache, lock, record)
        self.assertEqual(result['source.csv']['sha256'], record['files'][0]['sha256'])
        self.assertEqual(result['source.csv']['bytes'], 15)

    def test_changed_same_length_bytes(self):
        cache, lock, record = self.metadata()
        (cache / 'source.csv').write_bytes(b'name,count\na,2\n')
        with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
            audit.verify_inputs(cache, lock, record)

    def test_bad_record_sha_even_if_git_blob_matches(self):
        cache, lock, record = self.metadata()
        record['files'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'sha256'):
            audit.verify_inputs(cache, lock, record)

    def test_record_cannot_override_upstream_blob(self):
        cache, lock, record = self.metadata()
        record['files'][0]['git_blob_sha1'] = '0' * 40
        with self.assertRaisesRegex(ValueError, 'lock/download mismatch'):
            audit.verify_inputs(cache, lock, record)

    def test_no_missing_record_entry(self):
        cache, lock, record = self.metadata()
        record['files'].append(dict(record['files'][0], path='unlocked.csv'))
        with self.assertRaisesRegex(ValueError, 'file-set mismatch'):
            audit.verify_inputs(cache, lock, record)

    def test_duplicate_lock_path_rejected(self):
        cache, lock, record = self.metadata()
        lock['files'].append(copy.deepcopy(lock['files'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate metadata path'):
            audit.verify_inputs(cache, lock, record)

    def test_no_parent_traversal(self):
        cache, lock, record = self.metadata()
        for metadata in (lock, record):
            metadata['files'][0]['path'] = '../source.csv'
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            audit.verify_inputs(cache, lock, record)

    def test_no_symlink_escape(self):
        cache, lock, record = self.metadata()
        source = cache / 'source.csv'
        outside = self.base / 'outside.csv'
        outside.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'escaped cache'):
            audit.verify_inputs(cache, lock, record)

    def test_revision_and_total_size(self):
        cache, lock, record = self.metadata()
        wrong_revision = dict(record, revision='different')
        with self.assertRaisesRegex(ValueError, 'revision mismatch'):
            audit.verify_inputs(cache, lock, wrong_revision)
        with self.assertRaisesRegex(ValueError, 'total-byte mismatch'):
            audit.verify_inputs(cache, lock, dict(record, total_bytes=0))

    def test_repository_is_fixed_not_an_arbitrary_label(self):
        cache, lock, record = self.metadata()
        lock['repository'] = 'https://github.com/elsewhere/clusterdata'
        with self.assertRaisesRegex(ValueError, 'unexpected source repository'):
            audit.verify_inputs(cache, lock, record)

    def test_revision_requires_full_lowercase_git_identity(self):
        cache, lock, record = self.metadata()
        for revision in ('main', 'A' * 40, 'a' * 39, 'a' * 41, 17, None):
            with self.subTest(revision=revision):
                lock['revision'] = record['revision'] = revision
                with self.assertRaisesRegex(ValueError, '40-hex'):
                    audit.verify_inputs(cache, lock, record)

    def test_jointly_changed_url_cannot_relabel_download_origin(self):
        cache, lock, record = self.metadata()
        for url in ('https://example.invalid/source.csv',
                    audit.SOURCE_RAW_BASE + 'b' * 40 + '/source.csv',
                    audit.SOURCE_RAW_BASE + 'a' * 40 + '/different.csv'):
            with self.subTest(url=url):
                lock['files'][0]['url'] = record['files'][0]['url'] = url
                with self.assertRaisesRegex(ValueError, 'source URL'):
                    audit.verify_inputs(cache, lock, record)

    def test_duplicate_and_nonfinite_metadata_json_rejected(self):
        path = self.base / 'metadata.json'
        for value in ('{"files": [], "files": [1]}', '{"x": NaN}'):
            path.write_text(value)
            with self.assertRaises(ValueError):
                audit.load_json(path)


class DesignFreeze(TemporaryCase):
    def inputs(self):
        cache = self.base / 'raw'
        cache.mkdir()
        entries = []
        revision = 'a' * 40
        for name, spec in audit.TABLES.items():
            path = cache / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('w', newline='') as handle:
                csv.writer(handle).writerow([spec['id']] + spec['numeric'] + spec['categorical'])
            entries.append(dict(audit.file_hashes(path), path=name,
                                url=audit.SOURCE_RAW_BASE + revision + '/' + name))
        lock = {'repository': audit.SOURCE_REPOSITORY, 'revision': revision,
                'files': [{k: v for k, v in entry.items() if k != 'sha256'} for entry in entries]}
        record = {'revision': revision, 'files': entries,
                  'total_bytes': sum(entry['bytes'] for entry in entries)}
        lock_path, record_path = self.base / 'SOURCE_LOCK.json', self.base / 'DOWNLOAD_RECORD.json'
        lock_path.write_text(json.dumps(lock))
        record_path.write_text(json.dumps(record))
        (self.base / 'PROTOCOL.txt').write_text('Frozen test protocol.\n')
        self.freeze()
        return cache, lock_path, record_path

    def freeze(self):
        hashes = {name: audit.file_hashes(self.base / name)['sha256']
                  for name in ('PROTOCOL.txt', 'SOURCE_LOCK.json')}
        (self.base / 'DESIGN_FREEZE.json').write_text(json.dumps({'sha256': hashes}))

    def test_unmodified_frozen_inputs_succeed(self):
        result = audit.run(*self.inputs())
        self.assertEqual(sum(table['rows'] for table in result['tables'].values()), 0)
        self.assertTrue(result['augmentation_comparison']['identical_id_sets'])

    def test_protocol_mutation_fails_before_any_csv_parsing(self):
        inputs = self.inputs()
        (self.base / 'PROTOCOL.txt').write_text('Changed protocol.\n')
        with patch.object(audit, 'audit_table') as parse:
            with self.assertRaisesRegex(ValueError, 'design freeze mismatch: PROTOCOL'):
                audit.run(*inputs)
            parse.assert_not_called()

    def test_joint_source_relabeling_cannot_evade_frozen_identity(self):
        inputs = self.inputs()
        for path in inputs[1:]:
            metadata = json.loads(path.read_text())
            metadata['revision'] = 'b' * 40
            for entry in metadata['files']:
                entry['url'] = audit.SOURCE_RAW_BASE + metadata['revision'] + '/' + entry['path']
            path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError, 'design freeze mismatch: SOURCE_LOCK'):
            audit.run(*inputs)

    def test_missing_hash_in_freeze_cannot_silently_skip_protocol(self):
        inputs = self.inputs()
        path = self.base / 'DESIGN_FREEZE.json'
        metadata = json.loads(path.read_text())
        del metadata['sha256']['PROTOCOL.txt']
        path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError, 'cover exactly'):
            audit.run(*inputs)

    def test_protocol_mutated_during_analysis_is_caught_afterward(self):
        inputs = self.inputs()
        original = audit.compare_augmentation
        def mutate(*args):
            result = original(*args)
            (self.base / 'PROTOCOL.txt').write_text('Changed during analysis.\n')
            return result
        with patch.object(audit, 'compare_augmentation', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'design freeze mismatch: PROTOCOL'):
                audit.run(*inputs)

    def test_rewriting_freeze_during_analysis_is_also_caught(self):
        inputs = self.inputs()
        original = audit.compare_augmentation
        def mutate(*args):
            result = original(*args)
            (self.base / 'PROTOCOL.txt').write_text('Changed and rehashed.\n')
            self.freeze()
            return result
        with patch.object(audit, 'compare_augmentation', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'design freeze changed during analysis'):
                audit.run(*inputs)


class NumericAndRows(TemporaryCase):
    def test_numeric_categories_are_separate_and_exact(self):
        stats = audit.Numeric()
        for value in (None, '', ' ', 'NaN', '-Infinity', 'abc', '-1', '0', '1.25',
                      '9007199254740993', '1.0'):
            stats.add(value)
        result = stats.report()
        self.assertEqual(result['counts'], {
            'absent_cell': 1, 'blank': 2, 'invalid': 1, 'nonfinite': 2, 'finite': 5,
            'negative': 1, 'zero': 1, 'positive': 3, 'integral': 4, 'nonintegral': 1})
        self.assertEqual(result['minimum'], '-1')
        self.assertEqual(result['maximum'], '9007199254740993')
        self.assertEqual(result['examples_first_seen']['nonfinite'], ['NaN', '-Infinity'])

    def test_decimal_equality_distribution_without_float_rounding(self):
        stats = audit.Numeric()
        for raw in ['1', '1.0', '0.100000000000000000000000001', '0.100000000000000000000000002']:
            stats.add(raw)
        result = stats.report()
        self.assertEqual(result['distinct_finite_values'], 3)
        self.assertEqual(result['most_frequent_values'][0], {'value': '1', 'rows': 2})

    def test_shape_blanks_duplicates_not_dropped(self):
        path = self.table('tiny.csv', ['name', 'amount', 'tag'], [
            ['a', '3', 'x'], ['a', '3', 'x'], ['', '-2'], [], ['b', 'oops', '', 'extra']])
        result = audit.audit_table(path, {
            'id': 'name', 'numeric': ['amount'], 'categorical': ['tag'], 'kind': 'job2026'})
        self.assertEqual(result['header'], ['name', 'amount', 'tag'])
        self.assertEqual(result['rows'], 5)
        self.assertEqual(result['unique_nonblank_ids'], 2)
        self.assertEqual(result['ids_with_duplicates'], 1)
        self.assertEqual(result['duplicate_id_rows_beyond_first'], 1)
        self.assertEqual(result['duplicate_row_fingerprints_beyond_first'], 1)
        self.assertEqual(result['blank_id_rows'], 1)
        self.assertEqual(result['absent_id_rows'], 1)
        self.assertEqual(result['row_width_anomalies']['rows'], 3)
        self.assertEqual(result['numeric']['amount']['counts']['negative'], 1)
        self.assertEqual(result['numeric']['amount']['counts']['invalid'], 1)
        self.assertEqual(result['numeric']['amount']['counts']['absent_cell'], 1)
        self.assertEqual(result['absent_cells_by_column']['tag'], 2)
        self.assertEqual(result['blank_cells_by_column']['tag'], 1)

    def test_duplicate_header_has_no_unique_interpretation(self):
        path = self.table('bad.csv', ['name', 'name'], [['a', 'b']])
        with self.assertRaisesRegex(ValueError, 'duplicate CSV header'):
            list(audit.csv_rows(path))

    def test_malformed_quoting_rejected(self):
        path = self.base / 'bad.csv'
        path.write_text('name,value\n"unclosed,1\n')
        with self.assertRaises(csv.Error):
            list(audit.csv_rows(path))

    def test_literal_absent_columns_are_not_semantic_claims(self):
        path = self.table('node.csv', ['sn', 'cpu_milli'], [['n1', '1000']])
        result = audit.audit_table(path, {
            'id': 'sn', 'numeric': ['cpu_milli'], 'categorical': [], 'kind': 'node'})
        self.assertIn('cpu_units', result['literal_contract_columns_absent'])
        self.assertEqual(result['literal_contract_columns_present'], [])
        self.assertIn('Literal names only', result['column_comparison_caution'])


class GPUClassification(unittest.TestCase):
    def test_source_defined_categories(self):
        pairs = [
            ('0', '0', 'cpu_only'), ('0', '1000', 'cpu_only'),
            ('1', '1000', 'full_gpu_single'), ('1', '250', 'fractional_gpu_single'),
            ('1', '0', 'unexpected_single_gpu_milli'), ('1', '', 'unexpected_single_gpu_milli'),
            ('1', '1001', 'unexpected_single_gpu_milli'), ('1', 'NaN', 'unexpected_single_gpu_milli'),
            ('2', '0', 'full_gpu_multi'), ('8', 'invalid', 'full_gpu_multi'),
            ('9', '1000', 'unexpected_num_gpu'), ('-1', '1000', 'unexpected_num_gpu'),
            ('0.5', '1000', 'unexpected_num_gpu'), ('nan', '1000', 'unexpected_num_gpu')]
        for count, milli, expected in pairs:
            with self.subTest(count=count, milli=milli):
                self.assertEqual(audit.gpu2023_category({'num_gpu': count, 'gpu_milli': milli}), expected)

    def test_no_mutation(self):
        row = {'num_gpu': '1', 'gpu_milli': '200'}
        original = row.copy()
        audit.gpu2023_category(row)
        self.assertEqual(row, original)


class Augmentation(TemporaryCase):
    def test_join_by_id_not_row_position_and_exposes_all_fields(self):
        left = self.table('default.csv', ['name', 'gpu_spec', 'cpu'], [
            ['b', 'nan', '2'], ['a', '', '1'], ['c', 'A100', '3']])
        right = self.table('augmented.csv', ['name', 'gpu_spec', 'cpu'], [
            ['c', 'A100', '3'], ['a', 'V100|A100', '1'], ['b', 'nan', '4']])
        result = audit.compare_augmentation(left, right)
        self.assertTrue(result['identical_id_sets'])
        self.assertEqual(result['changed_shared_rows'], 2)
        self.assertEqual(result['changed_cells_by_field'], {'name': 0, 'gpu_spec': 1, 'cpu': 1})
        self.assertEqual(result['nonblank_gpu_spec_rows'], {'default': 2, 'augmented': 3})
        self.assertEqual(result['nonblank_non_nan_gpu_spec_rows'], {'default': 1, 'augmented': 2})
        self.assertEqual(result['modification_examples'][0]['name'], 'a')
        self.assertEqual(result['modification_examples'][1]['changes']['cpu'], {'default': '2', 'augmented': '4'})

    def test_missing_ids_are_retained_as_join_discrepancies(self):
        left = self.table('default.csv', ['name', 'gpu_spec'], [['a', ''], ['b', '']])
        right = self.table('augmented.csv', ['name', 'gpu_spec'], [['b', ''], ['c', '']])
        result = audit.compare_augmentation(left, right)
        self.assertFalse(result['identical_id_sets'])
        self.assertEqual(result['shared_ids'], 1)
        self.assertEqual(result['default_only_sample'], ['a'])
        self.assertEqual(result['augmented_only_sample'], ['c'])

    def test_duplicate_blank_and_bad_width_make_join_ambiguous(self):
        left = self.table('default.csv', ['name', 'gpu_spec'], [['a', '']])
        for rows in ([['a', ''], ['a', 'A100']], [['', 'A100']], [['a']]):
            right = self.table('augmented.csv', ['name', 'gpu_spec'], rows)
            with self.assertRaisesRegex(ValueError, 'ambiguous augmentation join'):
                audit.compare_augmentation(left, right)

    def test_modification_examples_capped_at_ten(self):
        left = self.table('default.csv', ['name', 'gpu_spec'], [[str(n), ''] for n in range(25)])
        right = self.table('augmented.csv', ['name', 'gpu_spec'], [[str(n), 'A100'] for n in range(25)])
        result = audit.compare_augmentation(left, right)
        self.assertEqual(result['changed_shared_rows'], 25)
        self.assertEqual(len(result['modification_examples']), 10)


if __name__ == '__main__':
    unittest.main()
