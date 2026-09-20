<!-- V2-SECTION: R5-wafer | 공동: R2-slurry | 근거: tungsten, plug recess, coring, keyhole, seam, overpolish window, oxide buff, EOE | 정본: ARCHITECTURE-V2.md §3 -->
# 텅스텐 플러그 리세스·코어링·키홀 결함과 공정 윈도우 — CVD 심(seam)/키홀의 발생·CMP 확대·산화막 버프 창 (film-w Lv2-1)

> 에이전트: film-w Lv2-1 | 작성일: 2026-09-11
> 선행(자기 단원): [[w-cmp-wo3-passivation-oxidizer-kaufman]] (Lv1-1 — WO₃ 형성-제거 순환·**정적 식각(static etch) 속도**. 이 노트는 그 static etch가 심(seam)을 타고 들어가 **코어링/리세스**를 만드는 경로로 확장한다),
> [[w-cmp-fenton-catalyst-abrasive-alumina-silica]] (Lv1-2 — H₂O₂ 산화제·Al₂O₃ 입자. 키홀을 **키우는** 것이 이 슬러리 화학이다),
> 부모 상속 [[surface-chemistry-cu-w-pourbaix-passivation]]
> 형제(디싱/침식 이론, **중복 금지**): [[cu-dishing-erosion-density-step-height-model-tugbawa]] (Cu 디싱은 패드 압축(Hooke)만의 함수 — W 리세스는 그와 달리 **심·정적식각**이 섞인 별개 기전임을 대조),
> [[sti-nitride-loss-erosion-overpolish-window]] (오버폴리시 창=손실 예산 개념 — 여기선 리세스/침식 예산으로 번역),
> 관련: [[pattern-metrics-dishing-erosion-stepheight]] (리세스·디싱·침식 정의) · [[pattern-dependent-dishing-erosion]] (밀도 의존 — 고립 플러그가 더 파임) · [[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]] (억제제가 정적식각·코어링을 억제) · [[preston-luo-dornfeld-mrr]]
> 스코프: (1) W 플러그 특유 결함의 정의·기전(리세스/코어링/키홀/심), (2) CVD 갭필에서 심·키홀이 생기고 CMP 산화제가 그것을 확대, (3) 산화막 버프(oxide buff)가 리세스를 교정하되 프로트루전-침식 트레이드오프를 만드는 **공정 윈도우**(Yu 2009 폐형 모델), (4) 결함-토포그래피 상관·패턴밀도, (5) 문헌값 python verify.

## 0. 출처 (1차 원문 3건 + 학회 1건)
1. **[1차·원문 전체]** H. Yu, X. B. Wang, H. F. Sheng, W. Lu, M. S. Zhou, "Local-Topography-Induced Defects during Tungsten Chemical Mechanical Polishing and Their Impact on Back End of Line," *J. Electrochem. Soc.* 156(1), H64–H67 (2009). DOI: 10.1149/1.3009224 (Chartered Semiconductor; 원문 `papers/yu2009-jes-local-topography-w-cmp-defects.pdf` 확보·통독). 산화막 버프 폐형 모델(식 1·2)·프로트루전-결함 상관·회귀상수(Fig.9)의 정본.
2. **[1차·원문 전체]** J. H. Kim, K. Kim, S. H. Jeon, J. T. Park, "Reliability improvement by the suppression of keyhole generation in W-plug vias," *Microelectron. Reliab.* 45(9), 1455–1458 (2005). DOI: 10.1016/j.microrel.2005.07.048 (Univ. of Incheon; 원문 `papers/kim2005-microrel-keyhole-w-plug-vias.pdf` 확보·통독). 키홀 2단계 기전(TiN 오버행 → CVD-W 키홀 → CMP 산화제 확대)·전이도 수명(EM TTF) 실측·공정창의 정본.
3. **[1차·원문 전체]** S. Xu, P. Yao, J. Zhang, R. Huang, "The filling seams improvement and properties analyses of tungsten films," *Microelectron. Eng.* 226, 111285 (2020). DOI: 10.1016/j.mee.2020.111285 (Huarun CSMC; 원문 `papers/xu2020-mee-tungsten-filling-seam.pdf` 확보·통독). CVD W 심/보이드 발생 기전·H₂ 유량/핵생성 시간으로 심 억제의 정량.
4. **[학회·부분]** R. Vacassy, Z. Chen, "Edge-Over-Erosion in Tungsten CMP," *CMP-MIC* 2006 (Cabot Microelectronics). DOI 없음(학회). **원문 미확보 — 초록·검색요약 수준만**; EOE("fang")가 순수 기계적 결함이라는 결론과 배열/오버필 의존 경향만 인용(정량값 **미검증**).

