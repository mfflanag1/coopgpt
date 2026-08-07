"""Parse the Studeny-Kratochvil electronic catalogue of indecomposable
min-semi-balanced systems and expose a permutational-type lookup.

Catalogue convention (from the site's own definitions page):
  sum_{S in curly-S} lambda_S chi_S = r * 1_N,  integers, gcd 1,
  at most one lambda_S < 0 (the exceptional set T),
  lambda_N := r  and  lambda_empty := -r + sum_S lambda_S,  both >= 0.

The CSV stores, for each permutational type, one row whose columns are
  [lambda_empty] [proper subsets in a fixed order] [N]
and whose proper-subset entries are the NEGATED lambda_S.  decode() checks
that identity on every row rather than assuming it.
"""
from __future__ import annotations

import csv
import itertools
from math import gcd
from pathlib import Path

CATDIR = Path(__file__).resolve().parent / "cat"


def _mask(name, letters):
    return sum(1 << letters.index(ch) for ch in name)


def load(n):
    """Return (letters, [row]) where row = {'lam': {mask: int}, 'r': int,
    'lam_empty': int, 'exceptional': mask or None}."""
    letters = "abcdefgh"[:n]
    full = (1 << n) - 1
    path = CATDIR / f"n{n}.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh, delimiter=";"))
    header = rows[0]
    assert header[0] == "", header[:2]
    cols = [_mask(name, letters) for name in header[1:]]
    assert cols[-1] == full, "last column is not the grand coalition"
    out = []
    for raw in rows[1:]:
        vals = [int(x) for x in raw]
        lam_empty_csv = vals[0]
        r = vals[-1]
        lam = {}
        for mask, val in zip(cols[:-1], vals[1:-1]):
            if val:
                lam[mask] = -val            # CSV stores -lambda_S
        # verify balance
        load_vec = [sum(c for m, c in lam.items() if m >> i & 1) for i in range(n)]
        assert load_vec == [r] * n, (raw, load_vec, r)
        assert -r + sum(lam.values()) == lam_empty_csv, (raw, lam, r)
        assert gcd(*[abs(c) for c in lam.values()], 0) == 1 or len(lam) == 1
        neg = [m for m, c in lam.items() if c < 0]
        assert len(neg) <= 1, raw
        out.append({
            "lam": lam,
            "r": r,
            "lam_empty": lam_empty_csv,
            "exceptional": neg[0] if neg else None,
        })
    return letters, out


def canon(n, lam):
    """Canonical key of a semi-balanced system up to permutation of N.

    Input lam: {mask: integer coefficient}.  Coefficients are first reduced by
    their gcd so that the key is scale-free, matching the catalogue's
    normalization.
    """
    g = 0
    for c in lam.values():
        g = gcd(g, abs(c))
    assert g, "empty system"
    red = {m: c // g for m, c in lam.items()}
    best = None
    for perm in itertools.permutations(range(n)):
        key = tuple(sorted(
            (sum(1 << perm[i] for i in range(n) if m >> i & 1), c)
            for m, c in red.items()
        ))
        if best is None or key < best:
            best = key
    return best


def index(n):
    """canon-key -> list of catalogue row numbers (1-based within the CSV)."""
    _, rows = load(n)
    table = {}
    for k, row in enumerate(rows, start=1):
        table.setdefault(canon(n, row["lam"]), []).append(k)
    return table, rows


def pretty(n, lam):
    letters = "abcdefgh"[:n]
    def nm(m):
        return "".join(letters[i] for i in range(n) if m >> i & 1)
    parts = []
    for m, c in sorted(lam.items(), key=lambda kv: (bin(kv[0]).count("1"), kv[0])):
        parts.append(f"{c:+d}*{nm(m)}")
    return " ".join(parts)


if __name__ == "__main__":
    for n in (3, 4, 5, 6):
        letters, rows = load(n)
        sing = [row for row in rows
                if row["exceptional"] is not None
                and bin(row["exceptional"]).count("1") == 1]
        table, _ = index(n)
        print(f"n={n}: {len(rows)} rows, {len(table)} distinct permutational types, "
              f"{len(sing)} with singleton exceptional set, "
              f"{sum(1 for r in rows if r['exceptional'] is None)} purely balanced (no exceptional)")
