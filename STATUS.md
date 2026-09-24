# CMP-Sim — STATUS

## DONE (phase, module, tests)
- P1 Preston · P2 GW contact · P3 Luo-Dornfeld · P4 chemistry (pH/oxidizer/
  inhibitor + Arrhenius) · P5 radial uniformity · P6 pattern dishing/erosion
  · P7 pad glazing & conditioner ageing · P8 defect proxy. **774 tests pass.**
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
- **`cmp-sim accuracy` now prints `repl%` — each dataset's own reproducibility.**
  Reporting only: medians (19.5%/22.6%), scored count (43) and beats-mean (33) all
  unmoved, asserted by test. Three datasets marked `floor` (already at their own
  noise) so they stop reading as model failures. Audit of all 49 files found the
  blank column covers THREE states, not one: rates-are-averages-with-spread-
  withheld (du2004 says so), digitized-with-stated-read-error (bouvet2002_w 1.0%,
  _ti 2.7%), and nothing-stated. That separates bouvet2002_w (2.3% vs 1.0% floor,
  finished) from bouvet2002_ti (30.7% vs 2.7%, a real miss) — previously
  indistinguishable. `at_noise_floor` is None, never False, when unmeasured.
- **Borrowed-pack audit** (`tests/test_borrowed_pack_audit.py`): 7 datasets score a
  film with another film's pack, in 3 kinds — justified by mechanism (5: sti_ceria
  on oxide, since its exponents split by ABRASIVE not film), deliberate negative
  controls (2: carbide2023/sic2023 on the oxide pack on purpose, each noting the
  gap its bad number documents), and placeholder packs on unsupported films (2).
  **New find: us8142675b2_pt scores 12.3% on an oxide pack — a PLAUSIBLE number
  from another material's constants**, which is more dangerous than Ti's visible
  30.7%. Audit's own blind spot named: 23/49 datasets declare no film at all, so
  prose inference was needed to surface both negative controls. No packs created.
- **Ti declared UNSUPPORTED (limit 9).** bouvet2002_ti was the largest miss vs its
  own floor (30.7% vs 2.7% digitisation). Cause found: three sweeps from ONE figure
  (Ti/W/oxide, same tool+slurry) have exponents -0.454 / -0.049 / +0.001, and the
  shared pack carries -0.05 = W's value. Fitting Ti's -0.45 was REJECTED: it is the
  only Ti data in the corpus, so the constant would be tested on its own fitting
  set (and R^2 is only 0.89 on 4 digitised points). Miss kept visible in the score.
- **`docs/limits.md` — one page for what the model REFUSES to predict.** 9 entries,
  each with the measurement that establishes the limit, the refit that was rejected
  and its cost, and the experiment that would lift it. Distinct from
  open-questions.md (undecided items): these are DECIDED refusals. Guarded by
  tests/test_limits_doc.py (11 tests) both ways — a limit-enforcing test not cited
  on the page fails, and a cited test that no longer exists fails. README's
  validation table now points at it and states the noise-floor caveat: only 5
  datasets have replicates, so elsewhere the achievable floor is UNKNOWN.
- **Two ceria datasets demand OPPOSITE pH terms; the pack keeps the right one.**
  netzband2020 (49.2%) has a VALLEY — 198/113/200/213 over pH 4/6/8/10, two IEPs
  (oxide 2-3, ceria ~8) with pH 6 optimal for neither — and `ph_response` is
  unimodal, so no constant produces it. Ruled out first: NOT a scale offset (the
  benchtop 2.25 cm2 coupon puts absolute rate 8x out, but 49.2% is already
  scale-free, k=0.128) and NOT out-of-range. A netzband-only refit reaches 15.0%
  by going nearly FLAT — and costs dandu2009 (81x swing, the set the constants
  were fitted to) 31.5% -> 492.6%. Left alone, deliberately.
