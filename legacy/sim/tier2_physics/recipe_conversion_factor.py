"""레시피 간 CMP 제거율(RR) 변환계수 - work function 지수 반응식 곱.

지식 근거: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §2.2,
  §6 python verify 블록 (A)
1차 문헌: US20060116785A1 "Method of predicting CMP removal rate for CMP process
  in a CMP process tool" (공개 2006-06-01, 출원 2004-11-29, 등록판 US7333875B2,
  Taiwan Semiconductor Manufacturing Co.), 식(1)·표 1·표 2·청구항 6.

계약 (엔진과의 경계):
  이 모듈은 순수 함수 라이브러리다. engine.py / models.py에 등록하지 않는다.
  사유: Recipe 스키마에 "레시피 간 전이"라는 개념 자체가 없어(docs/ARCHITECTURE.md
  §4 스키마 부채) engine.Model로 조립할 입력이 아직 없다. S17
  frictional_heating_arrhenius, S19 particle_chemomechanical_synergy, S20
  friction_cof_epd, S21 metal_contamination_surface, S31
  ceria_redox_selectivity와 같은 지위 — "산출값 하나"를 계산하는 함수만 제공한다.

함수:
  work_function(downforce_psi, slurry_flow_ml_min, platen_rpm) -> F(X,Y,Z)
  recipe_conversion_factor(recipe_from, recipe_to)             -> F(to)/F(from)

상수:
  RECIPE_TABLE  US20060116785A1 표 1의 ILD/STI/IMD 레시피
"""
from __future__ import annotations

import math


def work_function(downforce_psi: float, slurry_flow_ml_min: float, platen_rpm: float) -> float:
    """제어변수 3종(다운포스 X psi, 슬러리 유량 Y ml/min, 패드 회전 Z rpm)의 work function F(X,Y,Z).

    근거: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §2.2·§6 verify (A).
      US20060116785A1 식(1). 특허 원문 표기 "e^{-(Y-80/98.39)}"는 괄호가 빠진 오기로
      판단 - (Y-80)/98.39로 읽어야 표 2의 변환계수(STI 1.12, IMD 1.41)가 재현된다.
    """
    X, Y, Z = downforce_psi, slurry_flow_ml_min, platen_rpm
    return ((1.223 - 0.605 * math.exp(-(X - 3.4) / 2.117))
            * (1.085 - 0.302 * math.exp(-(Y - 80) / 98.39))
            * (1.187 - 0.719 * math.exp(-(Z - 40) / 66.304)))


def recipe_conversion_factor(recipe_from: dict, recipe_to: dict) -> float:
    """레시피 전환 변환계수 = F(recipe_to) / F(recipe_from).

    근거: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §2.2, US20060116785A1
      식(1)·표 2. 특허 실시예: ILD 기준 STI 1.12, IMD 1.41. 청구항 6은 이 계수가
      "substantially 0.5~2"의 범위로 보고된다고 명시하지만, 다른 레시피 조합에서는
      이 범위를 벗어날 수 있으므로 여기서는 예외를 던지지 않는다(범위 확인은
      호출측 책임).

    recipe_from / recipe_to: {"downforce_psi": ..., "slurry_flow_ml_min": ...,
      "platen_rpm": ...} 형태.
    """
    F_from = work_function(recipe_from["downforce_psi"], recipe_from["slurry_flow_ml_min"],
                            recipe_from["platen_rpm"])
    F_to = work_function(recipe_to["downforce_psi"], recipe_to["slurry_flow_ml_min"],
                          recipe_to["platen_rpm"])
    return F_to / F_from


# US20060116785A1 표 1 (다운포스 psi, 슬러리 유량 ml/min, 패드 회전 rpm)
RECIPE_TABLE = {
    "ILD": {"downforce_psi": 4.0, "slurry_flow_ml_min": 150, "platen_rpm": 63},
    "STI": {"downforce_psi": 4.2, "slurry_flow_ml_min": 200, "platen_rpm": 63},
    "IMD": {"downforce_psi": 4.6, "slurry_flow_ml_min": 100, "platen_rpm": 108},
}
