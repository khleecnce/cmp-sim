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
- **558 tests**; verified from a clean clone including `pip install -e .`

## NEXT
Owner review of the three judgement calls where measurements disagreed and a
compromise was chosen over a flattering fit. Detail and derivations:
`docs/predictive-accuracy.md`.
1. `oxide_silica` loading `C_half = 4.4` — its two datasets want 0.6 (0.5–3
   wt%) and 5.9 (5–25 wt%). The compromise costs both ~20%. A single Langmuir
   may not span that range.
2. `sti_ceria` pH pools Dandu (81× swing, peak 4.5, TEOS) with Netzband (1.9×,
   rises to pH 10, thermal oxide) at 34%; either alone is 20–26%. Likely two
   packs.
3. Acid-side pH floors for `oxide_silica` and `cu_h2o2_bta` are 1%-of-peak
   bounds, not measurements — no dataset sweeps the acid side of their optima.

## BLOCKED
- **Particle-size exponent sign: settled by data, and my grouping was wrong.**
  It splits by ABRASIVE, not by film — ceria +0.87, alumina +0.29, silica
  −0.05; within one abrasive the sweeps agree, across them they do not share a
  sign. Leaving oxide `null` was not neutral: it selected the derived −0.84,
  wrong in sign for 8 of 10 measured sweeps.
- **`contact_branch` decided without circular input** via the pad-limited load
  criterion (particle size cancels): Cu plastic, oxide/STI transition. It did
  NOT unblock the P3 exponent derivation — plastic α=3/2 with copper's measured
  χ=1.0 gives n_C = −0.5 ("more abrasive removes less"), violating the model's
  own bound, and α and χ are not independently adjustable. The engine reports
  the branch and leaves the exponents `unverified`. Loading is now fitted
  directly instead, which bypasses the conflict rather than resolving it.
  **Depth limit no bookkeeping removes:** no nanoindentation of an actually
  CMP-polished surface exists in the 324-paper corpus, and instruments resolve
  ~5 nm while an abrasive indents under 1 nm. Λ ∝ 1/H³, so 2× in hardness is
  8× in Λ.
- **SnAg has no published Preston coefficient** (68 sourced numbers, no rate).
  Runs as a ranking on the Archard estimate and says so; four measured rates
  take it to ±1.4% cross-validated. No envelope exists to sanity-check its
  absolute rate, which the run states outright.
- **SiC inherits SiO₂'s modulus through its lineage** (92 vs ~450 GPa, and
  Λ ∝ E²). Blocked with `null` + TODO(owner): the same route once carried the
  oxide Kp into this pack and over-predicted SiC by 128×.

## VALIDATION
| dataset | n | MAPE | verdict |
|---|---:|---:|---|
| US9499721B2 TEOS/silica | 4 | 1.9% | pass |
| US8142675B2 Pt/alumina | 4 | 12.3% | pass |
| US6564116B2 oxide L25 | 5 | 12.6% | pass |
| Mariscal 2020 PETEOS/ceria | 9 | 12.9% | pass |
| Wang SiC DOE50 | 6 | 31.9% | **kept failing** — chemically limited, R²=0.09 |
| US6918821B2 Cu/IC1000 | 6 | 44.1% | **kept failing** — lubrication transition, flagged at λ=1.24 without seeing a rate |

Gate: 4 in-scope datasets within ±15% (need 3) → **PASS**

Prediction on every axis (320 points): median **19.5%** trend, **23.6%**
leave-one-out, 27/37 datasets beat predicting their own mean. By axis —
particle size 8.7%, loading 34.6%, pH 36.2%, oxidizer 36.2%, pressure 40.7%,
velocity 44.1%. Was 42.8% / 53.9% with 16 of 36 losing to the mean, before
three silent failures were found: pH was inert, `abrasive_d50_nm` was dropped,
and zero oxidizer predicted both 3× too fast and exactly zero.
