"""`used_for_calibration` is a SELF-DECLARATION, and 12 datasets get it wrong.

The claim under test
--------------------
Every admissibility filter in this repository -- `absolute_scale_audit` (S4),
`ce3_residual_probe`, `oxidizer_order_probe`, `ph_derived_probe` -- decides
whether a dataset may testify by reading ONE boolean out of the dataset's own
header: ``used_for_calibration``. Nothing had ever checked that boolean against
the packs.

It is checkable. A pack constant records where its value came from in
``source:``. When that string names a dataset in the scored corpus, and the
dataset sweeps an axis that constant governs, then the constant was fitted on
those rows -- so scoring the model against them is grading it on its own answer
key, whatever the header says.

`tools/calibration_flag_audit.py` performs the cross-check. These tests pin its
findings so the state cannot silently grow, and so the headline median is never
again quoted without the held-out figure beside it.

Why this is NOT the forbidden kind of dataset exclusion
-------------------------------------------------------
The standing rule is "never drop a dataset to LOWER the median" (STATUS.md).
The exclusion measured here moves the number the other way -- removing the
blocks the model was fitted on RAISES the median, 18.9% -> 20.2% -- so it is
the one exclusion that rule demands rather than forbids.
"""
from __future__ import annotations

import pytest

from tools.calibration_flag_audit import collect, headline_effect

#: Datasets whose header says `used_for_calibration: false` while a pack
#: constant's `source:` names them on an axis they sweep. Pinned so that a new
#: fitted constant citing a "held-out" dataset fails here instead of quietly
#: improving the headline. Shrinking this list is progress; do it by correcting
#: the dataset's flag (and re-scoring), never by deleting the citation, which
#: would restore the undetectable state (docs/limits.md §27).
KNOWN_SELF_GRADED = {
    "bouvet2002_oxide_silica_size_sweep",
    "bouvet2002_ti_silica_size_sweep",
    "bouvet2002_w_silica_size_sweep",
    "cn109609035b_oxide_anionic_silica_ph",
    "dandu2009_sio2_ceria_ph_sweep",
    "du2004_cu_h2o2_concentration_sweep",
    "lai2001_cu_alumina_size_sweep",
    "son2021_oxide_ceria_size_sweep",
    "su2011_sic_alumina_size_sweep",
    "tw202115224a_cu_abrasive_size_pressure",
    "us9422456b2_teos_silica_ph_pressure",
    "wei2026_sic_silica_size_sweep",
}


@pytest.fixture(scope="module")
def citations():
    return collect()


def test_the_audit_actually_finds_citations(citations):
    """Non-vacuity guard.

    If the stem-matching ever breaks -- a rename, a `source:` rewritten to a
    DOI instead of a dataset name -- every assertion below would pass by
    comparing empty sets. That failure mode is exactly the one this whole file
    exists to prevent, so it must fail loudly rather than go green.
    """
    assert len(citations) >= 40, (
        "the audit found almost no pack constant citing a scored dataset; the "
        "cross-check has probably stopped matching, not the repository stopped "
        "citing")


def test_no_new_dataset_is_graded_on_a_constant_fitted_to_it(citations):
    found = {c.dataset for c in citations if c.implicated}
    new = found - KNOWN_SELF_GRADED
    assert not new, (
        "these datasets declare used_for_calibration: false while a pack "
        "constant's source: names them on an axis they sweep, so the corpus is "
        "scoring the model on its own fit: %s" % sorted(new))


def test_the_known_list_expires_when_a_flag_is_corrected(citations):
    """The exit condition. Fixing one is meant to fail this test.

    Pinning only an upper bound would let the list sit at 12 forever. When a
    dataset's flag is corrected, this fails and the corrected name must be
    removed here -- and the held-out median in STATUS.md re-measured, because
    correcting a flag moves which blocks count.
    """
    found = {c.dataset for c in citations if c.implicated}
    stale = KNOWN_SELF_GRADED - found
    assert not stale, (
        "these datasets are no longer self-graded -- remove them from "
        "KNOWN_SELF_GRADED and re-measure the held-out median: %s"
        % sorted(stale))


def test_the_held_out_median_is_worse_than_the_published_one(citations):
    """A physics-free claim about the score, and the reason this matters.

    The published headline is measured partly on rows the model was fitted to.
    Removing them can only remove an advantage, so the held-out median must not
    come out BETTER. If it ever does, the taint set is being computed wrongly
    (most likely `implicated` has gone vacuous) rather than the model having
    improved.
    """
    lines = headline_effect(citations)
    numbers = [float(line.split("median=")[1].rstrip("%"))
               for line in lines if "median=" in line]
    assert len(numbers) == 2, lines
    published, held_out = numbers
    assert held_out >= published - 1e-9, (
        "held-out median (%.1f%%) beat the published one (%.1f%%); the "
        "exclusion set is wrong" % (held_out, published))


def test_size_exponents_are_the_dominant_family(citations):
    """WHICH constants do this, because that names the next piece of work.

    Nine of the implicated citations are `abrasive_size_exponent` on five
    packs: that single constant family is the corpus's main self-grading
    surface, and it is also the one the repository already knows is not
    transferable across abrasives (sic_ceria_h2o2's own note). The pH-response
    quartets are the second family. Asserting the SHAPE of the finding stops a
    future session reading the raw count as a uniform problem.
    """
    families = [c.constant for c in citations if c.implicated]
    size = [f for f in families if "abrasive_size" in f]
    assert len(size) >= len(families) / 3, (
        "abrasive_size_exponent was the dominant self-graded family; if that "
        "has changed, the next target has changed too: %s" % sorted(set(families)))
