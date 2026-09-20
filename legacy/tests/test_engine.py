"""엔진 + 지표 회귀. 물리 재정의 없이 계약(스키마·단조성·정의)만 검증."""
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.special import ellipe

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.engine import Recipe, simulate, available_models  # noqa: E402
from sim.metrics.uniformity import compute_metrics, compute_metrics_points  # noqa: E402


def test_models_registered():
    assert "tier1.preston_radial" in available_models()


def test_simulate_shapes_and_units():
    r = Recipe(n_points=81, time_s=60)
    res = simulate(r)
    assert res.radius_m.shape == (81,) == res.mrr_nm_per_min.shape == res.removed_nm.shape
    assert np.all(res.mrr_nm_per_min > 0)
    # 60초 = 1분이므로 removed == mrr
    assert np.allclose(res.removed_nm, res.mrr_nm_per_min)
    assert res.remaining_nm is None
    assert res.metrics.n_points == 81


def test_preston_linearity_in_pressure_and_time():
    """압력은 여전히 엄밀히 선형. **시간은 2026-09-14부터 초선형(superlinear)이다.**

    시간 계약 변경의 근거: Philipossian & Mitchell 2004(doi:10.1149/1.1731539)는
    턴오버비 TR = MRT/t_polish 가 커질수록 Preston 상수가 **떨어진다**는 것을 ILD oxide
    실측으로 보였다(TR=1.13에서 370 Å vs TR=0에서 500 Å, 26% 감소). 짧은 폴리시일수록
    물→슬러리 치환 과도기가 차지하는 비중이 커져 계면 고형분 농도가 정상상태에 못 미치기
    때문이다. 그래서 시간을 2배로 늘리면 제거량은 **2배보다 조금 더** 나온다.
    → knowledge/cmp/slurry-turnover-ratio-mrt-preston-constant.md §5, τ의 turnover 항.

    ⚠ 압력 선형성은 **의도적으로 지켰다.** Mu 2016이 MRT의 압력 의존도 실측했지만
      (3→5 PSI에서 MRT 약 0.90배), P는 이미 Preston 본항이 지배적으로 담고 있고
      MRT 경로 기여는 30 s·2 PSI 스윙에서 약 1.1%에 불과하다. 오더가 두 자릿수 차이나는
      부차 경로 때문에 전역 계약을 깨지 않는다(sim/factors.py::_f_tau 주석 참조).
    """
    a = simulate(Recipe(pressure_psi=2.0, time_s=30)).removed_nm
    b = simulate(Recipe(pressure_psi=4.0, time_s=30)).removed_nm
    c = simulate(Recipe(pressure_psi=2.0, time_s=60)).removed_nm
    assert np.allclose(b, 2 * a, rtol=1e-9), "압력 선형성은 유지돼야 한다"

    # 시간: 2배보다 크되, 문헌이 준 크기(30 s에서 τ 배수 0.9576)와 일치해야 한다.
    ratio = float(np.mean(c) / np.mean(2 * a))
    assert ratio > 1.0, "TR 효과로 긴 폴리시가 유리해야 한다(2배보다 더 제거)"
    assert ratio == pytest.approx(1 / 0.9576, abs=0.002), (
        f"시간 2배 제거량 비가 {ratio:.4f} — 문헌 유도값 1/0.9576=1.0443이어야 한다. "
        "τ turnover 항이 빠졌거나 크기가 달라졌다.")


