**Provisional verdict: no findings in reviewed scope.** The most consequential step, the exact rational drop (8), reproduces under independent hand recomputation: I(x0)−I(x1) = [−3/80000 + 28501/456000000 − 15/19000000 + 1/24000000]/6 = 11060/2736000000 = 553/136800000. The certified delta denominator 2^8·3^24·5^5·7·19 and numerator 121476081746439−23750000000000 = 97726081746439 also check.

## Findings

**No invalid steps identified.** Verified items:

- **Five minimal cuts (1)** (lines 28–30): paths are {x,z_j,r_i}, {y,w,r_i}, {x,h,w,r_i}, {p,r_i}. Any minimal cut containing r_1 must contain r_2 and is then {r_1,r_2}; otherwise the cut is a bridge cut ∪ {p}. {x,y},{Z,w},{y,Z,h},{x,w} are the Wheatstone cuts. Correct; grand value min(…,1)=1.
- **Effective capacities (2)**: D_x=x≤1, D_y=ε, D_zj=min(2,x,1)=x, D_w=min(2,ε+min(x,h),1)=x+ε (exactly 1 at x1, still attainable), D_h=min(2,x,w)=x, D_p=1, D_r=1/2. Correct for the CONTRACT definition (max feasible edge flow, any total).
- **Conditional formula (3)**: A=P+min(Y,W); B=min(P+Z+min(W,Y+H),R); min(W,Y+H)−min(Y,W)=min(H,(W−Y)_+) in both cases Y≤W and W<Y. Payment min(x,(B−A)_+) is the correct fixed-x conditional expression (THEOREM §4/§9 do not need co-cut independence for this identity, only d>0 and probability-zero ties).
- **Ideal comparison (4)**: q_k≤q_∞; Z≥1 forces equality since R−P−A≤1; both in [0,1]. Direction correct: lower bound at x0, upper bound at x1.
- **Simplex bound (5)**: {u∈[0,1]^k: Σu<1/x} ⊂ nonnegative simplex of volume (1/x)^k/k!; upper bound, correct. Only x0 is needed. Ratio (10/9)/(k+1)<1 for k≥10, so delta_k≥delta_10.
- **Moments (6)**: ∫_0^ε j a^{j−1}(1−a/ε)(1−a/b)da = ε^j/(j+1) − jε^{j+1}/((j+1)(j+2)b). Correct.
- **Stop-loss (84),(86)**: R−P = S−1 with widths (1/2,1/2,1); reflection gives E[(S−c)_+]=E[(2−c−S)_+]; inclusion–exclusion with 1/(4!·W), W=1/4, yields factor 1/6; subsets {3},{1,2},… vanish for 0≤a≤ε, and for c'=1−x−a≤1/10<1/2 only the empty term survives. Correct. min(x,y_+)=y_+−(y−x)_+ gives (7).
- **Scope separation**: lines 3, 13–14, 107–110 correctly confine the result to this rule; consistent with CONTRACT lines 10–14 that all-mechanism impossibility needs a separate certificate.

**Minor (informational, severity low):**
- Line 100: "Coverage and the U(5) budget argument survive" is asserted, not proved here. Value preservation v_D(S)=v_c(S) does hold in any graph (feasible coalition flows are grand flows, D≤c), and THEOREM §5 uses only cut count and independence, so this is plausible, but it is not needed for the theorem.
- The DAG definition of D_e is inherited from CONTRACT lines 19–20, not restated; the obstruction refutes exactly that normalization, not every conceivable DAG capping. Line 13 wording is consistent with this.

## Scope limitations
- No code executed; rational identities verified by hand only (intermediate values: F(1)=0.90487625, G(1)=−37089/24000000, G(1/2)=−17176/96000000).
- Did not re-derive the generic rule derivation in THEOREM §4 beyond confirming the fixed-x conditional identity.
- The margin (≈3.25e−6) is small; correctness depends entirely on the moment/stop-loss algebra, which I checked but a machine-exact recomputation is still advisable.

## Verdict
**No findings in reviewed scope.** Suggested verification: exact-rational script recomputing (6)–(8) and a Monte-Carlo sanity check of z_x(9/10)>z_x(19/20) at k=10 (expected gap ≈4e−6, so ≥10^12 samples would be needed for direct confirmation; prefer exact integration of (7)).
