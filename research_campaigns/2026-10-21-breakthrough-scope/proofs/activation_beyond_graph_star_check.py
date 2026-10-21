from fractions import Fraction as Q
import json
from pathlib import Path
sizes=[11,448,652,24,148,160]
counts=[[11,11,0,0],[112,448,0,112],[163,652,163,0],[12,24,0,24],[111,0,111,148],[120,0,160,120]]
assert all(0<=c<=n for n,row in zip(sizes,counts) for c in row)
beta=[Q(0),Q(1,10),Q(9,20),Q(9,20)]
alpha=[Q(1,2),Q(0),Q(1,4),Q(1,4)]
assert sum(beta)==sum(alpha)==1
v=[sum(Q(c,n)*b for c,b in zip(row,beta)) for n,row in zip(sizes,counts)]
w=[sum(Q(c,n)*a for c,a in zip(row,alpha)) for n,row in zip(sizes,counts)]
vpot=[sum(row[j]*x for row,x in zip(counts,v)) for j in range(4)]
wpot=[sum(row[j]*x for row,x in zip(counts,w)) for j in range(4)]
vnorm=sum(n*x*x for n,x in zip(sizes,v));wnorm=sum(n*x*x for n,x in zip(sizes,w))
assert v==list(map(Q,['1/10','17/80','17/80','11/20','63/80','63/80']))
assert w==list(map(Q,['1/2','3/16','3/16','1/2','13/16','13/16']))
assert vnorm==Q(4961,20) and all(x==vnorm for x in vpot)
assert wnorm==Q(1003,4) and wpot==list(map(Q,['1003/4','895/4','1003/4','1003/4']))
rho=1/vnorm;ell=1/wnorm;z=[x*rho for x in v];q=[x*ell for x in w]
# Each row-class multiplier is distributed uniformly over its finite class.
assert all(sum(Q(c,n)*b*rho for c,b in zip(row,beta))==zz for n,row,zz in zip(sizes,counts,z))
assert all(sum(Q(c,n)*a*ell for c,a in zip(row,alpha))==qq for n,row,qq in zip(sizes,counts,q))
assert all(x*rho==1 for x in vpot)
rhs=[1,0,1,1]
assert all(x*ell>=b for x,b in zip(wpot,rhs))
assert all(a==0 or x*ell==b for a,x,b in zip(alpha,wpot,rhs))
assert q[0]/ell==Q(1,2) and v[0]==Q(1,10)
Hfallback=rho*(sizes[0]*w[0]**2+sum(n*x*x for n,x in zip(sizes[1:],v[1:])))
assert Hfallback==1+Q(264,24805)
out={'status':'PASS','coordinate_count':sum(sizes),'row_sizes':[sum(row[j] for row in counts) for j in range(4)],'full_norm_squared':str(vnorm),'full_rho':str(rho),'local_norm_squared':str(wnorm),'local_mass':str(ell),'focal_payment':str(q[0]),'pointwise_ratio':str(w[0]/v[0]),'aggregate_with_other_full_witnesses':str(Hfallback),'v':[str(x) for x in v],'w':[str(x) for x in w]}
(Path(__file__).parent/'activation_beyond_graph_star_check_results.txt').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
