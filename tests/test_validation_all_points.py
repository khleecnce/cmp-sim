"""The validation gate must not be passable by picking a flattering subset.

The bug this file exists to prevent
-----------------------------------
``best_fit_per_dataset`` selects the largest sweep per dataset and breaks ties
by LOWER MAPE. For a dataset that splits into several equally sized groups,
that tie-break is a cherry-pick: it reports the group the model happens to fit
best and says nothing about the rest.

EP3161098B1's tungsten table made this visible. Six chemistries × three
pressures fit as six groups of three; their MAPEs run 10.6 % to 59.1 %. The old
CLI printed 10.6 % and counted the dataset as passing a 15 % gate. Over all 18
printed points the error is 40.2 %, and the dataset does not pass.

The same check caught a dataset that had been counted as passing for a while:
the US6564116B2 Taguchi set reports 12.6 % on its best group and 18.9 % overall.
"""
from __future__ import annotations

import numpy as np
import pytest

from cmp_sim.core.validation import (GroupFit, all_points_error,
                                     best_fit_per_dataset, fit_dataset,
                                     dataset_paths, run_all)


def _find(name):
    for p in dataset_paths():
        if p.stem == name:
            return p
    raise AssertionError(f"dataset {name} not found")


# ---------------------------------------------------------------------------
# the mechanism
# ---------------------------------------------------------------------------

def _fake(dataset, group, errs):
    e = [float(x) for x in errs]
    return GroupFit(dataset=dataset, group=group, n=len(e), kp_fit=1.0,
                    max_abs_error_pct=max(abs(x) for x in e),
                    mape_pct=float(np.mean([abs(x) for x in e])),
                    errors_pct=e, labels=[""] * len(e), source="",
                    in_scope=True, read_method="table")


def test_all_points_error_does_not_drop_the_bad_groups():
    fits = [_fake("d", "g1", [1, 1, 1]), _fake("d", "g2", [50, 50, 50])]
    best = best_fit_per_dataset(fits)["d"]
    allp = all_points_error(fits)["d"]

    assert best.mape_pct == pytest.approx(1.0), "tie-break picks the good group"
    assert allp["mape_pct"] == pytest.approx(25.5), "all points keeps both"
    assert allp["n"] == 6
    assert allp["groups"] == 2
    assert allp["max_abs_error_pct"] == pytest.approx(50.0)


def test_single_group_dataset_reports_the_same_either_way():
    """No penalty for datasets that do not split — the two must agree."""
    fits = [_fake("d", "only", [3, -5, 4])]
    assert (all_points_error(fits)["d"]["mape_pct"]
            == pytest.approx(best_fit_per_dataset(fits)["d"].mape_pct))


# ---------------------------------------------------------------------------
# the real datasets that exposed it
# ---------------------------------------------------------------------------

def test_ep3161098b1_w_is_judged_on_all_eighteen_points():
    """The W table must not look like a 3-point dataset.

    If this starts failing because the numbers improved, that is real progress
    — but the *count* must stay at 18, because that is how many rates the
    patent prints.
    """
    fits = fit_dataset(_find("ep3161098b1_w_silica_pressure_sweep"))
    allp = all_points_error(fits)["ep3161098b1_w_silica_pressure_sweep"]

    assert allp["n"] == 18, "all six compositions × three pressures"
    assert allp["groups"] == 6
    best = best_fit_per_dataset(fits)["ep3161098b1_w_silica_pressure_sweep"]
    assert allp["mape_pct"] > best.mape_pct, (
        "if these ever coincide the cherry-pick check has been defeated")


def test_w_pressure_response_is_steeper_than_oxide_on_the_same_wafers():
    """The physics claim the pair of datasets was added to support.

    Same slurry, same tool, same pressures, two films. W's rate ratio over
    1.5 -> 3.0 psi must exceed TEOS's. If a future model change flattens W to
    Preston, this fails — which is the point.
    """
    import yaml

    def ratios(stem, film_key):
        raw = yaml.safe_load(_find(stem).read_text(encoding="utf-8"))
        by_label = {}
        for c in raw["conditions"]:
            comp = c["label"].split()[0]
            by_label.setdefault(comp, {})[c["pressure_psi"]] = c["mrr_nm_per_min"]
        return {k: v[3.0] / v[1.5] for k, v in by_label.items() if 1.5 in v and 3.0 in v}

    w = ratios("ep3161098b1_w_silica_pressure_sweep", "w")
    teos = ratios("ep3161098b1_teos_silica_pressure_sweep", "oxide")

    assert len(w) == 6 and len(teos) == 6
    # TEOS sits on Preston: a 2x pressure change gives ~2x the rate.
    assert all(1.7 <= r <= 2.3 for r in teos.values()), teos
    # W does not, and in most chemistries is far steeper.
    assert max(w.values()) > 5.0, w
    assert max(w.values()) > max(teos.values()) * 2, (w, teos)


def test_gate_counts_only_datasets_that_pass_on_all_points():
    """End-to-end: the shipped gate must use the honest number.

    Guards the CLI wiring, not just the library function.
    """
    import subprocess, sys

    out = subprocess.run(
        [sys.executable, "-m", "cmp_sim.validate_cli", "--gate", "15"],
        capture_output=True, text=True, timeout=300).stdout

    assert "-> PASS" in out
    # The W dataset's best group is under 15% but its all-points error is not,
    # so it must appear as explicitly NOT counted rather than silently passing.
    assert "ep3161098b1_w_silica_pressure_sweep best group" in out
    assert "not counted" in out
    passing_block = out.split("(need 3) ->")[1]
    counted = [ln for ln in passing_block.splitlines() if ln.strip().startswith("+")]
    assert not any("ep3161098b1_w_silica" in ln for ln in counted), counted
