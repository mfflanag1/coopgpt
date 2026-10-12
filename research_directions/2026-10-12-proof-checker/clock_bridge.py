"""Pure helpers for bracketing wall-clock readings with a monotonic clock.

See CLOCK_CONTRACT.txt. Standard library only; no hardware, network, or
filesystem access. All validation raises ValueError explicitly (never via
``assert``) so behaviour is identical under ``python -O``.

A *stamp* is a mapping with exact-int nanosecond keys::

    monotonic_before_ns <= monotonic_after_ns   (both >= 0)
    wall_ns                                      (any int; negative epochs ok)

The wall reading is known to have happened somewhere inside the monotonic
bracket, so the true wall-minus-monotonic offset for a stamp lies in
``[wall_ns - monotonic_after_ns, wall_ns - monotonic_before_ns]``.

Limitations: ``bridge_diagnostics`` only inspects the *sampled* offsets; it
can never prove that no unobserved clock jump occurred between samples.
"""

import math
import numbers
import time
from collections.abc import Mapping

__all__ = ["paired_stamp", "duration_bounds_s", "bridge_diagnostics"]

_NS_PER_S = 10**9
_STAMP_KEYS = ("monotonic_before_ns", "wall_ns", "monotonic_after_ns")


# --------------------------------------------------------------------------- #
# validation helpers
# --------------------------------------------------------------------------- #
def _require_int(value, name):
    """Return ``value`` if it is an exact int (bool excluded); else ValueError."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"{name} must be an exact int of nanoseconds, got {type(value).__name__}"
        )
    return value


def _require_nonneg_int(value, name):
    _require_int(value, name)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative, got {value}")
    return value


def _validate_stamp(stamp, name="stamp"):
    """Validate a stamp mapping and return a fresh (before, wall, after) tuple.

    The input is never mutated; only read.
    """
    if not isinstance(stamp, Mapping):
        raise ValueError(
            f"{name} must be a mapping with keys {_STAMP_KEYS}, "
            f"got {type(stamp).__name__}"
        )
    missing = [k for k in _STAMP_KEYS if k not in stamp]
    if missing:
        raise ValueError(f"{name} is missing keys: {missing}")
    before = _require_nonneg_int(stamp["monotonic_before_ns"], f"{name}.monotonic_before_ns")
    after = _require_nonneg_int(stamp["monotonic_after_ns"], f"{name}.monotonic_after_ns")
    wall = _require_int(stamp["wall_ns"], f"{name}.wall_ns")
    if after < before:
        raise ValueError(
            f"{name} has a reversed bracket: monotonic_after_ns={after} < "
            f"monotonic_before_ns={before}"
        )
    return before, wall, after


def _require_tolerance(value, name):
    """Finite, nonnegative real number; bool excluded. Returned unchanged."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(
            f"{name} must be a finite nonnegative number, got {type(value).__name__}"
        )
    if not isinstance(value, numbers.Rational) and not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value!r}")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative, got {value!r}")
    return value


def _ns_to_s(ns):
    """Integer nanoseconds -> float seconds via correctly rounded int/int division.

    ``int / int`` true division in CPython is correctly rounded even for huge
    ints, unlike ``int / 1e9`` which would first round the int to a float.
    """
    return ns / _NS_PER_S


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def paired_stamp(monotonic_ns=None, wall_ns=None):
    """Read the wall clock bracketed by two monotonic readings.

    ``monotonic_ns`` / ``wall_ns`` are zero-argument callables returning exact
    int nanoseconds; they default to ``time.monotonic_ns`` / ``time.time_ns``.
    Calls happen strictly in the order mono, wall, mono.

    Returns a new dict with keys ``monotonic_before_ns``, ``wall_ns``,
    ``monotonic_after_ns``. Raises ValueError for bool/non-int readings or a
    reversed bracket.
    """
    if monotonic_ns is None:
        monotonic_ns = time.monotonic_ns
    if wall_ns is None:
        wall_ns = time.time_ns
    if not callable(monotonic_ns):
        raise ValueError("monotonic_ns must be a zero-argument callable or None")
    if not callable(wall_ns):
        raise ValueError("wall_ns must be a zero-argument callable or None")

    before = monotonic_ns()
    wall = wall_ns()
    after = monotonic_ns()

    stamp = {
        "monotonic_before_ns": before,
        "wall_ns": wall,
        "monotonic_after_ns": after,
    }
    _validate_stamp(stamp, "paired_stamp result")
    return stamp


