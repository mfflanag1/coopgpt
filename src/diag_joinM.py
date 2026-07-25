"""Diagnostic: for exact base b with exact single-bump arms {(S_j,d_j)}, test whether
the pointwise-MAX game M (all arms bumped simultaneously) is balanced. If M is
balanced, the family is feasible (common core point of M works). Counts how often
M is UNbalanced for pairs/triples of exact arms -- the only route to infeasibility.
"""
import random, sys
from fractions import Fraction as F
from itertools import combinations
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from hunt_sd import exactify, is_exact_game

def bumpg(g, bumps):
    v=list(g.v)
    for S,d in bumps: v[S]+=d
    return Game(4,v)

def run(trials, seed, dmax=2):
    rng=random.Random(seed)
    bases=0; pairM_unbal=0; pairs=0; triM_unbal=0; tris=0
    pairM_unbal_but_membersExact=0
    for t in range(trials):
        g=rand_game(4,rng,"general")
        if not is_balanced_game(g): continue
        base=exactify(g)
        if base is None: continue
        arms=[]
        for S in range(1,15):
            for d in range(1,dmax+1):
                if is_exact_game(bumpg(base,[(S,d)])): arms.append((S,d)); break
        if len(arms)<2: continue
        bases+=1
        for a,b in combinations(arms,2):
            pairs+=1
            M=bumpg(base,[a,b])
            if not is_balanced_game(M):
                pairM_unbal+=1
        for a,b,c in combinations(arms,3):
            tris+=1
            M=bumpg(base,[a,b,c])
            if not is_balanced_game(M):
                triM_unbal+=1
        if bases and bases%50==0:
            print(f"[t={t}] bases={bases} pairs={pairs} pairM_unbal={pairM_unbal} "
                  f"tris={tris} triM_unbal={triM_unbal}", flush=True)
        if bases>=400: break
    print(f"FINAL bases={bases} pairs={pairs} pairM_unbal={pairM_unbal} "
          f"tris={tris} triM_unbal={triM_unbal}", flush=True)

if __name__=="__main__":
    run(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv)>2 else 1)
