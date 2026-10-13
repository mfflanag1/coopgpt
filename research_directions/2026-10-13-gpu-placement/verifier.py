"""Strict, independent checker for the bounded GPU snapshot placement model.

The checker validates declarations and arithmetic only. It neither establishes
optimality nor checks actual hardware/software compatibility or permission.
"""

import json
import math
import re


_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}", re.ASCII)
_MEMORY_MAX = 1099511627776


def strict_loads(text):
    """Parse JSON, rejecting duplicate keys and every nonfinite number."""
    if type(text) is not str:
        raise ValueError("JSON input must be text")

    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON object key: " + key)
            result[key] = value
        return result

    def finite_float(token):
        value = float(token)
        if not math.isfinite(value):
            raise ValueError("nonfinite JSON number")
        return value

    def bad_constant(token):
        raise ValueError("nonfinite JSON constant: " + token)

    try:
        return json.loads(text, object_pairs_hook=object_pairs,
                          parse_float=finite_float, parse_constant=bad_constant)
    except (RecursionError, OverflowError) as error:
        raise ValueError("JSON exceeds supported parsing limits") from error


def _object(value, keys, path):
    if type(value) is not dict:
        raise ValueError(path + " must be an object")
    if any(type(key) is not str for key in value) or set(value) != set(keys):
        raise ValueError(path + " has incorrect object keys")


def _list(value, minimum, maximum, path):
    if type(value) is not list or not minimum <= len(value) <= maximum:
        raise ValueError(f"{path} must be a list of length {minimum}..{maximum}")


def _integer(value, minimum, maximum, path):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{path} must be an integer in {minimum}..{maximum}")


def _identifier(value, path):
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise ValueError(path + " must be a valid ASCII identifier")


def _unique_id(value, seen, path):
    _identifier(value, path)
    if value in seen:
        raise ValueError(path + " duplicates an identifier")
    seen.add(value)


def _id_list(value, minimum, maximum, path):
    _list(value, minimum, maximum, path)
    seen = set()
    for index, item in enumerate(value):
        _unique_id(item, seen, f"{path}[{index}]")


def validate_manifest(manifest):
    """Validate every schema and size constraint; never mutate the input."""
    _object(manifest, ("schema_version", "nodes", "jobs"), "manifest")
    _integer(manifest["schema_version"], 1, 1, "manifest.schema_version")
    _list(manifest["nodes"], 1, 4, "manifest.nodes")
    _list(manifest["jobs"], 0, 8, "manifest.jobs")
    node_ids, gpu_ids, job_ids = set(), set(), set()
    for index, node in enumerate(manifest["nodes"]):
        path = f"manifest.nodes[{index}]"
        _object(node, ("id", "owner", "cpu_units", "ram_mib", "gpus"), path)
        _unique_id(node["id"], node_ids, path + ".id")
        _identifier(node["owner"], path + ".owner")
        _integer(node["cpu_units"], 0, 65536, path + ".cpu_units")
        _integer(node["ram_mib"], 0, _MEMORY_MAX, path + ".ram_mib")
        _list(node["gpus"], 0, 8, path + ".gpus")
        for gpu_index, gpu in enumerate(node["gpus"]):
            gpu_path = f"{path}.gpus[{gpu_index}]"
            _object(gpu, ("id", "family", "vram_mib"), gpu_path)
            _unique_id(gpu["id"], gpu_ids, gpu_path + ".id")
            _identifier(gpu["family"], gpu_path + ".family")
            _integer(gpu["vram_mib"], 1, _MEMORY_MAX, gpu_path + ".vram_mib")
    if len(gpu_ids) > 8:
        raise ValueError("manifest has more than eight GPUs in total")

    for index, job in enumerate(manifest["jobs"]):
        path = f"manifest.jobs[{index}]"
        _object(job, ("id", "priority", "cpu_units", "ram_mib", "gpu_count",
                      "min_vram_mib", "allowed_families", "allowed_owners"), path)
        _unique_id(job["id"], job_ids, path + ".id")
        _integer(job["priority"], 1, 1000000, path + ".priority")
        _integer(job["cpu_units"], 1, 65536, path + ".cpu_units")
        _integer(job["ram_mib"], 1, _MEMORY_MAX, path + ".ram_mib")
        _integer(job["gpu_count"], 1, 8, path + ".gpu_count")
        _integer(job["min_vram_mib"], 1, _MEMORY_MAX, path + ".min_vram_mib")
        _id_list(job["allowed_families"], 1, 16, path + ".allowed_families")
        _id_list(job["allowed_owners"], 1, 16, path + ".allowed_owners")


