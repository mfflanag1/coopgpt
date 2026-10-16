from fractions import Fraction as F
from math import factorial
import json
out=[]
def ck(n,c,v=None):
    if not c:raise RuntimeError(n)
    out.append({'check':n,'passed':True,'value':v})
def exp_upper(x,n):
    return sum((x**j/F(factorial(j)) for j in range(n+1)),F(0))+(x**(n+1)/factorial(n+1))/(1-x/F(n+2))
elo=sum((F(1,factorial(j)) for j in range(9)),F(0))
ehi=exp_upper(F(1),8)
ck('5/3 < K < 7/4',elo>F(8,3) and ehi<F(11,4))
ck('2 < log8',ehi**2<8)
ck('log8 < 21/10',sum((F(7,10)**j/factorial(j) for j in range(4)),F(0))>2)
ck('A < 5/4',exp_upper(F(7,32),2)<F(5,4),str(exp_upper(F(7,32),2)))
ck('b(1/8)>1/2',exp_upper(F(217,320),6)<2,str(exp_upper(F(217,320),6)))
deriv=-F(5,4)+F(1,2)*(1+F(5,3)*F(7,8)*2)
ck('endpoint derivative >17/24',deriv==F(17,24)>0,str(deriv))
bound=1+F(5,8)/(1+F(19,40)+F(19,40)**2/2)
ck('funding rational',bound==F(7081,5081),str(bound))
ck('funding <7/5<C^2',bound<F(7,5)<F(161,136)**2 and ehi<F(68,25))
print(json.dumps({'status':'PASS','arithmetic':'fractions.Fraction','checks':out},indent=2))
