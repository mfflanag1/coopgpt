"""Portable consolidated runner; subprocess failures invalidate success."""
from pathlib import Path
import argparse,json,subprocess,sys,time,os
ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--smt',action='store_true');args=parser.parse_args()
    dest=ROOT/'results';dest.mkdir(exist_ok=True);summary=dest/'SUMMARY.json'
    summary.write_text(json.dumps({'status':'RUNNING','smt':args.smt})+'\n')
    jobs=[('graph_dichotomy','verify.py'),('simultaneous_protection','verify.py')]
    if args.smt:jobs.insert(0,('tree_extension','check_clipping.py'))
    results=[]
    try:
        for folder,script in jobs:
            command=[sys.executable,'-O',str(ROOT/folder/script)]
            if args.smt and folder!='tree_extension':command.append('--smt')
            started=time.time()
            with (dest/(folder+'.log')).open('w') as log:
                proc=subprocess.run(command,cwd=ROOT/folder,stdout=log,stderr=subprocess.STDOUT,timeout=1800,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
            if proc.returncode:raise RuntimeError(f'{folder}: exit {proc.returncode}')
            result_file=ROOT/folder/('CLIPPING_RESULTS.json' if folder=='tree_extension' else 'VERIFICATION.json')
            report=json.loads(result_file.read_text())
            if report.get('status')!='PASS':raise RuntimeError(f'{folder}: no PASS report')
            results.append({'stage':folder,'status':'PASS','elapsed_seconds':round(time.time()-started,2),'report':str(result_file.relative_to(ROOT))})
        result={'status':'PASS','smt':args.smt,'stages':results,'scope':'Finite corroboration; universal theorems are proved in the manuscript'}
        summary.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    except BaseException as error:
        summary.write_text(json.dumps({'status':'FAILED','smt':args.smt,'completed_stages':results,'error':str(error)},indent=2)+'\n');raise
if __name__=='__main__':main()
