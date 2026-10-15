from fractions import Fraction as Q
from flow_oracle import value
import json

def check(k):
    d=4*k;T=2*k-1
    P=[1]*d;P[0]=P[-1]=0
    U=[2 if j%4==3 else P[j] for j in range(d)]
    V=[2 if j%4==0 else P[j] for j in range(d)]
    profiles=[P,U,V];edges=[(j,j+1,1) for j in range(d-1)]
    pays=[(Q(k-1,2),Q(k,2),Q(k,2),Q(k-1,2)),(Q(3*(k-1),4),Q(k-1,4),Q(3*k+1,4),Q(k-1,2)),(Q(k-1,2),Q(3*k+1,4),Q(k-1,4),Q(3*(k-1),4))]
    factor=1+Q(k-1,4*T)
    def require(t,msg):
        if not t:raise RuntimeError((k,msg))
    def worth(t,mask):return value([profiles[t][j] if mask>>(j%4)&1 else 0 for j in range(d)],edges)
    for t in range(3):
        require(worth(t,15)==T,'grand')
        require(sum(pays[t])<=factor*T,'budget')
        for mask in range(1,16):require(sum(pays[t][i] for i in range(4) if mask>>i&1)>=worth(t,mask),'coverage')
    require(pays[0][3]<=pays[1][3] and pays[0][0]<=pays[2][0],'incentives')
    require(worth(0,9)==k-1,'baseline AD')
    for t,claims in [(1,{3:k-1,6:k,13:T}),(2,{6:k,11:T,12:k-1})]:
        for mask,v in claims.items():require(worth(t,mask)==v,'lower witness')
    require(4*T*(factor-1)==k-1,'ratio')
    return {'k':k,'resources':d,'exact_three_profile_optimum':str(factor)}
if __name__=='__main__':
    print(json.dumps({'status':'PASS','oracle':'independent exact max-profit flow','checks':[check(k) for k in [2,3,4,5,8,12,20]],'scope':'samples verify the stated general proof, not a substitute for it'},indent=2))
