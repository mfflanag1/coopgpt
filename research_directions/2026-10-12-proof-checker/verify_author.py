from pathlib import Path
from collections import Counter
import json,hashlib,re,html,itertools
BASE=Path(__file__).resolve().parent

def verify():
 sources={s['id']:s for s in json.loads((BASE/'SOURCE_MANIFEST.json').read_text())};cases=json.loads((BASE/'AUTHOR_CASES.json').read_text());assertlen=len(cases)
 if assertlen!=24 or len({c['author_id'] for c in cases})!=24:raise ValueError('24 unique cases required')
 counts=Counter();labels=Counter()
 for c in cases:
  sid=c['source_id'];src=sources[sid];raw=(BASE/src['source_file']).read_text();counts[sid]+=1
  ps=c['passages'];ids={p['id'] for p in ps}
  if len(ps) not in [3,4] or len(ids)!=len(ps) or not 100<=sum(len(p['text'].split()) for p in ps)<=450:raise ValueError(('packet size',c['author_id']))
  for p in ps:
   lo,hi=p['source_char_start'],p['source_char_end'];piece=raw[lo:hi]
   if type(lo)is not int or type(hi)is not int or not 0<=lo<hi<=len(raw) or p['source_file']!=src['source_file'] or hashlib.sha256(piece.encode()).hexdigest()!=p['source_text_sha256']:raise ValueError(('offset/hash',c['author_id']))
   if p['transformation']=='verbatim':shown=piece
   elif p['transformation']=='strip_html_and_collapse_whitespace':shown=' '.join(html.unescape(re.sub(r'<[^>]*>',' ',piece)).split())
   else:raise ValueError('transform')
   if shown!=p['text']:raise ValueError(('source slice',c['author_id']))
  parts=c['components']
  if [x['id'] for x in parts]!=['a1','a2']:raise ValueError('two ordered components')
  for part in parts:
   s,t=part['support'],part['contradict'];state='supported' if s and not t else 'contradicted' if t and not s else 'insufficient' if not s and not t else 'conflict'
   if state!=part['label'] or not part['claim'].strip():raise ValueError('component status')
   for proof in s+t:
    if not 1<=len(proof)<=3 or len(set(proof))!=len(proof) or not set(proof)<=ids:raise ValueError('proof ids')
  states=[p['label'] for p in parts];label='contradicted' if 'contradicted' in states else 'supported' if set(states)=={'supported'} else 'insufficient';labels[label]+=1
  if label=='supported':
   combinations=[set(a)|set(z) for a,z in itertools.product(parts[0]['support'],parts[1]['support'])]
   if not any(len(x)<=3 for x in combinations):raise ValueError('support union too large')
   if any(set(a)<=set(z) or set(z)<=set(a) for a,z in itertools.product(parts[0]['support'],parts[1]['support'])):raise ValueError('both components need distinct proof')
  elif sorted(states)!=sorted(['supported',label]):raise ValueError('one known true plus one false/unknown required')
 if counts!=Counter(dict.fromkeys(sources,4)) or labels!=Counter(supported=8,contradicted=8,insufficient=8):raise ValueError(('composition',counts,labels))
 print(json.dumps(dict(cases=len(cases),source_balance=dict(counts),label_balance=dict(labels),source_slices_valid=True)))
if __name__=='__main__':verify()
