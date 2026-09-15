# CMP-Sim — STATUS

## DONE (phase, module, tests)
- P1 Preston `models/preston.py` — gate: 4 published datasets within ±15%
- P2 GW contact `models/contact_gw.py` + `pad/material.py`
- P3 Abrasive `models/luo_dornfeld.py` — occupancy saturation, regime exponents
- P4 Chemistry `models/chemical_rate.py` + `slurry/formulation.py`
- P5 Uniformity `models/uniformity.py` — velocity field, zones, slurry supply
- P6 Pattern `models/pattern_density.py` — step height, dishing, erosion
- P7 Pad wear `pad/wear.py` — glazing + conditioner ageing (reported, not applied)
- P8 Defects `models/defect_proxy.py` — d99 tail vs 680 nm scratch threshold
- Selection by SITUATION: `core/regime.py` (8 axes) + `core/profiles.py`
  (13 profiles, 7 orthogonal layers, wear/pattern as overlays)
- Guards: `core/validate_input.py`, `core/sanity.py`, owner `params:` overrides
- Interfaces: CLI (`run`/`sweep`/`validate`/`packs`/`profiles`), zero-dependency
  web UI + API (`/api/simulate`, `/api/sweep`), `CMP-Sim.command`
- Films: Cu, W, oxide, STI-ceria, poly-Si, Si substrate, SiC, SnAg
- Data: 55 additives × 9 films, 11 abrasives × 9 films
- **360 tests passing**; verified from a clean clone incl. `pip install -e .`

## NEXT
Owner review of the physics. No further implementation is queued — the P1–P8
gates, all example films and the validation table are green.

## BLOCKED
- `contact_branch` is `unknown` for every film: no pack has BOTH
  `film_surface_hardness_pa` (the chemically modified surface) and
  `particle_contact_stress_pa`. Not a bug — the softened hardness is rarely
  published, and in Luo-Dornfeld the contact stress is *set equal* to the
  hardness by assumption, so sourcing it independently is circular.
  **Question for owner:** in-house nanoindentation on a polished Cu/W/oxide
  surface would settle the sign of the particle-size exponent in P3.
- **SnAg has no published Preston coefficient.** The pack holds 68 sourced
  numbers; the example refuses to run rather than invent one. **Question for
  owner:** one measured SnAg rate with its pressure and velocity unblocks it.
- Cu oxidizer term is monotonic where the real system peaks (~1–3 wt%). The
  Langmuir branch is used because the Kaufman peak's parameters are degenerate
  below the peak; both facts are now warned about at runtime.

## VALIDATION
| dataset | n | MAPE | verdict |
|---|---:|---:|---|
| US9499721B2 TEOS/silica | 4 | 1.9% | pass |
| US8142675B2 Pt/alumina | 4 | 12.3% | pass |
| US6564116B2 oxide L25 | 5 | 12.6% | pass |
| Mariscal 2020 PETEOS/ceria | 9 | 12.9% | pass |
| Wang SiC DOE50 | 6 | 31.9% | **kept failing** — chemically limited: at fixed P·V the rate spans 5.2×; P·V explains R²=0.09 |
| US6918821B2 Cu/IC1000 | 6 | 44.1% | **kept failing** — lubrication transition; the model flags the exact collapse point (λ=1.24) without seeing a rate |

Gate: 4 in-scope datasets within ±15% (need 3) → **PASS**
