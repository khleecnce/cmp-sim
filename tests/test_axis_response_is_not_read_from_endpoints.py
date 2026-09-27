"""An axis's response cannot be read from its ENDPOINTS (docs/limits.md §44).

Why this exists
---------------
`tools/inert_axis_scan.py` and `tools/residual_census.py` decide whether a
swept input reaches the rate by running the dataset's first row twice -- at the
axis minimum and at the axis maximum the paper ran -- and comparing the two
predicted rates. Every admissibility filter downstream reads that map, so those
two points are the single reader behind a large family of closure arguments
here ("0 silent inert axes", `Census.responsive_axes`, the oxidiser probe's
confound test).

§43 established that the perturbation is part of the instrument, and fixed the
probe whose displacement it controlled. It could not fix this one: here the two
evaluation points are **not chosen by the probe at all** -- they are the first
and last level of the PUBLICATION's design. So the cancellation arrives through
the data, and no change to a perturbation constant avoids it.

The cancellation is exact, not statistical. For any peaked `f`, two levels
placed symmetrically about the optimum give ``f(lo) == f(hi)`` for **every**
width -- the same identity §43 found in its own displacement, now reached from
the other side. This repository models several peaked responses (the Gaussian
pH term, the oxidiser Langmuir, the IEP-referenced zeta terms), and the better
the experiment -- the more levels it ran -- the more of them the endpoint
reading throws away.

Measured (`tools/interior_level_response_probe.py`): 4 of 83 multi-level axes
are UNDERSTATED, the worst by 1.9x (`us9422456b2` pH, 11 levels: endpoint
51.8 % against 98.2 % across the sweep). None of the 22 genuinely inert axes
changes class, so this fix moves no verdict -- it removes the possibility of a
verdict nobody could have checked.

Nothing here is pinned as a literal. Every number is re-measured through the
shipping solver at run time, because the pH and oxidiser constants are sourced
and re-sourcing them must break the CODE's claim, not leave a stale sentence
behind (the §40 failure mode).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import interior_level_response_probe as ilrp  # noqa: E402
import residual_census as rc  # noqa: E402

from cmp_sim.core.predictive_score import (  # noqa: E402
    _measured, score_all,
)
from cmp_sim.core.validation import dataset_paths

#: The measured understated axes. Used only to keep the run affordable -- every
#: claim below is re-measured, and the non-vacuity test fails if this list stops
#: describing the corpus.
UNDERSTATED = {
    "us9422456b2_teos_silica_ph_pressure": "slurry_ph",
    "li2021_oxide_silica_ph": "slurry_ph",
    "dandu2009_sio2_ceria_ph_sweep": "slurry_ph",
    "du2004_cu_h2o2_concentration_sweep": "h2o2_vol_pct",
}

#: An axis whose endpoints DO span its response. The probe must recover it, or
#: it is not measuring anything (§43's instrument control).
CONTROL = "netzband2020_thermal_oxide_ceria_ph"


@pytest.fixture(scope="module")
def scores():
    return score_all()


@pytest.fixture(scope="module")
def result(scores):
    return ilrp.probe(scores, only=set(UNDERSTATED) | {CONTROL})


def _doc_and_rows(stem: str):
    for path in dataset_paths():
        if Path(path).stem == stem:
            doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
            rows = [r for r in (doc.get("conditions") or [])
                    if _measured(r) is not None]
            return doc, rows
    raise AssertionError(f"{stem} is not in the corpus")


def test_the_probe_recovers_an_endpoint_responsive_axis(result):
    """Instrument control: a probe that sees nothing proves nothing (§43)."""
    assert result.control_passed, (
        "no examined axis had an endpoint-responsive reading -- the likelier "
        "reading is that the harness never reached the solver, so no verdict "
        "in this file may be quoted")


def test_the_endpoint_reading_understates_a_real_axis(result):
    """The finding, re-measured: some axis moves more inside than across."""
    understated = result.by_kind("understated")
    assert understated, (
        "no axis is understated by its endpoint pair. Either the peaked terms "
        "were withdrawn (then delete this limit, do not weaken it) or the "
        "restricted dataset list above has gone stale")
    worst = max(understated, key=lambda r: r.understatement or 0.0)
    assert worst.understatement > 1.1, (
        f"the worst understatement is only x{worst.understatement:.2f} "
        f"({worst.dataset}/{worst.axis}); §44 claims the endpoint pair can "
        "hide a large part of a response")


def test_the_census_now_publishes_the_full_range_not_the_endpoints():
    """The repair, measured end to end on the tool the filters actually read.

    `residual_census._axis_response` is what `responsive_axes` and every
    admissibility filter consume. It must return the widest reading over all
    levels, which on an understated axis is strictly larger than the endpoint
    difference this repository published until §44.
    """
    checked = 0
    for stem, axis in UNDERSTATED.items():
        doc, rows = _doc_and_rows(stem)
        values = sorted({v for v in (rc._axis_value(r, axis) for r in rows)
                         if isinstance(v, (int, float))})
        if len(values) < 3:
            continue
        lo = rc._predict(doc, rc._with_axis(rows[0], axis, values[0]))
        hi = rc._predict(doc, rc._with_axis(rows[0], axis, values[-1]))
        if lo is None or hi is None:
            continue
        endpoint = 100.0 * abs(hi - lo) / max(hi, lo)
        published = rc._axis_response(doc, rows, axis)
        assert published is not None
        assert published >= endpoint - 1e-9, (
            f"{stem}/{axis}: the census publishes {published:.2f}% but the "
            f"endpoint pair alone gives {endpoint:.2f}% -- the full-range "
            "reading can never be the smaller of the two")
        if published > endpoint + 0.5:
            checked += 1
    assert checked, (
        "on no understated axis does the census reading now exceed the "
        "endpoint reading -- the §44 repair is not in effect")


def test_the_inert_scan_reads_the_same_repaired_response(scores):
    """`inert_axis_scan` keeps its own copy of the comparison; both must move.

    A repair applied to one of two duplicated readers is how a fixed limit
    reappears: the scan's `silent`/`declared` classification is the published
    artefact, and it computed its own endpoint difference inline.
    """
    import inert_axis_scan as ias

    stem = max(UNDERSTATED, key=lambda s: len(_doc_and_rows(s)[1]))
    axis = UNDERSTATED[stem]
    subset = [s for s in scores if s.dataset == stem]
    assert subset, f"{stem} must be scored for this test to mean anything"

    doc, rows = _doc_and_rows(stem)
    values = sorted({v for v in (rc._axis_value(r, axis) for r in rows)
                     if isinstance(v, (int, float))})
    lo = rc._predict(doc, rc._with_axis(rows[0], axis, values[0]))
    hi = rc._predict(doc, rc._with_axis(rows[0], axis, values[-1]))
    endpoint = 100.0 * abs(hi - lo) / max(hi, lo)

    scanned = ias.scan(subset).response[stem][axis]
    assert scanned > endpoint + 0.5, (
        f"inert_axis_scan reports {scanned:.2f}% for {stem}/{axis} against an "
        f"endpoint-only {endpoint:.2f}% -- it is still reading two points")


def test_a_peaked_term_cancels_at_its_own_mirror_pair_by_derivation():
    """The mechanism, derived on the term itself rather than observed on data.

    `models.chemical_rate.ph_response` is
    ``floor_side + (1 - floor_side) * exp(-((pH - peak)/w)**2)``. At two pH
    levels mirrored about `peak` the exponential is identical for EVERY width,
    so an endpoint-only reader is blind on such a pair by derivation, not by
    coincidence -- exactly the identity §43 found inside its own displacement,
    reached here from the other side.

    The cancellation is exact only when both floors are equal, and the packs
    disagree on that (`sti_ceria` carries an acid floor of 0.012 against an
    alkaline 0.15, `oxide_silica` has no acid floor at all). Both cases are
    asserted, because the asymmetric one is what a naive end-to-end test on the
    solver stumbles over: a 1.6 % mirror residual is not the identity failing,
    it is the two floors differing, and it is still ~40x smaller than the
    response the same sweep's interior carries.
    """
    from cmp_sim.models.chemical_rate import ph_response

    peak, width, floor = 4.5, 1.2, 0.15
    for delta in (0.4, 0.8, 1.6, 3.0):
        below = ph_response(peak - delta, peak, width, floor=floor,
                            acid_floor=floor)
        above = ph_response(peak + delta, peak, width, floor=floor,
                            acid_floor=floor)
        assert abs(above - below) < 1e-12, (
            f"the pH factor differs by {abs(above - below):.3e} between "
            f"pH {peak - delta:g} and pH {peak + delta:g} at equal floors. "
            "§44 rests on that pair being an EXACT cancellation; if the term "
            "is no longer Gaussian, re-derive the section rather than "
            "relaxing this bar")
        interior = ph_response(peak, peak, width, floor=floor,
                               acid_floor=floor)
        assert interior > below * 1.005, (
            "the optimum is not above the mirror pair, so the term is flat "
            "and the cancellation above is not the peaked-response identity")

    # Unequal floors: the mirror pair no longer cancels exactly, and the
    # residual must stay far below the interior response -- otherwise an
    # endpoint reader would not have been blind and §44 would not apply.
    delta = 0.4
    below = ph_response(peak - delta, peak, width, floor=floor, acid_floor=0.012)
    above = ph_response(peak + delta, peak, width, floor=floor, acid_floor=0.012)
    interior = ph_response(peak, peak, width, floor=floor, acid_floor=0.012)
    mirror = 100.0 * abs(above - below) / max(above, below)
    span = 100.0 * abs(interior - below) / max(interior, below)
    assert 0.0 < mirror < span / 5.0, (
        f"with unequal floors the mirror pair differs by {mirror:.3f}% "
        f"against an interior response of {span:.3f}%. §44 needs the endpoint "
        "reading to be much the smaller of the two; if the floors now dominate "
        "the peak, this is a different section")


def test_two_level_axes_are_excluded_and_counted(result):
    """A two-level axis cannot answer this question; it must not be graded.

    Silently including them would fill `agrees` with axes for which the two
    readings are the same measurement, and the section's count would then be a
    statement about how many sweeps are short rather than about the reader.
    """
    assert result.two_level_axes > 0, (
        "no two-level axis was found -- with none excluded this probe's counts "
        "cannot be compared against `inert_axis_scan`'s, which grades them")
    for reading in result.readings:
        assert reading.levels >= ilrp.MIN_LEVELS, (
            f"{reading.dataset}/{reading.axis} was graded on "
            f"{reading.levels} levels")


def test_every_reading_publishes_the_levels_it_used(result):
    """§43's rule: a response of 0.00 % is unquotable without what was tried."""
    for reading in result.readings:
        assert len(reading.rates) == reading.levels, (
            f"{reading.dataset}/{reading.axis} reports {reading.levels} levels "
            f"but recorded {len(reading.rates)} runs")
        assert all(isinstance(lvl, float) for lvl, _ in reading.rates)
