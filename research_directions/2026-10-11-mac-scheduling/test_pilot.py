"""Safety/provenance checks; no hardware or serving processes are started."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pilot

class PilotTests(unittest.TestCase):
    def test_runtime_parallel_evidence_includes_contradictions(self):
        self.assertEqual(pilot.actual_parallel('load request={Parallel:2} n_seq_max = 2'), [2])
        self.assertEqual(pilot.actual_parallel('desired OLLAMA_NUM_PARALLEL:2'), [])
        self.assertEqual(pilot.actual_parallel('n_seq_max = 1 --parallel 2'), [1,2])

    def test_active_original_server_aborts_without_launch_and_retains_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(pilot,'original_idle',return_value=False), patch.object(pilot,'state',return_value={}), patch.object(pilot.subprocess,'Popen') as launch:
                with self.assertRaisesRegex(RuntimeError,'idle original'):
                    pilot.window(1,1,[],Path(tmp))
                launch.assert_not_called()
            saved=json.loads((Path(tmp)/'window-01-p1'/'RUN.json').read_text())
            self.assertEqual(saved['status'],'aborted')
            self.assertIn('idle original',saved['error'])

if __name__=='__main__':unittest.main()
