"""Exact bounded GPU placement by dynamic programming; two explicit greedy baselines.

The DP considers each job deferred or on every eligible node/GPU subset. Its
state records all remaining shared resources, so feasible continuations depend
only on that state. Lexicographic additive objectives preserve optimal substructure.
Search is exponential; this is a small-instance reference, not a scalable scheduler.
"""
from functools import lru_cache
from itertools import combinations
from verifier import validate_manifest,verify_plan


class InvalidProducedPlan(RuntimeError):
    """Preserve a rejected producer output for the caller's failure record."""
    def __init__(self, plan, verification):
        super().__init__('Solver emitted invalid plan: ' + str(verification['errors']))
        self.plan = plan
        self.verification = verification


def _prepare(manifest):
    validate_manifest(manifest)
    nodes=sorted(manifest['nodes'],key=lambda n:n['id'])
    jobs=sorted(manifest['jobs'],key=lambda j:j['id'])
    gpu_ids=sorted(g['id'] for n in nodes for g in n['gpus'])
    bit={g:1<<i for i,g in enumerate(gpu_ids)}
    options={}
    for j in jobs:
        choices=[]
        for ni,n in enumerate(nodes):
            if n['owner'] not in j['allowed_owners'] or j['cpu_units']>n['cpu_units'] or j['ram_mib']>n['ram_mib']:continue
            for family in sorted(set(j['allowed_families'])):
                eligible=sorted(g['id'] for g in n['gpus'] if g['family']==family and g['vram_mib']>=j['min_vram_mib'])
                for gs in combinations(eligible,j['gpu_count']):choices.append((ni,gs,sum(bit[g] for g in gs)))
        options[j['id']]=choices
    state=((1<<len(gpu_ids))-1,tuple(n['cpu_units'] for n in nodes),tuple(n['ram_mib'] for n in nodes))
    return nodes,jobs,options,state


def _consume(state,job,choice):
    free,cpu,ram=state;ni,gs,mask=choice
    if free&mask!=mask or cpu[ni]<job['cpu_units'] or ram[ni]<job['ram_mib']:return None
    c=list(cpu);r=list(ram);c[ni]-=job['cpu_units'];r[ni]-=job['ram_mib']
    return free^mask,tuple(c),tuple(r)


def _plan(manifest,nodes,placements):
    used={x[0] for x in placements}
    result={'schema_version':1,'placements':[{'job':j,'node':nodes[ni]['id'],'gpus':list(gs)} for j,ni,gs in sorted(placements)],'deferred':sorted(j['id'] for j in manifest['jobs'] if j['id'] not in used)}
    checked=verify_plan(manifest,result)
    if not checked['valid']:raise InvalidProducedPlan(result, checked)
    return result


def solve(manifest):
    nodes,jobs,options,initial=_prepare(manifest)
    @lru_cache(None)
    def visit(index,free,cpu,ram):
        if index==len(jobs):return (0,0),()
        job=jobs[index];best,placements=visit(index+1,free,cpu,ram)
        for choice in options[job['id']]:
            nxt=_consume((free,cpu,ram),job,choice)
            if nxt is None:continue
            value,rest=visit(index+1,*nxt);candidate=(value[0]+job['priority'],value[1]+1)
            if candidate>best:best,placements=candidate,((job['id'],choice[0],choice[1]),)+rest
        return best,placements
    _,placements=visit(0,*initial)
    return _plan(manifest,nodes,placements)


def greedy(manifest,strategy='priority_first'):
    nodes,jobs,options,state=_prepare(manifest)
    if strategy=='priority_first':jobs.sort(key=lambda j:(-j['priority'],j['id']))
    elif strategy=='scarcity_first':jobs.sort(key=lambda j:(len(options[j['id']]),-j['priority'],j['id']))
    else:raise ValueError('Unknown strategy')
    placements=[]
    for job in jobs:
        for choice in options[job['id']]:
            nxt=_consume(state,job,choice)
            if nxt is not None:
                placements.append((job['id'],choice[0],choice[1]));state=nxt;break
    return _plan(manifest,nodes,placements)
