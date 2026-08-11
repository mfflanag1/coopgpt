# Specialist novelty sign-off packet: six-player Lmin--Lmax theorem

Date prepared: 2026-08-10

This packet asks an external cooperative-game theorist to determine whether an
equivalent result is already known.  It is not itself a novelty certificate.
The repository authors and computational agents must not fill in the final
specialist verdict on the reviewer's behalf.

## Result to compare with the literature

For a finite TU game `v`, let `Lmin(v)` be the core allocation whose increasing
payoff vector is lexicographically maximal and let `Lmax(v)` be the core
allocation whose decreasing payoff vector is lexicographically minimal.  On
singleton-normalized exact games (`v({i})=0`) define

```text
s(n) = sup ||Lmin(v)-Lmax(v)||_1 / v(N),
```

over nonzero `n`-player games in that domain.  The candidate theorem is

```text
s(6) = 2/3.
```

The companion classification currently gives `s(n)=0` for `n<=4`, `s(5)=1/2`,
an explicit sharp six-player family and equality profiles, and examples whose
ratios approach `2` as the player count grows.  The novelty question is not
whether leximin, leximax, Lorenz-stable allocations, exact games, or exact-cone
facets are known separately.  It is whether a prior theorem, after an explicit
translation, implies this fixed-dimensional separation statement or its
exchange/blocker mechanism.

Review branch: `codex/fixed-n-handover-facets`

Baseline reviewed state when this packet was prepared: `410acdd` or later.
The reviewer should record the full commit SHA actually inspected.

## Read in this order

```text
coopgames/paper5/S6_LITERATURE_NOVELTY_AUDIT.md
coopgames/paper5/S6_EXTERNAL_RECONSTRUCTION_PACKET.md
coopgames/paper5/S6_DIRECT_EXCHANGE_BOUND.md
coopgames/paper5/paper.tex
coopgames/paper5/paper.pdf
coopgames/MATHSCINET_CHECKLIST.md
```

Correctness review and novelty review are logically separate.  A reviewer may
answer the novelty question without endorsing the proof, but should state that
limitation explicitly.

## What counts as an equivalent prior result

Flag a collision if a prior source proves any of the following, even with
different notation:

1. the sharp normalized `L1` distance between increasing-lex-optimal and
   decreasing-lex-optimal points of every six-dimensional exact-game core;
2. the exact values `0, 1/2, 2/3` at player counts at most six;
3. a dimension-free theorem that specializes immediately to the `2/3` bound;
4. an exchange, facet, majorization, or credal-set theorem that implies the
   singleton-exactness blocker used in the proof with no new substantive
   lemma; or
5. an equivalent equality classification under strategic equivalence,
   anti-duality, exactification, or coherent-lower-probability terminology.

Mere definitions, algorithms for computing the two selectors, examples where
they differ, axiomatizations, exact-cone membership tests, or results confined
to convex/two-bound/Owen-set cores are neighboring prior art, not collisions.

## Closest checked results and missing implication

| Source line | What it proves | Missing step needed to subsume this theorem |
|---|---|---|
| Arin--Iñarra; Arin--Kuipers--Vermeulen | Lorenz-stable, `Lmin`, `Lmax`, and egalitarian-core foundations | No fixed-dimensional distance extremum |
| Dietzenbacher--Yanovskaya | Antiduality and exact-partition structure | No quantitative full-exact-domain bound |
| Biswas et al.; Llerena--Mauri | Small-player large-core boundary and exact-partition coincidence | Stops before the six-player separation problem |
| Studený--Kratochvíl | Facets of the exact-game cone via indecomposable semi-balanced systems | No theorem about the relative position of two selected core points |
| Frank--Murota | Dec-min/inc-max structure on base-polyhedra and M-convex sets | General exact-game cores are not directly base-polyhedra unless convex |
| Schoot Uiterkamp | Translated least-majorization characterizes base-polyhedra/convex games | Applies to all translations and the convex boundary, not two selectors on arbitrary exact cores |
| Gong--Dietzenbacher--Peters | Clipped egalitarian point on two-bound cores | The two selectors coincide there; general exact cores are not two-bound |
| Izquierdo--Montes--Rafels | Lorenz-monotonic schemes and a convexity characterization | Allocations vary across subgames; no `Lmin`--`Lmax` distance |
| Vazirani; Gangam et al. | Leximin/leximax algorithms and complexity on combinatorial cores/Owen sets | No normalized distance or exact-game supremum |
| Coherent-lower-probability literature checked | Credal/core representations, coherence, extreme rays and normal fans | No located opposing-selector separation theorem |

