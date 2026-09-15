# CMP-Sim — STATUS

## DONE (phase, module, tests)
- P1 Preston — gate: 4 published datasets within ±15%
- P2 GW contact · P3 Luo-Dornfeld abrasive · P4 chemistry (Arrhenius)
- P5 radial uniformity, zone pressure, slurry supply
- P6 pattern dishing/erosion · P7 pad glazing + conditioner ageing · P8 defects
- Model selection by SITUATION: `core/regime.py` (8 axes) + `core/profiles.py`
  (13 profiles, 7 orthogonal layers, wear/pattern as overlays)
- CMP maturity grading `core/maturity.py` — established / emerging /
  unestablished, derived from pack evidence; a pack may lower its grade, never
  raise it. Unestablished films refuse defaults and ask for specific inputs.
- Kp from first principles `models/first_principles.py` — Archard Kp = k/H when
  no CMP data exist, with its ~1.8x uncertainty stated rather than hidden
- **Learning from data**: `core/calibration.py` (scale + leave-one-out accuracy),
  `core/factor_fit.py` (6 named physical factors, three anti-overfitting gates),
  `core/measurement_io.py` (CSV logs)
- Interfaces: CLI (`run`/`fit`/`sweep`/`validate`/`packs`/`profiles`),
  zero-dependency web UI + API, `CMP-Sim.command` launcher
- Films: Cu, W, oxide, STI-ceria, poly-Si, Si substrate, SiC, SnAg
- Data: 55 additives × 9 films, 11 abrasives × 9 films
- **442 tests**; verified from a clean clone including `pip install -e .`

## NEXT
Owner review of the physics. No implementation is queued — every P1–P8 gate,
all example films, the validation table and the data-fitting path are green.

## BLOCKED
- `contact_branch` is `unknown` for every film: no pack has BOTH
  `film_surface_hardness_pa` and `particle_contact_stress_pa`. Not a bug — in
  Luo-Dornfeld the contact stress is *set equal* to the hardness by assumption,
  so sourcing it independently is circular. Nanoindentation of a polished
  surface would settle the sign of the particle-size exponent in P3.
- **SnAg has no published Preston coefficient** (68 sourced numbers, no rate;
  searched 320 local CMP papers, ScienceDirect and Crossref again this session).
  It runs as a ranking on the Archard estimate and says so; four measured rates
  take it to +/-1.4% cross-validated. Also means there is no envelope to
  sanity-check its absolute rate against, which the run now states outright.
- Cu oxidizer term is monotonic where the real system peaks (~1–3 wt%). The
  Langmuir branch is used because the Kaufman peak's parameters are degenerate
  below the peak; both facts are warned about at runtime.

## VALIDATION
| dataset | n | MAPE | verdict |
|---|---:|---:|---|
| US9499721B2 TEOS/silica | 4 | 1.9% | pass |
| US8142675B2 Pt/alumina | 4 | 12.3% | pass |
| US6564116B2 oxide L25 | 5 | 12.6% | pass |
| Mariscal 2020 PETEOS/ceria | 9 | 12.9% | pass |
| Wang SiC DOE50 | 6 | 31.9% | **kept failing** — chemically limited: rate spans 5.2× at identical P·V, R²=0.09 |
| US6918821B2 Cu/IC1000 | 6 | 44.1% | **kept failing** — lubrication transition; the model flags the collapse point (λ=1.24) without seeing a rate |

Gate: 4 in-scope datasets within ±15% (need 3) → **PASS**

Factor recovery against synthetic tools with known answers: pressure exponent
0.65→0.652, abrasive C_half 3.0→3.08, Ea 45→44.5 kJ/mol, two effects at once
0.70/3.0→0.68/3.08. Preston-true data unlock nothing.
