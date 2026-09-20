# -*- coding: utf-8 -*-
"""정체성 상속 감사 도구의 계약 고정 (EVIDENCE-RULES.md 판정#60).

이 파일이 지키는 것:
  (a) 도구가 판정#59 가 실제로 잡아낸 유형을 잡는다(회귀 방지).
  (b) 오탐을 내지 않는다 — 패드 물성처럼 재료축과 무관한 키는 신고하지 않는다.
  (c) 현재 신고 목록이 **줄지 않는다**(누가 축 분류를 지우면 실패한다).
      늘어나는 것은 막지 않는다 — 새 팩이 생기면 신고가 느는 게 정상이다.
      단, 결함이 실제로 해소돼 줄어드는 것은 정당하다 — 그 경우 _KNOWN 에서 빼되
      해소 상태를 별도 테스트로 고정한다.
  (d) 도구가 MRR 을 바꾸지 않는다(순수 감사 도구다).
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe, simulate           # noqa: E402
from sim.params import load_pack                  # noqa: E402
from tools.audit_identity_inheritance import (    # noqa: E402
    AXIS_NONE, IDENTITY_KEYS, _axis_of, audit,
)

# 판정#60 시점의 실측 신고 목록(팩, 키). 이 조합들은 재료가 실제로 어긋난다.
#
# 입경 5키(abrasive_size_nm / abrasive_ref_size_nm / abrasive_size_peak_nm /
# abrasive_size_exp_below_peak / abrasive_size_exp_above_peak)는 2026-09-18,
# 판정#60 §5 후속으로 sic_alumina_kmno4 가 세리아 상속을 끊고 Su et al. 2011
# (DOI 10.1016/j.proeng.2011.11.2673) 근거로 자기선언(own)하여 해소됐다 —
# knowledge/cmp/alumina-abrasive-size-mrr-relation.md 참조. 해소 상태는
# test_alumina_pack_size_axis_is_self_declared 로 고정한다.
_KNOWN = {
    ("sic_alumina_kmno4", "abrasive_iep_ph"),
    ("sic_alumina_kmno4", "ce3_fraction"),
    ("sic_alumina_kmno4", "ceria_tooth_gain"),
    ("sic_alumina_kmno4", "ceria_tooth_exponent"),
}

# ⚠ 2026-09-19 학습총괄 — oxidizer_langmuir_K / _species 를 이 목록에서 **뺐다.**
# 원래 여기 있던 이유는 그 두 키가 부모(sic_ceria_h2o2, H2O2 로 적합)에서 상속돼
# 재료 불일치로 신고되던 상태였기 때문이다. 그 뒤 이 팩이 자기 재료계 문헌
# (Gong 2024, 4H-SiC×α-Al2O3×KMnO4)에서 K=2.28 을 역산해 **자기선언**했으므로
# 더 이상 상속이 아니고, 감사가 신고하지 않는 것이 정답이다.
#
# 교훈(이 클래스의 실패가 이번 회차에만 3건 나왔다): 감사 테스트에 "지금 신고되는
# 것"을 목록으로 박으면, 그 결함을 **정당하게 고치는 순간** 테스트가 깨진다.
# 고정할 계약은 '현재 신고 목록'이 아니라 '남의 재료 값이 상속된 채로 쓰이면
# 신고된다' 이다. 아래 회귀 가드가 그 형태로 다시 쓴 것이다.
_RESOLVED_BY_SELF_DECLARATION = {
    ("sic_alumina_kmno4", "oxidizer_langmuir_K"),
    ("sic_alumina_kmno4", "oxidizer_langmuir_species"),
}

# 2026-09-18, 판정#63 — ph_peak/ph_mrr_at_peak_rel 을 연마입자축으로 새로 분류하며
# 드러난 신고 6건. EVIDENCE-RULES 판정#59 ③이 이미 "abrasive: alumina 만 선언하면
# ph_peak(오이드_silica 소유, 정점 pH=11 실리카 전용)로 떨어져 실리카 곡선을 산성
# 알루미나계에 씌운 오염값이 나온다"를 실측으로 확인해 둔 바로 그 경로다 — 셋 다
# 현재는 sim/factors.py::_f_chi has_own 우선순위(판정#34)가 다른 own pH 분기를
# 먼저 골라 비활성(dead)이지만, 그 own 키가 사라지면 즉시 이 오염이 되살아난다.
_KNOWN_PH_PEAK_AXIS = {
    ("sic_alumina_kmno4", "ph_peak"),
    ("sic_alumina_kmno4", "ph_mrr_at_peak_rel"),
    ("sic_ceria_h2o2", "ph_peak"),
    ("sic_ceria_h2o2", "ph_mrr_at_peak_rel"),
    ("sti_ceria", "ph_peak"),
    ("sti_ceria", "ph_mrr_at_peak_rel"),
}
_KNOWN |= _KNOWN_PH_PEAK_AXIS


def test_audit_reports_known_material_mismatches():
    got = {(m["pack"], m["key"]) for m in audit()["mismatches"]}
    missing = _KNOWN - got
    assert not missing, f"감사가 알려진 재료 불일치를 놓쳤다: {sorted(missing)}"


def test_resolved_keys_are_self_declared_not_merely_unreported():
    """해소된 키는 '신고 안 됨'이 아니라 '자기선언됨'이어야 한다.

    목록에서 뺐다는 것만으로는 불충분하다 — 감사가 조용해진 이유가 (a) 팩이
    자기 값을 선언해서인지 (b) 감사기가 그 키를 못 보게 돼서인지 구분되지
    않으면, 규칙을 무력화해 위반을 없애는 일이 조용히 일어난다.
    그래서 **팩 쪽에서** 자기선언을 직접 확인하고, 동시에 그 키가 상속으로
    되돌아가면 감사가 다시 울어야 한다는 계약을 건다.
    """
    from sim.params import load_pack

    got = {(m["pack"], m["key"]) for m in audit()["mismatches"]}
    for pack_name, key in _RESOLVED_BY_SELF_DECLARATION:
        pk = load_pack(pack_name)
        assert pk.has_own(key), (
            f"{pack_name}:{key} 가 자기선언이 아닌데 감사에서도 빠졌다 — "
            "결함이 고쳐진 게 아니라 감사기가 눈을 감은 것이다.")
        assert (pack_name, key) not in got, (
            f"{pack_name}:{key} 는 자기선언인데 상속으로 신고됐다 — 감사기 오탐.")


def test_audit_does_not_flag_pad_or_tool_keys():
    """패드·장비 물성은 연마입자/막질과 무관하다 — 신고되면 오탐이다."""
    flagged = {m["key"] for m in audit()["mismatches"]}
    for k in flagged:
        head = k.split("_")[0]
        assert head not in {"pad", "cond", "platen", "rpm", "sfr", "groove",
                            "retaining", "cof", "asperity", "center", "edge"}, k


def test_ceria_specific_params_are_flagged_for_alumina_pack():
    """판정#59 의 본질 — 알루미나 팩이 세리아 고유 계수를 물려받는 것."""
    ms = [m for m in audit()["mismatches"]
          if m["pack"] == "sic_alumina_kmno4" and m["key"].startswith("ce")]
    assert ms, "세리아 고유 계수(ce3_*/ceria_*) 상속이 신고되지 않았다"
    for m in ms:
        assert m["axis"] == "abrasive"
        assert m["mine"] == "alumina" and m["theirs"] == "ceria"


