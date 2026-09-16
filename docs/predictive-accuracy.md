# Predictive accuracy: what was measured, what failed, and why

Companion to `STATUS.md`, which stays short by design. This file holds the
detail behind the accuracy numbers so the checkpoint does not grow into a
report.

Regenerate every number here with:

```bash
.venv/bin/cmp-sim accuracy              # all axes
.venv/bin/cmp-sim accuracy --axis slurry_ph
.venv/bin/cmp-sim accuracy --json
```

## Why a second scoring path exists

`cmp-sim validate` asks one question well — does Preston's law hold — and only
admits datasets that sweep pressure or speed. That is **6 of 38 files** here,
about 40% of the measured points. The slurry axes this simulator exists to
predict (pH, oxidizer, loading, particle size) were therefore **never compared
to a measurement at all**, and 546 tests passed in that state.

`cmp-sim accuracy` scores all 320 points on whichever axis each dataset varies,
and reports three numbers that mean different things:

* **shape** — scale fitted to the dataset, so it measures the trend. No pack's
  `Kp` is calibrated to another lab's tool, so absolute agreement is not the
  question being asked.
* **leave-one-out** — fit on n−1 points, predict the held-out one. The only
  number quotable as accuracy without qualification.
* **predict-the-mean** — the baseline. A model that cannot beat "assume this
  dataset's average" contributed nothing on that dataset.

## Results
| dataset | n | MAPE | verdict |
|---|---:|---:|---|
| US9499721B2 TEOS/silica | 4 | 1.9% | pass |
| US8142675B2 Pt/alumina | 4 | 12.3% | pass |
| US6564116B2 oxide L25 | 5 | 12.6% | pass |
| Mariscal 2020 PETEOS/ceria | 9 | 12.9% | pass |
| Wang SiC DOE50 | 6 | 31.9% | **kept failing** — chemically limited: rate spans 5.2× at identical P·V, R²=0.09 |
| US6918821B2 Cu/IC1000 | 6 | 44.1% | **kept failing** — lubrication transition; the model flags the collapse point (λ=1.24) without seeing a rate |

Gate: 4 in-scope datasets within ±15% (need 3) → **PASS**

### Prediction on every axis (`cmp-sim accuracy`, 320 measured points)
| axis | datasets | median trend error |
|---|---:|---:|
| abrasive particle size | 9 | **8.7%** |
| abrasive loading | 8 | 34.6% |
| pH | 9 | 36.2% |
| oxidizer | 8 | 36.2% |
| pressure | 10 | 40.7% |
| velocity | 6 | 44.1% |

Overall **19.5%** trend / **23.6%** leave-one-out; 27/37 datasets beat
"predict this dataset's average". Pressure and velocity include the three
datasets kept as deliberate counter-examples; clean P·V sweeps run 12–23%.
Was 42.8% / 53.9% with 16 of 36 losing to the mean, before the three silent
failures above were fixed.

Worst remaining, with the reason rather than a plan: `son2021` ceria size
sweep 212% (a 3→100 nm range where the model is a power law and the data are
not), `cn109609035b` 95% (anionic-surfactant acidic silica whose optimum is
pH 2 served by a pack whose optimum is 11 — a different slurry system, pinned
by a test so it cannot be hidden), `entegris2022` 101% (loading FALLS 5× as
alumina rises 50×).

Factor recovery against synthetic tools with known answers: pressure exponent
0.65→0.652, abrasive C_half 3.0→3.08, Ea 45→44.5 kJ/mol, two effects at once
0.70/3.0→0.68/3.08. Preston-true data unlock nothing.


## The three silent failures

None was visible to a passing test suite, because nothing compared these axes
to a measurement.

### 1. pH did nothing

The packs carried `ph_peak` and `ph_ref` but no width parameter, so the term
never ran. A pH 2→10 scan returned **one number** while Dandu's measurement
moved 81×:

| pH | measured | model (before) |
|---:|---:|---:|
| 2 | 43 | 1062 |
| 4 | 3474 | 1062 |
| 5.5 | 3504 | 1062 |
| 10 | 643 | 1062 |

An accepted-and-ignored parameter is worse than a missing one: the scan still
looks like an answer.

**The fix, and why the peak is an input.** Five measured pH sweeps peak at pH
2, 4.5, 10 and 11 and span 1.2× to 81×. No single pH function produces all of
those, so the optimum is a property of the formulation and must be supplied —
the same discipline the oxidizer term already used. That leaves width and floor
free, which the data identify.

**The floor is asymmetric, with a mechanism.** Dandu's pH 2 point is 1.2% of
peak while pH 10 is 18%; one floor cannot be both, and forcing it costs 18
points of error. Below the optimum the abrasive and film approach the same
charge state and particles stop attaching; above it alkaline hydrolysis keeps
softening the film. Both floors must still be non-zero — setting the acid side
to zero made the response decay without bound and return 0.0 Å/min at pH 2,
where 109 Å/min is measured.

**Normalised to `ph_ref`, not to the optimum.** `Kp` was back-calculated from a
rate measured at `ph_ref`, so the raw peak-normalised term double-counted it
and reported 57% of the rate the pack was calibrated to produce. The existing
unity-invariant test caught this.

