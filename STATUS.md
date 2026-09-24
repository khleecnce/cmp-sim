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
  rate. 38 of 46 datasets scorable, 330 points.
- Interfaces: CLI (`run`/`fit`/`sweep`/`validate`/`accuracy`/`packs`/
  `profiles`), zero-dependency web UI + API, `CMP-Sim.command` launcher
- **Published**: github.com/khleecnce/cmp-sim (MIT) and a link-protected
  demo at cmp-sim.vercel.app (`CMPSIM_TOKEN`; unset = open, for local runs).
  History scrubbed of the employer name and rewritten to a single author
  before going public; no copyrighted article text is tracked.
- Films: Cu, W, oxide, STI-ceria, poly-Si, Si substrate, SiC, SnAg.
  Data: 55 additives × 9 films, 11 abrasives × 9 films
- **Abrasive TYPE reaches the rate** (`slurry/abrasive_effects.py`): packs
  declare `reference_abrasive`; a swap rescales only by a published
  matched-condition ratio, withdraws the pack's measured exponents, and says
  `ranking_only` when unanchored. Was: all 4 abrasives → identical 1601 Å/min.
- **3D tool view** (`/tool`): click wafer / head / pad / platen / disk / slurry
  supply to enter that part's data; wafer colour map is the predicted radial
  profile; three.js vendored for offline fab machines.
- Legacy 2nd transfer absorbed (`legacy/HANDOVER-2.md`). **583 tests pass**
  (the four cited-value conflicts from the transfer are resolved; the
  remaining known limits are listed under BLOCKED, not failing tests).

## NEXT
Fill `abrasives.yaml → relative_rate` from matched-condition literature. Only
1 of 35 film×abrasive pairs is anchored today (oxide+ceria = 3.0× silica); the
other 34 run `ranking_only`. Two research agents are mining matched pairs and a
per-film validation index. Until they land, an abrasive swap ranks recipes
correctly but does not predict an absolute rate.

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

Prediction on every axis (330 points, 38 of 46 datasets scorable): median
**20.3%** trend, **23.6%** leave-one-out, 29/38 beat predicting their own mean.
By axis — particle size 8.7%, pressure 22.9%, loading 22.9%, oxidizer 39.3%,
velocity 44.1%, pH 49.2%.

pH is now the weakest axis, and the reason is structural rather than a missing
tune: ceria and charged silica peak at pH 4.5 and pH 2 on the *same* film, so
the optimum belongs to the slurry SYSTEM, not the film. Splitting them needs a
separate Kp per system, which no public dataset supplies.

Resume handover, every figure re-verified against the CLI:
`~/CMP-SIM-FOR-RESUME.md`
