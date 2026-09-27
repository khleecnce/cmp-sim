"""The `abrasive_size_exponent` self-grade cannot be repaired by leave-one-out.

docs/limits.md §33. §32 named this constant family the first repair target and
required the repair to be DISTINGUISHED by measurement between two outcomes:
(a) the `used_for_calibration` flag is wrong and the block leaves the corpus,
or (b) the constant is over-claimed and can stand on evidence excluding the
block. Outcome (b) is reachable only for this family, because
``SIZE_EXPONENT_BY_ABRASIVE`` already treats the exponent as a material
property averaged over several sweeps.

Measured (``tools/size_exponent_loo_probe.py``): outcome (b) is refused. Every
implicated block scores WORSE under a leave-one-out exponent, ceria has no
donor at all, and the donor counts collapse to k=1 once the holdout unit is
the PUBLICATION rather than the file.

Every number here is re-measured at test time from the dataset files and the
shipping solver. Nothing is pinned as a literal that a data change could make
stale while still passing.
"""
from __future__ import annotations

import pytest

from tools.size_exponent_loo_probe import (
    IMPLICATED,
    independence_audit,
    loo_exponent,
    measured_groups,
    publication,
    rescore,
)


@pytest.fixture(scope="module")
def groups():
    g = measured_groups()
    assert len(g) >= 6, (
        "the size-sweep reader found %d usable groups; below this the whole "
        "measurement is vacuous and every assertion here passes by default"
        % len(g))
    return g


@pytest.fixture(scope="module")
def rows():
    r = rescore()
    scored = [x for x in r if x["dataset"] in IMPLICATED]
    assert len(scored) >= 5, (
        "only %d of the implicated size blocks could be re-scored; the probe "
        "has stopped reaching the corpus" % len(scored))
    return r


def test_the_holdout_unit_is_the_publication_not_the_file(groups):
    """Bouvet 2002 must not be allowed to donate an exponent to itself.

    Three files (Ti, W, oxide) come from one paper, one slurry set, one tool.
    A file-level holdout counts them as independent evidence for each other;
    a publication-level holdout does not. If the two ever agree for bouvet,
    the distinction has been dropped and the k counts are overstated again.
    """
    bouvet = [g for g in groups if publication(g["dataset"]) == "bouvet2002"]
    assert len(bouvet) >= 2, (
        "this test is about a multi-file publication; bouvet2002 now "
        "contributes %d groups, so the guard has nothing to guard" % len(bouvet))
    target = bouvet[0]
    _, k_pub, _ = loo_exponent(groups, target["dataset"], target["material"],
                               by_publication=True)
    _, k_file, _ = loo_exponent(groups, target["dataset"], target["material"],
                                by_publication=False)
    assert k_file > k_pub, (
        "a file-level holdout must report MORE donors than a publication-level "
        "one for %s (got file=%d, pub=%d); if they are equal the sibling files "
        "are being counted as independent evidence"
        % (target["dataset"], k_file, k_pub))


def test_no_implicated_block_improves_under_leave_one_out(rows):
    """The repair is refused on the data, not on the median.

    A single improving block would reopen outcome (b) for that constant, so
    this is the assertion that must fail when new evidence arrives.
    """
    improved = [r["dataset"] for r in rows
                if r["dataset"] in IMPLICATED
                and r["shape_after"] is not None
                and r["shape_after"] < r["shape_before"] - 0.05]
    assert not improved, (
        "%s now score BETTER with their own size exponent held out, so the "
        "constant is over-claimed for them (outcome b) and the block can "
        "re-enter the scored corpus. Re-measure before editing this test."
        % improved)


def test_ceria_is_unidentifiable_and_the_exit_condition_is_named(rows, groups):
    """son2021 is the only pure-ceria sweep, so its exponent cannot be held out.

    This is outcome (a) with no measurement left to take. The exit condition
    is a second pure-ceria sweep from another publication.
    """
    ceria_pubs = {publication(g["dataset"]) for g in groups
                  if g["material"] == "ceria"}
    assert len(ceria_pubs) == 1, (
        "ceria now has %d publications (%s); son2021's exponent is no longer "
        "unidentifiable and §33's refusal for it must be re-measured"
        % (len(ceria_pubs), sorted(ceria_pubs)))
    son = next(r for r in rows if r["dataset"] == "son2021_oxide_ceria_size_sweep")
    assert son["loo_exponent"] is None and son["k_donors"] == 0, (
        "son2021 reports %d donor publications; the ceria exponent has become "
        "identifiable without the block it is scored on" % son["k_donors"])


def test_the_material_split_survives_collapsing_to_publications(groups):
    """The repair fails; the ATTRIBUTION it rested on does not.

    Asserted so a later session cannot read §33 as withdrawing
    SIZE_EXPONENT_BY_ABRASIVE. Non-independent replicates deflate a
    within-group spread, so correcting for them could have destroyed the
    3.2x ratio; measured, it rises. The bar is the 2x the repository uses
    elsewhere to license a material split.
    """
    audit = independence_audit(groups)
    by_pub = audit["by_publication"]
    assert by_pub["ratio"] >= 2.0, (
        "between/within with publications as the unit is %.2fx, below the 2x "
        "bar; the material attribution in abrasive_effects.py no longer holds "
        "and the size table must be re-examined, not just the repair"
        % by_pub["ratio"])
    assert by_pub["ratio"] >= audit["by_group"]["ratio"] - 0.5, (
        "collapsing replicates was expected to leave the ratio intact or "
        "raise it (%.2fx group -> %.2fx publication); a large fall means the "
        "split was carried by within-paper replicates"
        % (audit["by_group"]["ratio"], by_pub["ratio"]))


def test_expiry_two_independent_donors_would_reopen_the_repair(groups):
    """§33 refuses (b) because every material has k<=1 INDEPENDENT donor.

    A transplanted single foreign number is not a held-out measurement. At two
    independent donor publications for any material, a leave-one-out exponent
    stops being a transplant and the refusal is stale — so this fails then.
    """
    by_material = {}
    for g in groups:
        by_material.setdefault(g["material"], set()).add(publication(g["dataset"]))
    # Donor count for a block of material m is |pubs(m)| - 1 (its own).
    reopened = {m: sorted(p) for m, p in by_material.items() if len(p) - 1 >= 2}
    assert not reopened, (
        "%s now have two or more independent donor publications, so a "
        "leave-one-out exponent is no longer a transplant and the §33 refusal "
        "must be re-measured with tools/size_exponent_loo_probe.py" % reopened)
