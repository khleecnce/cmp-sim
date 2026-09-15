"""계측 샘플링 손실 정량화 — wafer-metrology 에이전트 소유 (순수함수 라이브러리).

근거 노트 `knowledge/cmp/inline-virtual-metrology-sampling-optimization.md` §3.1, §3.2, §4 블록2.
엔진/Recipe·WaferResult 스키마에 등록하지 않는다 — 사이트 플랜을 나타낼 필드가 아직 없음(S36 브리프).

- material_at_risk: Nduhura-Munga et al. 2013 §3.1 "material at risk" 정의(로트 단위 static 샘플링).
- mssi_min_balanced / mssi_cds / woi: McLoone, Johnston & Susto 2018 §4 블록2 Table III 닫힌형.
- static_sampling_plan: §3.1 정의를 로트 인덱스 규칙으로 구현한 보조 유틸(문헌 상수 없음).
"""
from __future__ import annotations

import math


def material_at_risk(sample_interval: int) -> int:
    if sample_interval < 1:
        raise ValueError(f"sample_interval must be >= 1, got {sample_interval}")
    return sample_interval


def mssi_min_balanced(V: int, Vm: int) -> int:
    if V <= 0 or Vm <= 0 or Vm > V:
        raise ValueError(f"require 0 < Vm <= V, got V={V}, Vm={Vm}")
    return math.ceil(V / Vm) - 1


def mssi_cds(V: int, Vm: int) -> int:
    if V <= 0 or Vm <= 0 or Vm > V:
        raise ValueError(f"require 0 < Vm <= V, got V={V}, Vm={Vm}")
    return V - Vm


def woi(V: int, Vm: int) -> float:
    return mssi_min_balanced(V, Vm) / mssi_cds(V, Vm) * 100


def static_sampling_plan(total_lots: int, sample_interval: int) -> list[bool]:
    if total_lots < 0:
        raise ValueError(f"total_lots must be >= 0, got {total_lots}")
    if sample_interval < 1:
        raise ValueError(f"sample_interval must be >= 1, got {sample_interval}")
    return [i % sample_interval == 0 for i in range(total_lots)]
