#!/usr/bin/env python3
"""Independent exact checker for 'core-witness-v1' certificates.

Standard library only.  Does not import the solver or generator and shares
no layout or coefficient code with them.  Every scientific check raises
CertificateError (a ValueError) explicitly; no check relies on ``assert``,
so behaviour is identical under ``python -O``.

Conventions (reconstructed from CHECKER_CONTRACT.md / FORMULATION.md):
  * three sectors A, B, C with m players each; global id = sector*m + label;
  * pair types 0 = AB, 1 = AC, 2 = BC; matrices[t][row][col] is indexed by
    the labels of the first and second sector named in the type;
  * a team (a, b, c) has worth AB[a][b] + AC[a][c] + BC[b][c];
  * the support is the set of pairs of the diagonal teams (j, j, j) and of
    the teams of P.

Public API: ``check(data) -> dict``; raises on any invalid certificate.
CLI: ``python check_certificate.py CERT.json`` (exit 0 accepted, 1 rejected).
"""

import json
import re
import sys
from fractions import Fraction

SCHEMA = "core-witness-v1"

# Exact rational strings only: integer, integer/integer, or plain decimal.
# Exponent forms, nan/inf, underscores and whitespace are rejected.
_RATIONAL_RE = re.compile(r"[+-]?[0-9]+(?:/[0-9]+|\.[0-9]+)?\Z")
_MAX_RATIONAL_CHARS = 4000


class CertificateError(ValueError):
    """Raised when a certificate is malformed or fails an exact check."""


def _fail(message):
    raise CertificateError(message)


def _is_int(value):
    # bool is a subclass of int and is forbidden everywhere.
    return type(value) is int


def _rational(value, where):
    if type(value) is int:
        return Fraction(value)
    if type(value) is str:
        if len(value) > _MAX_RATIONAL_CHARS:
            _fail("%s: rational string too long" % where)
        if _RATIONAL_RE.match(value) is None:
            _fail("%s: not an exact rational string: %r" % (where, value))
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError):
            _fail("%s: not an exact rational string: %r" % (where, value))
    _fail(
        "%s: rational must be an int or a rational string, got %s"
        % (where, type(value).__name__)
    )


def _field(mapping, key, where):
    if key not in mapping:
        _fail("%s: missing field %r" % (where, key))
    return mapping[key]


def _list(value, where, length=None):
    if type(value) is not list:
        _fail("%s: expected a list, got %s" % (where, type(value).__name__))
    if length is not None and len(value) != length:
        _fail("%s: expected length %d, got %d" % (where, length, len(value)))
    return value


def _team_pairs(a, b, c):
    """The three (pair_type, row, col) positions of team (a, b, c)."""
    return ((0, a, b), (1, a, c), (2, b, c))


