"""Independent placement-oracle regression tests; no solver/verifier imports."""

import copy
import unittest

from oracle import optimum


def gpu(identifier, family="A", vram=16):
    return {"id": identifier, "family": family, "vram_mib": vram}


def node(identifier="N", *, owner="Owner", cpu=8, ram=32, gpus=()):
    return {
        "id": identifier, "owner": owner, "cpu_units": cpu,
        "ram_mib": ram, "gpus": list(gpus),
    }


def job(identifier="J", *, priority=1, cpu=1, ram=1, count=1,
        vram=1, families=("A",), owners=("Owner",)):
    return {
        "id": identifier, "priority": priority, "cpu_units": cpu,
        "ram_mib": ram, "gpu_count": count, "min_vram_mib": vram,
        "allowed_families": list(families), "allowed_owners": list(owners),
    }


def manifest(nodes, jobs):
    return {"schema_version": 1, "nodes": nodes, "jobs": jobs}


class OracleTests(unittest.TestCase):
    def test_no_jobs_and_no_gpus(self):
        self.assertEqual(optimum(manifest([node(cpu=0, ram=0)], [])), (0, 0))

    def test_no_fit(self):
        self.assertEqual(optimum(manifest([node()], [job()])), (0, 0))

    def test_vram_is_not_fungible(self):
        m = manifest([node(gpus=[gpu("G1", vram=8), gpu("G2", vram=8)])],
                     [job(count=1, vram=16, priority=90)])
        self.assertEqual(optimum(m), (0, 0))

    def test_every_gpu_in_gang_meets_vram(self):
        m = manifest([node(gpus=[gpu("G1", vram=24), gpu("G2", vram=8)])],
                     [job(count=2, vram=16)])
        self.assertEqual(optimum(m), (0, 0))

    def test_owner_filter_even_with_identical_hardware(self):
        m = manifest([
            node("N1", owner="Denied", gpus=[gpu("G1", vram=32)]),
            node("N2", owner="Allowed", gpus=[gpu("G2", vram=8)]),
        ], [job(owners=("Allowed",), vram=16)])
        self.assertEqual(optimum(m), (0, 0))
        m["jobs"][0]["allowed_owners"].append("Denied")
        self.assertEqual(optimum(m), (1, 1))

    def test_global_gpu_exclusive_even_for_small_vram_jobs(self):
        m = manifest([node(gpus=[gpu("G", vram=1024)])], [
            job("J1", priority=3, vram=1), job("J2", priority=5, vram=1),
        ])
        self.assertEqual(optimum(m), (5, 1))

    def test_gpu_identity_is_global_not_node_local(self):
        m = manifest([
            node("N1", gpus=[gpu("G1")]),
            node("N2", gpus=[gpu("G2")]),
        ], [job("J1", priority=3), job("J2", priority=5)])
        self.assertEqual(optimum(m), (8, 2))

    def test_cpu_and_ram_joint_capacity(self):
        # All pairs meet one resource limit or the other; only B+C meet both.
        m = manifest([node(cpu=6, ram=6,
                           gpus=[gpu("G1"), gpu("G2"), gpu("G3")])], [
            job("A", priority=10, cpu=4, ram=4),
            job("B", priority=6, cpu=3, ram=2),
            job("C", priority=6, cpu=2, ram=3),
        ])
        self.assertEqual(optimum(m), (12, 2))

    def test_node_resources_cannot_be_pooled(self):
        m = manifest([
            node("N1", cpu=4, ram=1, gpus=[gpu("G1")]),
            node("N2", cpu=1, ram=4, gpus=[gpu("G2")]),
        ], [job(cpu=2, ram=2)])
        self.assertEqual(optimum(m), (0, 0))

    def test_same_family_gang(self):
        m = manifest([node(gpus=[gpu("G1", "A"), gpu("G2", "B")])],
                     [job(count=2, families=("A", "B"))])
        self.assertEqual(optimum(m), (0, 0))
        m["nodes"][0]["gpus"][1]["family"] = "A"
        self.assertEqual(optimum(m), (1, 1))

    def test_same_node_gang(self):
        m = manifest([
            node("N1", gpus=[gpu("G1")]),
            node("N2", gpus=[gpu("G2")]),
        ], [job(count=2)])
        self.assertEqual(optimum(m), (0, 0))

    def test_priority_before_admitted_count(self):
        m = manifest([node(gpus=[gpu("G1"), gpu("G2")])], [
            job("High", priority=7, count=2),
            job("Low1", priority=3), job("Low2", priority=3),
        ])
        self.assertEqual(optimum(m), (7, 1))

    def test_admitted_count_breaks_equal_priority(self):
        m = manifest([node(gpus=[gpu("G1"), gpu("G2")])], [
            job("High", priority=6, count=2),
            job("Low1", priority=3), job("Low2", priority=3),
        ])
        self.assertEqual(optimum(m), (6, 2))

    def test_search_finds_assignment_behind_resource_conflict(self):
        # Flexible has two choices, Large has three GPU-pair choices. Trying
        # Flexible on N1 first consumes CPU needed by Large; N2 is the solution.
        m = manifest([
            node("N1", cpu=2, ram=4, gpus=[gpu("G1", vram=32),
                                          gpu("G2", vram=8),
                                          gpu("G3", vram=8)]),
            node("N2", cpu=1, ram=4, gpus=[gpu("G4", vram=32)]),
        ], [
            job("Flexible", vram=16),
            job("Large", cpu=2, count=2),
        ])
        self.assertEqual(optimum(m), (2, 2))

    def test_absent_families_and_owners_are_infeasible(self):
        m = manifest([node(gpus=[gpu("G")])], [
            job("WrongFamily", families=("Absent",)),
            job("WrongOwner", owners=("Absent",)),
        ])
        self.assertEqual(optimum(m), (0, 0))

    def test_namespace_overlap_and_input_unchanged(self):
        m = manifest([node("Same", gpus=[gpu("Same")])], [job("Same")])
        original = copy.deepcopy(m)
        self.assertEqual(optimum(m), (1, 1))
        self.assertEqual(m, original)

    def test_boundary_eight_jobs_gpus_four_nodes(self):
        nodes = [node("N" + str(i), gpus=[gpu("G" + str(2*i)),
                                        gpu("G" + str(2*i+1))])
                 for i in range(4)]
        jobs = [job("J" + str(i), priority=i+1) for i in range(8)]
        self.assertEqual(optimum(manifest(nodes, jobs)), (36, 8))

    def test_exact_large_integer_ram(self):
        large = 1099511627776
        m = manifest([node(ram=large, gpus=[gpu("G1"), gpu("G2")])], [
            job("J1", priority=7, ram=large // 2 + 1),
            job("J2", priority=5, ram=large // 2),
        ])
        self.assertEqual(optimum(m), (7, 1))


if __name__ == "__main__":
    unittest.main()
