"""회귀 — model_hygiene.py 극한(L) 검사의 조용한 건너뜀 제거 (EVIDENCE-RULES 판정#95).

배경: time_s(Recipe 필드) · dispersant_type(범주형)이 팩 YAML 정규식 치환으로만
극한값을 주입하던 model_hygiene.py::check_limits 에서 "바꾸지 못함"으로 조용히
건너뛰어지고 있었다. 또한 chelator_M/promoter_M 이 LIMIT_ROLE 에 미등록이었고,
_f_psi 의 ψ>1 정의위반 검사가 착화제 항을 곱하기 전에만 걸려 있어 chelator_M=0
에서 ψ=1.223 > 1 을 아무 게이트도 못 잡는 사각지대가 있었다.
knowledge/cmp/model-hygiene-limit-check-silent-skip-time-chelator.md 참조.
"""
import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from sim.engine import Recipe, simulate  # noqa: E402
from sim.factors import LIMIT_ROLE, CATEGORICAL_ABSENT  # noqa: E402
from sim.params import available_packs, load_pack  # noqa: E402
from tools.model_hygiene import (  # noqa: E402
    check_limits, _recipe_field_names, _INTENSIVE_PROBES,
)


# ══════════════════════════════════════════════════════════════════════
# 실물 A·B 절대값 고정 — rel=1e-9. 되돌리면 반드시 FAIL 해야 한다.
# ══════════════════════════════════════════════════════════════════════

def test_tau_time_s_1s_absolute_value():
    rr = simulate(Recipe(pack="cu_h2o2_bta", time_s=1.0))
    assert rr.factors["tau"].value == pytest.approx(0.05211867631070653, rel=1e-9)


def test_tau_time_s_zero_is_gated_not_a_free_pass():
    """time_s=0 에서 τ=1.0 은 항이 스스로 꺼진 결과다 — 우연한 통과가 아니라
    신고된 것이어야 한다(_f_tau 의 t_pol>0 가드)."""
    rr = simulate(Recipe(pack="cu_h2o2_bta", time_s=0.0))
    assert rr.factors["tau"].value == 1.0
    assert "time_s" not in rr.factors["tau"].drivers
    assert any("turnover 항 미적용" in n for n in rr.factors["tau"].notes)


def test_psi_chelator_zero_absolute_value():
    rr = simulate(Recipe(pack="cu_h2o2_bta", pack_overrides={"chelator_M": 0.0}))
    assert rr.factors["psi"].value == pytest.approx(1.2230956708315368, rel=1e-9)


def test_psi_chelator_zero_flags_definition_violation():
    """ψ 는 정의상 ≤1 이어야 한다. chelator_M=0 에서 최종값이 1을 넘으면
    (착화제 항까지 곱한 뒤에도) 반드시 notes 에 신고돼야 한다 — 판정#95
    이전에는 착화제 항을 곱하기 **전의** v 에만 이 검사가 걸려 있어 놓쳤다."""
    rr = simulate(Recipe(pack="cu_h2o2_bta", pack_overrides={"chelator_M": 0.0}))
    psi = rr.factors["psi"].value
    assert psi > 1.0
    assert any("정의(표면 보호 ≤1) 위반" in n for n in rr.factors["psi"].notes)


# ══════════════════════════════════════════════════════════════════════
# MRR 비트 불변 — 이 과제는 진단 계층만 고친다. 값 계산은 손대지 않는다.
# 기준 조건(Recipe 기본값)에서 각 팩의 평균 MRR 이 정확히 이 리터럴과
# 일치해야 한다(rel/abs tolerance 없음 — 비트 단위 재현).
# ══════════════════════════════════════════════════════════════════════
_EXPECTED_MEAN_MRR_NM_MIN = {
    "cu_h2o2_bta": 500.5453363064934,
    "oxide_silica": 143.01295323042672,
    "w_fe_oxidizer": 400.4362690451948,
    "sti_ceria": 314.6284971069387,
    "sic_ceria_h2o2": 2.0227752104911554,
    "sic_alumina_kmno4": 7.132342003507841,
    "cu_alkaline_benzenesulfonic": 27.330323101945417,
}


@pytest.mark.parametrize("pack, expected", sorted(_EXPECTED_MEAN_MRR_NM_MIN.items()))
def test_mrr_bitwise_unchanged(pack, expected):
    import numpy as np
    rr = simulate(Recipe(pack=pack))
    got = float(np.mean(rr.mrr_nm_per_min))
    assert got == expected, (
        f"[{pack}] 평균 MRR 이 바뀌었다 ({expected!r} → {got!r}). 이 과제는 "
        "진단·검사 계층만 고쳐야 하고 sim/ 의 수치는 비트 단위로 불변이어야 "
        "한다.")


# ══════════════════════════════════════════════════════════════════════
# time_s / dispersant_type 이 더는 "바꾸지 못함"으로 건너뛰어지지 않는다
# (성질 검사 — 특정 문자열이 아니라 "판정이 실제로 났는가"를 본다).
# ══════════════════════════════════════════════════════════════════════

