**Provisional verdict: no invalidating findings in reviewed scope.** The most important check: the headline identities (ceiling C, g_C, quintic J, cubic T, balance quartic N) all rederive correctly, and the lower/upper bounds genuinely meet at g_C(ρ).

## Findings

**1. (Verified, no defect) Pointwise ceiling, Sec. 11.** For shorts (1/2,1/2,0,0), longs (0,0,1,R), R≤1/2: λ=1−R, aux inactive, P=1−R, s=1/2 ⇒ f(s)=0, so Y(R)=[1/2+f(1/(1+R))]R(1−R). Y(1/2)=1/8 and Y≤1/8 ⇔ f(t)≤t²/[8(1−t)(2t−1)]−1/2 with t=1/(1+R). Correct; uses only one owner's underreport, no regularity. With f=C, Y≡1/8 (owner indifferent) — consistent with extremality.

**2. (Verified) Funding algebra, Sec. 10.** 1−2C(s)=(−17s²+24s−8)/[4(1−s)(2s−1)] gives g_C as stated. I expanded N′D₀−ND₀′ and obtained exactly J=68s⁵−235s⁴+308s³−199s²+64s−8; J(2/3)=4/243, J(1)=−2; Taylor coefficients at 2/3 (−164/81, −221/27, −148/9, −25/3, 68) check; J′<0 bound on [0,1/3] valid. Tangent-segment sign A(2s−1)−6κs² and discriminant 4A(4/5−4κ)<0 verified. Lower bound Γ=1+g_C(ρ) matches the constructed rule's max since g_C increases on [2/3,ρ], F(2/3)=125/972<g_C(ρ), g_lin decreasing.

**3. (Verified) Tangent/τ, Sec. 2.** Multiplying (1−u)C′+C−1/10 out gives 2T(u) with T=53u³−91u²+55u−12; T′ discriminant −1856; T(17/25)=−211/15625; decimal checks of C′(17/25)≈0.2562, C′(0.683)≈0.3108<5/16 agree (κ<5/16 is tight: margin ≈0.0017).

**4. (Verified) Balance polynomial, Sec. 6.** Numerator of 1/2−Q(1) times 40(1−s)²(2s−1)² is 186s⁴−316s³+173s²−24s−4; expansion (52/9)x+37x²+180x³+186x⁴ confirmed via derivatives at 2/3. Note N(2/3)=0: the balance inequality has **zero margin at s=2/3** (and OS_critical is an equality on [2/3,τ]). Monotonicity is nonstrict there; exact-implementation ties near 2/3 and τ must not perturb signs.

**5. (Verified) Replacement of the 1/16 bound, Sec. 5.** Margins 7/1350 and 41/3672 recomputed; require C′ increasing and 17/25<τ (both proved). Low severity: slack is ~0.5%, so any later change to f near 2/3 would need re-checking.

**6. (Low) Dependencies.** The OS proof inherits β identities, the dominant-cap lemma, (RT_F), and the Sec. 9 L-raise/R-raise reductions verbatim from PF/WATERFILL; I re-derived β, the R-derivative sign ⇔ (OS_long), and R=1/2 comparison 32(1+s)³−27(2s+1)²=(2s−1)²(8s+5). No gap found. Consistency check: C″(2/3)=81/4=9/(5·4/45), exactly PF's necessity threshold, as expected.

## Scope limitations
- Did not verify exact rationals T(683/1000)=936311/10⁹, C′(683/1000) fraction, J(27/40) numerator (decimals agree).
- Did not re-prove WATERFILL cell-finiteness/continuity claims.
- Cannot execute the algebraic implementation; τ/ρ isolation relies on stated endpoint signs.
- Lower bound presumes the universal eligibility class admits the four pure owners (stated caveat).

## Verdict
No findings invalidating the claim within reviewed scope. Minor notes: zero-margin configurations (items 4, 1) and thin margins (items 3, 5) should be documented for the exact implementation.
