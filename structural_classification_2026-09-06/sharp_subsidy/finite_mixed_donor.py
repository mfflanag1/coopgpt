"""Finite-size sharpening of the existing universal mixed donor certificate."""
from fractions import Fraction as F
from pathlib import Path
import json
from mixed_donor_template import construct

def main():
 root=Path(__file__).parent
 prior=json.loads((root/'MIXED_DONOR_CERTIFICATES.json').read_text())
 out=[]
 for old in prior:
  m=old['m'];P=old['P'];h=m-len(P)
  d=construct(m,P,t=F(4,5)+F(1,20*h));d['case']=old['case'];out.append(d)
 (root/'FINITE_MIXED_DONOR_CERTIFICATES.json').write_text(json.dumps(out)+'\n')
 print(json.dumps({'status':'GENERATED','cases':len(out),'bound':'2/5-1/(60h)'}))
if __name__=='__main__':main()
