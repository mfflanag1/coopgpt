import itertools, math, json, random
# Coordinates A,B,C,D; graph B-A-D-C.
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def scale(a,t):return tuple(x*t for x in a)
def dot(a,c):return sum(x*y for x,y in zip(a,c))
def choose(forms,c,which=min):
    vals=[dot(f,c) for f in forms]; j=vals.index(which(vals));return forms[j], min((abs(v-vals[j]) for k,v in enumerate(vals) if k!=j),default=1)
def calc(c,alpha,beta):
    A,B,C,D=c;e=[tuple(int(i==j) for j in range(4)) for i in range(4)]
    va,gap1=choose([add(e[0],e[2]),scale(add(e[1],e[3]),alpha),add(e[0],scale(e[3],alpha))],c)
    vd,gap2=choose([add(e[1],e[3]),scale(add(e[0],e[2]),alpha),add(e[3],scale(e[0],alpha))],c)
    # lower=max(0,V-A), upper=min(C,alphaD); clip betaC
    lo,gap3=choose([(0,0,0,0),add(va,scale(e[0],-1))],c,max)
    hi,gap4=choose([e[2],scale(e[3],alpha)],c)
    wc0,gap5=choose([scale(e[2],beta),lo],c,max)
    wc,gap6=choose([wc0,hi],c)
    lob,gap7=choose([(0,0,0,0),add(vd,scale(e[3],-1))],c,max)
    hib,gap8=choose([e[1],scale(e[0],alpha)],c)
    wb0,gap9=choose([scale(e[1],beta),lob],c,max)
    wb,gap10=choose([wb0,hib],c)
    W=[add(va,scale(wc,-1)),wb,wc,add(vd,scale(wb,-1))]
    w=[dot(f,c) for f in W];p=[x/y for x,y in zip(w,c)]
    # exact derivatives of p=w/c on the smooth selected cell
    J=[[W[j][v]/c[j]-(p[j]/c[j] if j==v else 0) for v in range(4)] for j in range(4)]
    singles=[p[v]+sum(c[j]*min(J[j][v],0) for j in range(4)) for v in range(4)]
    edges=[p[u]+p[v]+sum(c[j]*min(J[j][u]+J[j][v],0) for j in range(4)) for u,v in [(0,1),(0,3),(2,3)]]
    return min(singles),min(edges),p,W,edges
if __name__=='__main__':
    rng=random.Random(4421);out=[]
    for alpha,beta in [(1/math.sqrt(2),.5),(.75,.5),(.8,.5),(.9,.5),(1.,.5)]:
      worst=(10,None)
      for z in range(100000):
        c=[math.exp(rng.uniform(-7,7)) for _ in range(4)]
        s,e,p,W,es=calc(c,alpha,beta)
        if e<worst[0]:worst=(e,(c,p,W,es,s))
        if s<-1e-7 or e<1-1e-7:break
      out.append({'alpha':alpha,'beta':beta,'count':z+1,'worst':worst})
    print(json.dumps(out,indent=2))
