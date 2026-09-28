# Changelog

All notable changes to CMP-Sim. Newest first.

## Unreleased

### Added — a named reader for every `scale-only` constant, and the plausibility envelope measured across the corpus (2026-09-28)
- **§57 left 14 constants classified `scale-only`**: perturbing them moves the
  predicted rate (up to 929%) and leaves every block's `shape_mape` *exactly*
  unchanged, because the headline score fits one free multiplicative scale per
  dataset. No corpus growth repairs that. `tools/scale_only_jurisdiction_probe.py`
  asks the question that *is* answerable — does **any** reader see it? —
  and finds **12 of 14 graded by `absolute_scale_audit`** (the only reader here
  that looks at absolute rate), three of them crossing that audit's own 3× bar.
  The deliverable is a **declaration of jurisdiction**: "the median cannot test
  this constant" was true and written down nowhere, so a wrong value looked, in
  every report, exactly like a graded one. No constant, prediction or median
  changed.
- The probe is checkable rather than trusted: `kp_m_per_pa` multiplies every
  predicted rate, so it must move `log10(scale)` by exactly `|log10 f|`. The
  three recovered controls come back at **2.8e-17 / 2.2e-16 / 2.2e-16**.
- **The by-product is larger than the question, and it is a negative result about
  this repository's own guard.** For the 2 constants with no scored reader the
  probe falls back to `core/sanity.py`'s per-film plausibility envelope, and both
  come back **NO READER, by different mechanisms**: `dlc` has no published
  envelope at all (correctly — no source publishes an amorphous-carbon CMP rate
  at a stated pressure and velocity), and `si`'s envelope is **already firing on
  the unperturbed run** (8,830 Å/min against 100–3,000), so every perturbation
  looks identical to it. "First complains at ×1" is a saturated alarm, not a
  bound.
- `tools/envelope_saturation_census.py` measures how general that is — nothing
  had, because `check_rate` is a per-run annotation no probe read across the
  corpus, so "the envelope would catch a 10× error" had aged into fact. It fires
  on **30 of 52** scored blocks, and splits them by something the envelope itself
  cannot see, the **measurement** at the same row: 11 `model-scale-failure`
  (measured inside, predicted outside — what the guard is for; `gong2024` on
  25/25 rows), 8 `mixed`, 11 `envelope-too-narrow` (measured outside *too*, so
  the warning is about the envelope and is not a model defect), 4 `no-envelope`.
- **Rejected:** widening any envelope to lower that count — every bound cites a
  measurement and `core/sanity.py`'s own header records the `snag` entry being
  *deleted* for citing nothing ("a guard that cannot fire is worse than no
  guard"); and scoring the headline on absolute scale, which §34 already measured
  as trading one failure for another. Both have mutation guards.
- `docs/limits.md` §58;
  `tests/test_scale_only_constants_have_a_named_reader.py` (14 pass, 6/6
  mutations caught). Median unchanged: 18.9% published, 19.5% held-out, 21.3%
  leave-one-out.

### Fixed — the published median was computed on a DISPLAY rounding (2026-09-28)
- **Every error number this repository has ever published was computed on a
  removal rate quantised to 0.1 Å/min.** `StateResult.summary()` publishes
  `round(mean_rr_angstrom_per_min, 1)` — correct for a JSON result a person
  reads — and `cmp_sim/core/predictive_score._predict_with_gate` read that very
  field. The relative size of the quantisation is set by the *magnitude* of the
  rate: 3e-5 on a Cu block near 3000 Å/min, and up to **1.45% per row** on
  4H-SiC, which is chemically inert and polishes at a few Å/min
  (`sic_ceria_h2o2`'s slowest scored row predicts 3.44 Å/min).
- Because the quantisation **does not scale with Kp**, it survived the shape
  score's one free multiplicative scale per block — so a purely multiplicative
  constant could move a statistic it is mathematically invariant to.
  `sic_ceria_h2o2.kp_m_per_pa` moved four blocks' `shape_mape` by up to
  **1.303 pp**; per-row ratios under a ×0.8 perturbation came back
  0.8235 / 0.7895 / 0.8049 where `cu_h2o2_bta`'s ten blocks all return 0.8000.
- `summary()` now also publishes `removal_rate_A_per_min_exact` at full
  precision, and the scorer reads it (falling back to the rounded field, so an
  older result stays scorable rather than becoming silently unscorable). The
  rounded field is **unchanged**: it is right for its audience. After the fix
  every shape delta under a Kp perturbation is **0.000 pp** on every pack.
- **Median unchanged and asserted** — the SHAPE median, which is the headline:
  published upper median 18.9%, held-out 19.5%, before and after. The
  quantisation was symmetric noise on four SiC blocks, none at the centre of a
  48-block distribution. Zero movement is the correct outcome for an honesty
  fix, and the test says so.
- **Leave-one-out moves 20.9% → 21.3%, and the direction matters**: the old
  number was *flattered* by the rounding. The LOO-median block is the 4H-SiC
  loading ladder at 3.44 Å/min; un-rounded its own LOO goes 20.90 → 21.32 and
  it swaps rank with `us6564116b2_oxide_taguchi_L25` (21.28). §55's physics
  gain is not withdrawn — both sides of that comparison were measured on the
  same quantised scorer — but the absolute pin is.

### Fixed — `beats_flat` decided exact ties on floating-point noise (2026-09-28)
- Found by the same measurement. The baseline check that says whether the
  physics contributed anything was `shape_mape < flat_mape`, a **strict
  comparison with no margin** — and a flat block (§36) reproduces `flat_mape`
  *exactly*, because the shape score's free scale fits its constant prediction
  to the measured mean. Five blocks here agree to within 2e-14 (`bae2022`,
  `hong2007`, `kenchappa2021`, `lee2021`, `phm2016`), so the published count
  was being decided on float noise: un-rounding the rate flipped two of them
  from `False` to `True` while neither score moved by 1e-9.
- The repository's own test file had **described** this tie in a comment since
  2026-09-27 and left it live. `beats_flat` now requires
  `BEATS_FLAT_MARGIN_PP`, and a tie counts as **not** beating the mean: a block
  that merely reproduces the mean has added nothing. Published count
  **37 → 36**, now stable under the un-rounding instead of flipping with it.

- `docs/limits.md` §57;
  `tests/test_published_median_is_not_a_display_rounding.py` (27 pass), whose
  arithmetic is pinned on synthetic numbers and whose per-pack Kp-invariance
  check derives its pack list from the corpus at test time. Six mutations run,
  six caught — including one that escaped the first draft because the guard
  was a grep of the probe's source rather than a measurement of its behaviour.

### Added — §56's largest class is now measured rather than inferred (2026-09-28)
- `tools/quiet_constant_response_probe.py` takes the 35 constants §56 filed as
  `untestable-no-sweep-in-reach` — decided from an *axis name mapping*, a proxy
  — and answers the question directly: perturb the constant (§43 rules: both
  directions, small factors first, largest response kept) and re-score the
  held-out blocks in its reach through the **shipping** scorer. Does the
  published number move?
- That separates three states previously conflated: **19 `rate-inert`**
  (nothing in reach consumes them — the §53/§17 class, unfalsifiable because
  unreachable; 13 of them `sic_alumina_kmno4`, a pack standing on one source),
  **14 `scale-only`** (the rate moves up to 60% and the shape score cannot see
  it, *by the scorer's own construction* — this cannot be fixed by adding
  data), and **0 `shape-testable`**: all three apparent members were the
  rounding artefact above.
- `tools/rate_quantisation_probe.py` re-scores every block against an
  unrounded rate read from the result object, reporting each block's minimum
  predicted rate and the quantisation it implies, so the reading can never be
  quoted without the magnitude that produces it.

### Added — the orphan class §55 opened is now enumerable, and its next two members are priced and refused (2026-09-28)
- `tools/departed_evidence_census.py` asks, of every live numeric pack
  constant, **whether anything in the scored corpus could still contradict
  it**: it computes the constant's *reach* (packs whose effective parameter of
  that name is this object, obtained by loading every pack so inheritance and
  shadowing are exact), the datasets its `source:` names, and the held-out
  scored blocks inside the reach that sweep an axis it governs. This is the
  direction `tools/calibration_flag_audit.py` structurally cannot look: that
  audit **excuses** a cross-pack citation as ordinary evidence reuse, and that
  excuse is where these findings live.
  361 constants: 80 testable, 69 reference-condition, 174 with no axis mapping,
  35 with home evidence but no sweep in reach, 1 declared cross-system, and
  **2 in the §55 orphan class** — `cu_alkaline_benzenesulfonic` and
  `w_fe_oxidizer`'s `abrasive_size_exponent`.
- `tools/size_exponent_derivation_price.py` prices §55's repair on this axis
  before anyone applies it: replacing the declared exponent with the engine's
  derived `n_d = -q(1-alpha*chi)+beta` scores **1 better / 10 worse**, median
  shape **19.23% -> 25.13%**, with the damage concentrated on the blocks that
  actually sweep size. **Refused** — §55's rule is asymmetric on purpose: a
  derived value is adopted *because* it is derived, and only if it is not
  worse. Re-assigning the departed datasets back was priced too (W: exactly
  neutral, no median movement; Cu: 0.4 pp of shape for a 6.4x absolute-scale
  error) and also refused. **Zero constants changed; both medians unchanged
  (18.9% published, 19.5% held out) — the correct outcome for an honesty fix.**
- Both packs' notes now carry their untestability, the numbers behind both
  refused repairs, and the measurement that would end it. `docs/limits.md` §56;
  `tests/test_departed_evidence_orphans_are_priced_and_refused.py` (11 tests,
  every number re-measured at run time, 5 mutations verified to turn it red).

### Fixed — an orphaned fitted constant was withdrawn, and the derivation it masked is better everywhere (2026-09-28)
- `sic_ceria_h2o2.abrasive_conc_exponent` (+0.227, a fit over 17 matched pairs)
  is now **null**, so the engine's own three-factor contact decomposition
  supplies the surface-area limit `n_C = p*(1-alpha*chi) = +1/3` — derived from
  no data and no free parameter. **A constant was deleted, not refitted.**
  Measured through the shipping solver: **0 blocks worse, 3 better**
  (`liang2026_4hsic_ceria_composite_h2o2_conc` 18.17 % → **11.21 %**,
  `su2011_procengr_6hsic_alumina_abrasive_conc` 14.36 % → 13.98 %,
  `sic2026_ceria_h2o2_ph_DOE50` 33.96 % → 33.47 %), and both meaningfully
  improved blocks are **held out**. Headline median unchanged at 18.9 % (no
  middle dataset moved — it is a counting statistic); leave-one-out
  21.3 % → 20.9 %; the held-out must-cross count falls **3 → 2**.
- How it was found: the neighbouring `abrasive_conc_half_wt_pct: null` was
  justified by an **enumeration** of six loading ladders whose decisive falling
  member, Entegris US 2022/0315802 A1, had been **moved to another pack** by
  ruling #49-B. The citation still resolved, the grade still read `literature`,
  and nothing broke — so the constant aged into fact. Re-running the enumeration
  finds **zero** falling ladders under this pack. The sibling constant on the
  same axis had already been corrected for exactly this cause by ruling #52,
  which fixed the instance and not the class.
- The `C_half` null **survives**, for a new and measured reason rather than the
  dissolved one: only one loading ladder remains under this pack (a saturation
  constant is not identifiable from it), and every scanned value from 1 to
  8 wt% leaves the binding block worse than the derivation.
- New: `tools/sic_conc_half_refusal_reaudit.py` (never writes — asserted),
  `tests/test_orphaned_conc_constant_withdrawn_for_derivation.py` (11 tests,
  every number re-measured at run time), `docs/limits.md` §55.
- Also corrected: `test_load_sharing_onset_is_refuted_by_the_data.py` priced its
  counterfactual with a **ratio** bar (`after < before/3`), which encodes the
  incumbent model's error as a property of the counterfactual and tightens on
  its own whenever the shipping model improves for an unrelated reason. Re-pinned
  as an absolute gain in percentage points plus a direction.

### Measured — twelve cited, graded constants that reach nothing AND that the corpus refutes (2026-09-28)
- Four pack families declare a three-parameter **peaked particle-size curve**
  (`abrasive_size_peak_nm` / `_exp_below_peak` / `_exp_above_peak`): twelve
  constants, every one `confidence: literature` with a primary citation. Measured
  through the shipping solver, **none of the twelve moves any prediction
  (0.000000 %)**. The piecewise curve is implemented in the inherited layer
  (`legacy/sim/factors.py`) while the shipping size factor is one pooled exponent
  per abrasive family (`cmp_sim/models/luo_dornfeld.py`), which never consults a
  peak. §42 (does the engine name the key?) and a pack audit (does the pack
  declare it?) both pass; only the (key, pack) measurement fails.
- §49's probe could not have caught these: it perturbs from each pack's reference
  composition, where `d == d_ref` makes every size factor exactly 1.0 for *every*
  exponent. The base run is displaced to `1.7 x abrasive_ref_size_nm` first, and
  §43's instrument control passes on all six packs (`abrasive_size_nm` itself
  moves the rate 3.5 / 12.3 / 82.8 %).
