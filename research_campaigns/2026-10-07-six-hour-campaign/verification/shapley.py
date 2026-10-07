"""Exact Shapley obstruction checks, with two independent enumeration forms."""
from fractions import Fraction as Q
from itertools import permutations
from math import factorial
import json


def subset_shapley(values, n):
    weights=[Q(factorial(k)*factorial(n-k-1),factorial(n)) for k in range(n)]
    return [sum((weights[m.bit_count()]*(values[m|1<<i]-values[m])
                 for m in range(1<<n) if not m>>i&1),Q(0)) for i in range(n)]


def path_game(n,l):
    owners=1+n+l;long=((1<<n)-1)<<1;short=((1<<l)-1)<<(n+1)
    values=[int(bool(m&1) and (m&long==long or m&short==short))
            for m in range(1<<owners)]
    phi=subset_shapley(values,owners)
    expected=[Q(1,n+1)+Q(1,l+1)-Q(1,n+l+1)]
    expected += [Q(1,n+1)-Q(1,n+l+1)]*n
    expected += [Q(1,l+1)-Q(1,n+l+1)]*l
    assert phi==expected and sum(phi)==1
    payment=sum(phi[:n+1]);assert payment==Q(1,l+1)+Q(l,n+l+1)
    return dict(n=n,l=l,K=1+n*l,owners=owners,coalition_payment=str(payment),
                shares=list(map(str,phi)))


def balanced_game():
    caps=[1]*7+[2];pool=[0,0,0,1,1,1,2,2];n=8
    values=[]
    for m in range(1<<n):
        totals=[0]*3
        for i in range(n):
            if m>>i&1:totals[pool[i]]+=caps[i]
        values.append(min(totals))
    phi=subset_shapley(values,n)
    assert phi==[Q(9,28)]*6+[Q(7,20),Q(101,140)]
    sums=[0]*n
    for perm in permutations(range(n)):
        m=0
        for i in perm:
            nxt=m|1<<i;sums[i]+=values[nxt]-values[m];m=nxt
    assert [Q(x,factorial(n)) for x in sums]==phi
    payment=phi[0]+phi[3]+phi[6]
    assert payment==Q(139,140) and values[(1<<0)|(1<<3)|(1<<6)]==1
    return dict(owners=n,K=3,coalition_value=1,coalition_payment=str(payment),
                shares=list(map(str,phi)),permutations=factorial(n))


def run():
    paths=[path_game(n,l) for n,l in [(2,2),(3,2),(4,2),(4,3),(9,3)]]
    assert paths[-1]['coalition_payment']=='25/52'
    for l in range(2,101):
        assert Q(1,l+1)+Q(l,l*l+l+1)<Q(2,l)
    return dict(status='PASS',path_cases=paths,balanced=balanced_game(),
                asymptotic_parameter_checks=99,
                scope='Exact finite game enumeration and rational algebra; all-size proof is in the note.')


if __name__=='__main__':print(json.dumps(run(),indent=2))
