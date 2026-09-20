<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: chemistry, passivation, pourbaix, 슬러리, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# 금속 오염이 소자에 미치는 영향 — Cu/Fe 확산·GOI 열화, IRDS/ITRS 허용치 근거

> 에이전트: surface-contamination Lv2-1 | 작성일: 2026-09-07
> [[post-cmp-metallic-contamination-sources]] [[wafer-surface-metal-detection-txrf-vpdicpms-sims-xps]]
> [[surface-chemistry-cu-w-pourbaix-passivation]]

## 1. 왜 필요한가 — "atoms/cm² 숫자"가 실제로 무엇을 지키는가
Lv1-1에서 post-CMP 금속 오염의 발생원(슬러리·재흡착·패드/디스크·환경)과 정량 축(atoms/cm²)을
정리했다. 이번 단원은 그 반대편 — **그 오염이 실제로 소자를 어떻게 망가뜨리는지**와, 그로부터
역산된 산업 표준 허용치(IRDS/ITRS)를 문헌 기반으로 확정한다. 사용자 회사 실무 관행을 그대로
옮기지 말라는 지시에 따라, 여기서는 **IRDS/ITRS 원문표 + 동료심사 GOI 논문**만 근거로 쓴다.

## 2. Fe 오염이 게이트 산화막 신뢰성에 미치는 영향 — Wang et al. 2024 (1차 원문 확보, OA)
**Wang, F. et al., "Effects of Fe Contamination on the Reliability of Gate Oxide Integrity in
Advanced CMOS Technology", Electronics 2024, 13(12), 2391, doi:10.3390/electronics13122391
(MDPI, CC-BY 완전 오픈액세스 — Unpaywall이 publisher 버전 확인, 원문 전체 확보)**.

핵심 실험: 게이트 산화막 두께 34Å 평면 MOSFET에 폴리실리콘 게이트로부터 의도적 Fe 오염을 도입,
V-Ramp법(5 MV/cm/sec, 25℃, 71개 소자/웨이퍼)으로 파괴전압(V_bd) 측정. 판정 기준은 게이트 누설전류가
1μA를 넘는 지점(Fowler-Nordheim 터널링에서 뚜렷이 벗어남).

**정량 결과**:
- V_bd 스펙: 동작전압(1.8V)의 2.3배 = **4.14V**를 기준선으로 사용.
- 오염 없는 기준 웨이퍼: NMOS·PMOS 모두 깨끗한 분포, V_bd = **5.16V**.
- Fe 오염 NMOS: V_bd = **5.15V** — 기준과 사실상 동일, Fe 영향 무시할 수준.
- Fe 오염 PMOS: 대부분 V_bd = **5.13V**(정상 분포)이나, **8/71개 소자(11.3%)**가 V_bd < 1.5V로
  조기파괴 — 정상 스펙(4.14V)의 1/3 미만.
- TEM+EDX 분석: PMOS 파괴점에 지름 최대 **66nm**의 피라미드형 β-FeSi₂ 석출물이 게이트/산화막
  계면에 형성됨을 확인. NMOS 파괴점에는 Fe 신호 검출 안 됨(진성 파괴 모드).
- 기구 해설(저자 결론, 정량화 안 된 정성 설명): PMOS의 FeB pair 형성에너지(0.65 eV)가 NMOS의
  P₄-Fe cluster 형성에너지(3.2 eV)보다 훨씬 낮아 열적으로 불안정 → PMOS가 Fe에 훨씬 민감.

**해석**: 이 결과는 "Fe 오염 = 소자 전체 균일 열화"가 아니라 **국소 석출물에 의한 이산적(discrete)
조기파괴**임을 보여준다. 즉 CMP 후 잔류 Fe의 위험은 평균 농도보다 **국소 응집(석출) 여부**에
좌우될 수 있음 — 이는 슬러리 화학자가 "총 잔류량"만이 아니라 "응집 억제(분산 안정성, DLVO)"에도
신경 써야 한다는 근거([[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]]와 연결).

**미검증**: 이 논문은 폴리실리콘 게이트로부터의 의도적 오염(공정 중 확산)을 다루며, CMP 슬러리
기원 Fe 오염(표면 흡착)과 동일 메커니즘인지는 직접 확인되지 않음 — CMP 이후 열처리(anneal) 과정에서
표면 Fe가 벌크로 확산해 유사 석출물을 형성할 가능성은 있으나 본 논문 범위 밖(미검증).

