#!/usr/bin/env python3
"""Re-extract the one frozen post-result case; never modifies the supplied archive."""
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path
ACCESSION="0001450011-25-000308"
EXPECTED="08b90e310da506ae46e8a5b276022861808d61d56ce434ce310f52f31f608ca7"
def main():
    a=argparse.ArgumentParser();a.add_argument("archive",type=Path);a.add_argument("--output",required=True,type=Path);args=a.parse_args()
    if args.output.exists():raise FileExistsError("Use a fresh output path")
    h=hashlib.sha256()
    with args.archive.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    if h.hexdigest()!=EXPECTED:raise ValueError("Not the frozen archive")
    out={}
    with zipfile.ZipFile(args.archive) as z:
        def rows(name):
            with z.open(name) as f:
                yield from csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig"),delimiter="\t")
        for name in ["FUND_REPORTED_INFO.tsv","FUND_REPORTED_HOLDING.tsv"]:
            out[name]=[r for r in rows(name) if r["ACCESSION_NUMBER"]==ACCESSION]
        if len(out["FUND_REPORTED_INFO.tsv"])!=1:raise ValueError("Fund key not unique")
        ids={r["HOLDING_ID"] for r in out["FUND_REPORTED_HOLDING.tsv"]}
        if len(ids)!=len(out["FUND_REPORTED_HOLDING.tsv"]):raise ValueError("Holding key not unique")
        out["DEBT_SECURITY.tsv"]=[r for r in rows("DEBT_SECURITY.tsv") if r["HOLDING_ID"] in ids]
    args.output.write_text(json.dumps(out,indent=2)+"\n")
    print({k:len(v) for k,v in out.items()})
if __name__=="__main__":main()
