# 배리어(Ta/TaN/Co) CMP와 Cu:배리어:옥사이드 선택비 (film-cu Lv2-2)

> film-cu Lv2-2 | 작성일: 2026-09-11
> 선행: [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Lv1-2 — Cu Pourbaix·BTA 패시베이션. 이 노트의 §2 pH 의존성이
> 그 열역학 경계를 그대로 쓴다) [[cu-dishing-erosion-density-step-height-model-tugbawa]] (Lv2-1 — dishing/erosion의 압력분배
> 모델. 그 노트 eq 3.19–3.30의 "배리어 클리어 단계"는 이 노트가 다루는 배리어:Cu:옥사이드 선택비가 r_b로 들어가는 자리다)
> 스코프: (1) 2단계 Cu CMP 공정에서 왜 배리어(Ta/TaN/Co) 전용 슬러리가 필요한가, (2) Ta/TaN 제거의 pH 의존 화학(패시베이션 막
> 정체·KIO3 산화제 정량 데이터), (3) 특허 청구범위로 본 배리어:Cu·배리어:옥사이드 선택비의 **설계 목표값**, (4) Co 배리어/라이너의
> 근본적 차이 — 갈바닉 부식과 부식전위 매칭, (5) 연마재 종류(실리카 vs 알루미나)가 선택비 방향을 바꾸는 정성 증거.

## 0. 출처 (4건, 1차 3건 + 특허 1건)

1. **[1차·원문 전체]** Y. Li, S. V. Babu, "Chemical Mechanical Polishing of Copper and Tantalum in Potassium Iodate-Based
   Slurries," *Electrochem. Solid-State Lett.* 4(2) G20–G22 (2001), doi.org/10.1149/1.1342185 (papers/li2001-kio3-cu-ta-cmp.pdf,
   fitz 텍스트 추출 전문 확보). 이 노트 §2의 pH·KIO3 농도별 Cu/Ta 제거율 수치는 전부 이 논문.
2. **[초록만]** H. Nishizawa, H. Nojo, A. Isobe, "Fundamental Study of Chemical–Mechanical Polishing Slurry of Cobalt Barrier
   Metal for the Next-Generation Interconnect Process," *Jpn. J. Appl. Phys.* 49(5) 05FC03 (2010),
   doi.org/10.1143/jjap.49.05fc03 (OpenAlex 초록 확인. IOP 원문은 2026-09-11 접근 시도 시 JS 챌린지·미러 사이트 전 미러
   404/챌린지로 본문 미확보 — 초록만). §4의 Cu/Co 선택비 0.5 수치는 이 초록에서 직접 인용.
3. **[초록만]** A. Vijayakumar, T. Du, K. B. Sundaram, V. Desai, "Selectivity Studies On Tantalum Barrier Layer In Copper
   CMP," *MRS Proceedings* 767, F6.3 (2003), doi.org/10.1557/proc-767-f6.3 (Unpaywall 경유 UCF STARS 리포지토리
   https://stars.library.ucf.edu/scopus2000/2107, 랜딩페이지 메타데이터 초록 확인 — 본문 PDF는 확보 못함). §5의 알루미나 vs
   실리카 연마재 선택비 반전은 이 초록의 서술.
4. **[특허·1차]** M. Grumbine et al. (Assignee: Rohm and Haas Electronic Materials CMP Holdings, Inc.), "Selective Barrier
   Metal Polishing Solution," US Patent 7,300,602 B2, filed 2003-01-23, issued 2007-11-27.
   https://www.freepatentsonline.com/7300602.html (청구항·명세서 전문, patents.google.com 미러 캡차로 FPO 경유).
   §3의 TaN:Cu·TaN:TEOS 선택비 하한값(≥3:1, ≥4:1)은 청구항 1·4를 그대로 인용.

## 1. 왜 배리어 전용 슬러리가 필요한가 — 2단계 공정의 구조

