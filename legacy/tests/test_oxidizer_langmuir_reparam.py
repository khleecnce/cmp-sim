"""χ 산화제 항 재파라미터화 — Langmuir 1파라미터 경로 계약 테스트.

배경: EVIDENCE-RULES 판정#19(knowledge/cmp/chi-oxidizer-curve-exponent-identifiability.md)로
기존 Kaufman 단봉 (n, C_peak) 형상이 정점 아래 관측만으로는 완전축퇴(식별 불가)임이
수치로 확인됐다. 대체 경로는 자유 파라미터 K 하나뿐인 Langmuir 표면피복
θ(C)=K·C/(1+K·C), f(C)=φ+(1-φ)·θ(C)/θ(C_ref)이다.

이 파일이 지키는 것: 새 경로가 폐형식 유도값(K=0.549550)으로 3관측점을 재현하는가,
그리고 레거시 경로(oxidizer_langmuir_K 없는 팩)의 동작이 그대로인가.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sim.chemistry import chemistry_factor  # noqa: E402
from sim.engine import Recipe  # noqa: E402
from sim.factors import compute_factors  # noqa: E402
import sim.models  # noqa: E402,F401


class FakePack:
    """팩 인터페이스 최소 구현 — 화학 항만 격리해 검사한다(test_chemistry.py와 동일 패턴)."""
    def __init__(self, **kw):
        self.d = kw
        self.name = "fake"
    def has(self, k): return k in self.d
    def get(self, k): return self.d[k]
    def get_or(self, k, dv): return self.d.get(k, dv)


K_W_FE = 0.549550          # knowledge/params/w_fe_oxidizer.yaml 폐형식 유도값
PHI_W_FE = 0.14


def _f(C, K=K_W_FE, C_ref=3.0, phi=PHI_W_FE):
    return chemistry_factor(FakePack(
        abrasive="alumina",
        oxidizer_wt_pct=C, oxidizer_ref_wt_pct=C_ref,
        oxidizer_langmuir_K=K, oxidizer_mech_floor=phi)).factor


# (a) K=0.549550에서 f(0)/f(1)/f(3)이 0.14/0.63/1.00을 1e-6 이내 재현
def test_langmuir_reproduces_us20110186542a1_three_points():
    assert _f(0.0) == pytest.approx(0.14, abs=1e-6)
    assert _f(1.0) == pytest.approx(0.63, abs=1e-6)
    assert _f(3.0) == pytest.approx(1.00, abs=1e-6)


# (b) f(C_ref) == 1.0 항등 (Langmuir 경로, 임의의 K·phi에서도 성립해야 한다)
def test_langmuir_identity_at_reference_concentration():
    for K, phi, C_ref in [(0.1, 0.0, 2.0), (5.0, 0.2, 5.0), (0.5495, 0.14, 3.0)]:
        assert _f(C_ref, K=K, C_ref=C_ref, phi=phi) == pytest.approx(1.0, abs=1e-9)


# (c) 단조증가 + 포화 (f(100) > f(20)이고 증가폭이 감소)
def test_langmuir_monotonic_and_saturating():
    vals = {C: _f(C) for C in (0.0, 1.0, 3.0, 10.0, 20.0, 100.0)}
    concs = sorted(vals)
    for a, b in zip(concs, concs[1:]):
        assert vals[b] > vals[a], f"단조증가 위반: f({a})={vals[a]} >= f({b})={vals[b]}"
    step_20_100 = vals[100.0] - vals[20.0]
    step_3_20 = vals[20.0] - vals[3.0]
    assert step_20_100 < step_3_20, (
        f"포화 위반: 고농도 구간 증가폭({step_20_100:.4f})이 "
        f"저농도 구간({step_3_20:.4f})보다 작지 않다")


# (d) Langmuir 키 없는 팩은 레거시 경로로 기존과 동일 값 산출 (회귀 방지)
def test_legacy_pack_without_langmuir_key_is_unchanged():
    """oxidizer_langmuir_K가 없으면 예전 그대로 (n, C_peak) 단봉+가산 하한 공식을 쓴다."""
    def legacy_expected(C, C_peak, C_ref, n, floor):
        from sim.tier2_physics.slurry_components import mrr_oxidizer
        cur = mrr_oxidizer(C, C_peak, mrr_peak=1.0, n=n)
        ref = mrr_oxidizer(C_ref, C_peak, mrr_peak=1.0, n=n)
        cur = floor + (1.0 - floor) * cur
        ref = floor + (1.0 - floor) * ref
        return cur / ref

    C_peak, C_ref, n, floor = 6.0, 3.0, 3.0, 0.14
    for C in (0.0, 1.0, 3.0, 5.0, 9.0):
        eff = chemistry_factor(FakePack(
            abrasive="alumina",
            oxidizer_wt_pct=C, oxidizer_ref_wt_pct=C_ref,
            oxidizer_peak_wt_pct=C_peak, oxidizer_curve_n=n,
            oxidizer_mech_floor=floor))
        assert eff.factor == pytest.approx(
            legacy_expected(C, C_peak, C_ref, n, floor), rel=1e-12)

    # 실제 저장 팩(w_fe_oxidizer)도 Langmuir 키가 추가됐을 뿐, 레거시 값 자체는
    # yaml에 그대로 남아 있다 — 여기서 직접 골라 쓰면 여전히 같은 수를 낸다는 뜻.
    assert legacy_expected(1.0, 6.0, 3.0, 3.0, 0.14) == pytest.approx(0.6373, abs=1e-4)


# (e) cu_h2o2_bta — 2026-09-14 판정#20으로 Langmuir 부동태 억제 경로로 이관됐다
def test_cu_h2o2_bta_chi_migrated_to_passivation_langmuir():
    """기준 운전점(C=C_ref=3.0)에서 배수는 여전히 항등 1.0 — Kp 이중계상이 없다.

    단 등급은 unverified → estimated 로 올라간다: 축퇴해 식별 불가능하던
    (oxidizer_curve_n, oxidizer_peak_wt_pct) 대신, 데이터로 식별되는
    oxidizer_passivation_K(estimated) 하나를 형상 파라미터로 읽기 때문이다.
    근거: knowledge/cmp/chi-oxidizer-cu-h2o2-reparameterization.md (판정#20)
    """
    f = compute_factors(Recipe(pack="cu_h2o2_bta").resolve())["chi"]
    assert f.value == pytest.approx(1.0, abs=1e-9)
    assert f.confidence == "estimated", (
        "oxidizer_passivation_K(estimated)가 형상 파라미터 등급으로 읽혀야 한다 — "
        "비활성화된 oxidizer_curve_n(unverified)이 더 이상 발목잡으면 안 된다")


# ── 보너스: w_fe_oxidizer 팩 등급이 Langmuir 채택으로 올라갔는가 (완성도 회귀 방지) ──
def test_w_fe_oxidizer_chi_confidence_upgraded_by_langmuir_key():
    f = compute_factors(Recipe(pack="w_fe_oxidizer").resolve())["chi"]
    assert f.value == pytest.approx(1.0, abs=1e-9)
    assert f.confidence == "literature", (
        "oxidizer_langmuir_K(literature)가 형상 파라미터 등급으로 읽혀야 한다 — "
        "비활성화된 oxidizer_curve_n/oxidizer_peak_wt_pct(estimated)가 더 이상 발목잡으면 안 된다")
