"""Owned, single-slot Ollama lifecycle for offline-scored calibration runs.

Constructing this class performs no I/O. Entering it checks local locks and host
state, then starts a fresh process group. No power authentication is requested.
Call verify_loaded() after loading/generation. stop_owned() is for a watchdog;
it deliberately does not claim that a forced stop cleanly unloaded the model.
"""
from datetime import datetime, timezone
import hashlib
import http.client
import json
import math
import os
from pathlib import Path
import plistlib
import re
import signal
import socket
import subprocess
import threading
import time

MODEL = 'qwen3:32b'
DIGEST = '030ee887880fc378860c2dd35101da424377520441ae4bfe7be6deff8ade7840'
VERSION, PORT, ORIGINAL_PORT = '0.20.0', 11562, 11434
COMMON = dict(OLLAMA_CONTEXT_LENGTH='4096', OLLAMA_DEBUG='1', OLLAMA_FLASH_ATTENTION='0',
              OLLAMA_HOST='http://127.0.0.1:11562', OLLAMA_KEEP_ALIVE='120s',
              OLLAMA_KV_CACHE_TYPE='f16', OLLAMA_MAX_LOADED_MODELS='1', OLLAMA_MAX_QUEUE='256',
              OLLAMA_MULTIUSER_CACHE='0', OLLAMA_NOHISTORY='1', OLLAMA_NOPRUNE='1', OLLAMA_NO_CLOUD='1')


class ServerControlError(RuntimeError):
    pass


def utc():
    return datetime.now(timezone.utc).isoformat()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def thermal_ok(value):
    cleaned = re.sub(r'(?im)^\s*(?:Note:\s*)?No (?:thermal warning level|performance warning level|CPU power status) has been recorded\s*$', '', value)
    return ('No thermal warning level has been recorded' in value
            and 'No performance warning level has been recorded' in value
            and not re.search(r'(?i)warning|thermal|CPU_Speed_Limit|Scheduler_Limit', cleaned))


def power_values(text):
    sources = re.findall(r"(?m)^Now drawing from '(AC Power|Battery Power)'$", text)
    percentages = re.findall(r'(?m)^\s*-InternalBattery-\d+\b[^\n]*?[ \t](\d{1,3})%;', text)
    return (sources[0] if len(sources) == 1 else None,
            int(percentages[0]) if len(percentages) == 1 else None)


