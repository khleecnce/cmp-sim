"""병합 파라미터(sim/factors.py) 계약 테스트 — ARCHITECTURE-V2.md §2.

여기서 고정하는 것은 **물리가 아니라 계약**이다:
  ① 기준 조건에서 모든 팩터가 정확히 1.0 (이중 계상 방지)
  ② 입력을 바꾸면 출력이 실제로 바뀐다 (V1의 핵심 결함 회귀 방지)
  ③ 미모델링을 조용한 1.0으로 숨기지 않는다
  ④ 장비축과 소모품축이 섞이지 않는다 (사용자 확정 규칙)
  ⑤ 문헌 실측 재현 (pH 정점형)
"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe, simulate                      # noqa: E402
from sim.factors import (compute_factors, mrr_multiplier, coverage,   # noqa: E402
                         FACTOR_SPEC, MRR_COUPLED,
                         AXIS_EQUIPMENT, AXIS_CONSUMABLE)


def _factors(pack="oxide_silica", **overrides):
    return compute_factors(Recipe(pack=pack, pack_overrides=overrides).resolve())


def _mean_mrr(pack="oxide_silica", **overrides):
    r = simulate(Recipe(pack=pack, pack_overrides=overrides))
    return float(np.mean(r.mrr_nm_per_min))


# ═══════════════════════════════ ① 기준 조건 = 1.0 (이중 계상 방지)

def test_all_factors_are_unity_at_reference_condition():
    """기준 조건에서 모든 팩터는 정확히 1.0이어야 한다.

    왜 이게 가장 중요한 테스트인가: Kp는 이미 특정 조성·조건에서 역산된 값이다.
    팩터를 절대값으로 곱하면 같은 효과를 두 번 센다 — 2026-09-06에 Cu MRR이
    20배 붕괴한 사고가 정확히 이것이었다.
    """
    for key, f in _factors().items():
        if f.value is None:
            continue
        assert f.value == pytest.approx(1.0, abs=1e-9), (
            f"{f.symbol} {f.name}이 기준 조건에서 {f.value}다 — 1.0이어야 한다. "
            f"'_ref' 파라미터가 현재 조건과 다르면 이중 계상이 된다.")


def test_mrr_multiplier_is_unity_at_reference():
    mult, _ = mrr_multiplier(_factors())
    assert mult == pytest.approx(1.0, abs=1e-9)


def test_engine_does_not_double_count_chemistry():
    """엔진은 chemistry_factor와 factors.χ를 **둘 다** 곱하면 안 된다.

    χ는 chemistry.py의 산화제·세리아 항을 승계했다. 결합 지점이 두 곳이면
    화학이 제곱으로 들어간다.
    """
    import inspect
    from sim import engine
    src = inspect.getsource(engine.simulate)
    # 주석은 걷어내고 **실행되는 코드**만 본다 — 주석에 함수명을 언급했다고
    # 실패하면 테스트가 문서를 못 쓰게 만든다.
    code_only = "\n".join(
        line for line in src.splitlines()
        if not line.lstrip().startswith("#"))
    assert "chemistry_factor(" not in code_only, (
        "simulate()가 chemistry_factor를 직접 호출한다 — factors.χ가 이미 "
        "그 항을 승계했으므로 화학을 두 번 세게 된다.")


# ═══════════════════════════════ ② 입력이 실제로 출력을 바꾼다 (V1 결함 회귀)

@pytest.mark.parametrize("key,ref,expect_sign", [
    ("abrasive_wt_pct", 20.0, +1),        # 농도↑ → MRR↑ (문헌 직접 서술)
    ("pad_hardness_shore_d", 60.0, -1),   # 경도↑ → MRR↓ (H^-1.5)
    ("asperity_density_per_m2", 1e11, +1),
])
def test_consumable_inputs_actually_move_mrr(key, ref, expect_sign):
    """소모품 인자를 바꾸면 MRR이 **실제로** 변해야 한다.

    V1의 핵심 결함이 여기였다: --sensitivity에서 pH·입자크기·패드조도가 전부
    탄성도 0.000이었다. 소재 개발자용 도구인데 조성을 바꿔도 결과가 같았다.
    """
    lo = _mean_mrr(**{key: ref * 0.9})
    hi = _mean_mrr(**{key: ref * 1.1})
    assert lo != pytest.approx(hi, rel=1e-6), (
        f"{key}를 ±10% 바꿨는데 MRR이 안 변한다 — 엔진에 연결되지 않았다.")
    assert np.sign(hi - lo) == expect_sign, (
        f"{key} 증가 시 MRR 방향이 {np.sign(hi-lo)}인데 {expect_sign}이어야 한다.")


def test_kappa_abrasive_wt_pct_wired_for_w_fe_oxidizer():
    """2026-09-12 정확도루프: w_fe_oxidizer에 abrasive_wt_pct(Bielmann 1999, 10 wt%)와
    abrasive_conc_exponent(Wang 2012, 1/3)를 신규 배선했다. cu_h2o2_bta·w_fe_oxidizer 중
    w_fe_oxidizer만 값이 있으므로 이 팩에서만 농도가 MRR을 움직여야 한다.
    """
    lo = _mean_mrr(pack="w_fe_oxidizer", abrasive_wt_pct=9.0)
    hi = _mean_mrr(pack="w_fe_oxidizer", abrasive_wt_pct=11.0)
    assert lo != pytest.approx(hi, rel=1e-6), (
        "w_fe_oxidizer의 abrasive_wt_pct를 바꿨는데 MRR이 안 변한다 — 배선이 깨졌다.")
    assert hi > lo, "농도 증가는 MRR 증가로 이어져야 한다(Bielmann/Wang 1/3 지수)."


def test_kappa_reference_unity_for_w_fe_oxidizer():
    """기준 농도(10.0 wt%, Bielmann 1999 실험 조건)에서 κ의 conc 항은 정확히 1.0."""
    f = _factors(pack="w_fe_oxidizer")["kappa"]
    assert f.terms.get("conc") == pytest.approx(1.0, rel=1e-9), (
        f"기준 조건(abrasive_wt_pct=abrasive_ref_wt_pct=10.0)에서 conc항은 1.0이어야 하는데 "
        f"{f.terms.get('conc')}다.")


def test_kappa_size_null_result_for_w_fe_oxidizer():
    """2026-09-12 정확도루프: w_fe_oxidizer에 abrasive_size_exponent=0.0(검증된 null)을 배선했다.

    Egan & Kim 2019(GLOBALFOUNDRIES W CMP 실측) + Bouvet 2002(콜로이달 실리카, 12-75nm 정량 확인)
    독립 두 문헌이 "입경-MRR 무반응" 방향으로 수렴 — cu_h2o2_bta와 별개로 확정된 두 번째 null.
    지수 0은 팩에 명시된 값이므로 size 항이 terms에 계상되어야 하고(미모델링과 구분), 값은 1.0.
    """
    f = _factors(pack="w_fe_oxidizer")["kappa"]
    assert "size" in f.terms, "지수가 명시(0.0)됐는데 size 항이 계상되지 않았다 — null과 미모델링을 혼동했다."
    assert f.terms["size"] == pytest.approx(1.0, rel=1e-9), (
        "지수 0이면 입경을 바꿔도 size 항은 항상 1.0이어야 한다.")


def test_kappa_size_null_result_insensitive_to_size_change():
    """abrasive_size_nm을 바꿔도 w_fe_oxidizer의 κ 총 배수는 불변(검증된 null 결과)."""
    lo = _mean_mrr(pack="w_fe_oxidizer", abrasive_size_nm=25.0)
    hi = _mean_mrr(pack="w_fe_oxidizer", abrasive_size_nm=100.0)
    assert lo == pytest.approx(hi, rel=1e-6), (
        "w_fe_oxidizer는 입경 지수가 0(검증된 null)인데 입경을 바꾸자 MRR이 변했다 — 배선 오류.")


def test_ph_moves_mrr():
    """pH는 정점형이라 부호 테스트가 아니라 '변하는가'로 묻는다."""
    assert _mean_mrr(slurry_ph=10.0) != pytest.approx(_mean_mrr(slurry_ph=11.0), rel=1e-6)


# ═══════════════════════════════ ③ 미모델링을 숨기지 않는다

def test_stab_reference_at_default_time_is_unity():
    """S(안정성)는 기준 조건(in-situ duty 100%·신품 디스크·time_s=60s)에서 1.0.

    2026-09-14 글레이징-컨디셔닝 균형 모델(knowledge/materials/
    pad-steady-state-glazing-conditioning-balance.md): S = R_ss(G)/R_ss(G_ref).
    기준점은 Γ과 공유(cond_ref_duty_pct, cond_ref_disk_usage_hours)한다.
    """
    f = _factors()["stab"]
    assert f.status == "modeled"
    assert f.value == pytest.approx(1.0, abs=1e-9)
    assert f.terms["R_ss(G)"] == pytest.approx(0.9932, abs=5e-4)   # k_c/(k_g+k_c), 노트 §5-1


def _stab(pack="oxide_silica", time_s=60, **ov):
    return compute_factors(Recipe(pack=pack, time_s=time_s, pack_overrides=ov).resolve())["stab"]


def test_stab_no_conditioning_reproduces_jeong2024_log_decay():
    """duty=0(웨이퍼마다 ex-situ 재생, 연마 중 무컨디셔닝) 특수해 = Jeong 2024 로그감쇠 회귀.

    회귀 테스트: 균형 모델로 바꿔도 무컨디셔닝 10 min 값(0.7775)은 기존 로그감쇠
    (a=1.1478, b=−0.1109)와 1e-9 이내로 같아야 한다 — k_g가 그 값에서 역산됐기 때문.
    """
    a, b = 1.1478, -0.1109
    for t in (60, 180, 600):
        f = _stab(time_s=t, cond_duty_pct=0.0)
        assert "no_conditioning_decay" in f.terms
        legacy_10 = (a + b * math.log(10)) / a
        if t == 600:
            assert f.value == pytest.approx(legacy_10, abs=1e-9)
    short = _stab(time_s=60, cond_duty_pct=0.0).value
    long_ = _stab(time_s=600, cond_duty_pct=0.0).value
    assert short == pytest.approx(1.0, abs=1e-9)
    assert long_ < short and 0.7 < long_ < 1.0


def test_stab_in_situ_steady_state_is_time_independent():
    """in-situ(G>0)에서는 시정수 0.24 min ≪ 연마시간이라 S가 time_s에 무관하다 (식 5a)."""
    assert _stab(time_s=60).value == pytest.approx(_stab(time_s=600).value, abs=1e-12)
    assert _stab(time_s=600).value == pytest.approx(_stab(time_s=3600).value, abs=1e-12)


def test_stab_clamped_outside_observed_range():
    """무컨디셔닝 분기의 관측범위(1~10 min) 밖은 clamp — 외삽으로 거짓 정밀도를 내지 않는다."""
    at_10 = _stab(time_s=600, cond_duty_pct=0.0).value
    at_60min = _stab(time_s=3600, cond_duty_pct=0.0).value
    assert at_60min == pytest.approx(at_10), "10 min 초과는 t=10 min 값으로 clamp되어야 한다"


def test_stab_increases_with_conditioning_duty():
    """duty↑ → 컨디셔닝 강도 G↑ → R_ss↑ → S↑ (단조), 100%에서 1.0."""
    # duty=0 은 무컨디셔닝 분기(시간 의존)이므로 10 min 연마로 고정해 비교한다.
    vals = [_stab(time_s=600, cond_duty_pct=d).value for d in (0.0, 25.0, 50.0, 100.0)]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)), vals
    assert vals[-1] == pytest.approx(1.0, abs=1e-9)


def test_stab_decreases_with_dresser_usage_and_shares_gamma_aging():
    """드레서 사용량↑ → A(t)↓ → G↓ → S↓ (단조). PHM2016 실장비 ρ=−0.70의 방향.

    S와 Γ은 같은 pcr_decay 배수를 본다 — 'dresser_wear_A' == Γ 'aging(pcr_decay)'.
    """
    hours = [0.0, 10.0, 27.4, 50.0, 100.0]
    vals = [_stab(cond_disk_usage_hours=h).value for h in hours]
    assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)), vals
    for h in (0.0, 50.0):
        fs = compute_factors(Recipe(pack="oxide_silica", pack_overrides={"cond_disk_usage_hours": h}).resolve())
        assert fs["stab"].terms["dresser_wear_A"] == pytest.approx(fs["gamma"].terms["aging(pcr_decay)"], abs=1e-12)


def test_stab_confidence_is_computed_from_k_g_band_not_literal():
    """비-실리카 팩의 등급은 리터럴 강등이 아니라 k_g 밴드(×5)가 이번 운전점에 미치는 |ΔS|로 판정.

    기준점(G=G_ref)에서는 k_g가 상쇄돼 ΔS=0 → literature. 무컨디셔닝(duty=0)에서는
    밴드가 지배적(|ΔS|≈0.49) → 판정#9대로 estimated. 실리카는 어느 구간이든 literature.
    """
    assert _stab("cu_h2o2_bta").confidence == "literature"
    assert _stab("cu_h2o2_bta").terms["k_g_band_dS"] == pytest.approx(0.0, abs=1e-12)
    silica = _stab("oxide_silica", time_s=600, cond_duty_pct=0.0)
    alumina = _stab("cu_h2o2_bta", time_s=600, cond_duty_pct=0.0)
    assert silica.confidence == "literature"
    assert alumina.confidence == "estimated"
    assert alumina.terms["k_g_band_dS"] > 0.03
    # 드레서 50 h: 밴드 0.11 > 0.03 → 비-실리카는 estimated (정직한 강등, 계산된 값)
    assert _stab("cu_h2o2_bta", cond_disk_usage_hours=50.0).confidence == "estimated"
    assert _stab("oxide_silica", cond_disk_usage_hours=50.0).confidence == "literature"


# ═══════════════════════════════ τ 슬러리 전달 — 실측이 직관을 기각한 축

def test_tau_porosity_reproduces_prasad_8_percent():
    """기공률 15→45%(3배)에 MRR은 **8%만** 오른다 (Prasad 2013 III.D.3).

    ⚠ 이 테스트가 지키는 것: "슬러리를 더 많이 나르면 MRR이 비례해 오른다"는
      직관은 실측으로 기각됐다. 저자 스스로 비례 증가를 기대했다가 빗나갔다고
      적었다("nominal increase"). 누군가 이 지수를 '상식적으로' 키우면
      여기서 잡힌다.
    """
    lo = _factors(pad_porosity_pct=15.0, pad_ref_porosity_pct=15.0)["tau"].value
    hi = _factors(pad_porosity_pct=45.0, pad_ref_porosity_pct=15.0)["tau"].value
    assert lo == pytest.approx(1.0)
    assert hi / lo == pytest.approx(1.08, abs=0.005), (
        f"기공률 3배에 τ가 {hi/lo:.4f}배 — 문헌은 1.08배다. "
        "비례 가정으로 퇴행했을 수 있다.")


def test_tau_groove_width_reduces_mrr_via_turnover():
    """그루브를 넓히면 슬러리 체류시간(MRT)이 길어져 **MRR이 내려간다**.

    2026-09-14 교체. 이전 테스트는 η(이용효율) 정점 형상(600 µm 최대)을 지켰으나,
    η와 MRT는 같은 실측의 종속량(η·MRT = V_total/q_total, 실측 6점 2% 이내 일치)이라
    TR 항과 함께 쓰면 이중 계상이었다. 등급이 낮은 쪽(η 지수 0.07 = 기공률→그루브
    교차대입, E4)을 빼고 TR(ILD oxide 직접 실측 폐형식, E2)만 남겼다.
    근거: knowledge/cmp/slurry-turnover-ratio-mrt-preston-constant.md §4.

    ⚠ 방향의 독립 확인: Kao 2011(doi:10.1016/j.wear.2010.10.057) "the removal rate was
      reduced by increasing the groove width such that it finally approached the result
      of a non-grooved pad". 누군가 "넓을수록 잘 흐르니 MRR이 오른다"로 되돌리면 여기서 잡힌다.
    """
    t300 = _factors(groove_width_um=300.0)["tau"].value
    t600 = _factors(groove_width_um=600.0)["tau"].value
    t900 = _factors(groove_width_um=900.0)["tau"].value
    assert t300 > t600 > t900, (
        f"좁은 그루브가 유리해야 한다(MRT 9.2 < 10.6 < 13.9 s) — 실제 {t300:.4f}/"
        f"{t600:.4f}/{t900:.4f}")
    assert t600 == pytest.approx(1.0), "기준 폭 600 µm에서 τ=1.0 계약"


def test_tau_polish_time_lowers_mrr_philipossian_2004():
    """폴리시 시간을 60 s→30 s로 줄이면 TR이 2배가 되어 평균 MRR이 4.2% 더 떨어진다.

    Philipossian & Mitchell 2004 (doi:10.1149/1.1731539): f_TR = 1 − 0.2301·TR.
    기준 조건(W=600 µm, 3 PSI)에서 MRT=10.6 s(Mu 2016 Table 3)이므로
      60 s: TR=0.177 → 0.9594 / 30 s: TR=0.353 → 0.9187  ⟹ 비 0.9576.

    ⚠ 이 테스트가 지키는 것: time_s가 MRR에 **영향을 준다**는 사실. 예전 엔진에서
      time_s는 총 제거량만 선형 스케일했고 순간 MRR과 무관했다 — 그 구조적 결측을
      되돌리면 여기서 잡힌다.
    """
    # time_s는 팩 파라미터가 아니라 **레시피** 필드다 — _factors의 pack_overrides로는
    # 안 들어간다. Recipe에 직접 준다.
    def _tau(t):
        return compute_factors(
            Recipe(pack="oxide_silica", time_s=t).resolve())["tau"].value
    t30, t60, t120 = _tau(30.0), _tau(60.0), _tau(120.0)
    assert t60 == pytest.approx(1.0), "기준 60 s에서 τ=1.0 계약"
    assert t30 / t60 == pytest.approx(0.9576, abs=0.001), (
        f"30 s 배수가 {t30/t60:.4f} — 문헌 유도값은 0.9576이다")
    assert t120 > t60, "긴 폴리시는 과도기 비중이 작아 유리해야 한다"


def test_tau_status_is_modeled_after_scope_reduction():
    """2026-09-13: groove_depth_mm·groove_pitch_mm을 드라이버 수집에서 제외(스코프 축소,
    EVIDENCE-RULES §3회차 규칙 — 배수 관계가 그래프 이미지로만 존재해 텍스트로 확보 불가).
    남은 두 드라이버(groove_width_um·pad_porosity_pct)가 전부 term으로 반영되므로
    τ는 이제 'partial'이 아니라 'modeled'다 — 스코프를 줄인 것이지 입력을 놓친 게 아니다.
    accuracy_gaps.py --next가 더 이상 τ PARTIAL을 반환하지 않아야 한다.
    """
    for pack in ("cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"):
        f = _factors(pack=pack)["tau"]
        assert f.status == "modeled", f"{pack}: τ가 여전히 {f.status} — 스코프 축소가 반영 안 됨"
        # time_s는 2026-09-14 TR 채널이 끌어온 **레시피** 드라이버라 소모품 스코프 계약에서
        # 제외한다(turnover 항 안에 이미 반영됨).
        assert set(f.drivers) - {"time_s"} == {"groove_width_um", "pad_porosity_pct"}, (
            f"{pack}: τ 드라이버에 groove_depth_mm/groove_pitch_mm이 남아있다 — 스코프 축소 미반영")


def test_tau_admits_profile_coupling_is_missing():
    """τ의 진짜 효과(반경 프로파일)가 미구현임을 스스로 신고해야 한다."""
    f = _factors()["tau"]
    assert any("프로파일" in n for n in f.notes), (
        "τ가 '평균 MRR이 아니라 프로파일을 지배한다'는 한계를 숨기고 있다.")


def test_unmodeled_factors_are_excluded_from_mrr():
    """미모델링 팩터는 MRR 배수에 1.0으로도 참여하지 않고 '제외'로 보고된다."""
    fs = _factors()
    _, notes = mrr_multiplier(fs)
    for k in MRR_COUPLED:
        if fs[k].status == "unmodeled":
            assert any("미모델링" in n and fs[k].name in n for n in notes)


def test_missing_size_exponent_does_not_invent_a_value():
    """입경 정점형 파라미터가 전혀 없는 팩(w_fe_oxidizer는 null 지수 0.0을 명시하므로 제외,
    가상의 팩 없음 시나리오는 오버라이드로 피크 파라미터를 지워 재현)이면 항을 만들지
    않고 경고해야 한다.

    2026-09-13: Li et al. 2021 Eq.3-4를 벡터좌표로 재추출해 지수·부호가 확정됐고
    oxide_silica 팩에 정점형 파라미터(abrasive_size_peak_nm 등)를 배선했다 — 이제
    oxide_silica 기본 조건에서는 입경 항이 계상된다(과거엔 미적용이었다). 이 테스트는
    "파라미터가 아예 없을 때"의 안전장치(지어내지 않는다)를 확인하도록 갱신한다.
    """
    f = _factors(
        pack="oxide_silica",
        abrasive_size_peak_nm=None,
        abrasive_size_exp_below_peak=None,
        abrasive_size_exp_above_peak=None,
        abrasive_size_exponent=None,
    )["kappa"]
    assert "size" not in f.terms, "정점형·단일지수 파라미터를 모두 지웠는데 입경 항을 만들어냈다."
    assert any("입경" in n and "미적용" in n for n in f.notes)


def test_oxide_silica_size_peak_at_80nm():
    """2026-09-13: Li et al. 2021 Eq.3-4 벡터좌표 재추출로 확정된 정점형 입경 반응.

    40→80nm(압입 지배, φ^(4/3))은 증가, 80→130nm(표면적 지배, φ^(-1/3))은 감소해야
    하며, 80nm에서 정점(같은 기준 50nm 대비 최댓값)을 가져야 한다.
    """
    v40 = _factors(abrasive_size_nm=40.0)["kappa"].terms["size"]
    v80 = _factors(abrasive_size_nm=80.0)["kappa"].terms["size"]
    v130 = _factors(abrasive_size_nm=130.0)["kappa"].terms["size"]
    assert v80 > v40, "40->80nm 구간(압입 지배)은 입경 증가시 값이 커져야 한다."
    assert v80 > v130, "80->130nm 구간(표면적 지배)은 입경 증가시 값이 작아져야 한다."
    assert v80 == max(v40, v80, v130), "80nm이 세 값 중 정점(최댓값)이어야 한다."


def test_oxide_silica_size_unity_at_reference():
    """기준 입경(abrasive_size_nm=abrasive_ref_size_nm=50.0)에서 정점형 size 항은 1.0."""
    f = _factors()["kappa"]
    assert f.terms["size"] == pytest.approx(1.0, rel=1e-9)


# ═══════════════════════════════ ④ 축 분리 (사용자 확정 규칙)

def test_delta_is_unity_when_d99_equals_reference():
    """Δ 손상 유발도 — 기준 조건(D99==ref D99)에서 1.0 계약.

    sti_ceria(및 상속하는 sic_ceria_h2o2)에 Hitachi US8439995B2 Example 1
    (D99=700nm)을 baseline으로 이식했다 — 팩의 실제 조성값이 아니라 화학종
    (세리아, oxide/STI CMP) 일치를 근거로 한 what-if 기준점이다.
    """
    f = _factors(pack="sti_ceria")["delta"]
    assert f.value == pytest.approx(1.0, abs=1e-9)
    # 2026-09-13: abrasive_size_nm 스코프 축소 이후 남은 드라이버(d99)가 전부 term으로
    # 반영되므로 status는 modeled다(τ와 동일 패턴 — 스코프 축소는 완전 모델링과 구분되지 않음).
    assert f.status == "modeled"


def test_delta_increases_with_larger_d99_per_hitachi_exponent():
    """D99가 커지면 Δ가 실측 지수(n=1.44, US8439995B2)로 늘어난다.

    문헌 4점: D99 500->2500nm(5배)일 때 스크래치 10->100(10배).
    n=log(10)/log(5)=1.4306 — sti_ceria 팩의 damage_exponent=1.44와 근접
    (팩은 500nm가 아니라 700nm를 기준점으로 잡았으므로 완전히 같은 배수는
    아니다. 방향·오더만 검증한다).
    """
    f_ref = _factors(pack="sti_ceria")["delta"]
    f_big = _factors(pack="sti_ceria", abrasive_d99_nm=2500.0)["delta"]
    assert f_big.value > f_ref.value
    # US8439995B2: D99 700->2500nm(3.571배)에서 스크래치 20->100(5배 근방)
    # 이 팩의 n=1.44 기준으로는 3.571^1.44 = 6.25배 예측 -- 문헌 원값(5배,
    # 20->100)보다 다소 크다(기준점을 500이 아니라 700으로 잡았기 때문).
    # 순위(단조 증가)와 오더(같은 자릿수)만 검증 -- 절대 일치는 주장하지 않는다.
    ratio = f_big.value / f_ref.value
    assert 3.0 < ratio < 10.0, f"오더 이탈: {ratio:.2f}배 (문헌 5배 근방 기대)"


def test_delta_activated_for_three_more_packs_at_unity():
    """2026-09-11 COMPLETION-C1: cu_h2o2_bta/oxide_silica/w_fe_oxidizer 3팩에 D99를
    이식해 Δ가 unmodeled -> modeled(스코프 축소 이후)로 전환됐다. 3팩 모두 기준
    조건(D99==ref)에서 정확히 1.0이어야 한다 — 유도값(D99/D50 일반비)의 불확실성이
    기준점 계약을 깨면 안 된다(knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §6-D).

    2026-09-13: abrasive_size_nm을 Δ 드라이버 스코프에서 뺀 이후(τ와 동일 패턴,
    lpc-scratch-density-tail-correlation.md §3 — D99는 LPC 대리변수이지 평균 입경과
    동일 개념 아님) 남은 드라이버는 d99(+선언 시 aggregate_ratio)뿐이라
    status가 partial이 아니라 modeled로 승격됐다.
    """
    for pack in ("cu_h2o2_bta", "oxide_silica", "w_fe_oxidizer"):
        f = _factors(pack=pack)["delta"]
        assert f.status == "modeled", f"{pack}: Δ가 unmodeled/partial — D99 이식이 반영 안 됨"
        assert f.value == pytest.approx(1.0, abs=1e-9), f"{pack}: 기준 조건 Δ != 1.0"


def test_delta_aggregate_ratio_absent_by_default():
    """aggregate_ratio 미선언(팩에 키 자체가 없음)이면 Δ는 d99 항만으로 기존과 동일해야 한다.

    2026-09-13: aggregate_ratio는 이 회차 기준 어느 팩에도 파라미터로 선언돼 있지 않다
    (조사 완료가 아니라 "아직 이 경로를 조사하지 않았다"는 뜻) — 그래서 terms에 "aggregate"
    키 자체가 없어야 한다. 예전 버전은 기본값 0.0을 항상 term으로 넣어 "발동했지만
    무효과"와 "조사 안 됨"을 구분하지 못했다(τ와 같은 문제, 이번에 함께 고침).
    """
    f = _factors(pack="sti_ceria")
    assert "aggregate" not in f["delta"].terms
    assert f["delta"].value == pytest.approx(f["delta"].terms["d99"], rel=1e-9)


def test_delta_aggregate_ratio_override_creates_term():
    """aggregate_ratio를 recipe override로 명시하면(팩에 없어도) term에 잡혀야 한다.

    pack_overrides로 주입된 값도 pk.has()가 True를 반환하므로(sim/params.py),
    "이 회차에 조사·주입된 값"과 "팩 기본 스키마에 없는 값"을 이 테스트가 함께 검증한다.
    """
    f = _factors(pack="sti_ceria", aggregate_ratio=0.0)["delta"]
    assert "aggregate" in f.terms
    assert f.terms["aggregate"] == pytest.approx(1.0, abs=1e-9)


def test_delta_aggregate_ratio_scales_damage():
    """aggregate_ratio=1.0(문헌 NaCl 0.2M 상당 불안정화)이면 Δ가 정확히 2배가 된다.

    Basim & Moudgil 2002 Table 1: NaCl 0.2M(CCC=0.25M 미달, 평균 입경 불변)에서
    Rmax 25nm->50nm, 정확히 2.0배. aggregate_ratio=1.0을 이 배수로 정의했으므로
    (1+1.0)=2.0 배수가 d99 항에 곱해져야 한다 — d99는 변화 없이도 손상이 는다는
    것이 이 항의 핵심 계약이다.
    """
    f_ref = _factors(pack="sti_ceria")["delta"]
    f_agg = _factors(pack="sti_ceria", aggregate_ratio=1.0)["delta"]
    assert f_agg.terms["aggregate"] == pytest.approx(2.0, abs=1e-9)
    # d99 항은 안 건드렸으므로(같은 d99) 총 배수 = d99항(그대로) * 2.0
    assert f_agg.value == pytest.approx(f_ref.value * 2.0, rel=1e-9)
    # d99는 그대로인데(팩 오버라이드 안 함) 손상이 늘었다 -- 문헌의 핵심 발견 재현
    assert f_agg.terms["d99"] == pytest.approx(f_ref.terms["d99"], rel=1e-9)


def test_delta_excluded_from_mrr_multiplier():
    """Δ는 MRR_COUPLED가 아니다 — 손상 지표이지 제거율 배수가 아니다.

    실측(백테스트)이 지지하기 전까지는 MRR에 곱해 넣지 않는다(사용자 원칙:
    "MRR_COUPLED 편입은 held-out이 지지할 때만").
    """
    assert "delta" not in MRR_COUPLED
    mult_ref, _ = mrr_multiplier(_factors(pack="sti_ceria"))
    mult_big, _ = mrr_multiplier(_factors(pack="sti_ceria", abrasive_d99_nm=2500.0))
    assert mult_ref == pytest.approx(mult_big), (
        "Δ 변화가 MRR에 새어 들어갔다 -- delta는 MRR_COUPLED 밖에 있어야 한다.")


# ── Δ 종합 모델 (knowledge/cmp/delta-damage-model-synthesis.md, 2026-09-14) ──

_DELTA_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


@pytest.mark.parametrize("pack", _DELTA_PACKS)
def test_delta_synthesis_unity_and_modeled_in_all_five_packs(pack):
    """5팩 전부: 기준 조건 Δ=1.0 정확히, status가 unmodeled가 아니고, D99 항이 계상된다.

    D99 없는 팩은 D50×일반비(Levitronix 2008) 유도값이라 estimated로 남지만 모델링은 완결이다.
    w_fe_oxidizer는 유도 입력(D50 150→50 nm) 승격에 맞춰 D99·_ref 짝을 750→250으로 함께 옮겼다
    — 기준 1.0이 깨지지 않았음을 여기서 잠근다.
    """
    f = _factors(pack=pack)["delta"]
    assert f.status in ("modeled", "partial"), f.status
    assert f.value == pytest.approx(1.0, abs=1e-12), (pack, f.value)
    assert f.terms["d99"] == pytest.approx(1.0, abs=1e-12)
    assert "knowledge/cmp/delta-damage-model-synthesis.md" in f.sources


@pytest.mark.parametrize("pack", _DELTA_PACKS)
def test_delta_synthesis_monotone_in_d99_and_aggregation(pack):
    """D99↑ → Δ↑ (지수 n>0, 팩별 damage_exponent 정확 재현), 응집↑ → Δ↑ (1+a), 두 항은 곱셈 독립."""
    pk = Recipe(pack=pack).resolve().pack
    d0 = float(pk.get("abrasive_d99_nm")); n = float(pk.get("damage_exponent"))
    f_ref = _factors(pack=pack)["delta"]
    f_big = _factors(pack=pack, abrasive_d99_nm=2.0 * d0)["delta"]
    f_small = _factors(pack=pack, abrasive_d99_nm=0.5 * d0)["delta"]
    assert f_small.value < f_ref.value < f_big.value
    assert f_big.value == pytest.approx(2.0 ** n, rel=1e-9)
    assert f_small.value == pytest.approx(0.5 ** n, rel=1e-9)
    f_agg = _factors(pack=pack, aggregate_ratio=1.0)["delta"]          # Basim&Moudgil 0.2M NaCl 조건
    assert f_agg.value == pytest.approx(2.0, rel=1e-9)
    f_both = _factors(pack=pack, abrasive_d99_nm=2.0 * d0, aggregate_ratio=1.0)["delta"]
    assert f_both.value == pytest.approx(2.0 ** n * 2.0, rel=1e-9), "꼬리 항과 응집 항은 곱셈 독립"


def test_delta_synthesis_exponent_provenance_per_pack():
    """팩별 지수가 종합 노트 §3 표와 같다 — 세리아·실리카 1.44(Hitachi), 텅스텐·구리 2.54(Egan&Kim 기하평균)."""
    expect = {"sti_ceria": 1.44, "sic_ceria_h2o2": 1.44, "oxide_silica": 1.44,
              "w_fe_oxidizer": 2.54, "cu_h2o2_bta": 2.54}
    for pack, n in expect.items():
        pk = Recipe(pack=pack).resolve().pack
        assert float(pk.get("damage_exponent")) == pytest.approx(n)
        assert float(pk.get("abrasive_d99_nm")) == float(pk.get("abrasive_ref_d99_nm")), pack
    assert math.sqrt((math.log(60) / math.log(3)) * (math.log(1 / 0.15) / math.log(3))) == pytest.approx(2.54, abs=0.01)


def test_delta_synthesis_derived_d99_matches_d50_times_generic_ratio():
    """알루미나 2팩(cu_h2o2_bta/w_fe_oxidizer)의 D99=D50×5.00은 US7344988B2(DuPont, 알루미나
    CMP 1차 특허) 'more preferably <5x D50' 상한과 일치해 literature. oxide_silica는 같은
    일반비가 실리카 실측(US10894906B2, 비율 1.887)과 안 맞아 폐기하고 실측 절대값(287.5nm)을
    쓴다 — 세 팩 모두 [[abrasive-particle-size-distribution-d99-tail]] 근거로 literature."""
    for pack in ("cu_h2o2_bta", "w_fe_oxidizer"):
        pk = Recipe(pack=pack).resolve().pack
        assert float(pk.get("abrasive_d99_nm")) == pytest.approx(5.00 * float(pk.get("abrasive_size_nm"))), pack
        assert pk.param("abrasive_d99_nm").confidence == "literature", pack

    pk = Recipe(pack="oxide_silica").resolve().pack
    assert float(pk.get("abrasive_d99_nm")) == pytest.approx(287.5)
    assert pk.param("abrasive_d99_nm").confidence == "literature"


def test_delta_synthesis_diagnostics_do_not_touch_value_or_status():
    """③ 임계 위치·④ 치수 상한은 notes에만 나가고 value/terms/status/confidence는 불변.

    ④는 Eusner 2009 식(10)(11): 2a_max = D99·√(H_p,max/H_film). sti_ceria(D99 700, H_film 9 GPa,
    H_p,max 0.31 GPa) → 2a_max ≈ 130 nm, δ_max ≈ 12.1 nm (종합 노트 §5-E 재현값).
    """
    f = _factors(pack="sti_ceria")["delta"]
    diag = [n for n in f.notes if n.startswith("Δ 진단")]
    assert len(diag) == 2, f.notes
    assert "D99/d_c = 1.03" in diag[0] and "근처" in diag[0]
    assert "2a_max≈130 nm" in diag[1] and "δ_max≈12.1 nm" in diag[1]
    assert set(f.terms) == {"d99"} and f.value == 1.0
    g = _factors(pack="sti_ceria", scratch_threshold_nm=0.0)["delta"]     # 상수 없으면 그 줄만 빠진다
    assert len([n for n in g.notes if n.startswith("Δ 진단③")]) == 0
    assert g.value == f.value and g.status == f.status and g.confidence == f.confidence


def test_equipment_and_consumable_axes_do_not_mix():
    """장비 팩터의 driver 파트에 소모품이 섞이면 안 되고, 그 역도 안 된다.

    사용자 확정 규칙: "장비는 세가지 consumable과 묶이면 안된다."
    섞이면 "슬러리를 바꿀까 RPM을 올릴까"에 답할 수 없다 — 그 비교가 이 도구의
    존재 이유다.
    """
    consumable_parts = {"slurry", "pad", "disk"}
    for key, (sym, name, axis, parts) in FACTOR_SPEC.items():
        if axis == AXIS_EQUIPMENT:
            assert not (set(parts) & consumable_parts), (
                f"장비축 팩터 {sym} {name}의 파트에 소모품이 섞였다: {parts}")
        else:
            assert "tool" not in parts, (
                f"소모품축 팩터 {sym} {name}에 장비가 섞였다: {parts}")


def test_wafer_is_never_a_factor():
    """웨이퍼는 대상막질이지 조절 파라미터가 아니다 (사용자 확정)."""
    for key, (sym, name, axis, parts) in FACTOR_SPEC.items():
        assert "wafer" not in parts, (
            f"{sym} {name}이 웨이퍼를 driver로 삼는다 — 웨이퍼는 디폴트 대상값이라 "
            "파라미터에 포함시키면 안 된다.")


def test_equipment_factors_do_not_multiply_mrr_directly():
    """장비 팩터는 MRR 배수에 들어가지 않는다 — Preston이 이미 P·V를 쓴다.

    Λ을 또 곱하면 P·V가 제곱으로 들어간다.
    """
    for key in MRR_COUPLED:
        assert FACTOR_SPEC[key][2] == AXIS_CONSUMABLE, (
            f"{key}가 MRR에 곱해지는데 장비축이다 — Preston과 이중 계상된다.")


# ═══════════════════════════════ ⑤ 문헌 실측 재현

def test_ph_peak_reproduces_li2021_measurements():
    """Li et al. 2021 (doi:10.1149/2162-8777/ac3e44) Fig.1 재현.

        pH 10.0 → 1551 Å/min
        pH 11.0 → 1727 Å/min  (정점, +11.3%)
        pH 12.5 → 1407 Å/min  (−18.5% from peak)

    ⚠ 절대값이 아니라 **비율**을 검증한다. Kp는 다른 조건에서 역산됐으므로
    절대 MRR은 이 논문과 다르다 — 순위·비율만 비교 가능하다.
    """
    m10 = _mean_mrr(slurry_ph=10.0)
    m11 = _mean_mrr(slurry_ph=11.0)
    m125 = _mean_mrr(slurry_ph=12.5)

    assert m11 > m10 and m11 > m125, "pH 11.0이 정점이 아니다 — 정점형 거동 실패"
    assert m11 / m10 == pytest.approx(1727 / 1551, rel=0.02), (
        f"pH 10→11 상승비 {m11/m10:.4f}, 문헌 {1727/1551:.4f}")
    assert m125 / m10 == pytest.approx(1407 / 1551, rel=0.02), (
        f"pH 10→12.5 비 {m125/m10:.4f}, 문헌 {1407/1551:.4f}")


def test_ph_monotonic_model_would_have_failed():
    """단조 모델이었다면 pH 12.5를 과대평가했을 것 — 그걸 명시적으로 고정한다.

    이 테스트가 있는 이유: 누군가 '단순화'하려고 정점형을 단조로 되돌리면
    pH 12.5 예측이 정점보다 높아진다. 소재 개발자에게 **틀린 방향**을 가리키는
    것이라 부정확한 정도가 아니라 위험하다.
    """
    assert _mean_mrr(slurry_ph=12.5) < _mean_mrr(slurry_ph=11.0), (
        "pH 12.5가 정점(11.0)보다 높다 — 단조 모델로 퇴행했다.")


def test_pad_hardness_follows_h_minus_1_5():
    """MRR ∝ H^-1.5 (knowledge/cmp/particle-wafer-interaction... §4, verify PASS)."""
    h0, h1 = 60.0, 66.0
    m0 = _mean_mrr(pad_hardness_shore_d=h0)
    m1 = _mean_mrr(pad_hardness_shore_d=h1)
    assert m1 / m0 == pytest.approx((h1 / h0) ** -1.5, rel=1e-6)


# ═══════════════════════════════ 커버리지 정직성

def test_coverage_counts_only_real_connections():
    cov = coverage(_factors())
    assert cov["total"] == len(FACTOR_SPEC)
    assert set(cov["modeled"]) & set(cov["unmodeled"]) == set()
    # 미모델링 축이 남아 있다는 사실 자체가 보고돼야 한다 — 100%를 가장하지 않는다
    assert cov["score"] < 1.0, (
        "커버리지가 100%로 나온다 — τ·S 등 미연결 축이 있는데 숨기고 있다.")


def test_every_factor_declares_drivers_or_explains_absence():
    """모든 팩터는 자기 driver를 신고하거나, 없는 이유를 notes에 남긴다.

    이게 있어야 "κ를 올리려면 무엇을 만지나"에 기계가 답한다.
    """
    for key, f in _factors().items():
        if not f.drivers:
            assert f.notes, f"{f.symbol} {f.name}이 driver도 설명도 없다"


def test_factor_result_is_json_serializable():
    """UI(API)가 그대로 실어 보낼 수 있어야 한다."""
    import json
    res = simulate(Recipe(pack="oxide_silica"))
    s = json.dumps(res.summary()["factors"], ensure_ascii=False)
    assert "kappa" in s and "symbol" in s



# ═══════════════════════════════ psi(표면 보호도) — w_fe_oxidizer 억제제 배선 (2026-09-10)
# 정확도 루프 UNMODELED 갭 해결: knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-
# dissolution-suppression.md (Lee & Seo 2022, DOI:10.3390/app12031227) 근거.

def test_psi_is_modeled_for_w_fe_oxidizer():
    """w_fe_oxidizer는 이제 억제제 파라미터가 있어 psi가 partial/dead가 아니라 modeled여야 한다."""
    f = _factors(pack="w_fe_oxidizer")["psi"]
    assert f.status == "modeled", (
        f"w_fe_oxidizer의 psi가 {f.status}다 — inhibitor_mM/K/strength_k 배선이 깨졌다.")


def test_psi_is_unity_at_reference_for_w_fe_oxidizer():
    """기준 농도(inhibitor_mM == inhibitor_ref_mM)에서 psi=1.0 (이중 계상 방지 계약)."""
    f = _factors(pack="w_fe_oxidizer")["psi"]
    assert f.value == pytest.approx(1.0, abs=1e-9)


def test_lower_inhibitor_raises_w_mrr():
    """억제제(피콜린산) 농도를 낮추면 W CMP 제거율이 올라가야 한다.

    문헌(Lee & Seo 2022, Fig.4): 0->1.5 wt%로 억제제를 늘리면 제거율이 120->85 A/min로
    떨어진다(1.41배 감소) — 역방향인 억제제 감소는 제거율 증가를 뜻해야 한다.
    """
    high_inhib = _mean_mrr(pack="w_fe_oxidizer")          # 기준(포화 농도 121.8 mM)
    low_inhib = _mean_mrr(pack="w_fe_oxidizer", inhibitor_mM=10.0)
    assert low_inhib > high_inhib, (
        f"억제제를 낮췄는데 MRR이 안 올랐다: 기준 {high_inhib:.1f} vs 저농도 {low_inhib:.1f} nm/min")


def test_theta_reference_is_unity_with_coolant_temp_driver():
    """냉각수온도 항 추가 후에도 기준 조건(platen_coolant_temp_c==platen_coolant_ref_c)에서 Θ=1.0.

    knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md — Θ=heat/cool 이중계상
    방지 계약. sfr, coolant_temp 모두 기준값일 때 곱 1.0이어야 한다.
    """
    f = _factors(pack="oxide_silica")["theta"]
    assert f.value == pytest.approx(1.0, abs=1e-6), f"기준 Θ={f.value} != 1.0"
    assert "cool(coolant_temp)" in f.terms


def test_theta_colder_coolant_lowers_load():
    """냉각수를 더 차게(값을 낮게) 하면 냉각여유가 커져 Θ(부하비)가 낮아져야 한다.

    Yuh 2015(doi:10.1007/s40684-015-0041-8) 방향: 냉각수온도 10->30C에서 MRR_avg 단조증가
    == 냉각을 강화(온도를 낮춤)하면 열부하가 준다는 것과 같은 방향.
    """
    f_ref = _factors(pack="oxide_silica")["theta"]
    f_cold = _factors(pack="oxide_silica", platen_coolant_temp_c=26.5)["theta"]
    assert f_cold.value < f_ref.value, (
        f"냉각수 26.5C가 기준 30C보다 Θ가 낮아야 한다: {f_cold.value} vs {f_ref.value}")


def test_theta_hotter_coolant_raises_load():
    """냉각수를 덥게 하면(열원에 근접) 냉각여유가 줄어 Θ가 높아져야 한다."""
    f_ref = _factors(pack="oxide_silica")["theta"]
    f_hot = _factors(pack="oxide_silica", platen_coolant_temp_c=35.0)["theta"]
    assert f_hot.value > f_ref.value, (
        f"냉각수 35C가 기준 30C보다 Θ가 높아야 한다: {f_hot.value} vs {f_ref.value}")


def test_theta_rotation_cooling_present_at_reference():
    """회전 대류냉각 항 추가 후에도 기준 rpm_platen(=lambda_ref_rpm_platen)에서 Θ=1.0 유지.

    knowledge/physics/cmp-theta-rotation-convective-cooling-driver.md — von Karman
    회전원판 냉각 채널을 추가해도 기준점 1.0 계약은 깨지지 않아야 한다.
    """
    f = _factors(pack="oxide_silica")["theta"]
    assert f.value == pytest.approx(1.0, abs=1e-6), f"기준 Θ={f.value} != 1.0"
    assert "cool(rotation)" in f.terms


def test_theta_faster_rotation_moderates_but_not_cancels_load():
    """rpm_platen을 올리면 발열(Λ, 선형)과 냉각(rotation, 제곱근)이 함께 커지지만,

    발열이 냉각보다 빠르게 늘어 순net Θ는 여전히 증가해야 한다(von Karman 지수 b=0.5 <
    Λ의 V 선형 지수 1.0 — knowledge/physics/cmp-theta-rotation-convective-cooling-driver.md §2).
    단, rpm_platen만 올린 단순 배율보다는 완화되어 있어야 한다(회전냉각이 일부 상쇄).
    """
    f_ref = _factors(pack="oxide_silica")["theta"]
    f_fast = _factors(pack="oxide_silica", rpm_platen=110.0)["theta"]
    assert f_fast.value > f_ref.value, (
        f"회전수를 올렸는데 Θ가 안 올랐다: {f_fast.value} vs {f_ref.value}")
    # 회전냉각 항이 없다면 Λ만 2배가 되어 Θ도 정확히 2배가 됐을 것 — 실제로는 sqrt(2)로 나눠 완화됨
    naive_double = f_ref.value * 2.0
    assert f_fast.value < naive_double, (
        f"회전 대류냉각이 반영 안 됨 — Θ가 순수 2배({naive_double})만큼 올랐다: {f_fast.value}")


def test_theta_rotation_cooling_channel_is_weighted_not_full_sqrt():
    """cool_rotation은 전체 냉각의 7%(공기 채널)만 √Ω로 스케일해야 한다.

    2026-09-13 정정: 과거에는 cool_rotation=sqrt(rpm/rpm_ref) 하나로 냉각 전체를
    스케일했다. 그러나 frictional-heating-temperature-arrhenius-coupling.md §8.4
    (White 2003 + Shin 2025 정상상태 열저항 네트워크)에 따르면 회전 대류냉각(G_air)은
    전체 냉각 컨덕턴스의 약 7%만 차지하고(슬러리 74%/패드 19%/공기 7%, 중앙 케이스),
    나머지는 회전수와 무관하다. rpm_platen이 기준(55) 대비 2배(110)가 되면
    cool_rotation은 sqrt(2)≈1.414가 아니라 0.93*1.0+0.07*sqrt(2)≈1.029에 가까워야 한다
    — 회전 냉각 효과의 과대평가를 없애는 정정이다.
    """
    f_fast = _factors(pack="oxide_silica", rpm_platen=110.0)["theta"]
    cool_rotation = f_fast.terms["cool(rotation)"]
    expected = 0.93 * 1.0 + 0.07 * math.sqrt(2.0)
    assert cool_rotation == pytest.approx(expected, abs=1e-6), (
        f"cool_rotation={cool_rotation}이 가중평균 근사치 {expected}와 다르다 — "
        f"√Ω가 냉각 전체에 그대로 적용되고 있을 가능성(과대평가 회귀).")
    assert cool_rotation < math.sqrt(2.0), (
        "cool_rotation이 여전히 순수 sqrt(rpm 비)와 같다 — w_air 가중치가 반영 안 됨.")


def test_theta_retaining_ring_present_at_reference():
    """리테이닝 링 압력 채널 추가 후에도 기준(5 psi)에서 Θ=1.0 유지.

    knowledge/physics/cmp-theta-retaining-ring-pressure-heat-channel.md — Lee/Guo/Jeong 2012
    Table 1(총마찰력 선형회귀 R²>0.99)을 근거로 한 새 발열 채널이 기준점 계약을 깨지 않아야 한다.
    """
    f = _factors(pack="oxide_silica")["theta"]
    assert f.value == pytest.approx(1.0, abs=1e-6), f"기준 Θ={f.value} != 1.0"
    assert "heat(ring)" in f.terms


def test_theta_higher_retaining_ring_pressure_raises_load():
    """리테이닝 링 압력을 올리면 링-패드 마찰열이 늘어 Θ가 높아져야 한다.

    Lee/Guo/Jeong 2012 Table 1: RR압력 2->6psi에서 총 마찰력(F_wafer+F_ring) 단조증가
    (308.6N -> 432.4N, 1.40배).
    """
    f_ref = _factors(pack="oxide_silica")["theta"]
    f_high = _factors(pack="oxide_silica", retaining_ring_pressure_psi=6.0)["theta"]
    assert f_high.value > f_ref.value, (
        f"RR압력 6psi가 기준 5psi보다 Θ가 높아야 한다: {f_high.value} vs {f_ref.value}")


def test_theta_lower_retaining_ring_pressure_lowers_load():
    """리테이닝 링 압력을 내리면 Θ가 낮아져야 한다(Table 1 2psi 조건)."""
    f_ref = _factors(pack="oxide_silica")["theta"]
    f_low = _factors(pack="oxide_silica", retaining_ring_pressure_psi=2.0)["theta"]
    assert f_low.value < f_ref.value, (
        f"RR압력 2psi가 기준 5psi보다 Θ가 낮아야 한다: {f_low.value} vs {f_ref.value}")


# ═══════════════════ 세리아 입경 정점 — 교차계 오전이 회귀 방지 ═══════════════════
# 근거: knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.md
# 배경: 세리아 팩(sti_ceria·sic_ceria_h2o2)이 base=oxide_silica 상속으로 **실리카**
#       슬러리의 입경 정점(80nm)을 조용히 물려받아, 세리아 문헌(60~163nm 구간 증가)과
#       반대 방향을 예측하고 있었다. 기준조건 κ는 1.0이라 백테스트 ρ로는 안 잡힌다.

CERIA_PACKS = ("sti_ceria", "sic_ceria_h2o2")


@pytest.mark.parametrize("pack", CERIA_PACKS)
def test_ceria_size_peak_is_declared_not_inherited(pack):
    """세리아 팩은 입경 3파라미터를 **자기 값으로** 가져야 한다(상속 금지).

    값이 부모와 같더라도 상속이면 안 된다 — 부모(실리카)가 바뀔 때 세리아가
    조용히 끌려가는 경로가 이 결함의 원인이었다.
    """
    from sim.params import load_pack
    pk = load_pack(pack)
    for key in ("abrasive_size_peak_nm",
                "abrasive_size_exp_below_peak",
                "abrasive_size_exp_above_peak"):
        assert pk.has_own(key), (
            f"{pack}.{key} 가 상속 상태다 — 실리카(oxide_silica) 값이 세리아 팩에 "
            f"다시 새어든다. knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.md §1")


@pytest.mark.parametrize("pack", CERIA_PACKS)
def test_ceria_size_peak_matches_ceria_literature(pack):
    """정점은 세리아 실측(Oh et al. 2010, doi:10.1016/j.mee.2010.07.040)의 163nm."""
    from sim.params import load_pack
    assert float(load_pack(pack).get("abrasive_size_peak_nm")) == pytest.approx(163.0)


@pytest.mark.parametrize("pack", CERIA_PACKS)
def test_ceria_mrr_rises_with_size_up_to_peak(pack):
    """세리아 계 문헌 방향: 60 -> 120 -> 163 nm 구간에서 MRR이 단조 증가해야 한다.

    Oh 2010(62/116/163/232nm, 163 최대) · Oh 2011 Powder Tech(84~417nm 단조증가) ·
    Kang 2004 JJAP(입경↑ -> oxide RR↑) 세 편이 같은 방향을 준다. 구 설정(정점 80nm)
    에서는 120->163 이 **감소**했다 — 그 회귀를 막는다.
    """
    m60 = _mean_mrr(pack=pack, abrasive_size_nm=60.0)
    m120 = _mean_mrr(pack=pack, abrasive_size_nm=120.0)
    m163 = _mean_mrr(pack=pack, abrasive_size_nm=163.0)
    assert m60 < m120 < m163, (
        f"{pack}: 세리아 입경 증가 구간에서 MRR이 증가해야 한다 "
        f"(60nm={m60:.1f}, 120nm={m120:.1f}, 163nm={m163:.1f})")


@pytest.mark.parametrize("pack", CERIA_PACKS)
def test_ceria_size_term_is_unity_at_reference(pack):
    """기준 조건(팩 본값 = 기준점)에서 κ 입경항은 정확히 1.0 — 이중 계상 금지."""
    from sim.params import load_pack
    pk = load_pack(pack)
    f = compute_factors(Recipe(pack=pack).resolve())["kappa"]
    assert float(pk.get("abrasive_size_nm")) == pytest.approx(
        float(pk.get("abrasive_ref_size_nm"))), f"{pack}: 본값과 기준점이 어긋났다"
    assert f.terms.get("size") == pytest.approx(1.0), (
        f"{pack}: 기준조건 입경항이 1.0이 아니다 ({f.terms.get('size')}) — Kp에 이중 계상된다")


def test_silica_pack_keeps_its_own_peak():
    """실리카 팩의 정점은 80nm 그대로여야 한다 — 세리아 수정이 부모를 오염시키면 안 된다."""
    from sim.params import load_pack
    assert float(load_pack("oxide_silica").get("abrasive_size_peak_nm")) == pytest.approx(80.0)



# ═══════════════════════════════ psi(표면 흡착 보호) — 산화막 계 3팩 농도축 (2026-09-14)
# 근거: knowledge/cmp/psi-adsorption-shield-oxide-systems.md,
#       knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md (Park 2003 JJAP Fig.3)

OXIDE_PSI_PACKS = ["oxide_silica", "sti_ceria", "sic_ceria_h2o2"]


@pytest.mark.parametrize("pack", OXIDE_PSI_PACKS)
def test_psi_oxide_packs_are_unity_at_reference(pack):
    """기준 농도(shield_additive_wt_pct == shield_ref_wt_pct)에서 ψ는 정확히 1.0."""
    from sim.params import load_pack
    pk = load_pack(pack)
    assert float(pk.get("shield_additive_wt_pct")) == pytest.approx(
        float(pk.get("shield_ref_wt_pct"))), f"{pack}: 본값과 기준점이 어긋났다"
    f = _factors(pack=pack)["psi"]
    assert f.value == pytest.approx(1.0, abs=1e-12), f"{pack}: ψ={f.value}"
    assert f.status in ("modeled", "partial")


def test_psi_sti_ceria_surfactant_suppresses_monotonically():
    """sti_ceria: 음이온 계면활성제 ↑ → ψ ↓ 엄격 단조 (Park 2003 Fig.3(a) 방향).

    0.8 wt%에서 산화막 RR이 무첨가의 1/5 (원문 텍스트 정박점) — 배수 0.20 ± 0.01.
    """
    f = _factors(pack="sti_ceria")["psi"]
    assert f.status == "modeled" and "adsorption_shield" in f.terms
    vals = [_factors(pack="sti_ceria", shield_additive_wt_pct=C)["psi"].value
            for C in (0.0, 0.08, 0.2, 0.4, 0.8, 1.6)]
    assert all(a > b for a, b in zip(vals, vals[1:])), vals
    assert vals[4] == pytest.approx(0.20, abs=0.01), vals[4]
    # MRR 결합 확인 — 팩터가 살아 있어도 엔진에 안 곱히면 dead 다.
    assert _mean_mrr(pack="sti_ceria", shield_additive_wt_pct=0.8) < \
        0.3 * _mean_mrr(pack="sti_ceria")


def test_psi_sti_ceria_nitride_stops_before_oxide():
    """STI 선택비의 기원: 질화막 K(14.02)가 산화막 K(1.29)의 ~11배 → 질화막이 먼저 정지."""
    from sim.params import load_pack
    pk = load_pack("sti_ceria")
    assert pk.has_own("shield_langmuir_K") and pk.has_own("shield_nitride_langmuir_K")
    ratio = float(pk.get("shield_nitride_langmuir_K")) / float(pk.get("shield_langmuir_K"))
    assert 10.0 < ratio < 12.0, ratio
    f = _factors(pack="sti_ceria", shield_additive_wt_pct=0.1)["psi"]
    assert f.value > 0.99                      # 산화막은 아직 온전
    assert any("선택비" in n for n in f.notes)  # 질화막 진단이 나온다


def test_psi_oxide_silica_is_verified_null():
    """oxide_silica: 음이온 계면활성제/PEG는 산화막에 흡착하지 않는다(Penta 2013 §4.5,
    US10526508B2 Table 2) — K=0 이므로 어떤 농도에서도 정확히 1.0. 단, 항은 계상돼야
    한다('모름'이 아니라 '효과 없음')."""
    f = _factors(pack="oxide_silica")["psi"]
    assert "adsorption_shield" in f.terms and f.status == "modeled"
    assert f.confidence in ("literature", "measured", "verified")
    for C in (0.5, 1.4, 5.0):
        assert _factors(pack="oxide_silica", shield_additive_wt_pct=C)["psi"].value == 1.0
    assert any("검증된 영" in n for n in f.notes)


def test_psi_sic_pack_does_not_inherit_surfactant_constant():
    """sic_ceria_h2o2: SiC 위 첨가제 문헌이 없다. 부모 K를 상속해 쓰면 남의 재료 숫자다 —
    항을 만들지 않고 partial + 사유. 농도를 올려도 결과 불변이어야 한다."""
    from sim.params import load_pack
    pk = load_pack("sic_ceria_h2o2")
    assert not pk.has_own("shield_langmuir_K")
    f = _factors(pack="sic_ceria_h2o2")["psi"]
    assert f.status == "partial" and "adsorption_shield" not in f.terms
    assert any("자기선언이 아니다" in n for n in f.notes)
    assert _factors(pack="sic_ceria_h2o2", shield_additive_wt_pct=0.5)["psi"].value == 1.0


@pytest.mark.parametrize("pack", ["cu_h2o2_bta", "w_fe_oxidizer"])
def test_psi_metal_packs_unchanged_by_oxide_extension(pack):
    """금속 팩은 산화막 확장(adsorption_shield) 경로를 타지 않고, 기준에서 1.0.

    [2026-09-19 판정#72] 허용 term 집합에 `chelator_suppression` 을 추가했다.
    이름의 "oxide_extension"이 가리키는 것은 세리아/산화막용 `adsorption_shield`
    경로이며, 착화제 억제는 금속계 고유의 ψ 갈래다(글리신 → Cu 표면 흡착 보호,
    근거: knowledge/cmp/psi-glycine-chelator-suppression-cu-jani2025.md).
    금속 팩이 절대 가져서는 안 되는 것은 산화막 경로이므로 그것을 직접 금지한다 —
    "term 이 하나여야 한다"는 원래 의도의 대리 조건이었을 뿐이다.
    기준 조건 1.0 계약은 그대로 유지된다(각 항이 개별로 항등원).
    """
    f = _factors(pack=pack)["psi"]
    assert set(f.terms) <= {"inhibitor", "chelator_suppression"}
    assert "inhibitor" in f.terms
    assert "adsorption_shield" not in f.terms
    assert f.value == pytest.approx(1.0, abs=1e-9)
    assert "shield_additive_wt_pct" not in f.drivers


# ═══════════════════════════════ χ 세리아 chemical tooth 지수 (판정#23)

@pytest.mark.parametrize("pack", ["sti_ceria", "sic_ceria_h2o2"])
def test_chi_ceria_tooth_reference_is_unity_regardless_of_exponent(pack):
    """기준 조건(ce3_fraction == ce3_fraction_ref)에서는 지수와 무관하게 정확히 1.0.

    (θ/θ_ref)^p 는 θ=θ_ref 에서 어떤 p 에 대해서도 1 이므로 이중계상이 생기지 않는다.
    이 계약이 깨지면 Kp 가 이미 흡수한 화학 효과를 두 번 세게 된다.
    """
    from sim.params import load_pack
    from sim.chemistry import _ceria_term
    pk = load_pack(pack)
    assert pk.get("ceria_tooth_exponent") != 1.0, "지수가 선언돼 있어야 이 테스트가 의미 있다"
    assert _ceria_term(pk, []) == pytest.approx(1.0, abs=1e-12)


def test_chi_ceria_tooth_exponent_reproduces_netzband_pair():
    """Netzband 쌍 재현: θ 12.55%→25.71% 일 때 MRR 비 2.75배 (문헌 S2 본문).

    근거: knowledge/cmp/ceria-tooth-ce3-mrr-exponent-netzband-pair.md §4
      - Netzband & Dunn 2019 (doi:10.1149/2.0311910jss) Fig.4+Table I → θ
      - Netzband & Dunn 2020 (doi:10.1149/2162-8777/ab8393) 본문 → MRR 2.0배/5.5배
    선형(p=1)은 이 비를 구조적으로 만들 수 없다(상한 = θ 비 2.05배)는 점도 함께 고정한다.
    """
    from sim.params import load_pack
    from sim.chemistry import _ceria_term
    LIT_MRR_RATIO = 5.5 / 2.0   # = 2.75, 같은 슬러리 내부 비 (상용 기준 약분)

    def tooth(theta, exponent=None):
        pk = load_pack("sti_ceria")
        pk.params["ce3_fraction"].value = theta
        if exponent is not None:
            pk.params["ceria_tooth_exponent"].value = exponent
        return _ceria_term(pk, [])

    ratio = tooth(0.2571) / tooth(0.1255)
    assert ratio == pytest.approx(LIT_MRR_RATIO, rel=0.01), ratio

    # 선형이면 문헌 비를 못 만든다 — 함수형 문제였지 gain 튜닝 문제가 아니다.
    linear = tooth(0.2571, exponent=1.0) / tooth(0.1255, exponent=1.0)
    assert linear < LIT_MRR_RATIO
    assert linear == pytest.approx(1.829, rel=0.01), linear


def test_chi_ceria_tooth_defaults_to_linear_when_pack_is_silent():
    """지수를 선언하지 않은 팩은 p=1.0 (기존 동작) — 하위호환 계약."""
    from sim.params import load_pack
    from sim.chemistry import _ceria_term
    pk = load_pack("sti_ceria")
    del pk.params["ceria_tooth_exponent"]
    pk.params["ce3_fraction"].value = 0.30
    notes = []
    v = _ceria_term(pk, notes)
    floor = 1.0 / 5.5
    assert v == pytest.approx(floor + (1 - floor) * (0.30 / 0.15), rel=1e-9)
    assert any("선형(p=1)" in n for n in notes)


# ─────────────────────────────────────────────────────────────────────────────
# W 산성역 pH 항 (2026-09-15, χ PARTIAL 해소)
# 근거: knowledge/cmp/w-cmp-ph-acidic-oxidizer-mediated-stojadinovic.md
#       Stojadinović, Bouvet, Mischler (2016) doi:10.1007/s40735-016-0041-4 Table 1
# ─────────────────────────────────────────────────────────────────────────────

def test_chi_w_ph_term_is_unity_at_pack_reference():
    """기준조건 1.0 계약 — 깨지면 Kp 와 이중 계상이다."""
    from sim.params import load_pack
    from sim.factors import _ph_w_acidic_term
    pk = load_pack("w_fe_oxidizer")
    assert _ph_w_acidic_term(pk, []) == pytest.approx(1.0, abs=1e-12)


def test_chi_w_ph_term_reproduces_stojadinovic_ratio():
    """pH 5→2 에서 문헌 비(로그평균 1.417배)를 재현한다."""
    import math
    from sim.params import load_pack
    from sim.factors import _ph_w_acidic_term

    def f(ph):
        pk = load_pack("w_fe_oxidizer")
        pk.params["slurry_ph"].value = ph
        return _ph_w_acidic_term(pk, [])

    # Table 1 산화제 존재 3조건 비
    lit = [200 / 140, 1150 / 750, 1950 / 1500]
    lit_geo = math.exp(sum(math.log(r) for r in lit) / 3)
    assert f(2.0) / f(5.0) == pytest.approx(lit_geo, rel=0.01)
    # 개별 조건과는 ±10% 이내로만 맞는다 — 완벽하지 않음을 그대로 고정
    for r in lit:
        assert abs(f(2.0) / f(5.0) - r) / r < 0.10


def test_chi_w_ph_term_direction_and_extrapolation_warning():
    """산성일수록 빠르다 + 근거구간(2~5) 밖이면 경고를 남긴다."""
    from sim.params import load_pack
    from sim.factors import _ph_w_acidic_term

    def f(ph, notes=None):
        pk = load_pack("w_fe_oxidizer")
        pk.params["slurry_ph"].value = ph
        return _ph_w_acidic_term(pk, notes if notes is not None else [])

    assert f(2.0) > f(2.5) > f(4.0) > f(5.0)
    notes = []
    f(9.0, notes)
    assert any("외삽" in n for n in notes)
    notes2 = []
    f(3.0, notes2)
    assert not any("외삽" in n for n in notes2)


def test_chi_w_ph_term_gated_on_pack_declaration():
    """`w_ph_acid_k` 를 선언하지 않은 팩에서는 항이 꺼진다 (산화제 없는 W 계 보호)."""
    from sim.params import load_pack
    from sim.factors import _ph_w_acidic_term
    pk = load_pack("w_fe_oxidizer")
    del pk.params["w_ph_acid_k"]
    assert _ph_w_acidic_term(pk, []) is None
    # 다른 막질 팩도 이 항을 잘못 주워가지 않는다
    assert _ph_w_acidic_term(load_pack("oxide_silica"), []) is None
    assert _ph_w_acidic_term(load_pack("sti_ceria"), []) is None


def test_chi_w_pack_is_now_fully_modeled():
    """w_fe_oxidizer 의 χ 가 partial → modeled 로 올라갔고, 기준조건 값은 1.0 이다."""
    from sim.params import load_pack
    from sim.engine import Recipe, ResolvedRecipe
    from sim.factors import _f_chi
    pk = load_pack("w_fe_oxidizer")
    rr = ResolvedRecipe(base=Recipe(), pack=pk, used_keys=[], film="w",
                        wafer_radius_m=0.15, pressure_psi=3.0, rpm_wafer=60,
                        rpm_platen=60, center_offset_m=0.12,
                        kp_m_per_pa=float(pk.get("kp_m_per_pa")),
                        n_points=81, edge_exclusion_m=0.003)
    f = _f_chi(rr)
    assert f.status == "modeled", f.status
    assert "ph_w_acidic" in f.terms
    assert f.value == pytest.approx(1.0, abs=1e-9)


# ═══════════════════════════════ χ 산화제축 — sic_ceria_h2o2 배선 (2026-09-16)
# 근거 노트: knowledge/cmp/sic-h2o2-oxidizer-saturation-alkaline-ceria.md

def test_chi_oxidizer_axis_is_alive_for_sic_ceria_h2o2():
    """H2O2 농도를 바꾸면 MRR이 실제로 움직여야 한다.

    2026-09-16 이전에는 oxidizer_wt_pct/_ref는 있는데 형상 파라미터가 없어
    χ가 산화제 변화에 **조용히 무반응**이었다(죽은 축). 배선이 풀리면 이 테스트가 잡는다.
    """
    lo = _mean_mrr(pack="sic_ceria_h2o2", oxidizer_wt_pct=2.0)
    mid = _mean_mrr(pack="sic_ceria_h2o2", oxidizer_wt_pct=4.0)
    hi = _mean_mrr(pack="sic_ceria_h2o2", oxidizer_wt_pct=6.0)
    assert lo < mid < hi, (
        f"H2O2 2/4/6 vol%에서 MRR이 단조 증가하지 않는다: {lo:.4f}/{mid:.4f}/{hi:.4f} "
        "— 촉진-포화형(Langmuir) 배선이 깨졌다.")


def test_chi_oxidizer_reference_unity_for_sic_ceria_h2o2():
    """기준 조성(H2O2 4 vol%)에서 χ는 정확히 1.0 — Kp 이중 계상 방지."""
    f = _factors(pack="sic_ceria_h2o2")["chi"]
    assert f.value == pytest.approx(1.0, abs=1e-9), (
        f"기준 조건 χ가 {f.value}다 — oxidizer_wt_pct와 oxidizer_ref_wt_pct가 "
        "어긋났거나 단위가 섞였다(vol% vs wt%).")


def test_oxidizer_shape_is_not_transferred_across_oxidizer_species():
    """산화제 종이 다른 팩은 **부모의** Langmuir 곡선을 상속하지 않는다.

    부모(sic_ceria_h2o2)의 K 는 H2O2 데이터로 적합됐고 sic_alumina_kmno4 는
    KMnO4(E°(MnO4-/MnO2)=+1.68 V)를 쓴다. 종 게이트가 꺼져 있으면 남의 산화제로
    적합한 곡선으로 이 팩의 MRR 을 예측하게 된다 — 그건 지어낸 값이다.

    ⚠ 2026-09-19 갱신: 이 테스트는 원래 "sic_alumina_kmno4 는 산화제에 반응하지
    않는다"를 고정했다. 그 무반응은 **목표가 아니라 증상**이었다 — 자기 종의 K 가
    없어서 게이트가 막고 있던 상태다. 그 뒤 이 팩이 Gong 2024(자기 재료계 문헌)로
    `oxidizer_langmuir_K` + `oxidizer_langmuir_species=KMnO4` 를 **자기선언**해
    게이트를 정당하게 통과했다. 무반응을 계약으로 고정하면 게이트를 통과하는 정상
    경로까지 막히므로, 고정할 계약을 원래 의도대로 다시 쓴다: **종이 일치할 때만
    항이 선다.**
    """
    from sim.params import load_pack

    pk = load_pack("sic_alumina_kmno4")
    # 전제: 이 팩은 자기 종의 K 를 자기선언했다(상속이 아니다)
    assert pk.has_own("oxidizer_langmuir_K"), (
        "K 가 상속 상태다 — 그렇다면 종 게이트가 막아야 하고 아래 반응은 결함이다.")
    assert pk.has_own("oxidizer_langmuir_species")
    assert str(pk.get("oxidizer_langmuir_species")) == str(pk.get("oxidizer")), (
        "적합된 산화제 종과 팩의 실제 산화제가 다르다 — 종 게이트가 막아야 한다.")

    # 종이 일치하므로 항이 서고 농도에 단조 반응한다
    vals = [_mean_mrr(pack="sic_alumina_kmno4", oxidizer_wt_pct=c)
            for c in (2.0, 4.0, 6.0)]
    assert vals[0] < vals[1] < vals[2], (
        f"자기 종 K 를 선언했는데도 KMnO4 농도에 무반응이다({vals}) — 종 게이트가 "
        "일치하는 종까지 막고 있다.")

    # 그리고 그 곡선은 부모(H2O2)의 것이 아니다
    parent = load_pack("sic_ceria_h2o2")
    assert float(pk.get("oxidizer_langmuir_K")) != pytest.approx(
        float(parent.get("oxidizer_langmuir_K")), rel=1e-9), (
        "이 팩의 K 가 부모(H2O2 적합값)와 같다 — 종이 다른데 곡선을 물려받았다.")


def test_sic_kmno4_ph_floor_scales_with_oxidizer_concentration():
    """판정#64 — pH 평탄부(기계 하한 φ)는 산화제 농도에 따라 올라간다.

    두 실측 앵커가 서로 다른 φ 를 준다:
      · Chen 2020 (0.05 M ≈ 0.79 wt% KMnO4) — pH 2→10 에서 3.56배 감소 (φ=0.268)
      · Wang 2021 (6.5 wt% KMnO4)           — pH 2→12 에서 1.4→1.1 µm/h (φ=0.785)
    진한 산화제에서는 알칼리 쪽 산화가 덜 꺼지므로 감쇠가 얕아야 한다.
    이 계약이 깨지면 두 문헌 중 하나를 버린 것이다.
    """
    lo = _mean_mrr(pack="sic_alumina_kmno4", oxidizer_wt_pct=0.79, slurry_ph=10.0)
    hi = _mean_mrr(pack="sic_alumina_kmno4", oxidizer_wt_pct=6.5, slurry_ph=10.0)
    ref_lo = _mean_mrr(pack="sic_alumina_kmno4", oxidizer_wt_pct=0.79)
    ref_hi = _mean_mrr(pack="sic_alumina_kmno4", oxidizer_wt_pct=6.5)
    drop_lo, drop_hi = lo / ref_lo, hi / ref_hi
    assert drop_hi > drop_lo, (
        f"진한 산화제(6.5 wt%)의 pH 10 감쇠({drop_hi:.3f})가 묽은 쪽"
        f"({drop_lo:.3f})보다 깊다 — φ 농도 보간의 부호가 뒤집혔다.")
    # Chen 2020 저농도 앵커 재현: pH 2→10 에서 약 3.56배 감소 (φ=0.268)
    a = _mean_mrr(pack="sic_alumina_kmno4", oxidizer_wt_pct=0.79, slurry_ph=2.0)
    assert a / lo == pytest.approx(3.56, rel=0.03), a / lo


def test_sic_kmno4_ph_floor_reference_unity_unaffected_by_oxidizer():
    """φ 를 농도로 흔들어도 **기준 pH 에서 pH 항은** 정확히 1.0 이다.

    φ 는 g(pH)/g(pH_ref) 의 분자·분모에 동시에 들어가므로 pH=pH_ref 에서
    상쇄된다. 이 계약이 깨지면 Kp 가 이중 계상된다.

    ⚠ 2026-09-19 갱신: 원래 이 테스트는 χ **전체**가 1.0 이라고 단언했다. 그것이
    성립했던 이유는 당시 이 팩의 산화제 항이 종 게이트에 막혀 꺼져 있어서지,
    pH 항의 계약 때문이 아니었다. 이 팩이 자기 종의 K 를 선언해 산화제 항이
    켜지자 χ 전체는 농도에 따라 움직인다(그게 정상이다 — C≠C_ref 에서 1.0 이면
    오히려 산화제축이 죽은 것이다). 고정할 계약은 **pH 항 단독의 기준 단위성**
    이므로 그렇게 좁힌다.
    """
    for c in (0.79, 4.0, 6.5):
        f = _factors(pack="sic_alumina_kmno4", oxidizer_wt_pct=c)["chi"]
        ph_terms = [v for k, v in f.terms.items() if k.startswith("ph_")]
        assert ph_terms, (c, f.terms, "pH 항이 사라졌다")
        for v in ph_terms:
            assert v == pytest.approx(1.0, abs=1e-9), (c, f.terms)

    # 그리고 기준 농도·기준 pH 에서는 χ 전체가 정확히 1.0 이다(Kp 이중 계상 방지)
    ref = _factors(pack="sic_alumina_kmno4")["chi"]
    assert ref.value == pytest.approx(1.0, abs=1e-9), ref.terms

    # 산화제 항은 기준 농도를 벗어나면 반드시 움직인다(죽은 축 회귀 방지)
    off = _factors(pack="sic_alumina_kmno4", oxidizer_wt_pct=0.79)["chi"]
    assert off.value != pytest.approx(1.0, abs=1e-6), (
        "기준을 벗어난 농도에서도 χ 가 1.0 이다 — 산화제축이 다시 죽었다.")


# ═══════════════ χ 카복실레이트 촉진축 (판정#75, US6309560B1)

def test_chi_carboxylate_promoter_reference_is_unity():
    """기준 농도(promoter_M == promoter_ref_M)에서 촉진 항은 정확히 1.0.

    이 팩의 Kp 는 옥살산이 **없는** 조성(US20080090500A1 TABLE 4)에서 역산됐다.
    기준점에서 1.0 이 아니면 Kp 가 이미 삼킨 화학을 두 번 센다 — 2026-09-06
    Cu MRR 20배 붕괴 사고와 같은 유형이다.
    """
    f = _factors(pack="cu_h2o2_bta")["chi"]
    assert "carboxylate_promoter" in f.terms, f.terms
    assert f.terms["carboxylate_promoter"] == pytest.approx(1.0, abs=1e-12)
    # χ 전체도 기준에서 1.0 (다른 항들의 계약과 함께)
    assert f.value == pytest.approx(1.0, abs=1e-9), f.terms


def test_chi_carboxylate_promoter_monotonic_increasing():
    """옥살산 농도를 올리면 촉진 배수는 **단조 증가**한다(부호 계약).

    글리신(ψ, 판정#72)은 반대로 억제다. 부호가 섞이면 두 축이 서로를 지운다.
    """
    vals = []
    for C in (0.0, 0.02, 0.05, 0.08):
        f = _factors(pack="cu_h2o2_bta", promoter_M=C)["chi"]
        vals.append(f.terms["carboxylate_promoter"])
    assert vals == sorted(vals), vals
    assert vals[0] < vals[-1], vals
    # C=0 에서도 0 으로 붕괴하지 않는다(기계 바닥 φ)
    assert vals[0] > 0.0, vals


def test_chi_carboxylate_promoter_reproduces_patent_control_pair():
    """US6309560B1 TABLE 1 통제쌍(0.5 → 1.0 wt%)의 배수 1.6007 을 재현한다.

    근거 노트: knowledge/cmp/chi-carboxylate-promoter-cu-oxalate-us6309560.md §4
    """
    MW = 124.10
    C_half, C_one = 0.5 * 10.0 / MW, 1.0 * 10.0 / MW
    a = _factors(pack="cu_h2o2_bta", promoter_M=C_half)["chi"].terms["carboxylate_promoter"]
    b = _factors(pack="cu_h2o2_bta", promoter_M=C_one)["chi"].terms["carboxylate_promoter"]
    assert b / a == pytest.approx(1.6007, rel=1e-3), (a, b, b / a)


def test_chi_carboxylate_promoter_species_gate_blocks_glycine():
    """종 게이트: 글리신을 촉진 경로로 흘리면 항을 켜지 않는다(부호 반전 방지).

    같은 Jani 2025 회귀에서 옥살산 +536.63 / 글리신 −440.91 로 부호가 반대다
    (판정#45·#47). 종이 다르면 계수를 전이하지 않는다.
    """
    f = _factors(pack="cu_h2o2_bta", promoter_species="glycine", promoter_M=0.08)["chi"]
    assert "carboxylate_promoter" not in f.terms, f.terms
    assert any("부호가 반대" in n for n in f.notes), f.notes


@pytest.mark.parametrize("pack", ["oxide_silica", "w_fe_oxidizer", "sti_ceria"])
def test_chi_carboxylate_promoter_absent_in_unrelated_packs(pack):
    """촉진 파라미터를 선언하지 않은 팩은 이 항을 갖지 않는다(조용한 전이 금지)."""
    f = _factors(pack=pack)["chi"]
    assert "carboxylate_promoter" not in f.terms, f.terms