def test_time_s_limit_check_actually_runs():
    issues = check_limits(["cu_h2o2_bta"])
    time_s_issues = [i for i in issues if "time_s" in i.title]
    assert time_s_issues, "time_s 에 대한 판정이 전혀 없다 — 검사가 수행되지 않았다"
    assert not any("바꾸지 못함" in i.title for i in time_s_issues), (
        f"time_s 가 여전히 극한값으로 바꾸지 못하고 건너뛰어진다: {time_s_issues}")


def test_dispersant_type_limit_check_actually_runs():
    issues = check_limits(["oxide_silica"])
    disp_issues = [i for i in issues if "dispersant_type" in i.title]
    assert not any("바꾸지 못함" in i.title for i in disp_issues), (
        f"dispersant_type 이 여전히 극한값으로 바꾸지 못하고 건너뛰어진다: {disp_issues}")


def test_no_pack_reports_cannot_write_for_recipe_or_categorical_keys():
    """전 팩에 대해 '드라이버 X 를 극한값으로 바꾸지 못함' 이 하나도 없어야
    한다 — 남아 있다면 그건 Recipe 필드도 범주형(선언됨)도 아닌 진짜 결함이고,
    이제는 error 로 격상돼 있어야 한다(warn 으로 조용히 남지 않는다)."""
    issues = check_limits(list(available_packs()))
    skip_warns = [i for i in issues
                  if "바꾸지 못함" in i.title and i.severity == "warn"]
    assert not skip_warns, (
        "'바꾸지 못함'이 여전히 warn 으로 조용히 보고되고 있다 — error 로 "
        f"격상됐어야 한다: {skip_warns}")


# ══════════════════════════════════════════════════════════════════════
# LIMIT_ROLE 에 등록된 모든 키가 실제로 검사 가능한 경로를 가진다.
# 동형 재발(새 드라이버가 또 조용히 건너뛰어지는 것) 차단.
# ══════════════════════════════════════════════════════════════════════

def _observed_driver_keys(packs):
    """check_limits() 가 실제로 순회하는 것과 같은 집합 — 어느 팩의 어느
    MRR 결합 팩터든 **실제로 드라이버로 보고한** 키만 모은다.

    LIMIT_ROLE 에는 등록만 되고 어느 팩터도 드라이버로 보고하지 않는 키가
    있을 수 있다(예: relative_velocity_m_s — AGENT 로 선언은 됐지만 지금
    kappa 구현이 실제 드라이버 딕셔너리에 싣지 않는다). 그런 키는
    check_limits() 의 for-loop 에 애초에 들어오지 않으므로 이번 판정#95의
    "조용한 건너뜀"과는 다른 종류의 문제(선언은 있으나 미사용)다 — 이
    테스트의 스코프 밖이라 여기서 걸러낸다.
    """
    import warnings
    warnings.filterwarnings("ignore")
    keys = set()
    for p in packs:
        try:
            rr = simulate(Recipe(pack=p))
        except Exception:
            continue
        for f in rr.factors.values():
            if f.mrr_coupled:
                for d in (f.drivers or {}):
                    keys.add(d.split("(")[0])
    return keys


def test_limit_role_keys_all_have_a_check_path():
    recipe_fields = _recipe_field_names()
    packs = list(available_packs())
    observed = _observed_driver_keys(packs)

    for key, role in LIMIT_ROLE.items():
        if key not in observed:
            continue    # 어느 팩터도 드라이버로 보고하지 않음 — 이 테스트 스코프 밖
        if role == "INTENSIVE":
            assert key in _INTENSIVE_PROBES, (
                f"'{key}' 는 INTENSIVE 인데 tools/model_hygiene.py 의 "
                "_INTENSIVE_PROBES 에 정의역이 등록돼 있지 않다.")
            continue

        if key in recipe_fields:
            continue  # Recipe kwarg 로 직접 주입 가능

        is_categorical = False
        found_numeric = False
        for p in packs:
            try:
                pk = load_pack(p)
            except Exception:
                continue
            if not pk.has(key):
                continue
            val = pk.get(key)
            if isinstance(val, str):
                is_categorical = True
            else:
                found_numeric = True

        if is_categorical:
            assert key in CATEGORICAL_ABSENT, (
                f"'{key}' 는 범주형 드라이버인데 CATEGORICAL_ABSENT 에 '없음' "
                "값이 선언돼 있지 않다 — 검사기가 극한값을 추측해야 한다.")
        else:
            assert found_numeric, (
                f"'{key}' 는 어느 팩에도 숫자 파라미터로 존재하지 않는다 — "
                "_write_value 로도 Recipe kwarg 로도 닿을 방법이 없다.")


def test_chelator_and_promoter_m_registered():
    """이번 조사에서 드러난 미선언 두 건 — 재발 방지용 명시 확인."""
    assert LIMIT_ROLE.get("chelator_M") == "MODULATOR"
    assert LIMIT_ROLE.get("promoter_M") == "MODULATOR"
