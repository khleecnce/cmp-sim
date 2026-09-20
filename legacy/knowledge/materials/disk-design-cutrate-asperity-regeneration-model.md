<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: asperity-regeneration, cutrate, disk-, disk-design, 디스크 | 정본: ARCHITECTURE-V2.md §3 -->
# 디스크 파라미터 → 절삭율·asperity 재생 결합모델 (disk-design Lv3-2)

> disk-design Lv3-2 | 작성일: 2026-09-08
> 선행: [[disk-design-pad-roughness-asperity-relation]] (Lv2-2) [[../equipment/conditioner-grit-density-protrusion-cutrate]] (Lv1-2)
> [[../equipment/cvd-diamond-disk-patterned-grit-array]] (Lv3-1) [[../equipment/conditioner-grit-design-space]]
> 형제(다른 에이전트, 인용만·수정 안 함): [[../equipment/conditioner-disk-pad-cutting-model]]
> [[../equipment/conditioning-mechanism-asperity-regeneration]] [[../equipment/conditioner-asperity-population-balance]]
> 스코프: disk-conditioner 형제 에이전트가 이미 다룬 **일반 절삭·재생 프레임워크**(Evans-Marshall
> 마모율, Ring population balance PDE)는 재유도하지 않는다. 이 노트가 새로 하는 일은 그
> 프레임워크에 꽂을 **디스크 설계 파라미터(그릿 밀도 N, 크기 D, 활성 비율 f_a)의 정량 계수**를
> Lv1-2·Lv2-2·Lv3-1이 이미 확보한 1차 문헌 수치로부터 직접 회귀·교차검산하는 것이다.

## 1. 왜 이 단원인가 — 세 조각을 하나의 절삭율 함수로 묶기

지금까지 disk-design 트랙은 세 조각을 따로 확보했다: Lv1-2는 "그릿 밀도가 절삭율에 선형으로
기여한다"는 Feng(2007)의 **구조적 주장**(정확한 계수는 OCR 실패로 미확보), Lv2-2는 그릿
밀도·크기가 Ra·Rpk·λ에 미치는 **멱법칙 계수**(회귀 완료), Lv3-1은 활성 그릿 비율 f_a가
디스크 제조방식(전착/브레이징/CVD/SARD)에 따라 절삭율 방향을 바꾼다는 **정성 결론**이었다.
이 단원의 질문: **같은 1차 데이터(Kwon 2013, Tsai 2014, Pysher 2010)를 다시 열어, 절삭율을
그릿 밀도·활성 비율·크기의 명시적 함수로 회귀할 수 있는가, 그리고 Feng의 선형 가정은
실측과 맞는가.** 두 번째 축은 asperity 재생(regeneration) — disk-conditioner Lv3-1의 Ring
population balance PDE가 요구하는 "그릿 크기 → 재생된 asperity 분포 폭" 입력을, 이미 검증된
Pysher 멱법칙으로 교차검산한다.

## 2. 절삭율 결합모델 (1) — Kwon(2013) 동일 실험 내 CR·Ra·Rpk 동시 회귀

Kwon 2013(Tribology International 67, 272–277, doi.org/10.1016/j.triboint.2013.08.008,
[[disk-design-pad-roughness-asperity-relation]] §2.1에서 원문 확보·표 판독)는 **같은 3점
밀도 시리즈(17k/40k/60k grade 640)**에서 패드 절삭율(CR, 2h, µm/h: 37/23/19)과 Ra(8.05/6.8/5.95
µm)·Rpk(3.75/2.25/1.7 µm)를 동시에 보고한 유일한 출처다. 이 노트가 새로 하는 계산: 세 지표를
모두 밀도에 대해 회귀하고, **CR을 Ra·Rpk에 대해서도 직접 회귀**해 "표면통계가 절삭율의 대리
변수(proxy)로 얼마나 좋은가"를 정량화한다.

