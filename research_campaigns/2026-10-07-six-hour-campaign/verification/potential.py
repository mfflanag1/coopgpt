"""Exact checks for the potential-repair obstruction; finite support, not proof."""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import json

REPO=Path(__file__).resolve().parents[3]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj


def formulas(k,beta):
    phi=(beta**k/2-Q(k)*beta**(k+2)/(6*(k+3))
         +(Q(1,2)-beta**2/6)*(1-beta**k)
         -Q(k)*(1-beta**(k+2))/(2*(k+2))
         +Q(k)*beta*(1-beta**(k+1))/(2*(k+1)))
    q=(Q(k)*beta**(k+1)/(2*(k+2))
       +Q(k)*(1-beta**(k+1))/(k+1)-beta*(1-beta**k)/2)
    return phi,q


def run():
    cdf=load('cdf',REPO/'research_campaigns/2026-10-06-series-parallel/verification/verify.py')
    graph=load('graph',REPO/'research_campaigns/2026-10-06-monotone-envelope/verification/verify.py')
    count=0;deletions=0
    A=cdf.uniform(Q(1))
    for k in range(1,9):
        if k>1:A=cdf.minimum(A,cdf.uniform(Q(1)))
        edges=[(j,j+1) for j in range(k)]+[(0,k),(k,k+1)]
        cuts=graph.cutsets(k+2,edges)
        expected=[(1<<j)|(1<<k) for j in range(k)]+[1<<(k+1)]
        graph.require(cuts==sorted(expected),'structural cuts')
        for beta in (Q(1,4),Q(1,2),Q(3,4),Q(1)):
            phi,q=formulas(k,beta)
            S=cdf.convolution(A,cdf.uniform(beta))
            graph.require(phi==cdf.expectation(cdf.minimum(S,cdf.uniform(Q(1))),Q(1)),
                          'independent CDF check of phi')
            graph.require(q==1-cdf.expectation(cdf.minimum(S,cdf.atom(Q(1))),Q(1)),
                          'independent CDF check of winning probability')
            caps=[Q(1)]*k+[beta,Q(1)]
            graph.require(graph.effective(k+2,edges,caps)==caps,'original caps')
            graph.require(graph.maxflow(k+2,edges,caps)==1,'T=1')
            for e in range(k+2):
                erased=caps.copy();erased[e]=Q(0)
                ds=graph.effective(k+2,edges,erased)
                want=[Q(0)]*k+[beta,beta] if e<k else (
                    [Q(1)]*k+[Q(0),Q(1)] if e==k else [Q(0)]*(k+2))
                graph.require(ds==want,'deletion normalization')
                deletions+=1
            graph.require(phi-beta/3>=beta*(1-beta)/6,'uniform marginal lower bound')
            graph.require(1<=1+beta*q<=1+beta,'base payment bound')
            count+=1
    witnesses=[]
    for k in (8,16,37,64,128):
        phi,q=formulas(k,Q(1,2))
        total=2*((k+2)*phi-Q(k,6)-Q(1,k+2))
        base=1+q/2
        graph.require(total>=Q(k,12),'growing exact budget obstruction')
        if k>=37:graph.require(total/2>base,'failed aggregate marginal inequality')
        witnesses.append(dict(k=k,K=k+1,p_total=str(total),z_total=str(base),
                              p_lower_bound=str(Q(k,12))))
    return dict(status='PASS',cdf_cases=count,deletion_profiles=deletions,
                exact_witnesses=witnesses,
                scope='Checks support the all-k conventional proof; this does not refute the envelope bound.')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,help='Optionally also write the JSON result to this path')
    args=parser.parse_args()
    result=run();content=json.dumps(result,indent=2)+'\n'
    if args.output is not None:
        args.output.write_text(content)
    print(content,end='')
