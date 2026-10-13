"""Manual solver fixtures, independent of the comparison cohort or generator."""

import copy
import unittest

from oracle import optimum
from solver import greedy, solve
from verifier import verify_plan


def gpu(identifier, *, family="A", vram=16):
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
    return {"schema_version": 1, "nodes": list(nodes), "jobs": list(jobs)}


class SolverTests(unittest.TestCase):
    strategies = ("priority_first", "scarcity_first")

    def checked_objective(self, m, plan):
        checked = verify_plan(m, plan)
        self.assertTrue(checked["valid"], checked["errors"])
        self.assertEqual(checked["errors"], [])
        self.assertEqual(set(plan), {"schema_version", "placements", "deferred"})
        return checked["priority"], checked["admitted"]

    def assert_optimum(self, m, expected):
        self.assertEqual(optimum(m), expected, "manual expectation vs oracle")
        plan = solve(m)
        self.assertEqual(self.checked_objective(m, plan), expected)
        return plan

    def test_empty_queue_with_no_resources(self):
        m = manifest([node(cpu=0, ram=0)], [])
        expected = {"schema_version": 1, "placements": [], "deferred": []}
        self.assertEqual(self.assert_optimum(m, (0, 0)), expected)
        for strategy in self.strategies:
            with self.subTest(strategy=strategy):
                self.assertEqual(greedy(m, strategy), expected)

    def test_all_infeasible_jobs_are_deferred_once(self):
        m = manifest([node(gpus=[gpu("G")])], [
            job("NoOwner", owners=("Absent",)),
            job("NoFamily", families=("Absent",)),
            job("NoVram", vram=17),
            job("NoCpu", cpu=9),
            job("NoRam", ram=33),
            job("NoGang", count=2),
        ])
        expected_ids = sorted(j["id"] for j in m["jobs"])
        exact = self.assert_optimum(m, (0, 0))
        self.assertEqual(exact["placements"], [])
        self.assertEqual(sorted(exact["deferred"]), expected_ids)
        for strategy in self.strategies:
            with self.subTest(strategy=strategy):
                plan = greedy(m, strategy)
                self.assertEqual(self.checked_objective(m, plan), (0, 0))
                self.assertEqual(sorted(plan["deferred"]), expected_ids)

    def test_priority_precedes_admitted_count(self):
        m = manifest([node(gpus=[gpu("G1"), gpu("G2")])], [
            job("Large", priority=7, count=2),
            job("Small1", priority=3), job("Small2", priority=3),
        ])
        plan = self.assert_optimum(m, (7, 1))
        self.assertEqual([p["job"] for p in plan["placements"]], ["Large"])

    def test_admitted_count_breaks_equal_priority(self):
        m = manifest([node(gpus=[gpu("G1"), gpu("G2")])], [
            job("Large", priority=6, count=2),
            job("Small1", priority=3), job("Small2", priority=3),
        ])
        plan = self.assert_optimum(m, (6, 2))
        self.assertEqual({p["job"] for p in plan["placements"]},
                         {"Small1", "Small2"})

    def test_both_greedy_strategies_can_lose_priority(self):
        m = manifest([node(gpus=[gpu("G1"), gpu("G2")])], [
            job("Large", priority=10, count=2),
            job("Small1", priority=6), job("Small2", priority=6),
        ])
        self.assert_optimum(m, (12, 2))
        for strategy in self.strategies:
            with self.subTest(strategy=strategy):
                plan = greedy(m, strategy)
                self.assertEqual(self.checked_objective(m, plan), (10, 1))

    def test_scarcity_can_prefer_low_priority_under_shared_cpu(self):
        m = manifest([node(cpu=1, gpus=[gpu("G1", family="A"),
                                       gpu("G2", family="B")])], [
            job("Scarce", priority=1, families=("A",)),
            job("Valuable", priority=10, families=("A", "B")),
        ])
        self.assert_optimum(m, (10, 1))
        self.assertEqual(self.checked_objective(m, greedy(m, "priority_first")),
                         (10, 1))
        self.assertEqual(self.checked_objective(m, greedy(m, "scarcity_first")),
                         (1, 1))

    def test_preserves_only_high_vram_gpu_for_constrained_job(self):
        m = manifest([node(gpus=[gpu("G1", vram=32), gpu("G2", vram=8)])], [
            job("AFlexible", priority=6),
            job("BConstrained", priority=5, vram=16),
        ])
        plan = self.assert_optimum(m, (11, 2))
        assignments = {p["job"]: p["gpus"] for p in plan["placements"]}
        self.assertEqual(assignments, {"AFlexible": ["G2"],
                                       "BConstrained": ["G1"]})
        self.assertEqual(self.checked_objective(m, greedy(m, "priority_first")),
                         (6, 1))
        self.assertEqual(self.checked_objective(m, greedy(m, "scarcity_first")),
                         (11, 2))

    def test_backtracks_over_same_family_gpu_gangs(self):
        m = manifest([node(gpus=[gpu("G1", family="A"),
                                gpu("G2", family="A"),
                                gpu("G3", family="B"),
                                gpu("G4", family="B")])], [
            job("AFlexible", priority=5, count=2, families=("A", "B")),
            job("BOnlyA", priority=4, count=2, families=("A",)),
        ])
        plan = self.assert_optimum(m, (9, 2))
        assignments = {p["job"]: set(p["gpus"]) for p in plan["placements"]}
        self.assertEqual(assignments, {"AFlexible": {"G3", "G4"},
                                       "BOnlyA": {"G1", "G2"}})

    def test_backtracks_over_node_cpu_capacity(self):
        m = manifest([
            node("N1", cpu=2, ram=4, gpus=[gpu("G1", vram=32),
                                          gpu("G2", vram=8),
                                          gpu("G3", vram=8)]),
            node("N2", cpu=1, ram=4, gpus=[gpu("G4", vram=32)]),
        ], [job("AFlexible", vram=16), job("BLarge", cpu=2, count=2)])
        plan = self.assert_optimum(m, (2, 2))
        assignments = {p["job"]: p["node"] for p in plan["placements"]}
        self.assertEqual(assignments, {"AFlexible": "N2", "BLarge": "N1"})

    def test_cpu_and_ram_joint_capacity(self):
        m = manifest([node(cpu=6, ram=6,
                           gpus=[gpu("G1"), gpu("G2"), gpu("G3")])], [
            job("A", priority=10, cpu=4, ram=4),
            job("B", priority=6, cpu=3, ram=2),
            job("C", priority=6, cpu=2, ram=3),
        ])
        plan = self.assert_optimum(m, (12, 2))
        self.assertEqual({p["job"] for p in plan["placements"]}, {"B", "C"})

    def test_resources_are_not_pooled_across_nodes(self):
        m = manifest([
            node("N1", cpu=4, ram=1, gpus=[gpu("G1")]),
            node("N2", cpu=1, ram=4, gpus=[gpu("G2")]),
        ], [job(cpu=2, ram=2)])
        self.assert_optimum(m, (0, 0))

    def test_vram_not_pooled_across_gpus(self):
        m = manifest([node(gpus=[gpu("G1", vram=8), gpu("G2", vram=8)])],
                     [job(vram=16)])
        self.assert_optimum(m, (0, 0))

    def test_gang_must_share_family_and_node(self):
        fixtures = [
            manifest([node(gpus=[gpu("G1", family="A"),
                                  gpu("G2", family="B")])],
                     [job(count=2, families=("A", "B"))]),
            manifest([node("N1", gpus=[gpu("G1")]),
                      node("N2", gpus=[gpu("G2")])], [job(count=2)]),
        ]
        for index, m in enumerate(fixtures):
            with self.subTest(fixture=index):
                self.assert_optimum(m, (0, 0))

    def test_gpu_is_wholly_occupied_for_tiny_vram_jobs(self):
        m = manifest([node(gpus=[gpu("G", vram=1024)])], [
            job("J1", priority=3, vram=1), job("J2", priority=5, vram=1),
        ])
        self.assert_optimum(m, (5, 1))

    def test_owner_filter_controls_placement(self):
        m = manifest([
            node("First", owner="Denied", gpus=[gpu("G1")]),
            node("Second", owner="Allowed", gpus=[gpu("G2")]),
        ], [job(owners=("Allowed",))])
        plan = self.assert_optimum(m, (1, 1))
        self.assertEqual(plan["placements"],
                         [{"job": "J", "node": "Second", "gpus": ["G2"]}])

    def test_same_id_in_separate_namespaces(self):
        m = manifest([node("Same", gpus=[gpu("Same")])], [job("Same")])
        self.assert_optimum(m, (1, 1))

    def test_input_order_invariance_and_no_mutation(self):
        m = manifest([
            node("N2", owner="O2", gpus=[gpu("G4", family="B"), gpu("G3")]),
            node("N1", owner="O1", gpus=[gpu("G2", family="B"), gpu("G1")]),
        ], [
            job("J2", priority=2, owners=("O2", "O1"), families=("B", "A")),
            job("J1", priority=2, owners=("O2", "O1"), families=("B", "A")),
        ])
        reordered = copy.deepcopy(m)
        reordered["nodes"].reverse()
        reordered["jobs"].reverse()
        for n in reordered["nodes"]:
            n["gpus"].reverse()
        for j in reordered["jobs"]:
            j["allowed_families"].reverse()
            j["allowed_owners"].reverse()
        for name, run in [("exact", solve)] + [
            (strategy, lambda value, s=strategy: greedy(value, s))
            for strategy in self.strategies
        ]:
            with self.subTest(solver=name):
                original = copy.deepcopy(m)
                reversed_original = copy.deepcopy(reordered)
                first, second = run(m), run(reordered)
                self.assertEqual(self.checked_objective(m, first), (4, 2))
                self.assertEqual(self.checked_objective(reordered, second), (4, 2))
                self.assertEqual(first, second)
                self.assertEqual(m, original)
                self.assertEqual(reordered, reversed_original)

    def test_repeated_calls_do_not_reuse_resource_state(self):
        m = manifest([node(gpus=[gpu("G")])], [job(priority=7)])
        first = solve(m)
        self.assertEqual(solve(m), first)
        empty = manifest([node(cpu=0, ram=0)], [])
        self.assertEqual(self.checked_objective(empty, solve(empty)), (0, 0))
        self.assertEqual(solve(m), first)
        for strategy in self.strategies:
            self.assertEqual(self.checked_objective(m, greedy(m, strategy)), (7, 1))
            self.assertEqual(self.checked_objective(m, greedy(m, strategy)), (7, 1))

    def test_exact_integer_resource_boundary(self):
        large = 1099511627776
        m = manifest([node(ram=large, gpus=[gpu("G1"), gpu("G2")])], [
            job("A", priority=7, ram=large // 2 + 1),
            job("B", priority=5, ram=large // 2),
        ])
        self.assert_optimum(m, (7, 1))

    def test_eight_jobs_and_gpus_on_four_nodes(self):
        nodes = [node("N" + str(i), gpus=[gpu("G" + str(2*i)),
                                        gpu("G" + str(2*i+1))])
                 for i in range(4)]
        jobs = [job("J" + str(i), priority=i+1) for i in range(8)]
        self.assert_optimum(manifest(nodes, jobs), (36, 8))

    def test_eight_gpu_gang_and_exact_schema_maxima(self):
        large = 1099511627776
        owner_id = "O" * 32
        family_id = "F" * 32
        gpu_ids = ["G" + str(i) + "x" * 30 for i in range(8)]
        m = manifest([
            node("N" * 32, owner=owner_id, cpu=65536, ram=large,
                 gpus=[gpu(identifier, family=family_id, vram=large)
                       for identifier in gpu_ids]),
        ], [
            job("J" * 32, priority=1000000, cpu=65536, ram=large, count=8,
                vram=large,
                families=tuple("AbsentF" + str(i) for i in range(15)) + (family_id,),
                owners=tuple("AbsentO" + str(i) for i in range(15)) + (owner_id,)),
        ])
        plan = self.assert_optimum(m, (1000000, 1))
        self.assertEqual(set(plan["placements"][0]["gpus"]), set(gpu_ids))
        for strategy in self.strategies:
            with self.subTest(strategy=strategy):
                self.assertEqual(self.checked_objective(m, greedy(m, strategy)),
                                 (1000000, 1))

    def test_zero_cpu_or_ram_blocks_jobs_with_available_gpu(self):
        for cpu, ram in [(0, 32), (8, 0)]:
            with self.subTest(cpu=cpu, ram=ram):
                m = manifest([node(cpu=cpu, ram=ram, gpus=[gpu("G")])], [job()])
                self.assert_optimum(m, (0, 0))
                for strategy in self.strategies:
                    self.assertEqual(self.checked_objective(m, greedy(m, strategy)),
                                     (0, 0))

    def test_mixed_present_and_absent_policy_entries(self):
        m = manifest([node(gpus=[gpu("G")])], [
            job(priority=9, owners=("AbsentOwner", "Owner"),
                families=("AbsentFamily", "A")),
        ])
        self.assert_optimum(m, (9, 1))
        for strategy in self.strategies:
            with self.subTest(strategy=strategy):
                self.assertEqual(self.checked_objective(m, greedy(m, strategy)),
                                 (9, 1))

    def test_unknown_greedy_strategy_rejected(self):
        m = manifest([node()], [])
        with self.assertRaises(ValueError):
            greedy(m, "unknown")


if __name__ == "__main__":
    unittest.main()
