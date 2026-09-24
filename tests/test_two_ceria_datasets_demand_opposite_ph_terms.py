"""Two ceria datasets demand incompatible pH terms, and the pack keeps the right one.

netzband2020_thermal_oxide_ceria_ph was the last large undiagnosed miss: 49.2%
shape error, inside sti_ceria's declared pH range, already known NOT to share a
second pH channel with the other ceria residuals.

FIRST, TWO EXPLANATIONS RULED OUT.

Not a scale offset. The dataset runs on a BENCHTOP polisher (Allied MultiPrep,
2.25 cm2 coupon) rather than a 300 mm wafer, so the engine computes a sliding
velocity that has nothing to do with the real experiment, and absolute rates are
off by 8x. But the reported 49.2% is ALREADY scale-free: fitting the best common
scale k = 0.128 leaves exactly 49.2%. The tool mismatch is real and costs
nothing, because the metric divides it out.

Not the pH range either. All four points (pH 4/6/8/10) sit inside sti_ceria's
declared 2.0-10.0.

WHAT IT ACTUALLY IS: A VALLEY, WHICH A SINGLE BELL CANNOT MAKE.

    pH        4     6     8     10
    measured 198   113   200   213      normalised 0.93 / 0.53 / 0.94 / 1.00
    model   2032   792   362   362      normalised 1.00 / 0.39 / 0.18 / 0.18

The measurement is high at pH 4, dips at pH 6, and recovers at pH 8-10 — a
double extremum, which Netzband attributes to two isoelectric points: the oxide's
(pH 2-3) and ceria's (~8), with pH 6 optimal for neither. `ph_response` is
unimodal, so between its ends it can rise-then-fall but never fall-then-rise. No
parameter choice produces a valley. The failure is structural, not numerical.

AND THE BEST AVAILABLE COMPROMISE IS THE ONE THE PACK ALREADY HAS.

Searching the full (peak, width, floor, acid_floor) grid for netzband alone finds
a much better fit — 15.0% against 49.2% — at peak 8.50, width 0.75, floor 0.95,
acid_floor 0.70. It works by making the pH response nearly FLAT, which suits a
dataset whose rates only span 1.9x.

That fit is catastrophic for the experiment the constants were actually fitted to.
dandu2009 sweeps nine pH points on the same pack and swings 81x (43 to 3504
A/min):

    current constants (peak 4.5, width 1.2, floor 0.15, acid 0.012):   31.5%
    netzband's preferred flat fit (8.5 / 0.75 / 0.95 / 0.70):         492.6%

So the two datasets do not disagree about a detail, they demand opposite
functional forms: one needs a sharp 81x peak, the other a flat response with a
notch. A single unimodal term serves the first, and the pack correctly keeps it.

This is the third time this session that the honest answer has been to leave a
term alone and record why — like the velocity exponent and the pressure-coupled
oxidiser sign. What would resolve it is a second pH channel tied to the abrasive's
isoelectric point, but a universal second channel was already tested and
falsified, and one benchtop dataset is not grounds for inventing a per-pack one.
"""
from __future__ import annotations

import statistics

import yaml

from cmp_sim.api import run_recipe
from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, _recipe_for, score_dataset
from cmp_sim.core.validation import dataset_paths
from cmp_sim.models.chemical_rate import ph_response

NETZBAND = "netzband2020_thermal_oxide_ceria_ph"
DANDU = "dandu2009_sio2_ceria_ph_sweep"

#: the fit that is better for netzband alone and ruinous for dandu2009
FLAT_FIT = dict(ph_peak=8.5, width=0.75, floor=0.95, acid_floor=0.70)


def _doc(stem):
    return yaml.safe_load(next(p for p in dataset_paths() if p.stem == stem)
                          .read_text(encoding="utf-8"))


def _series(stem):
    """(pH values, measured rates) for a pH sweep."""
    doc = _doc(stem)
    return ([row["overrides"]["slurry_ph"] for row in doc["conditions"]],
            [_measured(row) for row in doc["conditions"]])


def _shape_error(phs, measured, **kwargs):
    """Scale-free error of a bell against a measured series."""
    predicted = [ph_response(ph, kwargs["ph_peak"], kwargs["width"],
                             kwargs["floor"], kwargs["acid_floor"])
                 for ph in phs]
    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    return 100 * statistics.mean(
        [abs(scale * p - m) / m for m, p in zip(measured, predicted)])


