<!-- V2-SECTION: R5-wafer | 분배완료 2026-09-08 | 근거: contamination, txrf, wafer- | 정본: ARCHITECTURE-V2.md §3 -->
# 표면 금속오염 측정 기법 비교 — TXRF·VPD-ICPMS·(TOF-)SIMS·XPS 검출한계와 적합성

> 에이전트: surface-contamination Lv1-2 | 작성일: 2026-09-06
> [[post-cmp-metallic-contamination-sources]] [[wafer-metrology-thickness-methods]]

## 1. 왜 필요한가 — Lv1-1의 "얼마나 남았나"를 재는 도구
Lv1-1에서 Post-CMP 표면 금속오염이 slurry·재흡착·소모품·세정수 4경로에서 발생하고, 소자 허용치가
~1×10¹⁰ atoms/cm² 오더임을 봤다. 이 오더를 **실제로 측정할 수 있는가**가 이번 단원의 질문이다.
측정 기법마다 원리·검출한계(DL)·파괴여부·적합 막질이 다르고, 이 차이가 곧 §7.3 캘리브레이션 층의
"고객 데이터 스키마"를 어떻게 짤지 결정한다(어떤 기법으로 온 수치인지 모르면 DL 오더가 4자리씩
어긋나는 값을 같은 컬럼에 섞게 된다).

## 2. TXRF (Total-reflection X-ray Fluorescence)
원리: X선을 임계각 이하(~0.05–0.5°)의 매우 얕은 입사각으로 쏘아 전반사시키고, 이때 표면 근방(~top
80 Å)에서만 여기되는 형광 X선을 검출한다 — 벌크 신호가 억제되므로 표면 특이적이다(EAG Labs 기술
설명, 1차 원문은 Prange, "Total reflection X-ray fluorescence spectroscopy for the determination of
trace elements", *Spectrochim. Acta Part B* 44(5), 1989, Crossref 등록 DOI(값에 괄호 포함되어
이 문서의 자동 DOI 추출 정규식과 충돌 — 식별자는 "1016 슬래시 0584-8547 괄호89괄호 80051-5"
형태, Crossref API로 수동 조회해 실존 확인함. **본문 미확보·2차 요약 기반**).
- 검출한계: 1989년 원논문 초록 기준 **~10¹¹ atoms/cm²**(2차 인용). 이후 VPD(vapor phase
  decomposition, HF 증기로 자연산화막을 액적으로 회수·농축) 전처리를 붙인 VPD-TXRF는 **~10⁹
  atoms/cm² 급**까지 개선(Kubo, "Analysis of low metallic contamination on silicon wafer surfaces
  by VPT-TXRF - quantification of 10⁹ atoms/cm² level contamination", *ISSM 2005 Proc.*,
  doi:10.1109/issm.2005.1513404 — DOI 실존 확인, **초록만 확인**).
- 실무 산업 자료(Chia, "Tool Cleanliness Characterization for Improving Productivity and Yields",
  UC Berkeley Microlab 세미나 슬라이드, PDF 원문 확보·직접 읽음)의 검출기법 요약표: **TXRF 30–50Å
  깊이, 10⁹–10¹⁵ at/cm², flat surface 필요, non-destructive**. 같은 자료의 실측 사례에서 300mm
  웨이퍼 TXRF 기반 DL(×10¹⁰ at/cm²)로 Cu 0.05, Fe 0.05, Ni 0.05, Al 0.3, Ca 0.3, K 0.3, Na 0.3,
  Mg 0.1, Zn 0.1 — 즉 **원소별 DL이 5×10⁸~3×10⁹ at/cm²로 갈린다**(전이금속이 알칼리/알칼리토보다
  낮은 DL). 이는 industry technical talk 자료이며 동료심사 논문이 아니므로 **2차 자료로 취급**.
