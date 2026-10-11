"""Hardware-free tests: all NVML calls use explicit fake modules."""
import copy
import threading
import time
from types import SimpleNamespace
import unittest

from telemetry import NVMLBackend, SamplingThread, TelemetryError, integrate_energy


def sample(t, power=10.0, energy=None, uuids=("GPU-a",), read_seconds=0.0):
    return {"sample_monotonic": t, "read_start_monotonic": t - read_seconds / 2,
            "read_end_monotonic": t + read_seconds / 2, "status": "ok", "error": None,
            "readings": [{"gpu_uuid": u, "power_w": power, "cumulative_energy_j": energy,
                          "status": "ok"} for u in uuids]}


def integrate(rows, start=0, end=2, uuids=("GPU-a",), **kwargs):
    return integrate_energy(rows, start, end, uuids, max_gap_seconds=kwargs.pop("max_gap_seconds", 1.0),
                            max_read_seconds=kwargs.pop("max_read_seconds", 0.05), **kwargs)


class IntegrationTests(unittest.TestCase):
    def test_constant_power(self):
        r = integrate([sample(t) for t in (0, 1, 2)])
        self.assertEqual(r["aggregate_board_energy_j"], 20)
        self.assertEqual(r["per_gpu"]["GPU-a"]["method"], "trapezoidal_power")
        self.assertIn("one-second", r["power_warning"])

    def test_ramp_interpolated_boundaries(self):
        r = integrate([sample(0, 0), sample(1, 10), sample(2, 20)], 0.5, 1.5)
        self.assertEqual(r["aggregate_board_energy_j"], 10)

    def test_counter_preferred_beside_power_diagnostic(self):
        r = integrate([sample(0, 10, 100), sample(1, 10, 112), sample(2, 10, 124)], 0.5, 1.5)
        self.assertEqual(r["aggregate_board_energy_j"], 12)
        self.assertEqual(r["aggregate_power_integral_j"], 10)
        self.assertEqual(r["per_gpu"]["GPU-a"]["counter_minus_power_j"], 2)

    def test_counter_reset_is_error(self):
        with self.assertRaisesRegex(TelemetryError, "reset"):
            integrate([sample(0, 10, 100), sample(1, 10, 5), sample(2, 10, 15)])

    def test_partial_counter_loss_is_error(self):
        with self.assertRaisesRegex(TelemetryError, "partial"):
            integrate([sample(0, 10, 100), sample(1), sample(2, 10, 120)])

    def test_boundaries_require_brackets(self):
        for start, end in [(-0.1, 1), (1, 2.1)]:
            with self.subTest(start=start), self.assertRaisesRegex(TelemetryError, "bracket"):
                integrate([sample(0), sample(1), sample(2)], start, end)

    def test_gap_rejected(self):
        with self.assertRaisesRegex(TelemetryError, "gap"):
            integrate([sample(0), sample(2)], max_gap_seconds=1)

    def test_slow_read_rejected(self):
        with self.assertRaisesRegex(TelemetryError, "latency"):
            integrate([sample(0), sample(1, read_seconds=0.2), sample(2)])

    def test_missing_sample_reading_rejected(self):
        rows = [sample(0), sample(1), sample(2)]
        rows[1]["readings"] = []
        with self.assertRaisesRegex(TelemetryError, "fixed board"):
            integrate(rows)

    def test_nonfinite_missing_and_negative_power_rejected(self):
        for value in (None, float("nan"), float("inf"), -1):
            with self.subTest(value=value), self.assertRaises(TelemetryError):
                integrate([sample(0), sample(1, value), sample(2)])

    def test_multi_gpu_aggregate(self):
        r = integrate([sample(t, uuids=("GPU-a", "GPU-b")) for t in (0, 1, 2)], uuids=("GPU-a", "GPU-b"))
        self.assertEqual(r["aggregate_board_energy_j"], 40)

    def test_one_gpu_failure_invalidates_whole_sum(self):
        rows = [sample(t, uuids=("GPU-a", "GPU-b")) for t in (0, 1, 2)]
        rows[1]["readings"][1]["status"] = "error"
        with self.assertRaisesRegex(TelemetryError, "GPU reading"):
            integrate(rows, uuids=("GPU-a", "GPU-b"))

    def test_duplicate_gpu_fails(self):
        rows = [sample(t, uuids=("GPU-a", "GPU-a")) for t in (0, 1, 2)]
        with self.assertRaises(TelemetryError):
            integrate(rows)

    def test_sample_exception_fails(self):
        rows = [sample(0), sample(1), sample(2)]
        rows[1]["status"] = "error"
        rows[1]["error"] = "read failed"
        with self.assertRaisesRegex(TelemetryError, "read failed"):
            integrate(rows)

    def test_order_and_timestamp_consistency(self):
        with self.assertRaisesRegex(TelemetryError, "increasing"):
            integrate([sample(0), sample(2), sample(1)])
        rows = [sample(0), sample(1), sample(2)]
        rows[1]["read_start_monotonic"] = 1.01
        rows[1]["read_end_monotonic"] = 1.02
        with self.assertRaisesRegex(TelemetryError, "outside"):
            integrate(rows)

    def test_irrelevant_outside_interval_error_does_not_pollute(self):
        rows = [sample(t) for t in (-1, 0, 1, 2, 3)]
        rows[0]["status"] = "error"
        rows[-1]["status"] = "error"
        self.assertEqual(integrate(rows)["aggregate_board_energy_j"], 20)


