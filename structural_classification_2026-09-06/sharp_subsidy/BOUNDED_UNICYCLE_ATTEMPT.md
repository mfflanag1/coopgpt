# Bounded unicyclic attempt: stopped without a one-third theorem

Date: 2026-09-07 (America/New_York).

The user requested one bounded attempt. The announced limit was 20 minutes,
starting 2026-09-08 00:27:22 UTC, and at most two proof variants. Success required
an all-weight `J(M,P) <= T/3` theorem for every connected unicyclic support,
including repeated labels, or an exact admissible counterexample above one third.
Stopping criteria were failure of both variants, dependence on an equally hard
unresolved theorem, or the time limit. Both variants below failed to close the
bound. The proof record was finished by 00:36:56 UTC, within the bound.
Mathematical exploration stopped after those two variants; subsequent
work only records and verifies their outcome.

**Outcome:** unsuccessful attempt at the full unicyclic case. No counterexample,
no improved global bound, and no novelty confirmation. The global interval remains
`1/3 <= S_3 <= 2/5`. The overarching research goal is not completed by this note.

## Definitions

Use the original strict three-sector, nonnegative pair-additive market, an
optimal diagonal matching mu, and a partial matching P. The entire original
core is nonempty. Its coordinate maxima are H; grand worth is T>0. Write

    J = w(P) + sum_{i unmatched by P} H_i/3 - T.

After the reductions in REDUCTIONS.md, pair support is contained in mu union P.
There are m diagonal labels and r P-team nodes. Incidences count multiplicity,
including two players of a P-team at the same diagonal label. Connected unicyclic
means cycle rank `2r-m+1=1`, so m=2r. A tree has m=2r+1.

## Variant 1: clone and split a cycle label

### Selective cloning lemma

Let j be a diagonal label of worth d. Add one copy of each of its three players.
Every pair involving a copy inherits the corresponding original pair value.
Then the new grand worth is T+d and its entire core is exactly the original
core with the three payoffs at j repeated. In particular every original and
copied coordinate ideal is preserved exactly at this intermediate step.

Proof. Every original core point makes each optimal diagonal team tight. Lift
it by repeating the three payoffs at j. Every new triple maps to an original
triple, so the lifted vector covers all triples. Its total is T+d. The old
optimal diagonal matching together with the copy diagonal attains T+d, proving
optimality and core feasibility.

Conversely, in a new core point all those optimal diagonals are tight. Replacing
one player of the old j-diagonal by its copy gives copy payoff >= old payoff.
Replacing the corresponding player of the copy diagonal by the old player gives
the reverse inequality. This works separately in every sector. Restriction to
the old players therefore has total T and covers all old triples, and belongs
to the old entire core. This proves both inclusions. Triple coverage and
nonnegativity imply all coalition constraints in this strict full-team model.

### The split and its unavoidable error in this argument

Choose a label j on the unique incidence cycle and clone it as above. Partition
its incidences between the old and copied labels so that the two cycle
incidences go to different copies. Send any third incidence to either copy.
This is legal because P uses each sector-player at most once. It also handles
a repeated-label team: the two parallel incidences are placed at different
copies of j. The graph stays connected, gains one label node and no P-node or
incidence, and becomes a tree. Its new P-team values are unchanged.

Sparsify to the new diagonal matching and relocated P. The new grand worth
remains T+d; its core contains every lifted old core point. Consequently its
ideals weakly increase from the preserved old/copied ideals. The unmatched
multiset, mapped back to original identities, gains exactly one copy of each
of the three players at j. Set K=H_Aj+H_Bj+H_Cj. Then

    J_tree >= J_unicycle + K/3 - d.                         (1)

Every H_sj <= d by diagonal tightness and nonnegativity; also K>=d because any
one original core point has diagonal sum d. Thus d<=K<=3d.

Even IF the still-unproved general tree inequality were available, combining
`J_tree <= (T+d)/3` with (1) would give only

    J_unicycle <= T/3 + (4d-K)/3.                          (2)

For d>0 the error term in this derived bound is at least d/3. Thus exact
preservation of ideals before sparsification does not eliminate the grand-worth
cost. This calculation is a limitation of this inference, not a proof that a
stronger tree estimate or another splitting operation is impossible. A zero-worth
cycle label removes this error, but still leaves the unresolved general tree
bound. The established one-hub tree theorem cannot cover arbitrary split trees.

**Stopping diagnosis:** this variant needs both a stronger error-cancelling
estimate and a currently unresolved tree theorem. It does not prove the requested
all-unicyclic statement.

### Reverse construction: a precise asymptotic dependency

The same lemma gives a useful additional diagnostic, without another search.
Start with a connected tree support with r>=1, m=2r+1 and h=m-r>=2. Choose a
minimum-worth diagonal label j, so d<=T/m. Choose an unmatched sector-A player a
of minimum ideal, and an unmatched sector-B player b of minimum ideal among
labels other than a's label. There are h and at least h-1 choices, respectively.
Since each sector's sum of ideals is at most T,

    H_a <= T/h,    H_b <= T/(h-1).

