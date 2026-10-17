from pathlib import Path
import json,hashlib
b=Path('/private/tmp/coopgpt-overnight-20261017')
p=b/'handoff/MINIMAL_REVIEW_PACKETS.json';d=json.loads(p.read_text())
for packet in d['main_packets']:
 packet['source_gates_unresolved']=[x for x in packet['source_gates_unresolved'] if not x.startswith('Young1985 source')]
 names=['sources/FINAL_YOUNG1985_GATE.txt']
 if packet['id']=='B':names.append('sources/FINAL_BALOG2017_GATE.txt')
 packet['necessary_extra_files']=[{'path':n,'role':'late original-source attribution clarification; not a mathematical proof dependency','sections':'all','sha256':hashlib.sha256((b/n).read_bytes()).hexdigest()} for n in names]
for archive in d['archive_sets']:
 if archive['id'] in ['A','A-with-partial-frontier','B']:
  archive['proof_and_evidence_paths'].append('sources/FINAL_YOUNG1985_GATE.txt')
 if archive['id']=='B':archive['proof_and_evidence_paths'].append('sources/FINAL_BALOG2017_GATE.txt')
p.write_text(json.dumps(d,indent=2)+'\n')
p=b/'handoff/REVIEW_READING_ORDER.txt';s=p.read_text()
s=s.replace('There are two proposed main packets, with 14 and 15 essential files respectively.','There are two proposed main packets, with14and15essential files respectively,\nplus one and two late source-attribution addenda listed as necessary extras.')
s=s.replace('exhaustive priority for the quantitative sharp contracts. Young1985 is a further\nattribution task. Different abstracts or terminology do not resolve those gates.','''exhaustive priority for the quantitative sharp contracts. The Young1985 original
was found and directly inspected: FINAL_YOUNG1985_GATE.txt traces the exact
five-player example and distinguishes its characteristic-function monotonicity
from TCWM. That attribution task is resolved; quantitative novelty is not.''')
s=s.replace('Denault\'s static allocation result does not by itself establish this dynamic\nwithdrawal contract. Moulin1999, the final Balog2017 original, and related\nentry-monotone pool comparisons remain source gates. Combined novelty is unconfirmed.','''Denault's static allocation result does not by itself establish this dynamic
withdrawal contract. The Young1985 antecedent is now directly checked. The late
Balog2017 note adds precise definitions from an author presentation, without
substituting it for the unavailable final article. Moulin1999, the final
Balog2017 original, and related entry-monotone pool comparisons remain source
gates. Combined novelty is unconfirmed.''')
p.write_text(s)
p=b/'handoff/SPECIALIST_QUESTIONS.txt';s=p.read_text().replace('Moulin1999\'s full original and the exact Young1985 antecedent remain priorities;\nread the latest source notes for any later resolved comparison.','''Moulin1999's full original remains a priority. Young1985's exact five-player
antecedent has now been checked in the original; Csoka-Pinter's fixed-owner
realization matches every coalition value. The Balog2017 author presentation
clarifies definitions but does not replace the unavailable final article.''');p.write_text(s)
p=b/'handoff/RECONCILIATION_NOTES.txt';p.write_text(p.read_text()+'''
13. Young1985's original has now been obtained and read. Its exact five-player
core conflict matches every coalition value of the later Csoka-Pinter example;
the latter supplies the explicit fixed-owner19-state report realization. Old
notes calling Young an unresolved attribution task are superseded by
sources/FINAL_YOUNG1985_GATE.txt. Young's term coalitional monotonicity is not
the coalition-total report condition TCWM. The precise quantitative priority
question is still open. Balog2017's author presentation was read, but its final
original remains unavailable; the presentation is not substituted for it.
''')
p=b/'handoff/build_handoff.py';s=p.read_text();s=s.replace('A direct five-owner withholding/core incompatibility example appears in Csóka–Pintér’s original risk-allocation work. We reproduced its decisive inequalities exactly.','Young’s 1985 original supplies the exact five-player core-selection conflict. Csóka–Pintér’s later risk-allocation work gives its explicit fixed-owner report realization. We matched all coalition values and reproduced the decisive inequalities exactly.')
s=s.replace("link('energy/SEMIVALUE_MIXTURE_PRIORITY_GATE.txt','Read the marginal-rule source comparison')","link('energy/SEMIVALUE_MIXTURE_PRIORITY_GATE.txt','Read the marginal-rule source comparison')+' · '+link('sources/FINAL_YOUNG1985_GATE.txt','Read the resolved Young attribution')+' · '+link('sources/FINAL_BALOG2017_GATE.txt','Read the Balog access and definition boundary')")
s=s.replace("link('handoff/REVIEW_ARCHIVES.json','All packet scopes and hashes')","link('handoff/REVIEW_ARCHIVES.json','All packet scopes and hashes')+' · '+link('handoff/SPECIALIST_QUESTIONS.txt','Proposed specialist questions')")
s=s.replace("link('unrestricted/RESEARCH_FRONTIER_RANKING.txt','Read the ranked next campaigns and stopping gates')","link('unrestricted/RESEARCH_FRONTIER_RANKING.txt','Read the ranked next campaigns and stopping gates')+' · '+link('handoff/NEXT_CAMPAIGN_GOAL.txt','Copy the proposed next goal; not started')")
p.write_text(s)
(b/'root/FINAL_SOURCE_RECONCILIATION.txt').write_text('''FINAL SOURCE RECONCILIATION\n17 October2026. Root inspected Young1985 original scanned pp68-69 directly.\nEquations4-5 concern allocation monotonicity under characteristic-function\nchanges, and Theorem1 gives the exact five-player efficient-core conflict.\nThe specialist source note and all31-coalition comparison were independently\nprovided by the unrestricted lane. The fixed-owner report realization is\ncredited to the later Csoka-Pinter original. No new quantitative result or\nnovelty confirmation follows from this source clarification.\n\nThe late Young note is included in main packetsA/B; the Balog author-presentation\naccess boundary is additionally included inB. Main proof/checker files are\nunchanged. Manifest changes add source-only dependencies and remove the now-\nresolved Young attribution gate. Packet runtime replays remain applicable to\nthe unchanged executable member bytes.\n''')
print('Reconciled Young original attribution and preserved Balog final-source limit')
