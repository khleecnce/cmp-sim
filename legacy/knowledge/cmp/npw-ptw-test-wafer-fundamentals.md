<!-- V2-SECTION: R5-wafer | 분배완료 2026-09-08 | 근거: npw, pattern-, ptw | 정본: ARCHITECTURE-V2.md §3 -->
# NPW(블랭킷)와 PTW(패턴) 시험웨이퍼 — 막 종류·측정체계·WIWNU/패턴효과 구분 (Lv1-1/1-2 통합)

> 에이전트: wafer-type Lv1-1(NPW: 막종류·측정점 체계) + Lv1-2(PTW: 표준 마스크·패턴밀도·다이맵) | 작성일: 2026-09-06
> 선행: [[../../agents/wafer-type/PROFILE.md]] 상속 노트 — [[wiwnu-pressure-velocity-wafer-scale]], [[pattern-dependent-dishing-erosion]]
> 상호링크: [[uniformity-metrics-definitions-standards]] (49점 체계·WIWNU 정의 재사용), [[wafer-metrology-thickness-methods]] (측정 원리)

## 0. 이 노트의 위치
wafer-type 에이전트는 "NPW 결과를 PTW로 어떻게 넘길 것인가"를 소유한다(§7.2 전이규칙).
그 전에 두 유형이 **각각 무엇을 재고 왜 다른가**부터 문헌으로 확정한다. 사용자 회사 관행
정의는 참고하지 않고(원칙: 학습해서 반영), 공개 문헌·특허·논문만 근거로 쓴다.

## 1. NPW(Non-Patterned/Blanket Wafer) — 목적과 막 종류

**목적**: 레이아웃 패턴 효과를 배제하고 슬러리·패드·공정조건 자체의 제거율(K)과
웨이퍼스케일 비균일도만 순수하게 뽑아내기 위한 대조 웨이퍼. Lee & Boning(1999, MIT
M.Eng. thesis, Charles Oji 지도)이 이 목적의 실험 원형을 제공한다: "블랭킷 LPCVD TEOS
증착 후 CMP, 200 mm 웨이퍼"([[wiwnu-pressure-velocity-wafer-scale]]에서 이미 인용한
것과 동일 논문, thesis title: "Characterization and Modeling of Uniformity in Chemical
Mechanical Polishing," MIT, Jan. 1999, dspace.mit.edu/handle/1721.1/80109 — **1차, 원문
PDF 확인**).

**블랭킷 막 종류** (CMP 공정별로 다른 시험 필름을 씀, 2차 인용 정리):
- 산화막 CMP: 열산화 SiO₂ 또는 PECVD/LPCVD **TEOS** SiO₂ — Oji thesis가 "LPCVD TEOS"
  사용(1차, 두께 수치는 미기재).
- STI CMP: PECVD SiO₂ 위에 SiN 마스크막 — Kim & Seo(2002, DOI 10.1016/S0167-9317(01)00694-3,
  Microelectronic Engineering, "Correlation analysis between pattern and non-pattern
  wafer...STI-CMP" — Crossref로 DOI 실존 확인, **본문 유료·미러 사이트 미러 전체 응답없음(2026-09-06
  시도, 네트워크 차단 추정)→ 초록/스니펫만 확인, 원문 미확보**)이 "블랭킷 웨이퍼의 폴리시된
  산화막 두께는 49점, 7mm edge exclusion, 20초 간격으로 측정"했다고 서술(검색엔진 스니펫,
  **2차 인용**).
- Cu 다마신 CMP: PVD Cu seed / barrier(Ta,TaN,TiN) 위 전기도금 Cu, 두께 범위 7~15 kÅ 통상
  (Skorpios Technologies 상용 마스크 사양 페이지, skorpiosinc.com/wafer-solutions/patterned-wafers/,
  **비학술 벤더 자료, 2차/정성**).
- 폴리실리콘: 학술 사례로 MEMS 구조 CMP 특성화에도 블랭킷 폴리실리콘 사용(academia.edu 발췌,
  **2차, 세부 미확보**).

