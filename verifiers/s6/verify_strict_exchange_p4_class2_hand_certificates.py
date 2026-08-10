#!/usr/bin/env python3
"""Verify the class-2 universal-order relay using exact rational arithmetic.

This checker imports no solver and no production encoder.  It reconstructs
the affine premises at all 132 certificate uses, recomputes twenty-one exact
difference-cone candidate censuses, and audits all 72 activation-failure
cases after solver-free minimum/maximum-level DNF compression.
"""
from __future__ import annotations

import argparse
import copy
import json
from fractions import Fraction
from itertools import combinations
from math import lcm
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'strict_exchange_p4_class2_hand_certificate_rows.json'
H={10:(1,-1,0,0,0,0),16:(0,-1,-1,0,1,1),
   17:(0,-1,0,-1,1,1),18:(0,0,-1,-1,1,1),
   11:(1,0,0,1,-1,-1),12:(1,0,1,0,-1,-1)}
BRANCH_SIDE_MAP={}

def parse_stage(stage):
 parts=stage.split('-');order=parts[0]
 if order not in ('W','S') or not parts[-1].startswith('h'):raise AssertionError(f'bad stage {stage}')
 direction=int(parts[-1][1:]);path=[]
 for token in parts[1:-1]:
  if not token.startswith('C'):raise AssertionError(f'bad path token {token}')
  path.append(tuple(int(i) for i in token[1:]))
 sides=BRANCH_SIDE_MAP.get(stage,())
 if path and len(sides)!=len(path):raise AssertionError(f'missing branch-side map for {stage}')
 branches=[]
 for index,C in enumerate(path):branches.append(('C'+''.join(map(str,C)),C,sides[index]))
 return {'orders':(order,),'branches':tuple(branches),'blocker_side':'max' if direction in (10,11,12) else 'min','direction':direction,'path':tuple(path)}

def linear(*terms):
 out={}
 for a,form in terms:
  a=Fraction(a)
  for name,value in form.items():
   result=out.get(name,Fraction())+a*value
   if result:out[name]=result
   else:out.pop(name,None)
 return out
def variable(name):return {name:Fraction(1)}
def constant(value):return {'constant':Fraction(value)} if Fraction(value) else {}
def point_sum(point,players):return linear(*((1,point[i]) for i in players))
def comparison(table,name,C,left,right):table[name]=linear((1,point_sum(left,C)),(-1,point_sum(right,C)))

def named_system(stage,identity,use):
 config=parse_stage(stage);x=[variable(f'x{i}') for i in range(6)];z=[variable(f'z{i}') for i in range(6)];q=[variable(f'q{i}') for i in range(6)]
 I={}
 for prefix,point in (('x',x),('z',z),('q',q)):
  for i in range(6):I[f'{prefix}{i}>=0']=linear((-1,point[i]))
 for i in range(4):I[f'd{i}>=0']=linear((1,z[i]),(-1,x[i]))
 for i in (4,5):I[f'delta{i}>=0']=linear((1,x[i]),(-1,z[i]))
 for i in range(1,6):I[f'x0<=x{i}']=linear((1,x[0]),(-1,x[i]))
 for i in (0,2,3,4,5):I[f'z{i}<=z1']=linear((1,z[i]),(-1,z[1]))
 for name,C in (('P4',(1,4)),('P5',(0,1,5))):comparison(I,name+'o',C,x,z);comparison(I,name+'q',C,x,q)
 order_forms={'W':linear((1,x[3]),(-1,x[4])),'S':linear((1,x[4]),(-1,x[3])),
              'L':linear((1,x[1]),(-1,x[2])),'R':linear((1,x[2]),(-1,x[1]))}
 for order in config['orders']:I[order]=order_forms[order]
 for name,C,side in config['branches']:
  ref,opp=(x,z) if side=='min' else (z,x);comparison(I,name+'o',C,ref,opp);comparison(I,name+'q',C,ref,q)
 if identity['kind']=='blocker':
  side=config['blocker_side']
  if side is None:raise AssertionError(f'blocker used at non-blocker stage {stage}')
  ref,opp=(z,x) if side=='max' else (x,z);C=tuple(identity['coalition'])
  comparison(I,'Co',C,ref,opp);comparison(I,'Cq',C,ref,q)
 hypotheses={'z1<=z0':linear((1,z[1]),(-1,z[0]))}
 for i in (1,2,3):
  for rich in (4,5):hypotheses[f'x{i}<=x{rich}']=linear((1,x[i]),(-1,x[rich]))
 hypotheses['x4<=x5']=linear((1,x[4]),(-1,x[5]));hypotheses['x5<=x4']=linear((1,x[5]),(-1,x[4]))
 for i in (0,2,3):
  for rich in (4,5):hypotheses[f'z{rich}<=z{i}']=linear((1,z[rich]),(-1,z[i]))
 if identity['kind']=='activation':
  expected=set(use.get('failure_atoms',[]))
  if not expected:raise AssertionError('activation use lacks failure atoms')
  for name in expected:
   if name not in hypotheses:raise AssertionError(f'unknown failure atom {name}')
   I[name]=hypotheses[name]
 E={'sumx':linear((1,point_sum(x,range(6))),(-1,constant(1))),
    'sumz':linear((1,point_sum(z,range(6))),(-1,constant(1))),
    'sumq':linear((1,point_sum(q,range(6))),(-1,constant(1))),'q1':q[1]}
 D=linear((1,point_sum(x,(0,1,2,3))),(-1,point_sum(z,(0,1,2,3))))
 T={'D-1/3':linear((1,D),(-1,constant(Fraction(1,3)))),'d0':linear((1,x[0]),(-1,z[0])),
    'S-strict':linear((1,x[4]),(-1,x[3]))}
 if identity['target'] not in T:raise AssertionError(f"unknown target {identity['target']}")
 return I,E,T[identity['target']]

