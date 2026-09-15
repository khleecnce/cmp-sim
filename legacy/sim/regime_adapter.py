"""팩 물성 → 레짐 판정 → 지수. 사람이 지수를 적어넣지 않게 하는 배선.

이 파일이 하는 일
────────────────
`sim/abrasive_mechanics.py` 는 "세 질문에 답하면 지수가 나온다"는 절차를 담고,
이 파일은 **그 세 질문을 팩의 물성으로 자동 응답**한다. 즉 사용자가 슬러리
정보를 넣으면 지수가 따라 나오게 하는 연결부다.

    팩 물성                     →  판단                     →  지수
    ───────────────────────────────────────────────────────────────
    패드 탄성·거칠기·돌기밀도    →  실접촉면적의 압력 지수   →  χ
    입자당 접촉응력·표면층 경도  →  탄성인가 소성인가        →  α, β
    간극·입자 직경               →  단층인가 다층인가        →  p, q

어느 단계에도 물질명이 없다. 팩이 무엇이든 같은 물성을 읽는다.

없는 값은 지어내지 않는다
─────────────────────────
물성이 없으면 그 질문은 "미판정"으로 남고 등급이 내려간다. 이때 팩이 지수를
직접 선언했다면 **그것을 쓰되 '유도된 값이 아님'을 신고**한다 — 기존 팩이
깨지지 않으면서, 무엇이 이론에서 나왔고 무엇이 손으로 넣은 값인지 구분된다.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from sim.abrasive_mechanics import (
    ALPHA_ELASTIC, ALPHA_PLASTIC, BETA_FOR_ALPHA, LoadRegime, resolve_regime,
)

PSI_TO_PA = 6894.757


def _num(pk, key: str) -> Optional[float]:
    """팩에서 수치를 꺼낸다. 없거나 숫자가 아니면 None (기본값을 놓지 않는다)."""
    v = pk.get_or(key, None)
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def area_pressure_exponent(pk, notes: List[str]) -> Optional[float]:
    """실접촉면적이 압력에 대해 갖는 지수 m (A_r ∝ P^m) → χ 판정의 입력.

    입력: 돌기 높이 분포의 형태
    판단: 지수분포로 근사되는 거친 표면에서는 실접촉면적이 하중에 **선형**이고
          분리거리와 무관하다 — 이것이 GW 모델의 해석적 결과다. 이 경우 압력을
          올리면 접촉 자리가 비례해 늘어나므로 하중이 입자들에게 재분배된다.
    출력: m. 분포 형태를 모르면 None.

    ⚠ 가우시안 분포에서는 m 이 1 보다 약간 작고 분리거리에 의존한다. 팩이 분포
      형태를 선언하면 그것을 따르고, 없으면 이 계의 표준 근사(지수분포)를 쓰되
      근거 등급을 낮춘다.
    """
    m = _num(pk, "contact_area_pressure_exponent")
    if m is not None:
        notes.append(f"실접촉면적 압력지수 m={m:.3f} (팩 선언)")
        return m

    dist = str(pk.get_or("asperity_height_distribution", "") or "").lower()
    if dist in ("exponential", "exp"):
        notes.append(
            "실접촉면적 압력지수 m=1.0 — 돌기 높이가 지수분포면 A_r 이 하중에 "
            "선형이고 분리거리와 무관하다(GW 해석해).")
        return 1.0
    if dist in ("gaussian", "normal"):
        # 가우시안에서는 완전 선형이 아니지만 실용 범위에서 1 에 가깝다.
        notes.append(
            "⚠ 실접촉면적 압력지수 m≈0.95 — 가우시안 분포는 지수분포처럼 완전 "
            "선형이 아니다. 근사값이며 분리거리 의존성은 무시했다.")
        return 0.95
    return None


def contact_stress_pa(pk, pressure_psi: Optional[float],
                      notes: List[str]) -> Optional[float]:
    """입자 하나가 받는 접촉 응력 → α 판정의 입력.

    ⚠ 면적 기준을 섞지 않는다 — 이 계산이 틀리는 가장 흔한 방식이다.
    실접촉 압력은 **실접촉면적** 기준이고 돌기 밀도는 **명목면적** 기준이다.
    둘을 그대로 나누면 단위는 맞지만 물리가 어긋나 수십 자릿수 틀린 값이 나온다.
    그래서 전부 명목면적 1 m² 기준으로 통일해 따라간다:

        명목 1 m² 의 총하중            W_tot = P_nom
        접촉 자리 수                   N_c   = n_density
        자리당 하중                    W_c   = W_tot / N_c
        자리 하나의 실제 면적          A_c   = (실접촉면적비) / N_c
        자리 하나에 들어가는 입자 수   k     = A_c / (입자 단면적)
        입자당 하중                    F_p   = W_c / k
        입자 접촉응력                  σ     = F_p / (입자 단면적)

    마지막 두 줄을 합치면 σ = W_c / A_c 가 되어 **자리 압력과 같아진다**.
    즉 단층 가정에서 입자가 받는 응력은 그 자리의 실접촉 압력이다 — 입자가
    자리를 고르게 채우고 있다면 응력이 그대로 전달되기 때문이다.
    입자가 자리를 다 못 채우면(피복률 < 1) 응력은 그만큼 커진다.
    """
    if pressure_psi is None:
        return None
    p_nom = float(pressure_psi) * PSI_TO_PA

    ar_ratio = _num(pk, "real_contact_area_ratio")
    if ar_ratio is None or ar_ratio <= 0:
        notes.append(
            "⚠ 접촉응력 미산출: 실접촉면적 비(real_contact_area_ratio)가 없다. "
            "명목 압력만으로는 입자 하나가 받는 응력을 알 수 없다 — 실접촉은 "
            "명목의 작은 일부이고 그 비가 응력을 수천 배로 키운다.")
        return None

    # 자리 압력 = 명목 압력 / 실접촉면적비 (면적 기준 통일)
    p_contact = p_nom / ar_ratio

    # 입자가 자리를 얼마나 채우는가. 피복률 1 이면 입자 응력 = 자리 압력.
    coverage = _num(pk, "particle_surface_coverage")
    if coverage is None:
        # 선언이 없으면 **팩 물성에서 유도**한다 (θ_p = 1.5·φ·h/d).
        # 이 유도가 없으면 σ 가 팩을 전혀 안 봐서 다섯 팩이 같은 값이 되고,
        # 그 결과 α 판정이 전 팩 동일하게 떨어진다 — 그 α 가 n_C 를 통해
        # 농도 반응의 부호를 정하므로 조용한 오판의 근원이 된다.
        coverage = particle_coverage(pk, notes)
    if coverage is None:
        notes.append(
            f"입자 접촉응력 {p_contact:.3g} Pa — 단층·완전피복 가정에서 입자가 "
            "받는 응력은 그 자리의 실접촉 압력과 같다. "
            "⚠ 피복률을 선언도 유도도 못 했다. θ_p ≤ 1 이므로 이 값은 "
            "**하한**이고, 실제 응력은 이보다 크다 — α 판정이 탄성 쪽으로 "
            "치우친다는 뜻이다.")
        return p_contact

    coverage = max(min(float(coverage), 1.0), 1e-6)
    sigma = p_contact / coverage
    notes.append(
        f"입자 접촉응력 {sigma:.3g} Pa (자리 압력 {p_contact:.3g} Pa ÷ "
        f"피복률 {coverage:.3g})")
    return sigma


def surface_hardness_pa(pk, notes: List[str]) -> Optional[float]:
    """제거되는 표면층의 유효 경도 → α 판정의 입력.

    ⚠ **벌크 경도가 아니다.** CMP 에서 깎이는 것은 화학적으로 변질된 얇은 층이고
    그 층의 경도는 벌크보다 낮다. 이 값의 절대치는 공개 문헌에 없다
    (_knowledge_audit/mechanics.md 가 지목한 최대 병목).

    ── 절대값을 몰라도 판정이 가능한 경우가 있다 ──────────────────────
    우리가 α 를 고르기 위해 필요한 것은 경도의 **절대값이 아니라 접촉응력과의
    대소 관계**다. 변질층은 정의상 벌크보다 무르므로

        H_surface ≤ H_bulk

    이 부등식은 절대값 없이도 성립한다. 따라서

        접촉응력 ≥ H_bulk  →  H_surface 는 그보다 작으니 **반드시 소성**

    이 방향의 판정은 벌크만으로도 확정된다. 반대 방향(접촉응력 ≪ H_bulk)은
    확정되지 않는다 — 변질층이 얼마나 무른지 모르므로 소성일 수도 있다.
    그러므로 **한쪽 방향으로만** 벌크를 쓰고, 반대쪽은 판정을 보류한다.
    이것은 "벌크로 대체"가 아니라 부등식이 허용하는 만큼만 결론내는 것이다.
    """
    h = _num(pk, "surface_layer_hardness_pa")
    if h is not None and h > 0:
        notes.append(f"표면층 유효경도 {h:.3g} Pa (팩 선언)")
        return h
    return None


def particle_coverage(pk, notes: List[str]) -> Optional[float]:
    """접촉 자리에서 입자가 실제로 차지하는 면적 비 θ_p ∈ (0, 1].

    왜 필요한가
    ──────────
    `contact_stress_pa` 가 내는 σ 는 **입자가 자리를 빈틈없이 덮는다**는
    가정의 값이다. 실제로는 θ_p < 1 이고 그만큼 응력이 커진다:

        σ_real = σ_계산 / θ_p

    θ_p 가 없으면 σ 가 팩 물성을 전혀 안 보게 되고(실제로 다섯 팩이
    같은 값이었다), 그 결과 α 판정이 전 팩 동일하게 떨어진다.
    그 α 가 n_C = p(1−αχ) 를 통해 **농도 반응의 부호**를 정한다.

    유도 (입력 → 판단 기준 → 출력, 물질명 없음)
    ──────────────────────────────────────────
        고형분 부피분율          φ   = (wt/100) / ρ_p / [(wt/100)/ρ_p + (1−wt/100)/ρ_f]
        슬러리 단위부피 입자 수  n_v = φ / (π d³/6)
        간극 h 안의 면밀도       n_a = n_v · h
        입자 단면적              a_p = π d²/4
        피복률                   θ_p = n_a · a_p = 1.5 · φ · h / d

    ⚠ 상한 1 로 자른다. θ_p > 1 은 단층 가정이 깨졌다는 뜻(다층)이고,
      그 경우 응력은 더 이상 커지지 않는다 — 자르는 것이 물리적으로 옳다.
      다만 잘렸다는 사실을 신고한다(다층 레짐 신호다).
    """
    wt = _num(pk, "abrasive_wt_pct")
    d_nm = _num(pk, "abrasive_size_nm")
    rho_p = _num(pk, "abrasive_density_kg_m3")
    gap = None
    for key in ("fluid_gap_m", "pad_wafer_gap_m", "film_thickness_m"):
        gap = gap or _num(pk, key)

    # 간극이 선언돼 있지 않으면 윤활 이론의 **길이 스케일** z0 로 대신한다.
    #   z0 = sqrt(2·μ·ω·R1·R2 / P)   (Thakurta 2001 Eq.19)
    # ⚠ z0 는 정확한 최소 유막두께 h_min 이 아니다 — 무차원화 기준 길이다.
    #   그래서 여기서 나온 θ_p 는 **자릿수 추정**이고, 그 사실을 신고한다.
    #   그럼에도 쓰는 이유: θ_p 가 아예 없으면 σ 가 팩 물성을 전혀 안 보게 되고
    #   (다섯 팩이 같은 값이 됐다) α 판정이 입력 부재로 전부 같아진다.
    #   자릿수라도 팩마다 갈리는 편이 '조용한 동일 판정'보다 낫다.
    z0_used = False
    if gap is None:
        mu = _num(pk, "slurry_viscosity_pa_s")
        if mu and mu > 0:
            try:
                import math as _m
                rpm = _num(pk, "rpm_platen") or 60.0
                r1 = _num(pk, "wafer_radius_m") or 0.15
                r2 = _num(pk, "center_offset_m") or 0.20
                p_app = (_num(pk, "pressure_psi") or 3.0) * PSI_TO_PA
                omega = 2.0 * _m.pi * float(rpm) / 60.0
                gap = _m.sqrt(2.0 * float(mu) * omega * float(r1) * float(r2)
                              / p_app)
                z0_used = True
            except Exception:
                gap = None

    missing = [n for n, v in (("abrasive_wt_pct", wt), ("abrasive_size_nm", d_nm),
                              ("abrasive_density_kg_m3", rho_p),
                              ("간극(fluid_gap_m 또는 점도)", gap)) if not v or v <= 0]
    if missing:
        notes.append(
            "⚠ 피복률 미산출: " + ", ".join(missing) + " 가 없다. "
            "θ_p=1(완전피복)로 가정되며, 이는 접촉응력을 **하한**으로 만든다 "
            "— α 판정이 탄성 쪽으로 치우친다.")
        return None

    rho_f = float(_num(pk, "slurry_density_kg_m3") or 1000.0)   # 물 기준
    rho_s = float(rho_p)          # type: ignore[arg-type]
    w = float(wt) / 100.0         # type: ignore[arg-type]
    phi = (w / rho_s) / ((w / rho_s) + (1.0 - w) / rho_f)
    d_m = float(d_nm) * 1e-9      # type: ignore[arg-type]
    theta = 1.5 * phi * float(gap) / d_m

    if theta > 1.0:
        notes.append(
            f"피복률 θ_p = {theta:.3g} → 1.0 으로 제한. 단층 가정이 깨진 "
            "다층 레짐 신호다(간극 안에 입자가 여러 겹). 응력은 더 커지지 않는다.")
        return 1.0
    src = ("윤활 길이스케일 z0" if z0_used else "팩 선언 간극")
    warn = (" ⚠ z0 는 정확한 최소 유막두께가 아니라 무차원화 기준 길이다 "
            "(Thakurta 2001 Eq.19) — 이 θ_p 는 **자릿수 추정**이고 절대값을 "
            "주장하지 않는다. 정밀값은 유막 두께 실측이 필요하다(R8)."
            if z0_used else "")
    notes.append(
        f"피복률 θ_p = {theta:.4f} (φ={phi:.5f}, h={gap:.3g} m [{src}], "
        f"d={d_nm:g} nm). 입자당 접촉응력이 {1.0 / theta:.1f} 배로 커진다.{warn}")
    return theta


def alpha_from_bulk_bound(pk, sigma_pa: Optional[float],
                          notes: List[str]) -> Optional[Tuple[float, str]]:
    """벌크 경도만 있을 때, 부등식이 허용하는 범위에서만 α 를 판정한다.

    입력: 입자당 접촉응력, 막질 벌크 경도
    판단: H_surface ≤ H_bulk 이므로
          응력 ≥ H_bulk        → 소성 확정 (변질층은 더 무르다)
          응력 ≤ H_bulk × 여유 → 탄성 쪽이 유력하나 확정 아님
    출력: (α, 등급) 또는 None(판정 불가)
    """
    h_bulk = _num(pk, "film_bulk_hardness_pa")
    if sigma_pa is None or h_bulk is None or h_bulk <= 0:
        return None
    ratio = sigma_pa / h_bulk
    if ratio >= 1.0:
        notes.append(
            f"α 확정(소성): 접촉응력이 **벌크** 경도의 {ratio:.2f}배다. 제거되는 "
            "변질층은 벌크보다 무르므로 변질층 경도를 몰라도 소성이 확정된다.")
        return ALPHA_PLASTIC, "literature"
    if ratio <= 0.1:
        # ⚠ 이 가지는 "탄성 확정"이 아니다 (2026-09-15 재판정).
        #
        # σ 는 피복률 θ_p 로 나뉘어야 하는 값인데(contact_stress_pa docstring),
        # θ_p 가 어느 팩에도 선언돼 있지 않아 1.0(완전피복)으로 가정된다.
        # θ_p ≤ 1 이므로 **실제 응력은 지금 값보다 크거나 같다**:
        #       σ_real = σ_계산 / θ_p ≥ σ_계산
        # 따라서 여기서 나온 낮은 비는 상한이 아니라 **하한 비**이고,
        # θ_p 가 이 비만큼 작으면 소성으로 뒤집힌다.
        #
        # 실측이 이 미확정을 뒷받침한다: 접촉응력이 다섯 팩 전부 동일한
        # 3.566e7 Pa 다 — 입자 크기·농도·재료가 계산에 들어가지 않기 때문이다.
        # 그런데 이 가지의 결과(α=2/3)가 n_C = p(1-αχ) = +1/3 을 전 팩에
        # 강제하고, 실측은 세 재료계 모두 농도와 **음의 상관**을 보인다
        # (최강 -0.893, 한 계열은 회귀 지수가 -0.406).
        #
        # 그래서 등급을 estimated 로 두되 **왜 확정이 아닌지**를 신고한다.
        # 값을 바꾸지 않는 이유: θ_p 를 모르는 상태에서 소성으로 뒤집는 것도
        # 근거 없는 선택이고, 그쪽이 오히려 지표를 좋게 만들어 더 위험하다.
        need = ratio          # θ_p 가 이 값 이하면 소성으로 뒤집힌다
        notes.append(
            f"⚠ α 잠정(탄성): 접촉응력/벌크경도 = {ratio:.4f}. **확정이 아니다.** "
            f"이 σ 는 입자 피복률 θ_p=1(완전피복) 가정값이고 θ_p ≤ 1 이므로 "
            f"실제 응력은 이보다 크다 — θ_p 가 {need:.3f} 이하이면 소성으로 "
            "뒤집힌다. 저농도 슬러리에서 충분히 가능한 값이다. "
            "θ_p 를 유도하려면 입자 밀도와 패드-웨이퍼 간극이 필요한데 둘 다 "
            "팩에 없다(R8: 연마 후 패드 SEM/AFM 입자 면밀도, 유막 두께 측정). "
            "⚠ 이 미확정이 n_C 를 통해 농도 반응의 부호를 정한다.")
        return ALPHA_ELASTIC, "estimated"
    notes.append(
        f"⚠ α 미확정: 접촉응력/벌크경도 = {ratio:.3f} 는 중간 영역이다. 변질층이 "
        "벌크보다 얼마나 무른지 모르면 탄성·소성을 가를 수 없다. 이 구간에서는 "
        "변질층 경도의 실측이 필요하다.")
    return None


def fluid_gap_m(pk, notes: List[str]) -> Optional[float]:
    """패드-웨이퍼 간극 → 공급 형태(p, q) 판정의 입력."""
    for key in ("fluid_gap_m", "pad_wafer_gap_m", "film_thickness_m"):
        v = _num(pk, key)
        if v is not None and v > 0:
            notes.append(f"패드-웨이퍼 간극 {v:.3g} m ({key})")
            return v
    return None


def derive_regime(pk, pressure_psi: Optional[float] = None
                  ) -> Tuple[LoadRegime, List[str]]:
    """팩 물성만으로 레짐을 판정한다. 물질명을 보지 않는다."""
    notes: List[str] = []
    m = area_pressure_exponent(pk, notes)
    sigma = contact_stress_pa(pk, pressure_psi, notes)
    h_s = surface_hardness_pa(pk, notes)
    gap = fluid_gap_m(pk, notes)
    d_nm = _num(pk, "abrasive_size_nm")
    d_m = d_nm * 1e-9 if d_nm else None

    # 변질층 경도가 없어도, 벌크 경도와의 부등식이 한쪽 방향은 확정해 준다.
    alpha_override: Optional[Tuple[float, str]] = None
    if h_s is None:
        alpha_override = alpha_from_bulk_bound(pk, sigma, notes)

    reg = resolve_regime(
        area_pressure_exponent=m,
        contact_stress_pa=sigma,
        surface_hardness_pa=h_s,
        gap_m=gap,
        d_p_m=d_m,
        beta=0.0,
    )
    if alpha_override is not None:
        a, conf = alpha_override
        reg.alpha = a
        order = ["unverified", "estimated", "literature", "measured", "verified"]
        # 전체 등급은 여전히 가장 약한 고리를 따른다
        if order.index(conf) > order.index(reg.confidence):
            reg.confidence = conf if reg.confidence == "unverified" else reg.confidence
        if reg.confidence == "unverified":
            reg.confidence = conf
    # β 는 α 와 짝이다 — 따로 고르면 물리가 깨진다.
    reg.beta = BETA_FOR_ALPHA.get(reg.alpha, 0.0)
    if reg.alpha not in BETA_FOR_ALPHA:
        # 전이구간에서 보간된 α — β 도 같은 비율로 보간한다
        t = (reg.alpha - ALPHA_ELASTIC) / (ALPHA_PLASTIC - ALPHA_ELASTIC)
        b_e, b_p = BETA_FOR_ALPHA[ALPHA_ELASTIC], BETA_FOR_ALPHA[ALPHA_PLASTIC]
        reg.beta = b_e + t * (b_p - b_e)
    notes.extend(reg.notes)
    return reg, notes


def exponents_for(pk, pressure_psi: Optional[float] = None) -> Dict[str, object]:
    """최종 산출 — 농도·입경 지수와 그것이 어디서 왔는지.

    반환:
      n_conc / n_size : 쓸 지수
      derived         : 이론에서 유도됐는가 (False 면 팩 선언값)
      confidence      : 근거 등급
      notes           : 판정 과정
    """
    reg, notes = derive_regime(pk, pressure_psi)
    declared_c = _num(pk, "abrasive_conc_exponent")
    declared_d = _num(pk, "abrasive_size_exponent")

    out: Dict[str, object] = {"regime": reg, "notes": notes}

    if reg.confidence == "unverified":
        # 판정에 필요한 물성이 없다. 팩이 선언한 값이 있으면 그것을 쓰되
        # '유도된 값이 아님'을 분명히 남긴다.
        out["n_conc"] = declared_c
        out["n_size"] = declared_d
        out["derived"] = False
        out["confidence"] = "estimated" if (declared_c is not None) else "unverified"
        notes.append(
            "⚠ 지수를 이론에서 유도하지 못했다 — 판정에 필요한 물성(실접촉면적 "
            "압력지수 / 표면층 유효경도 / 간극)이 팩에 없다. 팩이 선언한 지수를 "
            "그대로 쓰지만 이것은 **그 조건에서 회귀된 값**이지 예측이 아니다. "
            "다른 조건으로 외삽하면 틀릴 수 있다.")
        return out

    out["n_conc"] = reg.n_conc
    out["n_size"] = reg.n_size
    out["derived"] = True
    out["confidence"] = reg.confidence

    # EVIDENCE-RULES.md 서열: 팩이 이미 대상계 직접실측(E1~E3)으로 판정해
    # literature/measured 등급을 선언했다면, 검증 안 된 범용 이론(GW접촉+탄성
    # 가정, 이 계에서 실측 검증된 바 없음)이 그것을 조용히 덮으면 안 된다.
    # 2026-09-13 QA루프 퇴보(entegris2022 데이터셋 유의->비유의)로 발견:
    # sic_ceria_h2o2의 declared -0.406(E3, Entegris 특허 Table1 n=5 직접실측)이
    # 이론값 +1/3(범용 GW 유도, 이 계 미검증)로 덮여 예측 방향이 뒤집혔다.
    for label, key_out, derived, declared, declared_key in (
        ("농도", "n_conc", reg.n_conc, declared_c, "abrasive_conc_exponent"),
        ("입경", "n_size", reg.n_size, declared_d, "abrasive_size_exponent"),
    ):
        if declared is None:
            continue
        declared_conf = pk.param(declared_key).confidence if pk.has(declared_key) else "unknown"
        if abs(derived - declared) > 0.05:
            if declared_conf in ("literature", "measured", "verified"):
                out[key_out] = declared
                notes.append(
                    "EVIDENCE-RULES 판정: " + label + " 지수는 팩 선언값 "
                    + format(declared, "+.3f") + "(" + declared_conf
                    + ", 대상계 직접실측/문헌)이 범용 이론 유도값 "
                    + format(derived, "+.3f") + "(이 계 미검증)보다 등급이 높아 "
                    "선언값을 채택한다. 이론값은 참고로만 남긴다.")
            else:
                notes.append(
                    label + " 지수 불일치: 이론 유도 " + format(derived, "+.3f")
                    + " vs 팩 선언 " + format(declared, "+.3f") + "(" + declared_conf
                    + "). 둘 중 하나가 틀렸다 — 유도 입력(χ·α·공급형태)을 의심하거나, "
                    "선언값이 다른 레짐에서 회귀된 것인지 확인하라.")
    return out
