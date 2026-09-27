import json, hashlib, urllib.request
from pathlib import Path
root = Path(__file__).parent
url = 'https://webgrec.ub.edu/webpages/000005/cat/crafels.ub.edu.html'
record = {'url': url, 'reason': 'New author-page route discovered from official UB members list; web parser could not decode HTML.'}
try:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = response.read()
        record.update(status=response.status, final_url=response.url, headers=dict(response.headers), bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        (root/'rafels_author.html').write_bytes(payload)
except Exception as exc:
    record['error'] = str(exc)
(root/'author_direct_retrieval.json').write_text(json.dumps(record, indent=2))
print(json.dumps(record, indent=2))
