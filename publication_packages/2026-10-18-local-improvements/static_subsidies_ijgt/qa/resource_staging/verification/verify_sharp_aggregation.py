"""Exact symbolic identities and semantic corroboration of the candidate bound.

Standard library only. The written all-size argument, not this finite sample,
establishes the universal statement. Run with python -O.
"""
import json,sys,itertools,hashlib
from pathlib import Path
from fractions import Fraction as Q

def need(ok,msg):
 if not ok:raise ValueError(msg)

class Poly(dict):
 def __add__(a,b):
  b=poly(b);out=Poly(a)
  for k,v in b.items():out[k]=out.get(k,Q(0))+v
  return Poly({k:v for k,v in out.items() if v})
 __radd__=__add__
 def __neg__(a):return Poly({k:-v for k,v in a.items()})
 def __sub__(a,b):return a+-poly(b)
 def __rsub__(a,b):return poly(b)+-a
 def __mul__(a,b):
  out=Poly()
  for k,v in a.items():
   for l,w in poly(b).items():
    term=tuple(sorted(k+l));out[term]=out.get(term,Q(0))+v*w
  return Poly({k:v for k,v in out.items() if v})
 __rmul__=__mul__

def poly(v):return v if isinstance(v,Poly) else Poly({():Q(v)}) if v else Poly()
def var(s):return Poly({(s,):Q(1)})
def equal(a,b,msg):need(not (poly(a)-b),msg)

def symbolic():
 count=0
 for labels in itertools.product(range(3),repeat=3):
  d=[var('d'+str(j)) for j in range(3)];u=[[var(f'u{s}{j}') for j in range(3)] for s in range(3)];h=[[var(f'h{s}{j}') for j in range(3)] for s in range(3)];v=var('v')
  summed=sum(d[labels[s]]+u[r][labels[r]]+h[t][labels[t]]-h[t][labels[s]]-v for r,s,t in itertools.permutations(range(3)))
  expected=2*sum(d[j] for j in labels)+2*sum(u[s][labels[s]] for s in range(3))+3*sum(h[s][labels[s]] for s in range(3))-sum(sum(h[s][j] for s in range(3)) for j in labels)-6*v
  equal(summed,expected,'sixfold count');need(bool(summed-(expected-sum(h[s][labels[s]] for s in range(3)))),'changed positive coefficient undetected');count+=1
 # One arbitrary diagonal label suffices for the all-size sum; use raw pair symbols.
 a,b,c=map(var,['ab','ac','bc']);d=a+b+c;u=[a+b,a+c,b+c];p=[var('p'+str(s)) for s in range(3)];q=[1-z for z in p];h=[var('h'+str(s)) for s in range(3)];n=sum(p)
 E=sum(sum(q[t] for t in range(3) if t!=s)*(d-h[s]) for s in range(3))
 left=2*n*d+2*sum(p[s]*u[s] for s in range(3))+3*sum(p[s]*h[s] for s in range(3))-n*sum(h)+2*sum(q[s]*h[s] for s in range(3))
 right=10*d-2*sum(q[s]*u[s] for s in range(3))-E
 equal(left,right,'fractional label aggregation')
 for s in range(3):equal((3-n)*p[s]+(2-n)*q[s],sum(q[t] for t in range(3) if t!=s),'fractional deficit coefficient')
 k,T,B,V,C=map(var,['k','T','B','V','C'])
 EL=10*T-2*B-2*V;F=3*k*T+k*B-C-k*V
 equal(2*k*(4*T-V),Q(1,2)*k*EL+C+F,'fractional slack identity')
 FI=3*k*T+(k-1)*B-k*V
 equal((8*k-5)*T-(2*k-1)*V,Q(1,2)*(k-1)*EL+FI,'integral slack identity')
 need(bool((8*k-5)*T-(2*k)*V-(Q(1,2)*(k-1)*EL+FI)),'denominator corruption undetected')
 return {'repeated_label_team_patterns':count,'per_label_polynomial_identities':4,'global_slack_identities':2,'symbolic_corruptions_rejected':count+1}