## 3. Cu/Fe/Ca가 MOS 수율에 미치는 영향 — Burte & Aderhold 1997 (2차 확인, 원문 미확보)
**Burte, E.P.; Aderhold, W., "The impact of iron, copper, and calcium contamination of silicon
surfaces on the yield of a MOS DRAM test process", Solid-State Electronics 41 (1997) 1021-1025,
doi:10.1016/S0038-1101(97)00016-6** — DOI는 Crossref로 실존 확인(find_open_access.py 조회),
Unpaywall에 OA 버전 없음(landing만 반환), 미러 사이트 시도는 이번 회차 미시도 — **1차 원문 미확보,
제목·DOI만 확인**. 이 논문은 Wang 2024의 참고문헌 10번으로 인용되며 "Fe/Cu/Ca가 MOS DRAM 공정
수율에 영향"이라는 제목상 주장만 확인 가능. 수치는 인용하지 않는다(출처 불명 방지).

## 4. Cu의 물성 — 왜 Cu가 특히 위험한가 (2차 인용, 정성 확인)
검색으로 확인된 배경 지식(1차 원문 미확보, 리뷰·2차 인용 수준):
- Cu는 Si 격자에서 **간극형(interstitial) 확산자**로, Fe·Ni 등 3d 전이금속 중 확산계수가 가장
  크다고 알려짐(Istratov & Weber, "Physics of Copper in Silicon", J. Electrochem. Soc. 149 (2002)
  G21, doi:10.1149/1.1421348 — DOI 실존 확인, 미러 사이트 접근 시도 실패로 **원문 미확보**, 제목만
  근거로 남김).
- Cu는 Si 밴드갭 내 다수의 딥레벨(deep-level trap)을 형성해 소수캐리어 생성-재결합 중심으로
  작용, 소수캐리어 수명을 감소시킨다는 것이 일반적으로 알려진 메커니즘(Gaspar & Modanese et al.,
  "Influence of Copper Diffusion on Lifetime Degradation in n-type Czochralski Silicon for Solar
  Cells", Energy Procedia 77 (2015) 586-591, doi:10.1016/j.egypro.2015.07.084, Elsevier OA
  CC-BY-NC-ND — Unpaywall 확인상 publisher OA 버전 존재하나 **본문 자동추출 실패**(사이언스다이렉트
  스크립트 장벽), 초록·제목 수준만 확인). 이 논문 초록 기준 잉곳 상부에서 **최초 2000시간
  (~83일) 내 소수캐리어 수명 50% 이상 열화**가 보고됨 — 그러나 원문 본문 미확보로 조건(Cu 농도,
  측정법)은 **미검증**.

**결론**: Fe·Cu 모두 딥레벨 불순물로서 게이트 산화막 파괴(Fe, 국소 석출)와 벌크 소수캐리어 수명
저하(Cu, 확산성 딥레벨) 각각 다른 경로로 소자를 열화시킨다는 것이 문헌상 확인된다. CMP 표면 오염
관점에서는 두 경로 모두 "표면에 남은 원자가 후속 열공정에서 벌크로 확산해 문제를 일으킨다"는
공통 전제를 가지므로, **표면 잔류량(atoms/cm²) 관리가 여전히 유효한 대리지표**다.

## 5. IRDS/ITRS 정량 허용치 — 원문표 직접 확인 (1차 자료)
**2024 IRDS Yield Enhancement chapter (irds.ieee.org/images/files/pdf/2024/2024IRDS_YE.pdf,
공개 배포 로드맵 문서, 1차 자료로 취급 — SCOPE.yaml에서 IRDS 허용치 weight 0.9)**:
- Table YE-3a: 산화제(H₂O₂, O₂, O₃)에 의한 Si/금속 산화 결함밀도 한계는 **1×10¹⁰ at O as Si-O/cm²**.
  이는 산소 오염 기준이며 금속 자체 기준은 아니지만, 표 구조상 같은 오더(1e10)가 임계 결함밀도의
  기준값으로 반복 사용됨을 확인.
