"""Open-loop Ollama request collector. Implementation delegated under CLIENT_CONTRACT.txt.

Standard library only. One worker thread per offered job; each sleeps until its
arrival offset on a shared monotonic epoch and dispatches regardless of what any
earlier job is doing (open loop). The client never retries, never filters, never
peeks at token lengths, and never changes admission; server parallelism is an
external knob, not a function of this worker count.

http.client is used deliberately instead of urllib.request: urllib consults
proxy environment variables, which this client must not inspect.
"""

import http.client
import json
import math
import socket
import threading
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit

_LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")
_DEFAULT_PORT = 80  # Standard HTTP port when the URL omits one (pilot always passes one).
_MAX_LINE_BYTES = 1 << 20  # 1 MiB bound per NDJSON line against runaway responses.
_MAX_ERROR_BODY_BYTES = 64 * 1024
_USAGE_FIELDS = (
    "prompt_eval_count",
    "eval_count",
    "total_duration",
    "load_duration",
    "prompt_eval_duration",
    "eval_duration",
)


# --------------------------------------------------------------------------- #
# Validation (all of it happens before any dispatch)
# --------------------------------------------------------------------------- #

def _parse_base_url(base_url):
    """Return (host, port) for an HTTP literal-loopback base URL, else ValueError."""
    if not isinstance(base_url, str) or not base_url:
        raise ValueError("base_url must be a nonempty string")
    parts = urlsplit(base_url)
    if parts.scheme != "http":
        raise ValueError("base_url scheme must be http (got %r)" % (parts.scheme,))
    if parts.username is not None or parts.password is not None:
        raise ValueError("base_url must not contain userinfo")
    if parts.path not in ("", "/"):
        raise ValueError("base_url must not contain a path (got %r)" % (parts.path,))
    if parts.query or parts.fragment:
        raise ValueError("base_url must not contain query or fragment")
    host = parts.hostname
    if host not in _LOOPBACK_HOSTS:
        raise ValueError(
            "base_url host must be a literal loopback host %s (got %r)"
            % (_LOOPBACK_HOSTS, host)
        )
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError("base_url port is invalid") from exc
    if port is None:
        port = _DEFAULT_PORT
    return host, port


def _is_finite_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _validate_trace(trace):
    """Raise ValueError on any malformed trace entry; return nothing."""
    if not isinstance(trace, list):
        raise ValueError("trace must be a list of request dicts")
    seen = set()
    for index, item in enumerate(trace):
        if not isinstance(item, dict):
            raise ValueError("trace[%d] is not a dict" % index)
        request_id = item.get("request_id")
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("trace[%d].request_id must be a nonempty string" % index)
        if request_id in seen:
            raise ValueError("trace[%d].request_id %r is duplicated" % (index, request_id))
        seen.add(request_id)
        if not isinstance(item.get("prompt"), str):
            raise ValueError("trace[%d].prompt must be a string" % index)
        offset = item.get("arrival_offset_s")
        if not _is_finite_number(offset) or offset < 0:
            raise ValueError(
                "trace[%d].arrival_offset_s must be a finite nonnegative number" % index
            )


def _validate_timeout(timeout_s):
    if not _is_finite_number(timeout_s) or timeout_s <= 0:
        raise ValueError("timeout_s must be a finite positive number")


# --------------------------------------------------------------------------- #
# Terminal validation of a completed stream
# --------------------------------------------------------------------------- #

def _is_nonneg_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_final(final, expected_model, content):
    """Return None when the terminal object satisfies the contract, else an error string."""
    if final.get("done") is not True:
        return "terminal object does not have done=true"
    if not content:
        return "stream completed with empty response content"
    if final.get("model") != expected_model:
        return "model mismatch: expected %r, got %r" % (expected_model, final.get("model"))
    for field in _USAGE_FIELDS:
        if field not in final:
            return "missing usage field %r" % field
        if not _is_nonneg_int(final[field]):
            return "usage field %r is not a nonnegative integer (got %r)" % (field, final[field])
    if final["eval_count"] <= 0:
        return "eval_count must be > 0 (got %r)" % (final["eval_count"],)
    return None


# --------------------------------------------------------------------------- #
# Worker
# --------------------------------------------------------------------------- #

