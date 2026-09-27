"""Exact construction checks for the three-halves factorization lemma."""
from fractions import Fraction as F
from pathlib import Path
import json


def split(matrices, p, scale):
    A, B, C = matrices
    m = len(A)
    H = [scale * F(v) for v in p]
    edges = []
    for i in range(m):
        for j in range(m):
            edges.append((i, m+j, -F(A[i][j])))
    for j in range(m):
        for k in range(m):
            edges.append((m+j, 2*m+k, H[m+j]+H[2*m+k]-F(C[j][k])))
    for k in range(m):
        for i in range(m):
            edges.append((2*m+k, i, H[i]-F(B[i][k])))
    # An implicit source has zero-cost arcs to every graph node.
    dist = [F(0)] * (3*m)
    for iteration in range(3*m):
        changed = False
        for tail, head, cost in edges:
            candidate = dist[tail] + cost
            if candidate < dist[head]:
                dist[head] = candidate
                changed = True
        if not changed:
            break
    else:
        return {'status': 'negative_cycle'}
    alpha = dist[:m]
    beta = [-v for v in dist[m:2*m]]
    gamma = dist[2*m:]
    aI, aJ = alpha, beta
    bI, bK = [H[i]-alpha[i] for i in range(m)], gamma
    cJ = [H[m+j]-beta[j] for j in range(m)]
    cK = [H[2*m+k]-gamma[k] for k in range(m)]
    conditions = []
    for i in range(m):
        for j in range(m):
            conditions.append(aI[i]+aJ[j] >= F(A[i][j]))
    for i in range(m):
        for k in range(m):
            conditions.append(bI[i]+bK[k] >= F(B[i][k]))
    for j in range(m):
        for k in range(m):
            conditions.append(cJ[j]+cK[k] >= F(C[j][k]))
    conditions.extend(aI[i]+bI[i] == H[i] for i in range(m))
    conditions.extend(aJ[j]+cJ[j] == H[m+j] for j in range(m))
    conditions.extend(bK[k]+cK[k] == H[2*m+k] for k in range(m))
    if not all(conditions):
        raise RuntimeError('Constructed pair split failed an exact inequality or payoff identity')
    return {'status': 'feasible_split', 'exact_checks': len(conditions),
            'components': [[str(v) for v in row] for row in [aI,aJ,bI,bK,cJ,cK]]}


def main():
    record = json.loads((Path(__file__).resolve().parents[1]/'experiment'/'finite_attainment_exact.json').read_text())
    outputs = {}
    for name in ['x', 'z', 'target_ideal_witness']:
        outputs['finite_attainment_'+name] = split(record['matrices'], record[name], F(3,2))
        if outputs['finite_attainment_'+name]['status'] != 'feasible_split':
            raise RuntimeError('Three-halves split missing')
    anti = [[0,1],[1,0]]
    p = [F(2,3)] * 6
    outputs['sharp_antiferromagnetic_3_over_2'] = split([anti,anti,anti], p, F(3,2))
    outputs['sharp_antiferromagnetic_7_over_5'] = split([anti,anti,anti], p, F(7,5))
    if outputs['sharp_antiferromagnetic_3_over_2']['status'] != 'feasible_split':
        raise RuntimeError('Sharp endpoint failed')
    if outputs['sharp_antiferromagnetic_7_over_5']['status'] != 'negative_cycle':
        raise RuntimeError('Expected factor-below-3/2 obstruction absent')
    result = {'status':'PASS', 'method':'Fraction arithmetic; Bellman-Ford construction and direct pair-cover/payoff checks',
              'scope':'finite construction controls; all-parameter proof is in CERTIFICATE_GATE.md', 'cases':outputs}
    Path(__file__).with_name('factorization_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'], 'cases':{k:v['status'] for k,v in outputs.items()}},indent=2))

if __name__ == '__main__':
    main()
