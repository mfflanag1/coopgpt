from pathlib import Path
import json
import os
import subprocess

base = Path(__file__).resolve().parent
root = Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery')
relative = 'coopgames/paper4/threshold.tex'
old = r'''Finally, for $T=S\cup\{j\}$ and $x$ with $x(T)=v(T)$,
$x(S)=v(S\cup\{j\})-x_j\le v(S\cup\{j\})$, so
$\beta_{S\cup\{j\}}\le v(S\cup\{j\})-v(S)$, whence
$\alpha_{\mathrm{ex}}(S)\le g(S)$.'''
new = r'''If $|N\setminus S|\ge2$, take $T=S\cup\{j\}$ proper. For $x(T)=v(T)$,
$x(S)=v(T)-x_j\le v(T)$, so $\beta_T\le v(T)-v(S)$; minimizing over
$j\notin S$ gives $\alpha_{\mathrm{ex}}(S)\le g(S)$.
If $N\setminus S=\{j\}$, every core point satisfies $x(S)=v(N)-x_j\le v(N)$,
so every $\beta_T\le v(N)-v(S)=g(S)$, giving the same bound.'''
source = (root / relative).read_text()
if source.count(old) != 1: raise RuntimeError('paper4 patch target changed')
patched = source.replace(old,new)
target = base/'text_fixes'/relative
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(patched)
build = base/'builds/paper4'
build.mkdir(parents=True,exist_ok=True)
(build/'threshold.tex').write_text(patched)
changes=json.loads((base/'text_fixes/changed_files.json').read_text())
if relative not in changes: changes.append(relative)
(base/'text_fixes/changed_files.json').write_text(json.dumps(changes,indent=2)+'\n')

relative='coopgames/paper5/verify_release.sh'
source=(root/relative).read_text()
anchor='python_bin="${1:-python3}"\n'
guard='''# Legacy release stages use assertions as proof gates.
"$python_bin" -c 'import sys; sys.exit("This release requires assertions enabled; unset PYTHONOPTIMIZE and use Python without -O or -OO.") if sys.flags.optimize else None'
'''
if source.count(anchor)!=1: raise RuntimeError('release patch target changed')
target=base/'text_fixes'/relative
target.write_text(source.replace(anchor,anchor+guard))
if relative not in changes: changes.append(relative)
(base/'text_fixes/changed_files.json').write_text(json.dumps(changes,indent=2)+'\n')
python='/private/tmp/coopgt-research-20260904/.venv/bin/python'
tests=[]
for optimization in ('1','2'):
    env=dict(os.environ,PYTHONOPTIMIZE=optimization)
    result=subprocess.run(['bash',str(target),python],capture_output=True,text=True,env=env)
    if result.returncode==0 or result.stdout or 'requires assertions enabled' not in result.stderr:
        raise RuntimeError('release guard failed')
    tests.append({'mode':'PYTHONOPTIMIZE='+optimization,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
# Exercise exactly the new preflight in ordinary mode, without starting the full release.
env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
result=subprocess.run(['bash','-c',anchor+guard,'bash',python],capture_output=True,text=True,env=env)
if result.returncode or result.stdout or result.stderr:raise RuntimeError('ordinary preflight failed')
tests.append({'mode':'ordinary preflight only','exit_code':0})
subprocess.run(['bash','-n',str(target)],check=True)
(base/'release_preflight_tests.json').write_text(json.dumps(tests,indent=2)+'\n')
print('Prepared paper4 repair and release guard; preflight controls PASS.')
