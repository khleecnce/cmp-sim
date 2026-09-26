# Sorooshian 2005 — ILD CMP flow/velocity/pressure factorial (DIGITISED)

source: "Sorooshian, J. (2005), Fundamental Tribological, Thermal and Kinetic
  Attributes of Interlayer Dielectric, Tungsten and Shallow Trench Isolation
  Chemical Mechanical Planarization, PhD dissertation, Dept. of Chemical &
  Environmental Engineering, University of Arizona (Philipossian group).
  Chapter 4.3, pp. 175-189, Figures 4.4-4.15.
  Repository record: https://repository.arizona.edu/handle/10150/194809"
confidence: med
read_method: FIGURE (programmatic digitisation — see caveats below)

## Why this dataset was sought

`tools/velocity_thermal_probe.py` found a large one-sided residual on the
velocity axis (median b_V = -0.549 against b_P = -0.036) with exactly one
surviving zero-constant explanation, reactant starvation:
`MRR ~ P * V^(2/3) * Q^(1/3)`. The corpus held only ONE flow-varying dataset
(`yang2023_quartz_ceria_L25`), and it fails a Preston P-linearity audit
(its own b_P = -1.276), so it could not arbitrate. This dissertation is a full
factorial in all three constrained variables and can decide all three legs.

## Experimental conditions (TEXT — reliable, p. 176)

| factor | levels |
|---|---|
| film | thermal SiO2, 100 mm wafers |
| slurry | Fujimi PL-4217 fumed silica, 12.5 wt%, pH 11 |
| slurry flow | 40, 120 cc/min (2 levels, 3x span) |
| sliding velocity | 0.32, 0.64, 0.96 m/s = 40, 80, 120 rpm (3 levels, 3x span) |
| wafer pressure | 2, 4, 6 psi (3 levels, 3x span) |
| pad groove | flat, XY, perforated |
| pad thickness | 1.39, 2.03 mm |
| replication | every p-V cell run in duplicate |
| other | in-situ conditioning, 24 C platen, 90 s polish |

## Data file

`sorooshian2005_ild_cmp.csv` — 117 points across 108 design cells (8 cells
missing where duplicate markers exactly coincide).
Columns: `fig, groove, thick, flow, psi, vel, rpm, rr, xerr, merged, hpx`.
`rr` is removal rate in A/min. Extraction code: `sorooshian2005_digitize.py`.

## Provenance caveats — READ BEFORE USING

1. **The removal rates are FIGURE READS, not a printed table.** The
   dissertation plots RR against the p*V product and never tabulates it.
   The factor LEVELS above are text and are reliable; the RATES are not.
2. Digitisation was programmatic (marker detection against the detected
   500 A/min gridline ladder and the 0-45000 Pa*m/s frame), not eyeballed.
3. **Self-check that the calibration is right:** all 117 recovered markers land
   on a nominal (psi x m/s) product to within 0.5 %. A wrong axis calibration
   could not pass this.
4. Rows flagged `merged=True` (~20) are the centroid of two overlapping
   duplicate markers, not two independent replicates. Treat as low confidence.
5. Estimated per-point read error 5-10 %.

**Because of caveat 1, this dataset is used only to FALSIFY — to establish the
SIGN and rough MAGNITUDE of log-log slopes across 3x spans. No constant in any
pack is fitted to it.** A 5-10 % read error cannot manufacture or conceal an
effect of the size being tested (the flow leg needs +44 % and measures -1 %).

## What it decided (`tools/sorooshian_flow_probe.py`)

| quantity | measured | starvation law predicts | verdict |
|---|---|---|---|
| b_P | **+1.165** (30 ladders) | +1.000 (Preston) | PASSES audit — may arbitrate |
| b_V | **+0.655** (29 ladders) | +0.667 | matches |
| b_Q | **-0.010** (47 matched pairs) | +0.333 | **absent** |

b_Q is measured on MATCHED PAIRS — identical groove, thickness, pressure and
velocity, differing only in flow — so no model of the other axes enters. The
sign is a coin flip (22/47 positive). Tripling the flow moves the rate by
**-1.1 %** where the law requires **+44.2 %**.

## Conclusion, and the rule it sets

Two legs of the derivation land almost exactly and the third is flatly absent.
Since `b_V` and `b_Q` both come from the SAME mass balance (`Q/V` is one
quantity), **the derivation cannot be adopted one half at a time.** Keeping
`V^(2/3)` while discarding `Q^(1/3)` would turn a derived law into a fitted
exponent that merely happens to be written as a fraction. The exponent
therefore stays OUT of the model, and the corpus median stays at 18.9 % by
choice. Locked by `tests/test_sorooshian_flow_falsifies_starvation.py`.

## Independent corroboration of the EXPONENT (not of the derivation)

The sub-linear velocity response itself is now well supported; it is the
mechanism that is missing.

- **Tseng & Wang (1997)**, J. Electrochem. Soc. 144(2) L15, DOI 10.1149/1.1837417 —
  derive and report a **(speed)^(1/2)** dependence for thermal oxide.
  *Abstract only (publisher bot-wall); the velocity exponent is quoted verbatim.*
- **Park, Lee & Jeong (2005)**, Proc. 2nd PacRim Int. Conf. on Planarization CMP,
  Seoul, p. 123 — fit **RR ~ p^0.52 V^0.74** for copper.
  *NOT read directly — quoted verbatim in Borucki et al. 2023 (below). Do not
  enter these numbers anywhere without obtaining the original.*
- **Borucki, Sampurno & Philipossian (2023)**, "The Shear Force Law: A Guide to
  Modeling CMP Removal Rates", ECS J. Solid State Sci. Technol. 12(4) 044003,
  DOI 10.1149/2162-8777/accaa6 — attribute non-Prestonian behaviour to a
  **Stribeck/mixed-lubrication COF decline**. This is the field's leading
  hypothesis and **this repo has rejected it**: a COF depending on V/p forces
  the two log-coefficients to be equal and opposite, and the corpus measures
  (-0.036, -0.549). See `tools/velocity_thermal_probe.py`.
- **Li, Borucki, Koshiyama & Philipossian (2004)**, J. Electrochem. Soc. 151(7)
  G482, DOI 10.1149/1.1758818 — Cu CMP: *"the removal rate at any fixed value
  of p x V generally decreases as slurry flow rate increases"*, attributed to
  convective cooling. *Abstract only.* Independently **contradicts the SIGN**
  of the starvation law's Q term.
- **Park et al. (2015)**, Int. J. Precis. Eng. Manuf.-Green Tech.,
  DOI 10.1007/s40684-015-0041-8 — replicates that negative flow sign for Cu.
- **Philipossian & Mitchell (2003)**, MRS Proc. 767 F1.4,
  DOI 10.1557/PROC-767-F1.4 — slurry utilisation efficiency is only **2-22 %**
  and *depends on velocity*. Any future law written in terms of DISPENSED flow
  inherits a ~10x uncertainty in the flow actually reaching the interface;
  this is a reason the raw-Q formulation may have been wrong in the first place.

## Open question left for a future run

Find a mechanism that predicts sub-linear velocity dependence **without**
predicting a flow dependence. Note that Borucki et al. (2025),
DOI 10.1149/2162-8777/adce88, predict an actual removal-rate *maximum* in
velocity for W CMP, and their Cu data show the velocity exponent changing sign
with pressure (-0.81 at 1 psi, -0.62 at 1.5 psi, +0.33 at 2 psi) — which no
single global exponent, derived or fitted, can reproduce. That pressure
dependence is the next thing worth measuring.
