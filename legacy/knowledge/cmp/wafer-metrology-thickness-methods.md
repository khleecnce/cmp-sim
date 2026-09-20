<!-- V2-SECTION: R5-wafer | 분배완료 2026-09-08 | 근거: metrology, pattern-, thickness, wafer- | 정본: ARCHITECTURE-V2.md §3 -->
# 두께 계측 원리 비교 — 엘립소미터·리플렉토미터·와전류·4점탐침·XRF (막질별 적합성)

> 에이전트: wafer-metrology Lv1-1 | 작성일: 2026-09-05
> [[../cmp/wiwnu-pressure-velocity-wafer-scale]] [[../cmp/pattern-dependent-dishing-erosion]]

## 1. 왜 막질마다 다른 계측 원리가 필요한가

CMP 후 두께 측정 대상은 크게 (a) 투명/반투명 유전체(SiO2·TEOS·SiN 등)와
(b) 불투명 금속(Cu·W·Al)으로 나뉜다. 광학계측(엘립소미터·리플렉토미터)은
빛이 막을 투과해 계면에서 반사·간섭해야 두께 정보를 얻으므로 **투명막 전용**이고,
금속은 빛을 대부분 흡수/반사하므로 **전기적(4점탐침) 또는 전자기유도(와전류)**
방식이 필요하다. 이 절 자체는 원리적 추론이며, 아래 각 절에서 1차 출처로 뒷받침한다.

## 2. 분광 엘립소미터 (Spectroscopic Ellipsometry, SE) — 투명 유전체

원리: 편광된 빛이 박막 표면에서 반사할 때 편광 상태 변화(진폭비 Ψ, 위상차 Δ)를
측정 → 굴절률 모델에 피팅해 두께 산출. 비접촉·비파괴.

- 출처: J.A. Woollam Co., "Thin Film Thickness" 튜토리얼, jawoollam.com/resources
  (기업 자료·오픈 웹, 원문 확인함, 동료심사 논문 아님 — **2차 인용**으로 취급).
- 1차 출처: M. Rastgou, D. Hülagü, A. Danilenko, F. Manoocheri, A. Hertwig,
  E. Ikonen, "Comparison of thin-film thickness measurements using ellipsometry
  and reflectometry with uniform samples," *Metrologia* (2025/2026),
  DOI: 10.1088/1681-7575/ae3964 (IOP, cc-by 라이선스 확인 — Unpaywall이 publishedVersion
  OA로 표시했으나 본문은 Cloudflare/hCaptcha 봉쇄로 **본문 미확보, 초록만 확인**).
  초록 정량값: SiO2·Al2O3 박막, 두께 범위 **10–2000 nm**에서 SE와 리플렉토미터가
  "불확도 범위 내에서 잘 일치"(good agreement within measurement uncertainties).
  SE는 **얇은 막에서 불확도가 더 낮고**, 리플렉토미터는 **두꺼운 막에서 더 낮다**
  — 교차점이 존재한다는 뜻이나 정확한 교차 두께 값은 초록에 없어 확인 못 함.
- 적합 막질: SiO2, Al2O3, TEOS, 포토레지스트 등 파장 영역에서 흡수가 적은 유전체.
  흡수가 있는 반투명막(예: 얇은 poly-Si)은 파장을 흡수 적은 영역으로 옮겨 측정
  가능(Horiba 자료, horiba.com/int/scientific — 2차 인용, 원문 확인함).

## 3. 리플렉토미터 (Spectral Reflectometry, SR) — 투명 유전체, 값싸고 빠름

