"""Parameter used only to locate possible two-fifths extremizing obstructions."""
from fractions import Fraction as F

def parameter(m,P):
    h=m-len(P)
    if h<2:raise ValueError('elementary branch')
    used={s*m+j for team in P for s,j in enumerate(team)}
    degree=[sum(s*m+j in used for s in range(3))for j in range(m)]
    B=F(degree.count(1),h)
    if B<=1:return F(81,100)
    x=[F(sum(degree[j]==1 and s*m+j in used for j in range(m)),h)for s in range(3)]
    cycle_density=F(m-2*h+1,h)
    variance=sum((z-B/3)**2 for z in x)
    gap=F(2,3)*(F(3,2)-B)*(B-F(3,5))
    if cycle_density<0 or gap<0:raise ValueError('outside connected-count domain')
    return F(4,5)+min(F(1),gap+variance+cycle_density)/100
