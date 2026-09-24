"""Titanium is not a supported film, and four points from one figure cannot make it one.

bouvet2002_ti_silica_size_sweep is the corpus's largest miss relative to its own
floor: 30.7% shape error against a ~2.7% digitisation floor, on the size axis —
otherwise the model's best (11.2% median). The obvious reading is a broken size
term. It isn't.

WHAT THE RESIDUAL SAYS

Three files come from the same paper, the same figure, the same slurry family and
the same tool. Only the film differs, and the three films disagree completely
about what particle size does:

    d50 (nm)      Ti        W       oxide
        12      2055     3097      1355
        25      1840     2975      1875
        45      1141     2743      1564
        75       946     2893      1402

    empirical size exponent   Ti -0.454   W -0.049   oxide +0.001

All three are scored with `pack: oxide_silica`, whose `abrasive_size_exponent` is
-0.05 — which is W's value to two decimals. The pack is right for W (2.3%), right
for oxide (11.2%), and wrong for Ti, and that single mismatched exponent is the
entire 30.7%.

WHY NOT SIMPLY FIT IT

Because the fit would validate itself. These four points are the ONLY titanium
data in the corpus — no other dataset carries a Ti film. An exponent fitted to
them would be tested on them and on nothing else, so its 30.7% would collapse to
near zero while telling us nothing about whether it generalises. That is the
definition of a number that looks like knowledge and isn't.

The data also does not support the fit as strongly as the clean-looking trend
suggests: as a pure power law Ti gives R^2 = 0.89 with a -13.9% residual at
25 nm. On four digitised points that is a weak basis for a new film constant.

The dataset itself already says so: `film: other`, and the notes flag the pack as
a placeholder for shape and rank use only. This file makes that refusal explicit
and checkable, rather than leaving it as a 30.7% that reads like a bug.

The honest position: Ti is UNSUPPORTED. The miss stays visible, and the entry in
docs/limits.md names the experiment that would change it — a second independent
Ti size sweep, from a different group, with a stated rate table.
"""
from __future__ import annotations

import math
import statistics as st

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, score_dataset
from cmp_sim.core.validation import dataset_paths

SIBLINGS = ("bouvet2002_ti_silica_size_sweep",
            "bouvet2002_w_silica_size_sweep",
            "bouvet2002_oxide_silica_size_sweep")


def _path(stem):
    return next(p for p in dataset_paths() if p.stem == stem)


def _sweep(stem):
    doc = yaml.safe_load(_path(stem).read_text(encoding="utf-8"))
    rows = [((row.get("overrides") or {}).get("abrasive_d50_nm"),
             _measured(row)) for row in doc["conditions"]]
    return sorted((d, m) for d, m in rows if d and m)


def _exponent(stem):
    pairs = _sweep(stem)
    lx = [math.log(d) for d, _ in pairs]
    ly = [math.log(m) for _, m in pairs]
    mx, my = st.mean(lx), st.mean(ly)
    return (sum((a - mx) * (b - my) for a, b in zip(lx, ly))
            / sum((a - mx) ** 2 for a in lx))


def test_the_three_siblings_share_everything_except_the_film():
    """Same paper, same figure, same pack — so the film is the only variable."""
    packs, tools = set(), set()
    for stem in SIBLINGS:
        doc = yaml.safe_load(_path(stem).read_text(encoding="utf-8"))
        packs.add(doc.get("pack"))
        tools.add(str(doc.get("source", ""))[:40])
    assert packs == {"oxide_silica"}, packs
    assert len(tools) == 1, (
        "the three files no longer share a source; the comparison this test "
        "rests on has changed")


def test_the_three_films_disagree_about_particle_size():
    ti, w, oxide = (_exponent(s) for s in SIBLINGS)
    assert ti < -0.3, ti            # falls steeply
    assert abs(w) < 0.15, w         # essentially flat
    assert abs(oxide) < 0.15, oxide # essentially flat
    assert ti < w - 0.3, (
        "Ti no longer differs from W by a wide margin; if the data changed, "
        "the whole 'one exponent cannot serve three films' argument needs "
        "rechecking")


def test_the_packs_exponent_is_ws_value_not_tis():
    """Explains the miss: the pack was fitted to the films that agree."""
    pack_value = load_pack("oxide_silica").get("abrasive_size_exponent")
    value = getattr(pack_value, "value", pack_value)
    assert abs(float(value) - _exponent("bouvet2002_w_silica_size_sweep")) < 0.05
    assert abs(float(value) - _exponent("bouvet2002_ti_silica_size_sweep")) > 0.3


def test_titanium_is_the_only_film_with_no_second_dataset():
    """Why fitting an exponent to it would validate itself."""
    ti_files = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if "ti" in path.stem.split("_")[1:2] or "_ti_" in path.stem:
            ti_files.append(path.stem)
    assert ti_files == ["bouvet2002_ti_silica_size_sweep"], (
        f"{ti_files}: a second Ti dataset would make a fitted exponent "
        "testable, and this refusal should be revisited")


def test_the_ti_power_law_is_not_strong_enough_to_fit_from():
    """R^2 = 0.89 on four digitised points is a weak basis for a constant."""
    pairs = _sweep("bouvet2002_ti_silica_size_sweep")
    lx = [math.log(d) for d, _ in pairs]
    measured = [m for _, m in pairs]
    b = _exponent("bouvet2002_ti_silica_size_sweep")
    a = st.mean(math.log(m) for m in measured) - b * st.mean(lx)
    pred = [math.exp(a + b * x) for x in lx]
    ss_res = sum((p - m) ** 2 for p, m in zip(pred, measured))
    ss_tot = sum((m - st.mean(measured)) ** 2 for m in measured)
    r2 = 1 - ss_res / ss_tot
    assert 0.8 < r2 < 0.95, r2
    assert len(pairs) == 4, len(pairs)


def test_the_dataset_declares_itself_unsupported():
    """The refusal must be in the data, not only in this test."""
    doc = yaml.safe_load(_path("bouvet2002_ti_silica_size_sweep")
                         .read_text(encoding="utf-8"))
    assert str(doc.get("film")).lower() == "other", (
        "film must not be promoted to 'ti' while no Ti pack exists")
    notes = str(doc.get("notes", "")).lower()
    assert "placeholder" in notes
    assert "shape" in notes or "rank" in notes


def test_the_miss_stays_visible():
    """We do not hide an unsupported film by excluding it from the score."""
    score = score_dataset(_path("bouvet2002_ti_silica_size_sweep"))
    assert score.shape_mape is not None, (
        "the Ti dataset must stay scored: an unsupported film that quietly "
        "disappears from the report is worse than a visible 30.7%")
    assert score.shape_mape > 20
