"""Replay earlier standard-library verifiers, writing only inside this cycle."""
from pathlib import Path
import hashlib,json,runpy

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'cycle3'/'experiment'
if not SOURCE.is_dir():SOURCE=Path('/private/tmp/coopgt-pairadd-cycle3/experiment')

def main():
    dest=ROOT/'calibration';dest.mkdir(exist_ok=True)
    names=['finite_attainment_exact.json','composition_input.json','composition_exact.json','composition_210_input.json','composition_210_exact.json']
    for name in names:(dest/name).write_bytes((SOURCE/name).read_bytes())
    first=runpy.run_path(str(SOURCE/'verify_bridge_counterexample.py'));first['main'].__globals__['ROOT']=dest;first['main']()
    second=runpy.run_path(str(SOURCE/'verify_composition.py'));second['main'].__globals__['ROOT']=dest
    for tag in ('201','210'):second['main'](tag)
    manifest=dict(status='PASS',source=str(SOURCE),source_hashes={name:hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() for name in names+['verify_bridge_counterexample.py','verify_composition.py']},finite_ratio='1/6',composition_201_ratio='2/9',composition_210_ratio='2/9')
    (ROOT/'calibration_summary.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