### 2. A size override was accepted and dropped

The solver read only `abrasive_size_nm`, while most datasets use
`abrasive_d50_nm`. Quadrupling the particle diameter returned a bit-identical
rate.

### 3. Zero oxidizer was wrong in both directions

The peaked branch required `C > 0`, so zero oxidizer fell through to a Langmuir
term that returns **3.10** there — copper polishing three times faster with no
oxidizer at all. Du 2004 came out inverted: 25107 Å/min predicted against 203
measured. Handling `C = 0` then exposed the opposite failure: with no floor
declared the multiplicative term gave **exactly 0.0 Å/min** against 187
measured. Chemistry scales removal; it does not switch it off.

## The size exponent belongs to the abrasive, not the film

An earlier conclusion in this project was that the exponent is per-film, and
oxide was left `null` on the grounds that its response is contradictory. It is
— but only because "oxide" pools experiments with different abrasives.
Regrouped by abrasive the scatter collapses:

| abrasive | exponent | sweeps | size range |
|---|---:|---:|---|
| ceria | **+0.87** | 3 | 3–211 nm |
| alumina | **+0.29** | 2 | 50–3500 nm |
| silica | **−0.05** | 5 | 12–160 nm, five different films |

Within one abrasive the sweeps agree; across abrasives they do not share a
sign. Ceria removes silica chemically at the contact (Cook 1990: one SiO₂
molecule per 24 collisions, against one per 5×10⁸ for silica), so a larger
ceria particle carries a proportionally larger reacted footprint. Silica
abrades mechanically — the regime Luo–Dornfeld derived, where the size
dependence cancels — which is why the derived exponent is right for silica and
wrong by a whole sign for ceria.

Leaving oxide `null` was **not** neutral: it selected the derived −0.84, wrong
in sign for 8 of the 10 measured sweeps. A null that silently picks a wrong
number is worse than a sourced approximation.

Nine of the ten size-sweep datasets were also pointed at `oxide_silica`
regardless of what they polished, so Cu/alumina and SiC/ceria runs were being
scored with the silica exponent.

## Where data disagreed, and what was chosen

These are judgement calls, marked `confidence: low` in the packs and pinned by
tests so they cannot be quietly re-tuned.

**Oxide loading saturation.** The two datasets want different constants:
us9499721b2 (0.5–3 wt%) wants `C_half` ≈ 0.6, us6564116b2 (5–25 wt%) wants 5.9.
Taking the first dataset's own optimum scored it at 7.3% but pushed the second
from 20.6% to 26.6%, with the residual climbing monotonically from 0.52 to 0.89
across the loading range — a systematic 2× over-prediction at 5 wt%, which is
the signature of a saturation that is too aggressive, not a random miss. The
pack carries the compromise (4.4, ~20% on both). Either the response is not a
single Langmuir over 0.5–25 wt%, or the two tools differ in slurry delivery.

**Ceria pH.** `sti_ceria` pools Dandu (81× swing, peak 4.5, TEOS) with Netzband
(1.9×, rises to pH 10, thermal oxide). Joint fit 34%; either alone is 20–26%.
A symmetric Gaussian cannot reproduce Dandu's shape anyway — it rises 22×
between pH 2 and 3.5, plateaus to 5.5, then steps down 3.5× — so 26.5% is the
floor for this functional form even fitted alone. These may need separate packs.

**SiC refuses a loading saturation.** Its six iso-condition series run −0.40 to
+1.43, and two *fall* with loading: Entegris US 2022/0315802 A1 measures
966.7 → 200 Å/min as alumina goes 0.1 → 5 wt%, a 5× drop for 50× more
abrasive. No saturating form produces that, so the constant stays `null`.
Consistent with SiC being chemically rate-limited (its P·V correlation is
R² = 0.09).

**Acid-side pH floors** for `oxide_silica` and `cu_h2o2_bta` are
order-of-magnitude bounds (1% of peak), not measurements: no dataset here
sweeps the acid side of their optima. They exist to stop the rate collapsing to
zero.

## Worst remaining errors, with reasons rather than plans

* **`son2021` ceria size sweep, 212%** — a 3→100 nm range where the model is a
  power law and the data are not.
* **`entegris2022` SiC loading, 101%** — rate falls 5× as loading rises 50×.
* **`cn109609035b`, 95%** — anionic-surfactant acidic silica whose optimum is
  near pH 2, served by a pack whose optimum is 11. Different slurry systems
  that happen to share a film and an abrasive mineral. Widening the bell to
  cover pH 2–12 would flatten the pH dependence everywhere and wreck Li 2021
  (currently 0.2%); a separate pack needs its own `Kp`, which no dataset here
  provides. A test asserts this stays bad so it cannot be hidden.

## Inherited blockers