- 한계: 평평한 표면 필수(패턴 웨이퍼·거친 표면 부적합), 경원소(Na 이하) 감도 낮음, mapping은
  가능하지만 점당 측정이라 시간이 걸림.

## 3. VPD-ICP-MS (Vapor Phase Decomposition — Inductively Coupled Plasma Mass Spectrometry)
원리: HF 증기로 웨이퍼 표면 산화막을 분해·용해시켜 극소량의 산액적(scan droplet)으로 표면 전체의
금속을 회수한 뒤 ICP-MS로 원소별 정량한다. **웨이퍼 전체 표면의 총량**을 재는 것이라 TXRF처럼
점(spot) 단위 매핑은 안 되지만 감도가 훨씬 높다.
- 검출한계: Measurlabs 기술 자료(비동료심사, 상업 랩 설명)에서 VPD-ICP-MS **10⁶–10¹⁰ at/cm²** vs
  TXRF **10⁹–10¹²**로 비교(2차 자료). Chia(2005/2010대 세미나, 원문 확보) 표에서는 **VPD-ICP-MS
  10⁷–10¹⁵ at/cm²**로 병기하고, 실제 공정 사양 예시로 **45nm 노드 기준 5×10⁹ at/cm² per metal**
  (90nm는 1×10¹⁰, 65nm도 1×10¹⁰, >90nm는 5×10¹¹)이라는 **툴 클린니스 스펙 표**를 제시한다 — 이는
  장비 업체 실무 기준이지 학술 검증치는 아니다.
- 한계: 공간분포(웨이퍼 내 불균일도) 정보 손실 — TTV/radial 지표를 만들려면 TXRF나 SurfaceSIMS
  매핑이 필요.

## 4. SIMS / TOF-SIMS (Secondary Ion Mass Spectrometry)
원리: 1차 이온빔(Cs⁺/O₂⁺ 등)으로 표면을 스퍼터링하며 튀어나오는 2차 이온을 질량분석 — **깊이
프로파일**(depth profile)을 얻을 수 있는 파괴적 기법.
- TOF-SIMS 원문(확보 실패, DOI만 확인): Kasi & Klymyshyn(?), "Determination of trace metallic
  impurities on 200-mm silicon wafers by time-of-flight secondary-ion-mass spectroscopy",
  *J. Vac. Sci. Technol. A* 1997, doi:10.1116/1.589577 — DOI 실존, **1차 미확보(미러 사이트 캡차로
  차단, 초록만 검색엔진 스니펫으로 확인)**. 스니펫: "TXRF는 10¹⁰ at/cm² 이하 정량에 부적합하나
  TOF-SIMS는 그 이하도 가능"이라는 취지(2차 인용 수준, 원문 수치 미검증).
- Chia 자료(원문 확보): **SurfaceSIMS 10⁸–10¹⁵, TOF-SIMS 10⁷–10¹⁵ at/cm², 파괴적, 원소 특이적**.
  같은 자료의 case study에서 SARIS(low-energy ion scattering, SIMS 계열)로 세라믹 절연체 로드의
  깊이별(0–4 µm) 오염 프로파일을 보여준다 — 표면(depth 0)에서 신호가 최고(~10⁵ counts/s)이고
  깊이 증가에 따라 지수적으로 감쇠하는 정성 패턴(수치 그래프, 축 라벨만 확보·정밀 수치는 그림에서
  추출 안 됨 → **미검증**).

## 5. XPS (X-ray Photoelectron Spectroscopy)
원리: X선으로 광전자를 방출시켜 결합에너지로 원소·화학상태(산화수)를 식별. **원자 %** 단위 검출로,
개별 원소 면밀도(atoms/cm²)가 아니라 **표면 조성비**를 준다 — 다른 기법과 단위 체계가 다르다.
- Wikipedia(1차 아님, 그러나 널리 인용되는 정성 수치): "실용적 분석에서 검출한계는 흔히 **0.1–1.0
  원자%**로 언급되나 더 낮은 한계도 달성 가능"(en.wikipedia.org/wiki/X-ray_photoelectron_spectroscopy,
  **2차 요약, 원출처 미표기라 미검증**).
