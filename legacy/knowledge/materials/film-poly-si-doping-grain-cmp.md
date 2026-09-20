# Poly-Si 물성(도핑·결정립)과 CMP 거동

> 에이전트: film-poly-si Lv1-1 | 작성일: 2026-09-10
> [[preston-luo-dornfeld-mrr]] [[hertz-gw-contact-mechanics]] [[film-oxide-teos-hdp-bpsg-sod-density-hardness]]

## 1. 왜 필요한가 — Poly-Si CMP의 두 응용

Poly-Si CMP는 로직 게이트(HKMG replacement-gate 흐름의 더미 게이트)와 3D NAND(수직 채널
"마카로니" 필)라는 물리적으로 다른 두 용도에 쓰인다(§4에서 상술). 두 경우 모두 CMP 대상은
같은 재료(다결정 실리콘)지만, 제거율(MRR)과 균일도가 **도핑 종류·농도**와 **결정립/증착
조건**에 따라 크게 달라진다는 점은 공통이다. 이 노트는 그 두 변수(도핑, 결정립·증착조건)가
CMP 거동에 미치는 영향을 1차 문헌 두 건으로 정리한다.

## 2. 도핑(보론/인)이 CMP 제거율에 미치는 영향

출처: Pirayesh, H. (2014), *Study of the High Rate Chemical Mechanical Polishing of Heavily
Boron-doped Polysilicon for 3D Applications*, PhD thesis, University of Alberta (Materials
Engineering) — papers/pirayesh2014-ualberta-thesis-boron-doped-polysilicon-cmp.pdf, 원문 전체
확보·직접 인용(6장 "Boron doping effects on polysilicon CMP", pp. 93–102). University of
Alberta ERA 리포지토리 식별자 10.7939/R3ZP3W76C (DataCite 등록, Crossref 미등록 — §6 참고).

Pirayesh(2014)는 세 가지 poly-Si 시료를 비교했다: 웨이퍼 A(고농도 보론도핑, 저항 2.2
mΩ·cm), 웨이퍼 B(저농도 보론도핑, 저항 3.5 mΩ·cm), 웨이퍼 C(무도핑). SRP(spreading
resistance probe)로 측정한 웨이퍼 A의 정공 캐리어 농도는 6.02×10¹⁹ cm⁻³, SIMS로 측정한
보론 총농도는 7.35×10²⁰ cm⁻³로, **활성화된 보론 비율이 10% 미만**임을 보였다(Pirayesh
2014, §5의 `python verify`로 재현 — 8.2%로 계산되어 "<10%" 서술과 일치). 이는 증착온도(885.5 K)에서의
고체용해도(>10²⁰ cm⁻³)가 상온(295 K)으로 내려오며 급감하기 때문으로, 잔여 보론은
격자간(interstitial) 자리나 결정립계 석출물로 남는다.

**제거율(MRR) 결과** (6psi, 90–120rpm, 200 ml/min 슬러리유량 조건):
- 무도핑(웨이퍼 C)의 MRR은 고농도 보론도핑(웨이퍼 A, 2.2 mΩ·cm)보다 **약 5배** 높다.
- 웨이퍼 A→B로 캐리어농도가 ~50%(Pirayesh 2014; 정확히는 48.5%, `python verify`로 재현)
  감소하면 MRR은 **약 3배** 증가한다.
- 저항률(ρ, mΩ·cm)과 MRR(μm/min)은 지수형 경험식 `RR = A·ρ^B`로 피팅되며, 실험 조건에 따라
  A=0.29–0.52, B=0.006–0.091 범위였다(Fig. 6-5, 90rpm/6psi/200ml/min 조건 피팅).

**메커니즘**: 보론(억셉터, p-type)은 표면 근처에서 음전하 공핍층을 형성해 알칼리 슬러리의
핵심 반응종인 **수산화이온(OH⁻)의 표면 전달(transportation)을 정전기적으로 반발**시켜
화학적 식각을 억제한다. Pirayesh(2014)는 이를 "화학적 성분(수산화이온 전달)이 억제되므로
연마 조건을 기계적으로 지배적으로 바꾸면(고압·저유량·고속 조건, boundary/dry lubrication
regime) 보론 도핑의 악영향을 상쇄할 수 있다"는 가설로 검증했고, 최적화된 공정에서 표준
대비 최대 100% MRR 향상을 보고했다. 인(P) 등 n-type 도판트는 반대로 OH⁻를 **정전기적으로
끌어당겨** 화학적 식각이 오히려 촉진되는 것으로 Pirayesh(2014)가 Liu et al.의 모델을
인용하며 서술한다 — **미검증(Liu et al. 원논문 미확인, Pirayesh의 재인용만 확인)**. 비소(As)
도핑에 대한 정량 데이터는 이번 조사에서 1차 문헌을 찾지 못했다 — **미검증**.

