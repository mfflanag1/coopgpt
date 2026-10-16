**Provisional verdict: no invalid inequality found in reviewed scope; one dependency-status finding (medium) and one thin-margin step (low).**

Most important: DM2 (δ₊ ≤ 1/100 ⇒ ΣE_i < 7/5) is only valid with the *sharp* incoming constant K = e−1, whose source file is itself marked "independent review pending"; HT2 does not share this fragility.

## Findings

**1. Medium — DIRECTIONAL_LOCAL_MASS_FUNDING.txt:33–40, 75–83.** Section 1 calls the incoming estimate `E_i ≤ a_i − q0 f(z_i) g_i`, f(z)=exp[−Kz(1+log(1/z))], "accepted". Its only source in the packet is SHARP_INCOMING_ENTROPY_v2.txt (I-sharp), header: "Candidate strengthening; independent review pending." The context file lists only the v1 constant (e+1) form and the L-form negative-gap bound as audited. The constant matters: DM5 needs f(1/4) > 1/3, which uses K<7/4 (line 78). With e+1 instead, f(1/4) ≈ exp(−2.22) ≈ 0.11, so sup v[1−f(1−v)] ≈ 0.89, the bracket becomes A−0.11, and at A=1 the bound is 1+(1/2)exp(−0.11) ≈ 1.45 > 7/5. DM2 therefore fails without the sharp constant. Verification: either confirm (I-sharp) has been adjudicated, or relabel DM as conditional on it. (HT1's coefficient also uses K via exp(−K), but HT2 drops the v-term entirely and survives even with no negative-gap savings: 1+q0[r+7/2−v].)

**2. Low — HIGH_CAPPED_TOTAL_FUNDING.txt:69–75 (HT6).** log(11/3) − 1069/825 ≈ 1.29928 − 1.29576 ≈ 0.0035, so the tangent argument closes with ≈0.35% margin. I confirm the arithmetic (h′(3/4)=56/33−43/25=−19/825; h(3/4)+h′(3/4)/4 = log(11/3) − 1069/825) and the sign numerically, but the exact rational Taylor upper bound exp(1069/825)<11/3 is delegated to a checker I did not run. Verification: display the finite Taylor sum plus tail bound in the note.

## Recomputed and confirmed

- **DM3/DM4:** negative gap ⇒ d_i uncapped, Σ_{J₋}(z_i+g_i)=Σ(a_i−p_i)≤1; f′=K log z·f ≤0, f″=[K/z+K²log²z]f>0; weighted Jensen with weights g_i/v and g_i/v≤1 gives v f(Zminus) ≥ v f(1−v). Correct.
- **DM5:** K(1/4)(1+log4)<21/20, e·exp(1/20)<(11/4)(20/19)=55/19<3. Correct.
- **DM6→DM1:** G₊=r+v; [A−f(1−v)]v ≤ A−1/4; exp(−r)(Ar+A−1/4) has derivative exp(−r)(1/4−Ar), max at r=1/(4A), value A·exp(−1/(4A)); increasing in A. Correct. DM2 numerics (400/393<51/50; exp(25/102)>51/40 from terms 0–3) check.
- **HT3:** q·ρ=ρe^{1−ρ}/2≤1/2; (1−q)T≤ρT/2 ⇔ 2−e^{1−ρ}≤ρ; ρT=D≤H_j. Correct.
- **HT4:** convexity in l; l=0 endpoint via ψ′(a)=K{1/[(1+(K−1)a)(1−a)]−1}≥0 (denominator =1+(K−2)a−(K−1)a²≤1); a≥1/2 endpoint 5(1−a)≤3−a; a≤1/2 endpoint reduces exactly to HT5; h″>0. Correct.
- **HT7/HT1:** g_i≤1−a_i, z_i≤min(1,a_i+l_i), Σ_{J₊}a_i≤1−v, Σl_i≤1/2 ⇒ Pextra≤7/2−2v; summation algebra correct. **HT2:** d/dr e^{−r}(r+7/2)<0; 11/(4e²)<99/256<2/5. Correct.
- All-profile dependence: each per-owner envelope bound is evaluated at the same full profile; summation requires no simultaneous attainment. Fixed owners and unbounded counts preserved. Section 6 example arithmetic (z=(1+c)/(4n), d<a, δ₊=0; weighted variant z=(1+c)/8) checks.

## Scope limitations

Imported comparisons (8),(9) of INCOMING_ENTROPY_DIFFUSE_FUNDING §5 and sharp outgoing O_i≤Kz_i taken as given; I did not re-audit them. Checker scripts not executed. No claim about the 1≤S<3 region or unrestricted C².

## Verdict

Findings (dependency status for DM; thin margin HT6). Both results are correctly stated as sufficient profile classes, not unrestricted C² funding.