- **The corrective half inverts §49's.** There the declared value won when priced
  and the entry protected it; here it loses twice. Priced on 8 pure size sweeps
  the pooled exponent wins **8 of 8** (that column is partly in-sample, so it is
  stated as an upper bound). Fit-free, **6 of 8 sweeps refute** the declared peak
  — decisively `bouvet2002_oxide_silica_size_sweep`, the corpus's only genuine
  colloidal-silica-on-thermal-oxide match, whose authors print the maximum at
  **25 nm** (p. 1560) where the declared curve requires a rise to 80 nm. Two
  primary sources disagree about the optimum's position by 3.2x in one system.
- **Nothing was wired and no value moved**: the repair is that all twelve now
  state their own inertness, per §49's rule that an unquotable number ages into
  fact. Re-fitting the peak onto a refuting dataset's argmax was rejected (it
  fits a dead term to its own refutation, and 210.7 nm is a *range endpoint*,
  which §44 forbids reading as an optimum), as was deleting the constants (the
  inherited branch survives, so a later session would re-wire them with no
  record). Median **unchanged at 18.9 % / 19.5 %**, which is the correct outcome
  for a change that touches zero constants.
- A false claim fell out of it: `sic_ceria_h2o2`'s above-peak note asserted the
  exponent "is only used when the size goes above 163 nm". It is false at every
  size. **Never write "this term activates under condition X" from reading the
  source; run the solver at X.**
- `docs/limits.md` §53, `research/size_peak_reachability.yaml`,
  `tools/size_peak_reachability_probe.py`,
  `tests/test_declared_size_peak_is_inert_and_refuted.py` (20 tests; calibrated
  against the bug — re-fitting the silica peak fails 2, deleting one INERT marker
  from a folded note fails 1).

### Measured — a single-sourced refusal named a MECHANISM, and the mechanism is falsifiable outside the corpus (2026-09-28)
- `sti_ceria` carries `ph_response_is_unimodal_but_this_system_is_not: true`,
  which stops a later session repairing `netzband2020` (49.2 %) by flattening
  `ph_peak` at a 15x cost to `dandu2009`. Its stated ground was Netzband's own
  explanation of the valley: **two isoelectric points** (oxide pH 2-3, ceria
  ~8), pH 6 optimal for neither. That is a claim about the world, not about the
  model's function, so it predicts a valley in *any* ceria-on-oxide pH sweep
  with those two IEPs — and had never been tested outside the dataset that
  produced it.
- Dawkins 2019 (UAlberta PhD, doi:10.7939/r3-g3c2-xe63) is that test: five pH
  levels, two abrasive compositions, independent institution, tool, ceria size
  (5 nm vs 68 nm) and decade. It measures the **same two IEPs** in its own
  conclusions (ceria 9.0-9.6; silica negative across pH 3-13) and shows **no
  valley in either panel**:

  | series | 3.5 | 4 | 6 | 8 | 10 | shape | best ONE bell |
  |---|---|---|---|---|---|---|---|
  | Fig 5-12(a) ceria:silica 0.1 | 365 | 375 | 305 | 182 | 183 | falls, then flat | **1.7 %** |
  | Fig 5-12(b) ceria:silica 0.2 | 202 | 381 | 420 | 315 | 202 | single peak, pH 6 | **10.4 %** |
  | `netzband2020` (incumbent) | — | 198 | 113 | 200 | 213 | **valley** | 14.9 % |

  Mechanism present, consequence absent. Two of three independent ceria pH
  series are single-extremum and the shipping `ph_response` represents them, so
  netzband is the **dissenting member**, not the representative one — the case
  for keeping one bell gets stronger, not weaker.
- The figure is a raster (0 vector paths), so the reading was graded against
  **six quantities the thesis prints in prose**; all six reproduce, worst
  disagreement **3.6 %**. That precision then became the bar and **caught this
  entry's own first draft**: the test originally asked for interior minima
  arithmetically and failed on panel (a), where 182 then 183 is literally a
  minimum — a 0.5 % step, 1/7 of the reading precision, i.e. §40's
  noise-as-finding error recurring inside a tool built after §40. The bar is
  now read from the evidence file and paired with a control (netzband's 43 %
  dip must still register at the same bar).
- **Scope narrowed, decision unchanged**: from "this system is not unimodal
  *because* two IEPs straddle the range" to "*this dataset's* series is
  non-unimodal, for a reason not yet identified". The superseded sentence is
  kept in place beside its refutation.