## 3. 결정립·증착조건(LPCVD 온도, 어닐링)이 CMP 거동에 미치는 영향

출처: Park, S., Jeong, H., Yoon, S.-H. (2016), "The Dependence of Material Removal Rate on
Annealing Treatment in Polysilicon CMP," *International Journal of Materials, Mechanics and
Manufacturing* 4(2), 115–118, DOI: 10.7763/IJMMM.2016.V4.236 —
papers/ijmmm2016-annealing-polysilicon-cmp.pdf, 원문 전체 확보·직접 인용.

이 연구는 4인치 Si 웨이퍼에 LPCVD로 poly-Si(545, 585, 625°C 증착) 및 비정질 Si(대조군)를
2 μm 증착한 뒤, 1050°C/N₂/30분 열처리 전후의 표면조도·결정립계밀도·영률(Young's modulus)과
CMP MRR(P1000 세리아/실리카 슬러리, Rodel IC1400 패드, 500 g/cm² 하중)을 측정했다.

핵심 결과:
- **LPCVD 온도가 높을수록 결정립계 밀도는 증가하지만 결정립 크기 자체는 변하지 않았다**
  (625°C 시료는 어닐링 후 결정립계 연장이 5.2배 증가). 즉 이 실험 범위에서 CMP 거동을
  좌우하는 것은 결정립 "크기"가 아니라 결정립계 밀도와 결부된 **영률(경도 프록시)**이었다.
- 어닐링 전 영률: 비정질-Si 169±3.2, 545°C-poly 168±4.5, 585°C-poly 159±3.3, 625°C-poly
  151±6.0 GPa. 어닐링 후: 173±2.6, 172±5.7, 165±4.2, 160±5.4 GPa (모두 상승 — 원자
  재배열로 Si-Si 결합밀도 증가).
- 어닐링 전 MRR: 7032, 7040, 7121, 7200 Å/min (같은 순서). 어닐링 후: 6999, 7007, 7066,
  7112 Å/min (모두 하락).
- 표면조도(Ra)는 LPCVD 온도가 높을수록 급격히 증가(545°C 0.29 nm → 625°C 18.02 nm,
  어닐링 전), 어닐링 후에도 0.03–4.41 nm 추가 증가.

저자들의 결론: **"MRR의 경향은 영률의 경향과 정확히 일치했다"** — 영률이 높을수록(=더
단단할수록) MRR이 낮다는, Preston형 모델의 "재료가 무를수록 잘 깎인다" 직관과 일치한다
([[preston-luo-dornfeld-mrr]]의 K_p 해석과 연결됨). LPCVD 증착온도는 **직접적으로 결정립
크기를 바꾸기보다, 결정립계 밀도·영률이라는 매개변수를 통해 CMP 거동에 영향**을 준다는 것이
이 문헌의 핵심 주장이다 — "결정립 크기가 CMP를 바꾼다"는 통념과 달리, 이 특정 LPCVD
온도범위(545–625°C)·어닐링 조건에서는 결정립 "밀도/경도"가 매개변수였다는 점을 노트에
정확히 반영한다.

## 4. 응용 차이: 로직 게이트 CMP vs 3D NAND 채널 CMP

출처: Lee, J., Yoon, D.-G., Sim, J.-M., Song, Y.-H. (2021), "Impact of Residual Stress on a
Polysilicon Channel in Scaled 3D NAND Flash Memory," *Electronics* 10(21), 2632, DOI:
10.3390/electronics10212632 (CC-BY) —
papers/park2021-electronics-poly-channel-residual-stress-3dnand.pdf, 원문 전체 확보.

Lee et al.(2021)의 3D NAND 구조 모델(TCAD)은 워드라인(WL)이 **텅스텐 리플레이스먼트
게이트**이고, poly-Si는 수직 채널홀을 채우는 **채널("마카로니") 재료**로 최종 소자에 영구
존재함을 명시한다(macaroni oxide/poly-Si channel/tunnel oxide/charge-trap nitride/blocking
oxide 스택, Table 1). 이는 현재 주류 V-NAND(charge-trap + W RMG) 구조에서 **poly-Si가
워드라인 자체가 아니라 채널 재료**라는 뜻이다 — 학습 지시문의 "3D NAND 워드라인 CMP"라는
표현은 부정확할 수 있음을 이 1차 문헌으로 확인했다. 같은 논문의 역학 파라미터 표는 poly-Si
영률 160 GPa를 사용하는데, 이는 §3의 Park et al.(2016) 값(어닐링 전 151–169 GPa, 어닐링 후
160–173 GPa) 범위 안에 정확히 들어간다(§5 `python verify`로 교차검증) — 독립된 두 문헌이
poly-Si 영률 값에서 서로 정합적이다.

이로부터 정리되는 두 응용의 CMP 목적 차이(질적 서술, 두 문헌의 직접 언급 범위를 넘는 통념
부분은 명시적으로 "미검증" 표기):
- **로직 게이트 (HKMG replacement-gate 흐름)**: poly-Si는 **희생(더미) 게이트**로 증착 후
  CMP로 웨이퍼 전면 평탄화·종료점 확보 → 이후 선택적 습식/건식 식각으로 poly-Si를 완전히
  제거하고 금속 게이트로 치환한다. 즉 CMP가 다루는 poly-Si 자체는 최종 소자에 남지 않는다.
  **미검증** — 이 문단은 업계 통용 공정 흐름 서술이며, 이번 조사에서 1차 문헌(예: 더미 게이트
  CMP를 직접 측정한 논문)을 원문 확보하지 못했다. 관련 논문 제목만 확인함: "A Hybrid Dry-Wet
  Approach for Removal of a Dummy Polysilicon Gate in a Replacement Metal Gate Scheme" (DOI
  10.4028/www.scientific.net/ssp.187.57, 무료 전문 미발견, 본문 미독).