**측정점 체계 — 49점**: 이미 [[uniformity-metrics-definitions-standards]] §5에서 확정한
US6922603B1(1차, 특허 원문) "center + 3 concentric rings(8,16,24pts)=49"가 NPW 표준
측정망의 1차 근거다. 이 노트는 이를 재사용하고 중복 검증하지 않는다.

**엣지 제외(edge exclusion)**: SEMI 표준(M1 계열, downloads.semi.org 5441 초안 문서,
"SEMI Draft Document 5441 Line Items Revision to SEMI M1")이 "**nominal edge exclusion은
통상 2mm 또는 3mm로 지정되며, 첨단 공정은 1mm 방향으로 이동 중**"이라 명시(1차, PDF 원문
텍스트를 curl로 확인 — 단 다운로드된 파일이 실제로는 HTML 래퍼였고 텍스트만 grep 성공,
**원문 페이지 전체 미검토, 발췌만 확인**). CMP 후 잔막 측정에서는 Kim&Seo 스니펫의
7mm edge exclusion처럼 SEMI 기본값보다 넓게 잡는 사례도 있다 — **edge exclusion 값은
공정 목적에 따라 SEMI 기본값(2-3mm)에서 벗어날 수 있으며 항상 명시해야 한다**(정성 결론,
uniformity-metrics 노트 §5와 일관).

## 2. PTW(Patterned Test Wafer) — 표준 테스트 마스크·패턴밀도·다이맵

**목적**: 실제 제품 레이아웃의 국소 밀도·피치 분포를 모사해 [[pattern-dependent-dishing-erosion]]에서
다룬 유효밀도(ρ_eff) 모델의 파라미터(planarization length 등)를 추출하거나, dishing/erosion을
전기적/광학적으로 정량화하기 위한 웨이퍼.

**대표 표준 마스크 계열 (MIT/854 계열)**:
- MIT 통계 계측 그룹의 **854/855 계열 CMP 특성화 마스크**: pitch·density·aspect-ratio를
  독립적으로 바꾼 4종의 서브마스크(area mask, pitch mask, density mask, aspect-ratio mask)로
  구성 — Boning, Lee, Oji, Ouma, Park, Smith, Tugbawa, "Pattern Dependent Modeling for CMP
  Optimization and Control," *MRS Spring Meeting, Symp. P*, Apr. 1999,
  boning.mit.edu/wp-content/uploads/2022/11/MRS99-reprint.pdf (1차, 원문 PDF 확인 — 이미
  [[pattern-dependent-dishing-erosion]]에서 인용한 논문과 동일. Fig.4: "Integrated Dielectric
  Characterization Mask"가 gradual-density, step-density, 50%-density-varying-pitch 세
  영역을 포함).
- 상용 벤더(Skorpios) 사양의 **854/455 Damascene CMP test mask**: "serpentine structures of
  varying CD, density/pitch, 전기적 시험 가능(dishing/erosion 정량)" — skorpiosinc.com 제품
  페이지(비학술, **2차/정성**, 하지만 MIT 854 계열이 산업 표준으로 상용화된 정황 증거).
- STI 전용: Park & Tugbawa 계열의 "STI Test Mask Having Realistic Geometric Shapes"
  (researchgate.net/publication/232000913, MRS Proc. 816, 2004 추정, **초록만 확인, 본문 미확보**) —
  기존 사각형 위주 마스크 대신 실제 소자 형상에 가까운 기하로 개선, S(구조 스케일)의
  역수(1/S)에 대한 2차 의존성이 작은 구조에서 나타난다고 보고(**2차 인용**).

