"""Read-only placement planning and verification; never reserves or dispatches jobs."""
import argparse
import json
from pathlib import Path
from solver import solve
from verifier import strict_loads, verify_plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    planner = sub.add_parser('solve')
    planner.add_argument('manifest', type=Path)
    checker = sub.add_parser('verify')
    checker.add_argument('manifest', type=Path)
    checker.add_argument('plan', type=Path)
    args = parser.parse_args()
    try:
        manifest = strict_loads(args.manifest.read_text())
        result = solve(manifest) if args.command == 'solve' else verify_plan(manifest, strict_loads(args.plan.read_text()))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if args.command == 'solve' or result['valid'] else 1
    except (ValueError, OSError) as error:
        print(json.dumps({'error': str(error)}, sort_keys=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
