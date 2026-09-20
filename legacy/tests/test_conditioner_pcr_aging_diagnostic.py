"""엔진에 등록된 컨디셔너 PCR 노화 진단(conditioner_pcr_decay.pcr_decay)의 계약 테스트.

근거: sim/tier2_physics/conditioner_pcr_decay.py::pcr_decay·calibrate_tau_from_anchor
(원본 무수정), knowledge/equipment/conditioner-disk-pad-cutting-model.md,
knowledge/equipment/gamma-conditioning-load-confidence-basis.md §3.

여기서 고정하는 것:
  1. 5팩 전부 cond_disk_usage_hours=0.0(신품 기준조건)이라 항상 ratio=1.0이 정상.
  2. cond_disk_usage_hours를 앵커점(50h)까지 올리면 앵커비율(0.16)을 정확히 재현한다.
  3. tau는 팩의 pad_pcr_anchor_hours/pad_pcr_anchor_ratio로 역산한 값과 같다.
  4. 앵커 키가 팩에 없으면 지어내지 않고 None + 스킵사유.
  5. MRR 경로에 어떤 영향도 주지 않는다(비트 불변).
  6. ratio는 사용시간에 대해 단조 비증가.
  7. simulate_conditioned_wear는 엔진 어디에서도 호출되지 않는다(경계 고정 — 등록 대상은
     pcr_decay 뿐이고, 재생항 계수는 문헌값이 아닌 fab-sim 최소확장 가정이라 제외한다).
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim" / "tier2_physics"))

import conditioner_pcr_decay as CPD  # noqa: E402
from sim.engine import Recipe, simulate, _conditioner_pcr_aging_diagnostic  # noqa: E402
from sim.params import Param  # noqa: E402

PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]
PCR_FIELDS = ["conditioner_pcr_aging_ratio", "conditioner_pcr_tau_hours",
              "conditioner_disk_usage_hours"]


@pytest.mark.parametrize("pack", PACKS)
def test_new_disk_default_gives_ratio_one(pack):
    """5팩 전부 cond_disk_usage_hours=0.0(신품) — 감쇠 없음(ratio=1.0)이 기준조건."""
    r = simulate(Recipe(pack=pack, time_s=60))
    assert r.conditioner_pcr_aging_ratio == 1.0
    assert r.conditioner_disk_usage_hours == 0.0
    assert r.conditioner_pcr_note is not None


def test_anchor_hours_override_reproduces_anchor_ratio():
    """cond_disk_usage_hours=50(앵커점)으로 올리면 pad_pcr_anchor_ratio=0.16을 재현한다."""
    r = simulate(Recipe(pack="oxide_silica", time_s=60,
                        pack_overrides={"cond_disk_usage_hours": 50.0}))
    assert r.conditioner_pcr_aging_ratio is not None
    assert abs(r.conditioner_pcr_aging_ratio - 0.16) < 1e-9


def test_tau_matches_calibrate_tau_from_anchor():
    r = simulate(Recipe(pack="oxide_silica", time_s=60,
                        pack_overrides={"cond_disk_usage_hours": 50.0}))
    expected_tau = CPD.calibrate_tau_from_anchor(50.0, 0.16)
    assert r.conditioner_pcr_tau_hours is not None
    assert abs(r.conditioner_pcr_tau_hours - expected_tau) < 1e-9
    # base.yaml 앵커(50h -> 0.16)는 모듈 하드코딩 ENTEGRIS_ANCHOR_*와 수치가 같다.
    assert abs(expected_tau - CPD.TAU_AGING_HOURS) < 1e-9


def test_missing_anchor_key_skips_with_reason():
    """앵커 키(pad_pcr_anchor_hours)가 팩에 없으면 지어내지 않고 None + 스킵사유."""
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    assert rr.pack.has("pad_pcr_anchor_hours")
    del rr.pack.params["pad_pcr_anchor_hours"]
    out = _conditioner_pcr_aging_diagnostic(rr)
    assert out["conditioner_pcr_aging_ratio"] is None
    assert out["conditioner_pcr_tau_hours"] is None
    assert out["conditioner_pcr_note"] is not None
    assert "pad_pcr_anchor_hours" in out["conditioner_pcr_note"]


def test_diagnostic_does_not_touch_mrr():
    """진단 입력(cond_disk_usage_hours)을 바꿔도 MRR은 비트 단위로 같아야 한다."""
    off = simulate(Recipe(pack="oxide_silica", time_s=180, pressure_psi=3.0))
    on = simulate(Recipe(pack="oxide_silica", time_s=180, pressure_psi=3.0,
                         pack_overrides={"cond_disk_usage_hours": 50.0}))
    assert off.conditioner_pcr_aging_ratio == 1.0
    assert on.conditioner_pcr_aging_ratio is not None and on.conditioner_pcr_aging_ratio != 1.0
    np.testing.assert_array_equal(off.mrr_nm_per_min, on.mrr_nm_per_min)
    np.testing.assert_array_equal(off.removed_nm, on.removed_nm)


def test_ratio_monotonically_decreases_with_usage_hours():
    hours = [0.0, 10.0, 27.4, 50.0, 100.0]
    ratios = []
    for h in hours:
        r = simulate(Recipe(pack="oxide_silica", time_s=60,
                            pack_overrides={"cond_disk_usage_hours": h}))
        ratios.append(r.conditioner_pcr_aging_ratio)
    assert all(a >= b for a, b in zip(ratios, ratios[1:]))
    assert ratios[0] == 1.0
    assert ratios[-1] < ratios[0]


def test_simulate_conditioned_wear_never_called_from_engine():
    """경계 고정: 등록 대상은 pcr_decay 뿐 — simulate_conditioned_wear는 CPD 별칭으로 호출되지 않는다.

    engine.py/factors.py는 모두 `import conditioner_pcr_decay as CPD` 관례를 쓴다(원본 무수정
    모듈을 그대로 참조). docstring 산문에서 "등록하지 않는다"는 경계 설명으로 함수명을
    언급하는 것은 허용하되, 실제 호출 형태(`CPD.simulate_conditioned_wear(`)는 금지한다.
    """
    import re
    engine_src = (ROOT / "sim" / "engine.py").read_text(encoding="utf-8")
    factors_src = (ROOT / "sim" / "factors.py").read_text(encoding="utf-8")
    pattern = re.compile(r"CPD\.simulate_conditioned_wear\s*\(")
    for name, src in (("engine.py", engine_src), ("factors.py", factors_src)):
        assert not pattern.search(src), (
            f"sim/{name}가 CPD.simulate_conditioned_wear(...)를 호출한다(등록 금지 대상 — "
            "재생항 계수는 문헌값이 아닌 fab-sim 최소확장 가정)")