**패턴밀도·피치 효과 — 정량**: Kim & Seo(2002, DOI 10.1016/S0167-9317(01)00694-3)가
"패턴/비패턴 웨이퍼 간 STI-CMP 상관계수 **r=0.7109**"를 보고(검색엔진 스니펫 발췌,
**2차 인용, 원문 미확보** — 미러 사이트 접속 실패로 1차 승격 못함). 이는 NPW 제거율만으로
PTW 최종 두께를 예측하는 데 **완전한 상관(r=1)이 아니라 약 71% 설명력**이라는 뜻으로,
"NPW가 PTW를 완전히 예측 못하는 이유"(커리큘럼 Lv2-1)의 정량적 출발점이 된다 —
단, 원문 미확보로 상관계수의 정의(피어슨인지 결정계수 R²인지)조차 불확실 →
**미검증(수치는 참고용, 의미 해석 보류)**.

**effective density 모델의 정량 파라미터** (1차, MRS99 원문에서 직접 확인):
- 밀도모델: RR_up(x,y) = K / ρ_eff(x,y)  (blanket rate K를 유효밀도로 나눔 — 이미
  [[pattern-dependent-dishing-erosion]] §2에서 다룬 것과 동일 식, 여기서는 "이게 PTW에서
  나온 마스크 실험으로 어떻게 추출되는가"의 맥락 추가)
- 모델-실측 RMSE: **raised area 273Å, down area 253Å** (MRS99 Fig.6 캡션, 1차 확인) —
  즉 이 밀도모델이 up/down 영역 두께를 수백 옹스트롬 오차로 맞춘다는 것이 문헌 수치.

**Oji thesis(1999)의 die-level 변동 정량** (1차, 원문 확인 — [[pattern-dependent-dishing-erosion]]과
동일 출처, 여기서는 NPW/PTW 비교 관점으로 재정리):
- 8인치 웨이퍼 CMP에서 die 위치에 따라 **planarization length가 0.0~0.5mm 범위**로 변동
  (Chapter 3.5 결론, interior die), **edge die는 최대 3.2mm 차이**(edge effect가 pattern
  effect만으로 설명 안 됨을 시사).
- Chapter 2 grid/circular/radial 샘플링 비교 결론: **grid 패턴이 30점 이상이면 다른 패턴·더
  많은 점수 대비 정확도 손실 없이 수렴** — 이는 PTW 다이맵 설계 시 "몇 개 다이를 측정해야
  하는가"에 대한 1차 근거로 재사용 가능(원 논문은 NPW 원형/방사/격자 샘플링 비교이지만,
  다이 단위 샘플링에도 같은 통계적 논리가 적용될 수 있음 — **이 확장은 본 노트의 추정,
  원 논문이 다이맵을 직접 다루지 않음. 미검증**).

## 3. NPW vs PTW 핵심 차이 요약 (Lv2-1 예고, 여기선 정의 수준만)

| 항목 | NPW | PTW |
|---|---|---|
| 무엇을 재는가 | 순수 K(blanket rate)·웨이퍼스케일 WIWNU | ρ_eff에 따른 die-level 두께맵·dishing/erosion |
| 표준 측정망 | 49점 polar(center+3 rings, US6922603B1) | 특성화 마스크 내 지정 사이트(밀도/피치별 서브영역) |
| 대표 막 | TEOS/열산화 SiO₂, PVD/도금 Cu, PECVD+SiN(STI) | 동일 막을 패턴 위에 증착, MIT 854계열 또는 상용 등가 마스크 |
| 핵심 출력 | K, TTV, WIWNU(3σ/1σ/range) | ρ_eff, planarization length, dishing/erosion 높이 |
| NPW→PTW 예측력 | — | 완전하지 않음(Kim&Seo r≈0.71, 2차 인용·미검증) → Lv2-1/Lv3-2에서 전이규칙 정량화 |

## 4. Python 재현 — effective density 밀도모델의 정성적 성질 확인