class FakeNVML:
    class NVMLError_NotSupported(Exception):
        pass

    def __init__(self, unsupported=False, fail_gpu=None, wrong_uuid=False):
        self.unsupported = unsupported
        self.fail_gpu = fail_gpu
        self.wrong_uuid = wrong_uuid
        self.init_count = 0
        self.close_count = 0

    def nvmlInit(self): self.init_count += 1
    def nvmlShutdown(self): self.close_count += 1
    def nvmlSystemGetDriverVersion(self): return b"fake-driver"
    def nvmlDeviceGetHandleByUUID(self, uuid): return uuid
    def nvmlDeviceGetUUID(self, handle): return "GPU-wrong" if self.wrong_uuid else handle
    def nvmlDeviceGetName(self, handle): return b"fake GPU"
    def nvmlDeviceGetMemoryInfo(self, handle): return SimpleNamespace(total=80 * 1024**3)
    def nvmlDeviceGetPowerManagementLimit(self, handle): return 250000
    def nvmlDeviceGetPowerManagementDefaultLimit(self, handle): return 300000
    def nvmlDeviceGetPowerManagementLimitConstraints(self, handle): return (100000, 350000)
    def nvmlDeviceGetPowerUsage(self, handle):
        if handle == self.fail_gpu:
            raise RuntimeError("lost GPU")
        return 123000
    def nvmlDeviceGetTotalEnergyConsumption(self, handle):
        if self.unsupported:
            raise self.NVMLError_NotSupported("counter unsupported")
        return 456000


