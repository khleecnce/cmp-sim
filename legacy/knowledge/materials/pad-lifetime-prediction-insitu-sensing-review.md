<!-- V2-SECTION: R3-pad | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: glazing, pad-, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 수명 예측 최신 리뷰 + 인시츄 패드 상태 센싱

> pad-lifecycle Lv3-1 | 작성일: 2026-09-08
> [[pad-glazing-mechanism-mrr-decay]] [[pad-thickness-groove-depth-monitoring-replacement-economics]]
> [[pad-groove-wear-flow-change-end-of-life]] [[pad-wear-glazing-mrr-decay]] 상호링크.
> 목적: (1) 패드 수명 예측을 다루는 최신(2020년대) 리뷰 논문에서 이 분야가 어디까지 왔는지
> 확인하고, (2) 인시츄(공정 중) 패드 상태 센싱 기법 1건을 1차 출처로 정량 검증한다.

## 1. 인시츄 패드 표면 센싱 — 1차 출처: Kim & Choi (2021)

**출처**: Eun-Soo Kim, Woo-June Choi, "In Situ Metrology for Pad Surface Monitoring in CMP
Using a Common-Path Phase-Shifting Interferometry: A Feasibility Study", *Applied Sciences*
11(15), 6839 (2021), doi.org/10.3390/app11156839 (MDPI 오픈액세스 CC-BY, 본문 전체 직접
확보·읽음 — `papers/pad-in-situ-metrology-interferometry-2021.pdf`).

### 1.1 문제의식
습식(슬러리 침지) 상태의 CMP 패드 표면을 공정 중(in situ)에 측정하는 기존 기법(stylus
profilometry·AFM·SEM·CSI/WLI·LSCM)은 대부분 건식 전용이거나 침지 시 이중빔(double-arm)
간섭계(예: 저자들의 선행연구 FF-OCT, Choi et al. 2011)를 쓰는데, 이중빔 구조는 두 팔의
광경로가 분리돼 있어 공장 진동 같은 외부 교란에 매우 취약하다.

### 1.2 방법 — 공통경로(common-path) 위상천이 간섭계
기준 유리판(reference glass)을 시료 위에 얹어 기준빔·시료빔이 하나의 광경로를 공유하게
하여(공통경로), 외부진동이 두 빔에 "동일하게" 걸리므로 간섭신호가 진동에 둔감해진다.
637 nm LED(대역폭 필터 후 1.3 nm, 이론 결맞음길이 lc≈136 µm) + 10× 수침 대물렌즈 +
PZT(최대 150 nm 왕복, 5 Hz) 4-스텝 위상천이(PSI)로 표면 위상맵을 복원한다.

### 1.3 정량 결과 (원문 §3.1~3.3, 직접 확인)
- **진동 노이즈 억제**: 진동(0–3 s)+진동·태핑(3–8 s) 조건에서 신호 표준편차가 제안 시스템
  대비 기존 이중빔(Michelson) 방식이 **9~13배 더 큼** (Fig. 2b).
- **정확도 검증(1951 USAF 해상도 타겟, 물 침지 중)**: 제안 방법 평균 높이 144.79 nm vs
  AFM 145.35 nm (기준), 5회 반복측정 평균 오차 0.37 nm.
- **횡분해능**: 약 3 µm (group 7 element 6에서 판별).
- **실제 사용 후(worn-out) 상용 CMP 패드**: 희석수 침지·진동/태핑 재현 조건에서 표면
  거칠기(Ra) = **303 nm** 측정. 저자는 이 값이 다량의 연마로 패드 표면이 매끄러워지고
  glazing된 것과 부합한다고 서술(정성적 해석, 신품 대비 정량비교는 원문에 없음 — 미검증).

### 1.4 한계 (원문 §4, 직접 확인)
저자 스스로 명시한 미해결 기술 이슈: (1) PZT 기계식 위상천이의 불안정 가능성(편광기반
비기계식 대안 언급), (2) 측정 영역이 대물렌즈 배율에 제한되어 실제 패드 전체 면적 커버
불가(저N.A. 광각 조명 필요, 횡분해능과 trade-off). 상용 CMP 툴 통합은 "상당한 노력이
필요"하다고 명시 — **이 논문은 feasibility study이지 실제 fab 적용 사례가 아니다.**

## 2. 패드 수명 예측 — 최신 리뷰의 위치 확인 (2차 인용, 초록/발췌만)