```python verify
# Kwon et al. 2013, Tribol. Int. 67, 272 (doi:10.1016/j.triboint.2013.08.008)
# 동일 밀도 시리즈(17k/40k/60k, grade 640) 3지표 동시 판독값
import numpy as np
N   = np.array([17e3, 40e3, 60e3])          # 그릿 개수/디스크
CR  = np.array([37.0, 23.0, 19.0])          # µm/h, 2h 패드 절삭율(본문 명시)
Ra  = np.array([8.05, 6.8, 5.95])           # µm, Fig.2a 판독(disk-design-pad-roughness-asperity-relation §2.1)
Rpk = np.array([3.75, 2.25, 1.7])           # µm, Fig.2b 판독

cN,   _ = np.polyfit(np.log(N),   np.log(CR), 1)
cRa,  _ = np.polyfit(np.log(Ra),  np.log(CR), 1)
cRpk, _ = np.polyfit(np.log(Rpk), np.log(CR), 1)
print(f"CR ∝ N^{cN:.2f}  (Feng 2007 구조적 가정: N^1, 선형)")
print(f"CR ∝ Ra^{cRa:.2f}")
print(f"CR ∝ Rpk^{cRpk:.2f}")

# R^2: CR을 Rpk로 설명하는 멱법칙의 적합도
logCR, logRpk = np.log(CR), np.log(Rpk)
p = np.polyfit(logRpk, logCR, 1)
pred = np.polyval(p, logRpk)
r2 = 1 - np.sum((logCR - pred)**2) / np.sum((logCR - logCR.mean())**2)
print(f"CR~Rpk 멱법칙 R² = {r2:.3f}")

# (a) 밀도 방향: 절삭율은 밀도 증가에 따라 "감소"해야 함(Kwon 본문 §3, 그릿당 하중 분산)
assert cN < 0, "밀도↑ → 절삭율↓ 방향이 Kwon 본문 결론과 어긋남"
assert -0.7 < cN < -0.35, f"밀도 지수 {cN:.2f}가 3점 회귀의 판독오차 범위(±0.15µm Ra 기준 환산) 밖"

# (b) Feng(2007)의 "CD(=절삭율 대리) ∝ n_g 선형" 구조적 가정과의 충돌
#     Feng는 방향(+)과 크기(지수=1)를 모두 주장하지만 Kwon 실측은 방향이 반대(-)다.
assert cN < 0 < 1.0, "Feng 선형가정(exp=1, 방향+)과 Kwon 실측(방향-) 비교용 assert"
print(f"Feng 가정(exp=+1) vs Kwon 실측(exp={cN:.2f}): 부호부터 불일치 — "
      f"Feng의 CD는 '총 슬라이딩 노출량'이고 Kwon의 CR은 '순 재료제거율'이라 서로 다른 물리량임을 시사")

# (c) CR~Rpk는 강한 멱법칙(지수 거의 1에 가까움, R² 높음) — Rpk가 절삭율의 좋은 기계적 대리변수
assert cRpk > 0.5, "Rpk 지수가 0.5 이하 — Kwon 결론('Rpk가 MRR과 가장 강한 상관')과 약하게만 일치"
assert r2 > 0.95, "CR~Rpk 멱법칙 적합도가 낮음 — 3점 회귀라 아주 좋아야 신뢰 가능"
print("OK: 밀도 방향 확인, Feng 선형가정과의 부호 불일치 확인, CR~Rpk 강한 멱법칙(R²>0.95) 확인")
```

