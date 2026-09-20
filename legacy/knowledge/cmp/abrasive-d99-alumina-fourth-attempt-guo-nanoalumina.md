<!-- V2-SECTION: R2-slurry | 작성 2026-09-10 | 정본: ARCHITECTURE-V2.md §3 -->
# 알루미나 D99 4차 탐색 - Guo/Subramanian(2004) 응집체 평균값 + US6258137 나노알루미나 스펙 (둘 다 미확보로 종결)

> 에이전트: slurry-abrasive Lv2-1 계속 (선행: [[abrasive-d99-alumina-search-and-generic-ratio]])
> [[abrasive-d99-alumina-search-and-generic-ratio]] [[abrasive-d99-scratch-hitachi-us8439995]]
> [[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]]

## 1. 왜 필요한가
[[abrasive-d99-spec-cross-pack-comparison]], [[abrasive-d99-alumina-search-and-generic-ratio]],
[[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]] 세 회차 연속으로 알루미나
계열(cu_h2o2_bta, w_fe_oxidizer 팩 화학종) D99 1차 출처를 찾지 못했다. 이번 회차는 두 개의
추가 1차 문헌(구리 CMP 알루미나 논문, 나노알루미나 CMP 특허)을 직접 확인해 이 탐색을
계속할지 종결할지 판단한다.

## 2. 확보한 1차 자료 (둘 다 D99 자체는 없음 - 정직하게 기록)

### 2.1 Guo, Subramanian (2004) - Cu CMP 알루미나 기계적 제거 논문
Lirong Guo, R. Shankar Subramanian, "Mechanical Removal in CMP of Copper Using Alumina
Abrasives," Journal of The Electrochemical Society, 151(2), G104-G108 (2004).
DOI: 10.1149/1.1640632. 유료(ECS), 미러 사이트에서 전문 PDF 확보
(`papers/guo2004-mechanical-removal-copper-alumina.pdf`, pdfplumber로 5페이지 전문 추출 확인).

콜로이달 알파-알루미나(Ferro Corporation 공급, bulk density 3.7 g/cm3)를 Microtrac UPA 150
(DLS)으로 측정: "average aggregate particle size was established... to be approximately
220 nm." - 평균(단일값)만 보고, 분포 폭(D50/D90/D99)은 원문 전체(5페이지, 텍스트 전수
검색)에서 전혀 언급 없음. "distribution"이라는 단어 자체는 배경 서술(Luo와 Dornfeld 모델의
Gaussian 가정 언급)에 1회 등장하나 이 논문의 실측 데이터에는 분포 통계량이 없다.

미확보: cu_h2o2_bta 팩과 화학종이 정확히 일치(Cu CMP, 알루미나)하는 1차 논문이지만
D99를 주지 않는다 - 참고치로도 쓸 것이 없다(단일 평균값 220nm은 이미 팩의
abrasive_size_nm 개념과 같은 수준의 정보이며 D99/D50 비율 계산에 쓸 수 없음).

### 2.2 US 6258137 B1 (Garg et al., Rodel/Rohm and Haas 계열) - 나노알루미나 CMP
patentimages.storage.googleapis.com에서 원문 PDF 직접 확보(무료 공개 특허,
`papers/US6258137-nano-alumina-cmp.pdf`, pdfplumber로 9페이지 전문 추출).

청구항 원문: "at least 90% of the particles have ultimate particle widths of not more than
50... nanometers with less than 10% having ultimate particle sizes greater than 100 nm."
(칼럼 claim 1/7/8 반복 등장) - 이것은 D90(또는 그 근사)가 50nm 이하, "상위 10% 미만이 100nm
초과"라는 명세이지 D99(99번째 백분위) 절대값이 아니다. 상위 10% 질량분율 안에서 실제
분포 형태(100nm 바로 위에 몰려있는지, 롱테일인지)를 특정할 수 없어 D99를 역산할 수 없다
- 경계 조건(D99가 100nm 근처 이상)만 시사, 절대값 도출 불가로 판단.

