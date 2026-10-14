#!/usr/bin/env python3
"""Independent integer audit of the fixed SIFT-small Mac retrieval qualification."""
import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import struct
import tarfile

BASE_FILE = 'data/siftsmall_base.fvecs'
QUERY_FILE = 'data/siftsmall_query.fvecs'
GT_FILE = 'data/siftsmall_groundtruth.ivecs'
ARCHIVE_MD5 = '0b8324a7a82d7f2663d7dcbd57642df7'
CAP = 64 * 1024 * 1024


def load(path):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def reject(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=unique, parse_constant=reject)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def finite(value, minimum=0):
    return type(value) in (int, float) and math.isfinite(value) and value >= minimum


def read_vecs(path, rows, dimension, floating):
    """Check every little-endian record header; do not reshape around bad input."""
    raw = Path(path).read_bytes()
    stride = 4 * (dimension + 1)
    if len(raw) != rows * stride:
        raise ValueError('Vector file length/count mismatch: ' + str(path))
    values = []
    for i in range(rows):
        offset = i * stride
        if struct.unpack_from('<i', raw, offset)[0] != dimension:
            raise ValueError('Vector dimension header mismatch at row ' + str(i))
        row = struct.unpack_from('<' + ('f' if floating else 'i') * dimension, raw, offset + 4)
        if floating:
            if any(not math.isfinite(x) or not 0 <= x <= 255 or x != int(x) for x in row):
                raise ValueError('Coordinate is not a finite integer in [0,255] at row ' + str(i))
            row = tuple(map(int, row))
        values.append(row)
    return values


def integer_oracle(base, queries, k=10):
    """Direct integer difference squares; independent of the GPU dot-product route."""
    if not base or not queries or not 0 < k <= len(base):
        raise ValueError('Empty corpus or invalid k')
    dimension = len(base[0])
    if not dimension or any(len(row) != dimension or any(type(x) is not int or not 0 <= x <= 255 for x in row)
                            for row in base + queries):
        raise ValueError('Invalid oracle coordinates or dimension')
    distances, top_ids, top_distances = [], [], []
    for query in queries:
        row = [sum((q-x)*(q-x) for q,x in zip(query, vector)) for vector in base]
        ids = sorted(range(len(base)), key=lambda j: (row[j], j))[:k]
        distances.append(row)
        top_ids.append(ids)
        top_distances.append([row[j] for j in ids])
    return {'distances': distances, 'top_ids': top_ids, 'top_distances': top_distances}


def check_groundtruth(groundtruth, oracle, base_count):
    errors, overlap = [], []
    distances = oracle['distances']
    if len(groundtruth) != len(distances):
        errors.append('Official ground-truth query count mismatch')
    for qi, row in enumerate(groundtruth):
        if qi >= len(distances):
            break
        if not row or len(set(row)) != len(row) or any(type(j) is not int or not 0 <= j < base_count for j in row):
            errors.append(f'Official ground-truth invalid/duplicate IDs at query {qi}')
            continue
        actual = [distances[qi][j] for j in row]
        wanted = sorted(distances[qi])[:len(row)]
        if actual != wanted:
            errors.append(f'Official ground-truth ordered distance/tie-boundary mismatch at query {qi}')
        k = len(oracle['top_ids'][qi])
        overlap.append(len(set(row[:k]) & set(oracle['top_ids'][qi])))
    return {'checks_passed': not errors, 'errors': errors, 'queries_checked': min(len(groundtruth), len(distances)),
            'canonical_top10_official_id_set_overlap_total': sum(overlap),
            'canonical_top10_official_id_overlap_by_query': overlap,
            'tie_rule': 'Official IDs may differ within exact-distance ties; ordered distances must equal the full-oracle smallest distances.'}