## Search obligations for the specialist

Please search at least the following channels, recording databases and dates:

- MathSciNet or zbMATH review text under MSC 91A12;
- Web of Science, Scopus, or a comparable citation index for papers citing
  Arin--Kuipers--Vermeulen (2003, 2008), Dietzenbacher--Yanovskaya (2020), and
  Studený--Kratochvíl (2022);
- current working papers and conference versions using `leximin core`,
  `leximax core`, `Lorenz stable`, `exact partition`, `semi-balanced`,
  `least-majorized`, `increasingly maximal`, `decreasingly minimal`, and
  `coherent lower probability`; and
- literature known personally to the reviewer under terminology not covered
  above.

The detailed subscription queries are in `coopgames/MATHSCINET_CHECKLIST.md`.
Please identify any unsearched language, database, or author network that
materially limits the opinion.

## Questions requiring an explicit answer

1. Is an equivalent theorem already known?  If yes, give the exact citation,
   theorem number, and a complete translation of hypotheses and conclusion.
2. Does any known base-polyhedron or majorization theorem cover nonconvex exact
   games while preserving both selectors and the normalized `L1` metric?
3. Does exact-partition, antiduality, large-core, two-bound-core, or
   exact-core-bound theory imply the six-player inequality?
4. Can exact-cone facet theory derive the singleton-exactness exchange blocker
   without a new substantive argument?
5. Is there an equivalent result in coherent-lower-probability language?
6. What narrower attribution or claim wording is required even if no
   equivalent theorem is found?

## Reviewer verdict form

```text
Reviewer name:
Institution / relevant expertise:
Date:
Commit SHA inspected:
Databases and citation networks searched:
Languages / literatures covered:

[ ] Equivalent prior theorem located.
    Citation and theorem number:
    Explicit translation:

[ ] No equivalent result located within the search scope stated above.
    Closest prior result:
    Why it does not imply the candidate theorem:

[ ] Novelty remains indeterminate.
    Missing source, terminology, or expertise:

Permissible manuscript wording:

Correctness reviewed separately?  yes / no / partially
If yes, point to the separate correctness report:
```

The desired external conclusion, if justified, is narrowly phrased:

> I located no equivalent prior result after the search described above.

That statement is stronger and more auditable than an undocumented assertion
that the theorem is “known to be new,” but it is not a universal guarantee
that no obscure or unpublished equivalent exists.

## Suggested expertise coverage

One reviewer deeply familiar with the Arin--Iñarra--Kuipers--Vermeulen and
Dietzenbacher egalitarian-core line is the minimum useful check.  Because the
proof also touches the exact cone and majorization, a stronger process uses a
second reader familiar with Studený--Kratochvíl exact-cone theory or with
Frank--Murota/base-polyhedron majorization.  These are expertise descriptions,
not claims that any named author has reviewed or endorsed the work.

Plausible first readers, based solely on the public authorship record, include
Bas Dietzenbacher for the recent `Lmin`/`Lmax`, exact-partition, and core-bound
line; Javier Arin, Jeroen Kuipers, or Dries Vermeulen for the foundational
egalitarian-selector line; and Milan Studený or Václav Kratochvíl for the exact
cone.  Martijn Schoot Uiterkamp is a useful adjacent reader for the strongest
majorization/base-polyhedron transfer.  Listing a person here is not evidence
of contact, willingness to review, or endorsement.

## Short outreach text

```text
I am seeking a narrowly scoped novelty opinion on a candidate cooperative-game
theorem, not a general endorsement.  For singleton-normalized exact TU games,
the manuscript claims that the normalized L1 separation between the Lmin and
Lmax core selections has sharp six-player supremum 2/3 (with the small-n
values and equality cases also classified).

Would you review the novelty packet on branch codex/fixed-n-handover-facets,
record the exact commit inspected, and state either (i) an equivalent prior
theorem with an explicit translation, (ii) that no equivalent was located
within your stated search scope, or (iii) that novelty remains indeterminate?

Start here:
coopgames/paper5/S6_SPECIALIST_NOVELTY_SIGNOFF.md
coopgames/paper5/S6_LITERATURE_NOVELTY_AUDIT.md
coopgames/paper5/S6_EXTERNAL_RECONSTRUCTION_PACKET.md

Please keep correctness and novelty as separate verdicts.  In particular,
please test exact-partition/antiduality, exact-cone facets, two-bound cores,
base-polyhedron majorization, and coherent-lower-probability translations.
```
