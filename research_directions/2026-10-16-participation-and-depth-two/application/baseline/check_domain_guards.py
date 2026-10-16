"""Fail-closed certificate-domain tests; no solver dependencies."""
import copy
import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from verify_floor_certificates import verify

here=Path(__file__).parent
path=next(iter(sorted(here.glob('floor-marginal-m2-levels3-theta1_1.json*'))))
raw=gzip.open(path,'rt').read() if str(path).endswith('.gz') else path.read_text()
original=json.loads(raw)
cases={
    'duplicate_profile': lambda d:d['all_profiles'].__setitem__(1,d['all_profiles'][0]),
    'missing_profile': lambda d:d['all_profiles'].pop(),
    'duplicate_level': lambda d:d['levels'].__setitem__(1,d['levels'][0]),
    'unsorted_levels': lambda d:d['levels'].reverse(),
    'wrong_dimension': lambda d:d['all_profiles'][0].append(0),
    'incorrect_count': lambda d:d.__setitem__('profiles',242),
    'out_of_domain': lambda d:d['all_profiles'][0].__setitem__(0,99),
    'unknown_normalizer': lambda d:d.__setitem__('normalizer','unrecognized'),
}
with TemporaryDirectory(prefix='floor-guard-',dir=here) as tmp:
    candidate=Path(tmp)/'bad.json'
    for label,mutate in cases.items():
        doc=copy.deepcopy(original);mutate(doc);candidate.write_text(json.dumps(doc))
        try:verify(candidate)
        except RuntimeError as exc:print(json.dumps({'case':label,'status':'REJECTED','reason':str(exc)}))
        else:raise RuntimeError('invalid certificate accepted: '+label)
