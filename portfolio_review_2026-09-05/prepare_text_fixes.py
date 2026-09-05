from pathlib import Path
import json

root=Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery')
out=Path(__file__).resolve().parent/'text_fixes'
changes=[]
def replace(rel,old,new):
    p=root/rel; text=p.read_text()
    if text.count(old)!=1: raise RuntimeError(f'Expected one target in {rel}')
    q=out/rel; q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(text.replace(old,new))
    changes.append(rel)

replace('coopgames/paper3/sections_leximin.tex',
'''the core; on convex games it is the constrained egalitarian solution of
\\citet{DuttaRay89}. Implementation (exact rational + float) in
\\texttt{src/leximin.py}, validated against those two coincidences.''',
'''the core. On singleton-normalized convex games it is the constrained
egalitarian solution of \\citet{DuttaRay89}. For a general convex game it is
that solution of $v^0$, translated by $m$; the two rules need not agree on
$v$ itself. Implementation (exact rational + float) in
\\texttt{src/leximin.py}.''')

replace('coopgames/paper5/assignment_comparison/pairs_and_triples.tex',
'has maximum greater than one, attained at a small positive feasible $q_0$.',
'has maximum greater than one, as witnessed by a small positive feasible $q_0$.')

replace('coopgames/paper5/SHARP_ASYMPTOTIC_GAP_PROGRAM.md',
'''O >= mu |supp(z)| >= mu T/M.
```

Indeed `min(x_i,z_i)>=mu` on `supp(z)` and
`T=sum_i z_i<=M|supp(z)|`.  Therefore `M<=Cn mu` would imply the universal
gap `2-rho>=2/(Cn)`.''',
'''O >= mu T/M.
```

Since `0<mu<=M`, `x_i>=mu`, and `0<=z_i<=M`, one has
`min(x_i,z_i)>=(mu/M) z_i` coordinatewise. Summing proves the bound.
The stronger support-cardinality step formerly printed here is false:
the Fibonacci segment with `m=2,r=4` has `mu=1/3`, full support of `z`,
and `O=8/3<3=mu |supp(z)|`. Therefore `M<=Cn mu` would imply the universal
gap `2-rho>=2/(Cn)`. Corrected in the portfolio audit of 2026-09-05.''')

replace('coopgames/paper5/SHARP_GAP_CHAMBER_REDUCTION.md',
'''PXC151 and does not supply an asymptotic bound.
''',
'''PXC151 and does not supply an asymptotic bound.

**Review update, 2026-09-05: not an established theorem.** The proof below
does not justify joint linearity with variable primal and dual certificates,
or the closed weak-polyhedral graph across strict non-forcing strata.
Consequently fixed-n attainment and rationality are not certified by this
note. See `../portfolio_review_2026-09-05/REVIEW.md` and its unrestricted
audit. The separate constant-two theorem does not depend on this candidate.
''')

replace('coopgames/paper5/PROTECTED_RESULTS_LEDGER.md',
'# Protected results ledger for the hybrid-overlap program\n',
'''# Protected results ledger for the hybrid-overlap program

**Current-status override — 2026-09-05.** This is a historical dependency
ledger. The old all-n hybrid-overlap target and a fixed-n upper bound matching
the balanced G family are false (PXC143–PXC146). Statements below calling
their universal selection/gluing step "open" describe the abandoned program,
not a live conjecture. Scoped conditional lemmas are retained. The unrestricted
first-order deficit is now proved to be 2; see `asymptotic_constant_two/`.
For assignment results and revised attribution see `assignment_comparison/`.
The current portfolio audit and identified errata are in
`../portfolio_review_2026-09-05/REVIEW.md`.
''')

replace('coopgames/paper6/README.md',
'''Twelve pages, one open TODO: prior-art positioning, marked in the introduction
for the lead's citation verification pass. The bibliography deliberately lists
only the three works actually cited, each carried over verbatim from paper4's
bibliography; nothing was reconstructed from memory.''',
'''Twelve pages. The earlier prior-art TODO was addressed by the citation pass
in commit `1061fc4c` (2026-08-09); the current manuscript contains that
positioning and an expanded bibliography. This is not external novelty
confirmation. The central characterization was reviewed again internally on
2026-09-05; see `../portfolio_review_2026-09-05/REVIEW.md` for the exact scope.''')

(out/'changed_files.json').write_text(json.dumps(changes,indent=2)+'\n')
print('\n'.join(changes))