def check_distance_file(path, oracle):
    raw = Path(path).read_bytes()
    expected_rows = oracle['distances']
    count = sum(map(len, expected_rows))
    if len(raw) != 4 * count:
        return {'checks_passed': False, 'errors': ['Distance output length/count mismatch'],
                'planned_distances': count, 'reported_distances': len(raw)//4, 'compared_distances': 0,
                'mismatch_count': None, 'sha256': hashlib.sha256(raw).hexdigest()}
    actual = struct.iter_unpack('<I', raw)
    mismatch = sum(next(actual)[0] != expected for row in expected_rows for expected in row)
    expected_digest = hashlib.sha256()
    for row in expected_rows:
        expected_digest.update(struct.pack('<' + 'I'*len(row), *row))
    return {'checks_passed': mismatch == 0, 'errors': [] if not mismatch else ['Distance values/query order differ from independent integer oracle'],
            'planned_distances': count, 'reported_distances': count, 'compared_distances': count,
            'mismatch_count': mismatch, 'sha256': hashlib.sha256(raw).hexdigest(),
            'independent_expected_sha256': expected_digest.hexdigest()}


def power(diagnostic):
    if not isinstance(diagnostic, dict) or type(diagnostic.get('returncode')) is not int or diagnostic['returncode'] != 0:
        return None
    text = diagnostic.get('stdout', '')
    if not isinstance(text, str):
        return None
    sources = re.findall(r"Now drawing from '([^']+)'", text)
    return sources[0] if len(sources) == 1 and sources[0] in ('AC Power', 'Battery Power') else None


def source_data(root):
    """Verify exact extracted bytes and full source schema; no candidate imports."""
    root = Path(root)
    manifest = load(root/'DATA_MANIFEST.json')
    raw_archive = (root/'siftsmall.tar.gz').read_bytes()
    if hashlib.md5(raw_archive).hexdigest() != ARCHIVE_MD5 or manifest.get('archive_md5') != ARCHIVE_MD5:
        raise ValueError('Official archive MD5 mismatch')
    if manifest.get('archive_sha256') != hashlib.sha256(raw_archive).hexdigest() or manifest.get('archive_bytes') != len(raw_archive):
        raise ValueError('Archive manifest mismatch')
    if manifest.get('archive_url') != 'ftp://ftp.irisa.fr/local/texmex/corpus/siftsmall.tar.gz':
        raise ValueError('Archive URL changed')
    wanted = {BASE_FILE:(10000,128,True), QUERY_FILE:(100,128,True), GT_FILE:(100,100,False)}
    values, summaries = {}, {}
    with tarfile.open(root/'siftsmall.tar.gz','r:gz') as archive:
        members = archive.getmembers()
        for name, (rows, dimension, floating) in wanted.items():
            raw = (root/name).read_bytes()
            archived_name = 'siftsmall/' + Path(name).name
            selected = [m for m in members if m.name == archived_name]
            if len(selected) != 1 or not selected[0].isfile() or selected[0].size != len(raw):
                raise ValueError('Missing/ambiguous archive member: '+name)
            with archive.extractfile(selected[0]) as handle:
                if handle.read() != raw:
                    raise ValueError('Extracted bytes differ from original archive: '+name)
            metadata = manifest['files'][name]
            digest = hashlib.sha256(raw).hexdigest()
            if (metadata.get('sha256') != digest or metadata.get('bytes') != len(raw)
                    or metadata.get('rows') != rows or metadata.get('dimensions') != dimension):
                raise ValueError('Data manifest mismatch: '+name)
            matrix = read_vecs(root/name, rows, dimension, floating)
            stats = {'rows':rows,'dimensions':dimension,'bytes':len(raw),'sha256':digest,
                     'minimum_component_or_id':min(map(min,matrix)),
                     'maximum_component_or_id':max(map(max,matrix))}
            if floating:
                norms = [sum(x*x for x in row) for row in matrix]
                stats.update(coordinates_all_integral_0_to_255=True,
                             minimum_squared_norm=min(norms),maximum_squared_norm=max(norms))
            if any(metadata.get(key) != value for key,value in stats.items()):
                raise ValueError('Data manifest structural statistic mismatch: '+name)
            values[name] = matrix; summaries[name] = stats
    return values, summaries


def safe_relative(name):
    if not isinstance(name,str):
        raise ValueError('Nonstring relative path')
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or name != path.as_posix():
        raise ValueError('Unsafe relative path: '+name)
    return name


