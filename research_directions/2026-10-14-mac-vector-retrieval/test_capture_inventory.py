"""Fixture tests; these never invoke hardware commands or claim a benchmark."""
import contextlib
from datetime import datetime
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import capture_inventory as inventory


PROFILE = json.dumps({"SPDisplaysDataType": [{
    "spdisplays_chipset-model": "Apple M3 Max", "sppci_cores": "40",
    "spdisplays_metalfamily": "spdisplays_metal3",
    "serial_number": "secret_serial", "_name": "ignored_model",
    "spdisplays_ndrvs": [{"uuid": "secret_uuid", "hostname": "secret_hostname"}],
}]})


class InventoryTests(unittest.TestCase):
    def capture_fixture(self, ram="137438953472\n", profile=PROFILE, statuses=None):
        statuses = statuses or {}
        def run(key):
            return (ram if key == "ram" else profile,
                    {"status": statuses.get(key, "completed")})
        with patch.object(inventory.platform, "system", return_value="Darwin"), \
             patch.object(inventory.platform, "machine", return_value="arm64"), \
             patch.object(inventory.os, "cpu_count", return_value=16), \
             patch.object(inventory, "run_command", side_effect=run):
            return inventory.capture("test-mac")

    def test_command_allowlist_uses_fixed_arguments_no_shell(self):
        expected = {
            "ram": ["/usr/sbin/sysctl", "-n", "hw.memsize"],
            "mac_gpu": ["/usr/sbin/system_profiler", "SPDisplaysDataType", "-json"],
        }
        for key, command in expected.items():
            with self.subTest(key=key), patch.object(inventory.subprocess, "run") as run:
                run.return_value = subprocess.CompletedProcess(command, 0, "selected", "secret")
                raw, metadata = inventory.run_command(key)
                run.assert_called_once_with(command, shell=False, capture_output=True,
                                            text=True, timeout=15, check=False)
                self.assertEqual(raw, "selected")
                self.assertEqual(metadata["command"], command)
                self.assertEqual(metadata["status"], "completed")
                self.assertNotIn("secret", json.dumps(metadata))
                self.assertNotIn("selected", json.dumps(metadata))
        with patch.object(inventory.subprocess, "run") as run:
            with self.assertRaises(KeyError):
                inventory.run_command("power_off")
            run.assert_not_called()

    def test_command_failure_timeout_and_missing_tool_are_explicit(self):
        cases = [
            (FileNotFoundError("secret_path"), "missing_tool"),
            (PermissionError("secret_path"), "failed"),
            (subprocess.TimeoutExpired("private", 15, output=b"secret_serial",
                                       stderr=b"secret_hostname"), "timed_out"),
            (UnicodeError("secret_payload"), "failed"),
        ]
        for error, status in cases:
            with self.subTest(status=status), patch.object(inventory.subprocess, "run", side_effect=error):
                raw, metadata = inventory.run_command("mac_gpu")
                self.assertEqual(raw, "")
                self.assertEqual(metadata["status"], status)
                self.assertNotIn("secret", json.dumps(metadata))

    def test_nonzero_exit_preserves_code_without_profiler_payload(self):
        result = subprocess.CompletedProcess([], 7, PROFILE, "secret_hostname")
        with patch.object(inventory.subprocess, "run", return_value=result):
            _, metadata = inventory.run_command("mac_gpu")
        self.assertEqual(metadata["returncode"], 7)
        self.assertEqual(metadata["status"], "failed")
        self.assertNotIn("secret", json.dumps(metadata))

    def test_only_selected_gpu_facts_survive(self):
        devices = inventory.parse_mac(PROFILE)
        self.assertEqual(devices[0]["model"], "Apple M3 Max")
        self.assertEqual(devices[0]["gpu_core_count"]["value"], 40)
        self.assertEqual(devices[0]["metal_facts"], {"spdisplays_metalfamily": "spdisplays_metal3"})
        self.assertNotIn("secret", json.dumps(devices))
        self.assertNotIn("ignored_model", json.dumps(devices))

    def test_missing_core_and_metal_facts_stay_unknown(self):
        for cores in (None, "N/A", 0, -1, True, "40.5"):
            with self.subTest(cores=cores):
                raw = json.dumps({"SPDisplaysDataType": [{"_name": "GPU", "sppci_cores": cores}]})
                device = inventory.parse_mac(raw)[0]
                self.assertIsNone(device["gpu_core_count"]["value"])
                self.assertEqual(device["gpu_core_count"]["status"], "unknown")
                self.assertEqual(device["metal_status"], "unknown")
                self.assertEqual(device["whole_device_availability"], "unknown")

    def test_bad_or_empty_profiles_are_not_successful_empty_lists(self):
        for raw in ("not json", "[]", "{}", '{"SPDisplaysDataType":[]}',
                    '{"SPDisplaysDataType":[null]}', '{"SPDisplaysDataType":[{}]}',
                    '{"SPDisplaysDataType":[{"_name":""}]}'):
            with self.subTest(raw=raw):
                report = self.capture_fixture(profile=raw)
                gpu = report["hardware"]["gpu_inventory"]
                self.assertEqual(gpu["status"], "parse_error")
                self.assertIsNone(gpu["devices"])

    def test_failed_queries_never_parse_even_plausible_payloads(self):
        for status in ("failed", "timed_out", "missing_tool"):
            with self.subTest(status=status):
                report = self.capture_fixture(statuses={"ram": status, "mac_gpu": status})
                gpu = report["hardware"]["gpu_inventory"]
                self.assertEqual(gpu["status"], status)
                self.assertIsNone(gpu["devices"])
                self.assertIsNone(report["hardware"]["physical_ram_bytes"]["value"])

    def test_hardware_totals_do_not_become_available_resources(self):
        report = self.capture_fixture()
        self.assertEqual(report["hardware"]["physical_ram_bytes"]["value"], 137438953472)
        self.assertEqual(report["hardware"]["logical_cpu_count"]["value"], 16)
        self.assertEqual(report["status"], "hardware_inventory_only")
        self.assertIs(report["placement_ready"], False)
        self.assertEqual(report["capacity_kind"], "hardware_totals")
        self.assertEqual(report["availability"]["allocatable_capacity"], "unknown")
        self.assertEqual(report["availability"]["reservations"], "unknown")
        self.assertIn("unified memory", report["memory_semantics"])
        self.assertNotIn("memory_total_mib", json.dumps(report))
        self.assertNotIn("secret", json.dumps(report))

    def test_invalid_ram_and_cpu_are_not_zero_capacity(self):
        for raw in ("N/A", "", "0", "-1", "123.5", "123 bytes"):
            with self.subTest(raw=raw):
                memory = self.capture_fixture(ram=raw)["hardware"]["physical_ram_bytes"]
                self.assertIsNone(memory["value"])
                self.assertEqual(memory["status"], "unknown")
        self.assertEqual(inventory.fact(None, "cpu"), {"value": None, "status": "unknown", "source": "cpu"})

    def test_capture_has_utc_interval_and_monotonic_elapsed_time(self):
        with patch.object(inventory.time, "monotonic", side_effect=[10.0, 10.25]):
            timing = self.capture_fixture()["capture"]
        self.assertEqual(timing["monotonic_duration_seconds"], 0.25)
        for key in ("started_at_utc", "finished_at_utc"):
            self.assertEqual(datetime.fromisoformat(timing[key]).utcoffset().total_seconds(), 0)

    def test_non_mac_does_not_run_hardware_commands(self):
        with patch.object(inventory.platform, "system", return_value="Linux"), \
             patch.object(inventory, "run_command") as run:
            report = inventory.capture("unsupported-host")
        run.assert_not_called()
        self.assertEqual(report["hardware"]["gpu_inventory"]["status"], "unsupported_platform")
        self.assertFalse(report["placement_ready"])

    def test_existing_file_and_symlink_are_preserved_without_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "inventory.json"
            target.write_text("preserve this")
            link = Path(directory) / "alias.json"
            link.symlink_to(target)
            for output in (target, link):
                with self.subTest(output=output.name), patch.object(inventory, "capture") as capture, \
                     contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    inventory.main(["--node-id", "my-mac", "--output", str(output)])
                capture.assert_not_called()
                self.assertEqual(target.read_text(), "preserve this")

    def test_successful_cli_writes_only_json_with_no_stdout(self):
        report = self.capture_fixture()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new.json"
            stdout = io.StringIO()
            with patch.object(inventory, "capture", return_value=report), contextlib.redirect_stdout(stdout):
                inventory.main(["--node-id", "my-mac", "--output", str(output)])
            self.assertEqual(json.loads(output.read_text()), report)
            self.assertEqual(stdout.getvalue(), "")

    def test_alias_validation_precedes_file_creation_and_commands(self):
        for alias in ("", "host name", "$(hostname)", "../mac", "mác", "x" * 65):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "new.json"
                with patch.object(inventory, "capture") as capture, \
                     contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    inventory.main(["--node-id", alias, "--output", str(output)])
                self.assertFalse(output.exists())
                capture.assert_not_called()


if __name__ == "__main__":
    unittest.main()
