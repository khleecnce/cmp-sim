"""(억제제 × 기질) 쌍 표의 계약을 잠근다.

왜 이 테스트가 필요한가
──────────────────────
ΔG_ads 는 억제제 단독의 성질이 아니라 **쌍**의 성질이다. 과거에 한 쌍의
값이 다른 쌍에 이식돼 흡착상수가 5,700 배 어긋난 채 예측이 나왔고,
그 사고는 예외도 경고도 없이 조용히 일어났다. 사람의 주의로는 못 막는다.

여기서 잠그는 것 셋:
  1) 표의 모든 줄이 기질을 갖고 근거를 단다 (이식 방지의 최소 조건)
  2) `lookup_dG` 는 없는 쌍에 **유사 값을 돌려주지 않는다**
  3) '미측정'과 '메커니즘 부재'가 구분된다 — 후자는 억제 항이 없는 것이
     물리적으로 옳고, 전자는 절대값 주장 금지 + R8 발행 대상이다.
     둘을 섞으면 다음 회차가 존재하지 않는 문헌을 계속 찾는다.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.inhibitor_pairs import (  # noqa: E402
    PAIR_TABLE, NO_ADSORPTION, lookup_dG, K_from_dG, adsorption_ruled_out,
)

VALID_CONF = {"verified", "measured", "literature", "estimated", "unverified"}


def test_every_pair_declares_substrate_method_and_source():
    """기질·측정법·출처가 없는 줄은 이식 사고의 씨앗이다."""
    for (inhib, subst), p in PAIR_TABLE.items():
        assert inhib and subst, f"쌍 키가 불완전하다: {(inhib, subst)}"
        assert p.substrate.lower() == subst, f"{inhib}×{subst}: 기질 불일치"
        assert p.method.strip(), f"{inhib}×{subst}: 측정법이 비었다"
        assert p.source.strip(), f"{inhib}×{subst}: 출처가 비었다"
        assert p.confidence in VALID_CONF, f"{inhib}×{subst}: 등급 {p.confidence}"


def test_adsorption_is_negative_and_physical():
    """흡착이면 ΔG < 0. 자릿수 이탈(계산 ΔG 혼입)도 함께 막는다."""
    for (inhib, subst), p in PAIR_TABLE.items():
        assert p.dG_kJ_per_mol < 0, f"{inhib}×{subst}: 흡착인데 ΔG ≥ 0"
        # MD/DFT 결합에너지(≈ -368 kJ/mol)를 실험 ΔG_ads 줄에 넣는 오독을 막는다.
        assert abs(p.dG_kJ_per_mol) < 150, (
            f"{inhib}×{subst}: |ΔG|={abs(p.dG_kJ_per_mol)} — 실험 흡착 ΔG 범위 밖이다. "
            "MD/DFT 흡착에너지를 실험 ΔG_ads 로 혼용하지 마라."
        )


def test_lookup_never_substitutes_a_different_pair():
    """없는 쌍에 유사 값을 돌려주면 안 된다 — 5,700배 오차의 경로."""
    assert lookup_dG("bta", "cu") is not None
    for missing in [("bta", "ta"), ("benzenesulfonic", "cu"),
                    ("malonate", "w"), ("아무거나", "아무기질")]:
        assert lookup_dG(*missing) is None, f"{missing}: 없는 쌍에 값이 나왔다"


def test_aliases_resolve_same_species_but_not_neighbours():
    """표기 차이로 조회가 실패하면 '값이 있는데 미확보'로 보고된다.

    단 정규화는 **같은 흡착종**에만 적용된다 — 인접 분자를 별칭으로 넣으면
    이식 금지 규칙이 무너지므로, 여기서 그 경계를 함께 잠근다.
    """
    # 같은 흡착종의 다른 표기 → 같은 줄로 해석된다
    assert lookup_dG("malonic", "cu") is lookup_dG("malonate", "cu")
    assert lookup_dG("benzotriazole", "copper") is lookup_dG("bta", "cu")
    assert lookup_dG("bta", "silica") is lookup_dG("bta", "sio2")
    # 인접 분자는 별칭이 아니다 — 값이 있어서는 안 된다
    for neighbour in [("succinate", "cu"), ("ethylmalonate", "cu"),
                      ("tta", "cu"), ("sdbs", "cu")]:
        assert lookup_dG(*neighbour) is None, f"{neighbour}: 인접 분자에 값이 나왔다"


def test_same_molecule_different_substrate_is_a_different_row():
    """기질이 다르면 다른 줄 — 이 표의 존재 이유 자체."""
    cu = lookup_dG("bta", "cu")
    fe = lookup_dG("bta", "fe")
    assert cu is not None and fe is not None
    assert cu.dG_kJ_per_mol != fe.dG_kJ_per_mol


def test_ruled_out_pairs_carry_a_reason_and_are_not_in_the_value_table():
    """근거 없이 '흡착 없음'을 선언하면 억제를 조용히 0 으로 만드는 것이다."""
    for key, reason in NO_ADSORPTION.items():
        assert len(reason) > 40, f"{key}: 메커니즘 부재 근거가 너무 짧다"
        assert key not in PAIR_TABLE, f"{key}: 값 표와 부재 선언에 동시에 있다"


def test_missing_and_ruled_out_are_distinguishable():
    """'아무도 안 쟀다'와 '그 메커니즘이 없다'는 다른 결론이다.

    ⚠ 예시 쌍을 고를 때 주의: 여기 쓰는 '미확보' 쌍은 언젠가 값이 확보되거나
    메커니즘 부재로 선언될 수 있다. 실제로 benzenesulfonic×cu 를 예시로 썼다가
    특허 원문이 '억제제가 아님'을 확정하면서 이 테스트가 깨졌다 — 테스트가
    낡은 것이지 코드가 틀린 게 아니었다. 아직 어느 쪽으로도 판정되지 않은
    쌍(nicotinic×cu)을 쓴다.
    """
    # 메커니즘 부재로 선언된 쌍 — 근거가 함께 나온다
    assert adsorption_ruled_out("bta", "ta")
    assert adsorption_ruled_out("benzenesulfonic", "cu")
    # 아직 판정되지 않은 쌍 — 선언이 없으므로 R8(측정 명세) 대상이다
    assert adsorption_ruled_out("nicotinic", "cu") is None
    assert lookup_dG("nicotinic", "cu") is None


def test_malonate_cu_uses_the_oxidized_surface_value():
    """CMP 는 산화제를 포함한다 — 환원 표면 값(-38.3)을 쓰면 안 된다."""
    p = lookup_dG("malonate", "cu")
    assert p is not None
    assert p.dG_kJ_per_mol == pytest.approx(-47.7)
    assert "Temkin" in p.method


def test_K_from_dG_is_monotonic_in_binding_strength():
    """더 음수인 ΔG 는 더 큰 흡착상수여야 한다."""
    assert K_from_dG(-47.7) > K_from_dG(-30.02) > K_from_dG(-5.59) > 0