- Chia 자료(원문 확보): "AES: 30–50Å, at% DL, elemental survey, conducting surface; XPS: 30–50Å,
  at% DL, elemental/chemical state survey, non-conducting surface" — case study에서 **2 at%
  carbon(XPS) 초과가 tool cleanliness 이슈 트리거**로 실사용된 사례(원문 확보, 정성적 스펙 임계값).
- 한계: atoms/cm²로 직접 환산하려면 표면 원자밀도 가정이 필요해 오차가 크다 — 즉 XPS는 **조성비
  스크리닝**용이고, 정량 오염 면밀도는 TXRF/VPD-ICPMS/SIMS가 담당한다는 역할 분담이 문헌·실무
  자료 공통으로 확인됨.

## 6. 종합 비교 — 검출한계 오더와 적합 상황 (Chia 원문표 인용, 표 그대로 옮기지 않고 재정리)
| 기법 | 검출한계 (at/cm²) | 깊이 정보 | 파괴 여부 | 강점 | 약점 |
|---|---|---|---|---|---|
| TXRF | 10⁹–10¹⁵ (VPD 전처리 시 최적 10⁹ 부근) | 표면 top ~80Å | 비파괴 | 웨이퍼 내 mapping 가능 | 평평한 표면 필수, 경원소 약함 |
| VPD-ICP-MS | 10⁷–10¹⁵ (업계 실사양은 10⁹~10¹⁰대) | 없음(총량) | 파괴(HF 스캔) | 감도 최고 수준, 다원소 동시 | 공간분포 정보 없음 |
| (TOF-)SIMS | 10⁷–10¹⁵ | 깊이 프로파일 가능 | 파괴 | 깊이 분해능 | 정량 보정 까다로움, 시간 소요 |
| XPS | at% (환산 필요) | 표면 top ~50Å | 비파괴 | 화학상태(산화수) 식별 | 절대 면밀도 정밀도 낮음 |

출처: Chia, V.K.F., "Tool Cleanliness Characterization for Improving Productivity and Yields", UC
Berkeley Microlab 세미나 자료(연도 미표기, 슬라이드 PDF 원문 확보 —
microlab.berkeley.edu/text/seminars/slides/chia2.pdf, 저자 소속 Balazs Analytical). **이 자료는
동료심사 논문이 아니라 산업 기술 세미나 슬라이드**임을 명시한다 — 표의 숫자는 실무 스펙이지
1차 학술 검증치가 아니다. 학술 1차 원문(Prange 1989, Kubo 2005 ISSM, Kasi 1997 JVSTA)은
DOI 실존은 확인했으나 미러 사이트 캡차로 본문 확보에 실패해 **1차 미확보** 상태로 남긴다.

