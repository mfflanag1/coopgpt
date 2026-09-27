from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares,minimize_scalar
import two_hub_blocks as tb
from balanced_conductance import profiles,check
rec=json.loads(Path(__file__).with_name('BLOCK_STRESS_RESULTS.json').read_text())[0];m,P=tb.example(rec['same'],0);base=tb.structure(m,P);L=rec['L'];rb=[sum(L[b])+sum(b in bs for bs in base[6])-2 for b in range(5)];data=(*base[:3],rb,L,*base[5:]);out=[]
def test(mu):
 target=np.array([3+mu,4-mu]);fit=least_squares(lambda z:profiles(data,z)[1]-target,np.array([3.,3.]),bounds=(-15,25),max_nfev=200,xtol=1e-11,ftol=1e-11,gtol=1e-11);ps,A=profiles(data,fit.x);gap,wit,mind=check(data,ps);d={'mu':float(mu),'gap':gap,'residual':float(max(abs(A-target))),'witness':wit,'conductances':np.exp(fit.x).tolist()};out.append(d);return gap
for mu in np.linspace(.001,.999,11):print(mu,test(mu),flush=True)
r=minimize_scalar(test,bounds=(.001,.999),method='bounded',options={'xatol':1e-8});print('optimum',r.x,r.fun,flush=True)
Path(__file__).with_name('CONDUCTANCE_SPLIT_DISCOVERY.json').write_text(json.dumps(out)+'\n')
