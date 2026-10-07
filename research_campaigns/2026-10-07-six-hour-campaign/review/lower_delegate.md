**Static review / derivation only. No tools were run, no files inspected on disk; everything below is reasoned from the supplied text.**

## Targets, distinguished

- **Target A** (every eligible rule): a growing family with minimax subsidy ratio B ≫ log K/log log K.
- **Target B** (envelope only): a growing family with Σ_e y_e(c) ≫ U(K)·T(c) for the specific envelope y of THEOREM.txt.

Neither was achieved. What is delivered: three proved lemmas that (i) exactly characterise where envelope excess can come from, (ii) kill the two most natural amplification routes for both targets with explicit K and T, and (iii) isolate the load-bearing unresolved inequality.

Notation as in THEOREM.txt: c^t=(t,c_{-e}); for fixed U_{-e}, A_t = min over structural cuts C∋e of Σ_{h∈C\e} D_h(c^t)U_h, B_t = min over cuts C∌e of their score, d_t = D_e(c^t) = min(t,D_e(c)) (THEOREM (2)); z_e(t,c_{-e}) = E[min(d_t,(B_t−A_t)_+)] (THEOREM (4)). Facts used from the supplied text: D_h is nondecreasing in every report (§2); D_h is independent of c_e when h is path-incomparable to e (§3).

## Lemma 1 (antichain-cut networks are safe for the envelope)

If every inclusion-minimal structural cut is an antichain in the path order (equivalently h(C)=1 ∀C, i.e. H(G)=K), then z_e(t,c_{-e}) is nondecreasing in t for every e, every c; hence y=z at every profile.

*Proof.* Fix e, U_{-e}. Every h ≠ e in a cut containing e is incomparable to e, so by §3 each D_h(c^t), hence A_t, is constant in t. B_t is a min of sums of D_h(c^t)U_h with every D_h nondecreasing in t, so B_t is nondecreasing; d_t is nondecreasing. Thus min(d_t,(B_t−A_t)_+) is nondecreasing in t pointwise in U_{-e}; integrate. ∎

*Consequence.* On this class the envelope inherits whatever budget the base rule z has; CONTRACT states Σz ≤ U(K)T on all DAGs (from DAG_BASELINE.txt, not supplied—inherited, not re-verified here). TTSP ⊂ this class (induction: a minimal cut of a series composition lies in one factor; of a parallel composition is a union of incomparable factor cuts). Whether the class is strictly larger than TTSP is **unresolved**; every Wheatstone I tried (including with a bypass s→t) produces a cut of type {x,w,…} with x≺w, h=2. Any Target-B family must contain comparable co-cut pairs.

## Lemma 2 (per-edge envelope excess is bounded by comparable co-cut mass)

For every DAG, profile c and edge e, with ~ denoting path-comparability,

 y_e(c) − z_e(c) ≤ max_{C∋e} Σ_{h∈C\{e}, h~e} min(D_e(c), D_h(c)).

*Proof.* For t ≤ c_e: d_t ≤ d_c, B_t ≤ B_c, A_t ≤ A_c (monotonicity of D). Using that u↦min(d,u_+) is nondecreasing and 1-Lipschitz,
min(d_t,(B_t−A_t)_+) ≤ min(d_c,(B_c−A_t)_+) ≤ min(d_c,(B_c−A_c)_+) + (A_c−A_t) ≤ min(d_c,(B_c−A_c)_+) + (A_c−A_0),
where A_0 is at t=0. Let C* attain A_0; then A_c−A_0 ≤ a_{C*}(c)−a_{C*}(c^0) = Σ_{h∈C*\e}(D_h(c)−D_h(c^0))U_h ≤ max_{C∋e}Σ_{h∈C\e}(D_h(c)−D_h(c^0)). For incomparable h the increment is 0 (§3). For comparable h: take a flow attaining D_h(c) and delete its paths through e; the deleted h-flow is at most the e-flow ≤ D_e(c), and the remainder is feasible at c^0, so D_h(c)−D_h(c^0) ≤ min(D_e(c),D_h(c)). Take expectations, then sup over t. ∎

