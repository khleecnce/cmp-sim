"""세리아 pH 정전 창 + 런 저장소 계약 테스트."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.engine import Recipe, simulate            # noqa: E402
from sim.factors import compute_factors            # noqa: E402


def _chi(pack, **ov):
    return compute_factors(Recipe(pack=pack, pack_overrides=ov).resolve())["chi"]


# ═══════════════════ 세리아 pH — 실리카와 메커니즘·방향이 다르다

def test_ceria_uses_window_model_not_silica_peak():
    """sti_ceria가 oxide_silica를 상속해도 pH 항은 세리아 창이어야 한다.

    ⚠ 2026-09-08 백테스트에서 dandu2009가 ρ=−0.525(음의 상관)로 나온 원인:
      상속 때문에 실리카의 pH 11 정점 항이 세리아에 적용됐다. 실리카 IEP 2.5,
      세리아 6.8 — 정전 상호작용이 반대 방향이라 부호까지 틀렸다.
    """
    f = _chi("sti_ceria")
    assert "ph_ceria_window" in f.terms, f.terms
    assert "ph_peak" not in f.terms, "세리아에 실리카 정점 모델이 섞였다"


def test_silica_still_uses_peak_model():
    f = _chi("oxide_silica")
    assert "ph_peak" in f.terms and "ph_ceria_window" not in f.terms


def test_ceria_window_reproduces_dandu2009_ranking():
    """Dandu 2009 Fig.2a 9점의 **순위**를 재현해야 한다.

    pH 2→4.3, 3→95.3, 3.5→276.3, 4→347.4, 5→344.3, 5.5→350.4, 6→99.3, 8→69.4, 10→64.3
    """
    lit = {2.0: 4.3, 3.0: 95.3, 3.5: 276.3, 4.0: 347.4, 5.0: 344.3,
           5.5: 350.4, 6.0: 99.3, 8.0: 69.4, 10.0: 64.3}
    pred = {ph: _chi("sti_ceria", slurry_ph=ph).value for ph in lit}
    # 창 안(4~5.5) > 창 경계(3.5, 6) > 창 밖(2, 8, 10)
    inside = min(pred[4.0], pred[5.0], pred[5.5])
    edge = max(pred[3.5], pred[6.0])
    outside = max(pred[2.0], pred[8.0], pred[10.0])
    assert inside > edge > outside, pred
    # Spearman ≥ 0.9
    from validation.backtest import spearman_rho
    ks = sorted(lit)
    rho = spearman_rho([pred[k] for k in ks], [lit[k] for k in ks])
    assert rho >= 0.9, f"ρ={rho:.3f}"


def test_ceria_window_is_unity_at_reference():
    assert _chi("sti_ceria").value == pytest.approx(1.0, abs=1e-9)


def test_ceria_ph_cliff_at_iep():
    """pH 5.5→6.0 에서 급락(실측 350→99). 단조 완만 모델로 퇴행하면 잡힌다."""
    a = _chi("sti_ceria", slurry_ph=5.5).value
    b = _chi("sti_ceria", slurry_ph=6.0).value
    assert b / a < 0.5, f"pH 6에서 {b/a:.3f} — 급락이 사라졌다"


def test_ceria_warns_near_iep():
    f = _chi("sti_ceria", slurry_ph=6.5)
    assert any("IEP" in n and "응집" in n for n in f.notes)


def test_ceria_ph_moves_engine_mrr():
    a = float(np.mean(simulate(Recipe(pack="sti_ceria",
                                      pack_overrides={"slurry_ph": 5.0})).mrr_nm_per_min))
    b = float(np.mean(simulate(Recipe(pack="sti_ceria",
                                      pack_overrides={"slurry_ph": 9.0})).mrr_nm_per_min))
    assert a > b * 2, "세리아 pH가 엔진 MRR에 안 붙었다"


# ═══════════════════ 런 저장소

@pytest.fixture
def tmp_store(tmp_path, monkeypatch):
    from sim import store
    monkeypatch.setattr(store, "DB_DIR", tmp_path)
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "t.sqlite")
    return store


def test_store_saves_and_reads_run(tmp_store):
    s = simulate(Recipe(pack="oxide_silica")).summary()
    rid = tmp_store.save_run(s, {"pack": "oxide_silica"})
    r = tmp_store.get_run(rid)
    assert r and r["pack"] == "oxide_silica"
    assert r["summary"]["mean_mrr_nm_min"] == pytest.approx(s["mean_mrr_nm_min"])
    assert tmp_store.stats()["runs"] == 1


def test_measurement_mrr_derived_only_when_possible(tmp_store):
    """시간이 없으면 MRR을 지어내지 않고 None."""
    pts = [{"thickness_pre_nm": 1000.0, "thickness_post_nm": 870.0}] * 5
    m1 = tmp_store.save_measurement("a.xlsx", {"pressure_psi": 3.0}, pts, {})
    assert tmp_store.get_measurement(m1)["mrr_mean"] is None
    m2 = tmp_store.save_measurement("b.xlsx", {"pressure_psi": 3.0, "time_s": 60.0}, pts, {})
    assert tmp_store.get_measurement(m2)["mrr_mean"] == pytest.approx(130.0)


def test_calibration_refuses_below_min_n(tmp_store):
    """실측 1~2건으로 Kp를 흔들지 않는다 — 노이즈와 신호를 구분 못 한다."""
    pts = [{"mrr_nm_min": 140.0}]
    tmp_store.save_measurement("a.xlsx", {"pressure_psi": 3.0}, pts, {}, pack_hint="oxide_silica")
    cal = tmp_store.calibration_factor("oxide_silica", lambda c: 128.7)
    assert cal.factor == 1.0 and cal.n_used == 1
    assert "보정하지 않음" in cal.note


def test_calibration_uses_median_ratio(tmp_store):
    for v in (130.0, 140.0, 150.0):
        tmp_store.save_measurement("x.xlsx", {"pressure_psi": 3.0}, [{"mrr_nm_min": v}],
                                   {}, pack_hint="oxide_silica")
    cal = tmp_store.calibration_factor("oxide_silica", lambda c: 100.0)
    assert cal.factor == pytest.approx(1.4)
    assert cal.n_used == 3


def test_calibration_flags_wide_spread(tmp_store):
    for v in (50.0, 140.0, 400.0):
        tmp_store.save_measurement("x.xlsx", {"pressure_psi": 3.0}, [{"mrr_nm_min": v}],
                                   {}, pack_hint="oxide_silica")
    cal = tmp_store.calibration_factor("oxide_silica", lambda c: 100.0)
    assert "산포가 크다" in cal.note


def test_calibration_ignores_other_packs(tmp_store):
    for _ in range(3):
        tmp_store.save_measurement("x.xlsx", {"pressure_psi": 3.0}, [{"mrr_nm_min": 500.0}],
                                   {}, pack_hint="cu_h2o2_bta")
    cal = tmp_store.calibration_factor("oxide_silica", lambda c: 100.0)
    assert cal.factor == 1.0, "다른 팩의 실측이 섞였다"
