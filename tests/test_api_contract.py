"""The HTTP surface is a contract: route names and response keys.

Renaming a route or a response key breaks every caller silently - the web UI
would simply stop displaying a number rather than fail loudly. These tests pin
the names down, and check that a wrong path says what the right ones are.
"""
import json

import pytest

from cmp_sim.api import run_recipe, run_sweep

RECIPE = {
    "model": "auto",
    "wafer": {"film": "oxide"},
    "slurry": {"pack": "oxide_silica"},
    "tool": {"pressure_psi": 3.0, "rpm_platen": 60, "rpm_head": 60, "time_s": 60},
}

#: Keys the web UI reads directly. Renaming one blanks a field on screen.
REQUIRED_KEYS = ("removal_rate_A_per_min", "wiwnu_percent", "warnings")


def test_a_run_returns_the_keys_the_ui_reads():
    result = run_recipe(dict(RECIPE))
    missing = [k for k in REQUIRED_KEYS if k not in result]
    assert not missing, f"the response is missing {missing}"
    assert result["removal_rate_A_per_min"] > 0


def test_the_response_is_json_serialisable():
    """A numpy float or a NaN here returns a 500 at runtime, not at import."""
    text = json.dumps(run_recipe(dict(RECIPE)), allow_nan=False)
    assert len(text) > 100


def test_a_sweep_returns_one_point_per_requested_value():
    result = run_sweep({"parameter": "pressure_psi",
                        "values": [1.0, 2.0, 3.0, 4.0, 5.0],
                        "recipe": dict(RECIPE)})
    assert "points" in result, f"sweep response keys: {list(result)}"
    assert len(result["points"]) == 5
    rates = [p.get("removal_rate_A_per_min") for p in result["points"]]
    assert all(r is not None for r in rates), "a sweep point has no rate"
    assert rates == sorted(rates), "rate should rise with pressure here"


def test_a_sweep_rejects_an_unknown_parameter_by_listing_the_known_ones():
    with pytest.raises(ValueError, match="pressure_psi"):
        run_sweep({"parameter": "not_a_knob", "values": [1, 2],
                   "recipe": dict(RECIPE)})


def test_the_post_routes_are_named_as_documented():
    """README documents /api/simulate and /api/sweep; the handler must agree."""
    import inspect

    from cmp_sim import api

    source = inspect.getsource(api.Handler.do_POST)
    assert '"/api/simulate"' in source
    assert '"/api/sweep"' in source


def test_an_unknown_route_names_the_valid_ones():
    """A bare "no such path" sends the caller reading source code."""
    import inspect

    from cmp_sim import api

    source = inspect.getsource(api.Handler.do_POST)
    assert "valid_post_paths" in source, (
        "a 404 does not tell the caller which paths exist")
