"""Run the bounded release checks with the current Python interpreter."""
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parent
for script in ['verify_published_empty_core.py','calibrate_three.py','verify_gadgets.py','verify_family_independent.py','verify_coordinate_amplification.py']:
    print('RUN',script,flush=True)
    subprocess.run([sys.executable,str(root/script)],cwd=root,check=True)
print('PASS complete three-sided release checks',flush=True)
