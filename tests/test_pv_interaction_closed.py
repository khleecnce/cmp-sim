"""The P-V interaction axis is CLOSED: both named mechanisms are rejected.

STATUS.md's NEXT (after the 9th run) required that the two candidate
mechanisms for the measured P-V interaction be checked for SIGN against the
four measured bodies, from parameters already in the repository, before any
pack is touched. ``tools/pv_interaction_closure.py`` did that and both failed
with zero fitted constants:

  (A) contact-area evolution -- structurally cannot move b_V (A_r is a
      quasi-static response to the NORMAL load and contains no V at all), and
      in any case A_r is exactly proportional to load on every pack's own
      reference pad at every measured pressure (GW exponential-summit result,
      summit saturation only 1-5%).
  (B) pad-asperity flash heating as a CROSS term -- the Arrhenius derivation
      gives b_V = 1 + (Ea/R)*c*P*V/(T0+c*P*V)**2, which is > 1 for every
      positive (Ea, c). Two of the four bodies measure b_V BELOW 1 at every
      pressure, so no parameter choice can reach them.

These tests pin the closure so a future run cannot quietly re-open it with a
fitted constant, and pin the honesty caveats that make the closure readable:
the axis's own price, and the fact that the oracle's median shift is far larger
than the share of measured points the axis can actually reach.
"""
from __future__ import annotations

import math

import pytest

from cmp_sim.core.params import available_packs, load_pack
from tools import pv_interaction_closure as closure


def test_flash_heating_cross_term_cannot_produce_sub_linear_velocity():
    """(B) The derivation forbids b_V < 1, and two bodies measure b_V < 1.

    This is the whole rejection, and it costs no constants: the sign of the
    Arrhenius cross term depends only on Ea > 0 and c > 0, never on their
    values. The scan is kept wide (10-200 kJ/mol x six decades of heating
    coefficient) so that "we just did not try hard enough" is not available.
    """
    assert closure.flash_heating_is_capable_of_sub_linear() is False

    measured_below_one = [
        (label, levels) for label, _pack, levels, _v in closure.MEASURED_BODIES
        if all(b < 1.0 for _p, b in levels)
    ]
    assert len(measured_below_one) >= 2, (
        "the rejection rests on bodies measuring b_V < 1; if the measured "
        "table no longer contains at least two such bodies, re-derive the "
        f"verdict instead of trusting it (found {measured_below_one})")


def test_flash_heating_is_monotone_up_in_pressure_which_two_bodies_contradict():
    """(B), sharper: the cross term's PRESSURE trend is also fixed in sign.

    db_V/dP > 0 while the temperature rise is below T0, so a body whose b_V
    FALLS with pressure contradicts the mechanism independently of magnitude.
    mariscal2020 falls monotonically (+1.105 -> +0.857 -> +0.625).
    """
    bv = [closure.flash_heating_bv(psi, 1.0, 80e3, 1e-6)
          for psi in (1.0, 2.0, 4.0, 6.0)]
    assert all(b > a for a, b in zip(bv, bv[1:])), (
        f"the derivation must rise with pressure, got {bv}")

    falling = [label for label, _pack, levels, _v in closure.MEASURED_BODIES
               if len(levels) >= 3
               and all(b < a for (_p1, a), (_p2, b) in zip(levels, levels[1:]))]
    assert falling, ("no body falls with pressure any more -- the independent "
                     "half of the (B) rejection no longer holds")


def test_contact_area_is_exactly_linear_in_load_so_it_has_no_sub_linearity():
    """(A2) Measured on each pack's OWN reference pad at its OWN pressures."""
    slopes = closure.contact_area_exponents()
    assert slopes, "no pack exposed a reference pad state -- cannot conclude"
    worst = max(abs(s.dln_ar_dln_p - 1.0) for s in slopes)
    assert worst < closure.SUBLINEARITY_BAR, (
        f"A_r(P) is now sub-linear by {worst:.4f}, past the pre-registered "
        f"{closure.SUBLINEARITY_BAR} bar. The (A) rejection was argued on "
        "strict linearity and must be re-derived.")
    # Deep inside the linear regime is WHY it is linear, so pin that too:
    # past ~50% saturation GW's exponential-tail result fails and A_r would bend.
    assert max(s.saturation for s in slopes) < 0.10, (
        "summit saturation has risen; the linearity above is then a claim "
        "about a regime the pads are no longer in")


def test_the_A_rejection_does_not_rest_on_three_independent_pads():
    """Honesty guard: the three packs resolve to ONE inherited base pad.

    A reader seeing three pack names in the report could take the identical
    1.0000 as three independent confirmations. It is one pad. The structural
    argument (A1) is what makes the rejection general; this test exists so the
    weaker half cannot be quoted as the stronger one.
    """
    keys = ("pad_E_star_pa", "pad_asperity_radius_m",
            "pad_asperity_density_m2", "pad_height_beta_inv_m")
    packs = {p for _l, p, _lv, _v in closure.MEASURED_BODIES}
    states = {p: tuple(load_pack(p).get(k) for k in keys) for p in packs}
    assert len(set(states.values())) == 1, (
        "the packs now describe DIFFERENT reference pads, so the report's "
        "identical slopes would no longer be one measurement repeated: "
        f"{states}")


