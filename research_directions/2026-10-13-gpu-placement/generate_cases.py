"""Prospective synthetic stress suite; no measured hardware or sampled job trace."""
from pathlib import Path
import hashlib,json

class Draw:
    def __init__(self,seed):self.seed=seed;self.index=0
    def pick(self,values):
        b=hashlib.sha256(f'coop-gpu-placement-v1:{self.seed}:{self.index}'.encode()).digest();self.index+=1
        return values[int.from_bytes(b,'big')%len(values)]

def gpu(i,family='A',vram=16384):return dict(id=i,family=family,vram_mib=vram)
def node(i,owner='o1',cpu=8,ram=32768,gpus=None):return dict(id=i,owner=owner,cpu_units=cpu,ram_mib=ram,gpus=[gpu(i+'_g0')] if gpus is None else gpus)
def job(i,priority=1,cpu=1,ram=1024,count=1,vram=16384,families=None,owners=None):return dict(id=i,priority=priority,cpu_units=cpu,ram_mib=ram,gpu_count=count,min_vram_mib=vram,allowed_families=['A','B'] if families is None else families,allowed_owners=['o1','o2'] if owners is None else owners)
def case(name,nodes,jobs,kind='constructed'):return dict(case_id=name,kind=kind,manifest=dict(schema_version=1,nodes=nodes,jobs=jobs))

def make_cases():
    cases=[
      case('empty_queue',[node('n1')],[]),
      case('no_free_gpus',[node('n1',gpus=[])],[job('j1')]),
      case('vram_cannot_pool',[node('n1',gpus=[gpu('g1'),gpu('g2')])],[job('j1',count=1,vram=32768)]),
      case('gang_cannot_cross_nodes',[node('n1'),node('n2')],[job('j1',count=2)]),
      case('gang_cannot_mix_families',[node('n1',gpus=[gpu('g1','A'),gpu('g2','B')])],[job('j1',count=2)]),
      case('owner_permission_blocks',[node('n1','o2')],[job('j1',owners=['o1'])]),
      case('one_cpu_bottleneck',[node('n1',cpu=1,gpus=[gpu('g1'),gpu('g2')])],[job('j1',priority=2),job('j2',priority=3)]),
      case('one_ram_bottleneck',[node('n1',ram=1024,gpus=[gpu('g1'),gpu('g2')])],[job('j1',priority=2),job('j2',priority=3)]),
      case('priority_tie_more_jobs',[node('n1',gpus=[gpu('g1'),gpu('g2')])],[job('j1',priority=4,count=2),job('j2',priority=2),job('j3',priority=2)]),
      case('priority_first_gang_trap',[node('n1',gpus=[gpu('g1'),gpu('g2')])],[job('j1',priority=5,count=2),job('j2',priority=3),job('j3',priority=3)]),
      case('scarce_memory_placement',[node('n1',gpus=[gpu('g1',vram=32768)]),node('n2')],[job('j1',priority=6),job('j2',priority=5,vram=32768)]),
      case('exact_cpu_ram_fit',[node('n1',cpu=2,ram=2048,gpus=[gpu('g1'),gpu('g2')])],[job('j1'),job('j2')])]
    for seed in range(128):
        r=Draw(seed);nodes=[];total=0
        for ni in range(r.pick([1,2,3])):
            k=r.pick([1,2,3]);k=min(k,8-total);total+=k
            gs=[gpu(f'n{ni}_g{gi}',r.pick(['A','B']),r.pick([8192,16384,32768,49152])) for gi in range(k)]
            nodes.append(node(f'n{ni}',r.pick(['o1','o2']),r.pick([2,4,8,16]),r.pick([4096,8192,16384,32768]),gs))
        jobs=[]
        for ji in range(r.pick([4,5,6,7,8])):
            jobs.append(job(f'j{ji}',r.pick([1,2,3,5,8,13]),r.pick([1,2,4,8]),r.pick([1024,2048,4096,8192,16384]),r.pick([1,1,1,2,2,3]),r.pick([8192,16384,32768,49152]),r.pick([['A'],['B'],['A','B']]),r.pick([['o1'],['o2'],['o1','o2']])))
        cases.append(case('seed_'+str(seed).zfill(3),nodes,jobs,'generated'))
    return cases
if __name__=='__main__':Path(__file__).with_name('cases.json').write_text(json.dumps(make_cases(),indent=2,sort_keys=True)+'\n')