class NVMLTests(unittest.TestCase):
    def test_units_metadata_and_idempotent_close(self):
        fake = FakeNVML()
        with NVMLBackend(["GPU-a"], _nvml_module=fake) as backend:
            row = backend.read()[0]
            self.assertEqual((row["power_w"], row["cumulative_energy_j"]), (123, 456))
            self.assertEqual(backend.metadata["boards"][0]["power_limit_w"], 250)
            self.assertEqual(backend.metadata["driver_version"], "fake-driver")
        backend.close()
        self.assertEqual(fake.close_count, 1)

    def test_unsupported_energy_not_zero(self):
        with NVMLBackend(["GPU-a"], _nvml_module=FakeNVML(unsupported=True)) as backend:
            row = backend.read()[0]
            self.assertIsNone(row["cumulative_energy_j"])
            self.assertEqual(row["energy_counter_status"], "unsupported")
            self.assertEqual(row["status"], "ok")

    def test_failed_board_preserved_not_dropped(self):
        with NVMLBackend(["GPU-a", "GPU-b"], _nvml_module=FakeNVML(fail_gpu="GPU-b")) as backend:
            rows = backend.read()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[1]["status"], "error")
            self.assertIsNone(rows[1]["power_w"])
            self.assertIn("lost GPU", rows[1]["error"])

    def test_compute_process_ids_sorted_and_unique(self):
        fake = FakeNVML()
        fake.nvmlDeviceGetComputeRunningProcesses = lambda handle: [
            SimpleNamespace(pid=901), SimpleNamespace(pid=101), SimpleNamespace(pid=901)]
        with NVMLBackend(["GPU-a"], _nvml_module=fake) as backend:
            row = backend.read()[0]
            self.assertEqual(row["compute_process_ids"], [101, 901])
            self.assertEqual(row["compute_process_status"], "ok")
            self.assertIsNone(row["compute_process_error"])

    def test_compute_process_genuinely_empty_is_distinct_from_unsupported(self):
        fake = FakeNVML()
        fake.nvmlDeviceGetComputeRunningProcesses = lambda handle: []
        with NVMLBackend(["GPU-a"], _nvml_module=fake) as backend:
            row = backend.read()[0]
            self.assertEqual(row["compute_process_ids"], [])
            self.assertEqual(row["compute_process_status"], "ok")

    def test_compute_process_missing_api_is_none_not_empty(self):
        with NVMLBackend(["GPU-a"], _nvml_module=FakeNVML()) as backend:
            row = backend.read()[0]
            self.assertIsNone(row["compute_process_ids"])
            self.assertEqual(row["compute_process_status"], "unsupported")
            self.assertIn("unavailable", row["compute_process_error"])
            self.assertEqual(row["power_w"], 123)

    def test_compute_process_not_supported_is_none(self):
        fake = FakeNVML()
        def unsupported(handle):
            raise fake.NVMLError_NotSupported("not supported on board")
        fake.nvmlDeviceGetComputeRunningProcesses = unsupported
        with NVMLBackend(["GPU-a"], _nvml_module=fake) as backend:
            row = backend.read()[0]
            self.assertIsNone(row["compute_process_ids"])
            self.assertEqual(row["compute_process_status"], "unsupported")
            self.assertIn("not supported on board", row["compute_process_error"])
            self.assertEqual(row["cumulative_energy_j"], 456)

    def test_compute_process_query_error_preserves_power(self):
        fake = FakeNVML()
        def denied(handle):
            raise PermissionError("cannot query PIDs")
        fake.nvmlDeviceGetComputeRunningProcesses = denied
        with NVMLBackend(["GPU-a"], _nvml_module=fake) as backend:
            row = backend.read()[0]
            self.assertIsNone(row["compute_process_ids"])
            self.assertEqual(row["compute_process_status"], "error")
            self.assertIn("PermissionError", row["compute_process_error"])
            self.assertEqual(row["power_w"], 123)
            self.assertEqual(row["cumulative_energy_j"], 456)
            self.assertEqual(row["status"], "ok")

    def test_compute_process_invalid_pid_is_error(self):
        fake = FakeNVML()
        fake.nvmlDeviceGetComputeRunningProcesses = lambda handle: [SimpleNamespace(pid="101")]
        with NVMLBackend(["GPU-a"], _nvml_module=fake) as backend:
            row = backend.read()[0]
            self.assertIsNone(row["compute_process_ids"])
            self.assertEqual(row["compute_process_status"], "error")

    def test_compute_process_reads_each_selected_gpu(self):
        fake = FakeNVML()
        fake.nvmlDeviceGetComputeRunningProcesses = lambda handle: [SimpleNamespace(pid={"GPU-a": 11, "GPU-b": 22}[handle])]
        with NVMLBackend(["GPU-a", "GPU-b"], _nvml_module=fake) as backend:
            rows = backend.read()
            self.assertEqual([row["compute_process_ids"] for row in rows], [[11], [22]])

    def test_init_validation_failure_shuts_down(self):
        fake = FakeNVML(wrong_uuid=True)
        with self.assertRaises(TelemetryError):
            NVMLBackend(["GPU-a"], _nvml_module=fake)
        self.assertEqual(fake.close_count, 1)

    def test_uuid_selection_validated_before_init(self):
        for uuids in ([], ["GPU-a", "GPU-a"], ["MIG-a"], ["0"]):
            fake = FakeNVML()
            with self.subTest(uuids=uuids), self.assertRaises(TelemetryError):
                NVMLBackend(uuids, _nvml_module=fake)
            self.assertEqual(fake.init_count, 0)


