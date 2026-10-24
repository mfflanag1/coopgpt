from pathlib import Path
import hashlib,json,shutil
T=Path("/Users/maxf/.codex/visualizations/2026/09/04/01a06e8a-dcbb-7c81-9929-e72831a14ac8/research-campaigns/2026-10-24-tree-extension")
P=T/"integration/package"
C=Path("/Users/maxf/projects/economics-research/game-theory/coopgpt/paper5/coalition_withholding")
for item in json.loads((T/"integration/BASELINE.json").read_text()):
 assert hashlib.sha256((C/item["path"]).read_bytes()).hexdigest()==item["sha256"],"Canonical file changed since snapshot: "+item["path"]
files=["manuscript.tex","specialist_brief.tex","assemble.py","README.txt","OPEN_REVIEW_REQUEST.txt","source/frontmatter.tex","source/core.tex","source/references.tex","source/graph_path.tex","source/graph_recursion_obstruction.tex","review/PRIORITY_MATRIX.txt","review/GRAPH_SOURCE_STRUCTURE.json"]
files += [str(p.relative_to(P)) for p in (P/"evidence/graph").rglob("*") if p.is_file()]
for rel in files:
 src=P/rel;dst=C/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
(T/"integration/APPLIED_SOURCE_FILES.json").write_text(json.dumps([{"path":r,"sha256":hashlib.sha256((C/r).read_bytes()).hexdigest()} for r in files],indent=2)+"\n")
print("Applied",len(files),"scoped source/review files to the existing coalition paper; baseline hashes verified.")
