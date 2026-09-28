"""The ceria pH-valley marker was single-sourced, and the second source REFUTES
its stated mechanism while leaving its decision intact.

BACKGROUND.  `data/params/sti_ceria.yaml` carries
`ph_response_is_unimodal_but_this_system_is_not: true`, a marker key whose job
is to stop a later session "fixing" netzband2020 by flattening `ph_peak` (which
would cost dandu2009 a factor of 15).  Its stated ground is Netzband's own
explanation of the valley: TWO isoelectric points, the oxide's (pH 2-3) and
ceria's (~8), with pH 6 optimal for neither.

THAT GROUND IS A MECHANISM CLAIM, AND A MECHANISM CLAIM IS TRANSFERABLE --
which makes it falsifiable outside the corpus.  If two straddling isoelectric
points produce a valley, then another ceria-on-oxide pH sweep whose ceria and
oxide isoelectric points straddle the swept range must also show one.

Dawkins 2019 (UAlberta PhD, doi:10.7939/r3-g3c2-xe63) is exactly that
experiment and shows NO VALLEY in either of its two panels -- while measuring
the same two isoelectric points (ceria pH 9.0-9.6, silica negative over
pH 3-13).  So the mechanism is present and the consequence is absent.

WHAT THIS TEST FIXES IN PLACE, in the order that matters:

1. The DECISION does not change.  The pack keeps one unimodal bell and its
   current constants; netzband2020 stays an honest, unrepaired miss.  A
   refutation of a reason is not a licence to refit.
2. The REASON is narrowed from a general mechanism to a statement about one
   dataset, and the narrowing is asserted against the pack's own note so the
   over-claiming sentence cannot quietly come back.
3. The evidence file is PARSED, never restated, so the claim and its numbers
   cannot drift apart (the rule that `psd_width_sign_evidence.yaml` is read
   under, docs/limits.md §38/§40).
4. `magnitude` must stay null.  The failure mode of a shape-evidence file is a
   shape quietly growing into a constant, and this one CANNOT become a scored
   dataset: the slurry is a ceria/silica composite and `sti_ceria` is a
   pure-ceria pack with no composite-abrasive term (docs/limits.md §27).
"""
from __future__ import annotations

import math
import statistics
from pathlib import Path

import pytest
import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.models.chemical_rate import ph_response

EVIDENCE = (Path(__file__).resolve().parents[1]
            / "research" / "ceria_ph_valley_second_source.yaml")

#: netzband2020's measured series, the incumbent and still the only valley.
NETZBAND_PH = [4.0, 6.0, 8.0, 10.0]
NETZBAND = [198.0, 113.0, 200.0, 213.0]


@pytest.fixture(scope="module")
def ev():
    return yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))


def _interior_minima(series, tol_pct=0.0):
    """Interior minima deeper than `tol_pct` on BOTH sides.

    `tol_pct = 0` is the bare arithmetic reading and is the wrong question for
    a raster digitisation: Dawkins panel (a) ends 182, 183 nm/min, a 0.5 %
    step, and calling that a second extremum is exactly the noise-as-finding
    error docs/limits.md §40 was written about (two residual slopes of opposite
    sign, both consistent with zero, read as a disagreement).

    So the caller passes the reading's own DEMONSTRATED precision -- the worst
    disagreement between the figure reading and the numbers the thesis prints
    in prose -- and a dip shallower than that is not a measurement of a dip.
    The bar is therefore derived from the evidence file rather than chosen,
    and it tightens automatically if a better transcription ever lands.
    """
    out = []
    for i in range(1, len(series) - 1):
        lo, mid, hi = series[i - 1], series[i], series[i + 1]
        depth_left = 100 * (lo - mid) / mid
        depth_right = 100 * (hi - mid) / mid
        if depth_left > tol_pct and depth_right > tol_pct:
            out.append(i)
    return out


def _interior_maxima(series):
    return [i for i in range(1, len(series) - 1)
            if series[i] > series[i - 1] and series[i] > series[i + 1]]


def _best_bell_mape(phs, measured):
    """Best scale-free error of ONE unimodal bell over a coarse full grid.

    One free multiplicative scale per series, which is exactly the freedom the
    repository's shape scorer grants a dataset.
    """
    best = 1e9
    for peak_q in range(8, 49):                       # pH 2.00 .. 12.00
        peak = peak_q / 4
        for width_q in range(2, 41):                  # 0.50 .. 10.00
            width = width_q / 4
            for floor in (0.0, 0.15, 0.3, 0.5, 0.7, 0.95):
                for acid in (0.0, 0.012, 0.1, 0.3, 0.7, 0.95):
                    pred = [ph_response(p, peak, width, floor, acid)
                            for p in phs]
                    denom = sum(p * p for p in pred)
                    if denom <= 0:
                        continue
                    k = sum(m * p for m, p in zip(measured, pred)) / denom
                    e = 100 * statistics.mean(
                        [abs(k * p - m) / m for m, p in zip(measured, pred)])
                    best = min(best, e)
    return best


# ---------------------------------------------------------------------------
# the source is real, independent, and self-verified before it is used
# ---------------------------------------------------------------------------

def test_the_evidence_file_exists_and_is_outside_the_scored_corpus(ev):
    assert EVIDENCE.is_file()
    assert ev["independent_of_corpus"] is True
    # it must NOT have been promoted into the scored corpus
    datasets = (Path(__file__).resolve().parents[1]
                / "cmp_sim" / "data" / "validation" / "datasets")
    assert not list(datasets.glob("*dawkins*")), (
        "the Dawkins thesis has been turned into a scored dataset. It is a "
        "ceria/silica COMPOSITE abrasive and sti_ceria is a pure-ceria pack "
        "with no composite term, so scoring it attributes a composite-particle "
        "response to a ceria constant (docs/limits.md §27).")


