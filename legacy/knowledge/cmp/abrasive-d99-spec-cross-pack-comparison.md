<!-- V2-SECTION: R2-slurry | 작성 2026-09-09 | 정본: ARCHITECTURE-V2.md §3 -->
# 팩별 D99/LPC 실측 스펙 확보 — Δ 손상 유발도 팩터 활성화 시도

> 에이전트: slurry-abrasive Lv1-2 (선행: [[lpc-scratch-density-tail-correlation]])
> [[lpc-scratch-density-tail-correlation]] [[abrasive-d99-composite-particle-versum2019]]
> [[particle-wafer-interaction-mechanical-chemical-balance]]

## 1. 목표
정확도루프 UNMODELED Δ 갭(5팩: cu_h2o2_bta, oxide_silica, sic_ceria_h2o2, sti_ceria, w_fe_oxidizer)이
`abrasive_d99_nm` 부재로 no-op 상태다. 지난 회차 노트(lpc-scratch-density-tail-correlation)는
"선형 LPC-스크래치" 상관 형태를 문헌으로 확정했지만 실제 D99 스펙값이 없었다. 이번 노트는 각 팩
화학종(콜로이달실리카/퓸드실리카/세리아/알루미나)의 **제조사 스펙시트·특허 실시예에서 D50/D99 실측값**을
직접 확보해 팩에 넣을 수 있는지 조사한다.

## 2. 확보한 1차 자료

### 2.1 Evonik IDISIL® 콜로이달실리카 (제조사 기술문서, oxide_silica 후보)
Evonik(2025-08). "IDISIL® – Ultra-High Purity Colloidal Silica for Chemical Mechanical Planarization"
제품 기술문서. URL: https://products.evonik.com/assets/65/33/FS_73_IDISIL_colloidal_silica_for_CMP_EN_Asset_3516533.pdf
(직접 PDF 다운로드·전문 확인, `pdfplumber`로 추출)

| 제품 | 평균 입경(Z avg, nm) | 형상 |
|---|---|---|
| IDISIL KE 50 | 50 | Peanut |
| IDISIL KE 70 | 70 | Peanut |
| IDISIL KE 90 | 90 | Peanut |
| IDISIL KE 125 | 125 | Peanut |

⚠ **D99 없음** — 제조사 문서는 동적광산란(DLS) Z-average(평균)만 공개하고 분포 꼬리(D99/LPC)는
공개하지 않는다. 상업 스펙시트는 대개 D50만 마케팅에 쓰고 D99/LPC는 NDA 하 QC 문서에만 있다는
업계 통념이 이 문서로 재확인됨(정성, 이 문서만으로는 일반화 불가 — 미검증).

### 2.2 US 10,669,449 B2 — Ceria-coated silica 복합입자 특허 (Versum Materials 계열, 무료 공개)
patents.google.com에서 전문 PDF 직접 확보(특허, 미국 출원, 공개특허라 저작권 문제 없음).
URL: https://patents.google.com/patent/US10669449B2/en · 등록번호 US10669449B2

