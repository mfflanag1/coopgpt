"""Fixed-board NVML telemetry and strict aggregate-energy integration.

No GPU library is imported until NVMLBackend is instantiated. This module neither
runs workloads nor changes clocks/power limits. NVML board energy excludes the
rest of the host/facility and does not identify per-request energy.

Source: https://docs.nvidia.com/deploy/nvml-api/latest/api/group__nvmlDeviceQueries.html
NVML power is mW and cumulative energy is mJ since driver reload. Power may be a
one-second hardware average (Ampere except GA100, and newer GPUs); dense polling
must not be described as instantaneous high-resolution power measurement.
"""
from __future__ import annotations

import argparse
import bisect
import copy
import importlib
import json
import math
from pathlib import Path
import threading
import time
from typing import Callable, Sequence

POWER_WARNING = (
    "NVML power may be averaged over a one-second hardware interval; dense polling "
    "does not establish instantaneous power. Energy is selected GPU-board energy, "
    "not whole-server/facility energy or per-request attribution."
)


class TelemetryError(ValueError):
    """Data cannot support the requested complete, bracketed energy integral."""


def _number(value, name, *, nonnegative=False, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise TelemetryError(f"{name} must be a finite number")
    if positive and value <= 0 or nonnegative and value < 0:
        raise TelemetryError(f"{name} has an invalid sign")
    return float(value)


def _uuid_list(uuids):
    values = list(uuids)
    if not values or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):
        raise TelemetryError("expected a nonempty list of unique GPU UUIDs")
    return values


class NVMLBackend:
    """Read only explicitly selected full GPU boards, identified by immutable UUID.

    Unsupported cumulative counters are None, never zero. Failed board reads are
    returned as explicit error rows so a later integral cannot silently drop them.
    The private module injection is solely for hardware-free unit tests.
    """

    def __init__(self, gpu_uuids: Sequence[str], *, _nvml_module=None):
        self.gpu_uuids = _uuid_list(gpu_uuids)
        if any(not uuid.startswith("GPU-") for uuid in self.gpu_uuids):
            raise TelemetryError("select full GPU- UUIDs; MIG/ordinal selection is unsupported")
        self._nvml = _nvml_module or importlib.import_module("pynvml")
        self._closed = True
        self._handles = []
        self.metadata = {"gpu_uuids": self.gpu_uuids[:], "boards": [], "power_warning": POWER_WARNING}
        self._nvml.nvmlInit()
        self._closed = False
        try:
            self.metadata["driver_version"] = self._text(self._nvml.nvmlSystemGetDriverVersion())
            for requested in self.gpu_uuids:
                handle = self._nvml.nvmlDeviceGetHandleByUUID(requested)
                actual = self._text(self._nvml.nvmlDeviceGetUUID(handle))
                if actual != requested:
                    raise TelemetryError(f"requested {requested}, NVML resolved {actual}")
                self._handles.append((requested, handle))
                limits = self._optional(lambda: self._nvml.nvmlDeviceGetPowerManagementLimitConstraints(handle))
                board = {
                    "gpu_uuid": actual,
                    "name": self._text(self._nvml.nvmlDeviceGetName(handle)),
                    "memory_total_bytes": int(self._nvml.nvmlDeviceGetMemoryInfo(handle).total),
                    "power_limit_w": self._scaled_optional(lambda: self._nvml.nvmlDeviceGetPowerManagementLimit(handle)),
                    "default_power_limit_w": self._scaled_optional(lambda: self._nvml.nvmlDeviceGetPowerManagementDefaultLimit(handle)),
                    "power_limit_constraints_w": None if limits is None else [v / 1000.0 for v in limits],
                }
                self.metadata["boards"].append(board)
        except BaseException:
            self.close()
            raise

    @staticmethod
    def _text(value):
        return value.decode("utf-8") if isinstance(value, bytes) else str(value)

    def _optional(self, function):
        try:
            return function()
        except self._nvml.NVMLError_NotSupported:
            return None

    def _scaled_optional(self, function):
        value = self._optional(function)
        return None if value is None else value / 1000.0

    def _compute_processes(self, handle):
        """Snapshot resident compute contexts, not proof of model/endpoint identity."""
        result = {"compute_process_ids": None, "compute_process_status": "unsupported",
                  "compute_process_error": None}
        query = getattr(self._nvml, "nvmlDeviceGetComputeRunningProcesses", None)
        if not callable(query):
            result["compute_process_error"] = "NVML compute-process query API is unavailable"
            return result
        unsupported_types = tuple(
            error_type for name in ("NVMLError_NotSupported", "NVMLError_FunctionNotFound")
            if isinstance(error_type := getattr(self._nvml, name, None), type)
        )
        try:
            processes = query(handle)
            if processes is None:
                raise ValueError("NVML returned no process collection")
            pids = [process.pid for process in processes]
            if any(isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0 for pid in pids):
                raise ValueError("NVML returned an invalid compute-process PID")
            result["compute_process_ids"] = sorted(set(pids))
            result["compute_process_status"] = "ok"
        except unsupported_types as exc:
            result["compute_process_error"] = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            result["compute_process_status"] = "error"
            result["compute_process_error"] = f"{type(exc).__name__}: {exc}"
        return result

    def read(self):
        if self._closed:
            raise RuntimeError("NVML backend is closed")
        readings = []
        for uuid, handle in self._handles:
            row = {"gpu_uuid": uuid, "power_w": None, "cumulative_energy_j": None,
                   "energy_counter_status": "not_read", "status": "ok", "error": None}
            try:
                row["power_w"] = self._nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                energy = self._optional(lambda: self._nvml.nvmlDeviceGetTotalEnergyConsumption(handle))
                row["cumulative_energy_j"] = None if energy is None else energy / 1000.0
                row["energy_counter_status"] = "unsupported" if energy is None else "ok"
            except Exception as exc:
                row["status"] = "error"
                row["error"] = f"{type(exc).__name__}: {exc}"
            # Process capture has a separate status: a failed PID query must not
            # discard valid energy data or masquerade as an empty device.
            row.update(self._compute_processes(handle))
            readings.append(row)
        return readings

    def close(self):
        if not self._closed:
            self._closed = True
            self._nvml.nvmlShutdown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