- **No constant added or changed, no exponent fitted, no dataset entered or
  left the corpus; median unchanged at 18.9 % / 19.5 % held out** — the correct
  outcome for an honesty fix, asserted rather than hoped for.
- Rejected: refitting `ph_peak` (a refuted *reason* is not a licence to refit);
  withdrawing the marker (the structural failure is still real); promoting
  Dawkins into the scored corpus (ceria/silica **composite** abrasive under a
  pure-ceria pack = §27); deleting the old mechanism sentence (restores the
  undetectable state).
- Added `docs/limits.md` §50, `research/ceria_ph_valley_second_source.yaml`,
  `tools/ceria_ph_valley_second_source_probe.py`,
  `tests/test_ceria_ph_valley_is_not_a_general_two_iep_effect.py` (16 tests).

### Measured — §42's wiring audit is per KEY, and reachability is a property of the (key, PACK) pair (2026-09-28)
- §42 asked "a pack key that is DECLARED and reads nothing" per **key**: does
  any engine path read this name? `oxidizer_peak_wt_pct` passes — three packs
  declare it with a unit, a source and a confidence grade, and
  `chemical_rate.py::peaked_oxidizer_response` consumes it. Measured per
  **(key, pack)** through the shipping solver, two of the three invert:

  | pack | declared | grade | max response |
  |---|---|---|---|
  | `cu_h2o2_bta` | 3.0 wt% | `literature` | **13.889 %** reached |
  | `cu_alkaline_benzenesulfonic` | 1.0 wt% | `estimated` | **0.000 %** unreachable |
  | `w_fe_oxidizer` | 6.0 wt% | `estimated` | **0.000 %** unreachable |

  The branch consuming the peak is selected by a *different* key,
  `oxidizer_peak_shape_K`, which only `cu_h2o2_bta` declares; the other two
  return from the Langmuir branch first. Both zeros pass §43's control (their
  own `slurry_ph` / `abrasive_wt_pct` did move), so they are wiring facts.
  Neither the key-level audit nor the pack-level audit can see this: neither
  asks whether a key a pack declares moves **that pack's** rate.
- **The two inert packs' notes disagreed, and that is the sharper finding.**
  `w_fe_oxidizer` says `(비활성 — Langmuir 경로로 대체됨, 판정#19)` — inactive,
  superseded — and is graded `estimated`, so it was honest.
  `cu_alkaline_benzenesulfonic` said the opposite: that the peak is placed at
  the operating point "so the whole observed band falls on the post-peak side",
  a claim that the value **acts**. It does not; the band falls because of the
  Langmuir passivation term, and the stated design intent never executes. That
  note is corrected in place (value and grade unchanged) because it is the kind
  of prose a later session reasons from. Reading the notes cannot separate the
  two cases — both read as deliberate — only measurement per (key, pack) can.
