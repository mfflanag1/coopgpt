#!/usr/bin/env python3
"""Fail closed on silent TeX corruption from non-raw generated strings.

Python string escapes such as ``\b`` can insert control bytes, while a lost
backslash can leave display delimiters or environment commands as ordinary
text.  TeX may still produce a PDF in those cases, so the release build needs
an independent source-level gate.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CONTROL_BYTES = set(range(0x00, 0x09)) | {0x0B, 0x0C} | set(range(0x0E, 0x20))
BARE_DISPLAY = re.compile(rb"^\s*[\[\]]\s*$")
BARE_ENVIRONMENT = re.compile(rb"^\s*(?:begin|end)\{")


def audit(path: Path) -> None:
    data = path.read_bytes()
    failures: list[str] = []
    for line_number, line in enumerate(data.splitlines(), 1):
        controls = sorted(set(line) & CONTROL_BYTES)
        if controls:
            failures.append(f"line {line_number}: control bytes {controls}")
        if BARE_DISPLAY.match(line):
            failures.append(f"line {line_number}: bare display delimiter")
        if BARE_ENVIRONMENT.match(line):
            failures.append(f"line {line_number}: bare TeX environment command")
        without_valid_qquad = line.replace(b"\\qquad", b"")
        if b"qquad" in without_valid_qquad or b"\\boxed{quad" in line:
            failures.append(f"line {line_number}: likely lost spacing escape")
    if failures:
        joined = "\n".join(failures)
        raise AssertionError(f"TeX source-sanity audit failed for {path}:\n{joined}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.paths:
        audit(path)
    print(f"TeX source-sanity audit passed for {len(args.paths)} file(s)")


if __name__ == "__main__":
    main()