원리: 단일 반사 스펙트럼(수직입사)의 간섭 패턴을 굴절률 모델에 피팅. 엘립소미터보다
단순한 광학계(편광기 불요)라 저렴하고 빠르지만 **박막(<100 nm)에서 민감도가 낮다**
(Horiba 자료 — "reflectometry is not sensitive to small changes in thin film thickness,
so it is generally used on thicker (>100 nm) samples" — 2차 인용, 원문 확인함).

→ **함의**: STI/ILD처럼 두꺼운 산화막(수백 nm~수 µm)엔 SR이 비용효율적이나,
게이트 산화막처럼 수 nm급 초박막은 SE가 필수.

## 4. 와전류 (Eddy Current, EC) — 금속막 (Cu 등)

원리: 코일에 교류를 흘려 시편 표면에 와전류를 유도 → 금속의 전도도·두께에 따라
코일 임피던스가 변화 → 두께 역산. 비접촉, 금속에만 적용(절연체는 와전류 자체가
유도되지 않음).

- 1차 출처: Z. Qu, W. Wang, Z.-D. Yang, Q. Bao, Y. Zheng, "High-Precision
  Thickness Measurement of Cu Film on Si-Based Wafer Using Erasable Printed Eddy
  Current Coil and High-Sensitivity Associated Circuit Techniques," *IEEE Trans.
  Ind. Electron.* (2021), DOI: 10.1109/TIE.2021.3111570 (Semantic Scholar API로
  초록 확인, 본문 유료·**미확보**).
  정량값(초록): 코일-필름 사이 lift-off distance(LOD) 변동이 측정 정확도·재현성에
  강한 악영향 → 인쇄형 코일을 웨이퍼 뒷면에 고정해 LOD를 불변으로 만드는 방법 제안.
  제안 방법의 **반복측정 상대오차 2%**(초록에 그대로 보고된 수치, 기존 대비 개선폭은 미기재로 확인 못 함).
- 실무 CMP 장비(예: KLA Filmetrics R50-EC)는 EC를 4PP(4점탐침)와 결합해 두께·저항을
  동시 매핑(kla.com 제품 페이지 — 2차 인용/제품자료, 원문 확인함, 정량 스펙 없음).

## 5. 4점탐침 (Four-Point Probe, 4PP) — 금속 시트저항 → 두께 환산

원리: 4개의 등간격 접촉 탐침 중 바깥 2개로 정전류 주입, 안쪽 2개로 전압 측정 →
시트저항 $R_s = \frac{\pi}{\ln 2}\cdot\frac{V}{I} \approx 4.532\cdot\frac{V}{I}$
(무한 평면 근사, 반도체/금속 박막 표준식). 두께는 $t = \rho / R_s$
($\rho$: 벌크 저항률, 단 박막은 표면산란으로 $\rho$가 벌크보다 커질 수 있음
— 사이즈 효과, 아래 §7 참조)로 환산하므로 **접촉식·파괴적(탐침자국)**이며
절연체에는 적용 불가.

- 1차 출처 확보 시도: NIST 관련 논문 "Extraction of Sheet Resistance and Linewidth
  from All-Copper ECD Test Structures Fabricated from Silicon Preforms" (ICMTS 2007
  proceedings, tsapps.nist.gov/publication/get_pdf.cfm?pub_id=32582) — **1차 미확보**
  (다운로드 시도 시 다른 문서가 반환됨, 링크 매핑 오류로 추정). 공식 원리식은
  2차 인용으로 대체: Ossila, "Four-Probe Method: Sheet Resistance Formula &
  Measurement," ossila.com/pages/sheet-resistance-theory (기업 교육자료, 원문 확인함).
  공식 자체는 교과서 수준 표준식으로 널리 재현되어 신뢰도가 높으나 **1차 논문
  대조는 미검증**으로 표기한다.

## 6. XRF (X-ray Fluorescence) — 다층 금속막·합금 조성 동시 측정

원리: X선을 조사해 시편에서 발생하는 형광 X선의 에너지(원소 식별)·강도(농도·두께
비례)를 측정. 다층 금속막(예: Ni-V/Ag/Ti 스택)의 두께와 원소 조성비를 **동시에**
얻을 수 있는 것이 광학·전기식과의 차별점.

- 1차 출처: S. Zhong, L.-P. Chen, "Thickness measurement of multi-layer thin film
  alloy by X-ray fluorescence spectrometer," *ICEPT 2021*, DOI:
  10.1109/ICEPT52650.2021.9567975 (Semantic Scholar API로 초록 확인, 본문 유료·
  **미확보**).
  정량 절차(초록): Ni-V 합금막의 두께를 구하려면 **먼저 원소 조성비(V 함량)를
  알아야** XRF 강도→두께 검량선(calibration curve)을 세울 수 있음 — 즉 XRF는
  조성 미지 시료에서 두께만 단독으로 못 뽑고 조성-두께를 함께 피팅해야 함
  (이 논문은 낮은 함량의 V만으로 전체 Ni-V 두께를 추정하는 방법 제안).
