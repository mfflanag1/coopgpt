#!/usr/bin/env python3
"""Verify the class-10 two-order-split relay using exact rational arithmetic.

This checker imports no solver and no production encoder.  It reconstructs
the affine premises at all 122 certificate uses, recomputes eighteen exact
difference-cone candidate censuses, and audits the complete blocker and
activation use maps.
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
SOURCE=HERE/'strict_exchange_p4_class10_hand_certificate_rows.json'
H12=(1,0,1,0,-1,-1);H17=(0,-1,0,-1,1,1);H9=H14=(0,-1,1,0,0,0)
C0=(3,4);C5=(3,5);C2=(0,1,3);C3=(1,3);D4=(1,2,3,4);D5=(1,2,3,5)

def cfg(orders,branches=(),side=None):return {'orders':tuple(orders),'branches':tuple(branches),'blocker_side':side}
CONFIG={
 'WL-root12':cfg(('W','L'),side='max'),'WL-root12-z0':cfg(('W','L')),'WL-root12-z2':cfg(('W','L')),
 'WL-C0-term17':cfg(('W','L'),(('C0',C0,'max'),),'min'),'WL-C0-h17':cfg(('W','L'),(('C0',C0,'max'),)),
 'WR-root12':cfg(('W','R'),side='max'),'WR-root12-z0':cfg(('W','R')),'WR-root12-z2':cfg(('W','R')),
 'WR-C0-h9':cfg(('W','R'),(('C0',C0,'max'),),'max'),'WR-C5-h9':cfg(('W','R'),(('C5',C5,'max'),),'max'),
 'WR-C0-C3-term':cfg(('W','R'),(('C0',C0,'max'),('C3',C3,'max')),'min'),
 'WR-C0-C2-term':cfg(('W','R'),(('C0',C0,'max'),('C2',C2,'max')),'min'),
 'WR-C5-C3-term':cfg(('W','R'),(('C5',C5,'max'),('C3',C3,'max')),'min'),
 'WR-C5-C2-term':cfg(('W','R'),(('C5',C5,'max'),('C2',C2,'max')),'min'),
 'S-root17':cfg(('S',),side='min'),
 'S-D4-h12':cfg(('S',),(('D4',D4,'min'),),'max'),'S-D5-h12':cfg(('S',),(('D5',D5,'min'),),'max'),
 'S-D4-h12-z0':cfg(('S',),(('D4',D4,'min'),)),'S-D4-h12-z2':cfg(('S',),(('D4',D4,'min'),)),
 'S-D5-h12-z0':cfg(('S',),(('D5',D5,'min'),)),'S-D5-h12-z2':cfg(('S',),(('D5',D5,'min'),)),
 'S-D4-C5-h9':cfg(('S',),(('D4',D4,'min'),('C5',C5,'max')),'max'),
 'S-D5-C0-h9':cfg(('S',),(('D5',D5,'min'),('C0',C0,'max')),'max'),
}
for dn,DB,bn,B in (('D4',D4,'C5',C5),('D5',D5,'C0',C0)):
 for cn,C in (('C3',C3),('C2',C2)):
  CONFIG[f'S-{dn}-{bn}-{cn}-term']=cfg(('S',),((dn,DB,'min'),(bn,B,'max'),(cn,C,'max')),'min')
  CONFIG[f'S-{dn}-{bn}-{cn}-h14']=cfg(('S',),((dn,DB,'min'),(bn,B,'max'),(cn,C,'max')))

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

def named_system(stage,identity):
 if stage not in CONFIG:raise AssertionError(f'unknown stage {stage}')
 config=CONFIG[stage];x=[variable(f'x{i}') for i in range(6)];z=[variable(f'z{i}') for i in range(6)];q=[variable(f'q{i}') for i in range(6)]
 I={}
 for prefix,point in (('x',x),('z',z),('q',q)):
  for i in range(6):I[f'{prefix}{i}>=0']=linear((-1,point[i]))
 for i in range(4):I[f'd{i}>=0']=linear((1,z[i]),(-1,x[i]))
 for i in (4,5):I[f'delta{i}>=0']=linear((1,x[i]),(-1,z[i]))
 for i in range(1,6):I[f'x0<=x{i}']=linear((1,x[0]),(-1,x[i]))
 for i in (0,2,3,4,5):I[f'z{i}<=z1']=linear((1,z[i]),(-1,z[1]))
 for name,C in (('P4',(1,2,4)),('P5',(1,2,5))):comparison(I,name+'o',C,x,z);comparison(I,name+'q',C,x,q)
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
 hypotheses={
  'z4<=z0':linear((1,z[4]),(-1,z[0])),'z5<=z0':linear((1,z[5]),(-1,z[0])),
  'z4<=z2':linear((1,z[4]),(-1,z[2])),'z5<=z2':linear((1,z[5]),(-1,z[2])),
  'x3<=x5':linear((1,x[3]),(-1,x[5])),'z1<=z2':linear((1,z[1]),(-1,z[2])),
  'x1<=x2':linear((1,x[1]),(-1,x[2])),
 }
 for name in identity['inequality_multipliers']:
  if name in hypotheses:I[name]=hypotheses[name]
 E={'sumx':linear((1,point_sum(x,range(6))),(-1,constant(1))),
    'sumz':linear((1,point_sum(z,range(6))),(-1,constant(1))),
    'sumq':linear((1,point_sum(q,range(6))),(-1,constant(1))),'q1':q[1]}
 D=linear((1,point_sum(x,(0,1,2,3))),(-1,point_sum(z,(0,1,2,3))))
 T={'D-1/3':linear((1,D),(-1,constant(Fraction(1,3)))),'d0':linear((1,x[0]),(-1,z[0]))}
 if identity['target'] not in T:raise AssertionError(f"unknown target {identity['target']}")
 return I,E,T[identity['target']]

def verify_use(use,identities):
 if use['identity'] not in identities:raise AssertionError(f"unknown identity {use['identity']}")
 row=identities[use['identity']]
 if use['kind']!=row['kind']:raise AssertionError('kind mismatch')
 if row['kind']=='blocker':
  if tuple(use['coalition'])!=tuple(row['coalition']):raise AssertionError('coalition mismatch')
  if use.get('sources')!=['opposite','q1'] or row.get('sources')!=['opposite','q1']:raise AssertionError('source mismatch')
 I,E,target=named_system(use['stage'],row);terms=[]
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
 rows.extend([((0,1,1,0,-1),Fraction()),((-1,0,0,-1,1),Fraction())])
 for C,side in branches:
  form=d_form(C);rows.append((form if side=='min' else tuple(-v for v in form),Fraction()))
 return rows

T0={(1,4),(1,5),(0,1,4),(0,1,5),(1,3,5),(1,4,5),(0,1,4,5),(1,3,4,5),(0,1,3,4,5)}
T5={(1,4),(1,5),(0,1,4),(0,1,5),(1,3,4),(1,4,5),(0,1,4,5),(1,3,4,5),(0,1,3,4,5)}
TS4={(1,4),(1,5),(0,1,4),(1,3,4),(1,4,5),(0,1,4,5),(1,3,4,5),(0,1,3,4,5)}
TS5={(1,4),(1,5),(0,1,5),(1,3,5),(1,4,5),(0,1,4,5),(1,3,4,5),(0,1,3,4,5)}
STRUCT={
 'WL-root12':(H12,'max',(),{C0,C5,(1,3,4),(1,3,5)}),'WL-C0-term17':(H17,'min',((C0,'max'),),{(1,3,5),(1,2,3,5)}),
 'WR-root12':(H12,'max',(),{C0,C5,(1,3,4),(1,3,5)}),
 'WR-C0-h9':(H9,'max',((C0,'max'),),{(1,),(0,1),C3,C2,(0,1,4),(1,3,4),(1,3,5),(0,1,3,4),(0,1,3,5)}),
 'WR-C5-h9':(H9,'max',((C5,'max'),),{(1,),(0,1),C3,C2,(0,1,5),(1,3,4),(1,3,5),(0,1,3,4),(0,1,3,5)}),
 'WR-C0-C3-term':(H14,'min',((C0,'max'),(C3,'max')),T0),'WR-C0-C2-term':(H14,'min',((C0,'max'),(C2,'max')),T0),
 'WR-C5-C3-term':(H14,'min',((C5,'max'),(C3,'max')),T5),'WR-C5-C2-term':(H14,'min',((C5,'max'),(C2,'max')),T5),
 'S-root17':(H17,'min',(),{(1,3,4),(1,3,5),D4,D5}),
 'S-D4-h12':(H12,'max',((D4,'min'),),{C5,(1,3,5)}),'S-D5-h12':(H12,'max',((D5,'min'),),{C0,(1,3,4)}),
 'S-D4-C5-h9':(H9,'max',((D4,'min'),(C5,'max')),{(1,),(0,1),C3,C2,(0,1,5),(1,3,5),(0,1,3,4),(0,1,3,5)}),
 'S-D5-C0-h9':(H9,'max',((D5,'min'),(C0,'max')),{(1,),(0,1),C3,C2,(0,1,4),(1,3,4),(0,1,3,4),(0,1,3,5)}),
 'S-D4-C5-C3-term':(H14,'min',((D4,'min'),(C5,'max'),(C3,'max')),TS4),
 'S-D4-C5-C2-term':(H14,'min',((D4,'min'),(C5,'max'),(C2,'max')),TS4),
 'S-D5-C0-C3-term':(H14,'min',((D5,'min'),(C0,'max'),(C3,'max')),TS5),
 'S-D5-C0-C2-term':(H14,'min',((D5,'min'),(C0,'max'),(C2,'max')),TS5),
}
SURVIVORS={'WL-root12':{C0},'WL-C0-term17':set(),'WR-root12':{C0,C5},'WR-C0-h9':{C3,C2},'WR-C5-h9':{C3,C2},
 'WR-C0-C3-term':set(),'WR-C0-C2-term':set(),'WR-C5-C3-term':set(),'WR-C5-C2-term':set(),
 'S-root17':{D4,D5},'S-D4-h12':{C5},'S-D5-h12':{C0},'S-D4-C5-h9':{C3,C2},'S-D5-C0-h9':{C3,C2},
 'S-D4-C5-C3-term':set(),'S-D4-C5-C2-term':set(),'S-D5-C0-C3-term':set(),'S-D5-C0-C2-term':set()}
ACTIVATIONS={'WL-root12-z0','WL-root12-z2','WR-root12-z0','WR-root12-z2','WL-C0-h17','WR-C0-h9','WR-C5-h9',
 'S-D4-h12-z0','S-D4-h12-z2','S-D5-h12-z0','S-D5-h12-z2','S-D4-C5-h9','S-D5-C0-h9',
 'S-D4-C5-C3-h14','S-D4-C5-C2-h14','S-D5-C0-C3-h14','S-D5-C0-C2-h14'}

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
 keys=[(u['kind'],u['stage'],tuple(u.get('coalition',()))) for u in uses]
 if len(keys)!=len(set(keys)):raise AssertionError('duplicate use')
 blockers=[u for u in uses if u['kind']=='blocker'];actual={s:{tuple(u['coalition']) for u in blockers if u['stage']==s} for s in SURVIVORS}
 expected={s:STRUCT[s][3]-survivors for s,survivors in SURVIVORS.items()}
 if actual!=expected:raise AssertionError(f'blocker use map incomplete: {actual}')
 acts=[u['stage'] for u in uses if u['kind']=='activation']
 if set(acts)!=ACTIVATIONS or len(acts)!=17:raise AssertionError(f'activation use map changed: {acts}')
 if {u['identity'] for u in uses}!=set(identities):raise AssertionError('orphan identity')
 return {'blocker_uses_by_stage':{s:len(v) for s,v in expected.items()},'activation_stages':sorted(acts)}

def audit_semantics(uses,identities,strict=frozenset({'d0'})):
 counts={'D-1/3':0,'d0':0};sources={'q1_only':0,'opposite_only':0,'both':0}
 for use in uses:
  row=identities[use['identity']];target=row['target'];counts[target]+=1
  if target=='d0' and 'd0' not in strict:raise AssertionError('d0 lacks strict P-sign semantics')
  if row['kind']=='blocker':
   co='Co' in row['inequality_multipliers'];cq='Cq' in row['inequality_multipliers']
   sources['both' if co and cq else 'opposite_only' if co else 'q1_only' if cq else 'both']+=1
   if not (co or cq):raise AssertionError('blocker certificate uses neither source comparison')
 if counts!={'D-1/3':116,'d0':6}:raise AssertionError(f'target counts changed: {counts}')
 if sources!={'q1_only':103,'opposite_only':2,'both':0}:raise AssertionError(f'source localization changed: {sources}')
 return counts,sources

def reject(fn,label):
 try:fn()
 except AssertionError:return label
 raise AssertionError(f'mutation passed: {label}')
def signature(row):return (row['kind'],row['target'],tuple(row.get('coalition',())),tuple(sorted(row['inequality_multipliers'].items())),tuple(sorted(row['equality_multipliers'].items())))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=SOURCE);parser.add_argument('--output',type=Path);args=parser.parse_args()
 source=json.loads(args.source.read_text())
 if source.get('schema')!='strict-exchange-p4-class10-hand-certificate-rows-v1' or source.get('status')!='FROZEN_PROOF_OBJECT':raise AssertionError('unexpected proof object')
 identities={row['id']:row for row in source['identities']}
 if len(identities)!=len(source['identities']) or len({signature(r) for r in identities.values()})!=len(identities):raise AssertionError('identity ids are not deduplicated')
 counts={k:sum(r['kind']==k for r in identities.values()) for k in ('blocker','activation')}
 if counts!={'blocker':95,'activation':13}:raise AssertionError(f'identity counts changed: {counts}')
 structure=census();use_audit=audit_uses(source['uses'],identities);targets,sources=audit_semantics(source['uses'],identities)
 checked=[verify_use(use,identities) for use in source['uses']]
 bad=copy.deepcopy(identities);first=bad[source['uses'][0]['identity']];premise=next(iter(first['inequality_multipliers']));first['inequality_multipliers'][premise]=str(Fraction(first['inequality_multipliers'][premise])+1)
 coefficient=reject(lambda:verify_use(source['uses'][0],bad),'rejected coefficient perturbation')
 displaced=next(copy.deepcopy(u) for u in source['uses'] if u['kind']=='blocker' and u['stage']=='S-D4-C5-h9');displaced['stage']='WL-root12'
 use_site=reject(lambda:verify_use(displaced,identities),'rejected identity at stage lacking branch premises')
 expected=set(STRUCT['WL-root12'][3]);expected.remove(next(iter(expected)))
 candidate=reject(lambda:census({'WL-root12':expected}),'rejected candidate deletion')
 use_delete=reject(lambda:audit_uses(source['uses'][1:],identities),'rejected use-map deletion')
 strict=reject(lambda:audit_semantics(source['uses'],identities,frozenset()),'rejected removal of strict-target semantics')
 payload={'schema':'strict-exchange-p4-class10-hand-certificate-audit-v1','status':'PASS',
  'scope':'eighteen exact difference-cone censuses, 108 deduplicated rational identities, and exhaustive 122-use map; no solver or production encoder',
  'packet':{'first_optional_players':[2],'second_optional_players':[2]},
  'order_tree':['x3<=x4 and x1<=x2','x3<=x4 and x1>x2','x3>x4'],
  'identity_counts':counts,'use_counts':{k:sum(u['kind']==k for u in source['uses']) for k in ('blocker','activation')},
  'target_use_counts':targets,'blocker_source_localization':sources,'strict_target_semantics':{'d0':'strictly positive by the original P-sign premise'},
  'structural_census':structure,'use_map_audit':use_audit,'coefficient_mutation_control':coefficient,
  'use_site_mutation_control':use_site,'census_mutation_control':candidate,'use_map_mutation_control':use_delete,
  'strict_target_mutation_control':strict,'checked_uses':checked}
 rendered=json.dumps(payload,indent=2,sort_keys=True)+'\n'
 if args.output:args.output.write_text(rendered)
 print(rendered,end='')
if __name__=='__main__':main()
