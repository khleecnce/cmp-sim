"""The sweep endpoint.

A process engineer asks "what happens as I raise the pressure", so a sweep is
the natural unit of work. The one thing a sweep must not do is draw a confident
trend through a regime change.
"""
import pytest

from cmp_sim.api import SWEEPABLE, run_sweep

BASE = {
    "model": "auto",
    "wafer": {"film": "cu", "n_radial": 11},
    "slurry": {"pack": "cu_h2o2_bta"},
    "pad": {"name": "IC1000", "groove_width_mm": 0.5, "groove_pitch_mm": 2.0,
            "groove_depth_mm": 0.75},
    "disk": {},
    "tool": {"pressure_psi": 1.5, "rpm_platen": 60, "rpm_head": 60,
             "time_s": 60, "flow_ml_min": 150},
}


def test_a_pressure_sweep_is_linear_in_pressure():
    out = run_sweep({"parameter": "pressure_psi", "values": [1, 2, 3, 4],
                     "recipe": BASE})
    rates = [p["removal_rate_A_per_min"] for p in out["points"]]
    assert all(r is not None for r in rates)
    assert rates[3] == pytest.approx(4.0 * rates[0], rel=1e-3)


def test_crossing_a_regime_boundary_is_warned_about():
    """A sweep that genuinely changes lubrication regime must say so.

    This used to sweep 60-200 rpm at 1.5 psi, because that crossed the
    boundary/mixed line at lambda = 1.24. That crossing disappeared when the
    legacy transfer replaced the pad roughness with a sourced value: lambda is
    inversely proportional to sigma, sigma grew 6.7x, and all six conditions of
    that dataset now sit at lambda <= 0.19. See
    tests/test_lubrication_limit.py for why the old constant was never
    physical (it was smoother than a brand-new pad).

    So the sweep is pushed to where a transition genuinely happens now —
    3000 rpm reaches mixed lubrication. The behaviour under test is unchanged:
    when the regime moves, the sweep warns instead of implying one smooth
    trend. Verified that 60-200 rpm no longer crosses anything, so keeping the
    old values would have tested nothing.
    """
    out = run_sweep({"parameter": "rpm_platen", "values": [60, 600, 1500, 3000],
                     "recipe": BASE})
    assert any("regime boundary" in w for w in out["warnings"])
    assert len({p["lubrication"] for p in out["points"]}) > 1


def test_a_sweep_within_one_regime_is_not_warned_about():
    out = run_sweep({"parameter": "pressure_psi", "values": [3, 4, 5],
                     "recipe": BASE})
    assert not any("regime boundary" in w for w in out["warnings"])


def test_the_reason_for_a_regime_warning_is_always_visible():
    """A sweep once warned about a boundary while every displayed column read
    the same, because the transition was in an axis that was not reported.
    Whatever triggers the warning must be present in the points."""
    out = run_sweep({"parameter": "pressure_psi", "values": [1, 2, 3, 4],
                     "recipe": BASE})
    if any("regime boundary" in w for w in out["warnings"]):
        axes = ("lubrication", "load_regime")
        assert any(len({p.get(a) for p in out["points"]}) > 1 for a in axes), (
            "the sweep warned about a regime change that none of the reported "
            "axes shows")


def test_each_point_carries_its_own_regime():
    out = run_sweep({"parameter": "rpm_platen", "values": [60, 200],
                     "recipe": BASE})
    for p in out["points"]:
        assert p["lubrication"]
        assert p["load_regime"]
        assert p["profile"]


def test_one_bad_point_does_not_kill_the_sweep():
    out = run_sweep({"parameter": "pressure_psi", "values": [2, -1, 4],
                     "recipe": BASE})
    assert out["n_ok"] >= 2
    assert any("error" in p for p in out["points"]) or out["n_failed"] == 0


def test_an_unsweepable_parameter_is_rejected_with_the_list():
    with pytest.raises(ValueError) as exc:
        run_sweep({"parameter": "wafer_colour", "values": [1], "recipe": BASE})
    assert "pressure_psi" in str(exc.value)


def test_empty_values_are_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        run_sweep({"parameter": "pressure_psi", "values": [], "recipe": BASE})


def test_a_sweep_is_bounded():
    with pytest.raises(ValueError, match="at most 50"):
        run_sweep({"parameter": "pressure_psi", "values": list(range(60)),
                   "recipe": BASE})


@pytest.mark.parametrize("param", sorted(SWEEPABLE))
def test_every_advertised_parameter_can_actually_be_swept(param):
    """The meta endpoint advertises these; none may be a dead option."""
    values = {"ph": [3.0, 4.0], "temperature_c": [25, 40],
              "pattern_density": [0.3, 0.6], "pad_use_hours": [0.0, 0.1],
              "disk_hours_used": [0, 20], "abrasive_d50_nm": [60, 90],
              "abrasive_conc_wt_pct": [2, 4], "flow_ml_min": [150, 250],
              }.get(param, [2, 3])
    out = run_sweep({"parameter": param, "values": values, "recipe": BASE})
    assert out["n_ok"] == len(values), (
        f"{param}: " + "; ".join(p.get("error", "") for p in out["points"]))
