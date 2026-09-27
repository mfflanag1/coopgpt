import json, hashlib, urllib.request, sys
from pathlib import Path
root = Path(__file__).parent
records = []
for url in sys.argv[1:]:
    record = {'url': url}
    try:
        with urllib.request.urlopen(url, timeout=25) as response:
            payload = response.read()
            name = 'public_' + hashlib.sha256(url.encode()).hexdigest()[:12] + '.txt'
            (root/name).write_bytes(payload)
            record.update(status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type'), bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(), file=name)
    except Exception as exc:
        record['error'] = str(exc)
    records.append(record)
recordpath=root/'public_assets_retrieval.json'
previous=json.loads(recordpath.read_text()) if recordpath.exists() else []
recordpath.write_text(json.dumps(previous+records, indent=2))
print(json.dumps(records, indent=2))
