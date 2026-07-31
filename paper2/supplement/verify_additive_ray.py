"""Symbolic exact certificate for the one-parameter Paper 2 perturbation.

For c(t)=(t,0,0,0,t,0), t >= 0, this script proves the procedural-claim
formulas on each open parameter interval by checking affine inequalities at
the interval endpoints (and slopes on the unbounded interval).  It separately
checks the breakpoints t=0, 2/3, 1 with exact rational arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F



def members(S, n=6):
    return [i for i in range(n) if S >> i & 1]


@dataclass(frozen=True)
class Aff:
    slope: F = F(0)
    intercept: F = F(0)

    def __add__(self, other):
        other = as_aff(other)
        return Aff(self.slope + other.slope, self.intercept + other.intercept)

    __radd__ = __add__

    def __sub__(self, other):
        other = as_aff(other)
        return Aff(self.slope - other.slope, self.intercept - other.intercept)

    def __rsub__(self, other):
        return as_aff(other) - self

    def __truediv__(self, denominator):
        return Aff(self.slope / denominator, self.intercept / denominator)

    def at(self, t):
        return self.slope * t + self.intercept


def as_aff(value):
    return value if isinstance(value, Aff) else Aff(F(0), F(value))


U = (0, 1, 0, 1, 2, 0)
V = (1, 0, 1, 0, 0, 2)
N = (1 << 6) - 1


def additive_values(c):
    values = [F(0)] * (N + 1)
    for S in range(1, N + 1):
        mem = members(S)
        values[S] = min(sum(U[i] for i in mem), sum(V[i] for i in mem)) + sum(
            c[i] for i in mem
        )
    return values


def procedure_trace(values):
    fixed = {}
    rounds = []
    final_A = []
    for _ in range(7):
        if len(fixed) == 6:
            break
        chi = {}
        maxima = {i: None for i in range(6)}
        for S in range(1, N + 1):
            mem = members(S)
            free = [i for i in mem if i not in fixed]
            fixed_sum = sum((fixed[i] for i in mem if i in fixed), F(0))
            share = (values[S] - fixed_sum) / len(free) if free else None
            chi[S] = {i: (fixed[i] if i in fixed else share) for i in mem}
            for i in mem:
                if maxima[i] is None or chi[S][i] > maxima[i]:
                    maxima[i] = chi[S][i]
        A = []
        for S in range(1, N + 1):
            mem = members(S)
            if sum((chi[S][i] for i in mem), F(0)) != values[S]:
                continue
            if all(chi[S][i] == maxima[i] for i in mem):
                A.append(S)
        before = set(fixed)
        for S in A:
            for i in members(S):
                if i not in fixed:
                    fixed[i] = maxima[i]
        rounds.append((tuple(A), tuple(sorted(set(fixed) - before))))
        final_A = A
    return tuple(fixed[i] for i in range(6)), N in final_A, tuple(rounds)


def worth(S):
    mem = members(S, 6)
    base = min(sum(U[i] for i in mem), sum(V[i] for i in mem))
    return Aff(sum(1 for i in mem if i in (0, 4)), F(base))


def nonnegative_on_interval(form, lo, hi):
    """Check form(t)>=0 on the closed interval; hi=None means +infinity."""
    if form.at(lo) < 0:
        return False
    if hi is None:
        return form.slope >= 0
    return form.at(hi) >= 0


def certify_piece(lo, hi, strata, claims):
    """Certify one trace on the open interval (lo,hi), using closure checks."""
    fixed = {}
    for expected_new in strata:
        chi = {}
        for S in range(1, N + 1):
            mem = members(S, 6)
            free = [i for i in mem if i not in fixed]
            fixed_sum = sum((fixed[i] for i in mem if i in fixed), Aff())
            share = (worth(S) - fixed_sum) / len(free) if free else None
            chi[S] = {i: (fixed[i] if i in fixed else share) for i in mem}

        sample = lo + 1 if hi is None else (lo + hi) / 2
        maxima = {}
        for i in range(6):
            candidates = [chi[S][i] for S in range(1, N + 1) if S >> i & 1]
            maxima[i] = max(candidates, key=lambda form: form.at(sample))
        for i in range(6):
            for S in range(1, N + 1):
                if S >> i & 1:
                    assert nonnegative_on_interval(maxima[i] - chi[S][i], lo, hi), (
                        lo,
                        hi,
                        i,
                        S,
                        maxima[i],
                        chi[S][i],
                    )

        always_admissible = []
        for S in range(1, N + 1):
            mem = members(S, 6)
            sum_identity = sum((chi[S][i] for i in mem), Aff()) == worth(S)
            max_identities = all(chi[S][i] == maxima[i] for i in mem)
            if sum_identity and max_identities:
                always_admissible.append(S)
        union = 0
        for S in always_admissible:
            union |= S
        actual_new = tuple(i for i in range(6) if union >> i & 1 and i not in fixed)
        assert actual_new == expected_new, (lo, hi, actual_new, expected_new)
        for i in actual_new:
            assert maxima[i] == claims[i], (lo, hi, i, maxima[i], claims[i])
            fixed[i] = claims[i]
    assert len(fixed) == 6


def certify_piece_subdivided(lo, hi, strata, claims):
    """Split at every affine max-comparison crossing, then certify each cell."""
    fixed = {}
    cuts = {lo}
    if hi is not None:
        cuts.add(hi)
    for expected_new in strata:
        chi = {}
        for S in range(1, N + 1):
            mem = members(S, 6)
            free = [i for i in mem if i not in fixed]
            fixed_sum = sum((fixed[i] for i in mem if i in fixed), Aff())
            share = (worth(S) - fixed_sum) / len(free) if free else None
            chi[S] = {i: (fixed[i] if i in fixed else share) for i in mem}
        for i in range(6):
            candidates = [chi[S][i] for S in range(1, N + 1) if S >> i & 1]
            for a_index, a in enumerate(candidates):
                for b in candidates[a_index + 1 :]:
                    diff = a - b
                    if diff.slope == 0:
                        continue
                    root = -diff.intercept / diff.slope
                    if root > lo and (hi is None or root < hi):
                        cuts.add(root)
        for i in expected_new:
            fixed[i] = claims[i]

    ordered = sorted(cuts)
    for left, right in zip(ordered, ordered[1:]):
        certify_piece(left, right, strata, claims)
    if hi is None:
        certify_piece(ordered[-1], None, strata, claims)
    return ordered


def check_breakpoint(t, expected_claims, expected_es):
    values = additive_values((t, 0, 0, 0, t, 0))
    claims, is_es, _ = procedure_trace(values)
    assert claims == tuple(form.at(t) for form in expected_claims)
    assert is_es is expected_es


def main():
    piece_1 = (
        Aff(F(3, 4), F(1, 2)),
        Aff(F(1, 4), F(1, 2)),
        Aff(F(3, 4), F(1, 2)),
        Aff(F(1, 4), F(1, 2)),
        Aff(F(1, 2), F(1)),
        Aff(F(1, 2), F(1)),
    )
    piece_2 = (
        Aff(F(3, 2), F(0)),
        Aff(F(-1, 2), F(1)),
        Aff(F(0), F(1)),
        Aff(F(-1, 2), F(1)),
        Aff(F(1, 2), F(1)),
        Aff(F(1, 2), F(1)),
    )
    piece_3 = (
        Aff(F(1), F(1, 2)),
        Aff(F(0), F(1, 2)),
        Aff(F(0), F(1)),
        Aff(F(0), F(1, 2)),
        Aff(F(1), F(1, 2)),
        Aff(F(0), F(3, 2)),
    )

    cuts_1 = certify_piece_subdivided(
        F(0), F(2, 3), ((4, 5), (0, 2), (1, 3)), piece_1
    )
    cuts_2 = certify_piece_subdivided(
        F(2, 3), F(1), ((4, 5), (0,), (1, 2, 3)), piece_2
    )
    cuts_3 = certify_piece_subdivided(
        F(1), None, ((0, 4), (2, 5), (1, 3)), piece_3
    )

    check_breakpoint(F(0), piece_1, True)
    for t in cuts_1[1:]:
        check_breakpoint(t, piece_1, False)
    for t in cuts_2:
        check_breakpoint(t, piece_2, False)
    for t in cuts_3:
        check_breakpoint(t, piece_3, False)

    # The claim excesses over v_t(N)=4+2t are respectively t, 1-t/2,
    # and 1/2, all strictly positive on their positive parameter ranges.
    assert sum(piece_1, Aff()) - Aff(F(2), F(4)) == Aff(F(1), F(0))
    assert sum(piece_2, Aff()) - Aff(F(2), F(4)) == Aff(F(-1, 2), F(1))
    assert sum(piece_3, Aff()) - Aff(F(2), F(4)) == Aff(F(0), F(1, 2))
    print(
        "ADDITIVE RAY CERTIFICATE PASSED "
        f"(claim chambers 3; comparison cells "
        f"{len(cuts_1)-1}+{len(cuts_2)-1}+{len(cuts_3)}; exact arithmetic)."
    )


if __name__ == "__main__":
    main()