def test_uniform_pressure_gives_low_nonuniformity():
    """균일압력에서 CV는 순수 운동학 효과 — 완전타원적분 폐형식과 대조 (TEST-AUDIT §3-A #2).

    폐형식(test_preston.py::rs_neq1_edge_center_ratio_matches_kinematics와 동일 유도,
    Lai 2001 Eq.2.11): <|v|>_theta/v_ref(x) = (2/pi)*(1+|x|)*ellipe(4|x|/(1+|x|)^2),
    x = (r/R_w)*mu, mu=(R_w/r_cc)(1-Rs). 균일압력이므로 MRR ∝ 이 속도비(상수 배율은
    CV에 기여 없음) → 엔진 결과와 무관하게 독립 재계산해 비교.
    """
    res = simulate(Recipe(edge_pressure_amp=0.0))
    rr = Recipe(edge_pressure_amp=0.0).resolve()
    mu = (rr.wafer_radius_m / rr.center_offset_m) * (1.0 - rr.rpm_wafer / rr.rpm_platen)
    x = np.abs(res.radius_m / rr.wafer_radius_m * mu)
    speed_ratio = (2.0 / np.pi) * (1.0 + x) * ellipe(4.0 * x / (1.0 + x) ** 2)
    cv_analytic = float(np.std(speed_ratio) / np.mean(speed_ratio) * 100.0)
    rel = abs(res.metrics.cv_pct - cv_analytic) / cv_analytic
    assert rel < 1e-3, (res.metrics.cv_pct, cv_analytic, rel)


def test_edge_pressure_increases_ttv():
    flat = simulate(Recipe(edge_pressure_amp=0.0)).metrics.ttv_nm
    edge = simulate(Recipe(edge_pressure_amp=0.3)).metrics.ttv_nm
    assert edge > flat * 3


def test_remaining_and_overpolish_note():
    res = simulate(Recipe(initial_thickness_nm=100.0, time_s=60))
    assert res.remaining_nm is not None
    assert any("오버폴리시" in n for n in res.notes)


def test_ptw_and_film_notes_are_honest():
    """모르는 것을 모른다고 말하는지.

    ⚠ 2026-09-06 파라미터 팩 도입으로 이 테스트의 의미가 하나 바뀌었다.
    예전에는 film='cu'로 돌려도 산화막 Kp를 그대로 써서 "막질별 Kp 미분화"라고
    경고했다. 이제는 팩(cu_h2o2_bta)이 Cu Kp를 실제로 갖고 있으므로 그 경고는
    사실이 아니다 — 대신 그 값이 estimated(미재현)라는 경고가 나와야 한다.
    """
    res = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW"))
    assert res.dishing_nm is None and res.metal_contamination is None
    assert any("PTW" in n for n in res.notes)
    # 막질은 팩이 정한다 — 레시피에 안 써도 cu가 되어야 한다
    assert res.film == "cu"
    # Cu Kp는 문헌 역산(estimated)이므로 정직하게 미검증 경고가 붙어야 한다
    assert any("미검증" in n and "kp_m_per_pa" in n for n in res.notes), res.notes


def test_metric_definitions():
    r = np.linspace(0, 0.147, 81)
    v = np.linspace(500, 520, 81)
    m = compute_metrics(r, v)
    assert m.ttv_nm == pytest.approx(20)
    assert m.cv_pct == pytest.approx(np.std(v) / np.mean(v) * 100)
    assert m.wiwnu_halfrange_pct == pytest.approx(20 / (2 * np.mean(v)) * 100)
    assert len(m.ring_ttv_nm) == 8
    assert m.radial_maxring_range_nm == pytest.approx(max(m.ring_ttv_nm))
    # 문헌 항등식 (uniformity-metrics-definitions-standards.md §2·§3)
    assert m.wiwnu_3sigma_pct == pytest.approx(3 * m.cv_pct)  # US6922603B1: 3σ = 3×1σ
    assert m.cv_pct == pytest.approx(m.sigma_nm / m.mean_nm * 100)  # CV ≡ 1σ WIWNU


def test_points_and_profile_agree():
    th = np.linspace(0, 2 * np.pi, 81, endpoint=False)
    rr = np.linspace(0, 0.147, 81)
    v = np.linspace(500, 520, 81)
    a = compute_metrics(rr, v)
    b = compute_metrics_points(rr * np.cos(th), rr * np.sin(th), v)
    assert a.ttv_nm == pytest.approx(b.ttv_nm) and a.radial_maxring_range_nm == pytest.approx(b.radial_maxring_range_nm)
