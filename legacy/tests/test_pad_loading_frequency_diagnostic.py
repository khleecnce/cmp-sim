"""viscoelastic_maxwell.py 엔진 등록 회귀 — 패드 공정 하중주파수 역진단 5필드.

근거: sim/tier2_physics/viscoelastic_maxwell.py::maxwell_storage_loss/tan_delta,
sim/tier2_physics/gw_pressure_solve.py::local_contact_state,
sim/tier2_physics/gw_contact.py::hertz_contact_area(전부 원본 무수정),
sim/tier1_empirical/kinematics.py::rpm_to_rads/speed_stats(원본 무수정),
knowledge/materials/pad-viscoelasticity-dma.md §3(Maxwell), §7(a)(ω=1/τ0 → E'/E=0.5 항등식),
§8(개정).

설계: τ0(패드 실측 이완시간) 문헌값이 없어(노트 §4 자백) De를 지어낼 수 없다 — 대신
ω_process 후보 2개(플래튼 회전 ω_rot, 애스퍼리티 접촉 ω_asperity)를 역산하고 τ_crit=1/ω를
낸다. 2026-09-16 정정: ω_asperity는 GW 지수분포 해의 δ_mean=1/β 항등식(A_r/(πR·n)=1/β,
d와 무관)으로 실제 산출된다 — GW 5개 패드 파라미터(_gw_contact_state_diagnostic과 동일
키)가 팩에 선언돼 있고 asperity_height_distribution=="exponential"일 때만 계산하고,
그 외에는 None + 스킵사유. pad_relaxation_time_s는 현재 어느 팩도 미선언이라 De는
항상 None이 정상이다.
"""
import math

import numpy as np
import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _pad_loading_frequency_diagnostic, PSI_TO_PA
from sim.params import available_packs, Param
from sim.tier1_empirical import kinematics as kin
import viscoelastic_maxwell as VM
import gw_pressure_solve as GWP
import gw_contact as GWC

_ALL_PACKS = [p for p in available_packs() if p != "base"]
_EXPECTED_OMEGA_ASPERITY = 362097.5784382698   # rad/s, base.yaml GW 파라미터 상속(5+팩 전부 동일)


def test_omega_rot_matches_2pi_rpm_over_60_for_all_packs():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _pad_loading_frequency_diagnostic(rr)
        expected = 2.0 * math.pi * rr.rpm_platen / 60.0
        assert out["pad_loading_omega_rot_rad_s"] == pytest.approx(expected)
        assert out["pad_loading_omega_rot_rad_s"] == pytest.approx(kin.rpm_to_rads(rr.rpm_platen))


def test_omega_rot_absolute_scale_base_pack():
    # base.yaml rpm_platen=55.0 rpm (literature) → omega_rot 절대값을 못박는다
    # (판정 근거: 과거 21,600km 오답이 상대 테스트만으로 8건 통과한 전례 — 절대 스케일 필수).
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    assert rr.rpm_platen == pytest.approx(55.0)
    out = _pad_loading_frequency_diagnostic(rr)
    assert out["pad_loading_omega_rot_rad_s"] == pytest.approx(5.759586531581287, rel=1e-9)


def test_tau_crit_identity_is_inverse_of_omega_rot():
    rr = Recipe(pack="sti_ceria", time_s=60).resolve()
    out = _pad_loading_frequency_diagnostic(rr)
    omega = out["pad_loading_omega_rot_rad_s"]
    tau_crit = out["pad_relaxation_time_threshold_s"]["rot"]
    assert tau_crit == pytest.approx(1.0 / omega)


def test_omega_asperity_computed_absolute_scale_all_packs():
    # GW 파라미터는 base.yaml 상속이라 전 팩이 같은 값이어야 한다(절대 스케일 고정 —
    # 21,600km 오답이 상대 테스트만으로 8건 통과한 전례 있어 상대비교만으로 두지 않는다).
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _pad_loading_frequency_diagnostic(rr)
        assert out["pad_loading_omega_asperity_rad_s"] == pytest.approx(
            _EXPECTED_OMEGA_ASPERITY, rel=1e-6)
        assert out["pad_relaxation_time_threshold_s"]["asperity"] == pytest.approx(
            1.0 / _EXPECTED_OMEGA_ASPERITY, rel=1e-6)


def test_tau_crit_asperity_identity_is_inverse_of_omega_asperity():
    rr = Recipe(pack="sti_ceria", time_s=60).resolve()
    out = _pad_loading_frequency_diagnostic(rr)
    omega_asp = out["pad_loading_omega_asperity_rad_s"]
    tau_crit_asp = out["pad_relaxation_time_threshold_s"]["asperity"]
    assert omega_asp is not None
    assert tau_crit_asp * omega_asp == pytest.approx(1.0)


