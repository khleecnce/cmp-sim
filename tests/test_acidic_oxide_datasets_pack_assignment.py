"""Which acidic oxide datasets belong to which silica pack.

The Kp audit found three oxide datasets running at pH 3-4.7 on `oxide_silica`, a
pack fitted at pH 10-12.5, and under-predicting by 39x, 98x and 139x. The obvious
move is to reassign them to `oxide_silica_anionic` (ph_peak 2.0). Measured, that
looks tempting:

    dataset                          oxide_silica -> anionic      shape
    ep3161098b1_teos_pressure          139.24x  ->  20.94x      7.1 -> 7.0%
    us9499721b2_teos_conc               98.25x  ->  23.75x     22.9 -> 22.9%
    bouvet2002_oxide_size_sweep         39.21x  ->   3.59x     11.2 -> 11.2%

Every scale error improves 4-11x. **Shape does not move at all** — which is the
tell. These datasets sweep pressure, concentration and particle size; no pH
constant touches those axes. A pack swap here buys absolute calibration only, so
"it fits better" is not evidence about which pack is correct, and choosing by
that number would be fitting by outcome.

THE SOURCES DECIDE, AND THEY ONLY DECIDE ONE

Only `us9499721b2` states its abrasive's surface charge. Its own notes say:

    입자가 아미노실란 내장 **양전하(cationic)** 콜로이달 실리카, pH 4.7 산성.
    팩 기본은 음전하 실리카 pH 10.5 염기성이다.

That is verbatim the system `oxide_silica_aminosilane` was built for — a
cationic aminosilane-cored silica, ph_peak 4.9, fitted on US9422456B2, the
sibling Cabot patent. Scoring it with that pack instead:

    oxide_silica              shape 22.9%   measured/predicted  98.25x
    oxide_silica_anionic      shape 22.9%   measured/predicted  23.75x
    oxide_silica_aminosilane  shape 22.9%   measured/predicted   2.68x

So the dataset was reassigned — on the source's chemistry, not on the 2.68x.

`ep3161098b1` and `bouvet2002_oxide_silica_size_sweep` were NOT reassigned.
Neither source states its abrasive's surface charge, so any move would rest on
the improvement itself. They stay mis-scaled and visible.

A TRAP CHECKED ALONG THE WAY

`ep3161098b1` is a *tungsten* CMP patent, which raised the question of whether
its oxide arm was mislabelled. It is not: the patent reports both films, and the
corpus already carries `ep3161098b1_w_silica_pressure_sweep` (film w, pack
w_fe_oxidizer) separately. The TEOS arm is genuinely oxide.

THE CIRCULARITY THIS EXPOSED

`us9499721b2` carries a `calibration_contact` recording that `oxide_silica`'s
`abrasive_conc_exponent` (0.3333) was regressed from this file's 3 psi row. So
the parent pack's concentration exponent is evidenced by a **cationic** slurry
the pack is not built for. All three silica packs share the exponent unchanged,
so nothing moves numerically — but the provenance is now stated rather than
implied.
"""
from __future__ import annotations

import statistics as st

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, _predict, score_dataset
from cmp_sim.core.validation import dataset_paths

REASSIGNED = "us9499721b2_teos_colloidal_silica_pressure_conc"
LEFT_ALONE = ("ep3161098b1_teos_silica_pressure_sweep",
              "bouvet2002_oxide_silica_size_sweep")


def _path(stem):
    return next(p for p in dataset_paths() if p.stem == stem)


def _doc(stem):
    return yaml.safe_load(_path(stem).read_text(encoding="utf-8"))


def _scale(doc):
    rows = [r for r in doc["conditions"] if _measured(r) is not None]
    ratios = []
    for row in rows:
        predicted, measured = _predict(doc, row), _measured(row)
        if predicted and measured:
            ratios.append(measured / predicted)
    return st.median(ratios)


def _with_pack(stem, pack):
    """Score `stem` as if it declared `pack`, then restore the file."""
    path = _path(stem)
    original = path.read_text(encoding="utf-8")
    current = yaml.safe_load(original)["pack"]
    try:
        path.write_text(
            original.replace(f"\npack: {current}\n", f"\npack: {pack}\n"),
            encoding="utf-8")
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert doc["pack"] == pack, "pack substitution did not take"
        return score_dataset(path), _scale(doc)
    finally:
        path.write_text(original, encoding="utf-8")


def test_the_reassigned_dataset_uses_the_pack_its_source_describes():
    assert _doc(REASSIGNED)["pack"] == "oxide_silica_aminosilane"


def test_the_source_actually_says_cationic_aminosilane():
    """The reassignment must rest on the source, not on the improvement."""
    notes = str(_doc(REASSIGNED).get("notes", ""))
    assert "아미노실란" in notes and "양전하" in notes, (
        "the note naming this abrasive cationic aminosilane silica is gone; "
        "without it the reassignment has no justification and must be reverted")


def test_the_pack_swap_changes_scale_but_not_shape():
    """Why 'it fits better' could not decide this: shape is untouched."""
    own = score_dataset(_path(REASSIGNED))
    parent_score, parent_scale = _with_pack(REASSIGNED, "oxide_silica")

    assert own.shape_mape is not None and parent_score.shape_mape is not None
    assert abs(own.shape_mape - parent_score.shape_mape) < 0.1, (
        "shape moved under a pack swap on pressure/concentration axes — the "
        "reasoning in this file assumed no pH constant touches them")
    assert parent_scale > 10 * _scale(_doc(REASSIGNED)), (
        f"the scale improvement that motivated the check is gone: "
        f"{parent_scale:.2f}x vs {_scale(_doc(REASSIGNED)):.2f}x")


def test_the_unstated_ones_were_left_mis_scaled_on_purpose():
    for stem in LEFT_ALONE:
        doc = _doc(stem)
        assert doc["pack"] == "oxide_silica", (
            f"{stem} was reassigned, but its source does not state the "
            "abrasive's surface charge — that is fitting by outcome")
        assert _scale(doc) > 10, (
            f"{stem} is no longer strongly mis-scaled; if a model change fixed "
            "it, this file's reasoning needs revisiting")


def test_the_tungsten_arm_of_the_same_patent_is_a_separate_dataset():
    """ep3161098b1 is a W patent; its oxide arm is not a mislabel."""
    w = _doc("ep3161098b1_w_silica_pressure_sweep")
    oxide = _doc("ep3161098b1_teos_silica_pressure_sweep")
    assert w["film"] == "w" and w["pack"] == "w_fe_oxidizer"
    assert oxide["film"] == "oxide"


def test_the_concentration_exponent_is_shared_so_nothing_moved():
    """The circularity is disclosed, not corrected — check it is inert."""
    values = {name: load_pack(name).param("abrasive_conc_exponent").value
              for name in ("oxide_silica", "oxide_silica_anionic",
                           "oxide_silica_aminosilane")}
    assert len(set(values.values())) == 1, (
        f"the silica packs no longer share abrasive_conc_exponent {values}; "
        "the reassignment is no longer numerically inert and the disclosure "
        "note in the dataset must be rewritten")


def test_the_calibration_contact_still_records_the_circularity():
    contacts = _doc(REASSIGNED).get("calibration_contact") or []
    params = {c.get("param") for c in contacts}
    assert "abrasive_conc_exponent" in params, (
        "the record that oxide_silica's concentration exponent was fitted on "
        "this cationic dataset has been removed")