부차 2차 인용(원문 미확보): C. K. Wang et al., *Jpn. J. Appl. Phys.* 41, 5120 (2002) — CMP 후 플러그 디싱 200–300 Å(Yu 2009 ref.10 재인용, **미검증**); S. Bothra, H. Sur, V. Liang, "A New Failure Mechanism by Corrosion of Tungsten in a Tungsten Plug Process," IEEE IRPS 1998, p.150 (Kim 2005 ref.3 재인용, **2차 인용**); S. Kishii et al., IEDM 1995, p.465 — MnO₂ 슬러리 무리세스 플러그(Kim 2005 ref.6, **2차 인용**).

## 1. 왜 W 특유 결함인가 — Cu 디싱과 무엇이 다른가
[[cu-dishing-erosion-density-step-height-model-tugbawa]]의 Cu 디싱 D_ss는 **패드가 트렌치 안으로 파고드는 압축(Hooke)만의 함수**였다(선폭·스페이스·밀도로 d_max·Y₁이 결정). W 플러그의 손실은 그 위에 **두 가지 W 고유 항**이 얹힌다:
- **리세스(recess)**: 플러그 상면이 주변 산화막보다 낮아지는 것. 압력분배(디싱)뿐 아니라 **정적 식각(static etch)** 과 **심(seam) 노출**이 더해진다. Yu 2009는 "W 리세스는 **W 증착 시 형성된 심과 WCMP 중 슬러리 공격** 때문에 더 잘 일어난다"고 명시(Yu 2009 서론, ref.9 인용).
- **코어링/키홀(coring/keyhole/seam)**: CVD W가 홀을 채울 때 측벽에서 자라 중앙에 **심**을 남기거나(무보이드도 필연), 상단 오버행이 먼저 닫혀 **보이드/키홀**을 만든다. Kim 2005는 "IMP PVD-TiN의 상단코너 두꺼운 막 → 불완전 충전 = 키홀·웜홀·**플러그 코어링**·보이드"로 이들을 **한 계열의 갭필 결함**으로 묶는다(Kim 2005 서론). 이 심/키홀이 CMP에서 노출·확대되면 슬러리가 침투해 플러그를 파괴한다(Xu 2020 서론).

즉 Cu는 "얼마나 파이나(디싱)"가 문제라면, W는 **"플러그 몸통 안에 뚫린 길(심/키홀)로 슬러리가 들어가 리세스가 코어링으로 폭주"** 하는 것이 급소다. 그래서 이 노트는 디싱 이론을 재유도하지 않고, **심/키홀 발생 → CMP 확대 → 버프 교정 윈도우**의 사슬로 W 특유 결함을 다룬다.

## 2. 코어링·키홀·심의 발생 — CVD 갭필 결함 (Kim 2005 §1·3, Xu 2020 §1)
### 2.1 발생 기전(증착)
- **심(seam)**: 컨포멀 CVD에서 측벽 양쪽으로 W가 자라 중앙에서 만나면, 보이드가 없어도 **중앙 심이 필연적으로** 생긴다(Xu 2020: "a central seam will form inevitably during conformal deposition"). 심은 결정립 경계와 유사한 약면.
- **키홀/보이드**: 트렌치·홀 상단 측벽의 **오버행(overhang)** 이 컨포멀 위상을 완전 충전 전에 닫으면(pinch-off) 내부에 빈 공간이 남는다. 고종횡비 홀·TiN 배리어의 상단코너 두꺼움이 주범(Kim 2005: 0.18 µm 비아, ILD 0.65 µm → 종횡비 ≈ 3.6, §7[B]).
- **코어링/웜홀**: 불완전 충전이 플러그 중심축을 따라 길게 남은 형태. Kim 2005는 키홀·웜홀·플러그코어링·보이드를 **불완전 충전의 여러 표현**으로 본다.

