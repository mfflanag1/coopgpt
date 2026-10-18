"""Independent vertex enumeration for the actual four-owner arity3 obstruction."""
from fractions import Fraction as F
from itertools import combinations
import json

A=[[1,1,0,0],[1,0,1,0],[1,0,0,1],[0,1,1,0],[0,1,0,1],[0,0,1,1]]
bundles=[[1,1,1,0,0,0],[0,0,0,2,0,0],[0,0,0,0,2,0],[0,0,0,0,0,2]]

def solve(rows,rhs):
    z=[[F(x) for x in row]+[F(b)] for row,b in zip(rows,rhs)]
    for col in range(4):
        pivot=next((j for j in range(col,4) if z[j][col]),None)
        if pivot is None:return None
        z[col],z[pivot]=z[pivot],z[col]
        q=z[col][col];z[col]=[x/q for x in z[col]]
        for j in range(4):
            if j!=col:
                q=z[j][col];z[j]=[a-q*b for a,b in zip(z[j],z[col])]
    return [z[j][-1] for j in range(4)]

def main():
    v=[];systems=0
    for mask in range(16):
        cap=[sum(bundles[i][j] for i in range(4) if mask>>i&1) for j in range(6)]
        rows=A+[[-int(i==j) for j in range(4)] for i in range(4)]
        rhs=cap+[0]*4;best=F(0)
        for active in combinations(range(10),4):
            systems+=1;x=solve([rows[j] for j in active],[rhs[j] for j in active])
            if x is not None and all(sum(a*z for a,z in zip(row,x))<=b for row,b in zip(rows,rhs)):
                best=max(best,sum(x,F(0))/3)
        expected=F(0) if not(mask&1) else (F(1) if mask==15 else F(1,3))
        assert best==expected,(mask,best,expected);v.append(best)
    p=F(1,2)
    margins=[sum(p**S.bit_count()*(1-p)**(3-S.bit_count())*(v[S|1<<i]-v[S]) for S in range(16) if not(S>>i&1)) for i in range(4)]
    assert margins==[F(5,12),F(1,12),F(1,12),F(1,12)]
    assert sum(margins)==F(2,3)<3*p*p*v[15]
    print(json.dumps({'status':'PASS','arithmetic':'Fraction','coalition_values':list(map(str,v)),'vertex_systems':systems,'marginals_p_half':list(map(str,margins)),'actual_total':'2/3','rejected_threshold':'3/4','technology':'four arity3 columns; all profits1/3; multiplying profits by3 gives unit profits with identical normalized violation'},indent=2))

if __name__=='__main__':main()