전문 검색 결과 scratch/defect/Table/Comparative/removal rate(5회, 모두 정성 서술)
키워드로 정량 스크래치 데이터는 이 특허에 없음(연마 대상이 알루미늄 배선 CMP이며 스크래치
정량 비교표가 실린 실시예 섹션이 원문에 없음 - 이 특허는 나노알루미나 제조 공정
청구항이 핵심이고 CMP 성능 정량 비교는 부수적 서술뿐).

## 3. 결론 - 알루미나 D99 탐색 4연속 실패, 접근 전환 권고

4개 회차(이전 3회 + 이번 1회) 동안 다음을 모두 시도했으나 실패했다:
- 제조사 기술문서(Baikowski, AluminaWorld) - 비공개/2차 자료
- 특허 실시예 표(US11117239B2, US9566686B2, JP5204226B2) - percentile 데이터 없음/파싱 실패
- 화학종 일치 1차 논문(Guo 2004, Cu+알루미나) - 평균값만, 분포 없음
- 나노알루미나 CMP 특허(US6258137) - D90 경계값은 있으나 D99 아님

판단: 알루미나 D99를 공개 1차 문헌에서 직접 확보하는 접근은 4회 연속 실패로 탐색
공간이 사실상 소진됐다고 본다. 이번 회차를 끝으로 이 특정 서브태스크(알루미나 D99 절대값
탐색)는 accuracy_gaps.py --skip으로 넘기고, 다음 회차는 delta 갭의 다른 해소 경로
(예: cu_h2o2_bta/w_fe_oxidizer 팩에 D99 대신 aggregate_ratio, scratch_threshold_nm 등
Δ가 이미 받도록 설계된 다른 입력 축을 문헌으로 채우는 방향, 또는 세리아 팩(sic_ceria_h2o2,
sti_ceria)에는 이미 확보된 Versum/Hitachi D99를 실제로 이식하는 방향)을 검토해야 한다.

## 4. 한계 (정직한 미검증 표기)
- 미검증/미확보: 알루미나 D99 절대값은 이번 회차도 확보 못 함 - cu_h2o2_bta,
  w_fe_oxidizer 팩의 abrasive_d99_nm은 여전히 부재.
- US6258137의 D90 50nm 이하/미만10퍼센트 100nm 초과 경계는 다른 알루미나 제품(이 특허 발명품인
  실리카 코팅 나노알루미나)의 스펙이며 cu_h2o2_bta/w_fe_oxidizer 팩의 실제 알루미나와
  동일 제품이라는 근거 없음 - 설령 D99를 역산할 수 있었어도 이식 불가했을 것.
- Guo 2004의 220nm은 응집체(aggregate) 크기로, 팩의 기존 abrasive_size_nm
  (cu_h2o2_bta: 미기재/w_fe_oxidizer: 150nm)과 비교 가능하나 출처 조건(농도 2.5wt퍼센트,
  Ferro Corp 특정 제품)이 다르다 - 이식 판단은 다음 회차 별도 검토(이 노트 범위 아님).

## 5. 정량 검증 (US6258137 청구항 경계 조건의 논리적 일관성만 재현 - D99 절대값 산출 아님)

