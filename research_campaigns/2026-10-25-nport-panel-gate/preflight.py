#!/usr/bin/env python3
"""Offline integrity/schema/sample preflight for the fixed 2025Q2 N-PORT ZIP.

No network, archive extraction, headline residuals or automatic research promotion.
The output distinguishes field-compatible candidates from source-validated funds.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

NODES = ['3MON', '1YR', '5YR', '10YR', '30YR']
METRICS = [f'INTRST_RATE_CHANGE_{n}_{m}' for m in ['DV01', 'DV100'] for n in NODES]
FIELDS = {
    'SUBMISSION.tsv': ['ACCESSION_NUMBER', 'FILING_DATE', 'REPORT_DATE', 'SUB_TYPE'],
    'REGISTRANT.tsv': ['ACCESSION_NUMBER', 'CIK'],
    'FUND_REPORTED_INFO.tsv': ['ACCESSION_NUMBER', 'SERIES_ID', 'SERIES_NAME', 'NET_ASSETS', 'TOTAL_ASSETS', 'TOTAL_LIABILITIES'],
    'INTEREST_RATE_RISK.tsv': ['ACCESSION_NUMBER', 'INTEREST_RATE_RISK_ID', 'CURRENCY_CODE'] + METRICS,
    'EXPLANATORY_NOTE.tsv': ['ACCESSION_NUMBER', 'EXPLANATORY_NOTE_ID', 'ITEM_NO', 'EXPLANATORY_NOTE'],
}
KEYS = {name: ['ACCESSION_NUMBER'] for name in FIELDS}
KEYS['INTEREST_RATE_RISK.tsv'].append('INTEREST_RATE_RISK_ID')
KEYS['EXPLANATORY_NOTE.tsv'].append('EXPLANATORY_NOTE_ID')


class InvalidArchive(ValueError):
    pass


def number(text):
    # Preserve blank != zero and reject nonfinite or nonstandard encodings.
    if not text or not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)', text):
        raise ValueError('missing_or_invalid_decimal')
    value = Decimal(text)
    if not value.is_finite():
        raise ValueError('nonfinite_decimal')
    return value


def parse_date(text):
    # The inspected archive metadata specifies DD-MON-YYYY.
    if not re.fullmatch(r'\d{2}-[A-Za-z]{3}-\d{4}', text):
        raise ValueError('date_does_not_match_metadata')
    return datetime.strptime(text, '%d-%b-%Y').date()


def load_archive(path):
    if path.suffix.lower() != '.zip':
        raise InvalidArchive('A completed .zip file is required; partial downloads are refused.')
    with path.open('rb') as stream:
        hasher = hashlib.sha256()
        while chunk := stream.read(1024 * 1024):
            hasher.update(chunk)
        digest = hasher.hexdigest()
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if len(names) != len(set(names)):
                raise InvalidArchive('Duplicate archive member names.')
            required = set(FIELDS) | {'nport_metadata.json'}
            if not required.issubset(names):
                raise InvalidArchive('Missing required tables or metadata.')
            # Read every member to EOF: ZIP CRC must pass, including tables not used here.
            # Bound expansion without extracting paths or executing archive contents.
            if sum(i.file_size for i in z.infolist()) > 12_000_000_000:
                raise InvalidArchive('Archive expands above the 12GB safety ceiling.')
            for item in z.infolist():
                with z.open(item) as stream:
                    while stream.read(1024 * 1024):
                        pass
            metadata = json.loads(z.read('nport_metadata.json'))
            if not isinstance(metadata, dict) or not isinstance(metadata.get('tables'), list):
                raise InvalidArchive('Metadata must contain a tables array.')
            dialect = metadata.get('dialect', {})
            if (not isinstance(dialect, dict) or dialect.get('delimiter') != '\t'
                    or dialect.get('header', True) is not True
                    or dialect.get('headerRowCount', 1) != 1):
                raise InvalidArchive('Unsupported metadata dialect; inspect before parsing.')
            quote = dialect.get('quoteChar', '"')  # CSVW default, not assumed unquoted.
            if quote not in {None, '"'} or dialect.get('doubleQuote', True) is not True:
                raise InvalidArchive('Unsupported metadata quoting convention.')
            schema = {t['url']: t['tableSchema'] for t in metadata['tables']}
            for column in schema['SUBMISSION.tsv']['columns']:
                if column['name'] in {'REPORT_DATE', 'FILING_DATE'} and column['datatype']['base'] != 'date (DD-MON-YYYY)':
                    raise InvalidArchive('Unsupported metadata date format.')
            tables = {}
            for name, required_fields in FIELDS.items():
                declared = {c['name'] for c in schema[name]['columns']}
                if not set(required_fields).issubset(declared):
                    raise InvalidArchive(f'Metadata fields missing: {name}')
                if z.getinfo(name).file_size > 600_000_000:
                    raise InvalidArchive(f'Preflight input table exceeds 600MB: {name}')
                with z.open(name) as raw:
                    reader = csv.DictReader(io.TextIOWrapper(raw, encoding='utf-8-sig', newline=''),
                        delimiter='\t', quotechar=quote, quoting=csv.QUOTE_NONE if quote is None else csv.QUOTE_MINIMAL,
                        strict=True)
                    if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
                        raise InvalidArchive(f'Invalid column header: {name}')
                    if not set(required_fields).issubset(reader.fieldnames):
                        raise InvalidArchive(f'Table fields missing: {name}')
                    rows, seen = [], set()
                    for row in reader:
                        if None in row or any(v is None for v in row.values()):
                            raise InvalidArchive(f'Malformed TSV row: {name}')
                        key = tuple(row[k] for k in KEYS[name])
                        if not all(key) or key in seen:
                            raise InvalidArchive(f'Duplicate/blank table primary key: {name}')
                        seen.add(key)
                        rows.append(row)
                    tables[name] = rows
    except (zipfile.BadZipFile, EOFError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise InvalidArchive(str(error)) from error
    return tables, digest


def screen(tables):
    submissions = tables['SUBMISSION.tsv']
    sub = {r['ACCESSION_NUMBER']: r for r in submissions}
    fund = {r['ACCESSION_NUMBER']: r for r in tables['FUND_REPORTED_INFO.tsv']}
    registrant = {r['ACCESSION_NUMBER']: r for r in tables['REGISTRANT.tsv']}
    risks, notes = defaultdict(list), defaultdict(list)
    for name, rows in tables.items():
        if name != 'SUBMISSION.tsv' and any(r['ACCESSION_NUMBER'] not in sub for r in rows):
            raise InvalidArchive(f'Orphan accession: {name}')
    for r in tables['INTEREST_RATE_RISK.tsv']:
        risks[r['ACCESSION_NUMBER']].append(r)
    for r in tables['EXPLANATORY_NOTE.tsv']:
        notes[r['ACCESSION_NUMBER']].append(r)
    excluded, versions, coverage = [], defaultdict(list), Counter()

    def reject(acc, reason):
        excluded.append({'accession': acc, 'reason': reason})

    for row in submissions:
        acc = row['ACCESSION_NUMBER']
        coverage[row['REPORT_DATE']] += 1
        try:
            reported, filed = parse_date(row['REPORT_DATE']), parse_date(row['FILING_DATE'])
        except ValueError:
            reject(acc, 'invalid_date'); continue
        if reported != date(2025, 3, 31):
            reject(acc, 'outside_fixed_reference_date'); continue
        if not date(2025, 4, 1) <= filed <= date(2025, 6, 30):
            reject(acc, 'outside_fixed_filing_quarter'); continue
        if row['SUB_TYPE'] not in {'NPORT-P', 'NPORT-P/A'}:
            reject(acc, 'not_portfolio_filing'); continue
        f = fund.get(acc)
        if f is None:
            # Otherwise an unlinked later amendment might silently revive an
            # earlier version of the same fund. Repair the join before screening.
            raise InvalidArchive('Target-date portfolio filing lacks its fund row: ' + acc)
        sid = f['SERIES_ID']
        if not sid:
            reject(acc, 'missing_series_id'); continue
        versions[sid].append((filed, acc))

    candidates, amendments = [], []
    for sid, filings in sorted(versions.items()):
        ordered = sorted(filings)
        acc = ordered[-1][1]
        amendments.append({'series_id': sid, 'selected': acc, 'all_batch_accessions': [x[1] for x in ordered]})
        for _, superseded in ordered[:-1]:
            reject(superseded, 'superseded_within_batch')
        f = fund[acc]
        usd = [r for r in risks[acc] if r['CURRENCY_CODE'] == 'USD']
        if not risks[acc]:
            reject(acc, 'b3_omitted_reason_unknown'); continue
        if not usd:
            reject(acc, 'no_usd_entry'); continue
        if len(usd) != 1:
            reject(acc, 'duplicate_usd_entries'); continue
        try:
            nav = number(f['NET_ASSETS'])
            assets, liabilities = number(f['TOTAL_ASSETS']), number(f['TOTAL_LIABILITIES'])
            values = [number(usd[0][key]) for key in METRICS]
        except (ValueError, InvalidOperation):
            reject(acc, 'missing_or_invalid_financial_field'); continue
        if nav <= 0:
            reject(acc, 'nonpositive_nav'); continue
        # Exact decimal comparison only. A mismatch is quarantined for documented
        # source precision reconciliation, not diagnosed as a reporting error.
        from fractions import Fraction
        if Fraction(assets) - Fraction(liabilities) != Fraction(nav):
            reject(acc, 'nav_reconciliation_requires_source_check'); continue
        candidates.append({
            'series_id': sid, 'accession': acc,
            'cik': registrant.get(acc, {}).get('CIK') or None,
            'series_name': f['SERIES_NAME'], 'nav': f['NET_ASSETS'],
            'currency': 'USD', 'raw_metrics': {k: usd[0][k] for k in METRICS},
            'all_zero_vector': all(v == 0 for v in values),
            'notes': notes[acc],
            'units_and_direction': 'source_review_required',
            'source_validated': False,
        })
    return {
        'table_rows': {k: len(v) for k, v in tables.items()},
        'reference_date_coverage': dict(sorted(coverage.items())),
        'filing_date_coverage': dict(sorted(Counter(r['FILING_DATE'] for r in submissions).items())),
        'exclusion_counts': dict(sorted(Counter(x['reason'] for x in excluded).items())),
        'exclusions': excluded, 'amendment_audit': amendments,
        'field_compatible_candidate_count': len(candidates),
        'candidate_scale_screen_at_least_100': len(candidates) >= 100,
        'protocol_scale_gate': 'NOT_EVALUATED_field_screen_only; resolve source conventions and quarantined NAV/format rows first',
        'candidate_all_zero_vectors': sum(x['all_zero_vector'] for x in candidates),
        'candidates': candidates,
        'materiality_gate': 'NOT_EVALUATED', 'economic_interpretation_gate': 'NOT_EVALUATED',
        'headline_residuals_computed': False,
        'warning': 'Field compatibility is not source validation or economic interpretation. No B.3 exemption inferred from absence. Current archive is not a real-time vintage.',
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Output exists; preserve previous results by using a new path.')
    try:
        tables, digest = load_archive(args.archive)
        result = screen(tables)
        result.update(status='preflight_only', archive_sha256=digest,
                      archive_bytes=args.archive.stat().st_size)
    except (InvalidArchive, OSError, UnicodeError, csv.Error) as error:
        result = {'status': 'STOP_PREFLIGHT_VALIDATION', 'reason': str(error),
                  'research_gate_conclusion': 'NONE; parser/integrity failures are not empirical failures',
                  'headline_residuals_computed': False}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in {
        'candidates', 'exclusions', 'amendment_audit', 'reference_date_coverage', 'filing_date_coverage'}}, indent=2))


if __name__ == '__main__':
    main()