- **Partly resolved.** `contact_branch` is now decided without any circular
  input, via the pad-limited load criterion
  `Lambda = 48*Hp*E^2/(pi^2*H^3) > 1` (Saka CIRP 2008 Eq. 3, Eusner JES 2009
  Fig. 15 pad hardness). Particle size cancels out. Cu = plastic (117),
  oxide/STI = transition (2.8), SiC = blocked (see below).
  **What it did NOT unblock:** the sign of the P3 particle-size exponent. The
  exponent relations assume `0 <= 1-alpha*chi <= 1`, but the plastic branch
  (alpha=3/2) with copper's measured load sharing (chi=1.0) gives
  `n_C = -0.5` — "more abrasive removes less". alpha and chi are not
  independently adjustable (chi comes from the measured area-pressure
  exponent), so the engine reports the branch and leaves the exponents
  `unverified` rather than publishing a negative concentration exponent.
  **Now partly settled by data:** nine measured loading sweeps were scored.
  Fitted on ISO-CONDITION series only (pooling non-iso rows fits the oxidizer
  with a concentration knob — the W patent moves oxidizer 0–3 wt%, an 8×
  effect, alongside loading), the saturating form gives Cu 9.5%, oxide 5.8%,
  W 9.3%. **SiC refuses**: its six series run −0.40 to +1.43 and two FALL with
  loading, which no saturating form produces, so it stays null. This still
  does not settle the alpha/chi conflict — it bypasses it by fitting the
  saturation directly instead of deriving the exponent.
  **A depth limit no bookkeeping removes:** no nanoindentation of an actually
  CMP-polished surface exists in the 324-paper corpus (every "surface" value is
  static immersion or as-deposited), and instruments resolve to ~5 nm while an
  abrasive indents under 1 nm. Lambda goes as 1/H^3, so 2x in hardness is 8x in
  Lambda. Cu at 117 survives that; oxide at 2.8 does not, which is why it is
  reported `transition` rather than assigned a side.
  **Settled by data, and my earlier grouping was wrong.** I had concluded the
  size exponent was per-FILM and left oxide null. Regrouping ten measured
  sweeps by ABRASIVE collapses the scatter that per-film grouping could not:
  ceria **+0.87** (3 sweeps, 3–211 nm), alumina **+0.29** (2 sweeps,
  50–3500 nm), silica **-0.05** (5 sweeps, 12–160 nm, five different films).
  Within one abrasive the sweeps agree; across abrasives they do not share a
  sign. Mechanism: ceria removes silica chemically at the contact (Cook: one
  SiO2 per 24 collisions vs one per 5e8 for silica), so a bigger particle
  carries a bigger reacted footprint; silica abrades mechanically, the regime
  the derivation assumes, where the size dependence cancels.
  Leaving oxide null was **not** neutral — it selected the derived -0.84,
  wrong in sign for 8 of the 10 sweeps. A null that silently picks a wrong
  number is worse than a sourced approximation.
- **SnAg has no published Preston coefficient** (68 sourced numbers, no rate;
  searched 320 local CMP papers, ScienceDirect and Crossref again this session).
  It runs as a ranking on the Archard estimate and says so; four measured rates
  take it to +/-1.4% cross-validated. Also means there is no envelope to
  sanity-check its absolute rate against, which the run now states outright.
- **RESOLVED.** The Cu oxidizer term now peaks instead of falling monotonically.
  Pinning the peak to a MEASURED position makes the decay scale a consequence
  of it, leaving one free parameter, which Du 2004 (doi:10.1149/1.1648029,
  6 points across the peak) supplies: 5.6% MAPE, beats plain Langmuir by >2x.
  Curvature is borrowed across a vol%/wt% axis difference and a glycine
  difference, recorded at `confidence: low`.
- **Three silent failures found by scoring the unscored axes.** None was
  visible to 546 passing tests, because nothing compared the slurry axes to a
  measurement:
  1. **pH did nothing.** Packs carried `ph_peak` and `ph_ref` but no width, so
     the term never ran: a pH 2→10 scan returned ONE number while Dandu's
     measurement moved 81×. An accepted-and-ignored parameter is worse than a
     missing one — the scan still looks like an answer.
  2. **`params: {abrasive_d50_nm}` was dropped.** The solver read only
     `abrasive_size_nm`, so quadrupling the diameter returned a bit-identical
     rate.
  3. **Zero oxidizer was wrong in both directions.** The peaked branch skipped
     `C = 0` and fell through to a Langmuir that returns 3.10 there (copper 3×
     faster with no oxidizer: 25107 Å/min predicted vs 203 measured). Fixing
     that exposed the opposite bug — with no floor declared the multiplicative
     term gave exactly **0.0 Å/min** against 187 measured.
  Also: nine of ten size-sweep datasets were pointed at `oxide_silica`
  regardless of what they polished, so Cu/alumina and SiC/ceria runs were
  scored with the silica exponent.
- **New, found while fixing the above:** SiC was inheriting SiO2's elastic
  modulus (92 GPa vs SiC's ~450) through its SiC -> sti_ceria -> oxide_silica
  lineage, and Lambda goes as E^2. Blocked with `value: null` + TODO(owner)
  rather than a handbook number: the same inheritance route once carried the
  oxide Kp into this pack and over-predicted SiC by 128x.