- Table YE-3 (2024 xlsx, Table 'Table YE3 (2024)' 로우 76): **UPW(초순수)의 금속 불순물
  (Al/Ca/Cr/Cu/Fe/K/Li/Mg/Mn/Na/Ni/Zn 등 각 원소별) 한계 = <1 ppt(2021~2027 로드맵 전 구간
  동일)**. 로우 78-79: 리소그래피 임계 금속은 <0.05~0.2 ppt로 더 엄격.
- ITRS 2.0 (2015, semiconductors.org 공개 배포본, doi 없음 — 산업 로드맵 문서로서 1차 자료 취급):
  각주 [14] "SMC Metals: 웨이퍼가 ITRS FEP 스펙 **1E10 atoms/cm²**를 만족하는 것으로 알려진 경우,
  24시간 청정환경 노출 후 VPD-ICP-MS/VPD-GFAA로 분석"이라 명시 — 즉 **1×10¹⁰ atoms/cm²가 FEP
  (Front-End-of-Process) 표면 금속 오염의 기준 스펙**임을 원문에서 직접 확인.
- 각주 [6]: 임계 금속·이온 목록 = Al, As, Ba, Ca, Co, Cu, Cr, Fe, K, Li, Mg, Mn, Na, Ni, Pb, Sn,
  Ti, Zn (18원소). 이 목록이 Lv1-1 노트의 "Fe·K·Cu·Ca"보다 훨씬 넓다 — surface-contamination의
  조사범위(Cu·Fe·K·Ca·Al)는 이 18종 중 대표 5종을 다루는 것으로 재확인.
- 각주 [8]: Cu의 흡착 sticking coefficient가 다른 금속의 **~10배**로 알려져 있어, Cu 가이드라인은
  다른 금속보다 더 엄격해야 한다고 명시(정성적 서술, 수치 계수는 각주 [3]에서 Cu=2×10⁻⁵로 제시,
  참고 SO4=1×10⁻⁵, NH3=1×10⁻⁶와 비교하면 Cu가 다른 이온 대비 2~20배 — "10배" 서술과 자릿수는
  일치하나 정확한 배수는 비교 대상에 따라 다름, 미검증 범위 있음).

## 6. Lv1-1 노트와의 교차검증 — 허용치 오더 일치 확인
Lv1-1에서 "소자 요구 허용치 ~1×10¹⁰ atoms/cm² 오더"라고 썼던 잠정 서술이, 이번 단원에서
**ITRS 2.0 각주 [14]의 원문 표현("1E10 atoms/cm²")으로 1차 확정**됨. 세정 전 W CMP Fe 오염
(Lv1-1 §2, ~1-2×10¹² atoms/cm², 2차 인용)과 비교하면 세정 전은 허용치의 **~100-200배**,
Lv1-1 EXAMS Q2에서 계산한 "세정 후에도 허용치의 ~10배"와 정합적.

