"""The copper pH optimum is a BOUND, not a fitted peak — and from ONE system.

`cu_h2o2_bta` carried `ph_peak: 4.0` at `confidence: low`, with the note "a
sweep across pH 2-6 would pin it". That sweep was already in the repository.

US 2008/0090500 A1 TABLE 4 runs pH 3/4/5/6 at three silica loadings with
glycine, BTA, H2O2, load, speeds, flow and time all held fixed — the same table
`cu_ph_acid_k` was back-fitted from — and the rate falls monotonically at every
loading. There is no interior maximum, so the optimum lies AT OR BELOW pH 3 and
a peak at 4.0 placed the model's maximum inside a measured falling limb.

THE TRAP THIS FILE ALSO GUARDS. US 9,200,180 B2 continues the fall to pH 9.9
and pooling both legs gives 17 points instead of 12 — but that series is
BTA-free and benzenesulfonic-based, and the repository already files it under
a SEPARATE pack (`cu_alkaline_benzenesulfonic`). Pooling them to tighten a
constant would manufacture agreement between two slurry systems, the exact
error that `oxide_silica_aminosilane` was split off to avoid. The fitted values
happen to be the same either way; the JUSTIFICATION is not, and only the
system-matched 12 points may be cited.

These tests fix the evidence, the discipline, and the honest scope of the
claim — including that this change does not move the corpus median at all,
because the acidic table prints no down force and cannot be scored.
"""
from __future__ import annotations

import pytest
import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured
from cmp_sim.core.validation import dataset_paths
from cmp_sim.models.chemical_rate import ph_response

ACIDIC = "us20080090500a1_cu_ph_silica_cross"
ALKALINE = "us9200180b2_cu_ph_alkaline_sweep"


def _doc(stem: str) -> dict:
    for path in dataset_paths():
        if path.stem == stem:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise AssertionError(f"dataset {stem} not found")


def _acidic_series() -> list[dict]:
    """One {pH: rate} dict per silica loading — everything else held fixed."""
    by_loading: dict[float, dict[float, float]] = {}
    for row in _doc(ACIDIC)["conditions"]:
        ov = row["overrides"]
        by_loading.setdefault(ov["abrasive_wt_pct"], {})[ov["slurry_ph"]] = _measured(row)
    return list(by_loading.values())


def _mape(peak: float, width: float, floor: float) -> float:
    """Shape error over the 12 system-matched points, one free scale each."""
    errs: list[float] = []
    for s in _acidic_series():
        phs = sorted(s)
        pred = [ph_response(p, peak, width, floor, floor) for p in phs]
        meas = [s[p] for p in phs]
        scale = sum(m * p for m, p in zip(meas, pred)) / sum(p * p for p in pred)
        errs += [abs(scale * p - m) / m for m, p in zip(meas, pred)]
    return 100.0 * sum(errs) / len(errs)


def _pack():
    return load_pack("cu_h2o2_bta")


# ---------------------------------------------------------------------------
# the evidence
# ---------------------------------------------------------------------------

def test_the_acidic_leg_falls_at_every_abrasive_loading():
    """Three independent series, same direction. Not one noisy sweep."""
    series = _acidic_series()
    assert len(series) == 3
    for s in series:
        assert sorted(s) == [3.0, 4.0, 5.0, 6.0]
        rates = [s[p] for p in sorted(s)]
        assert rates == sorted(rates, reverse=True), s


def test_there_is_no_interior_maximum_so_the_peak_is_a_bound():
    for s in _acidic_series():
        best_ph = max(s, key=lambda p: s[p])
        assert best_ph == min(s), (
            "the highest rate must sit at the LOWEST measured pH; an interior "
            "maximum would make the optimum measurable rather than bounded")


# ---------------------------------------------------------------------------
# the discipline
# ---------------------------------------------------------------------------

def test_the_peak_sits_at_the_edge_of_the_data_not_beyond_it():
    lowest_measured = min(p for s in _acidic_series() for p in s)
    assert _pack().param("ph_peak").value == pytest.approx(lowest_measured), (
        "the peak must be the lowest MEASURED pH — placing it lower is "
        "extrapolating into pH nobody probed")


def test_the_alkaline_sweep_is_a_different_slurry_system_and_is_excluded():
    """The anti-pooling rule, enforced from both ends."""
    assert _doc(ALKALINE)["pack"] == "cu_alkaline_benzenesulfonic"
    assert _doc(ACIDIC)["pack"] == "cu_h2o2_bta"
    for key in ("ph_peak", "ph_response_width"):
        param = _pack().param(key)
        assert ACIDIC in param.source, key
        assert ALKALINE not in param.source, (
            f"{key} must not be justified on a BTA-free benzenesulfonic "
            "series; that is a different pack")


def test_the_cross_system_floor_is_labelled_as_cross_system():
    """The floor IS taken from the other system, deliberately. It must say so
    rather than look like same-system evidence."""
    floor = _pack().param("ph_mechanical_floor")
    assert ALKALINE in floor.source
    assert "CROSS-SYSTEM" in floor.note
    assert "TODO(owner)" in floor.note


def test_the_refit_improves_the_system_matched_shape():
    pack = _pack()
    floor = pack.param("ph_mechanical_floor").value
    now = _mape(pack.param("ph_peak").value,
                pack.param("ph_response_width").value, floor)
    before = _mape(4.0, 4.1, floor)          # the previous pack values
    assert now < before
    assert now < 5.0, now


def test_the_width_is_not_claimed_to_more_precision_than_the_fit_supports():
    """4.0 and 5.0 score within ~1 point of the optimum, so the note must warn
    against reading 4.45 as precise."""
    floor = _pack().param("ph_mechanical_floor").value
    at_best = _mape(3.0, 4.45, floor)
    assert abs(_mape(3.0, 4.0, floor) - at_best) < 1.5
    assert abs(_mape(3.0, 5.0, floor) - at_best) < 1.5
    assert "do not read 4.45 as precise" in _pack().param("ph_response_width").note


def test_the_model_no_longer_predicts_a_rise_where_the_patent_measures_a_fall():
    """The concrete defect: peak 4.0 made pH 3 -> 4 go UP."""
    pack = _pack()
    peak = pack.param("ph_peak").value
    width = pack.param("ph_response_width").value
    floor = pack.param("ph_mechanical_floor").value
    shape = [ph_response(p, peak, width, floor, floor) for p in (3.0, 4.0, 5.0, 6.0)]
    assert shape == sorted(shape, reverse=True), shape

    old = [ph_response(p, 4.0, 4.1, floor, floor) for p in (3.0, 4.0)]
    assert old[1] > old[0], "the old value really did predict a rise"


# ---------------------------------------------------------------------------
# the honest scope
# ---------------------------------------------------------------------------

def test_this_change_is_invisible_to_the_corpus_score():
    """The acidic table prints no down force, so it cannot be scored.

    The justification is shape against the printed table. If a future edit
    makes this dataset scorable, this test should fail and be replaced by a
    real scored assertion rather than deleted.
    """
    doc = _doc(ACIDIC)
    assert not any(r.get("pressure_psi") for r in doc["conditions"])
    assert doc["used_for_calibration"] is True, (
        "and it is calibration data, so it could not carry a held-out claim "
        "even if it were scorable")


def test_the_bound_is_labelled_as_a_bound():
    peak = _pack().param("ph_peak")
    assert "UPPER BOUND" in peak.note
    assert "at or below" in peak.note.lower()
    assert peak.confidence == "med", (
        "a bound from 12 points beats 'low', but it is not a measured "
        "optimum and must not be promoted to 'literature'")
