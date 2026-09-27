"""Minimize the first verified witness and add the published control."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import json
from pilot import ROOT, exact_check, float_check, require

def main():
    summary=json.loads((ROOT/'pilot_summary.json').read_text())
    first=next(r for r in summary['exact_records'] if r.get('violates_one_third'))
    published=float_check([[4,4],[5,0]],[[2,0],[1,5]],[[4,3],[0,9]],'Atay_Nunez_2019_Example5_strict_control')
    published_exact=exact_check(published)
    require(published_exact['T']=='24','published strict total mismatch')
    (ROOT/'published_control.json').write_text(json.dumps(published_exact,indent=2)+'\n')
    print('PUBLISHED',published_exact['min_coordinate_fraction'],published_exact['rho'],flush=True)
    matrices=[first[k] for k in ('A','B','C')]
    attempts=0;accepted=[]
    for passno in range(4):
        changed=False
        for s in range(3):
            for i in range(3):
                for j in range(3):
                    old=matrices[s][i][j]
                    for value in range(old):
                        trial=deepcopy(matrices);trial[s][i][j]=value
                        rec=float_check(*trial,label=f'reduction_{attempts}')
                        attempts+=1
                        if rec['status']=='nonempty_core_float' and rec['min_fraction']<1/3-1e-7:
                            matrices=trial;changed=True
                            accepted.append(dict(passno=passno,matrix=s,row=i,column=j,before=old,after=value,fraction=rec['min_fraction']))
                            print('REDUCE',s,i,j,old,value,rec['min_fraction'],flush=True)
                            break
        if not changed:
            break
    minimized=float_check(*matrices,label='greedy_reduced_m3_counterexample')
    exact=exact_check(minimized)
    require(exact['violates_one_third'],'reduced witness must violate exactly')
    exact.update(reduction=dict(attempts=attempts,accepted=accepted,objective='greedy total matrix-entry mass; not globally minimal',initial_mass=sum(sum(row) for M in [first[k] for k in ('A','B','C')] for row in M),final_mass=sum(sum(row) for M in matrices for row in M)))
    (ROOT/'reduced_counterexample.json').write_text(json.dumps(exact,indent=2)+'\n')
    print('REDUCED',exact['min_coordinate_fraction'],exact['rho'],'mass',exact['reduction']['final_mass'],flush=True)

if __name__=='__main__':main()
