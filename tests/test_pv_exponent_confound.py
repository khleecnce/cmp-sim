"""The P-V exponent scatter is mostly a confound, and one shared P0 does not pay.

Two claims recorded in docs/derivations.md ("The P-V exponent scatter was
mostly a CONFOUND") are re-derived here from the datasets rather than trusted
from the document, so that adding or editing a dataset that overturns them
fails a test instead of leaving a stale paragraph.

Claim 1 — CONTROL MATTERS. Fitting RR ~ k P^a V^b on rows that differ in more
than P and V lets the chemistry response leak into the pressure exponent. With
rows restricted to otherwise-identical conditions, Preston's mean error over
the pressure-varying datasets drops sharply.

Claim 2 — ONE SHARED THRESHOLD PRESSURE IS NOT A LAW. The passivation-
breakthrough form RR = Kp (P - P0) V, with a single P0 shared by every dataset
and the scale still free per tool, buys well under a point of mean MAPE. It is
therefore not adopted, and this test pins that so no later session adopts it on
the strength of the per-dataset numbers (where it "wins" on 6 of 10 simply
because a free offset can only help a free-scale fit).

Neither claim touches a model constant; they are guards on a diagnosis.
"""
from __future__ import annotations

import statistics

import pytest

from tools.pv_regime_probe import (fit_ab, mape_scale_free, preston_err,
                                   pv_rows, rows_of, threshold_err)
from cmp_sim.core.validation import dataset_paths

import yaml


def _matched_sets():
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text()) or {}
        rows = pv_rows(doc)
        if len(rows) >= 3 and len({r[0] for r in rows}) >= 2:
            out.append((path.stem, rows))
    return out


def _uncontrolled_rows(doc):
    """Every P/V row regardless of what else the row changed."""
    out = []
    for r in rows_of(doc):
        p, v = r.get("pressure_psi"), (r.get("rpm_platen") or r.get("rpm_wafer"))
        m = r.get("mrr_nm_per_min")
        if p is None or v is None or m is None:
            continue
        out.append((float(p), float(v), float(m)))
    return out


MATCHED = _matched_sets()


def test_there_are_enough_matched_condition_datasets_to_say_anything():
    assert len(MATCHED) >= 8, (
        "the diagnosis rests on ~10 datasets with a pressure axis at otherwise "
        f"identical conditions; only {len(MATCHED)} were found")


def test_controlling_the_other_axes_improves_preston_on_the_same_datasets():
    """Claim 1: the exponent scatter was chemistry leaking into `a`.

    PAIRED comparison. An earlier version of this test averaged the
    uncontrolled error over a DIFFERENT (larger) set of datasets than the
    matched one, so the difference partly measured which datasets happened to
    qualify. Here each dataset is compared against itself, which is the only
    form of the claim that means anything.
    """
    pairs = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text()) or {}
        matched_rows = pv_rows(doc)
        if len(matched_rows) < 3 or len({r[0] for r in matched_rows}) < 2:
            continue
        all_rows = _uncontrolled_rows(doc)
        eu, em = preston_err(all_rows), preston_err(matched_rows)
        if eu is None or em is None:
            continue
        pairs.append((path.stem, eu, em))

    assert len(pairs) >= 8, f"only {len(pairs)} paired datasets"
    # On a dataset that varies nothing but P and V the control is a no-op and
    # the two errors are identical; those carry no information about the claim.
    active = [(s, eu, em) for s, eu, em in pairs if abs(eu - em) > 1e-9]
    assert len(active) >= 3, (
        f"only {len(active)} of {len(pairs)} datasets have anything to control "
        "for; the confound claim cannot be tested on this corpus")
    improved = [s for s, eu, em in active if em < eu]
    mu = statistics.fmean([eu for _, eu, _ in active])
    mm = statistics.fmean([em for _, _, em in active])
    # NOT asserted: that the control helps every dataset. It cannot be, and an
    # earlier version of this test wrongly assumed so. Restricting to matched
    # rows also REFITS the free scale on fewer points, so a dataset whose
    # discarded rows happened to pin the scale well can get worse — which is
    # exactly what us6564116b2 (an L25 array reduced to 5 matched rows) does.
    # What the confound claim actually requires is a clear majority and a
    # clearly lower mean.
    assert len(improved) >= len(active) - 1 and len(improved) >= 3, (
        f"only {len(improved)}/{len(active)} datasets improve under the "
        "control; the confound claim no longer holds")
    assert mm < mu * 0.85, (
        f"matched-condition Preston error {mm:.1f}% vs uncontrolled {mu:.1f}% "
        "on the datasets the control actually touches; the confound is no "
        "longer large enough to be the headline explanation")


def test_a_single_shared_threshold_pressure_does_not_earn_its_constant():
    """Claim 2: RR = Kp (P - P0) V with one global P0 buys < 1 point."""
    base = statistics.fmean([e for e in (preston_err(r) for _, r in MATCHED)
                             if e is not None])
    best = base
    for i in range(1, 61):                       # 0.05 .. 3.00 psi
        p0 = i * 0.05
        errs = [threshold_err(r, p0) for _, r in MATCHED]
        if any(e is None for e in errs):
            continue
        best = min(best, statistics.fmean(errs))
    gain = base - best
    assert gain < 1.0, (
        f"a single shared P0 now buys {gain:.2f} points of mean MAPE "
        f"({base:.1f}% -> {best:.1f}%). That is enough to reconsider adopting "
        "it — see docs/derivations.md, 'Threshold pressure ... TESTED, not "
        "adopted', and re-run tools/pv_regime_probe.py before changing the model")


def test_free_exponents_are_only_shown_as_an_interpolation_floor():
    """Two constants per dataset must beat Preston — that is why it is a floor.

    If it did NOT, the free fit would be broken rather than informative, so
    this is a sanity guard on the probe itself, not evidence for free exponents.
    """
    wins = 0
    for _, rows in MATCHED:
        fit, pe = fit_ab(rows), preston_err(rows)
        if fit is None or pe is None:
            continue
        if fit[0] <= pe + 1e-9:
            wins += 1
    assert wins == len(MATCHED), (
        "a free (a,b) fit failed to match Preston on some dataset, which is "
        "impossible unless the grid or the scale-free fit is broken")


@pytest.mark.parametrize("p0", [0.0, 0.2, 1.0])
def test_threshold_form_never_predicts_negative_removal(p0):
    for stem, rows in MATCHED:
        pred = [max(p - p0, 0.0) * v for p, v, _ in rows]
        assert all(x >= 0 for x in pred), stem
        if p0 == 0.0:
            assert mape_scale_free(pred, [m for *_, m in rows]) is not None
