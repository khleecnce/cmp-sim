"""Score the model on every measured axis, and refuse to let the numbers rot.

The P*V gate answers one question well: does Preston's law hold. It fits one
constant per dataset and reports the residual. But it only admits datasets
where pressure or speed varies, which in this repository is 6 of 38 files and
about 40% of the measured points. The pH sweeps, oxidizer series, loading
sweeps and particle-size sweeps -- the slurry axes this simulator exists to
predict -- were never scored against a measurement at all.

These tests close that gap. They are deliberately written as thresholds on the
CURRENT measured performance, so that a change which improves one axis by
wrecking another cannot pass quietly.
"""
from __future__ import annotations

import math

import pytest
import yaml

from cmp_sim.core.predictive_score import score_all, score_dataset
from cmp_sim.core.validation import dataset_paths


@pytest.fixture(scope="module")
def scores():
    return {s.dataset: s for s in score_all()}


# ── the headline numbers ─────────────────────────────────────────────
def test_most_datasets_can_actually_be_run(scores):
    """A dataset the engine cannot run is not evidence of anything.

    A dataset the engine DECLINES to run is a different thing, and is counted
    separately below: a regime gate means the pack states its constants were
    never measured in that regime, so predicting there would be extrapolation
    with a sign the data contradict. That is a data gap, not a broken engine,
    and it must not be laundered into either bucket — hence two assertions.
    """
    ran = [s for s in scores.values() if s.shape_mape is not None]
    declined = [s for s in scores.values() if s.gated_reason and s.error]
    broken = [s for s in scores.values()
              if s.error and not s.gated_reason]
    assert len(ran) + len(declined) >= 37, (
        f"only {len(ran)}/{len(scores)} datasets ran and {len(declined)} were "
        "declined for a declared reason: "
        + "; ".join(f"{s.dataset}: {s.error}" for s in broken)[:600])
    # The gate must stay narrow. If it ever silences a large share of the
    # corpus, it has stopped being a statement about one pH branch and become
    # a way of not being scored.
    assert len(declined) <= 3, (
        "too many datasets are being declined rather than predicted: "
        + ", ".join(s.dataset for s in declined))


def test_every_declined_dataset_names_the_missing_measurement(scores):
    """Silence is only acceptable if it is specific.

    A gated dataset must say which regime is unmeasured and why the sign
    cannot be extrapolated, so the gap is actionable as an experiment rather
    than a permanent excuse.
    """
    declined = [s for s in scores.values() if s.gated_reason]
    assert declined, "the regime gate is wired but nothing exercises it"
    for s in declined:
        assert "GATED" in s.gated_reason
        assert "measured between pH" in s.gated_reason, s.dataset
        assert s.gated > 0, s.dataset


