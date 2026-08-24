# External review packet — PXC136 stationary singleton-witness bridge

Date: 2026-08-24

Status: internal proof and exact audit complete; no cooperative-game specialist review yet
Novelty status: unclaimed

## Result to review

Let `v` be an exact singleton-normalized TU game of total `T>0`.  Exactness
provides, for every player `r`, a core allocation `w^r` with `w^r_r=0`.
PXC136 proves that these witnesses admit one shared stationary circulation

```text
pi>=0, sum pi=1, F>=0, F_rr=0,
sum_i F_ri=pi_r=sum_i F_ir,
T F_r(S)>=pi_r v(S) for every r and every proper coalition S.
```

The allocation `y=T*pi` lies in the core and satisfies `y_i<=T/2`.  For any
two core allocations `x,z`, define

```text
Psi_stat=max sum_i[min(x_i,y_i)+min(z_i,y_i)]-T.
```

Then, with `a_i=min(x_i,z_i)` and `b_i=max(x_i,z_i)`, the exact identity is

```text
Psi_stat = O(x,z)-min sum_i dist(y_i,[a_i,b_i]) <= O(x,z).
```

The theorem also gives the complete rational LP dual, whose exact-game row
coefficients are coupled across roots by shared row and column potentials.
This is the proposed replacement for the factorized carrier-price dual.

The main hybrid-overlap theorem is **not claimed**.  The new open reduction is

```text
max(B_star,Psi_stat) >= [n/floor(n^2/4)] T.          (PXC136?)
```

## Proof dependency map

1. Exactness at singleton `{r}` plus `v({r})=0` gives `w^r_r=0`.
2. `P_ri=w^r_i/T` is a finite zero-diagonal stochastic matrix.
3. A stationary distribution exists; `F_ri=pi_r P_ri` satisfies the flow
   system.
4. `y=T*pi=sum_r pi_r w^r` is a core allocation.
5. Zero diagonal and stationarity give `pi_i<=1-pi_i`, hence `y_i<=T/2`.
6. The scalar interval-distance identity proves the bridge formula.
7. Ordinary rational LP duality gives PXC136e.

No verifier output is used in this proof.

## Exact controls

- PXC101: target-reaching stationary bridge.
- PXC104 and PXC118: target-reaching reciprocal controls.
- PXC125 positive-demand anchor: stationary bridge exceeds the target where
  the actual-top spectral bound does not.
- PXC90: faithful full-rank spectral boundary.
- Every balanced `G(p,k)`: the explicit stationary distribution

  ```text
  ((k-1)/(2k), (1/(2pk))^p, (1/(2k))^k)
  ```

  places `T*pi` coordinatewise between Lmin and Lmax, so `Psi_stat=O`.
- Complete archived six-player bank: 374 raw records, 373 distinct exact
  selector triples; `B_star` closes 321 and `Psi_stat` closes the remaining
  52, with no combined failure.
- Sharp complementary control:

  ```text
  x=(4/3,1/3,1/3,1/3,4/3,1/3),
  z=(1,1,0,0,1,1), T=4.
  ```

  Matched exact primal and dual certificates give
  `Psi_stat=45/17<8/3=B_star=O`.  Dropping the witness-core rows raises the
  relaxed bridge to `8/3`.

The archive result is finite evidence only.  It is not offered as a proof of
PXC136?.

## Reproduction

From the repository root:

```bash
/Users/maxf/miniforge3/bin/python3 \
  verifiers/divergence/verify_pxc136_stationary_witness_bridge.py \
  --output verifiers/divergence/pxc136_stationary_witness_bridge.json
```

The release script regenerates and byte-compares the pinned artifact.  The
driver uses exact rational Z3 feasibility for named/archive bridge witnesses
and exact Fraction replay of every returned flow.  The sharp failure control
has separately stored rational primal and dual certificates.

## Hostile mathematical questions

1. Does the converse interpretation of a zero-mass flow row require any
   qualification beyond choosing an arbitrary exact singleton witness?
2. Are the signs and free/nonnegative variables in PXC136e exactly correct?
3. Does `y_i<=T/2` have a simpler known proof or a known name in exact-game,
   credal-set, or cooperative allocation theory?
4. Is the stationary bridge already known as a Markov coupling, circulation
   of exposed faces, or coherent-lower-probability construction?
5. Does any known exactness/balancedness theorem imply PXC136? directly?
6. Can a counterexample to PXC136? be produced from a known exact game with a
   highly constrained singleton-witness hull?
7. Can the staged Lmin/Lmax Farkas identities be inserted into PXC136e to
   prove the spectral-deficit implication without reintroducing overlap as a
   scalar assumption?

## Prior-art search, 2026-08-24

The search covered exact-game characterizations, coherent lower
probabilities/credal sets, egalitarian core selections, assignment-game
leximin/leximax algorithms, and Markov/stationary allocation terminology.
Closest sources found were:

- Csóka, Herings and Kóczy, *Balancedness conditions for exact games*
  (2011), for exact-balanced characterizations.
- The coherent-lower-probability interpretation of normalized exact games in
  Štěpán/Studený-related exact-cone work.
- Mauri Masdeu's thesis on egalitarian core selections and exactification.
- Vazirani's and Gangam et al.'s recent primal-dual leximin/leximax work for
  structured cooperative games.

No source located in this search states the stationary singleton-witness
circulation, the universal `T/2` core ceiling obtained from it, or the bridge
LP/box-distance identity.  This is not a novelty conclusion; the terminology
may differ, and specialist review is required before any novelty claim.

## Requested verdict

Please report separately:

- correctness of PXC136a–e;
- correctness and reproducibility of the exact controls;
- whether PXC136? is a genuinely sharper route or a disguised restatement;
- significance if PXC136? is proved;
- known prior art under different terminology;
- critical, major, minor, and presentational issues.
