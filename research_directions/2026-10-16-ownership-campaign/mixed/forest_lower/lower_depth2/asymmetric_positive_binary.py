from report_lp import solve
for a,b in [(2,3),(2,4),(3,4)]:
 for h in [3,4,8]:
  domains=[[(1,0,0),(h,0,0)]]*a+[[(0,1,0),(0,h,0)]]*b
  solve(f'asymmetric_A{a}_B{b}_H{h}',domains)