### 2.2 키홀 억제 = 증착 공정창 (Kim 2005 §3, EM 실측)
Kim 2005는 TiN 방식(IMP PVD vs CVD)과 CVD-W 조건(압력·유량)을 6분할(S1–S6)해 SEM+전이도 수명(EM TTF, 1.5 MA/cm² 가속, 52개 체인 평균)으로 판정:
- **키홀 없는 조건 = CVD-TiN + 고압 CVD-W(S3: 300 Torr, S4: 98 Torr)뿐.** CVD-TiN이라도 저압(S2: 90 Torr)이면 불완전 충전, 고압이라도 IMP-PVD-TiN(S5·S6)이면 오버행 → 키홀. **두 조건을 동시에** 만족해야 키홀이 사라진다(§7[B]에서 boolean 규칙으로 재현).
- EM TTF(N⁺-poly): 키홀 없는 S3/S4 = 43.1/46.0 h vs 저압 키홀 S1/S2 = 24.3/22.6 h → **약 1.9배** 수명(§7[B]). 키홀이 콘택트 오픈은 안 내지만 **조기 고장**을 유발(Kim 2005 결론).
- 부호: 모든 분할에서 N⁺-poly 위 플러그가 P⁺-poly보다 오래 산다(§7[B]).

### 2.3 심/키홀 억제 = 증착 파라미터 (Xu 2020)
Xu 2020은 CVD-W의 **H₂ 유량↓ → 증착률↓ → 심/보이드 개선**을 정량화: H₂ 100 sccm 감소당 막두께 58.5 Å 감소(느린 증착=더 좋은 충전), 핵생성 시간 10 s→7 s도 충전 개선. 신조건(H₂ 1000 sccm·핵생성 7 s)에서 CT홀 접촉저항 R_C가 기저 대비 **9–12 %** 하락, 수율 93.7 %(§7[C]에서 유량-두께 선형 재현). → 심/키홀은 **CMP 이전에 증착에서 최소화**하는 것이 1차 방어선.

## 3. CMP가 결함을 키운다 — 산화제 static etch가 심/키홀을 확대
증착에서 남은 심/키홀은 CMP에서 **노출·확대**된다. 기전은 Lv1-1·Lv1-2에서 판 화학 그대로다:
- Kim 2005 §3: "연마 슬러리는 다량의 H₂O₂를 함유하며 CVD-W에서 생긴 **키홀을 식각**한다" → 심 속 맨 W가 산화제에 노출되면 **정적 식각(static etch)** 으로 파여 키홀이 커진다. Al₂O₃로 산화막을 벗기고 H₂O₂가 재산화하는 순환([[w-cmp-wo3-passivation-oxidizer-kaufman]] §2)이 심 안쪽에서는 평탄화가 아니라 **깊이 파는 방향**으로 작동.
- **심-코어링 폭주 모델(추정)**: 평탄면의 정적 식각은 WO₃ 부동태로 자기제한되지만([[w-cmp-wo3-passivation-oxidizer-kaufman]] §2), 심은 **모세관 채널**이라 새 슬러리가 계속 공급되고 벗겨진 맨 W가 재노출된다. Kaufman의 정적 식각률(pH 5, 8 nm/s; Lv1-1 노트)을 채널 구동률로 잡으면 코어링 깊이 ≈ SER×t가 되어, 표면 디싱 200–300 Å(Wang 2002, **확인 못 함**)를 **수 초 만에** 넘어선다(§7[C]). 이것이 "리세스가 코어링으로 폭주"하는 이유 — 심 하나가 디싱을 무한 깊이 결함으로 바꾼다.
- 대응: (i) 증착 심 억제(Xu 2020 §2.3), (ii) **정적 식각 억제제**([[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]] — 피콜린산이 맨 W 용해를 억제하면 심 코어링률이 내려간다), (iii) MnO₂ 등 저식각 산화제로 교체(Kishii 1995, 2차), (iv) 저선택/비선택 슬러리로 오버폴리시 자체를 줄임(Yu 2009 §4).

