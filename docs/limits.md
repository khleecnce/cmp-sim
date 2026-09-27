# What this model cannot do

`docs/open-questions.md` lists things that are **undecided** and waiting on the
owner. This page lists the opposite: questions that have been **settled**, where
the answer is that the model declines to predict something, and the decision is
final until a specific named experiment arrives.

Each entry gives the measurement that establishes the limit, the refit that was
rejected and what it would have cost, and the experiment that would resolve it.
None of these is a TODO. A future session that "fixes" one without the named
measurement is reintroducing an error that was removed deliberately.

Every limit here is enforced by a test, so it cannot be quietly undone.

---

## 1. The velocity exponent is not fitted, because the corpus cannot resolve it

**The measurement.** Fitting `RR ∝ V^n` independently on each velocity-isolated
group gives exponents scattered from **−0.42 to 1.10**, straddling the Preston
value of 1.0. The negative case is not noise: it is the documented low-pressure
regime of US 6,918,821 B2, where the measured rate collapses as speed rises.
Checking whether the exponent varies systematically with pressure gives
**opposite trends in the two datasets that allow the test**.

**The refit rejected.** Any single global exponent. With the in-scope values
spanning both sides of 1.0, a fitted mean would be a number with no support in
either regime.

**What would resolve it.** A velocity sweep repeated at three or more down forces
on one tool and one consumable set, so that the pressure dependence of the
exponent is measured rather than inferred across labs.

**Enforced by** `tests/test_velocity_exponent_unresolvable.py`.

---

## 2. The lubrication gate would be *wrong*, not merely uncalibrated

**The measurement.** The obvious explanation for the velocity inversion is a
transition into hydrodynamic lubrication, and `core/regime.py` already computes
λ. The inverting rows really are the highest-λ rows (0.187 against 0.070), and λ
correlates with over-prediction (ρ = −0.71 and −0.52 on the two datasets).

But λ turns out to be **exactly proportional to V/p** — it *is* the
pseudo-Sommerfeld number, carrying no information beyond the two variables
already in Preston's law. And the λ intervals of the inverting and
non-inverting rows **overlap**, so no threshold separates them.

**The refit rejected.** Rescaling λ so that the inverting rows cross a boundary.
This was the plan of an earlier commit in this project, which the next commit
corrected: because the intervals overlap, *no* calibration can work. The gate
would fire on rows that do not invert.

**What would resolve it.** A direct film-thickness measurement (e.g. dual-emission
UV fluorescence) on the conditions that invert, giving λ independently of V/p.

**Enforced by** `tests/test_lubrication_gate_is_wrong_not_premature.py`.

---

## 3. Pad contact does not separate the inversion either

**The measurement.** With fluid film excluded, pad contact is the next candidate.
`summit_saturation` appears to separate the cases cleanly — 0.0111 on the
inverting rows against 0.0296 — but it equals **0.00739 × P** exactly: it is
pressure relabelled, with the same pad in both datasets, and carries no
independent information. `plasticity_index` and `pad_limited_plasticity_lambda`
differ *between* datasets (0.0219 against 0.0029) but are **constant within**
each one, so they are fixed by the consumable set and cannot vary with the recipe
rows that invert.

**The refit rejected.** A contact-based gate. It would be pressure under another
name, and the inversion is not a function of pressure alone.

**What would resolve it.** Asperity statistics measured on the specific pads used,
rather than inherited pad-class constants.

**Enforced by** `tests/test_contact_metrics_do_not_separate_the_inversion.py`.

---

## 4. The oxidiser term's sign flips with pressure, and the coupling is not fitted

**The measurement.** The Cu oxidiser sweeps disagree: ihnfeldt2008 peaks near
0.1 wt%, jani2025 is still rising at 6 wt%, and US 8,501,625 B2 contains **both
signs**. The hypothesis that the sign tracks BTA presence is falsified — that
patent shows both signs at the same 0.08 mM BTA.

What separates them is **down force**. Two groups identical in every slurry
variable (0.17 wt% abrasive, 0.0078 M citric acid, 0.08 mM BTA, no oxalic acid,
200 ml/min, pH 3.6, 93 rpm) differ only in pressure:

    2 psi:  8200 → 7200 → 6300    monotone falling
    1 psi:  1900 → 3900 → 3300    rising, peak near 9 wt%

This is mechanistically sensible — H₂O₂ grows a passivating film, and whether more
film helps or hurts depends on whether the mechanics can clear it, which is why
the falling group is also the higher-rate one.

**The refit rejected.** Moving `oxidizer_peak_wt_pct` up to fit
`jani2025_cu_rsm_composition_heldout`, whose 51.2% error is caused by this. It
would break ihnfeldt2008 and the 2 psi group of US 8,501,625 B2. Two pressures
from one patent cannot fit a coupling.

**Confound that cannot be separated.** The peak's citation (GT07, 2–3.6 wt%) is
for an **alumina**/glycine slurry while jani2025 is silica. Abrasive type and
pressure co-vary across these datasets.

**What would resolve it.** One H₂O₂ sweep repeated at three or more down forces
with everything else fixed.

**Enforced by** `tests/test_oxidizer_sign_tracks_pressure.py`.

---

## 5. Ceria's pH response is not unimodal, and `ph_response` is

**The measurement.** `netzband2020` measures a **valley**: 198 / 113 / 200 / 213
Å/min at pH 4 / 6 / 8 / 10. Netzband attributes it to two isoelectric points —
the oxide's (pH 2–3) and ceria's (~8) — with pH 6 optimal for neither.
`ph_response` is a single bell: between its ends it can rise-then-fall but never
fall-then-rise, so no parameter choice produces a valley. The 49.2% error is
structural.

Note what this is *not*. The experiment is a 2.25 cm² benchtop coupon, so absolute
rates are ~8× out — but the reported error is already scale-free (best common
scale k = 0.128 leaves exactly 49.2%), so the tool mismatch costs nothing. And
every point is inside the pack's declared pH range.

**The refit rejected.** A netzband-only fit reaches **15.0%** at peak 8.50, width
0.75, floor 0.95, acid_floor 0.70 — by making the pH response nearly flat, which
suits a dataset spanning only 1.9×. The same constants score **492.6%** on
dandu2009, the nine-point sweep they were fitted to, which swings 81×. The two
datasets demand opposite functional forms.

**What would resolve it.** A second pH channel keyed to the abrasive's isoelectric
point. Note a *universal* second channel was already tested and **falsified** —
the three pH residuals in this corpus have three different shapes — so this would
have to be a per-pack channel justified by more than one benchtop dataset.

**Enforced by** `tests/test_two_ceria_datasets_demand_opposite_ph_terms.py` and
`tests/test_no_universal_second_ph_channel.py`.

---

## 6. Where a bounded peak has no measured side, the answer is a refusal

**The measurement.** Three packs pin `ph_peak` to the lowest pH their source table
contains, because free fitting wanted an optimum at a pH nobody polished at. The
consequence is that one side of the bell is unmeasured, and `ph_acid_mechanical_floor`
is often 0 because there is no measured acid limb to floor. The model then decays
to **0.00 Å/min**, with no warning from the existing "2.5 widths from the optimum"
check (at pH 1.0 the distance is only 2.0 widths).

**The decision.** Each pack declares `ph_valid_range` — the span of the experiment
its constants were fitted to, never the union of every dataset that uses the pack
— and the engine warns outside it, naming the floor and stating that a **zero**
floor makes the result a refusal rather than a number.

**Deliberately *not* a gate.** Splitting the corpus by range membership gives
in-range median 18.9% (n=19) against out-of-range 19.4% (n=11), Mann-Whitney
**z = −0.15**. Out-of-range prediction is not measurably worse, and the group
contains some of the best results in the corpus (bouvet2002_w 2.3%). A gate is for
*"this prediction would be wrong"*, not for *"this prediction rests on fewer
measurements"*.

**Enforced by** `tests/test_ph_validity_range_is_declared.py` and
`tests/test_out_of_range_ph_is_a_warning_not_a_gate.py`.

---

## 7. Some datasets cannot be predicted better than they were measured

**The measurement.** `hong2007` contains three rows identical in every override,
reporting **2650 / 2400 / 1850 Å/min** — 13.0% mean absolute deviation. No model
can score better than that on this dataset. The model's 14.8% is at the floor,
and it *ties* the flat baseline rather than losing to it (both are 14.8%; a
previously recorded 12.6% was stale).

Corpus-wide, three datasets sit at or below their own replicate scatter:

| dataset | replicate scatter | shape error |
|---|---:|---:|
| `sic2026_ceria_h2o2_ph_DOE50` | 38.5% | 34.0% |
| `us9200180b2_cu_benzenesulfonic_series` | 24.6% | 26.8% |
| `hong2007_cu_ads_bta_polish_rate` | 13.0% | 14.8% |

**The refit rejected.** Any further fitting on these three. The SiC entry is the
instructive one: its 34.0% was treated as a weakness all session and is in fact
better than the set's own reproducibility.

⚠ Only 5 datasets have genuine replicates. For the rest the noise floor is
**unknown**, which is a limit of the evidence and not a licence to assume it is
zero. The blank `repl%` column in `cmp-sim accuracy` covers *three* different
states, and collapsing them into "no noise here" is the mistake this entry
guards against:

* the rates **are** averages and the source withholds the spread — the floor is
  real and unrecoverable (`du2004` says so explicitly of its five-run averages);
* the rates were **digitized from a figure** with the read error stated — a
  *transcription* floor (`bouvet2002_w` ~1.0% of typical rate, `bouvet2002_ti`
  ~2.7%);
* nothing is stated at all.

The transcription floors earn the column: `bouvet2002_w` scores 2.3% against a
1.0% floor and is effectively finished, while `bouvet2002_ti` scores 30.7%
against 2.7% and is a genuine unexplained miss. Without the floors both read as
"one good number, one bad number".

**What would resolve it.** Replicate runs at a handful of conditions per
dataset — three repeats of one condition is enough to bound the floor. This is
the cheapest missing experiment in the whole corpus and would tell us how much of
the remaining 19.5% median is even addressable.

**Enforced by** `tests/test_replicate_noise_floor.py`,
`tests/test_noise_floor_can_exist_unmeasured.py`,
`tests/test_replicate_column_is_reporting_only.py`.

---

## 8. A null result is not an omission, and silence must be sourced

**The measurement.** `w_fe_oxidizer` declares no pH response while its own dataset
sweeps pH. That pattern is exactly how a missing term hides: in
`cu_alkaline_benzenesulfonic`, a missing pH response had its work absorbed by the
oxidiser term, whose shape constant was then justified by what was really pH drift.

Here the silence is correct. US 2011/0186542 A1 runs a two-level pH control at
matched oxidiser and abrasive — six matched pairs, mean ratio **0.958** with an
**inconsistent sign** (more acid raises the rate in one pair, lowers it in five),
against an 8× oxidiser effect in the same table.

**The decision.** The null result is declared in the pack with its table and its
scope (pH 3–6 only — nothing licenses an alkaline W slurry), registered in the
audit, and **re-derived by the test** from the six pairs rather than trusted.

**What would resolve it** — i.e. what would turn the silence back into a term: a
W pH sweep outside 3–6, particularly alkaline, at fixed oxidiser. The current null
is a statement about pH 3–6 and nothing wider; outside that window the honest
behaviour is to decline rather than to extrapolate a flat response.

**Enforced by** `tests/test_pack_axis_blindness_audit.py`.

---

## 9. Titanium is an unsupported film, and one figure cannot make it supported

**The measurement.** `bouvet2002_ti_silica_size_sweep` is the corpus's largest
miss relative to its own floor: **30.7%** shape error against a ~2.7%
digitisation floor, on the size axis — otherwise the model's best (11.2%).

Three files come from the same paper, the same figure, the same slurry family and
the same tool. Only the film differs, and the three films disagree completely
about what particle size does:

| d50 (nm) | Ti | W | oxide |
|---|---|---|---|
| 12 | 2055 | 3097 | 1355 |
| 25 | 1840 | 2975 | 1875 |
| 45 | 1141 | 2743 | 1564 |
| 75 | 946 | 2893 | 1402 |

Empirical size exponent: **Ti −0.454, W −0.049, oxide +0.001**. All three are
scored with `pack: oxide_silica`, whose `abrasive_size_exponent` is **−0.05** —
W's value to two decimals. The pack is right for W (2.3%) and oxide (11.2%) and
wrong for Ti, and that one mismatched exponent is the entire 30.7%.

**The refit that was rejected.** Fitting a Ti exponent of −0.45. It would have
taken the error to near zero — and told us nothing. These four points are the
**only** titanium data in the corpus, so the constant would be tested on exactly
the data it was fitted to. The data is also weaker than the clean trend suggests:
as a pure power law Ti gives R² = 0.89 with a −13.9% residual at 25 nm, on four
*digitised* points.

**What would resolve it.** A second, independent Ti size sweep from a different
group, with a printed rate table rather than a figure. Two datasets make a fitted
exponent testable; one makes it self-validating.

The dataset already declares `film: other` and flags its pack as a placeholder
for shape/rank use only. The miss stays **visible** in the score rather than
being excluded — an unsupported film that quietly disappears from the report is
worse than a 30.7% a reader can see and interrogate.

**Enforced by** `tests/test_titanium_is_unsupported.py`.

---

## 10. A pack can look complete and be evidenced in one axis only

**The measurement.** `oxide_silica_anionic` and `oxide_silica_aminosilane` are
the two least-evidenced packs in the corpus (11% and 16% of their parameters
exercised by any dataset). Both are silica-on-oxide variants carrying a different
pH optimum. Diffing each against its parent `oxide_silica`:

| variant | parameters differing | all pH? |
|---|---|---|
| `oxide_silica_anionic` | 6 of 124 | yes |
| `oxide_silica_aminosilane` | 7 of 125 | yes |

Every other constant — Preston coefficient, pad mechanics, abrasive exponents,
conditioning, pattern terms — is inherited unchanged.

**The refit that was rejected.** Merging the variants back into the parent, which
would have removed two thinly-evidenced files. Re-scoring each variant's dataset
with the parent pack instead:

    cn109609035b_oxide_anionic_silica_ph    32.1%  ->   94.7%   (+62.5 points)
    us9422456b2_teos_silica_ph_pressure     25.3%  ->  126.6%  (+101.3 points)

The splits are decisively justified — one bell centred at pH 11 cannot also serve
pH 2 and pH 4.9 — so the packs stay.

**The limit.** They are justified *in pH and nothing else*. A reader opening a
62-parameter variant file could reasonably conclude that an anionic-silica slurry
had been characterised independently; it has been characterised in pH, on seven
rows, and borrows the rest. That is what inheritance is for, but the failure mode
is silent because the pack looks complete. Each pack now says so in its own
header.

**What would resolve it.** Any dataset for these slurry systems that sweeps a
non-pH axis — pressure, abrasive size or loading — would turn inherited constants
into evidenced ones. Today there is not one.

**Enforced by** `tests/test_silica_variant_packs_earn_their_split.py`,
`tests/test_parameter_evidence_inventory.py`.

---

## 11. A good shape error does not mean a good rate

**The measurement.** Shape error (how well the model ranks conditions) and scale
error (whether the absolute rate is right) fail independently. The corpus median
shape error is 19.5%, but of the 34 datasets whose sources permit absolute
comparison, **13 are off by more than 3×**:

| dataset | shape | measured ÷ predicted |
|---|---:|---:|
| `ep3161098b1_teos_silica_pressure_sweep` | **7.1%** | **139.2×** |
| `liang2026_4hsic_ceria_composite_h2o2_conc` | 20.6% | 92.0× |
| `bouvet2002_w_silica_size_sweep` | **2.3%** | 75.6× |
| `bouvet2002_oxide_silica_size_sweep` | 11.2% | 39.2× |
| `us6918821b2_cu_ic1000_pressure_speed_2x3` | 44.1% | 0.08× (over-predicts 12×) |

The first and third rows are the point: near-perfect *trends* on rates that are
wrong by one to two orders of magnitude.

**The refit that was rejected.** Re-anchoring each pack's `Kp` so its datasets
land near 1.0×. Rejected because the deficit is not in `Kp`: the packs that
*inherit* `Kp` unchanged are among the best calibrated (0.51×, 2.04×) while the
worst offender is their parent, and its gap tracks pH distance from the fitted
peak — inside `oxide_silica`'s range [10.0, 12.5] the same pack scores 0.60× and
0.85×, at pH 3–4.7 it scores 39×, 98×, 139×. Refitting `Kp` would bake an
extrapolation error into a constant that is currently correct.

**The limit.** A 19.5% median is a **ranking** claim. It supports "which
direction does this knob move the rate, and roughly how much"; it does not
support "this slurry removes 2,400 Å/min". Absolute rate depends on tool, pad
break-in and consumable lot, none of which the literature reports consistently.

**What would resolve it.** One calibration wafer on the user's own tool, and the
simulator already accepts it — this is what `cmp-sim fit` is for:

```bash
cmp-sim fit --template > runs.csv     # label, pressure, rpm, measured rate
cmp-sim fit myprocess.yaml runs.csv   # -> re-anchored Kp + leave-one-out error
```

A single measured rate at a known P·V re-anchors `Kp` for that pack and turns the
ranking claim into a rate claim; more rows unlock more factors, and `fit` names
the ones the data cannot identify rather than fitting them anyway. Verified
against an injected 2.5× tool factor, recovered to within 0.3%.

Note that the fitted `Kp` is an **effective Preston constant for your tool**, not
the pack constant times a tool factor: the chemistry and contact factors sit
between them (0.929× on the oxide example). The calibration is per-tool by
nature and never reaches the validation corpus — no corpus can do it in advance,
and a user factor that leaked into scoring would make the validation circular.

**Enforced by** `tests/test_scale_column_is_reporting_only.py`,
`tests/test_inherited_kp_is_not_the_problem.py`,
`tests/test_readme_numbers_are_computed.py`,
`tests/test_calibration_recovers_a_known_factor.py`.

---

## 12. Two levels cannot fit a peak: the silicon pH term is unfittable, not absent

**The measurement.** Bae 2022 (doi:10.3390/nano12213893) polishes bare (100) Si
with 1 wt% colloidal silica at 5.7 psi and raises pH from 9.70 to 10.90:

| condition | pH | rate (nm/min) |
|---|---:|---:|
| colloidal silica only | 9.70 | 139.5 |
| + NaOH 0.125 wt% | 10.90 | 177.1 |
| + KOH 0.069 wt% | 10.90 | 193.2 |

The effect is **real but weak**: a 15.8× rise in OH⁻ buys only 1.27–1.38× rate,
consistent with Seidel 1990's fourth-root alkali dependence
(R ∝ [H₂O]⁴·[KOH]^(1/4)).

**The fit that was rejected.** Giving `si_substrate_alkaline` a `ph_peak` and a
`ph_response_width`. Those are **two free constants** and the dataset holds
**two distinct pH levels**, so the fit is exactly determined — zero residual by
construction, an interpolation wearing a fit's clothes. It would also look like
validation on the accuracy report, because the dataset it was fitted to is the
only Si dataset in the corpus.

**Why this is a THIRD state, not one of the two we already had.** The blindness
audit previously knew only "missing physics" and "sourced null result". Silicon
is neither: the effect is present (unlike W's pH null, where six matched pairs
give a mean ratio of 0.958 with an inconsistent sign) but under-determined. The
distinction matters because the two demand opposite follow-ups — a null result
is finished, an unfittable axis is waiting for data.

**The cost, stated.** With no pH term the pack predicts one number for a ladder
that moves 1.38×, so `bae2022_si_wafer_alkali_ph` scores 12.6% and **does not
beat predicting the dataset's own mean** (also 12.6%). That is the honest
reading and it is left visible rather than repaired by a two-point fit.

**Also declined: the amine rows.** The same figure reports EDA 552.8, DETA
617.2 and TETA 499.1 nm/min at pH 10.81–10.90 — up to 3.5× the NaOH rate at the
*same* pH and the *same* OH⁻ concentration. The authors' own conclusion is that
the Si rate is not a function of pH alone. Scoring those rows on a pH term
would manufacture a model failure out of chemistry the pack never claimed to
contain; the amine gain is recorded where it belongs, in
`data/params/additives.yaml` (`ethylenediamine`, `gain_vs_naoh` 3.12×).

**What would resolve it.** A bare-Si pH sweep with **three or more** levels at
fixed colloidal-silica loading and fixed alkali source. Three levels
over-determine peak and width and make the fit testable.

**Enforced by** `tests/test_pack_axis_blindness_audit.py` —
`DECLARED_UNFITTABLE`, whose tests re-derive the level count and the 1.1–2.0×
gain from the dataset, fail if the two exemption tables ever overlap, and fail
if a third pH level is added (at which point the axis must be fitted or a new
reason recorded).

---

## 13. The pressure–velocity interaction is real, and both of its candidate mechanisms are rejected

**The measurement.** Three runs searched for a velocity exponent `b_V` in
`MRR ∝ P·V^b_V`. The ninth measured the shape of the thing being fitted instead
of proposing a fourth form, at fixed pressure, with no model in the loop
(`tools/velocity_pressure_interaction_probe.py`):

| body | film / abrasive | pressures | measured `b_V` |
|---|---|---|---|
| Sorooshian 2005 | thermal oxide / fumed silica | 2 / 4 / 6 psi | +0.370 +0.687 +0.764 (**up**) |
| mariscal2020 | PETEOS / ceria | 2 / 3 / 4 psi | +1.105 +0.857 +0.625 (**down**) |
| us6918821b2 | Cu / IC1000 | 1.5 / 4 psi | −0.416 → +0.863 (**sign change**) |
| Borucki 2023 (published) | Cu | 1 / 1.5 / 2 psi | −0.810 −0.620 +0.330 (**sign change**) |

So `b_V` is not a constant, and it is not a single function `b_V(P)` either: the
*direction* of `db_V/dP` inverts between consumable sets. The missing physics is
therefore a P–V **interaction** whose sign is selected by the film/slurry pair.

**The two mechanisms rejected, with zero fitted constants**
(`tools/pv_interaction_closure.py`):

1. **Contact-area evolution.** `MRR = c·A_r(P)·V` has `d ln MRR / d ln V = 1`
   for *every* pressure, because `A_r` is a quasi-static elastic response to the
   **normal** load and contains no velocity at all. Sub-linearity in `A_r(P)`
   moves the *pressure* exponent; it cannot move the velocity one. The
   magnitude check agrees for a second, independent reason: on every pack's own
   reference pad, at every measured pressure, `d ln A_r / d ln P = 1.0000` — the
   Greenwood–Williamson analytic result for exponential summit heights — with
   summit saturation only 1–5%, i.e. deep inside the linear regime.
2. **Pad-asperity flash heating as a cross term.** With `T = T₀ + c·P·V` and an
   Arrhenius chemical term,
   `b_V = 1 + (Ea/R)·c·P·V/(T₀ + c·P·V)²`, which is **> 1 for every positive
   `(Ea, c)`** and **rises with pressure**. Two of the four bodies measure
   `b_V < 1` at every pressure, and mariscal2020 *falls* with pressure. Scanned
   over 10–200 kJ/mol × six decades of heating coefficient: no parameter choice
   reaches the data. This is a different claim from the eighth run's rejection
   of heating as a pure *velocity* law (residual slope −0.549) and was tested
   separately rather than inherited.

**The refit rejected.** A per-pack `b_V(P)`. It replaces a fitted constant with
a fitted function, and the very measurement that motivates it forbids it: no
single `f` covers both clean factorials, since one rises with pressure and the
other falls.

**The cost, priced.** An oracle upper bound — give every (pressure, chemistry)
group its own *measured* `b_V`, fitted on the rows being scored — moves the
corpus median 16.72% → 14.54% (+2.18 pp). That number flatters the axis and is
reported with its own correction: only **3 of 49 datasets and 24 of 440
measured points (5.5%)** are touched at all, so the median moves largely by
re-ranking the median dataset, not by explaining anything. The P–V axis is a
**thin** axis, like velocity itself, and it is not the lever that reaches 10%.

**What would resolve it.** A mechanism that couples P and V with a sign
selected by a *measurable consumable property*. The corpus cannot supply it: the
three clean bodies differ simultaneously in abrasive material, film and pressure
range, so with three bodies the selector can only be narrowed, never decided.
Concretely: one velocity sweep at three or more down forces, repeated on two
abrasives (silica and ceria) with everything else held fixed on one tool.

**Enforced by** `tests/test_pv_interaction_closed.py` (12 tests) — the
flash-heating derivation's sign, the exact linearity of `A_r(P)` with its
saturation precondition, a ban on any pack declaring a P–V coupling constant,
the point share rather than the median as the axis's size, and a guard that the
three packs in the report resolve to **one** inherited base pad so the identical
slopes cannot be quoted as three independent confirmations.

---

## 14. The improvable error is DISTRIBUTED: no single-axis law reaches 10%

**Why this entry is the decisive one.** Four axes were closed in a row (pH,
velocity exponent, pressure saturation, P–V interaction) and the corpus median
moved about 1 pp in total. Every one of those axes was chosen because its
physics looked derivable; every one turned out to be *thin* (velocity 29
measured points, P–V 24, out of 427). STATUS.md therefore **pre-registered** a
reading before this measurement was run: if one axis holds ≥ 30% of the
improvable points it is the next target regardless of how its physics looks; if
none does, the error is distributed and the ≤ 15% allowance is invoked with the
evidence below rather than with the word "hard".

**The measurement** (`tools/axis_error_census.py`, fits nothing into any pack).
Each axis a dataset sweeps is priced by an **oracle**: grant the model one extra
free exponent `b` on that axis alone, `predicted' = predicted·(x/x_ref)^b`, fit
`b` per dataset in log space beside the single free scale the shape score
already allows, and re-measure the shape MAPE. The drop bounds what *any*
closed-form law on that axis could buy, because a law must carry **one** shared
constant into every dataset while the oracle gets a fresh one per dataset. A
dataset's points are owned by its best axis if that axis buys ≥ 2.0 pp;
otherwise the dataset is `distributed`. Correlation of residual with axis is
deliberately **not** used: in a Taguchi array several axes move together, so
correlation blames whichever axis co-varies with the true cause.

