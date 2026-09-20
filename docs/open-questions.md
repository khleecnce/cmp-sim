# Open questions for the owner

`STATUS.md` keeps one line per item; the reasoning lives here. Each entry says
what was measured, what the model does now, and what the owner has to decide.
Nothing here has been resolved by picking whichever value made a test green.

---

## 1. The λ roughness scale (blocks the regime layer)

The second legacy transfer (`8ed1649`) replaced three `base.yaml` pad-surface
constants with sourced literature values:

| key | before (`estimated`) | after (`literature`) | source |
|---|---|---|---|
| `pad_E_star_pa` | 1.0e9 Pa | 1.316e8 Pa | Bozkaya & Müftü 2009 JES 156(12) H890, median of 3 groups |
| `pad_asperity_radius_m` | 5.0e-6 m | 5.0e-5 m | Bozkaya 2009 Table I, Shi & Ring 2010 |
| `pad_height_beta_inv_m` | 0.3e-6 m | 2.0e-6 m | Sorooshian 2005 thesis p.358, Fig. A.1 |

The old numbers were order-of-magnitude guesses with no primary source, so the
replacement is right on evidence grounds. But λ = h/σ is inversely proportional
to σ, and σ just grew 6.7×.

The consequence is not cosmetic. The US 6,918,821 B2 copper dataset is the
project's strongest validation result precisely because the model is *not*
fitted there — the regime detector sees only pressure, speed, pad and flow, and
flags the single condition (1.5 psi / 200 rpm) where the measured rate collapses
against Preston. That flag fired at λ = 1.24, above the boundary threshold of
1.0. With the new σ, every condition lands at λ ≤ 0.19:

```
(1.5 psi,  60 rpm)  boundary  λ = 0.056
(1.5 psi, 120 rpm)  boundary  λ = 0.112
(1.5 psi, 200 rpm)  boundary  λ = 0.187   <- must NOT be "boundary"
(4.0 psi,  60 rpm)  boundary  λ = 0.021
(4.0 psi, 120 rpm)  boundary  λ = 0.042
(4.0 psi, 200 rpm)  boundary  λ = 0.070
```

The *ordering* is still physically correct — λ rises with speed and falls with
load, and `test_lambda_rises_with_speed_and_falls_with_load` still passes. Only
the absolute scale moved, and with it the threshold crossing.

Restoring the old trio makes three of the four failing tests pass. That was run
as a diagnostic and reverted; it is not a fix, because it trades sourced numbers
for guesses.

**The decision — and a measurement that narrows it sharply.**

Before asking which threshold to use: what roughness values does the corpus
actually contain, and does *any* of them put the collapse point above λ = 1?
Sweeping σ with everything else held fixed (λ ∝ 1/σ):

| σ source | σ [µm] | λ(1.5 psi, 200 rpm) | regime at the collapse point |
|---|---:|---:|---|
| old unsourced estimate (pre-transfer) | 0.300 | **1.245** | mixed |
| Zhou 2018, new pad Rq (stated in text) | 0.474 | 0.788 | boundary |
| Zhou 2018, in-use Rq, 0.9 psi / 30 min | 0.680 | 0.549 | boundary |
| Zhou 2018, in-use Rq, 1.26 psi / 300 min | 1.115 | 0.335 | boundary |
| Sorooshian 2005 exponential scale (current) | 2.000 | 0.187 | boundary |
| Bozkaya 2009 Table I Gaussian σ_s | 5.000 | 0.075 | boundary |

σ would have to be **0.373 µm** for that point to sit exactly at λ = 1.

The uncomfortable part: **no sourced roughness value in the corpus puts the
collapse point above the boundary threshold.** The only value that does is the
unsourced 0.3 µm — and it is *below the roughness of a brand-new pad*
(Zhou et al. 2018, ECS JSS 7(6) P295, doi:10.1149/2.0011806jss, measures
Rq = 0.474 µm before any use, rising to 0.68–1.1 µm in service). A polished pad
is not smoother than a new one.

So reading 2 below does not rescue the result either. Swapping the exponential
scale for a properly-measured RMS roughness moves λ from 0.187 to 0.788 — much
closer, still boundary.

**What this means for the validation claim.** The λ = 1.24 crossing was an
artifact of a roughness constant chosen without a source, and the claim "the
model predicts where it fails, against an absolute threshold" does not survive
sourcing that constant. What *does* survive, and is unaffected by σ because a
pure rescale cannot change an ordering:

- λ rises with speed and falls with load, as hydrodynamics requires
  (`test_lambda_rises_with_speed_and_falls_with_load`).
- The collapse point is the **maximum** λ of all six conditions — 3.3× the λ of
  the same pressure at 60 rpm and 2.7× the runner-up. The *ranking* still
  singles out the right condition without seeing a rate. Locked in by
  `test_lambda_ranks_the_collapse_point_first_without_seeing_a_rate`.

The honest repair is therefore probably not a new threshold number but a
different kind of claim: flag the condition whose λ is anomalously high
*relative to the rest of the process window*, rather than against an absolute
cut that no sourced σ supports. That changes what the detector asserts, which
is the owner's call rather than a tuning knob — so it has not been made.

Two readings remain for the constant itself, and they are not equivalent:

