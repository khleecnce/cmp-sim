"""What the two newly-scorable SiC datasets actually validate — and what they don't.

Declaring films made `entegris2022_us20220315802a1_sic_alumina_conc` (14.1%) and
`gong2024_4hsic_alumina_kmno4_L25` (24.9%) scorable for the first time. They are
the only datasets that exercise `sic_alumina_kmno4`, so until now every constant
in that pack was untested against data. STATUS asked which parameters they
evidence and which remain unexercised. The answer is more awkward than either.

NO INERT TERMS — the pH, oxidizer, loading and size terms all move the
prediction, so this pack does not repeat the `sic_ceria_h2o2` trap of a constant
that looks active but is switched off. Sweeping one axis at a time from each
dataset's own first row:

    slurry_ph        3 -> 7 -> 10.5 -> 13     94.7 -> 97.7 -> 7889.4 -> 919.0
    oxidizer_wt_pct  0 -> 1 -> 4 -> 8         17.6 -> 94.7 -> 117.5 -> 122.7
    abrasive_wt_pct  1 -> 3 -> 6 -> 9         94.7 -> 60.6 -> 45.7 -> 38.8
    abrasive_size_nm 30 -> 80 -> 200          58.7 -> 69.3 -> 81.0

BUT BOTH DATASETS SIT ENTIRELY OUTSIDE THE PACK'S DECLARED pH RANGE.
`sic_alumina_kmno4` declares `ph_valid_range: [9.0, 11.0]` with a peak at 10.5.
entegris2022 is a single-pH dataset at **2.3**; gong2024 sweeps **2 to 6**.
Neither reaches 9. So the scores are real, but they do not test the pH term the
pack was fitted with — they test it in extrapolation, on its acidic tail.

That is why the sweep above shows an 83x jump between pH 7 and 10.5: the
datasets live on the flat acidic side, far from the peak that dominates the
term's shape. A reader seeing '14.1%' would reasonably assume the pH physics had
been validated. It has not.

WHAT IS ACTUALLY EVIDENCED. entegris2022 varies only `abrasive_wt_pct` and beats
predicting its own mean decisively (14.1% vs 65.1%), so it is genuine evidence
for the loading term — at one pH, on five points. gong2024 varies loading, pH and
oxidizer together and LOSES to its own mean (24.9% vs 15.0%): across 25 rows its
measured MRR moves only 99-119 by loading and 100-119 by pH, i.e. the experiment
is nearly flat while the model asserts structure.

This is consistent with the corpus-wide finding that out-of-range pH is a warning
rather than a gate (measured: in-range 18.9% vs out-of-range 19.4%, z = -0.15).
Gating these two would discard the only evidence the pack has. So they stay
scored, and this test records what the numbers do and do not license.
"""
from __future__ import annotations

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, _predict, score_dataset
from cmp_sim.core.validation import dataset_paths

PACK = "sic_alumina_kmno4"
ENTEGRIS = "entegris2022_us20220315802a1_sic_alumina_conc"
GONG = "gong2024_4hsic_alumina_kmno4_L25"


def _path(stem):
    return next(p for p in dataset_paths() if p.stem == stem)


def _doc(stem):
    return yaml.safe_load(_path(stem).read_text(encoding="utf-8"))


def _rows(stem):
    return [r for r in _doc(stem)["conditions"] if _measured(r) is not None]


def _value(key):
    param = load_pack(PACK).get(key)
    return getattr(param, "value", param)


def _sweep(stem, axis, values):
    doc = _doc(stem)
    base = _rows(stem)[0]
    out = []
    for value in values:
        row = dict(base)
        overrides = dict(row.get("overrides") or {})
        overrides[axis] = value
        row["overrides"] = overrides
        out.append(_predict(doc, row))
    return [x for x in out if x is not None]


def test_these_are_the_only_datasets_exercising_the_pack():
    users = set()
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if doc.get("pack") == PACK:
            users.add(path.stem)
    assert users == {ENTEGRIS, GONG}, (
        f"{sorted(users)}: if another dataset now uses this pack, the claims in "
        "this file about what is and is not evidenced must be rechecked")