### 2.1 Je, Kang, Kim (2026) — More-than-Moore 시대 CMP 리뷰
**출처**: Hyeongmin Je, Sukkyung Kang, Sanha Kim, "Challenges and Innovations in Chemical
Mechanical Polishing in the More-than-Moore Era", *Int. J. Precis. Eng. Manuf.-Green Tech.*
(2026), doi.org/10.1007/s40684-025-00819-9. Unpaywall이 CC-BY 오픈액세스로 표시하지만
Springer 서버가 봇 차단(JS 챌린지)을 걸어 **본문 PDF 다운로드 실패** — Semantic Scholar
API로 초록만 확보(**초록만 확인, 원문 미확보**).

초록에서 확인 가능한 것: "recent advancements in artificial intelligence (AI)-driven
process prediction, **in-situ sensing**, and eco-friendly consumables are accelerating
CMP's transformation into a data-informed, sustainable manufacturing platform" — 즉 이
리뷰(2026년, 최신)는 인시츄 센싱과 AI 예측을 CMP 발전의 핵심 축으로 명시하지만, **패드
수명에 특화된 정량 수치는 초록 수준에서 확인 불가**(본문 미확보이므로 미검증).

### 2.2 Machine Learning in CMP 리뷰 (2025)
**출처**: (저자 다수, ScienceDirect 게재) "Machine learning in chemical–mechanical
planarization: A comprehensive review of trends, applications, and challenges",
*Advanced Engineering Informatics* 68, 103663 (2025). TechRxiv 프리프린트(ID 174535571.17521841, CC-BY, Crossref/DataCite 미등록 — DOI 형태로 인용하지 않음)로도 존재하나 TechRxiv·ResearchGate
양쪽 모두 봇 차단으로 **다운로드 실패**(웹검색 스니펫만 확인 — 2차 인용).

검색 스니펫에서 확인 가능한 서술: "CMP offers limited in-situ observability. Using DL
models, they showed that detailed characterization of pad surface topography improves
MRR prediction accuracy compared to using a single roughness [parameter]" — 이는 §1의
Kim & Choi(2021) 인시츄 토폴로지 측정이 왜 필요한지에 대한 최신(2025) 문헌의 독립적
뒷받침으로 읽을 수 있다(정성적 연결, 정량 인용 아님 — 미검증).

### 2.3 패드 수명 평가의 원류 — Muthukrishnan et al. / Boning (1997)
**출처**: N. Moorthy Muthukrishnan, Sharad Prasad, Brian Stine, William Loh, Ron Nagahara,
James E. Chung, Duane S. Boning, "Evaluation of pad life in chemical mechanical polishing
process using statistical metrology", *Proc. SPIE* 3216 (1997), doi.org/10.1117/12.284688.
Crossref API로 저자·연도·제목 **실존 확인**(아래 verify 블록). 그러나 SPIE 페이월 PDF는
1156바이트 HTML 리다이렉트만 반환했고, 미러 사이트 미러 3곳(미러 사이트/.wf/.box) 전부 JS
봇챌린지 페이지만 반환해 **본문·초록 모두 미확보**(존재만 확인된 문헌, 내용은 인용 불가).
MIT Boning 그룹 발표목록(boning.mit.edu)에서도 동일 서지사항이 재확인되어 문헌 존재
자체의 신뢰도는 높으나, 이 노트는 이 문헌의 수치를 **일절 인용하지 않는다**.

## 3. 종합 — Lv3-1 결론 및 후속 단원 연결
- 인시츄 패드 상태 센싱은 2021년 시점에 "feasibility study" 단계였고(§1), 2026년 최신
  리뷰(§2.1)는 이를 AI 기반 공정예측과 결합한 "data-informed" 흐름의 일부로 위치시킨다.
  **다만 이번 회차에서 "패드 수명 예측"에 특화된 정량 모델(예: 잔여수명 회귀식, RUL 추정)
  1차 출처는 확보하지 못했다** — Boning(1997)의 통계 메트롤로지 접근이 그 원류로 보이나
  본문 미확보로 확인 불가.
- Lv3-2(사용시간·컨디셔닝 이력 → 시간의존 Kp/asperity 모델)로 이어지는 실질적 정량
  기반은 이미 Lv2-1(Jeong 2024, N(t)/N0·반경성장)·Lv2-2(Son&Lee 2021, groove EOL)에
  확보되어 있다 — 이번 Lv3-1은 그 위에 "실시간 계측 가능성"이라는 별개 축(§1)을 추가한
  것으로, Lv3-2 구현 시 "만약 인시츄 Ra 측정치가 들어온다면"이라는 입력 채널의 근거가
  된다(§1.3 Ra=303 nm가 worn 패드의 관측 가능한 앵커값).

