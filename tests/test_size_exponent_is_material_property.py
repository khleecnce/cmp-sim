"""The abrasive-size exponent is a MATERIAL property, not a per-pack handle.

These tests re-derive the claim from the validation corpus every run, so the
numbers written into ``tools/size_derived_probe.py``'s docstring and into
STATUS.md cannot drift away from the data behind them.

Two separate claims are pinned, because they point in opposite directions and
both matter:

1. A SINGLE global size exponent is falsified — the measured exponents scatter
   across roughly half the range a Luo-Dornfeld branch choice spans, so
   "derive one exponent" would pick its branch from the data.
2. The scatter is nevertheless ORGANISED: between-material variance clearly
   exceeds within-material variance, which is what licenses assigning the
   exponent from abrasive identity instead of fitting it per pack.
"""
from __future__ import annotations

import statistics

import pytest

from tools.size_derived_probe import (
    DERIVABLE_MAX,
    DERIVABLE_MIN,
    _abrasive,
    fit_power,
    load_size_groups,
)


@pytest.fixture(scope="module")
def rows():
    out = []
    for g in load_size_groups():
        n, r2 = fit_power(g["points"])
        out.append({"dataset": g["dataset"], "n": n, "r2": r2,
                    "abrasive": _abrasive(g["dataset"], g["pack"]),
                    "k": len({d for d, _ in g["points"]})})
    return out


def test_corpus_has_enough_size_sweeps_to_test_a_size_law(rows):
    # A whitelist of process axes is used for grouping; a blacklist silently
    # split every group into singletons because provenance fields differ per
    # row. If that regresses, this count collapses.
    assert len(rows) >= 9, f"only {len(rows)} usable size groups"
    assert all(r["k"] >= 3 for r in rows)


def test_single_global_size_exponent_is_falsified(rows):
    ns = [r["n"] for r in rows]
    span = (max(ns) - min(ns)) / (DERIVABLE_MAX - DERIVABLE_MIN)
    assert span > 0.3, (
        "the corpus no longer scatters across the derivable range; the "
        "falsification recorded in STATUS.md may no longer hold"
    )
    assert statistics.stdev(ns) > 0.25


def test_between_material_spread_exceeds_within_material_spread(rows):
    by = {}
    for r in rows:
        if r["r2"] >= 0.5:
            by.setdefault(r["abrasive"], []).append(r["n"])
    assert "?" not in by, "an abrasive went unlabelled; _abrasive needs updating"
    multi = {k: v for k, v in by.items() if len(v) > 1}
    assert len(multi) >= 2, "need >=2 materials with replicates to compare"
    within = statistics.pstdev(
        [v - statistics.fmean(vals) for vals in multi.values() for v in vals])
    between = statistics.stdev([statistics.fmean(v) for v in by.values()])
    assert between > 2.0 * within, (
        f"between-material {between:.2f} vs within-material {within:.2f}: the "
        "exponent no longer looks like a material property"
    )


def test_placeholder_packs_do_not_decide_the_abrasive_label(rows):
    """wei2026 and su2011 borrow ``sic_ceria_h2o2`` (their headers say so).

    Reading the pack rather than the filename labels both 'ceria' and
    manufactures a false within-ceria spread. That bug is what this pins.
    """
    assert _abrasive("wei2026_sic_silica_size_sweep", "sic_ceria_h2o2") == "silica"
    assert _abrasive("su2011_sic_alumina_size_sweep", "sic_ceria_h2o2") == "alumina"


def test_ceria_family_exponent_exceeds_silica(rows):
    """The ordering, not the values — this is the transferable part."""
    strong = [r for r in rows if r["r2"] >= 0.5]
    silica = [r["n"] for r in strong if r["abrasive"] == "silica"]
    ceria = [r["n"] for r in strong if r["abrasive"].startswith("ceria")]
    assert silica and ceria
    assert max(silica) < min(ceria), (
        f"silica {silica} no longer sits strictly below ceria {ceria}"
    )
