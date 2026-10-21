"""Synthetic protocol fixtures plus exact replay, without outcome decoding."""
import json
from pathlib import Path
import unittest
from footer_structure import CompactReader, COLUMN_METADATA, COLUMN_CHUNK, project_footer, audit
from header_inventory import audit as headers

ROOT = Path(__file__).resolve().parent


class StructuralChecks(unittest.TestCase):
    def test_binary_statistic_is_discarded(self):
        # Field 12 is a nested Statistics struct containing invalid UTF-8;
        # field 13 lists one DATA_PAGE_V2/PLAIN encoding with count one.
        raw = bytes.fromhex('cc 18 02 ff fe 26 00 00 19 1c 15 06 15 00 15 02 00 00')
        reader = CompactReader(raw)
        self.assertEqual(reader.struct(COLUMN_METADATA), {13: [{1: 3, 2: 0, 3: 1}]})
        self.assertEqual(reader.pos, len(raw))

    def test_multiple_data_pages_and_dictionary_are_distinct(self):
        raw = bytes.fromhex('d9 2c 15 06 15 00 15 04 00 15 04 15 00 15 02 00 00')
        out = CompactReader(raw).struct(COLUMN_METADATA)[13]
        self.assertEqual(sum(x[3] for x in out if x[1] in (0, 3)), 2)
        self.assertEqual(sum(x[3] for x in out if x[1] == 2), 1)

    def test_real_index_fields_are_retained(self):
        raw = bytes.fromhex('46 0e 15 08 16 12 15 0c 00')
        self.assertEqual(CompactReader(raw).struct(COLUMN_CHUNK), {4: 7, 5: 4, 6: 9, 7: 6})

    def test_missing_page_counts_remain_missing(self):
        self.assertNotIn(13, CompactReader(bytes([0])).struct(COLUMN_METADATA))

    def test_extended_field_id_and_signed_integer(self):
        self.assertEqual(CompactReader(bytes.fromhex('05 28 03 00')).struct({20: 'int'}), {20: -2})

    def test_truncation_duplicate_and_wrong_type_fail(self):
        for raw in [bytes.fromhex('18 05 00'), bytes.fromhex('15 02 05 02 04 00'), bytes.fromhex('18 00 00')]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                CompactReader(raw).struct({1: 'int'})

    def test_truncated_and_trailing_footer_fail(self):
        body = (ROOT / 'inputs/state_footer.bin').read_bytes()
        for bad in [body[:-1], body + b'\x00']:
            with self.assertRaises(ValueError):
                project_footer(bad)

    def test_retained_footer_projection_replays(self):
        actual = audit(ROOT)
        self.assertEqual(json.loads(json.dumps(actual)), json.loads((ROOT / 'footer_structure.json').read_text()))
        for member in actual['members']:
            self.assertEqual(member['page_count_histogram'], {'1': member['column_chunks']})
            self.assertEqual((member['offset_indexes'], member['column_indexes']), (0, 0))

    def test_header_chain_replays(self):
        out = headers(ROOT)
        self.assertEqual(out, json.loads((ROOT / 'june_tar_inventory.json').read_text()))
        self.assertEqual(out['header_bodies_verified'], 325)
        self.assertEqual(out['regular_members'], 159)
        self.assertEqual(out['archive_bytes'] - out['first_tar_terminator_offset'], 2048)
        self.assertEqual(out['uninspected_bytes_after_first_zero_header'], 1536)
        self.assertFalse(any('logics' in p.lower() or 'schneider' in p.lower()
                             for p in out['regular_members_by_plugin']))


if __name__ == '__main__':
    unittest.main()