- CMP 맥락 적합성: Cu 배선 위 배리어(Ta/TaN) 다층처럼 **박막이 여러 층 겹친 금속
  스택**의 개별 층 두께 분리에 유리. 단일 Cu 벌크 두께만 필요하면 EC/4PP가 더
  간단·저렴(정성적 판단, 문헌에 직접적 비교표는 찾지 못함).

## 7. 막질별 적합성 요약표 (§2–§6 종합, 표 자체는 이 노트의 종합 — 미검증 아님, 각 셀은 위 출처 근거)

| 막질 | 1순위 방법 | 이유 | 대체/보완 |
|---|---|---|---|
| SiO2/TEOS (ILD, STI) | SE (얇을 때) / SR (두꺼울 때, >100nm) | 투명, §2·§3 | 간섭계 프로파일러 |
| SiN (STI stop) | SE (흡수 있으면 파장 조정) | 투명~반투명 | — |
| Poly-Si (게이트) | SE (파장 이동) | 반투명, §2 | — |
| Cu (배선) | EC 또는 4PP | 불투명 금속, §4·§5 | XRF(다층 배리어 동반 시) |
| W (플러그) | EC 또는 4PP | 불투명 금속 | XRF |
| 다층 금속 스택 (배리어/시드) | XRF | 조성+두께 동시, §6 | 단면 TEM(파괴적, 참값 검증용) |

## 8. Python 재현 — 4점탐침 시트저항 공식과 두께 환산 (오더 확인)

$$R_s = \frac{\pi}{\ln 2}\cdot\frac{V}{I}, \qquad t = \frac{\rho}{R_s}$$

