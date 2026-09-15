"""P1 unit tests — Preston's defining properties must hold exactly."""
import numpy as np
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Recipe, Slurry, Tool, Wafer
from cmp_sim.core.units import psi_to_pa
from cmp_sim.models import preston


PAD = dict(wafer_radius_m=0.150, center_offset_m=0.200)


def _mrr(P_psi=3.0, rpm=60.0, kp=1e-13, **kw):
    rs, mrr, _ = preston.mrr_radial_nm_per_min(
        PAD["wafer_radius_m"], PAD["center_offset_m"], rpm, rpm, kp,
        psi_to_pa(P_psi), n_radial=41, **kw)
    return rs, mrr


def test_mrr_is_linear_in_pressure():
    _, a = _mrr(P_psi=2.0)
    _, b = _mrr(P_psi=4.0)
    assert np.allclose(b, 2.0 * a, rtol=1e-12)


def test_mrr_is_linear_in_velocity():
    _, a = _mrr(rpm=30.0)
    _, b = _mrr(rpm=60.0)
    assert np.allclose(b, 2.0 * a, rtol=1e-12)


def test_mrr_is_linear_in_kp():
    _, a = _mrr(kp=1e-13)
    _, b = _mrr(kp=3e-13)
    assert np.allclose(b, 3.0 * a, rtol=1e-12)


def test_equal_head_and_platen_rpm_gives_a_flat_profile():
    """Rs = 1 makes the relative speed uniform over the wafer, so uniform
    pressure must give zero non-uniformity — the structural statement that
    WIWNU originates in the pressure field, not in kinematics."""
    rs, mrr = _mrr(rpm=60.0)
    assert np.std(mrr) / np.mean(mrr) < 1e-9
    assert preston.uniformity(rs, mrr)["sigma_pct"] < 1e-6


def test_zone_pressure_raises_edge_rate_and_nonuniformity():
    rs, flat = _mrr()
    _, zoned = preston.mrr_radial_nm_per_min(
        PAD["wafer_radius_m"], PAD["center_offset_m"], 60.0, 60.0, 1e-13,
        psi_to_pa(3.0), n_radial=41,
        zone_pressures_pa=[psi_to_pa(2.5), psi_to_pa(3.0), psi_to_pa(4.0)],
        zone_edges_norm=[0.0, 0.5, 0.8, 1.0])[:2]
    assert zoned[-1] > zoned[0]
    assert preston.uniformity(rs, zoned)["sigma_pct"] > preston.uniformity(rs, flat)["sigma_pct"]


def test_zone_edges_length_is_validated():
    with pytest.raises(ValueError):
        preston.mrr_radial_nm_per_min(
            0.15, 0.2, 60.0, 60.0, 1e-13, psi_to_pa(3.0),
            zone_pressures_pa=[1e4, 2e4], zone_edges_norm=[0.0, 0.3, 0.6, 1.0])


def test_velocity_scales_with_center_offset():
    """V ~ omega_p * r_cc dominates, so doubling r_cc must raise MRR."""
    rs1, m1, _ = preston.mrr_radial_nm_per_min(0.15, 0.20, 60, 60, 1e-13, psi_to_pa(3.0), n_radial=21)
    rs2, m2, _ = preston.mrr_radial_nm_per_min(0.15, 0.40, 60, 60, 1e-13, psi_to_pa(3.0), n_radial=21)
    assert np.mean(m2) > 1.8 * np.mean(m1)


# ── solver-level contract ────────────────────────────────────────────
def test_simulate_returns_a_complete_result():
    r = simulate(Recipe(wafer=Wafer(film="oxide", initial_thickness_nm=1000.0),
                        slurry=Slurry(pack="oxide_silica"),
                        tool=Tool(pressure_psi=3.0, rpm_platen=66.31, rpm_head=66.31, time_s=60)))
    s = r.summary()
    assert s["removal_rate_A_per_min"] > 0
    assert s["film"] == "oxide"
    assert len(s["radial_profile"]["radius_mm"]) == 81
    assert r.remaining_nm is not None
    assert r.provenance["kp_m_per_pa"]["source"]


def test_simulate_removed_thickness_matches_rate_times_time():
    rec = Recipe(slurry=Slurry(pack="oxide_silica"),
                 tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=120))
    r = simulate(rec)
    assert np.allclose(r.removed_nm, r.mrr_nm_per_min * 2.0, rtol=1e-12)


def test_every_film_in_the_map_resolves_to_a_pack_or_says_why():
    from cmp_sim.core.solver import FILM_PACK
    from cmp_sim.core.params import available_packs
    have = set(available_packs())
    missing = sorted(p for p in FILM_PACK.values() if p not in have)
    # P1 ships the inherited packs; poly-Si / Si / SnAg packs are later phases.
    assert missing == ["poly_si_alkaline", "si_substrate_alkaline", "snag_solder"], missing
