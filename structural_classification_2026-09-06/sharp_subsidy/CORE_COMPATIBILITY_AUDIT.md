# Internal completion audit: uniform core-compatibility bound

2026-09-08 UTC. The exploratory phase began at 03:05:49 UTC, with a two-hour
checkpoint at 05:05:49 UTC. The mathematical target was reached and internally
verified before that checkpoint. No follow-on research campaign is started here.

## Result and scope

CORE_COMPATIBILITY_UPPER.md supplies a complete conventional argument for

    S_3 <= 39999/100000 = 2/5 - 1/100000,

retaining strict three-sector nonnegative pair additivity, equal finite sector
sizes, positive ordinary matching worth, nonempty original entire core, and
floors equal to one third of each actual ORIGINAL core maximum. The established
one-third lower sequence remains unchanged. This proves a uniform improvement,
not the sharp constant and not a field-level breakthrough.

## Load-bearing audit

1. **Actual ideals and quantifiers.** Every H_i is attained in its own compact
   original core. No simultaneous maximizer is required. The three y^s in the
   proof are averages of selected original attaining witnesses. They are core
   points by convexity. Nothing replaces H_i by a marginal contribution.

2. **Local affine theorem.** The explicit six-row table avoids its excluded
   player, gives every other player load at most 1/3, and covers P once plus
   17/18 of each pair at the other two diagonal labels. These facts directly
   prove J<=T/18+(17/18)d_0. The independent full-team checker uses all 27
   triples and does not import the sector-minimum core code. Its rational dual
   has no residual correction. The compressed-core zero-boundary certificate
   separately agrees with the coefficient 17/18.

3. **Selective cloning.** Each internal label gets exactly its P-degree copies.
   Tight copied diagonal teams and two-way same-sector swaps prove equality of
   copied payoffs in every copied core point. Grand worth increases by 2D-D_2.
   Unmatched multiplicities increase by k_j-1 for EVERY sector coordinate.
   Thus J' >= J-2Q/3. The finite combinatorial audit checks these counts, including
   repeated labels and degree-two labels.

4. **Component restriction direction.** Sparsification expands the core and
   preserves diagonal/P worth. Restriction to a component gives a local core
   point at its diagonal total; therefore local ideals are at least global
   copied ideals. The argument needs only J'<=sum local J, not equality or a
   product-core assertion. Zero-total components have zero pair worths and ideals.

5. **Value-weighted graph bound.** In every proper threshold subset of internal
   labels, each component has at least one outgoing incidence. Euler counting
   retains cycle rank with its correct negative sign. Integrating yields
   B_all<=2D-D_2+minimum internal worth. It treats repeated incidences as edges
   and does not discard cycles or assume uniform weights. The minimum term
   cannot be omitted, as the two-team control shows.

6. **Master inequality.** Three valid linear bounds are combined with positive
   weights 26/47,333/799,24/799. Exact arithmetic cancels D/T and B_3/T and leaves
   a nonpositive degree-two-worth coefficient. The resulting bound is
   R<=37/94+(61/47)Q/T+(37/94)tau. The exact-real counterexample query is UNSAT.

7. **Witness slack and degree-two concentration.** The old packing supplies
   nonnegative capacity, coalition, and pair excess slack totaling 3gT. Near
   its ceiling, every sector's positive extra transfer is shared equally over
   unmatched leaf rows. At a donor's other two sector players the load is at
   most one minus the donor reduction, also when that donor has degree two.
   This gives Q/T<=60g without assuming degree-two value is small. Direct
   checks exercise 608 degree-two and 2,752 degree-three donor coordinates.

8. **Uniform constants and original market return.** Full-domain scalar checks
   give Delta_s/Gamma>=1/4 and |I|/h>=1/3 for g<=1/100000. The existing finite
   bound gives 1/h<=60g, hence tau<=180g. Substitution forces
   g>=3/70370>1/100000. Rational packing replication and positive component
   selection then give the bound for every original market, including real
   pair values; rationality of those values is not assumed.

## Executed verification

The complete `build.sh --smt` run finished with exit code 0. BUILD.log retains
its output. New checks include:

- four rational fixed-support primal/dual intervals, 12,891,756 exact original
  team checks, and three all-internal-team branch calibrations;
- an exact all-weight zero-label module maximum of 1/18;
- an independently reconstructed 162-row, 66-variable full-team affine dual;
- 768 exhaustively listed small connected supports and six additional supports,
  with 4,737 weighted incidence checks and the donor-load checks above;
- five exact-real counterexample queries returning UNSAT and a widened-range
  positive control returning SAT. Unknown or damaged certificates fail closed.

The finite tests support specified steps. They are not substitutes for the
all-size conventional proof. Five additional full-core LP searches attacked
the master inequality numerically, including a repeated-label unicycle and a
degree-two tree. They found no violation and are recorded only as non-exhaustive
numerical evidence in discovery/core_slack_discovery.zip.

One larger synthesis reached its 45-second solver limit and remains
inconclusive. An initial rational dual reconstruction failed exact residual
checks; the four supporting finite intervals explicitly pay those residuals.
The final load-bearing affine-module dual needs no such correction.

## Review, priority and completion limits

CORE_COMPATIBILITY_SOURCE_AUDIT.md records free-primary-source comparisons and
separates established cost-of-stability, priority, core-cover, copying and LP
ingredients from the proposed quantitative combination. It does not establish
novelty or resolve previously inaccessible originals. No paid source or outreach
was used.

The preliminary Claude review timed out. A fresh `claude auth status` returned
loggedIn=false, authMethod=none. The final proof has a prepared review packet,
not a completed independent-model review. Independent specialist assessment
remains unavailable and is not counted as verification.

The active goal's requested conventional-proof outcome has been supplied, with
an explicit epsilon and reproducible certificates. The broader sharp-constant
problem, priority confirmation, external review and field-level significance
remain unresolved. This completion does not authorize a new campaign or claim
a published breakthrough.
