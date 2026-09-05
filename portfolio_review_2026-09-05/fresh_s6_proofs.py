from pathlib import Path
import hashlib
import json
import subprocess
import time

ROOT = Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery')
OUT = Path(__file__).resolve().parent
S6 = ROOT / 'coopgames/verifiers/s6'
TOOLS = Path('/Users/maxf/projects/economics-research/game-theory/experimental-runs/additive-efx-counting-runs/parkability/certification-20260801-v2/tools')
CVC = TOOLS / 'cvc5-1.3.3/cvc5-macOS-arm64-static/bin/cvc5'
ETHOS = TOOLS / 'ethos-0.2.3/ethos'
SIG = TOOLS / 'cvc5-1.3.3-source/proofs/eo/cpc'

def run(cmd):
    start = time.monotonic()
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, timeout=150)
    return {'exit_code': p.returncode, 'output': p.stdout.strip(), 'stderr': p.stderr.strip(), 'seconds': round(time.monotonic()-start,3)}

rows=[]
for family, audit_name, prefix in [
    ('strict','strict_exchange_direction_cores.json','strict_exchange_'),
    ('equality','equality_exchange_classification.json','equality_exchange_')
]:
    audit_path = S6 / audit_name
    if not audit_path.exists():
        if family == 'equality':
            records = sorted((S6/'certificates').glob('equality_exchange_*.json'))
        else: raise RuntimeError(str(audit_path))
    else:
        audit=json.loads(audit_path.read_text())
        records=[S6/'certificates'/f"{prefix}{r['case']}.json" for r in audit['rows']]
    if len(records)!=15: raise RuntimeError(f'wrong {family} record count {len(records)}')
    for record in records:
        data=json.loads(record.read_text())
        formula=record.with_suffix('.smt2'); proof=record.with_suffix('.cpc')
        for path,key,block in [(formula,'formula_sha256',data),(proof,'proof_sha256',data['cpc_proof'])]:
            if hashlib.sha256(path.read_bytes()).hexdigest()!=block[key]: raise RuntimeError('hash mismatch '+str(path))
        body=proof.read_text()
        if any(s in body.lower() for s in ('trust','hole','warning')):raise RuntimeError('forbidden proof marker')
        wrapper=OUT/'current-proof.cpc'
        wrapper.write_text(f'(include "{SIG / "Cpc.eo"}")\n(include "{SIG / "expert/CpcExpert.eo"}")\n'+body)
        cv=run([CVC,'--strict-parsing','--tlimit=120000',formula])
        ep=run([ETHOS,wrapper])
        okay=cv['exit_code']==0 and cv['output']=='unsat' and ep['exit_code']==0 and ep['output']=='correct'
        rows.append({'family':family,'record':str(record.relative_to(ROOT)),'formula_sha256':data['formula_sha256'],'proof_sha256':data['cpc_proof']['proof_sha256'],'cvc5':cv,'ethos':ep,'passed':okay})
        (OUT/'fresh_s6_proofs.json').write_text(json.dumps({'complete':False,'rows':rows},indent=2)+'\n')
        print(f"{family} {record.stem}: {'PASS' if okay else 'FAIL'}",flush=True)
        if not okay:raise RuntimeError(rows[-1])
(OUT/'fresh_s6_proofs.json').write_text(json.dumps({'complete':True,'count':len(rows),'rows':rows},indent=2)+'\n')
print('PASS: all 30 fresh cvc5 verdicts and Ethos proof checks',flush=True)