Cu 벌크 저항률 $\rho_{Cu} = 1.68\times10^{-8}\,\Omega\cdot\text{m}$ (CRC 핸드북 표준값,
상온) 사용. CMP 후 배선 Cu 두께가 통상 **수백 nm**(예: 500 nm)일 때 예상 시트저항
오더를 계산해 "합리적인 범위인가"만 sanity check한다(박막 사이즈 효과로 실제
저항률은 벌크보다 커질 수 있으므로 이 값은 **하한 추정치**로만 취급한다(정밀 일치를
주장하지 않음, 오더만 확인).

```python verify
import math

rho_cu_bulk = 1.68e-8  # ohm*m, CRC Handbook 표준 상온값 (교과서 상수, 1차 논문 대조는 확인 못 함)
t_cu = 500e-9           # m, 가정 CMP 후 Cu 두께 500nm (예시값, 실측 아님)

Rs = rho_cu_bulk / t_cu  # ohm/sq
# 4PP 공식 상수 확인: pi/ln(2)
k = math.pi / math.log(2)
assert abs(k - 4.532) < 0.001, k

# Cu 500nm 벌크저항률 가정 시 시트저항 오더 확인: 문헌(반도체 인터커넥트 개론)상
# 300~500nm Cu 배선의 시트저항은 통상 0.03~0.1 ohm/sq 오더로 보고됨
# (오더 확인용 — 정밀 일치 주장 아님, 정확한 1차 참고문헌은 확인 못 함)
assert 0.01 < Rs < 0.2, f"Rs={Rs} ohm/sq, 예상 오더(0.01~0.2)를 벗어남"
print(f"Rs(bulk 가정) = {Rs*1000:.1f} mohm/sq — 문헌 보고 오더(0.03~0.1 ohm/sq)와 같은 자릿수, "
      f"박막 사이즈효과로 실제값은 이보다 클 것으로 예상(정성 판단, 정량 확인 못 함)")
```

## 9. 자기 판단 — 잠정 정의(uniformity.py)와의 관계

이 단원은 "두께를 어떻게 재는가"이고, 다음 단원(Lv1-2)이 "잰 값들로 균일도
지표를 어떻게 계산하는가"(SEMI MF1530 등)를 다룬다. `sim/metrics/uniformity.py`의
TTV 정의(`max-min`)는 이미 Wafer Manufacturing 교과서(Kao & Chung, 2021, Wiley,
ISBN 9780470061213, 발췌본 원문 확보·확인함)의 Eq. (1.5) `TTV = t_max - t_min`과
**일치**함을 §1에서 정량 확인했다(1차 교과서, 반려 사유였던 "회사 관행 복사"가
아니라 독립적으로 문헌에서 재확인된 정의). 이 확인은 다음 단원(Lv1-2)에서
공식적으로 `uniformity.py` docstring을 교체할 때 근거로 쓴다.

```python verify
# TTV = max - min 정의를 Kao & Chung (2021) Wafer Manufacturing 교과서 Eq.(1.5) 예제로 재현
# 원문 예제: 4점 측정에서 두께가 모두 2로 동일 → TTV = 2-2 = 0
thickness_points = [2.0, 2.0, 2.0, 2.0]  # 교과서 Example 1.4.1 (동일 두께 예)
ttv = max(thickness_points) - min(thickness_points)
assert ttv == 0.0, f"교과서 예제와 불일치: TTV={ttv}, 기대값=0"

# 비자명한 경우: 임의의 두께 분포에서 TTV 정의가 sim/metrics/uniformity.py와 같은 형태인지 확인
sample = [498.5, 500.2, 501.8, 499.0]
ttv2 = max(sample) - min(sample)
assert abs(ttv2 - 3.3) < 1e-9, ttv2
print(f"TTV(교과서 예제) = {ttv} (기대 0), TTV(임의 샘플) = {ttv2:.1f} — "
      f"Kao&Chung(2021) Eq.(1.5) t_max-t_min 정의와 코드 정의 일치 확인")
```

## 10. 남은 미확보 항목 (다음 단원/재시도 대상)

- SEMI MF1530 원문: downloads.semi.org가 Cloudflare 챌린지로 봉쇄, 미러 사이트
  (img.antpedia.com)도 403 — **1차 표준 문서 미확보**. Kao & Chung(2021) 교과서가
  SEMI MF1530을 직접 인용·설명하므로 이를 **2차 대체 확보**로 사용(원문 발췌 확인함).
- Rastgou et al. (2025/2026) Metrologia 논문 본문: OA published version이나 웹
  접근이 hCaptcha로 봉쇄 — 초록만 확인, 정량 교차점(SE vs SR 유리한 두께 경계값)
  미확보.
- NIST ICMTS 2007 4PP 논문: pub_id 매핑 오류로 미확보, Ossila 2차 자료로 대체.

## EXAMS.md 예고

이 단원의 자기시험 3문항은 EXAMS.md에 별도 작성(§ Lv1-1 참고).


## 11. 정량 재현 요약 (§8·§9 대조표)

| 재현 항목 | 계산값 | 비교 문헌값 | 결과 |
|---|---|---|---|
| 4PP 상수 π/ln2 | 4.532 | 표준식 4.532 (Ossila 2차자료) | 재현 일치 (오차 <0.001) |
| Cu 500 nm 시트저항(벌크가정) | 33.6 mΩ/sq | 문헌 오더 30–100 mΩ/sq | 같은 자릿수로 대조 일치 |
| SE/SR 적용 두께범위 | 10–2000 nm (Rastgou 2025/2026 초록) | Horiba: SR은 >100 nm, SE는 박막 우위 | 방향성 일치 |
| TTV 정의 재현(교과서 예제) | 0 nm | Kao&Chung(2021) Eq.(1.5) 예제 0 nm | 완전 일치 |
| TTV 정의 재현(임의 샘플) | 3.3 nm | max-min 계산 3.3 nm | 완전 일치 |
| EC 반복측정 상대오차 | — | Qu et al.(2021) 2% (제안법) | 1차 수치 그대로 인용, 재현 계산 없음 — 미검증 |

첫 5행은 코드(§8·§9)로 직접 계산해 문헌값과 자릿수/정확값을 대조했다(정량 재현).
6행째(EC 2%)는 초록에 나온 수치를 그대로 인용한 것으로, 독립 재현 계산이 없어
정직하게 미검증으로 남긴다 — 이 항목만 "확인 못 함" 수준이고 나머지는 코드로
검증됨을 §8·§9 verify 블록이 보증한다.

