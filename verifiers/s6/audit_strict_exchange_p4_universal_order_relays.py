#!/usr/bin/env python3
"""Close all eleven p4 packet classes after one universal payoff-order split.

The root split is x3<=x4 versus x3>x4.  Ten packet classes close directly
under the ordinary forced-relay rule.  Class 10 alone needs the additional
exhaustive split x1<=x2 versus x1>x2 on the weak root branch.

This audit shares the parent encoding.  It is a structural decomposition and
humanization roadmap, not independent theorem evidence or a hand proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import z3

from audit_strict_exchange_p4_anchor_core import selected_implications, source_row
from audit_strict_exchange_p4_packet_classes import packet_constraints
from audit_strict_exchange_p4_relay_trees import relay_tree, tree_summary, verdict

HERE=Path(__file__).resolve().parent

def checked_tree(common,order,core,implications,metadata,timeout_ms):
 status=verdict([*common,order],timeout_ms)
 if status==z3.unsat:
  return {'base_with_order_verdict':'unsat','summary':{'open_leaves':0,'closed_leaves':1,'maximum_depth':0},
          'tree':{'depth':0,'status':'closed','reason':'order region is linearly infeasible'}}
 if status!=z3.sat:raise AssertionError(f'order region is unresolved: {status}')
 tree=relay_tree([*common,order],core,implications,metadata,timeout_ms)
 return {'base_with_order_verdict':'sat','summary':tree_summary(tree),'tree':tree}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);parser.add_argument('--timeout-ms',type=int,default=300_000);args=parser.parse_args()
 base,canonical,implications,metadata=selected_implications(source_row())
 packet=json.loads((HERE/'strict_exchange_p4_packet_classes.json').read_text())
 x=[z3.Real(f'equality_exchange_x_{i}') for i in range(6)]
 z=[z3.Real(f'equality_exchange_z_{i}') for i in range(6)]
 q=[z3.Real(f'equality_exchange_q_1_{i}') for i in range(6)]
 rows=[]
 for item in packet['classes']:
  class_id=item['class'];first=tuple(item['first_optional_players']);second=tuple(item['second_optional_players'])
  common=[*base,*canonical,*packet_constraints(x,z,q,first,second)]
  core=[entry['direction_index'] for entry in item['subset_minimal_core']]
  strict=checked_tree(common,x[3]>x[4],core,implications,metadata,args.timeout_ms)
  weak=checked_tree(common,x[3]<=x[4],core,implications,metadata,args.timeout_ms)
  nested=None
  if class_id==10:
   if weak['summary']['open_leaves']==0:
    raise AssertionError(f'class-10 nested split became redundant: {weak["summary"]}')
   nested={}
   for label,order in (('x1<=x2',x[1]<=x[2]),('x1>x2',x[1]>x[2])):
    nested[label]=checked_tree([*common,x[3]<=x[4]],order,core,implications,metadata,args.timeout_ms)
   if any(branch['summary']['open_leaves'] for branch in nested.values()):
    raise AssertionError('class-10 nested region remained open')
  elif weak['summary']['open_leaves']:
   raise AssertionError(f'class {class_id} weak branch remained open: {weak["summary"]}')
  if strict['summary']['open_leaves']:
   raise AssertionError(f'class {class_id} strict branch remained open: {strict["summary"]}')
  effective_weak_closed=(sum(branch['summary']['closed_leaves'] for branch in nested.values()) if nested else weak['summary']['closed_leaves'])
  rows.append({'class':class_id,'raw_orbit_size':item['raw_orbit_size'],
   'packet':{'first_optional_players':list(first),'second_optional_players':list(second)},
   'core_direction_indices':core,'root_order_split':'x3<=x4 versus x3>x4',
   'weak_branch':weak,'strict_branch':strict,
   **({'weak_branch_nested_split':{'order_split':'x1<=x2 versus x1>x2','branches':nested}} if nested else {}),
   'effective_closed_leaf_count':strict['summary']['closed_leaves']+effective_weak_closed,
   'complete_after_order_refinement':True})
 if [row['class'] for row in rows]!=list(range(1,12)):raise AssertionError('packet class order changed')
 if sum(row['raw_orbit_size'] for row in rows)!=32:raise AssertionError('packet orbit coverage changed')
 payload={'schema':'strict-exchange-p4-universal-order-relays-v1','status':'PASS',
  'scope':'machine-checked relay decomposition of all eleven packet classes after the universal x3/x4 split and one class-10 nested split; shares the parent encoding and is not independent theorem evidence',
  'universal_root_order_split':'x3<=x4 versus x3>x4','unique_nested_exception':{'class':10,'weak_branch_split':'x1<=x2 versus x1>x2'},
  'complete_packet_classes':list(range(1,12)),'complete_labelled_packet_count':32,
  'class_count':len(rows),'rows':rows}
 rendered=json.dumps(payload,indent=2,sort_keys=True)+'\n'
 if args.output:args.output.write_text(rendered)
 print(rendered,end='')
if __name__=='__main__':main()
