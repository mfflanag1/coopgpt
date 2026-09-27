"""Independent raw-array corroboration using integer arithmetic only.

The all-size conclusion rests on the conventional proof. This checks selected
sizes, every raw triple, and the exact inequality identities used by that proof.
"""
from itertools import product
from fractions import Fraction
import json


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def raw_arrays(q):
    m = 3*q
    mats = [[[0]*m for _ in range(m)] for _ in range(3)]
    # Sparse entries are transcribed independently from the family statement.
    entries = ((0,1,0,2), (0,1,2,1), (0,2,1,1),
               (1,0,2,1), (1,1,0,1), (2,0,1,1),
               (2,1,0,3), (2,2,0,2))
    for s in range(q):
        for a,i,j,w in entries:
            mats[a][3*s+i][3*s+j] = w
    for s in range(q-1):
        mats[0][3*s+2][3*(s+1)] = 2
    A,B,C = mats
    triples = [(i,m+j,2*m+k,A[i][j]+B[i][k]+C[j][k])
               for i,j,k in product(range(m),repeat=3)]
    require(sum(v>0 for M in mats for row in M for v in row) == 9*q-1,
            'positive pair count')
    require(max(t[3] for t in triples) == 4, 'maximum triple value')
    return m, triples


def player(q,s,letter):
    sector,offset = divmod('abcdefghi'.index(letter),3)
    return sector*(3*q)+3*s+offset


def flatten(q,blocks):
    return [blocks[s][3*r+j] for r in range(3)
            for s in range(q) for j in range(3)]


def floor_cover(q):
    # Denominator 6q: no floating or symbolic optimizer is involved.
    blocks = [(2*q,10*q,8*q,4*q,4*q,2*q,12*q,4*q,2*q)]
    for s in range(1,q):
        blocks.append((2*q,8*q-6*s+6,8*q-6*s,
                       5*q+3*s-3,2*q+6,2*q,
                       14*q+6*s-6,5*q+3*s-3,2*q))
    return flatten(q,blocks), 6*q


def ideal_cover(q,target):
    P=(0,1,1,1,1,1,2,1,0)
    E=(0,1,0,1,2,1,2,1,0)
    D=(0,0,0,2,1,1,3,1,0)
    return flatten(q,[P if s<target else E if s==target else D
                      for s in range(q)])


def vector(q,terms):
    row=[0]*(9*q)
    for s,letter,coefficient in terms:
        row[player(q,s,letter)] += coefficient
    return row


def check(q):
    m,triples=raw_arrays(q)
    weights={t[:3]:t[3] for t in triples}
    matching=[]
    for s in range(q):
        for letters,w in (('afi',1),('bdh',3),('ceg',4)):
            team=tuple(player(q,s,a) for a in letters)
            require(weights[team] == w, 'matching weight')
            matching.append(team)
    require(sorted(i for t in matching for i in t) == list(range(9*q)),
            'matching partition')
    require(sum(weights[t] for t in matching) == 8*q, 'integral lower bound')

    p,den=floor_cover(q)
    points=[('floor',p,den)]
    for s in range(1,q):
        y=ideal_cover(q,s)
        require(y[player(q,s,'e')] == 2, 'ideal attainment')
        points.append(('ideal_'+str(s),y,1))
    for label,v,d in points:
        require(min(v)>=0 and sum(v)==8*q*d, label+' nonnegativity/total')
        require(all(v[i]+v[j]+v[k]>=w*d for i,j,k,w in triples),
                label+' raw triple cover')
        require(all(sum(v[i] for i in t)==weights[t]*d for t in matching),
                label+' matched equalities')
    anchors={player(q,s,a) for s in range(q) for a in 'afi'}
    require(all(p[i]==den//3 for i in anchors), 'first floor')
    require(min(p[i] for i in range(9*q) if i not in anchors)==2*q+6,
            'second floor attained')
    require(p[player(q,0,'c')]==8*q, 'path cap attained')
    require(all(p[player(q,s,'e')]==2*q+6 for s in range(1,q)),
            'designated payoff fractions')
    t=Fraction(1,3)+Fraction(1,q)
    require(q*t-Fraction(q-1,3)==Fraction(4,3), 'telescoped floor bound')

    # Each ideal certificate sums to e_s<=2. Check the raw rows supporting it.
    for s in range(1,q):
        for letters,blocks,w in (
                ('cdh',(s-1,s,s),3), ('ceg',(s,s-1,s-1),3),
                ('bfg',(s,s,s),4)):
            key=tuple(player(q,b,a) for b,a in zip(blocks,letters))
            require(weights[key]==w, 'ideal certificate source weight')
        rows=[vector(q,[(s,'b',1),(s-1,'c',-1)]),
              vector(q,[(s-1,'c',1),(s,'c',-1)]),
              vector(q,[(s,'e',1),(s,'b',-1),(s,'f',-1),(s,'c',1)]),
              vector(q,[(s,'f',1)])]
        require([sum(r[j] for r in rows) for j in range(9*q)] ==
                vector(q,[(s,'e',1)]), 'ideal certificate cancellation')
    return {'q':q,'players':9*q,'T':8*q,'raw_triples':len(triples),
            'covers':len(points),'triple_checks':len(triples)*len(points),
            'second_floor':str(t),'designated_ideal':'2',
            'designated_ratio':str(t/2),'status':'PASS'}


if __name__=='__main__':
    records=[check(q) for q in (3,4,5,8,12,24)]
    print(json.dumps({'status':'PASS','arithmetic':'integer plus Fraction',
                      'scope':'bounded raw-array corroboration and proof identities',
                      'records':records},indent=2))
