"""The oxidizer floor is a property of the MECHANICAL path, not of the film.

`rate = floor + (1 - floor) * shape(C)` — the floor is the abrasive-only rate
at zero oxidizer, as a fraction of the reference rate. The inherited knowledge
base is explicit that this constant is set by the mechanical path (abrasive
hardness, load) rather than by chemistry: it converges to 0.12-0.27 across four
independent free-abrasive metal systems and falls to ~0.02 with the abrasives
removed.

US 8,070,843 B2 is a **fixed-abrasive pad with an abrasive-free solution**.
There are no free abrasives to supply a 14 % mechanical background, and the
patent's own table says so: 96 Å/min at 0 wt% H₂O₂ against 2396 Å/min at
4.06 wt% is a floor of 0.040. Scored with the pack's free-abrasive 0.14, the
dataset reported 51.7 % — the worst oxidizer result in the corpus — with the
entire headline coming from that one row at +220 %.

These tests pin the distinction that makes this a correction rather than a
tune:

* the floor is READ from two rows of the printed table, not fitted;
* declaring it necessarily fixes the zero row (near-tautological), so the
  number that actually measures the model is the four oxidizer-bearing rows,
  and those are ~unchanged — 9.5 % before, 8.6 % after;
* the pack's own 0.14 must stay put, because it is right for the free-abrasive
  systems it was measured on.
"""
from __future__ import annotations

import copy

import pytest
import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, _predict, score_dataset
from cmp_sim.core.validation import dataset_paths

DATASET = "us8070843b2_w_h2o2_series"


def _path():
    for path in dataset_paths():
        if path.stem == DATASET:
            return path
    raise AssertionError(f"dataset {DATASET} not found")


def _doc():
    return yaml.safe_load(_path().read_text(encoding="utf-8"))


def _errors(doc):
    """Per-point percentage error with one fitted scale, in table order."""
    rows = doc["conditions"]
    measured = [_measured(r) for r in rows]
    predicted = [_predict(doc, r) for r in rows]
    assert all(p is not None for p in predicted)
    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    return [100.0 * abs(scale * p - m) / m for m, p in zip(measured, predicted)]


# ---------------------------------------------------------------------------
# the measurement
# ---------------------------------------------------------------------------

def test_the_floor_is_read_from_the_table_not_fitted():
    doc = _doc()
    rows = {r["overrides"]["oxidizer_wt_pct"]: _measured(r)
            for r in doc["conditions"]}

    # 96 A/min at zero H2O2, 2396 A/min at the 4.06 wt% reference row
    assert rows[0.0] == pytest.approx(96.0)
    assert rows[4.06] == pytest.approx(2396.0)
    measured_floor = rows[0.0] / rows[4.06]
    assert measured_floor == pytest.approx(0.040, abs=0.001)

    declared = doc["pack_overrides"]["oxidizer_mech_floor"]
    assert declared == pytest.approx(measured_floor, abs=0.001), (
        "the declared floor must BE the measured ratio, not a nearby fit")


def test_the_series_is_monotonic_so_it_cannot_locate_a_peak():
    """Guards the pack's `oxidizer_peak_wt_pct` staying `estimated`.

    Every row rises. Nothing here identifies where the Kaufman maximum sits,
    and a future edit that quietly fits a peak to this dataset is fitting an
    unobserved parameter.
    """
    doc = _doc()
    series = sorted((r["overrides"]["oxidizer_wt_pct"], _measured(r))
                    for r in doc["conditions"])
    rates = [rate for _, rate in series]
    assert rates == sorted(rates), series

    peak = load_pack("w_fe_oxidizer").param("oxidizer_peak_wt_pct")
    assert peak.confidence == "estimated", (
        "the peak is outside this data; it must not be promoted on its basis")


def test_the_iron_confound_is_bounded_by_the_near_duplicate_pair():
    """Fe varies 5-1180 ppm across the table, which is not controlled.

    The 4.06 / 4.07 wt% pair brackets it: a 236x change in Fe moves the rate by
    under 1 %, so Fe is not the governing variable in this range. If those two
    rows were ever dropped as 'duplicates', this argument would vanish.
    """
    doc = _doc()
    rows = {r["overrides"]["oxidizer_wt_pct"]: _measured(r)
            for r in doc["conditions"]}
    assert 4.06 in rows and 4.07 in rows
    assert abs(rows[4.07] - rows[4.06]) / rows[4.06] < 0.01


# ---------------------------------------------------------------------------
# what declaring it does, stated honestly
# ---------------------------------------------------------------------------

def test_declaring_the_floor_removes_a_one_point_headline():
    doc = _doc()
    with_floor = _errors(doc)

    without = copy.deepcopy(doc)
    without.pop("pack_overrides")
    pack_floor = _errors(without)

    # the pack's free-abrasive floor blows up exactly one row: the zero point
    assert pack_floor[0] > 150.0, pack_floor
    assert with_floor[0] < 20.0, with_floor
    assert sum(pack_floor) / len(pack_floor) > 45.0
    assert sum(with_floor) / len(with_floor) < 15.0


def test_the_shape_did_not_improve_and_that_is_the_honest_claim():
    """The four oxidizer-bearing rows are ~unchanged. Nothing was tuned.

    Declaring the floor necessarily fixes the zero row, so quoting the whole
    51.7% -> 8.7% move as a modelling improvement would be self-congratulation.
    The rows that actually test the shape must stay where they were.
    """
    doc = _doc()
    with_floor = _errors(doc)[1:]
    without = copy.deepcopy(doc)
    without.pop("pack_overrides")
    pack_floor = _errors(without)[1:]

    mean_with = sum(with_floor) / len(with_floor)
    mean_without = sum(pack_floor) / len(pack_floor)
    assert abs(mean_with - mean_without) < 3.0, (mean_with, mean_without)
    assert mean_with < 12.0


def test_the_pack_keeps_its_own_free_abrasive_floor():
    """The correction belongs to the DATASET, not to the pack.

    0.14 is right for the free-abrasive metal systems it was measured on; this
    patent is a fixed-abrasive pad. Merging the two would break the other.
    """
    floor = load_pack("w_fe_oxidizer").param("oxidizer_mech_floor")
    assert floor.value == pytest.approx(0.14)
    assert floor.confidence == "literature"


def test_the_dataset_stays_rank_only():
    """The absolute-rate bias is a separate, unfixed finding.

    The pack's Kp sits 1.8-3.4x above three independent Preston
    back-calculations. Nothing in this change touches that, so the exemption
    must survive.
    """
    doc = _doc()
    assert doc["rank_only"] is True
    assert "Kp" in doc["rank_only_ruling"]
    assert doc["used_for_calibration"] is False


def test_the_scored_result_matches_what_the_docs_claim():
    scored = score_dataset(_path())
    assert scored.n == 5
    assert scored.axes == ["oxidizer_wt_pct"]
    assert scored.shape_mape is not None and scored.shape_mape < 12.0
    assert scored.beats_flat
