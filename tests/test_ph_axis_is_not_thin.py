"""The pH axis is not thin — unlike velocity — and it is genuinely the weakest.

When velocity looked like the worst axis, isolating it showed the headline was
an artefact: only 29 points in the whole corpus vary speed with everything else
fixed, and on the one isolated sweep the error was 11.7 %, not 44.1 %. The same
diagnosis had to be run on pH before touching any pH constant, because a
pooled median cannot tell "the term is wrong" from "the datasets move four
things at once".

pH answers the opposite way. Grouping rows so that ONLY pH varies leaves 12
groups and 66 points — more than twice velocity's isolated set — and the
isolated median (~30 %) is not much better than the pooled one (39.3 %). So the
pH term really is the weakest physics in the model, and the corpus can support
work on it.

This file pins that diagnosis, and the structural finding it produced: the pH
optimum belongs to the SLURRY SYSTEM. Three colloidal-silica sweeps on the same
TEOS film peak nine pH units apart, ordered by the abrasive's surface charge:

    anionic silica          peak at or below pH 2    (oxide_silica_anionic)
    cationic core-shell     peak pH 4.9              (oxide_silica_aminosilane)
    plain silica            peak pH 11               (oxide_silica)

Each is its own pack. Widening one bell to cover them would predict a rate
everywhere and the right rate nowhere.
"""
from __future__ import annotations

import statistics
from collections import defaultdict

import pytest
import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import (_measured, _predict_with_gate,
                                           score_dataset)
from cmp_sim.core.validation import dataset_paths


def _held_constant(row: dict) -> tuple:
    """Everything the row fixes APART from pH."""
    overrides = dict(row.get("overrides") or {})
    overrides.pop("slurry_ph", None)
    return (row.get("pressure_psi"), row.get("rpm_platen"), row.get("rpm_wafer"),
            tuple(sorted((k, str(v)) for k, v in overrides.items())))


def _isolated_groups():
    """Every run of >=3 rows where pH is the ONLY thing that changes."""
    groups = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
        buckets: dict[tuple, list] = defaultdict(list)
        for row in rows:
            if (row.get("overrides") or {}).get("slurry_ph") is not None:
                buckets[_held_constant(row)].append(row)
        for members in buckets.values():
            phs = {(m["overrides"])["slurry_ph"] for m in members}
            if len(phs) >= 3:
                groups.append((path.stem, doc, members))
    return groups


def _shape_error(doc: dict, rows: list) -> float | None:
    measured, predicted = [], []
    for row in rows:
        value, gate, _declined = _predict_with_gate(doc, row)
        if value is None:
            return None
        if gate:
            continue
        measured.append(_measured(row))
        predicted.append(value)
    if len(measured) < 3:
        return None
    scale = sum(m * p for m, p in zip(measured, predicted)) / sum(p * p for p in predicted)
    return 100.0 * sum(abs(scale * p - m) / m
                       for m, p in zip(measured, predicted)) / len(measured)


def _scored_groups():
    out = []
    for stem, doc, rows in _isolated_groups():
        err = _shape_error(doc, rows)
        if err is not None:
            out.append((stem, err, len(rows)))
    return out


# ---------------------------------------------------------------------------
# the diagnosis
# ---------------------------------------------------------------------------

def test_the_pH_axis_has_enough_isolated_points_to_work_on():
    """The velocity test, run on pH, with the opposite answer."""
    groups = _isolated_groups()
    points = sum(len(rows) for _, _, rows in groups)
    assert len(groups) >= 10, len(groups)
    assert points >= 60, (
        f"only {points} isolated pH points; if the corpus has shrunk to "
        "velocity's scale, stop refitting pH and say the axis is thin")


def test_isolating_pH_does_not_rescue_it_the_way_it_rescued_velocity():
    """This is what makes pH a real weakness rather than a pooling artefact.

    Velocity went 44.1% -> 11.7% once isolated. pH barely moves, so the error
    is in the term, not in the mixture of datasets.
    """
    scored = _scored_groups()
    median = statistics.median(e for _, e, _ in scored)
    assert 20.0 < median < 40.0, median


def test_no_isolated_pH_group_is_silently_unrunnable():
    """A group that cannot run must be a declared gate, not a quiet failure."""
    for stem, doc, rows in _isolated_groups():
        if _shape_error(doc, rows) is None:
            gates = [g for _v, g, _d in
                     (_predict_with_gate(doc, r) for r in rows) if g]
            missing_force = not any(r.get("pressure_psi") for r in rows)
            assert gates or missing_force, (
                f"{stem} silently fails to score on an isolated pH sweep")


# ---------------------------------------------------------------------------
# the structural finding: three silica systems, three optima
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pack_name,expected_peak", [
    ("oxide_silica_anionic", 2.0),
    ("oxide_silica_aminosilane", 4.9),
    ("oxide_silica", 11.0),
])
def test_each_silica_system_keeps_its_own_optimum(pack_name, expected_peak):
    assert load_pack(pack_name).param("ph_peak").value == pytest.approx(
        expected_peak, abs=0.25)


def test_the_optima_are_ordered_by_the_abrasives_surface_charge():
    """Not an accident of fitting: anionic < cationic < uncharged-alkaline.

    An anionic particle is repelled by the (negative) TEOS surface as soon as
    the oxide charges up past its IEP, so removal survives only at the acid
    end. A cationic shell is ATTRACTED, peaking mid-acid until its amine
    deprotonates. Plain silica has neither and follows alkaline hydrolysis.
    """
    peaks = [load_pack(p).param("ph_peak").value for p in
             ("oxide_silica_anionic", "oxide_silica_aminosilane", "oxide_silica")]
    assert peaks == sorted(peaks), peaks
    assert peaks[-1] - peaks[0] > 8.0, "the three systems must stay far apart"


def test_splitting_the_packs_did_not_disturb_the_other_systems():
    def _score(stem):
        return score_dataset(next(p for p in dataset_paths() if p.stem == stem))

    assert _score("li2021_oxide_silica_ph").shape_mape < 1.0
    assert _score("us9422456b2_teos_silica_ph_pressure").shape_mape < 30.0
    assert _score("cn109609035b_oxide_anionic_silica_ph").shape_mape < 40.0


def test_the_single_bell_limit_is_recorded_not_fitted_around():
    """The anionic sweep turns UP at pH 6 and a decaying bell cannot do that.

    The pack must say so rather than absorbing the upturn by widening, and the
    residual must remain visible.
    """
    from pathlib import Path

    import cmp_sim

    text = (Path(cmp_sim.__file__).parent / "data" / "params"
            / "oxide_silica_anionic.yaml").read_text(encoding="utf-8")
    assert "SECOND mechanism" in text, (
        "the pack must record that the pH 6 upturn needs a second channel")
    assert "not a wider bell" in text
    score = score_dataset(next(p for p in dataset_paths()
                               if p.stem == "cn109609035b_oxide_anionic_silica_ph"))
    assert score.shape_mape > 20.0, (
        "fitted too well for a single bell against the pH 6 upturn — check "
        "whether the upturn point was dropped")
