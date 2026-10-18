"""Bounded retrieval of named free research originals; no application data."""
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib, json, subprocess, sys, time

ROOT = Path(__file__).resolve().parent
SOURCES = {
    'immorlica_mahdian_mirrokni': 'https://immorlica.com/pubs/costshare.pdf',
    'dogan_2013': 'https://econ.gatech.edu/sites/default/files/seminars/201402/absence-proofness.pdf',
    'sprumont_nearly_serial': 'https://www.cireqmontreal.com/wp-content/uploads/cahiers/17-2004-cah.pdf',
    'immorlica_pountourakis_2012': 'https://immorlica.com/pubs/edgeCover.pdf',
    'zick_markakis_elkind_2014': 'https://people.cs.umass.edu/~yzick/papers/ocf_theoretical.pdf',
    'meir_rosenschein_malizia_2011': 'https://www.ijcai.org/Proceedings/11/Papers/060.pdf',
    'coinvestment_2017': 'https://diposit.ub.edu/server/api/core/bitstreams/d325b225-7dde-44ff-8a35-cd848434e593/content',
    'juarez_collusion': 'https://www2.hawaii.edu/~rubenj/groupstrategyproof_indiff3.pdf',
    'sprumont_serial_2010': 'https://epe.lac-bac.gc.ca/100/200/300/cireq/cahiers/2010/01-2010-cah.pdf?nodisclaimer=1',
    'bansal_etal_2012': 'https://theoryofcomputing.org/articles/v008a024/v008a024.pdf',
    'birmpas_etal_2019': 'https://drops.dagstuhl.de/storage/00lipics/lipics-vol144-esa2019/LIPIcs.ESA.2019.20/LIPIcs.ESA.2019.20.pdf',
    'moulin_sprumont_survey_2005': 'https://www.ruf.rice.edu/~econ/papers/2005papers/moulin%2009.pdf',
    'moulin_vohra_2002': 'https://www.kellogg.northwestern.edu/research/math/papers/1364.pdf',
    'moulin_vohra_2003_mirror': 'https://citeseerx.ist.psu.edu/document?doi=88b501d728d70aa07052617e624e0b977503ff09&repid=rep1&type=pdf',
    'sprumont_aumann_2004': 'https://cireqmontreal.com/wp-content/uploads/cahiers/11-2004-cah.pdf',
    'moulin_vohra_2003': 'https://www.ruf.rice.edu/~econ/papers/2003papers/07Moulin.pdf',
}
if __name__ == '__main__':
    ledger_path = ROOT / 'source_ledger.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    for key in sys.argv[1:]:
        url = SOURCES[key]
        row = {'key': key, 'url': url, 'retrieved_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        try:
            req = Request(url, headers={'User-Agent': 'Research-source-audit/1.0'})
            with urlopen(req, timeout=30) as response:
                body = response.read(5_000_001)
                row['final_url'] = response.url
            row['bytes'] = len(body)
            if len(body)>5_000_000:
                raise ValueError('per-original 5MB cap reached')
            if not body.startswith(b'%PDF'):
                raise ValueError('response is not PDF')
            target = ROOT / (key + '.pdf')
            target.write_bytes(body)
            row['sha256'] = hashlib.sha256(body).hexdigest()
            subprocess.run(['pdftotext', '-layout', str(target), str(target.with_suffix('.txt'))], check=True)
            row['status'] = 'downloaded_and_text_extracted'
        except Exception as exc:
            row['status'] = 'failed'
            row['error'] = str(exc)
        ledger.append(row)
        ledger_path.write_text(json.dumps(ledger, indent=2)+'\n')
        print(json.dumps(row))