- **The oxidizer term's SIGN flips with PRESSURE, inside one experiment.**
  Diagnosed the worst remaining miss (jani2025 RSM heldout, 51.2%): oxidizer
  correlates +0.76 with measurement but +0.04 with prediction — the term is blind,
  not mis-scaled (ratio spread 4.1x rules out a Kp offset). Cu sweeps contradict:
  ihnfeldt2008 peaks ~0.1 wt%, jani2025 still rising at 6, us8501625b2 shows BOTH
  signs. "Sign tracks BTA" FALSIFIED (both signs at the same 0.08 mM). The two
  groups differ ONLY in down force: 2 psi falls 8200->6300, 1 psi rises
  1900->3900. Left UNFITTED — two pressures cannot fit a coupling — so 51.2%
  stays an honest miss with a named cause. Confound: GT07's peak is ALUMINA,
  jani2025 is silica; abrasive type and pressure co-vary and cannot be separated.
- **Some datasets cannot be predicted better than they were measured.**
  hong2007's three IDENTICAL zero-inhibitor rows report 2650/2400/1850 A/min =
  13.0% replicate scatter, so 13% is the FLOOR on achievable error; the model's
  14.8% is at it. Also a correction: STATUS recorded hong2007's flat baseline as
  12.6%; it is 14.8%, identical to the model — it ties the mean, never lost to
  it. Corpus-wide, 3 datasets sit at/below their own replicate scatter, incl.
  sic2026 DOE50 (34.0% vs 38.5% scatter) — this session's pH refit crossed it
  from above the noise floor to below, so further fitting there is fitting noise.
  Only 5 datasets have replicates at all; the rest have an UNKNOWN floor.
- **Out-of-range pH is a WARNING, not a gate — measured, not assumed.** Fully
  in-range datasets (n=19) median 18.9%; fully out-of-range (n=11) 19.4%;
  Mann-Whitney z=-0.15. No separation, and the out-of-range group holds some of
  the best results (bouvet2002_w 2.3%, ep3161098b1 7.1%, lai2001 8.7%). A gate
  would discard working predictions. Differs from the oxidizer gate, which WAS
  justified: there the term's SIGN reversed (confidently wrong); here the model
  is merely less constrained. Gate = "would be wrong", warning = "rests on
  fewer measurements".
- **A validity range is the FITTING EXPERIMENT's span, never the union.** All 7
  pH-active packs now declare `ph_valid_range` (+ oxide_silica_calibrated_pad,
  which the enumerating test caught). oxide_silica is served by 9 datasets
  spanning pH 1.75-12.5 but 8 hold pH fixed and constrain nothing, so its range
  is li2021's 10-12.5 — the union would claim support no experiment gives.
  Consequence stated, not hidden: bouvet2002/us8142675b2/ep3161098b1/us9499721b2/
  carbide2023/mo2026/yang2023 now warn as out-of-range. No rate changed.
- **An inert constant that looks active is worse than no constant.**
  `sic_ceria_h2o2` had `ph_response_width: null` (to block the inherited acid
  ceria optimum) but still declared the inherited `ph_peak: 4.5` — a constant
  that looks like a SiC optimum and does nothing; the engine's own INERT warning
  had been firing. Its stated reason ("DOE50 cannot isolate the pH axis") was
  checkable and false: 5 groups isolate pH 9/10/11. Fitted peak 10.5 / width
  1.25 / floor 0.10 = 27.5% vs 57.1% inert, and ALKALINE, as the pack's own
  mechanism argument predicted. Interior to its range (unlike the bound packs).
  Trade recorded: DOE50 39.3->34.0, three held-out SiC sets worsen ~0.1-1.3.
