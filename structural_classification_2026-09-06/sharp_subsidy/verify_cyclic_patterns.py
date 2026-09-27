"""Solver-free exact upper certificate for a fixed matching incidence pattern."""
from pathlib import Path
from itertools import product
from fractions import Fraction
import json

def check(data, *, check_protected=True):
 m=data['m'];P=[tuple(t)for t in data['P']];D=data['denominator']
 if type(D) is not int or D<=0:raise ValueError('denominator')
 if any(len({t[s]for t in P})!=len(P)for s in range(3)):raise ValueError('not a matching')
 if any(len(t)!=3 or any(j<0 or j>=m for j in t)for t in P):raise ValueError('team indices')
 support=set()
 for a,b,c in [(j,j,j)for j in range(m)]+P:
  support.update(((0,a,b),(1,a,c),(2,b,c)))
 ordered=sorted(support);idx={e:i for i,e in enumerate(ordered)};off=len(ordered)
 used={s*m+j for t in P for s,j in enumerate(t)};U=sorted(set(range(3*m))-used)
 teams=[]
 for a,b,c in product(range(m),repeat=3):
  es=[idx[e]for e in ((0,a,b),(1,a,c),(2,b,c))if e in idx]
  if es:teams.append(((a,b,c),es))
 # Coefficients of the maximized objective at common denominator 3D.
 residual=[0]*(off+len(U)*3*m)
 for a,b,c in P:
  for e in ((0,a,b),(1,a,c),(2,b,c)):residual[idx[e]]+=3*D
 for k,i in enumerate(U):residual[off+k*3*m+i]=D
 seen=set()
 for row,z in data['inequality_multipliers']:
  if type(row) is not int or type(z) is not int or z<0 or row in seen or not 0<=row<len(U)*len(teams):raise ValueError('inequality multiplier')
  seen.add(row);k,tidx=divmod(row,len(teams));t,es=teams[tidx]
  for e in es:residual[e]-=3*z
  for s,j in enumerate(t):residual[off+k*3*m+s*m+j]+=3*z
 nu=data['equality_multipliers']
 if len(nu)!=len(U)+1 or any(type(z)is not int for z in nu):raise ValueError('equality multipliers')
 for j in range(m):
  for s in range(3):residual[idx[(s,j,j)]]-=3*nu[0]
 for k in range(len(U)):
  for j in range(3*m):residual[off+k*3*m+j]-=3*nu[k+1]
 # Every variable is in [0,1]. Positive residuals are absorbed by valid upper bounds.
 correction=sum(max(0,z)for z in residual)
 upper=Fraction(3*sum(nu)+correction-3*D,3*D)
 if upper>=Fraction(1,3):raise ValueError(f'certificate does not prove below one-third: {upper}')
 scale=data['primal_scale'];v=data['primal_integers']
 if type(scale)is not int or scale<=0 or len(v)!=len(residual) or any(type(z)is not int or z<0 or z>scale for z in v):raise ValueError('primal variables')
 if sum(v[idx[(s,j,j)]]for j in range(m)for s in range(3))!=scale:raise ValueError('primal diagonal worth')
 for k in range(len(U)):
  x=v[off+k*3*m:off+(k+1)*3*m]
  if sum(x)!=scale:raise ValueError('primal core total')
  for t,es in teams:
   if sum(x[s*m+j]for s,j in enumerate(t))<sum(v[e]for e in es):raise ValueError('primal core inequality')
 wp=sum(v[idx[e]]for a,b,c in P for e in ((0,a,b),(1,a,c),(2,b,c)))
 ideal_lower=sum(v[off+k*3*m+i]for k,i in enumerate(U))
 lower=Fraction(3*wp+ideal_lower-3*scale,3*scale)
 if lower<0 or lower>upper:raise ValueError(f'primal obstruction m={m} lower={lower} upper={upper} correction={correction}')
 result={'status':'PASS','m':m,'unmatched_per_sector':m-len(P),'fixed_pattern_lower':str(lower),'fixed_pattern_upper':str(upper),'decimal':float(upper),'nonzero_row_multipliers':len(seen),'residual_correction':str(Fraction(correction,3*D))}
 if not check_protected:
  result['scope']='fixed-pattern upper and primal obstruction only; full subsidy not checked'
  return result
 # Diagonal tightness bounds every original ideal by its diagonal team worth.
 yscale=data['protected_payoff_scale'];yi=data['protected_payoff_integers']
 if type(yscale)is not int or yscale<=0 or len(yi)!=3*m or any(type(z)is not int or z<0 for z in yi):raise ValueError('protected payoff format')
 y=[Fraction(z,yscale)for z in yi]
 diagonal=[Fraction(sum(v[idx[(s,j,j)]]for s in range(3)),scale)for j in range(m)]
 if any(y[s*m+j]<diagonal[j]/3 for s in range(3)for j in range(m)):raise ValueError('original ideal protection')
 for t,es in teams:
  if sum(y[s*m+j]for s,j in enumerate(t))<Fraction(sum(v[e]for e in es),scale):raise ValueError('protected coalition coverage')
 if sum(y)!=1+lower:raise ValueError('exact subsidy upper')
 return {'status':'PASS','m':m,'unmatched_per_sector':m-len(P),'fixed_pattern_lower':str(lower),'exact_witness_market_subsidy':str(lower),'fixed_pattern_upper':str(upper),'decimal':float(upper),'nonzero_row_multipliers':len(seen),'residual_correction':str(Fraction(correction,3*D))}

def main():
 results=[]
 for name in ['CYCLIC_WEIGHTS_2','CYCLIC_WEIGHTS_3','CYCLIC_WEIGHTS_4','MULTICYCLE_k33','MULTICYCLE_prism','MULTICYCLE_cube']:
  path=Path(__file__).with_name(name+'.json')
  d=json.loads(path.read_text());result=check(d);result['pattern']=name;results.append(result)
  bad=dict(d);bad['inequality_multipliers']=[];bad['equality_multipliers']=[0]*len(d['equality_multipliers'])
  try:check(bad)
  except ValueError:pass
  else:raise ValueError('empty dual negative control accepted')
 print(json.dumps({'status':'PASS','cases':results,'negative_controls':len(results),'scope':'specified obstruction patterns over all admissible pair coefficients, not all subsidy packings'}))
if __name__=='__main__':main()
