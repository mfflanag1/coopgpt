**Provisional verdict: no substantive findings in reviewed scope.** I re-derived every theorem in the packet (floor/cap lemmas, Banzhaf monotonicity and tail bound, the unrestricted two-profile certificate, the proportional certificate and minimax corollary, the one-pool nonlinear rule, all two-pool binary cases, and the bounded-$m$ continuous rule) and found the stated quantifiers and class distinctions consistently maintained. The most important concrete item is a mild overstatement in the abstract about the continuous rule's domain.

## Findings

**1. Low — abstract overstates Theorem 7.1's domain (line 38–39 vs. 484–486, 480–481).**
Abstract: "A different nonlinear rule handles all real reports when the number of altered pools is bounded." The theorem covers reports in $[0,1]$ (improved constant on $[1/r,1]$), with equal pool sizes and a fixed public reference capacity $1$. Reports above $1$ are outside the domain, and the rule is not scale-free. The introduction bullet (line 85–86) and Section 7 state this correctly; only the abstract is loose. Suggested fix: "all reports in $[0,1]$".

**2. Low / unverifiable — identification with Kurz Def. 6.11 (lines 102–104, 258–270).**
The algebra $T[f_d(1,u_{-i})-f_d(0,u_{-i})]=\min\{d_i,(Y-R)_+\}$ and endpoint values $0,1$ check out, so $z_i=T\cdot(\text{the stated integral})$. Whether that integral is exactly Kurz's "absolute continuous Banzhaf index" (including any normalization convention) cannot be confirmed from the packet. The manuscript appropriately does not claim novelty for the functional; a reviewer with the Kurz text should confirm the definition matches.

**Items checked with no defect found (selected evidence):**
- Lemma 2.1: $M_i=\min\{c_i,(D_j-A_i)_+\}=(c_i-(C_j-T))_+$ verified in all three orderings of $A_i,D_j,C_j$; $\sum M_i\le kT$ via $C_j-ps\le T$ for $p\ge1$.
- Thm 3.1: $R$ independent of $x$ (both cases $a\le b$, $a>b$); $d_i\Pr(U_id_i<Y-R)=\min\{d_i,(Y-R)_+\}$; $p_j\le e^t t^{-\rho_j}$ via Jensen on $u^a$; tail integral $1/\log R_k$ with $k(e/R_k)^{R_k}=1$. Bound is owner-count free.
- Thm 4.1: pool totals $t$, $2t-1$; weights $1,q,t-1,1$ give LHS $t[P+(k-1)Q]-(t-1)(k-1)w$, RHS $t^2$; weights $1,q,1$ on $Y$ give budget $+\,2(t-1)A\ge 2t-1$; $L\to H$ by raising one unit to $t$; $r=n{+}1,k=8n^2{+}1$ yields $(2n-1)/(2n+1)$. Averaging requires equal pool sizes, which holds. $B=1+\beta$ used consistently; no $B/\beta$ slip anywhere.
- Thm 5.1 / Cor 5.2: capping inert on the path ($T\ge1$, caps $\le1$); telescoping $r^r\pi_j(H)\ge\pi_j(L_j)$; certificate weights match; $(r-1)r^r=o(k)$ for $r=\lfloor(1-\epsilon)\log k/\log\log k\rfloor$. Corollary is explicitly floor-free; floored Banzhaf rule is correctly excluded (not proportional).
- Thm 6.1: $b_{s+1}=(r-1)(r-s-1)/r^2$, $a_s/b_{s+1}$ formula verified; $a_{r-1}=0$; coverage split $n\le b$ / $n\ge b+1$ holds; $F_h\le 2T_h$ both regimes.
- App. A: all four edge cases (incl. $r=2$ equality $q_0=1$, $b_1=a_0=1/4$); $F'\le2$ both regimes; slack $\ge1/r$; special values $13/8$, $125/72$, $w=1/16$ recomputed; case split exhaustive.
- Thm 7.1: $E_i\ge(r-1)/2$ when $T\le(r-1)/2$; uniform part $\le4T$ (resp. $\le3T$ on $[1/r,1]$, $r\ge3$); limitation example $3+4k/3$ exact.

## Scope limitations
- No access to the verification scripts, source ledger, or cited texts; the table in App. B is unverified.
- Priority/novelty not assessed.
- Only the supplied `.tex`; no prior component notes compared.

## Verdict
**No findings of substance in reviewed scope.** Two low-severity items: an abstract domain overstatement (fixable in one phrase) and an identification with Kurz that is plausible but unverifiable from the packet.