def verify_use(use,identities):
 if use['identity'] not in identities:raise AssertionError(f"unknown identity {use['identity']}")
 row=identities[use['identity']]
 if use['kind']!=row['kind']:raise AssertionError('kind mismatch')
 if row['kind']=='blocker':
  if tuple(use['coalition'])!=tuple(row['coalition']):raise AssertionError('coalition mismatch')
  if use.get('sources')!=['opposite','q1'] or row.get('sources')!=['opposite','q1']:raise AssertionError('source mismatch')
 I,E,target=named_system(use['stage'],row,use);terms=[]
 for name,value in row['inequality_multipliers'].items():
  value=Fraction(value)
  if name not in I:raise AssertionError(f"premise {name} unavailable at {use['stage']}")
  if value<0:raise AssertionError(f'negative multiplier {name}={value}')
  terms.append((value,I[name]))
 for name,value in row['equality_multipliers'].items():
  if name not in E:raise AssertionError(f"equality {name} unavailable at {use['stage']}")
  terms.append((Fraction(value),E[name]))
 residual=linear((1,linear(*terms)),(-1,target))
 if residual:raise AssertionError(f"identity {row['id']} fails at {use['stage']}: {residual}")
 scale=1
 for value in list(row['inequality_multipliers'].values())+list(row['equality_multipliers'].values()):scale=lcm(scale,Fraction(value).denominator)
 return {'stage':use['stage'],'identity':row['id'],'kind':row['kind'],'target':row['target'],
         **({'coalition':row['coalition'],'sources':row['sources']} if row['kind']=='blocker' else {}),'integer_scale':scale}

def eligible(h):return [C for size in range(1,6) for C in combinations(range(6),size) if sum(h[i] for i in C)<0]
def normalize(rows):
 best={}
 for coefficients,rhs in rows:
  coefficients=tuple(coefficients)
  if coefficients not in best or rhs<best[coefficients]:best[coefficients]=rhs
 return list(best.items())
def fm_feasible(rows,n):
 rows=normalize(rows)
 for index in reversed(range(n)):
  pos=[];neg=[];zero=[]
  for coefficients,rhs in rows:
   value=coefficients[index]
   if value>0:pos.append((coefficients,rhs))
   elif value<0:neg.append((coefficients,rhs))
   else:zero.append((coefficients[:index]+coefficients[index+1:],rhs))
  combined=list(zero)
  for p,pr in pos:
   for q,qr in neg:
    combined.append((tuple((-q[index])*p[j]+p[index]*q[j] for j in range(len(p)) if j!=index),(-q[index])*pr+p[index]*qr))
  rows=normalize(combined)
  if any(not c and rhs<0 for c,rhs in rows):return False
 return not any(rhs<0 for _,rhs in rows)
