# Split memo — one paper or two?

**Subject:** `paper4/threshold.tex`, "Balanced transport at the egalitarian
core: a complete boundary phase diagram", 23 pages at commit `99a16b9`.

**Recommendation: keep it as one paper. Submit the 22-page manuscript
unsplit.**

---

## The three movements and what they consume

| Movement | Sections | Pages (approx.) |
|---|---|---|
| A. Phase diagram | §§1–5 (Thms 1, 3, 4; Lem 2; Props 9, 12, 14–16; Cor 17) | ~10 |
| B. Selection | §6 (Lems 19, 21, 22, 25; Prop 26; Thms 27, 30, 31) | ~7 |
| C. Monotonicity | §7 (Lem 34; Thms 35, 36; Prop 38; Conj 42) | ~5 |

Reference counts from the source (excluding internal references within a
movement):

- **B → A:** Theorem 4 (×5), Theorem 3 (×2), Theorem 1 (×2), Lemma 2 (×2),
  plus Proposition 12, Lemma 11, Lemma 10, Lemma 13, Corollary 7.
  B is *about* the object A constructs: a "system (P)" has no definition
  outside Theorem 4, and Definition 18 (normal certificate) is stated as a
  generalization of Lemma 2's cover. Row 9 of the five-player classification
  is excluded **by Theorem 1 alone**, and the `h = 2` threshold theorem is
  explicitly positioned to "start where Lemma 11 stops".
- **C → A:** Theorem 1, Lemma 2 (the tangent cone `D` of Lemma 34(iii) *is*
  the cone of Lemma 2), Lemma 13 (both examples), Corollary 17 (the four/five
  threshold for monotonicity failures is derived from it, not re-proved).
- **C → B:** one cross-reference only (Remark 44's sampling caution points
  back to §6's).
- **B → C:** none.

So A is a genuine trunk; B is welded to it; C hangs off it by four load-bearing
citations and is otherwise independent of B.

## Option 1 — keep as one paper (recommended)

- **Referee burden.** 22 pages is normal for IJGT and MMOR, and the paper is
  self-segregating: three status tables plus §8 tell a referee exactly what to
  check and at what standard. A referee who bounces off §7 can still certify
  §§1–6.
- **Coherence.** The paper's actual thesis is stronger than its title: *one
  piece of boundary geometry (the Lmin normal cover) controls two unrelated
  pathologies of the leximin selection.* That claim exists only if §7 is in
  the same paper as §§1–5. Splitting it demotes §7 from "second application of
  a mechanism" to "a lemma, two examples and a conjecture", which is a weaker
  paper on its own.
- **Cost.** §7's headline is a conjecture. A referee may ask for it to be cut.
  That is a cheap outcome — §7 is terminal and removable without touching
  §§1–6.

## Option 2 — split as (phase + selection) / (monotonicity note)

- **For:** the note would be ~6 pages and could go to Mathematical Social
  Sciences quickly; the main paper drops to ~17 pages and loses its most
  conjectural section.
- **Against:** the note must re-import Lemma 2's tangent cone, Lemma 13, and
  Corollary 17, i.e. cite an unpublished preprint for its own machinery. Its
  proved content (Theorem 35 is two lines; Theorem 36 is a short
  superadditivity argument) is thin for a standalone; its interest lies in
  Examples 40 and 41 and in Conjecture 42, and a note whose headline is a
  conjecture on 1041 sampled failures is a hard sell without the mechanism
  around it.
- **Verdict:** viable, but strictly worse now. It stays available later — if a
  referee demands §7 be cut, the note can be spun out *then*, with the main
  paper already accepted and citable. Splitting now forecloses nothing and
  gains nothing; splitting later costs nothing.

## Option 3 — split as (phase) / (selection + monotonicity)

- **Against, decisively:** this cuts the tightest weld in the paper. §6 cites
  §§1–5 fourteen times and cannot state its own hypotheses without Theorem 4.
  The result would be two papers where the second is unreadable alone and the
  first is a 10-page theorem that a referee will reasonably ask "and which
  system does it produce?" — which is exactly §6. Reject.

## Secondary considerations

- **Venue fit.** MMOR and IJGT both take 20–30 page structural papers.
  Nothing in the target venues rewards splitting; MSS is the only venue where
  a short note is the natural unit, and MSS is the third choice for this
  paper anyway.
- **Self-citation overhead.** The program is already submitting two mutually
  citing preprints (`paper4` ↔ `paper5`) simultaneously, which must be
  disclosed in both cover letters. A third simultaneous submission citing the
  other two turns a clean disclosure into a salami-slicing question. That
  alone is a sufficient reason not to split now.
- **Priority.** One 22-page paper establishes priority over the whole
  mechanism at one date. Three staggered pieces do not.

## Decision

**One paper.** The selection section cannot leave (Option 3 is dead), and the
monotonicity section is worth more attached than detached while it is
conjectural. Keep the option to spin §7 out at revision if a referee asks —
that option is free and does not expire.
