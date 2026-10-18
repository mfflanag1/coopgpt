#!/usr/bin/env python3
"""Packet integrity/static closure only. No scientific replay or UI claims."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import ast
import hashlib
import json
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
PACKET = CAMP / 'specialist_packet'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]; self.ids=[]; self.tags=[]; self.remote_attrs=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        attrs=dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href','src','action','poster','srcset'):
            if key in attrs:
                self.links.append((key,attrs[key]))

def main():
    manifest_path=PACKET/'MANIFEST.json'
    manifest=json.loads(manifest_path.read_text())
    require(manifest['status']=='PREPARED_NOT_SENT','Unexpected packet status')
    require(len(manifest['source_files'])==13,'Unexpected source count')
    expected={'MANIFEST.json'}
    scientific=[]
    for row in manifest['source_files']:
        rel=row['packet_path']; source=CAMP/row['source_path_relative_to_campaign']
        copied=PACKET/rel
        require(rel not in expected,'Duplicate manifest path')
        expected.add(rel)
        a,b=source.read_bytes(),copied.read_bytes()
        require(a==b,'Source/packet bytes differ: '+rel)
        require(len(a)==row['bytes'],'Incorrect byte count: '+rel)
        require(digest(a)==row['source_sha256']==row['packet_sha256'],
                'Manifest hash mismatch: '+rel)
        scientific.append({'path':rel,'sha256':digest(a),'bytes':len(a)})
    for row in manifest['generated_files']:
        rel=row['packet_path']; data=(PACKET/rel).read_bytes()
        require(rel not in expected,'Duplicate presentation path')
        expected.add(rel)
        require(len(data)==row['bytes'] and digest(data)==row['sha256'],
                'Presentation hash mismatch: '+rel)
    actual={str(p.relative_to(PACKET)) for p in PACKET.rglob('*') if p.is_file()}
    require(actual==expected,'Unmanifested or missing packet file')
    require(not any(p.is_symlink() for p in PACKET.rglob('*')),'Unexpected packet symlink')

    page=Page(); html=(PACKET/'START_HERE.html').read_text(); page.feed(html)
    require(len(page.ids)==len(set(page.ids)),'Duplicate HTML id')
    linked=set(); fragments=0
    for kind,link in page.links:
        u=urlsplit(link)
        require(not u.scheme and not u.netloc,'Nonlocal HTML reference: '+link)
        target=(PACKET/unquote(u.path)).resolve() if u.path else (PACKET/'START_HERE.html')
        require(target.is_relative_to(PACKET.resolve()) and target.is_file(),
                'Missing/outside local HTML target: '+link)
        linked.add(str(target.relative_to(PACKET.resolve())))
        if u.fragment:
            require(target.name=='START_HERE.html' and unquote(u.fragment) in page.ids,
                    'Missing fragment: '+link)
            fragments+=1
    require(linked==actual,'Page does not link every included file')
    require('script' not in page.tags,'Unexpected JavaScript')
    require(not re.search(r'url\s*\(|@import',html,re.I),'Unexpected CSS external-resource rule')

    runner=ast.parse((PACKET/'reproduce_campaign.py').read_text())
    func=next(n for n in runner.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    jobs=next(n for n in ast.walk(func) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='jobs' for t in n.targets))
    jobs=ast.literal_eval(jobs.value)
    require(len(jobs)==2,'Unexpected basic job count')
    basic=[]
    for label,relative,args,fixtures in jobs:
        require((PACKET/relative).is_file(),'Missing basic checker')
        require(not fixtures,'Unexpected basic fixture dependency')
        tree=ast.parse((PACKET/relative).read_text())
        imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): imports.update(n.name.split('.')[0] for n in node.names)
            if isinstance(node,ast.ImportFrom): imports.add(node.module.split('.')[0])
        require(imports<=sys.stdlib_module_names,'Basic nonstandard import')
        basic.append({'name':label,'script':relative,'arguments':args,'fixtures':fixtures,
                      'imports':sorted(imports)})
    require(jobs[0][2]==['--max-geometry-m','4','--max-scalar-m','64'],
            'Basic advertised bounds mismatch')
    require(manifest['replay']['supported_suite']=='basic' and
            manifest['replay']['extended_inputs_included'] is False,'Replay scope mismatch')

    archive=CAMP/'specialist_packet.zip'
    with zipfile.ZipFile(archive) as z:
        entries=z.infolist()
        names=[i.filename for i in entries]
        require(len(names)==len(set(names)),'Duplicate ZIP path')
        require(z.testzip() is None,'ZIP CRC failure')
        files={i.filename for i in entries if not i.is_dir()}
        require(files=={'specialist_packet/'+p for p in actual},'ZIP file inventory mismatch')
        for name in names:
            path=PurePosixPath(name)
            require(not path.is_absolute() and '..' not in path.parts,'Unsafe ZIP path')
        for relative in actual:
            require(z.read('specialist_packet/'+relative)==(PACKET/relative).read_bytes(),
                    'ZIP/local bytes differ: '+relative)
    out={'status':'PASS','checked_utc':datetime.now(timezone.utc).isoformat(),
         'source_copies':len(scientific),'packet_files':len(actual),'zip_files':len(files),
         'all_source_copies_match_current_campaign_and_manifest':True,
         'all_zip_files_match_packet_bytes':True,'zip_crc':'PASS',
         'html_local_reference_occurrences':len(page.links),'html_unique_linked_files':len(linked),
         'html_fragments_checked':fragments,'external_html_assets_or_scripts':False,
         'basic_static_input_closure':basic,
         'scientific_replay_executed_by_this_audit':False,'browser_UI_executed_by_this_audit':False,
         'zip_sha256':digest(archive.read_bytes()),'manifest_sha256':digest(manifest_path.read_bytes()),
         'start_here_sha256':digest((PACKET/'START_HERE.html').read_bytes()),
         'readme_sha256':digest((PACKET/'README.txt').read_bytes()),
         'sources':scientific,
         'scope':'Delivery and claim/source consistency audit. Root owns extracted basic replay and UI. No new theorem, novelty or complete-source-archive claim.'}
    (HERE/'CHECK_RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
