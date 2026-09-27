"""A dataset can sweep an axis that lives on the ROW, and nothing was looking.

`tools/inert_axis_scan.py` reported **0 silent inert axes** across 94 swept
axes, and every admissibility filter in the repo reads the same axis list from
`core.predictive_score._varying_axes`.  That function read exactly three places:
``row["pressure_psi"]``, ``row["rpm_platen"]``, and the keys of
``row["overrides"]``.  A validation row is a free-form mapping, so a dataset
could vary a process input that sat straight on the row -- and two did:

* ``yang2023_quartz_ceria_L25`` sweeps slurry flow over **5 levels**.  The rate
  does not respond to flow in any run ever scored (the supply layer is a pure
  diagnostic unless a pack calibrates ``starvation_length_m``, and none does),
  and nothing said so in a machine-readable form.  The scorer therefore counted
  the flat response as a prediction -- the §36 failure, recurring in the space
  §36 could not see.
* ``us9422456b2_teos_silica_ph_pressure`` publishes a measured zeta potential at
  **10 levels**, and the scorer's recipe builder never put it into the recipe.
  The model was not inert on zeta; it was never asked.

These tests pin BOTH halves, because either one alone can be satisfied while
restoring the undetectable state: the axes must be published, and the refusals
must be machine-readable.  Everything is re-measured at test time from the
corpus, so a new dataset carrying a row-level axis is checked with no edit here.
"""
from __future__ import annotations

import yaml

from cmp_sim.core.declined_axes import declined_axes
from cmp_sim.core.predictive_score import (
    ROW_LEVEL_AXES, dataset_paths, _measured, _recipe_for, _varying_axes,
    score_dataset,
)
from tools.row_level_axis_scan import scan


def _doc(stem: str):
    path = next(p for p in dataset_paths() if p.stem == stem)
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    return path, doc, rows


def test_a_row_level_sweep_is_published_as_an_axis():
    """Every row-level key whose value varies must appear in the axis list.

    Measured from the corpus, not from a list of dataset names: a new file that
    sweeps flow on the row is covered without touching this test.
    """
    missed = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
        if len(rows) < 3:
            continue
        axes = set(_varying_axes(rows))
        for key, name in ROW_LEVEL_AXES.items():
            values = {r.get(key) for r in rows} - {None}
            if len(values) > 1 and name not in axes:
                missed.append(f"{path.stem}: {key} has {len(values)} levels "
                              f"but '{name}' is not in the axis list")
    assert not missed, "\n".join(missed)


def test_the_corpus_actually_contains_row_level_sweeps():
    """Non-vacuity guard.

    The test above passes trivially if no dataset sweeps a row-level key, which
    is indistinguishable from a deleted check. Two datasets do, and one of them
    (flow, 5 levels) is the reason the check exists.
    """
    found = scan()
    assert len(found) >= 4, found
    assert any(r["axis"] == "flow_ml_min" for r in found)
    assert any(r["axis"] == "zeta_mv" for r in found)


def test_no_row_level_axis_is_silently_inert():
    """Inert is acceptable; silently inert is not.

    A row-level axis that does not move the rate must carry a machine-readable
    `[DECLINES_AXIS: ...]` marker, so the scorer can tell a refusal from a
    prediction. Prose alone is what let a flow sweep be graded as physics.
    """
    bad = [r for r in scan() if r["verdict"] in ("silent", "prose-only", "dropped")]
    assert not bad, bad


def test_slurry_flow_is_declined_with_its_unblocking_measurement():
    """The flow refusal must name what would resolve it, not just refuse.

    A refusal with no exit condition becomes permanent by accident.
    """
    from cmp_sim.api import run_recipe

    _path, doc, rows = _doc("yang2023_quartz_ceria_L25")
    result = run_recipe(_recipe_for(doc, rows[0]))
    warns = [str(w) for w in (result.get("warnings") or [])]
    assert "flow_ml_min" in declined_axes(warns)
    text = next(w for w in warns if "flow_ml_min" in w)
    assert "starvation_length_m" in text        # WHERE the value would have to go
    assert "flow series" in text                # WHAT measurement unblocks it
    assert "does NOT move with flow" in text    # the honest consequence