(Kwon 2013) 문헌값 대조 실행 결과: CR ∝ N^−0.53(밀도 3.5배 증가에 절삭율 46% 감소), CR ∝ Ra^2.23, **CR ∝ Rpk^0.85
(R²=0.994)** — Rpk(봉우리 통계)가 절삭율과 거의 선형(지수 0.85)으로 움직이는 반면 Ra(평균
통계)는 훨씬 가파른 지수(2.23)로만 맞아, **Rpk가 밀도-절삭율 관계의 물리적 매개변수로서
Ra보다 우월**함을 같은 데이터 안에서 확인했다(Kwon 본문의 "Rpk가 MRR과 가장 강한 상관"이라는
정성 서술을 절삭율 자체에 대해 정량 재확인). Feng(2007)의 "CD(컨디셔닝 밀도, 절삭율의
운동학적 대리량) ∝ n_g 선형"이라는 구조적 주장([[../equipment/conditioner-grit-density-protrusion-cutrate]]
§2)은 Kwon의 실측(지수 −0.53, 부호 반대)과 정면으로 충돌한다 — **해석**: Feng의 CD는 "그릿이
그 반경을 스치고 지나간 총 궤적 길이"(접촉 기회의 총량)이고, Kwon의 CR은 "실제 깎여나간
패드 두께"(재료제거율)다. 그릿 수가 늘면 접촉 기회(CD)는 늘어날 수 있어도, 하중이 더 많은
그릿에 분산되어 그릿당 침투 깊이가 얕아지므로 순 재료제거율(CR)은 줄어든다 — **두 지표는
서로 다른 물리량이며 Feng의 CD를 절삭율(CR)의 대리로 그대로 쓰면 부호가 틀린다**는 것이
이 노트의 핵심 신규 발견이다.

## 3. 절삭율 결합모델 (2) — 활성 그릿 수만으로 설명되지 않는 PCR 증가: Tsai(2014) 재해석

[[../equipment/cvd-diamond-disk-patterned-grit-array]] §3(Tsai et al. 2014, DOI
10.1155/2014/913812)의 RCADD(그릿 10,000개, 방사·클러스터 브레이징+레벨링) vs CDD(25,000개,
종래)는 활성 팁 효율(스크래치 선 수/그릿 수)이 1.7%→4.8%로 2.8배 증가했다. §2에서 확인한
"절삭율은 활성 그릿 수(N_eff)에 좌우된다"는 가설이 맞다면, N_eff = f_a·N의 증가율이 PCR
증가율을 설명해야 한다.

```python verify
# Tsai et al. 2014 (DOI 10.1155/2014/913812) Fig.7a·Fig.8 문헌값
N_cdd, N_rcadd = 25000.0, 10000.0
lines_cdd, lines_rcadd = 432.0, 484.0        # 스크래치 선 수 = 활성 그릿 수의 대리(proxy)
Neff_cdd, Neff_rcadd = lines_cdd, lines_rcadd  # eff*N = lines 그 자체
pcr_cdd, pcr_rcadd = 24.0, 47.0              # µm/h, 1h

ratio_Neff = Neff_rcadd / Neff_cdd
ratio_pcr  = pcr_rcadd / pcr_cdd
residual   = ratio_pcr / ratio_Neff
print(f"N_eff(활성 그릿 수 proxy) 비 = {ratio_Neff:.2f}")
print(f"PCR 비 = {ratio_pcr:.2f}")
print(f"잔차(N_eff로 설명 안 되는 배율) = {residual:.2f}")

# N_eff 비만으로 PCR 비를 설명한다면 두 비율이 비슷해야 한다(단순 선형 가정 검정)
assert ratio_Neff < 1.3, "N_eff proxy 자체가 이미 크게 증가하면(>1.3배) 잔차 해석의 전제가 약해짐"
assert ratio_pcr > 1.7, "PCR '약 2배' 서술과 어긋남"
assert residual > 1.4, ("N_eff proxy 증가만으로 PCR 증가를 설명하기에 잔차가 충분히 크지 않음 — "
                        "'활성 그릿 수만이 절삭율을 결정한다'는 단순 가설이 기각되지 않음(재검토 필요)")
print("OK: N_eff 증가(1.12배)가 PCR 증가(1.96배)의 절반 남짓만 설명 — 잔차 1.75배는 "
      "레벨링(돌출 균일화)이 만드는 '그릿당 유효 침투 깊이' 증가로 추정(미검증)")
```

