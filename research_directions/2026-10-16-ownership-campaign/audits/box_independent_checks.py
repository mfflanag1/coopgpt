#!/usr/bin/env python3
"""Independent counterfactual-box audit; binary-float exp diagnostics only.

This harness does not import any original verification script's main/check
routine. It reconstructs extrema from four actual-owner corners and directly
enumerates interior reports, local-total underreports, and generic box domains.
The reference optimizer is treated as the candidate under test; all feasibility
and objective comparisons use the previously independent primitive definition.
"""
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import math
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'certificates'/'range_algorithm'))
from verify_range_mechanism import primitive, abstract_options, C0
sys.path.insert(0,str(ROOT/'mixed'))
from owner_box_reference import optimize_box_owner, counterfactual_ranges, box_range_rule

TOL=3e-10
COUNTS={}
def check(ok,kind):
    COUNTS[kind]=COUNTS.get(kind,0)+1
    if not ok:raise ValueError(kind)


def ceiling(a,b):
    A,B=math.fsum(a),math.fsum(b);T=min(A,B)
    if T==0:return 0.,([0.]*len(a),[0.]*len(a))
    short,long=(a,b) if A<=B else (b,a)
    capped=[min(x,T) for x in long]
    mass=math.fsum(capped);target=min(mass,2*T)
    chosen=[x*target/mass for x in capped]
    witness=(list(short),chosen) if A<=B else (chosen,list(short))
    s=target/T
    return T*(1+(s-1)*math.exp(1-s)/2),witness


def data(rows):
    n=len(rows);m=(len(rows[0])-1)//2
    p=[row[0] for row in rows];h=[math.fsum(row[1:1+m]) for row in rows]
    z=[0.]*n;M=Lbar=0.
    for j in range(m):
        a=[row[1+j] for row in rows];b=[row[1+m+j] for row in rows]
        value=primitive(a,b)
        z=[x+y for x,y in zip(z,value)]
        M+=min(math.fsum(a),math.fsum(b));Lbar+=ceiling(a,b)[0]
    return n,m,p,h,z,M,Lbar


def extrema(rows):
    n,m,_,_,_,_,_=data(rows)
    lo=[[0.]*n for _ in rows];up=[[0.]*n for _ in rows]
    for j in range(m):
        a=[row[1+j] for row in rows];b=[row[1+m+j] for row in rows]
        for i in range(n):
            corner=[]
            for fa,fb in ((0.,0.),(0.,1.),(1.,0.),(1.,1.)):
                aa=list(a);bb=list(b);aa[i]*=fa;bb[i]*=fb
                corner.append(primitive(aa,bb))
            for k in range(n):
                if i==k:continue
                low=min(v[k] for v in corner);high=max(v[k] for v in corner)
                expected_lo=corner[2][k] if a[k]>=b[k] else corner[1][k]
                expected_hi=corner[1][k] if a[k]>=b[k] else corner[2][k]
                scale=1+math.fsum(a)+math.fsum(b)
                check(abs(low-expected_lo)<=TOL*scale,'endpoint minimum at prescribed corner')
                check(abs(high-expected_hi)<=TOL*scale,'endpoint maximum at prescribed corner')
                lo[i][k]+=low;up[i][k]+=high
    return lo,up


def assemble(rows):
    n,m,p,h,z,M,Lbar=data(rows)
    low,high=extrema(rows);K=math.fsum(p)+Lbar
    y=[];witnesses=[]
    for i in range(n):
        lower=[p[k]+low[i][k] for k in range(n)]
        upper=[p[k]+high[i][k] for k in range(n)];beta=p[i]+z[i];upper[i]=beta
        value,w,mode=optimize_box_owner(h,lower,upper,beta,K,i)
        scale=1+K+math.fsum(h)
        check(all(l-TOL*scale<=v<=u+TOL*scale for l,v,u in zip(lower,w,upper)),
              'physical box attainer bounds')
        check(math.fsum(w)<=K+TOL*scale,'physical box attainer total')
        check(abs(primitive(h,w)[i]-value)<=TOL*scale,'physical box attainer objective')
        y.append(value);witnesses.append(w)
    return y,low,high,(n,m,p,h,z,M,Lbar)