def test_the_reading_was_graded_against_the_authors_own_printed_numbers(ev):
    """A raster digitisation nobody can check is not admissible here."""
    sv = ev["self_verification"]
    assert len(sv["checks"]) >= 5, (
        "fewer than five independently printed quantities were checked; one or "
        "two can be coincidence")
    assert sv["worst_disagreement_pct"] < 5.0, sv["worst_disagreement_pct"]
    for chk in sv["checks"]:
        assert chk["disagreement_pct"] < 5.0, chk


def test_the_evidence_stays_shape_only(ev):
    """The failure mode of a shape file is a shape growing into a constant."""
    assert ev["magnitude"] is None
    assert ev["axis"] == "ph_response_shape"


# ---------------------------------------------------------------------------
# the finding: the mechanism claim does not transfer
# ---------------------------------------------------------------------------

def test_netzband_really_is_a_valley(ev):
    """Guard the comparison's other half, so the contrast cannot go stale."""
    assert _interior_minima(NETZBAND) == [1], NETZBAND
    assert _interior_maxima(NETZBAND) == [], NETZBAND


def test_the_second_source_has_no_valley_in_either_panel(ev):
    """No interior minimum DEEPER THAN THE READING'S OWN PRECISION.

    The bar is the file's `worst_disagreement_pct` (3.6 % here), i.e. the
    largest error the reading demonstrably makes against numbers the thesis
    prints itself. Panel (a) ends 182, 183 -- a 0.5 % step, seven times inside
    that -- so it is flat, not a valley. Netzband's dip is 43 % deep and clears
    the same bar by more than an order of magnitude, which is why the contrast
    survives being measured honestly instead of arithmetically.
    """
    assert ev["valley_present"] is False
    tol = ev["self_verification"]["worst_disagreement_pct"]
    panels = ev["series"]
    assert len(panels) >= 2, "a single panel is one experiment, not two"

    # non-vacuity: the bar must not be so loose that nothing could ever fail it
    assert tol < 10.0, tol
    assert _interior_minima(NETZBAND, tol) == [1], (
        f"the incumbent valley must still be detectable at the same {tol}% "
        "bar, or the bar is doing the refuting rather than the data")

    for panel in panels:
        oxide = panel["oxide_nm_per_min"]
        assert len(oxide) >= 4, panel["label"]
        assert _interior_minima(oxide, tol) == [], (
            f"{panel['label']} now shows an interior minimum deeper than the "
            f"reading precision {tol}%: {oxide}. If a second independent "
            f"valley has arrived, the exit condition in {EVIDENCE.name} has "
            "fired: re-open the second-pH-channel case rather than editing "
            "this test.")


def test_one_bell_represents_the_second_source_and_not_the_first(ev):
    """The quantitative form of the same statement, on the shipping function."""
    netzband_best = _best_bell_mape(NETZBAND_PH, NETZBAND)
    assert netzband_best > 12.0, (
        f"one bell now fits netzband2020 to {netzband_best:.1f}%; the whole "
        "diagnosis in sti_ceria.yaml assumes it cannot")

    phs = ev["ph_levels"]
    for panel in ev["series"]:
        best = _best_bell_mape(phs, panel["oxide_nm_per_min"])
        assert best < netzband_best, (
            f"{panel['label']}: one bell scores {best:.1f}% against "
            f"netzband's {netzband_best:.1f}%. The claim is that the dissenter "
            "is netzband, not the function.")


# ---------------------------------------------------------------------------
# and the decision does not move
# ---------------------------------------------------------------------------

def test_the_pack_still_keeps_one_unimodal_bell():
    pack = load_pack("sti_ceria")

    def value(key):
        p = pack.param(key)
        return p.value if hasattr(p, "value") else p

    assert value("ph_response_is_unimodal_but_this_system_is_not") is True, (
        "the marker was withdrawn. One refuted REASON is not grounds for "
        "withdrawing the decision it guards: flattening ph_peak still costs "
        "dandu2009 a factor of 15.")
    assert abs(value("ph_peak") - 4.5) < 1e-9, value("ph_peak")


def test_the_marker_no_longer_asserts_the_refuted_mechanism_as_general():
    """Fix the wrong SENTENCE where it lives, not only in a docs file."""
    text = (Path(__file__).resolve().parents[1]
            / "cmp_sim" / "data" / "params" / "sti_ceria.yaml"
            ).read_text(encoding="utf-8")
    assert "dawkins" in text.lower(), (
        "sti_ceria.yaml still explains the valley with the two-isoelectric-"
        "point mechanism and does not mention the independent sweep that has "
        "the same two isoelectric points and no valley. A later session "
        "reading only the pack would inherit the over-claim.")


def test_ph_response_is_still_structurally_unable_to_make_a_valley():
    """The property the whole argument rests on, asserted directly."""
    for peak in (2.0, 4.5, 6.0, 8.5, 11.0):
        for width in (0.5, 1.2, 3.0):
            resp = [ph_response(p, peak, width, 0.15, 0.012)
                    for p in NETZBAND_PH]
            assert _interior_minima(resp) == [], (peak, width, resp)
    assert math.isfinite(ph_response(7.0, 4.5, 1.2, 0.15, 0.012))
