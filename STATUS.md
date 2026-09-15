# CMP-Sim — STATUS

## DONE
- P0 skeleton: `cmp_sim/{core,slurry,pad,disk,tool,wafer,models}`, CLI, pyproject, venv (pint/numpy/scipy/pyyaml/pytest)
- `core/legacy_bridge.py` wires inherited `legacy/` (FabSim e385ed1): preston, kinematics, wiwnu, pattern_density, params loader, dlvo_colloid
- `core/params.py` two-tier pack loader (own packs override inherited); missing constant -> `ParamMissing`, never a default
- `core/state.py` full input contract (Slurry/Abrasive/Additive/Pad/Disk/Tool/Wafer) + Result
- P1 `models/preston.py` + `core/solver.py`: MRR(r)=Kp*P*V, zone pressures, area-weighted WIWNU — 15 tests
- Slurry item 1-3 `slurry/rheology.py`: Krieger-Dougherty viscosity, wt%->phi mass balance, ionic strength, Debye length, IEP-based electrostatic regime — 19 tests
- `core/validation.py` literature back-test harness (group by chemistry, least-squares Kp per group)

## NEXT
P1 gate: 3 published RR-vs-P*V datasets within +/-15%. Currently 2 of the inherited
datasets pass (Mariscal 2020 MAPE 12.9%, US9499721B2 groups 1.4-3.6%); a third
independent source is being acquired. Then `docs/derivations.md` P1 entry + commit.

## BLOCKED
(none)

## VALIDATION
| dataset | metric | model error |
|---|---|---|
| mariscal2020_peteos_ceria_pv_3x3 (n=9, digitized) | Preston P*V shape, Kp fitted | MAPE 12.9%, max 20.5% |
| us9499721b2_teos_silica (best group, n=4, table) | Preston P*V shape, Kp fitted | MAPE 3.6%, max 4.4% |
| kenchappa2021_softpad_hdp_oxide (n=3, table) | Preston P*V shape, Kp fitted | MAPE 42.8% — pad/contact effect, P2 |

## OWNER QUESTIONS
1. Absolute RR or ranking? Kp is back-calculated from one literature point, so
   absolute values outside that regime can be far off. Do you have >=3 measured
   RR points we may use to re-calibrate Kp (kept out of git)?
2. Which film stack matters most first: Cu, W, STI oxide, or poly-Si?
