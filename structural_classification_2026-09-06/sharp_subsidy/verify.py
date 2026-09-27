from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,sys
from source_certificates import independent_triangle,vertices,ideals,unmatched,require
OUT=Path(__file__).resolve().parent

def market(q,a):
 g=independent_triangle(q)
 for M in g['matrices'][:2]:
  for row in M:
   for j in range(len(row)):row[j]=F(row[j])*a/2
 g['T']=2*a*q+2*q+1
 return g

def original_vertices(q,a):
 out=vertices(q)
 for v in out:
  for s in range(1,q+1):v[3*s-2]-=4-2*a
 return out

def Hvec(q,a):
 h=ideals(q)
 for s in range(1,q+1):h[3*s-2]=F(2*a)
 return h

def subsidy_payoff(q,a):
 m=3*q+1;alpha=F(1,3*(q+1));p=[F(0)]*(3*m)
 for s in range(q+1):
  L=0 if s==0 else 3*s-1
  p[L]=alpha;p[m+L]=F(2,3)-(s+1)*alpha;p[2*m+L]=F(1,3)+s*alpha
 for s in range(1,q+1):
  O,R=3*s-2,3*s
  p[O]=2*a-(s-1)*alpha;p[m+O]=F(1,3);p[2*m+O]=F(1,3)+(s-1)*alpha
  p[R]=alpha;p[m+R]=F(2,3)-alpha;p[2*m+R]=F(1,3)
 return p

def covers(g,p,total):
 require(sum(p)==total and min(p)>=0,'payoff budget or positivity')
 count=0;m=g['m'];A,B,C=g['matrices']
 for a,b,c in product(range(m),repeat=3):
  require(p[a]+p[m+b]+p[2*m+c]>=A[a][b]+B[a][c]+C[b][c],'uncovered triple')
  count+=1
 return count

def smt(g,H):
 import z3
 m=g['m'];p=[z3.Real(f'p{i}')for i in range(3*m)];A,B,C=g['matrices']
 rat=lambda v:z3.Q(F(v).numerator,F(v).denominator)
 raw=[v>=0 for v in p]+[z3.Sum(p)==rat(g['T'])]
 for a,b,c in product(range(m),repeat=3):raw.append(p[a]+p[m+b]+p[2*m+c]>=rat(A[a][b]+B[a][c]+C[b][c]))
 s=z3.Solver();s.set(timeout=60000);s.add(raw+[z3.Or([v>rat(h)for v,h in zip(p,H)])])
 require(s.check()==z3.unsat,'uncertified ideal upper bound')
 return {'q':g['q'],'T':str(g['T']),'query':'any_original_ideal_exceeds_formula','result':'UNSAT'}

def main():
 (OUT/'VERIFICATION.json').write_text('{"status":"RUNNING"}\n');out=[];count=0;queries=[]
 for a in [1,2]:
  for q in range(1,9):
   g=market(q,a);H=Hvec(q,a);vs=original_vertices(q,a);m=g['m'];T=g['T']
   require(sum(sum(M[j][j]for M in g['matrices'])for j in range(m))==T,'integral worth lower certificate')
   count+=sum(covers(g,v,T)for v in vs)
   require([max(v[i]for v in vs)for i in range(3*m)]==H,'ideal attainment')
   p=subsidy_payoff(q,a);s=F(2*q,3);count+=covers(g,p,T+s)
   require(all(v>=h/3 for v,h in zip(p,H)),'frozen-ideal floor')
   U,delta=unmatched(g);require(delta==1,'matching shortfall')
   require(sum(H[i]for i in U)/3-delta==s,'dual gap')
   out.append({'a':a,'q':q,'T':str(T),'subsidy':str(s),'ratio':str(s/T),'H':list(map(str,H)),'y':list(map(str,p)),'U':U,'dual_matching':g['partial_matching'],'status':'PASS'})
   if '--smt'in sys.argv and q<=4:queries.append(smt(g,H))
   print(json.dumps({k:out[-1][k]for k in ['a','q','subsidy','ratio','status']}),flush=True)
 (OUT/'CERTIFICATES.json').write_text(json.dumps(out,indent=2)+'\n')
 (OUT/'VERIFICATION.json').write_text(json.dumps({'status':'PASS','cover_checks':count,'cases':16,'smt_queries':queries},indent=2)+'\n')
 print(json.dumps({'status':'PASS','cover_checks':count,'smt_queries':len(queries)}))
if __name__=='__main__':
 try:main()
 except BaseException as e:
  (OUT/'VERIFICATION.json').write_text(json.dumps({'status':'FAILED','error':str(e)})+'\n');raise
