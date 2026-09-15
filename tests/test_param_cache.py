"""The parsed-YAML cache must not change any answer.

A cache is only safe if it is invisible. Two ways it could corrupt results, both
tested here:

* **Leakage** — packs are mutated in place by owner overrides and by fitted
  factors. If the cache handed out a shared object, one run's override would
  appear in the next run, which is a wrong answer with no error message.
* **Staleness** — during a parameter-tuning session the owner edits a YAML and
  re-runs. A cache keyed only on the path would keep serving the old number.
"""
import time
from pathlib import Path

import pytest

from cmp_sim.core import params as P


def test_a_second_load_gives_an_equal_but_separate_pack():
    a = P.load_pack("oxide_silica")
    b = P.load_pack("oxide_silica")
    assert a is not b, "the same pack object was handed out twice"
    assert a.get("kp_m_per_pa") == b.get("kp_m_per_pa")


def test_mutating_one_pack_does_not_affect_the_next_load():
    """The leak that would matter: owner overrides and fitted factors both
    write into the pack, so a shared object would carry them into later runs."""
    from sim.params import Param

    a = P.load_pack("oxide_silica")
    original = a.get("kp_m_per_pa")
    # This is how the solver writes a fitted Kp and an owner override: straight
    # into the pack's params dict.
    a.params["kp_m_per_pa"] = Param(
        key="kp_m_per_pa", value=1.234e-13, unit="m/Pa",
        source="test", confidence="low")
    assert a.get("kp_m_per_pa") == pytest.approx(1.234e-13)

    b = P.load_pack("oxide_silica")
    assert b.get("kp_m_per_pa") == pytest.approx(original), (
        "a mutation leaked through the cache into a fresh load")

    # And a nested structure, which a shallow copy would share
    db = P.load_pack("oxide_silica")
    assert db.params["kp_m_per_pa"] is not a.params["kp_m_per_pa"]


def test_editing_a_pack_is_picked_up_immediately(tmp_path, monkeypatch):
    """A stale cache during parameter tuning is a silent wrong answer."""
    pack = tmp_path / "cachetest.yaml"
    pack.write_text(
        "film: oxide\n"
        "params:\n"
        "  kp_m_per_pa:\n"
        "    value: 1.0e-13\n"
        "    unit: m/Pa\n"
        "    source: test\n"
        "    confidence: low\n",
        encoding="utf-8")
    monkeypatch.setattr(P, "SEARCH_PATH", [tmp_path, *P.SEARCH_PATH])

    first = P.load_pack("cachetest").get("kp_m_per_pa")
    assert first == pytest.approx(1.0e-13)

    # A same-size rewrite is the hard case: if the cache keyed on size alone it
    # would miss this. mtime_ns resolution is fine, but sleep a little so the
    # test does not depend on filesystem timestamp granularity.
    time.sleep(0.01)
    pack.write_text(
        "film: oxide\n"
        "params:\n"
        "  kp_m_per_pa:\n"
        "    value: 9.0e-13\n"
        "    unit: m/Pa\n"
        "    source: test\n"
        "    confidence: low\n",
        encoding="utf-8")

    second = P.load_pack("cachetest").get("kp_m_per_pa")
    assert second == pytest.approx(9.0e-13), (
        "an edited pack still returned the old value - the cache is stale")


def test_clear_cache_is_available_and_harmless():
    P.load_pack("oxide_silica")
    P.clear_cache()
    assert P.load_pack("oxide_silica").get("kp_m_per_pa") is not None


def test_the_cache_actually_speeds_repeated_loads():
    """If this regresses the cache has been bypassed; the win was ~10x."""
    P.clear_cache()
    t0 = time.perf_counter()
    for _ in range(3):
        P.clear_cache()
        P.load_pack("oxide_silica")
    cold = time.perf_counter() - t0

    P.load_pack("oxide_silica")          # warm it
    t1 = time.perf_counter()
    for _ in range(3):
        P.load_pack("oxide_silica")
    warm = time.perf_counter() - t1

    assert warm < cold, f"cached loads ({warm:.4f}s) are not faster than cold ({cold:.4f}s)"


def test_results_are_identical_with_and_without_the_cache():
    """The only acceptable effect of a cache is on the clock."""
    from cmp_sim.core.solver import simulate
    from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer

    def recipe():
        return Recipe(
            model="full", wafer=Wafer(film="oxide", n_radial=21),
            slurry=Slurry(pack="oxide_silica"),
            pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
            disk=Disk(),
            tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=60))

    P.clear_cache()
    cold = simulate(recipe()).mean_rr_angstrom_per_min
    warm = simulate(recipe()).mean_rr_angstrom_per_min
    assert cold == pytest.approx(warm, rel=1e-12), (
        f"cached run gave {warm} but uncached gave {cold}")