def duration_bounds_s(start, end):
    """Monotonic duration bounds between two stamps, in seconds.

    Wall timestamps are neither compared nor subtracted. The brackets may
    touch (``end.before == start.after``) but may not overlap.

    Returns ``{"lower_s": ..., "upper_s": ...}`` where
    ``lower_s = (end.before - start.after) / 1e9`` and
    ``upper_s = (end.after - start.before) / 1e9``; subtraction is done on
    ints before the single float conversion.
    """
    s_before, _s_wall, s_after = _validate_stamp(start, "start")
    e_before, _e_wall, e_after = _validate_stamp(end, "end")
    if e_before < s_after:
        raise ValueError(
            f"stamps overlap or are out of order: end.monotonic_before_ns={e_before} "
            f"< start.monotonic_after_ns={s_after}"
        )
    return {
        "lower_s": _ns_to_s(e_before - s_after),
        "upper_s": _ns_to_s(e_after - s_before),
    }


def bridge_diagnostics(stamps, max_bracket_s=0.01, max_observed_offset_span_s=0.05):
    """Diagnose a sequence of paired stamps.

    ``stamps`` must contain at least two valid stamps in chronological order
    with no overlapping monotonic brackets (touching is allowed). Tolerances
    must be finite nonnegative numbers (bool rejected).

    For each stamp the wall-minus-monotonic offset lies in
    ``[wall_ns - monotonic_after_ns, wall_ns - monotonic_before_ns]``. The
    conservative observed span is ``max(all uppers) - min(all lowers)``
    (not a minimum feasible span). All arithmetic is on ints; the single
    float conversion happens when reporting seconds.

    Returns a new dict::

        valid                   bool
        maximum_bracket_s       float
        observed_offset_span_s  float
        errors                  list[str]  (both failures retained if present)

    Invalid when maximum_bracket_s > max_bracket_s or
    observed_offset_span_s > max_observed_offset_span_s; equality passes.

    This only reasons about the sampled offsets. It never claims that no
    unobserved clock jump happened between samples. Inputs are not mutated.
    """
    _require_tolerance(max_bracket_s, "max_bracket_s")
    _require_tolerance(max_observed_offset_span_s, "max_observed_offset_span_s")

    if isinstance(stamps, (str, bytes, bytearray, Mapping)):
        raise ValueError("stamps must be a sequence of stamp mappings")
    try:
        items = tuple(stamps)
    except TypeError:
        raise ValueError("stamps must be an iterable sequence of stamp mappings") from None
    if len(items) < 2:
        raise ValueError(f"at least 2 stamps are required, got {len(items)}")

    parsed = [_validate_stamp(st, f"stamps[{i}]") for i, st in enumerate(items)]

    for i in range(1, len(parsed)):
        prev_after = parsed[i - 1][2]
        cur_before = parsed[i][0]
        if cur_before < prev_after:
            raise ValueError(
                f"stamps[{i}] overlaps or precedes stamps[{i - 1}]: "
                f"monotonic_before_ns={cur_before} < previous monotonic_after_ns={prev_after}"
            )

    max_bracket_ns = max(after - before for before, _wall, after in parsed)
    offset_lowers = [wall - after for before, wall, after in parsed]
    offset_uppers = [wall - before for before, wall, after in parsed]
    span_ns = max(offset_uppers) - min(offset_lowers)

    maximum_bracket_s = _ns_to_s(max_bracket_ns)
    observed_offset_span_s = _ns_to_s(span_ns)

    errors = []
    if maximum_bracket_s > max_bracket_s:
        errors.append(
            f"maximum monotonic bracket {maximum_bracket_s!r} s exceeds "
            f"max_bracket_s={max_bracket_s!r}"
        )
    if observed_offset_span_s > max_observed_offset_span_s:
        errors.append(
            f"observed wall/monotonic offset span {observed_offset_span_s!r} s exceeds "
            f"max_observed_offset_span_s={max_observed_offset_span_s!r}"
        )

    return {
        "valid": not errors,
        "maximum_bracket_s": maximum_bracket_s,
        "observed_offset_span_s": observed_offset_span_s,
        "errors": errors,
    }