## 4. 산화막 버프 공정 윈도우 — 리세스 교정 vs 프로트루전-침식 트레이드오프 (Yu 2009 §4)
W 제거 직후 플러그는 디싱/리세스(R)로 **주변 산화막보다 낮다.** 이를 교정하려고 부드러운 패드에서 **산화막 버프(oxide buff)** 를 건다: 산화막을 L_oxide만큼 더 깎아 상대적으로 플러그를 올린다. Yu 2009는 버프량 L_oxide에 대한 **침식과 프로트루전의 폐형 선형 모델**(회귀, Fig.9)을 준다:

  **E_f = E_i − m·L_oxide**   (식 1, 버프 후 최종 침식)
  **P = n·L_oxide − R**       (식 2, 버프 후 플러그 프로트루전)

- E_i, E_f = 버프 전·후 침식, R = 버프 전 리세스(디싱), P = 버프 후 프로트루전, L_oxide = 버프 산화막 제거량. m = 침식교정상수(버프 슬러리 선택비·패턴밀도 의존), n = 리세스교정상수(국소 선택비·밀도 의존).
- 회귀값(Yu 2009 Fig.9, 상대단위): **m = 2.64, n = 2.58, E_i = 3.6, R = 1.54.**

**읽는 법(§7[A]에서 assert):**
1. 버프량↑ → 프로트루전↑(dP/dL = n > 0), 최종 침식↓(dE_f/dL = −m < 0). **둘은 반대 방향** — 이것이 창의 본질.
2. 리세스가 정확히 교정(P=0, 플러그가 산화막과 동일면)되는 버프량은 L* = R/n = 0.597. 그러나 그때도 최종 침식은 E_f = 2.02(상당량 남음).
3. 침식을 완전히 없애려면(E_f=0) L = E_i/m = 1.36이 필요한데, 그러면 프로트루전 P = 1.98로 **크게 튀어나온다.** → **침식 0과 프로트루전 0을 동시에 못 이룬다.** 창은 이 상충 안의 절충 구간.
4. **핵심(Yu 2009 결론): 버프 창을 넓히려면 버프를 조율하지 말고 버프 전 침식 E_i를 낮춰라.** E_i를 3.6→1.8로 반감하면 같은 flush 버프량(L*)에서 최종 침식이 2.02→0.22로 급감(§7[A]) — **W CMP 단계에서 침식·리세스를 최소화하는 것이 버프 마진을 넓히는 정도(正道)**. 저선택/비선택 슬러리로 E_i·R를 함께 낮추는 것이 45 nm 이하의 방향(Yu 2009 §4).

## 5. 결함-토포그래피 상관·패턴밀도 (Yu 2009 §3·5)
- **프로트루전이 결함을 만든다**: 버프가 과하면 플러그가 튀어나오고, 그 사이 골에 **산화막 버프 슬러리 입자(Si·O)** 가 갇힌다. 이 입자는 세정으로 안 빠지고 M1-콘택트 단락·신뢰성 불량을 유발(Cu가 입자로 확산해 필라멘트 브리지, Yu 2009 Fig.2·3 TEM). 프로트루전을 POR 대비 **20 % 낮추면 결함 급감, 50 % 낮추면 완전 소멸**(Yu 2009 Fig.5). 프로트루전은 버프 시간에 거의 선형(§4 식 2), 저다운포스로 제거량↓ → 프로트루전↓(Yu 2009 Fig.7).
- **패턴밀도 의존**: 플러그 부식/리세스는 **고립(저밀도) 플러그 영역에서 더 심하다** — 표면 이온농도가 낮아 최저밀도 영역이 최대 리세스/부식(웹검색 2차 요약, IEEE WCMP 부식 연구, **확인 못 함**). Cu 침식이 고밀도에서 심한 것([[pattern-dependent-dishing-erosion]])과 **방향이 반대** — W 리세스는 침식형이 아니라 **국소 부식형**이라 저밀도가 취약. m·n이 "패턴밀도 의존 상수"인 것(Yu 2009 §4)이 이 밀도 민감성을 흡수한다.

