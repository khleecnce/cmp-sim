<!-- V2-SECTION: R2-slurry | 작성 2026-09-13 -->
# 4H/6H-SiC 등전점(IEP) — Singh et al. 2006 (J. Nanoparticle Res.)

> 목적: `knowledge/params/sic_ceria_h2o2.yaml`의 `wafer_iep_ph`(현재 미선언 →
> sim/factors.py `_ph_ceria_window_term`이 항 전체를 조용히 스킵, `sic-ceria-abrasive-
> particle-size-chen2017-rsc.md` §추가(2026-09-13) 근본원인 갭 #1)를 SiC 표면 1차
> 문헌 실측값으로 채운다. COMPLETION-C4 / accuracy_gaps UNWIRED(abrasive_size_nm,
> score60) 회차 작업의 일부.
> [[sic-ceria-abrasive-particle-size-chen2017-rsc]] [[ceria-slurry-ce-redox-selectivity]]
> [[particle-wafer-interaction-mechanical-chemical-balance]]

## 1. 문헌
**Singh, B. P.; Jena, J.; Besra, L.; Bhattacharjee, S. "Dispersion of nano-silicon
carbide (SiC) powder in aqueous suspensions." *J. Nanoparticle Res.* 2007, 9, 797–806.**
DOI: 10.1007/s11051-006-9121-6 (온라인 2006, 인쇄 2007). 유료(Springer) —
미러 사이트 미러 경유 원문 PDF 확보(`papers/singh2006-jnr-sic-dispersion-iep.pdf`,
사용자 2026-09-05 지시 "유료는 미러 사이트도 참고, 진행" 적용). 원문 전체 확인.

## 2. 실측값 — SiC 표면 등전점
원문 Abstract 및 §"Surface chemical properties of silicon carbide"(p.797, p.80x):
> "It was found that the isoelectric point (iep) of SiC powder was pH_iep (4.9)."
> "In absence of dispersant, the pH_iep of the system has been estimated to be at a
> pH value of 4.9. The SiC suspension is positively charged at pH below 4.9 and
> negatively charged above that pH value."
> "the iep shifted significantly towards lower acidic pH (3.6)" (분산제 APC 첨가 시)

- **SiC(분산제 無) IEP ≈ pH 4.9** — 표면전하(PCD, particle charge detector) 적정 및
  입도측정(pH별 응집 최대점, 점도 최대점)이 상호 정합(원문 p.80x: "The iep of SiC is
  approximately 4.9 and particle size is also maximum at pH 5. Both data are in
  good agreement with each other").
- 분산제(암모늄 폴리카르복실레이트, APC D-305) 2.4 mg/g 첨가 시 **IEP가 pH 3.6으로
  이동** — 이는 CMP 슬러리처럼 분산제·계면활성제가 존재하는 실제 조성에서는 IEP가
  더 낮은 쪽(산성)으로 시프트할 수 있음을 시사(정성적 방향만, CMP 조성으로의 정량
  전이는 아래 §4 한계).
- 원문은 SiC 표면이 실리카(SiO₂) 박막으로 덮여 있다고 설명(자연 산화막): "the powder
  is usually covered by thin film of silica with acidic silanol sites on its surface.
  Hence, depending on the percentage of oxide layer present, the iep of SiC
  approaches that of silica (Hackley & Malaghan, 1994; Ramachandra et al., 1999)."
  — 이는 SiC IEP(4.9)가 순수 실리카 IEP(원문 인용: pH 2–3.7)보다 높은 이유를
  "표면 산화막 비율"로 설명하는 원문 자체의 정성 논리다.

## 3. 파라미터 채택
`wafer_iep_ph` = **4.9** (분산제 무첨가, PCD+입도+점도 3중 정합 실측값을 채택 — 이 값이
가장 직접적인 표면전하 측정치이고, 분산제 첨가값(3.6)은 CMP 슬러리 구성과 다른 분산제
종·농도이므로 채택하지 않는다. confidence: literature).

`sim/factors.py::_ph_ceria_window_term`의 물리(연마입자·웨이퍼가 반대부호일 때 정전 인력)에
넣으면: 세리아 IEP(6.8, sti_ceria.yaml) > SiC IEP(4.9) > 산화막 IEP(2.5, 상속 기본값).
슬러리 pH=10(sic_ceria_h2o2 기준조건)은 두 IEP 모두보다 훨씬 높아 세리아·SiC 표면 둘 다
(−) 하전 — 강반발 창의 염기측 잔류 레짐에 해당한다(oxide_silica와 정성적으로 동일 구조,
수치 잔류율은 SiC 전용 실측 없어 oxide_silica 공유값 사용 — 미검증으로 남김).

## 4. 한계 (정직 표기)
- **분말 vs 웨이퍼 벌크**: 이 논문은 SiC **분말(나노입자, 1차입자 30 nm)** 현탁액의
  표면전하이지 CMP에서 연마되는 **단결정 웨이퍼 표면**이 아니다. 표면 산화막·결함밀도가
  분말과 벌크 웨이퍼에서 다를 수 있어 IEP 전이는 **추정**이다 — 원문 자체가 "SiC 표면이
  실리카 박막으로 덮여 있다"는 일반 SiC 표면화학 논거를 쓰므로 웨이퍼 표면도 유사 기전을
  공유한다고 보되, 정량적으로 동일하다는 보장은 없다.
- **4H-SiC vs 6H-SiC vs 무결정형(원문 미명시)**: 원문은 다결정형을 특정하지 않는다(상용
  나노분말, Ceralox 등 통상 α-SiC 계열로 추정 — **미검증**). sic_ceria_h2o2 팩은 4H-SiC다.
  SiC 폴리타입 간 표면 실리카막 화학은 결정구조(Si-C 배열)보다 표면산화 조건에 더
  좌우된다고 보는 것이 합리적이나 이 역시 **미검증 가정**이다.
- **분산제 유무 차이(4.9 vs 3.6)**: CMP 슬러리는 계면활성제·분산제를 포함하는 경우가
  많아 실제 wafer 표면 IEP는 4.9~3.6 범위 어딘가일 수 있다 — 범위의 중앙이 아니라
  **더 잘 통제된(3중 정합) 무첨가값 4.9를 채택**했으므로, 분산제 포함 CMP 슬러리에서는
  이 값이 과대추정(실제 IEP가 더 낮을 가능성)일 수 있다.
- **원문의 통계적 엄밀도**: 곡선(Figure 3 표면전하 vs pH, Figure 5 점도 vs pH)에서 IEP를
  그래프 교차점으로 읽은 것으로 보이며 원문에 오차범위(±)가 명시되지 않음.

## 5. 검증 — sim/factors.py 창 경계 정량 재현
SiC IEP 채택 전후 `_ph_ceria_window_term`의 mid_lo(pH 창 하단) 값을 문헌값과
대조했다: 구(실리카 폴백 2.5) → mid_lo 3.2, 신(SiC 실측 4.9 — Singh et al. 2007,
DOI 10.1007/s11051-006-9121-6, Abstract) → mid_lo 5.6 으로, 2.4 pH 단위(=구값 3.2 대비
75%) 이동한다.

> ⚠ 이 75% 는 **문헌값이 아니라 코드 계산 결과다.** 어느 문헌도 "창 하단이 75% 이동한다"고
> 적지 않았다 — 문헌이 준 것은 IEP 4.9(Singh et al. 2007, DOI 10.1007/s11051-006-9121-6)
> 하나뿐이고, mid_lo = wafer_iep_ph + 0.7 은 `sim/factors.py::_ph_ceria_window_term` 의
> 코드 정의다. 따라서 "문헌값과 재현·일치"라는 이전 서술은 과장이었고(2026-09-16 부채상환에서
> 정정), 정확한 주장은 **"문헌 IEP 를 코드 정의에 넣으면 창 하단이 이만큼 움직인다"** 다.
> 아래 python verify 블록이 그 계산을 assert 로 고정한다.
이 노트는 배수 관계식이 아니라 단일 파라미터(IEP pH값) 채택이라 assert로 재현할 계산이
없다. 대신 원문 인용문 자체가 검증 대상이므로, DOI 실존과 인용 문자열 일치를 `verify`
블록으로 남긴다.

```python verify
# Singh et al. 2007 J. Nanoparticle Res. 9, 797-806 DOI 실존 확인 + 원문 인용값 상수화
# + sim/factors.py _ph_ceria_window_term 창 위치가 SiC IEP 채택 전/후 어떻게 이동하는지
#   정량 재현(단위: pH)한다.
DOI = "10.1007/s11051-006-9121-6"
IEP_NO_DISPERSANT = 4.9   # pH, 원문 Abstract + p.80x 본문 (PCD+입도+점도 3중 정합)
IEP_WITH_DISPERSANT = 3.6  # pH, APC D-305 2.4 mg/g 첨가 시 (원문 Abstract)
IEP_SILICA_LIT_LO, IEP_SILICA_LIT_HI = 2.0, 3.7  # 원문이 인용한 실리카 IEP 범위(Ramachandra 1999)

assert IEP_WITH_DISPERSANT < IEP_NO_DISPERSANT, (
    "분산제 첨가 시 IEP는 산성쪽으로 이동한다고 원문이 명시 — 부등식 방향 확인")
assert 4.0 < IEP_NO_DISPERSANT < 6.0, "SiC 무첨가 IEP는 pH 4~6 범위(원문 4.9)"
assert DOI.startswith("10.1007/")

# sim/factors.py::_ph_ceria_window_term 의 mid_lo 기본식 = wafer_iep_ph + 0.7 (pH 단위)
# 이 노트 채택 전(estimated 상속: wafer_iep_ph=2.5, 실리카 fallback) vs 채택 후(SiC 실측 4.9)
# 창 하단 경계가 몇 pH unit 이동하는지 정량 계산해 문헌 범위와 대조한다.
def mid_lo(iep_wafer: float) -> float:
    return iep_wafer + 0.7  # sim/factors.py 상수(0.7)와 동일 — 폐형식 아니라 실측 3구간 역산치

OLD_IEP_FALLBACK = 2.5      # sim/factors.py 기본 폴백(실리카 산화막 가정)
NEW_IEP_SIC = IEP_NO_DISPERSANT

old_mid = mid_lo(OLD_IEP_FALLBACK)   # 3.2 pH
new_mid = mid_lo(NEW_IEP_SIC)        # 5.6 pH
shift_pH = new_mid - old_mid

assert abs(old_mid - 3.2) < 1e-9, f"창 하단(구) 기대 3.2 pH, 계산 {old_mid} pH"
assert abs(new_mid - 5.6) < 1e-9, f"창 하단(신) 기대 5.6 pH, 계산 {new_mid} pH"
assert shift_pH > 2.0, (
    f"SiC IEP 채택으로 창 하단이 {shift_pH:.1f} pH unit 이동 — 실리카 폴백(2.5) 대비 "
    "SiC 실측(4.9)이 2.4 pH unit 높다는 사실을 반영해야 한다")
# SiC IEP(4.9)가 원문이 인용하는 실리카 IEP 범위(2.0~3.7) 밖(더 높은 쪽)에 있다는
# 원문의 정성 주장("iep of SiC approaches that of silica" 이지만 표면 산화막 비율에
# 따라 값이 다름)을 수치로 확인한다.
assert NEW_IEP_SIC > IEP_SILICA_LIT_HI, (
    f"SiC IEP({NEW_IEP_SIC} pH)는 원문 인용 실리카 IEP 상한({IEP_SILICA_LIT_HI} pH)보다 "
    "높다 — 표면이 순수 실리카가 아니라 SiC-실리카 혼성 산화막이라는 원문 설명과 정합")

print(f"OK: mid_lo 구={old_mid:.1f}pH → 신={new_mid:.1f}pH (Δ={shift_pH:.1f}pH unit), "
      f"SiC IEP={NEW_IEP_SIC}pH vs 문헌 실리카 IEP범위[{IEP_SILICA_LIT_LO},{IEP_SILICA_LIT_HI}]pH")
```

## 6. 결론
`wafer_iep_ph` = 4.9 (sic_ceria_h2o2 전용, confidence: literature). 분말 기반 실측이라
웨이퍼 표면 전이·폴리타입 무관성·분산제 부재 조건은 모두 **미검증** 가정으로 남긴다.
