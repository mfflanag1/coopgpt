from report_lp import solve
for a,b,levels in [(3,3,(0,1,3)),(3,3,(1,2,4)),(3,3,(0,1,2,4)),(2,3,(0,1,2,4))]:
 domains=[[(x,0,0)for x in levels]]*a+[[(0,x,0)for x in levels]]*b
 solve(f'multilevel_A{a}_B{b}_levels'+''.join(map(str,levels)),domains)