문헌값 대조 실행 결과: N_eff proxy(스크래치 선 수)는 1.12배만 증가했는데 PCR은 1.96배 증가 — **활성 그릿
수 증가만으로는 PCR 증가폭의 절반 남짓밖에 설명하지 못한다.** 남는 1.75배는 §2에서 확인한
"Rpk(≈그릿당 침투 깊이)가 절삭율을 좌우한다"는 관계와 결합해 해석할 수 있다: RCADD는 소형
디스크 24장을 금속 정반으로 **레벨링**해 조립했으므로([[../equipment/cvd-diamond-disk-patterned-grit-array]]
§3.1), 활성 그릿 수뿐 아니라 그 활성 그릿들의 **돌출 높이 균일성(=그릿당 유효 침투 깊이)**도
함께 오른 것으로 추정된다 — 단, 이 노트가 참고한 원문에는 RCADD·CDD의 돌출 높이 분포 실측치가
없어 **이 해석 자체는 미검증**이다(Tsai 2014 본문은 활성 팁 비율과 PCR만 보고, 돌출 높이
분포는 보고하지 않음). 즉 "활성 그릿 수(f_a·N)"와 "그릿당 침투 깊이(Rpk 대리)"는 **독립적인
두 축**이며, 절삭율 모델은 둘 다 필요하다 — 이는 disk-conditioner 형제 노트가 다루는
Evans-Marshall 마모율식(개별 asperity당 P_n·cot(ψ/2))의 P_n 항(그릿당 하중, §2의 침투 깊이에
대응)과 접촉점 수 항(N_eff)이 원래 분리되어 있다는 구조와 정합한다(참고만, 그 식 자체는
재유도하지 않음).

## 4. Asperity 재생모델 입력 — 그릿 크기 스케일링의 두 후보 지수 비교

disk-conditioner Lv3-1([[../equipment/conditioner-asperity-population-balance]])의 Ring
population balance PDE는 "컨디셔너가 만드는 정상상태 asperity 분포"를 그릿 크기 D_grit의
함수로 요구한다. 그 논문 Table 1(η=(1/D_grit)², σ=D_grit/2)은 지수 **1**(σ∝D_grit)을
가정하지만, [[disk-design-pad-roughness-asperity-relation]] §2.7·§3.4(c)가 이미 확인했듯
이 규칙은 Ring 논문 자기 표 안의 수치와도 10⁴배·12배 어긋난다(η) 정도의 문제였다. 이 노트는
같은 문제를 **지수 자체**의 관점에서 재확인한다: Pysher 2010(3M, DOI 10.1557/proc-1249-e02-04,
[[disk-design-pad-roughness-asperity-relation]] §2.2·§3.2에서 이미 surface finish ∝ D^0.57로
회귀됨, R²≈0.91)이 실측한 그릿 크기 지수 0.57을 Ring의 가정 지수 1과 직접 비교한다.

```python verify
# Ring et al. Table 1 가정: sigma ∝ D_grit^1
# Pysher 2010 실측 회귀(disk-design-pad-roughness-asperity-relation §3.2): surface finish ∝ D^0.57
import numpy as np
D_lo, D_hi = 45.0, 250.0        # µm, Pysher 2010 Fig.1 다이아 크기 범위(§3.2와 동일 데이터)
n_measured = 0.57               # Pysher 실측 회귀 지수(같은 데이터로 재확인됨, R²=0.91)
n_ring = 1.0                    # Ring et al. Table 1의 암묵적 지수(σ = D_grit/2)

ratio_measured = (D_hi / D_lo) ** n_measured
ratio_ring     = (D_hi / D_lo) ** n_ring
overpredict    = ratio_ring / ratio_measured

print(f"그릿 크기비 {D_hi/D_lo:.2f}배(45→250 µm)에서:")
print(f"  Pysher 실측 지수(0.57) 예측 σ 배율 = {ratio_measured:.2f}")
print(f"  Ring 가정 지수(1.0)   예측 σ 배율 = {ratio_ring:.2f}")
print(f"  Ring의 과대예측 배율 = {overpredict:.2f}배")

assert n_measured < n_ring, "실측 지수가 Ring 가정보다 작아야 '과대예측' 결론이 성립"
assert 1.8 < overpredict < 2.3, f"과대예측 배율 {overpredict:.2f}이 예상 범위(1.8~2.3배) 밖"
print("OK: Ring의 σ∝D_grit(지수 1) 가정은 3M 실측 멱법칙(지수 0.57)보다 "
      "5.6배 대 2.7배 오더로 약 2배 과대예측 — population balance PDE에 그대로 넣으면 "
      "그릿 크기 효과를 계통적으로 과장한다")
```