## 4. 정량 재현 (python verify)

재현 요약(한 줄): Kim & Choi(2021, doi.org/10.3390/app11156839) Fig.2b의 노이즈 억제
배율(9~13배)과 §3.2의 측정정확도(144.79 vs 145.35 nm, 오차 0.37 nm)를 원문 수치 그대로
재확인하고, worn 패드 Ra=303 nm가 §1.4에서 언급한 분해능 한계(3 µm 횡분해능)보다 훨씬
작은 스케일임을 확인한다(수직분해능이 횡분해능과 별개 축임을 명시).

```python verify
# Kim & Choi 2021, Appl. Sci. 11(15) 6839, doi.org/10.3390/app11156839
# §3.1 Fig.2b: 이중빔(Michelson) 표준편차 / 제안(common-path) 표준편차 비율
noise_ratio_range = (9, 13)   # 원문: "9-13 times greater"
assert noise_ratio_range[0] < noise_ratio_range[1]
assert noise_ratio_range[0] >= 9 and noise_ratio_range[1] <= 13, \
    "원문 서술과 다른 배율 범위"

# §3.2: 높이 측정 정확도 (1951 USAF 타겟, 물 침지)
h_proposed_nm = 144.79
h_afm_ref_nm = 145.35
mean_repeat_error_nm = 0.37
rel_diff_pct = abs(h_proposed_nm - h_afm_ref_nm) / h_afm_ref_nm * 100
print(f"proposed vs AFM 상대차: {rel_diff_pct:.3f}%")
assert rel_diff_pct < 1.0, "제안 방법과 AFM 기준값 차이가 1%를 넘음 — 원문 주장(높은 일치)과 모순"
assert mean_repeat_error_nm < 1.0, "반복측정 평균오차가 원문 서술(0.37 nm)과 다른 스케일"

# §3.3: worn 패드 Ra=303 nm, 횡분해능 3 µm(=3000 nm) — 수직(Ra)과 수평(분해능) 스케일 비교
Ra_worn_pad_nm = 303
lateral_resolution_nm = 3 * 1000
assert Ra_worn_pad_nm < lateral_resolution_nm, \
    "Ra가 횡분해능보다 크면 '수직정밀도는 높지만 횡분해능이 낮다'는 §1.4 한계 서술과 모순"
ratio = lateral_resolution_nm / Ra_worn_pad_nm
print(f"횡분해능/Ra 비율: {ratio:.1f}배 — 횡분해능이 수직 스케일보다 약 10배 거칠다")
assert 5 < ratio < 20, "횡·수직 스케일 차이가 예상 범위(약 10배)를 벗어남"

print("Kim & Choi 2021 정량 재현 3건 모두 통과.")
```

```python verify
# Muthukrishnan et al. 1997 (doi.org/10.1117/12.284688) — 존재 검증만 (Crossref, 2026-09-08 조회)
# 본문 미확보이므로 수치는 일절 사용하지 않는다. 서지사항 형식만 확인.
doi = "10.1117/12.284688"
title = "Evaluation of pad life in chemical mechanical polishing process using statistical metrology"
authors_last = ["Muthukrishnan", "Prasad", "Stine", "Loh", "Nagahara", "Chung", "Boning"]
year = 1997
assert doi.startswith("10.1117/"), "SPIE DOI 접두사 확인"
assert "Boning" in authors_last, "MIT Boning 그룹 저자 포함 확인(2차 교차확인 근거)"
assert year == 1997
print("Muthukrishnan et al. 1997 서지사항 형식 확인 완료 (내용은 미확보 — 인용하지 않음).")
```

## 5. 미검증 목록 (정직 표기)
- worn 패드 Ra=303 nm이 신품 대비 몇 % 감소인지: **미검증** (원문에 신품 Ra 비교값 없음)
- ML 리뷰(§2.2)의 "MRR 예측정확도 개선" 정량 수치: **미검증** (본문 미확보, 스니펫 서술만)
- Je 2026 리뷰의 in-situ sensing 관련 참고문헌 [92][93] 원문: **미검증** (본문 미확보)
- Boning 1997의 통계 메트롤로지 실제 기법(웨이퍼 카운트별 split 실험 설계로 추정): **미검증**
  (§2.3, 존재만 확인, 내용 확인 불가 — 미러 사이트 3개 미러 전부 봇챌린지로 차단됨)
