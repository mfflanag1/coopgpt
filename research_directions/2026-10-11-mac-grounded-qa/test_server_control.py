"""Lifecycle tests mock all child, host and HTTP calls; no hardware is queried."""
import hashlib
import json
from pathlib import Path
import plistlib
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import server_control as sc

THERMAL = 'Note: No thermal warning level has been recorded\nNote: No performance warning level has been recorded\nNote: No CPU power status has been recorded'


class FixedQwenPin(unittest.TestCase):
    def test_only_qwen32_pin_and_existing_runtime_settings(self):
        self.assertEqual(sc.MODEL, 'qwen3:32b')
        self.assertEqual(sc.DIGEST, '030ee887880fc378860c2dd35101da424377520441ae4bfe7be6deff8ade7840')
        self.assertEqual(sc.VERSION, '0.20.0')
        self.assertEqual((sc.PORT, sc.ORIGINAL_PORT), (11562, 11434))
        self.assertEqual(sc.COMMON['OLLAMA_CONTEXT_LENGTH'], '4096')


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        binary, manifest = root/'ollama', root/'manifest'
        binary.write_bytes(b'locked binary')
        manifest.write_bytes(b'locked manifest')
        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
        self.patchers = [patch.object(sc, 'DIGEST', digest), patch.object(sc.os, 'getpgid', return_value=12345),
                         patch.object(sc.os, 'getpgrp', return_value=54321), patch.object(sc.socket, 'socket')]
        for p in self.patchers:
            p.start(); self.addCleanup(p.stop)
        self.config = dict(lock=dict(binary_sha256=sc.file_sha(binary), manifest_sha256=digest),
                           binary_path=str(binary), manifest_path=str(manifest))
        self.server = sc.OwnedServer(root/'out', self.config)
        self.proc = Mock(pid=12345, returncode=None)
        self.proc.poll.side_effect = lambda: self.proc.returncode
        self.proc.wait.side_effect = lambda timeout: self.proc.returncode
        self.group_alive = False
        self.force_timeout = False
        self.signals = []
        def killpg(pgid, sig):
            self.signals.append((pgid, sig))
            if sig == 0:
                if not self.group_alive:
                    raise ProcessLookupError()
            elif sig == signal.SIGTERM and not self.force_timeout or sig == signal.SIGKILL:
                self.proc.returncode = -sig
                self.group_alive = False
        self.popen = patch.object(sc.subprocess, 'Popen', return_value=self.proc)
        self.popen_mock = self.popen.start(); self.addCleanup(self.popen.stop)
        self.kill = patch.object(sc.os, 'killpg', side_effect=killpg)
        self.kill.start(); self.addCleanup(self.kill.stop)
        self.snapshot_patch = patch.object(self.server, 'snapshot', return_value=dict(utc=sc.utc(), power="Now drawing from 'AC Power'", external_power_connected=True, thermal=THERMAL, load_average=[1, 2, 3]))
        self.snapshot = self.snapshot_patch.start(); self.addCleanup(self.snapshot_patch.stop)
        self.loaded = False
        self.unload_fail = False
        self.version = sc.VERSION
        self.tag_digest = digest
        self.original_busy = False
        self.ps_override = None
        def request(port, path, body=None, timeout=5):
            if port == sc.ORIGINAL_PORT:
                return {'models': [{}] if self.original_busy else []}
            if path == '/api/version':return {'version': self.version}
            if path == '/api/tags':return {'models': [dict(name=sc.MODEL, digest=self.tag_digest)]}
            if path == '/api/generate':
                if self.unload_fail:raise TimeoutError('unload failed')
                self.loaded = False
                self.ps_override = None
                return {'done': True}
            if path == '/api/ps':
                if self.ps_override is not None:return self.ps_override
                return {'models': [dict(name=sc.MODEL, digest=sc.DIGEST, context_length=4096, size_vram=3_000_000_000)] if self.loaded else []}
            raise AssertionError(path)
        self.request_patch = patch.object(self.server, '_request', side_effect=request)
        self.request = self.request_patch.start(); self.addCleanup(self.request_patch.stop)

    def mark_loaded(self):
        self.loaded = True
        (self.server.output_dir/'SERVER.log').write_text('n_seq_max = 1\n'+str(Path.home())+'\n')

    def test_normal_verified_model_and_clean_owned_group(self):
        with self.server as owned:
            self.mark_loaded()
            value = owned.verify_loaded()
            self.assertEqual(value['models'][0]['context_length'], 4096)
        self.assertEqual(self.server.metadata['status'], 'completed')
        self.assertTrue(self.server.metadata['clean_unload_verified'])
        self.assertEqual(self.server.metadata['loaded_after_unload'], {'models': []})
        self.assertEqual(self.popen_mock.call_args.kwargs['env']['OLLAMA_NUM_PARALLEL'], '1')
        self.assertTrue(self.popen_mock.call_args.kwargs['start_new_session'])
        self.assertTrue(all(pid == 12345 for pid, _ in self.signals))
        self.assertNotIn(str(Path.home()), (self.server.output_dir/'SERVER.log').read_text())
        self.assertIn('USER_HOME', (self.server.output_dir/'SERVER.log').read_text())
        self.assertEqual(json.loads((self.server.output_dir/'SERVER_CONTROL.json').read_text())['status'], 'completed')

    def test_lock_failure_launches_nothing_and_persists(self):
        self.server.config['lock']['binary_sha256'] = 'bad'
        with self.assertRaisesRegex(sc.ServerControlError, 'lock mismatch'):
            with self.server:pass
        self.popen_mock.assert_not_called()
        self.assertEqual(self.server.metadata['status'], 'aborted')
        self.assertTrue((self.server.output_dir/'SERVER_CONTROL.json').exists())

    def test_lock_path_supported(self):
        path = Path(self.temp.name)/'LOCK.json';path.write_text(json.dumps(self.config['lock']))
        self.server.config.pop('lock');self.server.config['lock_path'] = str(path)
        with self.server:pass

    def test_default_manifest_path_is_cached_qwen32(self):
        root = Path(self.temp.name)
        manifest = root/'.ollama/models/manifests/registry.ollama.ai/library/qwen3/32b'
        manifest.parent.mkdir(parents=True)
        manifest.write_bytes((root/'manifest').read_bytes())
        self.server.config.pop('manifest_path')
        with patch.object(sc.Path, 'home', return_value=root):
            self.server._check_lock()
        self.assertEqual(self.server.metadata['lock_verification']['manifest_sha256'], sc.DIGEST)
        self.popen_mock.assert_not_called()

    def test_old_model_configuration_is_rejected_before_launch(self):
        self.server.config['model'] = 'llama3.2:3b'
        with self.assertRaisesRegex(sc.ServerControlError, 'unsupported configuration: model'):
            with self.server:pass
        self.popen_mock.assert_not_called()

    def test_old_digest_configuration_is_rejected_before_launch(self):
        self.server.config['digest'] = 'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
        with self.assertRaisesRegex(sc.ServerControlError, 'unsupported configuration: digest'):
            with self.server:pass
        self.popen_mock.assert_not_called()

    def test_existing_stage_directory_is_accepted_without_overwrite(self):
        self.server.output_dir.mkdir()
        stage = self.server.output_dir/'STAGE.json'
        stage.write_text('{"status":"starting"}')
        with self.server:pass
        self.assertEqual(stage.read_text(), '{"status":"starting"}')

    def test_previous_server_log_is_never_overwritten(self):
        self.server.output_dir.mkdir()
        log = self.server.output_dir/'SERVER.log'
        log.write_text('prior capture')
        with self.assertRaisesRegex(sc.ServerControlError, 'overwrite'):
            with self.server:pass
        self.assertEqual(log.read_text(), 'prior capture')
        self.popen_mock.assert_not_called()

    def test_dead_owned_leader_cannot_claim_clean_unload(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'cleanup'):
            with self.server:self.proc.returncode = 1
        self.assertNotIn('clean_unload_verified', self.server.metadata)
        self.assertEqual(self.server.metadata['status'], 'aborted')

    def test_original_busy_and_false_ac_cannot_launch(self):
        self.original_busy = True
        with self.assertRaisesRegex(sc.ServerControlError, 'original endpoint'):
            with self.server:pass
        self.popen_mock.assert_not_called()

    def test_pmset_alone_is_insufficient_ac_evidence(self):
        self.snapshot.return_value['external_power_connected'] = False
        with self.assertRaisesRegex(sc.ServerControlError, 'AC power'):
            with self.server:pass
        self.popen_mock.assert_not_called()

    def battery(self, percent=89, connected=False):
        self.snapshot.return_value.update(power=f"Now drawing from 'Battery Power'\n -InternalBattery-0 (id=REDACTED)\t{percent}%; discharging; present: true",
                                          external_power_connected=connected)

    def test_explicit_battery_quality_89_is_allowed(self):
        self.server.config['allow_battery_quality'] = True
        self.battery()
        with self.server:pass
        self.assertEqual(self.server.metadata['before']['battery_percent'], 89)
        self.assertEqual(self.server.metadata['after']['power_source'], 'Battery Power')
        self.assertTrue(self.server.metadata['allow_battery_quality'])

    def test_battery_59_is_blocked(self):
        self.server.config['allow_battery_quality'] = True
        self.battery(59)
        with self.assertRaisesRegex(sc.ServerControlError, 'battery quality'):
            with self.server:pass
        self.popen_mock.assert_not_called()

    def test_default_remains_strict_ac_on_high_battery(self):
        self.battery(99)
        with self.assertRaisesRegex(sc.ServerControlError, 'AC power'):
            with self.server:pass
        self.popen_mock.assert_not_called()

    def test_battery_state_must_consistently_report_disconnected(self):
        self.server.config['allow_battery_quality'] = True
        self.battery(89, connected=True)
        with self.assertRaisesRegex(sc.ServerControlError, 'battery quality'):
            with self.server:pass
        self.popen_mock.assert_not_called()

    def test_battery_percent_required_and_bounded(self):
        self.server.config['allow_battery_quality'] = True
        for percent in ('unknown', 101, -1, -89, '0.89'):
            self.battery(percent)
            with self.subTest(percent=percent), self.assertRaisesRegex(sc.ServerControlError, 'battery quality'):
                self.server._host_state('check')
        for percent in (60, 100):
            self.battery(percent)
            self.server._host_state('check')

    def test_ac_disconnected_does_not_fall_back_to_battery_permission(self):
        self.server.config['allow_battery_quality'] = True
        self.snapshot.return_value['external_power_connected'] = False
        with self.assertRaisesRegex(sc.ServerControlError, 'battery quality'):
            self.server._host_state('check')

    def test_battery_flag_must_be_boolean(self):
        for flag in (0, 1, None, 'true', []):
            self.server.config['allow_battery_quality'] = flag
            with self.subTest(flag=flag), self.assertRaisesRegex(sc.ServerControlError, 'must be bool'):
                self.server._check_lock()
        self.popen_mock.assert_not_called()

    def test_per_job_check_written_and_failure_retained(self):
        self.server.config['allow_battery_quality'] = True
        self.battery(89)
        with self.assertRaisesRegex(sc.ServerControlError, 'battery quality'):
            with self.server:
                self.server.check_host('job_1_before')
                saved = json.loads((self.server.output_dir/'SERVER_CONTROL.json').read_text())
                self.assertTrue(saved['host_checks'][0]['passed'])
                self.assertEqual(saved['host_checks'][0]['state']['battery_percent'], 89)
                self.battery(59)
                self.server.check_host('job_1_after')
        saved = json.loads((self.server.output_dir/'SERVER_CONTROL.json').read_text())
        self.assertEqual([check['passed'] for check in saved['host_checks']], [True, False])
        self.assertEqual(saved['before']['battery_percent'], 89)
        self.assertTrue(any(item['stage'] == 'host_check:job_1_after' for item in saved['errors']))

    def test_per_job_check_still_blocks_thermal_and_original_activity(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'thermal'):
            with self.server:
                self.snapshot.return_value['thermal'] += '\nCPU_Speed_Limit=75'
                self.server.check_host('job_1_before')

    def test_per_job_check_still_blocks_original_activity(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'original endpoint'):
            with self.server:
                self.original_busy = True
                self.server.check_host('job_1_after')

    def test_thermal_warning_cannot_launch(self):
        self.snapshot.return_value['thermal'] += '\nCPU_Speed_Limit=75'
        with self.assertRaisesRegex(sc.ServerControlError, 'thermal state'):
            with self.server:pass
        self.popen_mock.assert_not_called()

    def test_wrong_version_still_stops_owned_process(self):
        self.version = 'different'
        with self.assertRaisesRegex(sc.ServerControlError, 'version mismatch'):
            with self.server:pass
        self.assertIn((12345, signal.SIGTERM), self.signals)

    def test_wrong_tag_still_stops_owned_process(self):
        self.tag_digest = 'wrong'
        with self.assertRaisesRegex(sc.ServerControlError, 'tag/digest'):
            with self.server:pass
        self.assertIn((12345, signal.SIGTERM), self.signals)

    def test_loaded_context_and_parallel_mismatches_fail(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'loaded model'):
            with self.server:
                self.mark_loaded()
                self.ps_override = {'models': [dict(name=sc.MODEL, digest=sc.DIGEST, context_length=8192, size_vram=1)]}
                self.server.verify_loaded()
        self.assertEqual(self.server.metadata['status'], 'aborted')

    def test_loaded_old_model_name_is_rejected(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'loaded model'):
            with self.server:
                self.mark_loaded()
                self.ps_override = {'models': [dict(name='llama3.2:3b', digest=sc.DIGEST, context_length=4096, size_vram=1)]}
                self.server.verify_loaded()
        self.assertEqual(self.server.metadata['status'], 'aborted')

    def test_wrong_runtime_parallelism_fails(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'runtime parallelism'):
            with self.server:
                self.mark_loaded()
                (self.server.output_dir/'SERVER.log').write_text('n_seq_max = 4\n')
                self.server.verify_loaded()

    def test_caught_validation_failure_cannot_become_completed(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'validation'):
            with self.server:
                self.mark_loaded()
                (self.server.output_dir/'SERVER.log').write_text('n_seq_max = 4\n')
                try:self.server.verify_loaded()
                except sc.ServerControlError:pass
                (self.server.output_dir/'SERVER.log').write_text('n_seq_max = 1\n')
        self.assertEqual(self.server.metadata['status'], 'aborted')

    def test_watchdog_stop_idempotent_and_not_clean_unload(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'cleanup'):
            with self.server:
                self.server.stop_owned()
                before = list(self.signals)
                self.server.stop_owned()
                self.assertEqual(self.signals, before)
        self.assertTrue(self.server.metadata['forced_stop'])
        self.assertFalse(self.server.metadata['clean_unload_verified'])
        self.assertEqual(self.server.metadata['status'], 'aborted')

    def test_unload_failure_surfaces_after_owned_termination(self):
        self.unload_fail = True
        with self.assertRaisesRegex(sc.ServerControlError, 'cleanup'):
            with self.server:pass
        self.assertIn((12345, signal.SIGTERM), self.signals)
        self.assertTrue(any(x['stage'] == 'unload' for x in self.server.metadata['errors']))

    def test_cleanup_does_not_mask_body_exception(self):
        self.unload_fail = True
        problem = ValueError('original body error')
        with self.assertRaises(ValueError) as caught:
            with self.server:raise problem
        self.assertIs(caught.exception, problem)
        self.assertTrue(any(x['stage'] == 'unload' for x in self.server.metadata['errors']))

    def test_unverified_group_never_signaled(self):
        with patch.object(sc.os, 'getpgid', return_value=77777):
            with self.assertRaisesRegex(sc.ServerControlError, 'ownership'):
                with self.server:pass
        self.assertEqual(self.signals, [])
        self.proc.terminate.assert_called_once()

    def test_escalation_is_only_for_owned_group(self):
        self.force_timeout = True
        waits = [subprocess.TimeoutExpired('owned', 5), -signal.SIGKILL]
        def wait(timeout):
            value = waits.pop(0)
            if isinstance(value, BaseException):raise value
            self.proc.returncode = value;return value
        self.proc.wait.side_effect = wait
        with self.server:pass
        self.assertIn((12345, signal.SIGKILL), self.signals)
        self.assertTrue(all(pid == 12345 for pid, _ in self.signals))

    def test_postflight_change_fails_without_masking_cleanup(self):
        with self.assertRaisesRegex(sc.ServerControlError, 'postflight'):
            with self.server:self.original_busy = True
        self.assertTrue(self.server.metadata['clean_unload_verified'])
        self.assertFalse(self.server.metadata['original_endpoint_idle_after'])

    def test_snapshot_uses_explicit_battery_ac_and_redacts_id(self):
        outputs = [b"Now drawing from 'AC Power'\n -InternalBattery-0 (id=12345)\t89%; charging; present: true", THERMAL.encode(), plistlib.dumps([{'ExternalConnected': True}])]
        with patch.object(sc.subprocess, 'run', side_effect=[Mock(stdout=x) for x in outputs]), patch.object(sc.os, 'getloadavg', return_value=(1,2,3)):
            value = sc.OwnedServer.snapshot(self.server)
        self.assertTrue(value['external_power_connected'])
        self.assertIn('id=REDACTED', value['power'])
        self.assertNotIn('12345', value['power'])
        self.assertEqual(value['battery_percent'], 89)

    def test_missing_ioreg_evidence_is_unknown_not_disconnected(self):
        outputs = [b"Now drawing from 'Battery Power'\n -InternalBattery-0 (id=12345)\t89%; discharging; present: true", THERMAL.encode(), plistlib.dumps([{}])]
        with patch.object(sc.subprocess, 'run', side_effect=[Mock(stdout=x) for x in outputs]), patch.object(sc.os, 'getloadavg', return_value=(1,2,3)):
            value = sc.OwnedServer.snapshot(self.server)
        self.assertIsNone(value['external_power_connected'])
        self.server.config['allow_battery_quality'] = True
        self.snapshot.return_value = value
        with self.assertRaisesRegex(sc.ServerControlError, 'battery quality'):
            self.server._host_state('check')


class LiteralHTTP(unittest.TestCase):
    def test_literal_loopback_connection_and_error_rejection(self):
        connection = Mock()
        response = connection.getresponse.return_value
        response.status = 200
        response.read.return_value = b'{"models":[]}'
        owned = sc.OwnedServer('/unused', {})
        with patch.object(sc.http.client, 'HTTPConnection', return_value=connection) as constructor, patch.dict(sc.os.environ, {'HTTP_PROXY': 'http://invalid:1', 'ALL_PROXY': 'http://invalid:1'}):
            self.assertEqual(owned._request(sc.PORT, '/api/ps'), {'models': []})
            constructor.assert_called_with('127.0.0.1', sc.PORT, timeout=5)
            connection.close.assert_called_once()
            response.read.return_value = b'{"error":""}'
            with self.assertRaises(sc.ServerControlError):owned._request(sc.PORT, '/api/bad')
            response.status = 503
            with self.assertRaises(sc.ServerControlError):owned._request(sc.PORT, '/api/ps')


if __name__ == '__main__':
    unittest.main()
