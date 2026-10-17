**Provisional verdict: no substantive errors found in reviewed scope; two external dependencies unverifiable.** Most important item: the §7 "sharp 9/4" claim rests on properties of the Huber TCWM primitive (exact scalar bound 3/2 *and* membership in the §5 hypothesis class) that are asserted, not shown, in this packet.

## Findings

**1. (Medium – unverified dependency) §7 sharpness, `P4_SIGNED_BINARY_LIFT_OBSTRUCTION.txt:232–236`.**
The lower bound (8) is proven internally (checked below). Sharpness needs (i) the Huber primitive's total payment ≤ (3/2)·(term value) uniformly, and (ii) that it is symmetric, homogeneous, aggregate-price, coalition-covering, TCWM, and continuous at r=1 so that it belongs to the family being bounded. Neither is in the snapshot. Verification: cite/attach the primitive's defining file and check ell(1)=s(1), L(r)=ell(r)/r nonincreasing, and sup_r [L(r)+s(r)] = 3/2.

**2. (Low – unverified dependency) §3 and §7 logarithmic-primitive constants, lines 105–108, 238–240.**
"Imbalanced cost → 1+c" and "balanced unit pair total 2c" are external. The arithmetic (1/2)[2(1+c)+2c]=1+2c>2 and (3/2)(1+c) are correct given these inputs (c≈0.543>1/2). Verification: check the min2 price formulas at r→0 and r=1.

**3. (Low – quantifier ambiguity) §6 classification, lines 174–176, 207–208.**
Necessity sets "one pure unit owner at each vertex" of the induced P4/paw. The theorem statement quantifies over profiles but not explicitly over ownership models; if ownership is fixed (e.g., one owner holding adjacent vertices), the four-owner coalition game may not exist. Suggest stating "for every ownership model with pure owners at the obstruction's vertices" or quantifying existence of an ownership model.

**4. (Info) Implicit regularity.** (1) requires a_i,b_i measurable and the integral finite; harmless since H=v finite, but should be stated.

## Checked and confirmed
- P4 unit values (lines 12–13), F=min(x0+x2,x1+x3,x1+x2): all correct.
- Zero-coalition step: f_i=0, min(a_i,b_i)=0 a.e., nonedge ⇒ no cross support. Complete bipartite subgraphs of P4 are exactly edges and the two stars (P4 has no C4). Identity (2) holds per component; 2≠1, and 2≤2ρ−1 ⇒ ρ≥3/2. Correct.
- (4): F=L+R+min(U,V) verified in all four sign cases. (5) verified; 0≤H−F≤F/2. H(0123)=2, H(12)=1, H(012)=H(123)=3/2. Correct.
- H_t excess t·min(U−V,R) / (1−t)·min(V−U,L); distortion max(1+t,2−t) attained at (0,M,1,1). Correct.
- Scalar step (6): ell=O(r) from finite funding, liminf s≥1 from coverage, L nonincreasing from TCWM on the full-long-resource owner (valid as a constraint on the universal price function even when the long input is split, e.g. b+d), L(1)≥1/2 from symmetry. Correct.
- §5 profiles (0,M,1,1)/(1,1,M,0): F=1, bounds 3/2+t and 3/2+(1−t). §7 profiles (0,M,1,M)/(M,1,M,0): F=1, three imbalanced terms with weights t,1−t,t and t,1−t,1−t. (8) correct.
- Paw: F_paw formula (3) verified including the D>A case; unit values 2, 3/2, 1, 1, 0, 0 correct. Zeros BD, CD force D's opposite support ⊆{A}; concavity of min(a_A,·) gives (7); 1/2≤0 contradiction. Correct.
- Forbidden-subgraph proof (energy note §4) and formula (2) for complete multipartite: correct.

## Scope limitations
Snapshot only; no tests run; CONE_L1 and primitive-definition files, root barrier note, and the checker script were not supplied. Priority not assessed.

## Verdict
Findings (minor): internal proofs are sound; §7 sharpness and §3 limiting constants depend on unsupplied primitive properties; §6 ownership quantifier should be made explicit.
