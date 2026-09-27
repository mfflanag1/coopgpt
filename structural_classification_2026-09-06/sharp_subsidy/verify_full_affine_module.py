"""All-team affine-module dual verification without compressed core rows."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from collections import defaultdict
import json


def require(ok,msg):
    if not ok:raise ValueError(msg)


def check(d):
    P=(1,2,0);U=[0,2,3,4,7,8]
    def pairs(t):
        a,b,c=t;return ((0,a,b),(1,a,c),(2,b,c))
    edges=sorted({e for t in [(j,j,j) for j in range(3)]+[P] for e in pairs(t)})
    require(d['m']==3 and tuple(d['P'])==P and d['U']==U,'module scope')
    require([tuple(e) for e in d['edges']]==edges,'pair inventory')
    idx={e:k for k,e in enumerate(edges)};off=len(edges);res=[F(0)]*(off+6*9)
    y=list(map(F,d['y']));z=list(map(F,d['z']));coef=F(d['affine_coefficient'])
    require(len(y)==162 and len(z)==7 and min(y)>=0,'dual dimensions and signs')
    for j in range(3):
        for p in range(3):res[idx[p,j,j]]+=z[0]
    for k,i in enumerate(U):
        for v in range(9):res[off+k*9+v]+=z[k+1]
        for r,t in enumerate(product(range(3),repeat=3)):
            mass=y[k*27+r]
            for e in pairs(t):
                if e in idx:res[idx[e]]+=mass
            for s,j in enumerate(t):res[off+k*9+s*3+j]-=mass
    for e in pairs(P):res[idx[e]]-=1
    for k,i in enumerate(U):res[off+k*9+i]-=F(1,3)
    for p in range(3):res[idx[p,0,0]]+=coef
    coverage=defaultdict(F)
    for k,i in enumerate(U):
        loads=[F(0)]*9
        for r,t in enumerate(product(range(3),repeat=3)):
            mass=y[k*27+r]
            for sec,j in enumerate(t):loads[sec*3+j]+=mass
            for edge in pairs(t):coverage[edge]+=mass
        require(loads[i]==0 and max(loads)<=F(1,3),'explicit deletion row')
    target=defaultdict(F)
    for edge in pairs(P):target[edge]+=1
    for j in (1,2):
        for p in range(3):target[p,j,j]+=F(17,18)
    require(all(coverage[e]>=v for e,v in target.items()),'explicit aggregate pair coverage')
    require(min(res)>=0,'exact coefficient domination')
    require(sum(z)==F(19,18),'exact dual objective')
    return {'status':'PASS','affine_bound':'J <= T/18 + (17/18)d_0','full_core_rows':162,'variables':len(res),'arithmetic':'rational; no residual correction'}


def main():
    d=json.loads(Path(__file__).with_name('FULL_AFFINE_MODULE.json').read_text())
    require(F(d['affine_coefficient'])==F(17,18),'affine coefficient')
    result=check(d)
    for bad in (dict(d,y=['0']*162),dict(d,affine_coefficient='0')):
        try:check(bad)
        except ValueError:pass
        else:raise ValueError('damaged dual accepted')
    result['negative_controls']=2
    print(json.dumps(result))

if __name__=='__main__':main()
