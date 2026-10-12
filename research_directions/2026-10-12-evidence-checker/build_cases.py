"""Reconstruct fresh authored cases from pinned source slices and saved specifications."""
from pathlib import Path
import hashlib,html,json,re
BASE=Path(__file__).resolve().parent

def normalized_with_offsets(raw,strip_html):
    chars=[];spans=[];at=0
    token=re.compile(r'<[^>]*>|&(?:#\d+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);') if strip_html else re.compile(r'(?!)')
    for match in token.finditer(raw):
        for i in range(at,match.start()):chars.append(raw[i]);spans.append((i,i+1))
        shown=' ' if match.group().startswith('<') else html.unescape(match.group())
        for char in shown:chars.append(char);spans.append((match.start(),match.end()))
        at=match.end()
    for i in range(at,len(raw)):chars.append(raw[i]);spans.append((i,i+1))
    out=[];mapping=[]
    for ch,span in zip(chars,spans):
        if ch.isspace():
            if out and out[-1]==' ':mapping[-1]=(mapping[-1][0],span[1])
            else:out.append(' ');mapping.append(span)
        else:out.append(ch);mapping.append(span)
    return ''.join(out),mapping

def make_excerpt(source,anchors,identifier):
    raw=(BASE/source).read_text();strip=source.endswith('.shtml');norm,mapping=normalized_with_offsets(raw,strip)
    start,end=[' '.join(a.split()) for a in anchors]
    a=norm.index(start);b=norm.index(end,a)+len(end)
    lo,hi=mapping[a][0],mapping[b-1][1];piece=raw[lo:hi]
    shown=' '.join(html.unescape(re.sub(r'<[^>]*>',' ',piece)).split()) if strip else piece
    return dict(id=identifier,text=shown,source_file=source,source_char_start=lo,source_char_end=hi,source_text_sha256=hashlib.sha256(piece.encode()).hexdigest(),transformation='strip_html_and_collapse_whitespace' if strip else 'verbatim')

def main():
    spec=json.loads((BASE/'CASE_SPEC.json').read_text());sources={s['id']:s['source_file'] for s in json.loads((BASE/'SOURCE_MANIFEST.json').read_text())};cases=[]
    for item in spec['cases']:
        remap={k:'D'+str(i+1) for i,k in enumerate(item['packet'])};source=item['source_id']
        passages=[make_excerpt(sources[source],spec['anchors'][source][k],remap[k]) for k in item['packet']]
        label=item['label'];claim=item['claim'];cid=hashlib.sha256(('coop-evidence-check-20261012:'+source+':'+claim).encode()).hexdigest()[:20]
        cases.append(dict(request_id=cid,author_id=item['author_id'],source_id=source,claim=claim,label=label,passages=passages,acceptable_evidence=[[remap[x] for x in proof] for proof in item['proofs']],relevant_evidence=[remap[x] for x in item['relevant']],rationale=item['rationale'],max_output_tokens=256))
    cases.sort(key=lambda j:hashlib.sha256(('order:'+j['request_id']).encode()).hexdigest())
    (BASE/'cases.json').write_text(json.dumps(cases,indent=2,sort_keys=True)+'\n')
    blind=[{k:j[k] for k in ['request_id','source_id','claim','passages']} for j in cases]
    (BASE/'BLIND_CASES.json').write_text(json.dumps(blind,indent=2,sort_keys=True)+'\n')
    print('Built',len(cases),'cases.')
if __name__=='__main__':main()
