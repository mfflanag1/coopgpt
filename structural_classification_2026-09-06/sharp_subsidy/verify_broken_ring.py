"""Full integer verification, independent of the coloring construction."""
from pathlib import Path
from itertools import product
import json
from fractions import Fraction as F

def require(ok,msg):
 if not ok:raise ValueError(msg)

def verify(d):
 b=d['b'];m=d['m'];P=[tuple(e)for e in d['P']];require(b>=2 and m==4*b,'parameters');require(P==[(j,(j+1)%b,b+j)for j in range(b)]+[(2*b+2*j,2*b+2*j+1,j)for j in range(b)],'support')
 used=[s*m+j for e in P for s,j in enumerate(e)];require(len(used)==len(set(used)),'matching overlap');pairs=d['pairs'];expected=[[[int(a==c)for c in range(m)]for a in range(m)]for _ in range(3)]
 for a,c,z in P:expected[0][a][c]=2;expected[1][a][z]=1;expected[2][c][z]=2
 expected[0][0][1]=0;require(pairs==expected,'pair coefficients')
 require(d['T']==3*m and d['H']==[3]*(3*m),'worth and ideals');require(len(d['core_witnesses'])==3*m,'all ideal witnesses')
 triples=[(a,m+c,2*m+z,pairs[0][a][c]+pairs[1][a][z]+pairs[2][c][z])for a,c,z in product(range(m),repeat=3)]
 for i,x in enumerate(d['core_witnesses']):
  require(len(x)==3*m and all(type(v)is int and v>=0 for v in x),'payoff format');require(sum(x)==3*m and x[i]==3,'core ideal endpoint')
  for a,c,z,v in triples:require(x[a]+x[c]+x[z]>=v,'core coalition coverage')
 y=d['protected_y'];require(len(y)==3*m and all(type(v)is int and v>=1 for v in y),'protected floors')
 for a,c,z,v in triples:require(y[a]+y[c]+y[z]>=v,'protected coverage')
 wp=sum(pairs[0][a][c]+pairs[1][a][z]+pairs[2][c][z]for a,c,z in P);lower=wp+(3*m-len(used))-3*m
 require(wp==10*b-2 and lower==4*b-2==d['subsidy'],'packing subsidy lower');require(sum(y)==3*m+lower,'subsidy upper')
 return {'b':b,'m':m,'T':3*m,'exact_subsidy':lower,'ratio':str(F(lower,3*m)),'triple_checks':len(triples)*(3*m+1)}

def run():
 ds=json.loads(Path(__file__).with_name('BROKEN_RING_CERTIFICATES.json').read_text());require([d['b']for d in ds]==[2,3,4,6,8],'inventory');out=[verify(d)for d in ds]
 bad=dict(ds[0]);bad['core_witnesses']=[x[:]for x in ds[0]['core_witnesses']];bad['core_witnesses'][0][0]-=1
 try:verify(bad)
 except ValueError:pass
 else:raise ValueError('damaged ideal witness accepted')
 print(json.dumps({'status':'PASS','cases':out,'negative_controls':1,'all_size_claim':'s=4b-2 and T=12b for b>=2; conventional proof separate'}))
if __name__=='__main__':run()
