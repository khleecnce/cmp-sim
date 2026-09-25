"""The derived pH rate law is FALSIFIED — pinned so it is not re-attempted.

STATUS.md's NEXT proposed replacing the fitted pH Gaussian with

    r ~ [OH(-)-catalysed hydrolysis, half order, Brady & Walther 1990]
        * [electrostatic attraction between abrasive and film at their IEPs]

on the grounds that both legs come from laws and the combination would remove
the 3 fitted constants each pack carries. `tools/ph_derived_probe.py` ran it.
It lost, and — more usefully — the ABLATION says WHICH leg lost: dropping the
law-backed kinetic leg IMPROVES the fit. That is the fact this test pins,
because it is the one that would otherwise be forgotten and re-derived.

This is the SECOND falsification of a derived pH form in this repo (the first
was a 2-pKa surface-complexation product, 27.3 % vs 17.7 % on Dandu). Per the
rule written into that NEXT item, the pH axis is now closed to further
closed-form attempts until the corpus has more pH sweeps: 6 usable sweeps with
4 distinct peak positions cannot determine a form whose peak is free.
"""
from __future__ import annotations

import math
import statistics

import pytest

from tools.ph_derived_probe import (
    FILM_IEP,
    IEP,
    N_DISSOLUTION,
    SILANOL_PKA,
    derived,
    load_ph_groups,
    shape_error,
)


@pytest.fixture(scope="module")
def groups():
    g = load_ph_groups()
    assert len(g) >= 5, (
        "the probe found too few pH sweeps to conclude anything; if a dataset "
        "was renamed, fix the loader rather than lowering this bound")
    return g


def _elec(ph: float, g: dict, alpha: float, b: float) -> float:
    return math.exp(-b * math.tanh(alpha * (IEP[g["abrasive"]] - ph))
                    * math.tanh(alpha * (FILM_IEP[g["film"]] - ph)))


def _median(fn, groups) -> float:
    return statistics.median(
        shape_error([fn(p, g) for p, _ in g["points"]],
                    [m for _, m in g["points"]]) for g in groups)


def test_the_law_backed_kinetic_leg_makes_the_fit_worse(groups):
    """The decisive ablation: S(pH)**0.5 is not a component of the CMP rate.

    If half-order hydroxide catalysis were the chemical leg of removal, adding
    it to the electrostatic leg would help. It does the opposite. Reason:
    S(pH)**0.5 is monotone increasing in pH by construction, but 4 of the 6
    measured sweeps PEAK IN ACID. Dissolution kinetics set the hydrated layer's
    thickness (which saturates), not the removal rate.
    """
    best_full = min(
        _median(lambda p, g, a=a, b=b: derived(
            p, IEP[g["abrasive"]], FILM_IEP[g["film"]], a, b), groups)
        for a in (0.4, 0.6, 0.8, 1.0) for b in (1.0, 2.25, 3.75, 5.0))
    best_elec = min(
        _median(lambda p, g, a=a, b=b: _elec(p, g, a, b), groups)
        for a in (0.4, 0.6, 0.8, 1.0) for b in (1.0, 2.25, 3.75, 5.0))

    assert best_elec < best_full, (
        f"electrostatic-only {best_elec:.1f}% should beat kinetic x "
        f"electrostatic {best_full:.1f}%; if this ever reverses the "
        "falsification has been overturned and the NEXT item reopens")
    assert best_full - best_elec > 10.0, (
        "the ablation gap was ~25 points when measured; a gap that has shrunk "
        "below 10 means the corpus changed enough to re-run the probe")


def test_the_kinetic_leg_alone_is_not_a_ph_model(groups):
    """Zero constants, and ~94 % error — recorded so nobody re-tries it bare."""
    kin = _median(
        lambda p, g: (1.0 / (1.0 + 10.0 ** (SILANOL_PKA - p))) ** N_DISSOLUTION,
        groups)
    assert kin > 60.0, (
        f"half-order hydroxide kinetics alone scored {kin:.1f}%; it was 93.6% "
        "and is expected to stay a clear failure")


def test_the_incumbent_gaussian_is_an_interpolator_on_the_thin_sweeps(groups):
    """Guards against reading the Gaussian's in-sample 11 % as accuracy.

    The Gaussian fits 4 constants (peak, width, floor, acid_floor) per group.
    Any group with <= 4 pH levels therefore has constants >= data and cannot
    be evidence for the form. This test states how many such groups exist so
    the number cannot drift unnoticed.
    """
    thin = [g for g in groups if len({p for p, _ in g["points"]}) <= 4]
    assert thin, (
        "at least li2021 (3 levels) and netzband2020 (4) are constants-vs-data "
        "ties; if none remain, the corpus grew and the pH NEXT item reopens")
    for g in thin:
        n = len({p for p, _ in g["points"]})
        assert n <= 4 <= 4, f"{g['dataset']} has {n} pH levels"