def test_no_term_is_inert():
    """Unlike sic_ceria_h2o2's pH width, every swept term moves the answer."""
    for stem in (ENTEGRIS, GONG):
        for axis, values in (("slurry_ph", [3, 7, 10.5, 13]),
                             ("oxidizer_wt_pct", [0, 1, 4, 8]),
                             ("abrasive_wt_pct", [1, 3, 6, 9]),
                             ("abrasive_size_nm", [30, 80, 200])):
            predictions = _sweep(stem, axis, values)
            assert len(set(predictions)) > 1, (
                f"{stem}/{axis} is INERT: the parameter is accepted and ignored, "
                "which is worse than it being absent")


def test_both_datasets_lie_entirely_outside_the_packs_ph_range():
    """The headline finding: the scores do not validate the pH term."""
    low, high = _value("ph_valid_range")
    assert (low, high) == (9.0, 11.0)
    for stem in (ENTEGRIS, GONG):
        phs = [(r.get("overrides") or {}).get("slurry_ph") for r in _rows(stem)]
        phs = [p for p in phs if p is not None]
        assert phs, stem
        assert max(phs) < low, (
            f"{stem} now reaches into the pack's fitted pH range; it would then "
            "be real evidence for the pH term and this test's premise changes")


def test_the_datasets_all_sit_on_the_clamped_edge_of_the_ph_term():
    """Why 'scored' must not be read as 'pH validated' — restated after the fix.

    CHECKED, not re-baselined blindly. The concern flagged in STATUS was that
    the pH edge-hold might flatten a jump across a peak that lies OUTSIDE the
    pack's declared range, which would mean the RANGE is wrong rather than the
    clamp. It does not: this pack's peak (10.5) is interior to its declared
    range (9.0-11.0), asserted below, so the clamp never touches the peak.

    What the clamp DID remove is the extrapolated acidic tail. The sweep used
    to span >10x only because pH 3 and pH 7 were evaluated on a Gaussian tail
    fitted over pH 9-11 — a number produced by the function, not by any
    measurement. Both now return the SAME held edge value, and that is a
    sharper statement of this file's finding than the old one: both datasets
    (pH 2-6) sit entirely on the clamp, so the pH term contributes one constant
    factor to every row they contain and cannot be evidence for or against it.
    """
    low, high = _value("ph_valid_range")
    peak = _value("ph_peak")
    assert low < peak < high, (
        "if the peak were outside the declared range, the clamp would be "
        "hiding the pack's own optimum and the RANGE would be the bug")

    below_low, inside_low, at_peak = _sweep(GONG, "slurry_ph", [3, 7, 10.5])
    assert below_low == inside_low, (
        "every pH below the fitted range must return the same held edge value; "
        f"got {below_low} and {inside_low}")
    assert at_peak / below_low > 3, (
        "the pH term still carries a large unvisited peak inside its fitted "
        "range; the datasets simply never reach it")


def test_entegris_is_genuine_evidence_for_the_loading_term():
    score = score_dataset(_path(ENTEGRIS))
    assert score.axes == ["abrasive_wt_pct"], score.axes
    assert score.shape_mape is not None and score.flat_mape is not None
    assert score.shape_mape < score.flat_mape / 2, (
        "entegris beats predicting its own mean by a wide margin, which is what "
        "makes it evidence rather than a coincidence")


def test_gong_loses_to_its_own_mean_because_the_experiment_is_nearly_flat():
    score = score_dataset(_path(GONG))
    assert score.shape_mape is not None and score.flat_mape is not None
    assert not score.beats_flat, (
        "gong2024 is registered as losing to its own mean; if it now wins, the "
        "explanation below no longer applies")

    rates = [m for m in (_measured(r) for r in _rows(GONG)) if m is not None]
    spread = max(rates) / min(rates)
    assert spread < 2.0, (
        f"measured spread is only {spread:.2f}x across 25 rows — the experiment "
        "barely moves, so asserting structure costs more than it gains")


def test_the_evidence_is_recorded_where_a_pack_reader_will_see_it():
    """A limit discovered here must not live only in this test file."""
    from pathlib import Path

    import cmp_sim
    text = (Path(cmp_sim.__file__).parent / "data" / "params"
            / f"{PACK}.yaml").read_text(encoding="utf-8")
    assert "ph_valid_range" in text
    assert "entegris2022" in text and "gong2024" in text, (
        "the pack must name the two datasets that exercise it and say that "
        "both sit outside its fitted pH range")