def d_form(C):
 out=[Fraction() for _ in range(5)]
 for i in C:
  if i<4:out[i]+=1
  elif i==4:out[4]-=1
  else:
   for j in range(4):out[j]-=1
   out[4]+=1
 return tuple(out)
def dcone(branches):
 rows=[]
 for i in range(5):
  c=[Fraction() for _ in range(5)];c[i]=-1;rows.append((tuple(c),Fraction(-1)))
 rows.append(((-1,-1,-1,-1,1),Fraction(-1)))
 rows.extend([((0,1,0,0,-1),Fraction()),((0,0,-1,-1,1),Fraction())])
 for C,side in branches:
  form=d_form(C);rows.append((form if side=='min' else tuple(-v for v in form),Fraction()))
 return rows

SPEC='''
W-h16|124,125,0124,0125,1235|0124
W-C0124-h10|1,12,13,123,125,134,135,1234,1235|
S-h17|134,135,0134,0135,1235|134,0134,135,0135
S-C134-h16|124,125,0124,1235|124,0124
S-C134-C124-h18|234,235,1235|
S-C134-C0124-h18|234|234
S-C134-C0124-C234-h10|1,12,13,123,125,134,135,1234,1235|134
S-C134-C0124-C234-C134-h11|125|
S-C0134-h10|1,12,13,123,124,125,135,1234,1235|12,13,124,135
S-C0134-C12-h18|234|
S-C0134-C13-h18|234|
S-C0134-C124-h16|124|124
S-C0134-C124-C124-h18|234|234
S-C0134-C124-C124-C234-h12|135|
S-C0134-C135-h16|124,0124|
S-C135-h16|124,125,0125,1235|125,0125
S-C135-C125-h18|234,235,0235,1235|
S-C135-C0125-h18|235,0235,1235|
S-C0135-h16|125,0125,1235|125,0125
S-C0135-C125-h18|235,0235,1235|
S-C0135-C0125-h10|1,12,13,14,123,124,134,1234,1235|
'''.strip().splitlines()

SIDE_SPEC={
 'W-C0124-h10':'n','S-C134-h16':'n','S-C134-C124-h18':'nn','S-C134-C0124-h18':'nn',
 'S-C134-C0124-C234-h10':'nnn','S-C134-C0124-C234-C134-h11':'nnnx','S-C0134-h10':'n',
 'S-C0134-C12-h18':'nx','S-C0134-C13-h18':'nx','S-C0134-C124-h16':'nx',
 'S-C0134-C124-C124-h18':'nxn','S-C0134-C124-C124-C234-h12':'nxnn',
 'S-C0134-C135-h16':'nx','S-C135-h16':'n','S-C135-C125-h18':'nn',
 'S-C135-C0125-h18':'nn','S-C0135-h16':'n','S-C0135-C125-h18':'nn',
 'S-C0135-C0125-h10':'nn'}
for name,codes in SIDE_SPEC.items():BRANCH_SIDE_MAP[name]=tuple('min' if code=='n' else 'max' for code in codes)

def cuts(text):return {tuple(int(i) for i in token) for token in text.split(',') if token}
STRUCT={};SURVIVORS={}
for row in SPEC:
 name,candidate_text,survivor_text=row.split('|');config=parse_stage(name);direction=config['direction']
 branches=tuple((C,side) for _,C,side in config['branches'])
 STRUCT[name]=(H[direction],config['blocker_side'],branches,cuts(candidate_text));SURVIVORS[name]=cuts(survivor_text)

def failure_atoms(direction,case):
 if direction==10:return ('z1<=z0',) if case==1 else ()
 if direction in (16,17,18):
  a,b={16:(1,2),17:(1,3),18:(2,3)}[direction];pairs=((a,a),(a,b),(b,a),(b,b))
  return (f'x{pairs[case-1][0]}<=x4',f'x{pairs[case-1][1]}<=x5') if 1<=case<=4 else ()
 if direction in (11,12):
  a,b={11:(0,3),12:(0,2)}[direction];pairs=((a,a),(a,b),(b,a),(b,b))
  return (f'z4<=z{pairs[case-1][0]}',f'z5<=z{pairs[case-1][1]}') if 1<=case<=4 else ()
 return ()

