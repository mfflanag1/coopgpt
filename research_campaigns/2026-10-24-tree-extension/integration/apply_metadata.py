from pathlib import Path
import json,hashlib,shutil
T=Path("/Users/maxf/.codex/visualizations/2026/09/04/01a06e8a-dcbb-7c81-9929-e72831a14ac8/research-campaigns/2026-10-24-tree-extension")
P=T/"integration/package"
C=Path("/Users/maxf/projects/economics-research/game-theory/coopgpt/paper5/coalition_withholding")
items=json.loads((T/"integration/FINAL_METADATA_GUARD.json").read_text())
for item in items:
 f=C/item["path"]; current=hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None
 assert current==item["expected"],"Concurrent modification: "+item["path"]
for item in items:
 dst=C/item["path"];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/item["path"],dst)
shutil.copyfile(P/"GRAPH_ADDITION_PROVENANCE.json",C/"GRAPH_ADDITION_PROVENANCE.json")
files=sorted(p for p in C.rglob("*") if p.is_file() and p.name!="SHA256SUMS" and "__pycache__" not in p.parts)
(C/"SHA256SUMS").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+str(p.relative_to(C))+"\n" for p in files))
print("Applied",len(items),"metadata/evidence files; regenerated",len(files),"file identities. No Git actions.")
