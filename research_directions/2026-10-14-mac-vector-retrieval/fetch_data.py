"""Reacquire the pinned CC0 archive and exact three input files into a NEW directory."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time
from urllib.request import urlopen


def fetch(output):
    root=Path(__file__).resolve().parent
    manifest=json.loads((root/'DATA_MANIFEST.json').read_text())
    output.mkdir(exist_ok=False)
    archive=output/'siftsmall.tar.gz';tick=time.monotonic();size=0;h=hashlib.sha256()
    with urlopen(manifest['archive_url'],timeout=20) as response,archive.open('xb') as target:
        while True:
            if time.monotonic()-tick>120:raise TimeoutError('120-second read-loop budget exceeded')
            chunk=response.read(65536)
            if not chunk:break
            size+=len(chunk)
            if size>20_000_000:raise ValueError('Archive exceeds20MB bound')
            target.write(chunk);h.update(chunk)
    if size!=manifest['archive_bytes'] or h.hexdigest()!=manifest['archive_sha256']:
        raise ValueError('Downloaded archive differs from frozen source')
    if hashlib.md5(archive.read_bytes()).hexdigest()!=manifest['archive_md5']:
        raise ValueError('Original publisher MD5 mismatch')
    (output/'data').mkdir()
    with tarfile.open(archive,'r:gz') as tar:
        for path,record in manifest['files'].items():
            name=Path(path).name
            if path!='data/'+name:raise ValueError('Invalid fixed member path')
            member=tar.getmember('siftsmall/'+name)
            if not member.isfile() or member.size!=record['bytes']:raise ValueError('Invalid archive member')
            data=tar.extractfile(member).read()
            if hashlib.sha256(data).hexdigest()!=record['sha256']:raise ValueError('Input hash mismatch')
            with (output/path).open('xb') as target:target.write(data)
    return {'archive_sha256':h.hexdigest(),'bytes':size,'elapsed_seconds':time.monotonic()-tick}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(fetch(args.output.resolve())))