def frozen_sources(root, freeze):
    required = {'PROTOCOL.txt','PLAN.json','DATA_MANIFEST.json','retrieve.swift','run_retrieval.py',
                'capture_inventory.py','audit_retrieval.py','test_audit_retrieval.py',
                BASE_FILE,QUERY_FILE,GT_FILE,'siftsmall.tar.gz','SOURCES.txt','MD5SUM.source.txt'}
    mapping = freeze['source_sha256']
    errors = []
    if not required <= set(mapping):
        errors.append('Freeze omits required sources/data/tests')
    for name, expected in mapping.items():
        if sha(root/safe_relative(name)) != expected:
            errors.append('Frozen source mismatch: '+name)
    return errors


def check_plan(plan):
    expected = {'schema_version':1,'protocol_id':'mac-sift10k-retrieval-v1',
                'base_count':10000,'query_count':100,'dimension':128,'top_k':10,
                'official_groundtruth_k':100,'native_explicit_byte_cap':CAP,
                'campaign_timeout_seconds':300,'window_timeout_seconds':90,
                'profiles':[{'batch_size':1,'folder':'p01_b1','index':1,'profile_id':'b1'},
                            {'batch_size':16,'folder':'p02_b16','index':2,'profile_id':'b16'}]}
    if json.dumps(plan,sort_keys=True) != json.dumps(expected,sort_keys=True):
        raise ValueError('Plan differs from reviewed fixed qualification')


def utc_interval(value, start='started_utc', end='finished_utc'):
    try:
        a,b = [datetime.fromisoformat(value[key].replace('Z','+00:00')) for key in (start,end)]
        return a.utcoffset() is not None and b.utcoffset() is not None and a.utcoffset().total_seconds()==b.utcoffset().total_seconds()==0 and b>=a
    except (KeyError,ValueError,TypeError,AttributeError):
        return False


def check_queries(rows, oracle, batch_size):
    errors, matched, correct_queries = [], 0, 0
    if not isinstance(rows,list):
        return {'errors':['Query records are not a list'],'canonical_top10_positions_matched':0,
                'independently_correct_queries':0,'reported_queries':0}
    if len(rows) != len(oracle['distances']): errors.append('Query records missing/extra')
    for qi, expected_distances in enumerate(oracle['distances']):
        if qi >= len(rows) or not isinstance(rows[qi],dict):
            errors.append(f'Query {qi} missing/nonobject'); continue
        row = rows[qi]; before = len(errors)
        def check(ok,message):
            if not ok: errors.append(f'Query {qi}: '+message)
        check(type(row.get('query_id')) is int and row['query_id'] == qi,'Wrong query identity/order')
        check(type(row.get('batch_index')) is int and row['batch_index'] == qi//batch_size,'Wrong batch assignment')
        check(row.get('passed') is True and row.get('status') == 'passed' and row.get('failure') is None,'Native query failed/unrun')
        for key,value in [('compared_distances',len(expected_distances)),('mismatch_count',0),('invalid_dot_count',0)]:
            check(type(row.get(key)) is int and row[key] == value,'Wrong '+key)
        check(finite(row.get('max_abs_error')) and row['max_abs_error']==0,'Nonzero/invalid maximum error')
        check(row.get('top10_exact_match') is True,'Native top-ten comparison failed')
        digest = hashlib.sha256(struct.pack('<'+'I'*len(expected_distances),*expected_distances)).hexdigest()
        check(row.get('gpu_distance_sha256') == digest and row.get('cpu_distance_sha256') == digest,'Per-query distance hash mismatch')
        expected_top = [{'id':i,'distance':d} for i,d in zip(oracle['top_ids'][qi],oracle['top_distances'][qi])]
        for field in ('top10','cpu_top10'):
            candidate = row.get(field)
            # JSON representation distinguishes booleans/floats from integer IDs/distances.
            check(json.dumps(candidate,sort_keys=True)==json.dumps(expected_top,sort_keys=True),'Wrong canonical '+field)
        candidate = row.get('top10')
        if isinstance(candidate,list):
            matched += sum(json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True) for a,b in zip(candidate,expected_top))
        for key in ('reconstruction_selection_seconds','cpu_oracle_validation_seconds'):
            check(finite(row.get(key)), 'Invalid '+key)
        correct_queries += int(len(errors)==before)
    return {'errors':errors,'canonical_top10_positions_matched':matched,
            'independently_correct_queries':correct_queries,'reported_queries':len(rows)}