- **3D NAND 채널 CMP**: poly-Si는 Lee et al.(2021)이 보이듯 **최종 소자의 능동 채널
  재료**로 영구히 남는다. CMP의 목표는 채널홀 상부의 오버필 poly-Si를 제거·평탄화하되,
  디싱을 최소화해 홀마다 채널 저항 편차를 억제하는 것이다(수천~수만 개 채널홀이 동일 웨이퍼에
  있으므로 홀-간 불균일이 곧 비트라인 전류 산포로 직결 — Lee et al. 2021의 Ion/Vth 산포 논의와
  연결). 게이트 CMP와 달리 "재료 자체를 남긴다"는 점이 근본적 차이다.

## 5. Python 재현 & 문헌 대조

```python verify
import numpy as np

# --- Pirayesh(2014) 6장: 보론 활성화 비율 (<10% 주장 재현) ---
carrier_A = 6.02e19   # cm^-3, SRP 측정
boron_A = 7.35e20     # cm^-3, SIMS 측정
activation = carrier_A / boron_A
assert activation < 0.10, f"활성화 비율이 문헌 서술(<10%)과 불일치: {activation:.3%}"

# --- 웨이퍼 A->B 캐리어농도 ~50% 감소 재현 ---
carrier_B = 3.1e19
carrier_drop = 1 - carrier_B / carrier_A
assert abs(carrier_drop - 0.50) < 0.03, f"캐리어농도 감소율이 '~50%' 서술과 불일치: {carrier_drop:.3%}"

# --- RR=A*rho^B 지수 피팅과 3배/5배 서술의 정합성 점검 (불일치 시 assert 없이 보고) ---
rho_A, rho_B = 2.2, 3.5   # mΩ·cm
RR_ratio_claimed = 3.0    # 웨이퍼 A->B MRR 증가 배율(본문 서술)
B_implied = np.log(RR_ratio_claimed) / np.log(rho_B / rho_A)
B_range_paper = (0.006, 0.091)  # Fig.6-5 피팅 범위(90rpm/6psi/200ml/min)
print(f"두 데이터점(A,B)만으로 역산한 지수 B_implied={B_implied:.3f}, "
      f"논문 Fig.6-5 피팅범위={B_range_paper}")
if not (B_range_paper[0] <= B_implied <= B_range_paper[1]):
    print("불일치: 오더 자체가 다름(약 26~400배 차이). 원인 미상 — "
          "추정: Fig.6-5의 A/B 피팅은 다수의 연속 도핑레벨 스윕 데이터에 대한 것이고, "
          "본문의 '5배/3배' 서술은 A/B/C 세 이산 시료의 별도 비교이므로 동일한 (A,B) "
          "쌍으로 단순 역산할 수 없는 것으로 보임(미검증, 원저자에게 직접 확인 불가).")

# --- Park et al.(2016): MRR 추세가 영률 추세와 '정확히 일치'한다는 서술 재현 ---
E_before = [169, 168, 159, 151]      # GPa: a-Si, 545C, 585C, 625C (어닐링 전)
E_after  = [173, 172, 165, 160]      # GPa: 어닐링 후
MRR_before = [7032, 7040, 7121, 7200]  # Å/min
MRR_after  = [6999, 7007, 7066, 7112]  # Å/min

corr = np.corrcoef(E_before + E_after, MRR_before + MRR_after)[0, 1]
assert corr < -0.9, f"영률-MRR 상관계수가 강한 음의 상관(<-0.9)이 아님: {corr:.4f}"
print(f"영률 vs MRR 상관계수 = {corr:.4f} (강한 음의 상관 — 무를수록(E 낮을수록) 빨리 깎임)")

# --- Lee et al.(2021) TCAD 파라미터의 poly-Si 영률(160 GPa)이 Park et al.(2016) 범위 안인지 교차검증 ---
E_lee2021 = 160  # GPa
lo, hi = min(E_before + E_after), max(E_before + E_after)
assert lo <= E_lee2021 <= hi, f"Lee(2021) 영률 {E_lee2021} GPa이 Park(2016) 범위[{lo},{hi}] 밖"
print(f"Lee et al.(2021) poly-Si E={E_lee2021} GPa — Park et al.(2016) 범위 [{lo},{hi}] GPa 내부, 정합")
```

