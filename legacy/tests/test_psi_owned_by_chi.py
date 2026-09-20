"""ψ가 χ에 선점된 계(cu_alkaline_benzenesulfonic)에서 항등원으로 신고되는지 검사.

근거: knowledge/slurry/psi-cu-alkaline-h2o2-passivation.md (§3 선점·§4 화학종 부재·§6c 이중계상 수치)
판정#70 (EVIDENCE-RULES.md)

계약 3개:
 1. 이 팩의 ψ는 status='partial', value=1.0, terms={'owned_by_chi':1.0} — 즉 MRR에 영향 없음.
 2. 그 분기는 **has_own 게이트**를 지킨다: χ 부동태 계수를 자기선언하지 않은 팩은
    여전히 unmodeled로 남아 진짜 미모델링을 가리지 않는다.
 3. 기준 조건 배수 1.0 계약(이중계상 금지)을 깨지 않는다.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim.engine import Recipe                               # noqa: E402
from sim.factors import compute_factors                     # noqa: E402
from sim.params import load_pack                            # noqa: E402

PACK = "cu_alkaline_benzenesulfonic"


def _psi(pack, **ov):
    return compute_factors(Recipe(pack=pack, pack_overrides=ov or None).resolve())["psi"]


def test_psi_identity_when_owned_by_chi():
    f = _psi(PACK)
    assert f.status == "partial", f.status
    assert f.value == 1.0, f.value
    assert f.terms == {"owned_by_chi": 1.0}, f.terms
    assert any("항등원" in n for n in f.notes), f.notes
    # 근거 노트가 붙어 있어야 한다 — 사유 없는 partial은 미모델링 은폐다
    assert any("psi-cu-alkaline-h2o2-passivation" in s for s in f.sources), f.sources


def test_branch_requires_own_declaration():
    """부모(cu_h2o2_bta)는 억제제 항으로 modeled이고, 이 분기를 타지 않는다."""
    pk = load_pack(PACK)
    assert pk.has_own("cu_ph_alkaline_k") or pk.has_own("oxidizer_passivation_K")
    parent = _psi("cu_h2o2_bta")
    assert parent.terms != {"owned_by_chi": 1.0}, parent.terms


def test_identity_is_ph_and_oxidizer_invariant():
    """항등원이므로 pH·산화제를 흔들어도 ψ는 1.0 — χ가 그 축을 전담한다."""
    for ov in ({"slurry_ph": 6.2}, {"slurry_ph": 9.9}, {"oxidizer_wt_pct": 5.0}):
        f = _psi(PACK, **ov)
        assert f.value == 1.0, (ov, f.value)
