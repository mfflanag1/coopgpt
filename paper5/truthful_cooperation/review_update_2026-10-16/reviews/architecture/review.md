**Provisional verdict: no substantive mathematical findings in reviewed scope; two low-severity transcription/compile issues.** The most important concrete check: the multi-block threshold-weight inequality in Theorem `arch:vowner` ($S_0\le D$) reduces exactly to the defining inequality $m(m+7)/2\le n-1$, and the per-mask average $al+D\pi_{l+1}\ge am$ then holds; I found no gap there.

## Findings

**1. Low — `\R` macro not supplied (line 15).** The header comment (line 2) says the fragment "uses only the existing amsmath/amssymb/amsthm"; `\R` is not defined by those packages. Verification: confirm the host supplement defines `\R` (or replace with `\mathbb R`).

**2. Low — missing spaces before numerals (transcription).** Lines 184 ("below1"), 226/273/296 ("sum to1"), 291 ("and1 elsewhere"), 373 ("is1"), 413 ("is1"), 417 ("at least1"), 424 ("receive1"), 495 ("at least1"), 498 ("equal1"). These will typeset as "to1", "is1", etc. Verification: grep for `[a-z]1` in the fragment.

**3. Informational — unjustified but true inequality (line 466).** $(n-m)/(mn)\ge 1/n^2$ needs $n(n-m)\ge m$; this holds for $n\ge 9$ with $m=\lfloor\sqrt{2n}\rfloor\le n/2$ but is asserted without a word of justification. Suggest adding "since $m\le n/2$".

**Checks that passed (no finding):**
- Eligibility (Lemma `arch:caplemma`): $0\le V_i\le T$, own-bundle monotonicity of $V_i$, the one-at-a-time increment argument for simultaneous $V_i$ truncation, and the touching/majorization step $F(x_B)-F(x_B-b_i)\ge\ell_B(b_i)$ are all correct.
- Lemma `arch:realization`: masked value $v_l+\varepsilon E_l$ with $E_l\le 2n^3$; competitor exhaustion (subsets meeting an open coordinate $\ge n^2/(n-1)^2>1$; proper subsets of $C$ strictly costlier via $a_{|S|}\ge a_l$); interior unique-gradient forcing; closed raw price $\ge n^2/(n-1)^2>t$; endpoint bound $\delta_l-(2n^3+n)\varepsilon\ge\delta_l-\eta$ including $l=0$ and $l=n-1$; block-restriction argument uses $g(0)=0$ correctly.
- Lemma `arch:increments`: $a_l$ nonincreasing iff $v_{l+1}\le(n-l-1)\delta_l$ — correct; gap bound $\ge (n-l)(\delta_0-1/n)/(n-1)\ge 1/n^3$ correct.
- Theorem `arch:tbarrier` ($n\ge9$): $S_2<1$, $m<\sqrt{2n}<n/2$ (needs $n>8$), $\delta_0\ge 2/n\ge 1/n+1/n^2$, per-mask bound $\ge m-1/n^2$, $a_m=0\Rightarrow T_j\le 1/4$, Markov fraction $1-2m/n$, anchor average $n-2m>0$. Asymptotics via $S_{m+1}>1$ are sound.
- Theorem `arch:vowner`: $V_i/T\ge 1-(2m+1)/n$ uses $\eta\le 3/n$ (true); $(n-l)^3/n^2\ge n-3l$ true; anchor raw price $\ge 2(s/2)=s\ge1$; $A_0=n-2$ correct; same owners/technology across $P_1,\dots,P_m,Q_j$.
- Theorem `arch:vdimension`: $am-n\eta$ identity exact; coordinate $e$ with $w_e\ge1/D$ abundant in exactly $R$ anchors; pointwise-in-support argument valid despite $e$ depending on $w$; $H\to1$, $a\to1/2$, $C'_n\sim\sqrt{n/2}=\tfrac12\sqrt{2n}\sim\tfrac12\sqrt{d_n}$.
- Lemma `arch:averaging`: weights $A/(A+C)$, $C/(A+C)$ give $\ge AC/(A+C)$ for every mask; empty-mask hypothesis is pointwise in the fixed support, so commutes with its law; no profile-dependent empty-mask law is assumed.

## Scope limitations
- Cannot verify the externally referenced upper bounds ($n\sqrt{2/(n+1)}$, $O(\sqrt d)$) or that they are realized within this architecture; the "sharpness" claims in the Scope subsection rest on them.
- Eligibility conditions ("cover every coalition", own-bundle monotonicity) are assumed to match the host supplement's definitions.
- The relative-support paragraph (lines 527–538) concerns extended-valued selectors outside Definition `arch:def`; its claim is plausible but not a theorem here.
- No unrestricted lower bounds are inferred; the fragment correctly confines all conclusions to the fixed-mask common-support architecture.

## Verdict
**No mathematical findings in reviewed scope**; two low-severity transcription/compile issues (`\R`, missing spaces) and one cosmetic justification gap.
