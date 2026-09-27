"""Prove that every optimal subsidy dual contains a two-cycle support."""
from pathlib import Path
from fractions import Fraction as Q
import json
from verify_cyclic_frontier import full_market, geometry, require


def forced_step(player, expected, available, teams, covered, y, ideals):
    require(player not in covered and y[player] > ideals[player]/3, 'forcing player is not strictly protected')
    choices=[k for k in available if player in teams[k][0]]
    require(len(choices) == 1 and teams[choices[0]][0] == expected, 'team is not uniquely forced')
    row=choices[0];new=set(expected)
    return row, {k for k in available if not new.intersection(teams[k][0])}, covered | new


def run():
    records=json.loads(Path(__file__).with_name('CYCLIC_FRONTIER_CERTIFICATES.json').read_text())
    rec=next(r for r in records if r['name']=='CYCLIC_FRONTIER_6_2_0')
    d=rec['full_market'];verified=full_market(d,rec['pattern']);m=d['m'];n=3*m
    require(m==11 and verified['exact_witness_market_subsidy']=='76/303','market inventory')
    weights=list(map(Q,d['weights']));ideals=list(map(Q,d['H']));y=list(map(Q,d['protected_y']))
    edges,lookup,_=geometry(m,d['P'])
    diagonal_table=[[108,234,144],[252,144,90],[144,198,198],[90,108,108],[154,144,148],[108,234,144],[153,153,144],[189,144,153],[144,144,198],[198,144,198],[198,144,198]]
    team_table=[[252,288,252],[158,144,234],[252,198,108],[153,297,153],[288,234,306],[333,198,342]]
    require([[weights[lookup[(s,j,j)]]*5252 for s in range(3)]for j in range(m)]==diagonal_table,'diagonal table mismatch')
    require([[weights[lookup[e]]*5252 for e in ((0,a,b),(1,a,c),(2,b,c))]for a,b,c in d['P']]==team_table,'team table mismatch')
    _,_,teams=geometry(m,d['P']);values=[sum(weights[e]for e in es)for _,es in teams]
    xs=[list(map(Q,x))for x in d['core_witnesses']]
    interior=[sum(x[i]for x in xs)/n for i in range(n)]
    require(min(interior)>0,'averaged original core has a zero coordinate')
    original_tight=[team for (team,_),v in zip(teams,values)if sum(interior[i]for i in team)==v]
    require(set(original_tight)=={(j,m+j,2*m+j)for j in range(m)}|{(1,m,2*m+2),(7,m+10,2*m+8)},'original tight-team list')
    witnesses=[]
    for label in range(m):
        diagonal=(label,m+label,2*m+label)
        require(diagonal in original_tight,'diagonal not tight')
        unique=[s for s in range(3)if [t for t in original_tight if s*m+label in t]==[diagonal]]
        require(unique,'diagonal team not uniquely forced in original optimum')
        witnesses.append([label,unique[0]])
    # Every original optimum must cover every positive-payoff player and can
    # only use teams tight at the averaged original core point. Each diagonal
    # has a player occurring in no other such team, forcing all diagonals.
    require(min(y)>0,'protected payoff has zero coordinate')
    available={k for k,((team,_),v)in enumerate(zip(teams,values))if sum(y[i]for i in team)==v}
    tight_count=len(available);covered=set();forced=[]
    trace=[(0,(0,5,3)),(1,(1,0,2)),(20,(8,9,5)),(21,(7,10,8)),(23,(3,4,1)),(29,(6,3,7))]
    for player,labels in trace:
        expected=tuple(s*m+j for s,j in enumerate(labels))
        row,available,covered=forced_step(player,expected,available,teams,covered,y,ideals)
        forced.append(list(labels))
    require(sorted(forced)==sorted(d['P']),'not all P teams forced')
    parent=list(range(m+len(forced)));rank=0
    def find(j):
        while parent[j]!=j:
            parent[j]=parent[parent[j]];j=parent[j]
        return j
    for k,t in enumerate(forced):
        for label in t:
            a,b=find(label),find(m+k)
            if a==b:rank+=1
            else:parent[a]=b
    require(rank==2,'forced incidence support is not bicyclic')
    try:forced_step(0,(1,m,2*m+2),{k for k,((t,_),v)in enumerate(zip(teams,values))if sum(y[i]for i in t)==v},teams,set(),y,ideals)
    except ValueError:pass
    else:raise ValueError('false forcing step accepted')
    print(json.dumps({'status':'PASS','m':m,'exact_subsidy':d['subsidy'],'original_optimal_matching':'unique diagonal','diagonal_forcing_players':witnesses,'protected_tight_teams':tight_count,'forced_dual_teams':forced,'forced_cycle_rank':rank,'negative_controls':1,'scope':'every optimal team-form subsidy dual has these teams with multiplier one; no forest-supported optimum on this market'}))

if __name__=='__main__':run()