class SamplingThread:
    """Background sampler with explicit read-time uncertainty and a final drain.

    start() returns immediately. wait_for_first_sample() lets callers establish a
    pre-workload bracket. stop() finishes an in-flight read, takes one final drain
    sample, joins, then returns retained records. The bound backend's close method
    is called in the worker's finally block unless an explicit close_callable is
    supplied. No catch-up samples: each next read waits an interval AFTER the last
    read ends, so slow reads cannot cause a burst/busy loop.
    """

    def __init__(self, read_callable: Callable[[], list[dict]], interval_seconds: float = 0.1,
                 close_callable=None):
        _number(interval_seconds, "sampling interval", positive=True)
        self.read_callable = read_callable
        self.interval_seconds = float(interval_seconds)
        owner = getattr(read_callable, "__self__", None)
        self.close_callable = close_callable if close_callable is not None else getattr(owner, "close", None)
        self._stop_event = threading.Event()
        self._first_sample = threading.Event()
        self._lock = threading.Lock()
        self._records = []
        self._thread = None
        self.shutdown_error = None

    @property
    def records(self):
        with self._lock:
            return copy.deepcopy(self._records)

    def _read_once(self, phase):
        start = time.monotonic()
        readings = []
        error = None
        status = "ok"
        try:
            raw = self.read_callable()
            if not isinstance(raw, list):
                raise TypeError("read_callable must return a list of GPU dictionaries")
            readings = copy.deepcopy(raw)
            if any(not isinstance(row, dict) for row in readings):
                raise TypeError("each GPU reading must be a dictionary")
            if any(row.get("status", "ok") != "ok" for row in readings):
                status = "error"
                error = "one or more GPU readings failed"
        except Exception as exc:
            status = "error"
            error = f"{type(exc).__name__}: {exc}"
        end = time.monotonic()
        with self._lock:
            self._records.append({"sequence": len(self._records), "phase": phase,
                                  "read_start_monotonic": start, "read_end_monotonic": end,
                                  "sample_monotonic": (start + end) / 2.0,
                                  "status": status, "readings": readings, "error": error})
        self._first_sample.set()

    def _run(self):
        try:
            self._read_once("regular")
            while not self._stop_event.wait(self.interval_seconds):
                self._read_once("regular")
            self._read_once("drain")
        finally:
            if self.close_callable is not None:
                try:
                    self.close_callable()
                except Exception as exc:
                    self.shutdown_error = f"{type(exc).__name__}: {exc}"

    def start(self):
        if self._thread is not None:
            raise RuntimeError("sampler cannot be started more than once")
        self._thread = threading.Thread(target=self._run, name="gpu-telemetry", daemon=True)
        self._thread.start()
        return self

    def wait_for_first_sample(self, timeout=5.0):
        return self._first_sample.wait(timeout)

    def stop(self, timeout=None):
        if self._thread is None:
            raise RuntimeError("sampler has not been started")
        self._stop_event.set()
        self._thread.join(timeout)
        if self._thread.is_alive():
            raise TimeoutError("telemetry read did not drain; backend remains owned by worker")
        if self.shutdown_error is not None:
            raise TelemetryError(f"NVML shutdown failed: {self.shutdown_error}")
        return self.records


