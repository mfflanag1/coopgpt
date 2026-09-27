"""Deterministic restriction to the seven matching teams in the proof budget."""
from pathlib import Path
from fractions import Fraction as F
import json

ROOT=Path(__file__).resolve().parent

def main():
    old=json.loads((ROOT/'candidate.json').read_text());keep=[0,3,4,6,9,13,15]
    oldmatching=[old['matching'][idx] for idx in keep]
    sectors=[sorted(t[s] for t in oldmatching) for s in range(3)]
    maps=[{j:i for i,j in enumerate(group)} for group in sectors]
    pairs=((0,1),(0,2),(1,2))
    M=[[[str(F(old['matrices'][p][i][j])/3) for j in sectors[t]] for i in sectors[s]] for p,(s,t) in enumerate(pairs)]
    matching=[[maps[s][j] for s,j in enumerate(team)] for team in oldmatching]
    tripleterms=[[maps[s][j] for s,j in enumerate(t)] for t in ((0,3,8),(0,11,2),(0,13,2),(3,8,5),(4,5,13),(12,17,9))]
    result=dict(matrices=M,matching=matching,target=maps[0][6],floor_witness=[str(F(old['x'][21*s+j])/3) for s in range(3) for j in sectors[s]],ideal_witness=[str(F(old['y'][21*s+j])/3) for s in range(3) for j in sectors[s]],T='15',first_floor='1/3',target_ideal='3',ratio='1/9',budget_matching_multipliers=[3,1,1,1,1,1,1],budget_triples=tripleterms,budget_rhs='3',embedding=dict(original_sector_indices=sectors,original_matching_indices=keep,scale='1/3'))
    (ROOT/'reduced_candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Saved deterministic21-player restriction, T15, ratio1/9')

if __name__=='__main__':main()