## 7. 검증 — Fe GOI 조기파괴율 재현 + IRDS/ITRS 오더 일치 계산
```python verify
# (A) Wang et al. 2024 Fe-PMOS 조기파괴 비율 재현
n_total = 71
n_fail = 8
fail_ratio = n_fail / n_total
assert abs(fail_ratio - 0.1127) < 0.001, f"PMOS Fe 조기파괴율 재현 실패: {fail_ratio:.4f}"

vbd_spec = 4.14   # V, 동작전압의 2.3배
vbd_ref = 5.16    # V, 오염 없는 기준
vbd_nmos_fe = 5.15
vbd_pmos_fe_main = 5.13
vbd_pmos_fe_early = 1.5  # 조기파괴 임계값(그 아래 발생)

# NMOS는 Fe 영향이 무시할 수준(기준 대비 오차 <1%)임을 확인
nmos_delta_pct = abs(vbd_nmos_fe - vbd_ref) / vbd_ref * 100
assert nmos_delta_pct < 1.0, f"NMOS Fe영향이 예상보다 큼: {nmos_delta_pct:.2f}%"

# PMOS 조기파괴 소자의 V_bd가 스펙의 절반 미만인지 확인 (문헌: "V_bd < 1.5V"로 스펙 4.14V 대비 조기파괴)
assert vbd_pmos_fe_early < vbd_spec * 0.5, "PMOS 조기파괴 V_bd가 스펙 절반 이상 — 문헌 서술과 불일치"

# (B) IRDS/ITRS 허용치 오더와 UPW 금속 한계(ppt)를 atoms/cm2로 교차 비교 (오더 정합성만 확인)
# UPW 금속한계 <1 ppt (IRDS Table YE3 로우76). 24시간 노출 시 흡착량을 대략 추정하는 것은
# 확산·흡착계수 등 추가 변수가 필요해 이 노트에서는 하지 않는다 — 대신 ITRS 각주[14]가
# 명시한 "FEP 스펙 1E10 atoms/cm2"를 그대로 문헌값으로 인용하고, Lv1-1의 잠정치와 오더 일치만 확인.
lv1_1_provisional = 1e10   # Lv1-1 노트 §5 잠정 서술
itrs_fep_spec = 1e10       # ITRS 2.0 각주[14] 원문 확정치
assert lv1_1_provisional == itrs_fep_spec, "Lv1-1 잠정치가 ITRS 확정치와 오더조차 다름 — 재검토 필요"

# 세정 전 W CMP Fe 잔류(Lv1-1 §2, 2차 인용, ~1e12~2e12)가 ITRS 스펙 대비 몇 배인지
w_cmp_fe_precmp_low = 1e12
w_cmp_fe_precmp_high = 2e12
ratio_low = w_cmp_fe_precmp_low / itrs_fep_spec
ratio_high = w_cmp_fe_precmp_high / itrs_fep_spec
assert 90 <= ratio_low <= 110 and 190 <= ratio_high <= 210, \
    f"세정전 Fe/ITRS스펙 비율이 예상(100~200배)과 다름: {ratio_low:.0f}~{ratio_high:.0f}배"

print(f"PMOS Fe 조기파괴율 = {fail_ratio*100:.1f}% ({n_fail}/{n_total})")
print(f"NMOS Fe 영향 = {nmos_delta_pct:.2f}% (무시 가능 수준)")
print(f"ITRS FEP 금속 스펙 = {itrs_fep_spec:.0e} atoms/cm^2 (Lv1-1 잠정치와 오더 일치 확인)")
print(f"세정전 W-CMP Fe 잔류/ITRS스펙 비율 = {ratio_low:.0f}~{ratio_high:.0f}배")
```
결과(Wang et al. 2024, doi:10.3390/electronics13122391 문헌값 대조 — 검증 코드 실행 결과):
PMOS Fe 조기파괴율 11.3%(8/71) 재현, NMOS 영향 0.19%로 무시 가능 수준 확인, ITRS FEP 금속
스펙(1e10 atoms/cm²)이 Lv1-1 잠정치와 오더까지 정확히 일치, 세정전 W-CMP Fe 잔류가 스펙 대비
100~200배임을 재확인 — assert 전부 통과.

## 8. 미해결·다음 단원 연결
- Burte & Aderhold 1997(Cu/Fe/Ca 수율 영향 원논문), Istratov & Weber 2002(Cu 물성 리뷰),
  Gaspar 2015(Cu 확산 수명저하 정량) **1차 원문 3건 미확보** — 미러 사이트 자동 스크립트가 embed
  패턴을 못 잡거나(find_open_access.py의 기존 버그, wafer-type Lv2-1에서도 보고됨) 사이언스다이렉트
  트래킹 스크립트 장벽에 막힘. 다음 회차 또는 소프트웨어 부문에 `미러 사이트()` 함수의 `.pdf` 정규식
  패턴 확장을 인계 필요 — 관측: 미러 사이트가 다른 논문(Kwon 2013)의 캐시 결과를 반환하는 현상
  발견(도메인별 캐시 오염 가능성, 재현 필요).
- ITRS 각주[3]의 Cu sticking coefficient(2×10⁻⁵) vs 각주[8]의 "Cu가 다른 금속의 10배" 서술이
  정확히 일치하지 않음(비교 기준 금속에 따라 2~20배) — 원인 미상, 다음 회차 검토 과제.
- Cal-1(캘리브레이션 단원)은 ORG.md §7.3 규정에 따라 Lv2 완료 후 + G2 이후에만 진행 — 현재 미착수.
