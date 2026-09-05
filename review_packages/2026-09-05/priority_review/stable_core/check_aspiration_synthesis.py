from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json
import hashlib
P=Path(__file__).parent

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def run():
    N=range(6)
    coal=[tuple(c) for k in range(1,7) for c in combinations(N,k)]
    U=tuple(map(F,[0,1,0,1,2,0]))
    V=tuple(map(F,[1,0,1,0,0,2]))
    a=tuple(map(F,['1/2','1/2','1','1/2','1/2','3/2']))
    shift=tuple(F(3,2)-x for x in a)
    def su(x,S):return sum((x[i] for i in S),F(0))
    def w(S):return min(su(U,S),su(V,S))
    slack={S:su(a,S)-w(S) for S in coal}
    require(min(slack.values())>=0, "exact aspiration condition")
    tight=[S for S in coal if slack[S]==0]
    require(set().union(*map(set,tight))==set(N), "exact aspiration condition")
    require(su(a,N)>w(N), "exact aspiration condition")
    A=tuple(U[i]+shift[i] for i in N)
    B=tuple(V[i]+shift[i] for i in N)
    def q(S):return w(S)+su(shift,S)
    maxoffers=[max(q(S)/len(S) for S in coal if i in S) for i in N]
    require(maxoffers==[F(3,2)]*6, "exact aspiration condition")
    admissible=[S for S in coal if all(q(S)/len(S)==maxoffers[i] for i in S)]
    require(set().union(*map(set,admissible))==set(N), "exact aspiration condition")
    require(q(tuple(N))==F(17,2), "exact aspiration condition")
    require(all(q(tuple(sorted(S+(i,))))>=q(S) for S in [()]+coal for i in N if i not in S), "exact aspiration condition")
    require(all(q(tuple(sorted(S+T)))>=q(S)+q(T) for S in [()]+coal for T in [()]+coal if not set(S)&set(T)), "exact aspiration condition")
    # No point (1-t)U+tV is below a: player5 forces t>=3/4, player1 t<=1/2.
    require((U[4]-a[4])/(U[4]-V[4]) == F(3,4), "exact aspiration condition")
    require(a[0]/V[0] == F(1,2), "exact aspiration condition")
    out=dict(date="2026-09-05",definition="q=w-a+3/2 per player; not the manuscript ray",
    base_endpoints=[list(map(str,U)),list(map(str,V))],minimal_upper_core_a=list(map(str,a)),
    upper_core_grand_slack=str(su(a,N)-w(N)),all_nonempty_coalitions_checked=len(coal),
    tight_coalitions=["".join(str(i+1) for i in S) for S in tight],
    nonlarge_witness="Any core point below a would require t>=3/4 (player5) and t<=1/2 (player1).",
    additive_shift=list(map(str,shift)),new_endpoints=[list(map(str,A)),list(map(str,B))],
    first_round_claims=list(map(str,maxoffers)),terminal_in_one_round=True,grand_worth=str(q(tuple(N))),claims_excess=str(sum(maxoffers)-q(tuple(N))),
    monotone=True,superadditive=True,
    logic="Core stability/exactness inherited from the classical segment by relabeling and additive translation; the script checks only explicit aspiration/PES arithmetic and inequalities, not external stability.")
    return out

if __name__ == '__main__':
    path = P/'aspiration_synthesis_check.json'
    result = {'status':'RUNNING','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    path.write_text(json.dumps(result,indent=2)+'\n')
    try:
        result.update(run())
        result['status']='PASS'
    except Exception as exc:
        result.update(status='FAIL',error=repr(exc))
        raise
    finally:
        path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
