# CMP-Sim — STATUS

## DONE (phase, module, tests)
- P1 Preston · P2 GW contact · P3 Luo-Dornfeld abrasive · P4 chemistry
  (pH/oxidizer/inhibitor + Arrhenius) · P5 radial uniformity & slurry supply
  · P6 pattern dishing/erosion · P7 pad glazing & conditioner ageing
  · P8 defect proxy
- Model selection by SITUATION, not by film: `core/regime.py` (8 axes) +
  `core/profiles.py` (13 profiles, 7 orthogonal layers)
- Maturity grading `core/maturity.py` — a pack may lower its grade, never raise
  it; unestablished films refuse defaults and name the input they need
- Kp from first principles `models/first_principles.py` (Archard, ~1.8x
  uncertainty stated rather than hidden)
- Learning from data: `core/calibration.py`, `core/factor_fit.py` (6 physical
  factors, LOO-gated), `core/measurement_io.py` (CSV logs)
- **Prediction scored on every measured axis**: `core/predictive_score.py`,
  `cmp-sim accuracy`, `GET /api/accuracy`, surfaced in the web UI next to the
  rate. 37/38 datasets, 320 points.
- Interfaces: CLI (`run`/`fit`/`sweep`/`validate`/`accuracy`/`packs`/
  `profiles`), zero-dependency web UI + API, `CMP-Sim.command` launcher
- Films: Cu, W, oxide, STI-ceria, poly-Si, Si substrate, SiC, SnAg.
  Data: 55 additives × 9 films, 11 abrasives × 9 films
- Legacy 2nd transfer absorbed (`legacy/HANDOVER-2.md`). **558 tests: 554 pass,
  4 fail** — all four are cited-value conflicts listed below, not wrapper bugs.

## NEXT
Owner decision on the λ roughness scale (BLOCKED #1): does the lubrication
threshold move with the new literature σ = 2.0 µm, or is `pad_height_beta_inv_m`
(exponential scale) the wrong quantity to divide film thickness by (RMS)?
The rest of the regime layer is downstream of that answer.

## BLOCKED
Reasoning, numbers and sources for each: `docs/open-questions.md`.
1. **λ scale — the 2nd transfer broke the strongest validation result.**
   `base.yaml` pad stats went to literature values (σ 0.3 → 2.0 µm), so the
   US6918821B2 collapse point fell λ = 1.24 → 0.187 and no longer leaves
   boundary lubrication. Restoring the old `estimated` trio fixes 3 of the 4
   failures — diagnostic only, not applied. 3 tests parked.
2. **`sti_ceria` 7,235 Å/min vs a 200–6,000 envelope.** Pack loading terms
   re-declared from Dandu 2009 (0.25 wt%, n = −0.4295). Pack and envelope are
   both cited; one is wrong for this recipe. 1 test parked.
3. **Size exponent splits by ABRASIVE, not film** (ceria +0.87, alumina +0.29,
   silica −0.05). `null` was not neutral — it selected the derived −0.84, wrong
   in sign for 8 of 10 sweeps. Packs must now scope and cite the key.
4. **`contact_branch` resolved, P3 exponents still `unverified`** — plastic
   α=3/2 with Cu's χ=1.0 gives n_C = −0.5, violating the model's own bound.
   No nanoindentation of a CMP-polished surface exists in the 324-paper corpus.
5. **SnAg has no published Preston coefficient**; runs as an Archard ranking and
   says so. **SiC inherits SiO₂'s modulus** (92 vs ~450 GPa, Λ ∝ E²) — `null` +
   TODO(owner), since that route once over-predicted SiC by 128×.
6. **Three judgement calls where measurements disagreed** (`oxide_silica`
   C_half, `sti_ceria` pH pooling, acid-side pH floors) — compromises kept over
   flattering per-dataset fits.

## VALIDATION
| dataset | n | MAPE | verdict |
|---|---:|---:|---|
| US9499721B2 TEOS/silica | 4 | 1.9% | pass |
| US8142675B2 Pt/alumina | 4 | 12.3% | pass |
| US6564116B2 oxide L25 | 5 | 12.6% | pass |
| Mariscal 2020 PETEOS/ceria | 9 | 12.9% | pass |
| Wang SiC DOE50 | 6 | 31.9% | **kept failing** — chemically limited, R²=0.09 |
| US6918821B2 Cu/IC1000 | 6 | 44.1% | **kept failing** — lubrication transition |

Gate: 4 in-scope datasets within ±15% (need 3) → **PASS**

Prediction on every axis (320 points): median **19.5%** trend, **23.6%**
leave-one-out, 27/37 datasets beat predicting their own mean. By axis —
particle size 8.7%, loading 34.6%, pH 36.2%, oxidizer 36.2%, pressure 40.7%,
velocity 44.1%.