- The live peak's POSITION was priced against the corpus and the declared value
  **won**. The argument this entry was drafted to make — every scored H2O2 level
  sits past every candidate maximum, so the position is unfalsifiable (§35) —
  was re-scored and found **false**: 3 of 10 Cu blocks respond, one by 58 pp,
  and the declared 3.0 wt% is best on all three with the error monotone in
  distance (`jani2025` 5.6 → 26.7 %, held-out RSM 47.9 → 62.1 %, `us8501625b2`
  20.2 → 78.3 % as the peak moves to Lin & Du 2009's measured positions). The
  refuted draft is kept beside the refutation; how it failed is the lesson.
  Physically the transplant fails on the source's own data: that maximum
  marches 0.90 → 0.74 → 0.66 wt% under **dilution alone**, i.e. it is set by
  inhibitor and complexant concentrations the paper withholds.
- The species gate's stated REASON was corrected, and its decision was not.
  It rested on a sign claim ("oxalate rises, glycine decreases monotonically")
  read from one patent figure whose three points all start at 0.5 wt% H2O2.
  Two independent sources below that find the rate rising — Lin & Du resolve
  the maximum at 0.66-0.90 wt%, and `ihnfeldt2008_cu_alumina_ph_oxidizer_chelator`,
  **already a scored dataset here**, rises 0.1 → 2.0 wt% at pH 3.0 with 0.1 M
  glycine. The response is peaked, so the justification becomes structural: a
  saturating Langmuir promoter and a Langmuir passivation term are monotone for
  every K and cannot represent a peak at all. The contradicting evidence was in
  the corpus the whole time; nothing compared it to the note, so nothing failed.
- **No constant added, no pack value changed, no exponent fitted, gate
  unchanged, median unchanged at 18.9 % / 19.5 % held out** — the correct
  outcome for a priced-and-refused change plus an honesty fix.
- `docs/limits.md` §49 + `tests/test_declared_peak_reaches_nothing_on_two_packs.py`
  (12 pass / 1 skip, all re-measured at run time),
  `research/cu_oxidizer_peak_position_evidence.yaml`,
  `tools/oxidizer_peak_reachability_probe.py`,
  `tools/oxidizer_peak_position_price_probe.py`.

### Measured — the two readers that answer "did the model predict this axis?" are BINARY, and a token response clears both (2026-09-28)
- §43-§47 audited who chooses the perturbation, who chooses the evaluation
  points, what the reduction throws away, what family it represents, and whether
  it represents anything but a constant. The same question asked of the two
  readers that decide whether an axis was predicted **at all** has a blunter
  answer: neither takes the measurement as an argument.
  `inert_axis_scan` tests `predicted response < 0.5%`; `flat_prediction_census`
  tests `|shape_mape - flat_mape| < 0.05 pp`, a bar on the *score*, which the
  shape score's one free scale moves for any non-zero tilt.
- **Proved as arithmetic**, so no corpus change retires it (§45's class): fix a
  response at 1.2x the inert bar and grow only the measured span — both readers
  say "predicting" at 2x, 10x and 80x while the share of trend explained falls
  0.0086 -> 0.0026 -> **0.0014**.
- **Measured** (`tools/trend_share_census.py`, new; 48 blocks,
  `share = ln(predicted span)/ln(measured span)` in log space so the free scale
  cancels exactly): declined 13, span-too-small 1, predicting 31, and **3 in the
  token band** (share < 0.20) that cleared both bars. Every one had a reason that
  was already true and already written down, and none was machine-readable from
  the score — three *different* mechanisms, which matters more than the count:

  | block | axis | measured | applied | share | class |
  |---|---|---|---|---|---|
  | `jani2025_cu_h2o2_acidic_chelator` | `oxidizer_wt_pct` | **+0.167** | **-0.029** | 0.162 | `token-substituted` |
  | `bouvet2002_ti_silica_size_sweep` | `abrasive_d50_nm` | **-0.454** | **-0.050** | 0.118 | `token-shared` |
  | `us9200180b2_cu_benzenesulfonic_series` | `slurry_ph` | -24.97 | -3.91 | 0.103 | `token-declared` |

- **A new state between declined and predicted.** The Jani block sweeps H2O2 in
  the acidic + oxalate regime where the measured slope is POSITIVE; the pack's
  fitted chelator constant belongs to a species of the opposite sign, so
  `chemical_rate` correctly refuses to transfer it. The rate still moves, so
  `[DECLINES_AXIS]` would be false — but the response is not a test of this
  system. `core/declined_axes.py` gains `[SUBSTITUTED_AXIS: ...]` and
  `substituted_axes()` as a deliberately separate set.
- `Score.unmodelled_quantities` publishes each dataset's own `excluded_axes:`,
  which is what makes the third case legible: US9200180B2's real variable is
  benzenesulfonic acid (no term in this pack) while `slurry_ph` merely drifts
  8.5 -> 8.7 across the same rows and is therefore what `_varying_axes` counts.
- `token-shared` is recorded as **not a defect**: the silica size exponent is one
  number across k=3 sweeps on five films with its spread published (-0.45..+0.10)
  and titanium *is* the -0.45 member. Splitting it out would undo the
  re-attribution that removed five per-pack constants.
- After classification the **silent count is 0** — inert is acceptable, silently
  inert is not.
- **No constant added, no pack value changed, no exponent fitted; median
  unchanged at 18.9% / 19.5% held out**, which is the correct outcome for an
  instrument repair and is asserted rather than merely stated.
- Rejected: fitting a regime-specific oxidizer exponent on the three rows it
  would then be scored on; widening the silica spread or splitting titanium out;
  making `token-*` a gate (dropping blocks to move a median is forbidden);
  merging substitution into declined; lowering `TOKEN_SHARE` until the band
  emptied (the whole distribution is printed instead, §34).
- `docs/limits.md` §48 + `tests/test_trend_share_is_not_a_binary_bar.py`
  (18 tests, all re-measured at run time). Verified by reversion: removing the
  marker alone fails 5 of the 18.

### Measured — a pack's coherence verdict represents ONE CONSTANT OFFSET, so a scale that TRENDS along a condition is filed as "the blocks disagree, so Kp is not the cause" (2026-09-28)
- §46 asked what function family a reduction can represent, about the axis
  oracle. The same question about `tools/absolute_scale_audit.py` has a sharper
  answer: `median_log` and `spread` are functions of the **multiset** of
  `log10(measured/predicted)` values, so permuting which block holds which value
  leaves both bit-identical while every trend statistic moves freely. The
  reduction spans `scale = const + noise` and cannot express `A*x**b` at all.
  Arithmetic, so no corpus change retires it (§45's class).
- **Measured** (`tools/scale_coherence_trend_probe.py`, new; 38 comparable
  blocks, 4 packs with >= 4 blocks, every slope priced against a 2000-shuffle
  permutation null because a large |r| on 4-8 points is cheap): `cu_h2o2_bta`'s
  absolute scale trends with pressure, **slope -0.94, p_perm 0.009** (3.24x at
  1.0 psi to 0.057x at 6.96 psi). The 59.3x spread the audit reports is that
  trend with the ordering thrown away. The other three packs do not clear their
  own nulls (0.085 / 0.223 / 0.301).
- **Two controls refute it as physics**, both re-measured by the enforcing test
  rather than quoted: within-block pressure slopes straddle zero
  (`pressure_saturation_probe`, median -0.046, 6 of 10 negative), and the
  cross-block **measured**-rate exponent is **-0.55** where Preston requires
  **+1** — harder-pressed publications simply polished slower systems, so a
  correction fitted to the slope would encode publication selection.
- **Nothing wired, no constant added; median 18.9% / 19.5% held out UNCHANGED**,
  the correct outcome for an instrument repair. What changed is the sentence:
  `INCOHERENT` now means "no single constant fits these blocks", asserted in the
  audit's own docstring and report text with a pointer to `docs/limits.md` §47.
- Enforced by `tests/test_scale_coherence_cannot_see_a_trend.py` (9 tests); the
  blindness is proved on synthetic scales, so it cannot expire with the corpus.

### Measured — the axis oracle spans the MONOTONE POWER LAWS only, so "the most any law could buy" was measured with a statistic that cannot bend (2026-09-28)
- §45 asked what a reduction *throws away*; this asks what family it can
  **represent**. `tools/axis_error_census.py` prices an axis by granting one
  free exponent, `predicted*(x/x_ref)**b`, and calls the drop "the MOST any
  closed-form law on that axis could buy". Three published conclusions rest on
  that sentence: §14 ("the improvable error is DISTRIBUTED"), §16 ("≤ 10 % is
  outside reach"), and the `OWNERSHIP_MIN_GAIN = 2 pp` bar behind the
  pre-registered READING 1 / READING 2 verdict.
- **The blindness is arithmetic.** `(x/x_ref)**b` is a straight line in log–log.
  With a purely quadratic log-residual and levels spaced symmetrically in
  `log x` — a geometric ladder, the layout experimenters habitually choose — the
  odd moments vanish and the fitted slope is **exactly 0**, while one curvature
  constant explains the residual completely. The better the sweep's spacing, the
  more exactly it holds. The model being priced is not monotone: Gaussian pH,
  Langmuir oxidiser, IEP-referenced zeta all bend.
- **Measured** (`tools/oracle_curvature_blindness_probe.py`, new, 34
  (dataset, axis) pairs at ≥ 4 levels, each priced linear vs quadratic with a
  200-trial permutation null controlling the extra degree of freedom): curvature
  beats its own null on **12 of 34**, and **4 pairs cross the ownership bar only
  with a bend** — `entegris2022` loading −0.00 → **+10.16 pp** and `dandu2009`
  pH −0.26 → **+9.41 pp**, both with a *negative* linear price.
- **Only one axis survives as a LAW**: a single shared curvature on
  `abrasive_wt_pct` (`b2` = −0.15, sign-consistent on 6 of 8 ladders, mean shape
  25.2 % → 20.9 %). Every other axis's curvatures disagree in sign, so the best
  shared value collapses to ~0 — those axes are closed to a curved law too, now
  by measurement rather than assumption.
- ⚠ **No verdict changes and the median is unchanged at 18.9 % / 19.5 % held
  out** (the correct outcome for an instrument repair touching no constant). The
  surviving axis is **not a new opening**: its saturating sign re-derives §28
  through an independent reduction, and §28's amendment already priced and
  refused the zero-constant form while §14's second amendment withdrew
  `abrasive_conc_half_wt_pct` on necessity. §14/§16 stand — on that evidence
  rather than on the oracle argument.
- Rejected: swapping the quadratic into `axis_error_census` (§14/§16's quoted
  numbers become unattributable), pricing curvature without the permutation null
  (`netzband2020`'s null alone is +13.05 pp), `MIN_LEVELS_CURVE` = 3
  (interpolation), choosing the shared-bound axis by prettiest answer (the test
  picks it by member count), and restoring a fitted saturation constant on the
  strength of the 4.2 pp.
- `docs/limits.md` §46 + `tests/test_oracle_cannot_see_a_law_that_bends.py`
  (8 tests, every number re-measured at run time). Calibrated against the bug:
  forcing `b2 = 0` in `_oracle_curved` fails 4 of the 8.

### Measured — an axis's response was read from its ENDPOINTS, and a peaked term cancels exactly on an endpoint pair (2026-09-28)
- §43 fixed the probe whose perturbation it chose. It could not reach the two
  readers most of this repository's closure arguments rest on:
  `tools/inert_axis_scan.py` and `tools/residual_census.py` decided whether a
  swept input reaches the rate by running the dataset's first row **twice** —
  at the axis minimum and maximum the paper ran. That map is consumed by
  `Census.responsive_axes`, the `silent`/`declared` classification behind the
  corpus-wide "0 silent inert axes" verdict, and `oxidizer_order_probe`'s
  confound admissibility test. **Here the two points are chosen by the
  publication, not by the probe**, so no perturbation constant reaches them.
- **The cancellation is exact.** `models/chemical_rate.py:ph_response` is
  `floor + (1 − floor)·exp(−((pH − peak)/w)²)`, so at two levels mirrored about
  the optimum the exponential is identical **for every width** — §43(b)'s
  identity arriving through the experiment's design instead of the probe's
  displacement. Every peaked term inherits it (pH Gaussian, oxidiser Langmuir,
  IEP-referenced zeta), and the more levels a paper ran, the more of them a
  two-point reading discards.
- **Measured** (`tools/interior_level_response_probe.py`, new; 83 axes at ≥ 3
  levels): `endpoint-blind` **0**, `understated` **4** (worst **x1.9**),
  `inert` 22, `agrees` 57. Eleven two-level axes counted and excluded — for
  them the two readings are the same measurement. The four understated axes are
  all pH or oxidiser sweeps straddling their pack's declared optimum:
  `us9422456b2` 51.75% → **98.20%** (11 levels), `li2021` 10.59% → 18.37%,
  `dandu2009` 83.41% → 97.12%, `du2004` 76.78% → 89.00%.
- **Zero verdicts change, and that is the finding.** All four were already far
  above the 0.5% inert bar, so no classification, `responsive_axes` list or
  bucket moves and **the median is unchanged at 18.9% / 19.5% held out** — the
  correct outcome for an instrument repair touching no constant, term or
  prediction. What is removed is the *possibility* of a verdict nobody could
  check: an `endpoint-blind` axis would have been published as inert at 0.00%,
  indistinguishable from a model that weighed the input and found it
  unimportant. The 0 measures this corpus's sweep designs, not the reader's
  safety.
- Rejected: warning on a straddle instead of reading the interior (the oxidiser
  and zeta terms are peaked without declaring a peak key, so the straddle is
  undetectable); sub-sampling endpoints plus a midpoint (the arbitrary choice
  that produced §43; the levels a paper ran are a bounded set already loaded);
  special-casing the pH axis by name (§43's reason — the defect is in the
  reading).
- `docs/limits.md` §44 and
  `tests/test_axis_response_is_not_read_from_endpoints.py` (7 tests, every
  number re-measured through the shipping solver; both duplicated readers
  asserted, since fixing one of two copies is how a closed limit reopens).
  Reverting either tool fails 2 of the 7. Suite: 1233 pass.

### Measured — the perturbation is part of the instrument: §42's own probe filed the repository's strongest pH constants under `silent` (2026-09-28)
- `tools/declared_key_response_census.py` (added last session to ask *does every
  key a pack DECLARES move anything?*) had one half of its instrument fixed:
  **where** it stands, displaced off every reference condition. The other half
  — **how hard it pushes** — was a single large one-sided factor (x3), and that
  manufactured silence twice on `oxide_silica`, by two different mechanisms.
- **(a) x3 pushes a key out of its own validity window, where the model
  correctly refuses.** `ph_peak` is 11.0 with a width of 3.1 measured over
  pH 10–12.5; x3 puts the optimum at pH 33, seven widths from the query, where
  the §34 clamp holds the term at the nearest measured edge, rests the rate on
  the mechanical floor and warns. Measured at pH 11.5: **x3 → 0.00%,
  x1.25 → 54.81%** — the response is non-monotonic in the perturbation, so an
  honest out-of-domain refusal was being graded as a forgotten wire.
- **(b) the displacement landed exactly on a symmetry point.** `ph_ref` is 10.5
  and `ph_peak` 11.0, and `PH_DISPLACEMENT` was 1.0 — exactly twice that
  distance — so the query sat at pH 11.5, mirror-symmetric to the reference
  about the optimum, where `exp(-(x/w)²)/exp(-(x_ref/w)²)` is **1 for every w**.
  Measured: 0.00% on the point, 6.62% one unit off it. This is the previous
  session's own cancellation class recurring *inside the tool built to find it*.
- Fixed: `PERTURBATION_FACTORS` sweeps both directions, small factors first, and
  a key is inert only if no admissible perturbation reaches it; the displacement
  breaks symmetry about every declared optimum while staying inside
  `ph_valid_range`; every reported response records the perturbation that
  produced it; and `INSTRUMENT_CONTROLS` requires the census to recover keys
  known to be read, flagging its whole output when it cannot — without that, the
  census can silently decay into "nothing moves anything", which reads as a
  clean bill of health for the repository and which nothing else here would
  contradict.
- `reads` **147 → 157**, `silent` **584 → 574** of 1275 pack keys.
  **Median unchanged at 18.9%** (440 points, 48/52) — the correct outcome: no
  constant, pack, model term or prediction changed, only the instrument that
  judges them.
- Rejected: relaxing `INERT_TOLERANCE` (the x3 response really is 0.00%;
  loosening the bar would hide genuine silence everywhere else), dropping x3
  (the only factor that reaches a weakly-coupled key), and special-casing the pH
  keys by name (the defect is in the perturbation design, and a name list leaves
  every future key with a validity window exposed to it).
- `docs/limits.md` §43; `tests/test_perturbation_is_part_of_the_instrument.py`
  (8 tests, every number re-measured at run time, including a negative control
  on the instrument check itself; reverting the fix fails 6 of the 8).

### Measured — the completion bar is NOT floored: input degeneracy is an exact lower bound, and every genuine instance of it sits below 15% (2026-09-28)
- Answers the owner's standing precondition for relaxing the 10% bar toward
  15%: *write down what creates the lower bound on the error first*. Two
  earlier candidates were already refuted (replicate scatter — no corpus-wide
  floor, 1.5–37%; "these blocks are hard" — not a bound). This measures a
  third and reports that it **does not justify a relaxation either**.
- **Mechanism.** The prediction is a deterministic function of the input
  vector. When a table sweeps a quantity the recipe schema has no field for,
  two rows arrive at the solver identically and leave identically while the
  measurements differ — irreducible for this schema, and unlike a noise floor
  it is computable **exactly**.
- `tools/input_degeneracy_floor_probe.py` (nothing fitted): rows are grouped
  by identical prediction and each group gets its **own** free constant —
  strictly more freedom than the scorer's one scale per dataset, so the number
  is a genuine bound. The optimum is a weighted median, found by enumeration.
- **Verdict, three ways.** The median dataset's floor is **0.0%** (over half
  the corpus has none), so the attainable median is 0.0%. On the held-out
  corpus **no genuine bound reaches the 15% bar at all** (worst 9.9%,
  `us9200180b2`). And since the bar is a counting statistic, the decisive
  question — is a *must-cross* dataset floored above it? — answers no for all
  six on the shortlist (0.0–7.4%). The three crossers §38 left outstanding are
  missing physics or missing data, not structural impossibility.
- **Two false bounds had to be removed, and that is the substance of the
  change.** Both are the model's own declared silence arguing that the model
  cannot do better, and together they inflated the worst bound 9.9% → 67.2%:
  (a) a **gated row** is not degenerate — `ihnfeldt2008` led the first draft at
  67.2% but is not scored at all (6 of 7 rows gated outside the pack's pH 6.25
  oxidizer window), so the probe now mirrors the scorer's gate exactly; (b) a
  **flat block** is a declared refusal (§36), reported by name but excluded —
  `lee2021` 36.4, `kenchappa2021` 29.8, `hong2007` 14.7, `bae2022` 11.8,
  `phm2016` 7.0%.
- **The useful half.** `tw202115224a`'s 7.4% prices, for the first time, the
  cost of a refusal the dataset header already made correctly: the patent
  polishes Nalco and Fuso silica at the same *nominal* 15/27/50 nm and the
  pairs differ up to **1.9x** (4414 vs 8453 A/min at 50 nm). A vendor is not a
  physical quantity, so a key for it would be a dataset fingerprint — and the
  block can still reach the bar without one.
- **Unchanged by design:** no pack, constant or prediction was touched;
  published median 18.9%, held-out 19.5%. Standing still is the correct
  outcome for a bound-hunting entry, and the tests assert it.
- Also blocked this session, recorded rather than worked around: §38's exit
  condition (a second source printing a PSD width) could not be opened —
  `patentimages` 403s, EPO's publication server carries bibliographic data
  only, FreePatentsOnline's full text has the example tables as images, and a
  full scan of all 411 PDFs in `~/fab-sim/papers/` still finds exactly one
  publication reporting a width alongside removal rate.
- New: `tools/input_degeneracy_floor_probe.py`, `tools/degeneracy_groups.py`,
  `tests/test_completion_bar_is_not_floored.py` (7), `docs/limits.md` §39.

### Rejected — the PSD-width term the second-cheapest crosser needs is unidentifiable: one source, and inside it the two films disagree in SIGN (2026-09-27)
- `tools/median_crossing_probe.py --held-out` puts
  `us20190127607a1_teos_ceriasilica_size_sweep` (18.9%) second on the list of
  datasets that must cross the 15% bar. Its cause is explicit and physical:
  the TEOS rate is **non-monotonic** in D50 (875 → 1828 → 1311 → 2223 A/min)
  and the dip is the one abrasive with a broad 4-peak distribution
  (`(D99−D50)/D50 = 0.939` vs 0.503–0.787). A single power law cannot produce
  a reversal at all; per-row errors are 17.4 / 28.4 / 28.1 / **1.9%**.
- Luo–Dornfeld gives the mechanism and its sign for free: only particles in
  the top `~delta` of the distribution are indented, so at fixed D50 a broader
  PSD loads a smaller **fraction** of the abrasive. The driver
  (`abrasive_d99_nm`) is already transcribed on every row of both files, and
  the term would be a dimensionless ratio — so it cannot be a relabelled size
  exponent.
- **Measured and rejected** (`tools/psd_width_identifiability_probe.py`,
  nothing fitted — the residual slope `d ln(meas/pred) / d ln((D99−D50)/D50)`
  is immune to the scorer's one free scale because a scale cancels out of a
  slope): 8 rows, 2 datasets, **1 independent publication**, and within that
  single experiment the residual width slopes are **+0.024 (HDP)** against
  **−0.688 (TEOS)**. A mechanical particle-count term cannot know how the
  oxide underneath was deposited, so no shared width constant is even the
  right **direction** (§14). The two files are the same four polishing runs on
  two films, so the holdout unit is one (§33).
- Three weaker variants rejected with it: fitting on TEOS alone (forbidden
  dataset selection, and self-grading besides), a film-specific width exponent
  (two constants on four points each, attached to an axis the mechanism says
  cannot depend on the film), and routing D99 into the rate through the defect
  proxy's existing `tail_term` (same one-source problem through an existing key).
- **The corpus median is unchanged at 18.9% and that is the correct outcome** —
  no pack, constant or prediction was touched. The refusal leaves the project
  further from its own bar, which is exactly why it is written down.
- New: `docs/limits.md` §38, `tools/psd_width_identifiability_probe.py`,
  `tests/test_psd_width_axis_is_unidentifiable.py` (6 tests, all re-measured
  at test time). The exit condition is a **transcription** question rather
  than a new-physics one: several corpus size sweeps report a D50 and nothing
  else, so a second source may already exist in the literature already cited.
  `test_the_axis_still_rests_on_a_single_publication` fails the day one
  arrives; a mutation guard fails if the rate ever responds to width, and the
  "it goes somewhere else" claim is pinned by asserting D99 actually MOVES
  `defect_risk` (§18).

### Changed — §29's exit condition fired: a verified dilute ladder overturned the refutation, and the term is still refused (2026-09-27)
- Added `us9422456b2_teos_silica_dilute_loading` — US 9,422,456 B2 Example 1 /
  Table 1, a **printed** patent table: 54 nm aminosilane core-shell colloidal
  silica at 0.5 / 1.0 / 2.0 / 3.0 wt%, each at 4.0 and 5.0 psi, pH buffered at
  4.7, one tool / pad / speed / flow. Verified value-by-value against the
  cached patent text. The fumed-silica "Control" row is **excluded**: a
  different abrasive morphology inside a loading ladder would attribute a
  morphology change to concentration.
- **§29's refutation of the load-sharing onset did not survive it, and the
  cause was the cut, not the physics.** §29 split at `theta = 1`; the new
  ladder's most dilute pair sits at `theta = 1.38` (`chi = 0.75` — a quarter of
  the load still on bare pad), so the first datum ever to land near that
  threshold was sorted into the "dense" bucket and averaged with pairs at
  `theta = 18`. Re-measured on a **chi** band with the original diamond source
  dropped entirely (`tools/dilute_ladder_reopens_sec29_probe.py`, 44 pairs):
  `chi < 0.9` gives n=14, median slope **+0.826** against `chi >= 0.9` n=30,
  **+0.220**, from **5** independent sources (was 1). The separation survives
  sweeping the cut from 0.80 to 0.99.
- **The term is still NOT wired — on new grounds.** It fails where it acts
  most: on the diamond series at 0.01–0.04 wt% (`chi ≈ 0.03`) it takes the
  dataset from **8.7% → 34.2%**. New exit condition: an iso-condition loading
  ladder below ~0.5 wt% from a non-diamond abrasive.
- **The median must not be quoted as the verdict here.** The same
  counterfactual read 18.17% → 18.95% in §29 and reads 18.17% → **14.82%** now,
  i.e. across the completion bar, with no physical claim changed — nine
  measured points cannot decide a law. The enforcing test was rewritten to pin
  the median's *instability* rather than its direction.
- Two further exit conditions fired and were answered by **re-measurement, not
  by editing the claim to match**: the vetoed-branch scope note in
  `models/luo_dornfeld.py` widened from 4 ladders / 1 dataset to **6 ladders /
  2 datasets** (slopes +0.145 … +0.831, all positive, median +0.350 → +0.430 —
  the evidence strengthened), and `DERIVED_CONC_EXPONENT_WHY`'s "dissenters are
  all SiC" claim was **corrected**: the new oxide ladder dissents at m = +0.83,
  i.e. *steeper* than the derived +1/3, which is the load-sharing-onset
  direction rather than the supply-limited one. The enforcing test now asserts
  the dissenter's **sign** instead of its film, because that is what separates
  the two mechanisms.
- Corpus 46 → 47 scored datasets, 427 → 435 points. **Headline median unchanged
  at 18.2%.** Two invariance guards that asserted `statistics.median` in a
  16.2–16.8 band were re-expressed on the headline (upper) median: n going
  46 → 47 flips the symmetric median's parity and moved it to 18.2 with nothing
  fitted, so a guard against fitting was firing on arithmetic.
- `docs/limits.md` §30 (§29 kept in full, marked superseded in part — the
  reasoning was sound and the way it failed is the lesson).
  `tests/test_load_sharing_onset_is_refuted_by_the_data.py` 8 → 11 tests.

### Fixed — the SUPPLY axis was never decided, and the obvious fix would have been a silent bug (2026-09-27)
- Luo-Dornfeld's third regime question (`p`, `q`: monolayer or multilayer
  particle supply) is answered from `gap_m / d_p`, and the solver hands it
  `pad_wafer_gap_m` — a key **no pack declares and no caller sets**. So the
  decision was never made in any run of this corpus: the inherited layer
  returned the monolayer pair, graded itself `estimated`, and every result
  warned that the supply geometry "was not determined from data". That warning
  was false in every run ever scored here.
- **The one-line fix was rejected on measurement.** The same run already solves
  a mean fluid film `h`, but that is averaged over grooves and un-contacted
  valleys, whereas `decide_supply` means the clearance where a particle is
  *loaded*. `tools/supply_gap_probe.py`: `h/d` exceeds the 1.5 threshold on
  **20 of 49 datasets** (up to 26x), so feeding it to `gap_m` would have cut
  `p` from 1.0 to 0.46 and halved the derived concentration exponent on a third
  of the corpus. `tools/supply_gap_reachability_probe.py` shows only **5 of 49**
  predicted rates move when the branch is forced, so the error would have been
  nearly undetectable afterwards.
- **Adopted instead**: `_supply_from_lubrication` decides the axis from the
  lubrication regime — `lambda < 1` means asperities carry the load, so a
  loaded particle sits in a contact whose clearance is its own diameter. All 49
  runnable datasets are boundary (`lambda` 0.002–0.148). **Zero new constants
  and zero exponent change**; the median stays 18.2%, which a test asserts.
  `lambda >= 1` deliberately gets no verdict: a closure that fires everywhere
  is not a closure.
- `docs/limits.md` §24, `tests/test_supply_axis_decided_from_lubrication.py`
  (7 tests). Reused legacy `sim/abrasive_mechanics.decide_supply`,
  `P_MONOLAYER`, `Q_MONOLAYER`.

### Changed — completion redefined at the measured ceiling, which exposed a 3.2-point gap (2026-09-27)
- The owner redefined done as "the minimum you actually found", after the search
  for a 10% median was closed by measurement rather than by effort. Completion is
  now **median shape error ≤ 15%**, pinned in `tests/test_definition_of_done.py`
  as `COMPLETION_MEDIAN_PCT`.
- The bar rests on one measured bound: an oracle that grants every dataset a free
  exponent on its own best axis — impossible for a real model, which shares its
  constants — still reaches only **11.9%**, lifting datasets at or below 10% from
  15 to 20 of 46. So ≤10% is above the ceiling of the whole "add another law"
  programme, and 15% is the only band a shared-constant model can occupy.
- **The bar is not a noise-floor claim.** Published reproducibility in this corpus
  spans 1.5%–37%, so 15% is lenient against jani2025 and strict against
  miranda2004. A test now enforces that the two arguments stay apart, and another
  re-derives the oracle bound so the justification cannot silently rot.
- **Setting the bar made the project fail its own check.** The corpus sits at
  18.2%, so `test_the_completion_bar_is_met` is red. It is deliberately not
  xfail: marking it would convert a measured shortfall into a green tick. That
  test turning green is the completion signal.
- Rejected levers, all closed by measurement, recorded so they are not retried:
  a pairwise interaction term (all 9 recurring axis pairs flip sign across
  datasets), flipping the concentration exponent's sign (Dandu 2009 measured both
  signs in one paper — the Luo–Dornfeld size crossover), and gating out-of-range
  pH rows (0.5 points gained, 12 datasets lost including four of the best).

### Fixed — a signal tower was floating above the platens, invisible to 1070 green tests (2026-09-27, 22nd run)
- The polisher-side signal tower was placed at `0.74 * BAY_R` = 1.44 while the
  roof it stands on is an **annulus** whose inner edge is `R_DECK + PLATEN_R +
  0.10` = 1.74. It therefore hung over the roof's open centre, 0.36 m above the
  polishing pad, with nothing beneath it. The radius is now derived from the
  annulus mid-line, so it survives a change to either bound — the bug was
  created by exactly such a change (the roof became a ring; the tower kept its
  old radius).
- **This error class is transparent to every other check in the suite.** A
  floating part is lit, coloured, clickable and inside the framing bounds, so
  the scene, click, framing and both luminance tests all passed on it. It was
  found by a human looking at a screenshot, which is not a repeatable process.
- `tool3d.js`: `FIXTURES` / `standsOn()` / `fixtureGaps()`, exposed as
  `window.__gaps()`. Each free-standing fixture registers its foot; a ray is
  cast straight down, ignoring the fixture's own meshes, to the first surface
  below. Measured on the **rendered scene graph**, not on the coordinate
  arithmetic, so re-modelling cannot quietly invalidate it.
- `tests/test_tool_ui_3d.py::test_every_free_standing_fixture_stands_on_something`
  (30 → 31 UI tests). Calibrated against the bug: restoring the old radius
  fails with *"signal tower at (1.44, 0.44, -0.00) floats 0.36 above pad"*.
- A no-hit is reported as `null`, never `Infinity` — `Infinity` does not
  survive the automation bridge's structured clone, which would turn "nothing
  beneath it at all" into a silently passing value.
- `tools/prod_freshness.py` (new): compares the SHA-256 of each browser-served
  asset with the file on disk. A green e2e against production proves the
  deployed build *works*; it does not prove it is the build just committed, and
  every prior "the UI is fixed" report was made without checking. Both assets
  verified SAME.
- Shell-only: median unmoved at 18.9% / 21.3% LOO, no physics touched.

### Measured — the absolute-scale failures were already identified, in prose the scorer cannot read (2026-09-27, 21st run)
- `tools/kp_provenance_table.py` (new): for each block missing the absolute
  rate by ≥3×, what its pack silently conflates — the follow-up §22 named.
- **9 of the 11 failures state their own cause in their own dataset header**
  (placeholder pack, condition outside the Kp anchoring window, or a named
  systematic bias); a 10th is disclosed in its pack's `kp_m_per_pa` note. Only
  `us6918821b2` is genuinely unexplained — the patent states no slurry
  composition, so there is nothing to compare against the anchor.
- **The "out of scope" claim is tested, not asserted.** (1) The prose does not
  predict the miss: 9 of the 17 prose-carrying blocks land *inside* 3×, while 3
  of the 20 blocks without it fail (median miss 2.09× vs 2.00×). (2) The prose
  predates the measurement — committed 2026-09-15…24 against an audit dated
  2026-09-27.
- **One quantitative identification, and it could have failed.** `sti_ceria`
  excluded the ceria-coated-silica composites from its Kp average and recorded
  the value they imply (2.3e-14 vs 1.09e-13). That exclusion predicts a 0.211×
  scale with no free parameter; the two blocks measure **0.188× and 0.235×**,
  bracketing it.
- **Rejected: every pack split.** In each case the only available anchor is the
  block the new pack would then be scored on — the 13th-run rule applied to
  absolute scale. Zero packs split, zero constants changed, median shape
  **18.9 %** / LOO 21.3 % unmoved.
- `tests/test_kp_provenance_is_identified.py` (18) makes adjudication a standing
  obligation: a new ≥3× block fails the suite until its cause is named or
  explicitly recorded as unidentified. `docs/limits.md` §23.

### Measured — reproducibility, transcribed: 15 % is NOT the measurement floor (2026-09-27, 15th run)
- `cmp_sim/data/validation/reproducibility.yaml` (new): what each publication
  states about **its own** run-to-run scatter, verbatim, for 17 datasets.
  Searched in **corpus order** (alphabetical, independent of score) so the result
  cannot be steered; every statement found is recorded whether it helps or hurts.
- `tools/repro_statement_scan.py` scans the held full texts for reproducibility
  phrasing; `tools/stated_reproducibility.py` converts statements into a floor
  comparable to our MAPE — and refuses to convert the ones that cannot honestly
  be converted.
- **The answer is negative.** Only 4 of 17 sources state something quantifiable,
  and they disagree by an order of magnitude: jani2025 **1.5–9.5 %** RSD,
  ihnfeldt2008 **19.1 %** (±14 nm/min averaged per row), miranda2004
  **36.9–37.6 %** (derived from its printed ANOVA). A corpus-wide "15 % is the
  noise floor" is therefore unsupported in **both** directions. The case for
  ≤ 15 % remains §14 + §16 (axis-exponent sign dispersion; the 11.9 % oracle) and
  is *not* a noise-floor argument.
- **Three ways a floor can fail to exist, kept apart**: `spatial_only` (an SD
  across points on one wafer is WIWNU, not reproducibility — it must not excuse
  kenchappa2021's 42.8 %), `replicated_scatter_withheld` (exists, non-zero,
  unrecoverable), `none_stated`. mariscal2020's 4.6 %/11.9 % are its **own
  model's** RMS fit errors and are recorded as `none_stated` so that trap is
  documented rather than available.
- The one derived floor round-trips: the test inverts the algebra and reproduces
  miranda2004's printed adjusted R² = 0.69 to 3 dp.
- `docs/limits.md` §17; `tests/test_stated_reproducibility.py` (10 tests) pins
  that every transcribed number appears in its own quote and that the pass cannot
  move a median. Medians unmoved at **18.9 % / 21.3 %**, as required.

### Measured — the velocity exponent is not a number, it is an interaction (2026-09-26, 9th run)
- `tools/velocity_pressure_interaction_probe.py`: measures b_V at **fixed
  pressure** as the raw log-log slope of *measured* rate against speed — no model
  in the loop and no fitted scale, so the probe cannot inherit an artefact from
  the simulator it audits. Sorooshian 2005 thermal oxide gives
  **+0.370 / +0.687 / +0.764** at 2 / 4 / 6 psi (29 ladders, monotone up,
  endpoints ~4 median standard errors apart); `mariscal2020_peteos_ceria` gives
  **+1.105 / +0.857 / +0.625** at 2 / 3 / 4 psi (monotone **down**);
  `us6918821b2_cu_ic1000` gives **−0.416 → +0.863** across 1.5 → 4 psi, a **sign
  change** that independently reproduces Borucki & Philipossian 2023
  (doi:10.1149/2162-8777/accaa6).
- **Two conclusions, both negative and both stronger than a number.** b_V is not
  a constant, so no global exponent — derived or fitted — can be right and three
  runs of searching for one were aimed at the wrong object. And the
  interaction's *direction* is not universal either, so this is not one master
  curve b_V(P) waiting to be parameterised: any `V**f(P)` with a single f is
  excluded by the oxide and PETEOS bodies together. The "find the velocity
  exponent" line is therefore **closed**, as the pH axis is, and the open
  question is restated as *what couples P and V such that the coupling can
  invert between consumable sets?*
- `tests/test_velocity_exponent_is_not_constant.py` (8 tests) pins the verdict
  and forbids any pack from declaring a velocity exponent **or** a P–V coupling
  constant. Nothing was adopted; the corpus median stays **18.9% / 21.3%**, as
  it must when a run produces a negative shape result.
- Two honesty notes, both pinned by tests rather than buried: the pre-registered
  2x spread bar does **not** fire on Sorooshian (0.99x — it compares the spread
  of medians against the spread of single ladders and is structurally
  insensitive when a pressure holds ~10 ladders), so the monotone trend is
  labelled **post-hoc** and asserted only in its weaker standard-error form; and
  the probe's first cut reported a spurious **22x** interaction by pooling one
  ladder per pressure from *unrelated* datasets, so scoring is now strictly per
  dataset, every ladder-producing dataset carries an explicit admit/exclude
  reason, and a test fails when an unreviewed one appears.
  `sic2023_shear_rheological_L9` is excluded on **design** (its abrasive size and
  loading change per row and are recorded only in the row label, which is why one
  of its "ladders" read b_V = +6.76), not on its answer.

### Added — the simulator's shell is separated from its physics (2026-09-26)
- `cmp_sim/data/consumables.yaml`: named polishing pads and conditioner disks,
  one sourced property at a time (value / unit / source / confidence, `null`
  where the literature held here publishes nothing). `cmp_sim/pad/catalog.py`
  resolves a product name to properties and is applied once in `solver.resolve`,
  so every physics layer sees the same pad.
- `GET /api/model?film=`: every physics constant the engine will use for a film,
  with its source and confidence — the UI reads the model instead of restating
  it. A model-inspector panel in the tool view shows them, allows one to be
  edited, and re-predicts through the ordinary `recipe.params` override path
  (reported as owner-supplied, so an edit can never pass for a sourced value).
- The four input stations the brief names now all work and all reach the model:
  wafer cart (film stack), operation screen (pressure / platen & head rpm / flow
  / time / slurry and platen temperature / retaining-ring / zone pressures),
  slurry supply (abrasive kind, D50, D99, wt%, pH, additives), polishing unit
  (pad and conditioner disk **by product name**, with sources shown).
- `tools/web_smoke.py`: starts the server and exercises every route the tool view
  uses, including a full-chemistry prediction with a named pad and disk.

### Fixed
- `tool.html` hard-coded `groove_pitch_mm: 2.0` and `groove_width_mm: 0.5`. Both
  disagreed with what the project can source — 3.05 mm pitch (120 mil, base
  pack) and 0.6 mm width (Mu et al. 2016, doi:10.1016/j.mee.2016.02.035) — and
  nothing failed, because nothing compared the two. The 3D view was drawing a
  pad nobody measured while the engine computed with another.
- Selecting the pad a parameter pack was **calibrated on** multiplied the
  predicted rate by 1.9x. `kappa_contact` is a ratio against the pack's
  reference pad, and the catalogue's published Shore D 60 for IC1000 routed
  through the Qi correlation gives `E* = 2.5e8 Pa`, while
  `oxide_silica_calibrated_pad`'s reference is the `1.0e9 Pa` of Jeong et al.
  2024 (doi:10.3390/ma17081817) measured on that same physical pad. Two
  descriptions of one pad were being multiplied as though they were a physical
  difference. A pack may now declare `reference_pad_name`; naming that pad with
  no override pins kappa to exactly 1.0 — the same rule the whole factor system
  rests on, that every factor is 1.0 at its pack's reference condition.
- `Pad.name` defaults to `"IC1000"`, and the catalogue acted on that default,
  filling IC1000's properties into every recipe that never chose a pad. That
  made the pad differ from the pack reference and silently removed
  `kappa_contact` from three existing tests. `Pad.name_was_chosen` now defaults
  to `False`, so an unset flag means inert; both the config path and a bare
  `Pad()` built in code are pinned by tests.

### Testing
- `tests/test_web_holds_no_physics_constants.py` (11 tests) greps every
  browser-loaded file for an assignment of a literal to any key a parameter pack
  declares, or to any pad/disk property the catalogue owns. The forbidden
  vocabulary is derived from the packs **at test time**, so adding a constant to
  a pack immediately makes hard-coding it in the UI a failure with no test edit.
  Operating-condition names are excluded by intersecting with the recipe
  dataclasses' own fields: a form defaulting to 3 psi is not a physics claim.
- 8 browser-driven tests pin the four stations, including one that doubles the
  Preston coefficient in the model inspector and asserts the prediction doubles,
  and one that asserts two different conditioner disks predict the **same** rate
  — so the day grit design is wired with a sourced constant, it fails loudly.
- Corpus median is unmoved at 18.9% shape / 21.3% LOO, as required: no pack
  physics changed in this work. Had it moved, that would have been the bug.

### Physics
- **P1 Preston** baseline, `Kp` decomposed by slurry / pad / film.
- **P2 Greenwood-Williamson** asperity contact; the correction is applied only
  when the pack's reference pad has a real source, because normalising against
  an *estimated* reference inflated every rate two- to threefold.
- **P3 Luo-Dornfeld** abrasive mechanics with site-occupancy saturation.
- **P4 Chemistry** through a softened-hardness channel, Arrhenius temperature.
- **P5 Radial uniformity**: relative velocity field, zone pressures, and slurry
  supply on Mu's 2016 reactor model (an earlier invented supply number was
  discarded).