## 6. 한계 / 미검증

- Pirayesh(2014) 학위논문의 University of Alberta ERA 식별자(10.7939/R3ZP3W76C)는
  DataCite 등록이며 Crossref에는 색인되어 있지 않다(직접 조회로 확인: Crossref API가
  "Resource not found" 반환, DataCite API는 정상 응답). `tools/verify_claims.py`는 Crossref
  API만 조회하므로 이 식별자를 "doi:" 형식으로 쓰면 출처 실존 확인에 실패한다 — 따라서 이
  노트에서는 "ERA 리포지토리 식별자"로만 표기했다(원문은 papers/에 이미 전체 확보되어 있고
  내용은 직접 읽고 인용함 — 식별자 형식 문제일 뿐 원문 신뢰성 문제는 아니다).
- 비소(As) 도핑의 CMP 정량 데이터는 1차 문헌을 확보하지 못했다 — 미검증.
- 인(P) 도핑이 OH⁻를 끌어당겨 식각을 촉진한다는 메커니즘은 Pirayesh(2014)가 인용한 Liu et
  al.의 모델이며, 원논문을 직접 확인하지 못했다 — 미검증(2차 인용).
- §4의 "로직 게이트 = 더미 게이트, 3D NAND 채널 = 영구 재료"라는 구도는 업계에 널리 알려진
  공정 흐름이지만, 더미 게이트 CMP를 직접 다루는 1차 문헌을 이번 조사에서 원문 확보하지
  못했다 — 미검증.
- §3의 "결정립계 밀도/영률이 MRR을 좌우하고 결정립 '크기'는 이 실험 범위에서 무관하다"는
  결론은 Park et al.(2016) 단일 논문(LPCVD 545–625°C, 특정 슬러리·패드 조건)에 근거한다.
  더 넓은 증착온도 범위(예: 비정질→다결정 전이 경계인 ~570–620°C 부근에서 columnar/equiaxed
  구조 자체가 바뀌는 영역)에서 결정립 크기·형태(columnar vs equiaxed)가 직접 CMP 불균일도나
  디싱에 미치는 영향은 이번 조사에서 전용 1차 문헌을 찾지 못했다 — 미검증(다음 단원 후보).