class OwnedServer:
    def __init__(self, output_dir, config):
        self.output_dir, self.config = Path(output_dir), dict(config)
        self.metadata = dict(status='not_started', model=MODEL, context=4096, parallel=1, errors=[])
        self._proc = self._pgid = self._log = None
        self._stopped = self._entered = self._finished = False
        self._lock = threading.RLock()

    def _error(self, stage, error):
        item = dict(stage=stage, type=type(error).__name__, message=str(error).replace(str(Path.home()), 'USER_HOME'))
        self.metadata['errors'].append(item)
        return item

    def _save(self):
        path = self.output_dir/'SERVER_CONTROL.json'
        temporary = path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(self.metadata, sort_keys=True, allow_nan=False)+'\n')
        temporary.replace(path)

    def _request(self, port, path, body=None, timeout=5):
        if not isinstance(path, str) or not path.startswith('/api/') or '\r' in path or '\n' in path:
            raise ValueError('only literal /api/ paths are allowed')
        connection = http.client.HTTPConnection('127.0.0.1', port, timeout=timeout)
        try:
            payload = None if body is None else json.dumps(body, allow_nan=False).encode()
            connection.request('GET' if body is None else 'POST', path, body=payload,
                               headers={'Content-Type': 'application/json'})
            response = connection.getresponse()
            raw = response.read()
            if response.status != 200:
                raise ServerControlError(f'HTTP {response.status} from port {port} {path}')
            value = json.loads(raw)
            if not isinstance(value, dict) or 'error' in value:
                raise ServerControlError(f'invalid/error API object from port {port} {path}')
            return value
        finally:
            connection.close()

    def api(self, path, body=None, timeout=5):
        if self._proc is None or self._stopped or self._proc.poll() is not None:
            raise ServerControlError('owned server is not running')
        return self._request(PORT, path, body, timeout)

    def _original_idle(self):
        value = self._request(ORIGINAL_PORT, '/api/ps')
        return type(value.get('models')) is list and value['models'] == []

    def snapshot(self):
        def command(args):
            result = subprocess.run(args, capture_output=True, timeout=10, check=True)
            return result.stdout
        power = command(['/usr/bin/pmset', '-g', 'batt']).decode().strip()
        thermal = command(['/usr/bin/pmset', '-g', 'therm']).decode().strip()
        battery = plistlib.loads(command(['/usr/sbin/ioreg', '-r', '-c', 'AppleSmartBattery', '-a']))
        connected = None
        if (isinstance(battery, list) and len(battery) == 1 and isinstance(battery[0], dict)
                and type(battery[0].get('ExternalConnected')) is bool):
            connected = battery[0]['ExternalConnected']
        source, percent = power_values(power)
        return dict(utc=utc(), power=re.sub(r'\(id=\d+\)', '(id=REDACTED)', power),
                    external_power_connected=connected, power_source=source, battery_percent=percent, thermal=thermal,
                    load_average=list(os.getloadavg()))

    def _host_state(self, phase):
        state = dict(self.snapshot())
        source, percent = power_values(state['power'])
        state.update(power_source=source, battery_percent=percent)
        self.metadata[phase] = state
        idle = self._original_idle()
        self.metadata['original_endpoint_idle_'+phase] = idle
        if idle is not True:
            raise ServerControlError('original endpoint is not verified idle: '+phase)
        allowed = self.config.get('allow_battery_quality', False)
        if type(allowed) is not bool:
            raise ServerControlError('allow_battery_quality must be bool')
        ac = source == 'AC Power' and state.get('external_power_connected') is True
        battery = (allowed and source == 'Battery Power' and state.get('external_power_connected') is False
                   and type(percent) is int and 60 <= percent <= 100)
        if not ac and not battery:
            raise ServerControlError('AC power or explicitly permitted battery quality state is not verified: '+phase)
        if not thermal_ok(state['thermal']):
            raise ServerControlError('thermal state is not verified nominal: '+phase)

    def check_host(self, phase):
        """Persist a per-job gate; failures remain recorded even if a caller catches them."""
        if (not isinstance(phase, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,100}', phase)
                or phase in {'before', 'after', 'errors', 'status', 'host_checks', 'server_settings', 'options', 'lock_verification'}):
            raise ServerControlError('invalid host-check phase')
        if not self._entered or self._finished:
            raise ServerControlError('host checks require an active OwnedServer context')
        if phase in self.metadata and not (isinstance(self.metadata[phase], dict) and 'power' in self.metadata[phase]):
            raise ServerControlError('host-check phase would overwrite controller metadata')
        with self._lock:
            try:
                self._host_state(phase)
            except BaseException as error:
                self._error('host_check:'+phase, error)
                self.metadata.setdefault('host_checks', []).append(dict(phase=phase, passed=False, state=self.metadata.get(phase),
                                                                        original_endpoint_idle=self.metadata.get('original_endpoint_idle_'+phase)))
                try:
                    self._save()
                except BaseException as save_error:
                    self._error('save_host_check', save_error)
                    if hasattr(error, 'add_note'):
                        error.add_note('Host-check metadata save also failed: '+str(save_error))
                raise
            state = self.metadata[phase]
            self.metadata.setdefault('host_checks', []).append(dict(phase=phase, passed=True, state=dict(state), original_endpoint_idle=True))
            self._save()
            return state

    def _check_lock(self):
        allowed = self.config.get('allow_battery_quality', False)
        if type(allowed) is not bool:
            raise ServerControlError('allow_battery_quality must be bool')
        self.metadata['allow_battery_quality'] = allowed
        for key, wanted in (('model', MODEL), ('digest', DIGEST), ('context', 4096), ('version', VERSION), ('port', PORT), ('parallel', 1)):
            if self.config.get(key, wanted) != wanted or isinstance(self.config.get(key), bool):
                raise ServerControlError('unsupported configuration: '+key)
        common = self.config.get('server_settings_common', COMMON)
        if common != COMMON:
            raise ServerControlError('common server settings differ from fixed calibration settings')
        options = self.config.get('options', {})
        for key, wanted in (('num_ctx', 4096), ('temperature', 0), ('seed', 0)):
            if options.get(key, wanted) != wanted:
                raise ServerControlError('unsupported request option: '+key)
        if 'lock' in self.config and 'lock_path' in self.config:
            raise ServerControlError('provide exactly one lock or lock_path')
        lock = self.config.get('lock', self.config.get('lock_path'))
        if isinstance(lock, (str, Path)):
            lock = json.loads(Path(lock).read_text())
        if not isinstance(lock, dict):
            raise ServerControlError('explicit MODEL_LOCK dictionary/path is required')
        self.binary = Path(self.config.get('binary_path', '/opt/homebrew/bin/ollama')).resolve(strict=True)
        manifest = Path(self.config.get('manifest_path', Path.home()/'.ollama/models/manifests/registry.ollama.ai/library/qwen3/32b'))
        got = dict(binary_sha256=file_sha(self.binary), manifest_sha256=file_sha(manifest))
        self.metadata['lock_verification'] = got
        if any(got[key] != lock.get(key) for key in got) or got['manifest_sha256'] != DIGEST:
            raise ServerControlError('binary/model manifest lock mismatch')
        self.metadata['server_settings'] = dict(COMMON, OLLAMA_NUM_PARALLEL='1')
        self.metadata['options'] = options

    def verify_loaded(self):
        value = self.api('/api/ps')
        self.metadata['loaded_checks'] = self.metadata.get('loaded_checks', []) + [dict(utc=utc(), response=value)]
        models = value.get('models')
        ok = isinstance(models, list) and len(models) == 1
        if ok:
            model = models[0]
            if not isinstance(model, dict):
                model = {}
            vram = model.get('size_vram')
            ok = (model.get('name') == MODEL and model.get('digest') == DIGEST
                  and type(model.get('context_length')) is int and model['context_length'] == 4096
                  and type(vram) in (int, float) and math.isfinite(vram) and vram > 0)
        log = (self.output_dir/'SERVER.log').read_text(errors='replace')
        parallel = sorted({int(x) for pattern in (r'n_seq_max\s*=\s*(\d+)', r'\bParallel[=:]\s*(\d+)', r'--parallel\s+(\d+)') for x in re.findall(pattern, log)})
        self.metadata['runtime_parallel_values'] = parallel
        if not ok or parallel != [1] or re.search(r'(?i)truncat(?:ing|ed).*prompt|prompt.*truncat', log):
            error = ServerControlError('loaded model, context, GPU, runtime parallelism or prompt integrity mismatch')
            self._error('verify_loaded', error)
            self._save()
            raise error
        self._save()
        return value

    def __enter__(self):
        if self._entered:
            raise ServerControlError('OwnedServer instances cannot be reused')
        self._entered = True
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if any((self.output_dir/name).exists() for name in ('SERVER.log', 'SERVER_CONTROL.json', 'SERVER_CONTROL.json.tmp')):
            raise ServerControlError('refusing to overwrite a previous server capture')
        self.metadata.update(status='starting', started_utc=utc())
        try:
            self._check_lock()
            self._host_state('before')
            with socket.socket() as probe:
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                probe.bind(('127.0.0.1', PORT))
            self._log = (self.output_dir/'SERVER.log').open('w')
            env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL')}
            env.update(self.metadata['server_settings'])
            self._proc = subprocess.Popen([str(self.binary), 'serve'], env=env, stdout=self._log,
                                          stderr=subprocess.STDOUT, start_new_session=True)
            self.metadata['dedicated_server_pid'] = self._proc.pid
            if os.getpgid(self._proc.pid) != self._proc.pid or self._proc.pid == os.getpgrp():
                raise ServerControlError('new-session process group ownership unverified')
            self._pgid = self._proc.pid
            self.metadata['dedicated_process_group'] = self._pgid
            deadline = time.monotonic()+30
            while True:
                if self._proc.poll() is not None:
                    raise ServerControlError('server exited before readiness')
                try:
                    self.metadata['version'] = self.api('/api/version', timeout=1)
                    break
                except (OSError, http.client.HTTPException):
                    if time.monotonic() >= deadline:
                        raise ServerControlError('server readiness timeout')
                    time.sleep(.1)
            if self.metadata['version'].get('version') != VERSION:
                raise ServerControlError('server version mismatch')
            tags = self.api('/api/tags').get('models')
            matches = [m for m in tags if isinstance(m, dict) and m.get('name') == MODEL] if isinstance(tags, list) else []
            if len(matches) != 1 or matches[0].get('digest') != DIGEST:
                raise ServerControlError('model tag/digest mismatch')
            self.metadata['model_tag'] = matches[0]
            self.metadata['status'] = 'running'
            self._save()
            return self
        except BaseException as error:
            self._finish(error)
            raise

    def _group_alive(self):
        if self._pgid is None:
            return False
        try:
            os.killpg(self._pgid, 0)
            return True
        except ProcessLookupError:
            return False

    def _terminate_owned(self):
        if self._proc is None or self._stopped:
            return
        if self._pgid is None:
            # The child is ours, but an unverified group must never be signaled.
            if self._proc.poll() is None:
                self._proc.terminate()
        else:
            try:
                os.killpg(self._pgid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        try:
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if self._pgid is None:
                self._proc.kill()
            else:
                try:
                    os.killpg(self._pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            self._proc.wait(timeout=3)
        if self._pgid is not None:
            deadline = time.monotonic()+2
            while self._group_alive() and time.monotonic() < deadline:
                time.sleep(.05)
            if self._group_alive():
                try:
                    os.killpg(self._pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                deadline = time.monotonic()+2
                while self._group_alive() and time.monotonic() < deadline:
                    time.sleep(.05)
                if self._group_alive():
                    raise ServerControlError('owned process group survived bounded termination')
        self._stopped = True
        self.metadata['dedicated_server_returncode'] = self._proc.returncode

    def stop_owned(self):
        """Idempotent watchdog stop; only the captured owned group is signaled."""
        with self._lock:
            if self._proc is None or self._stopped:
                return
            self.metadata.update(forced_stop=True, clean_unload_verified=False)
            try:
                self._terminate_owned()
            except BaseException as error:
                self._error('stop_owned', error)
                raise
            finally:
                self._save()

    def _finish(self, original=None):
        with self._lock:
            if self._finished:
                return []
            self._finished = True
            cleanup = []
            if original is not None:
                self._error('body_or_enter', original)
            if self._proc is not None:
                if not self.metadata.get('forced_stop') and self._proc.poll() is None:
                    try:
                        loaded = self.api('/api/ps')
                        if not isinstance(loaded.get('models'), list):
                            raise ServerControlError('malformed loaded-model response before cleanup')
                        if loaded['models']:
                            self.verify_loaded()
                    except BaseException as error:
                        cleanup.append(self._error('model_before_cleanup', error))
                try:
                    if self.metadata.get('forced_stop') or self._proc.poll() is not None:
                        raise ServerControlError('server stopped without verified clean unload')
                    self.api('/api/generate', dict(model=MODEL, keep_alive=0, stream=False), timeout=10)
                    deadline = time.monotonic()+10
                    while True:
                        value = self.api('/api/ps', timeout=2)
                        self.metadata['loaded_after_unload'] = value
                        if type(value.get('models')) is list and value['models'] == []:
                            self.metadata['clean_unload_verified'] = True
                            break
                        if time.monotonic() >= deadline:
                            raise ServerControlError('model unload timeout')
                        time.sleep(.1)
                except BaseException as error:
                    cleanup.append(self._error('unload', error))
                try:
                    self._terminate_owned()
                except BaseException as error:
                    cleanup.append(self._error('terminate', error))
            try:
                self._host_state('after')
            except BaseException as error:
                cleanup.append(self._error('postflight', error))
            try:
                if self._log is not None:
                    self._log.close()
                logfile = self.output_dir/'SERVER.log'
                if logfile.exists():
                    logfile.write_text(logfile.read_text(errors='replace').replace(str(Path.home()), 'USER_HOME'))
            except BaseException as error:
                cleanup.append(self._error('sanitize_log', error))
            self.metadata.update(status='aborted' if self.metadata['errors'] else 'completed', finished_utc=utc())
            try:
                self._save()
            except BaseException as error:
                cleanup.append(self._error('save_metadata', error))
            if original is not None and cleanup and hasattr(original, 'add_note'):
                original.add_note('Server cleanup errors retained in metadata: '+json.dumps(cleanup))
            return cleanup

    def __exit__(self, kind, error, traceback):
        cleanup = self._finish(error)
        if error is None and self.metadata['errors']:
            raise ServerControlError('server cleanup/postflight/validation failed: '+json.dumps(self.metadata['errors']))
        return False
