"""Score saved primary and blind-inventory responses offline, without repair."""
import argparse
import json
from pathlib import Path

from contract import summarize, validate_inputs


def response_text(path, request_id):
    """Read exact response fragments from one run_trace capture; absent is None.

    run_trace stores requests[0].chunks in received order. Each chunk's data is
    the original streamed API object; only its optional response string is
    answer text. Prompts, thinking, final metadata, and cached summaries are not
    answers. A missing response field contributes the empty string.
    """
    path = Path(path)
    if not path.exists():
        return None
    raw = json.loads(path.read_text())
    rows = raw.get('requests') if type(raw) is dict else None
    if type(rows) is not list or len(rows) != 1 or type(rows[0]) is not dict:
        raise ValueError(f'{path}: expected exactly one raw request row')
    row = rows[0]
    if row.get('request_id') != request_id or type(row.get('chunks')) is not list:
        raise ValueError(f'{path}: request ID or chunks differ from raw capture contract')
    fragments = []
    for chunk in row['chunks']:
        data = chunk.get('data') if type(chunk) is dict else None
        if type(data) is not dict or type(data.get('response', '')) is not str:
            raise ValueError(f'{path}: raw response fragment is not a string')
        fragments.append(data.get('response', ''))
    return ''.join(fragments)


def main(base, capture):
    cases, controls = validate_inputs(Path(base))
    folder = Path(capture) / 'collection'
    answers = {}
    for phase, prefix in (('primary', 'p_'), ('inventory', 'i_')):
        by_case = {}
        for case in cases:
            case_id = case['request_id']
            request_id = prefix + case_id
            value = response_text(folder / (request_id + '.json'), request_id)
            if value is not None:
                by_case[case_id] = value
        answers[phase] = by_case
    # Both maps use bare case IDs. Controls reuse these inventories offline.
    return summarize(cases, controls, answers['primary'], answers['inventory'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path, help='frozen study directory')
    parser.add_argument('capture', type=Path, help='saved capture directory containing collection/')
    parser.add_argument('--output', type=Path, required=True, help='destination SUMMARY.json')
    args = parser.parse_args()
    result = main(args.base, args.capture)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('natural', 'controlled', 'inventories')}, sort_keys=True))