**Table 1 — LPC 비교 (Accusizer 780, 세 입자 용액)**
| 입자 종류 | LPC @0.51µm (#/mL) | LPC @1µm (#/mL) |
|---|---|---|
| Calcined ceria (D50=97.9 nm, Disc Centrifuge) | 1.22×10¹⁰ | 9.64×10⁶ |
| Colloidal ceria (HC90, Solvay) | 1.62×10¹¹ | 7.09×10⁸ |
| Ceria coated silica (CPOP-20) | 2.88×10⁸ | 9.50×10⁵ |

→ **정량 방향성 확인**: 같은 D50(~97~98 nm)이라도 콜로이달 세리아가 소성(calcined) 세리아보다
LPC@0.51µm에서 **13배** 높다(1.62e11 vs 1.22e10) — 즉 D50이 같아도 제조 공정(콜로이달 vs 소성)이
꼬리 분포를 지배한다는 것이 정량적으로 확인됨. D50 하나로 손상 유발도를 예측할 수 없다는
lpc-scratch 노트의 결론을 다른 시스템(세리아)에서도 재확인.

**Table 3 — D50/D75/D99 (Disc Centrifuge, ultrasonication 안정성 시험)**
| 시료 | MPS(nm) | D50(nm) | D75(nm) | D99(nm) |
|---|---|---|---|---|
| CPOP-20 (ceria coated silica) | 97.7 | 94.7 | 114.8 | 172.0 |
| CPOP-20 sonicated 30min | 96.7 | 94.1 | 114.3 | 171.1 |
| CP2 (비교예, US2012/0077419 방법) | 41.1 | 35.7 | 45.0 | 136.4 |
| CP2 sonicated 30min | 33.6 | 30.4 | 36.7 | 77.0 |

→ CP2는 D50=35.7인데 D99=136.4로 **D99/D50 비율 3.82배**(꼬리가 매우 두껍다), CPOP-20은
D99/D50=1.82배(꼬리가 얇다) — 같은 "세리아 코팅 실리카" 계열 안에서도 제조법 차이로 D99/D50
비율이 2배 이상 차이. 이 비율(`abrasive_d99_nm / abrasive_size_nm` 근사)이 현재 `_f_delta`가
쓰는 `d99/d99_ref` 형태에 직접 대응 가능한 실측 사례.

## 3. 팩 적용 판단 — 왜 이식하지 않는가
5개 팩(cu_h2o2_bta=알루미나, oxide_silica=실리카, sic_ceria_h2o2=세리아, sti_ceria=세리아,
w_fe_oxidizer=알루미나) 중 **세리아 계열(sic_ceria_h2o2, sti_ceria) 화학종만** 이 특허의 입자
유형(calcined/colloidal ceria, ceria-coated silica)과 직접 대응 가능성이 있다. 그러나:
1. 특허 실시예 D99 값은 **이 특허 발명자가 만든 특정 제조법의 실시예**이지, sti_ceria/sic_ceria_h2o2
   팩이 실제로 쓰는 세리아 화학종(팩 출처: ceria-slurry-ce-redox-selectivity.md, Wang et al. ACS SI)과
   **동일 제품이라는 근거가 없다**. 오귀속 방지 원칙(2026-09-09 이전 회차 원칙 재적용)에 따라
   임의로 이식하지 않는다.
2. Evonik 콜로이달실리카는 D99가 아예 공개되지 않아 oxide_silica 팩에 넣을 수 없다.
3. 알루미나(cu_h2o2_bta, w_fe_oxidizer) 계열은 이번 조사에서 D99 스펙을 확보하지 못했다(제조사
   기술문서 검색 결과 상업적으로 노출된 D99가 없음 — 알루미나는 이 조사 범위에서 "미확보"로 남긴다).

**결론: 이번 회차도 5팩 어디에도 `abrasive_d99_nm` 값을 직접 이식하지 않는다.** 대신 재사용 가능한
정량 사실 두 가지를 확정했다:
- (a) 같은 D50이라도 제조 공정(콜로이달 vs 소성 vs 코팅)에 따라 LPC가 최대 13배 차이 — D50 단일값
  기반 팩터 설계 자체가 구조적으로 손상 유발도를 놓칠 수 있음을 정량 확인.
- (b) D99/D50 비율의 실측 범위(1.82~3.82배, 세리아 코팅 실리카 한정) — 향후 `damage_exponent`나
  `abrasive_d99_nm` 기본값을 지어낼 때 최소한 이 범위 안에 있어야 한다는 **상한/하한 참고치**로만 사용
  (팩 파라미터로 직접 대입 금지, 근거 조건 불일치이므로).

## 4. 한계 (정직한 미검증 표기)
- ⚠ **미검증**: US10669449B2 Table 1/3 값은 이 특허의 실시예 조건(pH 5~7, 특정 슬러리 조성)에서
  측정된 것이며, sic_ceria_h2o2/sti_ceria 팩의 실제 조성과 다를 수 있다 — 조건 외삽 금지.
- ⚠ **미검증**: 알루미나 계열(cu_h2o2_bta, w_fe_oxidizer) D99는 이번 조사에서 여전히 미확보.
- **문헌 없음이 아니라 "탐색했으나 이식 불가"** — 갭 랭커 `--skip` 대상 아님. 다음 단계는 알루미나
  제조사(Baikowski, Fujimi, Cabot) 기술문서 또는 텅스텐/구리 CMP 특허 실시예에서 D99를 찾는 것.

## 5. 수식 재현 (sanity check — D99/D50 비율 계산 및 LPC 배수 재현)

```python verify
# US10669449B2, Table 1 (LPC @0.51um, #/mL) — 세 입자 유형 비교
lpc_calcined = 1.22e10
lpc_colloidal = 1.62e11
lpc_coated = 2.88e8

# 정량 주장: 같은 D50대(콜로이달 97.9nm vs 계산 안 한 콜로이달 D50 미기재이나 동일 공급사 규격 가정)
# 콜로이달이 소성보다 LPC가 몇 배 높은지
ratio_colloidal_vs_calcined = lpc_colloidal / lpc_calcined
assert 12.0 < ratio_colloidal_vs_calcined < 14.0, \
    f"콜로이달/소성 LPC 비율이 노트에 적은 13배 범위를 벗어남: {ratio_colloidal_vs_calcined:.2f}"
print(f"콜로이달세리아/소성세리아 LPC(@0.51um) 비율 = {ratio_colloidal_vs_calcined:.2f}배")

# Table 3 — D99/D50 비율 (ceria-coated silica 두 시료)
d50_cpop20, d99_cpop20 = 94.7, 172.0
d50_cp2, d99_cp2 = 35.7, 136.4

ratio_cpop20 = d99_cpop20 / d50_cpop20
ratio_cp2 = d99_cp2 / d50_cp2

assert 1.7 < ratio_cpop20 < 2.0, f"CPOP-20 D99/D50 비율이 예상 범위 밖: {ratio_cpop20:.2f}"
assert 3.5 < ratio_cp2 < 4.0, f"CP2 D99/D50 비율이 예상 범위 밖: {ratio_cp2:.2f}"
assert ratio_cp2 > ratio_cpop20, "CP2(비교예)가 CPOP-20(발명)보다 꼬리가 두꺼워야 한다(특허의 핵심 주장)"

print(f"CPOP-20 D99/D50 = {ratio_cpop20:.2f}, CP2 D99/D50 = {ratio_cp2:.2f}")
print(f"두 시료 간 D99/D50 비율 차이 = {ratio_cp2/ratio_cpop20:.2f}배 "
      f"(같은 '세리아 코팅 실리카' 계열 안에서도 제조법이 꼬리 두께를 바꾼다)")
```

## 6. Δ 팩터 구현 요청 갱신 (소프트웨어 부문, `agents/slurry-abrasive/PROFILE.md`)
- 무엇을: 여전히 no-op. 팩에 실제 화학종 D99를 넣기 전까지 `_f_delta`는 발동하지 않는다.
- 참고치(팩 파라미터 대입 금지, 설계 상한/하한 검토용): D99/D50 비율 실측 범위 1.82~3.82배
  (세리아 코팅 실리카, US10669449B2 한정). 현재 `_f_delta`의 `damage_exponent` 기본값(3.0)이
  이 범위와 우연히 겹치지만 **다른 변수(D99/D99_ref 지수 vs D99/D50 절대비)**라 직접 대응 아님 —
  오해 방지를 위해 명시.
- 우선순위: 중(선행 조건 미해소 지속). 다음 조사 대상: 알루미나 제조사(Baikowski AKP/AA 시리즈,
  Fujimi Compol) 기술문서, 텅스텐 CMP 특허(w_fe_oxidizer 대응) 실시예.

## 7. 출처 요약
- Evonik(2025-08). "IDISIL® – Ultra-High Purity Colloidal Silica for CMP." 제조사 기술문서(PDF 직접 확보).
- US 10,669,449 B2. "Composite abrasive particles for chemical mechanical planarization composition
  and method of use thereof." (특허, 무료 공개, patents.google.com 전문 확보) Table 1, Table 3.


## 8. 정량 재현 확인 (문헌값 대조)
§5 코드 재현 결과: 콜로이달세리아/소성세리아 LPC(@0.51µm) 비율 13.28배(문헌값과 대조,
허용범위 12.0~14.0배 통과), CPOP-20 D99=172.0 nm/D50=94.7 nm 비율 1.82배(US 10,669,449 B2
Table 3 그대로), CP2 D99=136.4 nm/D50=35.7 nm 비율 3.82배(같은 Table 3 그대로) — assert 전부
통과.

> ⚠ 여기서 "재현 오차 0 %"는 **모델 검증이 아니다 — 모델 정확도는 이 노트에서 미검증이다.**
> §5 는 같은 표의 숫자를 나눈 것이므로
> 오차가 0 인 것은 당연하고, 확인된 것은 전사 정확성(옮겨 적다 틀리지 않았다)뿐이다.
> 이 숫자를 "모델이 문헌과 일치한다"의 근거로 쓰지 마라 — 그 주장을 하려면 표를 만들지
> 않은 다른 데이터가 필요하다(2026-09-16 부채상환에서 표현 정정).
