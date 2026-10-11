"""Focused physical, accounting, and information-flow tests for the replay engine."""
import unittest

from replay import Job, Service, _choose_dispatch, replay


def job(name, arrival=0.0, deadline=10.0, prediction=(1.0, 1.0), actual=None, tail=0.0):
    predicted = {0: Service(*prediction), 1: Service(*prediction)}
    realized = {0: Service(*(actual or prediction)), 1: Service(*(actual or prediction))}
    return Job(name, arrival, deadline, predicted, realized, tail)


class ReplayTests(unittest.TestCase):
    def test_deterministic_ties_and_no_overlap(self):
        result = replay([job("b"), job("a"), job("c")], [10, 10], "pool")
        self.assertEqual([(r["id"], r["server"], r["start"]) for r in result["records"]],
                         [("a", 0, 0), ("b", 1, 0), ("c", 0, 1)])
        self.assertEqual(result["ontime"], 3)
        self.assertTrue(result["unique_started_ids"])
        self.assertTrue(result["no_server_overlap"])
        self.assertEqual(result["peak_busy"], 2)
        self.assertEqual(result["total_energy_j"], 3)

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            replay([job("a"), job("a")], [10, 10], "pool")

    def test_deadline_expiration_without_start(self):
        result = replay([job("a", deadline=0.5)], [10, 10], "pool")
        self.assertEqual((result["started"], result["rejected"]), (0, 1))
        self.assertEqual(result["rejections"][0]["time"], 0.5)
        self.assertEqual(result["total_energy_j"], 0)

    def test_actual_late_is_not_rejected_or_clipped(self):
        result = replay([job("a", deadline=1.5, actual=(2, 1))], [10, 10], "pool")
        self.assertEqual((result["late"], result["rejected"]), (1, 0))
        self.assertEqual(result["records"][0]["end"], 2)

    def test_actual_energy_overrun_settles_as_debt(self):
        result = replay([job("a", prediction=(1, 1), actual=(1, 4))], [1, 1], "pool")
        self.assertEqual(result["total_energy_j"], 4)
        self.assertEqual(result["remaining_accounts_j"], [-2])
        self.assertEqual(result["max_actual_budget_overrun_j"], 2)
        self.assertEqual(result["max_reservation_and_spend_overrun_j"], 2)
        self.assertEqual(result["per_owner_energy_j"], [4, 0])

    def test_actuals_do_not_change_initial_dispatch(self):
        first = [job("a"), job("b")]
        changed = [job("a", actual=(30, 99)), job("b", actual=(40, 123))]
        a = replay(first, [10, 10], "pool")
        b = replay(changed, [10, 10], "pool")
        project = lambda result: [(r["id"], r["server"], r["start"]) for r in result["records"]]
        self.assertEqual(project(a), project(b))
        self.assertNotEqual(a["total_energy_j"], b["total_energy_j"])

    def test_controller_does_not_read_realized_information(self):
        class ForbiddenRealized:
            def __getitem__(self, key):
                raise AssertionError("controller consulted realized profile")
        a = Job("a", 0, 10, {0: Service(1, 2), 1: Service(2, 1)}, ForbiddenRealized())
        chosen = _choose_dispatch(0, [a], [0, 1], [10], "pool")
        self.assertEqual(chosen[1], 1)
        # Job exposes no realized output-length field to the controller.
        self.assertNotIn("output_length", Job.__dataclass_fields__)

    def test_pooled_budget_and_autarky_use_same_controller(self):
        a = Job("a", 0, 5, {0: Service(1, 2), 1: Service(1, 3)},
                {0: Service(1, 2), 1: Service(1, 3)})
        pool = replay([a], [0, 3], "pool")
        autarky = replay([a], [0, 3], "autarky")
        self.assertEqual(pool["records"][0]["server"], 0)
        self.assertEqual(autarky["records"][0]["server"], 1)
        self.assertEqual(pool["max_actual_budget_overrun_j"], 0)
        # Nominal owner overruns under sharing are not pooled-account violations.
        self.assertEqual(pool["per_owner_nominal_overrun_j"], [2, 0])

    def test_oldest_feasible_can_skip_infeasible_job(self):
        result = replay([job("a", prediction=(1, 20)), job("b")], [1, 1], "pool")
        self.assertEqual([r["id"] for r in result["records"]], ["b"])
        self.assertEqual(result["rejections"][0]["id"], "a")

    def test_completion_releases_funds_before_equal_time_arrival(self):
        a = job("a", prediction=(1, 2), actual=(1, 1))
        b = job("b", arrival=1, deadline=2)
        result = replay([a, b], [1, 1], "pool")
        self.assertEqual([r["start"] for r in result["records"]], [0, 1])
        self.assertEqual(result["remaining_accounts_j"], [0])

    def test_reserved_energy_is_not_double_spent(self):
        result = replay([job("a"), job("b")], [0.5, 0.5], "pool")
        self.assertEqual(result["started"], 1)
        self.assertEqual(result["rejected"], 1)

    def test_response_deadline_excludes_cooldown_but_slot_stays_busy(self):
        a = job("a", deadline=1, prediction=(4.5, 1), tail=3.5)
        b = job("b", deadline=5, prediction=(4.5, 1), tail=3.5)
        # Owner 1 cannot dispatch; owner 0 must wait through the first cooldown.
        result = replay([a, b], [10, 0], "autarky")
        self.assertEqual(result["ontime"], 1)
        self.assertEqual(result["rejected"], 1)
        self.assertEqual(result["records"][0]["response_end"], 1)
        self.assertEqual(result["records"][0]["slot_end"], 4.5)
        self.assertEqual(result["records"][0]["predicted_response_end"], 1)

    def test_response_late_even_with_valid_forecast(self):
        result = replay([job("a", deadline=1, prediction=(4.5, 1), actual=(5.5, 1), tail=3.5)], [1, 0], "autarky")
        self.assertEqual(result["late"], 1)
        self.assertEqual(result["records"][0]["response_end"], 2)

    def test_tail_requires_positive_response_time(self):
        with self.assertRaises(ValueError):
            replay([job("a", tail=1)], [10, 10], "pool")

    def test_no_deadline_boundary_rejection_for_running_request(self):
        result = replay([job("a", deadline=1)], [1, 1], "pool")
        self.assertEqual((result["ontime"], result["rejected"]), (1, 0))

    def test_empty_replay(self):
        result = replay([], [1, 2], "autarky")
        self.assertEqual(result["offered"], 0)
        self.assertTrue(result["terminal_accounting_ok"])
        self.assertEqual(result["remaining_accounts_j"], [1, 2])

    def test_invalid_profiles(self):
        for invalid in [float("nan"), float("inf"), -1]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                replay([job("a", prediction=(invalid, 1))], [1, 1], "pool")
        with self.assertRaises(ValueError):
            replay([job("a")], [1], "pool")


if __name__ == "__main__":
    unittest.main()
