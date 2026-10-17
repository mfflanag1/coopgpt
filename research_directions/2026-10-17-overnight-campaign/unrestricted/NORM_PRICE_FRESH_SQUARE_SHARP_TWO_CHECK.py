from fractions import Fraction as Q
from itertools import product

def add(A,B):return tuple(x+y for x,y in zip(A,B))
def sub(A,B):return tuple(x-y for x,y in zip(A,B))
def dot(A,B):return sum(x*y for x,y in zip(A,B))
def cone(C):return C[0]>=max(abs(C[1]),abs(C[2]))
def val(C):return C[0]-max(abs(C[1]),abs(C[2]))
def price(C):
 t,x,y=map(Q,C)
 if t==0:return (Q(1),Q(0),Q(0))
 if abs(x)==t:return (Q(1),Q(-1 if x>0 else 1),Q(0))
 if abs(y)==t:return (Q(1),Q(0),Q(-1 if y>0 else 1))
 swap=abs(y)>abs(x)
 if swap:x,y=y,x
 sx=1 if x>=0 else -1;sy=1 if y>=0 else -1
 x,y=abs(x),abs(y);H=t*t-y*y
 b=(t*x-y*y)/H;c=(t-x)*y/H
 px,py=-sx*b,-sy*c
 return (Q(1),py,px) if swap else (Q(1),px,py)
def grad(t,x,y,v,w):
 H=t*t-y*y;a=(t-x)/H;at=(2*t*x-t*t-y*y)/H**2;Z=t*v-y*w
 return (1+a*v+Z*at,-1+a*t-Z/H,-a*(y+w)+2*y*a*Z/H)
def vertices(t,x,y):
 out=set()
 for u in [Q(0),(t-x)/2,(t-y)/2,(t+y)/2,(t+x)/2,t]:
  lo_v=max(-u,x-t+u);hi_v=min(u,x+t-u)
  lo_w=max(-u,y-t+u);hi_w=min(u,y+t-u)
  for v,w in product([lo_v,hi_v],[lo_w,hi_w]):out.add((u,v,w))
 return out

def main():
 derivative=0;endpoints=0
 for xn in range(20):
  for yn in range(xn+1):
   t=Q(1);x=Q(xn,20);y=Q(yn,20);H=t*t-y*y;a=(t-x)/H;h=(t-x)/2
   C=(t,x,y);P=price(C)
   assert 0<=-P[1]-P[2]<=1
   assert dot(C,P)==val(C)*(1+(t*x-y*y)/H)<=2*val(C)
   if x==y:assert P[1]==P[2]
   if y==0:assert P[2]==0
   for u,v,w in vertices(t,x,y):
    A=(u,v,w);assert cone(A) and cone(sub(C,A))
    g=grad(t,x,y,v,w)
    assert g[0]>=abs(g[1])+abs(g[2])
    for tau in [-1,1]:
     fact=a*(t-tau*y)/(t+tau*y)*(t-v+tau*(y-w))
     assert g[0]+g[1]+tau*g[2]==fact>=0
    derivative+=1
   gm=grad(t,x,y,-h,-h);gp=grad(t,x,y,-h,h)
   assert gp[0]-gp[1]+gp[2]==2*(x-y)/(t-y)
   assert gm[0]-gm[1]-gm[2]==2*(x+y)/(t+y)
   assert gp[0]-gp[1]-gp[2]==2-(t-x)/(t+y)-(t-x)*(x-y)/(t-y)**2>=Q(3,4)
   endpoints+=3
 reports=[tuple(map(Q,(t,x,y))) for t in range(3) for x in range(-t,t+1) for y in range(-t,t+1)]
 additions=[tuple(map(Q,(t,x,y))) for t in range(2) for x in range(-t,t+1) for y in range(-t,t+1)]
 comparisons=0;coverage=0
 for A,B in product(reports,repeat=2):
  C=add(A,B);P=price(C);old=dot(P,A)
  assert old>=val(A)>=0
  assert dot(P,B)>=val(B)>=0
  assert val(C)<=dot(P,C)<=2*val(C)
  coverage+=1
  for D in additions:
   highA=add(A,D);highC=add(C,D)
   assert dot(price(highC),highA)>=old
   comparisons+=1
 A=(Q(1),Q(-1),Q(-1));B=(Q(2),Q(2),Q(2));D=(Q(1),Q(0),Q(0));C=add(A,B)
 assert dot(price(C),A)==Q(3,2)
 assert dot(price(add(C,D)),add(A,D))==Q(12,5)
 assert Q(12,5)-Q(3,2)==Q(9,10)<val(D)
 print(f'PASS: {derivative} exact order-interval derivative vertices; {endpoints} exact ray-endpoint identities; {coverage} coverage/budget profiles; {comparisons} finite coalition-restoration comparisons including boundaries; exact full-OUT failure.')

if __name__=='__main__':main()
