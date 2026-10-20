"""Check the distinct pure-owner institution and all its zero-report owners."""
from itertools import combinations
import json


def image(r, basis):
    out = 0
    for j, value in enumerate(basis):
        if r & (1 << j):
            out ^= value
    return out


def run():
    profiles = actions = transitions = terminal_checks = 0
    for mmax in range(1, 9):
        d = 2**(mmax+1)-1
        base = [1 << j for j in range(mmax+1)]
        triples = {tuple(sorted((a, b, a^b)))
                   for a in range(1, d+1) for b in range(a+1, d+1)}
        high = {1 << j for j in range(1, mmax+1)}
        previous = None
        for m in range(1, mmax+1):
            active = {1} | high | {1^(1<<j) for j in range(1, m+1)}
            reports = {r: int(r in active) for r in range(1, d+1)}
            supported = {e for e in triples if all(reports[r] for r in e)}
            expected = {tuple(sorted((1, 1<<j, 1^(1<<j)))) for j in range(1, m+1)}
            assert supported == expected
            dual = {r: int(r == 1 or not reports[r]) for r in reports}
            assert sum(dual[r]*reports[r] for r in reports) == 1
            assert all(sum(dual[r] for r in e) >= 1 for e in triples)
            # Terminal coverage is for these three actual pure owners.
            terminal = {1, 2, 3}
            assert terminal <= active and tuple(sorted(terminal)) in triples
            terminal_checks += 1
            generators = []
            for j in range(1, m+1):
                g = base.copy(); g[j] ^= 1; generators.append(g)
            for j in range(2, m+1):
                g = base.copy(); g[1], g[j] = g[j], g[1]; generators.append(g)
            if m == 1:
                g = base.copy(); g[0], g[1] = g[1], g[0]; generators.append(g)
                g = base.copy(); g[0] ^= g[1]; generators.append(g)
            for g in generators:
                perm = {r: image(r, g) for r in reports}
                assert set(perm.values()) == set(reports)
                # Joint owner/resource action; checks ALL d owners, not just active ones.
                assert all(reports[perm[r]] == reports[r] for r in reports)
                assert all(tuple(sorted(perm[r] for r in e)) in triples for e in triples)
                actions += 1
            if previous is not None:
                changed = [r for r in reports if reports[r] != previous[r]]
                assert changed == [1^(1<<m)]
                coalition = {1<<j for j in range(1, m)} | {1^(1<<j) for j in range(1, m+1)}
                assert len(coalition) == 2*m-1 and set(changed) <= coalition
                assert all(reports[r] == previous[r] for r in reports if r not in coalition)
                transitions += 1
            previous = reports
            profiles += 1
        if mmax >= 2:
            assert all(any(r not in e for e in triples) for r in reports)
    return {"PASS": True, "pure_owner_profiles": profiles,
            "full_institution_stabilizer_actions": actions,
            "actual_owner_transitions": transitions,
            "three_owner_terminal_coverage_checks": terminal_checks,
            "scope": "Finite pure-owner realization checks; universal action proof is in the note."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