def test_axis_classification_is_explicit_not_guessed():
    """축을 모르는 키는 None 을 돌려야 한다 — 추측해서 신고하지 않는다."""
    assert _axis_of("pad_ra_m") is None
    assert _axis_of("kp_m_per_pa") is None
    for k in AXIS_NONE:
        assert _axis_of(k) is None, k
    # 정체성 키 자체는 자기 축이다(판정#59 가 걸린 자리)
    for k in IDENTITY_KEYS:
        assert _axis_of(k) == k


def test_audit_is_read_only_mrr_unchanged():
    packs = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2",
             "sti_ceria", "w_fe_oxidizer", "sic_alumina_kmno4"]
    before = {p: float(np.mean(simulate(Recipe(pack=p)).mrr_nm_per_min))
              for p in packs}
    audit()
    after = {p: float(np.mean(simulate(Recipe(pack=p)).mrr_nm_per_min))
             for p in packs}
    assert before == after


def test_alumina_pack_size_axis_is_self_declared():
    """판정#60 §5 후속(2026-09-18) — 입경 5키는 이제 세리아 상속이 아니라
    Su et al. 2011(DOI 10.1016/j.proeng.2011.11.2673) 근거의 자기선언 값이다.
    knowledge/cmp/alumina-abrasive-size-mrr-relation.md §4 표와 절대값으로 일치해야
    누가 YAML 에서 5키를 지워 상속으로 되돌려도 이 테스트가 잡아낸다.
    """
    pk = load_pack("sic_alumina_kmno4")
    expected = {
        "abrasive_size_nm": 500.0,
        "abrasive_ref_size_nm": 500.0,
        "abrasive_size_peak_nm": 2500.0,
        "abrasive_size_exp_below_peak": 0.3092888377,
        "abrasive_size_exp_above_peak": -0.0664695242,
    }
    for key, value in expected.items():
        assert pk.has_own(key), f"'{key}'가 자기선언이 아니다(상속으로 되돌아갔다)"
        assert pk.get(key) == pytest.approx(value, rel=1e-6), key

    got = {(m["pack"], m["key"]) for m in audit()["mismatches"]}
    for key in expected:
        assert ("sic_alumina_kmno4", key) not in got, (
            f"'{key}'가 다시 신고됐다 — 해소가 되돌려졌다"
        )


