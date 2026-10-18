#!/usr/bin/env python3
"""Bounded exact comparison for the new explanatory ladder, not a theorem test."""
from datetime import datetime, timezone
from fractions import Fraction as Q
from html.parser import HTMLParser
from math import comb
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
VIS = CAMP.parents[1]
HTML = VIS/'mega-build/CAMPAIGN_20261018.html'
JS = VIS/'mega-build/mega.js'


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.local=[]; self.href=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if 'data-local' in d: self.local.append(d['data-local'])
        if 'href' in d: self.href.append(d['href'])


def q_product(m):
    return Q(4**m, 2*comb(2*m,m))


def main():
    html_bytes, js_bytes = HTML.read_bytes(), JS.read_bytes()
    html, js = html_bytes.decode(), js_bytes.decode()
    (HERE/'DELTA_CHAPTER_SNAPSHOT.html').write_bytes(html_bytes)
    (HERE/'DELTA_MEGA_JS_SNAPSHOT.js').write_bytes(js_bytes)
    match=re.search(r'let q=1/3;const values=\[\];(.*?)const val=values\[M-1\]',js,re.S)
    assert match, 'Displayed recurrence code not found'
    actual='let q=1/3;const values=[];'+match.group(1)
    runner='const out=[];for(let s=2;s<=24;s++){const last=2*s;'+actual+'out.push({s,values});}process.stdout.write(JSON.stringify(out));\n'
    (HERE/'RUN_ACTUAL_LADDER.js').write_text(runner)
    node=shutil.which('node')
    assert node, 'A local Node runtime is needed to execute the actual arithmetic'
    executed=json.loads(subprocess.check_output([node,str(HERE/'RUN_ACTUAL_LADDER.js')],text=True))
    results=[]; count=0; max_error=0.0
    for case in executed:
        s=case['s']; h=(s+1)//2; product=Q(1); bounds=[]
        for m, js_value in enumerate(case['values'],1):
            if m>1:
                k=min(s-1,2*m-2); product*=Q(k,k+1)
            closed=q_product(m)/m if m<=h else q_product(h)/h*Q(s-1,s)**(m-h)
            assert product==closed
            exact=1+Q(2*(m-1),3)*product
            error=abs(js_value-float(exact)); max_error=max(max_error,error)
            assert error<1e-12
            assert 2*m+1<=97 and 2**(m+1)-1<=2**53-1
            count+=1; bounds.append(exact)
        peak=max(bounds); indices=[i+1 for i,b in enumerate(bounds) if b==peak]
        assert indices==[s,s+1]
        formula=1+Q(2*(s-1),3)*q_product(h)/h*Q(s-1,s)**(s-h)
        assert formula==peak and bounds[0]==1
        if s==6: assert peak==Q(493,243)
        results.append({'s':s,'checked_M':[1,2*s],'maximizers':indices,'peak':str(peak)})
    links=Links();links.feed(html)
    assert all(Path(p).is_file() for p in links.local)
    index=VIS/'research-campaigns/2026-10-18-coalition-size/campaign-index.html'
    assert index.is_file()
    assert 'with pure binary unit owners' in html
    assert 'with at least two input resources' in html
    assert 'Separable strictly convex, nondecreasing scalar-summary selectors' in html
    assert 'identical owner costs at identical features' in html
    assert 'rational technology and rational endowments' in html
    assert 'no matching upper on all 64 profiles is asserted' in html
    assert 'not a proposed mechanism' in html
    assert HTML.read_bytes()==html_bytes and JS.read_bytes()==js_bytes
    out={'status':'PASS','timestamp_utc':datetime.now(timezone.utc).isoformat(),
         'scope':'Scientific delta and explanatory arithmetic only; no campaign search/replay.',
         'arithmetic_values_checked':count,'s_range':[2,24],
         'executed_actual_javascript_arithmetic':True,'max_abs_float_error':max_error,
         'exact_recurrence_matches_closed_form':True,'peak_checks':results,
         'data_local_links_checked':len(links.local),'all_data_local_links_exist':True,
         'campaign_index_exists_at_assembled_document_root':True,
         'source_hashes':{str(HTML):hashlib.sha256(html_bytes).hexdigest(),
                          str(JS):hashlib.sha256(js_bytes).hexdigest(),
                          str(HERE/'CHAPTER_SNAPSHOT.html'):hashlib.sha256((HERE/'CHAPTER_SNAPSHOT.html').read_bytes()).hexdigest()}}
    Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='peak_checks'},indent=2))


if __name__=='__main__': main()
