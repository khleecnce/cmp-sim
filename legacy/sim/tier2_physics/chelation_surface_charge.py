"""post-CMP 세정 화학 — 킬레이트 조건부 안정도상수 K'(pH,I)·유리 금속이온 분율, 산화물 표면전하 부호·DHF pH.

지식 근거: knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md
  §3 (IEP·표면전하 부호), §4 (EDTA/시트르산 안정도상수 logK, Davies 이온세기 보정,
  Ringbom α_H 조건부 상수 K'(pH)), §6 python verify 블록 (A) Davies 보정 (B) K'(pH)·
  유리 Cu2+ 분율 (C) IEP·DHF pH·전하 부호
구현 요청: agents/surface-contamination/PROFILE.md Lv2-2 요청1(chelation_conditional_logK)·
  요청2(oxide_surface_charge_sign) (BACKLOG S23)

계약 (엔진과의 경계):
  이 모듈은 순수 함수 라이브러리다. engine.py / models.py에 등록하지 않는다.
  사유: Recipe에 pH·이온세기·킬레이트 농도 필드가 없어(docs/ARCHITECTURE.md §4
  스키마 부채) engine.Model로 조립할 입력이 아직 없다. S15 metal_contamination_surface,
  S17 frictional_heating_arrhenius, S19 particle_chemomechanical_synergy,
  S20 friction_cof_epd, S21 pad_viscoelastic_temperature, S22 ceria_redox_selectivity와
  같은 지위 — "산출값 하나"를 계산하는 함수만 제공하고, 레시피→세정 성능 예측 모델은 미완이다.

미검증 사항 (노트 §4.1·§4.2·§7 그대로, 지어내지 않음):
  - Ca-EDTA logK(I=0.1)의 OA 문헌 대조값은 미확보 — Davies 보정 예측 10.71은 검증 불가로
    남긴다(chelation_conditional_logK는 계산은 하되 이 조합의 정확도를 주장하지 않는다).
  - K'(pH)는 리간드 양성자화만 보정한다. 금속 가수분해·수산화물 침전·혼합 착물·HCit⁻ 착물은
    무시했다 — free_metal_fraction()의 알칼리 영역 값은 실제보다 높게(덜 억제되게) 나올 상한 추정이다.
  - Cu-시트르산 logK(7.57)의 출처 태그는 SCD2.62(IUPAC SC-Database)로 나머지(NIST46.2)와 다르다.
  - IEP(SiO2/CeO2/Al2O3)는 벌크 분말·유리 표면값(Brugnoli 2023, Ederer 2025, Zhang 2024)이며
    CMP 후 실제 박막(TEOS/HDP/low-k)의 IEP·ζ(pH) 곡선은 미확보 — oxide_surface_charge_sign()은
    부호(+/0/-)만 판정하고 |ζ| 크기는 다루지 않는다.
  - 금속 가수분해·수산화물 침전은 IEP 판정에도 반영하지 않았다(노트 §7).

  - chelation_conditional_logK()의 기본값 I=0.0은 노트 §6(B)가 실제로 사용한 경로(K0
    I=0 원값 + Ringbom α_H(pH)만 적용, Davies 이온세기 보정 미체이닝)를 그대로 재현한다.
    노트 §6(A)의 Davies 보정은 I=0→I=0.1 변환 자체의 문헌 대조 검증일 뿐 K'(pH) 계산에
    쓰이지 않는다 — I를 명시적으로 0보다 크게 넘겨 얻는 K'(pH,I) 조합값은 노트가
    검증하지 않은 외삽이다.

함수:
  logK_at_I(logK0, zM, zL, I=0.1)               -> Davies 식 이온세기 보정 logK
  log_alpha_H(betas, pH)                         -> Ringbom log(alpha_H) (리간드 양성자화 경쟁)
  chelation_conditional_logK(ligand, metal, pH, I=0.0) -> 조건부 logK'(pH, I) (I=0 기본: 노트 §6(B) 그대로)
  free_metal_fraction(logK_prime, ligand_conc_M) -> 유리 금속이온 분율 ~ 1/(1+K'*C_L)
  oxide_surface_charge_sign(oxide, pH)           -> '+' / '0' / '-'
  hf_solution_pH(wt_percent, Ka=10**-3.17, mw_hf=20.01) -> DHF 약산 평형 pH
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# 문헌 참조값 (노트 §4·§6 그대로 — 재현 검증용 참조표, 여기 외에 새 숫자 없음)
# ---------------------------------------------------------------------------
A_DH = 0.509  # Debye-Hückel A (25°C, log10 기준) — 교과서 상수 (노트 §6(A))

# 노트 §4.1·§6(A): USGS PHREEQC minteq.v4.dat (NIST46.2 태그) I=0 logK. {금속: (logK0, 원자가)}
EDTA_LOGK_I0 = {"Fe3+": (27.7, 3), "Cu2+": (20.5, 2), "Ca2+": (12.42, 2)}
CIT_LOGK_I0 = {"Fe3+": (13.1, 3), "Cu2+": (7.57, 2), "Ca2+": (4.87, 2)}  # Cu-Cit 출처태그 SCD2.62
K0 = {"EDTA": EDTA_LOGK_I0, "Cit": CIT_LOGK_I0}
LIGAND_CHARGE = {"EDTA": -4, "Cit": -3}  # EDTA4-, Cit3- (완전 탈양성자 형태)

# 노트 §4.1·§6(B): 양성자화 log β_n (n H+ + 리간드 -> 리간드H_n), minteq
BETA_EDTA = [10.948, 17.221, 20.34, 22.5, 24.0]
BETA_CIT = [6.396, 11.157, 14.285]
BETAS = {"EDTA": BETA_EDTA, "Cit": BETA_CIT}

# 노트 §4.1 OA 문헌 대조값 (I=0.1): Kontoghiorghes 2020 Table3 / Palden 2020 평균
EDTA_LOGK_LIT_I01 = {"Fe3+": 25.1, "Cu2+": 18.75}

# 노트 §3·§6(C): IEP [pH] — Brugnoli 2023(SiO2 2.0, CeO2 6.8), Zhang 2024(Al2O3 9.5, 세척 후)
IEP = {"SiO2": 2.0, "CeO2": 6.8, "Al2O3": 9.5}
CEO2_IEP_LIT_RANGE = (5.21, 9.40)  # Ederer 2025 Table 2, 합성법별 실측 범위

HF_PKA = 3.17  # HF 약산 pKa (minteq), 노트 §6(C)
HF_MW_G_MOL = 20.01


# ---------------------------------------------------------------------------
# 1. 킬레이트 조건부 안정도상수 (노트 §4, §6(A)(B))
# ---------------------------------------------------------------------------

def logK_at_I(logK0: float, zM: int, zL: int, I: float = 0.1) -> float:
    """Davies 식으로 I=0 logK를 이온세기 I로 보정.

    logK(I) = logK0 - A*f(I)*(zM^2 + zL^2 - zML^2), f(I) = sqrt(I)/(1+sqrt(I)) - 0.3*I.
    근거: 노트 §6(A). I=0.1에서 Fe-EDTA 27.7->25.13, Cu-EDTA 20.5->18.79
    (문헌 25.1/18.75와 0.3 log 단위 이내 일치).
    """
    if I < 0:
        raise ValueError("이온세기 I는 0 이상이어야 한다")
    f_dav = math.sqrt(I) / (1 + math.sqrt(I)) - 0.3 * I
    zML = zM + zL
    return logK0 - A_DH * f_dav * (zM ** 2 + zL ** 2 - zML ** 2)


def log_alpha_H(betas: list[float], pH: float) -> float:
    """Ringbom 부산물함수 log(alpha_H) = log10(1 + sum_n 10^(beta_n - n*pH)).

    리간드가 양성자화되어 금속과 경쟁하는 정도. 근거: 노트 §4.2·§6(B).
    """
    return math.log10(1 + sum(10 ** (b - n * pH) for n, b in enumerate(betas, 1)))


def chelation_conditional_logK(ligand: str, metal: str, pH: float, I: float = 0.0) -> float:
    """리간드-금속 조건부 안정도상수 K'(pH, I) = logK(I) - log(alpha_H(pH)).

    ligand: 'EDTA' | 'Cit'(시트르산). metal: 'Fe3+' | 'Cu2+' | 'Ca2+'.
    근거: 노트 §4·§6(A)(B). Davies로 이온세기 보정한 logK를 Ringbom α_H로 다시
    pH 보정한다 — 순서를 바꾸지 않는다(노트 §6 코드 순서 그대로).

    ⚠ 기본값 I=0.0: logK_at_I(I=0)은 보정을 걸지 않으므로(f_dav(0)=0) 이 기본값은
    노트 §6(B)의 K0 딕셔너리(I=0 MINTEQ 원값)에 Ringbom α_H(pH)만 적용한 것과
    정확히 같다 — 노트 §4.2·§6(B)가 실제로 검증한 수치(Fe/Cu/Ca EDTA pH3=16.1/8.9/0.8
    등, 유리 Cu2+ 분율<1e-5)는 이 I=0 경로로만 재현된다. 노트의 §6(A) Davies 보정은
    I=0→I=0.1 변환 자체의 검증(문헌 대조)이며 K'(pH) 계산에 체이닝되지 않는다
    (섹션 A·B가 별개 코드블록). I를 명시적으로 0보다 크게 넘기면 Davies 이온세기
    보정까지 추가 적용한 K'(pH,I)를 얻을 수 있으나, 이 조합값은 노트가 직접
    검증하지 않았다.

    선택성 Fe3+ > Cu2+ > Ca2+가 모든 pH·리간드에서 유지된다. pH가 오르면 α_H->1로
    수렴해 logK'가 logK(I)로 회복된다(단조증가). pH 3 시트르산-Ca는 logK'<0
    (착화 사실상 불가).
    """
    if ligand not in K0:
        raise ValueError(f"ligand는 'EDTA' 또는 'Cit': {ligand!r}")
    if metal not in K0[ligand]:
        raise ValueError(f"지원하지 않는 금속: {metal!r}")
    logK0, zM = K0[ligand][metal]
    zL = LIGAND_CHARGE[ligand]
    logK_I = logK_at_I(logK0, zM, zL, I)
    return logK_I - log_alpha_H(BETAS[ligand], pH)


def free_metal_fraction(logK_prime: float, ligand_conc_M: float) -> float:
    """유리(착화되지 않은) 금속이온 분율 ~ 1/(1 + K'*C_L).

    근거: 노트 §4.2·§6(B) — Seo 2019 조건(킬레이트 50 mM, pH 11)에서 EDTA/시트르산
    둘 다 유리 Cu2+ 분율을 1e-5 미만으로 억제.
    ⚠ 가수분해·수산화물 침전 무시한 단순화 — 상한 추정(노트 §7).
    """
    if ligand_conc_M < 0:
        raise ValueError("리간드 농도는 0 이상이어야 한다")
    return 1.0 / (1.0 + 10 ** logK_prime * ligand_conc_M)


# ---------------------------------------------------------------------------
# 2. 산화물 표면전하 부호와 DHF pH (노트 §3, §6(C))
# ---------------------------------------------------------------------------

def oxide_surface_charge_sign(oxide: str, pH: float) -> str:
    """산화물 표면전하 부호: pH<IEP -> '+', pH==IEP -> '0', pH>IEP -> '-'.

    IEP: SiO2=2.0, CeO2=6.8(실측범위 5.21-9.40), Al2O3=9.5. 근거: 노트 §3·§6(C).
    ⚠ 벌크 분말/유리값 — CMP 후 실제 박막 IEP는 미확보(노트 §7).
    """
    if oxide not in IEP:
        raise ValueError(f"지원하지 않는 산화물: {oxide!r} (지원: {list(IEP)})")
    iep = IEP[oxide]
    if pH < iep:
        return "+"
    if pH > iep:
        return "-"
    return "0"


def hf_solution_pH(wt_percent: float, Ka: float = 10 ** -3.17, mw_hf: float = HF_MW_G_MOL) -> float:
    """희석 HF(DHF) 수용액의 약산 평형 pH.

    C_HF[mol/L] = wt_percent/100 * (1000 g/L) / mw_hf (물 밀도 1 g/mL 근사).
    [H+] = (-Ka + sqrt(Ka^2 + 4*Ka*C_HF)) / 2 (약산 평형, HF <-> H+ + F-).
    근거: 노트 §6(C). 0.5 wt% -> C_HF≈0.25 M -> pH≈1.90 (HF pKa 3.17, minteq).
    """
    if wt_percent <= 0:
        raise ValueError("wt_percent는 양수여야 한다")
    if Ka <= 0:
        raise ValueError("Ka는 양수여야 한다")
    C_HF = wt_percent / 100 * 1000 / mw_hf
    H = (-Ka + math.sqrt(Ka ** 2 + 4 * Ka * C_HF)) / 2
    return -math.log10(H)


def _self_test() -> bool:
    results = []

    # --- Test 1: §6(A) Davies 보정 Fe-EDTA≈25.13, Cu-EDTA≈18.79, 문헌 25.1/18.75와 0.3 이내 ---
    zL_edta = LIGAND_CHARGE["EDTA"]
    pred_fe = logK_at_I(*EDTA_LOGK_I0["Fe3+"], zL_edta)
    pred_cu = logK_at_I(*EDTA_LOGK_I0["Cu2+"], zL_edta)
    ok1 = (abs(pred_fe - EDTA_LOGK_LIT_I01["Fe3+"]) < 0.3
           and abs(pred_cu - EDTA_LOGK_LIT_I01["Cu2+"]) < 0.3)
    results.append(("§6(A) Davies보정 Fe-EDTA/Cu-EDTA 문헌 0.3 log 이내", ok1,
                    f"Fe={pred_fe:.2f}(lit {EDTA_LOGK_LIT_I01['Fe3+']}), Cu={pred_cu:.2f}(lit {EDTA_LOGK_LIT_I01['Cu2+']})"))

    # --- Test 2: 선택성 순서 Fe3+ > Cu2+ > Ca2+ (I=0.1, pH11 조건부에서도) ---
    order_ok = all(
        chelation_conditional_logK(L, "Fe3+", 11.0) > chelation_conditional_logK(L, "Cu2+", 11.0)
        > chelation_conditional_logK(L, "Ca2+", 11.0)
        for L in ("EDTA", "Cit")
    )
    results.append(("선택성 순서 Fe3+ > Cu2+ > Ca2+ (EDTA·Cit, pH11)", order_ok, ""))

    # --- Test 3: pH 3/7/11에서 K'(pH) 단조증가 ---
    mono_ok = True
    for L in ("EDTA", "Cit"):
        for m in ("Fe3+", "Cu2+", "Ca2+"):
            vals = [chelation_conditional_logK(L, m, pH) for pH in (3.0, 7.0, 11.0)]
            mono_ok &= vals[0] < vals[1] < vals[2]
    results.append(("pH 3<7<11 에서 K'(pH) 단조증가 (전 리간드x금속)", mono_ok, ""))

    # --- Test 4: pH3 시트르산-Ca<0(착화 불가), Fe3+>0 ---
    kc_cit_ca_ph3 = chelation_conditional_logK("Cit", "Ca2+", 3.0)
    kc_cit_fe_ph3 = chelation_conditional_logK("Cit", "Fe3+", 3.0)
    ok4 = kc_cit_ca_ph3 < 0 < kc_cit_fe_ph3
    results.append(("pH3 시트르산: Ca logK'<0(착화불가), Fe3+ logK'>0", ok4,
                    f"Ca={kc_cit_ca_ph3:.2f}, Fe3+={kc_cit_fe_ph3:.2f}"))

    # --- Test 5: pH11, 50mM 킬레이트에서 유리 Cu2+ 분율 < 1e-5 (EDTA/Cit 둘 다) ---
    frac_ok = True
    fracs = {}
    for L in ("EDTA", "Cit"):
        kc = chelation_conditional_logK(L, "Cu2+", 11.0)
        fr = free_metal_fraction(kc, 0.050)
        fracs[L] = fr
        frac_ok &= fr < 1e-5
    results.append(("pH11·50mM 킬레이트: 유리 Cu2+ 분율 < 1e-5 (EDTA·Cit)", frac_ok,
                    ", ".join(f"{k}={v:.1e}" for k, v in fracs.items())))

    # --- Test 6: DHF 0.5wt% pH in (1.5, 2.5), HF pKa=3.17 ---
    pH_dhf = hf_solution_pH(0.5)
    ok6 = 1.5 < pH_dhf < 2.5
    results.append(("DHF 0.5wt% pH in (1.5, 2.5)", ok6, f"pH={pH_dhf:.2f}"))

    # --- Test 7: pH_dhf에서 SiO2/CeO2/Al2O3 전부 '+' ---
    ok7 = all(oxide_surface_charge_sign(ox, pH_dhf) == "+" for ox in IEP)
    results.append(("pH_dhf에서 SiO2·CeO2·Al2O3 전부 '+'", ok7,
                    ", ".join(f"{ox}{oxide_surface_charge_sign(ox, pH_dhf)}" for ox in IEP)))

    # --- Test 8: pH 11에서 세 산화물 전부 '-' ---
    ok8 = all(oxide_surface_charge_sign(ox, 11.0) == "-" for ox in IEP)
    results.append(("pH11에서 세 산화물 전부 '-'", ok8,
                    ", ".join(f"{ox}{oxide_surface_charge_sign(ox, 11.0)}" for ox in IEP)))

    # --- Test 9: pH 5에서 CeO2 '+' / SiO2 '-' (이부호) ---
    ok9 = oxide_surface_charge_sign("CeO2", 5.0) == "+" and oxide_surface_charge_sign("SiO2", 5.0) == "-"
    results.append(("pH5에서 CeO2(+)/SiO2(-) 이부호", ok9,
                    f"CeO2={oxide_surface_charge_sign('CeO2', 5.0)}, SiO2={oxide_surface_charge_sign('SiO2', 5.0)}"))

    # --- Test 10: CeO2 IEP 6.8이 Ederer 2025 실측범위 5.21~9.40 안 ---
    ok10 = CEO2_IEP_LIT_RANGE[0] <= IEP["CeO2"] <= CEO2_IEP_LIT_RANGE[1]
    results.append(("CeO2 IEP 6.8이 Ederer2025 실측범위 5.21~9.40 안", ok10,
                    f"IEP={IEP['CeO2']}, range={CEO2_IEP_LIT_RANGE}"))

    print("=== chelation_surface_charge.py self-test ===")
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