문헌값 대조 실행 결과: 45→250 µm(5.56배) 구간에서 Ring의 σ∝D_grit(지수 1) 가정은 σ가 5.56배 커진다고
예측하지만, 3M 실측 멱법칙(지수 0.57)은 2.66배만 예측한다 — **Ring의 지수-1 가정은 실측
멱법칙 대비 약 2.1배 과대예측**이다. 이는 [[disk-design-pad-roughness-asperity-relation]]
§2.7이 이미 지적한 절대값 불일치(η 10⁴배, σ 12배)와는 **다른 종류의 문제**(값이 아니라
지수 자체가 너무 크다)이므로, disk-conditioner Lv3-2/Cal 단계에서 population balance의 그릿
크기 입력을 만들 때 Ring의 D^1 대신 이 노트가 재확인한 **D^0.57(surface finish 대리)**을
1차 근사로 쓰는 편이 문헌 정합성이 높다 — 단, surface finish(3M 내부척도)가 σ(GW 지수분포
스케일)와 물리적으로 완전히 같은 양인지는 [[disk-design-pad-roughness-asperity-relation]]
§1.1이 이미 경고했듯 **미검증**이며, 여기서는 "그릿 크기 종속성의 지수 오더"만 빌려 쓴다.

## 5. 종합 — 절삭율↔재생 결합 제안 (이 노트의 합성, 문헌에 없음)

위 세 결과를 하나의 작업가설로 묶는다(**이 절 전체는 이 노트가 합성한 미검증 제안**이며
개별 구성요소만 문헌 회귀값이다):

```
CR(N, f_a, D)  ≈  CR_ref · (N/N_ref)^(-0.53) · (f_a/f_a,ref)^(g)  · h(D)
```

- 밀도 지수 −0.53: §2 Kwon 회귀(문헌값).
- 활성 비율 지수 g: §3에서 N_eff만으로 PCR 배율의 57%(1.12/1.96 ≈ 0.57배 몫)만 설명됨을
  확인했을 뿐, g 자체를 결정할 만한 독립 데이터점이 부족하다 — **g는 미확정, 캘리브레이션
  파라미터로 남긴다.**
- h(D): §4에서 재확인한 D^0.57 근사(surface finish 대리, 그릿 크기 → 재생 표면 통계). CR과
  D의 직접 관계가 아니라 σ(=asperity 재생 분포 폭)를 통한 **간접 경로**라는 점을 명시한다.

**재생 시간축과의 연결(정성)**: §2에서 확인한 CR∝N^−0.53(밀도가 높을수록 절삭율이 낮음)은
disk-conditioner 형제 노트([[../equipment/conditioner-disk-pad-cutting-model]] §3)가 도입한
PCR 지수감쇠 시상수 τ와 같은 축에 있다 — **절삭율이 낮은(밀도 높은) 디스크는 표면을 다시
깎아 정상상태 분포로 되돌리는 데(=asperity 재생) 더 오래 걸린다**는 것이 Cut Rate=Wear Rate
균형(Lawing 2004, [[../equipment/conditioning-mechanism-asperity-regeneration]] §1)의 직접
귀결이다. 이는 "밀도를 높이면 활성 그릿 수가 늘어 재생이 빨라질 것"이라는 순진한 직관과
반대이며, §2·§3의 정량 결과가 이 반직관적 결론을 뒷받침한다. **다만 τ 자체를 N의 함수로
피팅할 만한 독립 실측 데이터는 이번 회차에 확보하지 못했다 — 정성적 방향만 확정.**

## 6. 한계·미확보 (정직 기록)

