"""The oxidiser axis is closed: the derived half order is refuted.

STATUS.md's NEXT after the 12th run named ONE remaining open axis
(``oxidizer_wt_pct``, the only axis whose gain survived being tightened from a
per-dataset oracle to a single shared exponent) and pre-registered three tests
for the mechanism that would have made its +0.48 derivable rather than fitted:
a radical chain terminated by radical-radical recombination gives
``[R] ~ [ox]**(1/2)``, hence a HALF order with zero free constants.

``tools/oxidizer_order_probe.py`` ran all three and the axis closed:

  1. ORDER. Of four calibration-free blocks, one is consistent with +1/2 and
     TWO ARE NEGATIVE (-0.33 +- 0.04, -0.16 +- 0.03). No radical-chain order can
     be negative, so this refutes rather than under-determines.
  2. TERMINATION. No dataset has 3+ oxidant levels in both halves of its own
     sweep, so the termination order is UNMEASURABLE here and is not claimed.
  3. ZERO-OXIDANT. Six datasets measure a non-zero rate at [ox] = 0, one of them
     176 % of that block's best oxidised rate. A purely multiplicative term
     predicts zero, so the additive mechanical floor stays.

And the audit that matters most: the +9.5 pp that made the axis look open comes
from exactly two datasets, one of which the pack's oxidiser constant was FITTED
on and the other of which sweeps the oxidant in lockstep (r = +0.53) with
``promoter_M``, an axis the model does not implement at all. Admissible gain:
0.0 pp.

These tests pin the closure and the reasons, so a later run cannot reopen the
axis with a fitted exponent, and cannot quote the inadmissible gain as evidence.
"""
from __future__ import annotations

import functools

import pytest

from tools import oxidizer_order_probe as probe


@functools.lru_cache(maxsize=1)
def _blocks():
    return tuple(probe.blocks())


@functools.lru_cache(maxsize=1)
def _verdict():
    return probe.verdict(list(_blocks()))


@functools.lru_cache(maxsize=1)
def _audit():
    return tuple(probe.census_gain_audit())


def test_the_half_order_does_not_hold_in_every_admissible_block():
    """Test 1, as pre-registered: EVERY block, not the average.

    An average order near +1/2 built from -0.33 and +0.62 would describe no
    system that exists. The pre-registration demanded per-block agreement
    precisely so that cancelling errors could not pass as a law.
    """
    v = _verdict()
    assert v["judged"] >= 3, (
        f"only {v['judged']} calibration-free oxidiser blocks remain; the "
        "closure was measured on 4 and must be re-measured if that changed")
    assert v["half_order_survives"] is False, (
        "the half order now holds in every admissible block. That would be a "
        "real result: re-derive it, add the term WITH its derivation, and "
        "replace limit 15 -- do not relax this test.")


def test_two_admissible_blocks_measure_a_NEGATIVE_oxidiser_order():
    """The refutation is qualitative, not a near miss.

    A radical-chain order is positive for any rate constants: more oxidant
    cannot mean fewer carriers. A negative measured order is therefore a
    different mechanism (over-passivation), and it is what makes the rejection
    final rather than "needs more data".
    """
    negative = [b for b in _blocks()
                if not b.calibrated_on and b.order is not None and b.order < 0
                and b.stderr is not None and b.order + 2 * b.stderr < 0]
    assert len(negative) >= 2, (
        "fewer than two admissible blocks measure a significantly negative "
        f"oxidiser order ({[(b.dataset, b.order) for b in negative]}); limit 15 "
        "rests on this and must be re-argued")


def test_the_census_gain_on_this_axis_is_entirely_inadmissible():
    """The single most important assertion in this file.

    The 12th run's census said this axis kept +9.5 pp under a shared exponent.
    That number is produced by two datasets, and neither can testify: one is the
    pack's own calibration set, the other confounds the oxidant with an inert
    axis. If a future run quotes the +9.5 pp as evidence, this fails.
    """
    audit = _audit()
    assert audit, "no dataset contributes a positive oxidiser gain any more"
    admissible = [r for r in audit if r["admissible"]]
    assert not admissible, (
        "an admissible oxidiser gain has appeared "
        f"({[(r['dataset'], round(r['gain_pp'], 1)) for r in admissible]}). "
        "That is grounds to REOPEN the axis deliberately, with a derivation -- "
        "not grounds to edit this test.")


