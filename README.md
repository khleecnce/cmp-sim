# CMP-Sim

A physics-based simulator for **Chemical Mechanical Planarization**. Given a
slurry formulation, a pad, a conditioner and tool settings, it predicts what a
supplier or fab would otherwise have to measure: removal rate, within-wafer
non-uniformity, the radial profile, dishing and erosion on patterned wafers,
pad-life drift, and a scratch-risk index.

Every number it uses carries a source. Every number it cannot source is `null`
with a `TODO(owner)` rather than a plausible-looking invention, and every result
carries the warnings that tell you where not to trust it.

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

# reproduce the validation table below
.venv/bin/cmp-sim validate --gate 15

# interactive web UI (standard library only, no web framework)
.venv/bin/python -m cmp_sim.api          # -> http://127.0.0.1:8765

# the same engine over HTTP, standard library only:
#   POST /api/simulate   one run           GET /api/meta   films, packs, profiles
#   POST /api/sweep      vary one input    GET /           the web UI

# 546 tests
.venv/bin/python -m pytest -q
```

Worked examples for every supported film are in `examples/`: copper damascene,
tungsten plug, blanket oxide, STI with ceria, SiC substrate, silicon substrate,
multi-zone uniformity — and `snag_solder.yaml`, which **deliberately refuses to
run** because no published source gives a SnAg Preston coefficient, alongside
`snag_solder_screening.yaml`, which supplies the input it asks for and runs as a
ranking.

## Validation

Preston has exactly one free constant, `Kp`. A dataset that sweeps pressure and
speed at fixed chemistry therefore tests the *shape* the model predicts, with
`Kp` fitted by least squares within each chemistry group. Reported error is the
residual of that fit.

| dataset | n | read | MAPE | max | notes |
|---|---:|---|---:|---:|---|
| US9499721B2 TEOS / colloidal silica | 4 | table | **1.9%** | 2.8% | patent example table |
| US8142675B2 Pt / alumina, pure pressure sweep | 4 | table | **12.3%** | 20.9% | verified against the patent PDF |
| US6564116B2 oxide Taguchi L25 | 5 | table | **12.6%** | 27.2% | response table reproduced to 5 d.p. |
| Mariscal 2020 PETEOS / ceria 3x3 | 9 | digitized | **12.9%** | 20.5% | ECS JSS 9 044008 |
| Wang SiC / ceria-H2O2 50-run DOE | 6 | SI table | 31.9% | 88.8% | chemically limited — see below |
| US6918821B2 Cu / IC1000 | 6 | table | 44.1% | 161.2% | **deliberate counter-example** |

**Four independent published sources within ±15%**, which is success criterion
(a). All three patent datasets were re-verified by the parent agent against the
official USPTO PDFs, not accepted on a subagent's report:

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
