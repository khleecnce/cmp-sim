"""cu_alkaline_benzenesulfonic 연마입자 축(κ 입경·농도 지수, Δ D99·손상지수) 회귀.

판정#71(2026-09-19): 완성격자 미충족 3칸(C1 Δ · C2 κ · C2 Γ) 전진 과제 고정.
근거 노트: knowledge/cmp/cu-alkaline-benzenesulfonic-abrasive-axis-kappa-delta.md

이 파일이 고정하는 것:
  (a) 기준조건(abrasive_size_nm=abrasive_ref_size_nm, abrasive_wt_pct=abrasive_ref_wt_pct)
      에서 κ의 size·conc 항 배수가 정확히 1.0이다(이중계상 방지 계약).
  (b) Δ가 더 이상 unmodeled가 아니고(modeled 또는 partial), d99가 드라이버로 잡힌다.
  (c) 입경(abrasive_size_nm)을 흔들어도 κ는 불변(null 결과, n=0.0)이고,
      D99(abrasive_d99_nm)를 흔들면 Δ는 예상 방향(증가->증가)으로 움직인다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe          # noqa: E402
from sim.factors import _f_kappa, _f_delta  # noqa: E402
from sim.params import load_pack       # noqa: E402

PACK = "cu_alkaline_benzenesulfonic"


def _resolve(**overrides):
    return Recipe(pack=PACK, pack_overrides=overrides).resolve()


def test_kappa_size_and_conc_terms_are_1_at_baseline():
    """(a) 기준조건에서 κ의 size·conc 항 배수가 정확히 1.0 — 이중계상 방지 계약."""
    rr = _resolve()
    f = _f_kappa(rr)
    assert f.terms["size"] == 1.0, f.terms
    assert f.terms["conc"] == 1.0, f.terms


def test_kappa_size_and_conc_confidence_estimated_not_unverified():
    """κ가 unverified에서 실제로 벗어났는지(값 없음이 아니라 근거가 약함으로 승격).

    판정#80(2026-09-20): abrasive_conc_exponent는 Cooper 2002(Cu 직접 실측,
    doi:10.1149/1.1517772)로 literature 승격. abrasive_size_exponent는 실측
    다리(알칼리·무억제제 Cu 입경 스윕)를 확보하지 못해 estimated 유지
    (knowledge/cmp/kappa-cu-alkaline-shape-exponents-round2.md).
    """
    pk = load_pack(PACK)
    assert pk.has_own("abrasive_size_exponent")
    assert pk.has_own("abrasive_conc_exponent")
    assert pk.param("abrasive_size_exponent").confidence == "estimated"
    assert pk.param("abrasive_conc_exponent").confidence == "literature"
    rr = _resolve()
    f = _f_kappa(rr)
    assert f.confidence != "unverified"


def test_delta_no_longer_unmodeled_and_d99_is_driver():
    """(b) Δ가 unmodeled를 벗어나고 abrasive_d99_nm이 드라이버로 잡힌다."""
    rr = _resolve()
    f = _f_delta(rr)
    assert f.status in ("modeled", "partial"), f.status
    assert "abrasive_d99_nm" in f.drivers
    assert f.value is not None
    assert "d99" in f.terms


def test_kappa_size_term_invariant_to_abrasive_size_nm_null_result():
    """(c) 입경 지수가 0.0(null 결과)이므로 abrasive_size_nm을 흔들어도 κ의
    size 항은 불변이다 — n=0.0이 '모른다'가 아니라 '효과 없음'이라는 검증된
    결론을 반영한다."""
    rr_small = _resolve(abrasive_size_nm=30.0)
    rr_large = _resolve(abrasive_size_nm=90.0)
    f_small = _f_kappa(rr_small)
    f_large = _f_kappa(rr_large)
    assert f_small.terms["size"] == 1.0
    assert f_large.terms["size"] == 1.0
    assert f_small.terms["size"] == f_large.terms["size"]


def test_delta_increases_with_abrasive_d99_nm():
    """(c) D99를 키우면 Δ는 예상 방향(증가)으로 움직인다(양의 거듭제곱, n=2.54>0)."""
    pk = load_pack(PACK)
    d99_ref = float(pk.get("abrasive_ref_d99_nm"))

    rr_base = _resolve()
    rr_bigger = _resolve(abrasive_d99_nm=d99_ref * 2.0)
    rr_smaller = _resolve(abrasive_d99_nm=d99_ref * 0.5)

    f_base = _f_delta(rr_base)
    f_bigger = _f_delta(rr_bigger)
    f_smaller = _f_delta(rr_smaller)

    assert f_base.value == 1.0
    assert f_bigger.value > f_base.value
    assert f_smaller.value < f_base.value


def test_delta_damage_exponent_inherited_from_parent_unchanged():
    """damage_exponent는 부모(cu_h2o2_bta)와 값·등급 모두 동일 상속(막질=Cu 불변)."""
    pk_new = load_pack(PACK)
    pk_parent = load_pack("cu_h2o2_bta")
    assert float(pk_new.get("damage_exponent")) == float(pk_parent.get("damage_exponent")) == 2.54
    assert pk_new.param("damage_exponent").confidence == pk_parent.param("damage_exponent").confidence == "estimated"