def test_each_disqualification_names_its_specific_reason():
    """A blanket 'inadmissible' would be unfalsifiable; each must be checkable."""
    for rec in _audit():
        assert rec["used_for_calibration"] or rec["confounds"], (
            f"{rec['dataset']} is marked inadmissible with no stated reason")
        if rec["confounds"]:
            for c in rec["confounds"]:
                assert abs(c["r"]) >= 0.4, (
                    f"{rec['dataset']}: {c['axis']} is cited as a confounder at "
                    f"r={c['r']:+.2f}, below the threshold that justifies the word")


def test_the_promoter_confound_is_an_axis_the_model_does_not_implement():
    """Why the jani2025 gain is not merely correlated but MISATTRIBUTED.

    A co-varying axis the model DOES implement would already absorb its own
    effect, leaving the oxidiser exponent to fit what is left. An INERT axis
    cannot, so its entire effect sits in the residual and any free exponent on a
    co-varying input will claim it.
    """
    confounded = [r for r in _audit()
                  if any(c["inert_in_model"] for c in r["confounds"])]
    assert confounded, (
        "no oxidiser gain is attributed to an inert co-varying axis any more; "
        "if a previously inert axis became live, re-run the audit")


def test_zero_oxidant_rows_forbid_a_multiplicative_oxidiser_factor():
    """Test 3. Independent of the order question, and it constrains the FORM.

    This is the standing reason the chemical model keeps an additive mechanical
    floor instead of a clean product of chemical factors.
    """
    zeros = probe.zero_oxidant_rows()
    assert len(zeros) >= 4, (
        f"only {len(zeros)} datasets measure a rate at zero oxidant; limit 15's "
        "form argument rests on them")
    assert all(at_zero > 0 for _name, at_zero, _best in zeros)
    # At least one block polishes FASTER with no oxidiser at all: the strongest
    # single counter-example to a multiplicative term.
    assert any(at_zero > best for _name, at_zero, best in zeros), (
        "no block still measures a higher rate at zero oxidant than with it; "
        "that datum is quoted in limit 15 and in chemical_rate.py")


def test_the_termination_order_is_reported_as_unmeasurable_not_as_support():
    """Test 2 must stay a refusal.

    The corpus cannot split any sweep into two halves with 3 levels each, so
    the bimolecular-vs-first-order question is open. Claiming it either way
    would be inventing evidence.
    """
    splits = [probe.split_order(b) for b in _blocks()]
    assert all(s is None for s in splits), (
        "a dataset now supports the low-vs-high order split; that test became "
        "runnable and limit 15's 'unmeasurable' clause must be replaced with "
        "its actual result")


def test_the_probe_measures_the_rates_not_the_residual():
    """Guard the method that made the closure possible.

    Fitting the order to measured/predicted would have returned the pack's own
    oxidiser curve back with a correction, which is exactly how the +0.48
    illusion arose. The order here is fitted to the MEASURED rates.
    """
    import inspect
    source = inspect.getsource(probe.blocks)
    assert "_measured" in source
    assert "run_recipe" not in source, (
        "blocks() must not call the simulator: its orders are measurements of "
        "the literature, not of the model")


def test_the_probe_modifies_no_pack():
    import inspect
    source = inspect.getsource(probe)
    for forbidden in ("write_text", "safe_dump", "yaml.dump"):
        assert forbidden not in source, (
            f"tools/oxidizer_order_probe.py contains {forbidden!r}: a "
            "measurement tool must never write a pack")


@pytest.mark.parametrize("pack_key", ["oxidizer_order", "oxidizer_exponent",
                                      "oxidizer_half_order", "radical_order"])
def test_no_pack_declares_an_oxidiser_ORDER_constant(pack_key):
    """The closure, enforced where it could actually be violated."""
    from cmp_sim.core.params import available_packs, load_pack
    for name in available_packs():
        pack = load_pack(name)
        params = getattr(pack, "params", {}) or {}
        assert pack_key not in params, (
            f"pack {name} declares {pack_key}. The oxidiser order was measured "
            "and refuted (limit 15); adding it back requires a derivation and a "
            "rewrite of that limit.")
