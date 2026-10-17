"""Small independent edge cases; no downloads or production-data writes."""
import importlib.util
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import duckdb

SCRIPT = Path(__file__).with_name("reproduce_m100_gate.py")
SPEC = importlib.util.spec_from_file_location("m100_offline", SCRIPT)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class ReplayTests(unittest.TestCase):
    def test_exact_runs(self):
        self.assertEqual(M.times_summary([])["count"], 0)
        row = M.times_summary([0, 20_000_000_000, 40_000_000_000,
                               60_000_000_001, 80_000_000_001])
        self.assertEqual(row["longest_postselected_exact20s_run"]["cells"], 3)
        self.assertEqual(row["longest_postselected_exact20s_run"]["elapsed_seconds"], 40)
        with self.assertRaises(ValueError):
            M.times_summary([1, 1])

    def test_hash_gate_and_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            (directory/next(iter(M.INPUTS.values()))[0]).write_bytes(b"not the data")
            with self.assertRaisesRegex(ValueError, "Pinned input mismatch"):
                M.validate_inputs(directory)
            output = directory/"protected.json"
            output.write_text("untouched")
            result = subprocess.run([sys.executable,"-I",str(SCRIPT),
                "--raw-dir",str(directory),"--output",str(output)],
                capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(output.read_text(),"untouched")

    def test_dedup_conflicts_nulls_and_exact_time_join(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            connection = duckdb.connect()
            connection.execute("SET TimeZone='UTC'")
            rows = {
                "ps0_input_power": [
                    ("0",0,10),("0",0,10),("0",20_000_000,20),
                    ("1",0,None),("1",0,30),
                    ("1",20_000_000,40),("1",20_000_000,41),
                    ("2",0,-1),(None,0,5),("0",None,5),("3",0,None),
                    ("4",1,5)],
                "ps1_input_power": [
                    ("0",0,7),("0",20_000_000,8),("1",0,9),("4",2,4)],
                "total_power": [
                    ("0",0,18),("0",20_000_000,30),("1",0,41),("4",1,11)],
            }
            paths = {}
            for index,(metric,values) in enumerate(rows.items()):
                table = "fixture"+str(index)
                connection.execute(f"CREATE TABLE {table}(node VARCHAR,timestamp TIMESTAMPTZ,value INTEGER)")
                for node,microseconds,value in values:
                    connection.execute(f"INSERT INTO {table} VALUES (?,"
                        "TIMESTAMPTZ '1970-01-01 00:00:00+00' + ? * INTERVAL '1 microsecond',?)",
                        [node,microseconds,value])
                path = directory/(metric+".parquet")
                connection.execute(f"COPY {table} TO '{str(path)}' (FORMAT PARQUET)")
                paths[metric] = path
            report = M.analyze(connection,paths)
            stats = {x["metric"]:x for x in report["raw_by_metric"]}
            keys = {x["metric"]:x for x in report["keys_by_metric"]}
            self.assertEqual(stats["ps0_input_power"]["rows"],12)
            self.assertEqual(stats["ps0_input_power"]["null_node"],1)
            self.assertEqual(stats["ps0_input_power"]["null_time"],1)
            self.assertEqual(stats["ps0_input_power"]["null_value"],2)
            self.assertEqual(stats["ps0_input_power"]["negative_value"],1)
            self.assertEqual(stats["ps0_input_power"]["submillisecond_rows"],1)
            self.assertEqual(keys["ps0_input_power"]["duplicated_keys"],3)
            self.assertEqual(keys["ps0_input_power"]["conflicting_keys"],1)
            self.assertEqual(keys["ps0_input_power"]["null_mixed_keys"],1)
            self.assertEqual(keys["ps0_input_power"]["all_null_keys"],1)
            # Node4 has timestamps1us and2us: truncation to milliseconds would
            # wrongly create a fourth PSU pair. Exact timestamp matching must not.
            self.assertEqual(report["psu_pairs"]["n"],3)
            self.assertEqual(report["triples"]["n"],3)
            self.assertEqual(report["triples"]["min_delta_w"],1)
            self.assertEqual(report["triples"]["max_delta_w"],2)
            self.assertTrue(math.isclose(report["triples"]["mean_delta_w"],5/3))
            self.assertEqual(report["simultaneity"]["psu_sum"]["all980"]["count"],0)
            connection.close()


if __name__ == "__main__":
    unittest.main()
