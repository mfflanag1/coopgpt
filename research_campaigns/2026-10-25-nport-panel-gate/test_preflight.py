"""Synthetic contract tests only. These are not fund observations or panel evidence."""
from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import tempfile
import struct
import unittest
import zipfile

from preflight import FIELDS, METRICS, InvalidArchive, load_archive, screen


def fixture():
    acc = '0000000000-25-000001'
    data = {key: [] for key in FIELDS}
    data['SUBMISSION.tsv'] = [dict(ACCESSION_NUMBER=acc, FILING_DATE='15-MAY-2025',
        REPORT_DATE='31-MAR-2025', SUB_TYPE='NPORT-P')]
    data['REGISTRANT.tsv'] = [dict(ACCESSION_NUMBER=acc, CIK='0000000001')]
    data['FUND_REPORTED_INFO.tsv'] = [dict(ACCESSION_NUMBER=acc, SERIES_ID='S000000001',
        SERIES_NAME='SYNTHETIC TEST ONLY', NET_ASSETS='100.00', TOTAL_ASSETS='120.00', TOTAL_LIABILITIES='20.00')]
    data['INTEREST_RATE_RISK.tsv'] = [dict(ACCESSION_NUMBER=acc,
        INTEREST_RATE_RISK_ID='1', CURRENCY_CODE='USD', **{k:'0' for k in METRICS})]
    return data


def make_zip(path, data, quote=True, bad_meta=False, stored=False):
    meta = json.loads((Path(__file__).parent/'raw/nport_metadata_from_partial.json').read_text())
    if not quote: meta['dialect']['quoteChar']=None
    if bad_meta: meta['tables']=1
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED) as z:
        z.writestr('nport_metadata.json',json.dumps(meta))
        for name, fields in FIELDS.items():
            text=io.StringIO(newline='');w=csv.DictWriter(text,fieldnames=fields,delimiter='\t',quoting=csv.QUOTE_MINIMAL if quote else csv.QUOTE_NONE,quotechar='"' if quote else None)
            w.writeheader();w.writerows(data[name]);z.writestr(name,text.getvalue())


