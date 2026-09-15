"""갈바닉 부식 방향·Co/Cu 수산화물 전이 pH — CRC 표준전위표·minteq.v4.dat에서 직접 유도.

배경 지식: knowledge/cmp/low-level-metal-cobalt-ruthenium-cross-contamination.md
(surface-contamination Lv3-1) §3.1 (표준환원전위) · §3.3 (수산화물 전이 pH) ·
§6 verify (A)(B) (코드 대조).

(주의) 금속 가수분해·수산화물 침전·박막 실제 IEP는 미반영 — knowledge/cmp/
low-level-metal-cobalt-ruthenium-cross-contamination.md §7 한계 참조.
ΔE_corr(실제 부식전위차) 크기는 표준전위로 예측 불가(Lee 2021 4배, Seo 2019
1/15) — 방향(anode/cathode)만 신뢰할 것.
"""

from __future__ import annotations

import math

# CRC 'Electrochemical Series' (Vanysek) 표 값, V vs SHE (노트 §3.1)
E0_TABLE: dict[str, float] = {
    "Co": -0.28,
    "Cu": 0.3419,
    "Ru": 0.455,
    "Ti": -1.630,
    "Ta2O5/Ta": -0.750,
    "WO3/W": -0.090,
}

# M(OH)2 + 2H+ = M2+ + 2H2O, log K (minteq.v4.dat PHASES, NIST46.4 태그, 노트 §3.3)
LOG_K_HYDROXIDE: dict[str, float] = {
    "Cu": 8.674,
    "Co": 13.094,
}


def galvanic_pair_direction(
    metalA: str, metalB: str, E0_table: dict[str, float] | None = None
) -> dict[str, object]:
    """두 금속의 갈바닉 쌍에서 양극(anode, 용해되는 쪽)을 판정한다(노트 §3.1, §6(A)).

    표준환원전위가 더 낮은(비卑한) 쪽이 양극. ΔE0_V = E0(귀한 쪽) - E0(비한 쪽) (항상 양수).

    galvanic_pair_direction("Cu", "Co") -> anode "Co", delta_E0_V ~= 0.6219
    (Cu-Co 쌍, 0.62 V 근방, 노트 §6(A)).
    galvanic_pair_direction("Ru", "Cu") -> anode "Cu", delta_E0_V ~= 0.1131
    (Ru-Cu 쌍, 0.11 V 근방, 노트 §6(A)).
    """
    table = E0_table if E0_table is not None else E0_TABLE
    if metalA not in table or metalB not in table:
        raise KeyError(f"E0 table에 없는 금속: {metalA!r} 또는 {metalB!r}")

    if table[metalA] < table[metalB]:
        anode_metal, cathode_metal = metalA, metalB
    else:
        anode_metal, cathode_metal = metalB, metalA

    delta_E0 = table[cathode_metal] - table[anode_metal]
    return {"anode": anode_metal, "cathode": cathode_metal, "delta_E0_V": delta_E0}


def hydroxide_transition_pH(metal: str, C_mol_L: float) -> float:
    """수산화물 M(OH)2 석출이 시작되는 pH* (노트 §3.3, §6(B)).

    M(OH)2 + 2H+ = M2+ + 2H2O, pH* = (log K - log10(C_mol_L)) / 2.
    C_mol_L은 몰 농도 그대로 받는다(ppm -> mol/L 환산은 호출자 책임).
    """
    if metal not in LOG_K_HYDROXIDE:
        raise ValueError(f"수산화물 log K 표에 없는 금속: {metal!r}")

    log_K = LOG_K_HYDROXIDE[metal]
    return (log_K - math.log10(C_mol_L)) / 2.0