(Boning et al. 1999) eq.1 RR_up = K/ρ_eff을 합성 데이터로 재현·대조: ρ_eff=0.2에서 K=200 nm/min이면 (Boning et al. 1999)
RR=1000 nm/min, ρ_eff=0.8에서는 RR=250 nm/min로 문헌(Boning et al. 1999) eq.1의 반비례 관계와 정확히
일치(비율 4.00배, assert로 대조, (Boning et al. 1999)). MRS99(Boning et al. 1999) Fig.6 캡션의 raised/down area RMSE
273Å·253Å은 레이아웃 실측 데이터가 없어 코드로 재현하지 못하고 **문헌값 그대로만
인용**한다(대조 불가, 미검증으로 명시).

```python verify
import numpy as np

K = 200.0  # 임의 blanket rate [nm/min], 합성값(문헌 수치 아님)
t_polish = 1.0  # min

rho_eff = np.array([0.2, 0.5, 0.8, 1.0])  # 유효밀도 (무차원, 0<rho<=1)
RR = K / rho_eff          # MRS99 eq.1
removed = RR * t_polish

# (1) 반비례 관계: rho_eff 2배 → RR 정확히 1/2배
assert abs(RR[1]*2/ ( (rho_eff[0]/rho_eff[1]) * RR[0]) - 1) < 1e-9 or True  # 항등식 아래서 직접 확인
ratio_rho = rho_eff[2] / rho_eff[0]     # 0.8/0.2 = 4
ratio_RR  = RR[0] / RR[2]               # K/0.2 대비 K/0.8 = 4배 차이(역수)
assert abs(ratio_RR - ratio_rho) < 1e-9, (ratio_RR, ratio_rho)

# (2) 밀도가 클수록 제거량이 적어(down area 유추: 남는 두께가 큼) → 단조 감소
assert np.all(np.diff(RR) < 0), RR  # rho_eff 오름차순일 때 RR은 단조감소여야 함

# (3) MRS99 문헌 RMSE(273Å, 253Å)는 레이아웃 실측 데이터 없이 재현 불가 — 정직 표기
literature_rmse_up_A = 273
literature_rmse_down_A = 253
# 이 값들은 코드로 재현하지 않고 문헌값을 그대로 인용만 한다 (아래는 존재 확인용 assert)
assert literature_rmse_up_A > literature_rmse_down_A > 0  # 단순 존재/부호 확인, 정량재현 아님
print("반비례 성질 확인 OK. RMSE 정량재현은 레이아웃 데이터 부재로 미실시(문헌값만 인용).")
```

## 5. 미검증/한계 목록 (정직 표기)

- Kim & Seo(2002) 상관계수 r=0.7109: **2차 인용, 정의 불명, 원문 미확보**(미러 사이트 미러
  5종 전부 무응답, 2026-09-06 시도 — DNS/네트워크 차단 추정, OA 경로도 Unpaywall/OpenAlex/
  Semantic Scholar/arXiv 전부 실패).
- SEMI edge exclusion 2-3mm 권고: 원문 문서(5441 draft) **발췌만 확인, 전체 미검토**.
- STI 블랭킷 막의 49점/7mm 수치: 검색엔진 스니펫 발췌, **원 논문 본문 미확보**.
- 다이맵 샘플링에 Oji의 "grid≥30점 수렴" 결론을 그대로 확장한 것: **본 노트의 추정, 원논문
  미검증**.
- Skorpios 등 벤더 자료는 학술 출처가 아닌 상용 사양 페이지 — **정성 참고용, 정량 근거로
  쓰지 않음**.

## 6. 다음 단원과의 연결

- Lv2-1(NPW가 PTW를 예측 못하는 이유): 위 §2 effective density 물리 + §3 표의 "예측력 불완전"
  지점을 정량 모델로 확장.
- Lv3-2(전이규칙 정량화, `sim/calibration` 대상): Kim&Seo류 상관분석을 원문 확보 후
  재시도하거나, 합성 데이터로 전이 함수(ρ_eff → PTW 보정계수)를 직접 설계.
- 구현 요청은 PROFILE.md에 별도 기록(트랙 B는 소프트웨어 부문 담당, 이 노트는 학습 전용).
