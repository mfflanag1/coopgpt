"""Event-driven two-owner replay using predicted service and energy at dispatch.

This is a serial-replica model. Per-request measurements or predictions are supplied
by the caller; the engine makes no assumptions about GPU type or serving workload.
"""
from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Service:
    """One request on one server; energy is joules, service includes any cooldown."""

    service_seconds: float
    energy_j: float


@dataclass(frozen=True)
class Job:
    """Absolute arrival/deadline and separate forecast/realized server profiles."""

    id: str
    arrival: float
    deadline: float
    predictions: Mapping[int, Service]
    realized: Mapping[int, Service]
    response_tail_seconds: float = 0.0


def _finite(value: float, name: str, *, positive: bool = False) -> None:
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0 or (positive and value <= 0):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")


def _validate(jobs: Sequence[Job], budgets: Sequence[float], mode: str) -> None:
    if mode not in ("autarky", "pool"):
        raise ValueError("mode must be autarky or pool")
    if len(budgets) != 2:
        raise ValueError("exactly two owner budgets are required")
    for budget in budgets:
        _finite(budget, "budget")
    ids = set()
    for job in jobs:
        if not isinstance(job.id, str) or not job.id or job.id in ids:
            raise ValueError("job IDs must be unique nonempty strings")
        ids.add(job.id)
        _finite(job.arrival, "arrival")
        _finite(job.deadline, "deadline")
        if job.deadline < job.arrival:
            raise ValueError("deadline cannot precede arrival")
        _finite(job.response_tail_seconds, "response tail")
        for name, profiles in (("predictions", job.predictions), ("realized", job.realized)):
            if set(profiles) != {0, 1}:
                raise ValueError(f"{name} must supply exactly server keys 0 and 1")
            for profile in profiles.values():
                _finite(profile.service_seconds, f"{name} service", positive=True)
                _finite(profile.energy_j, f"{name} energy")
                if job.response_tail_seconds >= profile.service_seconds:
                    raise ValueError("response tail must be smaller than every service duration")


def _choose_dispatch(
    now: float,
    waiting: Sequence[Job],
    idle_servers: Sequence[int],
    available: Sequence[float],
    mode: str,
) -> tuple[Job, int] | None:
    """Controller: read predictions only; never inspect realized outcomes.

    Oldest feasible waiting request wins (arrival, then lexicographic ID). For that
    request choose the eligible idle server with least forecast energy, then index.
    An infeasible old request may wait while a later feasible one starts.
    A supplied response tail consumes the physical slot but not response latency.
    """
    for job in sorted(waiting, key=lambda j: (j.arrival, j.id)):
        choices = []
        for server in idle_servers:
            forecast = job.predictions[server]
            account = 0 if mode == "pool" else server
            if (now + forecast.service_seconds - job.response_tail_seconds <= job.deadline
                    and forecast.energy_j <= available[account]):
                choices.append((forecast.energy_j, server))
        if choices:
            return job, min(choices)[1]
    return None


