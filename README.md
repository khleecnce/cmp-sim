# CMP-Sim

[![tests](https://img.shields.io/badge/tests-898%20passing-brightgreen)](#)
[![validation](https://img.shields.io/badge/literature%20gate-4%20datasets%20within%20%C2%B115%25-brightgreen)](#validation)
[![accuracy](https://img.shields.io/badge/trend-18.9%25%20median%2C%20440%20points-blue)](#2-how-accurate-is-it-on-every-axis-cmp-sim-accuracy)
[![scale](https://img.shields.io/badge/absolute%20rate-24%2F35%20within%203x-yellow)](#2-how-accurate-is-it-on-every-axis-cmp-sim-accuracy)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A physics-based simulator for **Chemical Mechanical Planarization**. Given a
slurry formulation, a pad, a conditioner and tool settings, it predicts what a
supplier or fab would otherwise have to measure: removal rate, within-wafer
non-uniformity, the radial profile, dishing and erosion on patterned wafers,
pad-life drift, and a scratch-risk index.

Every number it uses carries a source. Every number it cannot source is `null`
with a `TODO(owner)` rather than a plausible-looking invention, and every result
carries the warnings that tell you where not to trust it.

**Feed it your own measurements and the model re-fits itself** — see
[Learning from your own data](#learning-from-your-own-data). It opens only the
physical factors your data can actually identify, locks the rest, and tells you
which experiment to run next.

Each **film** and each **abrasive type** is learned separately, never pooled —
the differences between them are too large to average. See
[the 3D tool view](#the-3d-tool-view-tool) for the click-to-enter-data UI, and
[Abrasive type](#abrasive-type-ceria-is-not-silica-but-harder) for why ceria and
silica cannot share a term.

## Run it

```bash
git clone https://github.com/khleecnce/cmp-sim && cd cmp-sim
python3 -m venv .venv && .venv/bin/pip install --upgrade pip setuptools
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q          # 567 tests
.venv/bin/python -m cmp_sim.api        # web UI at http://127.0.0.1:8765
```

macOS: double-click `CMP-Sim.command` instead.

### Hosting it

Set `CMPSIM_TOKEN` and every route — the page included — requires `?t=<token>`
or an `X-CMPSim-Token` header. Leave it unset and a local run stays open, so a
laptop user is not asked for a key they would have to give themselves. The
repository ships a `vercel.json`; `.vercelignore` keeps the function to the
~4 MB it actually imports.

---

## Quick start

**Double-click `CMP-Sim.command`** in Finder. It builds the environment on first
run, starts the local server and opens the UI. Nothing leaves the machine.

Or from a shell:

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip      # editable installs need a recent pip
.venv/bin/pip install -e ".[dev]"

# one recipe in, one JSON result out
.venv/bin/cmp-sim run examples/oxide_baseline.yaml --out result.json

# vary one parameter and see where the physics changes underneath you
.venv/bin/cmp-sim sweep examples/cu_damascene.yaml pressure_psi 1 4 --steps 4

# what physics is available, and what each bundle suits
.venv/bin/cmp-sim profiles

# fit the model to your own measurements
.venv/bin/cmp-sim fit examples/oxide_baseline.yaml mylog.csv

# reproduce the validation table below (does Preston's law hold?)
.venv/bin/cmp-sim validate --gate 15

# score against EVERY measured point, not just the P*V sweeps
.venv/bin/cmp-sim accuracy                     # all 320 points, all axes
.venv/bin/cmp-sim accuracy --axis slurry_ph    # one axis at a time
.venv/bin/cmp-sim accuracy --json              # machine-readable

# interactive web UI (standard library only, no web framework)
.venv/bin/python -m cmp_sim.api          # -> http://127.0.0.1:8765

# two UIs over the same engine:
#   GET  /        the form view  — every input on one page
#   GET  /tool    the 3D tool view — click a part of the polisher to enter
#                 its data (see below)

# the same engine over HTTP, standard library only:
#   POST /api/simulate   one run           GET /api/meta   films, packs, pads, disks
#   POST /api/sweep      vary one input    GET /api/model  constants + sources
#                                          GET /api/accuracy  measured error

# 930 tests
.venv/bin/python -m pytest -q
```

Worked examples for every supported film are in `examples/`: copper damascene,
tungsten plug, blanket oxide, STI with ceria, SiC substrate, silicon substrate,
multi-zone uniformity — and `snag_solder.yaml`, which **deliberately refuses to
run** because no published source gives a SnAg Preston coefficient, alongside
`snag_solder_screening.yaml`, which supplies the input it asks for and runs as a
ranking.

## Validation

Two different questions, answered separately, because conflating them is how a
model comes to look better than it is.

### 1. Does Preston's law hold? (`cmp-sim validate`)

Preston has exactly one free constant, `Kp`. A dataset that sweeps pressure and
speed at fixed chemistry therefore tests the *shape* the model predicts, with
`Kp` fitted by least squares within each chemistry group. Reported error is the
residual of that fit.

A dataset that splits into several chemistry groups is judged on **all** its
points, not on its best group — `cmp-sim validate` prints both. Selecting the
best group is a cherry-pick, and it had been flattering two datasets here
(see *A gate that could be passed by picking a subset* below).

| dataset | n | read | MAPE | max | notes |
|---|---:|---|---:|---:|---|
| EP3161098B1 TEOS / silica, 6 chem × 3 psi | 18 | table | **7.0%** | 14.9% | one group; verified against the EPO PDF |
| US9499721B2 TEOS / colloidal silica | 22 | table | **7.1%** | — | 6 groups; best group 1.9% over 4 pts |
| US8142675B2 Pt / alumina, pure pressure sweep | 4 | table | **12.3%** | 20.9% | verified against the patent PDF |
| Mariscal 2020 PETEOS / ceria 3x3 | 9 | digitized | **12.9%** | 20.5% | ECS JSS 9 044008 |
| US6564116B2 oxide Taguchi L25 | 25 | table | 18.9% | — | 5 groups; best group 12.6% over 5 pts |
| EP3161098B1 W / silica, 6 chem × 3 psi | 18 | table | 40.2% | — | 6 groups; best group 10.6%. **Super-Prestonian — see below** |
| Wang SiC / ceria-H2O2 50-run DOE | 24 | SI table | 33.2% | 88.8% | chemically limited — see below |
| US6918821B2 Cu / IC1000 | 6 | table | 44.1% | 161.2% | **deliberate counter-example** |

**Four independent published sources within ±15%**, which is success criterion
(a). All patent datasets were re-verified by the parent agent against the
official PDFs, not accepted on a subagent's report:

* **EP3161098B1** — Table 5B's 36 rates (W and TEOS, six compositions, three
  pressures) read from the EPO publication server's PDF, because Google Patents
  serves a bot-wall stub for this document. The patent contradicts itself twice
  — paragraph [0090] says "1.0, 2.0, 3.0 psi" where the table header says
  1.5/2.0/3.0, and Table 5A labels the compositions 5A–5F where Table 5B prints
  them 1A–1F. Both are recorded in the dataset files and resolved in favour of
  the table, with the reasoning stated rather than the ambiguity hidden.
* **US8142675B2** — TABLE P prints 220/470/750/1020 Å/min at 2/4/6/7 psi; all
  four values and the 200/18 rpm, 70 ml/min conditions match exactly.
* **US6564116B2** — the L25 array is OCR-scrambled in the PDF, so the factor
  assignment was verified *arithmetically* against the patent's own TABLE 3
  response table (which the transcription does not contain and so could not
  have been fitted to). Nine of ten factor levels reproduce to five decimal
  places. The tenth implicates a single cell; it is flagged in the file and
  **left as transcribed** rather than back-solved to the value that would make
  the arithmetic close.
* **US6918821B2** — all six IC1000 rows match TABLE 1 exactly.

### A gate that could be passed by picking a subset

`best_fit_per_dataset` takes the largest sweep per dataset and breaks ties by
*lower* MAPE. When a dataset splits into equally sized chemistry groups, that
tie-break reports whichever group the model fits best.

Adding EP3161098B1's tungsten table exposed it: six chemistries × three
pressures fit as six groups of three, with MAPEs from 10.6% to 59.1%. The gate
counted the dataset at **10.6%** and passed it. Across all 18 printed points the
error is **40.2%**, and it does not pass.

The gate now judges every split dataset on all its points and names the ones it
declines to count. The immediate cost was honest: US6564116B2, which had been
counted as passing at 12.6%, is 18.9% overall and no longer counts. The pass
total stayed at four only because the two EP3161098B1 datasets were added in the
same change.

### Tungsten is super-Prestonian, and that is a measurement, not a miss

EP3161098B1's W error (40.2%) is the most informative number in the table,
because the same patent measured TEOS **on the same wafers, with the same
slurry, over the same pressure axis**:

| 1.5 → 3.0 psi (a 2× pressure change) | rate ratio |
|---|---|
| TEOS (oxide) | 1.82× … 2.17× — Preston predicts 2.00× |
| W | 2.06× … 5.69× |

Because the oxide leg sits on Preston, the tungsten leg's 5.69× cannot be blamed
on the tool, the pad, or the pressure calibration. W's rate is limited by its
passivating WOx film: more pressure strips passivation faster, which feeds back
into the chemical term — a feedback oxide does not have.

This is the clearest data-level support in the repo for the owner's requirement
that **each film be learned separately**. A single global pressure exponent
cannot be right for both films at once, and the 40.2% is the size of the error
it produces when forced.

### The two datasets that fail, and why they are kept

**US6918821B2 (Cu, 44%) is a counter-example on purpose.** At 1.5 psi the
measured rate *falls* as speed rises (425 → 419 → 250 Å/min from 60 to 200 rpm),
the opposite of `MRR ~ P·V`; at 4 psi it climbs steeply. Fitted separately, the
4 psi branch alone gives **13.4%** and the 1.5 psi branch **60.3%** — no single
`Kp` can serve both, so the joint fit lands between them at 44.1%.

The reason to keep it is that **the model predicts its own failure.** The regime
detector computes λ = h_film / roughness from pressure, speed, pad and flow
alone — it never sees a measured rate — and flags exactly one of the six
conditions as leaving boundary lubrication:

| condition | λ | regime | measured |
|---|---:|---|---|
| 1.5 psi, 60 rpm | 0.37 | boundary | 425 |
| 1.5 psi, 120 rpm | 0.75 | boundary | 419 |
| **1.5 psi, 200 rpm** | **1.24** | **mixed** | **250 — the collapse** |
| 4.0 psi, 60/120/200 rpm | 0.14–0.47 | boundary | 594 / 1384 / 1636 |

The λ thresholds are Bhushan's standard tribology boundaries, not tuned here.
The patent corroborates it independently: its own inventive pads A, B and C do
**not** invert at 1.5 psi (pad A: 874 → 1293 → 1439 Å/min); only the
conventional IC1000 comparison pad does, which is the patent's whole thesis.
A test asserts this dataset keeps failing, so nobody can quietly tune `Kp` to it.

**SiC (32%) is chemically rate-limited.** In that DOE the factor ranking is pH >
head rpm > CeO₂ > pressure, and pump flow and polish time outrank composition
entirely. A mechanical `P·V` law cannot explain it, whatever `Kp` you choose.

### 2. How accurate is it on *every* axis? (`cmp-sim accuracy`)

The gate above only admits datasets that sweep pressure or speed — 6 of 49
files here, about 40% of the measured points. That left the slurry axes this
simulator exists to predict (pH, oxidizer, loading, particle size) **never
scored against a measurement at all**. `cmp-sim accuracy` scores all 440
points on whichever axis each dataset varies:

| axis | datasets | median error |
|---|---:|---:|
| abrasive particle size | 11 | **11.2%** |
| oxidizer | 12 | 21.3% |
| abrasive loading | 13 | 22.4% |
| pressure | 15 | 20.6% |
| pH | 15 | 25.3% |
| velocity | 6 | 38.8% |

**Overall: median 18.9% shape error, 21.3% leave-one-out**, over 48 of 52
datasets and 440 measured points. 36 of 48 beat "predict this dataset's
average" — the baseline that says whether the physics contributed anything.
(36, not 37: five blocks reproduce that baseline *exactly*, and a tie is not a
win. See `docs/limits.md` §57.)

> The corpus now has an **even** number of scored datasets, so the two usual
> median conventions no longer coincide: 18.9% taking the upper of the two
> middle datasets (`sorted(e)[n//2]`, quoted here and pinned by the regression
> tests) versus 18.6% interpolating between them (`statistics.median`, printed
> by `tools/readme_numbers.py`). Both are stated rather than one being chosen,
> because quoting whichever reads lower is exactly the selection this
> repository forbids.

> **⚠ And 11 of those 48 datasets were partly graded on their own fit.** A pack
> constant records its provenance in `source:`; when that string names a scored
> dataset whose own pack it belongs to, on an axis that dataset sweeps, the
> constant came from those rows. Eleven datasets declare
> `used_for_calibration: false` while being cited that way — and they sit at
> the good end of the table (the 2nd, 3rd and 5th best blocks are among them).
> Excluding them, plus the four that already admit calibration, leaves **33
> datasets at a held-out median of 19.5%**. That is the number to judge the
> model by. Note that this exclusion moves the headline the *wrong* way, which
> is why it is permitted here: dropping datasets to lower a median is
> forbidden, declining to count the ones the model was fitted to is not.
> Measured by `tools/calibration_flag_audit.py`, documented in
> `docs/limits.md` §32.

> **⚠ Read the 18.9% as a ranking claim, not a rate claim.** It says the model
> follows the *trend* to about 20%. It does **not** say it predicts absolute
> removal rate to 20%. Those fail independently, and on this corpus the second
> one often fails: `cmp-sim accuracy` now prints a `scale` column (median
> measured ÷ predicted absolute rate) beside it, and
> **11 of 35 comparable datasets are off by more than 3×** —
> `lai2001_cu_alumina` scores an excellent 8.7% shape while over-predicting
> absolute rate by **17.5×**. 24 of 35 are calibrated within 3×; the remaining
> 12 datasets print `-` because their own notes forbid absolute comparison
> (benchtop coupons, scaled units, shear-rheological polishing). Use this
> simulator to rank and optimise conditions; re-anchor `Kp` against your own
> tool with `cmp-sim fit` (one wafer is enough — see below) before trusting an
> Å/min number. See limit 11 in `docs/limits.md`.

Four numbers, and they mean different things:

* **shape** — scale fitted to the dataset, so it measures the *trend*. Use it
  when asking "which way does it move, and by how much"; no pack's `Kp` is
  calibrated to another lab's tool, so absolute agreement is not the question.
* **scale** — median measured ÷ predicted *absolute* rate. 1.0× is calibrated;
  9.7× is not. Independent of shape, and the number to check before quoting an
  Å/min.
* **leave-one-out** — fit on n−1 points, predict the held-out one. The only
  number quotable as accuracy without qualification.
* **predict-the-mean** — the baseline. A model that cannot beat it added
  nothing on that dataset.

The pressure and velocity medians look poor next to the ±15% gate because they
include the three datasets that are *supposed* to fail (SiC, quartz,
rheological). Restricted to clean `P·V` sweeps the same axis runs 12–23%.

**Velocity is worst for a reason no refit can remove.** US 6,918,821 B2
measures copper rate *falling* as speed rises at 1.5 psi (425 → 419 → 250
Å/min) while rising at 4.0 psi — an inversion the Preston form cannot express
at any exponent. Fitting isolated velocity groups gives exponents of −0.42,
+0.62, +0.86, +0.86 and +1.10 where Preston says 1.0, and the two datasets
require *opposite* pressure dependences, so no single exponent (or exponent
function) serves both. Two candidate regime criteria were tested and refused
because each turned out to be the operating point relabelled: the lubrication
λ equals the pseudo-Sommerfeld number *V/p* to five digits, and
`summit_saturation` equals 0.00739·*P* to six. Gating on either would be a
pressure threshold fitted to one patent's low-force arm. The miss is left
visible instead; see `docs/derivations.md`.

**What these medians do *not* tell you.** Five axes contain a limit the corpus
cannot lift, and averaging over them hides it. `docs/limits.md` is the index:
one entry per refusal, each naming the measurement that establishes it, the refit
that was rejected and its cost, and the experiment that would resolve it. The
short version:

| limit | consequence for the table above |
|---|---|
| velocity exponent unresolvable (−0.42 to 1.10) | the 44.1% cannot be fitted away |
| oxidiser sign flips with *pressure* | jani2025's 51.2% is a named miss, not a bad constant |
| ceria's pH response is *not unimodal* | netzband's 49.2% is structural; the better fit costs dandu2009 492.6% |
| out-of-range pH is warned, not gated | measured: no separation, z = −0.15 |
| three datasets sit at their replicate-noise floor | `sic2026` 34.0% is *better* than its own 38.5% reproducibility |

That last row matters when reading any single number here: only 5 datasets carry
genuine replicates, so for the rest the achievable floor is **unknown**. A 15%
error against an unmeasured floor is not the same claim as a 15% error against a
measured 2%.

### What "done" means here, and why the bar is 15%

Completion is defined as **median shape error ≤ 15%**, and the project is not
there yet: the corpus sits at **18.9%**, so a check in
`tests/test_definition_of_done.py` is deliberately red. It is not marked xfail,
because a green tick would hide a measured shortfall.

The bar is not a round number. Grant every scored dataset a free exponent on its
own best axis, fitted on the very rows being scored, with no requirement that
datasets agree — something no physical model can do, since a model *shares* its
constants. That oracle reaches only **12.4%** (from 16.9%). So **≤10% sits above
the ceiling of the entire "add another law" programme**, and 15% is the narrow
band a shared-constant model can occupy. The bound moves as the corpus grows —
it was 11.9% at 46 datasets, 12.4% at 52 — so a test re-derives it rather than
trusting a recorded number.

This is a *modelling* ceiling, not a noise floor. Published reproducibility in
this corpus spans 1.5% to 37%, which makes 15% lenient against jani2025 and
strict against miranda2004; the two arguments are kept apart on purpose, and
tests enforce the separation.

**How much of the model the data actually reaches.** A median says nothing about
which constants were tested. Counting, per pack, the parameters whose axis some
dataset actually sweeps:

| pack | exercised / fitted | backed by |
|---|---|---|
| `cu_h2o2_bta` | 54 / 79 (68%) | 86 rows, 11 swept axes |
| `oxide_silica` | 46 / 74 (62%) | 119 rows, 9 axes |
| `sti_ceria` | 55 / 91 (60%) | 63 rows, 9 axes |
| `w_fe_oxidizer` | 31 / 59 (53%) | 38 rows, 6 axes |
| `sic_alumina_kmno4` | 39 / 84 (46%) | 30 rows, 3 axes |
| `sic_ceria_h2o2` | 35 / 77 (45%) | 65 rows, 7 axes |
| `cu_alkaline_benzenesulfonic` | 13 / 39 (33%) | 17 rows, 2 axes |
| `oxide_silica_aminosilane` | 10 / 63 (16%) | 22 rows, 2 axes |
| `oxide_silica_anionic` | 7 / 62 (11%) | 7 rows, 1 axis |
| **total** | **290 / 628 (46%)** | |

So **46% of fitted parameters are exercised and 338 are not** — and the spread
matters more than the total. `cu_h2o2_bta` rests on 86 rows across eleven axes;
`oxide_silica_anionic` rests on a single 7-row pH sweep. Two packs reporting
similar shape errors are not equally supported.

The 46% is an **upper bound**, for three reasons: the mapping credits every
constant in a group to one sweep (four pH constants, one curve); *exercised* is
not *validated* (`sic_alumina_kmno4`'s pH constants were fitted at pH 9–11 but
its datasets only reach pH 2–6, so they test the term in extrapolation); and 512
user-supplied inputs — pad geometry, grooves, conditioner schedule, platen
temperatures — are excluded rather than counted as evidence.

This is not an argument for deleting the unexercised 338. A Preston coefficient
can be sound without a sweep in this corpus. It is an argument against reading
one median as if it certified the whole model. Details:
`tests/test_parameter_evidence_inventory.py`.

Finding this changed the model materially. Scored this way the first time, the
median was **42.8%** and 16 of 36 datasets lost to predicting the mean. Two
causes, both silent:

* **pH did nothing.** The packs carried `ph_peak` and `ph_ref` but no width, so
  the term never ran — a pH 2→10 scan returned one number while the measurement
  moved 81×. An accepted-and-ignored parameter is worse than a missing one,
  because the scan still looks like an answer.
* **the particle-size exponent had the wrong sign** on 8 of 10 sweeps. Every
  pack used the derived −0.84; the data run −0.45 to +1.08 and split cleanly by
  **abrasive**, not by film (ceria +0.87, alumina +0.29, silica −0.05).
* **zero oxidizer was answered two different wrong ways.** The peaked branch
  skipped `C = 0`, so it fell through to a Langmuir term that returns 3.10
  there — copper polishing 3× faster with no oxidizer at all, which inverted
  Du 2004 completely (25107 Å/min predicted against 203 measured). Handling
  `C = 0` then exposed the opposite bug: with no floor declared the
  multiplicative term gave exactly **0.0 Å/min**, against 187 measured.
  Chemistry scales removal; it does not switch it off.

Each fix is pinned by a test that names the dataset and the failure, so the
next change cannot quietly undo it.

## Film coverage

| film | pack | profile chosen by `auto` | status |
|---|---|---|---|
| oxide (TEOS/PETEOS) | `oxide_silica` | `dielectric_blanket` | validated, 1.9–12.9% |
| STI / oxide-ceria | `sti_ceria` | `dielectric_patterned` | validated |
| Cu | `cu_h2o2_bta` | `soft_metal_plastic` | counter-example kept failing |
| W | `w_fe_oxidizer` | `hard_metal_passivation` | Kp from two patent tables |
| poly-Si | `poly_si_alkaline` | `semiconductor_alkaline` | Kp derived, arithmetic in pack |
| Si substrate | `si_substrate_alkaline` | `semiconductor_alkaline` | Kp derived at 0.62 psi |
| SiC | `sic_ceria_h2o2` | `chemically_limited` | rankings only, see below |
| SnAg solder | `snag_solder` | `soft_metal_plastic` | **graded unestablished**: rankings only |

SnAg is not merely under-documented — it is a film the industry gave up
polishing. The only primary 300 mm report eliminated both pH windows it tried
(alkaline etched the tin away leaving Ni₃Sn₄ intermetallic; acidic-to-neutral
scratched it), and fine-pitch tin bumps are planarized by **fly-cutting**
instead. Tin is amphoteric, sits at ~0.6 of its melting point at room
temperature so it creeps rather than fractures, and is ~6x softer than copper
on the same indenter.

So it is graded `unestablished`, and the two examples show both halves of that:

* `snag_solder.yaml` **refuses to run** — given only a film name it will not guess.
* `snag_solder_screening.yaml` supplies the one input it asks for (an intended
  pH) and runs, on a Kp estimated from hardness via Archard. The rate carries a
  warning that it is a **ranking, not a prediction**: there is no published SnAg
  rate to bound it, so a 10x error would not be caught.

Four measured rates take it to **±1.4% cross-validated**. That is the intended
path for any unestablished film: refuse → rank → predict.

## Choosing a model: by situation, not by film

The appropriate physics is set by the **regime**, not by the material name.
SiC and sapphire are different films in the same regime; copper at 1.5 psi and
copper at 4 psi are the same film in different regimes.

So the simulator classifies each run on eight axes (contact branch, pad asperity
regime, summit saturation, lubrication, film class, rate limit, topography, pad
state) and picks a **profile** — a bundle of orthogonal physics layers — to suit
it. `auto` decides; naming a profile explicitly is respected, and mismatches are
warned about rather than silently corrected.

```
cmp-sim profiles        # list profiles, their layers and what each suits
```

An axis that cannot be computed is reported as undetermined, never defaulted.
The common case is `contact_branch`, which needs the chemically modified surface
hardness — rarely published, and assuming it would silently fix the sign of the
particle-size exponent in P3.

## Learning from your own data

The literature anchors the model; your tool is not the literature. Give it
measured rates and it fits its **named physical factors** to them — and reports
a **leave-one-out** accuracy, each point predicted by a fit that never saw it.

```bash
cmp-sim fit examples/oxide_baseline.yaml mylog.csv
cmp-sim fit --template            # see the CSV format
```

or paste the CSV straight into the web UI.

```
fitted to 12 measurement(s) from mylog.csv

  Kp            2.9932e-13 m/Pa
  accuracy      +/-0.8% leave-one-out  (scale alone: 56.0%)

  fitted factors
    abrasive_half_wt_pct             3.079
    pressure_exponent                0.694

  locked (this dataset cannot identify them)
    velocity_exponent                velocity varies by only 0% across these runs
    activation_energy_kj_per_mol     temperature_c varies by only 0% across these runs
```

### Why factors rather than a fresh regression each time
* **Identifiability.** A free-form fit walks into degenerate parameters. The
  Kaufman oxidizer curve's peak position and shape exponent cannot be separated
  from sub-peak data at all — which is why the copper pack uses a one-parameter
  Langmuir form. Named factors make that refusable instead of silent.
* **Extrapolation.** A fitted physical factor keeps the structure: doubling
  pressure still doubles rate. A black-box surface collapses outside its box.
* **Convergence on few points.** Every free parameter costs data.

### How overfitting is prevented
A factor unlocks only if **all three** hold:

1. its input actually varies across the runs (≥15% spread);
2. the dataset can afford it (3 measurements per free parameter);
3. it improves the **cross-validated** error — never the in-sample error, which
   more parameters always improve.

The gain threshold comes from a noise study rather than taste: at 8% measurement
scatter on data that genuinely obeys Preston's law, a 2% threshold admitted a
spurious pressure exponent in 2 runs out of 5. A true departure cuts the error
by 60–70%, so the floor is 25%.

Recovery against synthetic tools with known answers:

| truth | recovered | cross-validated error |
|---|---|---|
| pressure exponent 0.65 | 0.652 | 19.6% → 0.12% |
| abrasive C_half 3.0 wt% | 3.08 | 94.4% → 1.0% |
| activation energy 45 kJ/mol | 44.5 | 122.9% → 1.1% |
| both 0.70 and 3.0 at once, 5% noise | 0.68 / 3.08 | 56.2% → 2.8% |
| Preston-true data | **nothing unlocked** | unchanged |

That last row matters most: given data with no departure to find, the fitter
finds none and says the factors were rejected as overfitting.

## Sweeps

`POST /api/sweep` varies one of eleven parameters across up to 50 points, and
each point carries its own regime. A sweep that crosses a boundary says so
instead of drawing one confident trend through physics that changed underneath
it — which is precisely how the copper anomaly above would otherwise be hidden.

## What the model is, layer by layer

| phase | module | what it adds |
|---|---|---|
| P1 | `models/preston.py` | `MRR = Kp·P·V` with the rotary-tool velocity field and zone pressure |
| P2 | `models/contact_gw.py` | Greenwood–Williamson asperity contact: why `MRR ∝ P` is true at all |
| P3 | `models/luo_dornfeld.py` | abrasive count, size and load sharing; exponents computed, not tabulated |
| P4 | `models/chemical_rate.py` | oxidizer / inhibitor / ceria / pH through softened surface hardness, plus Arrhenius |
| P5 | `models/uniformity.py` | radial profile, lubrication regime, slurry starvation |
| P6 | `models/pattern_density.py` | step-height evolution, dishing, erosion, selectivity |
| P7 | `pad/wear.py` | glazing vs conditioning, disk ageing, pad-life drift |
| P8 | `models/defect_proxy.py` | scratch risk from the large-particle tail |

Derivations, assumptions and validity ranges are in
[`docs/derivations.md`](docs/derivations.md).

### The one rule that holds the model together

Each layer contributes a **dimensionless multiplier that is exactly 1.0 at its
pack's reference condition**:

```
Kp_eff = kp_m_per_pa · Π factor_i
```

A pack's `Kp` was back-calculated from a measurement that already contained that
pad, that chemistry and that abrasive. Multiplying in an *absolute* chemical or
contact term counts the same physics twice — in the inherited project that
mistake collapsed a Cu rate 20x before it was caught. Tests pin every factor to
1.0 at reference.

## Slurry: the part that matters most

* **`data/params/additives.yaml`** — 55 additives across 9 roles, mapped to 9
  films with mechanism, direction, adsorption model and citation, plus 15
  documented synergy/antagonism pairs. 221 sourced values, 33 honest nulls.
* **`data/params/abrasives.yaml`** — 11 particle types × 9 films: hardness,
  modulus, isoelectric point, concentration and size exponents, shape and the
  large-particle tail. It records explicitly that **ceria (Si–O–Ce chemisorption)
  and silica (physisorption) must not share a concentration term** — their
  per-collision efficiency differs by ~10⁷.
* **`slurry/rheology.py`** — viscosity (Krieger–Dougherty), ionic strength,
  Debye length and the electrostatic regime derived from the formulation.
* **`slurry/formulation.py`** — maps a human recipe onto the keys the physics
  actually reads. **An input that is not wired comes back as a warning rather
  than being silently dropped**, because an ignored input plus a confident
  number is the worst possible output.

## The 3D tool view (`/tool`)

An Applied Materials Reflexion-style 300 mm polisher you click to enter data:
three platens, four carrier heads on a rotating carousel, a load cup at the
fourth station, a conditioner sweep arm and a slurry delivery arm per platen.

It is **geometry, not a rendered image**, and that is the point — the picture is
driven by the recipe rather than decorating it:

* the platen and head turn at the rpm you entered;
* the pad's grooves are redrawn at the groove pitch you entered;
* the slurry stream's density and speed follow the flow rate;
* **the wafer's colour map is the simulated radial removal profile.**

A bitmap could do none of this, and would have to be clicked by guessing pixel
boxes. Here a click is a raycast onto the actual mesh.

One honesty constraint is built into the picture: the solver predicts **one**
polish step, so exactly one platen may claim to be simulated. Platen 1 is
active — it carries the painted wafer and gets the slurry stream and full rpm.
The other two turn slowly and are labelled inactive rather than implying three
simulated steps.

three.js is vendored under `cmp_sim/web/vendor/`, so the view works on a fab
machine with no outbound network. If WebGL is unavailable the scene is replaced
by a notice and every part stays reachable from the parts list.

### The four input stations

Data is entered where it belongs on the tool, not in one flat form:

| station | click | inputs |
|---|---|---|
| wafer cart / loading | load cup | film stack — Cu, W, oxide, poly-Si, Si, SiC, SnAg |
| operation | platen, carousel, head, frame | pressure, platen & head rpm, flow, time, slurry and platen temperature, retaining-ring pressure, zone pressures |
| slurry supply | slurry bottle, nozzle | abrasive kind, D50, D99, wt%, pH, temperature, two additives |
| polishing unit | pad, conditioner disk | pad and disk **by product name** |

A pad is chosen the way it is in a fab — as a product — and every property the
name implies comes from `cmp_sim/data/consumables.yaml` with its source shown.
Typing a Shore D directly is the fallback, not the interface.

### The shell holds no physics, and a test enforces it

A model change must not require touching the UI, and a UI change must not be
able to alter the model:

| kind of number | home | reaches the browser via |
|---|---|---|
| physics constants | `data/params/*.yaml`, `models/` | `GET /api/model?film=` |
| named pad / disk properties | `data/consumables.yaml` | `GET /api/meta` |
| operating conditions | the recipe being edited | the drawers themselves |

The **model inspector** (`Model & sources` in the tool view) lists every constant
the engine will use for the current film with its source and confidence, lets one
be edited, and re-predicts — through the ordinary `recipe.params` override path,
so the edit is reported as owner-supplied and can never pass for a sourced value.

`tests/test_web_holds_no_physics_constants.py` greps every browser-loaded file
for an assignment of a literal to any key a parameter pack declares. The
forbidden vocabulary is **derived from the packs at test time**, so adding a
constant to a pack immediately makes hard-coding it in the UI a failure with no
test edit. This caught a real divergence: `tool.html` had been drawing 2.0 mm
groove pitch while the engine computed with the sourced 3.05 mm, and nothing
failed because nothing compared them.

`.venv/bin/python tools/web_smoke.py` starts the server and exercises every
route, including a full-chemistry prediction with a named pad and disk.

## Abrasive type: ceria is not "silica but harder"

The abrasive is the first thing a slurry formulator changes, so it has its own
layer (`slurry/abrasive_effects.py`) rather than being a lookup key.

Each parameter pack declares the abrasive its `Kp` was calibrated with:

| pack | `reference_abrasive` |
|---|---|
| `oxide_silica`, `poly_si_alkaline`, `si_substrate_alkaline` | `colloidal_silica` |
| `sti_ceria`, `sic_ceria_h2o2` | `ceria` |
| `cu_h2o2_bta`, `w_fe_oxidizer` | `alumina` |

Swapping the abrasive invalidates the **absolute scale**, not just the
exponents. Rescaling it honestly requires a ratio measured on the *same tool,
same recipe, abrasive-only-swapped* — the only comparison where pad, pressure,
velocity, pH and oxidizer all cancel. Those comparisons are rare, so the ratio
table is mostly `null`, **and the emptiness is the honest state**: where no
ratio exists the rate is flagged `ranking_only` — good for comparing recipes,
not for quoting a number. Both UIs show this directly under the rate.

A hardness ranking is **not** used as a substitute, because it does not predict
CMP rate. Ceria (6.4 GPa) removes oxide ~3× faster than the much harder alumina
route, and silica polishes sapphire. Ceria's advantage on oxide is chemical
tooth (Si–O–Ce), not indentation — which is also why **ceria is ~3× silica on
oxide but ~0.88× silica on Cu** (US5575885). One particle cannot carry one
global "strength".

A worked example of declining a number: US5575885's four-abrasive Cu table is a
genuine matched comparison *with* an abrasive-free control, but its abrasives
span 30–1300 nm. Since this model already has a particle-size term, applying
those ratios double-counts size — it drove the Cu example below the published
rate floor. The numbers and arithmetic are recorded; the values stay `null` with
`TODO(owner)`.

## Honest limits — read before quoting a number

1. **This predicts rankings far better than absolute values.** Each `Kp` is
   back-calculated from one published point; outside that regime linear
   extrapolation can be badly wrong. `core/sanity.py` checks every result
   against a published per-film rate envelope and labels anything outside it
   `IMPLAUSIBLE` — that check caught three real bugs during development,
   including a SiC pack that had silently inherited the *oxide* `Kp` and
   over-predicted by 128x.
2. **Absolute rate needs your data.** Give it ≥3 measured points and recalibrate
   `Kp`; nothing else fixes it.
3. **Validity boundaries are enforced, not assumed.** Asperity saturation (where
   GW and Preston linearity both fail), plasticity, pad wear beyond the 10 min
   of measured data, pressures outside the measured 2–5 psi, full-film
   lubrication, and slurry starvation all raise warnings instead of returning a
   confident number.
4. **Not modelled:** post-CMP cleaning, particle shape in the removal term (it
   is recorded and used only for defect risk), real layout maps (pattern density
   is a scalar), and cross-term chemical couplings (the terms multiply as if
   independent, and say so).
5. **Pad-life drift and the defect index are diagnostics** and are never
   multiplied into the rate — a test enforces this.

## Provenance

`legacy/` holds inherited, independently verified modules (FabSim, commit
e385ed1) — Preston/kinematics, GW contact, the MIT pattern-density framework,
the Jeong 2024 glazing measurements, DLVO and the chemistry layer. They are
wrapped, never re-derived; each commit names the functions it reused. Values
live in YAML packs, so **a new process is a data file, not a code change**.

**No proprietary or employer-owned data was used.** Every parameter traces to a
published patent, article, thesis or open dataset. Full texts of copyrighted
articles are deliberately excluded — `papers/` is in `.gitignore` and no
article text is tracked here or in the history; the citations tell you exactly
which table or figure to look at if you want to verify a number.

## Licence

MIT — see [LICENSE](LICENSE), which also explains what the licence does and
does not cover with respect to the cited literature.
