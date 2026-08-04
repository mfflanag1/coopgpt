# Hostile review request: leximin face-ascent geometry

Please review the convex-geometric theorem and its exact-game specialization
as if recommending rejection unless every implication and novelty boundary is
correct.

## Primary paths

- `coopgames/paper3/LEXIMIN_FACE_ASCENT_GEOMETRY.md`
- `coopgames/paper3/UNIVERSAL_LMIN_SLACK_ASCENT.md`
- `coopgames/paper3/TERMINAL_SLACK_CUT_THEOREM.md`
- `coopgames/paper3/sections_leximin.tex`
- `coopgames/src/verify_leximin_face_ascent_geometry.py`
- `coopgames/results/leximin_face_ascent_geometry.json`
- `coopgames/paper3/wrapper.pdf`

## Hostile questions

1. Does componentwise nondecrease on the poorer side, together with a
   preserved strict boundary, necessarily lexicographically improve the
   increasingly sorted vector?  Identify any missing tied-stratum case.
2. Is compact convexity exactly what is needed for the segment and face
   minimizer arguments?
3. Is the positive-variation identity `(PV)` correct, including the sign in
   the final positive part?
4. Does the terminal sign-cell correspondence hold in both directions when
   some coordinates have zero displacement?
5. Does exactness give precisely the equality between game slack and face
   deficit used in the corollary?
6. Is the cover-free ascent theorem already known in leximin optimization,
   fair allocation, bargaining, polymatroid/base-polytope theory, coherent
   lower probabilities, or cooperative-game solution theory?
7. Is `(PV)` merely a standard support-function identity that should be
   stated as a lemma rather than promoted as a contribution?
8. After removing the strict-cover dependency, which remaining claims are
   genuinely specific to exact games and Lmin?

Do not treat the verifier or successful compilation as proof evidence.  Do
not endorse field-level significance without both a correctness verdict and
a specialist literature comparison.