def check(data):
    """Verify a core-witness-v1 certificate exactly.

    Returns a dict with exact rational strings 'lower', 'upper', 'gap', the
    boolean 'equal' (lower == upper) and dimensions.  Raises CertificateError
    (a ValueError) on any defect.  No threshold such as upper < 1/3 and no
    optimality (lower == upper) is required for acceptance.
    """
    if type(data) is not dict:
        _fail("certificate must be a JSON object")

    if _field(data, "schema", "certificate") != SCHEMA:
        _fail("schema must be %r" % SCHEMA)

    m = _field(data, "m", "certificate")
    if not _is_int(m) or m < 1:
        _fail("m must be a positive integer (bool forbidden)")

    # ---- P: sector-wise disjoint partial matching --------------------
    raw_p = _list(_field(data, "P", "certificate"), "P")
    if len(raw_p) > m:
        _fail("P has more than m triples")
    p_teams = []
    used = (set(), set(), set())
    for idx, triple in enumerate(raw_p):
        where = "P[%d]" % idx
        _list(triple, where, 3)
        for sector in range(3):
            label = triple[sector]
            if not _is_int(label) or label < 0 or label >= m:
                _fail("%s: label out of range or not an integer" % where)
            if label in used[sector]:
                _fail("%s: P is not sector-wise disjoint" % where)
            used[sector].add(label)
        p_teams.append((triple[0], triple[1], triple[2]))

    # ---- unmatched set ------------------------------------------------
    unmatched = [
        sector * m + label
        for sector in range(3)
        for label in range(m)
        if label not in used[sector]
    ]
    raw_unmatched = _list(_field(data, "unmatched", "certificate"), "unmatched")
    for value in raw_unmatched:
        if not _is_int(value):
            _fail("unmatched: entries must be integers")
    if raw_unmatched != unmatched:
        _fail("unmatched does not match the sorted reconstruction from P")

    # ---- support ------------------------------------------------------
    support_set = set()
    for j in range(m):
        support_set.update(_team_pairs(j, j, j))
    for (a, b, c) in p_teams:
        support_set.update(_team_pairs(a, b, c))
    support = sorted(support_set)
    raw_support = _list(_field(data, "support", "certificate"), "support")
    if len(raw_support) != len(support):
        _fail("support does not match the reconstruction (wrong size)")
    for idx, entry in enumerate(raw_support):
        _list(entry, "support[%d]" % idx, 3)
        for value in entry:
            if not _is_int(value):
                _fail("support[%d]: entries must be integers" % idx)
        if (entry[0], entry[1], entry[2]) != support[idx]:
            _fail(
                "support[%d] does not match the sorted reconstruction" % idx
            )

    # ---- matrices -----------------------------------------------------
    raw_matrices = _list(_field(data, "matrices", "certificate"), "matrices", 3)
    mats = []
    for t in range(3):
        rows = _list(raw_matrices[t], "matrices[%d]" % t, m)
        mat = []
        for r in range(m):
            row = _list(rows[r], "matrices[%d][%d]" % (t, r), m)
            parsed = []
            for col in range(m):
                where = "matrices[%d][%d][%d]" % (t, r, col)
                value = _rational(row[col], where)
                if value < 0:
                    _fail("%s: negative weight" % where)
                if (t, r, col) in support_set:
                    if value > 1:
                        _fail("%s: supported weight exceeds 1" % where)
                elif value != 0:
                    _fail("%s: nonzero weight outside the support" % where)
                parsed.append(value)
            mat.append(parsed)
        mats.append(mat)

    def worth(a, b, c):
        return mats[0][a][b] + mats[1][a][c] + mats[2][b][c]

    diagonal_total = sum((worth(j, j, j) for j in range(m)), Fraction(0))
    if diagonal_total != 1:
        _fail("diagonal team values sum to %s, not 1" % diagonal_total)

    # ---- witness targets ---------------------------------------------
    dummy = len(unmatched) == 0
    targets = [-1] if dummy else list(unmatched)
    raw_targets = _list(
        _field(data, "witness_targets", "certificate"), "witness_targets"
    )
    for value in raw_targets:
        if not _is_int(value):
            _fail("witness_targets: entries must be integers")
    if raw_targets != targets:
        _fail("witness_targets does not match the reconstruction")
    target_index = {}
    for idx, target in enumerate(targets):
        target_index[target] = idx
    n_targets = len(targets)

    # ---- witnesses: nonnegative, total 1, cover every triple ---------
    raw_witnesses = _list(
        _field(data, "witnesses", "certificate"), "witnesses", n_targets
    )
    witnesses = []
    for idx in range(n_targets):
        where = "witnesses[%d]" % idx
        raw_x = _list(raw_witnesses[idx], where, 3 * m)
        x = []
        for k in range(3 * m):
            value = _rational(raw_x[k], "%s[%d]" % (where, k))
            if value < 0:
                _fail("%s[%d]: negative payoff" % (where, k))
            if value > 1:
                _fail("%s[%d]: payoff exceeds 1" % (where, k))
            x.append(value)
        total = sum(x, Fraction(0))
        if total != 1:
            _fail("%s: payoffs sum to %s, not 1" % (where, total))
        for a in range(m):
            xa = x[a]
            for b in range(m):
                xab = xa + x[m + b]
                wab = mats[0][a][b]
                for c in range(m):
                    if xab + x[2 * m + c] < wab + mats[1][a][c] + mats[2][b][c]:
                        _fail(
                            "%s: core violation at team (%d, %d, %d)"
                            % (where, a, b, c)
                        )
        witnesses.append(x)

    # ---- primal objective --------------------------------------------
    lower = sum((worth(a, b, c) for (a, b, c) in p_teams), Fraction(0))
    if not dummy:
        own = Fraction(0)
        for idx, target in enumerate(targets):
            own += witnesses[idx][target]
        lower += own / 3
    lower -= 1
    claimed_j = _rational(_field(data, "primal_J", "certificate"), "primal_J")
    if claimed_j != lower:
        _fail(
            "primal_J mismatch: claimed %s, recomputed %s" % (claimed_j, lower)
        )

    # ---- dual certificate --------------------------------------------
    dual = _field(data, "dual", "certificate")
    if type(dual) is not dict:
        _fail("dual must be a JSON object")
    nu0 = _rational(_field(dual, "normalization", "dual"), "dual.normalization")
    raw_totals = _list(_field(dual, "totals", "dual"), "dual.totals", n_targets)
    nus = [
        _rational(raw_totals[idx], "dual.totals[%d]" % idx)
        for idx in range(n_targets)
    ]
    claimed_upper = _rational(_field(dual, "upper", "dual"), "dual.upper")

    # Residual r = c - A^T lambda - B^T nu, one entry per LP variable.
    res_w = {}
    for position in support:
        res_w[position] = Fraction(0)
    res_x = [[Fraction(0)] * (3 * m) for _ in range(n_targets)]

    # Objective 3*w(P) + sum of true target coordinates.
    for (a, b, c) in p_teams:
        for position in _team_pairs(a, b, c):
            res_w[position] += 3
    if not dummy:
        for idx, target in enumerate(targets):
            res_x[idx][target] += 1

    # Inequality rows: team weight minus witness payoff <= 0.
    raw_lambda = _list(_field(dual, "lambda", "dual"), "dual.lambda")
    seen_rows = set()
    for idx, entry in enumerate(raw_lambda):
        where = "dual.lambda[%d]" % idx
        _list(entry, where, 5)
        target, a, b, c = entry[0], entry[1], entry[2], entry[3]
        if not _is_int(target) or target not in target_index:
            _fail("%s: target is not a witness target" % where)
        for label in (a, b, c):
            if not _is_int(label) or label < 0 or label >= m:
                _fail("%s: invalid team label" % where)
        key = (target, a, b, c)
        if key in seen_rows:
            _fail("%s: duplicate (target, a, b, c)" % where)
        seen_rows.add(key)
        mass = _rational(entry[4], "%s mass" % where)
        if mass < 0:
            _fail("%s: negative multiplier" % where)
        for position in _team_pairs(a, b, c):
            if position in res_w:
                res_w[position] -= mass
        row = res_x[target_index[target]]
        row[a] += mass
        row[m + b] += mass
        row[2 * m + c] += mass

    # Equality rows: diagonal total, then each witness total.
    for j in range(m):
        for position in _team_pairs(j, j, j):
            res_w[position] -= nu0
    for idx in range(n_targets):
        nu = nus[idx]
        row = res_x[idx]
        for k in range(3 * m):
            row[k] -= nu

    positive = Fraction(0)
    for value in res_w.values():
        if value > 0:
            positive += value
    for row in res_x:
        for value in row:
            if value > 0:
                positive += value

    upper = (nu0 + sum(nus, Fraction(0)) + positive) / 3 - 1
    if claimed_upper != upper:
        _fail(
            "dual upper mismatch: claimed %s, exact residual bound %s"
            % (claimed_upper, upper)
        )
    if lower > upper:
        _fail("primal_J %s exceeds dual upper bound %s" % (lower, upper))

    return {
        "schema": SCHEMA,
        "accepted": True,
        "m": m,
        "lower": str(lower),
        "upper": str(upper),
        "gap": str(upper - lower),
        "equal": lower == upper,
        "dummy_witness": dummy,
        "num_P": len(p_teams),
        "num_unmatched": len(unmatched),
        "num_targets": n_targets,
        "num_support": len(support),
        "num_triples": m * m * m,
        "num_cover_checks": n_targets * m * m * m,
        "num_lambda": len(raw_lambda),
        "num_variables": len(support) + n_targets * 3 * m,
    }


def _reject_constant(name):
    raise CertificateError("non-finite JSON constant %s is not allowed" % name)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CertificateError("duplicate JSON key %r" % key)
        result[key] = value
    return result


def load(path):
    """Load certificate JSON, rejecting NaN/Infinity and duplicate keys."""
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(
            handle,
            parse_constant=_reject_constant,
            object_pairs_hook=_unique_object,
        )


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    if len(args) != 1:
        sys.stderr.write("usage: check_certificate.py CERTIFICATE.json\n")
        return 2
    try:
        result = check(load(args[0]))
    except Exception as exc:  # fail closed on anything unexpected
        sys.stderr.write("REJECTED: %s: %s\n" % (type(exc).__name__, exc))
        return 1
    sys.stdout.write(json.dumps(result, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
