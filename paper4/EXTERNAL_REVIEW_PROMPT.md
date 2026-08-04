# Hostile review — one-packet obstruction and boundary phase theorem

Please review the concise standalone manuscript:

```text
paper4/threshold.pdf
paper4/threshold.tex
```

The long technical archive is `paper3/wrapper.pdf`, but the ten-page
`paper4` manuscript is intended to contain a complete human proof of the
central theorem without finite enumeration.

The revision adds a general theorem before the phase classification. At any
failed strict Lmin boundary, a normal-cone certificate gives one simultaneous
strict tight cover. Projection and a convex defect functional then select a
single lifted minimal balanced packet with positive rooted defect; mixtures
are unnecessary. The associated rooted identity gives an exact slack budget.

## Main claim

For a strict payoff boundary of `phi=Lmin(v)` in a singleton-normalized exact
game, let `m` be the number of cumulative poorer players and `h` the number of
richer players. A slack richer suffix exists exactly when

```text
m >= m_min(h),
m_min(1)=4,
m_min(2)=m_min(3)=3,
m_min(h)=2 for h>=4.
```

Every admitted pair is claimed to have an explicit integral indecomposable
lower-envelope realization.

## Questions to answer hostilely

1. Audit the strict richer-cover lemma from first principles. In particular,
   does the absence of a nonzero tangent direction whose poorer coordinates
   are all nonnegative imply, by a strict polyhedral alternative, a normal
   vector positive on every poorer coordinate and zero on every richer
   coordinate? Is the subsequent polar-cone sign convention correct?
2. Is the balanced-trace transport proof complete, especially the lift from
   a convex decomposition of rich traces back to original tight coalitions?
3. Audit the new one-packet theorem. Check convexity of
   `F(r)=1+(m-1)max(r)-sum(r)`, the Jensen direction, every coefficient in the
   rooted incidence identity, and the exactifier derivation of the slack
   budget. Does it genuinely eliminate mixtures for every failure? Is the
   claimed `|N|` bound on positive coalitions valid for degenerate vertices?
4. Search specifically for an equivalent Lmin-selected one-packet reduction
   in property-I, exact-balanced, semi-balanced-system, coherent-lower-
   probability, and minimal-balanced-collection literature. Treat the
   semi-balanced incidence inequality itself and the Studeny--Kratochvil
   complement-of-the-exceptional-set correspondence as prior art. Determine
   whether projection to a packet on the richer suffix is genuinely distinct.
5. Does exactifying a slack suffix force both positive and negative
   displacement coordinates on the poorer side, thereby excluding `m=1`?
6. Is the sacrifice-budget inequality correct, and does the three-case
   protector argument exclude every unique-richest boundary with `m<=3`?
7. In the two-poorer proof, is the rank-two exact-cover component
   classification complete? Check the half-integral poor loads and the
   alternating odd-cycle rounding carefully.
8. Does the exact-face overload contradiction really give
   `phi_d<=phi_a`, contrary to the strict payoff boundary?
9. Independently verify every row total, singleton zero, displayed coalition
   value, and progressive Lmin step for all three parametric constructions.
10. Check the added indecomposability proof for the internal-sacrifice family:
   does `p1` have the displayed positive pair worth with every player for all
   `m>=2,h>=4`?
11. Does the final case split cover every positive integer pair `(m,h)` once,
   with no hidden assumption that the poorer side is one payoff stratum?
12. Is exact partition at Lmin genuinely stronger than the known statement
    that exact games through four players are PES stable?
13. Search for the exact staircase or an equivalent boundary-cardinality
    theorem under exact-partition, egalitarian-core, minimal balanced
    collection, semi-balanced system, or exact-game terminology.

Treat as prior art: exact partition, its Lorenz consequence, Lmin/property I,
exact balancedness, semi-balanced facet inequalities, minimal balanced
collections, the full-set semi-balanced/minimal-balanced correspondence,
lower-envelope exact games, and the graph description of rank-two exact-cover
vertices. The candidate new content is the simultaneous Lmin normal cover,
richer-side one-packet selection, complete staircase, and realizing families.

## Exact reproduction

From `coopgames/`:

```bash
python src/verify_unique_richest_family.py \
  --max-players 12 --exact-lmin-through 7 --exact-lmax-through 6 \
  --output /tmp/unique-richest.json
cmp /tmp/unique-richest.json results/unique_richest_family.json

python src/verify_two_poorer_rich_family.py \
  --max-poorer-block 5 --max-rich-block 10 --exact-replay-m2-h4 \
  --output /tmp/two-poorer.json
cmp /tmp/two-poorer.json results/two_poorer_rich_family.json

python src/verify_three_poorer_boundary_family.py \
  --max-poorer-side 6 --max-richer-suffix 6 \
  --exact-replay-through-players 6 \
  --output /tmp/three-poorer.json
cmp /tmp/three-poorer.json results/three_poorer_boundary_family.json

cd paper4
pdflatex -interaction=nonstopmode -halt-on-error threshold.tex
pdflatex -interaction=nonstopmode -halt-on-error threshold.tex
```

The programs are bug audits, not proof evidence. Please rederive the symbolic
arguments and implement at least the smallest `(m,h)=(4,1),(3,2),(2,4)`
instances independently.

Return separate verdicts for:

1. simultaneous normal-cover theorem;
2. one-packet selection and rooted slack budget;
3. lower-bound transport theorem;
4. unique-richest exclusion;
5. two-poorer exclusion;
6. each of the three constructions;
7. exhaustive phase classification;
8. novelty and field significance.

Use `verified`, `verified with qualifications`, or `not verified`. Classify
every issue as fatal, repairable, or expository and cite exact file lines.