*Consequences.* (a) Σ_e y_e ≤ Σ_e z_e + Σ_e Φ_e(c), Φ_e := the RHS above; an obstruction to C·U(K) needs Σ_eΦ_e(c) ≥ (C·U(K)−U(K))T at the *same* profile—so it must come from edges e whose containing cuts hold comparable edges h with D_h ≈ D_e, bottlenecked through e. (b) Lowering e can only *lower* B (hurting e); the sole source of gain is the drop of A through comparable co-cut edges. This is exactly the mechanism of OBSTRUCTION.txt (w in {x,w,p} with D_w=x+ε), where the gain is capped by min(Y,W) ≤ ε=1/20—explaining the tiny δ≈4·10⁻⁶ there.

## Lemma 3 (parallel composition is exactly neutral, for both targets)

Let G be the parallel composition of G_1,…,G_n (sharing only s,t). Then for every profile: D_e, z_e, y_e for e∈E_i coincide with their values computed in G_i alone; T=ΣT_i; K=ΠK_i; L=max L_i; and the minimax ratio satisfies B(G)=max_i B(G_i).

*Proof.* Every s–t path lies in one factor (acyclicity, shared vertices only s,t), so flows and D_e are factorwise. Minimal cuts are exactly unions of one minimal cut per factor; a score is a sum over factors, so the global minimiser is the union of factor minimisers, and for e∈E_i the event e∈W depends only on U_{E_i}. (Ties: among cuts differing in a positive-D edge, probability 0; cuts differing only in zero-D edges contain the same positive-D edges, and z_e=0 when D_e=0.) Own-report changes of e stay in E_i, so y_e^G=y_e^{G_i}. For B: factorwise rules compose (v_G(S)=Σ_i v_{G_i}(S∩E_i), budgets add), giving B(G) ≤ max B(G_i); conversely restrict any G-rule to profiles with all other factors reported 0, where v_G(S)=v_{G_i}(S∩E_i) and T=T_i, giving B(G_i) ≤ B(G). ∎

*Explicit calculation.* n parallel copies of the OBSTRUCTION network (k=10): K=5^n, T=n, L=4, H=6n (h-values 1,1,1,2,1), so Σy ≤ 12T while log K/log log K→∞: **not** an obstruction. n parallel copies of the k-pool layered game: K=k^n, B = B_k ~ log k/log log k while log K/log log K ~ n log k/log(n log k): parallel amplification of the layered certificate gives **no** stronger Target-A bound. Both targets therefore require growth that is *not* parallel composition.

## What was tried and failed (not certificates)

- Series chain e_1,pool_1,…,e_n,pool_n (all caps T): lowering e_i to t rescales every D to t, so Pr(e_i∈W) is unchanged and y=z, Σy=T, K=2n. No excess.
- Wheatstone with w replaced by a pool: puts m uniforms into the containing cut, which then never wins; excess vanishes.
- Single "wide-y" Wheatstone (x=T=1, y large, c_w ≥ x+y): Lemma 2 allows excess up to Φ_x ≈ 1; a heuristic estimate suggests y_x−z_x of order T/4 by reporting t≈1/2. **Unverified** (no exact integral done); even if true it is a bounded-gadget constant and Lemma 3 shows it cannot be amplified in parallel.

## Load-bearing unresolved inequality

For Target B one needs a family with Σ_e Φ_e(c)/T → ∞ faster than U(K) **and** actual attainment of the Lemma-2 slack, i.e. many edges e, at one profile, each with a comparable co-cut partner h carrying D_h≈D_e whose A-drop is not wasted on a small competing term (the min(Y,W) cap in OBSTRUCTION). No such family is exhibited; series and parallel composition provably do not produce it. For Target A, any lower bound beyond U(K) must come from a family where B is not a maximum over independent factors; the weighted transition theorem's d-level chain was not extended here.

## Limitations

Static derivation; Lemma 1's budget consequence depends on the unsupplied base-z bound; the "antichain-cut ⊋ TTSP?" question and the wide-y Wheatstone estimate are unresolved; no novelty claimed for any lemma.
