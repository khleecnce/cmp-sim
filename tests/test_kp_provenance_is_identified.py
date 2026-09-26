"""Every absolute-scale failure must be ADJUDICATED, and the ruling must hold up.

§22 proved the >=3x absolute-rate failures are not one mis-anchored constant:
five packs disagree with themselves by 8-222x, so no value of ``kp_m_per_pa``
satisfies both ends. It named the follow-up, and ``tools/kp_provenance_table``
is it: for each failing block, WHAT is the pack silently conflating?

The danger in that follow-up is obvious and these tests exist to contain it.
"The pack does not cover this block" is the most convenient sentence in the
project -- it excuses any miss at zero cost. So it is only allowed here under
four constraints, one per failure mode:

  1. EVERY failure must be adjudicated. A new >=3x block cannot appear and go
     unnamed; the table fails rather than quietly shrinking.
  2. Each ruling must CITE its dataset file, and the citation is checked
     against the file at runtime -- so a ruling cannot outlive the text it
     rests on.
  3. The rulings must not be post-hoc. Two independent checks:
     the prose must not partition the corpus into failures and successes
     (contingency), and a claim of identification must not be reachable by
     looking only at the miss.
  4. Identification must NOT become a licence to refit. A block whose only
     possible anchor is itself is marked not-splittable, and the suite asserts
     that this run split nothing.

The fifth test is the positive result, and the only one that could have come
out otherwise: ``sti_ceria``'s own excluded composite Kp predicts the scale of
the two blocks it excluded, to within the spread of the two.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools import kp_provenance_table as prov

BLOCKS = prov.comparable_blocks()
FAILURES = prov.failures(BLOCKS)
DATASETS = Path(prov.__file__).parent.parent / "cmp_sim/data/validation/datasets"


def test_every_absolute_scale_failure_is_adjudicated():
    """No >=3x block may sit in the corpus without a named cause.

    This is the test that makes the table a standing obligation rather than a
    snapshot: add a dataset that misses by 3x and this fails until somebody
    writes down what its pack is conflating.
    """
    unruled = [b.dataset for b in FAILURES if b.dataset not in prov.RULINGS]
    assert not unruled, (
        "these blocks miss the absolute rate by >=3x with no ruling: "
        f"{unruled}. Name what the pack conflates, or record it UNIDENTIFIED "
        "-- do not leave it silent.")


def test_no_ruling_survives_the_text_it_cites():
    """Each ruling quotes its dataset file, and the quote must still be there.

    A ruling is evidence only while the sentence it rests on exists. Checking
    the quote at runtime means a later edit that deletes the scope statement
    breaks the ruling instead of leaving a citation pointing at nothing.
    """
    for name, ruling in prov.RULINGS.items():
        path = DATASETS / f"{name}.yaml"
        assert path.exists(), f"{name} has a ruling but no dataset file"
        raw = path.read_text(encoding="utf-8")
        assert ruling.quote in raw, (
            f"{name}: the ruling cites {ruling.quote!r}, which is no longer in "
            "the dataset file. Re-read the file and re-adjudicate.")


def test_the_scope_prose_is_not_a_label_for_bad_numbers():
    """Anti-selection. If the prose marked exactly the failures, it would be an
    excuse written after the fact, and the whole table would be circular.

    Measured the other way: blocks carrying 'placeholder / rank-only / absolute
    incomparable' prose fail at roughly the same rate as blocks without it, and
    the two median miss factors are close. The prose says which QUESTION the
    block can answer, not how well it scored.
    """
    sel = prov.anti_selection(BLOCKS)
    assert sel["flagged"] >= 10 and sel["clean"] >= 10, (
        "too few blocks on one side to make the contingency meaningful: "
        f"{sel}")
    # The decisive fact: a majority of prose-carrying blocks are NOT failures.
    assert sel["flagged_failing"] < sel["flagged"] / 2, (
        "more than half the prose-flagged blocks fail, so the prose cannot be "
        f"distinguished from a post-hoc excuse: {sel}")
    # ...and failures exist among blocks with no prose at all.
    assert sel["clean_failing"] >= 1, (
        "every failure carries the prose, which is what a post-hoc excuse "
        f"would look like: {sel}")


def test_identifying_a_cause_did_not_license_a_refit():
    """Naming the conflated variable must not become permission to move a Kp.

    Every ruling here is marked not-splittable, and each says why: the anchor a
    split would need does not exist independently of the blocks the split would
    then be scored on. That is the 13th-run rule (a dataset may not testify for
    the constant fitted on it) applied to absolute scale.
    """
    splittable = [n for n, r in prov.RULINGS.items() if r.splittable]
    assert not splittable, (
        "a ruling claims a split is available: "
        f"{splittable}. Before splitting, show the INDEPENDENT anchor -- a "
        "dataset that is not one of the blocks the new pack would be scored "
        "on. Without it the split marks its own homework.")


def test_sti_ceria_predicts_the_scale_of_the_blocks_it_excluded():
    """The one QUANTITATIVE identification, and it could have failed.

    When ``sti_ceria``'s Kp was re-derived from four bare-ceria datasets, the
    two ceria-coated-silica composite blocks were deliberately excluded as a
    different abrasive, and the value they imply (~2.3e-14 against the pack's
    1.09e-13) was written into the note. That exclusion is a prediction with no
    free parameter: scored with the bare-ceria Kp, those two blocks must
    under-predict by the ratio of the two numbers.

    Both figures were in the pack before this run; the prediction is a
    division; and the two observations bracket it. So these two failures are
    not model error -- they are the pack's own statement, measured.
    """
    comp = prov.composite_prediction()
    predicted = comp["predicted_scale"]
    observed = {k: v for k, v in comp.items() if k.startswith("us2019")}
    assert len(observed) == 2, observed
    lo, hi = min(observed.values()), max(observed.values())
    assert lo <= predicted <= hi, (
        f"the composite Kp predicts {predicted:.3f}x but the two blocks "
        f"measure {observed} -- they no longer bracket it, so the "
        "identification must be re-examined rather than restated.")
    # And the agreement must be tight enough to be a claim: both within 25%.
    for name, value in observed.items():
        assert abs(value / predicted - 1.0) < 0.25, (
            f"{name} is {value:.3f}x against a predicted {predicted:.3f}x; "
            "that is no longer an identification, only a coincidence of sign.")


def test_the_composite_prediction_is_read_from_the_pack_not_retyped():
    """Guard against the prediction silently becoming a hardcoded pair.

    Both numbers must come out of ``sti_ceria.yaml`` at runtime. If a later
    edit removes the composite figure from the note, this fails loudly instead
    of leaving the test asserting a constant the pack no longer states.
    """
    source = Path(prov.__file__).read_text(encoding="utf-8")
    body = source.split("def composite_prediction")[1].split("\ndef ")[0]
    assert "load_pack" in body, "the bare Kp must be read from the pack"
    # Only EXECUTABLE lines may not carry a Kp: the docstring quotes both
    # values on purpose, because a reader has to see the prediction being made
    # to judge it. Stripping the docstring is what makes this test about
    # behaviour instead of about prose.
    code = body.split('"""')[2] if body.count('"""') >= 2 else body
    assert not re.search(r"1\.09e-13|2\.3e-14", code), (
        "composite_prediction() hardcodes a Kp value; read both from the pack "
        "so the test tracks the pack rather than a memory of it.")


def test_the_unidentified_failure_stays_unidentified():
    """One of the eleven is genuinely unexplained, and must stay labelled so.

    ``us6918821b2`` misses by 12.7x with a patent that states no slurry
    composition, so there is nothing to compare against the Kp anchor. It would
    be easy to fold it in with the nine identified blocks and report "all
    causes known"; the count is asserted instead.
    """
    unidentified = [n for n, r in prov.RULINGS.items() if not r.identified]
    assert unidentified == ["us6918821b2_cu_ic1000_pressure_speed_2x3"], (
        "the set of UNIDENTIFIED failures changed: " f"{unidentified}. "
        "If a cause was found, cite it; if one was lost, say so.")


@pytest.mark.parametrize("name", sorted(prov.RULINGS))
def test_each_ruling_names_a_variable_not_a_verdict(name):
    """A ruling must say WHAT differs, not merely that something does.

    'Out of scope' with no named variable is the failure mode this whole file
    exists to prevent, so the text is required to carry a concrete noun.
    """
    ruling = prov.RULINGS[name]
    concrete = ("abrasive", "pH", "ph ", "pressure", "film", "inhibitor",
                "chemistry", "tool", "loading", "anchor", "composition",
                "platinum", "silica", "species")
    assert any(word in ruling.conflated for word in concrete), (
        f"{name}: {ruling.conflated!r} names no concrete variable")
    assert len(ruling.why) > 80, f"{name}: the reasoning is too thin to review"
