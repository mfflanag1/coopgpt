"""Exact payment rules for small, fixed-owner production-game experiments.

The caller supplies a homogeneous monotone production value and, where needed,
the complete fixed family of dual vertices defining that value. Enumeration is
exponential in owner count; this module makes no large-instance runtime claim.
All numerical inputs are exact rationals. Finite tests of this code are not a
proof of its mechanisms' all-profile incentive or coverage guarantees.
"""

from fractions import Fraction as Q
from functools import lru_cache
from math import comb, factorial


RULES = ("proportional", "dual", "marginal", "shapley", "sharp_hybrid")


def rational(x):
    """Convert exact input without silently accepting binary floating point."""
    if isinstance(x, float):
        raise ValueError("Use exact rational inputs, not floats")
    return Q(x)


def dot(a, b):
    if len(a) != len(b):
        raise ValueError("Dot-product dimensions differ")
    return sum((rational(x) * rational(y) for x, y in zip(a, b)), Q(0))


def aggregate(bundles, members=None):
    if not bundles or not bundles[0]:
        raise ValueError("At least one owner and resource are required")
    d = len(bundles[0])
    if any(len(b) != d for b in bundles):
        raise ValueError("Owner bundles have different dimensions")
    members = tuple(range(len(bundles)) if members is None else members)
    return tuple(sum((rational(bundles[i][e]) for i in members), Q(0))
                 for e in range(d))


@lru_cache(None)
def integral_q_power(a, b, upper):
    """Exact integral of q**a * (1-q)**b from zero to upper."""
    if (not isinstance(a, int) or not isinstance(b, int)
            or a < 0 or b < 0):
        raise ValueError("Polynomial exponents must be nonnegative integers")
    upper = rational(upper)
    if not 0 <= upper <= 1:
        raise ValueError("Integration endpoint must be in [0,1]")
    return sum(((-1)**h * comb(b, h) * upper**(a+h+1) / (a+h+1)
                for h in range(b+1)), Q(0))


def payments(rule, bundles, value, dual_vertices, weights=None, j=2):
    """Return one exact nonnegative payment per owner.

    ``value`` takes an aggregate capacity tuple. ``dual_vertices`` is the fixed
    report-independent family: duplicates are removed and lexicographic order
    supplies tie priority. It may be None for rules other than dual and hybrid.
    Proportional allocation uses fixed strictly positive resource-unit weights,
    defaulting to one per resource; it does not use endogenous shadow prices.
    Hybrid uses an integer j >= 2 fixed independently of the report profile.
    """
    if rule not in RULES:
        raise ValueError("Unknown payment rule: " + str(rule))
    bundles = tuple(tuple(rational(x) for x in b) for b in bundles)
    capacity = aggregate(bundles)
    n, d = len(bundles), len(capacity)
    if any(x < 0 for b in bundles for x in b):
        raise ValueError("Owner capacities must be nonnegative")
    forms = None
    if rule in ("dual", "sharp_hybrid"):
        if dual_vertices is None:
            raise ValueError("This rule requires a fixed dual-vertex family")
        forms = tuple(sorted(set(tuple(rational(x) for x in w)
                                 for w in dual_vertices)))
        if not forms or any(len(w) != d or any(x < 0 for x in w)
                            for w in forms):
            raise ValueError("Dual forms must be nonempty, nonnegative and dimensionally valid")
    if rule == "sharp_hybrid" and (
            not isinstance(j, int) or isinstance(j, bool) or j < 2):
        raise ValueError("Hybrid j must be an integer at least two")
    if rule == "proportional":
        weights = (Q(1),) * d if weights is None else tuple(map(rational, weights))
        if len(weights) != d or any(x <= 0 for x in weights):
            raise ValueError("Proportional resource weights must be strictly positive")

    @lru_cache(None)
    def coalition(mask):
        members = tuple(i for i in range(n) if mask >> i & 1)
        c = aggregate(bundles, members)
        v = rational(value(c))
        if v < 0:
            raise ValueError("Production values must be nonnegative")
        return c, v

    full = (1 << n) - 1
    total = coalition(full)[1]
    if coalition(0)[1] != 0:
        raise ValueError("Production must vanish at zero capacity")
    if total == 0:
        return (Q(0),) * n

    @lru_cache(None)
    def selected_form(mask):
        c, v = coalition(mask)
        chosen = min(forms, key=lambda w: dot(w, c))
        if dot(chosen, c) != v:
            raise ValueError("Supplied dual forms do not reproduce production value")
        return chosen

    if rule == "proportional":
        scores = tuple(dot(weights, b) for b in bundles)
        score_total = sum(scores, Q(0))
        if score_total == 0:
            raise ValueError("Positive production has zero proportional score")
        result = tuple(total * score / score_total for score in scores)
    elif rule == "dual":
        chosen = selected_form(full)
        result = tuple(dot(chosen, b) for b in bundles)
    elif rule == "marginal":
        result = tuple(total - coalition(full ^ (1 << i))[1] for i in range(n))
    else:
        result = []
        for i in range(n):
            payment = Q(0)
            for mask in range(1 << n):
                if mask >> i & 1:
                    continue
                k = mask.bit_count()
                increment = coalition(mask | (1 << i))[1] - coalition(mask)[1]
                if increment < 0:
                    raise ValueError("Production is not monotone on evaluated coalitions")
                if rule == "shapley":
                    coefficient = Q(factorial(k) * factorial(n-k-1), factorial(n))
                    payment += coefficient * increment
                else:
                    # Select with uncapped scores; cap only the own payment.
                    own = min(dot(selected_form(mask), bundles[i]), total)
                    off = n - 1 - k
                    payment += j * (
                        integral_q_power(off+1, k, Q(1, j)) * own
                        + integral_q_power(off, k+1, Q(1, j)) * increment)
            result.append(payment)
        result = tuple(result)
    if any(x < 0 for x in result):
        raise ValueError("Negative payment: production assumptions are violated")
    return result