def _check_plan(manifest, plan):
    _object(plan, ("schema_version", "placements", "deferred"), "plan")
    _integer(plan["schema_version"], 1, 1, "plan.schema_version")
    _list(plan["placements"], 0, 8, "plan.placements")
    _id_list(plan["deferred"], 0, 8, "plan.deferred")
    nodes = {node["id"]: node for node in manifest["nodes"]}
    jobs = {job["id"]: job for job in manifest["jobs"]}
    gpus = {gpu["id"]: (node["id"], gpu)
            for node in manifest["nodes"] for gpu in node["gpus"]}
    covered_jobs = set()
    used_gpus = set()
    cpu_used = {node_id: 0 for node_id in nodes}
    ram_used = {node_id: 0 for node_id in nodes}
    priority = 0

    for job_id in plan["deferred"]:
        if job_id not in jobs:
            raise ValueError("plan.deferred names an unknown job")
        covered_jobs.add(job_id)

    for index, placement in enumerate(plan["placements"]):
        path = f"plan.placements[{index}]"
        _object(placement, ("job", "node", "gpus"), path)
        _identifier(placement["job"], path + ".job")
        _identifier(placement["node"], path + ".node")
        _id_list(placement["gpus"], 1, 8, path + ".gpus")
        job_id, node_id = placement["job"], placement["node"]
        if job_id not in jobs or node_id not in nodes:
            raise ValueError(path + " names an unknown job or node")
        if job_id in covered_jobs:
            raise ValueError(path + " covers a job more than once")
        covered_jobs.add(job_id)
        job, node = jobs[job_id], nodes[node_id]
        if len(placement["gpus"]) != job["gpu_count"]:
            raise ValueError(path + " has the wrong GPU count for its job")
        if node["owner"] not in job["allowed_owners"]:
            raise ValueError(path + " uses a disallowed owner")
        families = set()
        for gpu_id in placement["gpus"]:
            if gpu_id not in gpus:
                raise ValueError(path + " names an unknown GPU")
            if gpu_id in used_gpus:
                raise ValueError(path + " reuses a GPU")
            used_gpus.add(gpu_id)
            parent_node, gpu = gpus[gpu_id]
            if parent_node != node_id:
                raise ValueError(path + " uses a GPU on a different node")
            if gpu["family"] not in job["allowed_families"]:
                raise ValueError(path + " uses a disallowed GPU family")
            if gpu["vram_mib"] < job["min_vram_mib"]:
                raise ValueError(path + " uses a GPU below the per-device VRAM minimum")
            families.add(gpu["family"])
        if len(families) != 1:
            raise ValueError(path + " mixes GPU families within one job")
        cpu_used[node_id] += job["cpu_units"]
        ram_used[node_id] += job["ram_mib"]
        if cpu_used[node_id] > node["cpu_units"]:
            raise ValueError(path + " exceeds node CPU capacity")
        if ram_used[node_id] > node["ram_mib"]:
            raise ValueError(path + " exceeds node host-RAM capacity")
        priority += job["priority"]

    if covered_jobs != set(jobs):
        raise ValueError("plan does not cover every job exactly once")
    return priority, len(plan["placements"])


def verify_plan(manifest, plan):
    """Return a recomputed feasible score or a fail-closed invalid result.

    A malformed manifest raises ValueError. A malformed or infeasible plan
    returns one diagnostic and no score. This does not certify optimality.
    """
    validate_manifest(manifest)
    try:
        priority, admitted = _check_plan(manifest, plan)
    except ValueError as error:
        return {"valid": False, "errors": [str(error)],
                "priority": None, "admitted": None}
    return {"valid": True, "errors": [],
            "priority": priority, "admitted": admitted}