1. **The thresholds belong to the old σ.** λ = 1.0 / 3.0 are the textbook
   boundary/mixed/full-film cuts, but they were last sanity-checked against
   σ = 0.3 µm, which the table shows was never physical.
2. **`pad_height_beta_inv_m` is the wrong quantity to divide by.** It is the
   scale of an *exponential* asperity-height distribution (1/β). The λ of
   lubrication theory is film thickness over *composite RMS roughness* — which
   the corpus does have, measured, in Zhou 2018. `base.yaml` itself warns that
   Bozkaya's Gaussian σ_s = 5 µm is a different distribution family and must
   not be substituted here; the same caution applies in reverse to using 1/β
   as an RMS.

Reading 2 is better supported — the corpus has a directly measured Rq for a
polyurethane pad, and using it is a strict improvement over dividing by a
distribution scale. It is just not sufficient on its own.

Tests parked on this: `test_only_the_collapse_point_leaves_the_boundary_regime[1.5-200]`,
`test_crossing_a_regime_boundary_is_warned_about`,
`test_a_load_beyond_the_contact_model_explains_itself_in_english`
(the last one stopped raising because the contact solver's bracket now spans the
500 psi probe at the softer modulus).

---

## 2. `sti_ceria`: cited pack vs cited envelope

The same transfer cut `sti_ceria`'s inherited silica loading terms and
re-declared them from Dandu, Peddeti & Babu 2009 (JES 156(12) H936,
doi:10.1149/1.3230624):

- `abrasive_wt_pct` 20 → 0.25 wt% (the paper's stated loading; 20 wt% was
  inherited from a colloidal-silica pack and was two orders out for a ceria STI
  slurry)
- `abrasive_conc_exponent` → −0.4295, read off Fig. 2a (60 nm ceria, pH 4:
  352.1 / 211.3 / 194.1 nm/min at 0.25 / 0.50 / 1.0 wt%)

Both are better sourced than what they replaced. Together they raise the example
recipe to 7,235 Å/min against a plausibility envelope of 200–6,000 Å/min — 1.2×
over. A negative exponent means more ceria removes less, so shrinking the
reference loading 80× pushes the rate up.

One of the two cited numbers is wrong for this recipe, and nothing in the data
picks the loser. Note that the same paper's Fig. 2b (180 nm Ferro calcined
ceria) has the *opposite* sign (n = +0.343): the concentration exponent is not a
material constant, it splits by particle size and type. The pack took Fig. 2a on
system proximity (60 nm). The envelope, meanwhile, is a published range for STI
oxide generally, not for this slurry.

Left failing rather than retuned. Retuning either number to land inside the
range would make the test green by taste.

---

## 3. Particle-size exponent: it splits by abrasive, not by film

Settled by data, and the original grouping was wrong. Measured sweeps:
ceria +0.87, alumina +0.29, silica −0.05. Within one abrasive the sweeps agree;
across abrasives they do not share a sign.

Leaving oxide at `null` was not the neutral choice it looked like — it selected
the derived −0.84, which has the wrong sign for 8 of 10 measured sweeps.

Any pack declaring this key must now scope it to its own abrasive and cite the
sweeps (enforced by `test_no_pack_declares_a_global_size_exponent`).

---

## 4. `contact_branch` without circular input

Decided via the pad-limited load criterion, in which particle size cancels:
Cu plastic, oxide/STI transition.

This did **not** unblock the P3 exponent derivation. Plastic α = 3/2 with
copper's measured χ = 1.0 gives n_C = −0.5 ("more abrasive removes less"),
violating the model's own bound — and α and χ are not independently adjustable.
The engine reports the branch and leaves the exponents `unverified`; loading is
fitted directly, which bypasses the conflict rather than resolving it.

**A depth limit no bookkeeping removes:** no nanoindentation of an actually
CMP-polished surface exists in the 324-paper corpus, and instruments resolve
~5 nm while an abrasive indents under 1 nm. Λ ∝ 1/H³, so a 2× error in hardness
is 8× in Λ.

---

## 5. Films with a missing constant

- **SnAg has no published Preston coefficient** (68 sourced numbers for it, no
  rate). It runs as a ranking on the Archard estimate and says so; four measured
  rates take it to ±1.4% cross-validated. No envelope exists to sanity-check the
  absolute rate, which the run states outright.
- **SiC inherits SiO₂'s modulus through its lineage** (92 vs ~450 GPa, and
  Λ ∝ E²). Blocked with `null` + `TODO(owner)`: the same inheritance route once
  carried the oxide Kp into this pack and over-predicted SiC by 128×.

---

## 6. Three judgement calls where measurements disagreed

Full derivations in `docs/predictive-accuracy.md`.

- `oxide_silica` loading `C_half = 4.4` — its two datasets want 0.6 (0.5–3 wt%)
  and 5.9 (5–25 wt%). The compromise costs both ~20%. A single Langmuir may not
  span that range.
- `sti_ceria` pH pools Dandu (81× swing, peak 4.5, TEOS) with Netzband (1.9×,
  rising to pH 10, thermal oxide) at 34% error; either alone is 20–26%. Probably
  two packs.
- Acid-side pH floors for `oxide_silica` and `cu_h2o2_bta` are 1%-of-peak
  bounds, not measurements — no dataset sweeps the acid side of their optima.
