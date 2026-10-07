**Provisional verdict: no counterexamples found in reviewed scope.** A1–A3 check out as stated for all finite DAGs, fixed owners, and nonnegative reports including zeros. A4 is correct conditional on hypotheses not stated in this file (most importantly U_e ~ Uniform[0,1] in the formula q_e = min(D_e, θ_+)).

## Findings

**1. (Medium – missing hypothesis) A4, line 50: q_e(c)=min(D_e,(θ_e)_+) presumes U_e ~ Uniform[0,1] and payment D_e·1(e∈W).**
E_{U_e}[D_e 1(A_e + D_e U_e ≤ B_e)] = D_e·F(θ_e/D_e). This equals min(D_e, θ_+) only for F(x)=min(1,x_+). With any other U-law the inequality q_e(c^t)−q_e(c) ≤ min(t,Δ) does not follow from the shown algebra (it relies on F being 1-Lipschitz with slope 1). Also B_e non-increase (line 45) and Δ ≥ 0 need U_h ≥ 0. Verification: confirm CONTRACT.txt fixes U_e Uniform[0,1], nonnegative, ties measure-zero.

**2. (Low – unstated step) A4, line 55: the sup is taken over 0≤t≤D_e(c), but the lemma at line 50 is only proved for t≤D_e(c).**
Reports t∈(D_e(c), c_e] are not covered in this file. They are harmless: every c-feasible flow has f_e ≤ D_e(c) ≤ t, so c^t has the same feasible set as c and q_e(c^t)=q_e(c) (this is DAG_BASELINE lines 10–13). The file should cite that fact explicitly; otherwise "0 ≤ y_e−z_e ≤ …" is stated for a sup over a domain that excludes some lower reports.

**3. (Info – scope) A1 is one-sided.** For t > c_e, D_h(c^t)=min(A+t,B) is not determined by D_h(c), D_h(c^0) (e.g. when D_h(c^0)=D_h(c)). The file only claims lower reports, so no error, but A1 cannot be reused for upward deviations.

## Verified steps (independently rechecked)

- **A1, h≠e:** each cut-capacity sum in the prefix/suffix min-cut formula contains t at most once, so D_h(c^t)=min(A+t,B). Then min(min(A+c_e,B), t+min(A,B)) = min(A+c_e,B,A+t,B+t) = min(A+t,B) for t≤c_e. Holds whether A<B or A≥B, and when A=+∞.
- **A1, h=e:** s→tail(e) and head(e)→t flows cannot use e (would close a cycle), so D_e(c^t)=min(t,P); D_e(c^0)=0.
- **A2:** immediate from A1. δ_eh≤D_e(c): keep h-containing paths of an optimal flow, delete those through e; deleted mass ≤ f_e ≤ D_e(c). Incomparable ⇒ 0.
- **A3:** same single flow f gives δ_eh ≤ f_e for all e; antichain ⇒ Σ_{e∈A} f_e ≤ |f| = D_h(c). Length-L variant correct.
- **A4 algebra:** A_e(c)−A_e(c^t) ≤ S_{C*}(c)−S_{C*}(c^t) with C* optimal at c^t; θ bound; q_e(c^t) ≤ min(t,θ_++Δ) uses D_e(c^t)≤t; q_e(c) ≥ min(t,θ_+) uses t≤D_e(c); case split θ_+≥t / θ_+<t gives ≤ min(t,Δ).
- Zeros: c_e=0 or D_e(c)=0 collapse to t=0 and all δ_eh=0 — consistent.
- Side check: every edge on an s-t path lies in some minimal cut (S = vertices not reachable from head(e)), so A_e is a finite minimum.

## Scope limitations

CONTRACT.txt (definitions of y_e, z_e, U distribution, tie-breaking, K cut family) is not in the packet; Finding 1 is therefore a hypothesis check, not a confirmed defect. No exact graph checks were run.

## Verdict

**Findings (non-blocking):** A1–A3 are correct as stated. A4 is correct given U_e~Uniform[0,1], U≥0, payment D_e·1(e∈W), plus the omitted (true) remark that reports in (D_e,c_e] change nothing.
