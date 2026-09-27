"""Exact finite audits of weighted coarea and internal-label cloning counts."""
from itertools import combinations,permutations,product
from collections import Counter
import json
from universal_template import junctions,graft
from mixed_donor_template import construct
from fractions import Fraction as F


def require(ok,msg):
    if not ok:raise ValueError(msg)


def connected(m,P):
    graph=[set() for _ in range(m+len(P))]
    for i,e in enumerate(P):
        for j in e:graph[j].add(m+i);graph[m+i].add(j)
    seen={0};todo=[0]
    while todo:
        for v in graph[todo.pop()]-seen:seen.add(v);todo.append(v)
    return len(seen)==len(graph)


def check(m,P,exhaustive=True):
    P=[tuple(e) for e in P]
    require(connected(m,P),'disconnected')
    used={(s,e[s]) for e in P for s in range(3)}
    require(len(used)==3*len(P),'P overlaps')
    degree=[sum((s,j) in used for s in range(3)) for j in range(m)]
    I=[j for j in range(m) if degree[j]>=2]
    if not I:return 0
    require(all(any(j in I for j in e) for e in P),'all-leaf team')
    labels=[];copies=[]
    for j,k in enumerate(degree):
        copies.append(list(range(len(labels),len(labels)+k)));labels.extend([j]*k)
    usedcopy=Counter();newP=[]
    for e in P:
        out=[]
        for j in e:out.append(copies[j][usedcopy[j]]);usedcopy[j]+=1
        newP.append(tuple(out))
    require(len(labels)==3*len(P),'component label count')
    require(sorted(j for e in newP for j in e)==list(range(len(labels))),'not one use per label')
    new_used={(s,e[s]) for e in newP for s in range(3)}
    for s,j in product(range(3),range(m)):
        new_unmatched=sum((s,v) not in new_used for v in copies[j])
        require(new_unmatched-int((s,j) not in used)==degree[j]-1,'copied-ideal multiplicity')
    values=list(product(range(3),repeat=len(I))) if exhaustive else [tuple([1]*len(I)),tuple(range(len(I)))]+[tuple(int(k==j) for k in range(len(I))) for j in range(len(I))]
    for row in values:
        d=dict(zip(I,row));D=sum(row);D2=sum(d[j] for j in I if degree[j]==2)
        B=sum(min(d[j] for j in e if j in I) for e in P)
        inside=[e for e in P if all(j in I for j in e)]
        B3=sum(min(d[j] for j in e) for e in inside)
        M3=sum(sum(d[j] for j in e) for e in inside)
        require(B<=2*D-D2+min(row),'weighted coarea')
        require(M3>=3*B3 and B-B3<=3*D-D2-M3,'incidence weight bounds')
        require(sum((degree[j]-1)*d[j] for j in I)==2*D-D2,'cloned worth')
    return len(values)


def donor_load_checks():
    counts=Counter()
    for m,P in [junctions(8),graft(*junctions(8),1,1),graft(*junctions(8),1,4)]:
        pack=construct(m,P);h=m-len(P)
        used={(s,e[s]) for e in P for s in range(3)}
        degree=[sum((s,j) in used for s in range(3)) for j in range(m)]
        U=[s*m+j for s in range(3) for j in range(m) if (s,j) not in used]
        loads={i:[F(0)]*(3*m) for i in U}
        for i,e,v in pack['packings']:
            for s,j in enumerate(e):loads[i][s*m+j]+=F(v)
        gamma={j:F(1,5) if degree[j]==2 else F(6,5) for j in range(m) if degree[j]>=2}
        budget=sum(gamma.values());alpha=F(1,h);beta=1-alpha;delta=max(F(0),F(4,5)-2*alpha)
        for s in range(3):
            leafrows=[i for i in U if i//m==s and degree[i%m]==1]
            N=sum(i//m==s and degree[i%m]==2 for i in U)
            L=sum(degree[j]==1 and (s,j) in used for j in range(m))
            D=max(F(0),L*delta-N*min(L*alpha,beta)-len(leafrows)*min(L*alpha,beta-delta))
            if not D:continue
            require(leafrows and budget>0,'positive transfer denominator')
            for i in leafrows:
                for j,g in gamma.items():
                    z=D*g/(len(leafrows)*budget)
                    for r in range(3):
                        if r!=s:
                            require(loads[i][r*m+j]<=1-z,'donor other-sector capacity')
                            counts[degree[j]]+=1
    require(counts[2]>0 and counts[3]>0,'both donor degrees exercised')
    return dict(counts)


def main():
    configs=[]
    for m in (3,4,5):
        for r in range(1,min(2,m-1)+1):
            for aa in combinations(range(m),r):
                for bb in permutations(range(m),r):
                    for cc in permutations(range(m),r):
                        P=list(zip(aa,bb,cc))
                        if connected(m,P):configs.append((m,P))
    count=sum(check(m,P) for m,P in configs)
    extra=[]
    for b in (2,8):extra.append(junctions(b))
    for b in (2,4,8):extra.append((4*b,[(j,(j+1)%b,b+j) for j in range(b)]+[(2*b+2*j,2*b+2*j+1,j) for j in range(b)]))
    extra.append((3,[(0,1,2),(1,2,0)]))
    count+=sum(check(m,P,False) for m,P in extra)
    # A two-team tree with one degree-two internal label needs the +min term.
    m,P=5,[(0,1,2),(3,0,4)]
    require(connected(m,P),'negative control topology')
    require(2>2*1-1,'missing-minimum control')
    print(json.dumps({'status':'PASS','exhaustive_small_supports':len(configs),'additional_supports':len(extra),'weighted_checks':count,'donor_capacity_checks_by_degree':donor_load_checks(),'negative_controls':1,'scope':'finite topology/weight audit, not the all-size proof'}))

if __name__=='__main__':main()