class SamplingTests(unittest.TestCase):
    def test_exception_retained_and_shutdown(self):
        closed = []
        def fail():
            raise RuntimeError("read failure")
        sampler = SamplingThread(fail, interval_seconds=1, close_callable=lambda: closed.append(True)).start()
        self.assertTrue(sampler.wait_for_first_sample())
        records = sampler.stop()
        self.assertEqual(len(records), 2)
        self.assertTrue(all(row["status"] == "error" for row in records))
        self.assertIn("read failure", records[0]["error"])
        self.assertEqual(records[-1]["phase"], "drain")
        self.assertEqual(closed, [True])
        self.assertGreaterEqual(records[0]["read_end_monotonic"], records[0]["read_start_monotonic"])

    def test_slow_reads_do_not_catch_up_busy_loop(self):
        called = []
        reached = threading.Event()
        def slow():
            called.append(time.monotonic())
            time.sleep(0.025)
            if len(called) >= 3:
                reached.set()
            return [{"gpu_uuid": "GPU-a", "power_w": 1, "cumulative_energy_j": None}]
        sampler = SamplingThread(slow, interval_seconds=0.02).start()
        self.assertTrue(reached.wait(2))
        records = sampler.stop()
        regular = [row for row in records if row["phase"] == "regular"]
        self.assertGreaterEqual(len(regular), 3)
        # Compare end-to-next-start; scheduler delays can only increase the gap.
        for a, b in zip(regular, regular[1:]):
            self.assertGreaterEqual(b["read_start_monotonic"] - a["read_end_monotonic"], 0.018)

    def test_stop_finishes_inflight_and_drains_before_close(self):
        entered = threading.Event()
        release = threading.Event()
        order = []
        def read():
            order.append("read")
            entered.set()
            release.wait(2)
            return [{"gpu_uuid": "GPU-a", "power_w": 1}]
        sampler = SamplingThread(read, interval_seconds=1, close_callable=lambda: order.append("close")).start()
        self.assertTrue(entered.wait(1))
        with self.assertRaises(TimeoutError):
            sampler.stop(timeout=0.001)
        self.assertNotIn("close", order)
        release.set()
        records = sampler.stop(timeout=2)
        self.assertEqual(order, ["read", "read", "close"])
        self.assertEqual(records[-1]["phase"], "drain")

    def test_bound_backend_closed_automatically(self):
        fake = FakeNVML()
        backend = NVMLBackend(["GPU-a"], _nvml_module=fake)
        sampler = SamplingThread(backend.read, interval_seconds=1).start()
        self.assertTrue(sampler.wait_for_first_sample())
        sampler.stop()
        self.assertEqual(fake.close_count, 1)

    def test_invalid_interval_and_start_reuse(self):
        with self.assertRaises(TelemetryError):
            SamplingThread(lambda: [], interval_seconds=0)
        sampler = SamplingThread(lambda: []).start()
        sampler.stop()
        with self.assertRaises(RuntimeError):
            sampler.start()


if __name__ == "__main__":
    unittest.main()
