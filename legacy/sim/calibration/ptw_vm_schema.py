"""PTW(제품) 웨이퍼 VM 입력 스키마 — 순수 데이터 구조 + 검증 함수.

지식 근거: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §5.3
(표: NPW VM(PHM2016형) vs PTW VM(Jebri형) 요구 특징 비교) 및
agents/wafer-type/PROFILE.md "구현 요청 (2026-09-08, wafer-type Lv3-1)" 4번.

이 모듈은 sim/engine.py의 Recipe/WaferResult(물리 시뮬레이션 스키마)와는 별개다.
PTW VM은 아직 engine에 미등록 지위(S17·S27·S31·S33 등과 동일) — Cal-1 캘리브레이션
메타데이터 스키마의 후보 필드를 데이터클래스로 먼저 굳히는 단계다.

mrr_lag 필드 설계 노트: PROFILE 4번 항목은 `mrr_lag_1..11` 11개 개별 필드를 명시했으나,
노트 §5.3의 근거(Di et al. 2017 PHM2016, "MRR 시간지연 11개")는 지연 스텝 개수가
11이라는 사실만 말할 뿐 11개를 별도 필드로 두어야 한다는 요구는 아니다. 11개 스칼라
필드는 순서 실수(lag_3와 lag_5를 바꿔 넣는 등)에 취약하고 가변 길이 실험(예: lag 5개만
쓰는 축소 모델)을 표현할 수 없다. 따라서 `mrr_lag: Optional[List[float]]` 리스트 하나로
통합하고, 길이 제약(1~11)은 validate_ptw_vm_input에서 검사하는 쪽을 택했다 — 필드
개수 폭발을 피하면서 노트의 정량 근거(11개)는 검증 규칙에 그대로 보존한다.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PTWVMInput:
    """PTW VM 입력 레코드. 노트 §5.3 표의 6개 요구 특징 행 중 데이터로 옮길 수 있는 것을 담는다.

    - product_id, layer: 노트 §5.3 "제품/레이아웃 식별자" 행 (Jebri 2017 §2 — 제품 j별 타깃·국소모델).
    - die_density_mean, local_density: "패턴밀도(다이 평균·국소)" 행 (Sorooshian 2005, §4 유효압력비).
      local_density=None은 국소밀도 미측정을 뜻한다(다이 평균만 있는 경우와 구분).
    - prev_layer_topography: "이전 층 토포그래피" 행 (Park 1999 Fig.12, 정성) — 예: {"step_height_nm": 12.0}.
    - e_test_R_ohm: 전기 테스트 저항(§3 전기 대리 지표) — None=미측정.
    - forced_measurement_flag: "강제 실측 앵커" 행 (Jebri 2017 §III-B, k_est^max·N_min 조건부 실측).
    - mrr_lag: "시계열·소모품 이웃" 행 중 시계열 부분 (Di 2017, MRR 시간지연). 길이 제약은
      validate_ptw_vm_input에서 검사(위 모듈 docstring 참고).
    - consumable_usage_neighbors: 같은 행의 소모품 사용량 이웃 특징 부분 (Di 2017, 표 3
      "소모품 사용량 가까운 이웃 10개의 MRR"). 예: {"pad_hours": 12.5, "conditioner_disk_count": 3}.
    """

    product_id: str
    layer: str
    die_density_mean: float
    local_density: Optional[float] = None
    prev_layer_topography: Optional[Dict[str, float]] = None
    e_test_R_ohm: Optional[float] = None
    forced_measurement_flag: bool = False
    mrr_lag: Optional[List[float]] = None
    consumable_usage_neighbors: Optional[Dict[str, float]] = None


def validate_ptw_vm_input(x: PTWVMInput) -> List[str]:
    """경고 문자열 목록을 반환한다(예외를 던지지 않음 — 호출측이 정책을 정한다).

    규칙 (노트 §5.3 근거):
    - die_density_mean이 [0,1] 밖이면 경고(패턴밀도는 비율).
    - forced_measurement_flag=False이고 mrr_lag·local_density가 모두 없으면 경고 —
      §5.3 결론: 레이아웃(밀도)도 시계열도 없으면 PTW VM 입력이 NPW VM과 구분되지 않는다.
    - mrr_lag가 있는데 길이가 1~11 밖이면 경고(Di 2017 lag 구조 근거).
    - e_test_R_ohm이 음수이면 경고(저항은 음수가 될 수 없음).
    """
    warnings: List[str] = []

    if not (0.0 <= x.die_density_mean <= 1.0):
        warnings.append(
            f"die_density_mean={x.die_density_mean}이 [0,1] 범위 밖입니다 (패턴밀도는 비율)."
        )

    if not x.forced_measurement_flag and x.mrr_lag is None and x.local_density is None:
        warnings.append(
            "레이아웃·시계열 정보 전무 — NPW VM과 구분 안 됨 "
            "(local_density와 mrr_lag가 모두 없고 forced_measurement_flag도 False, 노트 §5.3 결론)."
        )

    if x.mrr_lag is not None and not (1 <= len(x.mrr_lag) <= 11):
        warnings.append(
            f"mrr_lag 길이={len(x.mrr_lag)}가 1~11 범위 밖입니다 (Di 2017 PHM2016 lag 구조 근거)."
        )

    if x.e_test_R_ohm is not None and x.e_test_R_ohm < 0:
        warnings.append(f"e_test_R_ohm={x.e_test_R_ohm}이 음수입니다 (저항은 음수가 될 수 없음).")

    return warnings


def is_npw_equivalent(x: PTWVMInput) -> bool:
    """local_density와 prev_layer_topography가 모두 없으면 True.

    노트 §5.3 결론 문장을 그대로 재현하는 판정 함수: 레이아웃 정보(국소밀도·이전 층
    토포그래피)가 하나도 없으면 이 PTW VM 입력은 NPW VM 입력과 동등하다.
    """
    return x.local_density is None and x.prev_layer_topography is None
