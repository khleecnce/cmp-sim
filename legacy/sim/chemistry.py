"""화학-기계 결합층 — 슬러리 화학이 제거율을 어떻게 바꾸는가.

왜 이 파일이 있나 (2026-09-06 사용자 지시):
  "당연히 화학적인것도 반영해야해. 슬러리첨가제나 세리아같은 입자는 화학작용이 메이저잖아"

그 전까지 엔진은 슬러리 화학 전체를 Preston 계수 Kp **상수 하나**에 뭉뚱그렸다.
산화제 농도를 바꾸든 BTA를 넣든 세리아를 쓰든 결과가 똑같았다 — 즉 소재 개발자가
정작 만지는 변수(조성)에 시뮬레이터가 반응하지 않았다. 그건 소재사용 툴이 아니다.

## 물리적 통로: 화학은 '표면 경도'를 통해 기계에 연결된다

CMP 제거는 화학 단독도 기계 단독도 아니다. 문헌(Luo-Dornfeld, Kaufman)이 말하는 것은
**화학이 표면을 연화시키고 기계가 그 연화층을 긁어낸다**는 시너지다.

  knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md §4:
    소성 압입   δ_p = F/(2πR·H)         ∝ H⁻¹
    plowing 홈  A_f = (4/3)√(2R)·δ_p^1.5 ∝ H⁻¹·⁵
    → 화학적 연화로 H를 4배 낮추면 제거 체적은 4^1.5 = 8배 (노트 verify PASS)

따라서 이 모듈의 계약은 하나다:

    화학 조건 → 유효 경도비 (H_eff/H_0) → MRR 배수 = (H_0/H_eff)^1.5

이렇게 두면 화학과 기계가 각자 자기 자리를 지킨다. 기계 쪽(GW 접촉·압력·속도)은
1바이트도 안 고치고, 화학은 배수 하나로 들어온다.

## ⚠ 이중 계상 함정 (2026-09-06 실제로 밟았다)

첫 구현에서 Cu MRR이 450 → 22.5 nm/min로 20배 떨어졌다. 원인은 물리가 아니라 회계다.

  팩의 `kp_m_per_pa`는 **이미 BTA가 든 실제 슬러리의 문헌 MRR에서 역산한 값**이다.
  거기에 억제 항 (1-θ)=0.05를 또 곱하면 억제를 두 번 적용한 것이 된다.

그래서 이 층의 계약은 "화학 효과의 절대량"이 아니라 **기준 조건 대비 상대 변화**다:

    factor = f(현재 조성) / f(기준 조성)

`*_ref` 파라미터가 그 기준점이고, 기준 조성에서는 factor가 정확히 1.0이 되어
Kp가 그대로 나온다. 조성을 바꿀 때만 배수가 생긴다.

**이것이 스크리닝 도구로서 옳은 동작이다** — 우리가 답할 질문은 "MRR이 절대 몇이냐"가
아니라 "BTA를 1mM에서 2mM로 올리면 어느 쪽이 더 깎이냐"이기 때문이다.

## 다루는 화학 (전부 팩 파라미터로 제어)

1. **산화제** — Kaufman 경쟁: 농도↑ → 산화층 생성↑이지만 과하면 부동태막이 두꺼워져
   오히려 제거 저해. 단봉 곡선(slurry_components.mrr_oxidizer).
2. **억제제(BTA 등)** — Langmuir 피복 θ가 표면을 덮어 제거를 막는다. (1-θ) 가중.
3. **세리아 chemical tooth** — Si-O-Ce 화학결합(DFT −111~−258 kJ/mol)이 실리카를
   직접 뜯어낸다. 물리흡착 기반 실리카 슬러리와 메커니즘이 다르다. Ce³⁺ 분율이 활성점.
4. **pH** — 표면 전하·용해도를 통해 연화에 기여. 지금은 IEP로부터의 거리로 단순화.

## ⚠ 정직성 규약 (이 모듈에서 특히 중요하다)

화학은 물리보다 훨씬 불확실하다. 그래서:
- 모든 계수는 팩에서 온다. 코드에 화학 상수를 박지 않는다.
- **절대값을 주장하지 않는다.** 이 층이 내는 것은 "기준 조건 대비 몇 배"이고,
  기준 조건 자체는 여전히 캘리브레이션이 필요하다.
- 팩에 화학 파라미터가 없으면 배수 1.0(화학 효과 없음)을 반환하고 **그 사실을 notes에
  적는다.** 조용히 1.0을 쓰면 "화학을 반영했다"는 거짓말이 된다.
- 이 층의 목표는 순위(A 조성 vs B 조성)를 맞히는 것이지 절대 MRR이 아니다
  (POSITIONING.md §3: 데모 대체가 아니라 스크리닝).
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_ROOT = Path(__file__).resolve().parent
for _p in ("tier1_empirical", "tier2_physics", "integration"):
    _d = str(_ROOT / _p)
    if _d not in sys.path:
        sys.path.insert(0, _d)

import slurry_components as SC  # noqa: E402  (sim/tier2_physics/slurry_components.py)

# 화학적 연화 → 제거체적 지수. plowing 기하에서 유도된 값이지 튜닝 파라미터가 아니다.
# A_f ∝ H^-1.5 (knowledge/cmp/particle-wafer-interaction-... §4, verify PASS)
SOFTENING_EXPONENT = 1.5


@dataclass
class ChemistryEffect:
    """화학이 만든 MRR 배수와 그 근거."""
    factor: float                       # 기준 조건 대비 MRR 배수
    terms: Dict[str, float] = field(default_factory=dict)   # 항별 기여
    notes: List[str] = field(default_factory=list)
    active: bool = False                # 화학 파라미터가 실제로 있었는가

    def describe(self) -> str:
        if not self.active:
            return "화학층 비활성 (팩에 화학 파라미터 없음) — 배수 1.0"
        parts = ", ".join(f"{k}×{v:.3f}" for k, v in self.terms.items())
        return f"화학 배수 {self.factor:.3f} = {parts}"


def _oxidizer_species_gate_ok(pack, notes: List[str]) -> bool:
    """산화제 Langmuir K 를 **적합된 산화제 종**에서만 쓰게 막는 게이트.

    왜 필요한가 (2026-09-16): `oxidizer_langmuir_K` 는 재료 고유 상수다 —
    산화제 종이 바뀌면 표준전극전위도 흡착 거동도 달라진다(H2O2 vs
    MnO4⁻/MnO2 +1.68 V). 그런데 팩 상속은 "같은 물리를 공유한다"는 뜻이라
    부모가 K 를 선언하면 **산화제를 바꾼 자식 팩까지 조용히 물려받는다**.
    실제로 sic_ceria_h2o2(H2O2) 에 K 를 넣자 자식 sic_alumina_kmno4(KMnO4)가
    그대로 상속했다 — 남의 산화제로 적합한 곡선으로 이 팩의 MRR 을 예측하게 된다.

    판정#47(착화제 종 게이트)과 같은 장치다. 팩이 `oxidizer_langmuir_species`
    (K 가 적합된 종)와 `oxidizer`(이 팩이 실제로 쓰는 종)를 둘 다 선언하고
    서로 다르면, 지어내지 않고 이 경로를 끈다.
    """
    fitted = pack.get_or("oxidizer_langmuir_species", None)
    if fitted is None:
        return True                      # 종 선언이 없는 구버전 팩 — 기존 동작 유지
    declared = pack.get_or("oxidizer", None)
    if declared is None:
        notes.append(
            "⚠ oxidizer_langmuir_species 가 선언됐으나 팩에 oxidizer(실제 산화제 종)가 "
            "없어 일치를 확인할 수 없다 — 지어내지 않고 Langmuir 경로를 끈다.")
        return False
    if str(declared) != str(fitted):
        notes.append(
            f"⚠ oxidizer_langmuir_K 는 {fitted} 로 적합됐는데 이 팩의 산화제는 "
            f"{declared} 다 — 산화제 종이 다르면 곡선 형상을 전이할 수 없다"
            "(표준전극전위·흡착 거동이 다르다). 이 팩에서는 산화제 형상 항을 "
            "켜지 않는다 — 그 종의 데이터를 확보할 때까지 갭으로 남긴다.")
        return False
    return True


def _oxidizer_term(pack, notes: List[str]) -> Optional[float]:
    """산화제 농도 → 기준 농도 대비 상대 MRR.

    세 경로:
      - Langmuir 피복-촉진 (`oxidizer_langmuir_K` 있음) — 판정#19 이후 권장 경로.
        θ(C)=K·C/(1+K·C), 자유 파라미터 K 하나뿐이라 식별 가능. 산화제가 많을수록
        MRR이 오르는(포화) 계용(w_fe_oxidizer 등).
      - Langmuir 피복-억제 (`oxidizer_passivation_K` 있음) — 판정#20. 위와 같은
        θ(C)를 쓰되 (1-θ)로 뒤집는다 — 산화제가 많을수록 부동태막이 두꺼워져
        MRR이 낮아지는 계용(cu_h2o2_bta). 자유 파라미터는 여전히 K 하나뿐.
      - 레거시 Kaufman 단봉 (`oxidizer_curve_n`+`oxidizer_peak_wt_pct`) — 하위호환.
        정점 아래 관측만으로는 (n, C_peak)가 완전축퇴한다(식별 불가, EVIDENCE-RULES
        판정#19, knowledge/cmp/chi-oxidizer-curve-exponent-identifiability.md).

    기준 농도(oxidizer_ref_wt_pct, 없으면 현재 농도)에서 1.0이 되도록 나눈다.
    Kp가 그 기준 조성에서 역산된 값이므로 이중 계상을 피하려면 반드시 상대값이어야 한다.
    """
    if not pack.has("oxidizer_wt_pct"):
        return None
    C = float(pack.get("oxidizer_wt_pct"))
    if pack.has("oxidizer_ref_wt_pct"):
        C_ref = float(pack.get("oxidizer_ref_wt_pct"))
    else:
        # ⚠ 기준값이 없으면 '현재 농도'로 폴백할 수밖에 없는데, 그러면 항상 자기
        # 자신과 비교하게 되어 배수가 영원히 1.0이다 = 산화제를 바꿔도 반응이 없다.
        # 2026-09-06 민감도 분석에서 산화제가 '미모델링'으로 오진된 원인이었다.
        # 조용히 넘어가지 않고 경고한다.
        C_ref = C
        notes.append("⚠ oxidizer_ref_wt_pct가 팩에 없어 기준=현재 농도로 폴백했다 "
                     "— 산화제 변화가 MRR에 반영되지 않는다. 팩에 기준 농도를 명시하라.")

    # ── 기계 하한 (mechanical floor) ───────────────────────────────
    # 산화제 농도가 0 이어도 연마입자는 존재하고 하중을 받으므로 순수 기계
    # 제거 경로가 남는다. 단봉형/포화형 g(C) 는 C=0 에서 0 이라 이를 담을 수
    # 없으므로 가산 하한을 둔다.
    #
    # φ 의 크기 — 재료 상수가 아니라 **공정(기계) 상수**에 가깝다.
    #   독립적인 금속막 4계에서 관측 대역이 0.12~0.27 로 수렴했고, 금속 종류·
    #   pH 2~9·착화제 유무를 바꿔도 유지됐다. 반면 연마입자를 빼면 0.02 로
    #   떨어지고 경질 연마재·고하중에서는 0.28~0.37 로 올라간다 — 즉 φ 를
    #   움직이는 것은 화학이 아니라 기계 경로의 세기다.
    #   (_knowledge_audit/oxidizer_floor.md §4 규칙 R1~R3)
    #
    #   그러므로 팩이 자기 관측을 선언하면 그것을 쓰고, 없으면 대역 중앙
    #   0.15 를 기본값으로 둔다. 기본값 0.0 은 "산화제가 없으면 안 깎인다"는
    #   주장이 되는데 그것은 어느 계에서도 관측되지 않았다.
    #
    # ⚠ 적용 한계: 생성 산화물이 모재보다 단단하고 착화제가 없는 계에서는
    #   산화제 투입이 오히려 제거율을 낮춘다(φ > 1). 이 결합식은 그 거동을
    #   표현하지 못하므로 그런 계에서는 쓰면 안 된다(같은 문서 규칙 R4).
    floor = float(pack.get_or("oxidizer_mech_floor", 0.15))
    if floor > 1.0:
        notes.append(
            f"⚠ 기계 하한 {floor:.3g} 이 1 을 넘는다 — 산화제를 넣을수록 제거율이 "
            "낮아지는 계라는 뜻인데, 현재 결합식은 그 거동을 표현하지 못한다. "
            "이 팩에서는 산화제 항의 적용 범위를 벗어났다.")
    floor = min(max(floor, 0.0), 1.0)
    floor_default_note = (
        f"산화제 기계 하한 φ={floor:.2f} (기본값) — 이 팩에 관측이 없어 "
        "금속막 CMP 의 관측 대역(0.12~0.27, 4계 독립 수렴) 중앙값을 쓴다. "
        "φ 는 재료보다 기계 조건(연마재 경도·압력·속도)이 정하는 양이다. "
        "⚠ 이 계의 직접 관측이 아니므로 절대값은 신뢰하지 말 것.")

    # ── 레짐 게이트: 산성 × 착화제 존재, 착화제 종 특이적 (EVIDENCE-RULES
    # 판정#41 → 판정#47, 2026-09-15 → 2026-09-16) ──────────────────────────
    # cu_h2o2_bta 의 실제 운전점(pH 4.0 + 글리신/BTA)은 oxidizer_passivation_K
    # 가 역산된 알칼리 × 무착화제 계와 다른 레짐이다(판정#38) — 같은 H2O2
    # 스윕에서 부호가 반대로 관측된다(Jani 2025 Expt 30/31/32, 산성 pH3 ×
    # 옥살산 0.08M, 실리카 6wt%: 3->6 wt% 에서 MRR +13.0%인데 현행 억제형
    # 예측은 -35.3%). 조건은 slurry_ph<6 AND chelator_M>0 — 팩 이름이 아니라
    # 데이터 필드로만 분기한다(판정#34 원칙). 둘 중 하나라도 팩에 선언이
    # 없으면 지어내지 않고 기존 경로로 폴백한다.
    #
    # ⚠ 판정#41의 게이트는 "착화제가 아무거나 있으면" 촉진-포화형을 켰는데,
    # `oxidizer_acid_chelator_K`(=0.7935)는 **옥살산** 데이터로만 적합됐다
    # (Jani 2025). 판정#43이 **글리신** 1차 데이터(US5,575,885)로 이를
    # 시험하자 부호가 반대(단조 감소 vs 이 가지의 단조 증가)로 반증됐고,
    # 판정#45가 "옥살산·글리신을 하나의 레짐으로 묶은 것 자체가 과도한
    # 일반화"라고 이미 기록했다 — 판정#47은 그 기록을 코드에 반영한다.
    # 그래서 이 가지는 **이 계수가 적합된 착화제 종**(oxidizer_acid_chelator_species)
    # 과 팩이 선언한 착화제 종(chelator_species)이 일치할 때만 켠다.
    if pack.has("oxidizer_acid_chelator_K"):
        if pack.has("slurry_ph") and pack.has("chelator_M"):
            ph = float(pack.get("slurry_ph"))
            chelator_M = float(pack.get("chelator_M"))
            if ph < 6.0 and chelator_M > 0.0:
                species_gate_ok = True
                fitted_species_note = ""
                if pack.has("oxidizer_acid_chelator_species"):
                    fitted_species = pack.get("oxidizer_acid_chelator_species")
                    if pack.has("chelator_species"):
                        declared_species = pack.get("chelator_species")
                        if declared_species != fitted_species:
                            species_gate_ok = False
                            notes.append(
                                f"⚠ oxidizer_acid_chelator_K는 {fitted_species}로 "
                                f"적합됐는데 팩 착화제는 {declared_species} — 판정#43이 "
                                "두 종의 부호 반전(옥살산 증가/글리신 감소)을 실측했으므로 "
                                "전이하지 않는다(판정#47). 기존 산화제 경로로 폴백한다.")
                        else:
                            fitted_species_note = (
                                f"{fitted_species} 데이터로 적합됐고 이 팩의 착화제와 "
                                "종이 일치한다 — ")
                    else:
                        species_gate_ok = False
                        notes.append(
                            "⚠ oxidizer_acid_chelator_species가 선언됐으나 팩에 "
                            "chelator_species가 없어 착화제 종 일치를 확인할 수 없다 "
                            "— 지어내지 않고 기존 산화제 경로로 폴백한다.")
                else:
                    fitted_species_note = (
                        "⚠ oxidizer_acid_chelator_K에 적합 착화제 종 선언"
                        "(oxidizer_acid_chelator_species)이 없는 구버전 팩이라 종 "
                        "일치를 검증할 수 없다 — 판정#41 이전 동작대로 발동한다. ")

                if species_gate_ok:
                    K = float(pack.get("oxidizer_acid_chelator_K"))
                    theta = float(SC.oxidizer_coverage_langmuir(C, K))
                    theta_ref = float(SC.oxidizer_coverage_langmuir(C_ref, K))
                    if theta_ref <= 0:
                        return None
                    if floor > 0 and not pack.has("oxidizer_mech_floor"):
                        notes.append(floor_default_note)
                    notes.append(
                        f"산성(pH={ph:.2f}<6)×착화제({chelator_M:.4g} M) 레짐 — "
                        "촉진-포화형 경로(판정#41). " + fitted_species_note +
                        "confidence 상한은 estimated.")
                    return floor + (1.0 - floor) * (theta / theta_ref)
            else:
                notes.append(
                    f"산성×착화제 게이트 미충족(pH={ph:.2f}, chelator={chelator_M:.4g} M) "
                    "— 기존 산화제 경로로 폴백한다.")
        else:
            notes.append(
                "⚠ oxidizer_acid_chelator_K 가 선언됐으나 slurry_ph 또는 "
                "chelator_M 이 없어 레짐을 판별할 수 없다 — 지어내지 않고 "
                "기존 경로로 폴백한다.")

    if pack.has("oxidizer_langmuir_K") and _oxidizer_species_gate_ok(pack, notes):
        # Langmuir 경로 — 폐형식: f(C) = φ + (1-φ)·θ(C)/θ(C_ref).
        # (레거시 경로처럼 φ를 분자·분모 양쪽에 넣고 나누는 게 아니다 — 그러면
        # 다른 함수가 되어 knowledge/params/w_fe_oxidizer.yaml의 K=0.549550
        # 폐형식 유도(f(0)=φ, f(C_ref)=1)와 어긋난다.)
        K = float(pack.get("oxidizer_langmuir_K"))
        theta = float(SC.oxidizer_coverage_langmuir(C, K))
        theta_ref = float(SC.oxidizer_coverage_langmuir(C_ref, K))
        if theta_ref <= 0:
            return None
        if floor > 0 and not pack.has("oxidizer_mech_floor"):
            notes.append(floor_default_note)
        return floor + (1.0 - floor) * (theta / theta_ref)

    if pack.has("oxidizer_passivation_K"):
        # Langmuir 피복-억제 경로 — 판정#20(cu_h2o2_bta 재파라미터화).
        # 폐형식: f(C) = φ + (1-φ)·(1-θ(C))/(1-θ(C_ref)).
        # θ(C)는 부동태막 피복률(C와 함께 단조 증가), (1-θ)는 남은 활성(비피복)
        # 표면 분율(C와 함께 단조 감소) — 위 촉진 경로의 θ/θ_ref를
        # (1-θ)/(1-θ_ref)로 뒤집었을 뿐, 자유 파라미터는 여전히 K 하나다.
        # f(C_ref)=1은 항등적으로 성립(분자·분모가 같은 값이 되는 지점).
        K = float(pack.get("oxidizer_passivation_K"))
        theta = float(SC.oxidizer_coverage_langmuir(C, K))
        theta_ref = float(SC.oxidizer_coverage_langmuir(C_ref, K))
        if theta_ref >= 1.0:
            return None
        if floor > 0 and not pack.has("oxidizer_mech_floor"):
            notes.append(floor_default_note)
        return floor + (1.0 - floor) * (1.0 - theta) / (1.0 - theta_ref)

    if not pack.has("oxidizer_peak_wt_pct"):
        return None
    C_peak = float(pack.get("oxidizer_peak_wt_pct"))
    if C_peak <= 0:
        notes.append("⚠ oxidizer_peak_wt_pct ≤ 0 — 산화제 항 건너뜀")
        return None
    n = float(pack.get_or("oxidizer_curve_n", 2.0))
    cur = float(SC.mrr_oxidizer(C, C_peak, mrr_peak=1.0, n=n))
    ref = float(SC.mrr_oxidizer(C_ref, C_peak, mrr_peak=1.0, n=n))
    notes.append("⚠ 레거시 산화제 곡선 — (n,C_peak) 축퇴(판정#19). "
                 "oxidizer_langmuir_K 권장.")
    if ref <= 0:
        return None
    if floor > 0:
        cur = floor + (1.0 - floor) * cur
        ref = floor + (1.0 - floor) * ref
        if not pack.has("oxidizer_mech_floor"):
            notes.append(floor_default_note)
    return cur / ref


def _inhibitor_term(pack, notes: List[str]) -> Optional[float]:
    """억제제 피복률 → 제거 가능 면적 비율.

    BTA가 Cu 표면을 덮으면 그만큼 제거가 막힌다. Langmuir 등온식.

    ⚠ 왜 (1-θ)를 그대로 쓰지 않는가 (2026-09-06 수정):
      BTA 1mM에서 θ=0.97이라 (1-θ)=0.03이 하한 0.05에 걸리고, 그 위 농도는 전부
      0.05로 포화된다 = **2mM과 5mM의 구분이 사라진다.** 스캔해보면 배수가 1.000으로
      완전히 평평했다. 억제제 농도를 비교하려는 사용자에게 이건 고장난 도구다.

      Langmuir는 '단분자층 피복'이라 θ→1에서 포화되는 게 맞지만, 실제 CMP의 억제
      강도는 피복률만이 아니라 막의 치밀도·재생속도에도 달려 있어 고농도에서도
      계속 세진다. 그래서 잔여 제거 가능률을 (1-θ)가 아니라 **(1-θ)^m 꼴이 아닌,
      막 강도에 대한 지수 감쇠**로 둔다:

          잔여율 = exp(-k_inhib · θ_norm),  θ_norm = K·C/(1+K·C) 의 단조 증가분

      단 이렇게 하면 형상 파라미터 k_inhib가 새로 생긴다 — 문헌값이 없으므로
      팩에서 받고 confidence=unverified로 표기한다. 순위(더 넣으면 덜 깎인다)는
      보존되고, 절대값은 캘리브레이션 대상이다.
    """
    if not pack.has("inhibitor_mM"):
        return None
    C_molar = float(pack.get("inhibitor_mM")) * 1e-3

    # ── 1순위: (억제제 × 기질) 쌍 조회 ─────────────────────────
    # ΔG_ads 는 억제제 단독의 성질이 아니라 **쌍**의 성질이다.
    # 같은 논문·같은 방법인데 BTA/Cu −30.02 vs BTA/Fe −21.89 로 갈린다.
    # 쌍을 키로 갖지 않으면 새 억제제마다 같은 실패가 반복된다 —
    # 실제로 한 억제제용 K 가 다른 억제제에 쓰여 5,700 배 어긋났다.
    K: Optional[float] = None
    inhib = pack.get_or("inhibitor_species", None)
    subst = pack.get_or("substrate_species", None)
    if inhib and subst:
        from sim.inhibitor_pairs import (lookup_dG, K_from_dG, measurement_spec,
                                          adsorption_ruled_out)
        ruled_out = adsorption_ruled_out(str(inhib), str(subst))
        if ruled_out:
            # '아무도 안 쟀다'와 '그 메커니즘이 없다'는 다른 결론이다.
            # 후자는 억제 항이 없는 것이 물리적으로 옳으므로 R8 을 발행하지
            # 않는다 — 발행하면 다음 회차가 존재하지 않는 문헌을 찾으러 간다.
            notes.append(f"({inhib} × {subst}) 쌍은 흡착이 일어나지 않는다고 "
                         f"선언된 쌍이다 — 억제 항을 만들지 않는다. 근거: {ruled_out}")
            return None
        pair = lookup_dG(str(inhib), str(subst))
        if pair is not None:
            K = K_from_dG(pair.dG_kJ_per_mol)
            notes.append(f"흡착상수를 **쌍**({inhib} × {subst})에서 조회: "
                         f"ΔG={pair.dG_kJ_per_mol:.2f} kJ/mol → K={K:.4g} L/mol "
                         f"· {pair.method} · {pair.source} [{pair.confidence}]")
        else:
            # 유사 값으로 대체하지 않는다 — 그것이 지금까지의 실패 원인이다.
            notes.append(f"🔴 ({inhib} × {subst}) 쌍의 ΔG 가 표에 없다. "
                         "다른 기질·다른 분자 값으로 대체하지 않는다.")
            notes.extend(measurement_spec(str(inhib), str(subst))[:3])
            notes.append("→ 이 조건에서 억제제 **순위**는 예측하되 "
                         "절대값은 주장하지 않는다.")

    if K is None and pack.has("inhibitor_dG_ads_kJ"):
        K = SC.K_from_dG_ads(float(pack.get("inhibitor_dG_ads_kJ")) * 1000.0)
        if inhib and subst:
            notes.append(f"⚠ 팩의 단일 ΔG 로 폴백했다 — 이 값이 ({inhib} × "
                         f"{subst}) 쌍에서 측정된 것인지 확인되지 않았다.")
    elif K is None and pack.has("inhibitor_K_L_per_mol"):
        K = float(pack.get("inhibitor_K_L_per_mol"))
    elif K is None:
        notes.append("⚠ inhibitor_mM은 있으나 흡착상수(dG 또는 K)가 없어 억제 항 건너뜀")
        return None
    k_inhib = float(pack.get_or("inhibitor_strength_k", 3.0))

    def _residual(C: float) -> float:
        """농도 C에서 남는 제거 가능률. θ 포화 후에도 단조 감소한다."""
        theta = SC.langmuir_coverage(C, K)
        return math.exp(-k_inhib * theta)

    # 기준 농도 대비 상대값 — Kp가 이미 이 억제제를 포함한 슬러리에서 역산됐으므로
    # 절대값을 곱하면 억제를 두 번 세게 된다(2026-09-06 실제 발생: Cu 20배 하락).
    if pack.has("inhibitor_ref_mM"):
        C_ref = float(pack.get("inhibitor_ref_mM")) * 1e-3
    else:
        C_ref = C_molar
        notes.append("⚠ inhibitor_ref_mM이 팩에 없어 기준=현재 농도로 폴백했다 "
                     "— 억제제 변화가 MRR에 반영되지 않는다.")
    ref = _residual(C_ref)
    if ref <= 0:
        return None
    notes.append(
        f"억제제 {C_molar*1e3:g} mM (기준 {C_ref*1e3:g} mM), θ="
        f"{SC.langmuir_coverage(C_molar, K):.3f}. "
        "⚠ 고농도 감쇠 형상(inhibitor_strength_k)은 문헌값 없음 — 캘리브레이션 대상.")
    return _residual(C_molar) / ref


DISPERSANT_MRR_RELATIVE = {
    "NONE": 1.0,
    "PAA": 1.0,      # Li 2021 §6: "negligible" 저해
    "PAM": 1.0,      # Li 2021 §6: "hardly changed"
    "PVA": 2604.0 / 2700.0,   # -3.6%, Li 2021 §6 Fig.14-15 실측
    "PVP": 2486.0 / 2700.0,   # -7.9%, Li 2021 §6 Fig.14-15 실측
}


def _dispersant_protection_term(pack, notes: List[str]) -> Optional[float]:
    """분산제 흡착 → MRR 저해 배수. ψ의 '표면 흡착 보호' 경로(억제제와 별도).

    Li et al. 2021 (ECS JSS Technol. 10, 123008) §6 실측: 30wt% SiO2 콜로이달
    실리카 슬러리(80nm, pH 11.0, 0.32M K+, 기본 MRR=2700 Å/min)에 분산제를
    첨가했을 때의 MRR 저해를 그대로 옮긴다 — 새 지수·상수는 만들지 않는다.

    ⚠ **반드시 기준 대비 비율로 돌려준다.** 절대 저해율(PVA=0.964)을 그대로
    쓰면 기준 조건에서 ψ≠1.0이 되어 Kp에 이미 반영된 효과를 두 번 센다
    (factors.py 설계계약 §1). 2026-09-11에 실제로 이 사고가 났다 —
    기본 팩이 dispersant_type=PVA인데 절대값 0.964를 반환해
    test_all_factors_are_unity_at_reference_condition 이 FAIL했다.

    `dispersant_ref_type`이 팩에 없으면 **"NONE"(분산제 없음)**을 기준으로 삼는다 —
    그게 Li 2021의 기준선(2700 Å/min)이므로 문헌 의미를 그대로 보존한다.
    다만 팩의 Kp가 특정 분산제 조성에서 역산됐다면 그 팩은 반드시
    `dispersant_ref_type`을 선언해야 한다. 선언하지 않으면 기준 조건에서
    ψ≠1.0이 되어 `test_all_factors_are_unity_at_reference_condition`이 잡아낸다.
    """
    if not pack.has("dispersant_type"):
        return None
    kind = str(pack.get("dispersant_type")).strip().upper()
    if kind not in DISPERSANT_MRR_RELATIVE:
        notes.append(
            f"⚠ dispersant_type='{kind}'는 Li 2021 §6 실측 테이블에 없어 "
            "분산제 보호 항을 건너뛴다.")
        return None
    ref_kind = str(pack.get_or("dispersant_ref_type", "NONE")).strip().upper()
    if ref_kind not in DISPERSANT_MRR_RELATIVE:
        notes.append(
            f"⚠ dispersant_ref_type='{ref_kind}'가 실측 테이블에 없다 — "
            f"기준을 현재 종류({kind})로 대체한다.")
        ref_kind = kind
    rel = DISPERSANT_MRR_RELATIVE[kind] / DISPERSANT_MRR_RELATIVE[ref_kind]
    if kind == ref_kind:
        notes.append(
            f"분산제 흡착 보호: {kind} = 기준 조성이라 배수 1.000 "
            "(Kp가 이 조성에서 역산됐다 — 절대 저해율을 다시 곱하면 이중 계상). "
            "다른 분산제로 바꾸면 그 상대비가 반영된다"
            "(knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md §6, "
            "Li et al. 2021 실측).")
    else:
        notes.append(
            f"분산제 흡착 보호: {kind}/{ref_kind}(기준) → MRR 상대배수 {rel:.3f} "
            f"[절대 저해율 {kind}={DISPERSANT_MRR_RELATIVE[kind]:.3f}, "
            f"{ref_kind}={DISPERSANT_MRR_RELATIVE[ref_kind]:.3f}] "
            "(knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md §6, "
            "Li et al. 2021 실측)")
    return rel


def _chelator_suppression_term(pack, notes: List[str]) -> Optional[float]:
    """착화제(글리신) 농도축 → Cu 제거율 **억제** 배수. ψ 경로(표면 흡착 보호).

    왜 억제인가 (직관과 반대다): 착화제는 산화된 Cu(II)를 가용성 착물로 빼내
    제거를 **촉진**할 것 같지만, Jani 2025 의 통제 실험쌍은 글리신을 넣을수록
    Cu RR 이 내려간다고 말한다. 원문 결론도 같다 — "the higher Cu dissolution
    in slurries without glycine indicates that glycine effectively functions as
    an inhibitor rather than a dissolution promoter". 회귀표의 [glycine] 계수도
    −440.91 (p=4.08e-7) 로 유의한 음수다.

    함수형: 잔여율 = exp(-a·C) 를 기준 농도로 정규화한다.
        f(C) = exp(-a·(C - C_ref))            → C = C_ref 에서 항등적으로 1.0
    Langmuir/Hill 피복형(θ)을 쓰지 않은 이유: 확보된 통제쌍이 2점(0.13 / 0.26 M)
    뿐이라 (K, k) 가 분리되지 않는다(K=0.13~32 /M 범위에서 SSE 가 7.7배 안에
    다 들어온다 — 근거 노트 §5 축퇴 스캔). 지수 1개는 그 2점에서 식별되고
    잔차가 -4.5% / +3.6% 다. 피복형의 포화 거동을 지어내지 않는다.

    게이트: 이 항은 **적합된 착화제 종**(chelator_suppression_species)과 팩이
    선언한 chelator_species 가 일치할 때만 켠다 — 옥살산은 같은 논문 회귀에서
    +536.63 으로 부호가 반대라(판정#43·#45·#47) 착화제를 하나로 묶으면 안 된다.

    근거 노트: knowledge/cmp/psi-glycine-chelator-suppression-cu-jani2025.md
    """
    if not pack.has("chelator_suppression_a"):
        return None
    if not pack.has("chelator_M"):
        notes.append("⚠ chelator_suppression_a 는 있으나 chelator_M 이 없어 "
                     "착화제 억제 항을 건너뛴다 — 농도를 지어내지 않는다.")
        return None
    if pack.has("chelator_suppression_species"):
        fitted = str(pack.get("chelator_suppression_species")).strip().lower()
        declared = str(pack.get_or("chelator_species", "")).strip().lower()
        if not declared:
            notes.append("⚠ chelator_suppression_species 가 선언됐으나 팩에 "
                         "chelator_species 가 없어 종 일치를 확인할 수 없다 — "
                         "항을 켜지 않는다.")
            return None
        if fitted != declared:
            notes.append(
                f"⚠ chelator_suppression_a 는 {fitted} 로 적합된 값이고 이 팩의 "
                f"착화제는 {declared} 다 — 같은 논문 회귀에서 옥살산(+536.63)과 "
                "글리신(−440.91)은 부호가 반대라 전이하지 않는다(판정#45). "
                "착화제 억제 항을 켜지 않는다.")
            return None
    a = float(pack.get("chelator_suppression_a"))
    C = float(pack.get("chelator_M"))
    C_ref = float(pack.get_or("chelator_ref_M", C))
    val = math.exp(-a * (C - C_ref))
    if abs(C - C_ref) < 1e-12:
        notes.append(
            f"착화제 억제: {C:.4g} M = 기준 조성이라 배수 1.000 "
            "(Kp 가 이 조성에서 역산됐다 — 절대 억제율을 다시 곱하면 이중 계상). "
            "글리신 농도를 바꾸면 exp(-a·ΔC) 가 반영된다 "
            "(knowledge/cmp/psi-glycine-chelator-suppression-cu-jani2025.md).")
    else:
        notes.append(
            f"착화제 억제: 글리신 {C:.4g} M / 기준 {C_ref:.4g} M, a={a:.4f} /M "
            f"→ 배수 {val:.4f}. 방향은 Jani 2025 통제쌍 2건(0.13 M: 0.861, "
            "0.26 M: 0.651)과 회귀 계수 −440.91(p=4.08e-7)이 지지한다. "
            "⚠ 2점 적합이라 절대 크기는 순위 목적으로만 쓸 것.")
    return val


def _ceria_term(pack, notes: List[str]) -> Optional[float]:
    """세리아 chemical tooth — Ce³⁺ 활성점이 Si-O-Ce 결합을 만든다.

    근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md
      - 규산 흡착 −111~−258 kJ/mol = 화학흡착 (물리흡착 −20~−40 대비 훨씬 강함)
      - Netzband & Dunn 2020: H₂O₂ 0.5wt%에서 Ce³⁺% 최대 → oxide MRR 5.5배

    ⚠ 이 항은 세리아 슬러리에만 적용된다(abrasive == 'ceria'). 실리카에 쓰면 안 된다 —
    메커니즘 자체가 다르다.
    ⚠ Ce³⁺ 분율과 MRR의 함수형은 문헌에 폐형식으로 없다. 선형 비례로 두되
    그 사실을 notes에 밝힌다. 이건 가정이지 검증된 물리가 아니다.

    함수형 — 왜 순수 비례가 아니라 두 경로의 합인가 (2026-09-13 정정):
      이전 형태 1 + gain·(f/f_ref − 1) 은 gain=1 에서 f→0 일 때 정확히 0 이 됐다.
      즉 "활성점이 없으면 제거율 0" 이라는 주장인데, 이는 물리적으로 거짓이다.
      활성점이 하나도 없어도 입자는 여전히 단단한 산화물이고, 하중을 받아 표면을
      긁는 **기계적 경로**가 남는다(이 노트 §1: 실리카·알루미나는 경도·접촉역학이
      지배하는 거의 순수 기계 연마 — 같은 경로가 세리아에서 사라질 이유가 없다).
      세리아의 특징은 기계 경로가 없다는 게 아니라 그 위에 화학 경로가 **더해져서**
      지배적이 된다는 것이다.

      그래서 제거를 두 경로의 합으로 쓴다:
          f(θ) = (1−a) + a·(θ/θ_ref)
      a = 기준 조건에서 화학(활성점) 경로가 차지하는 분율.
      θ→0 에서 (1−a) 로 유한하게 남고(기계 경로), θ=θ_ref 에서 정확히 1 이다.

      a 는 실측에서 나온다. Netzband & Dunn 2020 은 H₂O₂ 로 Ce³⁺% 를 올려 산화막
      MRR 이 상용 대비 5.5 배가 됐다고 보고한다. 화학 경로가 5.5 배 구간을
      만들어냈다면 기준 조건에서 기계 경로의 몫은 대략 1/5.5 ≈ 0.18 이므로
      a ≈ 0.82. 팩이 ceria_mechanical_floor 로 (1−a) 를 직접 주면 그것을 쓴다.

      ⚠ 이 분해 자체가 문헌의 폐형식이 아니라 5.5배 관측에서 역산한 가정이다.
      다만 극한에서 물리적으로 옳다는 점이 이전 형태와 다르다.

    지수 p — 왜 선형(p=1)이 아닌가 (2026-09-14, EVIDENCE-RULES 판정#23):
      위 형태는 θ 의존을 **선형**으로 놓았다. 그 가정은 "문헌에 폐형식이 없다"는
      이유로 남아 있었을 뿐 검증된 적이 없었다. 이제 검증 가능한 쌍이 생겼다.

      같은 저자·같은 입자(Ce1, 58~68 nm)·같은 실험계에서 두 논문이 한 축(H₂O₂ 첨가량)만
      바꿔 각각 θ 와 MRR 을 보고한다 — **교란이 통제된 대응쌍**이다(근거등급 E2):
        - Netzband & Dunn 2019 (ECS JSS 8, P629, doi:10.1149/2.0311910jss) Fig.4 + Table I:
          Ce1 의 Ce³⁺% 가 H₂O₂ 0 wt% 에서 12%(Table I 명시값; Fig.4 벡터 판독 12.55%),
          0.5 wt% 에서 최대 25.7%(판독) → **θ 비 2.05배**.
        - Netzband & Dunn 2020 (ECS JSS 9, 044001, doi:10.1149/2162-8777/ab8393) 본문:
          같은 슬러리가 H₂O₂ 무첨가에서 상용 대비 2.0배, 0.5 wt% 에서 5.5배
          → **MRR 비 2.75배**(상용 기준이 약분되므로 슬러리 내부 비율로 유효).
      선형이면 MRR 비는 θ 비를 넘을 수 없다(floor 가 0 이어도 상한이 정확히 2.05배,
      floor>0 이면 그보다 작아진다). 관측된 2.75배는 그 상한 밖이다 → **선형 반증.**

      멱형 f(θ) = floor + a·(θ/θ_ref)^p 로 역산하면
        floor=0     → p = ln2.75/ln2.05 = 1.41
        floor=1/5.5 → p = 1.65
      기본 floor(1/5.5)에서 p ≈ 1.65 다. 세리아 팩은 이 값을 선언해 쓴다.

      ⚠ 한계(정직하게): (a) 2019 의 θ 와 2020 의 MRR 은 같은 논문의 같은 표가 아니라
      같은 그룹의 연속 두 논문이다 — 동일 입자 로트라는 보장은 본문 서술("as described
      previously", 같은 Ce1 명명)에 의존한다. (b) 쌍이 2점이므로 p 는 할선이지
      국소 기울기가 아니다. (c) 2019 논문 자체는 "Ce³⁺ 자리 수는 반응속도를 직접
      정하지 않고 반응이 일어날 확률을 높인다"고 서술한다 — p>1 은 그 확률 해석과
      모순되지 않지만, 초선형의 메커니즘(활성점 군집·협동 효과)은 미확인이다.
    """
    if str(pack.get_or("abrasive", "")) != "ceria":
        return None
    if not pack.has("ce3_fraction"):
        return None
    f = float(pack.get("ce3_fraction"))
    f_ref = float(pack.get_or("ce3_fraction_ref", 0.15))
    if f_ref <= 0:
        return None
    gain = float(pack.get_or("ceria_tooth_gain", 1.0))
    # 기계 바닥값 — 활성점이 0 이어도 남는 몫. 기본 1/5.5 (Netzband 5.5배에서 역산).
    floor = float(pack.get_or("ceria_mechanical_floor", 1.0 / 5.5))
    floor = min(max(floor, 0.0), 1.0)
    a = (1.0 - floor) * gain
    # 활성점 지수 p — 2026-09-14 판정#23 이전에는 암묵적으로 1.0(선형)이었다.
    # 같은 슬러리 내 (θ, MRR) 쌍으로 선형 가정이 반증됐다(아래 docstring §"지수").
    # 팩이 ceria_tooth_exponent 를 선언하지 않으면 1.0 = 기존 동작 그대로(하위호환).
    p_exp = float(pack.get_or("ceria_tooth_exponent", 1.0))
    u = (f / f_ref) ** p_exp
    if abs(p_exp - 1.0) < 1e-9:
        shape = ("⚠ Ce³⁺–MRR 함수형을 선형(p=1)으로 두었다 — 이 팩은 "
                 "ceria_tooth_exponent 를 선언하지 않았다. Netzband 쌍에서는 선형이 "
                 "반증됐으므로(판정#23) 세리아 팩이라면 지수를 선언하라. 미검증.")
    else:
        shape = (f"활성점 지수 p={p_exp:g} — Netzband & Dunn 2019 Fig.4(Ce1 58 nm) × "
                 "2020 Fig.1a 의 **같은 슬러리 내** (Ce³⁺%, MRR) 쌍에서 역산. "
                 "θ 2.05배 → MRR 2.75배이므로 선형(p=1)으로는 재현 불가.")
    notes.append(
        f"세리아 chemical tooth: Ce³⁺ 분율 {f:.3f} (기준 {f_ref:.3f}). "
        f"화학 경로 {a * 100:.0f}% + 기계 경로 {floor * 100:.0f}% 로 분해 — "
        "활성점이 0 이어도 입자는 단단한 산화물이라 기계적 제거가 남는다. " + shape)
    return floor + a * u


def _ph_softening_term(pack, notes: List[str]) -> Optional[float]:
    """pH → 표면 연화 기여 (경도비를 통해 들어간다).

    ⚠ 가장 약한 항이다. pH가 용해도·표면전하를 바꾸는 건 확실하지만, 그것이
    '유효 경도'로 얼마나 번역되는지는 재료·슬러리마다 다르고 우리에겐 데이터가 없다.
    팩이 명시적으로 ph_softening_per_unit을 주지 않으면 **아예 적용하지 않는다.**
    """
    if not (pack.has("slurry_ph") and pack.has("ph_softening_ref")
            and pack.has("ph_softening_per_unit")):
        return None
    ph = float(pack.get("slurry_ph"))
    ph_ref = float(pack.get("ph_softening_ref"))
    k = float(pack.get("ph_softening_per_unit"))
    # 경도비 H/H0 = 1 - k*(pH - pH_ref), 하한 0.2로 클램프(경도가 0이 되진 않는다)
    h_ratio = max(1.0 - k * (ph - ph_ref), 0.2)
    notes.append(f"pH 연화: pH {ph:g} → 유효경도비 {h_ratio:.3f} "
                 "(⚠ 선형 가정, 미검증)")
    return h_ratio ** (-SOFTENING_EXPONENT)


def chemistry_factor(pack) -> ChemistryEffect:
    """팩의 화학 파라미터를 읽어 MRR 배수를 만든다.

    각 항은 독립이라 가정하고 곱한다. 실제로는 상호작용이 있다(예: pH가 BTA 흡착에
    영향) — 그 커플링은 아직 모델링하지 않았고, 이 사실을 notes에 남긴다.
    """
    notes: List[str] = []
    terms: Dict[str, float] = {}

    for name, fn in (("oxidizer", _oxidizer_term),
                     ("inhibitor", _inhibitor_term),
                     ("ceria_tooth", _ceria_term),
                     ("ph_softening", _ph_softening_term)):
        v = fn(pack, notes)
        if v is not None:
            terms[name] = v

    if not terms:
        return ChemistryEffect(
            factor=1.0, terms={}, active=False,
            notes=["화학층 비활성: 팩에 화학 파라미터(oxidizer/inhibitor/ce3_fraction 등)가 "
                   "없어 MRR에 화학 효과를 반영하지 않았다. Kp에 뭉뚱그려진 상태."])

    factor = 1.0
    for v in terms.values():
        factor *= v

    if len(terms) > 1:
        notes.append("⚠ 화학 항들을 독립으로 보고 곱했다. 실제로는 pH-흡착, 산화제-세리아 "
                     "산화환원 같은 커플링이 있다 — 미모델링.")
    return ChemistryEffect(factor=factor, terms=terms, notes=notes, active=True)


def _carboxylate_promoter_term(pack, notes: List[str]) -> Optional[float]:
    """디카복실레이트 착화제(옥살산/옥살산암모늄) 농도축 → Cu 제거율 **촉진** 배수.

    χ 경로(표면 반응성)다. 같은 팩의 글리신 축(ψ `_chelator_suppression_term`)과
    **부호가 반대이고 서로 다른 팩터에 산다** — 이것은 임의 분리가 아니라
    Jani 2025 회귀가 같은 표에서 [oxalic acid]=+536.63(p=1.7e-7) 과
    [glycine]=−440.91(p=4.1e-7) 로 직접 갈라놓은 결과다(판정#45·#47).

    함수형(멱 + 기계 바닥):
        g(C) = phi + (1 - phi) * (C / C_anchor) ** m
        f(C) = g(C) / g(C_ref)                 → C = C_ref 에서 항등적으로 1.0

    phi 가 하는 일: 착화제가 0 이어도 제거가 0 이 되지 않는다(순수 기계 성분).
    이 바닥이 없으면 C→0 에서 배수가 0 으로 떨어져 물리가 아니라 특이점이 된다.

    값의 출처 — US6309560B1 (Cabot, Kaufman/Kistler/Wang) TABLE 1, 통제쌍 2건:
      · 7% H2O2, wetting 50 ppm, BTA 0: 옥살산암모늄 0 → 0.5 wt% 에서
        Cu 21.7 → 278.0 nm/min  ⇒ phi = 21.7/278.0 = 0.07806
      · 11% H2O2, wetting 10 ppm, BTA 0: 0.5 → 1.0 wt% 에서
        Cu 251.7 → 402.9 nm/min ⇒ 비 1.6007 ⇒ m = log2((1.6007-phi)/(1-phi)) = 0.7238
    (NH4)2C2O4 MW 124.10 g/mol, 밀도 1.0 g/mL 근사로 wt% → mol/L 환산:
    0.5 wt% = 0.04029 M(= C_anchor), 1.0 wt% = 0.08058 M.

    독립 교차확인(적합에 쓰지 않음): Jani 2025(doi:10.1149/2162-8777/adc59e)
    RSM 회귀로 옥살산 0.02 → 0.08 M 예상비는 (1044.65+536.63)/(1044.65−536.63)
    = 3.113 인데 이 항은 2.515 — **19.2% 낮다**. 방향과 오더는 맞고 크기는
    어긋난다. 어긋나는 대로 둔다(계를 덮어씌우지 않는다): 두 계는 연마입자
    (알루미나 vs 실리카)·산 종(옥살산암모늄 vs 옥살산)·pH(7.5 자연 vs 3.0)가
    모두 다르다.

    게이트: 팩이 선언한 `promoter_species` 가 적합에 쓰인 종
    (`promoter_fitted_species`)과 일치할 때만 켠다. 글리신을 여기로 흘리면
    부호가 뒤집힌다.

    근거 노트: knowledge/cmp/chi-carboxylate-promoter-cu-oxalate-us6309560.md
    """
    for k in ("promoter_M", "promoter_anchor_M", "promoter_exponent_m",
              "promoter_floor_phi"):
        if not pack.has(k):
            return None
    if pack.has("promoter_fitted_species"):
        fitted = str(pack.get("promoter_fitted_species")).strip().lower()
        declared = str(pack.get_or("promoter_species", "")).strip().lower()
        if not declared:
            notes.append("⚠ promoter_fitted_species 는 있으나 팩에 promoter_species "
                         "가 없어 종 일치를 확인할 수 없다 — 항을 켜지 않는다.")
            return None
        if fitted != declared:
            notes.append(
                f"⚠ 카복실레이트 촉진 계수는 {fitted} 로 적합됐고 이 팩의 촉진제는 "
                f"{declared} 다 — 같은 회귀에서 옥살산(+536.63)과 글리신(−440.91)이 "
                "부호가 반대라 종을 넘겨 전이하지 않는다(판정#45). 항을 켜지 않는다.")
            return None
    C = float(pack.get("promoter_M"))
    C_ref = float(pack.get_or("promoter_ref_M", C))
    C_anchor = float(pack.get("promoter_anchor_M"))
    m = float(pack.get("promoter_exponent_m"))
    phi = float(pack.get("promoter_floor_phi"))
    if C < 0.0 or C_ref < 0.0:
        notes.append(f"⚠ promoter_M={C} / ref={C_ref} 에 음수가 있다 — 항을 켜지 않는다.")
        return None
    if C_anchor <= 0.0:
        notes.append("⚠ promoter_anchor_M 이 0 이하라 정규화가 불가능하다 — 항 생략.")
        return None

    def _g(x: float) -> float:
        return phi + (1.0 - phi) * (x / C_anchor) ** m

    denom = _g(C_ref)
    if denom <= 0.0:
        notes.append("⚠ 촉진 항 분모가 0 이하 — phi 가 0 이면 C_ref=0 에서 "
                     "정의되지 않는다. 항을 켜지 않는다.")
        return None
    val = _g(C) / denom
    if abs(C - C_ref) < 1e-12:
        notes.append(
            f"카복실레이트 촉진: {C:.4g} M = 기준 조성이라 배수 1.000 "
            "(Kp 가 이 조성에서 역산됐다 — 절대 촉진율을 다시 곱하면 이중 계상).")
    else:
        notes.append(
            f"카복실레이트 촉진: {C:.4g} M / 기준 {C_ref:.4g} M, "
            f"m={m:.4f}, phi={phi:.4f} → 배수 {val:.4f}. "
            "출처 US6309560B1 TABLE 1 통제쌍 2건. ⚠ 독립 교차확인(Jani 2025 RSM)은 "
            "0.02→0.08 M 에서 이 항보다 19.2% 큰 비를 준다 — 크기는 순위 목적으로만.")
    return val
