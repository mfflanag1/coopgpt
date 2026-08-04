# Structural phase paper

This directory contains the concise standalone version of the central
dimension-free result. The 118-page `paper3` manuscript remains the technical
archive; `threshold.tex` is organized around one theorem:

```text
m_min(1)=4,
m_min(2)=m_min(3)=3,
m_min(h)=2 for h>=4.
```

Build from this directory with:

```bash
pdflatex -interaction=nonstopmode -halt-on-error threshold.tex
pdflatex -interaction=nonstopmode -halt-on-error threshold.tex
```

The proof is human and dimension-free. The exact programs in `../src` and
saved outputs in `../results` are independent bug audits, not proof
dependencies.

For an independent audit, send `EXTERNAL_REVIEW_PROMPT.md` together with the
PDF and repository commit.