def audit_profile(raw, distance_path, profile, plan, oracle, stats, device_names):
    result = dict(profile,checks_passed=False)
    comparison = check_distance_file(distance_path,oracle)
    result['distance_output'] = comparison; result['compared_distances'] = comparison['compared_distances']
    queries = check_queries(raw.get('queries'),oracle,profile['batch_size'])
    result.update({k:v for k,v in queries.items() if k!='errors'})
    errors = comparison['errors'] + queries['errors']; result['errors'] = errors
    def check(ok,message):
        if not ok: errors.append(message)
    for key,value in [('schema_version',1),('batch_size',profile['batch_size']),('base_count',10000),
                      ('query_count',100),('dimensions',128),('top_k',10),('distance_file_bytes',4000000)]:
        check(type(raw.get(key)) is int and raw[key]==value,'Wrong native '+key)
    check(raw.get('protocol_id') == plan['protocol_id'],'Wrong native protocol')
    check(raw.get('gate_passed') is True and raw.get('cpu_self_test_passed') is True
          and raw.get('inputs_validated') is True and raw.get('failure') is None,'Native qualification/input/selftest failed')
    check(raw.get('input_base_sha256')==stats[BASE_FILE]['sha256'] and raw.get('input_query_sha256')==stats[QUERY_FILE]['sha256'],'Native input hashes differ')
    check(raw.get('device_name') in device_names and raw.get('has_unified_memory') is True,'Native device/inventory mismatch')
    check(integer(raw.get('max_buffer_length'),1) and integer(raw.get('recommended_max_working_set_size'),1),'Invalid device limits')
    check(integer(raw.get('clock_origin_uptime_ns'),1) and utc_interval(raw,'started_at','completed_at'),'Invalid native clock/UTC interval')
    check(raw.get('distance_file')=='distances.u32le' and raw.get('distance_file_sha256')==comparison['sha256'],'Distance output path/hash mismatch')
    phase_keys = ('input_read_validate_seconds','index_prepare_seconds','distances_write_seconds','processing_through_distance_output_seconds')
    check(all(finite(raw.get(k)) for k in phase_keys),'Invalid profile phase durations')
    memory = raw['memory']
    fixed_fields = {'cap_bytes':CAP,'input_file_staging_bound_bytes':10100*129*4,
                    'input_vector_bytes':10100*128,'integer_norm_bytes':10100*8,
                    'distance_matrix_bytes':4000000,'distance_serialization_bytes':4000000,
                    'cpu_selection_hash_scratch_bound_bytes':512*1024,'top10_storage_bound_bytes':64000,
                    'base_buffer_payload_bytes':10000*128*4}
    for key,value in fixed_fields.items():
        check(type(memory.get(key)) is int and memory[key]==value,'Wrong explicit-memory component '+key)
    fixed = sum(value for key,value in fixed_fields.items() if key not in ('cap_bytes','base_buffer_payload_bytes'))
    stride, length, allocated = [memory.get(k) for k in ('base_row_bytes','base_buffer_length_bytes','base_buffer_allocated_bytes')]
    check(integer(stride,512) and stride%4==0 and integer(length,1) and length==10000*stride,'Invalid base stride/length')
    check(integer(allocated,1) and integer(length,1) and allocated>=length,'Invalid base allocated size')
    check(integer(length,1) and integer(raw.get('max_buffer_length'),1) and length<=raw['max_buffer_length'],'Base exceeds device maximum buffer')
    for key in ('device_allocated_before_base_sample','device_allocated_with_base_sample','device_allocated_before_retrieve_return_sample'):
        check(integer(memory.get(key)), 'Invalid device allocation sample '+key)
    batches = raw.get('batches')
    if not isinstance(batches,list): raise ValueError('Native batches must be a list')
    expected_starts = list(range(0,100,profile['batch_size']))
    check(len(batches)==len(expected_starts),'Batch count differs')
    previous_release, maximum_batch_bytes = 0., 0
    timings = []
    for i,start in enumerate(expected_starts):
        if i>=len(batches) or not isinstance(batches[i],dict):
            check(False,f'Batch {i} missing/nonobject'); continue
        b = batches[i]; count=min(profile['batch_size'],100-start)
        for key,value in [('index',i),('query_start',start),('query_count',count),('command_buffer_status',4)]:
            check(type(b.get(key)) is int and b[key]==value,f'Batch {i}: wrong '+key)
        check(b.get('status')=='passed' and b.get('passed') is True and b.get('failure') is None and b.get('command_buffer_error') is None,f'Batch {i}: native failure')
        fields = ('preparation_start_s','submit_s','gpu_completion_observed_s','reconstruction_start_s',
                  'reconstruction_end_s','oracle_start_s','oracle_end_s','resource_release_s')
        t = [b.get(k) for k in fields]
        check(all(finite(x) for x in t),f'Batch {i}: invalid phase timestamp')
        if all(finite(x) for x in t):
            check(t[0]>=previous_release and all(y>=x for x,y in zip(t,t[1:])),f'Batch {i}: overlapping/reversed host phases')
            previous_release=t[-1]
            intervals = {'preparation_seconds':t[1]-t[0],'gpu_submit_to_completion_seconds':t[2]-t[1],
                         'reconstruction_selection_seconds':t[4]-t[3],'cpu_oracle_validation_seconds':t[6]-t[5]}
            for key,value in intervals.items():
                check(finite(b.get(key)) and math.isclose(b[key],value,rel_tol=1e-9,abs_tol=1e-9),f'Batch {i}: phase duration mismatch '+key)
            for key in ('reconstruction_selection_seconds','cpu_oracle_validation_seconds'):
                rows=raw['queries'][start:start+count]
                if finite(b.get(key)) and len(rows)==count and all(isinstance(q,dict) and finite(q.get(key)) for q in rows):
                    check(sum(q[key] for q in rows)<=b[key]+1e-9,f'Batch {i}: query times exceed enclosing phase')
            timings.append(intervals)
        device_t = [b.get(k) for k in ('gpu_start_time','gpu_end_time','gpu_interval_seconds')]
        if any(x is not None for x in device_t):
            check(all(finite(x,1e-12) for x in device_t),f'Batch {i}: partial/invalid device times')
            if all(finite(x,1e-12) for x in device_t):
                check(device_t[1]>device_t[0] and math.isclose(device_t[1]-device_t[0],device_t[2],rel_tol=1e-9,abs_tol=1e-12),f'Batch {i}: device interval mismatch')
        batch_bytes=0
        for prefix,columns in [('query',128),('dot',10000)]:
            rb,ln,alloc = [b.get(prefix+k) for k in ('_row_bytes','_buffer_length_bytes','_buffer_allocated_bytes')]
            check(integer(rb,columns*4) and rb%4==0 and integer(ln,1) and ln==count*rb,f'Batch {i}: invalid {prefix} stride/length')
            check(type(b.get(prefix+'_buffer_payload_bytes')) is int and b[prefix+'_buffer_payload_bytes']==count*columns*4,f'Batch {i}: wrong {prefix} payload')
            check(integer(alloc,1) and integer(ln,1) and alloc>=ln,f'Batch {i}: invalid {prefix} allocation')
            check(integer(ln,1) and integer(raw.get('max_buffer_length'),1) and ln<=raw['max_buffer_length'],f'Batch {i}: {prefix} exceeds maximum buffer')
            if integer(alloc): batch_bytes+=alloc
        bound=fixed+allocated+batch_bytes if integer(allocated) else None
        check(integer(bound) and type(b.get('explicit_bound_bytes')) is int and b['explicit_bound_bytes']==bound and bound<=CAP,f'Batch {i}: explicit memory bound mismatch/exceeded')
        maximum_batch_bytes=max(maximum_batch_bytes,batch_bytes)
        for key in ('device_allocated_before_buffers_sample','device_allocated_with_buffers_sample','device_allocated_after_release_sample'):
            check(integer(b.get(key)),f'Batch {i}: invalid device allocation sample')
    check(memory.get('maximum_batch_buffer_allocated_bytes')==maximum_batch_bytes,'Wrong maximum batch allocation')
    bound=fixed+allocated+maximum_batch_bytes if integer(allocated) else None
    check(integer(bound) and memory.get('conservative_explicit_bound_bytes')==bound and bound<=CAP,'Wrong/exceeded process explicit bound')
    if finite(raw.get('processing_through_distance_output_seconds')) and finite(raw.get('distances_write_seconds')):
        check(raw['processing_through_distance_output_seconds']>=previous_release+raw['distances_write_seconds']-1e-9,'Output duration ends before final release/write')
    result.update(checks_passed=not errors,reported_batches=len(batches),maximum_explicit_bound_bytes=bound,
                  phase_totals_seconds={k:sum(t[k] for t in timings) for k in timings[0]} if timings else {},
                  profile_phase_seconds={k:raw.get(k) for k in phase_keys})
    return result


