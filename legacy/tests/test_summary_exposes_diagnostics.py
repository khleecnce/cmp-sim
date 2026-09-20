"""summary()가 등록된 진단 필드를 빠짐없이 내보내는지 기계로 고정한다.

배경 (2026-09-16 실측 결함):
  WaferResult 필드는 125개인데 summary()가 내보내던 키는 37개뿐이었다. 즉 그간 엔진에
  등록된 진단 88개(gw_pressure_solve·tribology_basics·slurry_components·recipe_conversion_
  factor·blanket_rate_transfer 등)가 CLI(`sim.cli --json`)와 API 응답에서 **통째로 보이지
  않았다**. summary()의 키 목록을 손으로 유지하는 구조라, 진단을 등록해도 이 목록에
  추가하는 것을 잊으면 조용히 누락됐다 — 테스트가 없어 아무도 몰랐다.

  "엔진에 등록했다"는 것은 사용자에게 도달한다는 뜻이어야 한다. 도달하지 않으면 등록이
  아니다. 그래서 summary()를 필드 자동 순회로 바꾸고, 이 테스트가 재발을 막는다.

이 테스트가 지키는 계약:
  1. WaferResult의 모든 필드는 _SUMMARY_EXCLUDE에 명시되지 않는 한 summary()에 나온다.
  2. _SUMMARY_EXCLUDE에는 "요약에 담을 수 없는 것"만 들어간다(배열 프로파일 + 위에서
     이미 가공해 실은 구조체). 진단 스칼라를 여기 추가해 숨기는 것은 금지 —
     제외 목록 자체를 리터럴로 못 박아 몰래 늘어나는 것을 막는다.
  3. summary()는 json 직렬화 가능해야 한다(CLI --json이 json.dumps를 부른다).
  4. MRR 경로는 이 변경과 무관하다(비트 불변).
"""
import dataclasses
import json

import numpy as np
import pytest

from sim.engine import WaferResult, Recipe, simulate, _SUMMARY_EXCLUDE
from sim.params import available_packs

_ALL_PACKS = [p for p in available_packs() if p != "base"]

# 제외가 허용되는 필드 — 배열 프로파일(CLI --profile / API res["profile"]이 별도 경로로
# 내보냄)과 위에서 이미 가공해 실은 구조체뿐이다. 이 리터럴을 늘려서 진단을 숨기지 마라.
_ALLOWED_EXCLUDE = {
    "recipe", "radius_m", "mrr_nm_per_min", "removed_nm", "remaining_nm",
    "metrics", "factors", "equipment_outputs", "notes", "provenance",
}


def test_exclude_set_is_exactly_the_allowed_literal():
    assert set(_SUMMARY_EXCLUDE) == _ALLOWED_EXCLUDE, (
        "_SUMMARY_EXCLUDE가 바뀌었다. 진단 스칼라를 여기 넣어 summary()에서 숨기는 것은 "
        "2026-09-16에 고친 결함의 재발이다. 정말 제외가 필요하면 이 테스트의 "
        "_ALLOWED_EXCLUDE와 함께 사유를 문서에 남기고 바꿔라.")


@pytest.mark.parametrize("pack", _ALL_PACKS)
def test_every_field_reaches_summary(pack):
    res = simulate(Recipe(pack=pack))
    s = res.summary()
    names = [f.name for f in dataclasses.fields(WaferResult)]
    missing = [n for n in names if n not in s and n not in _SUMMARY_EXCLUDE]
    assert not missing, f"{pack}: summary()에서 누락된 필드 {missing}"


def test_recently_registered_diagnostics_are_visible():
    """대표 샘플 — 2026-09-13 이후 등록된 진단들이 실제로 키로 나오는지."""
    s = simulate(Recipe(pack="cu_h2o2_bta")).summary()
    for k in ("gw_solved_separation_m", "gw_plasticity_index",
              "archard_wear_coefficient", "tribology_hersey_number",
              "inhibitor_theta_equilibrium", "recipe_work_function",
              "blanket_transient_note", "thermal_chemical_rate_ratio",
              "conditioner_pcr_aging_ratio", "cu_pourbaix_note",
              "pourbaix_nernst_slope_mv_per_ph", "disk_contact_eta_c_m2"):
        assert k in s, f"{k}가 summary()에 없다 — 등록했는데 사용자에게 도달하지 않는다"


@pytest.mark.parametrize("pack", _ALL_PACKS)
def test_summary_is_json_serializable(pack):
    """CLI --json이 json.dumps(summary())를 부른다 — 직렬화 불가 값이 들어가면 즉시 깨진다."""
    s = simulate(Recipe(pack=pack)).summary()
    json.dumps(s, ensure_ascii=False)


def test_summary_json_serializable_on_ptw_with_full_meta():
    """진단이 최대로 켜지는 경로(PTW + 패턴 레이아웃 + 누적 패드시간)에서도 직렬화 가능."""
    r = Recipe(pack="cu_h2o2_bta", wafer="PTW", time_s=120,
               meta={"pattern_density": 0.5, "linewidth_um": 10.0, "space_um": 10.0,
                     "r_cu_angstrom_s": 159.0, "r_ox_angstrom_s": 10.0,
                     "pad_hours": 50.0, "initial_thickness_nm": 1000.0})
    s = simulate(r).summary()
    json.dumps(s, ensure_ascii=False)
    assert s["cu_dishing_tugbawa_nm"] is not None


def test_manual_keys_still_present_and_unchanged():
    """기존에 손으로 넣던 37개 키가 그대로 남아 있는지(하위호환) — 이름·값 경로 보존."""
    s = simulate(Recipe(pack="oxide_silica")).summary()
    for k in ("mean_mrr_nm_min", "ttv_nm", "radial_range_pct", "cv_pct",
              "wiwnu_halfrange_pct", "wiwnu_3sigma_pct", "model", "pack",
              "wafer", "film", "factors", "factor_coverage",
              "equipment_outputs", "notes"):
        assert k in s, f"기존 키 {k}가 사라졌다"


@pytest.mark.parametrize("pack", _ALL_PACKS)
def test_mrr_bit_identical(pack):
    """이 변경은 출력 직렬화만 건드린다 — MRR 경로는 비트 단위로 불변이어야 한다."""
    a = simulate(Recipe(pack=pack)).mrr_nm_per_min
    b = simulate(Recipe(pack=pack)).mrr_nm_per_min
    assert np.array_equal(a, b)
    s = simulate(Recipe(pack=pack)).summary()
    assert s["mean_mrr_nm_min"] == pytest.approx(float(np.mean(a)), rel=0, abs=0)
