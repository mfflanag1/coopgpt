from fractions import Fraction as F
from collections import defaultdict
import json

def certificate(k,s,M):
    a={m:min(s-1,k*(m-1)) for m in range(2,M+1)}
    P=F(1)
    for m in a:P*=F(a[m],a[m]+1)
    coefficients=defaultdict(F);rhs=F(0); rows=0
    def add(row,value,weight):
        nonlocal rhs,rows
        assert weight>=0;rows+=1
        for name,c in row.items():coefficients[name]+=weight*c
        rhs+=weight*value
    add({'K':1,'z':-1,f'q{M}':-k*M},0,F(1))
    add({'z':1,f'q{M}':k},1,F(1))
    residual=F(k*(M-1))
    for m in range(M,1,-1):
        w=residual/(a[m]+1)
        add({f'q{m}':a[m]+1,f'q{m-1}':-a[m]},0,w)
        residual=w*a[m]
    add({'q1':k+1},1,residual/(k+1))
    assert {key:value for key,value in coefficients.items() if value}=={'K':F(1)}
    bound=1+F(k*(M-1),k+1)*P
    assert rhs==bound
    return bound,P,rows

def main():
    tested=peaks=rows=0
    for k in range(2,17):
        for s in range(2,65):
            h=(s+k-1)//k; Q=F(1)
            for j in range(2,h+1):Q*=F(k*j,k*(j-1)+1)
            alpha=F(s-1,s)
            values=[]
            for M in range(1,2*s+3):
                B,P,count=certificate(k,s,M);rows+=count;tested+=1;values.append(B)
                if M>=h:assert P==Q/h*alpha**(M-h)
            top=max(values);positions=[j+1 for j,x in enumerate(values) if x==top]
            assert positions==[s,s+1],(k,s,positions)
            assert top==1+F(k*(s-1),(k+1)*h)*Q*alpha**(s-h)
            peaks+=1
    assert certificate(2,6,6)[0]==F(493,243)
    print(json.dumps({'status':'PASS','arithmetic':'Fraction','certificates':tested,'derived_rows':rows,'exact_peak_checks':peaks,'k_range':[2,16],'s_range':[2,64],'scope':'Exact scalar tail cancellation and closed-form maxima; geometry and asymptotic gamma formula checked separately in proof.'},indent=2))
if __name__=='__main__':main()