def local_tests():
    full_profiles=0;underreports=0;max_error=0.
    for values in product((0.,1.,2.),repeat=6):
        a,b=values[:3],values[3:];scale=1+math.fsum(values)
        target,witness=ceiling(a,b)
        check(all(0<=x<=y+TOL*scale for x,y in zip(witness[0],a)),
              'local total attainer first coordinates')
        check(all(0<=x<=y+TOL*scale for x,y in zip(witness[1],b)),
              'local total attainer second coordinates')
        error=abs(math.fsum(primitive(*witness))-target)/scale
        max_error=max(max_error,error)
        check(error<=TOL,'local total attainer objective')
        levels=[sorted(set((0.,x/2,x))) for x in values]
        for changed in product(*levels):
            aa,bb=changed[:3],changed[3:]
            check(math.fsum(primitive(aa,bb))<=target+TOL*scale,
                  'all-owner local report below ceiling')
            check(ceiling(aa,bb)[0]<=target+TOL*scale,
                  'local total ceiling is monotone')
            underreports+=1
        rows=tuple((0.,a[k],b[k]) for k in range(3))
        low,high=extrema(rows)
        for i in range(3):
            for ai,bi in product(sorted(set((0.,a[i]/2,a[i]))),
                                 sorted(set((0.,b[i]/2,b[i])))):
                aa=list(a);bb=list(b);aa[i]=ai;bb[i]=bi
                pay=primitive(aa,bb)
                for k in range(3):
                    if i!=k:
                        check(low[i][k]-TOL*scale<=pay[k]<=high[i][k]+TOL*scale,
                              'recipient interior report in exact endpoint range')
        full_profiles+=1
    return {'full_two_pool_profiles':full_profiles,'all_owner_underreports':underreports,
            'max_scaled_total_attainment_error':max_error}


def physical_tests():
    profiles=underreports=coalitions=0;max_box_factor=0.
    for n,m,levels in ((2,1,(0.,1.,2.)),(3,1,(0.,1.)),(2,2,(0.,1.))):
        width=2*m+1
        for values in product(levels,repeat=n*width):
            rows=tuple(tuple(values[i*width:(i+1)*width]) for i in range(n))
            y,low,high,info=assemble(rows)
            _,_,p,h,z,M,Lbar=info
            H=math.fsum(h);P=math.fsum(p);K=P+Lbar;scale=1+H+K
            old_low,old_up=counterfactual_ranges(rows)
            ref_y=box_range_rule(rows)[0]
            for i in range(n):
                check(abs(y[i]-ref_y[i])<=TOL*scale,'reference box payment agreement')
                for k in range(n):
                    if i!=k:
                        check(abs(low[i][k]-old_low[i][k])<=TOL*scale,
                              'reference endpoint minima agreement')
                        check(abs(high[i][k]-old_up[i][k])<=TOL*scale,
                              'reference endpoint maxima agreement')
                beta=p[i]+z[i]
                lower=[p[k]+low[i][k] for k in range(n)]
                floor=max(item['value'] for item in abstract_options(h,lower,beta,K,i))
                bar=max(item['value'] for item in abstract_options(h,p,beta,K,i))
                original=max(item['value'] for item in abstract_options(h,p,beta,P+C0*M,i))
                nested=primitive(h,[p[k]+z[k] for k in range(n)])[i]
                check(nested<=y[i]+TOL*scale,'nested below box')
                check(y[i]<=floor+TOL*scale<=bar+2*TOL*scale<=original+3*TOL*scale,
                      'pointwise box floor bar original sandwich')
                choices=[sorted(set((0.,x/2,x))) for x in rows[i]]
                for changed in product(*choices):
                    rr=list(rows);rr[i]=changed;rr=tuple(rr)
                    _,_,pp,hh,zz,MM,LL=data(rr)
                    actual=primitive(hh,[pp[k]+zz[k] for k in range(n)])[i]
                    check(actual<=y[i]+TOL*scale,'actual own underreport below box')
                    for k in range(n):
                        if k!=i:
                            check(low[i][k]-TOL*scale<=zz[k]<=high[i][k]+TOL*scale,
                                  'actual recipient payments inside box')
                    check(zz[i]<=z[i]+TOL*scale and math.fsum(zz)<=Lbar+TOL*scale,
                          'restored actual report inside own total ceilings')
                    # Full interval nesting and payment monotonicity are checked
                    # on the all-zero, half, and full whole-owner contractions.
                    if changed in (tuple(0. for _ in changed),tuple(x/2 for x in rows[i]),rows[i]):
                        yy,ll,uu,ii=assemble(rr)
                        delta=p[i]-pp[i]
                        check(yy[i]<=y[i]+TOL*scale,'whole-owner box monotonicity')
                        check(all(low[i][k]<=ll[i][k]+TOL*scale and
                                  high[i][k]+TOL*scale>=uu[i][k]
                                  for k in range(n) if k!=i),
                              'actual-owner interval domain inclusion')
                        check(pp[i]+zz[i]+delta<=beta+TOL*scale and
                              math.fsum(pp)+LL+delta<=K+TOL*scale,
                              'own translation and total ceiling inclusion')
                    underreports+=1
            F=min(H,P+M)
            check(math.fsum(y)<=1.75*F+TOL*scale,'physical box funding')
            if F:max_box_factor=max(max_box_factor,math.fsum(y)/F)
            for mask in range(1 << n):
                rr=tuple(row if mask & (1 << i) else tuple(0. for _ in row)
                         for i,row in enumerate(rows))
                _,_,pp,hh,_,MM,_=data(rr)
                val=min(math.fsum(hh),math.fsum(pp)+MM)
                check(math.fsum(y[i] for i in range(n) if mask & (1 << i))>=val-TOL*scale,
                      'all physical coalition coverage')
                coalitions+=1
            profiles+=1
    return {'profiles':profiles,'actual_own_underreports':underreports,
            'all_coalitions':coalitions,'largest_observed_box_factor':max_box_factor}


