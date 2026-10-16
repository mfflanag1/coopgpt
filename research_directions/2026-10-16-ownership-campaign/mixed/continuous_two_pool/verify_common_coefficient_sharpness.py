#!/usr/bin/env python3
from fractions import Fraction as Q
from pathlib import Path
import json

def need(ok,msg):
 if not ok:raise ValueError(msg)
# Rows are in p_U,p_W,p_Z,alpha, with >= conventions.
rows=[([1,0,0,0],Q(1,3)),([-Q(2,3),1,0,0],Q()),([0,-Q(2,3),1,0],Q()),([0,0,-1,1],Q(1))]
weights=[Q(4,9),Q(2,3),Q(1),Q(1)]
combo=[sum(w*row[j]for w,(row,rhs)in zip(weights,rows))for j in range(4)]
rhs=sum(w*b for w,(row,b)in zip(weights,rows))
need(combo==[0,0,0,1],'coefficient cancellation failed');need(rhs==Q(31,27),'bound failed')
out=dict(status='EXACT RATIONAL PASS',combined_coefficients=list(map(str,combo)),lower=str(rhs),weights=list(map(str,weights)),scope='Algebraic replay of the displayed four-profile class obstruction, not independent implementation or an unrestricted lower.')
Path(__file__).with_name('common_coefficient_sharpness.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
