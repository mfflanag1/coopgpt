#!/usr/bin/env python3
"""Exact Z3/LRA CEGAR search for a five-player fixed-Cx obstruction.

The query is deliberately one-sided.  It searches for an exact,
singleton-normalized game with two Lmax-top players, a tight top pair, a
selected complete staged Lmin certificate Cx, and a normalized PXC92b bad
direction for the lift retaining Cx and the top pair.  SAT is therefore only
a candidate: another positive extreme z-tight top cover may still be
faithful, and every SAT model must be independently reconstructed and have
all complete Cx choices and all qualifying extreme covers exhausted.

Exactness is the complete 280-row n=5 Studeny--Kratochvil cone description.
Both selectors are imposed by the per-stage/per-player Farkas identities.
No floating-point arithmetic is used; the external ``z3`` executable solves
SMT-LIB QF_LRA with Boolean support selectors.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
N = 5
FULL = (1 << N) - 1
PROPER = tuple(range(1, FULL))
TOP = (0, 1)
OUTSIDERS = (2, 3, 4)
SHAPES = {
    "all_tied": ((0, 1), (2, 3, 4)),
    "unique_high": ((0, 1), (2,), (3, 4)),
    "tied_high": ((0, 1), (2, 3), (4,)),
    "strict": ((0, 1), (2,), (3,), (4,)),
}
ARCHIVE = ROOT / "verifiers/divergence/search_archive/unrestricted_pxc91c_n5_archive.json"


def mask_sum(names: list[str], mask: int) -> str:
    terms = [names[i] for i in range(N) if mask >> i & 1]
    if not terms:
        return "0"
    if len(terms) == 1:
        return terms[0]
    return f"(+ {' '.join(terms)})"


def linear_sum(terms: list[str]) -> str:
    terms = [term for term in terms if term not in ("0", "(+ )")]
    if not terms:
        return "0"
    if len(terms) == 1:
        return terms[0]
    return f"(+ {' '.join(terms)})"


def mul(coefficient: int, name: str) -> str:
    if coefficient == 1:
        return name
    if coefficient == -1:
        return f"(- {name})"
    return f"(* {coefficient} {name})"


def ordered_partitions(items: tuple[int, ...]):
    """Yield every ordered set partition, with no duplicate block orderings."""
    if not items:
        yield ()
        return
    head, tail = items[0], items[1:]
    for partition in ordered_partitions(tail):
        for position in range(len(partition)):
            blocks = list(partition)
            blocks[position] = tuple(sorted((*blocks[position], head)))
            yield tuple(blocks)
        for position in range(len(partition) + 1):
            blocks = list(partition)
            blocks.insert(position, (head,))
            yield tuple(blocks)


def stabilizer(z_blocks: tuple[tuple[int, ...], ...]):
    choices = [tuple(itertools.permutations(block)) for block in z_blocks]
    for block_permutations in itertools.product(*choices):
        mapping = list(range(N))
        for block, image in zip(z_blocks, block_permutations):
            for source, target in zip(block, image):
                mapping[source] = target
        yield tuple(mapping)


def relabel_blocks(blocks, permutation):
    return tuple(tuple(sorted(permutation[i] for i in block)) for block in blocks)


def canonical_x(blocks, z_blocks):
    return min(relabel_blocks(blocks, permutation) for permutation in stabilizer(z_blocks))


def all_x_patterns(z_blocks):
    return tuple(sorted({canonical_x(q, z_blocks) for q in ordered_partitions(tuple(range(N))) }))


def partition_orbit_audit(z_blocks):
    raw = set(ordered_partitions(tuple(range(N))))
    if len(raw) != 541:
        raise AssertionError(("ordered Bell count changed", len(raw)))
    fibers = {}
    for partition in raw:
        key = canonical_x(partition, z_blocks)
        fibers[key] = fibers.get(key, 0) + 1
    if sum(fibers.values()) != 541 or set(fibers) != set(all_x_patterns(z_blocks)):
        raise AssertionError("ordered-partition orbit expansion failed")
    histogram = {}
    for size in fibers.values():
        histogram[str(size)] = histogram.get(str(size), 0) + 1
    return {
        "raw_ordered_partition_count": len(raw),
        "canonical_orbit_count": len(fibers),
        "orbit_size_histogram": dict(sorted(histogram.items(), key=lambda q: int(q[0]))),
        "expanded_count": sum(fibers.values()),
    }


def payoff_blocks(values, descending=False):
    levels = sorted(set(values), reverse=descending)
    return tuple(tuple(i for i, value in enumerate(values) if value == level)
                 for level in levels)


def observed_patterns():
    if not ARCHIVE.exists():
        raise FileNotFoundError(f"observed-pattern archive missing: {ARCHIVE}")
    payload = json.loads(ARCHIVE.read_text())
    if payload.get("audited_two_top_count") != 36:
        raise AssertionError("n=5 observed archive cardinality changed")
    result = {shape: set() for shape in SHAPES}
    for item in payload["audits"]:
        x = tuple(map(F, item["x"]))
        z = tuple(map(F, item["z"]))
        top = tuple(i for i, value in enumerate(z) if value == max(z))
        if len(top) != 2:
            raise AssertionError("observed record lost two-player top")
        z_old = payoff_blocks(z, descending=True)
        residual_sizes = tuple(len(block) for block in z_old[1:])
        shape = next((name for name, blocks in SHAPES.items()
                      if tuple(len(block) for block in blocks[1:]) == residual_sizes), None)
        if shape is None:
            raise AssertionError(("unknown residual shape", residual_sizes))
        target = SHAPES[shape]
        maps = []
        for images in itertools.product(*(
            tuple(itertools.permutations(target_block))
            for target_block in target
        )):
            mapping = list(range(N))
            for old_block, image in zip(z_old, images):
                for old, new in zip(old_block, image):
                    mapping[old] = new
            maps.append(tuple(mapping))
        x_old = payoff_blocks(x)
        result[shape].add(min(relabel_blocks(x_old, mapping) for mapping in maps))
    return {shape: tuple(sorted(patterns)) for shape, patterns in result.items()}


def exact_cone_rows():
    sys.path[:0] = [str(ROOT / "verifiers/lib"), str(ROOT / "verifiers/s5close/lib")]
    import cone  # type: ignore
    rows = tuple(cone.inequalities(N))
    if len(rows) != 280 or len(set(rows)) != 280:
        raise AssertionError(("exact-cone row count changed", len(rows)))
    return rows


class Query:
    def __init__(self, x_blocks, shape, cone_rows, *, drop_exact=False,
                 drop_selector_certs=False, drop_bad_direction=False):
        self.x_blocks = tuple(tuple(q) for q in x_blocks)
        self.shape = shape
        self.z_blocks = SHAPES[shape]
        self.lines = ["(set-logic QF_LRA)", "(set-option :produce-models true)"]
        self.v = [f"v{mask}" for mask in range(1 << N)]
        self.x = [f"x{i}" for i in range(N)]
        self.z = [f"z{i}" for i in range(N)]
        self.d = [f"d{i}" for i in range(N)]
        self.cx = {mask: f"cx{mask}" for mask in PROPER}
        for name in (*self.v, *self.x, *self.z, *self.d):
            self.lines.append(f"(declare-fun {name} () Real)")
        for name in self.cx.values():
            self.lines.append(f"(declare-fun {name} () Bool)")
        self._base(cone_rows, drop_exact)
        self._strata(self.x, self.x_blocks, increasing=True)
        self._strata(self.z, self.z_blocks, increasing=False)
        self.add(f"(= {linear_sum(self.x)} 1)")
        self.add(f"(= {linear_sum(self.z)} 1)")
        self.add("(= z0 z1)")
        self.add("(= v3 (+ z0 z1))")
        self.add(f"(or {' '.join(f'(not (= {a} {b}))' for a, b in zip(self.x, self.z))})")
        for mask in PROPER:
            self.add(f"(=> {self.cx[mask]} (= {mask_sum(self.x, mask)} {self.v[mask]}))")
        if not drop_selector_certs:
            self._farkas(self.x, self.x_blocks, "fx", selected=True, ceiling=False)
            self._farkas(self.z, self.z_blocks, "fz", selected=False, ceiling=True)
        if not drop_bad_direction:
            self._bad_direction()

    def add(self, expression):
        self.lines.append(f"(assert {expression})")

    def _base(self, cone_rows, drop_exact):
        self.add("(= v0 0)")
        self.add("(= v31 1)")
        for player in range(N):
            self.add(f"(= v{1 << player} 0)")
        for mask in PROPER:
            self.add(f"(>= {self.v[mask]} 0)")
            self.add(f"(<= {self.v[mask]} {mask_sum(self.x, mask)})")
            self.add(f"(<= {self.v[mask]} {mask_sum(self.z, mask)})")
        if not drop_exact:
            for row in cone_rows:
                terms = [mul(row[mask], self.v[mask]) for mask in range(1, FULL + 1)
                         if row[mask]]
                self.add(f"(<= {linear_sum(terms)} 0)")

    def _strata(self, coordinates, blocks, increasing):
        for coordinate in coordinates:
            self.add(f"(>= {coordinate} 0)")
        for block in blocks:
            for player in block[1:]:
                self.add(f"(= {coordinates[block[0]]} {coordinates[player]})")
        for left, right in zip(blocks, blocks[1:]):
            relation = "<" if increasing else ">"
            self.add(f"({relation} {coordinates[left[0]]} {coordinates[right[0]]})")

    def _farkas(self, phi, blocks, tag, selected, ceiling):
        pinned = []
        sign = 1 if ceiling else -1
        rhs = -1 if ceiling else 1
        for stage, block in enumerate(blocks):
            for target in block:
                ys = {mask: f"{tag}_y_{stage}_{target}_{mask}" for mask in PROPER}
                eta = f"{tag}_eta_{stage}_{target}"
                rhos = {player: f"{tag}_rho_{stage}_{target}_{player}" for player in pinned}
                sigmas = {player: f"{tag}_sig_{stage}_{target}_{player}" for player in block}
                for name in (*ys.values(), eta, *rhos.values(), *sigmas.values()):
                    self.lines.append(f"(declare-fun {name} () Real)")
                for mask, name in ys.items():
                    self.add(f"(>= {name} 0)")
                    support = self.cx[mask] if selected else f"(= {mask_sum(phi, mask)} {self.v[mask]})"
                    self.add(f"(or (= {name} 0) {support})")
                for name in sigmas.values():
                    self.add(f"(>= {name} 0)")
                for player in range(N):
                    terms = [f"(- {name})" for mask, name in ys.items() if mask >> player & 1]
                    terms.append(eta)
                    if player in rhos:
                        terms.append(rhos[player])
                    if player in sigmas:
                        terms.append(sigmas[player] if sign > 0 else f"(- {sigmas[player]})")
                    value = rhs if player == target else 0
                    self.add(f"(= {linear_sum(terms)} {value})")
            pinned.extend(block)

    def _bad_direction(self):
        self.add("(= d0 0)")
        self.add("(= d1 0)")
        self.add(f"(= {linear_sum(self.d)} 0)")
        for mask in PROPER:
            common = f"(and {self.cx[mask]} (= {mask_sum(self.z, mask)} {self.v[mask]}))"
            self.add(f"(=> {common} (>= {mask_sum(self.d, mask)} 0))")
        for player in OUTSIDERS:
            self.add(f"(=> (= {self.z[player]} 0) (>= {self.d[player]} 0))")
        if self.shape == "all_tied":
            for player in OUTSIDERS:
                self.add(f"(<= {self.d[player]} 0)")
            self.add(f"(or {' '.join(f'(= {self.d[i]} (- 1))' for i in OUTSIDERS)})")
        elif self.shape == "unique_high":
            self.add("(= d2 (- 1))")
        elif self.shape == "tied_high":
            self.add("(<= d2 0)")
            self.add("(<= d3 0)")
            self.add("(or (= d2 (- 1)) (= d3 (- 1)))")
        elif self.shape == "strict":
            self.add("(or (= d2 (- 1)) (and (= d2 0) (= d3 (- 1))))")
        else:
            raise AssertionError(self.shape)

    def render(self):
        requested = [*self.v, *self.x, *self.z, *self.d, *self.cx.values()]
        return "\n".join((*self.lines, "(check-sat)",
                           f"(get-value ({' '.join(requested)}))", ""))


def tokenize_sexpr(text):
    token = ""
    for char in text:
        if char in "()":
            if token:
                yield token
                token = ""
            yield char
        elif char.isspace():
            if token:
                yield token
                token = ""
        else:
            token += char
    if token:
        yield token


def parse_sexpr(tokens):
    tokens = list(tokens)

    def visit(position):
        token = tokens[position]
        if token != "(":
            return token, position + 1
        result = []
        position += 1
        while tokens[position] != ")":
            value, position = visit(position)
            result.append(value)
        return result, position + 1

    result, position = visit(0)
    if position != len(tokens):
        raise ValueError("trailing tokens in Z3 get-value response")
    return result


def sexpr_text(value):
    if isinstance(value, list):
        return f"({' '.join(sexpr_text(q) for q in value)})"
    return str(value)


def solve(query, z3_path, timeout):
    smt = query.render()
    with tempfile.NamedTemporaryFile("w", suffix=".smt2", delete=False) as handle:
        path = Path(handle.name)
        handle.write(smt)
    try:
        process = subprocess.run(
            [z3_path, f"-T:{timeout}", str(path)], capture_output=True,
            text=True, timeout=timeout + 5, check=False,
        )
    finally:
        path.unlink(missing_ok=True)
    lines = process.stdout.strip().splitlines()
    status = lines[0].strip() if lines else "error"
    if status not in {"sat", "unsat", "unknown"}:
        status = "error"
    assignments = None
    if status == "sat" and len(lines) > 1:
        parsed = parse_sexpr(iter(tokenize_sexpr("\n".join(lines[1:]))))
        assignments = {pair[0]: sexpr_text(pair[1]) for pair in parsed
                       if isinstance(pair, list) and len(pair) == 2}
    return {
        "status": status,
        "smt2_sha256": hashlib.sha256(smt.encode()).hexdigest(),
        "stderr": process.stderr.strip(),
        "assignments": assignments,
    }


def branch_catalogue(source):
    observed = observed_patterns()
    branches = []
    for shape, z_blocks in SHAPES.items():
        patterns = observed[shape] if source == "observed" else all_x_patterns(z_blocks)
        for x_blocks in patterns:
            branches.append((shape, x_blocks))
    return observed, tuple(branches)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--z3", default="z3")
    parser.add_argument("--pattern-source", choices=("observed", "all"), default="observed")
    parser.add_argument("--timeout", type=int, default=30, help="seconds per Z3 query")
    parser.add_argument("--max-branches", type=int, default=0,
                        help="deterministic prefix; zero means every selected branch")
    parser.add_argument("--controls", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cone_rows = exact_cone_rows()
    observed, branches = branch_catalogue(args.pattern_source)
    if args.max_branches:
        branches = branches[:args.max_branches]
    results = []
    for index, (shape, x_blocks) in enumerate(branches):
        query = Query(x_blocks, shape, cone_rows)
        item = {"index": index, "shape": shape,
                "x_blocks_low_to_high": [list(q) for q in x_blocks],
                **solve(query, args.z3, args.timeout)}
        if args.controls:
            item["controls"] = {
                "drop_exact_cone": solve(Query(x_blocks, shape, cone_rows,
                                                 drop_exact=True), args.z3, args.timeout)["status"],
                "drop_selector_certificates": solve(
                    Query(x_blocks, shape, cone_rows, drop_selector_certs=True),
                    args.z3, args.timeout)["status"],
                "drop_bad_direction": solve(
                    Query(x_blocks, shape, cone_rows, drop_bad_direction=True),
                    args.z3, args.timeout)["status"],
            }
        results.append(item)
    counts = {status: sum(q["status"] == status for q in results)
              for status in ("sat", "unsat", "unknown", "error")}
    orbit_audits = {shape: partition_orbit_audit(blocks) for shape, blocks in SHAPES.items()}
    all_branch_counts = {shape: audit["canonical_orbit_count"]
                         for shape, audit in orbit_audits.items()}
    observed_counts = {shape: len(patterns) for shape, patterns in observed.items()}
    complete = (args.pattern_source == "all" and args.max_branches == 0
                and counts["unknown"] == counts["error"] == 0)
    replay = ["python3", str(HERE.relative_to(ROOT)), "--pattern-source",
              args.pattern_source, "--timeout", str(args.timeout)]
    if args.max_branches:
        replay.extend(("--max-branches", str(args.max_branches)))
    if args.controls:
        replay.append("--controls")
    canonical_output = HERE.with_name(
        HERE.stem + ("_controls.json" if args.controls else ".json")
    )
    output_name = str(canonical_output.relative_to(ROOT))
    replay.extend(("--output", output_name))
    try:
        z3_version = subprocess.run(
            [args.z3, "--version"], check=True, capture_output=True, text=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("could not pin the external Z3 version") from exc
    payload = {
        "claim": "exact QF_LRA CEGAR search for a bad tight-pair lift at n=5",
        "status_counts": counts,
        "exact_cone_inequality_count": len(cone_rows),
        "pattern_source": args.pattern_source,
        "observed_pattern_counts": observed_counts,
        "all_ordered_partition_orbit_counts": all_branch_counts,
        "ordered_partition_expansion_audits": orbit_audits,
        "selected_branch_count": len(branches),
        "coverage_complete": complete,
        "results": results,
        "controls_enabled": args.controls,
        "provenance": {
            "driver": str(HERE.relative_to(ROOT)),
            "driver_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest(),
            "exact_cone_source": "verifiers/s5close/lib/cone.py",
            "exact_cone_source_sha256": hashlib.sha256(
                (ROOT / "verifiers/s5close/lib/cone.py").read_bytes()
            ).hexdigest(),
            "catalogue_source": "verifiers/lib/catalogue.py",
            "catalogue_source_sha256": hashlib.sha256(
                (ROOT / "verifiers/lib/catalogue.py").read_bytes()
            ).hexdigest(),
            "observed_archive": str(ARCHIVE.relative_to(ROOT)),
            "observed_archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
            "z3": args.z3,
            "z3_version": z3_version,
            "timeout_seconds_per_query": args.timeout,
            "replay_command": " ".join(replay),
        },
        "scope": (
            "SAT only identifies a fixed complete Cx for which the canonical eta=0 "
            "top-pair cover has a normalized PXC92b bad direction. It is not a PXC97b "
            "counterexample until an independent exact replay exhausts every qualifying "
            "positive extreme z-tight cover and every relevant Cx interpretation. This "
            "driver is retained only as a superseded coverage prototype: its selector "
            "layer omits active zero-coordinate normals, so even a complete all-UNSAT "
            "run is not theorem evidence. The promoted 3,840-cell raw and independent-NI "
            "encodings replace it; observed or capped runs are discovery evidence only."
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