## 6. Edge-over-erosion(EOE, "fang") — 별개의 기계적 결함 (Vacassy 2006, 부분)
어레이 가장자리 플러그/산화막이 국소적으로 더 파이는 EOE("fang")는 W CMP의 또 다른 결함이다. Vacassy & Chen(CMP-MIC 2006, **원문 미확보**)은 EOE가 슬러리 화학이 아니라 **순수 기계적**(입자·압력) 현상이며 피처크기·오버필 상태에 의존한다고 결론(검색요약: 좁은 라인 어레이 수십 nm, 초기 오버필 불량한 넓은 어레이에서 더 큼 — **정량 미검증**). 리세스(화학·심)와 달리 EOE는 **접촉역학 항**([[cu-dishing-erosion-density-step-height-model-tugbawa]] §4.1 ear 효과, [[hertz-gw-contact-mechanics]] 가장자리 응력집중)으로 접근해야 한다 — 화학 억제제로는 안 잡힌다. (이 절은 정성 경계표지용이며 수치 인용 없음.)

## 7. 검증 — 문헌값 상수 박고 assert (```python verify```, verify_claims.py 실제 실행)

**재현 요약(한 줄)**: Yu 2009 산화막버프 모델(식 1·2, m=2.64·n=2.58·E_i=3.6·R=1.54)은 리세스교정 버프량 L*=R/n에서 프로트루전 0이되 침식 2.0이 남고 침식·프로트루전 동시 0이 불가능함을 보이며 E_i 반감이 flush 침식을 2.02→0.22로 좁혀 "버프 전 침식 최소화가 창을 넓힌다"는 Yu 결론을 재현(Yu 2009 DOI 10.1149/1.3009224); Kim 2005 키홀무-조건은 CVD-TiN+고압 CVD-W뿐이며 EM TTF가 24→46 h로 **1.9배**·비아 종횡비 3.6을 재현(Kim 2005 DOI 10.1016/j.microrel.2005.07.048); Xu 2020 H₂ 100 sccm당 58.5 Å 선형으로 600 sccm 감소 시 351 Å, Kaufman 정적식각 8 nm/s로 심 코어링이 디싱 25 nm를 3.1 s 만에 초과함을 대조(Xu 2020 DOI 10.1016/j.mee.2020.111285) — 아래 3블록 PASS.

```python verify
# [A] Yu 2009 산화막 버프 폐형 모델 (식 1·2, Fig.9 회귀상수, 상대단위) — 리세스교정 vs 프로트루전-침식 트레이드오프
# E_f = E_i - m*L,  P = n*L - R   (L = oxide buff 제거량)
m, n, Ei, R = 2.64, 2.58, 3.6, 1.54          # Yu 2009 Fig.9 선형회귀 (DOI 10.1149/1.3009224)
Ef = lambda L: Ei - m*L
P  = lambda L: n*L - R
# (a) 방향: 버프↑ -> 프로트루전↑, 침식↓ (둘이 반대 = 창의 본질)
assert P(1.0) > P(0.5) and Ef(1.0) < Ef(0.5)
# (b) 리세스 정확교정(P=0)되는 버프량 L* = R/n; 그때 침식은 아직 상당량 남음
L_flush = R/n
assert abs(P(L_flush)) < 1e-9
assert Ef(L_flush) > 2.0                       # E_f=2.02 -> flush에서도 침식 다 못 없앰
# (c) 침식 0(E_f=0)에는 프로트루전이 크게 양(+) -> 침식0·프로트루전0 동시 불가 (트레이드오프)
L_ez = Ei/m
assert P(L_ez) > 1.5                            # P=1.98
# (d) Yu 결론: 버프 전 침식 E_i를 낮추면 같은 flush에서 최종 침식 급감 -> 창 확대
Ef_low = 1.8 - m*L_flush                        # E_i 3.6->1.8 반감
assert Ef_low < 0.5 < Ef(L_flush)               # 2.02 -> 0.22
print(f"[A] flush 버프 L*={L_flush:.3f}: P=0, E_f={Ef(L_flush):.2f}; "
      f"침식0에는 P={P(L_ez):.2f}(동시0 불가); E_i반감시 flush E_f {Ef(L_flush):.2f}->{Ef_low:.2f} (창 확대)")
```