def generic_optimizer_tests():
    rng=random.Random(16102030);cases=competitors=0;max_error=0.
    for trial in range(2400):
        n=1+trial%4;i=trial%n
        a=[rng.choice((0.,.25,.5,1.,2.,4.)) for _ in range(n)]
        lo=[rng.choice((0.,.25,1.,2.,4.)) for _ in range(n)]
        up=[x+rng.choice((0.,.25,1.,4.)) for x in lo]
        beta=up[i]
        base=beta+math.fsum(lo[k] for k in range(n) if k!=i)
        K=base+rng.random()*math.fsum(up[k]-lo[k] for k in range(n) if k!=i)
        H=math.fsum(a)
        if trial%3==0 and base<=H:
            K=H
        val,w,mode=optimize_box_owner(a,lo,up,beta,K,i)
        scale=1+H+K
        check(all(l-TOL*scale<=x<=u+TOL*scale for l,x,u in zip(lo,w,up)),
              'generic optimizer attainer box bounds')
        check(math.fsum(w)<=K+TOL*scale,'generic optimizer attainer budget')
        error=abs(primitive(a,w)[i]-val)/scale
        check(error<=TOL,'generic optimizer attainer objective')
        max_error=max(max_error,error)
        options=[sorted(set((lo[k],(lo[k]+up[k])/2,up[k],
                              min(up[k],max(lo[k],H)),
                              min(up[k],max(lo[k],a[i]))))) for k in range(n)]
        vectors=list(product(*options))
        # Also intersect every other-coordinate corner with the sum-cap face.
        for changing in range(n):
            others=[k for k in range(n) if k!=changing]
            for edge in product(*[(lo[k],up[k]) for k in others]):
                bb=list(lo)
                for k,x in zip(others,edge):bb[k]=x
                bb[changing]=K-math.fsum(edge)
                if lo[changing]<=bb[changing]<=up[changing]:vectors.append(tuple(bb))
        for b in vectors:
            if math.fsum(b)>K+TOL*scale:continue
            check(primitive(a,b)[i]<=val+TOL*scale,'generic feasible competitor below optimizer')
            competitors+=1
        cases+=1
    return {'generic_box_domains':cases,'feasible_opponent_vectors':competitors,
            'max_scaled_attainment_error':max_error}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    report={'local':local_tests(),'physical':physical_tests(),
            'generic':generic_optimizer_tests(),'check_counts':COUNTS,
            'status':'NUMERICAL PASS',
            'scope':'Independent finite diagnostics with binary floats/math.exp and tolerance 3e-10; no continuum certificate.',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    encoded=json.dumps(report,indent=2)+'\n'
    args.output.write_text(encoded)
    print(encoded,end='')
