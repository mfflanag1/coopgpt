# Hostile external review — universal Lmin slack ascent

Please review the proposed dimension-free theorem in the private repository
`mfflanag1/counterexample-hunt`. Treat it as unvalidated research. Report
fatal errors first, then repairable gaps, then novelty risks. Do not infer
correctness from the exact verifiers.

## Principal claim

For an exact TU game `v`, let `phi=Lmin(v)`. At any strict payoff boundary,
write `H` for the richer suffix and `L=N\H` for the poorer side. If `H` is
slack, then some `i in L` satisfies

```text
s_phi(H union {i}) > s_phi(H),
v(H union {i})-v(H) < phi_i.
```

Equivalently, no slack Lmin suffix is an upper local maximum of the
coalition-slack function. The statement is claimed for every dimension and
for both pure-star and trace-coupled failures.

## Exact paths

- manuscript theorem and proof:
  `coopgames/paper3/sections_leximin.tex`, labels
  `thm:lx-face-ascent-geometry`,
  `cor:lx-universal-lmin-slack-ascent`;
- general convex-geometric proof:
  `coopgames/paper3/LEXIMIN_FACE_ASCENT_GEOMETRY.md`;
- dedicated geometry review prompt:
  `coopgames/paper3/LEXIMIN_FACE_ASCENT_EXTERNAL_REVIEW_PROMPT.md`;
- standalone proof:
  `coopgames/paper3/UNIVERSAL_LMIN_SLACK_ASCENT.md`;
- quantitative strict-cover refinement:
  `coopgames/paper3/sections_leximin.tex`, label
  `thm:lx-strict-cover-slack-transfer`;
- geometry audit:
  `coopgames/src/verify_leximin_face_ascent_geometry.py` and
  `coopgames/results/leximin_face_ascent_geometry.json`;
- exact arithmetic audit:
  `coopgames/src/verify_two_sided_trace_coupling.py` and
  `coopgames/results/two_sided_trace_coupling.json`;
- prior-art audit:
  `coopgames/paper3/EXACT_PARTITION_CITATION_NETWORK_AUDIT.md`;
- compiled paper:
  `coopgames/paper3/wrapper.pdf`.

## Proof to audit independently

1. In a compact convex efficient allocation set, exactify the richer face at
   `z`, put `Delta=z-phi`, and verify

   ```text
   Delta(H)=-s, Delta(L)=s.
   ```

2. Check the cover-free strict step: if every poorer `Delta_i>=0`, does a
   sufficiently short segment preserve the strict payoff boundary and
   lexicographically improve the increasingly sorted vector, including all
   tied-stratum cases? Confirm that the selected negative displacement yields
   `s_phi(H union {i})>=s-Delta_i>s` and that the coalition is proper because
   some distinct poorer player gains.
3. Independently verify the positive-variation identity

   ```text
   max_(H subseteq C subseteq N) sigma_phi(C)
    = max_(z in K) sum_(i in L)(z_i-phi_i)_+,
   ```

   its terminal sign-cell correspondence, the treatment of zero
   displacements, the strict variation gap, and the core-vertex conclusion.
4. Confirm that exactness identifies face deficit with ordinary coalition
   slack for every coalition, and that no strict-cover hypothesis is hidden
   in the existence theorem.
5. Separately check the quantitative canonical completion with

   ```text
   b=max_i c_i, d_i=b-c_i,
   delta=1-b+sum_i d_i,
   ```

   including every coordinate, the `b=0` normalization, and the direction of
   the exact-balancedness inequality

   ```text
   delta s_phi(H) <= sum_i d_i s_phi(H union {i}).
   ```

6. Verify the quantitative factor
   `1+(1-b)/sum_i d_i>1`, and the sharper two-poorer packet factor
   `(1-r_a)/(r_b-r_a)`.
7. Recompute the three saturated examples from their defining exact games:
   the five-player pure-star factor `2`, the three-column factor `2`, and the
   four-co-singleton factor `3/2`. Confirm that the script derives coalition
   values rather than merely comparing hard-coded constants.

## Novelty questions

Search exact games, semi-balanced systems, exact-partition games,
egalitarian/lexmin solution theory, core-slack functions, and cooperative
game marginality for an equivalent result. The semi-balanced inequality and
the qualitative property-I characterization of Lmin are prior art and must
not be claimed as new. Assess novelty only for their combination into:

- cover-free leximin face ascent for arbitrary compact convex efficient sets;
- positive-variation duality and the terminal sign-cell correspondence;
- universal strict slack ascent at every failed exact-game Lmin boundary;
- the adjacent-edge marginal-deficit witness;
- the separately derived quantitative canonical-completion factor.

Please conclude with one of:

- correct as written;
- correct after explicitly named repairs;
- false, identifying the first invalid equation or implication.

Then separately rate likely significance as specialized lemma, strong field
result, or potential major result, conditional on novelty.
