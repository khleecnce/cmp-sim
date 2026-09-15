# CMP-Sim — STATUS

## DONE (phase, module, tests)
- P0 skeleton + `core/legacy_bridge.py` wrapping inherited FabSim modules — 5
- P1 Preston `models/preston.py` + `core/solver.py` — 15
- P2 Greenwood-Williamson `models/contact_gw.py`, `pad/material.py` — 29
- P3 abrasive mechanics `models/luo_dornfeld.py` — 22
- P4 chemistry `models/chemical_rate.py`, `slurry/formulation.py` — 22
- P5 uniformity/supply `models/uniformity.py`, `slurry/rheology.py` — 38
- P6 pattern `models/pattern_density.py` — 21
- P7 pad wear `pad/wear.py` + P8 defects `models/defect_proxy.py` — 27
- Databases: 55 additives x 9 films, 11 abrasives x 9 films — 18
- Plausibility guard `core/sanity.py` + validation gate — 25
- CLI, zero-dependency web UI + HTTP API (verified in headless chromium)
- 6 example recipes: oxide, Cu, W, STI-ceria, SiC, multi-zone
**217 tests, all passing.**

## NEXT
Owner review of the validation table and the three Kp corrections (SiC, W, and
the pad-contact baseline) before any further physics is added.

## BLOCKED
(none)

## VALIDATION — criterion (a) PASSED: 4 sources within +/-15%
| dataset | n | read | MAPE | max |
|---|---:|---|---:|---:|
| US9499721B2 TEOS/silica | 4 | table | 1.9% | 2.8% |
| US8142675B2 Pt/alumina | 4 | table | 12.3% | 20.9% |
| US6564116B2 oxide L25 | 5 | table | 12.6% | 27.2% |
| Mariscal 2020 PETEOS/ceria | 9 | digitized | 12.9% | 20.5% |
| Wang SiC DOE | 6 | SI table | 31.9% | 88.8% | chemically limited |
| US6918821B2 Cu/IC1000 | 6 | table | 44.1% | 161.2% | kept as counter-example |

All three patent datasets were re-verified by me against the official USPTO
PDFs, not accepted on the subagents' reports.

## OWNER QUESTIONS
1. **Absolute rate needs your data.** Every Kp is back-calculated from one
   literature point. Do you have >=3 measured RR points (any film) we can use to
   recalibrate? They stay out of git.
2. **I corrected three inherited numbers** — SiC Kp (was the oxide value, 128x
   too high), W Kp (from a quoted range; refit to two patent tables), and the
   pad-contact baseline. Please sanity-check these against your experience.
3. Which film should get depth next: Cu, W, STI oxide or poly-Si?
4. Poly-Si, Si-substrate and SnAg have no parameter pack yet — worth adding?
