# Terminal slack cuts above a failed Lmin suffix

## Theorem

Let `v` be an exact game, let `phi=Lmin(v)`, and let `N=H dot-union L`
be a strict payoff boundary, with `H` the richer suffix.  Suppose
`s_phi(H)>0`.  Among the coalitions in the Boolean interval

```text
[H,N] = {H union D : D subseteq L},
```

choose a slack maximizer `C=H union D`, and put `E=L\D`.  Then:

1. `D` and `E` are both nonempty, `C` is proper, and
   `s_phi(C)>s_phi(H)`.
2. For every core point `z` exact on `C`, with `Delta=z-phi` and
   `S=s_phi(C)`,

   ```text
   Delta_d <= 0  (d in D),       Delta_e >= 0  (e in E),
   Delta(E)=S,
   ```

   with a strict inequality of each sign for at least one player.
3. The terminal cut satisfies the adjacent marginal inequalities

   ```text
   v(C)-v(C\{d}) <= phi_d                 (d in D),
   v(C union {e})-v(C) >= phi_e           (e in E).
   ```

4. Normalize any strict Lmin cover of `H` to rich load one, write its
   poorer loads as `c_i<1`, and put `q_i=1-c_i`.  Every exactifier above
   satisfies the transport budget

   ```text
   sum_(d in D) q_d (-Delta_d)
     >= sum_(e in E) q_e Delta_e > 0.       (TC)
   ```

   Consequently, with `q_E=min_(e in E)q_e`,

   ```text
   q_E s_phi(C) <= sum_(d in D) q_d s_phi({d}).      (TS)
   ```

   In a singleton-normalized game the right side is
   `sum_(d in D)q_d phi_d`.

5. The cut is necessarily payoff-inverted: there are `d in D` and `e in E`
   with

   ```text
   Delta_d<0<Delta_e,       phi_d <= phi_e. (PI)
   ```

Thus a failed payoff suffix cannot terminate at another payoff suffix.  Its
maximal slack continuation is a punctured suffix: it contains a losing
poorer player while excluding a weakly richer gaining poorer player.  Its
slack is financed by a weighted singleton-sacrifice budget.

## Proof

The universal slack-ascent theorem gives an `i in L` for which
`s_phi(H union {i})>s_phi(H)`.  Since `s_phi(N)=0`, every maximizer `C` of
slack on `[H,N]` has the asserted form with nonempty proper `D subset L`, and
its slack `S` is strictly larger than the root slack.

For `d in D` and `e in E`, interval maximality gives

```text
s_phi(C\{d}) <= s_phi(C),       s_phi(C union {e}) <= s_phi(C).
```

Expanding the two slack differences yields the displayed marginal
inequalities.  Exactness supplies `z in Core(v)` with `z(C)=v(C)`.  Core
feasibility on the two neighboring coalitions now gives

```text
z_d = z(C)-z(C\{d})
    <= v(C)-v(C\{d}) <= phi_d,

z_e = z(C union {e})-z(C)
    >= v(C union {e})-v(C) >= phi_e.
```

Moreover, `Delta(C)=-S` and efficiency gives `Delta(E)=S>0`, so at least
one excluded poorer player gains strictly.

Let `lambda` be any normalized strict cover of `H`.  Every supported
coalition is tight at `phi`, hence `Delta(T)>=0`.  Summing with the cover
weights and using efficiency gives

```text
0 <= sum_T lambda_T Delta(T)
   = Delta(H)+sum_(i in L)c_i Delta_i
   = -sum_(i in L)q_i Delta_i.
```

Separating `D` and `E` proves `(TC)`.  Its right side is positive because
every `q_e>0` and some `Delta_e>0`; consequently some `d in D` has
`Delta_d<0`.

Since `Delta(E)=S`, the weighted gain is at least `q_E S`.  Core feasibility
on the singleton `{d}` gives
`-Delta_d<=phi_d-v({d})=s_phi({d})`.  Applying these two bounds to `(TC)`
proves `(TS)`.

Finally suppose every losing member of `D` had strictly larger Lmin payoff
than every gaining member of `E`.  Along a sufficiently short segment from
`phi` toward `z`, all strict payoff-stratum gaps are preserved.  The first
payoff stratum changed by the segment would then contain a gain and no loss,
so the sorted payoff vector would lexicographically improve.  This
contradicts `phi=Lmin(v)`.  Hence `(PI)` holds.

## What this adds

Universal slack ascent is local and cannot simply be iterated: after adding
one poorer player, the coalition need not be a payoff suffix and Lmin duality
does not automatically furnish another strict cover.  The terminal-cut
argument bypasses that obstruction by maximizing over the whole interval and
using exactness on the terminal coalition.

The conclusion is dimension-free and structural.  It reduces every failed
boundary to a sign-separated, deficit-weighted exchange cut with a forced
payoff inversion.  It does not yet classify which inverted cuts are
realizable, and it does not by itself resolve a broader monotonicity or
exact-partition conjecture.

The exact-rational audit is `src/verify_terminal_slack_cut.py`, with output
in `results/terminal_slack_cut.json`.  It recomputes the terminal cut, the
neighbor inequalities that force the signs for every exactifier, and the
displayed defining exactifiers for the five-player pure-star, three-trace,
and four-co-singleton mechanisms.  The audit is not proof evidence.