def _interpolate(times, values, when):
    index = bisect.bisect_left(times, when)
    if index < len(times) and times[index] == when:
        return values[index]
    if index == 0 or index == len(times):
        raise TelemetryError("integration boundary is not bracketed")
    fraction = (when - times[index - 1]) / (times[index] - times[index - 1])
    return values[index - 1] + fraction * (values[index] - values[index - 1])


def integrate_energy(records, start, end, expected_gpu_uuids, *, max_gap_seconds=0.5,
                     max_read_seconds=0.05):
    """Strict complete-board energy over a bracketed monotonic-time interval.

    Sample times are read-window midpoints, not synchronized GPU sensor times.
    Trapezoids interpolate power only within brackets. Counter differences are
    preferred when every selected sample has a finite monotonic counter; an all-
    None counter falls back to power. Partial counter loss or a reset is an error.
    Any missing/failed selected board or sample invalidates the entire aggregate.
    """
    start = _number(start, "interval start")
    end = _number(end, "interval end")
    if end <= start:
        raise TelemetryError("integration interval must have positive length")
    gap = _number(max_gap_seconds, "max gap", positive=True)
    read_bound = _number(max_read_seconds, "max read time", nonnegative=True)
    expected = _uuid_list(expected_gpu_uuids)
    if len(records) < 2:
        raise TelemetryError("at least two samples are required")
    if any(not isinstance(row, dict) for row in records):
        raise TelemetryError("every sample must be a dictionary")
    times = [_number(row.get("sample_monotonic"), "sample time") for row in records]
    if any(a >= b for a, b in zip(times, times[1:])):
        raise TelemetryError("sample times must be strictly increasing in recorded order")
    left = bisect.bisect_right(times, start) - 1
    right = bisect.bisect_left(times, end)
    if left < 0 or right >= len(times):
        raise TelemetryError("both integration boundaries must be bracketed")
    selected = records[left:right + 1]
    selected_times = times[left:right + 1]
    if any(b - a > gap for a, b in zip(selected_times, selected_times[1:])):
        raise TelemetryError("telemetry sampling gap exceeds configured limit")
    powers = {uuid: [] for uuid in expected}
    counters = {uuid: [] for uuid in expected}
    for row, timestamp in zip(selected, selected_times):
        read_start = _number(row.get("read_start_monotonic"), "read start")
        read_end = _number(row.get("read_end_monotonic"), "read end")
        if read_end < read_start or read_end - read_start > read_bound:
            raise TelemetryError("sample read latency exceeds configured bound or is negative")
        if not read_start <= timestamp <= read_end:
            raise TelemetryError("sample timestamp lies outside its read window")
        if row.get("status") != "ok":
            raise TelemetryError(f"failed telemetry sample: {row.get('error')}")
        readings = row.get("readings")
        if not isinstance(readings, list) or any(not isinstance(r, dict) for r in readings):
            raise TelemetryError("missing GPU readings")
        uuids = [r.get("gpu_uuid") for r in readings]
        if (any(not isinstance(uuid, str) for uuid in uuids)
                or len(uuids) != len(set(uuids)) or set(uuids) != set(expected)):
            raise TelemetryError("GPU readings do not exactly match the fixed board set")
        for reading in readings:
            if reading.get("status", "ok") != "ok":
                raise TelemetryError(f"failed GPU reading: {reading.get('error')}")
            uuid = reading["gpu_uuid"]
            powers[uuid].append(_number(reading.get("power_w"), "GPU power", nonnegative=True))
            value = reading.get("cumulative_energy_j")
            counters[uuid].append(None if value is None else _number(value, "GPU cumulative energy", nonnegative=True))
    knots = [start] + [t for t in selected_times if start < t < end] + [end]
    by_gpu = {}
    for uuid in expected:
        values = [_interpolate(selected_times, powers[uuid], t) for t in knots]
        power_energy = sum((b - a) * (pa + pb) / 2.0
                           for a, b, pa, pb in zip(knots, knots[1:], values, values[1:]))
        available = [value is not None for value in counters[uuid]]
        counter_energy = None
        if any(available):
            if not all(available):
                raise TelemetryError(f"partial cumulative-energy counter loss on {uuid}")
            if any(b < a for a, b in zip(counters[uuid], counters[uuid][1:])):
                raise TelemetryError(f"cumulative-energy counter reset/decrease on {uuid}")
            counter_energy = (_interpolate(selected_times, counters[uuid], end)
                              - _interpolate(selected_times, counters[uuid], start))
        _number(power_energy, "integrated GPU power", nonnegative=True)
        if counter_energy is not None:
            _number(counter_energy, "integrated GPU counter", nonnegative=True)
        by_gpu[uuid] = {"energy_j": counter_energy if counter_energy is not None else power_energy,
                       "method": "interpolated_cumulative_counter" if counter_energy is not None else "trapezoidal_power",
                       "counter_energy_j": counter_energy, "power_integral_j": power_energy,
                       "counter_minus_power_j": None if counter_energy is None else counter_energy - power_energy}
    return {"start_monotonic": start, "end_monotonic": end, "duration_seconds": end - start,
            "gpu_uuids": expected, "per_gpu": by_gpu,
            "aggregate_board_energy_j": sum(v["energy_j"] for v in by_gpu.values()),
            "aggregate_power_integral_j": sum(v["power_integral_j"] for v in by_gpu.values()),
            "selected_sample_count": len(selected), "power_warning": POWER_WARNING,
            "boundary_method": "linear interpolation within observed midpoint brackets",
            "scope": "selected GPU boards only; no per-request attribution"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpu-uuid", action="append", required=True)
    parser.add_argument("--seconds", type=float, default=10.0)
    parser.add_argument("--interval", type=float, default=0.1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _number(args.seconds, "capture duration", positive=True)
    _number(args.interval, "sampling interval", positive=True)
    backend = NVMLBackend(args.gpu_uuid)
    sampler = SamplingThread(backend.read, args.interval)
    try:
        sampler.start()
        if not sampler.wait_for_first_sample():
            raise TimeoutError("first NVML sample did not arrive")
        time.sleep(args.seconds)
    finally:
        try:
            if sampler._thread is not None:
                sampler.stop()
            else:
                backend.close()
        finally:
            args.output.write_text(json.dumps({"metadata": backend.metadata,
                                              "samples": sampler.records,
                                              "shutdown_error": sampler.shutdown_error}, indent=2) + "\n")


if __name__ == "__main__":
    main()