def test_delta_mean_matches_pad_height_beta_inv_m_identity():
    # δ_mean = A_r/(π·R·n) = 1/β 는 지수분포 GW 해의 정확한 항등식(d와 무관) —
    # pad_height_beta_inv_m(스케일 1/β)와 기계적으로 고정한다.
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    E_star = rr.p("pad_E_star_pa")
    R = rr.p("pad_asperity_radius_m")
    beta_inv = rr.p("pad_height_beta_inv_m")
    beta = 1.0 / beta_inv
    eta = rr.p("pad_asperity_density_m2")
    A_n = rr.p("pad_nominal_area_m2")
    P_center = rr.pressure_psi * PSI_TO_PA
    state = GWP.local_contact_state(P_center, A_n, beta, eta, E_star, R)
    delta_mean = state["A_r"] / (math.pi * R * state["n_contacts"])
    assert delta_mean == pytest.approx(beta_inv, rel=1e-9)


def test_omega_asperity_none_when_distribution_not_exponential():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr.pack.params["asperity_height_distribution"] = Param(
        key="asperity_height_distribution", value="gaussian", unit="-",
        source="test-probe", confidence="estimated")
    out = _pad_loading_frequency_diagnostic(rr)
    assert out["pad_loading_omega_asperity_rad_s"] is None
    assert out["pad_relaxation_time_threshold_s"]["asperity"] is None
    assert out["pad_deborah_number"]["asperity"] is None
    assert "exponential" in out["pad_loading_frequency_note"]


def test_omega_asperity_none_when_gw_pad_params_missing():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    del rr.pack.params["pad_E_star_pa"]
    out = _pad_loading_frequency_diagnostic(rr)
    assert out["pad_loading_omega_asperity_rad_s"] is None
    assert "pad_E_star_pa" in out["pad_loading_frequency_note"]


def test_reverting_beta_inversion_breaks_omega_asperity_scale():
    # 역수 변환(1/β)을 생략하면(팩 키를 감쇠율로 착각) delta/omega가 실제로 어긋나는지
    # 직접 확인한다 — 이 테스트는 구현이 아니라 "왜 역수 변환이 필수인지"를 기록한다.
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    E_star = rr.p("pad_E_star_pa")
    R = rr.p("pad_asperity_radius_m")
    beta_inv = rr.p("pad_height_beta_inv_m")
    eta = rr.p("pad_asperity_density_m2")
    A_n = rr.p("pad_nominal_area_m2")
    P_center = rr.pressure_psi * PSI_TO_PA
    beta_wrong = beta_inv   # 역수 안 취함 — 잘못된 인자
    state_wrong = GWP.local_contact_state(P_center, A_n, beta_wrong, eta, E_star, R)
    delta_wrong = state_wrong["A_r"] / (math.pi * R * state_wrong["n_contacts"])
    assert delta_wrong != pytest.approx(beta_inv, rel=1e-3)


def test_deborah_number_none_without_tau0_declared():
    rr = Recipe(pack="w_fe_oxidizer", time_s=60).resolve()
    assert not rr.pack.has("pad_relaxation_time_s")
    out = _pad_loading_frequency_diagnostic(rr)
    assert out["pad_deborah_number"]["rot"] is None
    assert "pad_relaxation_time_s" in out["pad_loading_frequency_note"]


def test_deborah_number_and_tan_delta_match_maxwell_analytic_when_tau0_injected():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    tau0 = 0.02  # s, test-probe 주입값 — 문헌값 아님
    rr.pack.params["pad_relaxation_time_s"] = Param(
        key="pad_relaxation_time_s", value=tau0, unit="s",
        source="test-probe", confidence="estimated")
    out = _pad_loading_frequency_diagnostic(rr)
    omega = out["pad_loading_omega_rot_rad_s"]
    de = out["pad_deborah_number"]["rot"]
    assert de["tau0_s"] == pytest.approx(tau0)
    assert de["De"] == pytest.approx(tau0 * omega)

    Es_expect, El_expect = VM.maxwell_storage_loss([omega], 1.0, tau0)
    td_expect = VM.tan_delta(Es_expect, El_expect)
    assert de["E_storage_ratio"] == pytest.approx(float(Es_expect[0]))
    assert de["E_loss_ratio"] == pytest.approx(float(El_expect[0]))
    assert de["tan_delta"] == pytest.approx(float(td_expect[0]))


def test_storage_ratio_is_half_when_tau0_equals_relaxation_threshold():
    # 노트 §7(a) 항등식: omega = 1/tau0 → E'/E = 0.5
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    omega_rot = kin.rpm_to_rads(rr.rpm_platen)
    tau0 = 1.0 / omega_rot
    rr.pack.params["pad_relaxation_time_s"] = Param(
        key="pad_relaxation_time_s", value=tau0, unit="s",
        source="test-probe", confidence="estimated")
    out = _pad_loading_frequency_diagnostic(rr)
    assert out["pad_deborah_number"]["rot"]["De"] == pytest.approx(1.0)
    assert out["pad_deborah_number"]["rot"]["E_storage_ratio"] == pytest.approx(0.5, abs=1e-9)