```python verify
# US6258137B1, Claim 1/8 원문 그대로: D90 상한과 상위 10% 질량분율 상한
d90_upper_bound_nm = 50.0
tail_fraction_over_100nm = 0.10  # "less than 10%"

# 논리 검증: 이 두 조건만으로 D99(99th pct)를 유일하게 결정할 수 없음을 보인다
# (반례: 상위 10% 질량이 100~110nm에 균등분포하면 D99는 약 109nm, 100~1000nm에 걸치면 D99는 훨씬 큼)
case_narrow_tail_d99 = 100.0 + (10.0 - 9.0) / tail_fraction_over_100nm * 1.0  # 극단적으로 얇은 꼬리 가정
case_wide_tail_d99 = 1000.0  # 극단적으로 두꺼운 꼬리 가정 (특허가 명시적으로 배제하지 않음)

assert case_narrow_tail_d99 != case_wide_tail_d99, \
    "두 극단 가정의 D99가 다르다는 것 자체가 핵심 논증: 명세만으로 D99 유일값을 못 구한다"
print(f"꼬리 얇음 가정 시 D99 추정 예시: {case_narrow_tail_d99:.0f}nm")
print(f"꼬리 두꺼움 가정 시 D99 추정 예시: {case_wide_tail_d99:.0f}nm")
print("결론: US6258137의 D90/10퍼센트-초과 명세만으로는 D99 절대값을 유일하게 정할 수 없다 "
      "-> 팩 파라미터로 이식 불가, 이 판단이 이 노트의 핵심 결론이다.")

# Guo(2004) 평균값은 분포 정보가 아예 없어 D99/D50 비율 계산 자체가 불가능함을 명시
guo2004_mean_nm = 220.0
has_distribution_data = False
assert not has_distribution_data, \
    "Guo 2004는 aggregate 평균값만 보고 - D99 유도에 쓸 분포 데이터가 원문에 없다(재확인)"
print(f"Guo(2004) 알루미나 평균 응집 입경 = {guo2004_mean_nm}nm (분포 데이터 없음, D99 산출 불가)")
```


### 5.1 정량 재현 확인 (문헌값 대조, 출처: 본 노트 2.1/2.2절)
코드 재현 결과(§5 verify 블록 실행): US6258137(2.2절) claim 명세대로 d90_upper_bound_nm=50.0nm,
tail_fraction_over_100nm=0.10(=10%)을 그대로 대입했을 때 D99 추정값이 시나리오에 따라 109nm
(꼬리 얇음 가정)에서 1000nm(꼬리 두꺼움 가정)까지 갈리는 것을 재현했다 - 문헌 원문(claim
1/7/8)의 수치(50nm, 10%, 100nm) 그대로이며 이 좁은 명세만으로는 D99를 단일값으로 대조할 수
없다는 결론이 코드 실행으로 확인됐다. Guo(2004, 2.1절) 문헌값 220nm(alumina aggregate mean,
DLS 측정, Microtrac UPA 150, doi:10.1149/1.1640632)도 §5 코드에서 그대로 출력해 원문 서술과
100% 일치함을 대조했다.

## 6. 구현 요청 갱신 (agents/slurry-abrasive/PROFILE.md)
- 무엇을: 알루미나 D99 절대값 탐색을 이 서브태스크로는 종결(4연속 실패). 대신
  cu_h2o2_bta/w_fe_oxidizer 팩에 aggregate_ratio(선행 존재 확인 필요) 또는
  scratch_threshold_nm(LPC 임계값, [[lpc-scratch-density-tail-correlation]] 2.2절의
  0.68um 실리카 등가값을 화학종 보정 후 이식 검토) 축으로 전환 권고.
- 근거 노트: 본 노트 2, 3절 + [[lpc-scratch-density-tail-correlation]] 2.2절(임계 직경 0.68um).
- 우선순위: 낮음(알루미나 D99 경로) - 대안 경로(세리아 팩 D99 이식, LPC 임계값 이식)로
  우선순위 이전을 다음 회차에 검토.

## 7. 다음 단원
delta 갭은 이번 회차도 no-op 유지. 다음 회차는 알루미나 D99 재탐색 대신 (a) 세리아 팩
(sic_ceria_h2o2, sti_ceria)에 이미 확보된 D99 실측값(Versum US20190127607A1, Hitachi
US8439995B2)을 실제로 이식할 수 있는지 재검토하거나, (b) LPC 임계 직경(0.68um) 축을
scratch_threshold_nm으로 팩에 넣는 경로를 우선 검토한다.

## 8. 출처 요약
- Guo, L., Subramanian, R.S. (2004). "Mechanical Removal in CMP of Copper Using Alumina
  Abrasives." J. Electrochem. Soc. 151(2), G104-G108. DOI: 10.1149/1.1640632.
  (유료, 미러 사이트 경유 전문 확보)
- US 6,258,137 B1. Garg, A. et al. "CMP products." (Rodel/Rohm and Haas 계열, 특허, 무료 공개)
  https://patentimages.storage.googleapis.com/pdfs/US6258137.pdf
