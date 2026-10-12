"""Primary fixed-contract scoring from saved raw calls; no inference or repairs."""
import argparse,json
from pathlib import Path
from contract import validate_inputs,summarize

def main(base,capture):
    cases,controls=validate_inputs(base);folder=Path(capture)/'collection'
    def text(key):
        path=folder/(key+'.json')
        if not path.exists():return None
        raw=json.loads(path.read_text())
        return ''.join(c['data'].get('response','') for c in raw['requests'][0]['chunks'])
    primary={j['request_id']:text('p_'+j['request_id']) for j in cases}
    checker={key:text(key) for key in ['n_'+j['request_id'] for j in cases]+[c['request_id'] for c in controls]}
    return summarize(cases,controls,{k:v for k,v in primary.items() if v is not None},{k:v for k,v in checker.items() if v is not None})
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('base',type=Path);parser.add_argument('capture',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=main(args.base,args.capture);args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['natural','controlled']},sort_keys=True))
