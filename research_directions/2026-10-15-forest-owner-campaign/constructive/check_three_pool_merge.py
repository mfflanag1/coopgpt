import math,random,json
r=random.Random(773)
def pay(rows):
    totals=[sum(row[j] for row in rows) for j in range(3)]
    T=min(totals)
    if T==0:return [0.]*len(rows)
    ds=[[min(x,T) for x in row] for row in rows]
    rho=[sum(row[j] for row in ds)/T for j in range(3)]
    weights=[math.exp(1-x) for x in rho];W=sum(weights)
    return [sum(row[j]*weights[j]/W for j in range(3)) for row in ds]
for z in range(200000):
    n=r.randrange(2,8)
    rows=[[r.choice([0.,.1,.25,.5,1.,2.,4.,10.])*r.choice([.1,1.,10.]) for j in range(3)] for i in range(n)]
    i=r.randrange(n);j=r.randrange(3)
    before=pay(rows)[i];old=rows[i][j];rows[i][j]+=1e-5
    after=pay(rows)[i]
    if after<before-1e-9:
       rows[i][j]=old
       print(json.dumps({'case':z,'rows':rows,'owner':i,'coordinate':j,'before':before,'after':after,'slope':(after-before)/1e-5}));break
else:print('no failure')
