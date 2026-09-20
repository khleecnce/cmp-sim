import pytest
"""sic_alumina_kmno4 연마입자 정체성 상속 결함 수정 — 회귀 고정 (EVIDENCE-RULES.md 판정#59).

배경: sim/factors.py::_f_chi 의 분기 판정 키 `abrasive` 를 sic_alumina_kmno4 팩이
부모(sic_ceria_h2o2)의 'ceria' 를 own 없이 상속하고 있었다. 그 결과 (a) 알루미나
슬러리에 세리아 chemical tooth(_ceria_term)가 켜져 있었고 (b) pH 분기가 세리아
IEP 창으로 들어가 wafer_iep_ph 부재로 skip → pH 축이 통째로 죽어 있었다.

수정: 팩이 `abrasive: alumina` 를 자기선언한다. 그리고 `_f_chi` 의 2차 패스(아무도
own이 아닐 때의 폴백)에 "그 pH 메커니즘의 고유 계수를 실제로 선언한 조상 팩의
abrasive가 이 팩과 다르면 그 분기를 쓰지 않는다"는 일반 규칙을 추가했다 — 안 그러면
폴백이 오이드_silica 소유 ph_peak(정점 pH=11, 실리카 전용)로 떨어져 산성
알루미나/KMnO4계에 실리카 곡선을 씌우는 사고가 난다(노트 §2 실측 확인).

이 파일이 고정하는 것:
  (a) 나머지 5팩(cu_h2o2_bta·oxide_silica·sic_ceria_h2o2·sti_ceria·w_fe_oxidizer)의
      χ 분기 선택과 수치는 **비트 단위로 불변**이어야 한다(값은 수정 전 상태를
      그대로 스냅샷했다 — git stash로 대조 확인 완료).
  (b) sic_alumina_kmno4는 abrasive='alumina'를 own으로 선언한다.
  (c) sic_alumina_kmno4에서 ceria_tooth 항이 사라진다(더 이상 세리아 화학을 안 쓴다).
  (d) sic_alumina_kmno4의 pH 분기는 재료 불일치로 전부 막혀 pH 항이 없다(갭으로 남음,
      실리카 ph_peak·세리아 ph_softening 어느 쪽도 새지 않는다) — notes에 이유가 남는다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe          # noqa: E402
from sim.factors import _f_chi         # noqa: E402
from sim.params import load_pack       # noqa: E402


def _chi(pack, **overrides):
    rr = Recipe(pack=pack, pack_overrides=overrides).resolve()
    return _f_chi(rr)


# (pack, overrides, expected chi.value, expected term-name set) — 수정 전 상태에서
# 그대로 캡처한 값(git stash 대조로 수정 후에도 동일함을 확인했다).
# ⚠ 2026-09-19 판정#75 갱신 — cu_h2o2_bta 의 기대 term 집합에
# `carboxylate_promoter` 를 추가했다. 이 테스트가 지키는 성질은
# "판정#59 의 분기 수정이 다른 5팩의 χ 를 건드리지 않았다"이고, 그 성질은
# **깨지지 않았다**: 두 cu 항목의 기대 **값**(1.0 / 1.153499078778735)은 소수점
# 끝자리까지 그대로다. 판정#75 가 추가한 옥살산 촉진 항은 이 팩의 기준 조성
# (promoter_M == promoter_ref_M == 0)에서 항등적으로 1.0 이라 곱해도 값이 안
# 변하기 때문이다(그 항등성 자체는 tests/test_factors.py::
# test_chi_carboxylate_promoter_reference_is_unity 가 따로 고정한다).
# 즉 여기서 바뀐 것은 "χ 가 몇으로 계산되는가"가 아니라 "χ 가 몇 개의 항으로
# 이루어져 있는가"이고, 후자는 축을 새로 배선하면 당연히 늘어난다.
# 값까지 함께 움직였다면 그때는 갱신이 아니라 회귀로 다뤘어야 한다.
_FIVE_PACK_SNAPSHOT = [
    ("cu_h2o2_bta", {}, 1.0, {"oxidizer", "ph_cu_acidic", "carboxylate_promoter"}),
    ("cu_h2o2_bta", {"slurry_ph": 3.0}, 1.153499078778735,
     {"oxidizer", "ph_cu_acidic", "carboxylate_promoter"}),
    ("oxide_silica", {}, 1.0, {"ph_peak"}),
    ("oxide_silica", {"slurry_ph": 9.0}, 0.607491021036429, {"ph_peak"}),
    ("sic_ceria_h2o2", {}, 1.0, {"ceria_tooth", "oxidizer", "ph_softening"}),
    ("sic_ceria_h2o2", {"slurry_ph": 9.0}, 0.691587288453854,
     {"ceria_tooth", "oxidizer", "ph_softening"}),
    ("sic_ceria_h2o2", {"slurry_ph": 11.0}, 1.6323981793187774,
     {"ceria_tooth", "oxidizer", "ph_softening"}),
    ("sti_ceria", {}, 1.0, {"ceria_tooth", "ph_ceria_window"}),
    ("sti_ceria", {"slurry_ph": 5.0}, 1.0400600259129777, {"ceria_tooth", "ph_ceria_window"}),
    ("w_fe_oxidizer", {}, 1.0, {"oxidizer", "ph_w_acidic"}),
    ("w_fe_oxidizer", {"slurry_ph": 2.0}, 1.059873964882034, {"oxidizer", "ph_w_acidic"}),
]


def test_five_other_packs_chi_bit_unchanged():
    for pack, overrides, want_val, want_terms in _FIVE_PACK_SNAPSHOT:
        f = _chi(pack, **overrides)
        assert f.value == want_val, (pack, overrides, f.value, want_val)
        assert set(f.terms.keys()) == want_terms, (pack, overrides, f.terms)


def test_sic_alumina_kmno4_declares_alumina_own():
    pk = load_pack("sic_alumina_kmno4")
    assert pk.get("abrasive") == "alumina"
    assert pk.has_own("abrasive")


def test_sic_alumina_kmno4_ceria_tooth_gone():
    f = _chi("sic_alumina_kmno4")
    assert "ceria_tooth" not in f.terms


def test_sic_alumina_kmno4_ph_branch_blocked_not_leaked():
    """판정#59 의 본질은 유지된다 — **남의 재료 pH 곡선은 여전히 안 샌다.**

    ⚠ 2026-09-18 판정#61 로 갱신: 이 팩은 이제 자기 재료계 문헌
    (Chen 2020, DOI 10.1134/S1070427220060099)에서 온 `ph_sic_kmno4_acidic`
    분기를 **직접 선언**해 쓴다. 그래서 (a) 차단 목록에서 검사하는 것은
    여전히 '남의 재료 계수 5종'이고, (b) 판정#59 의 차단 note 는 더 이상
    발생하지 않는다(1차 패스에서 own 계수로 선택이 끝나 2차 패스에 닿지 않는다).
    아래 마지막 assert 를 '판정#59 문구 존재'에서 '자기 분기 선택'으로 바꾼다 —
    지키려던 성질(남의 곡선 차단)은 그대로다.
    """
    f = _chi("sic_alumina_kmno4")
    leaked = {"ph_peak", "ph_softening", "ph_ceria_window",
              "ph_w_acidic", "ph_cu_acidic"} & set(f.terms.keys())
    assert not leaked, f"남의 재료 pH 곡선이 샜다: {leaked}"
    assert "ph_sic_kmno4_acidic" in f.terms, f.terms


def test_sic_alumina_kmno4_ph_axis_now_live_via_own_material_literature():
    """판정#61 로 **의도적으로 뒤집힌** 계약 — 이 테스트는 원래
    "pH 축이 여전히 무반응"을 고정하고 있었다.

    판정#59 가 그 무반응을 '정확한 갭'(알루미나계 pH 계수 미확보)이라 기록했고,
    판정#61 이 그 계수를 자기 재료계 문헌(Chen 2020, 6H-SiC + 0.05 M KMnO4 +
    2 wt% Al2O3, pH 2~10 단조 감소)에서 확보해 배선했다. 갭이 메워졌으므로
    '무반응' 고정은 더 이상 지킬 성질이 아니다 — 대신 **방향과 기준 1.0** 을 고정한다.
    근거 노트: knowledge/cmp/sic-kmno4-acidic-ph-decay-chen2020.md
    """
    chi_2 = _chi("sic_alumina_kmno4", slurry_ph=2.0).value
    chi_6 = _chi("sic_alumina_kmno4", slurry_ph=6.0).value
    assert chi_2 > chi_6, (chi_2, chi_6)      # 산성일수록 MnO4- 산화력이 크다
    assert _chi("sic_alumina_kmno4").value == pytest.approx(1.0, abs=1e-9)