def test_no_pack_declares_a_pressure_velocity_coupling_constant():
    """The closure means no pack may carry a fitted P-V handle.

    Both mechanisms were rejected without fitting, so any such constant
    arriving later is a fitted function replacing a fitted constant -- exactly
    what the 9th run's measurement forbids. Fails LOUDLY rather than letting it
    in quietly.
    """
    forbidden = ("velocity_exponent", "pv_exponent", "pv_coupling",
                 "velocity_pressure", "b_v", "flash_heating",
                 "contact_temperature_coefficient")
    offenders = []
    for name in available_packs():
        pack = load_pack(name)
        for key in pack.params:
            low = key.lower()
            if any(f in low for f in forbidden):
                offenders.append(f"{name}:{key}")
    assert not offenders, (
        "a P-V coupling constant appeared in a pack after the axis was closed "
        f"by measurement: {offenders}. Re-run tools/pv_interaction_closure.py "
        "and justify it, or remove it.")


def test_the_axis_price_is_an_oracle_and_its_point_share_is_small():
    """(C) What the axis costs, stated as an upper bound and not as a promise.

    The oracle gives every (pressure, chemistry) group its own MEASURED b_V,
    fitted on the very rows being scored, so it is unreachable by construction.
    The assertion that matters is the SHARE OF POINTS it touches: the median
    can move by re-ranking datasets, the point share cannot.
    """
    scores = closure.oracle_scores()
    assert scores, "the oracle scored nothing"
    movers = [s for s in scores if abs(s.gain_pp) > 0.05]
    total = sum(s.n_points for s in scores)
    moved = sum(s.n_points for s in movers)
    share = moved / total

    assert share < 0.15, (
        f"the P-V axis now reaches {100 * share:.1f}% of measured points "
        f"({moved}/{total}). Above ~15% it is no longer a thin axis and the "
        "closure should be revisited with the new data.")
    # And the oracle must genuinely help where it applies, or part (C) is
    # measuring nothing and the 'price' claim is empty.
    assert all(s.gain_pp > 0 for s in movers), (
        f"a dataset got WORSE under its own measured exponent: {movers}")


def test_the_oracle_median_shift_overstates_the_axis():
    """The reason the point share is asserted above and the median is not.

    Recorded as a test because it is the trap: 3 datasets of 49 move, yet the
    corpus median moves ~2 pp, which reads like a corpus-wide gain. It is a
    re-ranking of the median dataset.
    """
    scores = closure.oracle_scores()
    movers = [s for s in scores if abs(s.gain_pp) > 0.05]
    share = sum(s.n_points for s in movers) / sum(s.n_points for s in scores)

    import statistics
    base = statistics.median(s.baseline_pct for s in scores)
    orc = statistics.median(s.oracle_pct for s in scores)
    median_gain_frac = (base - orc) / base

    assert median_gain_frac > share, (
        "the median gain no longer exceeds the point share, so the warning "
        "this test pins would be misleading; re-read the report")


def test_the_report_states_both_rejections_and_the_honesty_notes():
    text = closure.report()
    for needle in ("(A) contact-area evolution", "(B) flash-heating cross term",
                   "MEASURED POINTS the axis can reach",
                   "not reused here",           # the 8th-run distinction
                   "HONESTY"):
        assert needle in text, f"the report no longer states: {needle}"
    assert "FAILS" in text, "the report no longer records a rejection"


def test_the_measured_bodies_table_matches_the_earlier_probe():
    """The four bodies are the 9th run's measurements, not new numbers.

    Guards against the table drifting into convenient values: the two Cu
    bodies must still change sign, and Sorooshian must still rise.
    """
    by_label = {label: levels for label, _p, levels, _v
                in closure.MEASURED_BODIES}
    cu = [levels for label, levels in by_label.items() if "Cu" in label]
    assert len(cu) == 2
    for levels in cu:
        signs = {math.copysign(1.0, b) for _p, b in levels}
        assert signs == {-1.0, 1.0}, (
            f"a Cu body no longer changes sign: {levels}")
    soro = next(v for k, v in by_label.items() if "Sorooshian" in k)
    assert all(b > a for (_1, a), (_2, b) in zip(soro, soro[1:]))


@pytest.mark.parametrize("psi,v", [(1.0, 0.3), (4.0, 1.0), (6.0, 2.0)])
def test_flash_heating_formula_reduces_to_preston_without_heating(psi, v):
    """c -> 0 must give exactly b_V = 1, or the derivation is mis-coded."""
    assert closure.flash_heating_bv(psi, v, 80e3, 0.0) == pytest.approx(1.0)
