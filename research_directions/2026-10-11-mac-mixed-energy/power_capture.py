"""Bounded macOS-authenticated telemetry; only powermetrics runs as root.

The root-owned temporary capture remains readable. A user-owned stop sentinel can
only stop this supervisor's own child; its contents are never interpreted as code.
"""
from datetime import datetime,timezone
import gzip,json,shlex,subprocess,time
from pathlib import Path

def utc():return datetime.now(timezone.utc).isoformat()

def launch(output_dir):
    output_dir=Path(output_dir).resolve();stop=output_dir/'STOP_POWER'
    if not str(output_dir).isascii():raise ValueError('Power capture path must be ASCII')
    if stop.exists():raise ValueError('Existing stop flag; output directory must be new')
    child=('trap \"\" HUP; umask 022; /usr/bin/powermetrics --samplers cpu_power,gpu_power -i 1000 -n 3000 -o "$1/samples.txt" & '
           'meter=$!; /bin/echo "$meter" > "$1/meter.pid"; ticks=0; '
           'while /bin/kill -0 "$meter" 2>/dev/null; do '
           'if [ -f '+shlex.quote(str(stop))+' ] || [ "$ticks" -ge 3000 ]; then /bin/kill -INT "$meter" 2>/dev/null; break; fi; '
           '/bin/sleep 1; ticks=$((ticks+1)); done; '
           'grace=0; while /bin/kill -0 \"$meter\" 2>/dev/null && [ \"$grace\" -lt 5 ]; do /bin/sleep 1; grace=$((grace+1)); done; '
           'if /bin/kill -0 \"$meter\" 2>/dev/null; then /bin/kill -KILL \"$meter\" 2>/dev/null; fi; '
           'wait "$meter"; code=$?; /bin/echo "$code" > "$1/exit_status"')
    command=('umask 022; d=$(/usr/bin/mktemp -d /private/tmp/coop-power.XXXXXX); /bin/chmod 755 "$d"; '
             '/bin/sh -c '+shlex.quote(child)+' sh "$d" > "$d/supervisor.log" 2>&1 < /dev/null & '
             '/bin/echo "$d"')
    # JSON string escaping is used for an AppleScript literal, never for shell quoting.
    apple='with timeout of 120 seconds\ndo shell script '+json.dumps(command)+' with administrator privileges without altering line endings\nend timeout'
    launched=utc()
    answer=subprocess.run(['/usr/bin/osascript','-e',apple],capture_output=True,text=True,timeout=135)
    if answer.returncode:raise RuntimeError('Power authentication/launch failed: '+answer.stderr.strip())
    root=Path(answer.stdout.strip())
    if root.parent!=Path('/private/tmp') or not root.name.startswith('coop-power.'):
        raise ValueError('Unexpected power capture path')
    meta=dict(launch_requested_utc=launched,launch_returned_utc=utc(),root_capture_dir=str(root),stop_flag=str(stop),
              interval_ms=1000,max_samples=3000,max_supervisor_seconds=3000,samplers=['cpu_power','gpu_power'])
    (output_dir/'POWER_LAUNCH.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
    try:
        deadline=time.monotonic()+15
        while True:
            text=(root/'samples.txt').read_text() if (root/'samples.txt').exists() else ''
            if text.count('Combined Power (CPU + GPU + ANE):')>=2:break
            if time.monotonic()>deadline:raise RuntimeError('Power sampler readiness timeout')
            time.sleep(.25)
    except Exception:
        stop.write_text('stop\n');stop_and_archive(meta,output_dir);raise
    return meta

def stop_and_archive(meta,output_dir):
    output_dir=Path(output_dir);root=Path(meta['root_capture_dir'])
    time.sleep(3)  # Conservative post-episode coverage beyond whole-second timestamp uncertainty.
    Path(meta['stop_flag']).write_text('stop\n')
    deadline=time.monotonic()+12
    while not (root/'exit_status').exists() and time.monotonic()<deadline:time.sleep(.2)
    status=dict(stopped_utc=utc(),stop_confirmed=(root/'exit_status').exists())
    if status['stop_confirmed']:status['returncode']=int((root/'exit_status').read_text())
    for name in ['supervisor.log','meter.pid','exit_status']:
        if (root/name).exists():(output_dir/('POWER_'+name.replace('.','_')+'.txt')).write_bytes((root/name).read_bytes())
    if (root/'samples.txt').exists():
        with (root/'samples.txt').open('rb') as source, (output_dir/'POWER.txt.gz').open('wb') as target:
            with gzip.GzipFile(fileobj=target,mode='wb',mtime=0) as zipped:
                while block:=source.read(1<<20):zipped.write(block)
    (output_dir/'POWER_STOP.json').write_text(json.dumps(status,indent=2,sort_keys=True)+'\n')
    return status
