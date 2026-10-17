from fractions import Fraction as Q
if not __debug__:raise RuntimeError('Assertions must remain enabled')
n=5;rows=[set((r+t)%n for t in range(3)) for r in range(n)]
full=[Q(1)]*n
assert sum(full)==5 and all(sum(full[j] for j in S)==3 for S in rows)
for i in range(n):
 b=[Q(3)]*n;b[(i-1)%n]=Q(3,2)
 q=[Q(3,2) if j in(i,(i+2)%n,(i+3)%n) else Q(0) for j in range(n)]
 assert [sum(q[j] for j in S) for S in rows]==b
 assert sum(q)==sum(b)/3==Q(9,2)
 a=rows[i];c=rows[(i+3)%n]
 assert a&c=={i} and a|c==set(range(n))
 assert b[i]+b[(i+3)%n]==6
 assert [int(j in a)+int(j in c) for j in range(n)]==[1+int(j==i) for j in range(n)]
k=Q(12,11)
assert k==6-Q(9,2)*k
print({'status':'PASS','low_profiles':5,'minimum_necessary_funding_factor':'12/11','row_arity':3,'column_frequency':3})