def analyze(root, capture, binary=None):
    root, capture = Path(root), Path(capture)
    if not capture.is_absolute(): capture = root/capture
    errors, results = [], []
    output = {'schema_version':1,'checks_passed':False,'errors':errors,'profiles':results,
              'planned_profiles':2,'planned_query_executions':200,'planned_distances':2000000,
              'planned_top10_positions':2000,'binary_bytes_reverified':False,
              'auditor_sha256':sha(Path(__file__)),
              'interpretation':'Exact fixed-corpus qualification; timings descriptive. No speed, energy, semantic relevance or pooling claim.'}
    def check(ok, message):
        if not ok: errors.append(message)
    try:
        plan = load(root/'PLAN.json'); check_plan(plan)
        freeze = load(root/'DESIGN_FREEZE.json'); freeze_sha = sha(root/'DESIGN_FREEZE.json')
        errors.extend(frozen_sources(root,freeze)); output['freeze_sha256'] = freeze_sha
        if binary is not None:
            output['binary_bytes_reverified'] = sha(binary) == freeze['binary_sha256']
            check(output['binary_bytes_reverified'],'Frozen binary mismatch')
        data, stats = source_data(root); output['source_data'] = stats
        oracle = integer_oracle(data[BASE_FILE],data[QUERY_FILE])
        output['official_groundtruth'] = check_groundtruth(data[GT_FILE],oracle,10000)
        check(output['official_groundtruth']['checks_passed'],'Official ground truth fails tie-aware check')
        campaign, inventory = load(capture/'CAMPAIGN.json'), load(capture/'INVENTORY.json')
        output['input_sha256'] = {'CAMPAIGN.json':sha(capture/'CAMPAIGN.json'),'INVENTORY.json':sha(capture/'INVENTORY.json')}
        check(campaign.get('schema_version') == 1,'Wrong campaign schema')
        check(campaign.get('plan_sha256') == sha(root/'PLAN.json') and campaign.get('freeze_sha256') == freeze_sha,'Campaign plan/freeze mismatch')
        check(campaign.get('source_changed') is False,'Campaign source changed')
        check(campaign.get('stop_reason') is None,'Campaign stopped early: '+str(campaign.get('stop_reason')))
        check(campaign.get('campaign_timeout_seconds') == 300 and finite(campaign.get('monotonic_duration_seconds')),'Campaign budget/duration invalid')
        check(utc_interval(campaign),'Campaign UTC interval invalid')
        gpu = inventory['hardware']['gpu_inventory']
        devices = gpu.get('devices',[])
        names = {d.get('model') for d in devices if isinstance(d,dict)}
        check(inventory['hardware'].get('platform') == 'Darwin' and gpu.get('status') == 'observed' and bool(names),'Mac GPU inventory unavailable')
        check(inventory.get('capacity_kind') == 'hardware_totals' and inventory.get('placement_ready') is False,'Inventory interpretation changed')
        recorded = campaign['profiles']
        if not isinstance(recorded,list): raise ValueError('Profiles must be a list')
        ids = [p.get('profile_id') for p in recorded]
        planned_ids = [p['profile_id'] for p in plan['profiles']]
        check(ids == planned_ids[:len(ids)],'Campaign profile order/duplicate/extra mismatch')
        unrun = [p for p in planned_ids if p not in ids]
        output['unrun_profile_ids'] = unrun
        check(campaign.get('unrun_profile_ids') == unrun,'Unrun profile accounting mismatch')
        check(not unrun and len(recorded) == 2,'Incomplete campaign')
        by_id = {p['profile_id']:p for p in recorded}
        previous_finish = None
        for profile in plan['profiles']:
            entry = by_id.get(profile['profile_id'])
            if entry is None:
                results.append(dict(profile,checks_passed=False,errors=['Profile unrun'],compared_distances=0,canonical_top10_positions_matched=0))
                continue
            local = []
            try:
                folder = capture/profile['folder']
                raw, execution = load(folder/'RAW.json'), load(folder/'EXECUTION.json')
                result = audit_profile(raw,folder/'distances.u32le',profile,plan,oracle,stats,names)
                for key,value in profile.items():
                    if entry.get(key) != value: local.append('Campaign profile metadata mismatch: '+key)
                    if key != 'folder' and execution.get(key) != value: local.append('Execution metadata mismatch: '+key)
                if entry.get('status') != 'completed' or entry.get('returncode') != 0: local.append('Campaign profile failed')
                if execution.get('returncode') != 0 or type(execution.get('returncode')) is not int or execution.get('process_status') != 'completed': local.append('Native process failed/incomplete')
                if execution.get('freeze_sha256') != freeze_sha or execution.get('source_changed') is not False: local.append('Execution source/freeze mismatch')
                if execution.get('raw_output_present') is not True or execution.get('raw_gate_passed') is not True: local.append('Execution raw-output gate failed')
                if execution.get('diagnostic_interrupted') is not False: local.append('Diagnostic interrupted')
                if not finite(execution.get('process_elapsed_seconds')): local.append('Invalid process duration')
                if not finite(execution.get('timeout_seconds'),1e-9) or execution['timeout_seconds'] > 90: local.append('Invalid process timeout')
                if not utc_interval(execution):
                    local.append('Invalid execution UTC interval')
                else:
                    started = datetime.fromisoformat(execution['started_utc'].replace('Z','+00:00'))
                    ended = datetime.fromisoformat(execution['finished_utc'].replace('Z','+00:00'))
                    if previous_finish is not None and started < previous_finish: local.append('Profiles overlap/reverse order')
                    previous_finish = ended
                command = execution.get('command',[])
                if (not isinstance(command,list) or len(command)!=7 or command[1]!='--data'
                        or command[3:6]!=['--batch-size',str(profile['batch_size']),'--output-dir']
                        or Path(command[2]).name!='data' or Path(command[6]).name!=profile['folder']):
                    local.append('Native command differs from fixed profile')
                result['power_sources'] = [power(execution.get(when,{}).get('batt')) for when in ('before','after')]
                result['input_sha256'] = {'RAW.json':sha(folder/'RAW.json'),'EXECUTION.json':sha(folder/'EXECUTION.json')}
                result['errors'].extend(local); result['checks_passed'] = not result['errors']
            except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
                result = dict(profile,checks_passed=False,errors=local+[type(exc).__name__+': '+str(exc)],
                              compared_distances=0,canonical_top10_positions_matched=0)
            results.append(result)
        check(sha(root/'DESIGN_FREEZE.json') == freeze_sha,'Freeze changed during audit')
        errors.extend(frozen_sources(root,freeze))
        output['compared_distances'] = sum(p.get('compared_distances',0) for p in results)
        output['canonical_top10_positions_matched'] = sum(p.get('canonical_top10_positions_matched',0) for p in results)
        output['checks_passed'] = not errors and len(results)==2 and all(p['checks_passed'] for p in results)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,tarfile.TarError) as exc:
        errors.append(type(exc).__name__+': '+str(exc))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--capture',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True,help='New JSON only; never overwritten')
    parser.add_argument('--binary',type=Path)
    args = parser.parse_args()
    if args.output.exists(): parser.error('Output already exists')
    result = analyze(args.root,args.capture,args.binary)
    with args.output.open('x') as handle:
        json.dump(result,handle,sort_keys=True,indent=2,allow_nan=False); handle.write('\n')
    print(json.dumps({'checks_passed':result['checks_passed'],'output':str(args.output)}))
    return 0 if result['checks_passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
