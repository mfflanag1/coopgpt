# Hostile review — complete boundary phase theorem

Please review the concise standalone manuscript:

```text
paper4/threshold.pdf
paper4/threshold.tex
```

The long technical archive is `paper3/wrapper.pdf`, but the eight-page
`paper4` manuscript is intended to contain a complete human proof of the
central theorem without finite enumeration.

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

1. Does the strict richer-cover lemma follow from the established
   transfer-blocking/property-I characterization with the orientation and
   strict inequalities used here?
2. Is the balanced-trace transport proof complete, especially the lift from
   a convex decomposition of rich traces back to original tight coalitions?
3. Does exactifying a slack suffix force both positive and negative
   displacement coordinates on the poorer side, thereby excluding `m=1`?
4. Is the sacrifice-budget inequality correct, and does the three-case
   protector argument exclude every unique-richest boundary with `m<=3`?
5. In the two-poorer proof, is the rank-two exact-cover component
   classification complete? Check the half-integral poor loads and the
   alternating odd-cycle rounding carefully.
6. Does the exact-face overload contradiction really give
   `phi_d<=phi_a`, contrary to the strict payoff boundary?
7. Independently verify every row total, singleton zero, displayed coalition
   value, and progressive Lmin step for all three parametric constructions.
8. Check the added indecomposability proof for the internal-sacrifice family:
   does `p1` have the displayed positive pair worth with every player for all
   `m>=2,h>=4`?
9. Does the final case split cover every positive integer pair `(m,h)` once,
   with no hidden assumption that the poorer side is one payoff stratum?
10. Is exact partition at Lmin genuinely stronger than the known statement
    that exact games through four players are PES stable?
11. Search for the exact staircase or an equivalent boundary-cardinality
    theorem under exact-partition, egalitarian-core, minimal balanced
    collection, semi-balanced system, or exact-game terminology.

Treat as prior art: exact partition, its Lorenz consequence, Lmin/property I,
exact balancedness, minimal balanced collections, lower-envelope exact games,
and the graph description of rank-two exact-cover vertices. The candidate
new content is only the Lmin-selected transport bridge, the complete
staircase, and the realizing families.

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

1. lower-bound transport theorem;
2. unique-richest exclusion;
3. two-poorer exclusion;
4. each of the three constructions;
5. exhaustive phase classification;
6. novelty and field significance.

Use `verified`, `verified with qualifications`, or `not verified`. Classify
every issue as fatal, repairable, or expository and cite exact file lines.
