"""Standard-library exact replay of the seed35 efficient-price reselection."""
from fractions import Fraction as Q
from pathlib import Path
import json
from check_certificate import check


root=Path(__file__).resolve().parent
checked=check(root/'case_35_certificate.json')
data=json.loads((root/'case_35_certificate.json').read_text())
selected=json.loads((root/'price_reselection.json').read_text())
case=data['case'];d=case['d'];A=case['A'];pi=list(map(Q,case['pi']))
values={tuple(x['cap']):Q(x['value']) for x in data['oracles']}
b=[[data['owner_states'][i][profile[i]] for i in range(4)] for profile in data['profiles']]
prices={int(k):list(map(Q,v)) for k,v in selected['prices'].items()}
for k,p in prices.items():
    B=tuple(sum(b[k][i][a] for i in range(4)) for a in range(d))
    if min(p)<0 or sum(p[a]*B[a] for a in range(d))!=values[B]:raise ValueError('price efficiency')
    if any(sum(A[a][e]*p[a] for a in range(d))<pi[e] for e in range(len(pi))):raise ValueError('price feasibility')
pos=neg=Q(0);count=0
for item in data['certificate']:
    if item['tag'][0]!='out':continue
    _,lo,hi,C=item['tag'];delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d))
    defect=sum(prices[lo][a]*b[lo][i][a]-prices[hi][a]*b[hi][i][a] for i in C for a in range(d))+values[delta]
    if defect<0:raise ValueError('negative price defect remains')
    pos+=Q(item['weight'])*defect;count+=1
if pos!=Q(selected['exact_positive_of_selected_prices']):raise ValueError('sum mismatch')
print(json.dumps(dict(status='EXACT PASS',efficient_prices=len(prices),comparison_rows=count,positive_defect=str(pos),negative_defect='0',conclusion='The selected seed35 cancellation can be eliminated by efficient-price reselection.'),indent=2))