def audit_activation_logic():
 for a in range(4):
  for b in range(4):
   for r in range(4):
    for s in range(4):
     production_min=(a>r and b>r and s>=r) or (a>s and b>s and r>=s)
     failure_min=(a<=r and a<=s) or (a<=r and b<=s) or (b<=r and a<=s) or (b<=r and b<=s)
     production_max=(a<r and b<r and s<=r) or (a<s and b<s and r<=s)
     failure_max=(a>=r and a>=s) or (a>=r and b>=s) or (b>=r and a>=s) or (b>=r and b>=s)
     if production_min==failure_min or production_max==failure_max:raise AssertionError('activation DNF equivalence failed')
 return {'tested_total_preorder_representatives':4**4,
         'lmin_equivalent_form':'min(a,b)>min(r,s)',
         'lmax_equivalent_form':'max(a,b)<max(r,s)','failure_dnf_cases':[1,2,3,4]}

def census(override=None):
 result={}
 for name,(h,side,branches,expected) in STRUCT.items():
  if override and name in override:expected=override[name]
  actual=set()
  for C in eligible(h):
   form=d_form(C);block=form if side=='min' else tuple(-v for v in form)
   if fm_feasible([*dcone(branches),(block,Fraction())],5):actual.add(C)
  if actual!=expected:raise AssertionError(f'census changed at {name}: {actual}')
  result[name]={'eligible_cut_count':len(eligible(h)),'opposite_candidate_count':len(actual),'opposite_candidates':[list(C) for C in sorted(actual)]}
 return result

def audit_uses(uses,identities):
 keys=[(u['kind'],u['stage'],tuple(u.get('coalition',())),u.get('failure_case')) for u in uses]
 if len(keys)!=len(set(keys)):raise AssertionError('duplicate use')
 blockers=[u for u in uses if u['kind']=='blocker'];actual={s:{tuple(u['coalition']) for u in blockers if u['stage']==s} for s in SURVIVORS}
 expected={s:STRUCT[s][3]-survivors for s,survivors in SURVIVORS.items()}
 if actual!=expected:raise AssertionError(f'blocker use map incomplete: {actual}')
 acts=[u for u in uses if u['kind']=='activation'];actual_cases={(u['stage'],u['failure_case']) for u in acts}
 expected_cases=set()
 for name,(_,_,_,_) in STRUCT.items():
  direction=parse_stage(name)['direction']
  for case in ((1,) if direction==10 else (1,2,3,4)):expected_cases.add((name,case))
 for use in acts:
  direction=parse_stage(use['stage'])['direction'];expected_atoms=failure_atoms(direction,use['failure_case'])
  if tuple(use.get('failure_atoms',()))!=expected_atoms:raise AssertionError(f'failure atoms changed at {use["stage"]} case {use["failure_case"]}')
 if actual_cases!=expected_cases or len(acts)!=72:raise AssertionError('activation failure map incomplete')
 if {u['identity'] for u in uses}!=set(identities):raise AssertionError('orphan identity')
 return {'blocker_uses_by_stage':{s:len(v) for s,v in expected.items()},
         'certified_activation_failures_by_stage':{s:sum(u['stage']==s for u in acts) for s in sorted(STRUCT)},
         'total_activation_failure_cases':len(acts)}

def audit_semantics(uses,identities,strict=frozenset({'d0','S-strict'})):
 counts={'D-1/3':0,'d0':0,'S-strict':0};sources={'q1_only':0,'opposite_only':0,'both':0}
 for use in uses:
  row=identities[use['identity']];target=row['target'];counts[target]+=1
  if target in ('d0','S-strict') and target not in strict:raise AssertionError(f'{target} lacks strict semantics')
  if row['kind']=='blocker':
   co='Co' in row['inequality_multipliers'];cq='Cq' in row['inequality_multipliers']
   sources['both' if co and cq else 'opposite_only' if co else 'q1_only' if cq else 'both']+=1
   if not (co or cq):raise AssertionError('blocker certificate uses neither source comparison')
 if counts!={'D-1/3':120,'d0':7,'S-strict':5}:raise AssertionError(f'target counts changed: {counts}')
 if sources!={'q1_only':38,'opposite_only':10,'both':12}:raise AssertionError(f'source localization changed: {sources}')
 return counts,sources

