"""엔진에 등록된 패드 글레이징 진단(pad_glazing_jeong2024)의 계약 테스트.

근거: Jeong et al. 2024, Materials 17, 1817 (doi:10.3390/ma17081817) Table 1 · Eq.4.
이 진단은 다른 진단보다 적용 전제가 좁다 — 세 관문(컨디셔닝 없음 / Table 1에 있는 압력 /
측정 구간 안의 시간)을 전부 통과할 때만 값을 낸다. 여기서 고정하는 것:

  1. 실제 5팩은 전부 cond_duty_pct=100(in-situ 연속)이라 **항상 None + 스킵사유**가 정상.
  2. 관문을 열어주면(pack_overrides로 duty=0) 값이 나오고, 원본 모듈과 비트 단위로 같다.
  3. Table 1 밖 압력·측정상한 초과 시간은 지어내지 않고 스킵.
  4. MRR 경로에 어떤 영향도 주지 않는다(비트 불변).
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim" / "tier2_physics"))

from sim.engine import Recipe, simulate  # noqa: E402

PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]
GLAZE_FIELDS = ["pad_glazing_contact_ratio", "pad_glazing_radius_growth_ratio",
                "pad_glazing_relative_mrr_proxy"]


@pytest.mark.parametrize("pack", PACKS)
def test_real_packs_skip_because_conditioning_is_on(pack):
    """5팩 전부 in-situ 컨디셔닝(duty=100) — 값 없이 스킵사유만 나와야 한다."""
    r = simulate(Recipe(pack=pack, time_s=60))
    for f in GLAZE_FIELDS:
        assert getattr(r, f) is None, f"{pack}: {f}가 채워졌다 — 컨디셔닝 중인데 외삽했다"
    assert r.pad_glazing_note is not None
    assert "컨디셔닝" in r.pad_glazing_note


def test_values_appear_when_all_three_gates_open():
    r = simulate(Recipe(pack="oxide_silica", time_s=180, pressure_psi=3.0,
                        pack_overrides={"cond_duty_pct": 0.0}))
    for f in GLAZE_FIELDS:
        assert getattr(r, f) is not None
    # 접촉점은 줄고(<1) 반경은 늘어야(>1) Jeong 2024의 정성 방향과 맞다
    assert r.pad_glazing_contact_ratio < 1.0
    assert r.pad_glazing_radius_growth_ratio > 1.0
    assert "정량 캘리브레이션 금지" in r.pad_glazing_note


def test_matches_source_module_bitwise():
    """엔진 값은 원본 모듈 함수의 값과 정확히 같아야 한다(재구현이 아니라 위임)."""
    import pad_glazing_jeong2024 as PGJ
    t_s, p = 240.0, 4.0
    r = simulate(Recipe(pack="oxide_silica", time_s=t_s, pressure_psi=p,
                        pack_overrides={"cond_duty_pct": 0.0}))
    t_min = t_s / 60.0
    assert r.pad_glazing_contact_ratio == float(PGJ.contact_ratio(4, t_min))
    assert r.pad_glazing_radius_growth_ratio == float(PGJ.radius_growth_ratio(4, t_min))
    assert r.pad_glazing_relative_mrr_proxy == float(PGJ.relative_mrr_proxy(4, t_min))


@pytest.mark.parametrize("psi", [1.0, 2.5, 3.5, 6.0])
def test_pressure_outside_table1_is_skipped_not_interpolated(psi):
    r = simulate(Recipe(pack="oxide_silica", time_s=120, pressure_psi=psi,
                        pack_overrides={"cond_duty_pct": 0.0}))
    for f in GLAZE_FIELDS:
        assert getattr(r, f) is None, f"{psi} psi는 Table 1에 없는데 값을 만들어냈다"
    assert "Table 1에 없는 압력" in r.pad_glazing_note


def test_time_beyond_measurement_window_is_skipped():
    # 5 psi의 Table 1 상한은 5분 — 6분은 외삽이라 스킵
    r = simulate(Recipe(pack="oxide_silica", time_s=360, pressure_psi=5.0,
                        pack_overrides={"cond_duty_pct": 0.0}))
    assert r.pad_glazing_contact_ratio is None
    assert "측정 상한" in r.pad_glazing_note
    # 4분은 구간 안이라 값이 나온다
    ok = simulate(Recipe(pack="oxide_silica", time_s=240, pressure_psi=5.0,
                         pack_overrides={"cond_duty_pct": 0.0}))
    assert ok.pad_glazing_contact_ratio is not None


def test_diagnostic_does_not_touch_mrr():
    """진단을 켠 런과 끈 런의 MRR이 비트 단위로 같아야 한다."""
    off = simulate(Recipe(pack="oxide_silica", time_s=180, pressure_psi=3.0))
    on = simulate(Recipe(pack="oxide_silica", time_s=180, pressure_psi=3.0,
                         pack_overrides={"cond_duty_pct": 0.0}))
    assert on.pad_glazing_contact_ratio is not None and off.pad_glazing_contact_ratio is None
    np.testing.assert_array_equal(off.mrr_nm_per_min, on.mrr_nm_per_min)
    np.testing.assert_array_equal(off.removed_nm, on.removed_nm)


def test_pad_hours_is_not_used_as_time_axis():
    """S13 판정: meta.pad_hours(누적 시간h)를 Jeong의 t(단일 연마 min)로 쓰면 안 된다."""
    a = simulate(Recipe(pack="oxide_silica", time_s=180, pressure_psi=3.0,
                        pack_overrides={"cond_duty_pct": 0.0}))
    b = simulate(Recipe(pack="oxide_silica", time_s=180, pressure_psi=3.0,
                        meta={"pad_hours": "500"},
                        pack_overrides={"cond_duty_pct": 0.0}))
    assert a.pad_glazing_contact_ratio == b.pad_glazing_contact_ratio
