from fractions import Fraction as Q
if not __debug__:raise RuntimeError('Assertions must remain enabled')
def worth(mask,c):
 return min(sum((c[2*s+j] if mask>>(2*s+j)&1 else 0) for j in range(2)) for s in range(len(c)//2))
def pays(mask,z):return sum((x for j,x in enumerate(z) if mask>>j&1),Q(0))
checks=0
for k in range(2,8):
 n=2*k;full=[Q(2),Q(1)]*k;high=sum(1<<(2*s) for s in range(k));low=sum(1<<(2*s+1) for s in range(k))
 q=[Q(2,k),Q(1,k)]*k
 assert sum(q)==3 and worth(high,full)==2 and worth(low,full)==1
 for mask in range(1<<n):assert pays(mask,q)>=worth(mask,full);checks+=1
 for i in range(k):
  c=full[:];c[2*i]=Q(1);z=[Q(0)]*n;z[2*i]=z[2*i+1]=Q(1)
  C=high|(1<<(2*i+1));DH=(1<<(2*i))|(low^(1<<(2*i+1)));DL=low
  assert worth(C,c)==2 and worth(DH,c)==1 and worth(DL,c)==1
  assert sum(z)==2 and pays(C,z)==2 and pays(DH,z)==1 and pays(DL,z)==1
  for mask in range(1<<n):assert pays(mask,z)>=worth(mask,c);checks+=1
 assert Q(k+1,3)==Q(n+2,6)
print({'status':'PASS','largest_pool_count':7,'coalition_checks':checks,'linear_bound':'(n+2)/6 for n=2k>=4'})
