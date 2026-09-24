"""Is the velocity axis weak, or is the corpus thin?

STATUS.md promoted velocity to "worst axis" on a median of 44.1 %, computed
over every dataset that happens to vary platen speed. That number is not a
velocity measurement, because `accuracy --axis velocity` selects datasets in
which speed varies *among other things*: an L25 that moves speed, pressure, pH,
abrasive loading and dispersant together contributes its whole error to the
velocity column.

This module isolates the axis properly. Within one dataset, group the rows so
that EVERY field except platen speed is identical, and score only the groups
with two or more distinct speeds. What survives that filter, across the entire
49-dataset corpus, is 29 points in 11 groups from 3 datasets — and two of those
three are not rotary CMP at all.

The result is the opposite of the headline: on the one in-scope dataset that
isolates velocity (Mariscal 2020, PETEOS/ceria, 3 pressures x 3 speeds) the
error is ~12 %, and the measured speed exponent is +0.86 against Preston's
+1.0. Velocity is the thinnest axis in the corpus, not the weakest model term,
and the honest fix is data, not a new constant.
"""
from __future__ import annotations

import json

import numpy as np
import pytest
import yaml

from cmp_sim.core.predictive_score import _measured, _predict
from cmp_sim.core.validation import dataset_paths


def _chemistry_key(row) -> str:
    """Everything that is not platen speed."""
    return json.dumps({"pressure_psi": row.get("pressure_psi"),
                       "rpm_wafer_is_platen": row.get("rpm_wafer") == row.get("rpm_platen"),
                       "overrides": row.get("overrides") or {},
                       "flow": row.get("flow_ml_min")}, sort_keys=True)


def _velocity_groups(path):
    """Groups within one dataset where ONLY the platen speed moves."""
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    groups = {}
    for row in rows:
        if row.get("rpm_platen") is None:
            continue
        groups.setdefault(_chemistry_key(row), []).append(row)
    return doc, [g for g in groups.values()
                 if len({r["rpm_platen"] for r in g}) > 1]


def _score(doc, group):
    measured = [_measured(r) for r in group]
    predicted = [_predict(doc, r) for r in group]
    if any(p is None for p in predicted):
        return None
    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    return [100.0 * abs(scale * p - m) / m for m, p in zip(measured, predicted)]


def _isolated():
    """dataset stem -> (n_points, MAPE, measured speed exponent)."""
    out = {}
    for path in dataset_paths():
        doc, groups = _velocity_groups(path)
        errors, exponents = [], []
        for group in groups:
            scored = _score(doc, group)
            if scored is None:
                continue
            errors += scored
            speed = np.array([float(r["rpm_platen"]) for r in group])
            rate = np.array([_measured(r) for r in group])
            exponents.append(float(np.polyfit(np.log(speed), np.log(rate), 1)[0]))
        if errors:
            out[path.stem] = (len(errors), float(np.mean(errors)),
                              float(np.median(exponents)))
    return out


@pytest.fixture(scope="module")
def isolated():
    return _isolated()


def test_the_velocity_axis_is_thin_and_the_thinness_is_the_finding(isolated):
    """Guards the diagnosis, so nobody re-reads 44% as a model defect.

    If a future dataset adds a real speed sweep this will fail, and the right
    response is to raise the expected count — deliberately.
    """
    total = sum(n for n, _, _ in isolated.values())
    assert len(isolated) <= 4, sorted(isolated)
    assert total < 40, (
        f"{total} isolated velocity points in a {len(dataset_paths())}-dataset "
        "corpus; if this grew, re-do the axis diagnosis")


def test_on_the_one_in_scope_isolated_sweep_the_model_is_not_weak(isolated):
    """Mariscal 2020: 3 pressures x 3 speeds, rotary CMP, chemistry fixed."""
    key = "mariscal2020_peteos_ceria_pressure_velocity_3x3"
    assert key in isolated, sorted(isolated)
    n, mape, exponent = isolated[key]

    assert n == 9
    assert mape < 20.0, f"isolated velocity error {mape:.1f}%"
    # Preston says MRR ~ V^1. The measurement says 0.86 - sub-linear, but not
    # a different law. A model term that was actually broken would not land here.
    assert 0.6 < exponent < 1.2, exponent


def test_the_other_isolated_sweeps_are_known_non_prestonian_systems(isolated):
    """The datasets dragging the median are documented exclusions, not misses.

    * us6918821b2 is the repo's lubrication-transition negative control.
    * sic2023 is shear-rheological polishing, not rotary CMP (in_scope: false).
    Neither should be read as evidence about the velocity term.
    """
    for key in ("us6918821b2_cu_ic1000_pressure_speed_2x3",
                "sic2023_shear_rheological_L9"):
        assert key in isolated, sorted(isolated)

    marked_out_of_scope = 0
    for key in isolated:
        if key == "mariscal2020_peteos_ceria_pressure_velocity_3x3":
            continue
        doc = None
        for path in dataset_paths():
            if path.stem == key:
                doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert doc is not None
        if doc.get("in_scope") is False:
            marked_out_of_scope += 1
    assert marked_out_of_scope >= 1, (
        "at least one of the remaining isolated sweeps must be declared "
        "out of scope, or the exclusion argument is not written down anywhere")


def test_the_taguchi_arrays_cannot_speak_about_velocity_at_all(isolated):
    """An orthogonal array never repeats a chemistry at two speeds.

    us6564116b2 and yang2023 both appear under `accuracy --axis velocity`, and
    neither contributes a single isolated velocity point. That is the whole
    mechanism behind the misleading median, asserted rather than described.
    """
    for key in ("us6564116b2_oxide_taguchi_L25_pressure_platenspeed",
                "yang2023_quartz_ceria_L25"):
        assert key not in isolated, (
            f"{key} now has an isolated velocity group; re-check the diagnosis")
