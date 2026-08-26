# Hostile external review packet — PXC144 (`H_7`) and PXC145 (n=8, n=9)

Review target: the PXC144 and PXC145 blocks in `paper5/divergence.tex` on
branch `cc/s7-sharp-frontier-20260825`, and the exact artifacts below.  No
external specialist has reviewed these results.

## Claimed results

1. **PXC144.**  `H_7`, the lower envelope of `A=(1,4,7,0,0,0,1)`,
   `B=(0,0,0,5,3,3,2)`, `C=(0,5,8,0,0,0,0)`, `D=(0,0,4,1,3,3,2)` (total 13),
   is exact, singleton-normalized and generator-minimal, with
   `Lmin=(1,3,5,1,1,1,1)`, `Lmax=(1,3,13,13,13,13,9)/5`, hence
   `rho=56/65=5/6+11/390` and `O/T=37/65<7/12`.  Therefore `s(7)>=56/65`.
2. **PXC145.**  Explicit exact singleton-normalized games at `n=8` (total 44,
   `rho=63/55`) and `n=9` (total 31, `rho=196/155`) exceed the formula values
   `2-8n/(n^2-(n mod 2))`, namely `1` and `11/10`.  They are the `m=2,3`
   members of the family `H_m` (PXC145a) whose closed forms are verified for
   `m<=4` (`m=4`: ten players, `rho=133/100>6/5`, outside the release replay)
   and are conjectural beyond.
3. The balanced two-generator family `G(p,k)` is therefore not extremal at
   `n=7,8,9`; the formula `s(n)=2-8n/(n^2-(n mod 2))` is false for these `n`
   (it is correct at `n=6` by Theorem `s6`, and `s(5)=1/2` separately).
4. Nothing is claimed about the sharp values `s(n)`, `n>=7`, nor about any
   upper bound.

## Files

- `paper5/divergence.tex` — PXC144a–c (with the eight-value hand proof) and PXC145a–c.
- `verifiers/divergence/verify_pxc144_h7_four_generator_counterexample.py` (+ JSON)
- `verifiers/divergence/verify_pxc144_h7_four_generator_counterexample_independent.py` (+ JSON)
- `verifiers/divergence/verify_pxc145_h8_h9_formula_failure.py` (+ JSON)
- `verifiers/divergence/verify_pxc145_h8_h9_formula_failure_independent.py` (+ JSON)
- `paper5/PROTECTED_RESULTS_LEDGER.md`, `paper5/MECHANISM_PRICE_PROGRAM.md` (§16–17)
- `paper5/PXC144_NOVELTY_AUDIT_20260826.md`

## Reproduction

From the repository root (each primary/independent pair must reproduce the
committed JSON byte for byte):

```bash
for name in pxc144_h7_four_generator_counterexample pxc145_h8_h9_formula_failure; do
  python3 verifiers/divergence/verify_${name}.py --output /tmp/${name}.json
  cmp verifiers/divergence/${name}.json /tmp/${name}.json
  python3 verifiers/divergence/verify_${name}_independent.py --output /tmp/${name}_independent.json
  cmp verifiers/divergence/${name}_independent.json /tmp/${name}_independent.json
done
bash paper5/verify_release.sh
```

The primary verifiers are LP-free (stdlib `fractions` only): they replay
explicit staged Farkas identities.  The independent verifiers recompute
both selectors from the coalition values with fresh Z3 optimization and
audit every stage by an active-tangent query; they share no code with the
primaries.

## Hostile questions

1. Verify from the four generators that `H_7` is exact and singleton-normalized,
   and that each three-generator sub-envelope is a different game.
2. Re-derive the eight coalition values in the hand proof and check every
   summation, including the halved identities that pin players 2 and 3 of the
   `Lmax` top.
3. Is the stage logic complete?  Each identity gives an upper (lower) bound on
   the stage value *and* forces one player once the others are held at the
   level; attainment by the displayed vector supplies the reverse direction and
   proves the non-forced players are genuinely free.  Confirm this proves the
   lexicographic optimum in both directions, including tie handling.
4. Recompute `rho` and `O/T` and the formula values at `n=7,8,9`.
5. Confirm that none of the eight- or nine-player games has a null player and
   that the nine-player game is not a mere null padding of the eight-player one
   (both split players carry positive `Lmin`).
6. Assess novelty separately from correctness (see the dated audit).  Do not
   infer sharp values; the packet supplies lower bounds only.
