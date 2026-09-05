"""Fresh Fraction implementation of the procedural calculation and witness checks.

All coalition inequalities are used. The five-player control is Mauri's prior
example, not a new claimed contribution. No external solver is required.
"""
from fractions import Fraction as F
from pathlib import Path

from data import require, members, parse_game, strict_json_load


def total(x, coalition):
    return sum((x[i] for i in members(coalition, len(x))), F(0))


def envelope(rows):
    require(rows and len({len(x) for x in rows}) == 1, "inconsistent generators")
    require(len({sum(x) for x in rows}) == 1, "unequal generator totals")
    return [min(total(x, s) for x in rows) for s in range(1 << len(rows[0]))]


def in_core(v, x):
    return sum(x) == v[-1] and all(total(x, s) >= v[s] for s in range(len(v)))


def procedure(v):
    n = (len(v) - 1).bit_length()
    require(len(v) == 1 << n and v[0] == 0, "invalid game vector")
    fixed, rounds, final_admissible = {}, [], []
    for _ in range(n):
        claims = {}
        maxima = [None] * n
        for s in range(1, len(v)):
            ids = members(s, n)
            free = [i for i in ids if i not in fixed]
            residual = v[s] - sum((fixed[i] for i in ids if i in fixed), F(0))
            rate = residual / len(free) if free else None
            claims[s] = {i: fixed[i] if i in fixed else rate for i in ids}
            for i, value in claims[s].items():
                if maxima[i] is None or value > maxima[i]:
                    maxima[i] = value
        final_admissible = [s for s in claims if
                            sum(claims[s].values(), F(0)) == v[s] and
                            all(value == maxima[i] for i, value in claims[s].items())]
        new = {i: maxima[i] for s in final_admissible for i in members(s, n)
               if i not in fixed}
        require(bool(new), "procedure stalled before all players were fixed")
        rounds.append({"admissible": final_admissible,
                       "maxima": list(map(str, maxima)),
                       "new": {str(i + 1): str(q) for i, q in new.items()}})
        fixed.update(new)
        if len(fixed) == n:
            return tuple(fixed[i] for i in range(n)), len(v) - 1 in final_admissible, rounds
    raise ValueError("procedure exceeded its n-round bound")


def expected_claims(t):
    if t <= F(2, 3):
        return (F(1, 2) + 3*t/4, F(1, 2) + t/4,
                F(1, 2) + 3*t/4, F(1, 2) + t/4, 1+t/2, 1+t/2)
    if t <= 1:
        return (3*t/2, 1-t/2, F(1), 1-t/2, 1+t/2, 1+t/2)
    return (t+F(1, 2), F(1, 2), F(1), F(1, 2), t+F(1, 2), F(3, 2))


def verify(blocks):
    results = {}
    # Published positive and negative procedural controls, before custom games.
    a = [F(0)] * 16
    a[15], a[10], a[12] = F(24), F(14), F(14)
    b = [F(0)] * 8
    b[5] = b[6] = b[7] = F(4)
    controls = [("Dietzenbacher2021_Example2", a, (3,7,7,7), True),
                ("Dietzenbacher2021_Example3", b, (2,2,2), False)]
    mauri = envelope([(1,-1,-1,0,0), (0,1,0,-1,-1)])
    controls.append(("Mauri2017_Example5_PRIOR_ART", mauri, (0,0,0,0,0), False))
    for name, v, expected, stable in controls:
        x, actual_stable, trace = procedure(v)
        require(x == tuple(map(F, expected)) and actual_stable == stable,
                "published procedural control failed: " + name)
        results[name] = {"claims": list(map(str, x)), "PES_stable": stable, "trace": trace}
    require(results["Mauri2017_Example5_PRIOR_ART"]["trace"][0]["admissible"] ==
            [1,3,5,11,19], "Mauri maximizing collection differs")

    for name in ("stable_witness_1", "stable_witness_2"):
        block = blocks[name]
        require(block["n"] == 6, "witness must have six players")
        v = parse_game(block["game_v"], 6)
        rows = [tuple(F(q) for q in block["generator_points"][k]) for k in ("A", "B")]
        require(all(len(row) == 6 for row in rows), "generator dimension")
        require(envelope(rows) == v, "full coalition table is not generator envelope")
        require(all(in_core(v, row) for row in rows), "generator outside entire core")
        # Every coalition has an exactifier among these verified core points.
        require(all(any(total(row,s) == v[s] for row in rows) for s in range(64)),
                "exactness coverage incomplete")
        monotone = all(v[s | (1 << i)] >= v[s] for s in range(64)
                       for i in range(6) if not s >> i & 1)
        superadditive = all(v[s|t] >= v[s] + v[t] for s in range(64)
                            for t in range(64) if not s & t)
        require(monotone and superadditive, "stated class property failed")
        x, stable, trace = procedure(v)
        require(x == tuple(F(q) for q in block["egalitarian_claims"]), "stored claims wrong")
        require(sum(x) > v[-1] and not stable, "claim oversum failed")
        if name == "stable_witness_1":
            require(rows == [(F(1),F(1),F(0),F(1),F(3),F(0)),
                             (F(2),F(0),F(1),F(0),F(1),F(2))], "manuscript generators changed")
            require(trace[0]["admissible"] == [17,48], "first-round collection")
            require(trace[1]["admissible"] == [3,9,17,21,48,51,57] and len(trace) == 2,
                    "second-round collection")
            require(trace[0]["maxima"] == ["3/2","5/4","4/3","5/4","3/2","3/2"],
                    "first-round individual maxima")
        results[name] = {"claims": list(map(str, x)), "grand_worth": str(v[-1]),
                         "oversum": str(sum(x)-v[-1]), "trace": trace,
                         "all_64_coalitions_exact": True}

    # Check the claimed alternate normalization over all coalitions and endpoints.
    first, second = blocks["stable_witness_1"], blocks["stable_witness_2"]
    equiv = second["equivalence_to_stable_witness_1"]
    order = [i-1 for i in equiv["old_player_order"]]
    shift = tuple(F(q) for q in equiv["additive_shift"])
    require(sorted(order) == list(range(6)) and len(shift) == 6, "invalid equivalence")
    mapped = [tuple(F(first["generator_points"][k][i])+shift[j] for j,i in enumerate(order))
              for k in ("A","B")]
    if equiv["endpoint_swap"]:
        mapped.reverse()
    require(mapped == [tuple(F(q) for q in second["generator_points"][k]) for k in ("A","B")],
            "generator equivalence failed")
    v1,v2 = parse_game(first["game_v"],6),parse_game(second["game_v"],6)
    require(all(v2[s] == v1[sum(1 << order[j] for j in members(s,6))] + total(shift,s)
                for s in range(64)), "coalition equivalence failed")

    # Independent finite diagnostics; the symbolic verifier proves all t>=0.
    U,V = (0,1,0,1,2,0),(1,0,1,0,0,2)
    for t in map(F, ("0","1/3","2/3","4/5","1","2","10")):
        rows = [tuple(F(row[i])+(t if i in (0,4) else 0) for i in range(6)) for row in (U,V)]
        x, stable, trace = procedure(envelope(rows))
        require(x == expected_claims(t) and stable == (t == 0), "ray diagnostic failed")
        results["ray_diagnostic_"+str(t)] = {"claims": list(map(str,x)), "PES_stable":stable}
    return results


if __name__ == "__main__":
    with (Path(__file__).parent / "supplement_data.json").open() as stream:
        result = verify(strict_json_load(stream))
    print("CLAIMS AND FULL-COALITION CHECKS PASSED:", len(result), "records")
