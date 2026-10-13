"""Independent exact objective oracle for VALID GPU snapshot v1 manifests.

``optimum(manifest)`` returns (total admitted priority, admitted job count).
It deliberately does not validate input: callers must supply manifests satisfying
the v1 contract, in particular at most 8 jobs, 8 physical GPUs, and 4 nodes.
There are no solver/verifier imports or external dependencies.

Correctness: enumerate every admitted-job subset, in descending lexicographic
objective order. For a subset, exhaustively backtrack over every same-node,
same-family GPU combination satisfying each job's per-GPU and owner conditions.
Track each physical GPU with a distinct bit and each node's residual CPU/RAM;
thus every explored complete assignment is feasible. Conversely, every feasible
assignment uses one of the enumerated choices for each admitted job, so some
branch represents it. Failures may be memoized because the remaining jobs,
occupied GPU bits, and residual resources determine all future feasibility.
The first feasible subset therefore has the exact optimal objective. Empty
admission is included and always feasible.

This is an exponential reference implementation, not a scalable scheduler:
there are 2**J subsets and combinatorial GPU assignments. The contract's small
J <= 8, G <= 8, N <= 4 limits are essential. Most-constrained-first search,
memoization, and aggregate resource lower bounds reduce work without relaxing
the placement rules. No runtimes, performance gains, or production claims are
implied.
"""

from functools import lru_cache
from itertools import combinations


def optimum(manifest):
    """Return the exact (priority, admitted) optimum for a VALID manifest."""
    nodes = manifest["nodes"]
    jobs = manifest["jobs"]
    initial_cpu = tuple(node["cpu_units"] for node in nodes)
    initial_ram = tuple(node["ram_mib"] for node in nodes)

    # IDs need not differ across entity namespaces; only physical GPU identity
    # receives a global bit. Node identity is its position in the node list.
    gpu_bits = {}
    for node in nodes:
        for gpu in node["gpus"]:
            gpu_bits[gpu["id"]] = 1 << len(gpu_bits)

    choices = []
    for job in jobs:
        job_choices = []
        for node_index, node in enumerate(nodes):
            if node["owner"] not in job["allowed_owners"]:
                continue
            if job["cpu_units"] > node["cpu_units"]:
                continue
            if job["ram_mib"] > node["ram_mib"]:
                continue
            families = {}
            for gpu in node["gpus"]:
                if (gpu["family"] in job["allowed_families"]
                        and gpu["vram_mib"] >= job["min_vram_mib"]):
                    families.setdefault(gpu["family"], []).append(
                        gpu_bits[gpu["id"]]
                    )
            for family_bits in families.values():
                for group in combinations(family_bits, job["gpu_count"]):
                    job_choices.append((node_index, sum(group)))
        choices.append(tuple(job_choices))

    @lru_cache(maxsize=None)
    def feasible(remaining_jobs, occupied, cpu_left, ram_left):
        if remaining_jobs == 0:
            return True
        indices = [j for j in range(len(jobs)) if remaining_jobs & (1 << j)]
        if sum(jobs[j]["gpu_count"] for j in indices) > (
            len(gpu_bits) - occupied.bit_count()
        ):
            return False
        if sum(jobs[j]["cpu_units"] for j in indices) > sum(cpu_left):
            return False
        if sum(jobs[j]["ram_mib"] for j in indices) > sum(ram_left):
            return False

        # Dynamically choose the remaining job with the fewest still-feasible
        # placements. Any ordering is complete; this one rejects bottlenecks early.
        selected = None
        options = None
        for job_index in indices:
            job = jobs[job_index]
            available = [
                (node_index, mask)
                for node_index, mask in choices[job_index]
                if not (occupied & mask)
                and job["cpu_units"] <= cpu_left[node_index]
                and job["ram_mib"] <= ram_left[node_index]
            ]
            if not available:
                return False
            if options is None or len(available) < len(options):
                selected, options = job_index, available

        job = jobs[selected]
        for node_index, mask in options:
            next_cpu = list(cpu_left)
            next_ram = list(ram_left)
            next_cpu[node_index] -= job["cpu_units"]
            next_ram[node_index] -= job["ram_mib"]
            if feasible(
                remaining_jobs ^ (1 << selected),
                occupied | mask,
                tuple(next_cpu),
                tuple(next_ram),
            ):
                return True
        return False

    ranked_subsets = []
    for subset in range(1 << len(jobs)):
        score = sum(
            job["priority"]
            for index, job in enumerate(jobs)
            if subset & (1 << index)
        )
        ranked_subsets.append(((score, subset.bit_count()), subset))
    ranked_subsets.sort(reverse=True)
    for objective, subset in ranked_subsets:
        if feasible(subset, 0, initial_cpu, initial_ram):
            return objective
    # The empty subset must succeed, independently of resource quantities.
    raise RuntimeError("internal error: empty admission was not feasible")
