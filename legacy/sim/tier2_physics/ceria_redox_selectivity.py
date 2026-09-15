"""세리아(CeO2) 슬러리 Ce3+/Ce4+ 산화환원 - Si-O-Ce 화학흡착 - IEP 정전인력 - oxide:nitride 선택비.

지식 근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §2 (산소공공-Ce3+ 전하균형),
  §3 (Si-O-Ce 화학흡착 DFT), §4 (세리아-실리카 IEP 정전인력), §5 (oxide:nitride 선택비),
  §7 python verify 블록 (A)~(E)
구현 요청: agents/slurry-chemist/PROFILE.md "구현 요청" 세리아 Ce3+비→oxide MRR/선택비 정량모델

계약 (엔진과의 경계):
  이 모듈은 순수 함수 라이브러리다. engine.py / models.py에 등록하지 않는다.
  사유: Recipe에 pH·H2O2 농도 필드가 없어(docs/ARCHITECTURE.md 스키마 부채) engine.Model로
  조립할 입력이 아직 없다. S17 frictional_heating_arrhenius, S19
  particle_chemomechanical_synergy, S20 friction_cof_epd, S21 metal_contamination_surface와
  같은 지위 — "산출값 하나"를 계산하는 함수만 제공한다.

미검증 사항 (노트 §6·§7 그대로, 지어내지 않음):
  - Ce3+ vs Ce4+ 최적방향은 계·목적별 상충 보고 존재 — 정량적 최적비는 미검증이라 함수화하지
    않는다(노트 §2·§6(a)).
  - 아미노산·계면활성제 절대 선택비(35-70)는 슬러리·패드·압력 의존 캘리브레이션 대상이라
    미검증이며 함수화하지 않는다(노트 §5·§6(c)). 여기서는 Hwang & Kim 2024의 MRR 원자료
    기반 선택비(59-80)만 재현한다.
  - 세리아 IEP 6.7-7.8, 실리카 IEP 2-3은 2차 인용 범위(노트 §4·§6(b)) — 함수 인자로 노출하되
    기본 상수로 박지 않는다(호출측이 노트 §7 값 6.8/2.5를 명시 전달).

함수:
  ce3_fraction(x)                                              -> f = 2x [Ce3+ 분율]
  chemisorption_energy_kj_mol(ev)                              -> eV -> kJ/mol
  is_chemisorption(energy_kj_mol, physisorption_threshold)     -> bool
  electrostatic_attraction(iep_ceria, iep_silica, pH)          -> {-1,0,+1}
  oxide_nitride_selectivity(oxide_mrr, nitride_mrr)            -> 선택비
  h2o2_boost_selectivity(sel_before, boost_factor)             -> 선택비
"""
from __future__ import annotations

EV_TO_KJ_MOL = 96.485  # 1 eV = 96.485 kJ/mol (노트 §7 verify (B))


def ce3_fraction(x: float) -> float:
    """산소공공 x(CeO2-x) -> Ce3+ 분율 f = 2x (전하균형).

    근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §2·§7 verify (A).
      O2- 하나 이탈 -> 남은 2전자가 이웃 Ce4+ 둘을 Ce3+로 환원. 전하중립:
      4(1-f) + 3f = 2(2-x) => f = 2x. Netzband & Dunn 2020, ECS J. Solid State
      Sci. Technol. 9, 044002, doi:10.1149/2162-8777/ab8393.
    """
    return 2 * x


def chemisorption_energy_kj_mol(ev: float) -> float:
    """흡착에너지 eV -> kJ/mol 변환 (1 eV = 96.485 kJ/mol).

    근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §3·§7 verify (B).
      Brugnoli et al., "New Atomistic Insights on the CMP of Silica Glass with
      Ceria Nanoparticles," Langmuir 39(16), 2023, doi:10.1021/acs.langmuir.3c00304
      (PMC10116594, OA): 규산(H4SiO4) 흡착에너지(DFT) 세리아(111)면 -1.15 eV,
      (100)면 -2.67 eV.
    """
    return ev * EV_TO_KJ_MOL


def is_chemisorption(energy_kj_mol: float, physisorption_threshold: float = -40.0) -> bool:
    """화학흡착 판정: 흡착에너지가 물리흡착 경계보다 강한(더 음의) 결합인가.

    근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §3·§7 verify (B).
      물리흡착 -20 ~ -40 kJ/mol 경계(cf. slurry-components-overview §4 BTA 흡착 경계)보다
      강하면 화학흡착. Brugnoli 2023, doi:10.1021/acs.langmuir.3c00304의 -111~-258 kJ/mol이
      이 경계를 크게 벗어나 화학흡착으로 판정된다.
    """
    return energy_kj_mol < physisorption_threshold


def electrostatic_attraction(iep_ceria: float, iep_silica: float, pH: float) -> int:
    """세리아-실리카 표면전하 부호곱으로 인력(-1)/반발(+1)/무전하(0) 판정.

    근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4·§7 verify (C).
      표면전하 부호 = sign(IEP - pH) (pH<IEP -> 양전하). 두 IEP 사이 작동 pH(대략 4-6)에서
      세리아(+)·실리카(-) 반대부호 -> 정전인력. Cambridge JMR, doi:10.1557/JMR.2005.0176 계열.
    """
    sign_ceria = 1 if pH < iep_ceria else (-1 if pH > iep_ceria else 0)
    sign_silica = 1 if pH < iep_silica else (-1 if pH > iep_silica else 0)
    return sign_ceria * sign_silica


def oxide_nitride_selectivity(oxide_mrr: float, nitride_mrr: float) -> float:
    """oxide:nitride 선택비 = oxide_MRR / nitride_MRR.

    근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §5·§7 verify (D).
      Hwang & Kim 2024, Polymers 16, 844, doi:10.3390/polym16060844 (PMC10974854, OA):
      소포폴리머별 oxide(PETEOS)/nitride MRR로 선택비 59-80 재현
      (예: BYK 5558/83=67, G-336 5417/68=80).
    """
    return oxide_mrr / nitride_mrr


def h2o2_boost_selectivity(sel_before: float, boost_factor: float = 3.0) -> float:
    """H2O2 첨가로 인한 선택비 배율 적용: sel_after = sel_before * boost_factor.

    근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §2·§7 verify (E).
      Netzband & Dunn 2020, ECS J. Solid State Sci. Technol. 9, 044002,
      doi:10.1149/2162-8777/ab8393 (OA): H2O2 0.5wt%로 표면 Ce3+% 최대 -> oxide MRR 5.5배,
      oxide:nitride 선택비 1:1 -> 3:1.
    """
    return sel_before * boost_factor