def test_deborah_number_asperity_axis_matches_maxwell_analytic_when_tau0_injected():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    tau0 = 0.02  # s, test-probe 주입값 — 문헌값 아님
    rr.pack.params["pad_relaxation_time_s"] = Param(
        key="pad_relaxation_time_s", value=tau0, unit="s",
        source="test-probe", confidence="estimated")
    out = _pad_loading_frequency_diagnostic(rr)
    omega_asp = out["pad_loading_omega_asperity_rad_s"]
    de_asp = out["pad_deborah_number"]["asperity"]
    assert omega_asp is not None
    assert de_asp["tau0_s"] == pytest.approx(tau0)
    assert de_asp["De"] == pytest.approx(tau0 * omega_asp)

    Es_expect, El_expect = VM.maxwell_storage_loss([omega_asp], 1.0, tau0)
    td_expect = VM.tan_delta(Es_expect, El_expect)
    assert de_asp["E_storage_ratio"] == pytest.approx(float(Es_expect[0]))
    assert de_asp["E_loss_ratio"] == pytest.approx(float(El_expect[0]))
    assert de_asp["tan_delta"] == pytest.approx(float(td_expect[0]))
    # rot과 asperity는 서로 다른 De — 하나로 뭉개거나 평균내지 않는다
    de_rot = out["pad_deborah_number"]["rot"]
    assert de_asp["De"] != pytest.approx(de_rot["De"])


def test_diagnostic_does_not_change_mrr():
    r = Recipe(pack="oxide_silica", time_s=60)
    res_with = simulate(r)

    orig = E._pad_loading_frequency_diagnostic
    E._pad_loading_frequency_diagnostic = lambda rr: {
        "pad_loading_omega_rot_rad_s": 999.0,
        "pad_loading_omega_asperity_rad_s": None,
        "pad_relaxation_time_threshold_s": {"rot": 999.0, "asperity": None},
        "pad_deborah_number": {"rot": None, "asperity": None},
        "pad_loading_frequency_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._pad_loading_frequency_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert res_forced.pad_loading_omega_rot_rad_s == 999.0


def test_all_packs_full_simulate_wires_the_field():
    for pack in _ALL_PACKS:
        res = simulate(Recipe(pack=pack, time_s=60))
        assert res.pad_loading_omega_rot_rad_s is not None
        assert res.pad_loading_omega_rot_rad_s > 0
        assert res.pad_loading_frequency_note is not None


def _git_diff_clean_or_skip(paths, label):
    """워킹트리에서 `git diff --quiet <paths>` 를 검사한다.

    ⚠ 이 검사는 **git 워킹트리 안에서만** 의미가 있다. `.githooks/pre-push` 는
    `git archive HEAD | tar -x` 로 만든 임시 디렉토리(= git 저장소가 아님)에서
    테스트를 돌리므로, 거기선 `git diff` 가 128을 반환해 무조건 실패한다.
    그 환경에서는 애초에 워킹트리 수정이라는 개념이 없으므로(HEAD를 그대로 꺼낸
    스냅샷이다) skip 하는 것이 옳다 — 실제 게이트는 워킹트리 실행과 CI가 지킨다.
    """
    import subprocess
    root = E.__file__.rsplit("/sim/", 1)[0]
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                            cwd=root, capture_output=True, text=True)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        pytest.skip("git 워킹트리가 아님(pre-push archive 등) — 원본 무수정 검사 스킵")
    result = subprocess.run(["git", "diff", "--quiet", "--"] + list(paths), cwd=root)
    assert result.returncode == 0, f"{label}에 diff가 있다 — 원본 무수정 위반"


def test_original_viscoelastic_maxwell_module_unmodified():
    _git_diff_clean_or_skip(["sim/tier2_physics/viscoelastic_maxwell.py"],
                            "viscoelastic_maxwell.py")


def test_original_gw_modules_unmodified():
    _git_diff_clean_or_skip(
        ["sim/tier2_physics/gw_pressure_solve.py", "sim/tier2_physics/gw_contact.py"],
        "gw_pressure_solve.py/gw_contact.py")


def test_hertz_contact_area_consistent_with_gw_contact_module():
    # GWC.hertz_contact_area(delta, R) = pi*R*delta 원본 그대로 재사용되는지 확인
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    R = rr.p("pad_asperity_radius_m")
    delta = rr.p("pad_height_beta_inv_m")
    assert GWC.hertz_contact_area(delta, R) == pytest.approx(math.pi * R * delta)
