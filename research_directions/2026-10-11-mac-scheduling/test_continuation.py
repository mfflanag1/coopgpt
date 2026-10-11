"""Regression checks for the archived setup repair; never launch Ollama."""
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
import continue_pilot as continuation

class ContinuationTests(unittest.TestCase):
    def test_reuse_probe_still_rejects_a_live_listener(self):
        with socket.socket() as listener, tempfile.TemporaryDirectory() as tmp:
            listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            listener.bind(('127.0.0.1',0));listener.listen(1)
            with patch.object(continuation,'PORT',listener.getsockname()[1]), patch.object(continuation,'state',return_value={}), patch.object(continuation,'original_idle',return_value=True), patch.object(continuation.subprocess,'Popen') as launch:
                with self.assertRaises(OSError):continuation.window(2,2,[],Path(tmp))
                launch.assert_not_called()
            saved=json.loads((Path(tmp)/'window-02-p2/RUN.json').read_text())
            self.assertEqual(saved['status'],'aborted')

    def test_continuation_cannot_replace_an_attempt_with_warmups(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);first={'status':'completed'}
            (out/'window-01-p1').mkdir();(out/'window-02-p2').mkdir()
            (out/'window-01-p1/RUN.json').write_text(json.dumps(first))
            (out/'CAMPAIGN.json').write_text(json.dumps({'status':'aborted','windows':[first]}))
            (out/'window-02-p2/WARMUP.json').write_text('{}')
            with patch.object(continuation,'check_lock'):
                with self.assertRaisesRegex(ValueError,'already has offers'):continuation.main(out)
            self.assertTrue((out/'window-02-p2/WARMUP.json').exists())
            self.assertFalse((out/'preflight_abort').exists())

if __name__=='__main__':unittest.main()