- **P6 Pattern**: density-smoothed step-height evolution, dishing, erosion.
- **P7 Pad life**: glazing and conditioner ageing, *reported* rather than
  multiplied into `Kp` — the inherited MRR proxy peaks at ~7 min against a
  measured ~3 min, so applying it would claim unearned precision.
- **P8 Defect proxy**: large-particle tail against the published ~680 nm
  scratch threshold, with scratch width and depth per film.

### Model selection
- Models are chosen by **situation, not by film**. `core/regime.py` classifies a
  run on eight axes; `core/profiles.py` offers 11 profiles bundling seven
  orthogonal layers. `auto` picks; an explicit choice is respected and
  mismatches are warned about. Pad wear and pattern are overlays, not rivals.
- Material family decides the film class before hardness does: W (~4-7 GPa) and
  thermal oxide (~7-9 GPa) overlap in hardness but polish by different
  mechanisms.

### Validation
- **The `si` film is scored against a measurement for the first time.**
  `bae2022_si_wafer_alkali_ph` (doi:10.3390/nano12213893) is an independent
  bare-Si polish at 5.7 psi — 9× the down force of the pack's Kp source — and
  its rates confirm the 100–3,000 Å/min envelope independently of the source
  that set it. Absolute comparison is disabled (the paper never states the
  carrier-platen centre distance, so no relative velocity can be recovered) and
  the pH term is left **unfitted**: two pH levels cannot determine a peak and a
  width. See `docs/limits.md` §12. The dataset does not beat predict-the-mean,
  which is reported rather than repaired.
