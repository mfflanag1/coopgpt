"""Exact scalar gates for the conventional core-compatibility improvement."""
from fractions import Fraction as F
import json,sys


def main():
    a,b,c=F(26,47),F(333,799),F(24,799)
    require=lambda ok,msg: None if ok else (_ for _ in ()).throw(ValueError(msg))
    require(a+b+c==1 and min(a,b,c)>0,'combination weights')
    require(-F(5,3)*a+2*b+F(53,18)*c==0,'hub mass coefficient')
    require(a-F(10,9)*b-3*c==0,'all-internal minimum coefficient')
    require(a/3-b-c==-F(37,141),'degree-two coefficient')
    require(F(2,3)*a+(b+c)/18==F(37,94),'constant')
    require(a+F(5,3)*(b+c)==F(61,47),'leakage coefficient')
    require(F(17,18)*b==F(37,94),'minimum internal worth coefficient')
    require((F(2,5)-F(37,94))/(1+F(61,47)*60+F(37,94)*180)==F(3,70370),'gap algebra')
    require(F(3,70370)>F(1,100000),'contradiction threshold')
    result={'status':'PASS','epsilon':'1/100000','upper':'39999/100000','scope':'scalar gates; conventional proof supplies core, cloning and counting reductions'}
    if '--smt' in sys.argv:
        import z3 as z
        g,aa,B,x,cycle=z.Reals('g aa B x cycle')
        def Q(n,d=1):return z.RealVal(n)/d
        constraints=[g>0,g<=Q(1,100000),aa>0,aa<=60*g,
          B>=0,B<=Q(3,2),Q(3,2)-B<=1125*g,
          (x-B/3)*(x-B/3)<=300*g,
          cycle>=0,cycle<=300*g]
        donor=Q(4,5)*B-Q(3,5)-Q(6,5)*aa+Q(6,5)*cycle
        shortfall=x*(B-x)-B/5-aa*(x+B)
        internal=2-B-aa+cycle
        cases={
          'positive_shortfall_and_donor_ratio': z.Or(donor<=0,4*shortfall<donor),
          'leaf_rows_have_common_positive_headroom':z.Or(x<=Q(1,5)+aa,x>=1-aa),
          'internal_label_count':internal<Q(1,3),
        }
        verdicts={}
        for name,bad in cases.items():
            solver=z.Solver();solver.set(timeout=10000);solver.add(*constraints,bad);r=solver.check()
            require(r==z.unsat,name+': '+str(r));verdicts[name]=str(r)
        q,p,v,leak,tau,R=z.Reals('q p v leak tau R')
        solver=z.Solver();solver.set(timeout=10000)
        solver.add(q>=0,p>=0,p<=q,leak>=0,tau>=0,
          R<=Q(2,3)-Q(5,3)*q+p/3+v+leak,
          R<=Q(1,18)+2*q-p-Q(10,9)*v+Q(17,18)*tau+Q(5,3)*leak,
          R<=Q(1,18)+Q(53,18)*q-p-3*v+Q(5,3)*leak,
          R>Q(37,94)-Q(37,141)*p+Q(61,47)*leak+Q(37,94)*tau)
        r=solver.check();require(r==z.unsat,'master inequality');verdicts['master_inequality']=str(r)
        solver=z.Solver();solver.set(timeout=10000)
        solver.add(g>0,g<=Q(1,100000),leak>=0,leak<=60*g,tau>=0,tau<=180*g,
           Q(2,5)-g<=Q(37,94)+Q(61,47)*leak+Q(37,94)*tau)
        r=solver.check();require(r==z.unsat,'global gap contradiction');verdicts['global_gap_contradiction']=str(r)
        # A wider range admits the scalar relaxation; UNSAT is not automatic.
        solver=z.Solver();solver.add(g>0,g<=Q(1,1000),leak>=0,leak<=60*g,tau>=0,tau<=180*g,
           Q(2,5)-g<=Q(37,94)+Q(61,47)*leak+Q(37,94)*tau)
        r=solver.check();require(r==z.sat,'widened-range control');verdicts['widened_range_control']=str(r)
        result['exact_real_queries']=verdicts
    print(json.dumps(result))

if __name__=='__main__':main()