def test_the_median_shape_error_does_not_regress(scores):
    """Median over every scored dataset. Was 42.8% when the pH term was inert
    and the size exponent had the wrong sign; 20.3% after both were fixed."""
    ran = sorted(s.shape_mape for s in scores.values()
                 if s.shape_mape is not None)
    median = ran[len(ran) // 2]
    assert median <= 25.0, f"median shape error regressed to {median:.1f}%"


def test_the_median_out_of_sample_error_does_not_regress(scores):
    """Leave-one-out, so this is prediction rather than description."""
    ran = sorted(s.loo_mape for s in scores.values()
                 if s.loo_mape is not None)
    median = ran[len(ran) // 2]
    assert median <= 30.0, f"median leave-one-out regressed to {median:.1f}%"


def test_the_physics_beats_predicting_the_mean_on_most_datasets(scores):
    """The baseline that matters: if the model cannot beat "assume the average
    of this dataset", its physics contributed nothing on that dataset."""
    ran = [s for s in scores.values() if s.beats_flat is not None]
    won = [s for s in ran if s.beats_flat]
    assert len(won) >= len(ran) * 0.6, (
        f"only {len(won)}/{len(ran)} datasets beat predicting the mean: "
        + ", ".join(s.dataset for s in ran if not s.beats_flat))


# ── per-axis: each slurry knob must actually move the rate ───────────
@pytest.mark.parametrize("axis,limit", [
    ("slurry_ph", 75.0),
    ("abrasive_wt_pct", 45.0),
    ("oxidizer_wt_pct", 95.0),
])
def test_each_slurry_axis_is_predicted_to_a_stated_accuracy(scores, axis, limit):
    """Per-axis thresholds, set from the current measured performance.

    The limits are not equal because the axes are not equally well modelled,
    and pretending otherwise would hide which one to fix next. Oxidizer is the
    loosest: Du 2004's peak sits at 1 vol% with only one point below it, so
    the rising limb is barely constrained.
    """
    sel = [s for s in scores.values()
           if s.shape_mape is not None and axis in s.axes]
    assert sel, f"no scored dataset varies {axis}"
    median = sorted(s.shape_mape for s in sel)[len(sel) // 2]
    assert median <= limit, (
        f"{axis}: median shape error {median:.1f}% over {len(sel)} datasets "
        f"exceeds {limit}%. Worst: "
        + ", ".join(f"{s.dataset} {s.shape_mape:.0f}%"
                    for s in sorted(sel, key=lambda x: -x.shape_mape)[:3]))


def test_the_ph_term_is_not_inert(scores):
    """The specific regression that motivated all of this: the packs carried
    ph_peak and ph_ref but no width, so pH 2 and pH 10 returned the same
    number. Dandu's sweep moves 81x and must not be answered with a constant.

    The threshold is 35%, not something tighter, and that is a real limit
    rather than slack. A symmetric Gaussian cannot reproduce this shape: the
    measurement rises 22x between pH 2 and 3.5, holds a plateau to 5.5, then
    steps down 3.5x at pH 6 and flattens into a long alkaline tail. Fitted to
    Dandu ALONE the best a bell can do is 26.5%; the pack also has to serve
    Netzband's thermal-oxide sweep, which peaks at the opposite end, and the
    joint optimum is 34%. Tightening this number would mean fitting one of the
    two sweeps and abandoning the other.

    What it does guarantee: pH still moves the rate by the right order, and
    the 244% failure (mis-normalised term, effectively unbounded) cannot
    return.
    """
    s = scores.get("dandu2009_sio2_ceria_ph_sweep")
    assert s is not None and s.shape_mape is not None
    assert s.shape_mape <= 35.0, (
        f"the ceria pH sweep is back to {s.shape_mape:.1f}%; it was 244% when "
        "the term was mis-normalised and effectively unbounded")
    assert s.beats_flat, (
        "the pH term no longer beats predicting the dataset mean, which means "
        "it has stopped contributing anything on an 81x sweep")


def test_the_size_exponent_has_the_right_sign_on_every_measured_sweep():
    """Eight of ten measured sweeps rise with particle size; the derived
    exponent was -0.84 for every pack. Checks the SIGN, dataset by dataset,
    because a good average can hide a systematic inversion."""
    from cmp_sim.core.predictive_score import _measured, _predict

    wrong = []
    for path in sorted(dataset_paths()):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        sizes = [((r.get("overrides") or {}).get("abrasive_d50_nm")
                  or (r.get("overrides") or {}).get("abrasive_size_nm"))
                 for r in rows]
        # Sort on the size alone: two rows can share a size AND a measured
        # rate, and a tuple sort would then fall through to comparing the
        # raw dicts (TypeError).
        pts = sorted(((float(s), _measured(r), r)
                      for s, r in zip(sizes, rows) if s),
                     key=lambda t: (t[0], t[1]))
        if len(pts) < 3 or len({p[0] for p in pts}) < 3:
            continue
        n_data = (math.log(pts[-1][1] / pts[0][1])
                  / math.log(pts[-1][0] / pts[0][0]))
        lo, hi = _predict(doc, pts[0][2]), _predict(doc, pts[-1][2])
        if not (lo and hi):
            continue
        n_model = math.log(hi / lo) / math.log(pts[-1][0] / pts[0][0])
        # Only flag a real inversion: both slopes clearly non-zero, opposite.
        if abs(n_data) > 0.15 and abs(n_model) > 0.15 and n_data * n_model < 0:
            wrong.append((path.stem, round(n_data, 2), round(n_model, 2)))
    assert not wrong, f"the size exponent is inverted on: {wrong}"


# ── the disagreements, pinned so they cannot be quietly averaged away ──
def test_the_two_oxide_loading_datasets_no_longer_disagree():
    """They disagreed because of a BUG, and the constant that mediated is gone.

    Until 2026-09-27 this test recorded a finding: us9499721b2 (0.5-3 wt%) was
    best fitted by ``abrasive_conc_half_wt_pct`` ~ 0.6 and us6564116b2
    (5-25 wt%) by ~5.9, so the pack carried a compromise (4.4, confidence low)
    and both datasets were held away from excellence to keep the conflict
    visible.

    Both of those numbers were fitted while the saturating branch of
    ``models/luo_dornfeld.mechanical_factor`` multiplied by the active-particle
    COUNT ratio (N^1), asserting chi = 0 against the chi = 1.0 the same call
    resolves. With the load-sharing exponent restored, a re-scan found BOTH
    datasets at or near their best with the constant ABSENT, and
    ``tools/conc_half_necessity_probe.py`` then found it NEEDED on zero of the
    corpus's seven iso-condition loading series. It was withdrawn from all
    three packs that carried a value.

    So the assertion flips: the two datasets must now BOTH be reasonable at
    once, which the compromise could not manage. If a saturation constant is
    ever restored, the old conflict should return and this test should fail.
    """
    a = score_dataset(next(p for p in dataset_paths()
                           if p.stem.startswith("us9499721b2")))
    b = score_dataset(next(p for p in dataset_paths()
                           if p.stem.startswith("us6564116b2")))
    assert a.shape_mape is not None and b.shape_mape is not None
    assert max(a.shape_mape, b.shape_mape) <= 22.0, (
        f"the two oxide loading datasets are in conflict again: "
        f"{a.dataset} {a.shape_mape:.1f}%, {b.dataset} {b.shape_mape:.1f}%. "
        "Check whether abrasive_conc_half_wt_pct was restored — with the "
        "withdrawn 4.4 wt% the pair read 7.8% / 23.9%, and without it "
        "8.2% / 20.6%.")
    # And the one that PAID for the withdrawal must not have been bought back
    # by re-fitting: it was 7.8% with the compromise and 8.2% without.
    assert a.shape_mape >= 7.0, (
        f"{a.dataset} is at {a.shape_mape:.1f}%, better than it was WITH the "
        "withdrawn constant. That dataset is what the constant was fitted on, "
        "so a gain here is the signature of a refit rather than a derivation")


def test_no_pack_carries_a_saturation_constant_that_is_never_necessary():
    """The withdrawal is structural, so pin the CONDITION, not the absence.

    ``abrasive_conc_half_wt_pct`` is the repo's clearest example of a fitted
    constant whose justification evaporated: every pack's note argued it was
    needed to bend a +1.0 model slope down to a measured +0.15..+0.53, and
    that +1.0 turned out to be a load-sharing bug on the same line. Once the
    bug was fixed the bare power law's own slope (+0.333) was already inside
    every measured band.

    A constant may legitimately come back — saturation at high loading is real
    physics — but only with a series where it is NECESSARY, meaning the model
    leaves the measured band without it. This test states that bar.
    """
    from cmp_sim.core.params import load_pack

    for name in ("oxide_silica", "cu_h2o2_bta", "w_fe_oxidizer",
                 "sic_ceria_h2o2", "sti_ceria"):
        pack = load_pack(name)
        value = pack.get_or("abrasive_conc_half_wt_pct", None)
        note = (pack.param("abrasive_conc_half_wt_pct").note or "").lower()
        if value is None:
            # The refusal must carry its own exit condition, not be silent.
            assert "todo(owner)" in note, (
                f"{name} leaves the saturation constant null without saying "
                "what measurement would restore it")
            continue
        assert "withdrawn" not in note, (
            f"{name} carries abrasive_conc_half_wt_pct = {value} while its "
            "own note still says WITHDRAWN. Restoring the value without "
            "rewriting the justification re-introduces exactly the constant "
            "whose reasoning was retracted.")
        assert "necessary" in note and "series" in note, (
            f"{name} restored abrasive_conc_half_wt_pct = {value} without "
            "recording a series on which it is NECESSARY (the model leaving "
            "the measured loading band without it). Run "
            "tools/conc_half_necessity_probe.py: the withdrawal was decided "
            "by NEEDED 0 / HARMFUL 1 / redundant 6 over seven series.")


def test_the_anionic_silica_system_got_its_own_pack_not_a_wider_bell():
    """CN109609035B was ~95% wrong, and the fix was a pack split.

    It measures a 22x FALL from pH 2 to pH 5 with anionic silica, i.e. its
    optimum is at or below pH 2. `oxide_silica`'s optimum is pH 11, measured by
    Li 2021 on a conventional alkaline slurry. Same film, same abrasive
    mineral, opposite charge sign — different slurry SYSTEMS, so serving both
    from one pack put the acid series entirely on the mechanical floor.

    The earlier version of this test recorded the error as accepted, listing
    two options: widen the bell to span pH 2-12 (which would flatten the pH
    dependence everywhere and wreck Li 2021), or give the system its own pack.
    The second was taken, following `oxide_silica_aminosilane`.

    The assertions below are the ones that make it a fix rather than a
    flattering refit: the split must not have moved the other two silica
    systems, and the residual must still be honest about what the single-bell
    form cannot do.
    """
    from cmp_sim.core.predictive_score import score_dataset

    def _score(stem):
        return score_dataset(next(p for p in dataset_paths() if p.stem == stem))

    anionic = _score("cn109609035b_oxide_anionic_silica_ph")
    assert anionic.shape_mape is not None, "it must at least RUN"
    assert anionic.shape_mape < 40.0, anionic.shape_mape
    assert anionic.beats_flat

    # The other two silica systems must be untouched — that is the whole point
    # of splitting rather than widening.
    assert _score("li2021_oxide_silica_ph").shape_mape < 1.0, (
        "the plain-silica calibration regressed, so the bell WAS widened")
    assert _score("us9422456b2_teos_silica_ph_pressure").shape_mape < 30.0, (
        "the cationic core-shell pack regressed")

    # And the residual must not be fitted away: a monotone-decaying bell cannot
    # reproduce the measured upturn at pH 6, which the patent attributes to a
    # second (alkaline hydrolysis) mechanism.
    assert anionic.shape_mape > 20.0, (
        "the anionic dataset is now fitted closely, which a single-bell pH "
        "response should not manage against the pH 6 upturn. Check that a "
        "second pH channel was not quietly added, or that the upturn point "
        "was not dropped")


def test_sic_declares_no_loading_saturation():
    """SiC's six iso-condition series run -0.40 to +1.43, including two that
    FALL with loading. No saturating form can produce that, so the pack must
    leave the constant null rather than fitting through a contradiction."""
    from cmp_sim.core.params import load_pack

    pack = load_pack("sic_ceria_h2o2")
    assert pack.get_or("abrasive_conc_half_wt_pct", None) is None
    note = (pack.param("abrasive_conc_half_wt_pct").note or "").lower()
    assert "todo(owner)" in note
    assert "contradiction" in note or "denies" in note
