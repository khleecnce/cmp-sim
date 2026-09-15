"""Unit conversions in the pattern report, and the honesty of the contact branch.

Both of these were real defects: the up-area rate was reported as 0.0 A/min for
every run while the same object's notes quoted the correct figure, and the
contact branch was reported as a confident finding when it rested on a bulk
hardness that biases the answer.
"""
import numpy as np
import pytest

from cmp_sim.core import regime as rg
from cmp_sim.models import pattern_density as pdm


def _evaluate(blanket_A_per_min=3639.0, density=0.5, time_s=60.0):
    return pdm.evaluate(
        blanket_rate_m_per_s=blanket_A_per_min * 1e-10 / 60.0,
        rho_local=np.full(201, density), x_m=np.linspace(0.0, 0.02, 201),
        planarization_length_m=2.456e-3, initial_step_m=1.2e-6, time_s=time_s,
    ).as_dict()


def test_up_area_rate_is_reported_in_angstrom_per_minute():
    """RR_up = blanket / rho_eff, so at 50% density it is exactly twice."""
    out = _evaluate(blanket_A_per_min=3639.0, density=0.5)
    assert out["up_area_rate_A_per_min"]["min"] == pytest.approx(7278.0, rel=1e-3)


def test_up_area_rate_is_never_silently_zero_for_a_real_rate():
    """The m/s -> A/min factor was wrong by 6e10, rounding every rate to 0.0."""
    out = _evaluate()
    assert out["up_area_rate_A_per_min"]["min"] > 0.0


def test_the_reported_rate_agrees_with_the_models_own_note():
    """The dict and the notes are generated separately; they must not disagree."""
    out = _evaluate()
    quoted = [n for n in out["notes"] if "up-area rate spans" in n]
    assert quoted, "the model no longer explains its up-area rate"
    figure = float(quoted[0].split("spans")[1].split("-")[0])
    assert out["up_area_rate_A_per_min"]["min"] == pytest.approx(figure, rel=0.01)


def test_denser_regions_polish_more_slowly():
    sparse = _evaluate(density=0.25)["up_area_rate_A_per_min"]["min"]
    dense = _evaluate(density=0.75)["up_area_rate_A_per_min"]["min"]
    assert sparse > dense


# ── contact branch honesty ───────────────────────────────────────────
class _Fake:
    """Minimal stand-in for a resolved recipe."""
    def __init__(self, values, film="cu"):
        self._v = values
        self.pressure_pa = 20000.0
        class _W:
            pattern_density = None
        class _P:
            use_hours = 0.0
        class _D:
            hours_used = 0.0
        class _R:
            wafer = _W(); pad = _P(); disk = _D()
        _R.wafer.film = film
        self.recipe = _R()

    def p_or(self, key, default=None):
        return self._v.get(key, default)

    def has(self, key):
        return self._v.get(key) is not None


def test_bulk_hardness_alone_does_not_decide_the_contact_branch():
    """CMP abrades a softened layer that is softer than the bulk, so a bulk
    ratio biases the answer toward 'elastic' — the branch that makes removal
    size-independent. It must be provisional, not a finding."""
    s = rg.detect(_Fake({"particle_contact_stress_pa": 2.58e8,
                         "film_bulk_hardness_pa": 8.0e9}, film="oxide"))
    assert s.contact_branch == "unknown"
    assert any("provisional" in u for u in s.undetermined)
    assert "contact_stress_over_bulk_hardness" in s.metrics


def test_the_softened_hardness_does_decide_it():
    s = rg.detect(_Fake({"particle_contact_stress_pa": 4.0e9,
                         "film_surface_hardness_pa": 3.24e9,
                         "film_bulk_hardness_pa": 1.0e9}, film="cu"))
    assert s.contact_branch == "plastic"
    assert "contact_stress_over_hardness" in s.metrics


def test_the_circularity_trap_is_stated_when_both_are_missing():
    """In Luo-Dornfeld the contact stress is SET EQUAL to the hardness, so
    sourcing it independently is circular unless directly measured."""
    s = rg.detect(_Fake({"film_bulk_hardness_pa": 1.0e9}, film="cu"))
    assert s.contact_branch == "unknown"
    assert any("circular" in u for u in s.undetermined)
