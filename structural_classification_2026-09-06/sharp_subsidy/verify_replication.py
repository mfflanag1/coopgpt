"""Exact replication and rational-packing lift calibration."""
from fractions import Fraction as F
from itertools import product
import json
from tree_certificate import market, rooted_colors, check_cover, require


def run():
    checks=0;cases=0
    for q in range(1,4):
        m,pairs,P=market(q)
        for copies in [2,3]:
            size=m*copies
            clone=[[[M[i//copies][j//copies]for j in range(size)]for i in range(size)]for M in pairs]
            for k,r in product(range(3),range(m)):
                colors=rooted_colors(m,P,r,k)
                x=[int(j==k)+2*int(colors[v]==j)for j in range(3)for v in range(m)]
                lift=[x[j*m+v//copies]for j in range(3)for v in range(size)]
                require(sum(lift)==copies*3*m,'replica core budget')
                check_cover(lift,clone,size);checks+=size**3
            y=[1]*(3*m)
            for a,b,c in P:y[a]+=2
            lift=[y[j*m+v//copies]for j in range(3)for v in range(size)]
            check_cover(lift,clone,size);checks+=size**3
            require(sum(lift)-copies*3*m==copies*2*q,'subsidy scaling')
            # Rational three-edge odd-cycle packing, with common denominator 2.
            packing=[((0,0,0),F(1,2)),((0,1,1),F(1,2)),((1,0,1),F(1,2))]
            den=2;used=[0]*(3*m);lifted=[]
            for t,weight in packing:
                for _ in range(int(den*weight)):
                    edge=[]
                    for k,v in enumerate(t):
                        index=k*m+v;edge.append(den*v+used[index]);used[index]+=1
                    lifted.append(tuple(edge))
            require(max(used)<=den,'packing capacity')
            require(len({k*den*m+t[k]for t in lifted for k in range(3)})==3*len(lifted),'lift is not a partial matching')
            w=lambda t:pairs[0][t[0]][t[1]]+pairs[1][t[0]][t[2]]+pairs[2][t[1]][t[2]]
            orig=sum(weight*w(t)for t,weight in packing)
            lifted_w=sum(w(tuple(v//den for v in t))for t in lifted)
            require(lifted_w==den*orig,'packing weight not preserved')
            residual=sum(1-F(u,den)for u in used)
            require(3*den*m-3*len(lifted)==den*residual,'unmatched claims not preserved')
            cases+=1
    print(json.dumps({'status':'PASS','replication_cases':cases,'integer_team_checks':checks,'rational_packing_lifts':cases}))


if __name__=='__main__':run()