- **Validity ranges: a bounded peak has an UNMEASURED side.** The three packs
  whose `ph_peak` is a bound at the data edge (oxide_silica_anionic 2.0,
  cu_alkaline_benzenesulfonic 6.2, cu_h2o2_bta 3.0) had no measured limb beyond
  it and an acid floor of 0, so the model decayed to 0.00 A/min at pH 0.5 with
  no warning (the "2.5 widths" check doesn't fire — pH 1.0 is only 2.0 widths).
  Each now declares `ph_valid_range` = its source table's span, and the engine
  warns outside it, naming the floor and calling a ZERO floor a refusal rather
  than a number. cu_h2o2_bta carries TWO ranges (pH constants 3-6, oxidizer
  constants 2-6.25) — different terms, different experiments, not merged.
- **Pack blindness audit (`tests/test_pack_axis_blindness_audit.py`)**: fails
  if any pack declares no response on an axis its own datasets sweep. One hit —
  `w_fe_oxidizer` on pH — and it is a SOURCED NULL RESULT, re-derived by the
  test from 6 matched pairs (pH 3 vs 6 at matched oxidizer+abrasive: mean ratio
  0.958, sign inconsistent, vs an 8x oxidizer effect in the same table). Null
  results and omissions look identical from outside, so silence is now declared
  in the pack with its table and scope (pH 3-6 only).
- **A missing pH term hid inside the OXIDIZER term.**
  `cu_alkaline_benzenesulfonic` declared no pH response at all (only a
  meaningless inherited `ph_ref: 4.0` from the acidic parent), so a measured
  3.4x pH fall predicted one constant = predict-the-mean, 51.0%. Worse, the
  pack's `oxidizer_peak_wt_pct: 1.0` was justified as "rate falls with
  oxidiser" — but that dataset's pH DRIFTS 10.2→8.5 as acidic H2O2 is added,
  while a KOH-BUFFERED one (us20110165777a1, pH 11.1) measures it FLAT and the
  patent says so explicitly. Added the pH term, peak bounded to the lowest
  measured pH 6.2 (free fit prefers 3.3, outside the data). HELD-OUT evidence:
  h2o2_series 51.7%→12.7%, benzenesulfonic 29.6%→26.8%, both now beat the
  mean. Corpus 20.2%→19.5% trend, 22.6%→21.7% LOO.
- **The velocity exponent is UNRESOLVABLE by this corpus — not fitted.**
  Isolated groups give -0.42 / +0.62 / +0.86 / +0.86 / +1.10 where Preston says
  1.0, and the two datasets need OPPOSITE pressure dependences (mariscal falls
  1.10->0.62 with P, us6918821b2 rises -0.42->0.86). The negative group is the
  patent's own point: an IC1000 pad LOSES Cu rate with speed at low down force
  (lubrication regime, no channel in Preston). A global fit would land ~0.86,
  be wrong at both ends of both datasets, and improve the pooled median.
  Nothing fitted; a test fails if any pack ever declares `velocity_exponent`.
- **NO universal "second pH channel" — hypothesis tested and FALSIFIED.**
  The three pH residuals are three different shapes, and two of them share a
  pack: dandu2009 is a BELL (peak pH 4-5.5), netzband2020 is a V (minimum at
  pH 6, both ends high), same `sti_ceria`, same film, same abrasive. A rising
  alkaline term would have to lift netzband 4.3-4.6x at pH 8/10 — exactly where
  dandu already matches to 1.03/0.96. Fixing one breaks the other, so NOTHING
  was added to the model; the contradiction is pinned as a measurement fact.
  Real lead (recorded, not built): Netzband varies the Ce3+/Ce4+ OXIDATION
  STATE, which the pack holds fixed — a ceria-specific coupling, not a pH term.
- **pH is NOT thin (unlike velocity) and the optimum follows the abrasive's
  CHARGE.** Isolated-pH groups: 12 groups / 66 pts (velocity had 29), isolated
  median ~30% vs pooled 39.3% — isolation does not rescue it, so the term is
  genuinely the weakest physics. Worst group (CN109609035B, 94.7%) was a THIRD
  silica system: anionic silica peaks at or below pH 2 on the same TEOS film
  where cationic core-shell peaks at 4.9 and plain silica at 11 — ordered by
  particle charge vs the oxide's IEP. New pack `oxide_silica_anionic`:
  94.7% -> 32.1%, pH axis 39.3% -> 32.1%, li2021 untouched at 0.2%.
  ⚠ Stops at 32%: the measured pH-6 UPTURN needs a second additive pH channel
  (alkaline hydrolysis), a functional-form change — recorded, not fitted around.
- **The Cu pH optimum is a BOUND, from ONE system.** `ph_peak` was 4.0 =
  "the pack's operating pH", with a note asking for a pH 2-6 sweep — which was
  already in the repo. US20080090500A1 T4 falls monotonically pH 3->6 at all
  three silica loadings, so the optimum is at or BELOW pH 3 and 4.0 predicted a
  rise where the patent measures a 10-24% drop. Peak -> 3.0 (edge of data),
  width 4.1 -> 4.45: shape 10.1% -> 4.3% on those 12 points. Refused to pool
  the alkaline US9200180B2 leg for 17 points — it is BTA-free benzenesulfonic
  and has its OWN pack; same trap `oxide_silica_aminosilane` was split to avoid.
  ⚠ Zero effect on the corpus median: that table prints no down force.
- **The oxidizer term's SIGN belongs to the pH branch — regime gate.**
  Miranda's 2x2 moves H2O2 1.5->3.5 wt% and gets +49% at pH 4, -86% at pH 8
  (interaction p=0.0207, Pourbaix: soluble Cu2+ vs hard CuO). One constant
  cannot be both, so `cu_h2o2_bta` declares `oxidizer_ph_window: [2.0, 6.25]`
  — bounds read off the gated constants' own provenance — and OUTSIDE it the
  term is switched off and says so, instead of extrapolating a wrong sign.
  Scoring now separates "declined" from "wrong"; a gate on an axis a dataset
  holds CONSTANT must not silence it (that rule saved 3 good datasets).
  ⚠ Corpus 20.2% -> 19.5% is NOT a physics gain: 2 datasets stopped answering.
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
Close the blind spot the borrowed-pack audit named: 23 of 49 datasets declare no
`film`, so the label-vs-pack check cannot see them and prose inference had to
stand in. Fill in `film:` for every dataset from its own source — the film is
stated in each paper/patent, so this is transcription, not inference — using
`other` where the film genuinely has no pack (as Ti and Pt already do). Then
tighten the audit to fail on ANY undeclared film rather than merely warning that
most are missing. Expect new mismatches to surface; classify them, do not fix
them by creating packs. Verify the corpus medians are unmoved: declaring a film
must not change a single prediction.

## BLOCKED  (numbers + sources: `docs/open-questions.md`)
0. `si` over-predicts at bare defaults (10,776 vs a 100–3,000 envelope); Kp
   rests on one Seidel 1990 point. Needs a second Si-substrate point.
1. Velocity inversion is NOT a lubrication effect — no dataset will fix it.
   λ = 0.001401·(rpm/P) exactly, i.e. λ IS the pseudo-Sommerfeld number V/p
   (Wu & Liao 2016, doi:10.5772/64484) up to one constant, so calibrating it
   with measured viscosity/roughness only rescales and cannot reorder. The
   inverting rows (λ .056/.112/.187) OVERLAP the non-inverting ones
   (.021/.042/.070), and mariscal2020 — 9 rows that never invert — sits inside
   that range. A threshold would need to be below .056 and above .070 at once.
   (This corrects the earlier entry asking for a film-thickness dataset.)
   Surviving evidence: λ ORDERING predicts over-prediction independently in
   both datasets (ρ −0.714, −0.517). Pad CONTACT was then tested and also
   fails: `plasticity_index`/`pad_limited_plasticity_lambda` are constant
   within each dataset (consumable properties) and differ between them the
   WRONG way (inverting set is MORE plastic ⇒ predicts more removal), while
   `summit_saturation` = 0.00739·P exactly — down force relabelled. Its clean
   separation (0.0111 inverting vs ≥0.0148) is therefore just "P < 2 psi"
   fitted to one patent's low-force arm. Twice now the candidate criterion was
   the operating point in disguise (λ=V/p, saturation=P).
   NEEDED: pad surface stats (asperity density/radius by confocal or AFM, or
   glazing state) measured beside a rate-vs-speed sweep. Nothing in the corpus
   reports them.
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

All axes (394 pts, 43/49 scored + 2 DECLINED): median **19.5%** trend,
**21.7%** LOO. By axis — size 11.2%, oxidizer 20.2%, loading 22.9%,
pressure 25.3%, pH 31.5%, velocity 44.1%. 33/43 beat predict-the-mean. ⚠ Caveats, all against us: the axis
medians pool datasets that vary several things at once — velocity's 44.1% is
11.7% once isolated (thin axis, 29 pts), while pH's holds up under isolation
(12 groups / 66 pts, ~30%) so it IS the weakest term. 2 Cu datasets are
DECLINED rather than answered wrongly (honesty, not accuracy), and the median
ticked 19.5 -> 20.2% because 4 newly-scorable datasets entered the pool.
Resume handover: `~/CMP-SIM-FOR-RESUME.md`
