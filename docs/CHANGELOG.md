# Changelog

All notable changes to CMP-Sim. Newest first.

## Unreleased

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
