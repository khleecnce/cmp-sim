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