def _pack_fit():
    pack = load_pack("sti_ceria")

    def value(key):
        param = pack.param(key)
        return param.value if hasattr(param, "value") else param

    return dict(ph_peak=value("ph_peak"), width=value("ph_response_width"),
                floor=value("ph_mechanical_floor"),
                acid_floor=value("ph_acid_mechanical_floor"))


# ---------------------------------------------------------------------------
# the two explanations that do NOT apply
# ---------------------------------------------------------------------------

def test_the_reported_error_is_already_scale_free():
    """The benchtop tool mismatch is divided out by the metric."""
    doc = _doc(NETZBAND)
    measured, predicted = [], []
    for row in doc["conditions"]:
        measured.append(_measured(row))
        predicted.append(
            run_recipe(_recipe_for(doc, row))["removal_rate_A_per_min"])

    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    scale_free = 100 * statistics.mean(
        [abs(scale * p - m) / m for m, p in zip(measured, predicted)])

    assert scale < 0.2, (
        f"common scale {scale:.3f}: absolute rates are off ~8x, as expected for "
        "a 2.25 cm2 benchtop coupon scored with 300 mm wafer kinematics")
    assert abs(scale_free - score_dataset(
        next(p for p in dataset_paths() if p.stem == NETZBAND)
    ).shape_mape) < 1.0, (
        "the reported error must be the scale-free one, or the tool mismatch "
        "would be doing the damage")


def test_every_point_is_inside_the_packs_declared_ph_range():
    phs, _ = _series(NETZBAND)
    pack = load_pack("sti_ceria")
    span = pack.param("ph_valid_range")
    low, high = (span.value if hasattr(span, "value") else span)
    assert all(low <= ph <= high for ph in phs), (phs, low, high)


# ---------------------------------------------------------------------------
# what it actually is: a valley
# ---------------------------------------------------------------------------

def test_the_measurement_has_a_valley_not_a_peak():
    phs, measured = _series(NETZBAND)
    assert phs == [4.0, 6.0, 8.0, 10.0], phs

    # high, dip, recover
    assert measured[1] < measured[0] * 0.75, measured
    assert measured[2] > measured[1] * 1.5, measured
    assert measured[3] >= measured[2], measured

    # and the whole span is narrow, unlike dandu2009's 81x
    assert max(measured) / min(measured) < 2.5, measured


def test_a_single_bell_cannot_produce_a_valley():
    """Structural, not numerical: ph_response is unimodal."""
    phs, _ = _series(NETZBAND)
    for peak in (2.0, 4.5, 6.0, 8.5, 11.0):
        for width in (0.5, 1.2, 3.0):
            response = [ph_response(ph, peak, width, 0.15, 0.012)
                        for ph in phs]
            interior_dips = [i for i in (1, 2)
                             if response[i] < response[i - 1]
                             and response[i] < response[i + 1]]
            assert not interior_dips, (
                f"peak={peak} width={width} produced a dip at {interior_dips}; "
                "if ph_response has gained a second channel this whole "
                "diagnosis needs redoing")


# ---------------------------------------------------------------------------
# and why the pack keeps the constants it has
# ---------------------------------------------------------------------------

def test_the_flat_fit_is_better_for_netzband():
    phs, measured = _series(NETZBAND)
    assert _shape_error(phs, measured, **FLAT_FIT) < 25.0
    assert _shape_error(phs, measured, **_pack_fit()) > 40.0


def test_and_ruinous_for_the_dataset_the_constants_were_fitted_to():
    phs, measured = _series(DANDU)
    assert max(measured) / min(measured) > 50.0, (
        "dandu2009's 81x swing is what needs a sharp peak")

    current = _shape_error(phs, measured, **_pack_fit())
    flat = _shape_error(phs, measured, **FLAT_FIT)

    assert current < 40.0, current
    assert flat > 300.0, (
        f"the flat fit scores {flat:.1f}% on dandu2009; the argument for keeping "
        "the current constants rests on this being catastrophic")
    assert flat > current * 10, (current, flat)


def test_the_miss_is_left_in_place_as_an_honest_one():
    score = score_dataset(next(p for p in dataset_paths() if p.stem == NETZBAND))
    assert score.shape_mape > 40.0, (
        "if netzband has improved, check what was changed and whether dandu2009 "
        "survived it")
    assert score.error is None, "it must still be scored, not declined"
