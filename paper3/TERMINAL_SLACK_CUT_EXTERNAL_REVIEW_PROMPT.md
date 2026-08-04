# Hostile external review request: terminal slack-cut theorem

Please review the candidate theorem at commit/branch supplied with this
packet as if recommending rejection unless every step is correct and the
literature positioning is defensible.

## Primary paths

- `coopgames/paper3/TERMINAL_SLACK_CUT_THEOREM.md`
- `coopgames/paper3/sections_leximin.tex`
- `coopgames/paper3/UNIVERSAL_LMIN_SLACK_ASCENT.md`
- `coopgames/src/verify_terminal_slack_cut.py`
- `coopgames/results/terminal_slack_cut.json`
- `coopgames/paper3/wrapper.pdf`

## Reproduction

From `coopgames/` run:

```bash
python src/verify_terminal_slack_cut.py --output /tmp/terminal.json
cmp /tmp/terminal.json results/terminal_slack_cut.json
cd paper3
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
```

## Questions that must be answered

1. Does interval maximality give both marginal inequalities with the stated
   directions?
2. Does exactifying `C` force `Delta_D<=0`, `Delta_E>=0`, and
   `Delta(E)=s_phi(C)` for every exactifier, rather than merely for a selected
   witness?
3. Is the deficit-weighted transport identity valid for every normalized
   strict Lmin cover of the original suffix `H`?
4. Is the payoff-inversion step a valid consequence of leximin optimality
   when there are tied strata?  Please write out any missing sorted-vector
   argument or give a counterexample.
5. Does the singleton bound
   `q_E s_phi(C) <= sum_(d in D)q_d s_phi({d})` follow with no hidden
   normalization assumption, and are its equality conditions stated
   cautiously enough?
6. Is an equivalent terminal-cut, punctured-suffix, or sign-separated
   exact-face theorem already present in the exact-game, egalitarian-solution,
   Lorenz-core, or semi-balanced-system literature?
7. Is the theorem materially stronger than the universal one-edge ascent
   result, or is it an immediate reformulation that should be presented only
   as a corollary?
8. Which additional hypothesis, if any, would make the terminal inversion
   rigid enough to classify all failures?

Do not treat the verifier, the three saturated examples, or successful PDF
compilation as independent proof evidence.  Do not describe novelty or
field-level significance as established without a specialist literature
comparison.
