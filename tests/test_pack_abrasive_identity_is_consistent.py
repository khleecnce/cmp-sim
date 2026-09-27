"""A pack must not name two different abrasives in two different keys.

WHAT THIS PINS
--------------
``slurry/abrasive_effects.resolve`` decides whether the abrasive in a recipe is
the one the pack's ``kp_m_per_pa`` was calibrated with. On a mismatch it does
something drastic and correct: it WITHDRAWS the pack's abrasive-scoped
exponents (they were fitted for a different material and the measured exponents
do not even share a sign across materials) and refuses to anchor the absolute
scale.

That decision is only as good as the identity it compares against. A pack
declares its abrasive TWICE:

  ``abrasive``            what the slurry contains
  ``reference_abrasive``  what the Kp was back-calculated from

For a pack whose Kp came from its own slurry -- which is every pack here, by
construction of how Kp is anchored -- those two keys name the SAME physical
material. If they disagree, the pack is lying to the swap detector about
itself, and running the pack's own slurry through it is scored as a swap.

THE BUG THIS WAS WRITTEN FOR
----------------------------
``sic_alumina_kmno4`` is an alumina pack: ``abrasive: alumina``, with two
citations, an alpha-alumina density, and a Kp anchored on Wang 2021 /
US20220315802A1, both alumina. It inherited ``reference_abrasive: ceria`` from
its ceria PARENT (``sic_ceria_h2o2``) and never overrode it.

Nothing failed, because nothing compared the two keys -- and the detector could
not fire either, since no validation dataset declared an abrasive at all, so
``kind`` was ``None`` in all 49 scored runs and ``matches_reference`` defaulted
to ``True`` everywhere. The defect was only visible once the abrasive WAS
declared: doing so on the pack's own dataset (entegris2022, an alumina series)
was scored as alumina-into-a-ceria-pack, withdrew that pack's MEASURED loading
exponent (-0.406, Entegris Table 1, n=5) in favour of the derived +1/3, and
took the shape error from 14.1% to 101.5%.

This is the same inheritance-accident class already recorded twice in this same
pack family (``sti_ceria`` inheriting silica's ``C_half``; ``sic_ceria_h2o2``
inheriting the oxide pH optimum). Fixing the instance is not enough -- these
recur because a child that differs from its parent in MATERIAL silently keeps
every key that names the material. So this test is written over ALL packs and
re-derives its own subject list at test time: a new pack, or a new child of a
ceria pack, is checked with no edit here.
"""
from __future__ import annotations

import pytest

from cmp_sim.core.params import available_packs, load_pack
from cmp_sim.slurry.abrasive_effects import canonical_kind


def _pack_names():
    return sorted(n for n in available_packs() if n != "base")


def _declared(pack_name):
    """(abrasive, reference_abrasive) as canonical DB keys, or None."""
    pack = load_pack(pack_name)
    out = []
    for key in ("abrasive", "reference_abrasive"):
        param = pack.params.get(key)
        value = getattr(param, "value", None)
        out.append(canonical_kind(value) if value else None)
    return tuple(out)


@pytest.mark.parametrize("pack_name", _pack_names())
def test_a_pack_names_the_same_abrasive_in_both_of_its_identity_keys(pack_name):
    """``abrasive`` and ``reference_abrasive`` must resolve to one material.

    Either key may be absent -- a pack that declares neither simply cannot
    detect a swap, which is reported at run time as a warning rather than
    guessed at. What is forbidden is declaring BOTH and having them disagree,
    because then the swap detector compares the recipe against a material this
    pack does not contain.
    """
    abrasive, reference = _declared(pack_name)
    if abrasive is None or reference is None:
        pytest.skip(f"{pack_name} declares only one of the two identity keys")
    assert abrasive == reference, (
        f"pack '{pack_name}' declares abrasive='{abrasive}' but "
        f"reference_abrasive='{reference}'. These name the same physical "
        f"material by definition (the Kp was back-calculated from a "
        f"measurement made with the pack's own slurry), so a disagreement "
        f"means the abrasive-swap detector will score this pack's OWN "
        f"abrasive as a swap and withdraw its measured exponents. If this "
        f"pack inherits from a parent with a different abrasive, it must "
        f"re-declare reference_abrasive, citing the same source as its "
        f"`abrasive` key")


def test_at_least_one_pack_actually_exercises_the_comparison():
    """The parametrised test must not pass by skipping everything.

    A check whose every case skips is indistinguishable from a check that was
    deleted. This repository has been bitten by exactly that shape before (a
    constant that was unreachable at every query, and therefore unfalsifiable),
    so the guard is asserted rather than assumed.
    """
    compared = [n for n in _pack_names()
                if all(v is not None for v in _declared(n))]
    assert len(compared) >= 5, (
        f"only {len(compared)} pack(s) declare both identity keys, so this "
        f"test is nearly vacuous: {compared}")


def test_the_alumina_sic_pack_no_longer_inherits_its_parents_ceria():
    """The specific regression, named, so the fix cannot be quietly undone.

    Kept alongside the general test because the general one would also pass if
    somebody 'fixed' the disagreement by deleting the key rather than by
    correcting it -- which would restore the undetectable state, not the right
    answer.
    """
    abrasive, reference = _declared("sic_alumina_kmno4")
    assert abrasive == "alumina", (
        "sic_alumina_kmno4 must declare alumina: its density, its two "
        "citations and its Kp anchor are all alpha-alumina")
    assert reference == "alumina", (
        "sic_alumina_kmno4 must OVERRIDE the ceria reference_abrasive it "
        "inherits from sic_ceria_h2o2. Deleting the key instead would make "
        "swaps undetectable for this pack, which is not the fix")


def test_the_parent_ceria_pack_is_untouched():
    """The fix must be scoped to the child, not applied to the family.

    ``sic_ceria_h2o2`` really is a ceria pack; its Kp is anchored on a ceria
    measurement (Wang et al. ACS SI Table S3 point S3-27). Overriding the child
    must not have been done by editing the parent, which would have inverted
    the bug rather than fixed it.
    """
    abrasive, reference = _declared("sic_ceria_h2o2")
    assert abrasive == "ceria" and reference == "ceria", (
        f"sic_ceria_h2o2 is a ceria pack (Kp anchored on a ceria polish) but "
        f"reads abrasive={abrasive}, reference_abrasive={reference}")
