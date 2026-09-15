"""post-CMP 금속 오염 산출 — 표면 면밀도·단분자층 비율·Boltzmann 정전농축·GOI 조기파괴율·스펙 비율.

지식 근거:
  knowledge/cmp/post-cmp-metallic-contamination-sources.md
    §5 (정량 축 atoms/cm², Si(100) 2/a², 허용치 ~1e10 오더),
    §6 python verify 블록 (A) 단분자층 밀도·허용치 비율, (B) 슬러리 유래 Fe vs 허용치,
    (C) Cu²⁺ 정전흡착의 pH 방향(Boltzmann 표면과잉)
  knowledge/cmp/metal-contamination-device-impact-irds-limits.md
    §2 (Wang et al. 2024 Fe-GOI 실험, doi:10.3390/electronics13122391),
    §5 (ITRS 2.0 각주[14] FEP 스펙 1E10 atoms/cm²),
    §7 python verify 블록 (A) PMOS 조기파괴율 8/71, (B) 세정전 Fe/ITRS스펙 비율
구현 요청: BACKLOG S15 "금속 오염 산출" (surface-contamination 활성 후 게이트 해제)

계약 (엔진과의 경계):
  이 모듈은 순수 함수 라이브러리다. engine.py / models.py에 등록하지 않는다.
  사유: Recipe에 pH·제타전위·오염원별 시계열 필드가 없어(docs/ARCHITECTURE.md §4
  스키마 부채) engine.Model로 조립할 입력이 아직 없다. S17 frictional_heating_arrhenius,
  S19 particle_chemomechanical_synergy, S20 friction_cof_epd와 같은 지위 — "산출값 하나"를
  계산하는 함수만 제공하고, 레시피→오염량 예측 모델은 미완이다.

미검증 사항 (두 노트 §7 그대로, 지어내지 않음):
  - Fe atoms/cm² 수치(세정 전 1~2e12, 세정 후 <1e11)는 **출처 불명·미검증(2차 요약 오귀속)**.
    post-cmp-metallic-contamination-sources.md §7 2026-09-09 추기: Seo et al. 2001
    (doi:10.1023/A:1011242900843) 원문 PDF를 실제 확보해 확인한 결과, 그 논문은 KOH 슬러리
    산화막 CMP의 K·Ca 잔류(PE-TEOS K≈1e12, O₃-BPSG K≈3e13 등, §3.1)를 다루며 Fe 수치는
    본문에 아예 없다 — 아래 SEO2001 딕셔너리 이름과 값을 그 논문 것으로 표기한 것은 오귀속.
    수치 자체(오더값)는 삭제하지 않고 정직하게 "출처 불명"으로 남긴다(precmp_to_spec_ratio()의
    입력 예시로서 오더 감각은 유효하나, Seo 2001을 근거로 인용하지 말 것).
  - 허용치 1e10 atoms/cm²는 ITRS 2.0 각주[14] "FEP 스펙 1E10"으로 1차 확정됐으나
    노드·금속종별 정확 표값(IRDS FEP 표)은 미확보.
  - boltzmann_surface_enrichment()는 균일 확산이중층 Boltzmann 근사 — pH 의존 **방향**만
    검증. 실제 Cu²⁺는 실라놀기 특이(화학)흡착·착화제 경쟁이 겹쳐 절대 흡착량(자리수)은 미검증.
  - Wang 2024는 폴리실리콘 게이트 기원 의도적 Fe 오염이며, CMP 슬러리 기원 표면 Fe와 동일
    기구인지는 미검증. goi_early_failure_ratio()는 그 논문 수치의 산술 재현일 뿐이다.

함수:
  monolayer_density_si100(a_cm)                          -> N_ML = 2/a² [atoms/cm²]
  fraction_of_monolayer(tolerance_atoms_cm2, monolayer)   -> 허용치/단분자층 [ML]
  boltzmann_surface_enrichment(zeta_mV, valence, T_K)     -> n_surf/n_bulk = exp(-z·ψ/(kT/e))
  goi_early_failure_ratio(n_fail, n_total)                -> 조기파괴 비율
  precmp_to_spec_ratio(precmp_atoms_cm2, spec_atoms_cm2)  -> 세정전/스펙 배율
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# 문헌 참조값 (두 노트 §5/§6/§7 그대로 — 재현 검증용 참조표, 여기 외에 새 숫자 없음)
# ---------------------------------------------------------------------------
SI_LATTICE_A_CM = 5.431e-8      # Si 격자상수 5.431 Å (sources.md §5·§6(A), 문헌 상수)
KT_E_MV_298 = 25.69             # kT/e @ 298.15 K [mV] (sources.md §6(C))
T_REF_K = 298.15                # 위 kT/e 의 기준온도 [K] (sources.md §6(C))
CU_VALENCE = 2                  # Cu²⁺ (sources.md §6(C))
ITRS_FEP_SPEC_ATOMS_CM2 = 1e10  # ITRS 2.0 각주[14] FEP 표면금속 스펙 (irds-limits.md §5·§7(B))

# sources.md §6(C) — SiO₂ IEP≈2, pH↑ → ζ 더 음성. 정성 대표값(절대 흡착량 미검증)
ZETA_MV_BY_PH = {"IEP(pH~2)": 0.0, "약산성": -20.0, "중성": -40.0, "약알칼리": -60.0}

# sources.md §6(B) — 출처 불명·미검증(2차 요약 오귀속, 2026-09-09 정정).
# 이름은 관례상 유지하지만 Seo et al. 2001(doi:10.1023/A:1011242900843)의 본문 수치가 아니다 —
# 원문 확보 결과 그 논문은 KOH 슬러리 산화막 CMP의 K·Ca(PE-TEOS/O3-BPSG)를 다루며 Fe 값이 없다.
FE_ORDER_OF_MAGNITUDE_UNVERIFIED = {
    "fe_asdep_atoms_cm2": 1.5e12,   # 세정 전 (100~200)e10 의 중앙값 — 출처 불명
    "fe_clean_atoms_cm2": 1e11,     # 세정 후 <10e10 — 출처 불명
}
SEO2001 = FE_ORDER_OF_MAGNITUDE_UNVERIFIED  # 하위호환 별칭(기존 호출부·테스트 유지용, 출처 아님)
# irds-limits.md §7(B) — 세정 전 W-CMP Fe 잔류 범위 (Lv1-1 §2, 2차 인용)
W_CMP_FE_PRECMP_LOW_ATOMS_CM2 = 1e12
W_CMP_FE_PRECMP_HIGH_ATOMS_CM2 = 2e12

# irds-limits.md §2·§7(A) — Wang et al. 2024, Electronics 13(12) 2391,
# doi:10.3390/electronics13122391 (MDPI CC-BY, 원문 전체 확보)
WANG2024 = {
    "n_total": 71,          # V-Ramp 소자 수/웨이퍼
    "n_fail_pmos_fe": 8,    # PMOS Fe 오염 조기파괴(V_bd < 1.5 V) 소자 수
    "fail_ratio": 0.1127,   # 8/71 (노트 §7(A) assert 값)
    "vbd_spec_v": 4.14,     # 동작전압 1.8 V × 2.3
    "vbd_ref_v": 5.16,      # 오염 없는 기준
    "vbd_nmos_fe_v": 5.15,
    "vbd_pmos_fe_main_v": 5.13,
    "vbd_pmos_fe_early_v": 1.5,
}


# ---------------------------------------------------------------------------
# 1. 단분자층 척도와 허용치 (sources.md §5, §6(A))
# ---------------------------------------------------------------------------

def monolayer_density_si100(a_cm: float = SI_LATTICE_A_CM) -> float:
    """Si(100) 표면원자밀도 N_ML = 2/a² [atoms/cm²] — "1 단분자층(ML)" 척도.

    근거: knowledge/cmp/post-cmp-metallic-contamination-sources.md §5·§6(A).
      a = 5.431 Å → N_ML ≈ 6.78e14 atoms/cm² (단위면적 a²당 2원자).
    """
    if a_cm <= 0:
        raise ValueError("격자상수 a_cm은 양수여야 한다")
    return 2.0 / a_cm ** 2


def fraction_of_monolayer(tolerance_atoms_cm2: float,
                          monolayer_atoms_cm2: float) -> float:
    """허용치/단분자층 비율 [ML] (×1e6 하면 ppm ML).

    근거: knowledge/cmp/post-cmp-metallic-contamination-sources.md §5·§6(A).
      허용치 1e10 / N_ML 6.78e14 ≈ 1.5e-5 ML (≈15 ppm ML) — ppm 수준 제어가 목표임을 정량화.
    """
    if monolayer_atoms_cm2 <= 0:
        raise ValueError("단분자층 밀도는 양수여야 한다")
    return tolerance_atoms_cm2 / monolayer_atoms_cm2


# ---------------------------------------------------------------------------
# 2. Cu²⁺ 정전흡착의 pH 방향 — Boltzmann 표면과잉 (sources.md §3, §6(C))
# ---------------------------------------------------------------------------

def thermal_voltage_mV(T_K: float = T_REF_K) -> float:
    """kT/e [mV]. 298.15 K에서 25.69 mV(노트 §6(C) 상수), 다른 온도는 T/298.15 비례로 재계산.

    근거: knowledge/cmp/post-cmp-metallic-contamination-sources.md §6(C).
      (물리상수 k_B·e를 따로 박지 않고 노트의 25.69 mV × T/T_ref로만 스케일한다 — 새 상수 없음.)
    """
    if T_K <= 0:
        raise ValueError("절대온도 T_K는 양수여야 한다")
    return KT_E_MV_298 * T_K / T_REF_K


def boltzmann_surface_enrichment(zeta_mV: float, valence: int = CU_VALENCE,
                                 T_K: float = T_REF_K) -> float:
    """확산이중층 Boltzmann 표면과잉 n_surf/n_bulk = exp(-z·e·ψ/kT), ψ≈ζ.

    근거: knowledge/cmp/post-cmp-metallic-contamination-sources.md §3·§6(C).
      SiO₂ IEP≈2 → pH>IEP에서 ζ<0, 양이온 Cu²⁺(z=+2) 끌림. pH↑ → |ζ|↑ → 농축↑.
      ζ=0(IEP) → 배율 1; ζ=-40 mV(중성) → 약 22배(>20).
    ⚠ 균일 확산층 근사 — pH 의존 **방향**만 검증. 특이흡착·착화 경쟁이 겹치는
      절대 흡착량(자리수)은 미검증(노트 §7).
    """
    return math.exp(-valence * zeta_mV / thermal_voltage_mV(T_K))


# ---------------------------------------------------------------------------
# 3. 소자 영향·스펙 비율 (irds-limits.md §2, §5, §7)
# ---------------------------------------------------------------------------

def goi_early_failure_ratio(n_fail: int, n_total: int) -> float:
    """GOI(게이트 산화막) 조기파괴 비율 = n_fail / n_total.

    근거: knowledge/cmp/metal-contamination-device-impact-irds-limits.md §2·§7(A).
      Wang et al. 2024, Electronics 13(12) 2391, doi:10.3390/electronics13122391:
      Fe 오염 PMOS 8/71 = 0.1127 (11.3%) 조기파괴(V_bd<1.5 V, β-FeSi₂ 석출물).
    """
    if n_total <= 0:
        raise ValueError("n_total은 양수여야 한다")
    if not (0 <= n_fail <= n_total):
        raise ValueError("n_fail은 0 이상 n_total 이하여야 한다")
    return n_fail / n_total


def precmp_to_spec_ratio(precmp_atoms_cm2: float,
                         spec_atoms_cm2: float = ITRS_FEP_SPEC_ATOMS_CM2) -> float:
    """세정 전 표면금속 면밀도 / 스펙 배율.

    근거: knowledge/cmp/metal-contamination-device-impact-irds-limits.md §5·§7(B).
      스펙 기본값 1e10 atoms/cm² = ITRS 2.0(2015) 각주[14] "FEP 스펙 1E10 atoms/cm²"(1차).
      세정 전 W-CMP Fe 1~2e12(Lv1-1 §2, 2차) → 100~200배.
    """
    if spec_atoms_cm2 <= 0:
        raise ValueError("스펙 면밀도는 양수여야 한다")
    return precmp_atoms_cm2 / spec_atoms_cm2


def _self_test() -> bool:
    results = []

    # --- Test 1: sources.md §6(A) Si(100) N_ML ≈ 6.78e14 (6.5e14 < N_ML < 7.0e14) ---
    N_ML = monolayer_density_si100()
    ok1 = 6.5e14 < N_ML < 7.0e14
    results.append(("§6(A) Si(100) N_ML=2/a² ≈ 6.78e14 atoms/cm²", ok1, f"N_ML={N_ML:.3e}"))

    # --- Test 2: §6(A) 허용치 1e10 / N_ML ≈ 1.5e-5 ML (1e-6 < frac < 1e-4) ---
    frac = fraction_of_monolayer(ITRS_FEP_SPEC_ATOMS_CM2, N_ML)
    ok2 = 1e-6 < frac < 1e-4
    results.append(("§6(A) 허용치 1e10/N_ML ~1e-5 ML 오더", ok2, f"frac={frac:.2e} ML ({frac*1e6:.0f} ppm ML)"))

    # --- Test 3: §6(B) 세정 전 Fe/허용치 >50, 세정 후 >1 ---
    r_asdep = precmp_to_spec_ratio(SEO2001["fe_asdep_atoms_cm2"])
    r_clean = precmp_to_spec_ratio(SEO2001["fe_clean_atoms_cm2"])
    ok3 = r_asdep > 50 and r_clean > 1
    results.append(("§6(B) Fe 세정전/허용치 >50배, 세정후 >1배", ok3, f"asdep={r_asdep:.0f}x, clean={r_clean:.0f}x"))

    # --- Test 4: §6(C) IEP 배율=1, pH↑ 단조증가, 중성 -40mV >20배 ---
    enrich = {k: boltzmann_surface_enrichment(z) for k, z in ZETA_MV_BY_PH.items()}
    vals = list(enrich.values())
    ok4 = (abs(vals[0] - 1.0) < 1e-9
           and all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))
           and enrich["중성"] > 20)
    results.append(("§6(C) Cu2+ Boltzmann: IEP=1, 단조증가, 중성(-40mV) >20배", ok4,
                    ", ".join(f"{k}={v:.1f}x" for k, v in enrich.items())))

    # --- Test 5: §6(C) kT/e 기준값 25.69 mV @298.15 K ---
    ok5 = abs(thermal_voltage_mV() - 25.69) < 1e-9
    results.append(("§6(C) kT/e(298.15K)=25.69 mV", ok5, f"{thermal_voltage_mV():.2f} mV"))

    # --- Test 6: irds-limits.md §7(A) Wang2024 PMOS 8/71 = 0.1127 ---
    fr = goi_early_failure_ratio(WANG2024["n_fail_pmos_fe"], WANG2024["n_total"])
    ok6 = abs(fr - WANG2024["fail_ratio"]) < 0.001
    results.append(("§7(A) Wang2024 PMOS Fe 조기파괴율 8/71=0.1127", ok6, f"{fr:.4f} ({fr*100:.1f}%)"))

    # --- Test 7: §7(B) 세정전 W-CMP Fe/ITRS스펙 100~200배 ---
    r_lo = precmp_to_spec_ratio(W_CMP_FE_PRECMP_LOW_ATOMS_CM2)
    r_hi = precmp_to_spec_ratio(W_CMP_FE_PRECMP_HIGH_ATOMS_CM2)
    ok7 = 90 <= r_lo <= 110 and 190 <= r_hi <= 210
    results.append(("§7(B) 세정전 Fe/ITRS스펙 = 100~200배", ok7, f"{r_lo:.0f}~{r_hi:.0f}x"))

    print("=== metal_contamination_surface.py self-test ===")
    n_pass = 0
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        if ok:
            n_pass += 1
        print(f"[{status}] {name}\n    {detail}")
    print(f"\n{n_pass}/{len(results)} PASS")
    return n_pass == len(results)


if __name__ == "__main__":
    import sys
    success = _self_test()
    sys.exit(0 if success else 1)