class PreflightTests(unittest.TestCase):
    def test_complete_zero_vector_is_not_missing(self):
        result=screen(fixture())
        self.assertEqual(result['field_compatible_candidate_count'],1)
        self.assertEqual(result['candidate_all_zero_vectors'],1)
        self.assertFalse(result['headline_residuals_computed'])
        self.assertEqual(result['materiality_gate'],'NOT_EVALUATED')

    def test_missing_node_and_nonfinite_values_rejected(self):
        for value in ['', 'NaN', 'Infinity', '1e100', '1,000']:
            with self.subTest(value=value):
                d=fixture();d['INTEREST_RATE_RISK.tsv'][0][METRICS[0]]=value
                self.assertEqual(screen(d)['field_compatible_candidate_count'],0)

    def test_duplicate_usd_not_summed(self):
        d=fixture();r=deepcopy(d['INTEREST_RATE_RISK.tsv'][0]);r['INTEREST_RATE_RISK_ID']='2'
        d['INTEREST_RATE_RISK.tsv'].append(r)
        self.assertEqual(screen(d)['exclusion_counts'],{'duplicate_usd_entries':1})

    def test_latest_bad_amendment_does_not_fall_back(self):
        d=fixture();new='0000000000-25-000002'
        for name in ['SUBMISSION.tsv','FUND_REPORTED_INFO.tsv','REGISTRANT.tsv','INTEREST_RATE_RISK.tsv']:
            row=deepcopy(d[name][0]);row['ACCESSION_NUMBER']=new;d[name].append(row)
        d['SUBMISSION.tsv'][1].update(FILING_DATE='20-MAY-2025',SUB_TYPE='NPORT-P/A')
        d['INTEREST_RATE_RISK.tsv'][1][METRICS[0]]=''
        r=screen(d)
        self.assertEqual(r['field_compatible_candidate_count'],0)
        self.assertEqual(r['amendment_audit'][0]['selected'],new)
        self.assertEqual(r['exclusion_counts']['superseded_within_batch'],1)

    def test_cutoff_and_reference_date_are_fixed(self):
        for field,value in [('FILING_DATE','01-JUL-2025'),('REPORT_DATE','30-APR-2025')]:
            d=fixture();d['SUBMISSION.tsv'][0][field]=value
            self.assertEqual(screen(d)['field_compatible_candidate_count'],0)

    def test_missing_b3_is_not_assumed_exempt(self):
        d=fixture();d['INTEREST_RATE_RISK.tsv']=[]
        self.assertEqual(screen(d)['exclusion_counts'],{'b3_omitted_reason_unknown':1})

    def test_nav_mismatch_quarantined_without_diagnosis(self):
        d=fixture();d['FUND_REPORTED_INFO.tsv'][0]['NET_ASSETS']='99.99'
        self.assertEqual(screen(d)['exclusion_counts'],{'nav_reconciliation_requires_source_check':1})

    def test_other_currency_not_relabelled(self):
        d=fixture();d['INTEREST_RATE_RISK.tsv'][0]['CURRENCY_CODE']='EUR'
        self.assertEqual(screen(d)['exclusion_counts'],{'no_usd_entry':1})

    def test_valid_archive_reads_and_preserves_values(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'fixture.zip';d=fixture();make_zip(p,d)
            tables,digest=load_archive(p)
            self.assertEqual(tables,d);self.assertEqual(len(digest),64)

    def test_duplicate_primary_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'fixture.zip';d=fixture();d['SUBMISSION.tsv']*=2;make_zip(p,d)
            with self.assertRaises(InvalidArchive):load_archive(p)

    def test_truncated_archive_refused_even_with_zip_extension(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'fixture.zip';make_zip(p,fixture());p.write_bytes(p.read_bytes()[:-100])
            with self.assertRaises(InvalidArchive):load_archive(p)

    def test_partial_extension_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'fixture.crdownload';make_zip(p,fixture())
            with self.assertRaises(InvalidArchive):load_archive(p)

    def test_orphan_accession_refused(self):
        d=fixture();d['REGISTRANT.tsv'][0]['ACCESSION_NUMBER']='orphan'
        with self.assertRaises(InvalidArchive):screen(d)

    def test_missing_target_fund_row_refused(self):
        d=fixture();d['FUND_REPORTED_INFO.tsv']=[]
        with self.assertRaises(InvalidArchive):screen(d)

    def test_literal_quotes_preserved_under_declared_dialect(self):
        for quote in [True,False]:
            with tempfile.TemporaryDirectory() as temp:
                p=Path(temp)/'fixture.zip';d=fixture()
                d['FUND_REPORTED_INFO.tsv'][0]['SERIES_NAME']='"Literal quoted name"'
                make_zip(p,d,quote=quote)
                got,_=load_archive(p);self.assertEqual(got,d)

    def test_quoted_note_embedded_tab_and_newline_preserved(self):
        d=fixture();d['EXPLANATORY_NOTE.tsv']=[dict(ACCESSION_NUMBER=d['SUBMISSION.tsv'][0]['ACCESSION_NUMBER'],EXPLANATORY_NOTE_ID='1',ITEM_NO='B.3',EXPLANATORY_NOTE='"quoted"\ttab\nnewline')]
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'fixture.zip';make_zip(p,d)
            got,_=load_archive(p);self.assertEqual(got,d)

    def test_bad_metadata_shape_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'fixture.zip';make_zip(p,fixture(),bad_meta=True)
            with self.assertRaises(InvalidArchive):load_archive(p)

    def test_crc_damage_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'fixture.zip';make_zip(p,fixture(),stored=True)
            raw=bytearray(p.read_bytes())
            with zipfile.ZipFile(p) as z: offset=z.getinfo('SUBMISSION.tsv').header_offset
            name_len,extra_len=struct.unpack_from('<HH',raw,offset+26)
            data_start=offset+30+name_len+extra_len
            raw[data_start]^=1;p.write_bytes(raw)
            with self.assertRaises(InvalidArchive):load_archive(p)


if __name__=='__main__':
    unittest.main(verbosity=2)