def replay(jobs: Sequence[Job], initial_budgets: Sequence[float], mode: str) -> dict:
    """Replay fixed owners' serial replicas with predicted reservations.

    Autarky has one energy account per owner. Pool has their combined account.
    Both use the same central queue and dispatch logic. Completing a request
    refunds its prediction and charges actual energy; debt is allowed and reported.
    No completed request is removed or retrospectively rejected. Realized profiles
    are consulted only by the physical event layer, not the controller.

    At equal timestamps, all completions settle before arrivals, then waiting
    expirations are processed before dispatch. A running request can finish late.
    """
    jobs = list(jobs)
    initial_budgets = [float(v) for v in initial_budgets]
    _validate(jobs, initial_budgets, mode)
    by_id = {job.id: job for job in jobs}
    account_budgets = ([sum(initial_budgets)] if mode == "pool" else initial_budgets[:])
    available = account_budgets[:]
    minimum_available = available[:]
    spent = [0.0, 0.0]
    account_spent = [0.0] * len(available)
    max_actual_overrun = [0.0] * len(available)
    status = {job.id: "unarrived" for job in jobs}
    waiting: dict[str, Job] = {}
    running: dict[int, dict] = {}
    records = []
    rejected = []
    events: list[tuple[float, int, str, int]] = []
    for job in jobs:
        heapq.heappush(events, (job.arrival, 1, job.id, -1))
        heapq.heappush(events, (job.deadline, 2, job.id, -1))
    peak_busy = 0

    while events:
        now = events[0][0]
        same_time = []
        while events and events[0][0] == now:
            same_time.append(heapq.heappop(events))
        # Tuple ordering enforces completions, arrivals, then expirations.
        for _, event_type, job_id, server in sorted(same_time):
            job = by_id[job_id]
            if event_type == 0:
                record = running.pop(server)
                if record["id"] != job_id or status[job_id] != "running":
                    raise RuntimeError("completion event does not match running job")
                account = 0 if mode == "pool" else server
                actual_energy = job.realized[server].energy_j
                available[account] += record["predicted_energy_j"] - actual_energy
                minimum_available[account] = min(minimum_available[account], available[account])
                account_spent[account] += actual_energy
                spent[server] += actual_energy
                max_actual_overrun[account] = max(
                    max_actual_overrun[account], account_spent[account] - account_budgets[account]
                )
                record["end"] = now  # Backward-compatible alias for slot_end.
                record["slot_end"] = now
                record["response_end"] = now - job.response_tail_seconds
                record["actual_service_seconds"] = now - record["start"]
                record["actual_energy_j"] = actual_energy
                record["outcome"] = "ontime" if record["response_end"] <= job.deadline else "late"
                status[job_id] = record["outcome"]
                records.append(record)
            elif event_type == 1:
                if status[job_id] != "unarrived":
                    raise RuntimeError("duplicate arrival")
                status[job_id] = "waiting"
                waiting[job_id] = job
            elif status[job_id] == "waiting":
                status[job_id] = "rejected"
                waiting.pop(job_id)
                rejected.append({"id": job_id, "time": now, "reason": "expired_without_start"})

        # The controller sees only now, waiting predictions, idle servers/accounts.
        while len(running) < 2:
            choice = _choose_dispatch(
                now, list(waiting.values()), [s for s in (0, 1) if s not in running],
                available, mode,
            )
            if choice is None:
                break
            job, server = choice
            forecast = job.predictions[server]
            account = 0 if mode == "pool" else server
            available[account] -= forecast.energy_j
            minimum_available[account] = min(minimum_available[account], available[account])
            record = {
                "id": job.id, "server": server, "arrival": job.arrival,
                "deadline": job.deadline, "start": now,
                "predicted_service_seconds": forecast.service_seconds,
                "predicted_energy_j": forecast.energy_j,
                "predicted_response_end": now + forecast.service_seconds - job.response_tail_seconds,
                "response_tail_seconds": job.response_tail_seconds,
            }
            running[server] = record
            status[job.id] = "running"
            waiting.pop(job.id)
            # Physical execution schedules a hidden completion; dispatch does not
            # inspect this event time or actual energy when selecting other jobs.
            completion = now + job.realized[server].service_seconds
            if not math.isfinite(completion) or completion <= now:
                raise ValueError("realized completion must be finite and advance time")
            heapq.heappush(events, (completion, 0, job.id, server))
            peak_busy = max(peak_busy, len(running))

    if running or waiting or any(s not in {"ontime", "late", "rejected"} for s in status.values()):
        raise RuntimeError("every offered job must reach a terminal outcome")
    records.sort(key=lambda r: (r["start"], r["id"]))
    rejected.sort(key=lambda r: (r["time"], r["id"]))
    unique = len({r["id"] for r in records}) == len(records)
    no_overlap = True
    for server in (0, 1):
        server_records = sorted((r for r in records if r["server"] == server), key=lambda r: r["start"])
        no_overlap = no_overlap and all(a["end"] <= b["start"] for a, b in zip(server_records, server_records[1:]))
    if not unique or not no_overlap:
        raise RuntimeError("physical schedule integrity failure")
    return {
        "mode": mode,
        "offered": len(jobs),
        "started": len(records),
        "ontime": sum(s == "ontime" for s in status.values()),
        "late": sum(s == "late" for s in status.values()),
        "rejected": len(rejected),
        "records": records,
        "rejections": rejected,
        "total_energy_j": sum(spent),
        "per_owner_energy_j": spent,
        "initial_budgets_j": initial_budgets,
        "remaining_accounts_j": available,
        "minimum_available_accounts_j": minimum_available,
        "max_reservation_and_spend_overrun_j": max([0.0] + [-v for v in minimum_available]),
        "max_actual_budget_overrun_j": max([0.0] + max_actual_overrun),
        "per_account_actual_budget_overrun_j": max_actual_overrun,
        "per_owner_nominal_overrun_j": [max(0.0, spent[s] - initial_budgets[s]) for s in (0, 1)],
        "peak_busy": peak_busy,
        "unique_started_ids": unique,
        "no_server_overlap": no_overlap,
        "terminal_accounting_ok": len(records) + len(rejected) == len(jobs),
    }