Cu 듀얼다마신에서 Ta/TaN(또는 Co) 배리어층은 Cu가 유전체로 확산하는 것을 막는다(US7300602 명세서 배경 §). [[cu-cmp-three-step-process-slurry-requirements]]에서
이미 다룬 벌크/소프트랜딩과 별도로, 벌크 Cu 제거가 끝나면 배리어를 옥사이드 위에서 완전히 걷어내는 **2단계 슬러리**가 필요하다(특허 원문:
"the polishing process uses a first-step slurry specifically designed to rapidly remove copper ... after the initial copper
removal, a second-step slurry removes the barrier material"). 이 단계의 화학적 요구가 앞 단계와 정반대인 이유는 두 가지다.

- **Cu 제거율은 낮아야 한다**: 배리어 아래 Cu 배선이 이미 노출돼 있으므로, 배리어를 깎는 시간 내내 Cu가 같이 깎이면 dishing이 커진다
  (특허 원문: "The metal removal rate should be very low to reduce dishing of the metal interconnects"). 이는 [[cu-dishing-erosion-density-step-height-model-tugbawa]]
  §1의 removal-rate diagram에서 배리어 클리어 단계(stage two, eq 3.19–3.30)가 pre-dishing d_cu를 남기는 것과 같은 메커니즘이다.
- **배리어 제거율은 옥사이드와 비슷하거나 통제 가능해야 한다**: 배리어를 너무 오래/빨리 깎으면 옥사이드 erosion이 커진다. 전통적으로
  알칼리~중성 슬러리가 Ta/TaN 제거율이 높다고 알려져 상용 2단계 슬러리는 중성~염기성이 많았지만(특허 배경), 산성 H₂O₂ 계열도
  가능하다는 것이 이 특허의 요지다.

## 2. Ta/TaN 제거의 pH 의존 화학 — Li & Babu 2001 정량 데이터

Li & Babu(2001)는 KIO3 기반 실리카 슬러리로 Cu·Ta 디스크(각 99.99%/99.95%)를 313 rpm급(선속 31.1 m/min), 압력 41.4 kPa(6.3 psi)에서
연마해 무게감소로 제거율을 측정했다(Struers DAP-V, Aerosil 130 실리카).

- **KIO3 농도 의존(pH 4.0, 3% 실리카)**: 연마재 없이는 Cu 용해속도가 선형분극법으로 5 nm/min 미만 — 순수 화학용해가 아니라
  기계적 마모가 제거를 지배한다는 근거. 연마재 있을 때 KIO3 농도가 늘수록 Cu 제거율이 급상승 후 ~150 nm/min에서 포화.
- **Ta는 반대 방향으로 반응**: KIO3 0%(DI수)에서 3% 실리카로 이미 77 nm/min이 나오지만, KIO3 0.5%를 넣으면 오히려 20 nm/min으로
  **떨어진다** — "harder pentoxide film"(Ta₂O₅) 형성으로 저자들은 해석한다. 즉 산화제가 Ta에서는 제거율을 낮추는 방향으로 작용할 수 있다.
- **pH 의존(2% KIO3, 3% 실리카)**: Cu 제거율은 pH 2.0의 약 450 nm/min에서 pH 8.0의 약 50 nm/min까지 **단조 감소**(저자들은 이를
  Cu 표면막의 보호능력이 산성에서 낮기 때문이라 설명 — [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §1의 Pourbaix 경계와
  일치: pH 2·4에서는 Cu 산화물이 열역학적으로 불안정). 반대로 Ta 제거율은 pH 2.0에서 사실상 0이다가 pH 10을 넘어서며 급상승해
  pH 12.0에서 약 215 nm/min에 이른다(OCP 측정으로 저pH일수록 더 귀한 방향 → 더 보호적인 막, 하지만 급격한 제거율 상승은 고pH에서
  막의 성질 자체가 물러지는 것으로 저자들은 추정, 원인은 불명확하다고 명시).
- **저자들의 결론적 관찰**: "같은 조건"(2% KIO3, 고pH, 3% 실리카)에서 Ta ≈ 215 nm/min, Cu ≈ 45 nm/min로, 이는 **배리어가 Cu보다
  빨리 깎이는 유리한 선택비**의 가능성을 시사한다(원문: "this offers the potential for a favorable polishing selectivity
  between the two"). §3의 verify 1에서 이 비를 계산해 특허 청구범위 하한과 대조한다.
- 저자들은 Cu(IO₃)₂ 막 가설(Luo 2000)에 회의적이다 — Cu(IO₃)₂의 Ksp(~9×10⁻⁸)가 Cu₂O의 Ksp(~4×10⁻³⁰)보다 22자릿수 이상 커서
  안정된 부동태막으로 작용하기 어렵다는 것이 근거(§3 verify 1에서 이 log비를 재현). **미검증**: 실제 막 조성은 XPS 등으로
  이 논문에서 확정되지 않았고, "duplex film" 가설로만 남는다.

## 3. Cu:배리어:옥사이드 선택비의 설계 목표 — 특허 청구범위

US7,300,602 B2(Rohm and Haas, 2007)는 실제 상용 2단계 슬러리 설계가 요구하는 **정량 선택비 하한**을 청구항에 명시한다. 조성은
산성(pH < 3, 청구항 2: pH 1.5–2.9) H₂O₂(0.1–10 wt%) + BTA(0.25–1.7 wt%, Cu 억제) + 콜로이드 실리카(<50 nm) + 계면활성제(Cu 제거율
추가 억제, 청구항 3)이며, 패드압 15 kPa 미만 조건에서:

- **청구항 1(넓은 범위)**: TaN:Cu 선택비 ≥ 3:1, **동시에** TaN:TEOS(옥사이드) 선택비 ≥ 3:1.
- **청구항 4(좁은 범위, pH 1.5–2.9로 한정)**: TaN:Cu 선택비 ≥ 4:1, TaN:TEOS 선택비 ≥ 4:1.

즉 목표는 배리어가 Cu와 옥사이드 **양쪽 모두보다** 최소 3–4배 빨리 깎이는 것이다 — Cu에 대한 선택비는 dishing 억제용, 옥사이드에
대한 선택비는 배리어 클리어 시간을 단축해 erosion 노출시간을 줄이는 용도로 읽을 수 있다(단, 이 특허 자체는 erosion 수치를 청구항에
명시하지 않는다 — **미검증**: 옥사이드 손실량과 선택비의 정량 관계는 이 특허에서 직접 주어지지 않고, [[cu-dishing-erosion-density-step-height-model-tugbawa]]의
배리어 클리어 단계 모델(eq 3.19–3.30)을 통해서만 간접 추론 가능하다). §2의 Li & Babu(2001) 데이터가 보인 Ta:Cu ≈ 4.8:1은 이 특허의
선택비 목표(3:1, 4:1) 범위와 같은 방향·같은 자릿수다 — 서로 다른 화학(KIO3 vs H₂O₂/BTA)에서도 "배리어가 Cu보다 수 배 빨리 깎여야
한다"는 설계 원칙이 반복된다는 교차 확인이다(§6 verify 2).

## 4. Co 배리어/라이너 — 근본적으로 다른 문제: 갈바닉 부식

Ta/TaN과 달리 Co는 Cu와 표준전위가 훨씬 가까운 금속이라 **갈바닉 커플**이 문제가 된다(Co가 Cu보다 덜 귀한 금속이면 Cu-Co 계면에서
Co가 우선 부식). Nishizawa et al.(2010)은 이 문제를 정면으로 다룬다 — 슬러리를 Cu와 Co의 **부식전위(corrosion potential)를
일치**시키도록 설계하면 갈바닉 부식을 억제할 수 있다는 것이 핵심 아이디어다.

- 산성 용액에서는 BTA를 넣어도 Co 표면에 부동태막이 형성되지 않았다(원문: Co의 억제제 화학이 Cu-BTA와 다르다는 뜻).
- 알칼리 용액에서는 Co 표면에 부동태막이 형성됐다.
- **pH 10 슬러리에서 Co의 부식전위가 Cu와 같아져** 갈바닉 부식이 일어나지 않는 조건을 확보했다고 보고한다.
- 이 조건에서 **안정적인 Cu/Co 제거율 선택비 0.5**를 얻었다(즉 Co가 Cu보다 2배 빨리 깎임, RR_Cu/RR_Co = 0.5).

이는 §3의 Ta 특허 목표(TaN:Cu ≥ 3–4:1, 배리어가 훨씬 빨리)와 방향은 같지만(배리어 > Cu) **크기가 훨씬 작다**(Co:Cu = 2:1
vs TaN:Cu ≥ 3–4:1) — Co 공정은 선택비 크기 자체보다 갈바닉 부식 회피가 1차 설계 변수이기 때문으로 해석된다. **미검증**: 이 초록만으로는
옥사이드에 대한 Co 선택비나 실제 슬러리 조성(오탈로타이저·억제제 화학종)을 확인할 수 없다 — 원문 미확보.

## 5. 연마재 종류가 선택비 방향을 바꾼다 — Vijayakumar 2003 (초록)

Vijayakumar et al.(2003, MRS Proceedings)은 Cu/Ta 선택비를 좌우하는 변수로 산화제·pH뿐 아니라 **연마재 종류**를 지목한다(초록
서술): 알루미나 기반 슬러리는 Cu를 잘 깎지만 Ta 제거율은 낮았고, 반대로 실리카 기반 슬러리는 Ta 제거율이 Cu보다 훨씬 높고 표면
평탄도(AFM)도 더 좋았다. 이는 Li & Babu(2001)가 실리카만으로 얻은 Ta > Cu 선택비 방향(§2)과 일치하며, 연마재 경도·화학이
선택비의 독립 조절 변수임을 시사한다. **미검증**: 이 초록에는 구체적 제거율 수치가 없어 정량 비교는 불가능하다 — 본문 PDF 미확보.

## 6. 검증

```python verify
import math

# --- Li & Babu 2001 (doi.org/10.1149/1.1342185) ---
# pH 의존 데이터: 논문 본문에 명시된 두 끝점만 사용 (중간값은 다른 Fig 조건이라 혼용하지 않음)
cu_ph2, cu_ph8 = 450.0, 50.0     # nm/min, Fig.3, 2% KIO3, 3% silica
ta_ph2, ta_ph12 = 0.0, 215.0     # nm/min, Fig.5, 2% KIO3, 3% silica
assert cu_ph2 > cu_ph8, "Cu 제거율은 pH 증가에 따라 단조 감소해야 한다"
assert ta_ph12 > ta_ph2, "Ta 제거율은 pH 증가에 따라 급증해야 한다"

# 저자들이 결론에서 제시한 "같은 조건" Ta/Cu 값으로 선택비 계산
Ta_rate = 215.0   # nm/min
Cu_rate = 45.0    # nm/min
selectivity_Ta_Cu = Ta_rate / Cu_rate
assert 4.5 < selectivity_Ta_Cu < 5.0, f"Li&Babu 결론 선택비 {selectivity_Ta_Cu:.2f}"

# Cu(IO3)2 vs Cu2O 용해도곱 비교 (논문이 Cu(IO3)2 부동태막 가설에 회의적인 근거)
Ksp_Cu_IO3_2 = 9e-8
Ksp_Cu2O = 4e-30
log10_ratio = math.log10(Ksp_Cu_IO3_2 / Ksp_Cu2O)
assert log10_ratio > 20, "Cu(IO3)2가 Cu2O보다 20자릿수 이상 더 잘 녹아야 부동태막으로 부적합하다는 논지가 성립"

# --- US7,300,602 B2 청구항 vs Li&Babu 결과 교차확인 ---
patent_TaN_Cu_min_broad = 3.0   # 청구항 1
patent_TaN_Cu_min_narrow = 4.0  # 청구항 4
assert selectivity_Ta_Cu >= patent_TaN_Cu_min_broad
assert selectivity_Ta_Cu >= patent_TaN_Cu_min_narrow * 0.9  # 좁은 범위 4:1에는 10% 이내로 근접(다른 화학이라 정확히 일치는 기대 안 함)

# --- Nishizawa 2010 (doi.org/10.1143/jjap.49.05fc03) Co 선택비, 방향성 교차확인 ---
nishizawa_Cu_over_Co = 0.5   # 초록에 보고된 값 (RR_Cu/RR_Co)
Co_over_Cu = 1.0 / nishizawa_Cu_over_Co
assert Co_over_Cu == 2.0
assert Co_over_Cu < patent_TaN_Cu_min_broad, (
    "Co:Cu 선택비(2:1)는 TaN 특허 목표(>=3:1)보다 작다 - "
    "Co 공정은 갈바닉 부식 회피가 우선이라 선택비 크기 자체는 더 작게 설계됨(미검증: 원문 미확보로 이유는 추정)"
)

print("selectivity_Ta_Cu(Li&Babu 2001) =", round(selectivity_Ta_Cu, 2))
print("Co:Cu selectivity(Nishizawa 2010) =", Co_over_Cu)
```

실행 결과: `selectivity_Ta_Cu(Li&Babu 2001) = 4.78`, `Co:Cu selectivity(Nishizawa 2010) = 2.0` — 모두 assert 통과.

## 7. 한계·미해결

- **옥사이드 제거율 자체는 이 노트 어느 출처에도 정량으로 없다**: 특허 청구항은 TaN:TEOS 선택비 하한(≥3:1, ≥4:1)만 주고 실제
  TEOS nm/min 값은 명세서 실시예에서 확인하지 못했다(FPO 페이지의 TABLE 1은 실리카 입자 스펙만 있었고 예시 제거율 표는 이번
  확보 범위에서 못 찾음) — **미검증**.
- Ta/TaN 구분: Li & Babu(2001)는 순수 Ta 디스크를 썼고, 실제 공정의 TaN(질화막)과 제거 메커니즘이 같은지는 이 노트에서
  확인하지 못했다 — **미검증**, Ta₂O₅ 부동태막 논리가 TaN에도 그대로 적용된다는 보장 없음.
- Co 초록(Nishizawa 2010)은 슬러리 조성을 전혀 명시하지 않는다 — 산화제·연마재 종류 모두 **불명**.
- [[cu-dishing-erosion-density-step-height-model-tugbawa]]의 배리어 클리어 단계 파라미터(r_b)에 이 노트의 선택비 수치를
  직접 연결하는 작업은 시뮬레이터 코드 변경이 필요해 이 노트 범위 밖이다 — PROFILE.md에 구현 요청으로 남긴다.
