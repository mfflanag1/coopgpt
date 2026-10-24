#!/usr/bin/env python3
"""Rebuild the standalone manuscript from the maintained editorial fragments."""
from pathlib import Path
P=Path(__file__).resolve().parent
front=(P/'source/frontmatter.tex').read_text()
core=(P/'source/core.tex').read_text()
model,rest=core.split(r'\section{Sparse production:',1)
body,discussion=rest.split(r'\section{Interpretation, scope and remaining questions}',1)
text=(front+'\n'+model+'\n'+(P/'source/dimension_frontier.tex').read_text()
      +'\n'+r'\section{Sparse production:'+body+'\n'
      +(P/'source/graph_path.tex').read_text()+'\n'
      +(P/'source/graph_recursion_obstruction.tex').read_text()+'\n'
      +r'\section{Interpretation, scope and remaining questions}'+discussion
      +'\n'+r'\appendix'+'\n'
      +(P/'source/arity_appendix.tex').read_text()+'\n'
      +(P/'source/references.tex').read_text()+'\n'+r'\end{document}'+'\n')
(P/'manuscript.tex').write_text(text)
print('Rebuilt manuscript.tex from source fragments.')
