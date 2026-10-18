#!/usr/bin/env python3
"""Static dependency inventory only: does not import or run a selected checker."""
import ast
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def source_record(path):
    blob = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(blob),
            'sha256': hashlib.sha256(blob).hexdigest(), 'symlink': path.is_symlink()}


def pathlike(value):
    return bool(re.search(r'(?:^/|^~[/\\]|^[A-Za-z]:\\|^file:|^https?://|/Users/|/home/)', value))


def inventory_source(path):
    text = path.read_text()
    tree = ast.parse(text)
    imports = []
    io_calls = []
    paths = []
    flagged = []
    io_names = {'open', 'read_text', 'read_bytes', 'write_text', 'write_bytes',
                'Path', 'resolve', 'with_suffix', 'copy2', 'is_file', 'iterdir',
                'mkdir', 'mkdtemp', 'run', 'find_spec'}
    forbidden = {'eval', 'exec', '__import__', 'run_path', 'run_module'}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append({'line': node.lineno, 'source': ast.get_source_segment(text, node)})
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and pathlike(node.value):
            paths.append({'line': node.lineno, 'literal': node.value})
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else fn.id if isinstance(fn, ast.Name) else ''
            if name in io_names:
                io_calls.append({'line': node.lineno, 'source': ast.get_source_segment(text, node)})
            if name in forbidden:
                flagged.append({'line': node.lineno, 'source': ast.get_source_segment(text, node)})
    return {**source_record(path), 'imports': sorted(imports, key=lambda x: x['line']),
            'pathlike_literals': sorted(paths, key=lambda x: x['line']),
            'file_or_process_calls': sorted(io_calls, key=lambda x: x['line']),
            'dynamic_execution_calls': flagged}


def scan_strings(value, at='$'):
    if isinstance(value, str):
        if pathlike(value):
            yield {'location': at, 'value': value}
    elif isinstance(value, dict):
        for key, item in value.items():
            if pathlike(key):
                yield {'location': at + '.<key>', 'value': key}
            yield from scan_strings(item, at + '.' + key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from scan_strings(item, at + '[' + str(i) + ']')


def main():
    runner = ROOT / 'reproduce_campaign.py'
    tree = ast.parse(runner.read_text())
    jobs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'jobs' for t in node.targets):
            jobs.extend(ast.literal_eval(node.value))
        elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == 'jobs':
            jobs.extend(ast.literal_eval(node.value))
    if len(jobs) != 6:
        raise SystemExit('Unexpected job table; audit needs manual update')
    scripts = [runner] + [ROOT / relative for label, relative, args, fixtures in jobs]
    fixtures = [ROOT / relative.parent / fixture
                for label, name, args, names in jobs
                for relative in [Path(name)] for fixture in names]
    fixture_records = []
    for path in fixtures:
        if path.name.endswith('.jsonl.gz'):
            documents = [json.loads(row) for row in gzip.decompress(path.read_bytes()).splitlines()]
        else:
            documents = [json.loads(path.read_text())]
        fixture_records.append({**source_record(path), 'serialized_documents': len(documents),
                                'pathlike_strings': list(scan_strings(documents)),
                                'top_level_keys': sorted(set(k for doc in documents for k in doc))})
    sources = [inventory_source(path) for path in scripts]
    result = {'status': 'STATIC_INVENTORY_COMPLETE',
              'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Source and serialized proof-data inspection only; no checker imported, executed, or mathematically replayed.',
              'jobs_from_runner_ast': jobs, 'sources': sources, 'fixtures': fixture_records,
              'input_count_including_runner': len(scripts) + len(fixtures),
              'absolute_or_url_literals_in_sources': sum(len(s['pathlike_literals']) for s in sources),
              'absolute_or_url_strings_in_fixtures': sum(len(f['pathlike_strings']) for f in fixture_records),
              'dynamic_execution_calls_in_sources': sum(len(s['dynamic_execution_calls']) for s in sources)}
    (HERE / 'DEPENDENCY_INVENTORY.json').write_text(json.dumps(result, indent=2) + '\n')
    manifest = {'timestamp_utc': result['timestamp_utc'],
                'scope': result['scope'], 'sources': [source_record(path) for path in scripts + fixtures]}
    (HERE / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'timestamp_utc', 'input_count_including_runner',
          'absolute_or_url_literals_in_sources', 'absolute_or_url_strings_in_fixtures',
          'dynamic_execution_calls_in_sources')}, indent=2))


if __name__ == '__main__':
    main()
