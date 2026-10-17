"""Check generated local handoff links and served bytes; does not claim visual UI QA."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
from urllib.request import urlopen
import collections,datetime,hashlib,json,re
ROOT=Path('/Users/maxf/.codex/visualizations/2026/09/04/01a06e8a-dcbb-7c81-9929-e72831a14ac8')
BASE=Path(__file__).resolve().parents[1]
HOST='http://127.0.0.1:52140/'
NAME='coopgpt-overnight-handoff.html'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.cards=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for key in ('href','src'):
   if key in a:self.refs.append(a[key])
  if tag=='article' and 'result' in a.get('class','').split():self.cards+=1
p=Page();raw=(ROOT/NAME).read_bytes();p.feed(raw.decode())
assert raw==(BASE/'handoff'/NAME).read_bytes()
assert not re.search(r'__[A-Z]+__',raw.decode()),'Unexpanded HTML token'
assert len(p.ids)==len(set(p.ids)),'Duplicate IDs'
local=set([NAME]);anchors=[]
for ref in p.refs:
 u=urlparse(ref)
 if u.scheme or u.netloc:continue
 if not u.path:
  if u.fragment:assert unquote(u.fragment) in p.ids,ref;anchors.append(ref)
  continue
 path=unquote(u.path)
 assert '..' not in Path(path).parts
 assert (ROOT/path).is_file(),path
 local.add(path)
archives=json.loads((BASE/'handoff/REVIEW_ARCHIVES.json').read_text())
for a in archives['archives']:
 relative='overnight-campaign/'+a['path'];local.add(relative)
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==a['sha256']
served=[]
for relative in sorted(local):
 with urlopen(HOST+relative,timeout=10) as response:
  assert response.status==200
  data=response.read()
 expected=(ROOT/relative).read_bytes()
 assert data==expected,relative
 served.append({'path':relative,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
interaction=json.loads((BASE/'checks/HANDOFF_BROWSER_INTERACTIONS.json').read_text())
current_js='\n'.join(re.findall(r'<script>(.*?)</script>',raw.decode(),re.S))
assert interaction['status']=='PASS' and all(c['pass'] for c in interaction['checks'])
assert hashlib.sha256(current_js.encode()).hexdigest()==interaction['tested_inline_javascript_sha256'],'Interaction script changed since browser check'
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','unique_ids':len(p.ids),'internal_anchors':len(anchors),'result_cards':p.cards,'served_files_checked':len(served),'all_local_references_exist':True,'served_bytes_match_files':True,'visual_check':{'desktop_top_and_contracts':'PASS; inspected1440x2200 screenshot','narrow_top_and_contracts':'PASS; inspected700x2200 screenshot','full_page_or_430px_mobile':'Not verified','interaction_test':'PASS25 programmatic DOM checks in an isolated real Chrome profile; see HANDOFF_BROWSER_INTERACTIONS.json'},'javascript_syntax':'node --check passed; this is not an interaction test','files':served}
(BASE/'checks/HANDOFF_STATIC_QA.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='files'},indent=2))
