from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
r=Path('/private/tmp/coopgpt-ownership-20261016')
now=datetime.now(timezone.utc)
start=datetime.fromisoformat('2026-10-16T18:53:56+00:00')
minimum=datetime.fromisoformat('2026-10-17T00:53:56+00:00')
if now<minimum:raise RuntimeError('Main synthesis cannot close before the six-hour threshold')
ended=now.strftime('%Y-%m-%d %H:%M:%S UTC');elapsed=int((now-start).total_seconds())
p=r/'CURRENT_RESULTS.txt';s=p.read_text()
s=s.replace('Updated17October2026 after adjudication40. Campaign ACTIVE; main synthesis after00:53:56UTC.', 'Closed '+ended+' after adjudication41. Bounded campaign complete.')
a=s.index('LIVE, NOT YET ACCEPTED\n');b=s.index('\nATTRIBUTION / LIMITS',a)
s=s[:a]+'''FINAL BOUNDED8/5 ATTEMPT — STOPPED
- Accepted new SUBREGIME theorem: at physical hardware bottlenecks with full
  normalized capped total S>=2, sum E_i<(8/5)H. Exact continuous partition:
  2,020 certified leaves,200 geometric exclusions; independent root/Codex
  Fraction replays agree. Cross-model algebra/code review resolved. Adjudication41.
- Global8/5 remains OPEN. An exact rational vector satisfies all255 selected
  supporting rows strictly while its relaxed objective is1.6016197790>8/5.
  This is a finite-relaxation obstruction, not an actual game, an unrestricted
  lower bound, or an impossibility for all supporting parameters.
- Inverse-deficit PF support is accepted as a corollary of the reviewed IG8 and
  sharp individual-gap ceiling. Stronger floating support searches remain
  diagnostics only. Discovery stopped; no failed partial tree is called a proof.
- Main general funding theorem remains323/200. Exact next diffuse residual,
  unrestricted mechanism optimality, deeper-network bounds and novelty remain open.
'''+s[b:]
p.write_text(s)
p=r/'PROOF_MAP.txt';s=p.read_text()
s=s.replace('17 October2026 after adjudication40. ACTIVE research supplement;', 'Closed '+ended+' after adjudication41. Research supplement;')
s=s.replace('A newer8/5 certificate attempt is LIVE and NOT established. In particular,\nS>=2 does NOT automatically imply C^2; the unsupported statement in a draft\none-cap note was withdrawn. Its valid S<2 inequality is unaffected.', '''The bounded8/5 attempt is STOPPED. Adjudication41 accepts an independent
8/5 theorem for the S>=2 hardware-bottleneck subregime, plus an exact255-row
finite-relaxation obstruction below2. It does NOT establish global8/5.
S>=2 does NOT imply the previously asserted C^2 shortcut; that unsupported
draft pointer was withdrawn. The valid S<2 one-cap inequality is unaffected.
 root/entropy_general_certificate/eight_fifths/EIGHT_FIFTHS_SUBREGIME_AND_STOPPING_OBSTRUCTION.txt
 root/entropy_general_certificate/eight_fifths/verify_high_S_certificate.py''')
p.write_text(s)
p=r/'CAMPAIGN_REPORT.txt';s=p.read_text()
s=s.replace('Status: final consolidation in progress; closing audit not yet complete.', 'Completed: '+ended+'. Elapsed: '+str(elapsed//3600)+'h '+str((elapsed%3600)//60)+'m.\nStatus: bounded campaign complete; internal closing audit resolved through41.')
s=s.replace('A successful subregime certificate is being independently checked. It must not\nbe described as a global theorem.', '''The successful S>=2 hardware-bottleneck subregime certificate passed independent
exact replay and closing audit. It must not be described as a global theorem.
Its continuous partition has2,020 certified leaves and200 geometric exclusions,
with maximum approximately1.5999986058. Below S=2, an exact rational point
satisfies all255 selected relaxation rows but has objective1.6016197790>8/5.
This stops that finite relaxation, not the mathematical8/5 question itself.
Read root/entropy_general_certificate/eight_fifths/
EIGHT_FIFTHS_SUBREGIME_AND_STOPPING_OBSTRUCTION.txt and adjudication41.''')
p.write_text(s)
with (r/'PROGRESS.txt').open('a') as f:f.write('\nCLOSED '+ended+' after '+str(elapsed)+' seconds. General323/200, sharp diffuse\nasymptotic and sharp signedLambda accepted; bounded8/5 attempt stopped with\nverified high-S subtheorem and exact finite-relaxation obstruction. All live\ndiscovery stopped. Internal review complete through41; external review and\nnovelty remain open. Canonical manuscripts not edited; no Git commit/push.\n')
status={'status':'complete','start_utc':start.isoformat(),'end_utc':now.isoformat(),'elapsed_seconds':elapsed,'main_general_factor':'323/200','global_8_5':'open; bounded attempt stopped','latest_adjudication':41,'canonical_manuscript_edited':False,'git_committed_or_pushed':False,'external_specialist_review':False,'novelty_cleared':False}
(r/'CAMPAIGN_STATUS.json').write_text(json.dumps(status,indent=2,sort_keys=True)+'\n')
proofs=sorted((r/'audits').glob('ROOT_REVIEW_ADJUDICATION_*.txt'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
if [int(p.stem.rsplit('_',1)[1]) for p in proofs]!=list(range(1,42)):raise RuntimeError('Adjudication sequence incomplete')
(r/'audits/ADJUDICATION_HASHES_FINAL.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in proofs},indent=2,sort_keys=True)+'\n')
print(json.dumps(status,indent=2,sort_keys=True))
