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
python3 -m venv .venv && .venv/bin/pip install -e .

# one recipe in, one JSON result out
.venv/bin/python -m cmp_sim.cli run examples/oxide_baseline.yaml --out result.json

# interactive web UI (standard library only, no web framework)
.venv/bin/python -m cmp_sim.api          # -> http://127.0.0.1:8765

# reproduce the validation table below
.venv/bin/python -m cmp_sim.validate_cli --gate 15

# 217 tests
.venv/bin/python -m pytest -q
```

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
the opposite of `MRR ~ P·V`; at 4 psi it climbs steeply. No single `Kp` can fit
both branches. This is the patent's own subject — it claims conventional IC1000
performs poorly at reduced down force — and physically the low-pressure branch
is leaving boundary lubrication, outside Preston's validity range. A test
asserts this dataset keeps failing, so that nobody can quietly tune `Kp` to it.

**SiC (32%) is chemically rate-limited.** In that DOE the factor ranking is pH >
head rpm > CeO₂ > pressure, and pump flow and polish time outrank composition
entirely. A mechanical `P·V` law cannot explain it, whatever `Kp` you choose.

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