Clone j, and add the P-team (a,b,the sector-C copy at the new label). It is
player-disjoint from old P and uses three distinct labels. Its incidence graph
is connected and has gained two nodes and three incidences, hence is unicyclic.
Sparsify to its diagonal and P support. Its worth is T'=T+d and

    J' >= J + w(a,b,Ccopy) - (H_a+H_b)/3
                + (H_Aj+H_Bj)/3 - d
       >= J - (H_a+H_b)/3 - d.                            (3)

Let R=J/T. We have R<=1 because w(P)<=T and sum_U H<=3T. Put
A=(H_a+H_b)/(3T) and z=d/T. Equation (3) implies

    J'/T' >= (R-A-z)/(1+z) >= R-A-2z
            >= R - 1/(3h) - 1/(3(h-1)) - 2/m.            (4)

The middle inequality follows from R<=1 and A,z>=0, and does not require
assuming that the lower numerator is positive.

Thus a large-tree sequence with limiting obstruction above one third would
produce a unicyclic sequence with the same limiting obstruction lower bound.
An all-unicyclic one-third theorem would settle the asymptotic large-tree upper
bound as well. This does NOT prove equivalence with every finite tree instance:
the loss in (4) need not vanish for a fixed small tree, and no size-amplification
lemma is supplied here. This is a difficulty diagnosis, not a novelty claim.

## Variant 2: use the existing donor packing directly at one third

In the parameterized mixed-donor construction, aggregate pair coverage is
`(u-5+t) mu + 3P`, giving `J/T <= (2-t)/3` when the construction is feasible.
The one-third target is therefore t=1. The endpoint retains meaningful row
capacities, but its donor budget must still pass; the established upper theorem
at t=4/5 does not assert feasibility at t=1.

Take b>=4, m=4b and the following 2b P-teams:

    e_j = (j,(j+1) mod b,b+j),
    f_j = (2b+2j,2b+2j+1,j),             0<=j<b.

This connected incidence support is unicyclic. It has b degree-three labels,
3b leaves, no degree-two labels, and h=2b unmatched players per sector. Every
sector has L=b leaf columns and all its unmatched rows are leaf rows. These
are the ring-with-attachments supports already used in BROKEN_RING_THEOREM.md;
no new support family or actual subsidy lower bound is claimed.

At t=1, alpha=1/(2b), beta=1-alpha, delta=1-1/b. Each leaf row has base capacity

    min(L alpha,beta-delta) = 1/(2b).

In each sector demand L delta=b-1 exceeds total base capacity 1 by b-2.
Across all three sectors the extra demand is therefore 3b-6. The b degree-three
donors have budget 2-t=1 each, giving total budget b. Their deficit is

    (3b-6)-b = 2b-6 > 0.

At b=4 this is an explicit 16-label unicyclic support with demand 6 and capacity
4. No redistribution within these stated donor budgets can remove the deficit.
More generally, for any fixed 4/5<t<=1 and sufficiently large b, the same raw
capacity calculation gives total demand minus budget

    b(10t-8)-6 > 0.

Hence restricting this existing constant-t template to unicyclic supports does
not permit any fixed improvement beyond its asymptotic two-fifths bound.
This is a template obstruction: it does NOT preclude size-dependent improvements,
a redesigned packing, weight-dependent arguments, or the actual one-third bound.
Indeed the previously certified broken-ring markets on these supports have
subsidy ratio `1/3-1/(6b)`, below one third.

**Stopping diagnosis:** the second variant fails its exact capacity test. No
third variant or larger blind search was started.

## Verification and next decision

`verify_bounded_unicycle.py` uses exact integer/Fraction arithmetic and explicit
exceptions that remain active under Python -O. It checks:

- 35 selective-clone/closure calibrations from the certified tree family;
- 9 cycle splits of certified broken-ring markets, with all lifted full-team
  core inequalities checked, and a repeated-label cycle/split topology check;
- 29 unicyclic supports (b=4,...,32) against the raw capacity deficit formula;
- a negative control rejecting the deficient donor budget.

The run checks 3,142,476 full-team inequalities. These are finite calibrations;
the all-size cloning and capacity statements rest on the conventional proofs
above. They do not prove the target unicyclic theorem. Build integration runs
the checker with the existing project verification suite. The full
`build.sh --smt` run completed with exit code 0, including this checker.

The authorized Claude review was invoked on this note and checker with a
30-second deadline. It returned `timed_out` (30.02 seconds), with no review or
approval. Earlier CLI authentication was unavailable; this invocation establishes
only a timeout, not a new authentication diagnosis. Its record is
`/Users/maxf/.local/state/claude-reviews/coopgt-recovery-53851b46c997/20260907-203809-1da748a8/status.json`.
Independent specialist review remains incomplete.

Recommendation: close this bounded attempt. Reopen it only with a concrete
proposal that cancels the split error in (2), or changes the donor accounting
that fails in Variant 2. More instances of the same template do not address
either obligation. No follow-on campaign is started by this note.
