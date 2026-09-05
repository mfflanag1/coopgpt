"""Apply only the reviewed repairs and preserve their audit evidence."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery')
DEST=ROOT/'coopgames/portfolio_review_2026-09-05'
START='842dd6cdae6f135eacb217812d72f38b873c3d37'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    require(digest(source)==digest(target),'copy mismatch '+str(target))

require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==START,'HEAD changed')
require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip(),'worktree is no longer clean')
require(not DEST.exists(),'review destination already exists')
changes={relative:BASE/'text_fixes'/relative for relative in json.loads((BASE/'text_fixes/changed_files.json').read_text())}
for source in sorted((BASE/'assignment/wrapper_patch/proposals').glob('*.py')):
    changes['coopgames/verifiers/s6/'+source.name]=source
for name in ('verify_n7_exact_carrier_counterexample.py','verify_n7_exact_carrier_counterexample_leximin.py'):
    changes['coopgames/src/'+name]=BASE/'asymptotic/guarded_carrier'/name
changes.update({
    'coopgames/paper3/wrapper.pdf':BASE/'builds/paper3/wrapper.pdf',
    'coopgames/paper4/threshold.pdf':BASE/'builds/paper4/threshold.pdf',
    'coopgames/paper5/assignment_comparison/output/pdf/pairs_and_triples.pdf':BASE/'builds/comparison/pairs_and_triples.pdf',
})
before={relative:digest(ROOT/relative) for relative in changes}
before['coopgames/paper5/assignment_comparison/SHA256SUMS']=digest(ROOT/'coopgames/paper5/assignment_comparison/SHA256SUMS')
# Existing isolated theorem packages and all six-player proof objects remain byte-identical.
protected={}
for relative in ('coopgames/paper5/asymptotic_constant_two','coopgames/paper5/assignment_separation','coopgames/paper5/three_sided_separation','coopgames/verifiers/s6/certificates','coopgames/verifiers/s6/orbit_core_certificates'):
    for path in sorted((ROOT/relative).rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            protected[str(path.relative_to(ROOT))]=digest(path)
for relative,source in changes.items(): copy(source,ROOT/relative)
copy(BASE/'COOPGAMES_README.md',ROOT/'coopgames/README.md')
copy(BASE/'PAPER5_README.md',ROOT/'coopgames/paper5/README.md')
report=(BASE/'REVIEW.md').read_text()
links={
    '(EARLY_PAPERS_REVIEW.md)':'(early/EARLY_PAPER_REVIEW_2026-09-05.md)',
    '(UNRESTRICTED_ASYMPTOTIC_AUDIT.md)':'(asymptotic/UNRESTRICTED_ASYMPTOTIC_AUDIT.md)',
    '(CARRIER_AUDIT.md)':'(asymptotic/CARRIER_AUDIT.md)',
    '(ASSIGNMENT_CORRECTNESS_REVIEW.md)':'(assignment/ASSIGNMENT_CORRECTNESS_REVIEW.md)',
    '(WRAPPER_REPAIR_REVIEW.md)':'(wrapper/WRAPPER_REVIEW.md)',
}
for old,new in links.items(): report=report.replace(old,new)
DEST.mkdir(parents=True)
(DEST/'REVIEW.md').write_text(report)
for name in ('history_index.json','legacy_assert_inventory.json','fresh_s6_proofs.py','fresh_s6_proofs.json','fresh_s6_semantic_interface.json','release_preflight_tests.json','prepare_text_fixes.py','prepare_final_repairs.py'):
    copy(BASE/name,DEST/name)
for lane in ('early','asymptotic','assignment'):
    for source in sorted((BASE/lane).iterdir()):
        if source.is_file() and source.suffix in ('.md','.py','.json','.log'):
            copy(source,DEST/lane/source.name)
for source in sorted((BASE/'asymptotic/guarded_carrier').iterdir()):
    if source.is_file(): copy(source,DEST/'asymptotic/guarded_carrier'/source.name)
for source in sorted((BASE/'assignment/wrapper_patch').iterdir()):
    if source.is_file() and source.suffix in ('.md','.py','.json','.log','.patch'):
        copy(source,DEST/'wrapper'/source.name)
for source in sorted((BASE/'assignment/wrapper_patch/proposals').glob('*.py')):
    copy(source,DEST/'wrapper/proposals'/source.name)
for source in sorted((BASE/'assignment/wrapper_patch/worktree').glob('old_verify_*.py')):
    copy(source,DEST/'wrapper/originals'/source.name)
copy(BASE/'builds/pdf_changes.json',DEST/'builds/pdf_changes.json')
for name in ('paper3','paper4','comparison'):
    for source in sorted((BASE/'builds'/name).iterdir()):
        if source.is_file() and (source.suffix=='.log' or source.name.endswith('.png')):
            copy(source,DEST/'builds'/name/source.name)
copy(BASE/'integrate_review.py',DEST/'integrate_review.py')
# The comparison manifest tracks current source and PDF bytes, using its existing scope.
package=ROOT/'coopgames/paper5/assignment_comparison'
manifest=package/'SHA256SUMS'
entries=[]
for line in manifest.read_text().splitlines():
    _,relative=line.split('  ',1)
    entries.append(f'{digest(package/relative)}  {relative}')
manifest.write_text('\n'.join(entries)+'\n')
require(all(digest(ROOT/p)==h for p,h in protected.items()),'protected artifact changed')
after={p:digest(ROOT/p) for p in before}
evidence={str(p.relative_to(DEST)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(DEST.rglob('*')) if p.is_file()}
tools_root=ROOT.parent/'experimental-runs/additive-efx-counting-runs/parkability/certification-20260801-v2/tools'
tool_hashes={}
for rel in ('cvc5-1.3.3/cvc5-macOS-arm64-static/bin/cvc5','ethos-0.2.3/ethos','cvc5-1.3.3-source/proofs/eo/cpc/Cpc.eo','cvc5-1.3.3-source/proofs/eo/cpc/expert/CpcExpert.eo'):
    tool_hashes[str(tools_root/rel)]=digest(tools_root/rel)
record={'review_date':'2026-09-05','starting_commit':START,'python_packaging':sys.version,
        'changes':{p:{'before_sha256':before[p],'after_sha256':after[p]} for p in before},
        'protected_artifact_count':len(protected),'protected_artifacts_unchanged':True,
        'protected_hashes':protected,'fresh_proof_tool_hashes':tool_hashes,'evidence':evidence,
        'full_legacy_release_rerun':False,'fresh_s6_proofs':30,'scope':'See REVIEW.md; no blanket certification of the historical archive.'}
(DEST/'integration_manifest.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'modified_existing_files':len(before),'evidence_files':len(evidence),'protected_unchanged':len(protected),'report':str(DEST/'REVIEW.md')},indent=2))
