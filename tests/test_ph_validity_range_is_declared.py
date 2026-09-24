"""A peak pinned to the edge of the data has an UNMEASURED side. Say so.

Three packs in this repository now carry a `ph_peak` that is deliberately a
BOUND rather than a fitted optimum: the free fit wanted a peak outside the
measured range, and extrapolating a maximum to a pH nobody polished at was
refused. `oxide_silica_anionic` (2.0), `cu_alkaline_benzenesulfonic` (6.2) and
`cu_h2o2_bta` (3.0) all sit at the LOWEST pH their source table contains.

That discipline fixed one problem and created a quieter one. When the peak is
the edge of the data, everything on the far side of it is the assumed bell
shape and nothing else — and `ph_acid_mechanical_floor` is frequently 0,
because there is no measured acid limb to floor. The model then decays towards
zero with total confidence:

    oxide_silica_anionic at pH 2.0 (measured)     213.60 A/min
    oxide_silica_anionic at pH 1.0 (unmeasured)     3.90 A/min
    oxide_silica_anionic at pH 0.5 (unmeasured)     0.00 A/min

A CMP slurry that removes exactly nothing is not a prediction; it is the tail
of a Gaussian being read as physics. Worse, the existing "2.5 widths from the
optimum" warning does not fire there — at pH 1.0 the distance is 2.0 widths, so
the number came back clean.

So each pack now declares `ph_valid_range`, the span of the source table its pH
constants were fitted to, and the engine warns when asked outside it, naming
the floor it is using and saying explicitly that a ZERO floor makes the result
a refusal rather than a number.

This is the validity-range half of the blindness audit: the audit asks whether
a pack declares a term at all, this asks whether the term states where it is
allowed to be believed.
"""
from __future__ import annotations

import yaml

from cmp_sim.api import run_recipe
from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths

#: pack -> the dataset whose pH span defines its validity range
BOUNDED_PEAK_PACKS = {
    "oxide_silica_anionic": "cn109609035b_oxide_anionic_silica_ph",
    "cu_alkaline_benzenesulfonic": "us9200180b2_cu_ph_alkaline_sweep",
    "cu_h2o2_bta": "us20080090500a1_cu_ph_silica_cross",
}


def _value(pack, key):
    param = pack.param(key)
    return param.value if hasattr(param, "value") else param


def _doc(stem: str) -> dict:
    return yaml.safe_load(
        next(p for p in dataset_paths() if p.stem == stem)
        .read_text(encoding="utf-8"))


def _measured_ph_span(stem: str) -> tuple[float, float]:
    phs = [row["overrides"]["slurry_ph"] for row in _doc(stem)["conditions"]
           if (row.get("overrides") or {}).get("slurry_ph") is not None]
    return min(phs), max(phs)


def _warnings_at(stem: str, ph: float):
    doc = _doc(stem)
    row = dict(doc["conditions"][0])
    row["overrides"] = dict(row["overrides"])
    row["overrides"]["slurry_ph"] = ph
    result = run_recipe(_recipe_for(doc, row))
    return result, [str(w) for w in (result.get("warnings") or [])]


# ---------------------------------------------------------------------------
# every bounded-peak pack declares the range it was measured over
# ---------------------------------------------------------------------------

def test_each_bounded_peak_pack_declares_its_valid_range():
    for pack_name in BOUNDED_PEAK_PACKS:
        span = _value(load_pack(pack_name), "ph_valid_range")
        assert span is not None, f"{pack_name} has no ph_valid_range"
        assert len(span) == 2 and span[0] < span[1], (pack_name, span)


def test_the_declared_range_matches_the_source_table():
    """The range must be the DATA's span, not a wider claim."""
    for pack_name, stem in BOUNDED_PEAK_PACKS.items():
        low, high = _value(load_pack(pack_name), "ph_valid_range")
        measured_low, measured_high = _measured_ph_span(stem)
        assert abs(low - measured_low) < 0.51, (pack_name, low, measured_low)
        assert abs(high - measured_high) < 0.51, (pack_name, high, measured_high)


def test_the_peak_sits_at_the_edge_of_the_declared_range():
    """That is what makes one side unmeasured, and the warning necessary."""
    for pack_name in BOUNDED_PEAK_PACKS:
        pack = load_pack(pack_name)
        peak = _value(pack, "ph_peak")
        low, high = _value(pack, "ph_valid_range")
        assert peak in (low, high) or abs(peak - low) < 0.51, (pack_name, peak, low)


# ---------------------------------------------------------------------------
# and the engine refuses to be quiet outside it
# ---------------------------------------------------------------------------

def test_a_pH_below_the_measured_range_is_warned_about():
    _result, warnings = _warnings_at(
        BOUNDED_PEAK_PACKS["oxide_silica_anionic"], 1.0)
    hits = [w for w in warnings if "OUTSIDE the range" in w]
    assert hits, warnings
    assert "below it" in hits[0]


def test_a_zero_acid_floor_is_called_a_refusal_not_a_number():
    """The specific trap: 0.00 A/min returned with confidence."""
    result, warnings = _warnings_at(
        BOUNDED_PEAK_PACKS["oxide_silica_anionic"], 0.5)
    hits = [w for w in warnings if "OUTSIDE the range" in w]
    assert hits, warnings
    assert "ZERO" in hits[0] and "refusal" in hits[0], hits[0]
    # and the rate really is the pathological one this guards
    assert result["removal_rate_A_per_min"] < 1.0


def test_inside_the_range_there_is_no_range_warning():
    for ph in (2.0, 4.0, 6.0):
        _result, warnings = _warnings_at(
            BOUNDED_PEAK_PACKS["oxide_silica_anionic"], ph)
        assert not [w for w in warnings if "OUTSIDE the range" in w], (ph, warnings)


def test_a_supported_floor_is_reported_without_the_refusal_language():
    """Above the range the alkaline floor IS measured, so the wording differs."""
    _result, warnings = _warnings_at(
        BOUNDED_PEAK_PACKS["oxide_silica_anionic"], 9.0)
    hits = [w for w in warnings if "OUTSIDE the range" in w]
    assert hits and "above it" in hits[0]
    assert "ZERO" not in hits[0], hits[0]


def test_the_existing_width_warning_did_not_already_cover_this():
    """Why the new warning was needed: at pH 1.0 the old one stays silent."""
    _result, warnings = _warnings_at(
        BOUNDED_PEAK_PACKS["oxide_silica_anionic"], 1.0)
    assert not [w for w in warnings if "widths from the" in w], (
        "the 2.5-widths warning now fires here too; if the pack's width "
        "changed, re-check whether ph_valid_range is still adding anything")
