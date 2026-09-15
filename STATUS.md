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
- **543 tests**; verified from a clean clone including `pip install -e .`

## NEXT
Owner review of the physics. No implementation is queued — every P1–P8 gate,
all example films, the validation table and the data-fitting path are green.

## BLOCKED
- **Partly resolved.** `contact_branch` is now decided without any circular
  input, via the pad-limited load criterion
  `Lambda = 48*Hp*E^2/(pi^2*H^3) > 1` (Saka CIRP 2008 Eq. 3, Eusner JES 2009
  Fig. 15 pad hardness). Particle size cancels out. Cu = plastic (117),
  oxide/STI = transition (2.8), SiC = blocked (see below).
  **What it did NOT unblock:** the sign of the P3 particle-size exponent. The
  exponent relations assume `0 <= 1-alpha*chi <= 1`, but the plastic branch
  (alpha=3/2) with copper's measured load sharing (chi=1.0) gives
  `n_C = -0.5` — "more abrasive removes less". alpha and chi are not
  independently adjustable (chi comes from the measured area-pressure
  exponent), so the engine reports the branch and leaves the exponents
  `unverified` rather than publishing a negative concentration exponent.
  **To settle it:** a measured abrasive-CONCENTRATION sweep per film.
  **Partly settled by data since:** 9 measured SIZE sweeps across 7 films were
  extracted and verified (exponents -0.45 to +1.0, three non-monotonic). Where
  a pack now has a sourced sweep for its own film the measured exponent
  OVERRIDES the derived one: Cu +0.33 (Lai 2001 printed table), W -0.05
  (Bouvet 2002, passivation-limited so size barely matters). Oxide stays null
  because its measured response is non-monotonic and depends on abrasive
  chemistry AND deposition method - a single number would be a lie.
- **SnAg has no published Preston coefficient** (68 sourced numbers, no rate;
  searched 320 local CMP papers, ScienceDirect and Crossref again this session).
  It runs as a ranking on the Archard estimate and says so; four measured rates
  take it to +/-1.4% cross-validated. Also means there is no envelope to
  sanity-check its absolute rate against, which the run now states outright.
- **RESOLVED.** The Cu oxidizer term now peaks instead of falling monotonically.
  Pinning the peak to a MEASURED position makes the decay scale a consequence
  of it, leaving one free parameter, which Du 2004 (doi:10.1149/1.1648029,
  6 points across the peak) supplies: 5.6% MAPE, beats plain Langmuir by >2x.
  Curvature is borrowed across a vol%/wt% axis difference and a glycine
  difference, recorded at `confidence: low`.
- **New, found while fixing the above:** SiC was inheriting SiO2's elastic
  modulus (92 GPa vs SiC's ~450) through its SiC -> sti_ceria -> oxide_silica
  lineage, and Lambda goes as E^2. Blocked with `value: null` + TODO(owner)
  rather than a handbook number: the same inheritance route once carried the
  oxide Kp into this pack and over-predicted SiC by 128x.

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
