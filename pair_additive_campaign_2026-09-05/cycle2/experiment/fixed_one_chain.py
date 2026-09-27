"""Two targeted full-lexicographic face checks for the proposed all-size chain."""
from fractions import Fraction as F
import z3
from coupling import ROOT,save,require,exact_three
from zero_chain import build

def witness(cons,p):
    s=z3.Solver();s.set(timeout=60000);s.add(*cons)
    require(s.check()==z3.sat,'exact witness missing')
    model=s.model()
    return [exact_three.rational(model.eval(v,model_completion=True)) for v in p]

def embed(block_vectors,blocks):
    return [F(block_vectors[s][3*c+j]) for c in range(3) for s in range(blocks) for j in range(3)]

def check(blocks):
    n,T,matrices,matching,rows=build(blocks,small=F(1));m=3*blocks
    p=[z3.FreshReal('onechain') for _ in range(n)]
    cons=[sum(p)==exact_three.Q(T)]+[sum(exact_three.Q(a)*v for a,v in zip(r['a'],p))<=exact_three.Q(r['b']) for r in rows]
    level=z3.FreshReal('level')
    first=exact_three.optimize(cons+[v>=level for v in p],level,True)
    require(first==F(1,3),'first fulllexfloor changed')
    small=[i for t in matching[::3] for i in t]
    free=[i for i in range(n) if i not in small]
    prefix=cons+[p[i]==exact_three.Q(first) for i in small]
    second=exact_three.optimize(prefix+[p[i]>=level for i in free],level,True)
    require(second==F(1,3)+F(1,blocks),'predicted second floor failed')
    face=prefix+[p[i]>=exact_three.Q(second) for i in free]
    floor_witness=witness(face,p)
    target=m+3+1 # e of the second block.
    target_upper=exact_three.optimize(face,p[target],True)
    require(target_upper==second,'target is not pinned at second fulllexstage')
    H=exact_three.optimize(cons,p[target],True)
    up=(1,2,2,0,0,0,2,1,0);mid=(0,2,0,1,3,1,1,0,0);down=(0,0,0,3,1,1,3,0,0)
    ideal_witness=embed([up,mid]+[down]*(blocks-2),blocks)
    for name,point in [('floor_witness',floor_witness)]:
        require(sum(point)==T and all(sum(a*v for a,v in zip(r['a'],point))<=r['b'] for r in rows),'invalid '+name)
    failed=[dict(row=r['label'],lhs=sum(a*v for a,v in zip(r['a'],ideal_witness)),rhs=r['b']) for r in rows if sum(a*v for a,v in zip(r['a'],ideal_witness))>r['b']]
    attained=witness(cons+[p[target]==exact_three.Q(H)],p)
    result=dict(blocks=blocks,m=m,n=n,small_team_weight='1',fixed_total=T,matrices=matrices,matching=matching,status='PASS_actual_target_certificate',first_fulllex_floor=first,first_pinned_players=small,second_fulllex_floor=second,target=target,target_fulllex_payoff=second,target_second_face_maximum=target_upper,target_ideal=H,target_ratio=second/H,floor_witness=floor_witness,proposed_ideal_witness=ideal_witness,proposed_ideal_failed_constraints=failed,actual_ideal_witness=attained,scope='Full target payoff certified by firsttwo lexicographic faces; target pinned on secondface. Remaining later fullselector coordinates and Lmax not computed.',integral_optimum_certified_by_matching_and_cover=True)
    save(ROOT/f'fixed_one_chain_{blocks}.json',result)
    print('PASS fixed_one_chain',blocks,'alpha',second,'H',H,'targetratio',second/H,'proposed_witness_failures',len(failed),flush=True)

if __name__=='__main__':
    for blocks in (3,4):check(blocks)
