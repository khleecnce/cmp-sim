"""Every pack key the engine reads must exist, or be a declared exception.

WHY THIS TEST EXISTS
--------------------
Four wiring bugs found in the 26th and 27th runs share one shape: the key name
the engine reads does not match the key name the packs declare, and NOTHING
FAILS. ``p_or(key, default)`` returns the default, the layer quietly takes its
"no data" branch, and the run still produces a plausible number. A sourced
constant sits unused in twelve pack files while the model uses a fallback.

* ``scratch_threshold_nm`` -- declared by all twelve packs, shadowed by a
  hardcoded module constant holding the SAME value, so no prediction was
  wrong and no test could notice.
* ``pad_glazing_rate`` / ``pad_conditioning_rate`` -- read by the solver,
  declared by no pack (they are ``stab_glaze_rate_per_min`` /
  ``stab_cond_recovery_rate_per_min``), so the steady-state pad balance had
  never executed once.
* ``oxidizer_mechanical_floor`` -- read by the peaked oxidiser branch, while
  the measured value lives under ``oxidizer_mech_floor``.

None of these could be caught by a unit test, because unit tests pass the
numbers in DIRECTLY and so never exercise the lookup. This test asks the one
static question that catches all four: does every key the engine asks for
exist somewhere in the packs?

HOW TO FIX A FAILURE
--------------------
If this test fails on a new key, one of two things is true:

1. It is a misspelling / renamed key. Fix the engine to read the name the
   packs use (or add a fallback, as the three fixes above did). This is the
   common case and the reason the test exists.
2. It is genuinely not a pack key -- a caller-supplied override, or a declared
   gap no pack has data for. Add it to ``KNOWN_NON_PACK_KEYS`` below WITH a
   one-line reason. The allow-list is deliberately annotated: an unexplained
   entry is how this class of bug gets re-admitted.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from tools.pack_key_wiring_audit import _asked_keys, _declared_keys  # noqa: E402

#: Keys the engine reads that legitimately do NOT come from a pack.
#: Every entry states why, so the list cannot quietly absorb a real bug.
KNOWN_NON_PACK_KEYS = {
    "abrasive_d50_nm":
        "caller input: the size of the abrasive in THIS recipe, not a pack "
        "property. Packs carry abrasive_size_nm as their reference.",
    "aggregate_ratio":
        "declared gap: the agglomeration path no pack has measured. The "
        "defect proxy states it is uninvestigated rather than assuming zero.",
    "die_size_m":
        "caller input: layout geometry, a property of the customer's product.",
    "inhibitor_ppm":
        "caller input: an alternative unit for the recipe's inhibitor "
        "concentration; packs declare inhibitor_mM.",
    "overpolish_time_s":
        "caller input: a process choice, not a material constant.",
    "pad_wafer_gap_m":
        "caller input / solved quantity, not declared by any pack.",
    "pressure_exponent":
        "owner fit: set only when the user fits their own exponents to their "
        "own data. Absent means Preston's 1.0, which is the default.",
    "velocity_exponent":
        "owner fit: same as pressure_exponent.",
    "velocity_ref_m_s":
        "owner fit: the reference velocity of the user's OWN fitted exponent. "
        "Defaults to this run's mean velocity, which makes the multiplier 1.0 "
        "at the fitting conditions. Deliberately not the packs' "
        "relative_velocity_ref_mps, which anchors a different quantity.",
    "starvation_length_m":
        "declared gap: no pack has measured a starvation length.",
    # Fixed in the 27th run; kept readable as fallbacks for external packs
    # that still use the long names.
    "oxidizer_mechanical_floor":
        "legacy long name, now falling back to the packs' "
        "oxidizer_mech_floor. Kept so an external pack using it still works.",
    "pad_glazing_rate":
        "legacy name, now falling back to stab_glaze_rate_per_min.",
    "pad_conditioning_rate":
        "legacy name, now falling back to stab_cond_recovery_rate_per_min.",
}


def test_every_key_the_engine_reads_exists_in_a_pack_or_is_declared():
    asked = _asked_keys(os.path.join(HERE, "cmp_sim"))
    declared, _valued = _declared_keys()

    orphans = {k: v for k, v in asked.items()
               if k not in declared and k not in KNOWN_NON_PACK_KEYS}

    if orphans:
        import difflib
        lines = []
        for key, where in sorted(orphans.items()):
            near = difflib.get_close_matches(key, sorted(declared), n=3,
                                             cutoff=0.6)
            hint = f"  packs declare similar: {', '.join(near)}" if near else \
                "  no similar pack key — likely a genuine declared gap"
            lines.append(f"\n  {key}\n    read at {where[0]}\n  {hint}")
        pytest.fail(
            "the engine reads pack key(s) that NO pack declares. Either the "
            "name is wrong (the packs carry the value under another name — "
            "see the suggestions), or it is not a pack key at all, in which "
            "case add it to KNOWN_NON_PACK_KEYS with a reason:"
            + "".join(lines))


def test_the_allow_list_does_not_outlive_its_keys():
    """An allow-list entry for a key nobody reads any more is stale.

    Left alone it would silently permit a future bug under the same name, so
    the list is required to track the code rather than accumulate.
    """
    asked = set(_asked_keys(os.path.join(HERE, "cmp_sim")))
    stale = sorted(set(KNOWN_NON_PACK_KEYS) - asked)
    assert not stale, (
        f"KNOWN_NON_PACK_KEYS lists keys the engine no longer reads: {stale}. "
        "Remove them so the allow-list keeps meaning what it says.")


def test_every_allow_list_entry_states_a_reason():
    vague = sorted(k for k, why in KNOWN_NON_PACK_KEYS.items()
                   if len(str(why).strip()) < 25)
    assert not vague, (
        f"these allow-list entries have no real justification: {vague}. "
        "An unexplained exemption is how a wiring bug gets re-admitted.")
