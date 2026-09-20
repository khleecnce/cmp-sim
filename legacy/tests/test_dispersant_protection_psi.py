"""ψ(표면 보호도) 분산제 흡착 경로 계약 테스트.

브리프: oxide_silica/sic_ceria_h2o2/sti_ceria 세 팩은 inhibitor_mM(금속 부동태
억제제)이 없어 ψ가 unmodeled로 신고됐다. ψ의 정의를 '표면 흡착 보호'로 넓혀
폴리머 분산제 흡착(PVA/PVP) 경로를 추가했다 — 이 테스트는 그 경로가
Li et al. 2021 §6 실측값을 그대로 재현하는지, unmodeled였던 세 팩이
modeled/partial로 바뀌었는지를 계약으로 고정한다. 새 숫자는 만들지 않는다.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.chemistry import _dispersant_protection_term          # noqa: E402
from sim.engine import Recipe                                   # noqa: E402
from sim.factors import compute_factors                         # noqa: E402
from sim.params import ParamPack, Param                         # noqa: E402


def _fake_pack(**params) -> ParamPack:
    return ParamPack(name="fake", params={
        k: Param(key=k, value=v, confidence="literature") for k, v in params.items()
    })


# ═══════════════════ 1~4: _dispersant_protection_term 순수함수 계약

def test_pva_relative_mrr_matches_li2021():
    notes = []
    v = _dispersant_protection_term(_fake_pack(dispersant_type="PVA"), notes)
    assert v == pytest.approx(2604.0 / 2700.0, rel=0.005)


def test_pvp_relative_mrr_matches_li2021():
    notes = []
    v = _dispersant_protection_term(_fake_pack(dispersant_type="PVP"), notes)
    assert v == pytest.approx(2486.0 / 2700.0, rel=0.005)


@pytest.mark.parametrize("kind", ["PAA", "PAM"])
def test_paa_pam_negligible_inhibition(kind):
    notes = []
    v = _dispersant_protection_term(_fake_pack(dispersant_type=kind), notes)
    assert v == pytest.approx(1.0, abs=1e-9)


def test_no_dispersant_type_returns_none():
    notes = []
    v = _dispersant_protection_term(_fake_pack(), notes)
    assert v is None


# ═══════════════════ 5~6: factors.compute_factors() 통합 — unmodeled 해소

def test_oxide_silica_psi_is_modeled():
    factors = compute_factors(Recipe(pack="oxide_silica").resolve())
    psi = factors["psi"]
    assert psi.status == "modeled"


@pytest.mark.parametrize("pack", ["sti_ceria", "sic_ceria_h2o2"])
def test_ceria_packs_psi_is_modeled_via_cross_system_transfer(pack):
    factors = compute_factors(Recipe(pack=pack).resolve())
    psi = factors["psi"]
    assert psi.status in ("modeled", "partial")
    # 분산제 이산 항의 등급은 literature (판정#15). 2026-09-14 ψ 농도축 배선 이후
    # sti_ceria 는 Park 2003 회귀(그림 판독·(K,n,k) 묶음 비식별)가 약한 고리라 팩터
    # 전체 등급은 estimated 로 내려간다 — 이것은 퇴보가 아니라 새 항이 정직하게 자기
    # 등급을 신고한 것이다(knowledge/cmp/psi-adsorption-shield-oxide-systems.md §3).
    disp_conf = psi.confidence if "adsorption_shield" not in psi.terms else None
    if disp_conf is not None:
        assert disp_conf == "literature", (
            "값(NONE, 배수 1.0)은 실리카에서 상속된 교차계 전이지만, EVIDENCE-RULES "
            "판정#15(Kim et al. 2024, doi:10.3390/polym16243593)가 세리아/EAA 분산제의 "
            "oxide MRR 방향이 실리카/PVA·PVP와 반대(억제가 아니라 촉진)임을 대상계 "
            "직접 실측(E3)으로 확인해, '실리카형 억제를 쓰지 않는다'는 이 팩의 결정 "
            "자체는 literature 등급 근거를 얻었다 — knowledge/cmp/"
            "ceria-dispersant-eaa-oxide-mrr-direction-vs-silica.md.")
    else:
        assert psi.confidence in ("estimated", "literature")
        assert "dispersant" in psi.terms and psi.terms["dispersant"] == 1.0


# ═══════════════════ 7: 기준 1.0 계약 회귀 방지

@pytest.mark.parametrize("kind", ["NONE", "PAA", "PAM"])
def test_negligible_dispersant_override_keeps_psi_at_unity(kind):
    factors = compute_factors(
        Recipe(pack="oxide_silica", pack_overrides={"dispersant_type": kind}).resolve())
    psi = factors["psi"]
    assert psi.value == pytest.approx(1.0, abs=1e-9)