def test_unclassified_keys_are_reported_separately_not_silently_dropped():
    """감사 사각지대는 숨기지 않고 별도 목록으로 낸다."""
    res = audit()
    assert "unclassified" in res
    # 사각지대가 신고 목록에 섞여 들어가지 않는다
    flagged = {(m["pack"], m["key"]) for m in res["mismatches"]}
    for u in res["unclassified"]:
        assert (u["pack"], u["key"]) not in flagged


def test_ph_peak_axis_is_abrasive_2026_09_18():
    """판정#63 — ph_peak/ph_mrr_at_peak_rel 은 연마입자축(Li 2021 실리카 전용 곡선).

    같은 문헌·같은 곡선의 두 키가 다른 축으로 갈라지면 그 자체가 결함이다
    (과제 지시 — "다르게 분류하면 그 자체가 결함이다").
    """
    assert _axis_of("ph_peak") == "abrasive"
    assert _axis_of("ph_mrr_at_peak_rel") == "abrasive"

    got = {(m["pack"], m["key"]) for m in audit()["mismatches"]}
    assert _KNOWN_PH_PEAK_AXIS <= got, (
        "ph_peak/ph_mrr_at_peak_rel 연마입자축 신고가 사라졌다 — "
        "판정#59 ③ 이 실측 확인한 오염 경로가 다시 사각지대로 돌아갔다"
    )


def test_ph_softening_per_unit_axis_is_film_and_silent_for_sic_alumina():
    """판정#63 — ph_softening_per_unit 은 막질축(SiC 표면화학, sic_ceria_h2o2.yaml
    note: "다른 재료계로 옮기지 마라"는 것은 abrasive/oxidizer 축을 가리킨 말이고,
    film(SiC)은 소유 조상과 sic_alumina_kmno4 사이에 실제로 일치한다 — 그래서
    신고되지 않는 것이 정확한 판정이지, 사각지대로 남아 우연히 조용한 게 아니다.
    """
    assert _axis_of("ph_softening_per_unit") == "film"
    me = load_pack("sic_alumina_kmno4").get_or("film", None)
    owner = load_pack("sic_ceria_h2o2").get_or("film", None)
    assert me == owner == "sic_4h", "막질이 실제로 일치해야 이 침묵이 정당하다"

    got = {(m["pack"], m["key"]) for m in audit()["mismatches"]}
    assert ("sic_alumina_kmno4", "ph_softening_per_unit") not in got


def test_pad_ra_m_and_bulk_slurry_viscosity_stay_axis_none():
    """판정#63 — 패드/장비·슬러리 전체 물성은 AXIS_NONE 이 맞다(사각지대가 아니라
    적극적 판정). AXIS_NONE 에 있다는 것은 신고 대상에서 빠진다는 뜻이므로 값
    자체가 여전히 유효한지(예: 도구 리팩터로 키가 사라지지 않았는지) 함께 고정한다.
    """
    assert _axis_of("pad_ra_m") is None
    assert _axis_of("slurry_viscosity_pa_s") is None
    assert "pad_ra_m" in AXIS_NONE
    assert "slurry_viscosity_pa_s" in AXIS_NONE

    got = {(m["pack"], m["key"]) for m in audit()["mismatches"]}
    for pack, key in got:
        assert key not in {"pad_ra_m", "slurry_viscosity_pa_s"}, (pack, key)


def test_unclassified_axis_blind_spot_is_now_empty():
    """과제 완료 조건 — 이번 회차 전 4키(pad_ra_m·ph_peak·ph_mrr_at_peak_rel·
    ph_softening_per_unit)가 전부 판정됐다. 새 사각지대가 생기면(새 팩·새 키) 이
    테스트가 아니라 --unclassified 로 드러나야 정상이라, 여기서는 '지금 아는 4키가
    더는 사각지대에 없다'만 고정한다(전체 unclassified==0을 강제하면 미래의 정당한
    사각지대까지 이 테스트를 깨뜨린다).
    """
    res = audit()
    unclassified_keys = {u["key"] for u in res["unclassified"]}
    resolved = {"pad_ra_m", "ph_peak", "ph_mrr_at_peak_rel", "ph_softening_per_unit"}
    assert not (resolved & unclassified_keys), resolved & unclassified_keys
