"""Discovery-only fixed-obstruction market synthesis for multiple junctions."""
import argparse,json,numpy as np
from pathlib import Path
from fractional_synthesis import Synthesis


def configuration(b):
 P=[];used=set();nextlabel=b
 for j in range(b-1):
  P.append((j,j+1,nextlabel));used.update([(0,j),(1,j+1)]);nextlabel+=1
 for j in range(b):
  for s in range(3):
   if (s,j)in used:continue
   t=[None]*3;t[s]=j
   for k in range(3):
    if k!=s:t[k]=nextlabel;nextlabel+=1
   P.append(tuple(t))
 if nextlabel!=4*b+3 or len(P)!=2*b+1:raise ValueError('construction counts')
 return nextlabel,P


if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--junctions',type=int,default=3);args=ap.parse_args();b=args.junctions
 m,P=configuration(b);s=Synthesis(m);lam=np.zeros(len(s.teams))
 for t in P:lam[s.teams.index(t)]=1
 value,pairs,witnesses=s.synth(lam)
 d={'junctions':b,'m':m,'P':P,'floating_obstruction':value,'matrices':pairs.reshape(3,m,m).tolist(),'witnesses':witnesses.tolist(),'status':'floating discovery only'}
 Path(__file__).with_name(f'JUNCTION_{b}_PROBE.json').write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps({k:v for k,v in d.items()if k not in ['matrices','witnesses']}),flush=True)
