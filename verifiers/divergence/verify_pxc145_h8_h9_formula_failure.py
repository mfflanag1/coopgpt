#!/usr/bin/env python3
"""Exact rational replay of PXC145: the fixed-n formula fails at n=8 and n=9.

Each embedded game is the lower envelope of integer allocations of equal
total; exactness and singleton normalization are checked directly.  Both
selectors are proved by embedded staged Farkas identities, replayed
coefficient by coefficient with stdlib Fractions (no LP, no project import):
each identity bounds the stage value and forces one player of the new
stratum onto it, and attainment by the displayed vector finishes the stage.
Finally rho=||Lmin-Lmax||_1/T is compared with the formula value
2-8n/(n^2-(n mod 2)).
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

GAMES = [
 {
  "name": "H8",
  "label": "eight players",
  "generators": [
   [
    2,
    12,
    20,
    2,
    2,
    2,
    2,
    2
   ],
   [
    0,
    0,
    0,
    18,
    10,
    10,
    6,
    0
   ],
   [
    0,
    16,
    28,
    0,
    0,
    0,
    0,
    0
   ],
   [
    0,
    0,
    15,
    3,
    10,
    10,
    6,
    0
   ]
  ],
  "Lmin": [
   "2",
   "12",
   "20",
   "2",
   "2",
   "2",
   "2",
   "2"
  ],
  "Lmax": [
   "1/5",
   "6/5",
   "46/5",
   "46/5",
   "46/5",
   "46/5",
   "28/5",
   "1/5"
  ],
  "min_certificates": [
   {
    "player": 0,
    "level": "2",
    "rows": {
     "98": "1",
     "156": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {}
   },
   {
    "player": 3,
    "level": "2",
    "rows": {
     "62": "2",
     "76": "1",
     "82": "1",
     "98": "1",
     "116": "1"
    },
    "eff": "4",
    "fixed": {},
    "stage": {
     "0": "4",
     "7": "4"
    }
   },
   {
    "player": 4,
    "level": "2",
    "rows": {
     "62": "1",
     "76": "1",
     "98": "1"
    },
    "eff": "2",
    "fixed": {},
    "stage": {
     "0": "2",
     "7": "2"
    }
   },
   {
    "player": 5,
    "level": "2",
    "rows": {
     "62": "1",
     "76": "1",
     "82": "1"
    },
    "eff": "2",
    "fixed": {},
    "stage": {
     "0": "2",
     "7": "2"
    }
   },
   {
    "player": 6,
    "level": "2",
    "rows": {
     "62": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {
     "0": "1",
     "7": "1"
    }
   },
   {
    "player": 7,
    "level": "2",
    "rows": {
     "45": "1",
     "82": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {}
   },
   {
    "player": 1,
    "level": "12",
    "rows": {
     "50": "1",
     "98": "1",
     "172": "1",
     "220": "2"
    },
    "eff": "3",
    "fixed": {
     "0": "-3"
    },
    "stage": {}
   },
   {
    "player": 2,
    "level": "20",
    "rows": {
     "82": "1",
     "98": "1",
     "188": "1"
    },
    "eff": "2",
    "fixed": {
     "0": "-2",
     "3": "-1",
     "7": "-1"
    },
    "stage": {}
   }
  ],
  "max_certificates": [
   {
    "player": 2,
    "level": "46/5",
    "rows": {
     "62": "1/2",
     "76": "1/2",
     "157": "1/2"
    },
    "eff": "1/2",
    "fixed": {},
    "stage": {
     "3": "1",
     "4": "1/2"
    }
   },
   {
    "player": 3,
    "level": "46/5",
    "rows": {
     "62": "1/2",
     "76": "1/2",
     "157": "1/2"
    },
    "eff": "1/2",
    "fixed": {},
    "stage": {
     "2": "1",
     "4": "1/2"
    }
   },
   {
    "player": 4,
    "level": "46/5",
    "rows": {
     "62": "1",
     "76": "1",
     "157": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {
     "2": "2",
     "3": "2"
    }
   },
   {
    "player": 5,
    "level": "46/5",
    "rows": {
     "62": "1",
     "76": "1",
     "173": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {
     "2": "2",
     "3": "2"
    }
   },
   {
    "player": 6,
    "level": "28/5",
    "rows": {
     "76": "1"
    },
    "eff": "0",
    "fixed": {
     "2": "1",
     "3": "1"
    },
    "stage": {}
   },
   {
    "player": 1,
    "level": "6/5",
    "rows": {
     "62": "1",
     "82": "1",
     "157": "1"
    },
    "eff": "1",
    "fixed": {
     "2": "1",
     "3": "1",
     "4": "2"
    },
    "stage": {}
   },
   {
    "player": 0,
    "level": "1/5",
    "rows": {
     "157": "1"
    },
    "eff": "0",
    "fixed": {
     "2": "1",
     "3": "1",
     "4": "1"
    },
    "stage": {
     "7": "1"
    }
   },
   {
    "player": 7,
    "level": "1/5",
    "rows": {
     "157": "1"
    },
    "eff": "0",
    "fixed": {
     "2": "1",
     "3": "1",
     "4": "1"
    },
    "stage": {
     "0": "1"
    }
   }
  ]
 },
 {
  "name": "H9",
  "label": "nine players",
  "generators": [
   [
    1,
    9,
    15,
    1,
    1,
    1,
    1,
    1,
    1
   ],
   [
    0,
    0,
    0,
    13,
    7,
    7,
    4,
    0,
    0
   ],
   [
    0,
    11,
    20,
    0,
    0,
    0,
    0,
    0,
    0
   ],
   [
    0,
    0,
    11,
    2,
    7,
    7,
    4,
    0,
    0
   ]
  ],
  "Lmin": [
   "1",
   "9",
   "15",
   "1",
   "1",
   "1",
   "1",
   "1",
   "1"
  ],
  "Lmax": [
   "1/15",
   "3/5",
   "33/5",
   "33/5",
   "33/5",
   "33/5",
   "19/5",
   "1/15",
   "1/15"
  ],
  "min_certificates": [
   {
    "player": 0,
    "level": "1",
    "rows": {
     "98": "1",
     "412": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {}
   },
   {
    "player": 3,
    "level": "1",
    "rows": {
     "62": "2",
     "76": "1",
     "82": "1",
     "98": "1",
     "116": "1"
    },
    "eff": "4",
    "fixed": {},
    "stage": {
     "0": "4",
     "7": "4",
     "8": "4"
    }
   },
   {
    "player": 4,
    "level": "1",
    "rows": {
     "62": "1",
     "76": "1",
     "98": "1"
    },
    "eff": "2",
    "fixed": {},
    "stage": {
     "0": "2",
     "7": "2",
     "8": "2"
    }
   },
   {
    "player": 5,
    "level": "1",
    "rows": {
     "62": "1",
     "76": "1",
     "82": "1"
    },
    "eff": "2",
    "fixed": {},
    "stage": {
     "0": "2",
     "7": "2",
     "8": "2"
    }
   },
   {
    "player": 6,
    "level": "1",
    "rows": {
     "62": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {
     "0": "1",
     "7": "1",
     "8": "1"
    }
   },
   {
    "player": 7,
    "level": "1",
    "rows": {
     "98": "1",
     "285": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {}
   },
   {
    "player": 8,
    "level": "1",
    "rows": {
     "98": "1",
     "157": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {}
   },
   {
    "player": 1,
    "level": "9",
    "rows": {
     "50": "1",
     "98": "1",
     "429": "1",
     "476": "2"
    },
    "eff": "3",
    "fixed": {
     "0": "-2"
    },
    "stage": {}
   },
   {
    "player": 2,
    "level": "15",
    "rows": {
     "50": "1",
     "98": "1",
     "348": "1"
    },
    "eff": "2",
    "fixed": {
     "0": "-2",
     "3": "-1",
     "7": "-2",
     "8": "-1"
    },
    "stage": {}
   }
  ],
  "max_certificates": [
   {
    "player": 2,
    "level": "33/5",
    "rows": {
     "62": "1/2",
     "76": "1/2",
     "413": "1/2"
    },
    "eff": "1/2",
    "fixed": {},
    "stage": {
     "3": "1",
     "4": "1/2"
    }
   },
   {
    "player": 3,
    "level": "33/5",
    "rows": {
     "62": "1/2",
     "76": "1/2",
     "413": "1/2"
    },
    "eff": "1/2",
    "fixed": {},
    "stage": {
     "2": "1",
     "4": "1/2"
    }
   },
   {
    "player": 4,
    "level": "33/5",
    "rows": {
     "62": "1",
     "76": "1",
     "413": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {
     "2": "2",
     "3": "2"
    }
   },
   {
    "player": 5,
    "level": "33/5",
    "rows": {
     "62": "1",
     "76": "1",
     "429": "1"
    },
    "eff": "1",
    "fixed": {},
    "stage": {
     "2": "2",
     "3": "2"
    }
   },
   {
    "player": 6,
    "level": "19/5",
    "rows": {
     "76": "1"
    },
    "eff": "0",
    "fixed": {
     "2": "1",
     "3": "1"
    },
    "stage": {}
   },
   {
    "player": 1,
    "level": "3/5",
    "rows": {
     "62": "1",
     "82": "1",
     "413": "1"
    },
    "eff": "1",
    "fixed": {
     "2": "1",
     "3": "1",
     "4": "2"
    },
    "stage": {}
   },
   {
    "player": 0,
    "level": "1/15",
    "rows": {
     "413": "1"
    },
    "eff": "0",
    "fixed": {
     "2": "1",
     "3": "1",
     "4": "1"
    },
    "stage": {
     "7": "1",
     "8": "1"
    }
   },
   {
    "player": 7,
    "level": "1/15",
    "rows": {
     "413": "1"
    },
    "eff": "0",
    "fixed": {
     "2": "1",
     "3": "1",
     "4": "1"
    },
    "stage": {
     "0": "1",
     "8": "1"
    }
   },
   {
    "player": 8,
    "level": "1/15",
    "rows": {
     "413": "1"
    },
    "eff": "0",
    "fixed": {
     "2": "1",
     "3": "1",
     "4": "1"
    },
    "stage": {
     "0": "1",
     "7": "1"
    }
   }
  ]
 }
]


def formula(n):
    return F(2) - F(8 * n, n * n - (n % 2))


def csum(point, coalition, n):
    return sum((point[i] for i in range(n) if coalition >> i & 1), F(0))


def check_certificate(mode, point, level, cert, pinned, unfixed, V, T, n):
    player = cert["player"]
    sgn = -1 if mode == "min" else 1
    vec = [F(0)] * n
    for coalition, lam in cert["rows"].items():
        coalition = int(coalition); lam = F(lam)
        assert lam >= 0
        for i in range(n):
            if coalition >> i & 1:
                vec[i] += sgn * lam
    eff = F(cert["eff"])
    vec = [c - sgn * eff for c in vec]
    for j, nu in cert["fixed"].items():
        j = int(j); assert j in pinned
        vec[j] += F(nu) * (1 if mode == "min" else -1)
    for j, beta in cert["stage"].items():
        j = int(j); beta = F(beta)
        assert beta >= 0 and j in unfixed and j != player
        vec[j] -= beta
    assert vec == [F(1 if i == player else 0) for i in range(n)], ("identity", mode, player, vec)
    constant = sgn * sum(F(lam) * V[int(s)] for s, lam in cert["rows"].items()) - sgn * eff * T
    constant += sum(F(nu) * point[int(j)] for j, nu in cert["fixed"].items()) * (1 if mode == "min" else -1)
    beta_total = sum((F(b) for b in cert["stage"].values()), F(0))
    assert constant / (1 + beta_total) == level, ("stage value", mode, player)
    assert constant - beta_total * level == level, ("forced bound", mode, player)


def replay(mode, point, certs, V, T, n):
    pinned, unfixed, stages = {}, set(range(n)), []
    remaining = list(certs)
    while unfixed:
        level = F(remaining[0]["level"])
        block = [c["player"] for c in remaining if F(c["level"]) == level]
        assert block and set(block) <= unfixed
        for c in [c for c in remaining if F(c["level"]) == level]:
            assert point[c["player"]] == level
            check_certificate(mode, point, level, c, pinned, unfixed, V, T, n)
        for j in unfixed:
            if j not in block:
                assert (point[j] > level) if mode == "min" else (point[j] < level), ("block incomplete", mode, j)
        for j in block:
            pinned[j] = level; unfixed.remove(j)
        remaining = [c for c in remaining if F(c["level"]) != level]
        stages.append({"level": str(level), "block": block})
    assert not remaining
    return stages


def verify(game):
    gens = [[F(a) for a in g] for g in game["generators"]]
    n = len(gens[0]); T = sum(gens[0])
    assert all(sum(g) == T and min(g) >= 0 for g in gens)
    V = [min(csum(g, s, n) for g in gens) for s in range(1 << n)]
    assert V[-1] == T and all(V[1 << i] == 0 for i in range(n)), "normalization"
    for s in range(1 << n):
        assert any(csum(g, s, n) == V[s] for g in gens)
    x = [F(a) for a in game["Lmin"]]; z = [F(a) for a in game["Lmax"]]
    for point in (x, z):
        assert sum(point) == T and all(csum(point, s, n) >= V[s] for s in range(1 << n)), "selector outside core"
    xs = replay("min", x, game["min_certificates"], V, T, n)
    zs = replay("max", z, game["max_certificates"], V, T, n)
    distance = sum(abs(a - b) for a, b in zip(x, z)); rho = distance / T
    overlap = sum(min(a, b) for a, b in zip(x, z))
    assert rho > formula(n), ("no violation", rho, formula(n))
    return {"name": game["name"], "n": n, "total": str(T), "generators": game["generators"],
            "Lmin": game["Lmin"], "Lmax": game["Lmax"], "Lmin_stages": xs, "Lmax_stages": zs,
            "rho": str(rho), "formula_value": str(formula(n)), "excess": str(rho - formula(n)),
            "overlap_over_T": str(overlap / T), "formula_overlap_floor": str(F(n, (n * n) // 4))}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); args = parser.parse_args()
    results = [verify(game) for game in GAMES]
    payload = {"claim": "PXC145: the formula s(n)=2-8n/(n^2-(n mod 2)) is exceeded by explicit exact games at n=8 and n=9",
               "method": "LP-free replay of embedded staged Farkas identities (stdlib Fractions only)",
               "games": results}
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
