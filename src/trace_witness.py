"""Emit a Dietzenbacher Example-2 style procedure trace for the canonical witness."""
from fractions import Fraction as F
from tugame import Game
from pes import egalitarian_procedure, pes

# Canonical (primary) witness: exact, symmetric egalitarian claims (1,1,1,1,1).
V = [0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
N_PLAYERS = 5
N = (1 << N_PLAYERS) - 1
g = Game(N_PLAYERS, [F(x) for x in V])


def label(S):
    return "{" + ",".join(str(i + 1) for i in range(N_PLAYERS) if S >> i & 1) + "}"


def traced_rounds(game):
    """Replay the procedure, returning per-round (chi dict, A^k, P^k, gamma^k)."""
    n, Nn, v = game.n, game.N, game.v
    P, gamma, rounds = 0, {}, []
    for _ in range(n + 1):
        chi, maxchi = {}, {i: None for i in range(n)}
        for S in range(1, Nn + 1):
            mem = [i for i in range(n) if S >> i & 1]
            fixed = [i for i in mem if P >> i & 1]
            unfixed = [i for i in mem if not (P >> i & 1)]
            sf = sum((gamma[i] for i in fixed), F(0))
            d = {}
            if unfixed:
                sh = (v[S] - sf) / len(unfixed)
                for i in fixed:
                    d[i] = gamma[i]
                for i in unfixed:
                    d[i] = sh
            else:
                for i in fixed:
                    d[i] = gamma[i]
            chi[S] = d
            for i in mem:
                if maxchi[i] is None or d[i] > maxchi[i]:
                    maxchi[i] = d[i]
        A = [S for S in range(1, Nn + 1)
             if sum((chi[S][i] for i in range(n) if S >> i & 1), F(0)) == v[S]
             and all(chi[S][i] == maxchi[i] for i in range(n) if S >> i & 1)]
        Pnew = 0
        for S in A:
            Pnew |= S
        newP = Pnew | P
        gnew = {i: (maxchi[i] if Pnew >> i & 1 else gamma[i])
                for i in range(n) if newP >> i & 1}
        rounds.append((dict(chi), list(A), newP, dict(gnew)))
        P, gamma = newP, gnew
        if P == N:
            break
    return rounds


def cell(chi_S, S):
    parts = []
    for i in range(N_PLAYERS):
        parts.append(str(chi_S[i]) if S >> i & 1 else "·")
    return "(" + ",".join(parts) + ")"


rounds = traced_rounds(g)
claims, A_hat, is_ES = egalitarian_procedure(g)
p, D = pes(g)

# columns: coalitions in A-hat (sorted by size) + the grand coalition N
cols = sorted(set(A_hat) | {N}, key=lambda S: (bin(S).count("1"), S))

lines = []
lines.append("Procedural egalitarian trace — canonical witness (refutes Dietzenbacher 2021)")
lines.append("N = {1,2,3,4,5}; v in bitmask order = " + str(V))
lines.append("Exact game (min-core x(S)=v(S) for all S); superadditive, monotone, balanced, not convex.")
lines.append("")
w = 16
hdr = "S".ljust(10) + "".join(label(S).ljust(w) for S in cols)
lines.append(hdr)
lines.append("v(S)".ljust(10) + "".join(str(int(g.v[S])).ljust(w) for S in cols))
lines.append("-" * len(hdr))
for k, (chi, A, P, gm) in enumerate(rounds, 1):
    row = f"chi^{k}(S)".ljust(10) + "".join(cell(chi[S], S).ljust(w) for S in cols)
    lines.append(row)
    adm = "  A^%d = " % k + ", ".join(label(S) for S in sorted(A, key=lambda s:(bin(s).count('1'),s)))
    lines.append(adm)
    lines.append("  P^%d = %s   gamma^%d = (%s)" %
                 (k, label(P), k, ",".join(str(gm[i]) for i in range(N_PLAYERS))))
lines.append("-" * len(hdr))
lines.append("")
lines.append(f"Iterations n^v = {len(rounds)}   (all players fixed after round {len(rounds)})")
lines.append("Egalitarian claims  gamma-hat = (" + ",".join(str(x) for x in claims) + ")   sum = "
             + str(sum(claims)) + "   >   v(N) = " + str(int(g.v[N])))
lines.append("Egalitarian admissible collection  A-hat = { "
             + ", ".join(label(S) for S in sorted(A_hat, key=lambda s:(bin(s).count('1'),s))) + " }")
lines.append("N = {1,2,3,4,5} NOT in A-hat  ==>  the game is NOT egalitarian stable.")
lines.append("")
lines.append("PES(v) = (" + ",".join(str(x) for x in p) + ")   (strong claimants D = " + label(D) + ")")
lines.append("PES is efficient but leaves the core:")
for S in g.core_violations(p):
    lines.append(f"    {label(S)}:  v = {int(g.v[S])}  >  PES(S) = {g.xS(p, S)}")
lines.append("")
lines.append("Reading: every player i attains payoff 1 in some coalition of worth |S| "
             "(its egalitarian claim), so gamma-hat = (1,1,1,1,1); but the grand coalition "
             "is worth only 4 < 5, so N cannot honour all claims and is not admissible.")

out = "\n".join(lines)
print(out)
with open("/Users/maxf/projects/counterexample-hunt/coopgames/results/canonical_witness_trace.txt", "w") as f:
    f.write(out + "\n")