def _run_one(epoch, host, port, job, model, options, timeout_s, budget_s, result_slot, index):
    """Dispatch a single job and store exactly one result row at result_slot[index]."""
    request_id = job["request_id"]
    arrival = job["arrival_offset_s"]

    row = {
        "request_id": request_id,
        "arrival_offset_s": arrival,
        "dispatch_offset_s": None,
        "first_content_offset_s": None,
        "terminal_offset_s": None,
        "completed": False,
        "error": None,
        "chunks": [],
        "final": None,
        "http_status": None,
        "deadline_exceeded": False,
    }
    result_slot[index] = row  # Present even if something below raises unexpectedly.

    def now():
        return time.monotonic() - epoch

    def finish(error):
        # Record the actual terminal time; never clear chunks already received.
        if row["terminal_offset_s"] is None:
            row["terminal_offset_s"] = now()
        row["error"] = error
        row["completed"] = error is None
        if row["dispatch_offset_s"] is not None:
            row["deadline_exceeded"] = (
                row["terminal_offset_s"] - row["dispatch_offset_s"] > budget_s
            )

    # Open-loop wait: only the shared epoch matters, never other jobs' progress.
    target = epoch + arrival
    while True:
        remaining = target - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(remaining)

    conn = None
    try:
        payload = {
            "model": model,
            "prompt": job["prompt"],
            "options": options,  # passed through unchanged
            "stream": True,
            "keep_alive": "120s",
        }
        body = json.dumps(payload).encode("utf-8")

        row["dispatch_offset_s"] = now()
        dispatch_mono = time.monotonic()
        conn = http.client.HTTPConnection(host, port, timeout=timeout_s)
        conn.request(
            "POST",
            "/api/generate",
            body=body,
            headers={"Content-Type": "application/json", "Accept": "application/x-ndjson"},
        )
        resp = conn.getresponse()
        row["http_status"] = resp.status

        if resp.status != 200:
            detail = b""
            try:
                detail = resp.read(_MAX_ERROR_BODY_BYTES)
            except Exception:  # body is diagnostic only
                pass
            finish(
                "http error %d %s: %s"
                % (resp.status, resp.reason, detail.decode("utf-8", "replace").strip()[:512])
            )
            return

        content_parts = []
        final = None
        while True:
            # Elapsed-budget check between received lines (not a hard deadline).
            if time.monotonic() - dispatch_mono > budget_s:
                finish("elapsed budget of %gs exceeded between lines" % budget_s)
                return

            line = resp.readline(_MAX_LINE_BYTES + 1)
            received = now()
            if not line:
                break  # EOF
            if len(line) > _MAX_LINE_BYTES:
                finish("stream line exceeded %d bytes" % _MAX_LINE_BYTES)
                return
            if not line.strip():
                continue  # keep-alive blank line; counts as activity only

            try:
                obj = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, ValueError) as exc:
                finish("malformed JSON in stream: %s" % exc)
                return

            row["chunks"].append({"offset_s": received, "data": obj})

            if not isinstance(obj, dict):
                finish("stream object is not a JSON object")
                return
            if "error" in obj:
                finish("server error: %s" % (obj["error"],))
                return

            response = obj.get("response")
            if isinstance(response, str) and response:
                content_parts.append(response)
                if row["first_content_offset_s"] is None:
                    row["first_content_offset_s"] = received

            if obj.get("done") is True:
                final = obj
                row["terminal_offset_s"] = received
                break

        if final is None:
            finish("stream ended without a terminal done=true object")
            return

        row["final"] = final
        finish(_validate_final(final, model, "".join(content_parts)))

    except socket.timeout:
        finish("socket inactivity timeout after %gs" % timeout_s)
    except (http.client.HTTPException, OSError) as exc:
        finish("%s: %s" % (type(exc).__name__, exc))
    except Exception as exc:  # any other failure still yields one retained result
        finish("unexpected %s: %s" % (type(exc).__name__, exc))
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
        if row["terminal_offset_s"] is None:
            row["terminal_offset_s"] = now()
        if row["error"] is None and not row["completed"]:
            row["error"] = "worker exited without a terminal classification"


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def _lifecycle_failure_row(job, error, terminal_offset_s):
    """Result row for a job whose worker never dispatched (creation/start failed)."""
    return {
        "request_id": job["request_id"],
        "arrival_offset_s": job["arrival_offset_s"],
        "dispatch_offset_s": None,
        "first_content_offset_s": None,
        "terminal_offset_s": terminal_offset_s,
        "completed": False,
        "error": error,
        "chunks": [],
        "final": None,
        "http_status": None,
        "deadline_exceeded": False,
    }


def run_trace(base_url, trace, model, options, timeout_s=60):
    """Replay an open-loop arrival trace against a loopback Ollama server.

    Returns {'started_utc', 'elapsed_seconds', 'requests'} with one result row
    per offered job in input order. ``timeout_s`` is the per-socket inactivity
    timeout and also the elapsed budget checked between received lines. Neither
    is a hard real-time deadline; the actual terminal time is always recorded
    and ``deadline_exceeded`` keeps the classification for later analysis.

    A worker that cannot be created or started is retained as a failed row
    (``dispatch_offset_s`` is None); remaining jobs are still dispatched and
    only workers that actually started are joined.
    """
    host, port = _parse_base_url(base_url)
    _validate_trace(trace)
    _validate_timeout(timeout_s)
    budget_s = timeout_s
    if not isinstance(model, str) or not model:
        raise ValueError("model must be a nonempty string")

    started_utc = datetime.now(timezone.utc).isoformat()
    jobs = list(trace)
    results = [None] * len(jobs)
    lifecycle_errors = {}  # index -> error string for workers that never started

    # Common monotonic epoch shared by every worker.
    epoch = time.monotonic()
    started = []
    for index, job in enumerate(jobs):
        # Creation and start are both guarded per job: a failure here must never
        # escape (losing the whole result dictionary) nor stop the remaining jobs.
        try:
            thread = threading.Thread(
                target=_run_one,
                args=(epoch, host, port, job, model, options, timeout_s, budget_s, results, index),
                name="trace-%s" % job["request_id"],
                daemon=True,
            )
            thread.start()
        except Exception as exc:
            lifecycle_errors[index] = "worker lifecycle failure: %s: %s" % (
                type(exc).__name__,
                exc,
            )
            continue
        started.append(thread)

    # Join only workers whose start() returned normally.
    for thread in started:
        thread.join()
    elapsed = time.monotonic() - epoch

    # Every offered job keeps exactly one row in input order. A worker that ran
    # wrote its own row; a worker that never started gets a lifecycle-failure row.
    for index, job in enumerate(jobs):
        if results[index] is None:
            results[index] = _lifecycle_failure_row(
                job,
                lifecycle_errors.get(index, "worker produced no result"),
                elapsed,
            )

    return {
        "started_utc": started_utc,
        "elapsed_seconds": elapsed,
        "requests": results,
    }
