Exact lower-bound lane: compact reviewed artifacts
Campaign15 October2026. This package contains selected results, not all raw
LP searches. Nothing here closes the general leading-constant gap.

Main mathematical outputs
1. FOREST_CLASSICAL_BOUNDARY.txt: efficient all-profile own-monotone allocation
   on fixed owner-interaction forests. This is an application of the classical
   hierarchical/average-tree allocation, explicitly attributed to Demange and
   Herings--van der Laan--Talman. Connected resource ownership blocks suffice
   but are not necessary. Do not claim the underlying core result as new.
2. FRAGMENTED_FOREST_FAMILY.txt: exclusively owned resources on repeated
   A-B-C-D paths force factor(9k-5)/(8k-4), tending to9/8. Ownership blocks
   are fragmented and their interaction graph has a four-cycle. Disjoint
   replication makes both actual owner and resource counts grow, even with
   arbitrary cross-component payment dependence. This extends the ownership
   interpretation of the known9/8 lower bound; it does not improve that number.
3. DISCONNECTED_OWNERSHIP_OBSTRUCTION.txt: k=2, an exact three-profile13/12
   certificate with four fixed owners and eight unshared resource rows.
4. SCALAR_BIAS_BARRIER.txt: a common scalar-bias family with p(1)=1/2 cannot
   improve the exponential factor1+1/(2e). This is a restricted-mechanism
   obstruction, not an unrestricted lower bound.
5. CYCLE_TO_PATH_TRANSFER.txt: every finite nonnegative report-transition
   lower certificate on an exclusively owned resource cycle transfers
   asymptotically to long paths by repeating capacities, while preserving
   fixed actual owners and all own-report comparisons. Lower transfer only.
6. NETTING_AND_THREE_OWNERS.txt: a precise zero-payment/1-Lipschitz lifting
   lemma for mixed ownership, including role-change seams; and an efficient
   all-real-profile rule for at most three mixed owners. The latter is a
   bounded-owner boundary, not the unrestricted campaign progress gate.

Exact replay, using ordinary Python only
Run from this directory:
  python3 -B -O check_disconnected_witness.py
  python3 -B -O check_fragmented_family.py
  python3 -B -O check_three.py
  python3 -B -O check_certificates.py
All checks use Fraction and explicit exceptions; -O does not disable them.
check_certificates.py reads the compact gzip files directly. It reconstructs
all lower-certificate constraints from profiles and independently recomputes
production values using max-profit flow. It also checks every coalition,
budget and all comparable own-bundle increases in each finite upper witness.
Discovery used different exact production oracles (dual vertices or weighted
vertex-cover dynamic programming), with SciPy only for locating LP solutions.

Selected finite-domain certificates
- calibrate.json: three-profile established two-input9/8 witness.
- path5-unit.json.gz: six owners on a five-edge path, one owner per vertex,
  independent scalar grid{0,1,2}^6; exact finite optimum1 (classical case).
- two-fullmixed-n4.json.gz: four mixed owners, independent coordinate grid
  {0,1,2}^8,6561 profiles; exact finite optimum9/8.
- path3-fullmixed-1-w0.json.gz: unit three-edge path, four actual owners
  with supports{0,2},{0,2},{1,3},{1,3}, same6561-profile grid; exact optimum9/8.
- disconnected-full-d8-w1.json.gz: exclusive owner patternA-B-C-D-A-B-C-D
  on a unit path,6561 profiles; exact optimum13/12.
The three large grids each have98415 coalition checks and78732 comparable
own-report checks. These rational feasible allocations are upper certificates
only on the finite domains. They do not establish continuous all-profile
mechanisms. CERTIFICATE_CHECKS.jsonl records the independent replay.

Scope of negative searches
No tested lower bound exceeded the established9/8. Sparse-profile long paths
with two owners per resource were tested at10,12,14 owners; the largest
non-calibration factor in the initial unit-weight family was19/18. A geometric
and weighted sparse sweep completed10 cases, hit a separator round limit on
four cases, and was stopped during case14 after runtime ceased being useful.
Those unfinished cases have no claimed optimum. Repeated-owner paths with
4--7 owners and3,5,10,20 repeats produced no stronger lower bound. Native
cycle probes were exploratory and are not themselves forest results.
Additional small merged-owner cycle probes found no factor above9/8; these
were discovery outputs rather than claims of independently replayed optima.
A final weighted-cycle probe completed two cases and was stopped during its
third case at the parent's explicit search freeze. Its unfinished case has no
claimed result. Except the selected certificates listed above, negative
search summaries should be read as exploratory diagnostics, not theorems.
The exact fragmented-ownership family above was extracted from an independent
full-coordinate probe, rather than inferred from sparse numerical fits.

Priority and status
Only the classical forest source was checked in the primary literature here:
Herings, van der Laan, Talman (2008), Games and Economic Behavior62,77--92,
equation(3.3), printedp83; Section4 and Theorem4.1, printedp85.
Free original: https://cris.maastrichtuniversity.nl/ws/files/64777103/Herings_2008_the_average_tree_solution_for.pdf
External novelty of the other internal derivations remains unconfirmed.
The useful outcome is an ownership-sensitive structural boundary and a clear
obstruction to one mechanism family. The unrestricted sharp constant remains
open; these artifacts should not be described as a field-level breakthrough.
