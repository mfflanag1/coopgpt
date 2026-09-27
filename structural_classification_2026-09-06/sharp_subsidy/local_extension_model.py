"""One-hub extension model with explicit frozen old-weight equations."""
from block_certificate_model import model
from two_hub_block_certificate import structure

def system():
 m=7;P=[(0,1,2),(3,0,4),(5,6,0)];mm,PP=11,P+[(1,7,8),(10,9,1)];old=structure(m,P);new=structure(mm,PP);types,stride,rows,rhs,eq,erhs,bounds=model(mm,PP);rows=[dict(r)for r in rows];rhs=list(rhs);eq=[dict(r)for r in eq];erhs=list(erhs);lookup={tuple(t):k for k,t in enumerate(types)};fixed=set()
 for j in range(2,7):
  t=next(s for s in range(3)if s*m+j in old[0]);e=old[0][t*m+j];b0=new[2][e]
  for s in range(3):
   if s==t:continue
   k=lookup[b0,t,s]
   for e in range(3):fixed.add(k*stride+new[2][e])
 for v in sorted(fixed):eq.append({v:4});erhs.append(1)
 for v,(lo,hi)in enumerate(bounds):rows.append({v:1});rhs.append(hi)
 return mm,PP,types,stride,rows,rhs,eq,erhs,len(bounds)