def test_the_flow_refusal_is_scored_as_a_declined_axis():
    """The marker is only worth something if the SCORER reads it."""
    path = next(p for p in dataset_paths()
                if p.stem == "yang2023_quartz_ceria_L25")
    score = score_dataset(path)
    assert "flow_ml_min" in score.axes
    assert "flow_ml_min" in score.declined_axes_swept


def test_a_measured_zeta_potential_reaches_the_model():
    """The value must arrive, even though it changes no rate.

    Dropping it in the recipe builder is not a refusal -- it is the model never
    being asked, which is indistinguishable from a model that weighed it.
    """
    _path, doc, rows = _doc("us9422456b2_teos_silica_ph_pressure")
    row = next(r for r in rows if r.get("zeta_mv") is not None)
    recipe = _recipe_for(doc, row)
    assert recipe["slurry"]["zeta_mv"] == float(row["zeta_mv"])


def test_zeta_is_declined_because_it_is_not_separable_from_ph_here():
    """The refusal must state the IDENTIFIABILITY reason, and it must be true.

    Re-measured: in the only dataset publishing zeta, each pH has exactly one
    zeta, so a fitted zeta term would be the pH term renamed. If a future
    dataset varies zeta at fixed pH this assertion fails and the axis reopens.
    """
    from cmp_sim.api import run_recipe

    _path, doc, rows = _doc("us9422456b2_teos_silica_ph_pressure")
    by_ph: dict = {}
    for row in rows:
        ph = (row.get("overrides") or {}).get("slurry_ph")
        by_ph.setdefault(ph, set()).add(row.get("zeta_mv"))
    assert all(len(z) == 1 for z in by_ph.values()), (
        "zeta now varies at fixed pH somewhere in this dataset -- the axis is "
        "separable and the refusal in solver.simulate must be re-measured")
    assert len(by_ph) >= 5

    result = run_recipe(_recipe_for(doc, rows[0]))
    warns = [str(w) for w in (result.get("warnings") or [])]
    assert "zeta_mv" in declined_axes(warns)
    text = next(w for w in warns if "zeta_mv" in w)
    assert "FIXED pH" in text
    assert "second name" in text


def test_the_zeta_refusal_sends_the_axis_somewhere_it_is_NOT_inert():
    """"It goes to the defect proxy instead" is an excuse unless proven.

    Both halves: zeta must not move the rate, and the large-particle tail it
    speaks about must actually move `defect_risk`.
    """
    from cmp_sim.api import run_recipe

    _path, doc, rows = _doc("us9422456b2_teos_silica_ph_pressure")
    row = dict(rows[0])
    base = run_recipe(_recipe_for(doc, row))
    row["zeta_mv"] = float(row["zeta_mv"]) * 0.2      # weak stabilisation
    weak = run_recipe(_recipe_for(doc, row))
    assert weak["removal_rate_A_per_min"] == base["removal_rate_A_per_min"]

    recipe = _recipe_for(doc, rows[0])
    recipe["slurry"].setdefault("abrasive", {})["d99_nm"] = 900.0
    tail = run_recipe(recipe)
    assert (tail.get("defect_risk") or {}) != (base.get("defect_risk") or {}), (
        "the refusal claims the tail is read by the defect proxy; if D99 does "
        "not move defect_risk, that claim is an excuse")


def test_publishing_the_row_level_axes_did_not_move_the_median():
    """Zero median movement is the CORRECT outcome for an honesty fix.

    Nothing was fitted: two axes became visible and two refusals became
    readable. If this number moves, a scoring path changed and the change is a
    bug, not an improvement.
    """
    from cmp_sim.core.predictive_score import score_all

    errs = sorted(s.shape_mape for s in score_all() if s.shape_mape is not None)
    assert round(errs[len(errs) // 2], 1) == 18.9