- **Four published datasets within ±15%**, all three patent sources re-verified
  against the official USPTO PDFs rather than trusted from a report.
- Two datasets are kept **failing on purpose**, each with a test that fails if
  the documented limit ever goes stale:
  - *US6918821B2 Cu* — the lubrication limit. The regime detector flags the
    exact condition where the measured rate collapses (λ = 1.24) without ever
    seeing a rate.
  - *SiC DOE50* — chemically rate-limited. At identical P·V the rate spans
    5.2×, and P·V explains only R² = 0.09 of the variance.

### Data
- 55 additives × 9 films; 11 abrasives × 9 films; packs for Cu, W, oxide,
  STI-ceria, SiC, Si substrate, SnAg.
- Unknown values are `null` with a `TODO(owner)` note, never invented. The SnAg
  pack carries 68 sourced numbers and **no Preston coefficient**, because none
  is published; the example refuses to run and says so.

### Interfaces
- CLI: `run`, `sweep`, `validate`, `packs`, `profiles`.
- Zero-dependency web UI and HTTP API (`/api/simulate`, `/api/sweep`).
- `CMP-Sim.command` launcher; verified from a clean clone.
- Sweeps mark any point where the regime changes instead of drawing one
  confident trend through physics that changed underneath it.

### Corrections found while verifying
- **SiC `Kp` inherited the oxide value** — 128× too high. Re-derived from the
  50-run DOE.
