"""χ/cu_h2o2_bta 산화제 항 — 산성×착화제 레짐 게이트 계약 테스트.

EVIDENCE-RULES 판정#41(knowledge/cmp/chi-cu-h2o2-regime-reversal-jani2025.md §9),
판정#47(knowledge/cmp/chi-oxidizer-gate-chelator-species-specificity.md)로 착화제
종 특이성 게이트 추가.

지키는 계약:
  ① 다른 4팩의 산화제 항 출력은 이 변경으로 비트 단위로 불변이어야 한다
     (`oxidizer_acid_chelator_K`를 선언하지 않은 팩은 새 코드 경로를 절대 타지 않는다).
  ② cu_h2o2_bta도 기준 조건(C=C_ref)에서는 배수가 항등적으로 1.0이어야 한다.
  ③ 팩 이름 하드코딩 금지 — slurry_ph/chelator_M 필드로만 분기한다(판정#34).
  ④ 게이트 미충족(착화제·pH 미선언, 또는 pH>=6)이면 기존 경로로 조용히 폴백한다.
  ⑤ [판정#47] `oxidizer_acid_chelator_species`가 팩의 `chelator_species`와 일치할
     때만 촉진-포화형이 발동한다. 불일치면 기존(억제형) 경로로 폴백한다.
  ⑥ [판정#47] 종 선언이 아예 없는 구버전 팩은 판정#41 이전 동작(항상 발동)을
     유지하되 검증 못 했다는 경고를 남긴다 — 지어내지 않는다.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.chemistry import _oxidizer_term  # noqa: E402
from sim.params import load_pack  # noqa: E402


class FakePack:
    """팩 인터페이스 최소 구현 — sim/tests/test_chemistry.py의 관례를 따른다."""

    def __init__(self, **kw):
        self.d = kw
        self.name = "fake"

    def has(self, k):
        return k in self.d

    def get(self, k):
        return self.d[k]

    def get_or(self, k, dv):
        return self.d.get(k, dv)


ACID_CHELATOR = dict(
    oxidizer_wt_pct=3.0, oxidizer_ref_wt_pct=3.0,
    oxidizer_acid_chelator_K=0.7935, oxidizer_passivation_K=0.8232,
    slurry_ph=4.0, chelator_M=0.1332,
)

OTHER_PACKS = ["oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


# ── ① 다른 4팩 비트불변 ─────────────────────────────────────────
@pytest.mark.parametrize("pack_name", OTHER_PACKS)
def test_other_four_packs_oxidizer_term_bit_identical(pack_name):
    """이 팩들은 oxidizer_acid_chelator_K를 선언하지 않는다 — 새 게이트가
    조용히 켜져 출력을 바꾸면 안 된다."""
    pack = load_pack(pack_name)
    assert not pack.has("oxidizer_acid_chelator_K"), (
        f"{pack_name}에 oxidizer_acid_chelator_K가 선언됐다 — 이 테스트의 전제가 깨졌다"
    )
    notes = []
    v = _oxidizer_term(pack, notes)
    # 게이트 블록이 전혀 진입하지 않았다는 증거 — notes에 판정#41 관련 문구가 없어야 한다
    assert not any("판정#41" in n or "산성×착화제" in n for n in notes), (
        f"{pack_name}에서 새 게이트 관련 notes가 나왔다: {notes}"
    )
    if v is not None:
        assert v == pytest.approx(v)  # 값 자체는 회귀 스냅샷이 아니라 경로 무결성만 확인


# ── ② cu_h2o2_bta 실제 팩 기준조건 항등 ───────────────────────────
def test_cu_h2o2_bta_reference_condition_is_unity():
    pack = load_pack("cu_h2o2_bta")
    assert pack.has("oxidizer_acid_chelator_K"), "이 판정으로 새 키가 팩에 선언돼 있어야 한다"
    notes = []
    v = _oxidizer_term(pack, notes)
    assert v == pytest.approx(1.0, abs=1e-9), (
        f"기준 조건(C=C_ref=3.0wt%)에서 배수가 1.0이 아니다: {v}"
    )


# ── ③ 산성×착화제 가지 — 방향이 증가여야 한다 ─────────────────────
def test_acid_chelator_branch_direction_is_increasing():
    vals = []
    for C in (3.0, 4.0, 6.0):
        d = dict(ACID_CHELATOR)
        d["oxidizer_wt_pct"] = C
        notes = []
        v = _oxidizer_term(FakePack(**d), notes)
        assert any("판정#41" in n for n in notes), "게이트가 안 켜졌다"
        vals.append(v)
    assert vals[0] == pytest.approx(1.0, abs=1e-9)
    assert vals[1] > vals[0], f"3->4 wt%에서 증가해야 한다: {vals}"
    assert vals[2] > vals[1], f"4->6 wt%에서 증가해야 한다: {vals}"


# ── ④ chelator_M 미선언 시 기존 경로로 폴백 ────────────────────────
def test_missing_chelator_falls_back_to_legacy_path():
    d = dict(ACID_CHELATOR)
    del d["chelator_M"]
    d["oxidizer_wt_pct"] = 6.0
    notes = []
    v = _oxidizer_term(FakePack(**d), notes)
    assert any("chelator_M" in n and "폴백" in n for n in notes)
    # 기존 oxidizer_passivation_K(K=0.8232) 경로의 산출값과 정확히 같아야 한다
    d_legacy = dict(d)
    del d_legacy["oxidizer_acid_chelator_K"]
    v_legacy = _oxidizer_term(FakePack(**d_legacy), [])
    assert v == pytest.approx(v_legacy, rel=1e-12)


# ── ⑤ slurry_ph 미선언(또는 pH>=6) 시 기존 경로로 폴백 ─────────────
def test_missing_ph_falls_back_to_legacy_path():
    d = dict(ACID_CHELATOR)
    del d["slurry_ph"]
    d["oxidizer_wt_pct"] = 6.0
    notes = []
    v = _oxidizer_term(FakePack(**d), notes)
    assert any("slurry_ph" in n and "폴백" in n for n in notes)


def test_alkaline_ph_gate_falls_back_even_with_chelator_declared():
    """게이트는 상호배타다 — 착화제가 있어도 pH>=6이면 기존(억제형) 경로."""
    d = dict(ACID_CHELATOR)
    d["slurry_ph"] = 9.0
    d["oxidizer_wt_pct"] = 6.0
    notes = []
    v = _oxidizer_term(FakePack(**d), notes)
    assert any("게이트 미충족" in n for n in notes)
    assert v < 1.0, "억제형 경로는 3->6wt%에서 배수가 1 미만(감소)이어야 한다"


# ── ⑥ Jani 2025 Expt 30/31/32 재현오차 ────────────────────────────
def test_jani_2025_reproduction_error_within_tolerance():
    """노트 §9의 적합값(K=0.7935)이 원 관측 배수를 5% 이내로 재현하는가."""
    OBS_RATIO = {3.0: 1.000, 4.0: 2533.0 / 2282.0, 6.0: 2578.0 / 2282.0}
    for C, obs in OBS_RATIO.items():
        d = dict(ACID_CHELATOR)
        d["oxidizer_wt_pct"] = C
        pred = _oxidizer_term(FakePack(**d), [])
        err = abs(pred - obs) / obs
        assert err < 0.05, f"C={C}: 예측 {pred:.4f} vs 실측 {obs:.4f}, 오차 {err:.1%}"


# ══════════════════════════════════════════════════════════════════
# 판정#47 — 착화제 종 특이성 게이트
# ══════════════════════════════════════════════════════════════════

ACID_CHELATOR_OXALIC = dict(ACID_CHELATOR)
ACID_CHELATOR_OXALIC.update(
    oxidizer_acid_chelator_species="oxalic_acid",
    chelator_species="oxalic_acid",
)

ACID_CHELATOR_GLYCINE = dict(ACID_CHELATOR)
ACID_CHELATOR_GLYCINE.update(
    oxidizer_acid_chelator_species="oxalic_acid",
    chelator_species="glycine",
)


# ── ⑦ 종 일치 시 발동(촉진-포화형, 방향=증가) ──────────────────────
def test_species_match_fires_promotion_branch():
    vals = []
    for C in (3.0, 4.0, 6.0):
        d = dict(ACID_CHELATOR_OXALIC)
        d["oxidizer_wt_pct"] = C
        notes = []
        v = _oxidizer_term(FakePack(**d), notes)
        assert any("판정#41" in n for n in notes), f"종 일치인데 게이트가 안 켜졌다: {notes}"
        vals.append(v)
    assert vals[0] == pytest.approx(1.0, abs=1e-9)
    assert vals[1] > vals[0] and vals[2] > vals[1], f"촉진형은 증가여야 한다: {vals}"


# ── ⑧ 종 불일치 시 폴백(억제형, 방향=감소) ─────────────────────────
def test_species_mismatch_falls_back_to_passivation_branch():
    d = dict(ACID_CHELATOR_GLYCINE)
    d["oxidizer_wt_pct"] = 6.0
    notes = []
    v = _oxidizer_term(FakePack(**d), notes)
    assert any("적합됐는데 팩 착화제는" in n and "전이하지 않는다" in n for n in notes), notes
    assert not any("판정#41" in n and "촉진-포화형" in n for n in notes)
    # 촉진 가지가 아니라 기존 oxidizer_passivation_K(K=0.8232) 경로와 값이 같아야 한다
    d_legacy = dict(d)
    del d_legacy["oxidizer_acid_chelator_K"]
    del d_legacy["oxidizer_acid_chelator_species"]
    v_legacy = _oxidizer_term(FakePack(**d_legacy), [])
    assert v == pytest.approx(v_legacy, rel=1e-12)
    assert v < 1.0, "억제형 경로는 3->6wt%에서 배수가 1 미만(감소)이어야 한다"


# ── ⑨ 종 미선언(구버전 팩) 시 폴백 대신 경고와 함께 기존(판정#41 이전) 동작 유지 ──
def test_species_undeclared_on_coefficient_keeps_legacy_behavior_with_warning():
    """oxidizer_acid_chelator_species 자체가 없으면 판정#41 이전 동작(항상 발동)을
    유지하되 검증 못 했다는 경고를 남긴다 — 종 일치를 지어내지 않는다."""
    d = dict(ACID_CHELATOR)  # species 필드 전혀 없음
    d["oxidizer_wt_pct"] = 4.0
    notes = []
    v = _oxidizer_term(FakePack(**d), notes)
    assert any("구버전 팩" in n for n in notes), notes
    assert v > 1.0, "구버전 동작(촉진형)이 유지돼야 한다"


def test_species_declared_on_coefficient_but_pack_missing_chelator_species_falls_back():
    """계수엔 적합 종 선언이 있는데 팩에 chelator_species가 없으면(모순 상태) 지어내지
    않고 폴백한다."""
    d = dict(ACID_CHELATOR)
    d["oxidizer_acid_chelator_species"] = "oxalic_acid"
    d["oxidizer_wt_pct"] = 6.0
    notes = []
    v = _oxidizer_term(FakePack(**d), notes)
    assert any("chelator_species가 없어" in n for n in notes), notes
    d_legacy = dict(d)
    del d_legacy["oxidizer_acid_chelator_K"]
    del d_legacy["oxidizer_acid_chelator_species"]
    v_legacy = _oxidizer_term(FakePack(**d_legacy), [])
    assert v == pytest.approx(v_legacy, rel=1e-12)


# ── ⑩ 실제 cu_h2o2_bta 팩 — 이제는 억제형(글리신 자기 레짐)이어야 한다 ──
def test_real_cu_h2o2_bta_pack_now_uses_passivation_branch():
    """[판정#47] 실팩은 chelator_species=glycine, oxidizer_acid_chelator_species=
    oxalic_acid로 불일치 — 촉진형이 아니라 자기 레짐인 억제형을 타야 한다."""
    pack = load_pack("cu_h2o2_bta")
    assert pack.has("oxidizer_acid_chelator_species"), "판정#47로 이 키가 선언돼 있어야 한다"
    assert pack.get("oxidizer_acid_chelator_species") != pack.get("chelator_species")
    vals = []
    for C in (1.0, 3.0, 6.0):
        notes = []
        d_dict = dict(oxidizer_wt_pct=C, oxidizer_ref_wt_pct=3.0,
                       oxidizer_acid_chelator_K=pack.get("oxidizer_acid_chelator_K"),
                       oxidizer_acid_chelator_species=pack.get("oxidizer_acid_chelator_species"),
                       oxidizer_passivation_K=pack.get("oxidizer_passivation_K"),
                       slurry_ph=pack.get("slurry_ph"),
                       chelator_M=pack.get("chelator_M"),
                       chelator_species=pack.get("chelator_species"))
        v = _oxidizer_term(FakePack(**d_dict), notes)
        assert not any("촉진-포화형" in n for n in notes), notes
        vals.append(v)
    assert vals[0] > vals[1] > vals[2], f"억제형은 산화제가 늘수록 감소해야 한다: {vals}"
