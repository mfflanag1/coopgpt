#!/usr/bin/env python3
"""Read-only hardware facts, never an allocatable-resource or placement snapshot."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import time

COMMANDS = {
    "ram": ("/usr/sbin/sysctl", "-n", "hw.memsize"),
    "mac_gpu": ("/usr/sbin/system_profiler", "SPDisplaysDataType", "-json"),
}
NODE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")


def run_command(key):
    """Only these two static read-only commands can be executed; no shell.

    Raw profiler output and stderr are deliberately omitted from the report.
    """
    command = COMMANDS[key]
    metadata = {"command": list(command), "timeout_seconds": 15}
    try:
        result = subprocess.run(list(command), shell=False,
                                capture_output=True, text=True, timeout=15, check=False)
        stdout = result.stdout
        metadata.update(status="completed" if result.returncode == 0 else "failed",
                        returncode=result.returncode)
        return stdout, metadata
    except subprocess.TimeoutExpired as exc:
        metadata.update(status="timed_out", error_type=type(exc).__name__)
    except FileNotFoundError as exc:
        metadata.update(status="missing_tool", error_type=type(exc).__name__)
    except (OSError, UnicodeError) as exc:
        metadata.update(status="failed", error_type=type(exc).__name__)
    return "", metadata


def fact(value, source):
    valid = isinstance(value, int) and not isinstance(value, bool) and value > 0
    return {"value": value if valid else None,
            "status": "observed" if valid else "unknown", "source": source}


def parse_mac(raw):
    records = json.loads(raw).get("SPDisplaysDataType")
    if not isinstance(records, list) or not records:
        raise ValueError("No display-device records; GPU presence is unknown")
    devices = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid display-device record")
        model = record.get("spdisplays_chipset-model", record.get("_name"))
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Missing GPU model")
        cores = record.get("sppci_cores")
        if isinstance(cores, str) and re.fullmatch(r"[0-9]+", cores):
            cores = int(cores)
        metal = {key: record[key] for key in
                 ("spdisplays_metal", "spdisplays_metalfamily", "spdisplays_metal_family")
                 if isinstance(record.get(key), str)}
        devices.append({"model": model,
                        "gpu_core_count": fact(cores, "system_profiler sppci_cores"),
                        "metal_facts": metal, "metal_status": "reported" if metal else "unknown",
                        "whole_device_availability": "unknown"})
    return devices


def capture(node_id):
    if not NODE_ID.fullmatch(node_id):
        raise ValueError("node-id must be a 1–64 character ASCII alias: letters, numbers, _, ., -")
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    system = platform.system()
    commands, memory = {}, fact(None, "unsupported_platform")
    gpu = {"status": "unsupported_platform", "devices": None}
    if system == "Darwin":
        raw, commands["ram"] = run_command("ram")
        if commands["ram"]["status"] == "completed" and re.fullmatch(r"[0-9]+\s*", raw):
            memory = fact(int(raw), "sysctl hw.memsize")
        else:
            memory = fact(None, "sysctl hw.memsize")
            memory["reason"] = "invalid_output" if commands["ram"]["status"] == "completed" else commands["ram"]["status"]
        raw, commands["mac_gpu"] = run_command("mac_gpu")
        gpu["status"] = commands["mac_gpu"]["status"]
        if gpu["status"] == "completed":
            try:
                gpu.update(devices=parse_mac(raw), status="observed")
            except (ValueError, TypeError, AttributeError) as exc:
                gpu.update(status="parse_error", error_type=type(exc).__name__)
    result = {
        "schema_version": 1, "node_id": node_id,
        "status": "hardware_inventory_only", "placement_ready": False,
        "capacity_kind": "hardware_totals",
        "availability": {"reservations": "unknown", "allocatable_capacity": "unknown",
                         "execution_permissions": "unverified", "application_fit": "unverified"},
        "memory_semantics": "Physical system RAM includes Apple silicon unified memory; it is not separate dedicated GPU capacity or currently available memory.",
        "hardware": {"platform": system, "architecture": platform.machine(),
                     "physical_ram_bytes": memory,
                     "logical_cpu_count": fact(os.cpu_count(), "os.cpu_count (hardware, not usable CPUs)"),
                     "gpu_inventory": gpu},
        "commands": commands,
        "capture": {"started_at_utc": started,
                    "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                    "monotonic_duration_seconds": time.monotonic() - tick},
    }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node-id", required=True, help="Human alias, not a hostname")
    parser.add_argument("--output", required=True, type=Path, help="New JSON file; never overwritten")
    args = parser.parse_args(argv)
    if not NODE_ID.fullmatch(args.node_id):
        parser.error("--node-id must match [A-Za-z0-9][A-Za-z0-9_.-]{0,63}")
    try:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(capture(args.node_id), stream, indent=2, allow_nan=False)
            stream.write("\n")
    except OSError as exc:
        parser.error(f"cannot create inventory output: {exc.strerror}")


if __name__ == "__main__":
    main()
