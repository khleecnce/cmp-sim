"""판정#61 — sic_alumina_kmno4 팩의 pH 축 배선 계약.

근거 노트: knowledge/cmp/sic-kmno4-acidic-ph-decay-chen2020.md
1차 출처: Chen et al. 2020, DOI 10.1134/S1070427220060099, Fig. 1(a).

판정#59 가 이 팩의 pH 항을 (남의 재료 계수라서) 껐고, 이 판정이 자기 재료계
문헌으로 다시 켰다. 아래 계약이 지키는 것:
  1. 기준 조건에서 배수 1.0 (Kp 이중 계상 방지)
  2. 산성→알칼리 단조 감소 (실리카 정점형·세리아 IEP 창과 부호가 반대)
  3. 게이트 — 계수를 직접 선언하지 않은 팩은 이 항을 주워가지 않는다
  4. 다른 5팩의 χ 분기 선택·값 불변
"""
import math
import pytest

from sim.params import load_pack
from sim.engine import Recipe, ResolvedRecipe, simulate
from sim.factors import _f_chi, _ph_sic_kmno4_acidic_term

PACK = "sic_alumina_kmno4"


def _rr(pack_name, **over):
    pk = load_pack(pack_name)
    for k, v in over.items():
        pk.params[k].value = v
    return pk, ResolvedRecipe(
        base=Recipe(pack=pack_name), pack=pk, used_keys=[], film=None,
        wafer_radius_m=0.15, pressure_psi=4.0, rpm_wafer=90, rpm_platen=90,
        center_offset_m=0.12, kp_m_per_pa=float(pk.get("kp_m_per_pa")),
        n_points=81, edge_exclusion_m=0.003)


def test_ph_term_is_unity_at_pack_reference():
    pk = load_pack(PACK)
    assert pk.has_own("sic_kmno4_ph_acid_k")
    v = _ph_sic_kmno4_acidic_term(pk, [])
    assert v == pytest.approx(1.0, abs=1e-12)


def test_ph_term_decreases_monotonically_toward_alkaline():
    """단조 감소는 산화제 농도와 무관한 계약 — φ 가 올라가도 부호는 안 바뀐다.

    ⚠ 판정#64(φ 농도 보간) 이후 **감소 배수는 산화제 농도의 함수**다. 저농도
    앵커에서만 Chen 2020 의 3.56 배가 나오고, 팩 기본 4 wt% 에서는 φ 가 높아
    평탄부가 올라가므로 배수가 작아진다. 배수를 상수로 박아 두면 그것은 계약이
    아니라 '그 시점의 팩 기본값'을 고정하는 것이다.
    """
    for ox in (0.79, 4.0, 6.5):
        pk = load_pack(PACK)
        pk.params["oxidizer_wt_pct"].value = ox
        vals = []
        for ph in (2.0, 4.0, 6.0, 8.0, 10.0):
            pk.params["slurry_ph"].value = ph
            vals.append(_ph_sic_kmno4_acidic_term(pk, []))
        assert all(vals[i] > vals[i + 1] for i in range(4)), (ox, vals)
        assert vals[0] / vals[4] > 1.0, (ox, vals)


def test_ph_decay_magnitude_matches_chen2020_at_its_own_concentration():
    """Chen 2020 Fig.1(a) 판독: pH2→10 이 3.56배.

    그 관측은 0.05 M(≈0.79 wt%) KMnO4 에서 나왔으므로 **그 농도에서** 재현돼야
    한다(판정#64 의 φ 저농도 앵커 조건). 팩 기본 4 wt% 로 재면 다른 조성의
    데이터를 다른 조성의 모델과 대조하는 것이다.
    """
    pk = load_pack(PACK)
    pk.params["oxidizer_wt_pct"].value = float(pk.get("sic_kmno4_ph_floor_lo_wt"))
    vals = []
    for ph in (2.0, 10.0):
        pk.params["slurry_ph"].value = ph
        vals.append(_ph_sic_kmno4_acidic_term(pk, []))
    assert vals[0] / vals[1] == pytest.approx(3.56, rel=0.05)


def test_ph_term_reproduces_chen2020_si_face_points():
    """팩에 넣은 k·φ 가 판독 5점을 3 % 이내로 재현한다(노트 §3).

    판정#64 이후 φ 가 산화제 농도에 의존하므로 Chen 의 조성(저농도 앵커)에서 잰다.
    """
    pk = load_pack(PACK)
    pk.params["oxidizer_wt_pct"].value = float(pk.get("sic_kmno4_ph_floor_lo_wt"))
    base = 192.38
    tops = [102.53, 145.10, 161.69, 165.93, 167.11]
    s = 400.0 / 23.272
    obs_abs = [(base - t) * s for t in tops]
    obs = [v / obs_abs[0] for v in obs_abs]
    pred = []
    for ph in (2.0, 4.0, 6.0, 8.0, 10.0):
        pk.params["slurry_ph"].value = ph
        pk.params["ph_ref"].value = 2.0          # 판독 기준점으로 정규화
        pred.append(_ph_sic_kmno4_acidic_term(pk, []))
    for o, p in zip(obs, pred):
        assert abs(p / o - 1) < 0.03, (o, p)


def test_ph_term_is_gated_to_packs_that_declare_the_coefficient():
    for name in ("oxide_silica", "sti_ceria", "cu_h2o2_bta",
                 "w_fe_oxidizer", "sic_ceria_h2o2"):
        assert _ph_sic_kmno4_acidic_term(load_pack(name), []) is None, name


def test_chi_is_no_longer_unmodeled_and_unity_at_reference():
    pk, rr = _rr(PACK)
    f = _f_chi(rr)
    assert f.status != "unmodeled", f.status
    assert "ph_sic_kmno4_acidic" in f.terms, f.terms
    assert f.value == pytest.approx(1.0, abs=1e-9)


def test_mrr_now_responds_to_ph_on_this_pack():
    """판정#59 이후 죽어 있던 축이 살아났는지 — 엔진 끝단에서 확인.

    ⚠ 배수 하한을 상수로 박지 않는다(판정#64). φ 가 산화제 농도의 함수가 된
    이상 "pH2/pH10 > 3" 은 물리 계약이 아니라 그때의 팩 기본 농도(0.79 wt%
    수준)를 고정하는 문장이었다. 계약은 **축이 살아 있고 방향이 맞다**이며,
    Chen 조성에서 배수가 회복되는지는 위 항목이 따로 잠근다.
    """
    import numpy as np
    out = {}
    for ph in (2.0, 6.0, 10.0):
        w = simulate(Recipe(pack=PACK, pack_overrides={"slurry_ph": ph}))
        out[ph] = float(np.mean(w.mrr_nm_per_min))
    assert out[2.0] > out[6.0] > out[10.0], out
    assert out[2.0] / out[10.0] > 1.2, out          # 죽은 축(=1.0)과 확실히 구분


@pytest.mark.parametrize("name", ["oxide_silica", "sti_ceria", "cu_h2o2_bta",
                                  "w_fe_oxidizer", "sic_ceria_h2o2"])
def test_other_packs_chi_branch_unchanged(name):
    """다른 팩이 이 새 분기를 고르지 않는다(후보 추가의 부작용 차단)."""
    pk, rr = _rr(name)
    f = _f_chi(rr)
    assert "ph_sic_kmno4_acidic" not in f.terms, (name, f.terms)