- §5의 결합식은 이 노트의 합성이며 어느 1차 문헌도 이 형태로 제시하지 않는다. 밀도 지수(−0.53)만
  3점 회귀로 확인됐고, 활성 비율 지수 g와 CR-D 직접 관계는 **미확정**.
  Kwon 3점 회귀 자체도 3.5배 밀도 범위 안에서만 유효하며 외삽 금지.
- Tsai(2014)의 "활성 그릿 수" proxy는 스크래치 선 수(별도 아크릴 긁기 시험)이지 실제
  절삭 중 접촉점 수의 직접 측정이 아니다 — §3의 "레벨링이 침투 깊이를 늘렸다"는 해석은
  RCADD/CDD 돌출 높이 분포 실측이 없어 **미검증 추정**으로 남긴다.
- §4의 D^0.57(surface finish)을 σ(GW 지수분포 스케일)의 대리로 쓰는 것은
  [[disk-design-pad-roughness-asperity-relation]] §1.1이 명시한 "지표 혼재 금지" 원칙의
  예외적 차용이며, 지수 오더만 빌려 쓴다고 명시했다 — 절대값 대응은 하지 않는다.
- Feng(2007)의 CD 정확한 폐형식 수식은 여전히 미확보([[../equipment/conditioner-grit-density-protrusion-cutrate]]
  §1)이므로 §2의 "CD와 CR은 다른 물리량"이라는 결론은 Feng 논문 자체의 수식이 아니라
  이 노트의 정성적 해석(구조적 주장 vs Kwon 실측의 부호 비교)에 근거한다.
- 컨디셔너 절삭·웨이퍼 마모 두 접촉의 동시성(in-situ)은 이 노트에서 다루지 않는다
  ([[../equipment/conditioner-asperity-population-balance]] §4.3 "응용 3"의 영역).

## 7. 구현 요청

→ [[../../agents/disk-design/PROFILE]] "## 구현 요청" 절에 추가: (1) `CR(N, Rpk)` 회귀
계수(§2, N^−0.53 / Rpk^0.85)를 절삭율 모델 1차 근사로, (2) Ring σ∝D_grit(지수1) 대신
D^0.57 지수를 population balance 그릿크기 입력의 기본값으로 교체 제안(§4), (3) N_eff·Rpk
독립 2축 구조(§3)를 반영해 절삭율 모델이 단일 스칼라(활성 그릿 수만)로 축약되지 않도록
인터페이스 설계. 이 노트는 sim/에 직접 코드를 넣지 않는다.

## 8. 출처 (한 줄 형식)

- T.-Y. Kwon et al. (2013), Tribology International 67, 272–277, doi.org/10.1016/j.triboint.2013.08.008 — 원문 전체(Lv2-1 확보, 본 노트는 §2.1의 CR·Ra·Rpk 동시 판독값을 재사용).
- M. Y. Tsai et al. (2014), Mathematical Problems in Engineering 2014, 913812, DOI 10.1155/2014/913812 — CC-BY 전문([[../equipment/cvd-diamond-disk-patterned-grit-array]] §3에서 확보).
- D. Pysher, B. Goers, J. Zabasajja (2010), MRS Proc. 1249, doi.org/10.1557/proc-1249-e02-04 — 3M 공개 PDF([[disk-design-pad-roughness-asperity-relation]] §2.2/§3.2에서 확보, 본 노트는 회귀 지수만 재사용).
- Tyan Feng (2007), IEEE Trans. Semicond. Manuf. 20(4), 464–475, DOI: 10.1109/TSM.2007.907618 — 원문 확보([[../equipment/conditioner-grit-density-protrusion-cutrate]] §1, CD 구조적 선형 가정의 출처).
- T. A. Ring, A. Prasad, J. A. Dirksen (연도 미기재), 저자 공개 PDF https://my.che.utah.edu/~ring/Publications-PDFs/J-120.pdf — Table 1 σ∝D_grit 가정([[../equipment/conditioner-asperity-population-balance]] 경유).
- A. S. Lawing (2004), NCCAVS CMPUG 발표자료(공개 PDF) — Cut Rate=Wear Rate 균형 개념([[../equipment/conditioning-mechanism-asperity-regeneration]] §1 경유, 정성 인용만).
