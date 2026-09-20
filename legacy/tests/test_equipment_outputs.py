"""장비 출력값(sim/equipment_outputs.py) 계약 테스트 — ARCHITECTURE-V2.md §1-①.

출력값 = 설정값이 아니라 **저절로 도출되는** 진단 신호(패드 온도, 모터 전류, μ).
여기서 고정하는 것은 물리 재정의가 아니라 계약이다.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe, simulate                       # noqa: E402
from sim.equipment_outputs import compute_outputs, summarize  # noqa: E402


def _out(**ov):
    return compute_outputs(Recipe(pack="oxide_silica", pack_overrides=ov).resolve())


# ═══════════════════════ 회귀: 마찰 발열이 압력에 반응해야 한다

def test_friction_heating_responds_to_pressure():
    """다운포스를 올리면 마찰 발열과 패드 온도가 **올라가야** 한다.

    ⚠ 2026-09-08 실제 버그의 회귀 테스트다.
      직접 지어낸 로지스틱 Stribeck 보간에서 CMP 전형 조건이 전부 '유체' 가지로
      들어가 μ = c_hydro·So ∝ 1/P 가 됐다. 그 결과 μ·P가 상수가 되어
      **다운포스를 1→8 psi로 8배 올려도 패드 온도가 11.632 K로 고정**이었다.
      코드는 예외 없이 조용히 돌았고 테스트도 없었다.

      교훈: 검증된 tier2 함수(cof_stribeck)가 있는데 새로 지어내지 마라.
    """
    temps = [_out(pressure_psi=p)["pad_temp_rise_k"].value for p in (1.0, 3.0, 8.0)]
    assert all(t is not None for t in temps)
    assert temps[0] < temps[1] < temps[2], (
        f"압력이 올라가는데 패드 온도가 안 오른다: {temps} — "
        "μ ∝ 1/P 붕괴가 재발했을 가능성이 높다.")
    # 8배 압력에서 온도상승이 최소 3배는 돼야 한다 (상수 고정 방지)
    assert temps[2] / temps[0] > 3.0, (
        f"압력 8배에 온도상승이 {temps[2]/temps[0]:.2f}배뿐 — 사실상 상수다.")


def test_heat_flux_scales_with_pressure():
    qs = [_out(pressure_psi=p)["heat_flux_w_m2"].value for p in (1.0, 8.0)]
    assert qs[1] > qs[0] * 3.0, f"q = μ·P·V가 압력에 반응하지 않는다: {qs}"


def test_cof_stays_in_literature_range():
    """oxide CMP의 COF는 문헌상 0.23~0.40(경계윤활) 오더다.

    유체 영역으로 잘못 떨어지면 0.001 오더가 나오고, 그때 μ·P가 상수화된다.
    """
    for p in (1.0, 3.0, 5.0, 8.0):
        mu = _out(pressure_psi=p)["cof"].value
        assert 0.05 < mu < 0.6, (
            f"P={p} psi에서 μ={mu:.5f} — CMP 경계·혼합 영역(0.23~0.40 오더)을 "
            "벗어났다. 윤활 레짐 판정이 무너졌을 수 있다.")


def test_cooling_responds_to_sfr():
    """SFR을 올리면 냉각이 강해져 온도상승이 내려가야 한다."""
    lo = _out(sfr_ml_min=50.0)["pad_temp_rise_k"].value
    hi = _out(sfr_ml_min=300.0)["pad_temp_rise_k"].value
    assert hi < lo, f"유량을 6배 늘렸는데 온도가 안 내려간다: {lo} → {hi}"
    # 에너지 균형상 dT ∝ 1/유량 이어야 한다
    assert lo / hi == pytest.approx(6.0, rel=0.05)


# ═══════════════════════ 설정값/출력값 구분

def test_outputs_are_derived_not_settable():
    """출력값은 Recipe 필드가 아니어야 한다 — 사용자가 넣는 값이 아니다."""
    fields = set(Recipe.__dataclass_fields__)
    for key in ("pad_temp_c", "carrier_current_a", "cof", "platen_torque_nm"):
        assert key not in fields, (
            f"{key}가 Recipe 입력 필드에 있다 — 출력값을 설정값으로 두면 "
            "사용자가 결과를 직접 쓰는 셈이 된다.")


def test_unavailable_outputs_are_not_invented():
    """계산 불가한 출력은 None + 이유를 남기고, 숫자를 지어내지 않는다."""
    o = _out()
    cur = o["carrier_current_a"]
    assert cur.value is None and cur.status == "unmodeled"
    assert "토크상수" in cur.note or "K_t" in cur.note, (
        "모터 전류가 미모델링인데 이유를 설명하지 않는다.")
    assert o["vibration"].value is None


def test_motor_current_appears_when_constant_given():
    """장비 상수(K_t)만 주면 전류가 나와야 한다 — 통로는 이미 뚫려 있다."""
    o = _out(motor_torque_constant_nm_per_a=0.5)
    cur = o["carrier_current_a"]
    assert cur.status == "computed" and cur.value > 0
    torque = o["platen_torque_nm"].value
    assert cur.value == pytest.approx(torque / 0.5, rel=1e-9)


def test_temp_rise_is_labelled_as_upper_bound():
    """패드 온도는 '상한'임을 반드시 밝혀야 한다.

    마찰열 전량이 슬러리로 간다는 가정이라 실제보다 높다. 이걸 안 밝히면
    사용자가 절대값을 신뢰한다.
    """
    note = _out()["pad_temp_rise_k"].note
    assert "상한" in note and "⚠" in note


# ═══════════════════════ 엔진 통합

def test_engine_attaches_equipment_outputs():
    res = simulate(Recipe(pack="oxide_silica"))
    assert res.equipment_outputs, "엔진 결과에 장비 출력값이 안 실렸다"
    assert res.equipment_outputs["pad_temp_c"].value is not None


def test_equipment_outputs_are_json_serializable():
    import json
    res = simulate(Recipe(pack="oxide_silica"))
    s = json.dumps(res.summary()["equipment_outputs"], ensure_ascii=False)
    assert "pad_temp_c" in s


def test_equipment_outputs_do_not_change_mrr():
    """출력값 계산은 MRR 경로와 완전히 독립이어야 한다(진단일 뿐)."""
    import numpy as np
    a = simulate(Recipe(pack="oxide_silica"))
    b = simulate(Recipe(pack="oxide_silica",
                        pack_overrides={"motor_torque_constant_nm_per_a": 0.5}))
    assert np.allclose(a.mrr_nm_per_min, b.mrr_nm_per_min), (
        "장비 상수를 넣었더니 MRR이 변했다 — 진단이 물리에 새고 있다.")


def test_summary_reports_unmodeled_honestly():
    s = summarize(_out())
    assert s["score"] < 1.0, "출력 커버리지가 100%로 나온다 — 미모델링을 숨긴다"
    assert "vibration" in s["unmodeled"]
