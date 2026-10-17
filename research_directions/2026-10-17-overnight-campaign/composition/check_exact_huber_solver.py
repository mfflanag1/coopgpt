#!/usr/bin/env python3
"""Independent regression against frozen enumerator certificates plus exact stress."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json
import random
import time

HERE=Path(__file__).resolve().parent
def load(name,filename):
    spec=importlib.util.spec_from_file_location(name,HERE/filename)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
solver=load('new_exact_huber','exact_huber_solver.py')
old_checker=load('old_exact_kkt','verify_huber_kkt.py')
enumerator=load('old_huber_enumerator','verify_huber_price.py')

def require(condition,message):
    if not condition:raise RuntimeError(message)

start=time.monotonic()
frozen=json.loads((HERE/'HUBER_KKT_CERTIFICATES.json').read_text())['certificates']
rows=[];calls=0;maxbits=0
for old in frozen:
    c=list(map(Q,old['capacities']));edges=list(map(tuple,old['edges']))
    cert=solver.certificate(c,edges)
    require(tuple(cert['p'])==tuple(map(Q,old['p'])),'frozen independent-enumerator price mismatch')
    old_checker.verify(cert)
    rows.append(cert);calls+=cert['maxflow_calls'];maxbits=max(maxbits,cert['integerized_capacity_bits'])

rng=random.Random(320261017)
fresh_enum=0
for n in range(2,8):
    for trial in range(12):
        edges=[(u,v) for u in range(n) for v in range(u+1,n) if rng.random()<.35]
        c=[Q(rng.randrange(10),rng.randrange(1,6)) for v in range(n)]
        cert=solver.certificate(c,edges)
        expected=enumerator.price(tuple(c),tuple(edges))
        require(tuple(cert['p'])==tuple(expected),'fresh exact enumerator mismatch')
        old_checker.verify(cert)
        rows.append(cert);fresh_enum+=1;calls+=cert['maxflow_calls'];maxbits=max(maxbits,cert['integerized_capacity_bits'])

large=[]
for n in [20,40,80]:
    edges=[(u,v) for u in range(n) for v in range(u+1,n) if rng.random()<min(.15,4/n)]
    c=[Q(rng.randrange(0,40),rng.randrange(1,8)) for v in range(n)]
    cert=solver.certificate(c,edges);old_checker.verify(cert)
    rows.append(cert);calls+=cert['maxflow_calls'];maxbits=max(maxbits,cert['integerized_capacity_bits'])
    large.append({'vertices':n,'edges':len(edges),'maxflow_calls':cert['maxflow_calls']})

primes=[101,103,107,109,113,127,131]
for shift in range(3):
    n=7;edges=[(v,(v+1)%n) for v in range(n)]
    c=[Q((v+2)**(shift+1),primes[v]) for v in range(n)]
    cert=solver.certificate(c,edges);old_checker.verify(cert)
    require(tuple(cert['p'])==tuple(enumerator.price(tuple(c),tuple(edges))),'high-bit exact enumerator mismatch')
    rows.append(cert);fresh_enum+=1;calls+=cert['maxflow_calls'];maxbits=max(maxbits,cert['integerized_capacity_bits'])

packet={'status':'PASS','arithmetic':'exact rational/integer; no floating point',
        'frozen_independent_enumerator_matches':len(frozen),'fresh_independent_enumerator_matches':fresh_enum,
        'certificate_count':len(rows),'total_density_maxflow_calls':calls,
        'largest_integerized_capacity_sum_bits':maxbits,'larger_graphs':large,
        'seconds':time.monotonic()-start,'certificates':rows}
(HERE/'EXACT_HUBER_SOLVER_CERTIFICATES.json').write_text(json.dumps(packet,default=str,indent=2))
print(json.dumps({k:v for k,v in packet.items() if k!='certificates'},default=str,indent=2))