- **W `Kp` was an estimate** 4× above two independent patent tables.
- **Up-area rate reported 0.0 Å/min for every run** — the m/s → Å/min factor
  was 10 instead of 1e10 × 60, while the same object's notes quoted the right
  figure.
- **The "softening" assumption was refuted by its own data.** H₂O₂ grows
  Cu₂O/CuO, *harder* than copper (3.24 GPa on a 1.2 GPa film; bulk cuprite
  17.0–17.5 GPa). The same study spans 0.05–20 GPa on one metal by chemistry
  and pH alone, so the modified surface is not assumed softer anywhere.
- **The library saw 2 passing datasets while the CLI saw 4** — dataset
  discovery searched only the inherited directory.
- **A stationary platen reported 815 Å/min**; Preston is proportional to
  velocity, so it now reports 0.0.
- **Bad input surfaced as an untranslated Korean bracket error.** Impossible
  recipes are now rejected by field and value; a load beyond the contact model
  explains that every summit is already engaged.

## [P4] §51 — a mechanism-based refusal's third instance, and an exit condition that had already fired

- `docs/limits.md` §51: the oxidiser gate `cu_h2o2_bta.oxidizer_ph_window`
  justified itself with a MECHANISM ("alkaline H2O2 grows a hard CuO film the
  abrasive cannot cut"), which transfers and is therefore falsifiable outside
  the single 2x2 that produced it. Measured against the two alkaline Cu/BTA
  H2O2 ladders already in this corpus: log-log slopes -0.01 (pH 11.1 fixed,
  4 levels, 1.04x span) and -0.27 (confounded, pH falls as H2O2 rises) against
  the mechanism's own -2.33. The SIGN transfers; the MAGNITUDE does not.
- The same note's exit condition read "no sweep has been located". Both
  ladders were already scored members of this corpus when that was written,
  under another pack. A refusal that asserts the absence of data must be
  RE-RUN, never re-read.
- The gate's VALUE, unit, source and confidence are unchanged: its decision
  rests on the two pH legs having opposite signs, not on the magnitude. The
  note is corrected and the superseded sentences are kept, marked refuted in
  place. Neither ladder can anchor the pack (foreign pack; one is
  `used_for_calibration` and flat; the other's pH is confounded).
- New: `tools/alkaline_oxidizer_sign_transfer_probe.py`,
  `research/alkaline_oxidizer_sign_transfer.yaml`,
  `tests/test_alkaline_oxidizer_mechanism_does_not_transfer.py` (8 tests,
  including an expiry test that fires when an admissible alkaline anchor
  appears, and a mutation-guard note about YAML folded blocks).
- **Zero constants, zero pack values, zero predictions changed; median
  unchanged at 18.9% published / 19.5% held out — the correct outcome for an
  honesty fix, and asserted rather than hoped for.**
- Stage-2 simulator re-verified end to end with the real browser harness
  (`tools/tool3d_e2e.py --serve`): all four input stations (wafer cart,
  operation, slurry supply, polishing unit) open their intended drawer and
  drive the model (3 psi 1559.6 -> 6 psi 3119.1 A/min; WIWNU 0.0% at matched
  rpm, 23.7% at 120/30).

## [P4] §52 — the next "no such data exists" claim is false too, and the decision survives for a stronger reason

- Applied §51's rule once more, to §49's sentence: "both packs' corpora sweep
  the oxidizer at one level or not at all". RE-RUN instead of re-read, the
  corpus holds FOUR >=3-level oxidiser ladders under
  `cu_alkaline_benzenesulfonic` and `w_fe_oxidizer` -- one five levels and
  held out. The sentence is false.
- The DECISION stands, for a better reason: `oxidizer_peak_shape_K` is a peak
  SHAPE constant and all four ladders are MONOTONE (and the two packs' run in
  opposite directions). A ladder that does not bracket an interior maximum
  cannot anchor a peak at any level count. "We have no data" becomes "the
  data we have refuse to place a peak".
- The real lesson is the trap in the re-audit itself: "3+ levels" was a PROXY
  for "enough to fit a peak", and the proxy is what went stale. Stopping at
  the proxy would have reported the axis reopened and fitted a peak to
  monotone data.
- §49's stale sentence is struck through and marked in place, not deleted.
- New: `tools/absent_data_claim_reaudit_probe.py`,
  `research/absent_data_claim_reaudit.yaml`,
  `tests/test_absent_data_claim_expires_but_decision_stands.py` (8 tests,
  3 mutations verified to bite, including a detector control and an expiry
  test that fires when a bracketing ladder appears).
- **Zero constants, zero pack values, zero predictions changed; median
  unchanged at 18.9% / 19.5% held out.**