def reject(fn,label):
 try:fn()
 except AssertionError:return label
 raise AssertionError(f'mutation passed: {label}')
def signature(row):return (row['kind'],row['target'],tuple(row.get('coalition',())),tuple(sorted(row['inequality_multipliers'].items())),tuple(sorted(row['equality_multipliers'].items())))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=SOURCE);parser.add_argument('--output',type=Path);args=parser.parse_args()
 source=json.loads(args.source.read_text())
 if source.get('schema')!='strict-exchange-p4-class2-hand-certificate-rows-v1' or source.get('status')!='FROZEN_PROOF_OBJECT':raise AssertionError('unexpected proof object')
 identities={row['id']:row for row in source['identities']}
 if len(identities)!=len(source['identities']) or len({signature(r) for r in identities.values()})!=len(identities):raise AssertionError('identity ids are not deduplicated')
 counts={k:sum(r['kind']==k for r in identities.values()) for k in ('blocker','activation')}
 if counts!={'blocker':52,'activation':56}:raise AssertionError(f'identity counts changed: {counts}')
 structure=census();logic=audit_activation_logic();use_audit=audit_uses(source['uses'],identities);targets,sources=audit_semantics(source['uses'],identities)
 checked=[verify_use(use,identities) for use in source['uses']]
 bad=copy.deepcopy(identities);first=bad[source['uses'][0]['identity']];premise=next(iter(first['inequality_multipliers']));first['inequality_multipliers'][premise]=str(Fraction(first['inequality_multipliers'][premise])+1)
 coefficient=reject(lambda:verify_use(source['uses'][0],bad),'rejected coefficient perturbation')
 displaced=next(copy.deepcopy(u) for u in source['uses'] if u['kind']=='blocker' and u['stage']=='S-C134-C124-h18');displaced['stage']='W-h16'
 use_site=reject(lambda:verify_use(displaced,identities),'rejected identity at stage lacking branch premises')
 expected=set(STRUCT['W-h16'][3]);expected.remove(next(iter(expected)))
 candidate=reject(lambda:census({'W-h16':expected}),'rejected candidate deletion')
 use_delete=reject(lambda:audit_uses(source['uses'][1:],identities),'rejected use-map deletion')
 altered=copy.deepcopy(source['uses']);activation=next(u for u in altered if u['kind']=='activation' and len(u['failure_atoms'])==2)
 activation['failure_atoms'][0]='x3<=x4' if activation['failure_atoms'][0]!='x3<=x4' else 'x2<=x4'
 atom_mutation=reject(lambda:audit_uses(altered,identities),'rejected activation-failure atom mutation')
 strict=reject(lambda:audit_semantics(source['uses'],identities,frozenset()),'rejected removal of strict-target semantics')
 payload={'schema':'strict-exchange-p4-class2-hand-certificate-audit-v1','status':'PASS',
  'scope':'twenty-one exact difference-cone censuses, 108 deduplicated rational identities, exhaustive 132-use map, and all 72 extremal-level activation-failure cases; no solver or production encoder',
  'packet':{'first_optional_players':[],'second_optional_players':[0]},
  'order_tree':['x3<=x4','x3>x4'],
  'identity_counts':counts,'use_counts':{k:sum(u['kind']==k for u in source['uses']) for k in ('blocker','activation')},
  'target_use_counts':targets,'blocker_source_localization':sources,
  'strict_target_semantics':{'d0':'x0-z0 is strictly positive by the original P-sign premise','S-strict':'x4-x3 is strictly negative on the strict root branch'},
  'structural_census':structure,'activation_logic_audit':logic,'use_map_audit':use_audit,'coefficient_mutation_control':coefficient,
  'use_site_mutation_control':use_site,'census_mutation_control':candidate,'use_map_mutation_control':use_delete,
  'activation_atom_mutation_control':atom_mutation,'strict_target_mutation_control':strict,'checked_uses':checked}
 rendered=json.dumps(payload,indent=2,sort_keys=True)+'\n'
 if args.output:args.output.write_text(rendered)
 print(rendered,end='')
if __name__=='__main__':main()