Of the 342 improvable points (`responsive_miss`, 35 datasets, median 19.5%):

| owning axis | points | share | datasets | median oracle gain |
|---|---|---|---|---|
| **distributed (no axis)** | **145** | **42.4%** | 17 | −0.0 pp |
| abrasive_wt_pct | 85 | 24.9% | 5 | 13.4 pp |
| velocity | 40 | 11.7% | 3 | 6.7 pp |
| abrasive_size_nm | 31 | 9.1% | 4 | 8.9 pp |
| oxidizer_wt_pct | 17 | 5.0% | 2 | 27.1 pp |
| pressure | 16 | 4.7% | 2 | 15.7 pp |
| slurry_ph | 8 | 2.3% | 2 | 16.1 pp |

The largest named axis holds **24.9%**, below the pre-registered 30%, and the
single biggest block — 42.4% of the improvable points — is error that **no axis
the dataset sweeps can reach even with a free exponent**. Reading 2 stands.

**Then the bound was tightened from oracle to law**, which is what makes this
final rather than discouraging. Refitting each axis with **one exponent shared
by every dataset that sweeps it** (each dataset keeps only its own free scale):

| axis | datasets | best shared Δb | mean shape | shared gain | oracle gain | per-dataset exponents |
|---|---|---|---|---|---|---|
| abrasive_size_nm | 9 | +0.00 | 13.8% → 13.8% | **+0.0 pp** | +5.0 pp | −0.40 … +0.13 |
| abrasive_wt_pct | 9 | +0.11 | 27.9% → 26.6% | **+1.4 pp** | +7.7 pp | −0.54 … +0.81 |
| pressure | 9 | +0.17 | 33.1% → 32.5% | **+0.6 pp** | +4.0 pp | −1.28 … +1.49 |
| slurry_ph | 8 | +0.05 | 30.4% → 30.2% | **+0.2 pp** | +3.9 pp | −0.67 … +2.20 |
| velocity | 5 | −0.43 | 43.5% → 39.5% | +4.0 pp | +5.5 pp | −0.88 … +0.15 |
| **oxidizer_wt_pct** | 4 | **+0.48** | 32.5% → **23.0%** | **+9.5 pp** | +13.4 pp | +0.01 … +0.92 |

On four of the six axes a shared exponent buys essentially nothing while the
per-dataset oracle buys 4–8 pp, and the reason is visible in the last column:
the per-dataset exponents **disagree in sign**. That is not a law waiting to be
found; it is between-dataset dispersion that a single constant cannot represent.
`abrasive_wt_pct`, the largest named axis, is the clearest case — exponents from
−0.54 to +0.81 across nine datasets, so its 13.4 pp oracle gain collapses to
1.4 pp for any law.

**The refit that was rejected.** The obvious response to a 24.9 % axis is to
give `abrasive_wt_pct` a fitted exponent, which the table above prices at
+1.4 pp of mean shape — and that offer is **rejected**, because the same table
shows the per-dataset exponents running −0.54 … +0.81. A shared constant would
then be pushing five of nine datasets in the *wrong direction* to help the other
four, which is interpolation dressed as a law. The `slurry_ph` (+0.2 pp),
`pressure` (+0.6 pp) and `abrasive_size_nm` (+0.0 pp) refits are rejected for the
same reason and at even lower price. **The decision** is that no exponent is
added on any of the four dispersed axes, and the ≤ 15 % allowance is invoked on
the evidence above.

**What licenses this, and what it does not.** It licenses the ≤ 15 % completion
criterion: the sum of every *law-attainable* gain above is ≈ 6 pp spread over
axes that overlap, against a 42.4 % block no axis reaches, so ≤ 10 % is not
reachable by adding closed-form laws one axis at a time. One axis appeared to
survive the tightening — `oxidizer_wt_pct`, shared exponent **+0.48**, 9.5 of
13.4 pp — and was pursued immediately as a derivation target, because +1/2 is
what a radical chain with bimolecular termination predicts with zero free
constants. **§15 records the outcome: the half order is refuted (two admissible
blocks measure a *negative* order) and the +9.5 pp itself is inadmissible — it
comes from one dataset the pack was calibrated on and one whose oxidant
co-varies with an axis the model does not implement. Admissible gain on this
axis: 0.0 pp.** With §15 the last open axis is closed and this limit is final.

**What would resolve it.** Not more datasets on the same axes: the dispersion is
*between* datasets that each sweep one axis cleanly, so adding a tenth such
dataset adds a tenth exponent, not agreement. What would resolve it is a
**cross-axis** body — one tool, one film, one operator, sweeping two axes in a
full factorial with consumable properties measured rather than inferred — which
is precisely the measurement the earlier limits (§1, §4, §13) also name.

### ⚠ AMENDED 2026-09-27: part of the dispersion on `abrasive_wt_pct` was the MODEL's

The argument above is **not withdrawn**, but its single strongest example has to
be given back. `abrasive_wt_pct` was presented as "the clearest case" of
irreducible between-dataset dispersion, on the strength of per-dataset exponents
running −0.54 … +0.81 — exponents that straddle zero, so no shared constant is
even the right *direction*. Three of those nine exponents were negative **because
the model was over-predicting the concentration response**, not because those
experiments disagreed with the others.

The cause is recorded in full in `docs/derivations.md`, "The two concentration
branches were different PHYSICS": the saturating branch of
`models/luo_dornfeld.mechanical_factor` multiplied by the active-particle *count*
ratio `N(C)/N(C_ref)`, i.e. `N^1`, where the module's own derivation requires
`N^(1-alpha*chi)`. That asserts `chi = 0` on datasets whose pack carries
`abrasive_conc_half_wt_pct`, against the `chi = 1.0` the same call resolves, so
those datasets — and only those — needed a negative residual exponent to undo
the model's excess slope. Re-running the identical census across that one fix:

| | per-dataset exponents | shared gain | oracle gain | points owned |
|---|---|---|---|---|
| before | −0.54 … +0.81 (3 negative) | +1.5 pp | +7.6 pp | 85 (24.9%) |
| after | **+0.00 … +1.05 (0 negative)** | **+2.5 pp** | +6.9 pp | 63 (18.4%) |

Three things follow, and they do not all favour the same conclusion, so all
three are recorded:

1. **The headline reading survives, and by a wider margin.** The pre-registered
   test was whether any one axis owns ≥ 30% of improvable points.
   `abrasive_wt_pct` fell from 24.9% to **18.4%**, and the `distributed` block
   — error no swept axis reaches even with a free exponent — *grew* from 42.4%
   to **48.8%**. Reading 2 stands more firmly than when it was written.
2. **The sign-disagreement evidence for this one axis is withdrawn.** The
   remaining dispersed axes (`abrasive_size_nm`, `pressure`, `slurry_ph`) still
   straddle zero and still buy < 2 pp shared, and they continue to carry the
   argument. `abrasive_wt_pct` no longer does, and
   `tests/test_axis_error_is_distributed.py` now measures it separately rather
   than asserting a sign scatter that is no longer there.
