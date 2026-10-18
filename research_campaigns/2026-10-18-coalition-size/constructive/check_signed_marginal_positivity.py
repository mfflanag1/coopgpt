from fractions import Fraction as R
from pathlib import Path
import json
comparisons=0
profiles=0
for n in range(1,9):
 m=n-1; W_all=2**m-1; M=2*W_all+1; eps=R(1,4); delta=R(1,8)
 for target in range(2**m):
  Wstar=target
  own=[eps/M,R(Wstar,M),(2*Wstar+eps)/M]
  high=own.copy(); high[1]+=delta/M
  assert all(0<=x<=1 for x in own+high)
  for subset in range(2**m):
   W=subset
   increment=min(high[0]+R(2*W,M),high[1]+R(W,M),high[2])-min(own[0]+R(2*W,M),own[1]+R(W,M),own[2])
   assert increment==(delta/M if subset==target else 0),(n,target,subset,increment)
   comparisons+=1
  profiles+=1
result={'status':'PASS','owner_counts':list(range(1,9)),'target_restorations':profiles,'exact_subset_comparisons':comparisons,'epsilon':'1/4','delta':'1/8','bounded_reports':True}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
