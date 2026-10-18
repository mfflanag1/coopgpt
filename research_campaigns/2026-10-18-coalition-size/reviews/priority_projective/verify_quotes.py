#!/usr/bin/env python3
"""Check the source map's short quotations against saved original PDF text.

Normalizes typography/line wrapping and one documented PDF fi-glyph error.
It checks quoted words, not theorem hypotheses or page locators.
"""
from pathlib import Path
import json
import re
import unicodedata

HERE = Path(__file__).resolve().parent
SOURCES = (
    'moulin_sprumont_2004', 'sprumont_nearly_serial', 'sprumont_serial_2010',
    'immorlica_mahdian_mirrokni', 'immorlica_pountourakis_2012', 'dogan_2013',
    'zick_markakis_elkind_2014', 'coinvestment_2017', 'meir_rosenschein_malizia_2011',
    'bachrach_etal_2009', 'bansal_etal_2012', 'birmpas_etal_2019',
    'moulin_sprumont_survey_2005', 'moulin_vohra_2003', 'sprumont_aumann_2004',
)


def normalize(text):
    text = text.replace('satis…es', 'satisfies')
    text = re.sub(r'([a-z])-\s*\n\s*([a-z])', r'\1\2', text)
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text)).strip()


def main():
    blocks = re.split(r'\nS\d+\. ', (HERE/'SOURCE_THEOREM_MAP.txt').read_text())[1:]
    assert len(blocks) == len(SOURCES) == 15
    results = []
    for number, (block, key) in enumerate(zip(blocks, SOURCES), 1):
        match = re.search(r'Exact (?:proof )?excerpt: "([^"]+)"', block)
        assert match is not None
        quote = normalize(match.group(1))
        body = normalize((HERE/(key+'.txt')).read_text())
        results.append({'source': 'S'+str(number), 'file': key+'.txt',
                        'quote_matches_after_documented_normalization': quote in body,
                        'quoted_words': len(quote.split())})
    assert all(row['quote_matches_after_documented_normalization'] for row in results)
    assert all(row['quoted_words'] <= 25 for row in results)
    report = {'status': 'PASS', 'scope': 'quotation text only, not theorem validation',
              'normalization': 'NFKC, whitespace, end-of-line hyphenation, satis…es fi-glyph error',
              'entries': results}
    (HERE/'quote_verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'status': 'PASS', 'quoted_source_entries': len(results)}))


if __name__ == '__main__':
    main()
