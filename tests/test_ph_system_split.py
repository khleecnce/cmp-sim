"""The pH optimum belongs to the SLURRY SYSTEM, not to the film.

STATUS.md named pH as the model's weakest scored axis and diagnosed the cause
as structural: two silica slurries can peak six pH units apart on the SAME
film, so a single per-film pH bell must be wrong for one of them.

US 9,422,456 B2 Table 3 is the clean demonstration. A cationic aminosilane
core-shell colloidal silica polishes TEOS with a maximum at pH 4.9 and a 57x
collapse by pH 9, on the same IC1010 pad and Mirra tool that the repo's other
oxide data uses. The inherited ``oxide_silica`` pack peaks at pH 11 (Li 2021,
plain silica) and scores 126.6 % on that table.

These tests pin three things:

1. the measured optimum really is acidic, straight from the dataset file, so a
   later edit that "tidies" the numbers is caught;
2. the new ``oxide_silica_aminosilane`` pack reproduces the table far better
   than the alkaline pack does — the split is worth its existence;
3. the split did NOT reach into the alkaline pack: ``oxide_silica`` still
   peaks at 11 and still scores its own datasets as before.

It also records, as an executable statement rather than a comment, the one
thing the engine provably cannot do here: below pH 3.5 the measured rate does
not respond to pressure at all, and a model that multiplies a pH factor by a
Preston P*V term must predict 2x for a 2x load everywhere.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import score_dataset
from cmp_sim.core.validation import dataset_paths

DATASET = "us9422456b2_teos_silica_ph_pressure"


def _dataset_path() -> Path:
    for path in dataset_paths():
        if path.stem == DATASET:
            return path
    raise AssertionError(f"dataset {DATASET} not found")


def _rows():
    doc = yaml.safe_load(_dataset_path().read_text(encoding="utf-8"))
    return doc, doc["conditions"]


def _by_ph(pressure_psi: float):
    _, rows = _rows()
    return {r["overrides"]["slurry_ph"]: r["mrr_a_per_min"]
            for r in rows if r["pressure_psi"] == pressure_psi}


def _param(pack: str, key: str):
    return load_pack(pack).param(key)


def _value(pack: str, key: str):
    return _param(pack, key).value


# ---------------------------------------------------------------------------
# 1. the measurement
# ---------------------------------------------------------------------------

def test_the_table_is_complete_and_carries_both_pressures():
    _, rows = _rows()
    assert len(rows) == 22, "11 pH levels x 2 pressures, as printed"
    assert {r["pressure_psi"] for r in rows} == {2.0, 4.0}
    assert len({r["overrides"]["slurry_ph"] for r in rows}) == 11
    assert all(r["read_method"] == "table" for r in rows), "no digitized figures"


def test_this_silica_peaks_in_the_ACID_and_dies_in_the_alkaline():
    at2, at4 = _by_ph(2.0), _by_ph(4.0)

    assert max(at2, key=at2.get) == 4.9, at2
    assert max(at4, key=at4.get) in (4.6, 4.9), at4
    # the collapse that makes the optimum unmistakable
    assert at2[4.9] / at2[9.0] > 50, "57x fall from the optimum to pH 9"
    # ... and it is not a slow roll-off: pH 11 is still near the floor
    assert at2[11.0] < 0.1 * at2[4.9]


def test_the_pack_records_the_measured_optimum_not_a_fitted_one():
    assert _value("oxide_silica_aminosilane", "ph_peak") == 4.9
    # the alkaline pack must be untouched by this work
    assert _value("oxide_silica", "ph_peak") == 11.0


# ---------------------------------------------------------------------------
# 2. the split earns its keep
# ---------------------------------------------------------------------------

def test_the_acidic_pack_beats_the_alkaline_one_on_this_table_by_a_wide_margin():
    """Guards the reason the pack was added at all.

    If a future change makes ``oxide_silica`` fit this table as well as the
    dedicated pack does, the split is no longer justified and this test should
    be revisited — deliberately, not silently.
    """
    doc, _ = _rows()
    assert doc["pack"] == "oxide_silica_aminosilane"

    scored = score_dataset(_dataset_path())
    assert scored.n == 22
    assert scored.shape_mape is not None
    assert scored.shape_mape < 35.0, scored.as_dict()
    assert scored.beats_flat

    # the same table through the alkaline pack, which is what it scored before
    path = _dataset_path()
    alkaline = yaml.safe_load(path.read_text(encoding="utf-8"))
    alkaline["pack"] = "oxide_silica"
    tmp = path.parent / "_tmp_alkaline_check.yaml"
    tmp.write_text(yaml.safe_dump(alkaline, sort_keys=False), encoding="utf-8")
    try:
        before = score_dataset(tmp)
    finally:
        tmp.unlink()

    assert before.shape_mape > 100.0, (
        "the pH-11 bell should be badly wrong on an acidic-optimum slurry")
    assert scored.shape_mape < before.shape_mape / 3.0, (
        scored.shape_mape, before.shape_mape)


def test_out_of_sample_error_is_close_to_the_in_sample_error():
    """Two shape parameters on 22 points should not be overfitting.

    If leave-one-out ever runs away from the fitted error, the width/floor fit
    has started memorising instead of describing.
    """
    scored = score_dataset(_dataset_path())
    assert scored.loo_mape is not None
    assert scored.loo_mape < scored.shape_mape * 1.5, scored.as_dict()


# ---------------------------------------------------------------------------
# 3. the limit this dataset exposes, stated as a test
# ---------------------------------------------------------------------------

def test_below_ph_3_5_the_measured_rate_ignores_pressure():
    """A multiplicative pH x Preston model cannot reproduce this.

    Doubling the down force does nothing at pH 2.5-3.5 and roughly doubles the
    rate from pH 4 upward. The engine's chemical factor multiplies a Preston
    term, so it must predict 2x everywhere. This test asserts the DATA, so the
    day a rate-limiting-step model lands, the target is already written down.
    """
    at2, at4 = _by_ph(2.0), _by_ph(4.0)
    ratio = {ph: at4[ph] / at2[ph] for ph in at2}

    chemically_starved = [ratio[ph] for ph in (2.5, 3.0, 3.5)]
    assert all(r < 1.05 for r in chemically_starved), ratio

    mechanically_limited = [ratio[ph] for ph in (4.0, 4.6, 4.9)]
    assert all(1.6 < r < 1.9 for r in mechanically_limited), ratio

    assert max(chemically_starved) < min(mechanically_limited), (
        "the two regimes must not overlap, or the claim is not in the data")


def test_the_pack_discloses_that_it_cannot_model_that_transition():
    entry = _param("oxide_silica_aminosilane", "ph_pressure_response_note")
    assert entry.value is None, "a limitation is not a parameter"
    assert entry.confidence == "unverified"
    assert "Preston" in entry.note


@pytest.mark.parametrize("key", ["ph_response_width",
                                 "ph_mechanical_floor",
                                 "ph_acid_mechanical_floor"])
def test_every_fitted_constant_names_the_dataset_it_was_fitted_to(key):
    entry = _param("oxide_silica_aminosilane", key)
    assert DATASET in entry.source, entry.source
    assert entry.confidence in ("med", "literature")
