"""Parser and conservative interval-energy bounds for powermetrics text.

Scope (see ENERGY_CONTRACT.txt):

* ``parse_text(text)`` parses text produced by the installed ``powermetrics``
  (samplers ``cpu_power,gpu_power``, 1000 ms) into per-sample records.  Only
  literal ``*** Sampled system activity (...) (...ms elapsed) ***`` headers
  start a sample.  Power values are read ONLY from the first
  ``**** Processor usage ****`` section of each sample; the ``GPU Power`` line
  repeated under ``**** GPU usage ****`` (which may differ by ~1 mW because of
  counter timing) is never read or added.
* ``energy_bounds(samples, start_utc, end_utc)`` computes conservative lower
  and upper bounds on component energy over a wall-clock window, treating each
  printed whole-second endpoint as uncertain by +/-1 s and NOT allocating any
  part of an edge interval's energy by assuming constant power.

This module is stdlib only.  It never runs ``powermetrics`` (or any other
process), never samples hardware, and performs no network I/O.  It makes no
baseline subtraction, interpolation, per-request allocation, or whole-machine
energy claims; it only integrates the explicitly reported component powers
over the explicitly reported elapsed interval.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

__all__ = [
    "parse_text",
    "energy_bounds",
    "CLOCK_TOLERANCE_S",
    "CONTINUITY_TOLERANCE_S",
    "COMBINED_ROUNDOFF_MW",
]

# Printed sample endpoints are whole seconds; treat each as uncertain +/-1 s.
CLOCK_TOLERANCE_S = 1.0
# Allowed discrepancy between header-time differences and elapsed durations.
CONTINUITY_TOLERANCE_S = 2.05
# Allowed |Combined - (CPU + GPU + ANE)| round-off in mW.
COMBINED_ROUNDOFF_MW = 3.0

COMPONENTS: Tuple[str, ...] = ("cpu", "gpu", "ane", "combined")

# A "block boundary" is any line starting with exactly three asterisks followed
# by a non-asterisk (e.g. the sample header or a summary heading).  Four-star
# lines are section headings *inside* a block.
_BLOCK_BOUNDARY_RE = re.compile(r"^\*\*\*[^*]")
_SECTION_RE = re.compile(r"^\*\*\*\* (?P<name>.*?) \*\*\*\*\s*$")
_HEADER_RE = re.compile(
    r"^\*\*\* Sampled system activity \((?P<ts>[^()]*)\) "
    r"\((?P<elapsed>[^()]*?)ms elapsed\) \*\*\*\s*$"
)
_TS_RE = re.compile(
    r"^\s*(?P<dow>[A-Za-z]{3})\s+(?P<mon>[A-Za-z]{3})\s+(?P<day>\d{1,2})\s+"
    r"(?P<H>\d{1,2}):(?P<M>\d{2}):(?P<S>\d{2})\s+(?P<Y>\d{4})\s+"
    r"(?P<sign>[+-])(?P<tzh>\d{2})(?P<tzm>\d{2})\s*$"
)
_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_POWER_RES = {
    "cpu": re.compile(r"^CPU Power:\s*(?P<v>\S+)\s*mW\s*$"),
    "gpu": re.compile(r"^GPU Power:\s*(?P<v>\S+)\s*mW\s*$"),
    "ane": re.compile(r"^ANE Power:\s*(?P<v>\S+)\s*mW\s*$"),
    "combined": re.compile(
        r"^Combined Power \(CPU \+ GPU \+ ANE\):\s*(?P<v>\S+)\s*mW\s*$"
    ),
}
_PROCESSOR_SECTION = "Processor usage"


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def _parse_header_timestamp(raw: str) -> Optional[datetime]:
    """Parse ``Sun Oct 11 16:29:16 2026 -0400`` into a tz-aware datetime.

    Done by hand (not ``strptime``) so the result does not depend on locale.
    Returns ``None`` when the text is not a well-formed timestamp.
    """
    m = _TS_RE.match(raw)
    if not m:
        return None
    if m.group("dow") not in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun") or int(m.group("tzh")) > 23 or int(m.group("tzm")) > 59:
        return None
    mon = _MONTHS.get(m.group("mon").lower())
    if mon is None:
        return None
    try:
        offset = timedelta(hours=int(m.group("tzh")), minutes=int(m.group("tzm")))
        if m.group("sign") == "-":
            offset = -offset
        tz = timezone(offset)
        return datetime(
            int(m.group("Y")), mon, int(m.group("day")),
            int(m.group("H")), int(m.group("M")), int(m.group("S")),
            tzinfo=tz,
        )
    except (ValueError, OverflowError):
        return None


def _parse_number(raw: str) -> Optional[float]:
    """Parse a decimal number; ``None`` if not a plain finite decimal literal."""
    s = raw.strip()
    # Reject things like 'nan', 'inf', '0x10', '1_000' which float() accepts.
    if not re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?", s):
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    if not math.isfinite(v):
        return None
    return v


def _split_blocks(lines: Sequence[str]) -> List[Tuple[int, str, List[str]]]:
    """Split lines into (line_no, boundary_line, body_lines) blocks.

    Text before the first three-star boundary line is the preamble and is
    dropped.  ``line_no`` is 1-based.
    """
    blocks: List[Tuple[int, str, List[str]]] = []
    current: Optional[Tuple[int, str, List[str]]] = None
    for idx, line in enumerate(lines, start=1):
        if _BLOCK_BOUNDARY_RE.match(line):
            current = (idx, line.rstrip("\r\n"), [])
            blocks.append(current)
        elif current is not None:
            current[2].append(line.rstrip("\r\n"))
    return blocks


def _processor_section(body: Sequence[str]) -> Tuple[Optional[List[str]], int]:
    """Return (lines of the first Processor usage section, count of such sections)."""
    sections: List[List[str]] = []
    active: Optional[List[str]] = None
    for line in body:
        sm = _SECTION_RE.match(line)
        if sm:
            if sm.group("name").strip() == _PROCESSOR_SECTION:
                active = []
                sections.append(active)
            else:
                active = None  # any other **** section ends the processor block
            continue
        if active is not None:
            active.append(line)
    if not sections:
        return None, 0
    return sections[0], len(sections)


def _mw_to_j(mw: float, elapsed_ms: float) -> float:
    """Energy in joules: mW * ms = 1e-6 J (computed as exact division by 1e6)."""
    return (mw * elapsed_ms) / 1_000_000.0


def parse_text(text: str) -> Dict[str, Any]:
    """Parse powermetrics text into ``{'samples': [...], 'errors': [...]}``.

    Each valid sample record contains:

    ``index``        0-based order among headers found,
    ``line``         1-based line number of the header,
    ``end_local``    header timestamp as printed (ISO 8601, original offset),
    ``end_utc``      header timestamp converted to UTC (ISO 8601),
    ``elapsed_ms``   elapsed as printed, ``elapsed_s`` = elapsed_ms / 1000,
    ``cpu_mw``, ``gpu_mw``, ``ane_mw``, ``combined_mw``   explicit mW values,
    ``cpu_j``, ``gpu_j``, ``ane_j``, ``combined_j``       = mW * elapsed_ms * 1e-6.

    ``combined_*`` is the explicitly printed Combined Power, never a
    recomputed component sum.  Samples with any missing/malformed/negative/
    non-finite required field are excluded from ``samples`` and reported in
    ``errors`` (so invalid samples never appear as silent zeros).
    """
    samples: List[Dict[str, Any]] = []
    errors: List[str] = []

    if not isinstance(text, str):
        return {"samples": [], "errors": ["input is not a string"]}

    lines = text.splitlines()
    blocks = _split_blocks(lines)

    header_blocks = [
        (ln, boundary, body) for (ln, boundary, body) in blocks
        if _HEADER_RE.match(boundary)
    ]
    for line_no, boundary, _ in blocks:
        if boundary.startswith("*** Sampled system activity") and not _HEADER_RE.match(boundary):
            errors.append(f"line {line_no}: malformed sample header {boundary!r}")
    if not header_blocks:
        errors.append("no 'Sampled system activity' headers found")
        return {"samples": samples, "errors": errors}

    seen_endpoints: Dict[datetime, int] = {}

    for index, (line_no, boundary, body) in enumerate(header_blocks):
        hm = _HEADER_RE.match(boundary)
        assert hm is not None
        tag = f"sample {index} (line {line_no})"
        sample_errors: List[str] = []

        end_dt = _parse_header_timestamp(hm.group("ts"))
        if end_dt is None:
            sample_errors.append(
                f"{tag}: malformed or non-timezone-aware header timestamp "
                f"{hm.group('ts')!r}"
            )

        elapsed_ms = _parse_number(hm.group("elapsed"))
        if elapsed_ms is None:
            sample_errors.append(
                f"{tag}: malformed/non-finite elapsed {hm.group('elapsed')!r}"
            )
        elif elapsed_ms <= 0:
            sample_errors.append(f"{tag}: non-positive elapsed {elapsed_ms} ms")

        if end_dt is not None:
            prior = seen_endpoints.get(end_dt)
            if prior is not None:
                sample_errors.append(
                    f"{tag}: duplicate header timestamp {end_dt.isoformat()} "
                    f"(also sample {prior})"
                )
            else:
                seen_endpoints[end_dt] = index

        section, n_sections = _processor_section(body)
        powers: Dict[str, float] = {}
        if section is None:
            sample_errors.append(f"{tag}: missing '**** Processor usage ****' section")
        else:
            if n_sections > 1:
                sample_errors.append(
                    f"{tag}: {n_sections} 'Processor usage' sections (ambiguous)"
                )
            for comp, rx in _POWER_RES.items():
                matches = [rx.match(l) for l in section]
                matches = [m for m in matches if m]
                if len(matches) == 0:
                    sample_errors.append(
                        f"{tag}: missing explicit-mW '{comp}' power line in "
                        f"Processor usage section"
                    )
                    continue
                if len(matches) > 1:
                    sample_errors.append(
                        f"{tag}: '{comp}' power line appears {len(matches)} "
                        f"times in Processor usage section"
                    )
                    continue
                v = _parse_number(matches[0].group("v"))
                if v is None:
                    sample_errors.append(
                        f"{tag}: malformed/non-finite '{comp}' power "
                        f"{matches[0].group('v')!r}"
                    )
                elif v < 0:
                    sample_errors.append(f"{tag}: negative '{comp}' power {v} mW")
                else:
                    powers[comp] = v

        if all(c in powers for c in COMPONENTS):
            component_sum = powers["cpu"] + powers["gpu"] + powers["ane"]
            if abs(powers["combined"] - component_sum) > COMBINED_ROUNDOFF_MW:
                sample_errors.append(
                    f"{tag}: Combined Power {powers['combined']} mW differs from "
                    f"CPU+GPU+ANE {component_sum} mW by more than "
                    f"{COMBINED_ROUNDOFF_MW} mW"
                )

        if sample_errors:
            errors.extend(sample_errors)
            continue

        assert end_dt is not None and elapsed_ms is not None
        record: Dict[str, Any] = {
            "index": index,
            "line": line_no,
            "end_local": end_dt.isoformat(),
            "end_utc": end_dt.astimezone(timezone.utc).isoformat(),
            "elapsed_ms": elapsed_ms,
            "elapsed_s": elapsed_ms / 1000.0,
        }
        for comp in COMPONENTS:
            record[f"{comp}_mw"] = powers[comp]
        for comp in COMPONENTS:
            record[f"{comp}_j"] = _mw_to_j(powers[comp], elapsed_ms)
        samples.append(record)

    return {"samples": samples, "errors": errors}


# --------------------------------------------------------------------------- #
# Conservative bounds
# --------------------------------------------------------------------------- #

def _parse_iso_utc(value: Any, label: str, errors: List[str]) -> Optional[datetime]:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{label}: not an ISO 8601 datetime: {value!r}")
            return None
    else:
        errors.append(f"{label}: expected ISO 8601 string, got {type(value).__name__}")
        return None
    if dt.tzinfo is None or dt.utcoffset() is None:
        errors.append(f"{label}: datetime must be timezone-aware: {value!r}")
        return None
    return dt.astimezone(timezone.utc)


def _finite_nonneg(value: Any) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    v = float(value)
    if not math.isfinite(v) or v < 0:
        return None
    return v


def _invalid(errors: List[str], duration_s: Optional[float],
             sample_count: int) -> Dict[str, Any]:
    return {
        "valid": False,
        "errors": list(errors),
        "duration_s": duration_s,
        "lower_j": None,
        "upper_j": None,
        "fully_inside_count": None,
        "possibly_overlapping_count": None,
        "sample_count": sample_count,
        "clock_tolerance_s": CLOCK_TOLERANCE_S,
    }


def energy_bounds(
    samples: Union[Sequence[Dict[str, Any]], Dict[str, Any]],
    start_utc: Any,
    end_utc: Any,
) -> Dict[str, Any]:
    """Conservative component-energy bounds over [start_utc, end_utc].

    ``samples`` is the ``samples`` list from :func:`parse_text` (or the whole
    ``parse_text`` result dict, in which case any parse errors make the result
    invalid).  ``start_utc``/``end_utc`` are timezone-aware ISO 8601 strings.

    Uncertainty model (clock alignment only, not calibration): each printed
    whole-second endpoint ``t`` is uncertain by +/-``CLOCK_TOLERANCE_S``, and the
    sample's beginning shares that uncertainty, i.e. actual end in
    ``[t-1, t+1]`` and actual beginning in ``[t-1-elapsed, t+1-elapsed]``.

    * ``lower_j``: sum of whole-interval energy of samples whose earliest
      possible beginning >= start AND latest possible end <= end.
    * ``upper_j``: sum of whole-interval energy of samples whose latest
      possible end > start AND earliest possible beginning < end.

    Conditional on a complete, contiguous, non-overlapping raw sampler capture.
    Text continuity checks cannot prove absence of one short missing interval.
    No portion of an edge interval's energy is attributed by assuming constant
    power; interval energy is non-negative so the bounds are sound under the
    stated alignment assumption.  Requires guaranteed outer coverage and a
    continuous, chronological sample sequence; otherwise returns
    ``valid: False`` with explicit errors and null bounds (never a silent zero).
    """
    errors: List[str] = []

    if isinstance(samples, dict):
        parse_errors = samples.get("errors") or []
        if parse_errors:
            errors.append(
                f"parse result carries {len(parse_errors)} error(s); refusing "
                f"to bound energy on an invalid parse"
            )
            errors.extend(f"parse: {e}" for e in parse_errors)
        samples = samples.get("samples") or []

    # --- window ----------------------------------------------------------- #
    start = _parse_iso_utc(start_utc, "start_utc", errors)
    end = _parse_iso_utc(end_utc, "end_utc", errors)
    duration_s: Optional[float] = None
    if start is not None and end is not None:
        duration_s = (end - start).total_seconds()
        if not math.isfinite(duration_s) or duration_s <= 0:
            errors.append(
                f"window must be a positive finite duration (got {duration_s} s)"
            )

    # --- samples ---------------------------------------------------------- #
    if not isinstance(samples, (list, tuple)):
        errors.append("samples must be a list of sample records")
        return _invalid(errors, duration_s, 0)
    if len(samples) == 0:
        errors.append("no samples supplied")
        return _invalid(errors, duration_s, 0)

    parsed: List[Dict[str, Any]] = []
    for i, s in enumerate(samples):
        tag = f"sample {i}"
        if not isinstance(s, dict):
            errors.append(f"{tag}: not a dict")
            continue
        t_end = _parse_iso_utc(s.get("end_utc"), f"{tag}.end_utc", errors)
        elapsed = s.get("elapsed_s")
        if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) \
                or not math.isfinite(float(elapsed)) or float(elapsed) <= 0:
            errors.append(f"{tag}: elapsed_s must be positive and finite: {elapsed!r}")
            elapsed = None
        energies: Dict[str, float] = {}
        for comp in COMPONENTS:
            v = _finite_nonneg(s.get(f"{comp}_j"))
            if v is None:
                errors.append(
                    f"{tag}: {comp}_j must be a finite non-negative number: "
                    f"{s.get(f'{comp}_j')!r}"
                )
            else:
                energies[comp] = v
        if t_end is None or elapsed is None or len(energies) != len(COMPONENTS):
            continue
        parsed.append({"end": t_end, "elapsed_s": float(elapsed), "j": energies})

    if errors:
        return _invalid(errors, duration_s, len(samples))
    assert start is not None and end is not None

    # --- chronology / continuity ----------------------------------------- #
    for i in range(1, len(parsed)):
        prev, cur = parsed[i - 1], parsed[i]
        diff = (cur["end"] - prev["end"]).total_seconds()
        if diff <= 0:
            errors.append(
                f"samples {i - 1} and {i}: header times not strictly increasing "
                f"({prev['end'].isoformat()} -> {cur['end'].isoformat()})"
            )
            continue
        if abs(diff - cur["elapsed_s"]) > CONTINUITY_TOLERANCE_S:
            errors.append(
                f"samples {i - 1} and {i}: header difference {diff:.3f} s is "
                f"inconsistent with elapsed {cur['elapsed_s']:.3f} s "
                f"(tolerance {CONTINUITY_TOLERANCE_S} s): missing sample or clock jump"
            )
    if errors:
        return _invalid(errors, duration_s, len(samples))

    if len(parsed) >= 2:
        span = (parsed[-1]["end"] - parsed[0]["end"]).total_seconds()
        cumulative = sum(p["elapsed_s"] for p in parsed[1:])
        if abs(span - cumulative) > CONTINUITY_TOLERANCE_S:
            errors.append(
                f"cumulative elapsed after first sample {cumulative:.3f} s differs "
                f"from first-to-last endpoint span {span:.3f} s by more than "
                f"{CONTINUITY_TOLERANCE_S} s: missing samples or clock jump"
            )
            return _invalid(errors, duration_s, len(samples))

    # One continuous sampler timeline must fit every rounded endpoint, not
    # merely each adjacent pair and the final total. Completeness remains an
    # instrument/provenance assumption; short missing intervals can be hidden
    # by whole-second timestamp uncertainty and cannot be ruled out from text.
    cumulative = 0.0
    residuals = [0.0]
    for p in parsed[1:]:
        cumulative += p["elapsed_s"]
        residuals.append((p["end"]-parsed[0]["end"]).total_seconds()-cumulative)
    if max(residuals)-min(residuals) > 2*CLOCK_TOLERANCE_S:
        errors.append("no continuous timeline fits all endpoint uncertainty intervals")
        return _invalid(errors, duration_s, len(samples))

    # --- uncertainty intervals ------------------------------------------- #
    tol = timedelta(seconds=CLOCK_TOLERANCE_S)
    for p in parsed:
        el = timedelta(seconds=p["elapsed_s"])
        p["earliest_end"] = p["end"] - tol
        p["latest_end"] = p["end"] + tol
        p["earliest_begin"] = p["earliest_end"] - el
        p["latest_begin"] = p["latest_end"] - el

    # --- guaranteed outer coverage --------------------------------------- #
    first, last = parsed[0], parsed[-1]
    if first["latest_begin"] > start:
        errors.append(
            f"coverage: first sample's latest possible beginning "
            f"{first['latest_begin'].isoformat()} is after window start "
            f"{start.isoformat()}"
        )
    if last["earliest_end"] < end:
        errors.append(
            f"coverage: last sample's earliest possible end "
            f"{last['earliest_end'].isoformat()} is before window end "
            f"{end.isoformat()}"
        )
    if errors:
        return _invalid(errors, duration_s, len(samples))

    # --- bounds ----------------------------------------------------------- #
    lower = {c: 0.0 for c in COMPONENTS}
    upper = {c: 0.0 for c in COMPONENTS}
    fully_inside = 0
    possibly_overlapping = 0
    for p in parsed:
        inside = p["earliest_begin"] >= start and p["latest_end"] <= end
        overlapping = p["latest_end"] > start and p["earliest_begin"] < end
        if inside:
            fully_inside += 1
            for c in COMPONENTS:
                lower[c] += p["j"][c]
        if overlapping:
            possibly_overlapping += 1
            for c in COMPONENTS:
                upper[c] += p["j"][c]

    return {
        "valid": True,
        "errors": [],
        "duration_s": duration_s,
        "lower_j": lower,
        "upper_j": upper,
        "fully_inside_count": fully_inside,
        "possibly_overlapping_count": possibly_overlapping,
        "sample_count": len(parsed),
        "clock_tolerance_s": CLOCK_TOLERANCE_S,
        "window": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
        "method": (
            "whole-interval sums under +/-1 s endpoint alignment uncertainty; "
            "no constant-power allocation across edge intervals; no baseline "
            "subtraction; component (CPU/GPU/ANE/Combined) energy only, not "
            "whole-machine energy"
        ),
    }
