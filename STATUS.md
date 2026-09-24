# CMP-Sim — STATUS

## DONE (phase, module, tests)
- P1 Preston · P2 GW contact · P3 Luo-Dornfeld · P4 chemistry (pH/oxidizer/
  inhibitor + Arrhenius) · P5 radial uniformity · P6 pattern dishing/erosion
  · P7 pad glazing & conditioner ageing · P8 defect proxy. **625 tests pass.**
- Model selection by SITUATION not film (`core/regime.py`, `core/profiles.py`);
  maturity grading (`core/maturity.py`) — a pack may lower its grade, never
  raise it; Kp from first principles (`models/first_principles.py`).
- Learning from data: `core/calibration.py`, `core/factor_fit.py` (LOO-gated),
  `core/measurement_io.py`. **Scored on every measured axis**
  (`core/predictive_score.py`, `cmp-sim accuracy`): 41/49 datasets, 388 points.
- **pH belongs to the slurry SYSTEM, not the film** — US9422456B2's cationic
  core-shell silica peaks at pH 4.9 on the SAME TEOS film where plain silica
  peaks at pH 11. Split into `oxide_silica_aminosilane` rather than widening
  the bell: 126.6% → 25.3% on its 22 points, pH axis 49.2% → 39.3%.
- **Abrasive TYPE reaches the rate** (`slurry/abrasive_effects.py`): a swap
  rescales only by a published matched-condition ratio, withdraws the pack's
  measured exponents, says `ranking_only` when unanchored.
- **The oxidizer floor is MECHANICAL, not chemical** — US8070843B2 is a
  fixed-abrasive pad with no free abrasive, so the pack's free-abrasive 0.14
  background is wrong for it; its own table prints 0.040. 51.7% -> 8.7%, but
  the honest number is the 4 oxidizer-bearing rows: 9.5% -> 8.6% (the zero row
  is near-tautological once the floor is declared). Pack keeps its 0.14.
- **Velocity is the THINNEST axis, not the weakest term** — the 44.1% median
  came from Taguchi arrays that never repeat a chemistry at two speeds. Only
  29 points in the whole corpus isolate velocity; on the one in-scope isolated
  sweep (Mariscal 3x3) the error is 11.7% and the exponent +0.86 vs Preston's
  +1.0. Also fixed a data-fidelity bug: the Yang L25 recorded 2 of its 6
  factors, so four chemical factors' scatter was being read as velocity error.
- Size-matched abrasive-ratio hunt CLOSED with 15 honest nulls
  (`research/rate_ratios_matched.yaml`) — 0 of 15 pairs pass both gates, so
  34/35 film×abrasive pairs stay `ranking_only`.
- Films: Cu, W, oxide, STI-ceria, poly-Si, Si, SiC, SnAg. 55 additives ×
  9 films, 11 abrasives × 9 films. Legacy 2nd transfer absorbed.
- Interfaces: CLI (`run`/`fit`/`sweep`/`validate`/`accuracy`/`packs`/
  `profiles`), zero-dep web UI + API, 3D tool view (`/tool`), `.command`
  launcher. **Published**: github.com/khleecnce/cmp-sim (MIT), demo at
  cmp-sim.vercel.app (`CMPSIM_TOKEN`). History scrubbed before going public.

## NEXT
`miranda2004_cu_ph_h2o2_2x2` (107.8%) and `ihnfeldt2008` (84.0%) are the two
worst remaining datasets and both vary pH AND oxidizer together on Cu. Isolate
as before: Miranda's 2x2 holds pH fixed in each leg, and its two legs move in
OPPOSITE directions with H2O2 (1953->2908 at one pH, 1743->243 at the other) —
a sign flip the multiplicative pH x oxidizer form cannot produce. Determine
whether that is a pH-dependent oxidizer regime (needs a coupling term) or two
different formulations mis-pooled, before touching any constant.

## BLOCKED  (numbers + sources: `docs/open-questions.md`)
0. `si` over-predicts at bare defaults (10,776 vs a 100–3,000 envelope); Kp
   rests on one Seidel 1990 point. Needs a second Si-substrate point.
1. λ scale — the 2nd transfer's literature pad stats (σ 0.3 → 2.0 µm) broke the
   US6918821B2 lubrication result. Diagnostic fix known, not applied. 3 parked.
2. `sti_ceria` 7,235 Å/min vs a 200–6,000 envelope; pack and envelope both
   cited, one is wrong for this recipe. 1 parked.
3. Size exponent splits by ABRASIVE, not film; packs must scope and cite it.
4. P3 exponents still `unverified` — no nanoindentation of a CMP-polished
   surface exists in the corpus.
5. SnAg has no published Preston coefficient (Archard ranking only); SiC
   inherits SiO₂'s modulus — `null` + TODO(owner).
6. Three judgement calls kept as compromises over flattering per-dataset fits.

## VALIDATION
| dataset | n | MAPE | verdict |
|---|---:|---:|---|
| US9499721B2 TEOS/silica | 4 | 1.9% | pass |
| US8142675B2 Pt/alumina | 4 | 12.3% | pass |
| US6564116B2 oxide L25 | 5 | 12.6% | pass |
| Mariscal 2020 PETEOS/ceria | 9 | 12.9% | pass |
| Wang SiC DOE50 | 6 | 31.9% | **kept failing** — chemically limited |
| US6918821B2 Cu/IC1000 | 6 | 44.1% | **kept failing** — lubrication transition |

Gate: 4 in-scope datasets within ±15% (need 3) → **PASS**

All axes (388 pts, 41/49 datasets): median **20.2%** trend, **22.6%** LOO.
By axis — size 11.2%, loading 22.9%, pressure 25.3%, oxidizer 39.3%,
pH 39.3%, velocity 44.1%. ⚠ The axis medians pool datasets that vary several
things at once; velocity's 44.1% is 11.7% once isolated (see DONE).
Resume handover: `~/CMP-SIM-FOR-RESUME.md`