def semantic(m,w,H,lam,integral=False):
 def val(t):a,b,c=t;return w[0][a][b]+w[1][a][c]+w[2][b][c]
 d=[val((j,j,j)) for j in range(m)];T=sum(d);need(T>0,'positive grand worth')
 u=[(w[0][j][j]+w[1][j][j],w[0][j][j]+w[2][j][j],w[1][j][j]+w[2][j][j])[s] for s in range(3) for j in range(m)]
 need(all(0<=H[s*m+j]<=d[j] for s in range(3) for j in range(m)),'ideal diagonal caps')
 p=[Q(0)]*(3*m);W=Q(0);L=Q(0)
 for team,mass in lam:
  need(mass>=0,'packing sign');W+=mass*val(team)
  for s,j in enumerate(team):p[s*m+j]+=mass
  for r,s,t in itertools.permutations(range(3)):
   slack=d[team[s]]+u[r*m+team[r]]+H[t*m+team[t]]-H[t*m+team[s]]-val(team)
   need(slack>=0,'ideal P-induced comparison');L+=mass*slack
 need(max(p)<=1,'packing capacities');q=[1-z for z in p];k=m-sum(mass for _,mass in lam)
 need(all(sum(q[s*m:(s+1)*m])==k for s in range(3)),'sector residual mass')
 S=sum(v*x for v,x in zip(q,H));B=sum(v*x for v,x in zip(q,u));C=sum(v*v*x for v,x in zip(q,u));V=3*W+S
 E=sum(sum(q[t*m+j] for t in range(3) if t!=s)*(d[j]-H[s*m+j]) for s in range(3) for j in range(m))
 need(10*T-2*B-2*V==E+L,'semantic sixfold identity');need(E>=0 and L>=0,'deficit/slack sign')
 if k==0:need(V<=3*T,'perfect fractional packing');return {'T':str(T),'k':'0','J':str(V/3-T),'strict':V<4*T}
 F=Q(0)
 for i in range(3*m):
  if not q[i]:continue
  slack=T-W+(k-q[i])*u[i]-k*H[i];need(slack>=0,'residual witness budget');F+=q[i]*slack
 need(2*k*(4*T-V)==k*(E+L)/2+C+F,'semantic fractional identity');need(V<4*T,'strict global upper')
 bound=None
 if integral:
  need(all(z in (0,1) for z in q),'integral capacities');need(k.denominator==1,'integral k')
  need((8*k-5)*T-(2*k-1)*V==(k-1)*(E+L)/2+F,'semantic integral identity')
  bound=2*(k-1)*T/(3*(2*k-1));need(V/3-T<=bound,'integral sharp upper')
 return {'T':str(T),'k':str(k),'J':str(V/3-T),'integral_upper':str(bound) if bound is not None else None,'E':str(E),'L':str(L),'F':str(F),'C2':str(C),'strict':True}

def main():
 root=Path(sys.argv[1]);report={'status':'PASS','optimized_python':sys.flags.optimize,'symbolic':symbolic(),'calibration':[],'enriched_points':{},'negative_controls':[]}
 for n in range(1,13):
  m=2*n+1;w=[[[Q(int(a==b)) for b in range(m)] for a in range(m)] for _ in range(3)];P=[(s,n+s,s-1 if s else 2*n) for s in range(n)]
  for a,b,c in P:w[0][a][b]=2;w[1][a][c]=1;w[2][b][c]=2
  H=[Q(3)]*(3*m)
  for alpha in (Q(0),Q(1,10),Q(1,2),Q(1)):
   lam=[((j,j,j),1-alpha) for j in range(m)]+[(t,alpha) for t in P];z=semantic(m,w,H,lam,integral=alpha in (0,1));z.update(q=n,alpha=str(alpha));report['calibration'].append(z)
   if alpha==1:need(z['J']==str(2*n) and z['integral_upper']==str(2*n),'lower family equality')
   if n==1 and alpha==Q(1,2):
    need(Q(z['k'])==1 and Q(z['J'])==1,'fractional scope countercontrol');report['negative_controls'].append('fractional k=1 can have J=1 at T=9; integral k formula must not be applied')
 for name,folder in [('CW-01','interpretation'),('CW-04','interpretation'),('CW-05','heldout'),('CW-06','heldout')]:
  raw=json.loads((root/folder/(name+'_residual.json')).read_text());w=[[[Q(v) for v in row] for row in mat] for mat in raw['matrices']];z=semantic(raw['m'],w,list(map(Q,raw['h'])),[(t,Q(1)) for t in raw['P']],True);need(z['J']==raw['J_relaxed'],'diagnostic objective');report['enriched_points'][name]=z
 for name in ('CW-01','CW-04'):
  raw=json.loads((root/'paired'/(name+'_relaxed.json')).read_text());w=[[[Q(v) for v in row] for row in mat] for mat in raw['matrices']]
  try:semantic(raw['m'],w,list(map(Q,raw['h'])),[(t,Q(1)) for t in raw['P']],True)
  except ValueError as e:need(str(e)=='residual witness budget','unexpected rejection');report['negative_controls'].append(name+' false relaxed point rejected by missing budget')
  else:raise ValueError('false diagnostic accepted')
 report['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','symbolic':report['symbolic'],'lower_family_fractional_cases':len(report['calibration']),'enriched_cases':len(report['enriched_points']),'negative_controls':len(report['negative_controls'])}))
if __name__=='__main__':main()
