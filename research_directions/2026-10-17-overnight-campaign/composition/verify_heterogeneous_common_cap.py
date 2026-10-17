"""Exact rational primal/dual and public-layer identities for weighted hyperstars."""
from fractions import Fraction as Q
from random import Random
from pathlib import Path
import json
rng=Random(197301);profiles=coalitions=0
for k in range(1,6):
  for M in range(1,14):
    for trial in range(20):
      alpha=[Q(rng.randrange(1,7),rng.randrange(1,5)) for _ in range(M)]
      beta=[[Q(rng.randrange(1,7),rng.randrange(1,5)) for _ in range(k)] for _ in range(M)]
      weights=[Q(rng.randrange(8),rng.randrange(1,5)) for _ in range(M)]
      public=[weights[j]/alpha[j] for j in range(M)]
      order=sorted(range(M),key=lambda j:-public[j])
      ownercount=4
      owners=[[Q(rng.randrange(5),rng.randrange(1,5)) for _ in range(1+k*M)] for _ in range(ownercount)]
      for mask in (15,1,3,5,10):
        c=[sum(owners[i][v] for i in range(ownercount) if mask>>i&1) for v in range(1+k*M)]
        P=c[0];caps=[min(alpha[j]/beta[j][l]*c[1+j*k+l] for l in range(k)) for j in range(M)]
        left=P;primal=Q(0);z=[Q(0)]*M
        for j in order:
          z[j]=min(left,caps[j]);left-=z[j];primal+=public[j]*z[j]
        prefix=Q(0);layer=Q(0)
        for idx,j in enumerate(order):
          prefix+=caps[j]
          nextv=public[order[idx+1]] if idx+1<M else Q(0)
          layer+=(public[j]-nextv)*min(P,prefix)
        # Independent scalar dual at a greedy breakpoint: min_t P*t+sum q_j(v_j-t)+.
        dual=min(P*t+sum(caps[j]*max(Q(0),public[j]-t) for j in range(M)) for t in [Q(0)]+public)
        assert primal==layer==dual
        # Pull the greedy plan back to original activity coordinates.
        activity=[z[j]/alpha[j] for j in range(M)]
        assert sum(alpha[j]*activity[j] for j in range(M))<=P
        assert all(beta[j][l]*activity[j]<=c[1+j*k+l] for j in range(M) for l in range(k))
        assert sum(weights[j]*activity[j] for j in range(M))==primal
        profiles+=1
        if mask!=15:coalitions+=1
out={'status':'PASS','exact_primal_dual_layer_profiles':profiles,'proper_coalition_profiles':coalitions,
     'private_arities':list(range(1,6)),'branches_up_to':13,
     'limits':'Checks exact fixed-public-layer identity and owner rescaling; incentive transfer follows analytically.'}
Path(__file__).with_name('HETEROGENEOUS_COMMON_CAP_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