3. **A shared exponent on this axis now buys 2.5 pp, over the 2.0 pp bar — and
   is still rejected, on different grounds.** The old rejection ("it would push
   five of nine datasets the wrong way") no longer applies. The new one is that
   all nine residual exponents are now **positive**, which says the model
   consistently *under*-responds to abrasive loading — a missing term with a
   definite sign, not noise. Fitting a shared offset would reproduce that
   residual by construction and destroy the evidence that a term is missing.
   **What would unblock it:** a derivation that predicts an additional positive
   concentration dependence from measured quantities — the obvious candidate
   being that `N_active` should scale with the real contact area (which itself
   grows with loading through slurry-film thickening), not with the nominal
   area. That is a derivation target, and it is the first one this corpus has
   produced with an unambiguous sign.

**The lesson this limit now also carries:** a "dispersion" diagnosis is only as
trustworthy as the model whose residuals it is measured on. Residual exponents
that straddle zero can mean the data disagree, or they can mean the model is
wrong in a way that some datasets are exposed to and others are not. The two
look identical in the census table. Distinguishing them requires asking *which
datasets carry the negative exponents and what they share* — here, the packs
that supply `C_half` — which is a question the census does not ask on its own.

### ⚠ AMENDED AGAIN 2026-09-28: point 3 above is largely withdrawn, and the same lesson is why

The amendment above concluded that a shared exponent on `abrasive_wt_pct` now
buys 2.5 pp — over the 2.0 pp bar — and called that "the first derivation
target this corpus has produced with an unambiguous sign". That reading has to
be given back in its turn, and for exactly the reason the amendment itself
states: the residual was still being measured on a model carrying the constant
under suspicion.

`abrasive_conc_half_wt_pct` was **withdrawn from every pack that carried a
value** on 2026-09-28. The decision was not made on error scores — those
recommend *re-fitting* it on tungsten (0.01 → 0.02 scores 10.1% → 7.8%) — but
on necessity: `tools/conc_half_necessity_probe.py` re-runs the shipping solver
at each condition of every iso-condition loading series with and without the
constant and fits a power law to the model's own predictions, asking whether
removing it pushes the model *outside the measured band*. Verdict over the
seven series it touches: **NEEDED 0, HARMFUL 1, redundant 6**. Full derivation
in `docs/derivations.md`, "Withdrawing `abrasive_conc_half_wt_pct`".

Re-running the identical census across that removal:

| | per-dataset exponents | shared gain | oracle gain |
|---|---|---|---|
| with `C_half` | +0.00 … +1.05 (0 negative) | +2.5 pp | +6.9 pp |
| without | **−0.06 … +0.84 (3 negative)** | **+1.5 pp** | +5.9 pp |

So the axis got **smaller**, not larger: a substantial part of what looked like
a missing law with a definite sign was the withdrawn constant's own residual,
and the shared gain fell back below the 2.0 pp bar. Point 3's "derivation
target with an unambiguous sign" is therefore withdrawn as a *quantified* lead;
the `N_active ∝ real contact area` idea remains physically reasonable but no
longer has a measured residual arguing for it on this corpus.

The three negatives that returned are **−0.06, −0.04, −0.02**, on precisely the
three datasets whose pack lost the constant. They are an order of magnitude
below the 0.15 exponent magnitude this repo treats as meaningful elsewhere, so
this is *indistinguishable from zero*, not a return of the sign disagreement
this section originally rested on. Point 2 stands: the sign-disagreement
evidence for this axis remains withdrawn, and the remaining dispersed axes
(`abrasive_size_nm`, `pressure`, `slurry_ph`) continue to carry the argument.
Point 1 stands unchanged.

**What would resolve it:** a loading sweep that resolves the saturation knee —
one film, one fixed process condition, at least a decade in wt%, reaching the
plateau. No dataset in this corpus does that, which is why the constant is
unidentifiable rather than merely unfitted, and why re-fitting it against
series that are already saturated at the bottom of their own range produced a
value (0.01 wt%) that suppressed a real 5× loading extrapolation into
invisibility on `ep3161098b1_w_silica_pressure_sweep`.

**The second-order lesson, which is the transferable one:** *re-examine a
fitted constant by asking whether it is NECESSARY, not whether it scores well.*
An error score compares the constant against itself on its own fitting data and
will recommend re-fitting a constant that should be deleted. And when a
constant's note states why it exists — all three said "without it the slope is
+1.0" — that sentence is testable, and it can expire.

**Enforced by** `tests/test_axis_error_is_distributed.py`,
`tests/test_predictive_accuracy.py::test_no_pack_carries_a_saturation_constant_that_is_never_necessary`.

**Enforced by** `tests/test_axis_error_is_distributed.py`.

---

## 15. The oxidiser axis is closed too: the half order is refuted and the gain that motivated it is inadmissible

**Why this entry exists.** §14 left exactly one axis open. `oxidizer_wt_pct` was
the only axis whose oracle gain survived being tightened to a single shared
exponent (+9.5 of 13.4 pp, shared exponent **+0.48**, all per-dataset exponents
positive), and +0.48 sat on a mechanism that could be *derived* rather than
fitted: an oxidant feeding a steady-state radical population terminated by
radical–radical recombination gives `[R] ∝ [ox]^(1/2)`, so a surface reaction
first order in the carrier inherits a **half order with zero free constants**.
`tools/oxidizer_order_probe.py` ran the three tests STATUS.md pre-registered
before any pack was touched. The axis closed on all of them.

**Test 1 — the order, measured from the rates themselves (not the residual).**
Eleven clean oxidiser blocks exist (same pressure, same rpm, same every other
override; only the oxidant moving). Seven are excluded because the pack's
oxidiser constant was fitted on them — scoring a mechanism on its own
calibration set is self-scoring. Of the four admissible blocks, the measured
log–log orders are

| block | [ox] range | order | ±2σ verdict |
|---|---|---|---|
| du2004_cu_h2o2 | 1–10 wt% | **−0.33 ± 0.04** | neither +1/2 nor +1 |
| us8070843b2_w_h2o2 | 2.0–6.1 wt% | **+0.62 ± 0.03** | neither |
| us8501625b2_cu (low-P block) | 3–15 wt% | **−0.16 ± 0.03** | neither |
| us8501625b2_cu (high-P block) | 3–15 wt% | +0.39 ± 0.24 | ~ +1/2 |

The pre-registered condition was "indistinguishable from +1/2 in **each** block,
not merely on average". One of four passes, and two of the four are **negative**
— the rate *falls* as oxidant rises. A negative order is not a noisy half order;
it is a different mechanism (over-passivation: the oxide/inhibitor film thickens
faster than it is sheared off). No radical-chain order can be negative, so the
derivation is refuted rather than unresolved.

**Test 2 — the termination order is untestable on this corpus, and is therefore
not claimed.** First-order termination gives +1, bimolecular gives +1/2, and the
two are distinguished by whether the apparent order *falls* as `[ox]` rises. That
needs ≥ 3 oxidant levels in each half of one sweep. No dataset in the corpus has
them (the widest, `us20110186542a1_w`, spreads its 15 points over other axes).
Recorded as unmeasurable, not as support.

**Test 3 — a purely multiplicative oxidiser term is forbidden, independently.**
Six datasets measure a *non-zero* rate at exactly zero oxidant: 203 (11 % of the
block maximum), 150 (4 %), 610 (47 %), 500 (19 %), 96 (3 %), and 208 nm/min —
the last being **176 %** of that block's best oxidised rate, i.e. copper polishes
*faster* with no oxidiser at all. Any `[ox]^n` factor multiplying the whole rate
predicts zero there. The existing additive mechanical floor
(`cmp_sim/models/chemical_rate.py`) stays, and this is why.

**The refit that was rejected, and why it was never admissible evidence.** The
+9.5 pp that made this axis look open comes from exactly two datasets, and the
audit in the same tool disqualifies both:

- `us20110165777a1_cu_h2o2_series` (b = +0.48, gain +32.3 pp) — `used_for_calibration:
  true`. The pack's `oxidizer_passivation_K` was least-squares fitted on this
  patent's own table. Its gain is the fit recognising itself.
- `jani2025_cu_rsm_composition_heldout` (b = +0.92, gain +21.9 pp) — its oxidant
  sweep **co-varies with `promoter_M` at r = +0.53**, and `promoter_M` is measured
  INERT in the model (0 % end-to-end response). A free exponent on the oxidant is
  therefore paid for by an axis the model does not implement: the residual it
  removes is the promoter's effect wearing the oxidant's label.

**Admissible oxidiser gain across the whole corpus: 0.0 pp.** The apparently
surviving axis was an artefact of one self-scored dataset and one confounded
one. Note that the exponent each one wanted also disagrees (+0.48 vs +0.92),
which is the same sign-dispersion signature §14 documents — it was hidden only
because both happened to be positive.

**The decision.** No oxidiser exponent is added. §14's single open axis is
closed, which makes §14 final: every axis carrying improvable error is now
either dispersed, thin, or evidentially empty, and the **≤ 15 % completion
criterion stands** on measurement rather than on effort.

**What would resolve it.** One oxidant sweep of ≥ 6 levels spanning a decade,
on a fixed formulation whose promoter/chelator loadings are held constant and
printed, on a film whose measured order is positive (the W systems are the
candidates). That single body would decide +1/2 versus +1 versus the
over-passivation branch, which the present corpus cannot.

**Enforced by** `tests/test_oxidizer_order_is_not_half.py`.

---

## 16. ≤ 10 % is outside the reach of any shared-constant model on this corpus, and the reason is not "missing physics"

**The single number.** Grant every scored dataset a free exponent on its own best
axis — fitted on the very rows being scored, with no requirement that different
datasets agree on it. That is an **oracle no physical model can attain**, since a
model must carry one constant into every dataset. Under that grant the corpus
median falls from **18.6 % to 11.9 %**, and the count of datasets at or below
10 % rises only from **14 to 20 of 46**.

So ≤ 10 % is not merely unreached; it is **above the ceiling of the entire
law-adding programme**, measured rather than asserted. This is the evidence
STATUS.md's completion criterion requires for invoking the ≤ 15 % allowance, and
§14 and §15 explain the mechanism: on four of six axes a shared exponent buys
almost nothing because the per-dataset exponents disagree in sign, and the one
axis that appeared to survive turned out to rest on inadmissible evidence.

**Where the error actually is — this reverses the intuition that motivated the
measurement.** §14 named a 145-point block that no axis owns, and it was natural
to read that as the hard part of the corpus. It is the opposite:

| block | datasets | points | median shape | point-weighted | share of weighted error |
|---|---|---|---|---|---|
| unowned by any axis | 17 | 145 | **11.2 %** | 18.4 % | 28.9 % |
| owned by some axis | 18 | 197 | **23.9 %** | 33.2 % | 71.1 % |

The datasets no axis explains are the ones the model gets **right**. "No axis
owns it" means "there is no single input whose mis-modelling dominates", which is
what a model in reasonable shape looks like on a clean sweep — not a mystery.
The error is concentrated in the *owned* block, and §14 already priced what any
shared law can recover there: ≈ 6 pp at most, spread over overlapping axes.

**Partition of the unowned block by cause** (`tools/unowned_error_partition.py`,
first matching cause in order, all other flags still printed):

| cause | datasets | points | median shape |
|---|---|---|---|
| at its own replicate floor | 0 | 0 | — |
| reproducibility **unmeasured** | 12 | 109 | 10.8 % |
| absolute-scale failure (>3×) | 3 | 14 | 18.9 % |
| loses to predicting the mean | 1 | 4 | 11.2 % |
| genuinely **unexplained** | 1 | 18 | 7.0 % |

Only **18 points (12.4 % of the block)** are unexplained by any of the named
causes, and that one dataset already scores 7.0 %. There is no reservoir of
unexplained error in the unowned block for new physics to drain.

**The refit that was rejected.** The tempting move is to chase the 3
scale-failure datasets (`us8501625b2` at 12.7×, the two `us20190127607a1`
variants at 0.19–0.24×) with per-dataset Kp corrections, which would improve the
absolute-rate column. **Rejected**: those are 14 of 427 points, the shape metric
already divides the scale out (limit 11), and a per-dataset Kp is a calibration
constant, not physics. **The decision** is that scale failures are reported in
their own column and not fitted.

**What this does NOT excuse.** The 12 datasets whose reproducibility is
unmeasured are 109 points — *the floor is unknown for most of the corpus*, and
unknown is not zero. The honest statement is therefore bounded from one side
only: ≤ 10 % is unreachable, and whether 15 % is *at* the floor cannot be settled
until more papers' stated reproducibility is transcribed. That is recorded in
STATUS.md as work, not as a limit.

**What would resolve it.** Papers reporting replicate scatter (±σ, n ≥ 3, error
bars) for the films in this corpus, transcribed into the datasets so
`Score.at_noise_floor` can speak for more than 6 of 46 — plus the cross-axis
factorial body named in §1, §4, §13 and §14.

**Enforced by** `tests/test_ten_percent_is_out_of_reach.py`.

## 17. 15 % is NOT the measurement floor: the corpus's own sources refute a blanket claim

§16 closed one side of the accuracy question — ≤ 10 % is outside the reach of any
model that shares its constants across datasets — and left the other side open:
*is 15 % simply where measurement noise starts?* The obstacle was that
`Score.replicate_scatter` can only be computed where a dataset repeats a
condition, which is 6 of 46 scored datasets. Unmeasured is not zero, and it is not
15 % either.

**The pass.** Every source whose full text is held locally was searched, **in
corpus order (alphabetical by dataset stem), which is independent of each
dataset's score**, for a reproducibility the *authors* state: ±σ, "n = 3", error
bars, "average of N runs", a stated repeatability. Every statement found was
transcribed verbatim into `cmp_sim/data/validation/reproducibility.yaml`,
including the ones that hurt. 17 datasets were searched and recorded.

**The answer is negative.** Only **four** of 17 state something quantifiable, and
they do not agree with each other by an order of magnitude:

| dataset | stated floor | kind | our shape error |
|---|---|---|---|
| jani2025 (both halves) | **1.5 – 9.5 %** RSD, "most below 7 %" | replicate RSD, per condition | 5.6 % / 51.2 % |
| ihnfeldt2008 | ±14 nm/min → **19.1 %** averaged per row | absolute uncertainty | gated |
| miranda2004 | **36.9 – 37.6 %** | derived from printed ANOVA | gated |
| bouvet2002 W / Ti | ±3 / ±4 nm/min | *transcription*, not measurement | 2.3 % / 30.7 % |

So published CMP reproducibility spans **1.5 % to ~37 %** within one small corpus.
A blanket "15 % is the noise floor" is therefore **unsupported in both
directions**: it is far too generous for jani2025, whose own RSD ceiling is 9.5 %,
and far too strict for miranda2004. The evidence for accepting ≤ 15 % remains what
§14 and §16 established — between-dataset dispersion of the axis exponents, and
the oracle bound of 11.9 % — and it is *not* a noise-floor argument. That
distinction is now pinned by a test.

**Three ways a floor can fail to exist, kept apart.** Collapsing them is how a
reporting change becomes an excuse:

* **`spatial_only`** — kenchappa2021 prints an SD across 48 points on *one wafer*
  diameter, dandu2009 across 17. That is within-wafer non-uniformity. A model
  predicting the *wafer-average* rate is not bounded by it. kenchappa2021 scores
  42.8 %; reading its within-wafer SD as a floor would excuse the corpus's largest
  single miss with the wrong statistic. **Yields no floor, by test.**
* **`replicated_scatter_withheld`** — son2021 (3 wafers), wei2026 ("repeated at
  least three times"), du2004 (5 runs) all replicate and none print the spread.
  The floor exists, is non-zero, and is unrecoverable. **Yields no floor.**
* **`none_stated`** — searched and silent: bae2022, li2021, su2011, lai2001,
  bouvet2002 oxide, mariscal2020.

**mariscal2020 is the trap worth naming.** It prints RMS errors of 4.6 % and
11.9 % — for *its own kinetic model's fit*, not for repeated measurement. Reading
those as reproducibility would credit this project with a bound the experiment
never measured. Recorded as `none_stated` with the quote, so the temptation is
documented rather than available.

**The one derived number, and why it is admissible.** miranda2004 withholds its
replicate rates but prints a 2² factorial with r = 3 (n = 12), the four cell
means, and adjusted R² = 0.69. A saturated 2² model passes exactly through the
four means, so SS_between is computable from the printed means alone, and the
printed adjusted R² then fixes SS_error:

    SS_between = r · Σ(ȳᵢ − ȳ)²
    SS_error   = (n−p)·a·SS_between / ((n−1) − (n−p)·a),    a = 1 − R²_adj
    σ_pure     = √(SS_error/(n−p))  →  36.9–37.6 % of the grand mean

The band is the p = 3 / p = 4 ambiguity (the text rejects the H₂O₂ main effect at
p = 0.588, so the fitted model may have three parameters, in which case SS_error
also carries lack of fit and this is an upper bound). The test **inverts the
algebra and reproduces the printed 0.69 to 3 decimal places**, so this is a
checkable transcription rather than a plausible-looking derivation. Both
miranda2004 rows that matter are gated by the pack anyway, so nothing is excused
by it — it exists to show that a ~37 % floor is a real published condition.

**What this changes about the target.** Nothing about the model, and one thing
about the claim: accuracy statements must now be made **per dataset against that
dataset's own floor**, never against a corpus-wide floor. jani2025's held-out half
at 51.2 % is 5.4× its own stated reproducibility — a real failure, and the most
valuable single number this pass produced, because it is the one place in the
corpus where "the data is just noisy" is definitively ruled out by the authors
themselves.

**What was tried and rejected.** Three tempting uses of this data were
**rejected**:
1. *Excusing the corpus median with a 15 % floor.* Rejected: only 4 of 17 sources
   quantify a floor and they span 1.5–37 %, so no single number covers the corpus.
2. *Using within-wafer SD as the floor* (it is available for kenchappa2021 and
   dandu2009, and would have made the corpus's largest miss look like noise).
   Rejected as the wrong statistic — it bounds a point prediction, not a
   wafer-average one. Enforced by test.
3. *Reading mariscal2020's 4.6 %/11.9 % RMS as reproducibility.* Rejected: those
   are its own kinetic model's fit residuals; the experiment never measured
   replication. **The decision** is that a floor is quoted per dataset, only where
   its own authors state one, and that ≤ 15 % is argued from §14/§16 dispersion
   rather than from noise.

**What would resolve it.** Replicate-level data, not summary statistics: a corpus
source that prints the individual repeated rates (or ±σ per condition) for films
other than Cu. jani2025 is currently the only such source, and it is Cu. For the
gated datasets (ihnfeldt2008, miranda2004) the floor is now known but the rows are
declined by the pack, so resolving §4's oxidiser-sign gap would also make two
measured floors usable for the first time.

**Enforced by** `tests/test_stated_reproducibility.py` (10 tests), which checks
that every transcribed number appears in its own quote, that `spatial_only` and
withheld-scatter kinds yield no floor, that the miranda algebra round-trips, and
that the transcription cannot move a median.

## 18. Two swept axes were INERT — and the fix splits cleanly into a wiring bug and a refuted transfer

**What was measured.** §17 left exactly one unambiguous target: `jani2025_cu_rsm_composition_heldout` at **51.2 % shape error** against the authors' own published reproducibility of **1.5–9.5 %** ("mostly below 7 %"). Uniquely in this corpus, the "it is just noise" explanation has been eliminated *by the source*. `tools/jani_residual_probe.py` decomposed that block by axis and the headline finding was not a missing law:

| axis | response to a 2× change (before) | residual log-slope |
|---|---|---|
| `abrasive_wt_pct` | +23.80 % | −0.15 ± 0.29 |
| `oxidizer_wt_pct` | −8.11 % | +0.92 ± 0.33 |
| **`chelator_M`** | **0.00 % — INERT** | −0.18 ± 0.46 |
| **`promoter_M`** | **0.00 % — INERT** | **+0.58 ± 0.23** |

Two of the four swept axes did not move the prediction **at all**, while the inherited layer (`legacy/sim/chemistry.py`) had carried a sourced, species-gated, unit-tested term for each all along. The inherited `chemistry_factor()` assembles only four terms (oxidizer, inhibitor, ceria, pH softening) and `cmp_sim`'s wrapper never called the other two. The engine accepted the inputs, stored them and ignored them — the accept-store-ignore failure this project rates as worse than a missing feature, because the output still *looks* like a prediction about those axes.

**The dataset's own excuse does not hold, and that matters.** This file's header blames the block's score on the E9/E23 pair, which differ only in an unmodelled oxalic-acid level and are therefore identical model inputs. Priced for the first time: the measured E9/E23 ratio is 1.142, and the block's median error **excluding that pair is 40.3 % against 38.6 % including it**. The pair is not the story. A standing in-file excuse that has never been quantified is indistinguishable from a wrong diagnosis.

**The fix splits, and only half of it is admissible.**

*`chelator_suppression` — wired, and it transfers.* `exp(−a(C − C_ref))`, glycine, `a = 1.5119 /M`. Its reference is a real composition (0.1332 M), so the normalisation is well posed and the term is exactly 1.0 there. Direction is the counter-intuitive, citable part: more glycine removes **less** copper, which is the paper's own conclusion ("glycine effectively functions as an inhibitor rather than a dissolution promoter", coefficient −440.91, p = 4.1e-7). Now live at −32.5 % per doubling.

*`carboxylate_promoter` — SHAPE transfers, MAGNITUDE is refuted.* This is the finding worth keeping, because the evidence points both ways at once and a single-number verdict would hide half of it:

| what was tested | result | verdict |
|---|---|---|
| exponent *m*, fitted on **US6309560B1** (a different document from any Cu dataset scored here) | local slope **+0.675** vs the measured residual slope **+0.58 ± 0.23**; switching the term on flattens the residual to **+0.010** and the block's shape error to **29.9 %**, with **zero new constants** | **transfers** |
| the floor φ = 0.078058 | absolute scale moves **0.91× → 0.075×**, a **13× over-prediction** | **refuted** |

The cause is structural and knowable without any fit. The pack declares `promoter_ref_M = 0`, so `f(C) = g(C)/g(0) = g(C)/φ` multiplies **every** non-zero concentration by `1/φ = 12.8×`. That factor is not a claim about oxalate; it is the claim *"this pack's reference composition removes material only mechanically"* — false, since that reference carries H2O2 and glycine whose own terms are already normalised to it. Applying it counts the reference chemistry twice, the error that once collapsed a Cu rate 20× in the predecessor. φ was measured (21.7 → 278.0 nm/min) in a BTA-free alumina system whose *only* chemistry was the complexant.

**What was rejected.** Taking the 21 pp shape gain. It is available and it was declined, because publishing a rate that is 13× wrong to improve a trend number is the exact trade `core/sanity.py` exists to prevent. Also rejected: fitting a per-pack φ to keep the shape gain while repairing the scale — that adds a free constant to a pack with one promoter level in its own calibration, which is interpolation, not physics. The promoter axis is therefore **inert by declaration**: the rate does not respond, and the model *says so*, with its evidence, in the result's warnings.

**What would resolve it.** One number: the measured rate of this pack's own reference composition with **zero oxalate**. Then φ is data rather than a transfer, the denominator is well posed, and the already-verified exponent can be switched on for real.

**Corpus effect.** Median shape **unmoved at 18.9 %** (LOO 21.3 %) by design — nothing was fitted. The jani block improves 51.2 % → 50.1 % from the chelator term alone, and its absolute scale improves 0.91× → 1.11×. A larger median move would have meant a term was firing on packs whose reference composition it does not describe, so the median is asserted, not merely reported.

**Enforced by** `tests/test_chelator_promoter_axes_are_wired.py` (7 tests): the chelator axis must respond and must respond *downwards*; the term must be exactly 1.0 at the pack reference; the promoter axis must be inert **and** must carry a warning containing its own evidence (`0 M`, `12.8`, `0.075`, `29.9`) plus the unblocking measurement; the gate must be about the **zero denominator**, verified by giving the same recipe a non-zero promoter reference and requiring the term to come back; and the corpus median must not move. Reverse-calibrated: **6 of the 7 fail against the pre-fix code.**

**An honest regression that came with the fix.** The jani block's flat-mean baseline is 49.2 %, and wiring the chelator term moved the model from 51.2 % to **50.1 %** — so this dataset now appears in the report's "does NOT beat predicting the mean" list, which it did not before (9 datasets → 10). That is recorded rather than smoothed over, because it is informative in a specific way: the improvement is real and directional (absolute scale 0.91× → 1.11×, and the chelator residual slope falls from −0.18 to +0.09), yet the block remains dominated by an axis the model still does not carry. Losing to the mean here is not evidence that the chelator term is wrong; it is evidence that **one correct term is not enough on a 4-axis RSM block where a second swept axis is declared inert**. The exit condition is the same single measurement named above.

## 19. Every swept axis in the corpus is now CONNECTED — the exhaustive scan, and the refuted constant it uncovered

§18 found two inert axes by accident, while investigating a single dataset. That is the wrong way to find them, and it left an unasked question: the other 45 datasets had never been checked the same way. An inert axis is an input the engine accepts, stores and then ignores while still printing a number that looks like a prediction about it — and it is the **only error class in this project fixable with zero new constants**, because the missing piece is a wire rather than a law. It is therefore both the cheapest thing to check and the easiest to mistake for missing physics.

It also bears directly on §14. That section read 145 points as "owned by no axis" and concluded this was the shape of a healthy model on a clean sweep. A **disconnected input looks exactly the same** from the census's point of view, because an input that never reaches the rate cannot own any of the residual either. Until now that reading was unverified.

**The scan.** `tools/inert_axis_scan.py` perturbs all **91 swept axes across 46 datasets** end to end over the range each paper actually ran, and classifies every inert result into one of four kinds. The classification, not the count, is the product.

| kind | axes | meaning |
|---|---|---|
| **wiring** | **2 → 0** | the term exists and was handed the value in a form it cannot read. **A bug; free to fix** |
| **silent** | 4 | inert, and nothing in the output says why. The worst kind |
| declared | 10 | the pack announces the gap (`chemistry layer inactive`, `not declared by pack`, a reasoned refusal) |
| aliased | 9 | the key restates another axis the same dataset varies (`abrasive_d50_nm` beside `abrasive_size_nm`), so perturbing it alone is not a perturbation of the physics |

**The wiring bug: every inhibitor sweep in the corpus was dead.** `Additive` carries `conc_wt_pct` and `conc_mM` as *separate* optional fields; the inhibitor role reads the molar one; the scoring harness was writing the millimolar figure into the weight-percent slot. Nothing raised, because both fields are `Optional[float]`. The term declined the value and emitted a warning saying exactly that — and nothing was reading the warning. `ADDITIVE_OVERRIDES` now declares the **unit** alongside the species and role, and a test requires the key's own suffix (`_mM`, `_wt_pct`) to agree with the field it routes to.

**Fixing the wire did not improve anything. It exposed a refuted constant — that is the result.** Connecting the axis drove `hong2007`'s absolute scale from 0.49× to **0.059×**, a 17× over-prediction. The reason is mechanistic: the only adsorption constant reachable for `cu_h2o2_bta` is the **equilibrium** (BTA × Cu) value K = 3283 L/mol (ΔG = −30.02 kJ/mol, doi:10.2320/matertrans.m2016310, electrochemical + quantum-chemical). Under polishing the Cu–BTA layer is continuously abraded away, so its **steady-state coverage cannot be the equilibrium coverage of a quiescent corrosion experiment**.

| | 0 / 10 mM BTA rate ratio |
|---|---|
| the term as parameterised | **18.4** |
| Hong 2007 measured (doi:10.1149/1.2717410 Fig. 1, pH 4, 5 wt% H2O2) | **1.21** |

Which constant is wrong was already on record and it is **not** the shape parameter `k`: the pack's own note (ruling #17) reports that holding k = 3.0 and lowering K alone to 183 L/mol reproduces [LEN00]'s 0.1 wt% point exactly and its 0.25 wt% point to −11.9 %.

**What was rejected.** Substituting K = 183 L/mol. It was measured in an **alkaline** NH4OH/alumina system, and BTA protonation and Cu(I)–BTA stability are both pH-dependent, so carrying it into an acidic H2O2/glycine pack is a transfer across the very variable that governs it — a free constant bought with a plausible story.

**Why the refusal is TWO-SIDED, and why the first attempt at this gate was wrong.** The first version kept the above-reference half on the argument that coverage is already θ_ref = 0.767 at the 1 mM reference, so the factor is bounded below by exp(−k[1−θ_ref]) = 0.50 there and "makes almost no claim". The bound is arithmetically correct; the inference drawn from it is not.

| | bound on the factor | what the one measurement says |
|---|---|---|
| C < C_ref | rises to exp(+k·θ_ref) = **9.97** at zero | hong2007's three zero-BTA rows come out **16.9×, 18.7×, 24.3×** high; absolute scale 0.49× → 0.059× |
| C > C_ref | bounded below by **0.50** | on the **only** above-reference point in the corpus the term asserts a 1.84× drop from 0 to 10 mM where Hong measures 1.21× — it **overstates by 1.53×** |

Shipping the one-sided version cost `hong2007` its noise-floor status (shape 14.8 % → 24.0 % against its own 13.0 % replicate scatter) and moved the corpus median 18.9 % → 19.5 %: a refuted constant being paid for in score. **A bound on a term's magnitude is not evidence that the term is harmless inside that bound — only a measurement is**, and the single measurement available refutes the term on both sides. The whole term is therefore refused, and the refusal warning states the 1.53× overstatement explicitly so that a later run cannot read the bound as a licence to switch the half back on.

**What would resolve it.** One experiment: a **BTA-concentration sweep of Cu removal at this pack's own pH 3–4 with H2O2**, at three or more loadings spanning the 1 mM reference. That yields a *steady-state* effective K — measured under abrasion rather than at equilibrium — which is the quantity the term actually needs, and it is the same measurement the pack's deliberately-null `inhibitor_K_ads_L_per_mol` has been asking for.

**Corpus effect.** Median shape **unmoved at 18.9 %**, by design: nothing was fitted, and one axis was reconnected while the constant behind it was refused. `hong2007` keeps its noise-floor status (14.8 % shape against 13.0 % replicate scatter). A median move here would have meant a refuted term was acting on the rate — which is exactly how the one-sided first attempt was caught.

**The four remaining SILENT axes**, pinned by name so that a fifth fails the build: `kenchappa2021 / pad_hardness_shore_d`, `us20110186542a1 / slurry_ph`, and `abrasive_d99_nm` on both `us20190127607a1` blocks. None needs a new constant — D99 legitimately reaches only the defect model, and `w_fe_oxidizer` already declares `ph_response_is_null_over_3_to_6` internally without publishing it. They are silent, not wrong, and that is the next item.

**Enforced by** `tests/test_every_swept_axis_is_connected.py` (10 tests): the unit must be declared and must agree with the key's suffix; a millimolar sweep must arrive as `conc_mM`; the refusal must fire on **both** sides of the reference, must divide its term back out of the factor, and must contain `3283`, the refuting DOI, `1.21`, `18.4`, the declined `183`, the `1.53` overstatement and the unblocking pH range; the corpus median must stay where it was; the refutation arithmetic is **recomputed from the pack's own constants** so it cannot go stale silently; and the scan itself must report no undeclared inert axis. The classifier's failure path is calibrated against the pre-fix situation: a warning about a *different* species must not excuse an axis, and an alias is only an excuse when its partner actually responds.

## 20. The last four SILENT axes now say why they do not move the rate — and one of them is a measured null, not a gap

§19 left four axes inert with **nothing in the output to say so**. That is the dangerous state: from outside, a model that weighed an input and found it unimportant is indistinguishable from a model that never received the input at all, and only one of those is an answer. Silence gets read as a physical claim the model never made.

They had three genuinely different causes, and merging them would have produced one vague apology instead of three usable statements:

| axis | dataset | cause | what the run now says |
|---|---|---|---|
| `pad_hardness_shore_d` | kenchappa2021 | **wrong path** — the key was set on the *pack*, while the GW contact layer reads pad stiffness from the `Pad` object | names the path that works (`pad: {shore_d: …}` or `youngs_modulus_pa`, Qi correlation) |
| `abrasive_d99_nm` | us20190127607a1 ×2 | **correct by design** — the tail feeds the defect proxy, not the rate | states that D50 carries removal while the tail makes scratches, and names `defect_risk` as where D99 does go |
| `slurry_ph` | us20110186542a1 | **a sourced NULL RESULT** — `w_fe_oxidizer` holds `ph_response_is_null_over_3_to_6`, derived from the patent's own matched pH 3 / pH 6 table, and never published it | prints the key, the window and the source, and says whether the queried pH is **inside** it |

**Zero constants were added and no term changed.** The corpus median is therefore required to stay at 18.9 %; a declaration that moves a score is a fit wearing a warning's clothes, and a test asserts the median directly.

**The scope clause is the part that can go wrong silently.** The tungsten pH null covers pH 3–6 only. Outside that window this repository holds no W measurement, so the identical flat response stops being a measured answer and becomes an extrapolation of one — and the warning must change accordingly, or the scope disappears into a reassuring sentence. The window is parsed from the key's own NAME (`…_over_3_to_6`) rather than carried alongside it, so a pack cannot declare one range and be checked against another; an unparseable name falls to the cautious side and reports extrapolation.

**Half a claim is not a claim.** Saying "D99 goes to the defect proxy" is an excuse rather than a description unless the value demonstrably arrives there, so the declaration is tested from both ends: a 4× larger tail must leave the rate bit-identical **and** must raise `defect_risk` (200 → 800 nm gives tail term 1.212 on a 700 nm reference). The same discipline applies to the pad: the recommended route must not be equally inert, so the test requires the Shore D given on the `Pad` object to reach the GW layer and be converted, and — for `sti_ceria`, whose reference pad is inherited rather than measured — requires the contact factor's withholding to be **stated**, which is a separate and already-tested policy.

**Corpus effect.** 91 swept axes, **25 still inert, 0 silent, 0 wiring** (16 declared, 9 aliased). Median shape unmoved at **18.9 %**, leave-one-out 21.3 %. The inert *count* is also pinned: turning silence into a declaration connects nothing, so any change in that count means something else moved.

**What was tried and rejected.** For each of the three causes the obvious "make the control feel responsive" repair was available and was **rejected**: (a) reading `pad_hardness_shore_d` off the pack into the GW layer as a second stiffness route — rejected because two descriptions of one pad would then multiply, which is exactly the 1.9× dropdown bug of §18; (b) letting D99 drive the rate through an added tail term — rejected because no measurement here separates a D99 rate effect from the D50 effect it co-varies with, so the constant would be pure interpolation; (c) extending the tungsten pH null past its measured 3–6 window — rejected because the decision to publish a null must carry the window that was measured, or it becomes an extrapolation dressed as data.

**What would resolve it.** (a) A pad sweep in which Shore D is varied with the same slurry and pack, so a contact factor can be anchored on a measured pad rather than an inherited reference. (b) A dataset holding D50 fixed while D99 varies — the Versum tables move both together, so the tail's rate effect is presently **unknown**, not zero. (c) A tungsten rate measurement below pH 3 or above pH 6 at the patent's chemistry, which would say whether the flat response continues or the null is local.

**Enforced by** `tests/test_silent_axes_now_declare_themselves.py` (9 tests) plus the now-**empty** known-silent allowlist in `tests/test_every_swept_axis_is_connected.py`, so the next disconnected input fails the build instead of being absorbed into the residual and read as missing physics three runs later.

## 21. The ceria Ce3+ axis is closed on IDENTIFIABILITY: surface Ce3+ cannot be separated from particle size in this corpus

Five ceria blocks sit in the corpus's worst tail (netzband2020 49.2 %, dandu2009 31.5 %, son2021 25.6 %, cn109609035b 32.1 %, us9422456b2 25.3 %) and §5/§14 closed the electrostatic pH route for all of them. The mechanism their own authors name is not electrostatics but Cook's chemical tooth: silica is removed through Si-O-Ce condensation at surface **Ce3+ sites**. Surface Ce3+ fraction (theta) is measurable by XPS, so this was the most attractive remaining lead in the whole project — an axis that could have replaced a fitted constant with a **material property**.

**What was measured.** `tools/ce3_residual_probe.py`, on the four questions pre-registered in STATUS.md before it ran.

*Q2 — the input is good, which matters because it rules out the easy excuse.* Netzband & Dunn 2019 (ECS JSS 8 P629, Table I) print theta at three sizes on one laboratory's powders: 58 nm → 12 %, 15 nm → 25 %, 6 nm → 31 %. A power law fits with **R² = 0.962**, theta = 71.3·D^**−0.428** — shallower than the fixed-shell limit m = −1, as a saturating surface population should be. Held out against Hwang et al. 2026 (Polymers 18, 1899, Table 3), a **different laboratory, synthesis and instrument**: predicted 24.4 % vs measured 22.1 % (+10.6 %) and 22.6 % vs 17.7 % (+27.9 %), both inside the pre-registered ±30 % bar. The relation transfers.

*Q4 — and it is still unusable, for a reason no amount of data in this corpus can fix.* theta is reachable **only through D**, and D already drives the rate through the size term. Inside any one block theta is therefore a strictly monotone function of D50: of **9 admissible ceria blocks, theta varies in 3, and in 0 of those is D50 fixed.** Any error reduction credited to Ce3+ here would be the size exponent fitted a second time under a new name — the §18 promoter mistake in different clothes. Three further blocks were **excluded before scoring** because a ceria *pack* is not a ceria *abrasive*: su2011 ×2 (alumina) and wei2026 (colloidal silica) borrow `sic_ceria_h2o2` as a declared placeholder, and alumina has no Ce 3d spectrum to measure. sic2026 cannot testify (`used_for_calibration`).

*Q3 — the sign disagrees too, independently.* Cook's tooth pre-registers a positive slope: more Ce3+ sites, faster removal, so the model (holding theta at the pack's 0.15) must under-predict where theta is high. The three blocks where theta varies measure **−0.302 (R² 0.427), +0.039 (R² 0.001), +0.276 (R² 0.145)** — a sign disagreement, which §14 established is the signature of between-dataset dispersion rather than of a missing shared law. The between-block slope is steep (+2.51) but explains almost nothing (**R² = 0.190**) and is confounded with every difference between the papers; it is recorded so a later run is not tempted to quote it.

**The refit that was rejected.** Fitting `ceria_tooth_gain` or `ceria_tooth_exponent` against theta(D50) across the ceria blocks was available and is **rejected**: with theta a deterministic function of D50, that regression is not identifiable against the existing `abrasive_size_exponent`, so it would move the median by re-describing a term the model already has. The pack's own note already records that this dead end was reached once before from the other direction (judgement #23: amplitude cannot produce the observed ratio, so the problem was never the gain).

**Corpus effect: none, by design.** Zero constants changed, median shape **18.9 %**, leave-one-out 21.3 %, and a test asserts the three `sti_ceria` Ce3+ constants are exactly as shipped. An axis closure that moved the score would be a fit wearing a refusal's clothes.

**What would resolve it.** One ceria dataset that reports **its own XPS Ce3+ fraction** alongside its rates, at fixed particle size — for example a calcination-temperature or dopant series, where theta is varied by synthesis rather than by diameter. That single measurement makes theta identifiable and reopens the axis. The exit is asserted, not merely described: `blocks_with_own_xps_theta` is counted, and the moment it becomes non-zero the closure test **fails on purpose** so the refusal cannot become permanent by accident.

**Enforced by** `tests/test_ce3_axis_is_closed.py` (10 tests).

## 22. The absolute-rate failure is not a mis-anchored constant: four of five failing packs disagree with THEMSELVES

Every closure in §14–§21 was measured against the **shape** score — MAPE after one free multiplicative scale per dataset. That free scale is what makes shape a fair test of a trend, and it is also what makes the corpus median **structurally blind** to being wrong about the rate itself. This entry is the first measurement of that blind spot, and it matters more than any remaining shape point: "the trend is right but the rate is 10× out" is not a usable process prediction.

**What was measured.** `tools/absolute_scale_audit.py`, on four questions pre-registered in STATUS.md before it ran. Of **37 blocks with a comparable absolute scale, 11 miss by ≥3×**, spanning **0.06× to 12.7×**.

> ⚠ The README quotes **9 of 34** for the same bar and both are right. The audit also counts blocks whose SHAPE is unscorable but whose SCALE is still comparable — `ihnfeldt2008` (3.19×) and `miranda2004` (0.31×) are declined on shape because their oxidiser rows fall in a regime the pack gates, yet their absolute rates can still be compared. A dataset the model refuses to rank can still be measured against, and dropping it from the scale count would quietly flatter the harder half of the corpus.

*S1 — there is no missing global factor, and that is knowable immediately.* The miss population is **centred**: median **1.11×**, with **20 blocks under-predicting and 17 over-predicting**. A term absent from every pack would push the whole population one way; this one straddles 1.0. The search for a single universal correction is therefore closed before it starts.

*S2 — THE FINDING. The packs disagree with themselves.* If Kp were merely mis-anchored, every block under a pack would miss the **same** way, and the fix would be one traceable constant per pack. Measured instead, under one shared Kp:

| pack | blocks | internal spread | verdict |
|---|---|---|---|
| `cu_h2o2_bta` | 8 | **222×** (0.06× … 12.7×) | INCOHERENT |
| `oxide_silica` | 7 | 25.5× | INCOHERENT |
| `sic_alumina_kmno4` | 2 | 16.1× | INCOHERENT |
| `sti_ceria` | 6 | 8.0× | INCOHERENT |
| `sic_ceria_h2o2` | 5 | 8.7× | INCOHERENT |
| `w_fe_oxidizer` | 3 | 1.8× | coherent |
| `cu_alkaline_benzenesulfonic` | 3 | 1.6× | coherent |
| `oxide_silica_aminosilane` | 2 | 1.3× | coherent |

No single value of `kp_m_per_pa` can satisfy both ends of a 222× spread. The three coherent packs are the ones where a re-anchoring would even be *meaningful*, and none of them carries a ≥3× failure — so the blocks that need fixing are precisely the blocks a constant cannot fix.

*S3 — and it does not track Kp's provenance either.* The `cu_h2o2_bta` misses all share one `estimated` Kp yet disagree by 222×, while `us8142675b2` misses 0.10× under a **`verified`** Kp. Confidence in the anchor does not predict the miss.

*S4 — one failure may not vote on its own pack.* `gong2024` (0.07×) is `used_for_calibration` for `sic_alumina_kmno4`; its miss is evidence about that pack's *other* blocks, not permission to move the constant to suit it. That is the 13th-run rule applied to scale rather than to shape.

**The refit that was rejected.** Re-anchoring `kp_m_per_pa` per pack to the median observed ratio was available and is **rejected**: on the five incoherent packs it would trade one failure for another (moving `cu_h2o2_bta` to fit `us8501625b2` at 12.7× makes `lai2001` at 0.06× worse by the same factor), and on the coherent packs there is no ≥3× failure to justify touching anything. A constant is the wrong shape of answer to a disagreement *within* a constant's own scope.

**Corpus effect: none, by design.** Zero constants changed, median shape **18.9 %**, leave-one-out 21.3 %.

**What would resolve it.** Blocks under one pack that disagree by 8–222× are not describing one material system, so the question is **what the pack is silently conflating** — different pads, polishers, film variants or abrasive materials sharing one Kp. The next step is a per-block provenance table: for each failing block, the condition its pack's Kp was back-calculated from and the distance between the two. Where the conflated variable is identifiable and sourced, the answer is a pack **split** (the precedent is `oxide_silica_aminosilane` earning its own split, which is why it is coherent today); where it is not, the answer is to declare the block out of the pack's scope rather than to average over it. **Deliberately *not* a gate**: these blocks still score, because hiding them would restore exactly the blindness this entry exists to remove.

**Enforced by** `tests/test_absolute_scale_is_not_one_constant.py` (7 tests).

## 23. Nine of the eleven absolute-scale failures were already identified — in prose the scorer cannot read

§22 ended by asking what each failing pack is **silently conflating**, and said the answer would be a per-block provenance table. `tools/kp_provenance_table.py` is that table, and its result is not the one the item anticipated.

**The finding.** Of the eleven blocks missing the absolute rate by ≥3×, **nine already state their own cause in their dataset header** — that the `pack:` field is a placeholder, or that the block sits outside the window the pack's Kp was back-calculated in, or that the absolute value carries a named systematic bias. One more (`gong2024`) is disclosed inside the pack's own `kp_m_per_pa` note. Only **one** is genuinely unexplained. Nothing was missing; it was **never machine-readable**, so every run since has re-measured the same misses as though their causes were unknown.

| block | scale | what the pack conflates |
|---|---|---|
| `lai2001_cu_alumina` | 0.06× | neutral pH 7 alumina, **no oxidiser or complexant**, scored against an acidic H2O2/glycine/BTA Kp |
| `gong2024_4hsic` | 0.07× | Kp anchored via a secondary citation, assuming an alumina loading the source never states |
| `us6918821b2_cu` | 0.08× | **UNIDENTIFIED** — the patent states no slurry composition |
| `us8142675b2_pt` | 0.10× | the FILM: platinum through an oxide pack (`film: other`; there is no Pt pack) |
| `us20190127607a1_teos` / `_hdpoxide` | 0.19× / 0.24× | ceria-**coated-silica composite** particles, which the pack's Kp note excludes by name |
| `miranda2004_cu` | 0.31× | a 4-inch benchtop tool against a 200 mm damascene Kp |
| `ihnfeldt2008_cu` | 3.19× | 1.0 psi, **below** the 2–3 psi window the Kp was anchored in |
| `liang2026_sic` | 4.57× | CuxO-CeO2/Al2O3 composite abrasive at pH 7, outside the pack's pH 9–11 window |
| `wei2026_sic` | 9.68× | colloidal **silica** through a pack that declares `reference_abrasive: ceria` |
| `us8501625b2_cu` | 12.68× | inhibitor is **1,2,4-triazole, not BTA**, and loading is 18× below the pack reference |

**Why this is not an excuse, tested two ways.** "Out of scope" is the cheapest sentence available, so the claim is checked rather than asserted:

1. **The prose does not predict the miss.** 17 comparable blocks carry placeholder/rank-only prose and **9 of them land inside 3×**; 20 blocks carry none and **3 of them fail**. Median miss factor 2.09× with the prose, 2.00× without. A post-hoc excuse would mark the failures and nothing else — this marks which *question* a block can answer.
2. **The prose predates the measurement.** Every quoted line was committed 2026-09-15 … 2026-09-24 (`git blame`); the audit that first measured these misses is 2026-09-27.

**The one quantitative identification, and it could have failed.** When `sti_ceria`'s Kp was re-derived from four bare-ceria datasets, the two ceria-coated-silica blocks were excluded as a different abrasive and the value they imply (**2.3e-14** against the pack's **1.09e-13**) was written into the note. That exclusion is a prediction with no free parameter: those blocks must under-predict by **0.211×**. Measured: **0.188× and 0.235×** — they bracket it. Those two failures are not model error; they are the pack's own statement being scored as if it had not been made.

**The split that was rejected.** Every ruling is marked **not splittable**, and the reason is the same in each case: the anchor a new pack would need does not exist independently of the blocks it would then be scored on. A composite-abrasive Kp can only be back-calculated from the two composite blocks; a Pt Kp from the single Pt block; a neutral-alumina-Cu Kp from the single such block. That is the 13th-run rule (a dataset may not testify for the constant fitted on it) applied to absolute scale. **Zero packs were split and zero constants changed.**

**Corpus effect: none, by design.** Median shape **18.9 %**, leave-one-out 21.3 %.

**What would resolve it.** Two different things, and conflating them is the trap:
- For the nine identified blocks — a **second dataset in the same material system** from an independent source (a composite-abrasive oxide polish outside US20190127607A1; a second Pt block; a second silica-on-SiC block). Then a split has an anchor that is not its own scorecard. Until then, identification is the whole of the available answer.
- For `us6918821b2` — nothing in this repo. The patent withholds the composition, so no comparison to the anchor exists at any effort.

**Enforced by** `tests/test_kp_provenance_is_identified.py` (18 tests), including an adjudication obligation: a new ≥3× block fails the suite until its cause is named or explicitly recorded as unidentified.

## 24. The supply axis was never DECIDED, and the obvious fix would have silently halved a third of the corpus

The Luo-Dornfeld decomposition here answers three measurable questions to get both abrasive exponents (`n_C = p(1-alpha*chi)`, `n_d = -q(1-alpha*chi)+beta`). The third — does the gap admit one layer of particles or several — is answered from `gap_m / d_p`, and the solver supplies `pad_wafer_gap_m`: a key **no pack declares and no caller sets**, listed in `tests/test_pack_key_wiring.KNOWN_NON_PACK_KEYS` as a "solved quantity". So the decision was **never made in any run of this corpus**. The inherited layer took its `None` branch, returned `p=1, q=2`, graded itself `estimated`, and every result warned that the supply geometry "was not determined from data". That warning was false, and had been false in every run ever scored here.

**The obvious fix is a bug, and that was established BEFORE wiring anything.** The same run already solves a mean fluid film `h` and publishes it under `slurry_supply`; one line would feed it to `gap_m`. But `decide_supply` means the clearance where a particle is *loaded* (pad asperity summit to wafer), while `h` averages over grooves and un-contacted valleys. The two coincide only when asperities carry the load — which is exactly `lambda = h/sigma < 1`, a quantity the run also already computes.

**Measured** (`tools/supply_gap_probe.py`): all 49 runnable datasets are boundary-lubricated, `lambda` 0.002–0.148, every one below 1 by at least 6.7×. So the monolayer verdict holds corpus-wide. **But `h/d` exceeds `decide_supply`s 1.5 threshold on 20 of those 49** (up to 26× on `son2021`). The naive wiring would have cut `p` from 1.0 to 0.46 and halved the derived concentration exponent on a third of the corpus, on the strength of a length measured in the wrong place.

**And it would have been nearly invisible.** `tools/supply_gap_reachability_probe.py` forces the gap to 10× the diameter and re-runs the shipping solver: **only 5 of 49 predicted rates move at all**, because each packs own measured exponent overrides the derived one inside `mechanical_factor`. A wrong number that changes almost nothing cannot be caught by the median, by any dataset score, or by a reachability census keyed on the rate. This is the same shape as §20s `scratch_threshold_nm` finding — the hard-coded value happened to equal the pack value, so nothing was wrong and nothing could ever be found wrong.

**What was adopted, and what was rejected.** `models/luo_dornfeld._supply_from_lubrication` decides the axis from the lubrication regime, with **zero new constants and zero change to any exponent** (`p=1, q=2` either way). Feeding the mean film to `gap_m` was **rejected** for the reason measured above. The gain is honesty, not accuracy: the confidence floor is released and the warning now names only the axes actually open. Corpus median **18.2 % unchanged**, which is the correct outcome and is asserted directly, so a future change that moves the exponents under this banner fails.

**The limit this records.** A closure that fires everywhere is not a closure: `lambda >= 1` (mixed / full film) deliberately gets **no verdict**, because once load is partly hydrodynamic the clearance at a loaded site is no longer pinned to the particle. This corpus cannot test that branch — every dataset in it is boundary — so the mixed/full-film case is **deliberately *not* a gate** and stays open. **What would resolve it**: a dataset run at high enough speed and viscosity, or low enough pressure, to reach `lambda >= 1`; only then does the multilayer branch become falsifiable here rather than merely unreachable.

**Enforced by** `tests/test_supply_axis_decided_from_lubrication.py` (7 tests), including the guard that matters: no boundary-lubricated run may report `p != 1`, which fires the moment anyone wires the mean film into the contact gap.

## 25. The load-sharing axis (chi) is closed on IDENTIFIABILITY — and the "last open axis" was never chi, it is a MEASURED alpha being thrown away

STATUS.md named `chi` the only remaining undecided question of the Luo-Dornfeld decomposition (`n_C = p(1-alpha*chi)`, `n_d = -q(1-alpha*chi)+beta`) after §24 closed the supply axis, on the evidence that every scored run reports `abrasive_regime.confidence == 'unverified'`. The 29th run asked the §24 question of chi — *is it reachable before it is wired?* — and both halves of the answer contradict that reading.

**Measured, part 1: chi's only input carries no information.** `decide_chi` takes `m`, the pressure exponent of the real contact area (`A_r ~ P^m`), which `solver._abrasive_hook` differentiates numerically out of the GW layer between `P/2` and `2P`. Across all 49 runnable datasets `m = 1.0000` with a spread of **1.3e-10** — every pad, every pressure, every film. That is not a measurement that happens to agree; it is the analytic property of the exponential summit-height distribution the GW layer uses, for which real area is linear in load by construction. Deciding chi from it would grade a structural constant as an observation, which is the third instance in this repo of a candidate diagnostic turning out to be the operating point or the model in disguise (BLOCKED #1: `lambda = V/p`, `summit_saturation = 0.00739·P`).

**Measured, part 2: chi does not reach the rate.** Forcing chi to 0.5 and to 0.0 and re-running the shipping solver moves the prediction on **5 of 49** datasets; 44 are inert, because `mechanical_factor` prefers each pack's own MEASURED concentration and size exponents over the derived ones. Even a correct chi could therefore own almost none of the corpus error.

**The finding the probe was not looking for, and it is the larger one.** Of the 49 runs, **33 have a contact branch decided** by the pad-limited load criterion (11 plastic, 22 transition) and `resolve_regime` **discards that verdict**: `alpha*chi > 1` breaks the structural bound `0 <= 1-alpha*chi <= 1`, so the code reverts to the inherited elastic pair and grades the regime `unverified`. The other 16 never decide alpha at all. So the `unverified` string is a report about **alpha in every single run** — in two thirds of them about a measured alpha being thrown away by its collision with a chi that carries no data.

**What was rejected, and it was priced first.** The symmetric resolution — keep the measured alpha, clamp chi to the bound `1/alpha` — looks strictly better on provenance. Scored through the real scorer it moves the corpus median **14.82% -> 14.82%** (mean 22.03 -> 22.12%, i.e. very slightly worse). It is **rejected** because it would fit the one quantity in the pair that is not adjustable evidence: with `m` pinned at 1, `chi = 1` is what the contact model states, and bending it to 2/3 to rescue alpha buys nothing measurable while converting a structural constant into a free handle. Nothing was adopted and no constant was added; **corpus median unchanged**, which is the correct outcome for a measurement run and is asserted directly.

**What would resolve it.** Not more data on chi — a pad model with a non-exponential summit-height distribution (Gaussian or measured), under which `m` would vary with pressure and pad state and chi would become a real axis. And separately, for the veto: a **measured concentration sweep on a film whose contact branch is plastic**, which is the one observation that could say whether `n_C` there is genuinely near zero (as plastic + full load sharing implies) or whether the load sharing is partial. **That observation EXISTS here** — `tools/plastic_branch_answerability_probe.py` finds 5 plastic/transition datasets carrying a >=3-level abrasive loading sweep (`jani2025_cu_rsm_composition_heldout` plastic at 1/3/4/6 wt%, `us9499721b2` 6 levels, `us6564116b2` 5 levels, `yang2023_quartz_ceria_L25` 5 levels, `carbide2023_L9` 3 levels) — so the veto is **falsifiable on this corpus**, and `us9499721b2`'s measured log-slope of +0.15..+0.53 already sits badly with the `n_C ≈ 0` that plastic plus full load sharing requires. That is the next run's target, not chi. **A caution recorded with it**: this probe's first cut read only the condition's top level, missed that swept values live under `overrides:`, and reported ZERO such datasets — a plausible negative that would have closed the line of work. In this repo a negative result retires a question, so it is the most expensive kind of reader bug; suspect the reader before writing the conclusion.

**Enforced by** `tests/test_chi_axis_closed_on_identifiability.py` (4 tests): the exponent's corpus-wide constancy (fails if a future pad model makes chi informative — the intended exit condition), the accounting that every `unverified` grade is one of exactly two alpha causes with the veto in the majority, the zero price of the rejected alternative, and the reachability ceiling. Probe: `tools/chi_reachability_probe.py`.

## 26. The alpha-chi veto is a statement of SCOPE, not of ignorance — and the substituted exponent is the one the data support

§25 found that `resolve_regime` measures a contact branch in **33 of 49** corpus runs and then discards it: the plastic `alpha = 3/2` against the measured `chi = 1.0` gives `alpha*chi = 1.5 > 1`, breaking the structural bound `0 <= 1 - alpha*chi <= 1` that the exponent relations rest on, so the code substitutes the inherited elastic pair and grades the regime `unverified`. Every such run then warned that "the elastic/plastic branch **was not determined from data**". That sentence was false in all 33, and it had been false in every run ever scored: alpha *was* determined, and then refused.

**The substitution is not neutral, which is what makes it testable.** It asserts

    n_C = p * (1 - alpha*chi) = 1 * (1 - 2/3) = +1/3

on every vetoed run, against the `-0.5` the plastic branch would give if the bound were simply lifted. So the veto is a choice between two numbers, and the corpus can score it.

**Measured** (`tools/plastic_branch_exponent_probe.py`, zero fitting in the model, zero constants touched): every iso-condition abrasive-loading series on a vetoed branch, log-log slope of the **measurements** with all other process axes held —

| slope | SE | r2 |
|---|---|---|
| +0.145 | 0.015 | 0.96 |
| +0.303 | 0.052 | 0.89 |
| +0.350 | 0.059 | 0.92 |
| +0.534 | 0.108 | 0.89 |

Median **+0.350** against the substitution's **+0.333** and the literal plastic **-0.500**. 4/4 closer to the substituted value, 3/4 within 2 SE of it, and **not one negative slope**. The measurements therefore refuse the literal plastic exponent and land on the one the veto substitutes.

**The decision.** The refusal stays exactly as it is — no constant, no exponent, no pack changed, corpus median **unmoved at 18.2%** — but it is now reported as what it is: this combination is **outside the `N_a·F^alpha` decomposition's validity**, and the elastic pair is the supported number there. The `unverified` grade is kept (the regime genuinely is not verified) but the two populations it covers are now distinguishable through `abrasive_regime.branch_outside_scope`, so a reader can tell "alpha was never decided" (16 runs) from "alpha was decided and is out of scope" (33). A zero median change is the correct outcome for an honesty fix and is asserted directly; had it moved, this work would have touched the physics.

**The scope of the evidence, stated rather than implied.** All four ladders are on the **transition** branch and all four come from **one dataset** (US9499721B2, silica on TEOS). No plastic-branch dataset in this corpus yields an iso-condition loading ladder at all — the plastic runs are entirely copper, and copper's loading sweeps sit inside RSM / L-array designs where no other axis is held, so nothing survives the grouping. The 11 plastic runs therefore **inherit** this verdict from the shared decomposition; they do not measure it. **What would resolve it**: a copper abrasive-loading ladder at frozen chemistry, pressure and speed. **What would reopen the whole limit**: any vetoed-branch ladder with a slope at or below zero, which is the observation the literal plastic exponent predicts.

**Enforced by** `tests/test_vetoed_branch_is_a_scope_claim.py` (7 tests): the run says "outside this decomposition's validity" and no longer says "was not determined from data"; the refusal names both its evidence and its exit condition; the supporting slopes are **re-derived from the dataset files at test time**, so a future dataset with a non-positive vetoed-branch slope fails the suite instead of quietly contradicting a memo; both caveats (transition-only, single-dataset) are asserted to be *facts* and fail the moment a plastic ladder or a second source appears; the two `unverified` populations both still exist, so the flag cannot have been set too widely; and alpha and `n_C` are pinned to the substituted values, so the honesty fix provably moved no number.

## 27. The abrasive-swap detector is inert in every scored run, and the one pack it could have fired on was lying about itself

`slurry/abrasive_effects.py` exists because `slurry.abrasive.kind` once had no effect on the predicted rate at all — silica, ceria, alumina, zirconia and diamond returned a bit-identical 1601 A/min on the same recipe. The module resolves the abrasive actually used, compares it against the pack's `reference_abrasive`, and on a mismatch **withdraws the pack's abrasive-scoped exponents** (they were fitted for a different material, and the measured exponents split by abrasive without even sharing a sign: silica −0.13, alumina +0.28, ceria +1.00) and refuses to anchor the absolute scale.

**Measured** (`tools/abrasive_declaration_probe.py`): running the shipping solver over all 49 corpus datasets returns `kind = None, reference_kind = None, matches_reference = True` in **49 of 49**. The module is inert in 100% of scored runs, because `_recipe_for` builds each recipe from a dataset's `overrides:` keys and **no dataset declares which abrasive it used**. `matches_reference: True` is therefore not a finding but a default — and it was being asserted for datasets whose own headers say in prose that the abrasive is *not* the pack's ("the abrasive here is alumina/zirconia, not ceria"; "the abrasive is a CeO2-LaOF composite, not plain ceria"; three files carry the literal word `PLACEHOLDER`).

**The defect this uncovered, which is the more important half.** `sic_alumina_kmno4` declares `abrasive: alumina` — with two citations, an α-alumina density, and a Kp anchored on Wang 2021 / US20220315802A1, both alumina — but never declared `reference_abrasive`, so that key was **inherited from its ceria parent** `sic_ceria_h2o2`. The pack named two different materials in its two identity keys, and the swap detector reads the inherited one. Nothing failed, because nothing compared them *and* the detector could not fire anyway. It became visible only on declaring the abrasive: doing so on the pack's **own** dataset (entegris2022, an alumina loading series) scored as alumina-into-a-ceria-pack, withdrew the pack's **measured** loading exponent (−0.406, Entegris Table 1, n=5) in favour of the derived +1/3, and took that dataset 14.1% → **101.5%**. This is the third instance of one inheritance accident in this same pack family (after `sti_ceria` inheriting silica's `C_half` and `sic_ceria_h2o2` inheriting the oxide pH optimum): **a child that differs from its parent in MATERIAL silently keeps every key that names the material.**

**The decision.** `reference_abrasive: alumina` is declared on `sic_alumina_kmno4`, citing the two sources its own `abrasive` key already carried. **No measured value changes and no constant is added** — the pack is made to state one identity instead of two. Corpus median is **unmoved at 18.2%**, which is the correct outcome and is asserted: the detector is still inert corpus-wide because no dataset declares an abrasive, so any movement would have meant an identity fix had touched the physics.

**What was deliberately *not* done.** The datasets were **not** given abrasive declarations. The probe prices that change and the price is not obviously positive: of the 22 datasets whose abrasive is quotable from their own header, 19 are unchanged, 2 improve (su2011 ×2, −0.4 / −0.3 pp) and **1 worsens sharply** (wei2026, colloidal silica scored through the ceria pack `sic_ceria_h2o2`, 3.2% → 11.7%). That last one is not a bug — it is a *genuine* swap, the file says `PLACEHOLDER` in its own `pack:` line, and the detector is doing exactly what it was built to do: refusing exponents fitted on ceria. The honest reading is that those three SiC files are mis-packed, and correcting a dataset's pack is a separate decision from declaring its abrasive; doing both at once would make the result unattributable. Five further datasets are left undeclared **on purpose**: four use composite particles whose composition the source never gives as a fraction (ceria-coated silica ×2, CuxO-CeO₂/Al₂O₃, CeO₂-LaOF) and resolving them onto a parent material would assert a composition nobody measured, and one (us6918821b2) has its ceria **in the pad**, not the slurry.

**What would resolve it.** Retargeting the three SiC placeholder datasets onto packs that match their abrasive, after which declaring the abrasive corpus-wide becomes a scoreable change rather than a mixture of a fix and a mis-pack. A canonical database key for ceria-coated silica, with a measured composition, would unlock two more.

**Enforced by** `tests/test_pack_abrasive_identity_is_consistent.py` (16 tests): every pack's two identity keys must resolve to one material, with the subject list **re-derived from `available_packs()` at test time** so a new pack — or a new child of a ceria pack — is checked with no edit to the test; a guard that fails if too few packs actually declare both keys, so the check can never pass by skipping everything; the specific regression named, including the requirement that it be fixed by *correcting* the key rather than deleting it (deletion would restore the undetectable state); and the parent asserted untouched, so the fix cannot have been applied to the family instead of the child. Calibrated against the bug: reverting the pack edit fails 2 of the 16.

## 28. The distance to the completion bar is ONE dataset, and what it needs is a curvature the model structurally cannot produce

**Why this entry exists.** STATUS had recorded the remaining work as "a 3.2 percentage point gap" between the corpus median (18.2%) and the redefined completion bar (15.0%), and every session since has planned against that framing — searching for a term worth ~3 points spread across the corpus. The framing is wrong, and the error is in the statistic, not in the physics.

**The headline median is a COUNTING statistic.** `tools/score_report.py`, the README and the definition-of-done test all use the upper median `sorted(errors)[n//2]`. That is `<= B` exactly when at least `n//2 + 1` datasets score `<= B`. With 46 scored datasets and 23 already at or under 15.0%, the requirement is 24 — so **one dataset must cross, and the corpus is otherwise already there** (`tools/median_crossing_probe.py`). Two consequences follow immediately and neither was visible in the old framing: improving any dataset that is above the median but still above the bar moves the headline by **exactly zero**, which is where several sessions' effort went; and the worst blocks in the corpus (`sic2023_shear_rheological_L9` 71.2%, `mo2026_double_sided_L16` 69.5%) are irrelevant to completion no matter how much they improve.

**The binding dataset, and the single row inside it.** The nearest block above the bar is `liang2026_4hsic_ceria_composite_h2o2_conc` at **18.17%**, 3.2 points over. Its four rows score **3.8 / 4.3 / 6.9 / 57.7%**: three of them are already far better than the bar and the headline for the entire project is decided by **one row** — the lowest abrasive loading in the file, 1 wt% against a pack whose reference composition is 5 wt%.

**The obvious explanation is measured and REJECTED.** A single badly over-predicted dilute row invites the reading "the model over-predicts dilute slurries everywhere", which would be a missing shared term. It is not there. `tools/low_loading_residual_probe.py` reproduces the scorer's own shape fit on all 11 loading-varying datasets (196 rows) and pairs each row's signed residual `ln(pred/meas)` with its loading **relative to its own pack's reference**, because an absolute 1 wt% is a deep extrapolation for a 20 wt% pack and the reference itself for a 1 wt% pack. Below reference: **81 rows, 36 over-predicting, median 0.97x**. That population is centred; there is no signed low-loading residual, and this reading is closed.

**What IS shared is CURVATURE, and the model cannot produce any.** The concentration response in `mechanical_factor` is a single power law `rate ∝ C^n`, whose local log-log slope is by construction the same at every loading. The corpus's ladders are not. `tools/concentration_curvature_probe.py` groups rows that differ **only** in `abrasive_wt_pct` (identical pressure, both speeds, and every other override) into iso-condition ladders of at least three loadings and measures the local slope between consecutive levels:

| | count |
|---|---|
| iso-condition ladders (>= 3 loadings) | **18**, across 7 datasets |
| flattening (slope falls as loading rises) | **12** |
| steepening | 6 |
| median curvature (last slope − first slope) | **−0.194** |
| ladders scored against the model's own curvature | 14 |
| **still flattening after the model** | **11** |
| **median residual curvature** | **−0.296** |

The model's own curvature is `|curv| < 0.01` on **every** ladder — it is a pure power law, as designed — so essentially the entire measured bend is residual. The binding Liang row is this effect, not a special case: its measured slopes are **+0.532** (1→5 wt%) then **+0.244** (5→9 wt%) while the model reports +0.226 / +0.234, i.e. the model is right where the pack is anchored and wrong far below it. This is the signature of curvature, **not of a wrong exponent** — re-fitting `abrasive_conc_exponent` trades the 1 wt% row for the 5 and 9 wt% rows and cannot fix both.

**Why this is a derivation target and not a fitting opportunity.** An all-one-sign residual across seven independent datasets is a missing term with a **known sign**, which is the one situation this repository treats as worth deriving. It is equally the argument that would be used to restore `abrasive_conc_half_wt_pct`, and that must not happen: limit 14's second amendment withdrew it from every pack on **necessity** (NEEDED 0 / HARMFUL 1 / redundant 6), and re-adding it here would fit the curvature using the very constant whose own residual once made this axis look like a law. The admissible version derives the saturation scale from geometry the model already carries — the monolayer areal density `N ∝ φ/d²` against the real contact area the GW layer already computes, i.e. the loading at which particles stop being able to occupy fresh contact — introducing **no new free constant**. That derivation is the next piece of work, and it is not done here: this entry records the target and the evidence, not a fix.

**What would resolve it, and what would reopen it.** What would resolve it: deriving the saturation scale from the monolayer/contact-area geometry above, so the curvature is produced with no new free constant. What would reopen it: a signed dilute residual returning (the rejected reading), the flattening majority disappearing, or the model acquiring curvature of its own — each of which fails a test below rather than quietly ageing into a stale memo.

**Enforced by** `tests/test_the_gap_to_the_bar_is_one_dataset.py` (6 tests), all re-measured from the shipping solver and the dataset files at test time, never from numbers copied out of this page: the gap stays a small integer number of datasets and the bar is **imported** from `test_definition_of_done.py` rather than retyped, so a re-derived bound cannot leave this entry asserting a stale one; the binding dataset stays close to the bar; the dilute population stays centred, with a non-vacuity guard so a probe that collects nothing cannot "pass"; the model's curvature stays below 0.05 on every ladder, so a future curvature term fails loudly instead of leaving this claim silently false; the flattening majority holds across at least three **distinct** datasets, because one curved ladder plus one constant is interpolation of a single experiment; and the withdrawn constant is asserted absent from every pack, which is the exit this limit must not be taken through.

### ⚠ AMENDED same day: the derived saturation §28 named as "the next piece of work" is PRICED AND REFUTED

§28 closed by naming the admissible fix: derive the saturation scale from geometry the model already carries, so the curvature appears with **no new free constant**. That derivation has now been written down, priced, and **rejected on measurement** — it is recorded here rather than attempted again.

**The derivation.** Particles remove material only where they are loaded, and they are loaded only inside the real pad–wafer contact. The Luo-Dornfeld layer supplies a monolayer areal count `N_supply ∝ φ/d²` per unit *nominal* area (`particles_per_unit_area`), while the number of monolayer sites lying inside the real contact is `N_sites ∝ (A_r/A_0)/d²`, with `A_r/A_0` the GW area fraction the contact layer already computes from the pad's own asperity statistics. The diameter cancels exactly and the occupancy is a ratio of two quantities the model already holds:

    theta = phi / (A_r / A_0),     N_active = N_sites * (1 - exp(-theta))

Normalised to the pack's own reference composition at the same pad and pressure, the correction to a prediction is `[((1-e^-θ)/θ) / ((1-e^-θ_ref)/θ_ref)]^n_eff`, which is **exactly 1.0 at every pack's reference composition** (the invariant every factor here must satisfy) and bends the response downward as loading rises. No constant is introduced.

**It is reachable — that was checked first** (`tools/monolayer_occupancy_reachability_probe.py`, 375 rows / 38 datasets, `A_r/A_0` read from the same `pad_state` the solver's kappa hook uses). The GW area fraction runs 4.6e-4 … 6.4e-3 (median 1.7e-3, spread 13.8x) and θ runs **0.018 … 97.9, median 4.9**, spanning up to 400x within a single pack. θ therefore crosses order 1: the filling law is neither linear everywhere (which would reproduce the present power law and change nothing) nor saturated everywhere (which would flatten every ladder). On reachability grounds this derivation deserved to be tried.

**Priced before wiring, and refused** (`tools/derived_saturation_counterfactual.py`, which applies the correction to the shipping model's own per-row predictions and measures `n_eff` **by perturbation** so a pack carrying a measured exponent is priced with the exponent it actually applies):

| | |
|---|---|
| datasets touched | 11 |
| improved / worsened | **3 / 8** |
| corpus median | **18.17% → 18.95%** |
| the binding dataset (liang2026) | **18.2% → 30.5%** |
| entegris2022 | 14.1% → **53.0%** |
| gong2024 (the one large win) | 24.9% → **12.3%**, scale 0.070 → 0.048 |

The term makes the **binding** dataset — the entire reason §28 exists — substantially worse, and moves the corpus median the wrong way. A physically clean, constant-free derivation that is reachable and has the right qualitative sign still does not describe this corpus.

**What this does and does not license.** It does *not* license restoring `abrasive_conc_half_wt_pct` under a new name, and it does not license searching functional forms until one scores: trying filling laws until a median drops is fitting with extra steps, and the derivation's failure is information, not an obstacle to route around. The honest reading is that loading-response curvature in this corpus is **not** set by monolayer site filling against the GW contact area. The one large win (gong2024, an alumina/KMnO₄ L25 whose absolute scale is 0.07x and therefore already flagged) is not evidence for the term; it is a block whose scale is so far off that almost any multiplicative bend improves its trend.

**What would resolve it** remains unchanged in kind but is now narrower: a mechanism that makes the response curve which is *not* site filling — agglomeration above a loading threshold (which would make the curvature depend on zeta potential and ionic strength, both of which the packs carry and neither of which the loading term reads) is the standing candidate, and it is testable because it predicts curvature that varies with dispersant, not merely with loading. **What would reopen the rejected derivation**: an `A_r/A_0` that comes from measured asperity statistics rather than the Qi correlation, since the refutation above inherits whatever error that correlation carries into θ.

**Enforced by** the same `tests/test_the_gap_to_the_bar_is_one_dataset.py`: its "the model produces no concentration curvature at all" test is what keeps this refusal honest — if a future session wires a curvature term, that test fails loudly and this amendment must be re-measured rather than quietly inherited.

## 29. The load-sharing ONSET has the sign §28's derivation lacked, repairs the binding dataset — and is still refuted, by the data rather than by the median

§28's amendment rejected a monolayer-occupancy saturation built on `theta = phi / (A_r/A_0)` and named the next candidate as something other than site filling. Before going there, this session asked a different question: **was theta refuted, or was its placement?** The answer is the placement — and the replacement is still refused, on evidence that does not run through the corpus median at all.

**The sign error was knowable without computing anything.** Session 32 applied theta to the particle COUNT, `N_active = N_sites (1 - e^-theta)`, making `N` sub-linear in `C`; raised to the sub-unity load-sharing exponent the model applies (`n_eff ~ 0.23`), that correction *raises* the dilute prediction. The measurements want the opposite: on the binding dataset the measured log-log slope is **+0.532** from 1→5 wt% and **+0.244** from 5→9 wt%, i.e. steeper than the model at dilute and in agreement above the pack reference. A term that flattens the dilute end cannot repair a ladder that is too steep to be flat.

**The placement with the right sign, and no new constant.** `core/regime.py` resolves the load-sharing fraction `chi = 1.0` on all 49 datasets with a spread of 1.3e-10 — an analytic property of the exponential GW summit distribution, not an observation (§21, §25). `chi = 1` asserts that particles intercept the whole applied load at *every* loading, which cannot hold as `C → 0`: with no particles in the contact the pad touches the wafer directly. Poisson occupancy of the contact sites gives the covered fraction directly,

    chi(theta) = 1 - exp(-theta),     theta = phi / (A_r / A_0)

and with `N` particles each indenting under the load they actually carry, `rate ~ N^(1-alpha) (chi L)^alpha`, so relative to the pack's own reference composition the correction is `[(1-e^-theta)/(1-e^-theta_ref)]^alpha`. Here `alpha = 1 - n_eff` is **read off the shipping model per row by perturbation**, because the model already applies `n_eff = 1 - alpha*chi` with `chi ≡ 1`. It is **exactly 1.0 at every pack reference**, tends to the model's own exponent for `theta >> 1`, and tends to a LINEAR dilute response — the measured direction.

**One pricing bug found on the way, which the §28 run also carried.** The solver normalises against `abrasive_ref_wt_pct` (`solver.py:546`), which a *row* may override; both counterfactuals initially read the pack's own `abrasive_wt_pct`. On `us20110186542a1` that put `theta_ref` at a composition the shipping factor never used, and the correction stopped being 1.0 where the model is anchored — absolute scale 1.87x → **17.5x**. Correcting it restores 1.90x. A reference-normalised factor is only as good as its reference lookup.

**Priced** (`tools/load_sharing_onset_counterfactual.py`, 11 datasets, 8 inside the premise):

| | |
|---|---|
| improved / worsened (in premise) | **5 / 2** |
| **the binding dataset (liang2026)** | **18.2% → 1.9%** |
| corpus median | 18.17% → **18.95%** |

The term **repairs the dataset the entire completion criterion hangs on**, by an order of magnitude, and the headline still moves the wrong way. That is §26's counting-statistic lesson arriving from the other side, and it is the reason the median could not settle this question either way.

**So it was settled on the data instead** (`tools/load_sharing_slope_probe.py`, 51 iso-condition adjacent loading pairs, 47 in premise, nothing fitted — there is no free parameter to fit). The derivation forces the local slope `s(theta) = (1-alpha) + alpha·theta·e^-theta/(1-e^-theta)`, which **must approach +1 as theta → 0**. Measured:

| | |
|---|---|
| spearman(theta, measured slope) | −0.249 (right direction, weak) |
| **theta < 1** | n=9, median slope **+0.277** |
| theta ≥ 1 | n=38, median slope +0.231 |

The dilute group is supposed to be near +1.0 and clearly above the dense group. It is at +0.277, statistically indistinguishable from the dense group. **The corpus does not show the load-sharing onset.**

**The refutation's own weakness is stated rather than hidden:** all nine `theta < 1` pairs come from a **single** source, one patent's diamond series at 0.01–0.04 wt%. So this says *this corpus gives no support*, not *the physics is wrong* — the same distinction §21 draws between an unidentifiable axis and a false one. The rejected term is also the one that fixes the binding dataset, so this is a refusal that costs something, which is precisely when the temptation to wire it anyway is strongest.

**What would resolve it:** a second dilute-loading ladder (`theta < 1`) from a different abrasive system, at fixed pressure, velocity and chemistry. One dataset decides this axis today, and `test_the_dilute_evidence_rests_on_a_single_dataset` fails the moment a second arrives — the refutation is built to expire rather than to age into fact. **What this does NOT license:** trying further filling laws until a median drops (fitting with extra steps, §28), or wiring the term on the strength of liang2026 alone (§22: a lone large win is not evidence).

**Enforced by** `tests/test_load_sharing_onset_is_refuted_by_the_data.py` (8 tests, all re-measured from the solver and the datasets at test time — no number copied from this document). It pins the structural invariants (factor ≡ 1.0 at reference, concave bend, no free argument), the fact that the median verdict alone would NOT have settled it, the dilute-slope refutation, its single-source weakness, and that the premise filter genuinely excludes datasets in both directions so the reading cannot be an artefact of an empty filter.

> **⚠ SUPERSEDED IN PART — see §30.** The exit condition above FIRED. A second dilute ladder arrived, the general refutation did not survive it, and what remains is a narrower refusal about the extreme-dilute band. §29 is kept in full because the reasoning that produced it is sound and the way it failed is the lesson; read §30 before acting on anything here.

---

## 30. §29's exit condition fired, and the refutation did not survive it — the cut was at a value the corpus had no data near

§29 refused the load-sharing onset `chi(theta) = 1 - exp(-theta)` — a zero-constant term that repairs the binding dataset from 18.2% to 1.9% — because the measured dilute slope did not approach +1. It also named its own weakness and built a test to expire: all nine `theta < 1` pairs came from one diamond patent, and `test_the_dilute_evidence_rests_on_a_single_dataset` was written to FAIL when a second dilute system arrived. **It arrived, and it failed.**

**The new evidence.** `us9422456b2_teos_silica_dilute_loading` — US 9,422,456 B2 Example 1 / Table 1, a printed patent table: 54 nm aminosilane core-shell colloidal silica at **0.5 / 1.0 / 2.0 / 3.0 wt%**, each measured at 4.0 and 5.0 psi, pH buffered at 4.7, one tool, one pad, one speed, one flow. Verified value-by-value against the cached patent text in the session that added it, not copied from a summary. The fumed-silica "Control" row was **excluded**: it is a different abrasive morphology, and putting an abrasive swap inside a loading ladder attributes a morphology change to concentration (§27).

**The refutation was an artefact of the cut, and the cut was inherited from a corpus that had nothing near it.** §29 split at `theta = 1`. The new ladder's most dilute pair sits at `theta = 1.38`, where `chi = 0.75` — a quarter of the load is still going to bare pad, unambiguously inside the regime the law makes a claim about — and it lands in the `>= 1` bucket, averaged with pairs at `theta = 18` where the term does essentially nothing. When the only datum was at `theta ≈ 0.03`, two orders below the cut, the knife edge was harmless. The first datum to land near it was silently discarded by it.

Re-measured with the band defined on **chi** — the physical statement "the derivation claims ≥10% of the load is not on particles here" — and with the original diamond source **dropped entirely**, so the reading stands on the rest of the corpus alone (`tools/dilute_ladder_reopens_sec29_probe.py`, 44 pairs):

| | |
|---|---|
| spearman(theta, slope), diamond source dropped | **−0.381** (was −0.287 with it) |
| **chi < 0.9** (dilute) | n=14, median measured slope **+0.826** |
| chi ≥ 0.9 (dense) | n=30, median measured slope **+0.220** |
| sources supplying the dilute band | **5** (was 1) |

The dilute band is near +1 where the derivation says it must be; the dense band sits at the model's own exponent. **The cut is not where the finding lives** — swept from chi 0.80 to 0.99 the gap runs +0.480 / +0.601 / +0.606 / +0.323 / +0.161, positive throughout and decaying monotonically as the cut is pushed into the saturated region, which is what the law predicts.

**The term is still not wired, and the reason changed.** It now fails where it acts *most*. On the diamond series at 0.01–0.04 wt% (`chi ≈ 0.03`), where the correction is largest, applying it takes the dataset from **8.7% → 34.2%**. A law cannot be adopted on the strength of the region where it barely acts while failing the region where it dominates. So the decision taken here is: **§29's general refutation is withdrawn, and wiring the term is rejected anyway** on the extreme-band damage — the term stays out, on new grounds, with a new exit condition. Two explanations are open, both measurable and neither measured: theta may be mis-scaled at very low loading (both the pack particle density and the GW contact area extrapolate three orders down to get there), or a second mechanism takes over below ~0.1 wt%.

**The median is now actively misleading here and must not be quoted as the verdict.** The same counterfactual that read 18.17% → 18.95% in §29 reads **18.17% → 14.82%** after nine measured points entered the corpus — i.e. across the completion bar — with no physical claim changed. Nine points cannot be the difference between a right and a wrong law. The reversal is a fact about the statistic (§26), and the enforcing test was rewritten to stop pinning the median's direction and to pin its **instability** instead.

**What would resolve it:** an iso-condition loading ladder below ~0.5 wt% from a **non-diamond** abrasive, which would put a second source in the extreme band and settle whether the failure belongs to the law or to the one patent. `test_the_extreme_dilute_evidence_still_rests_on_a_single_dataset` fails the moment one arrives — the exit condition moved down a band rather than being retired. **What this does NOT license:** wiring the term because the median now crosses the bar. That is the exact inversion of §29's own argument, and the number moved for a reason that has nothing to do with whether the physics is right.

**The general lesson, which is not about this term.** A threshold chosen while the data sit far from it is untested, and it will not announce itself when the first datum lands near it — it will quietly sort that datum into the wrong bucket and report the old answer. Prefer a cut stated on the **quantity the derivation is about** (here chi, the load fraction) over one stated on a convenient intermediate (theta), and **sweep it** whenever a conclusion depends on which side of it a point falls.

**Enforced by** `tests/test_load_sharing_onset_is_refuted_by_the_data.py` (11 tests, all re-measured at test time): the original theta-cut reading is kept alongside the chi-band reading so the contradiction stays visible; the band must have ≥3 independent sources and must survive dropping the diamond patent; the cut sweep must hold at every threshold; the surviving refusal must keep its evidence (the extreme dataset must still be damaged >2x) or be re-argued; and the exit condition must remain single-sourced.

> **⚠ SUPERSEDED IN PART, same-day (§31).** The exit condition above fired, the refusal was re-measured on two sources and SURVIVED — but the reading that reported it as still single-sourced was a reader bug. See §31.

## 31. §30's exit condition fired too — and the reader that was hiding it was measuring band membership on the wrong object

§30 refused the load-sharing onset a second time, on narrower grounds: the law is supported in the band the corpus reaches (chi 0.75–0.99) and badly damages the one place it acts hardest, the `us20110186542a1` diamond series at 0.01–0.04 wt% (chi ≈ 0.03), where applying it runs the shape error 8.7% → 34.2%. That refusal could not be promoted into a statement about the **law** because the extreme band (chi < 0.2) held exactly one applicant. `test_the_extreme_dilute_evidence_still_rests_on_a_single_dataset` was written to fail when a second arrived.

**The second source.** `us20230081442a1_dlc_zirconia_dilute_loading` — US 2023/0081442 A1 (Fujimi) Example 3 / Table 3, a printed patent table: colloidal zirconia at **0.1 / 0.3 / 0.5 / 1.0 / 3.0 wt%** on a DLC (amorphous carbon) film, at fixed pH 3.6, 25 mM permanganate, 2 psi, 200/23 rpm, Fujibo H7000, 50 mL/min. Chosen deliberately to share nothing with the incumbent: diamond → colloidal zirconia, tungsten → amorphous carbon, H₂O₂ → permanganate, different applicant. A second source that shared the first's abrasive or film could not have separated "the law fails at extreme dilution" from "that one patent behaves oddly", which is the entire purpose of the exit condition.

The transcription was checked **arithmetically rather than by re-reading**: Tables 2, 3 and 4 each contain the same composition (1 wt%, 25 mM, pH 3.6) and all three independently print 151 Å/min for it. Three separately typeset tables agreeing on the shared point is a stronger check than reading Table 3 twice. The 3.0 wt% turnover row (151 → 96 Å/min) is **kept**: the patent states the same reading in its own words, and dropping the row that disagrees with a monotonic power law is the selection this repository forbids.

A new film (`dlc`) and a new pack (`dlc_zirconia_permanganate`) were needed — no existing pack has this abrasive, this oxidiser or this workpiece. The pack claims **one** thing, the mechanical loading response, and is null everywhere else: no pH term (Table 2 measures one, but fitting it here and scoring Table 3 against it is the same experiment twice), no oxidiser term (Table 4, same objection), no hardness (DLC spans ~10–80 GPa with sp₃ fraction, which this patent does not report, so any value would decide the contact branch by assumption), no `material_family` (amorphous carbon is not metal, dielectric or semiconductor — `regime.py` correctly reports the axis undetermined rather than routing the run through contact physics chosen for a different bonding type), and **no `abrasive_conc_exponent`**, so the engine's derived +1/3 applies and the ladder is a genuine held-out test of that derivation rather than an interpolation.

**The reader bug, which is the transferable part.** The exit-condition test read `tools/load_sharing_slope_probe.slope_pairs()`, whose theta is the **geometric midpoint of an adjacent pair** — correct for a measured log-log slope, which belongs to an interval, and wrong for band membership, because the correction is applied to a **row**, at that row's own theta. This ladder's 0.1 wt% row sits at chi = 0.173, inside the band; every *pair midpoint* of the same ladder sits above it. So the new source entered the extreme band and the test that exists to detect exactly that reported one source, unchanged and green. `tools/extreme_dilute_second_source_probe.py` asks the membership question of the rows, with the same theta the counterfactual corrects them at, and prints both readings side by side.

**The refusal survives, and is now a claim about the law:**

| dataset | chi | onset applied |
|---|---|---|
| `us20110186542a1_w_diamond_h2o2_ph` | 0.018–0.070 | 8.7% → **34.2%** |
| `us20230081442a1_dlc_zirconia_dilute_loading` | 0.173 | 36.4% → **59.6%** |

Both worsen, both where the correction is largest, on two applicants sharing no material. The reading §30 could not exclude — one odd patent — is now excluded. The term stays out, and the reason is no longer provisional.

**The median moved a third time, and again for no physical reason.** The same counterfactual read 18.17 → 18.95% in §29, 18.17 → 14.82% in §30 after nine points entered, and 18.95 → 18.95% here after five more. Three verdicts, one derivation, zero changed claims. The enforcing test previously pinned the *gap* between the two median readings as evidence of that instability; adding this dataset made the readings agree and fired it. That test was **wrong to pin the gap** — a statistic's instability cannot itself be asserted as stable. It now pins the invariance that is real: the counterfactual's effect on the binding dataset is a physical claim and does not move when unrelated datasets enter, while the corpus median does.

**What would resolve it (moved, not retired):** a pack whose real contact area comes from **measured asperity statistics** rather than the Qi correlation, so theta at 0.01–0.1 wt% is no longer a three-order extrapolation. That is the one remaining way the extreme-band failure could turn out to be the scaling rather than the law. `test_the_extreme_dilute_band_is_read_off_rows_not_pair_midpoints` fails if the band's membership changes at all, so a third source cannot enter unnoticed.

**Corpus bookkeeping:** 47 → **48** scored datasets, 435 → **440** points. Headline median **18.2% → 18.9%** (upper median, `sorted(e)[n//2]`). That rise is not a regression: nothing was fitted, no constant changed, and no existing dataset's score moved. The new dataset scores 36.4%, above the old median, so it shifts the counting position — the same parity/counting effect recorded in §26. The 3.2 → 3.9 point gap to the bar is a fact about which dataset is now in the middle, not about the physics.

**The term stays out, and this is the decision taken:** wiring `chi(theta)` was **rejected** a second time, now on two-source evidence rather than one. Refitting it, narrowing it to a chi range that excludes the datasets it fails on, or dropping the DLC turnover row were each considered and refused — the first two would fit the refutation away, the third is the dataset selection this repository forbids.

**Enforced by** `tests/test_load_sharing_onset_is_refuted_by_the_data.py` (11 tests, all re-measured at test time; the single-source assertion is replaced by the row-vs-midpoint one).

## 32. `used_for_calibration` is a self-declaration, and eleven datasets contradict their own packs — the honest headline is 19.5%, not 18.9%

Every admissibility filter in this repository decides whether a dataset may testify by reading **one boolean out of that dataset's own header**: `used_for_calibration`. `absolute_scale_audit` (question S4), `ce3_residual_probe`, `oxidizer_order_probe` and `ph_derived_probe` all gate on it, and not one of them had ever checked it against anything. A dataset that declares itself held out is held out, by assertion.

It is checkable, and cheaply. A pack constant records where its value came from in `source:`. When that string **names a dataset in the scored corpus**, and the dataset **sweeps an axis that constant governs**, then the constant was fitted on those rows — so scoring the model against them grades it on its own answer key, whatever the header says. `tools/calibration_flag_audit.py` performs that cross-check across all 15 packs and the whole corpus.

**Eleven datasets are self-graded** while declaring `used_for_calibration: false`, across 18 pack-constant citations. They are, unhelpfully, concentrated at the good end of the score table: the corpus's 2nd, 3rd and 5th best blocks are all in this set.

| family | citations | example |
|---|---|---|
| `abrasive_size_exponent` (4 packs) | 6 | `sic_ceria_h2o2.abrasive_size_exponent` cites `su2011` (+0.24) and `wei2026` (+0.10) and **is their mean**; those two blocks then score 4.4% and 3.2% |
| pH-response groups (3 packs) | 11 | `oxide_silica_anionic`'s peak, width, floor and valid range all cite `cn109609035b`, which scores 32.1% |
| oxidiser peak shape | 1 | `cu_h2o2_bta.oxidizer_peak_shape_K` cites `du2004` (6.2%) |

**Four filters were needed to keep this measurement honest, and dropping any one inflates the count — the first version of this probe read 36.** A `note:` that merely mentions a dataset is not a fit, and several notes cite the dataset that **refuted** a constant (counting those would report honesty as circularity), so only `source:` is admitted. A constant whose value is `null` was withdrawn and changes no prediction, so its citation is inert. And seven of the keys are **documentation flags**, not degrees of freedom — `ph_response_is_unimodal_but_this_system_is_not`, `oxidizer_peak_is_pressure_dependent_unresolved` — whose value is a sentence or a bool recording a known limitation; citing the data that exposed the limitation is the correct behaviour.

**The fourth filter is the one the probe got wrong first, and it is the transferable lesson.** A dataset is predicted by exactly ONE pack. When a *different* pack's constant cites it, that constant is never evaluated on this block, so the score is not circular — it is ordinary cross-pack evidence reuse, which is how a corpus of 15 packs and 48 datasets is supposed to work. Five citations are of this kind, and one dataset, `tw202115224a_cu_abrasive_size_pressure`, is cited **only** this way: `oxide_silica` and `cu_alkaline_benzenesulfonic` both drew on it, while the block itself is scored under `cu_h2o2_bta`, whose size exponent comes from Lai 2001 instead. The first version of this audit condemned it. An instrument built to find dishonest scoring is worth nothing if it is itself imprecise, so the filter is asserted in BOTH directions — a foreign-only citation must not be counted, and every pinned self-graded dataset must really be cited by its own pack, so hard-wiring the flag either way fails.

**The held-out headline.** Removing every block the model was fitted on — the 11 above plus the 4 that already admit calibration — leaves 33 datasets at an upper median of **19.5%**, against the published **18.9%**. Note the direction: this is the one dataset exclusion the repository's own rule permits, because it moves the number the **wrong** way. Dropping datasets to lower a median is forbidden; declining to count the ones the model was fitted to is the opposite act. The 19.5% figure is the number a reviewer should be shown, and the completion bar should be read against it.

**What this does NOT claim, and the decision taken.** No constant is withdrawn here and no dataset's flag is flipped. A blanket repair was **rejected**, because the two possible repairs are not equivalent and the choice is per-constant: either the flag is wrong (the dataset *was* calibration evidence and should say so, at the cost of that block leaving the scored corpus), or the constant is over-claimed (it should be refitted on other evidence, or withdrawn). Deleting the citation "fixes" the audit while restoring exactly the undetectable state — the same error §27 records for the abrasive-identity keys. A repair made without measuring which of the two applies would be unattributable, so it is **deliberately *not* a gate** on this run and is left to be taken one constant at a time.

The `abrasive_size_exponent` family is the natural first target: it is six of the 18 citations, it spans four packs, and this repository already knows the constant is **not transferable across abrasives** — `sic_ceria_h2o2`'s own note says so while holding the mean of an alumina and a silica sweep.

**What would resolve it:** for each implicated constant, one independent measurement of the same quantity that is not in the scored corpus — then the constant stands on that, the citing dataset is genuinely held out, and its score becomes evidence. Until then the two medians must be quoted together.

**Enforced by** `tests/test_calibration_flags_match_the_packs.py` (6 tests, all re-measured at test time): a non-vacuity guard that fails if the stem matching ever stops finding citations, an upper bound that fails when a **new** self-graded dataset appears, an expiry that fails when one is corrected (so the list of 12 cannot become permanent), a direction check that fails if the held-out median ever beats the published one, a both-directions check that the cross-pack exemption is neither hard-wired on nor off, and a claim about which constant family dominates — because that names the next piece of work, and a bare count would read as a uniform problem.

## 33. The size-exponent self-grade cannot be repaired by holding a block out: every implicated block is WORSE under a leave-one-out exponent, and the "material property" it rests on is k=1 or k=2 evidence

§32 named `abrasive_size_exponent` the first repair target — six of eighteen self-graded citations, four packs — and said the repair is per-constant and is one of exactly two things, to be **distinguished by measurement** rather than chosen: either (a) the `used_for_calibration` flag is wrong and the block leaves the scored corpus, or (b) the constant is over-claimed and can stand on evidence that excludes the block, which then becomes an honest prediction.

Outcome (b) looked reachable here and nowhere else in the 18, because `cmp_sim/slurry/abrasive_effects.py:SIZE_EXPONENT_BY_ABRASIVE` already treats this exponent as a property of the **abrasive material** rather than of the pack. A material value is an average over several sweeps, so for any material with more than one independent sweep the exponent can be recomputed with the block under test held out. That is a leave-one-out on the constant itself, and it is decisive in both directions: with a donor, the block becomes a genuine prediction; with none, the constant is unidentifiable without the block and outcome (a) follows with no refit possible.

`tools/size_exponent_loo_probe.py` measures it. **Result: outcome (b) is refused on the data.**

| dataset | material | own n | LOO n | shape % | scale x |
|---|---|---|---|---|---|
| `bouvet2002_w_silica_size_sweep` | silica | −0.05 | +0.10 | 2.3 → **9.7** | 0.99 → 1.10 |
| `wei2026_sic_silica_size_sweep` | silica | +0.10 | −0.25 | 3.2 → **18.7** | 9.79 → 9.23 |
| `su2011_sic_alumina_size_sweep` | alumina | +0.24 | +0.33 | 4.4 → **5.2** | 1.14 → 0.75 |
| `lai2001_cu_alumina_size_sweep` | alumina | +0.33 | +0.24 | 8.7 → **13.5** | 0.06 → 0.07 |
| `bouvet2002_ti_silica_size_sweep` | silica | −0.45 | +0.10 | 30.7 → **39.6** | 0.61 → 0.68 |
| `son2021_oxide_ceria_size_sweep` | ceria | +1.00 | — | **unidentifiable** | — |

Six of six get worse or cannot be computed; not one block survives its own exponent being withdrawn. The corpus median with the self-graded blocks **returned under leave-one-out exponents** is 18.95% — identical to the published figure to two decimals — because none of these blocks sits at the median. So the repair buys nothing on the headline and costs honesty on every block it touches. The held-out 19.5% of §32 stands as the number to quote.

**The holdout must be by PUBLICATION, not by dataset, and that changes the answer.** `bouvet2002` contributes three files (Ti, W and oxide films measured in the same runs with the same slurry set). Holding out only the file lets that one paper donate an exponent to itself: under a dataset-level holdout, silica shows k=2 donors for every bouvet block. Under a publication-level holdout the true donor counts are k=1 for all three silica blocks and k=1 for both alumina blocks. The re-attribution is resting on far less independent evidence than the group counts suggest — which is the same non-independence that already, correctly, stops two size groups inside one file from counting as two sweeps.

**The between/within ratio survives the correction, and that is the one positive finding.** The material split was licensed by between-material stdev 0.51 against within-material 0.16 (3.2×) computed over groups. Recomputed with each publication collapsed to one observation first: 0.49 against 0.13, **3.8×**. Non-independent replicates had been *deflating* the within-material spread, so the correction could have destroyed the ratio and instead strengthens it slightly. The material attribution is not what fails here.

**What fails is the amount of evidence per material, and that is why (b) is refused rather than refuted.** With k=1 independent donor, a "leave-one-out exponent" is a single other paper's number transplanted across film, lab and decade — for `wei2026` (SiC) the donor is `bouvet2002` (Ti/W/oxide), and its −0.25 is not a measurement of the SiC system at all. Substituting it does not make the score honest; it makes it a different, worse guess. Ceria has k=0: `son2021` is the only pure-ceria sweep in the corpus, so `sti_ceria.abrasive_size_exponent` is **structurally unidentifiable** without the block it is scored on. That is outcome (a) with no measurement left to take.

**The decision.** No constant is refitted and no citation is deleted. The three blocks that cannot be repaired are recorded as permanently self-graded until new data arrives, and the §32 held-out median remains the headline. A functional-form search over the size term was **rejected** without being attempted: the refusal here is about evidence independence, not about the shape of the law, and trying alternative forms until one scores is fitting with extra steps (§28).

**What would resolve it:** one size sweep per material from a publication not already in the corpus — specifically a second pure-ceria sweep (which would make `son2021` computable at all) and a silica sweep from any group other than Bouvet's. Two independent donors per material is the threshold at which a leave-one-out exponent stops being a transplant, and the probe reports donor counts per publication so that threshold is checkable rather than asserted.

**Enforced by** `tests/test_size_exponent_loo_is_refused.py` (5 tests, every number re-measured at test time): the holdout unit is publications, not files (a dataset-level holdout must report strictly more donors for bouvet, so the distinction cannot be quietly dropped); no implicated block improves under leave-one-out; ceria is unidentifiable and the test names the exit condition; the between/within ratio survives collapsing to publications (so the material attribution is not silently withdrawn along with the repair); and an **expiry** that fails the moment any material reaches two independent donor publications, because at that point the repair becomes possible and this refusal is stale.

## 34. The pH-response self-grade has no path to a held-out value at all: the optimum is not a property of film or abrasive, and two ceria slurries disagree by 3.8 pH units

§32 left eleven pH-response citations across three packs — the largest self-graded family — and §33 measured the size family and refused the repair after doing the work. The instruction for this family was different and deliberately cheaper: **check whether outcome (b) exists STRUCTURALLY before pricing it.** The size family had a path to (b) only because `SIZE_EXPONENT_BY_ABRASIVE` had already established the exponent as a property of the abrasive material, making a material value an average over publications with one available to hold out. A pH peak has no such table, and this asks whether it could have one. That is the §19/§26 discipline — identifiability before law-hunting — applied before a single fit is priced.

`tools/ph_holdout_reachability_probe.py` re-fits every usable pH sweep's optimum from the raw rows (the pack values are the constants under audit, so reading them would be circular) and asks, for each candidate grouping, whether the optimum is a **property** of it: between-group spread against within-group spread, with each publication collapsed to one observation first (§33).

| dataset | film | abrasive | fitted optimum | fit % |
|---|---|---|---|---|
| `cn109609035b_oxide_anionic_silica_ph` * | oxide | silica | pH 1.2 | 5.0 |
| `us9422456b2_teos_silica_ph_pressure` * | oxide | aminosilane-silica | pH 4.3 | 8.3 |
| `us9422456b2_teos_silica_ph_pressure` * | oxide | aminosilane-silica | pH 4.3 | 9.6 |
| `dandu2009_sio2_ceria_ph_sweep` * | oxide | ceria | pH 5.4 | 5.4 |
| `netzband2020_thermal_oxide_ceria_ph` | oxide | ceria | pH 9.2 | 12.3 |
| `li2021_oxide_silica_ph` | oxide | silica | pH 11.0 | 0.0 |

(* = flagged self-graded)

**Donors exist and are worthless.** Every implicated block has at least one other publication sharing its film, and two of the three share an abrasive as well — so the naive reachability check passes. The property check fails, and fails hard:

| grouping | between-group | within-group | ratio |
|---|---|---|---|
| film | — (one group) | 3.50 pH | undefined |
| abrasive | 1.51 pH | 3.72 pH | **0.41×** |
| film + abrasive | 1.51 pH | 3.72 pH | **0.41×** |

A ratio below 1.0 means the grouping explains **less than nothing**: two members of the same group differ more than two groups do. Against the 2× bar this repository uses to license a group-scoped constant (the material split cleared 3.2×, and 3.8× after §33's correction), the pH optimum misses by nearly an order of magnitude. The single most damaging pair is within one grouping and one film: **`dandu2009` and `netzband2020` are both ceria on oxide and their optima sit at pH 5.4 and 9.2** — 3.8 units apart, on opposite sides of neutral, i.e. on opposite sides of the silica isoelectric point that any electrostatic reading of the axis turns on. The full within-film span is 9.8 pH units, which is the entire measured range.

**So a "held-out" pH optimum would be a transplant of up to 9.8 pH units, and outcome (b) is unreachable by structure.** This is not a statement that the corpus is too small. Adding pH sweeps cannot help unless they collapse the within-group spread, and the existing within-group disagreement is between two published, independently-measured ceria-on-oxide systems that genuinely optimise at different pH — a real difference in slurry chemistry (dispersant, ionic strength, ceria surface state), not scatter. The quantity being averaged is not shared.

**The decision, and what it is NOT.** The repair for all eleven pH citations is **(a)**: the flag is wrong, these blocks were calibration evidence, and they do not belong in the scored corpus — which is already how §32's held-out **19.5%** counts them, so nothing about the reported number changes. No constant is withdrawn, no citation is deleted (§27), and **no attempt is made to find a better pH grouping or functional form** — that was rejected before starting, because the failure is in evidence sharing, not in the shape of the law. `tools/ph_derived_probe.py` separately records that the derived electrostatic+kinetic form scores 60.4% against the per-group Gaussian's 11.0%, so the free constants here are not removable either; this entry adds that they are not even *shareable*.

**What this closes.** §32 named two repair families and required each to be measured rather than chosen. Both are now measured and both refuse: the size family on price (§33), the pH family on structure (§34). Together they cover 17 of the 18 self-graded citations, and the conclusion is that the held-out median **19.5%** is not a temporary accounting state to be repaired away — it is the honest figure, and the published 18.9% is the one that needs the caveat.

**What would resolve it:** two pH sweeps of the *same* abrasive-and-dispersant system from different publications, agreeing on an optimum to within ~1 pH unit. That would establish a grouping the optimum is genuinely a property of, and the probe reports the ratio per grouping so the threshold is checkable rather than asserted.

**Enforced by** `tests/test_ph_holdout_is_structurally_unreachable.py` (5 tests, every number re-measured at test time): donors exist (so the refusal cannot be mistaken for "no data"), no grouping clears the 2× property bar, the named ceria pair really is same-film-same-abrasive and really does disagree by more than 2 pH units, the verdict is invariant to the peak-grid resolution (so a speed choice cannot be load-bearing), and an **expiry** that fails the moment any grouping clears the bar.

## 35. The last self-graded citation closes the same way: the oxidiser shape constant K spans 3.6 decades inside one film, so no held-out value exists — all 18 are now measured and none is repairable

§32 listed eighteen self-graded pack-constant citations. §33 closed the six `abrasive_size_exponent` ones on **price** (every implicated block scores worse under a leave-one-out exponent). §34 closed the eleven pH-response ones on **structure** (the optimum is not a property of film or abrasive). This is the eighteenth and last: `cu_h2o2_bta.oxidizer_peak_shape_K = 8.0`, fitted to Du 2004's H2O2 series, which is then scored as a held-out block at 6.2%.

One citation, so only the reachability question needs asking — can K come from a sweep other than Du 2004? `tools/oxidizer_k_holdout_probe.py` re-fits K per oxidiser sweep from the raw rows, each sweep's peak pinned to its own argmax so that K is the only free parameter (the pack's note is explicit that a free peak *and* a free shape is degenerate when the data lie on one side of the maximum). K is the Langmuir constant of the promotion limb in `peaked_oxidizer_response`, a property of the oxidant-surface pair, so independent sweeps on the same film should return the same value if the mechanism is shared.

**Thirteen groups from seven datasets, and K spans four orders of magnitude.**

| grouping | between-group | within-group | ratio |
|---|---|---|---|
| film | 0.89 decades | 1.28 decades | **0.70×** |
| oxidant | 0.88 | 1.28 | **0.69×** |
| film + oxidant | 1.01 | 1.43 | **0.71×** |

Every ratio is below 1.0 — the same signature as §34, and against the same 2× bar. The worst within-group disagreement is **3.58 decades**, and it is inside Cu alone: `us20110165777a1` fits K = 190 while `us8501625b2` fits K = 0.05 on the same film. Du 2004's own 11.65 sits in the middle of that range and is reproduced to 2.4%, so the constant is well determined *by its own block* and completely undetermined by anyone else's. A held-out K would be a transplant of up to three and a half decades. Outcome **(a)**.

**Two limits of the table are stated by the probe before its verdict, because each could otherwise be mistaken for the finding.** Seven of thirteen groups pin K at a grid edge; six are at the LOW edge, which is not a fit failure but a result — as K → 0 the promotion limb is linear across the measured range, meaning those sweeps never reach a peak and carry no curvature for the peaked form to fit. They are kept, because dropping the blocks that disagree with the model's own functional form is precisely the selection this repository forbids. And twelve of thirteen groups carry oxidant `unknown`, because only Du 2004 uses the species-naming override key, so the by-oxidant row is nearly the same partition as by-film and must not be read as an independent third test.

**This closes §32 completely: 18 of 18 citations measured, 0 repairable.** The three closures have different reasons — price, structure, structure — and that matters more than the count, because each was measured rather than assumed, and each has its own exit condition. What they establish jointly is that the **held-out median 19.5% is not a temporary accounting artefact awaiting repair**. It is the honest figure. The published 18.9% is the number that needs the footnote, and the completion bar must be read against 19.5%.

**What this does NOT license, and the decision taken.** No constant is withdrawn, no flag is flipped in a pack file and no citation is deleted (§27 — deleting the citation passes the audit while restoring the undetectable state). Refitting K on the pooled corpus was **rejected** before it was attempted: a pooled value would be a mean over a 3.6-decade spread and would fit no block, including the one it was meant to free, and pooling data that disagree by four orders of magnitude to make an audit pass is fitting dressed as evidence. Searching for a fourth grouping until one clears the bar was **rejected** for the same reason as §34 (§28's rule: trying forms until one scores). The scored corpus is unchanged; what changed across §§33–35 is that the *reason* the held-out figure stands is now measured three times over instead of asserted once.

**What would resolve it:** a second H2O2 sweep on Cu that reaches and passes its peak — three or more concentrations either side — from a publication other than Du's. Two such sweeps agreeing on K to within a factor of ~3 would make K a property of the oxidant-film pair and reopen outcome (b). The pack's own note already asks for this in the same words ("replace it with your own H2O2 sweep... and the shape becomes calibrated rather than borrowed").

**Enforced by** `tests/test_oxidizer_k_holdout_is_unreachable.py` (5 tests, every number re-measured at test time): a non-vacuity guard on the number of fittable sweeps, no grouping clears the 2× property bar, the Cu within-film span exceeds 2 decades (the quoted example must stay true), grid-edge fits are reported rather than silently dropped (so the verdict can never be bought by excluding the blocks that refuse the peaked form), and an **expiry** firing when the worst within-group span falls below 1 decade.

---

## 36. Four of the five blocks the model has no opinion about were scored as though it did — a refusal only counts if the SCORER can read it

The scorer's job is to compare the model's opinion against measurement. When a term is switched off for a cited reason the model has **no opinion** about that axis: the rate is constant along it. The shape score then gives the block one free multiplicative scale, that scale fits the constant to the measured mean, and the block reproduces the `flat` baseline **exactly** — while still counting toward the headline median as though physics had been tested. A declared silence graded as an answer.

**The measurement.** `tools/ladder_span_probe.py` asks a question no fit is needed for: for each single-axis block, how does the span of the *predicted* rates compare to the span of the *measured* ones? The free scale cancels out of a ratio of ratios, so the number is independent of calibration. Five blocks came back at exactly `1.00×` predicted span — one rate for every row of a sweep. `tools/flat_prediction_census.py` then separated the two things that look identical from a score alone:

| block | axis | shape | flat | said so? |
|---|---|---|---|---|
| `lee2021_cu_nicotinic_inhibitor` | `inhibitor_mM` | 61.0% | 61.0% | yes — `GATED` |
| `kenchappa2021_softpad_hdp_oxide` | `pad_hardness_shore_d` | 42.8% | 42.8% | **no** |
| `hong2007_cu_ads_bta_polish_rate` | `inhibitor_mM` | 14.8% | 14.8% | **no** |
| `bae2022_si_wafer_alkali_ph` | `slurry_ph` | 12.6% | 12.6% | **no** |
| `phm2016_dresser_usage_mrr` | `cond_disk_usage_hours` | 7.2% | 7.2% | **no** |

**The cause was a reader, not a missing refusal.** Every one of the four had a warning, and three of them were *excellent* warnings — `hong2007`'s inhibitor term is REFUSED with a DOI, a measured 0/10 mM ratio of 1.21 against the term's asserted 18.4, the cost of applying it anyway, and the sweep that would unblock it. The scorer recognised exactly one word, `GATED`, so all of that was invisible to it. The repository already knew that **inert is acceptable and silently inert is not**; this is the same failure one level up — a refusal that is *stated* but not *machine-readable* is silent to the only reader whose opinion is published.

**The fix costs zero constants and moves zero predictions.** `cmp_sim/core/declined_axes.py` defines a marker naming the **axis** declined — `[DECLINES_AXIS: inhibitor_mM]` — written alongside the existing prose, never replacing it. It names the axis rather than the internal term because the scorer's question is about the input the *experiment* varied. Five call sites now emit it: the oxidiser pH gate, the inhibitor refusal, `UNREAD_BY_THE_RATE` (pad hardness, D99, and a new `cond_disk_usage_hours` entry), the inactive chemistry layer, and the P7 pad-life diagnostic. `Score` gained `declined_axes` and `declined_axes_swept`, the intersection with the axes the dataset actually sweeps.

**The median is unchanged at 18.9%, and that is the correct outcome** — the same rates are predicted for the same rows; only the description changed. A labelling fix that moved the score would be a selection, and a test asserts the invariance so the next session does not read the zero as a failure and "improve" it.

**Two things this was deliberately **rejected** from doing.** It does not drop the flat blocks: removing them to lower a median is forbidden, and the census prints its own removed-median (18.9%, identical) purely to measure how much of the headline rests on them. And `cond_disk_usage_hours` is the one entry in `UNREAD_BY_THE_RATE` with **no "put it here instead" path** — moving the value onto the disk object populates `pad_life` and leaves the rate equally unchanged, so offering that path was **rejected**: it would swap one silent inertness for another.

**A second finding fell out of the same probe, and it reversed the hypothesis that started it.** `tools/ladder_end_residual_probe.py` had found the worst row's *position* uniform (bottom 5 / middle 7 / top 6 of 18) but its *sign* skewed: 15 of 18 over-predictions against a fair-coin 9. The natural reading — the model's response is too steep and the fit parks most rows low — is **wrong**. The span probe measures the opposite: median span ratio **0.86×**, with 15 of 20 blocks *under*-spread. The skew comes from the flat blocks and from terms that respond too weakly, not too strongly. Recorded because a plausible unmeasured reading of a residual sign is exactly how a session spends itself deriving a damping term the data do not want. ⚠ **That 0.86× was itself an artefact and §37 retracts it** — it is the pooled figure, and pooling is what this very section forbids. Read §37 before citing this paragraph.

**What would resolve it** is named per block in the warnings themselves, and each remaining refusal has its own: a BTA-concentration sweep of Cu removal at this pack's own pH 3–4 with H2O2 (`hong2007`, `lee2021`); a pad-life series measuring removal rate against disk hours at one pad and one slurry, which would give the P7 proxy a time constant rather than only a shape (`phm2016`); pad hardness supplied on the `Pad` object rather than the pack, which reaches the GW contact layer (`kenchappa2021`); and oxidiser/pH constants declared by the `si_substrate_alkaline` pack, whose chemistry layer is inactive entirely (`bae2022`). None is a TODO here — each is a measurement, and each block's own warning states it at run time.

**Enforced by** `tests/test_flat_predictions_are_declared.py` (7 tests, all re-measured at test time): a non-vacuity guard (fails if no block is flat, so the suite cannot pass by examining nothing), **no flat block may be silent**, a declaration must name an axis the dataset actually sweeps (so declaring an unrelated axis cannot buy silence), the prose reason must survive beside the marker (>80 characters of body — a marker alone is a regression), the parser must require the marker and not merely the word `GATED`, the census tolerance must genuinely select constant predictions, and the **invariance**: marking a refusal must not move the headline.

## 37. The "model responds too weakly" signal was the refusals counted as answers — and it retracts a claim §36 made three paragraphs earlier

§36 established that a declared silence must not be graded as an answer, and then — in its own closing paragraph — cited the pooled span statistic as evidence that the model's terms "respond too weakly". This section retracts that, by applying §36's own rule to §36's own diagnostic. **No constants, no packs, no predictions changed; the corpus median stands at 18.9% and standing still is the correct outcome.**

**The claim under test.** `tools/ladder_span_probe.py` computes, per single-axis block and with no fitting, `span_ratio = (max/min predicted) / (max/min measured)`. The shape score's one free scale cancels from a ratio of ratios, so the number is calibration-independent. A population sitting below 1 would be **one claim rather than eighteen** — every exponent-bearing term collectively too shallow — and a licence to go derive a steepening term. Pooled over all 20 blocks the corpus said exactly that: geometric mean **0.80×**, 15 of 20 under-spread, two-sided sign test **p = 0.041**.

**Seven of those twenty blocks cannot dissent.** They sweep an axis the run explicitly DECLINED (`core.declined_axes`): the inhibitor term refused at 10 mM, pad hardness unread by the rate, conditioner usage hours, pH gated outside its calibration window. Five of them predict a *constant*, so their predicted span is `1.00×` and their ratio is pinned at or below 1 **by construction, whatever the physics does**. Pooling them with real predictions manufactures a one-sided population out of declared silence.

| population | n | median | geo-mean | under | sign test |
|---|---|---|---|---|---|
| all blocks (the claim) | 20 | 0.86× | **0.80×** | 15/20 | **p = 0.041** |
| declined axes only | 7 | 0.64× | 0.55× | 7/7 | p = 0.016 |
| drop fully-flat only | 15 | 0.95× | 0.93× | 10/15 | p = 0.302 |
| drop any declined | 13 | 0.95× | **0.98×** | 8/13 | **p = 0.581** |

**The verdict survives the choice of exclusion rule, which is why it is a measurement rather than a preference.** Two rules are defensible — drop only the blocks that predict a constant, or drop every block carrying a decline — and they differ by the two partially-declined pH blocks. Both land on a coin (p = 0.30, p = 0.58). Had one passed and the other failed, the conclusion would have been a choice of line, not a result. **There is no corpus-wide under-response to derive against**, and a damping or steepening term fitted to that pooled 0.80× would have been fitted to the refusals — a free parameter bought with the model's own silence, which is the most expensive kind because it looks like evidence.

**What was tried and rejected — the decision this section records.** The work §36 handed forward was to find *which term* produces the under-response and steepen it. That term was **not** sought, and the search was **rejected** before any fitting on the grounds above: the population that motivated it does not exist once refusals are removed. Two concrete candidates went with it. A **shared damping/steepening exponent** applied across the exponent-bearing terms was rejected — it is one new global constant whose entire support is the pooled 0.80×, i.e. the refusals. A **per-axis response-strength multiplier** on the pH, inhibitor and pad-hardness terms was rejected more firmly still: those are precisely the axes the packs DECLINE, so the multiplier would be fitted where the model has no opinion, converting a declared gap into a tuned number — the §36 failure re-entering through the back door. Also **rejected**: reporting the pooled figure with the declined blocks merely down-weighted rather than removed. They are not weak evidence for under-response, they are *no* evidence, and any non-zero weight re-imports the artefact in proportion.

**A structural fact fell out of writing the test, and the first draft got it backwards.** That draft asserted *declined ⇒ flat* and failed immediately: `cn109609035b` and `li2021` decline `slurry_ph` and still predict spans of **9.10×** and **1.23×**. **The gate fires per ROW, not per block** — rows outside the pack's calibration window are declined while the rest are predicted normally. So "declined" and "predicts a constant" are genuinely different properties and the split is three-way, not two-way. The true structural statement runs the other way (*flat ⇒ must be declared*, which is §36) and that is what is now pinned.

**Method note, recorded because it changed the answer.** The pooled claim was reported as a **median** (0.86×), which reads like a finding. The question is a sign question — "does the model respond less than the experiment more often than chance?" — and under a sign test with n = 13 the same numbers are a coin. A median of a ratio population carries no notion of how many samples produced it; when the population is small and the claim is directional, the summary statistic chose the conclusion.

**What would resolve it** is more predicting blocks, not more analysis of these. The test is a sign test over 13 single-axis ladders, and at that size it is **blunt**: the smallest under-count reaching p ≤ 0.05 is 11 of 13, a **5.5:1** imbalance. A genuine corpus-wide shallowness of modest size therefore sits undetected inside this null, and the honest reading of the result is *no detectable signal at this corpus size* — **not** "the terms are correctly steep". Three measurements would sharpen it, and each is the same measurement that would retire a refusal — which is the point: **every block converted from declined to predicting enlarges this test's power as a by-product.** A BTA-concentration sweep of Cu removal at pH 3–4 with H2O2 returns `hong2007` and `lee2021` to the predicting population; a pad-hardness value supplied on the `Pad` object rather than the pack returns `kenchappa2021` through the GW contact layer; oxidiser/pH constants declared by the `si_substrate_alkaline` pack return `bae2022`. That is 13 → 17, where the threshold falls to 13 of 17 (**3.2:1**). Even fully resolved the instrument stays coarse, so it is a veto on deriving against a *pooled* artefact rather than a licence to believe the terms are right — the per-axis error medians, not this sign test, remain the place where response strength is actually judged.

**Enforced by** `tests/test_span_evidence_excludes_declined_axes.py` (7 tests, all re-measured at test time): a non-vacuity guard on **both** sides of the split; every flat block must be declared (§36, restated where it is structural); partial declines must still exist, so the three-way split cannot silently collapse; the no-signal verdict asserted under **both** exclusion rules; the pooled population must remain more one-sided than the predicting one, so the exclusion stays load-bearing rather than decorative; and the sign-test arithmetic checked directly, since the verdict rests on it. **Verified by mutation**: removing the exclusion and pooling all 20 blocks drives p to 0.041 and fails the verdict test, so the guard catches the exact mistake it exists for.

**If the verdict test ever fails,** the corpus has genuinely turned one-sided and a steepening term becomes admissible. Read that failure as an instruction to derive one — and to **price it before wiring it** (§28) — not as a test to relax.

## 38. The second-cheapest crosser needs a PSD-WIDTH term, and the axis is unidentifiable in the strongest possible way: one source, and inside it the two films disagree in SIGN

> ⚠ **PARTIALLY RETRACTED by §40 (same corpus, one session later).** The "two films disagree in SIGN" half of this entry does not survive its own error bars: neither residual slope is distinguishable from zero (t = +0.09 and −1.76 on 2 residual degrees of freedom), so the two signs are two draws from noise rather than a contradiction, and §14's sign test was applied to numbers that were not measurements. The **identifiability** half below is correct and still load-bearing, and the refusal to wire a width term stands on it alone. §40 also supplies the second independent source this entry asked for — it was outside the scored corpus, which is where this entry told later sessions to look. **Read §40 before acting on anything in this section.**

**Why this entry exists.** `tools/median_crossing_probe.py --held-out` puts `us20190127607a1_teos_ceriasilica_size_sweep` second on the shortlist of datasets that must cross the 15% bar (18.9%, three needed). Unlike most blocks its cause is not obscure — the dataset's own header states it, and it is a genuine physical mechanism rather than a scatter story. This entry prices that mechanism and **rejects deriving it**, on identifiability rather than on a fit.

**The diagnosis, which is correct as far as it goes.** The four ceria-coated-silica abrasives are polished at one loading, one pH, one pressure, one speed pair and one tool, so D50 is the only *nominal* variable. Sorted by D50 the TEOS rate is **non-monotonic**: 875 → 1828 → 1311 → 2223 A/min. The model reads `abrasive_d50_nm` through a single power law, whose log-log slope is the same at every size by construction, so it cannot reproduce a reversal at all. Measured per row (free scale fitted as the scorer does it): 17.4 / 28.4 / 28.1 / **1.9%**. The dip particle (A, D50 156.1 nm) is also the one with a **broad, 4-peak distribution** — `(D99−D50)/D50 = 0.939` against 0.503–0.787 for the others — and Luo–Dornfeld supplies the mechanism directly: only particles within roughly the top `delta` of the distribution are indented at all, so at fixed D50 a broader PSD puts a **smaller fraction** of the abrasive to work. The sign is predicted, the driver `abrasive_d99_nm` is already transcribed on every row of both files, and the term would be dimensionless (a ratio, so it cannot be a relabelled size exponent).

**It is unidentifiable, and the measurement takes one probe** (`tools/psd_width_identifiability_probe.py`, no fitting anywhere — the residual slope `d ln(meas/pred) / d ln((D99−D50)/D50)` is immune to the scorer's one free scale because a scale cancels out of a slope):

| | |
|---|---|
| corpus rows declaring a D99 | **8** |
| datasets | 2 |
| **independent sources** | **1** (Versum US 2019/0127607 A1) |
| residual width slope, HDP film | **+0.024** |
| residual width slope, TEOS film | **−0.688** |
| signs agree | **no** |

Two facts kill it independently. First, the corpus contains exactly **one** publication that reports a PSD width at all, and the two files are the *same four polishing runs* measured on two films — so the holdout unit is one (§33), and any constant fitted here is interpolation of a single experiment wearing a derivation's clothes. Second, and worse: within that single experiment the two oxide films give residual slopes of **opposite sign**. A particle-count mechanism is mechanical; it cannot know whether the oxide underneath was deposited by TEOS or by HDP. So no shared width constant is even the right **direction** — §14's test, failed by the only data that exist.

**What was tried and rejected — the decision this section records.** Deriving and wiring a width term was **rejected**. Three weaker variants were rejected with it. Fitting the width exponent on **TEOS alone** (where it would work) is the dataset selection this repository forbids, and it is self-grading besides: the block it would be fitted on is the block it would be scored on. Making the width exponent **film-specific** (one value for TEOS, one for HDP) is worse than it looks — it is two free constants supported by four points each, drawn from one patent, attached to an axis the mechanism says cannot depend on the film; it would reduce the headline while asserting something the physics denies. Restoring a **D99-driven mechanical term** under the defect proxy's existing `tail_term` was rejected too: `abrasive_d99_nm` already feeds `defect_proxy` and that is where the corpus can support it (§18's rule — an axis that goes somewhere else must be shown to MOVE that something), whereas routing it into the rate re-imports the same one-source problem through a key that already exists.

**What this costs, stated plainly.** The block stays at 18.9% and the held-out corpus still needs three crossers. This is a refusal that keeps the project further from its own completion bar, which is exactly when a fitted constant is most tempting — and exactly why the refusal is worth writing down.

**What would resolve it:** a PSD width (D99, or D90/D10, or a distribution span) reported alongside removal rate by a **second, independent** applicant, at fixed D50 and fixed loading. Two sources, or one source measuring the same film twice, would make the axis testable; a same-film sign agreement across two applicants would make it derivable. Crucially, the *cheapest* version of this experiment already nearly exists in the corpus — several size sweeps report a D50 and nothing else — so the resolving step is a transcription question (does the source print a D90/D99?) rather than a new-physics question. **What would reopen it:** the probe finding a second source, or the two films ceasing to disagree.

**Enforced by** `tests/test_psd_width_axis_is_unidentifiable.py` (6 tests, every number re-measured from the shipping solver and the dataset files at test time, none copied from this page): the width driver must be present on the rows (so the refusal is about identifiability and not about a missing key); the source count must stay at one and the test **fails when a second arrives**, which is the exit condition rather than a memo; the two films' residual slopes must keep opposite signs; the rate must be **provably insensitive** to width at fixed D50 (a mutation guard — if a future session wires a width term the refusal fails loudly instead of being silently inherited); D99 must still MOVE the defect proxy, so "it goes somewhere else" is a measured claim and not an excuse (§18); and a non-vacuity guard fails if the probe collects nothing, because a probe that finds no rows would otherwise "pass" every assertion above.


## 39. The completion bar is not floored — the lower bound on this corpus's error exists, is exactly computable, and every genuine instance of it sits BELOW the bar

**Why this entry exists.** STATUS.md carries a standing instruction from the owner: the 10% completion bar may be relaxed toward 15% only if a session **first writes down what creates the lower bound on the error** — "what makes it hard" is explicitly not an answer; "this quantity is provably unreachable" is. Two candidate bounds have been offered here before and both were refuted. The measurement-reproducibility floor died in the 15th session: only a minority of the corpus publishes replicates and where it does the scatter runs 1.5%–37%, so there is no corpus-wide noise floor. "The remaining blocks are simply hard" was never a bound at all. This entry measures a third candidate that needs **no replicate data, no fitting and no new constant**, and that no functional form can evade — and then reports that it **does not justify a relaxation**. **No constants, no packs, no predictions changed; the held-out median stands at 19.5% and standing still is the correct outcome for a bound-hunting entry.**

**The mechanism: input degeneracy.** The prediction is a deterministic function of the input vector the scoring harness builds. When a published table varies a quantity the recipe schema has **no field for**, two rows arrive at the solver as the *same* input and leave with the *same* prediction, while the measured rates differ. No change to the physics can separate them, because the separating information never enters the model. That error is irreducible *for this input schema*, and — unlike a noise floor — it is computable exactly rather than estimated.

**Method** (`tools/input_degeneracy_floor_probe.py`, nothing fitted). Predictions come from the shipping solver by the same path `predictive_score` uses. Rows are grouped by identical prediction, and each group is then given its **own** free multiplicative constant — strictly *more* freedom than the real scorer, which allows one scale for the whole dataset — chosen to minimise that group's contribution to the MAPE. The result is therefore a valid **lower bound** on the shape score of any model, however derived, that reads only the inputs this harness supplies. The optimising constant is a weighted median: `sum |c − m_i| / m_i` is piecewise linear in `c` with breakpoints at the measured values, so the minimum is attained *at* one of them and enumerating them is exact, needing no optimiser. A dataset with no degeneracy scores a floor of exactly **0.0%**, which is the correct answer — nothing in its structure stops a better model from fitting it.

**Two false bounds had to be removed first, and the draft that did not remove them was badly wrong.** Both are the same error — *the model's own declared silence arguing that the model cannot do better* — and together they inflated the corpus's worst "irreducible" bound from 9.9% to **67.2%**, which would have carried the relaxation argument single-handed.

1. **A gated ROW is not a degenerate row.** The first draft grouped every measured row and crowned `ihnfeldt2008_cu_alumina_ph_oxidizer_chelator` at 67.2%. That dataset has no shape score at all: six of its seven rows are GATED because the pack's oxidiser constants stop at pH 6.25 and the response sign flips across the Cu Pourbaix boundary, so `predictive_score` already drops them. The probe now mirrors the scorer's gate exactly, and both `ihnfeldt2008` and `miranda2004` leave the table — they are not evidence about a headline they do not enter. (§37's lesson repeats here: gates fire per **row**, not per block.)
2. **A flat block is a declared refusal, not a limit.** A dataset whose rows fall into **one** group is the flat-prediction failure §36 exists to catch: the pack states it has no constants for the axis swept (`[DECLINES_AXIS: ...]`), so the prediction is constant by refusal, and supplying the missing measurement makes it vary and the floor evaporate. Five such blocks are reported by name and excluded from the verdict: `lee2021` (36.4%), `kenchappa2021` (29.8%), `hong2007` (14.7%), `bae2022` (11.8%), `phm2016` (7.0%).

| | held-out corpus | published corpus |
|---|---|---|
| scored datasets | 33 | 48 |
| non-zero floor | 13 | 15 |
| of which a genuine bound | **8** | 10 |
| of which a declared refusal (§36) | 5 | 5 |
| **median floor** | **0.0%** | **0.0%** |
| largest genuine bound | **9.9%** (`us9200180b2_cu_benzenesulfonic_series`) | 16.1% (`cn109609035b`, a *fitted* block) |

**The verdict, in the two forms that matter.** First, the headline is the **upper median** of the per-dataset shape errors, so a bound on the headline requires the **median dataset** to be floored. It is not — over half the corpus has a floor of exactly zero, so the *attainable* median is **0.0%** and degeneracy cannot support relaxing the bar to 15%, or to any value above zero. Second and stronger: on the held-out corpus **no genuine bound reaches the bar at all** (worst 9.9%). Every dataset is reachable in principle. The published corpus's one bound above the bar, `cn109609035b` at 16.1%, is a block the model was **fitted** to (§32–§35), so it is outside the honest headline and is not evidence about it either way.

**Sharper still, because the bar is a counting statistic (§26).** The median meets the bar exactly when enough *individual* datasets cross it, so degeneracy could block completion in only one way: a dataset that **must** cross being floored above the bar. Measured on the held-out shortlist, none is — `liang2026` 0.0%, `us20190127607a1_teos` 0.0%, `tw202115224a` 7.4%, `us8501625b2` 0.0%, `us6564116b2` 0.0%, `carbide2023` 6.1%. **The three crossers §38 left outstanding remain genuinely outstanding — they are missing physics or missing data, not structural impossibility.**

**What the bound does say, kept because it is the useful half.** `tw202115224a`'s 7.4% is the cleanest illustration of the mechanism in the corpus. The patent polishes Nalco and Fuso silica at the *same nominal* 15 / 27 / 50 nm, and the pairs differ by up to **1.9×** in measured rate (4414 vs 8453 A/min at 50 nm, where the particle shape also changes to cocoon). The dataset's own header already declares `abrasive_vendor` and `abrasive_shape` as excluded axes and forbids inventing a key for them, because a vendor is not a physical quantity and a key for it becomes a dataset fingerprint rather than a model. This probe prices that (correct) refusal at 7.4 of the block's 19.5 points — **the first time its cost has been a number** — and simultaneously shows the block can still reach the bar without it.

**What was tried and rejected.** Using the degeneracy floor as the bound argument for a 15% bar was **rejected**: the median floor is zero and no held-out genuine bound reaches the bar, so the argument does not exist. Quoting the *mean* floor across degenerate blocks (comfortably above 15%) was rejected as the §26 error — the headline is a median over datasets, so averaging a self-selected subset answers a question nobody asked. Including the gated and flat blocks was rejected per §36/§37, and that rejection was not cosmetic: it is the difference between a 67.2% worst bound and a 9.9% one. Creating `abrasive_vendor` / `abrasive_shape` keys to dissolve `tw202115224a`'s floor was rejected for the reason its own header gives.

**What would resolve it** — meaning, what would make a floor argument admissible — is a *measured* floor that binds at the median, and only two candidates exist: replicate scatter published by enough of the corpus to have a median at all (currently a minority, and refuted as a corpus-wide bound in the 15th session), or degeneracy reaching the median dataset. **What would reopen it:** a must-cross dataset acquiring a floor above the bar, or any held-out genuine bound crossing 15%. Two tests fail on that day and name the dataset — read the failure as a licence to argue for relaxation, with numbers, not as a test to relax.

**Enforced by** `tests/test_completion_bar_is_not_floored.py` (7 tests, every number re-measured from the shipping solver at test time, none copied from this page): a non-vacuity guard, so a probe that collects nothing cannot pass; the floor must be **provably a bound** (`floor <= shape` on every commonly scored dataset, which fails the moment the probe and the scorer stop grading the same rows); a flat block must never be counted as a bound, with both populations required non-empty so the distinction cannot quietly collapse; the **median floor must stay at zero**, which is the verdict; **no held-out genuine bound may reach the bar**, which is the stronger verdict; no must-cross dataset may be floored above the bar, which is the exit condition; and **every dataset carrying a floor must also be one `predictive_score` actually grades** — the guard against exactly the `ihnfeldt2008` mistake the first draft made.


## 40. §38's killing fact does not survive its own error bars — the two films never disagreed, and the second source §38 asked for existed outside the corpus all along

**Why this entry exists.** §38 refused to derive a PSD-width term and rested that refusal on two facts. The first — exactly one publication in the *scored corpus* reports a PSD width — is still true and is still decisive against fitting a constant. The second was stated as the killing one: *"within that single experiment the two oxide films give residual slopes of opposite sign. A particle-count mechanism is mechanical; it cannot know whether the oxide underneath was deposited by TEOS or by HDP. So no shared width constant is even the right direction."* That would be a genuine physical refutation rather than a data shortage, and it is the sentence a later session would cite to avoid re-opening the axis. **It is wrong, and it was wrong in a way the probe could have caught on the day it was written: the two slopes were reported as bare point estimates with no uncertainty attached.** This entry retracts it, replaces it with a measurement, and records that the refusal *survives* on the surviving half. **No constant, no pack and no prediction changed; the held-out median stands at 19.5%.**

**The measurement.** The same probe (`tools/psd_width_identifiability_probe.py`), now computing the ordinary OLS standard error on the residual slope. Each block has n = 4, hence **2 residual degrees of freedom**:

| block | slope | std. error | t | corr(ln width, ln D50) |
|---|---|---|---|---|
| `..._hdpoxide_ceriasilica_size_sweep` | **+0.024** | 0.280 | **+0.09** | −0.372 |
| `..._teos_ceriasilica_size_sweep` | **−0.688** | 0.391 | **−1.76** | −0.372 |

**Neither block measures a width slope at all.** The HDP film's estimate is smaller than a tenth of its own uncertainty — it is not a weak positive slope, it is *nothing*, and reading a `+` off it is reading the sign of noise. The TEOS estimate does not reach significance either. Two point estimates of opposite sign, both consistent with zero, are two draws from the same distribution; calling them a disagreement in sign is a claim about the arithmetic mean of a residual, not about the physics. The generalisable error: **§38 applied §14's "do the signs agree?" test, which is a sound test, to two numbers that were not measurements.** A sign test presupposes that each side has a sign to contribute.

**Why the mistake was available.** The corpus block is structurally the *wrong experiment* for this axis, and the table's last column says why: across the patent's four abrasives, PSD width and D50 move together (r = −0.372 in logs). The model already reads D50 through a power law, so a residual slope against width here is partly a relabelled size exponent — a quantity that is entitled to point in either direction between two films for reasons that have nothing to do with particle counting. The axis was never cleanly exposed, which is exactly the condition under which a noisy estimate looks like a finding.

**The second source, which was outside the place §38 looked.** §38's exit condition was written as *"a PSD width reported alongside removal rate by a second, independent applicant"* and was searched for among **scored datasets** — and the 41st and 42nd sessions both spent their transcription effort there, finding nothing and concluding the axis was still closed. That search space was wrong. **A publication can settle the sign of an axis while being permanently unscorable for a reason unconnected to that axis.** Basim et al., *J. Electrochem. Soc.* **147**, 3523 (2000) is precisely that: different applicant (University of Florida), different abrasive (fumed silica), different film (PECVD SiO₂), different tool (benchtop Struers Rotopol), different decade. Nothing about it re-measures US 2019/0127607 A1. Transcribed to `research/psd_width_sign_evidence.yaml`.

It is also a **cleaner width experiment than anything in the corpus**, which is the reason it is worth having. A 0.14 µm fumed-silica baseline at 12 wt% is spiked with 0.2–1.3 wt% of 0.5/1.0/1.5 µm sol-gel silica at fixed pH 10.5, 7 psi, 150/150 rpm, 100 ml/min and one pad. The coarse addition is at most 11% of the solids by weight, so the volume-median diameter stays inside the fine population while D99 moves by an order of magnitude: **width varies at essentially fixed D50**, which is the axis isolated rather than entangled. The direction is unanimous across three independent representations — the text (*"the removal rate decreased consistently, except for..."*, the authors naming their own single exception), TABLE II (5 of 5 spiked rows below the baseline), and FIG. 4 (four bars clearly below baseline, one marginally above, matching the stated exception) — and the authors supply a mechanism of their own: the coarse tail *"tend[s] to hold the wafer away from the pad reducing the pressure on the smaller size abrasive particles."* **Sign: negative.** Broadening the distribution at fixed D50 lowers the oxide rate, now from two unrelated applicants across three oxide films.

**And it still supplies no constant — which is the point.** The magnitude is deliberately recorded as `null`. The publication prints the same six removal rates **three times with mutually inconsistent absolute values**: the baseline is 10,000 Å/min in the text and 19,993 ± 380 Å/min in TABLE II — a factor of 2.0 on one quantity — while FIG. 4's axis reads a decade below the text (multiplying it by 10 reproduces the text's 10,000 and its 10,300 exception to within 0.3%, but then contradicts the table). Exactly one point is consistent across all three: 1.5 µm at 1.1 wt%. Choosing among the three to obtain a magnitude would be inventing a number. Worse, the two candidate mechanisms — Luo–Dornfeld's *fraction of the distribution actually indented* and these authors' *load sharing by the coarse tail* — predict the same sign with different size dependences, so even a clean magnitude from one experiment would not identify the term.

**What was tried and rejected.** Wiring a width term on the strength of the new sign evidence was **rejected**: a sign is not a constant, and the only block it would be scored on is the block it would be fitted on (§32). Re-deriving §38's refusal from the retracted sign claim was rejected — the claim is false and inheriting it would make the refusal unfalsifiable. Deleting §38 was rejected: its identifiability half is correct and load-bearing, and a retracted reason is more useful visible than erased. Promoting Basim 2000 to a scored dataset was rejected for the contradiction above; it lives in `research/` with the contradiction written into the file so no later session re-derives it as a discovery.

**What this costs.** Nothing moves. `us20190127607a1_teos...` stays at 18.9% and the held-out corpus still needs three crossers. What changes is the *reason* the axis is closed: not "the physics is refuted by the data" but "the experiment that would identify it has not been published with a usable scale."

**What would resolve it:** a lognormal-PSD reformulation of the active-particle count in which σ follows from the *published* D50 and D99 with **no free constant** — that is a prediction the eight corpus points and Basim's six can falsify, rather than a fit to them. **What would reopen it:** a second applicant publishing PSD width against removal rate with a *self-consistent* absolute scale, or either corpus block's width slope reaching |t| ≥ 2.

**Enforced by** `tests/test_psd_width_axis_is_unidentifiable.py` (8 tests, every number re-measured from the shipping solver and the source files at test time, none copied from this page): the corpus still rests on one scored publication (the identifiability half of §38, still live); **neither film may measure a width slope** (|t| < 2 — the retraction itself, which fails loudly if a future data addition gives either film a real slope, instead of letting §38's retracted sentence be silently inherited); the width axis must stay **confounded with D50** in the corpus block, so "the external source is the better experiment" is a measurement and not a preference; a second independent source must report the sign, and it must report **`magnitude: null`** with at least three separately cited readings behind its direction — the guard against this entry's own worst failure mode, a sign quietly growing into a constant; plus §38's surviving guards (the driver is present on the rows, the width span is wide enough to have been read, the rate is provably insensitive to width, and D99 still moves the defect proxy).

### ⚠ AMENDED same session: the zero-constant form §40 named as "what would resolve it" is PRICED AND REFUSED

§40 closed by naming the resolving step: *"a lognormal-PSD reformulation of the active-particle count in which σ follows from the published D50 and D99 with no free constant."* That form was derived and priced in the same session, before any wiring, per §28's rule. **It is not being wired, and the reason is the one §40 had just finished writing down.**

**The derivation, which genuinely costs nothing.** For a lognormal distribution with median `d50` and shape `σ`, the p-th quantile is `d_p = d50·exp(z_p σ)`, so a published (D50, D99) pair fixes σ outright: `σ = ln(D99/D50)/z₉₉` with `z₉₉ = 2.32635`. Abrasive is dosed by **mass** (wt%), not by number, so the particle count at fixed loading goes as `N ~ φ/⟨d³⟩`, and for a lognormal `⟨d³⟩ = d50³·exp(4.5σ²)`. Hence at fixed D50 and fixed wt%,

    f(σ) = exp(−4.5 σ²)                                              (W)

Every number in (W) is a definition — `z₉₉` is a standard-normal quantile and `4.5 = 3²/2` is the lognormal moment coefficient. There is no freedom to fit, and the sign is **structurally negative**: the same grams of abrasive spread over a broader distribution buy fewer particles, because the third moment outruns the median. That is the sign Basim 2000 measures, arrived at independently.

**The price** (`tools/lognormal_width_price_probe.py`, nothing fitted, no pack touched):

| block | shape before | shape after (W) | residual slope vs `ln f` |
|---|---|---|---|
| `..._teos_...` | 18.9% | **12.9%** (−6.0 pp — *crosses the bar*) | **+1.95 ± 1.04** |
| `..._hdpoxide_...` | 8.4% | **13.4%** (+5.1 pp — *broken*) | **−0.04 ± 0.78** |

**Refused, on three grounds, the first of which is this page's own lesson.** (1) **Neither slope is a measurement.** ±1.04 and ±0.78 on 2 residual degrees of freedom: `+1.95` is consistent with the predicted `+1.00` and equally consistent with zero, and `−0.04` is nothing at all. Wiring on this evidence would repeat §40's retracted error *in the opposite direction* — reading physics off the sign of noise, three paragraphs after retracting exactly that. (2) **It pays for one film with the other.** The same four polishing runs, one experiment: TEOS improves by 6.0 pp while HDP degrades by 5.1 pp. A mass-dosed particle-count term cannot know how the oxide underneath was deposited, so this is not physics discriminating between films — it is a block swap, and the headline median is a counting statistic that would happily reward it (§26). (3) **The available effect is 1.254×**, so the axis cannot repair much however right it is; a median that moved more than that moved for another reason.

**The generalisable point, and the reason this amendment is worth more than the term would have been.** A derivation with zero free constants is *not* self-justifying. (W) is almost certainly true physics — mass dosing really does mean broader distributions buy fewer particles — and it still must not be wired here, because **this corpus cannot tell whether it is true**. "Derived, not fitted" answers the question *is this constant earned?*; it does not answer *does the data confirm it?*, and those are separate gates. A term that is correct in principle and unconfirmed in practice belongs in the documentation, not in the solver.

**What would reopen it:** a third source measuring PSD width against removal rate **on one film**, which is the only thing that can decide whether the TEOS/HDP split is real or a coincidence of four points. Until then the sign is known (§40), the magnitude is not, and (W) sits here derived and unwired.

**Enforced by** `tests/test_lognormal_width_is_priced_not_wired.py` (5 tests, re-measured at run time): (W) must remain **absent from the solver** — the mutation guard, which fails if a later session wires it; the derivation must reproduce the published D99 from D50 and σ, so the zero-constant claim stays a computation rather than an assertion; the two blocks must keep **opposite-signed pp movements**, which is the refusal's load-bearing fact; neither residual slope may reach |t| ≥ 2, which is the exit condition; and the factor span must stay below the size of the error it would have to explain.

## 41. The corpus-wide "0 silent inert axes" verdict was reached without looking at two swept axes — a validation row can carry a process input, and `_varying_axes` only read `overrides:`

**Why this entry exists.** §17 perturbed every swept axis in the corpus and reported **0 wiring bugs and 0 silent inert axes**; §18 then certified all four remaining silent axes as declared. Every admissibility filter in the repository has since relied on that verdict, because they all read one function — `core.predictive_score._varying_axes` — for the list of axes a dataset varies (`Score.declined_axes_swept`, `tools/axis_error_census.py`, `tools/flat_prediction_census.py`, `tools/inert_axis_scan.py`). **That function read exactly three places: `row["pressure_psi"]`, `row["rpm_platen"]`, and the keys of `row["overrides"]`.** A validation row is a free-form YAML mapping, so nothing stops a dataset from putting a process input straight on the row next to `pressure_psi` — and two datasets do. Those axes were not classified as silent; they were **never enumerated**, so no census could see them and the "0 silent" answer was true only of the space it searched. **No constant, no pack and no prediction changed; the published median stands at 18.9% and the held-out median at 19.5%.** `tools/row_level_axis_scan.py`.

**What was hiding there.**

| dataset | row-level axis | levels | state before | state after |
|---|---|---|---|---|
| `yang2023_quartz_ceria_L25` | `flow_ml_min` | **5** | **silent** — rate inert, nothing machine-readable said why | declared |
| `us9422456b2_teos_silica_ph_pressure` | `zeta_mv` | **10** | **dropped** — the scorer never put the value into the recipe | declared |

**The flow sweep is §36 recurring where §36 could not look.** Slurry flow reaches the removal rate through exactly one path: the radial starvation weighting in `models/uniformity.starvation_profile`, which returns `None` — deliberately, rather than inventing a shape — unless a pack declares `starvation_length_m`. **No pack in this repository declares one**, and none should invent one, because the length encodes groove pattern and injection geometry. So the predicted rate has not responded to slurry flow in any run ever scored. The run *did* say a great deal about flow (supply number, λ regime, a starvation warning), and none of it carried the `[DECLINES_AXIS: ...]` marker, so the scorer graded a five-level flow sweep as a prediction that happened to be flat — the precise failure §36 identified and fixed for the axes it could enumerate. The measured cost of the refusal: an oracle free flow exponent on that block buys **69.0% → 59.2%** (b = −0.8), so this is not a cheap gain being declined, it is a real one being declined **honestly** for want of a length constant.

**The zeta case is a different and worse class: the model was never asked.** `Slurry` carries a `zeta_mv` field and `slurry/rheology.derive` reads it, but `_recipe_for` did not copy the row's value into the recipe. An unasked model and an indifferent model produce byte-identical output, so "|zeta| does not move the rate" was an untested assumption rather than a position. Passing the value through changes no rate — and that is the intended result, because the axis is genuinely declined: |zeta| sets the electrostatic barrier, hence agglomeration and the large-particle tail, and the tail is read by the defect proxy. **The refusal is additionally forced by identifiability, re-measured at test time: in the only corpus dataset publishing zeta, each of the 11 pH levels has exactly one zeta value, so a fitted zeta term would be the pH term under a second name.**

**The generalisable rule.** *A negative result retires a question, so suspect the READER that produced it* — already written down here after a probe read the wrong level of a condition. This is the same failure one level up: the reader was not a probe but the **schema assumption** shared by every probe, and it made a whole coordinate of the input space unobservable. When a census reports zero of something, ask what it enumerated, not how it classified. The fix makes the enumeration a declared whitelist (`ROW_LEVEL_AXES`) rather than a pattern match, because pattern-matching row keys would eventually perturb a measured-rate column and a probe that perturbs the *answer* reports nonsense confidently.

**What would resolve it.** Flow: a removal-rate-versus-flow series at one pad, one slurry and one *P·V*, which would give the starvation decay a length instead of only a direction. Zeta: a removal-rate-versus-zeta series at **fixed pH**, which does not exist in this corpus and without which the axis is not separable from pH. **The decision taken** was to publish both axes and declare both refusals rather than wire either — the flow-exponent refit was **rejected** even though it is worth 9.8 percentage points on that block, because an oracle exponent is not a length constant and fitting one per dataset is the thing this repository does not do.

**Enforced by** `tests/test_row_level_axes_are_visible.py` (9 tests, all re-measured at run time, so a new dataset carrying a row-level axis is covered with no test edit): every row-level key whose value varies must appear in the published axis list; a **non-vacuity guard** fails if the corpus stops containing such sweeps, because the first test passes trivially otherwise; no row-level axis may be `silent`, `prose-only` or `dropped`; the flow refusal must name **where** the value would have to live, **what measurement** unblocks it and the honest consequence, and the scorer must actually read it as a declined axis; a measured zeta must **arrive** in the recipe; the zeta refusal's identifiability claim is **re-measured** and fails the moment a dataset varies zeta at fixed pH; the "it goes to the defect proxy instead" half is tested in **both** directions, so the excuse fails unless D99 really does move `defect_risk`; and the median is pinned at 18.9%, because **zero movement is the correct outcome for an honesty fix** and a session reading that zero as failure would try to "improve" it.

---

## 42. The reverse wiring question: a pack key that is DECLARED and reads nothing — and the two answers are opposite

§41 fixed the enumeration of axes the corpus *sweeps*. This section asks the other direction, and it needs no corpus at all: **does every key a pack DECLARES move anything?** `tools/pack_key_wiring_audit.py` has always asked the mirror question — does every key the *engine* reads exist in some pack — which finds misspellings and declared gaps. It is structurally blind to §20's hardest case, because nothing in the system can report it: `apply_overrides` warns only when a key is **undeclared** (`'x' is not declared by pack ...`), `inert_axis_scan` enumerates only axes some dataset happens to sweep, and the run prints a plausible number either way. A key with a sourced value, a unit and a confidence grade that no line of code consumes therefore ages into fact.

`tools/declared_key_response_census.py` perturbs every numeric key of every pack by 3x through the **shipping solver** (reading the source would miss keys consumed via the inherited `legacy/` dispatchers, which is exactly where §18's silent terms were hiding) and classifies the response. Two findings came out of it, and **they are opposite in kind** — which is the point of the section, because both look identical from outside.

**The probe's own first answer was nonsense, and the reason is this repository's central rule.** Run at each pack's own reference composition it reported **1077 of 1275 keys silent**. Every factor is `Kp_eff = kp * prod(factor_i)` with each factor *exactly 1.0 at its pack's reference condition*; at `C == C_ref` the concentration factor is `(C/C_ref)^n = 1` for **every** n, so perturbing `abrasive_conc_exponent` cannot move the rate no matter how it is wired. The probe was measuring the normalisation contract and calling it inertness. The base run is now **displaced off every reference axis first**, and a key whose driving variable sits on the reference is reported `unreachable-here` — a statement about the probe's operating point, not about the pack. This is §21's rule (*a constant the model computes is not evidence*) applied to a perturbation: ask whether the input VARIES before reading anything out of the output.

### (a) `asperity_density_per_m2` is inert BY DERIVATION — declared, not wired

All fourteen packs declare a summit density (2e8 /m², literature-sourced) and a reference partner, and both move the predicted rate by **exactly nothing**. That is **correct Greenwood–Williamson physics**. With exponential summit heights the load balance fixes the separation `d` so that adding summits both adds contacts and shares the same total load among more of them:

| summit density η varied 16x | response |
|---|---|
| real area fraction `A_r/A_0` | relative spread **1.1e-10** (float noise) |
| mean real pressure `p_r` | **1.1e-10** |
| contact count at fixed nominal pressure | **1.1e-10** |
| `E*` ×3 / `σ` ×3 / `R` ×3 (non-vacuity) | −67% / −42% / +73% |

η then cancels a **second** time inside `kappa = A_r(pad)/A_r(reference)`. So the right action is a declaration, **not a wire**: `formulation.UNREAD_BY_THE_RATE` now carries the cancellation, names the pad properties that *do* reach the rate (`E*`, `R`, `σ` on the `Pad` object), and states where η **is** still read — the **saturation** diagnostic, i.e. the validity boundary of everything above. Per §20's both-halves rule that second claim is tested too: saturation must respond to η, or "not ignored" is an excuse rather than a location.

### (b) `pad_hardness_shore_d`'s "put it here instead" advice was itself inert on most packs

§20 established that a declaration recommending another path must prove the recommended path is **not equally inert**, and `test_the_pad_object_is_the_path_that_reaches_the_contact_layer` was written to do that. It asserted that a Shore D given on the `Pad` object was **converted** to a modulus. **Conversion is not reach.** Measured end to end on the packs that declare the key, the recommended path moves the rate on **one** of them; the others convert the value and then **withhold kappa**, because their reference pad is inherited from `base` rather than measured (`reference_pad_is_trustworthy`) — so the advice was, for most callers, a second silent failure wearing a green test.

And where kappa *is* applied it is only bounded over part of the range. On `oxide_silica_calibrated_pad` at 3 psi:

| `Pad.shore_d` | kappa | summit saturation |
|---|---|---|
| 60 | 1.90x | 30.1% |
| 55 | 3.25x | 51.6% (warned) |
| 45 | 9.34x | 100% |
| 40 | 14.55x | 100% |
| 30 | — | `ContactSolverOutOfRange` |

A 14.5x rate multiplier past full summit contact is not a prediction: the exponential-tail result kappa rests on is void there. The run already warns, and the declaration now states the bound and the crash class so a caller reading only the returned number cannot miss it.

**Zero median movement is the correct outcome** — 18.9% before and after (440 points, 48/52), no constant, pack or prediction changed. Only declarations and tests were added.

**What would resolve it (a):** nothing, and that is deliberate — it is a derivation, not a data gap, so a magnitude for η is not merely *unknown*, it does not exist to be measured. The exit condition is instead a **mutation guard**: `test_the_gw_real_area_fraction_does_not_depend_on_summit_density` re-measures the cancellation at test time, so if the contact layer ever gains a term in which η survives, the declaration fails loudly rather than asserting a cancellation that stopped happening. **What would resolve it (b):** a pack whose reference pad comes with its own **measured** asperity statistics, which would let kappa be applied on more than one pack; until then the advice is honest only because it says it is conditional.

**The decision taken, and what was rejected.** Wiring an η term into the rate was **rejected** — it would reproduce a quantity the contact model proves cancels, i.e. a free constant dressed as a pad property. Deleting η from the packs was also **rejected**: it is a real measured pad property and it is read by the saturation boundary, so removing it would restore the undetectable state (the same error class as §27's abrasive-identity keys). Relaxing `reference_pad_is_trustworthy` so kappa applies everywhere was **rejected** as well, because kappa against an inherited reference measures the distance from a guess (§22). Only declarations and tests were added.

**The generalisable rule.** An audit has a direction, and the opposite direction can be the one with no reporter at all. When every existing check reads the engine's *requests*, the unexamined set is the packs' *offers* — and there the two possible verdicts, "correct cancellation" and "forgotten wire", produce **byte-identical** output. Separate them by deriving the cancellation on the model in isolation, and never grade a "put it here instead" path by whether the value was parsed; grade it by whether the **rate moves**.

**Enforced by** `tests/test_gw_summit_density_cancels_by_derivation.py` (7 tests, every number re-measured at run time — a literal would go stale the moment a pack gains a measured reference pad, and going stale silently is the failure these tests exist to prevent): the η cancellation is re-derived on `PadContactState` directly and must hold to 1e-6; a **non-vacuity guard** requires `E*`, `R` and `σ` to still move the same quantity, so the cancellation test cannot pass on a dead model; both η keys must be inert **and** carry `[DECLINES_AXIS: ...]`; η must still move the saturation diagnostic; the recommended pad path must move the rate on at least one pack, and if it is inert on any the declaration must say **CONDITIONAL**; and the soft-pad case must emit the saturation warning while the declaration names both the saturation bound and `ContactSolverOutOfRange`. Calibrated against the bug: reverting `formulation.py` alone fails 4 of the 7.

---

## 43. The perturbation is part of the instrument: §42's own probe filed this repository's strongest pH constants under `silent`

§42 built `tools/declared_key_response_census.py` to ask *does every key a pack DECLARES move anything?*, and it fixed one half of the instrument: **where** the probe stands, displacing the base run off every reference condition so a factor that is 1.0 at reference is not mistaken for a dead wire. It did not fix the other half — **how hard the probe pushes**, and in which direction. A single large one-sided factor (x3) manufactured silence twice on one pack, and the two mechanisms are different:

### (a) x3 pushes a key OUT OF ITS OWN VALIDITY WINDOW, where the model correctly refuses

`ph_peak` on `oxide_silica` is 11.0 with a width of 3.1 measured over pH 10–12.5. Multiplying it by 3 puts the optimum at **pH 33**, seven widths from the query — and there the model does exactly what §34's clamp was built to do: it holds the pH term at the nearest measured edge, rests the rate on the mechanical floor, and **warns**. Measured at the original probe point (pH 11.5):

| perturbation of `ph_peak` | rate response |
|---|---|
| x3 | **0.00%** |
| x1.25 | **54.81%** |
| x1.05 | 10.52% |

The response is **non-monotonic in the perturbation**, so the probe was grading an honest out-of-domain refusal as a forgotten wire. The census now sweeps `PERTURBATION_FACTORS = (1.05, 0.95, 1.25, 0.80, 3.0, 1/3)` — small first, both directions — and a key is inert only when **no** admissible perturbation reaches it.

### (b) the DISPLACEMENT landed exactly on a symmetry point, where the width cancels by derivation

`ph_response_width` was reported silent for a second, unrelated reason, and it is §42's own finding recurring inside §42's own tool. `oxide_silica` has `ph_ref = 10.5` and `ph_peak = 11.0`; `PH_DISPLACEMENT` was **1.0**, exactly twice the ref-to-peak distance, so the query landed at pH 11.5 — mirror-symmetric to the reference about the optimum. The factor is normalised to the reference:

```
f(pH) = exp(-(x/w)²) / exp(-(x_ref/w)²),   x = pH − ph_peak
```

and with `|x| = |x_ref|` that is **exactly 1 for every w**. An exact cancellation, by derivation, at that single point:

| query pH | \|pH − peak\| | width x1.25 response |
|---|---|---|
| 11.5 (symmetry point) | 0.50 | **0.00%** |
| 12.1 | 1.10 | 3.17% |
| 12.5 | 1.50 | 6.62% |

The displacement now **breaks symmetry about every declared optimum** (`PH_SYMMETRY_BREAK`, stepping outward so it cannot re-enter the reference's mirror image) while staying inside `ph_valid_range` — otherwise the fix would swap one artefact for another.

### The measured effect, and the honest reading of it

`reads` goes **147 → 157** and `silent` **584 → 574** across 1275 pack keys. The ten recovered keys are pH and reference-normalised terms on the packs that own them. **The median is unchanged at 18.9%** (440 points, 48/52 datasets), and that is the correct outcome: no constant, pack, model term or prediction changed — only the instrument that judges them. A session reading that zero as failure would try to "improve" it.

The remaining 574 is still a **shortlist of questions, not a bug count**, for the reasons §42 gives (inherited keys, correct gates off at the probe's operating point).

**The decision taken, and what was rejected.** Widening `INERT_TOLERANCE` so the x3 response counted was **rejected**: the response really is 0.00% there, and loosening the bar would hide genuine silence everywhere else to paper over one artefact. Removing the x3 factor entirely was **rejected** too — a large factor is the only one that reaches a weakly-coupled key, so the set needs both ends. Special-casing the pH keys by name was **rejected**: the bug is in the perturbation design, and a name list would leave every future key with a validity window exposed to the same error.

**The generalisable rule.** *A perturbation magnitude and a displacement position are both part of the measuring instrument, not neutral choices.* A probe that reports zero response has to publish **which perturbations it tried** — a bare "silent" verdict is unquotable without them — and it must be held to recovering keys that are **known** to be read, or the whole census can silently decay into "nothing moves anything", which reads as a clean bill of health for the entire repository and which nothing else here would contradict. This is the instrument-control principle the repository already applies to non-vacuity guards, applied to a probe's own sensitivity. Note also that (b) is §42's derivation-cancellation class *inside the tool built to find it*: a tool is a model too, and a model's exact cancellations are invisible until someone derives them.

**What would resolve it.** Nothing external — this is an instrument defect that has been **measured** and corrected. The exit condition is a **mutation guard**: the enforcing test reproduces the bug at the original probe point, so if the out-of-domain refusal or the reference normalisation is ever re-derived such that x3 stops being inert there, the test fails and demands the limit be re-derived rather than the prose edited.

**Enforced by** `tests/test_perturbation_is_part_of_the_instrument.py` (8 tests, every number re-measured at run time — pinning `54.81%` as a literal would go stale the moment a pack's pH constants are re-sourced, and inviting a session to edit the claim instead of the code is how §40's stale correlation string happened): `ph_peak` and `ph_response_width` must both classify as `reads`; the **bug is reproduced** at the original probe point, where x3 must still be inert while x1.25 reaches past 10%, and at the current point a small factor must still out-reach x3; the width's cancellation is re-derived on the shipping solver at the mirror point and must vanish one step off it; **no pack** may be probed on its own pH symmetry point, derived from `available_packs()` at test time with a non-vacuity guard so a new pack is covered with no test edit; every reported response must carry the perturbation that produced it; the instrument controls must pass; and a **negative control** feeds a fabricated silent `ph_peak` through `instrument_control_failures` and requires it to trip, and to say that the census's own verdicts are suspect rather than merely that one key did not move. Calibrated against the bug: reverting the perturbation set and the symmetry break fails **6 of the 8**.

## 44. An axis's response was read from its ENDPOINTS, and a peaked term cancels exactly on an endpoint pair

§43 established that *the perturbation is part of the instrument* and repaired the probe whose displacement it controlled. It could not repair the two readers that most of this repository's closure arguments actually rest on. `tools/inert_axis_scan.py` and `tools/residual_census.py` decide whether a swept input reaches the rate by running the dataset's own first row **twice** — at the axis minimum and at the axis maximum the paper ran — and comparing the two predicted rates. That map is consumed by `Census.responsive_axes`, the `silent`/`declared`/`aliased` classification behind the corpus-wide "0 silent inert axes" verdict (§17/§18, and its enumeration repair in §41), and `tools/oxidizer_order_probe.py`'s confound admissibility test.

**Here the two evaluation points are not the probe's to choose.** They are the first and last level of the *publication's* design, so unlike §43 no change to a perturbation constant can avoid the cancellation — it arrives through the data.

### The cancellation is exact, not statistical

`models/chemical_rate.py:ph_response` is

```
f(pH) = floor_side + (1 − floor_side) · exp( −((pH − ph_peak)/w)² )
```

For two levels mirrored about `ph_peak` the exponential is **identical for every width w**, so at equal floors the endpoint difference is exactly zero while the interior of the same sweep moves the rate as much as the term can. This is §43(b)'s identity reached from the other side: there the probe's own displacement landed on the symmetry point, here the experiment's design does. This repository models several peaked responses that inherit the property — the Gaussian pH term, the oxidiser Langmuir saturation, the IEP-referenced zeta terms. And the *better* the experiment — the more levels it ran — the more of them a two-point reading discards.

### Measured (`tools/interior_level_response_probe.py`, 83 axes at ≥ 3 levels)

| class | count | reading |
|---|---|---|
| `endpoint-blind` (endpoints agree, an interior level does not) | **0** | no axis changes class |
| `understated` (endpoints disagree by less than the sweep does) | **4** | worst **x1.9** |
| `inert` (no level moves the rate) | 22 | the incumbent reading was right |
| `agrees` | 57 | the endpoints already spanned the response |

| dataset | axis | levels | endpoint | full sweep |
|---|---|---|---|---|
| `us9422456b2_teos_silica_ph_pressure` | `slurry_ph` | 11 | 51.75% | **98.20%** |
| `li2021_oxide_silica_ph` | `slurry_ph` | 3 | 10.59% | **18.37%** |
| `dandu2009_sio2_ceria_ph_sweep` | `slurry_ph` | 9 | 83.41% | **97.12%** |
| `du2004_cu_h2o2_concentration_sweep` | `h2o2_vol_pct` | 6 | 76.78% | **89.00%** |

All four are pH or oxidiser sweeps, i.e. precisely the peaked terms the derivation predicts, and every one of them straddles its pack's declared optimum. Eleven two-level axes are counted and **excluded**: for them the two readings are the same measurement, so they can neither confirm nor refute anything.

### The honest reading: this fixes no verdict, and that is the point

Zero axes were misclassified. Every understated axis was already far above the 0.5% inert bar, so no `silent`/`declared` verdict, no `responsive_axes` list and no bucket changes, and **the median is unchanged at 18.9% / 19.5% held out** — the correct outcome for an instrument repair that touches no constant, term or prediction. What the repair removes is the *possibility* of a verdict nobody could have checked: an `endpoint-blind` axis would have been reported as inert with a 0.00% response, indistinguishable from a model that weighed the input and found it unimportant, and the corpus contains no device that would have contradicted it. The count of 0 is a measurement of this corpus's sweep designs, not a proof that the reader was safe — a single future dataset placing its extreme levels symmetrically about a declared optimum would have produced one.

**What was rejected.** Keeping the endpoint reading and merely *warning* when a sweep straddles a declared optimum was **rejected**: the straddle is detectable only for terms whose optimum a pack declares, and the oxidiser Langmuir's saturation and the zeta terms' IEP references are peaked without a declared peak key. Sub-sampling the interior (endpoints plus the midpoint) was **rejected**: it is the same class of arbitrary choice that produced §43, and the levels a paper ran are a bounded, already-loaded set — the honest reading costs one solver call per extra level. Special-casing the pH axis by name was **rejected** for §43's reason: the defect is in the reading, and a name list leaves every future peaked term exposed.

**The generalisable rule.** *When a probe's evaluation points are chosen by the DATA rather than by the probe, the §43 repair does not reach it — and the same exact cancellation can arrive through the experiment's design.* Read a response over every level that exists, not over the extremes of the range; the extremes are a summary, and a summary of a non-monotone function is not a measurement of it.

**What would resolve it.** Nothing external.

**Enforced by** `tests/test_axis_response_is_not_read_from_endpoints.py` (7 tests, every number re-measured through the shipping solver at run time — pinning `98.20%` as a literal would go stale the moment a pH constant is re-sourced, and a stale literal invites editing the claim instead of the code, which is how §40's correlation string happened): the probe must recover an **endpoint-responsive** axis or its whole output is disowned (§43's instrument control); at least one axis must still be measurably understated, by more than x1.1, or the restricted dataset list has gone stale; `residual_census._axis_response` — the function every admissibility filter consumes — must return **≥** the endpoint reading on every understated axis and strictly more on at least one; `inert_axis_scan`, which keeps its **own copy** of the comparison, must read the repaired response too, because a fix applied to one of two duplicated readers is how a closed limit reopens; the cancellation is re-derived on `ph_response` itself in the equal-floor case (exact to 1e-12, with the optimum required to sit above the mirror pair so a flat term cannot pass) and in the unequal-floor case (the packs disagree on their acid floors, and the residual must stay below a fifth of the interior response); two-level axes must be excluded **and** counted, so the section's counts are about the reader rather than about how many sweeps are short; and every reading must publish the levels it used, because §43 requires a zero response to be unquotable without what was tried. Calibrated against the bug: reverting either tool fails 2 of the 7.

## 45. A span RATIO cannot see DIRECTION: §37's veto statistic scores a prediction that moves backwards as agreement

§44 fixed readers whose evaluation POINTS were chosen by the publication. This section asks the same question one level up, about a reader's *reduction* rather than its sampling: `tools/ladder_span_probe.py` collapses each single-axis block to

```
span_ratio = (max/min PREDICTED) / (max/min MEASURED)
```

and docs/limits.md §37 uses the population of those ratios to **veto** deriving a corpus-wide steepening term ("geo-mean 0.98x, 8 of 13 under, sign test p = 0.581"). The reduction's advertised virtue is real: the shape score's one free multiplicative scale cancels out of a ratio of ratios, so no fit is involved. Its defect is that a span is a **magnitude**, and a magnitude cannot distinguish a prediction that moves the right amount the right way from one that moves the right amount **backwards**.

### The blindness is arithmetic, not statistical

Reverse a predicted series against the same measured series. Every predicted value still occurs, so `max/min` is unchanged and the span ratio is **identical**, while the log-space correlation flips from **+1 to −1**. That holds for any series, so — unlike §43's perturbation constants and unlike §44's evaluation points — no corpus change and no constant can retire it. It is a property of the statistic.

And this repository is exactly the kind that reaches it: the chemistry layer's peaked terms (the Gaussian pH response, the oxidiser Langmuir) can descend where a sweep straddling their declared optimum climbs.

### Measured (`tools/span_direction_probe.py`, the same 20 blocks §37 reads)

`r_log` = Pearson correlation of log(predicted) against log(measured) over the block's rows — logs because the scorer's error is multiplicative and its free scale is an additive offset there, so `r_log` is invariant to calibration exactly as the span ratio is. `pair` = whether the prediction's argmax/argmin rows are the measurement's.

| class | count | meaning |
|---|---|---|
| `anti` (`r_log` < 0) | **2** | the prediction moves against the data |
| `non-monotonic` (`r_log` ≥ 0, extremes do not pair) | 6 | the two spans are excursions between *different* condition pairs |
| `agrees` | 5 | extremes pair, direction positive |
| `declined` | 7 | the run declined the swept axis — no direction to read (§37's own rule) |

| dataset | axis | span ratio | `r_log` | already published as a failure? |
|---|---|---|---|---|
| `jani2025_cu_h2o2_acidic_chelator` | `oxidizer_wt_pct` | **0.90x** | −0.73 | yes — `beats_predicting_the_mean = False` |
| `netzband2020_thermal_oxide_ceria_ph` | `slurry_ph` | 2.98x | −0.19 | yes — same |

`jani2025` is the instructive one: measured rates climb 22820 → 25330 → 25780 Å/min over H2O2 3–6 wt% while the prediction falls 10783 → 10748 → 10572, and its span ratio of **0.90x** reads in §37's table as a block the model tracks to within 10%.

### The honest reading: a mechanism, not a defect count

**Both `anti` blocks already fail `beats_predicting_the_mean` in `score_report`,** so this reader adds no unreported failure and **the median is unchanged at 18.9% / 19.5% held out** — the correct outcome for an instrument repair that touches no constant, term or prediction (§44, §36). Re-running §37's sign test with the `anti` blocks removed moves it from 0.98x / p = 0.581 to 0.89x / p = 0.549: **§37's verdict does not depend on them**, which is worth stating because the opposite would have retracted a limit.

What the reader removes is the *possibility* of a verdict nobody could check. An `anti` block that still beat its own measured mean would be invisible to every existing device here — the median would see a modest shape error, `flat_prediction_census` a genuine non-flat prediction, `ladder_span_probe` a span ratio near 1 — and nothing in this repository would contradict it. The count of such blocks is **0 measured today**, not proven impossible.

### What was rejected

Adding a `direction` column to `ladder_span_probe` itself was **rejected**: §37's verdict is quoted from that tool's pooled output, and silently changing what it prints makes the quoted numbers unattributable — a separate reader keeps the audit trail. Excluding the two `anti` blocks from §37's population was **rejected**: they are predictions, not refusals, and this repository's rule is that dropping data to move a statistic is forbidden even when the statistic improves (the exclusion is *reported* above instead). Defining `anti` at some negative bar (e.g. `r_log < −0.3`) to "avoid noise" was **rejected**: the claim is a sign claim, and a threshold chosen to make a classification come out is a constant fitted to its own answer (§39). Fixing `netzband2020`'s pH optimum so the term climbs across pH 4–10 was **rejected as out of scope here** and is genuinely refuted elsewhere: `sti_ceria` already declares `ph_response_is_unimodal_but_this_system_is_not`, because the same pack must serve `dandu2009`'s 81x monotone sweep and this paper's V-shaped one (pH 4 = 198, pH 6 = 113, pH 8 = 200, pH 10 = 213 Å/min) — a *fall-then-rise* shape a unimodal term cannot produce at any peak or width. The direction failure is therefore a known functional-form gap, newly visible in the span statistic.

### The generalisable rule

*A fit-free reduction is not a neutral one.* §43 asked who chooses the perturbation, §44 who chooses the evaluation points; this asks **what the reduction throws away**. `max/min` discards the pairing between prediction and measurement, so it can only ever answer "how much", never "which way" — and a reader that cannot be wrong in a given direction will never report that direction.

**What would resolve it.** For the `netzband2020` block, a non-unimodal pH form with a source, which is the open question `sti_ceria` already declares. Nothing external is needed for the reader.

**Enforced by** `tests/test_span_ratio_is_blind_to_direction.py` (9 tests, all re-measured at run time — pinning today's 2/6/5/7 counts would go stale the moment a pH constant is re-sourced, and a stale literal invites editing the claim instead of re-running the probe, which is how §40's correlation string happened): the blindness is **proved as arithmetic** on a reversed series (identical span ratio, `r_log` +1 → −1), so no corpus change can retire the motivation; `r_log` is asserted invariant under the scorer's free scale over three decades, or it would be reporting the calibration; **the exit condition** — an `anti` block that beats its own measured mean must not exist, and that test is the one allowed to fail, with the repair named as the peaked term rather than the statistic; declined axes must receive **no** direction verdict, with a non-vacuity guard on that side of the split; both readers must select the **same blocks** with the same axis, n and span ratio, since two readers of one population drifting apart would be invisible; at least one block must still hide a direction defect behind a span ratio inside 0.5x–2.0x, or the finding has gone stale; `ANTI_BAR` is pinned at exactly 0.0; and the classifier must be able to **return every class** from synthetic input, because a classifier collapsed to one answer passes every corpus-level test here. Calibrated against the bug: deleting the `anti` branch fails 2 of the 9.
