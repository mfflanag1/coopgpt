"""Mocked lifecycle regressions; no sockets, processes, models, or meters run."""
import copy
import errno
import json
from pathlib import Path
import signal
import tempfile
import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

import runstudy


class Clock:
    def __init__(self):
        self.value = 0.0

    def monotonic(self):
        self.value += 0.01
        return self.value

    def sleep(self, duration):
        self.value += duration


class Timer:
    def __init__(self, seconds, callback):
        self.seconds = seconds
        self.callback = callback
        self.daemon = False
        self.cancelled = False
        self.started = False

    def start(self):
        self.started = True

    def cancel(self):
        self.cancelled = True

    def join(self, *args, **kwargs):
        pass


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='coop-runtime-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.out = self.root / 'capture'
        self.out.mkdir()
        self.config = json.loads((Path(runstudy.__file__).parent / 'CONFIG.json').read_text())
        self.config['pre_idle_s'] = 0
        self.config['post_idle_s'] = 0
        self.config['offered_seconds'] = 0
        self.item = dict(index=1, parallel=4, rate=0.3, rep=1, trace_file='TRACE.json')
        self.trace = [dict(request_id='offered-one', arrival_offset_s=0, prompt='fixture', max_output_tokens=64)]
        (self.root / 'TRACE.json').write_text(json.dumps(self.trace))
        self.clock = Clock()
        self.proc = Mock()
        self.proc.pid = 432101
        self.proc.returncode = None
        self.proc.poll.side_effect = lambda: self.proc.returncode
        self.proc.wait.side_effect = self.wait_process
        self.group_alive = True
        self.ignore_term = False
        self.unloaded = False
        self.timers = []
        self.mode = 'normal'
        self.runtime_parallel = 4
        self.popen = Mock(side_effect=self.start_process)
        self.killpg = Mock(side_effect=self.signal_group)
        self.collect = Mock(side_effect=self.collect_trace)
        self.socket = Mock()
        self.socket.__enter__ = Mock(return_value=self.socket)
        self.socket.__exit__ = Mock(return_value=False)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.original = self.stack.enter_context(patch.object(runstudy, 'original_idle', return_value=True))
        self.stack.enter_context(patch.object(runstudy, 'state', return_value={
            'utc': '2026-10-11T20:00:00+00:00', 'power': "Now drawing from 'AC Power'",
            'thermal': 'No thermal warning', 'load_average': [0, 0, 0]}))
        self.stack.enter_context(patch.object(runstudy, 'BASE', self.root))
        self.stack.enter_context(patch.object(runstudy.socket, 'socket', return_value=self.socket))
        self.stack.enter_context(patch.object(runstudy.subprocess, 'Popen', self.popen))
        self.stack.enter_context(patch.object(runstudy.os, 'killpg', self.killpg))
        self.stack.enter_context(patch.object(runstudy, 'api', side_effect=self.api))
        self.stack.enter_context(patch.object(runstudy, 'run_trace', self.collect))
        self.stack.enter_context(patch.object(runstudy.threading, 'Timer', side_effect=self.make_timer))
        self.stack.enter_context(patch.object(runstudy.time, 'monotonic', side_effect=self.clock.monotonic))
        self.stack.enter_context(patch.object(runstudy.time, 'sleep', side_effect=self.clock.sleep))

    def wait_process(self, timeout=None):
        if self.proc.returncode is None:
            self.proc.returncode = 0
        return self.proc.returncode

    def start_process(self, command, **kwargs):
        kwargs['stdout'].write('llama_context: n_seq_max = %d\n' % self.runtime_parallel)
        kwargs['stdout'].flush()
        return self.proc

    def signal_group(self, pid, sig):
        if pid != self.proc.pid:
            raise AssertionError('attempted to signal an unowned group')
        if not self.group_alive:
            raise ProcessLookupError()
        if sig == 0:
            return
        if sig == signal.SIGTERM and self.ignore_term:
            return
        self.group_alive = False
        if self.proc.returncode is None:
            self.proc.returncode = -sig

    def api(self, endpoint, body=None, **kwargs):
        if endpoint == '/api/version':
            return {'version': '0.20.0'}
        if endpoint == '/api/tags':
            return {'models': [{'name': self.config['model'], 'digest': self.config['digest']}]}
        if endpoint == '/api/generate':
            self.unloaded = True
            return {'done': True}
        if endpoint == '/api/ps':
            return {'models': [] if self.unloaded else [{
                'digest': self.config['digest'], 'context_length': self.config['context'],
                'size_vram': 1234}]}
        raise AssertionError('unexpected mocked API call ' + endpoint)

    def make_timer(self, seconds, callback):
        timer = Timer(seconds, callback)
        self.timers.append(timer)
        return timer

    def collect_trace(self, url, trace, model, options, **kwargs):
        warm = trace is self.config['warmups']
        result = {
            'started_utc': '2026-10-11T20:00:00+00:00', 'elapsed_seconds': 0.5,
            'requests': [dict(request_id=job['request_id'], completed=True,
                              arrival_offset_s=job['arrival_offset_s'], chunks=[])
                         for job in trace]}
        if warm and self.mode == 'bad_warmup':
            result['requests'][0]['completed'] = False
        if not warm and self.mode in ('watchdog_timeout', 'interrupt'):
            result['requests'][0]['completed'] = False
            result['requests'][0]['chunks'] = [dict(offset_s=0.2, data={'response': 'partial'})]
            kwargs['checkpoint'](copy.deepcopy(result))
            if self.mode == 'watchdog_timeout':
                self.timers[0].callback()
                raise TimeoutError('mock collector hard timeout')
            raise KeyboardInterrupt('mock operator cancellation')
        kwargs['checkpoint'](copy.deepcopy(result))
        return result

    def window(self):
        return runstudy.window(self.item, self.config, self.out)

    def saved(self, name='RUN.json'):
        return json.loads((self.out / 'window-01' / name).read_text())

    def test_active_original_endpoint_rejects_before_process_or_port(self):
        self.original.return_value = False
        with self.assertRaisesRegex(RuntimeError, 'Original endpoint'):
            self.window()
        self.popen.assert_not_called()
        self.socket.bind.assert_not_called()
        self.killpg.assert_not_called()
        self.assertEqual(self.saved()['status'], 'aborted')

    def test_unknown_original_endpoint_rejects_before_process(self):
        self.original.return_value = None
        with self.assertRaisesRegex(RuntimeError, 'Original endpoint'):
            self.window()
        self.popen.assert_not_called()
        self.assertEqual(self.saved()['status'], 'aborted')

    def test_live_port_rejects_without_launching_or_signalling(self):
        self.socket.bind.side_effect = OSError(errno.EADDRINUSE, 'address already in use')
        with self.assertRaises(OSError):
            self.window()
        self.popen.assert_not_called()
        self.killpg.assert_not_called()
        self.assertEqual(self.saved()['status'], 'aborted')

    def test_crashed_leader_still_terminates_owned_process_group(self):
        self.proc.returncode = 1
        with self.assertRaisesRegex(RuntimeError, 'Server exited'):
            self.window()
        self.assertIn((self.proc.pid, signal.SIGTERM), [call.args for call in self.killpg.call_args_list])
        self.assertFalse(self.group_alive)
        self.assertEqual(self.saved()['status'], 'aborted')
        self.assertEqual(self.saved()['dedicated_server_returncode'], 1)

    def test_crashed_leader_with_stubborn_child_escalates_to_kill(self):
        self.proc.returncode = 1
        self.ignore_term = True
        with self.assertRaisesRegex(RuntimeError, 'Server exited'):
            self.window()
        signals = [call.args[1] for call in self.killpg.call_args_list]
        self.assertIn(signal.SIGTERM, signals)
        self.assertIn(signal.SIGKILL, signals)
        self.assertFalse(self.group_alive)

    def test_failed_warmup_is_retained_and_no_workload_starts(self):
        self.mode = 'bad_warmup'
        with self.assertRaisesRegex(RuntimeError, 'Warmup failed'):
            self.window()
        self.assertEqual(self.collect.call_count, 1)
        self.assertEqual(len(self.saved('WARMUP.json')['requests']), 4)
        self.assertFalse(self.saved('WARMUP.json')['requests'][0]['completed'])
        self.assertFalse((self.out / 'window-01' / 'REQUESTS.json').exists())
        self.assertFalse(self.group_alive)

    def test_wrong_runtime_parallelism_rejects_before_workload(self):
        self.runtime_parallel = 1
        with self.assertRaisesRegex(ValueError, 'parallelism'):
            self.window()
        self.assertEqual(self.collect.call_count, 1)
        self.assertFalse(self.group_alive)

    def test_watchdog_timeout_preserves_checkpoint_and_escalates(self):
        self.mode = 'watchdog_timeout'
        self.ignore_term = True
        with self.assertRaises(TimeoutError):
            self.window()
        self.assertEqual(self.saved()['status'], 'aborted')
        self.assertTrue(self.saved()['watchdog_fired'])
        rows = self.saved('REQUESTS.json')['requests']
        self.assertEqual([row['request_id'] for row in rows], ['offered-one'])
        self.assertEqual(rows[0]['chunks'][0]['data']['response'], 'partial')
        self.assertIn((self.proc.pid, signal.SIGKILL), [call.args for call in self.killpg.call_args_list])
        self.assertTrue(self.timers[0].cancelled)
        self.assertFalse(self.group_alive)

    def test_operator_interrupt_preserves_partial_rows_and_aborted_status(self):
        self.mode = 'interrupt'
        with self.assertRaises(KeyboardInterrupt):
            self.window()
        self.assertEqual(self.saved()['status'], 'aborted')
        self.assertIn('KeyboardInterrupt', self.saved()['error'])
        self.assertEqual(self.saved('REQUESTS.json')['requests'][0]['chunks'][0]['data']['response'], 'partial')
        self.assertFalse(self.group_alive)

    def test_normal_window_uses_four_warmups_and_distinct_workload(self):
        result = self.window()
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(self.collect.call_count, 2)
        warm_call, workload_call = self.collect.call_args_list
        self.assertEqual(len(warm_call.args[1]), 4)
        self.assertTrue(all(job['arrival_offset_s'] == 0 for job in warm_call.args[1]))
        self.assertEqual(workload_call.args[1], self.trace)
        self.assertIsNotNone(warm_call.kwargs['checkpoint'])
        self.assertIsNotNone(workload_call.kwargs['checkpoint'])
        self.assertTrue(self.popen.call_args.kwargs['start_new_session'])
        self.assertEqual(self.saved('REQUESTS.json')['requests'][0]['request_id'], 'offered-one')
        self.assertFalse(self.group_alive)

    def test_global_budget_stop_keeps_plan_and_does_not_launch_window(self):
        self.config['global_budget_s'] = 10
        (self.root / 'CONFIG.json').write_text(json.dumps(self.config))
        (self.root / 'PLAN.json').write_text(json.dumps([self.item]))
        destination = self.root / 'budget-capture'
        with patch.object(runstudy, 'check_lock'), patch.object(runstudy, 'window') as window, \
             patch.object(runstudy.power_capture, 'launch', return_value={'fixture': True}), \
             patch.object(runstudy.power_capture, 'stop_and_archive', return_value={'stop_confirmed': True}) as stop:
            runstudy.main(destination)
        window.assert_not_called()
        stop.assert_called_once()
        result = json.loads((destination / 'CAMPAIGN.json').read_text())
        self.assertEqual(result['status'], 'budget_stopped')
        self.assertEqual(result['windows'], [])
        self.assertEqual(json.loads((destination / 'PLAN.json').read_text()), [self.item])


if __name__ == '__main__':
    unittest.main()