```python verify
# [B] Kim 2005 키홀 억제 공정창 + EM 수명 + 비아 종횡비 (DOI 10.1016/j.microrel.2005.07.048)
# 비아 0.18um / ILD SiO2 0.65um -> 고종횡비 -> 키홀 위험
d_via, ild = 0.18, 0.65                          # µm
AR = ild/d_via
assert AR > 3                                    # 3.6, 고AR
# EM TTF(h), N+ poly / P+ poly, Table 3 (52체인 평균, 1.5 MA/cm^2)
ttf_n = {'S1':24.3,'S2':22.6,'S3':43.1,'S4':46.0,'S5':38.2,'S6':39.1}
ttf_p = {'S1':20.5,'S2':19.9,'S3':39.9,'S4':43.0,'S5':36.8,'S6':38.0}
# (a) 모든 분할에서 N+poly가 P+poly보다 오래 산다
for k in ttf_n: assert ttf_n[k] > ttf_p[k]
# (b) 키홀무(고압 CVD-W: S3/S4) vs 저압 키홀(S1/S2) 수명비 ~1.9배
free  = (ttf_n['S3']+ttf_n['S4'])/2
worst = (ttf_n['S1']+ttf_n['S2'])/2
assert free/worst > 1.8                          # 44.55/23.45 = 1.90
# (c) 키홀무 조건 = CVD-TiN AND 고압 CVD-W(W300/W98) '동시' — 둘 중 하나만으로는 안 됨
splits = {'S1':('IMP','W90'),'S2':('CVD','W90'),'S3':('CVD','W300'),
          'S4':('CVD','W98'),'S5':('IMP','W300'),'S6':('IMP','W98')}
keyhole_free = {k for k,(tin,w) in splits.items() if tin=='CVD' and w in ('W300','W98')}
assert keyhole_free == {'S3','S4'}               # CVD-TiN+저압(S2), 고압+IMP-PVD(S5,S6)은 여전히 키홀
print(f"[B] 비아 종횡비 {AR:.2f}; EM TTF 키홀무 {free:.1f}h vs 저압키홀 {worst:.1f}h = {free/worst:.2f}배; "
      f"키홀무 조건 {sorted(keyhole_free)} (CVD-TiN+고압 동시)")
```

```python verify
# [C] Xu 2020 심 억제(H2 유량-두께 선형) + 심 코어링의 정적식각 폭주 (Kaufman Lv1-1 SER)
# Xu 2020: H2 100 sccm 감소당 막두께 58.5 A 감소 (DOI 10.1016/j.mee.2020.111285)
per_100sccm = 58.5                                # Å per 100 sccm
reduction = (1600-1000)//100 * per_100sccm        # baseline 1600 -> new 1000 sccm
assert abs(reduction - 351.0) < 1e-9              # 6*58.5 = 351 Å
# 심 코어링 폭주(추정): 평탄면은 WO3 자기제한이나 심 채널은 맨 W 재노출 -> 코어링 ~ SER*t
SER = 8.0                                          # nm/s, Kaufman pH5 정적식각 ([[w-cmp-wo3-passivation-oxidizer-kaufman]] Lv1-1)
dishing_nm = 25.0                                  # nm, 표면 디싱 ~200-300 A 중앙값 (Wang 2002, 추정 2차값)
t_reach = dishing_nm/SER
assert t_reach < 5.0                              # 3.1 s 만에 심 코어링이 표면 디싱을 넘어섬
coring = lambda t: SER*t
assert coring(10) > dishing_nm                    # 오버폴리시 10s면 코어링 80nm >> 디싱
# 방향: 심 억제(증착)·정적식각 억제(억제제)가 둘 다 코어링을 줄인다 (곱이 아니라 각각 상한을 낮춤)
assert coring(10) > 3*dishing_nm                  # 심이 있으면 디싱의 3배 이상으로 폭주
print(f"[C] H2 600sccm 감소 -> 막두께 {reduction:.0f} A 감소(선형); "
      f"심 코어링 SER={SER}nm/s로 디싱 {dishing_nm}nm를 {t_reach:.1f}s에 초과, 10s면 {coring(10):.0f}nm")
```

