# Changelog

All notable changes to CMP-Sim. Newest first.

## Unreleased

### Physics
- **P1 Preston** baseline, `Kp` decomposed by slurry / pad / film.
- **P2 Greenwood-Williamson** asperity contact; the correction is applied only
  when the pack's reference pad has a real source, because normalising against
  an *estimated* reference inflated every rate two- to threefold.
- **P3 Luo-Dornfeld** abrasive mechanics with site-occupancy saturation.
- **P4 Chemistry** through a softened-hardness channel, Arrhenius temperature.
- **P5 Radial uniformity**: relative velocity field, zone pressures, and slurry
  supply on Mu's 2016 reactor model (an earlier invented supply number was
  discarded).
- **P6 Pattern**: density-smoothed step-height evolution, dishing, erosion.
- **P7 Pad life**: glazing and conditioner ageing, *reported* rather than
  multiplied into `Kp` — the inherited MRR proxy peaks at ~7 min against a
  measured ~3 min, so applying it would claim unearned precision.
- **P8 Defect proxy**: large-particle tail against the published ~680 nm
  scratch threshold, with scratch width and depth per film.

### Model selection
- Models are chosen by **situation, not by film**. `core/regime.py` classifies a
  run on eight axes; `core/profiles.py` offers 11 profiles bundling seven
  orthogonal layers. `auto` picks; an explicit choice is respected and
  mismatches are warned about. Pad wear and pattern are overlays, not rivals.
- Material family decides the film class before hardness does: W (~4-7 GPa) and
  thermal oxide (~7-9 GPa) overlap in hardness but polish by different
  mechanisms.

### Validation
- **The `si` film is scored against a measurement for the first time.**
  `bae2022_si_wafer_alkali_ph` (doi:10.3390/nano12213893) is an independent
  bare-Si polish at 5.7 psi — 9× the down force of the pack's Kp source — and
  its rates confirm the 100–3,000 Å/min envelope independently of the source
  that set it. Absolute comparison is disabled (the paper never states the
  carrier-platen centre distance, so no relative velocity can be recovered) and
  the pH term is left **unfitted**: two pH levels cannot determine a peak and a
  width. See `docs/limits.md` §12. The dataset does not beat predict-the-mean,
  which is reported rather than repaired.
- **Four published datasets within ±15%**, all three patent sources re-verified
  against the official USPTO PDFs rather than trusted from a report.
- Two datasets are kept **failing on purpose**, each with a test that fails if
  the documented limit ever goes stale:
  - *US6918821B2 Cu* — the lubrication limit. The regime detector flags the
    exact condition where the measured rate collapses (λ = 1.24) without ever
    seeing a rate.
  - *SiC DOE50* — chemically rate-limited. At identical P·V the rate spans
    5.2×, and P·V explains only R² = 0.09 of the variance.

### Data
- 55 additives × 9 films; 11 abrasives × 9 films; packs for Cu, W, oxide,
  STI-ceria, SiC, Si substrate, SnAg.
- Unknown values are `null` with a `TODO(owner)` note, never invented. The SnAg
  pack carries 68 sourced numbers and **no Preston coefficient**, because none
  is published; the example refuses to run and says so.

### Interfaces
- CLI: `run`, `sweep`, `validate`, `packs`, `profiles`.
- Zero-dependency web UI and HTTP API (`/api/simulate`, `/api/sweep`).
- `CMP-Sim.command` launcher; verified from a clean clone.
- Sweeps mark any point where the regime changes instead of drawing one
  confident trend through physics that changed underneath it.

### Corrections found while verifying
- **SiC `Kp` inherited the oxide value** — 128× too high. Re-derived from the
  50-run DOE.
- **W `Kp` was an estimate** 4× above two independent patent tables.
- **Up-area rate reported 0.0 Å/min for every run** — the m/s → Å/min factor
  was 10 instead of 1e10 × 60, while the same object's notes quoted the right
  figure.
- **The "softening" assumption was refuted by its own data.** H₂O₂ grows
  Cu₂O/CuO, *harder* than copper (3.24 GPa on a 1.2 GPa film; bulk cuprite
  17.0–17.5 GPa). The same study spans 0.05–20 GPa on one metal by chemistry
  and pH alone, so the modified surface is not assumed softer anywhere.
- **The library saw 2 passing datasets while the CLI saw 4** — dataset
  discovery searched only the inherited directory.
- **A stationary platen reported 815 Å/min**; Preston is proportional to
  velocity, so it now reports 0.0.
- **Bad input surfaced as an untranslated Korean bracket error.** Impossible
  recipes are now rejected by field and value; a load beyond the contact model
  explains that every summit is already engaged.