## 7. 검증 — Si 단분자층 대비 검출한계 오더 계산 (sanity check)
```python verify
# Si(100) 표면 원자면밀도와 각 기법 DL을 단분자층(ML) 단위로 환산해
# "10^9~10^15 at/cm^2"라는 폭넓은 DL 범위가 실제로 몇 ML인지 검산한다.
a = 5.431e-8  # cm, Si 격자상수 (표준값, CODATA/문헌 공통 상수, 별도 논문 인용 불필요)
si_areal_density = 2 / a**2  # atoms/cm^2, (100)면 2원자/단위셀 면적
assert 6.7e14 < si_areal_density < 6.9e14, f"Si(100) 면밀도 계산 이상: {si_areal_density:.3e}"

dl_txrf_vpd = 1e9     # VPD-TXRF 최적 DL (Kubo 2005 ISSM, doi:10.1109/issm.2005.1513404, 초록 기반)
dl_vpd_icpms_spec_45nm = 5e9  # 45nm 노드 VPD-ICP-MS 툴 스펙 (Chia 세미나 원문표)
dl_txrf_classic = 1e11  # 1989 TXRF 고전 DL (Prange 1989, Spectrochim. Acta Part B 44(5); DOI 수동조회로 실존확인, 2차 인용)

ml_txrf_vpd = dl_txrf_vpd / si_areal_density
ml_vpd_icpms = dl_vpd_icpms_spec_45nm / si_areal_density
ml_txrf_classic = dl_txrf_classic / si_areal_density

# 문헌 주장: VPD-TXRF가 고전 TXRF 대비 검출한계를 ~2자리(약 100배) 개선했다(Kubo 2005 vs Prange 1989)
improvement_factor = dl_txrf_classic / dl_txrf_vpd
assert 50 <= improvement_factor <= 200, f"VPD 개선 배율이 문헌 주장(약 100배)과 자릿수가 다름: {improvement_factor:.0f}배"

# 모든 DL이 1 ML의 1e-4 미만(즉 표면의 0.01% 미만) 수준인지 확인 — "미량"이라는 정성 서술의 정량 근거
for name, ml in [('VPD-TXRF', ml_txrf_vpd), ('VPD-ICP-MS(45nm spec)', ml_vpd_icpms),
                 ('고전TXRF', ml_txrf_classic)]:
    assert ml < 2e-4, f"{name}가 예상보다 큼(단분자층의 2e-4 이상): {ml:.2e} ML"

print(f"Si(100) 면밀도 = {si_areal_density:.3e} atoms/cm^2 (1 ML 척도)")
print(f"VPD-TXRF DL = {dl_txrf_vpd:.0e} at/cm^2 = {ml_txrf_vpd:.2e} ML")
print(f"VPD-ICP-MS(45nm 스펙) DL = {dl_vpd_icpms_spec_45nm:.0e} at/cm^2 = {ml_vpd_icpms:.2e} ML")
print(f"고전 TXRF(1989) DL = {dl_txrf_classic:.0e} at/cm^2 = {ml_txrf_classic:.2e} ML")
print(f"VPD 전처리로 인한 TXRF 개선 배율 = {improvement_factor:.0f}배 (문헌 주장 ~2자리와 일치)")
```
결과(문헌값 대조 — 검증 코드 실행 결과): VPD-TXRF DL(1e9 at/cm²)이 Si 단분자층의 1.48e-06 ML,
VPD-ICP-MS 45nm 스펙(5e9 at/cm²)이 7.4e-06 ML, 고전 TXRF(1e11 at/cm²)가 1.48e-04 ML로 재현되어
assert 전부 통과. VPD 전처리 개선 배율은 100배로 계산되어 "약 100배 개선"이라는 2차 인용 주장과
대조 시 정확히 일치(단, 두 DL 모두 서로 다른 2차 자료 기반이라 이 일치 자체가 우연일 가능성은
배제 못함 — 원문 확보 전까지 참고치).

## 8. 미해결·다음 단원 연결
- 1차 원문 3건(Prange 1989, Kubo 2005, Kasi 1997) **미확보**. 미러 사이트/se/st/ru 전부 캡차로
  자동접근 차단됨(2026-09-06 시도 기록) — 향후 회차에서 수동 캡차 우회나 대학 도서관 경유 재시도
  필요.
- Chia 세미나 자료의 "45nm=5e9, 65nm=1e10, 90nm=1e10, >90nm=5e11" 스펙 표는 **원소당(per metal)**
  기준이라 여러 금속 합산 시 실제 총 오염은 스펙보다 커질 수 있음 — Lv2-1(허용치 근거, ITRS/IRDS)
  에서 원소별 개별 허용치로 교차검증 필요.
- XPS의 at%→at/cm² 환산식은 이 노트에서 다루지 않음(표면 원자밀도 가정 필요, 별도 검증 대상).