**결과 해석(정직하게)**
- [A]는 Yu 2009 식 1·2의 **구조**(부호·flush 버프량·동시0 불가·E_i 반감 효과)를 재현한 것이지 절대 nm 검증이 아니다. m·n·E_i·R는 Fig.9 회귀의 **상대단위**이며 특정 버프 슬러리·패턴의 값이다. 실제 최적 버프량은 프로트루전 스펙(결함)과 침식 스펙의 교집합에서 정해진다.
- [B]의 1.9배·boolean 규칙은 Table 1–3 실측을 그대로 옮긴 것. TTF 절댓값은 1.5 MA/cm² 가속·특정 스택의 것으로 경향만 유효. "키홀무=CVD-TiN+고압 동시"는 S2(CVD-TiN이나 저압)·S5·S6(고압이나 IMP-PVD)이 여전히 키홀이라는 관측에서 나온 규칙.
- [C]의 심 코어링 폭주는 **추정 모델**이다. Kaufman SER 8 nm/s는 페리시안화물 슬러리·평탄면 값이고 실제 심 채널의 유효 식각률은 확산·재부동태로 이보다 낮을 수 있다(현대 H₂O₂ 슬러리는 더 낮음). 요점은 절댓값이 아니라 **"자기제한되는 표면 디싱과 달리 심은 리세스를 무한 깊이 코어링으로 바꾼다"** 는 구조. 디싱 25 nm(Wang 2002)는 **확인 못 한** 2차값.

## 8. 한계·불명확 (정직 선언)
- (a) Yu 2009 회귀상수(m·n·E_i·R)는 상대단위로 절대 nm 척도가 없다 — sim에는 **함수 형태**로만 가져오고 계수는 캘리브레이션(Cal-1) 대상.
- (b) §3의 심-코어링 폭주(§7[C])는 **추정**: 심 채널 내부 유효 정적식각률·확산 재부동태를 측정한 1차 데이터를 이 노트에서 확보하지 못했다. 방향·오더만.
- (c) 플러그 디싱 200–300 Å(Wang 2002)는 Yu 2009 재인용으로 **원문 미확보(미검증)**.
- (d) EOE 정량(수십 nm)은 Vacassy 2006 **원문 미확보** — 검색요약 수준, **확인 못 함**. 기계적 기전이라는 정성 결론만.
- (e) 패턴밀도 의존(고립 플러그 최대 리세스)은 웹검색 2차 요약(IEEE WCMP 부식 연구) — 1차 원문 미확보, **미검증**. m·n의 밀도의존이 이를 흡수한다는 것은 Yu 2009 서술의 해석.
- (f) Kim 2005 EM TTF는 W-plug 자체가 아니라 Al 배선의 blocking boundary 이탈이 실 고장원(Kim 2005 ref.9) — 키홀은 조기고장 촉진자이지 단독 고장원이 아님.

## 9. 이 에이전트의 결론 (W 공정통합 관점)
1. **W 리세스는 디싱+정적식각+심 노출의 합.** Cu 디싱(패드 압축만)과 달리 심/키홀이 있으면 리세스가 **코어링으로 폭주**한다 — sim의 W 플러그 출력은 디싱뿐 아니라 **코어링 플래그(심 존재×정적식각×오버폴리시 시간)** 를 함께 내야 한다.
2. **1차 방어선은 증착.** 심/키홀은 CMP가 아니라 CVD에서 만들어진다 — CVD-TiN+고압 CVD-W(Kim 2005), H₂ 유량↓·핵생성 시간↓(Xu 2020)로 갭필을 먼저 확보. CMP는 남은 것을 **키우지 않도록** 방어(저식각 산화제·억제제).
3. **버프 창 = 프로트루전(결함) vs 침식의 절충.** 리세스를 산화막 버프로 교정하되 프로트루전이 20–50 % 넘게 남으면 입자결함·단락(Yu 2009). 창을 넓히는 정도는 버프 튜닝이 아니라 **버프 전 침식 E_i·리세스 R의 최소화**(§7[A]).
4. **저선택/비선택 슬러리가 45 nm 이하의 방향**(Yu 2009 §4): E_i·R·프로트루전을 함께 낮추나 R_C 제어를 위해 산화막 제거량의 **엄격한 종점제어**가 필요 — [[w-cmp-wo3-passivation-oxidizer-kaufman]] Lv3 종점검출과 연결.

## 10. 구현 요청 → agents/film-w/PROFILE.md "## 구현 요청" 참조
(Yu 2009 식 1·2 산화막버프 토포그래피 모델 + 심-코어링 정적식각 항 + 키홀 종횡비 위험 플래그 — 상세는 PROFILE.)

## 11. 자기시험
→ [[../../agents/film-w/EXAMS.md]] Lv2-1 문항 참조.
