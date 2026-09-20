<!-- V2-SECTION: R1-equipment | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: endpoint, epd, kinematic, platen, thermal | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 장비 — 종점검출(EPD)·툴 온도관리·슬러리 공급계

> 담당: tool-platen-head / tool-endpoint · 작성 2026-09-06 · 상태: 문헌(원문 확인)
> 연결: [[cmp-tool-architecture]] · [[wiwnu-pressure-velocity-wafer-scale]] · [[cmp-kinematics-rotary]] ·
> EPD 방식별 원리는 [[epd-optical-motor-friction-eddy-current-comparison]], 트레이스→제거량
> 역산은 [[epd-trace-removal-remaining-thickness-inversion]] 참고.
>
> 목적: `knowledge/components/tool.yaml` 의 endpoint / thermal / slurry_delivery 그룹 근거.
> 기존 `cmp-tool-architecture.md` 는 헤드·플래튼·링의 **기구**를 다룬다. 이 노트는
> 그 위에 얹히는 **센싱·열·유체 공급** 축을 채운다.

## 1. 종점 검출(EPD) — 방식별 원리와 적용 막질

CMP는 "얼마나 깎였는지"를 밖에서 볼 수 없으므로 EPD가 있어야 고정시간 연마의
over/under polish를 벗어난다. 실무에서 쓰이는 계열은 셋이다.

### (a) 마찰 기반 — 모터 전류/토크
플래튼 또는 캐리어 모터의 전류를 본다. 연마면이 무른 상층(Cu)에서 단단한 하층
(Ta 배리어, 산화막 stop)으로 넘어가면 **마찰계수가 바뀌고 그것이 모터 전류의 계단으로
나타난다**. 창(window)이 필요 없어 구조가 가장 단순하지만, 막두께 자체를 재는 게 아니라
**계면 전이만** 잡고, 막질 대비가 작으면 신호가 묻힌다.
- H.K. Li, X.C. Lu, J.B. Luo, "Motor Power Signal Analysis for End-Point Detection ..."
  (*Micromachines* 8(6):177, 2017) — 모터 전력 신호 EPD.
- STI(고선택비 슬러리) 모터전류 EPD: *Jpn. J. Appl. Phys.* 42:6396 (2003).

### (b) 광학 — 플래튼 창을 통한 반사/간섭
플래튼에 레이저·수광부를 묻고 **패드의 투명 window(폭 약 10 mm)** 를 통해 웨이퍼를 본다.
- 금속: 반사율 차이로 계면을 잡는다. 650 nm에서 Cu 0.943, Al 0.912, Ti 0.538, W 0.518,
  Ta 0.460 — Cu→Ta 전이에서 반사강도가 급락하는 것이 종점이다. 금속막은 **30~40 nm
  이하가 되면 투명해진다**(관통깊이 한계).
- 유전막: 반사가 아니라 **간섭**(투명막의 두께 주기)으로 실제 두께를 얻는다.
- 플래튼이 돌 때 창이 웨이퍼를 **호(arc) 궤적**으로 스캔하고, 한 바퀴 신호 안에
  웨이퍼 구간 / 리테이너링 구간 / 외부(패드) 구간이 나눠 보인다 → 반경별 프로파일과
  엣지 잔막까지 볼 수 있다. 스캔 반경은 $r=\sqrt{e^2+R^2+2eR\cos\theta}$ (e=헤드-플래튼
  중심거리) 로 기구학과 직결된다 — 우리 `center_offset_m` 와 같은 양이다.
- 출처: "Endpoint Detection Based on Optical Method in Chemical Mechanical Polishing",
  PMC10673209 / PMID 38004910 (오픈액세스, 12인치 툴 실장) — 위 수치·창 폭·궤적식 모두 본문 확인.
- T. Bibby, J. Adams, K. Holland, "Optical endpoint detection for CMP", *JVST B* 17:2378 (1999),
  doi:10.1116/1.590922 (초록 수준 확인).

### (c) 와전류(eddy current) — 금속 전용, 두께 실측
코일이 금속막에 와전류를 유도해 임피던스 변화로 **두께 자체**를 본다. 비접촉·저비용·
넓은 측정범위·오염 둔감이 장점. 단, **극박 금속이나 계면 식별 정확도는 광학보다 떨어지고**
슬러리·온도·환경에 영향을 받는다(PMC10673209 서론). **유전막에는 원리상 쓸 수 없다.**
- 스킨효과 기반 EPD: *Jpn. J. Appl. Phys.* 50:05EC09 (2011).
- 광학+와전류 통합: US 6,966,816 B2 (Applied Materials, "Integrated endpoint detection
  system with optical and eddy current monitoring") — 두 센서를 한 플래튼에 통합.

### (d) 그 외 (실시간성 약함)
마찰력, 패드 온도, 음향방출(AE), Cu 이온 농도 등은 보조 지표로 쓰이나 실시간 두께
모니터링에는 부족하다고 정리된다(PMC10673209 §1). 다센서 상관 접근:
Jeong et al., *CIRP Annals* 55(1):325 (2006), doi:10.1016/S0007-8506(07)60427-2.

**요약 표**

| 방식 | 측정량 | 적용 막질 | 한계 |
|---|---|---|---|
| 모터전류 | 마찰 전이 | 금속·STI(선택비 큰 계면) | 두께 아님, 대비 작으면 실패, window 불필요 |
| 광학 반사 | 반사강도 | 금속(Cu/W/Al→배리어) | 30~40nm 이하 투명화, 패드 window 필요 |
| 광학 간섭 | 실두께 | 투명 유전막(산화막·STI) | 불투명막 불가, window 필요 |
| 와전류 | 금속 실두께 | 금속 전용 | 유전막 불가, 극박막 정확도↓, 온도·슬러리 민감 |

## 2. 툴 온도 관리 — 왜 "냉각"이 공정 손잡이인가

CMP 계면의 열은 거의 전부 **마찰열**이다. White, Melvin, Boning (*J. Electrochem. Soc.*
150:G271, 2003, doi:10.1149/1.1560642)의 에너지 수지 계산에서 마찰 발열 **200~300 W**,
화학 발열 **약 1 W** — 두 자릿수 차이다. 즉 온도는 압력·속도(=마찰일률)의 결과이면서,
동시에 화학 반응속도를 지배하는 원인이 된다.

Shin et al., "Process Temperature Control for Low Dishing in CMP", *Materials* 18(19):4461
(2025), doi:10.3390/ma18194461 (오픈액세스, 본문 확인)의 실측:

- Cu / Ta / SiO₂ 제거율이 모두 **Arrhenius형** $RR = A\exp(-E_a/RT)$ 를 따른다.
- 활성화에너지: **SiO₂ 8.75, Ta 29.9, Cu 151.7 kJ/mol** (lnA = 9.7 / 18.1 / 66.3).
  → **Cu가 압도적으로 온도 민감**하고 SiO₂는 거의 둔감하다.
  → **온도가 곧 선택비 손잡이다.** 고온=Cu 선택비↑(돌출 제거), 저온=Cu 선택비↓(디싱 보상),
  중온=평탄 유지. 이 실험에서 균형점은 **30 °C**.
- 패드 열전도도는 ≈0.02 W/m·K로 매우 낮아 **표면 강제대류로 빼야** 한다. vortex tube
  기반 패드 냉각(공급 4.5 bar, 명목 냉각능력 180~730 W)으로 디퓨저 1단 통과 시
  30→27.5 °C, 2단 27.5→26.5 °C.
- 결과: 온도 미제어 시 디싱이 100 µm 패턴 +12 nm / 50 µm 패턴 +16 nm 증가.
  온도 제어 시 각각 **4 nm / 1 nm 미만**.
- 실험 조건(참고): 200 mm, POLI-500, 배리어 슬러리 H₂O₂ 0.5 wt%,
  **웨이퍼/리테이너링 압력 2/3 psi**, 패드 표면 온도는 웨이퍼 접촉 직후 IR 센서로 측정.

→ 시뮬레이터 함의: `pressure_psi × velocity` 로 마찰일률을 만들고, 그 열이 계면온도를
올리고, 온도가 막질별 $E_a$ 를 통해 MRR 선택비를 바꾸는 **닫힌 루프**가 성립한다.
현재 엔진에는 온도 축이 없다(base.yaml에 온도 키 없음) — tool.yaml thermal 그룹은
전부 `not_wired`로 둔다.

## 3. 슬러리 공급계 — 노즐이 WIWNU를 움직인다

Lee et al., "Approaches to Sustainability in CMP: A Review", *Int. J. Precis. Eng. Manuf.-
Green Tech.* (2021), PMC8617369 §"CMP 슬러리/패드" 본문 확인:

- WIWNU의 **가장 지배적 인자는 멤브레인 가압 균일도**이나, 그 다음으로
  **패드 평탄도와 슬러리 공급 방식**이 직접 영향을 준다.
- **스프레이 노즐**: 관(tube) 적하 대신 패드 위에 분무. 같은 조건에서 MRR은 높고
  WIWNU는 낮으며 **슬러리 유량을 21%·52% 절감**(Lee, Lee, Jeong, *JMST* 29:5057, 2015,
  doi:10.1007/s12206-015-1101-2).
- **주입 위치**: Liao et al.은 리테이너링 바로 옆에 초승달형 주입기를 두어 링의
  **leading edge 쪽에 신선한 슬러리**를 넣었다(*ECS Solid-State Lett.* 15(4):H118, 2012,
  doi:10.1149/2.009205esl). Araca SIS는 **다점 주입**으로 링 주위 bow wave 두께를 균일화.
- → 실무 축: 아암 반경 위치, 노즐 개수, 적하 vs 분무, 링 근접 주입 여부. 공급 유량만이
  아니라 **어디에 어떻게 넣는가**가 변수다.

리테이너링 형상도 이 문헌군에서 반복 지적된다:
- Park Y. et al., 링-패드 **접촉각**이 제거 균일도를 좌우, doi:10.1007/s12541-013-0204-x.
- Park J., Han, Kim, **금속 인서트 링의 단면 형상**과 멀티존 헤드 압력분포,
  *Applied Sciences* 10(23):8362 (2020), doi:10.3390/app10238362.
- 에어백형 캐리어의 압력분포 예측: Suzuki et al., *CIRP Annals* 66(1):329 (2017),
  doi:10.1016/j.cirp.2017.04.088.

## 4. 검증 재현 — Arrhenius 선택비 계산 대 문헌값 대조

Shin et al. (2025)의 활성화에너지(SiO₂ 8.75, Ta 29.9, Cu 151.7 kJ/mol, lnA=9.7/18.1/66.3)로
$RR=A\exp(-E_a/RT)$ 를 30°C(303.15K)와 26.5°C(299.65K, 2단 냉각 후 온도)에서 직접 계산해
문헌이 주장하는 "Cu가 SiO₂보다 훨씬 온도 민감하다"는 정성 주장을 대조·재현했다:

```python verify
import math
R = 8.314  # J/mol/K
species = {
    "SiO2": (9.7, 8750.0),
    "Ta":   (18.1, 29900.0),
    "Cu":   (66.3, 151700.0),
}
T_hi, T_lo = 303.15, 299.65  # K (30 C -> 26.5 C, 문헌 2단 냉각 조건)

def rr(lnA, Ea, T):
    return math.exp(lnA) * math.exp(-Ea / (R * T))

ratios = {}
for name, (lnA, Ea) in species.items():
    r_hi, r_lo = rr(lnA, Ea, T_hi), rr(lnA, Ea, T_lo)
    ratios[name] = r_hi / r_lo  # 냉각으로 RR이 몇 배 떨어지는가

# 정성 검증: Cu 활성화에너지가 가장 크므로 같은 온도 강하에도
# Cu의 RR 감소비가 SiO2보다 훨씬 커야 한다 (문헌: "Cu가 압도적으로 온도 민감").
assert ratios["Cu"] > ratios["Ta"] > ratios["SiO2"], ratios
# 대략적 크기 대조: Cu는 3.5 °C 냉각으로 RR이 20%+ 감소해야 한다(문헌 취지:
# 디싱 저감이 온도제어 하나로 12~16nm -> <4nm까지 됨은 Cu의 큰 Ea가 근거).
assert ratios["Cu"] > 1.20, ratios["Cu"]
# SiO2는 Ea가 작아 같은 냉각에도 몇 % 수준만 변해야 한다(둔감함의 정량 재현).
assert ratios["SiO2"] < 1.05, ratios["SiO2"]
print("RR ratio (30C/26.5C):", {k: round(v, 3) for k, v in ratios.items()})
```

실제 실행 결과(위 verify 블록, `python3` 직접 재확인): Cu RR비 ≈2.02(즉 26.5°C에서 Cu
제거율이 30°C의 약 절반으로 떨어짐), Ta ≈1.15, SiO₂ ≈1.04(4%만 변화) — 순서(Cu>Ta>SiO₂)와
문헌의 정성 주장(Cu 선택적 민감)이 방향적으로 일치한다. 단, **디싱 저감량
(12~16nm→<4nm)까지 정량 재현한 것은 아니다** — 그 수치는 dishing 모델(패턴 밀도·압력 분포 결합)
까지 필요해 이 노트 범위를 넘는다. 이 부분은 **미검증**으로 남기고, 위 activation-energy 비율
재현만 확인된 사실로 표기한다.

## 5. 미확인으로 남긴 것 (⚠ 조사 필요)

- 플랫폼 계열 비교(rotary vs orbital vs linear belt)의 **정량 장단점** — 원문 확보 실패
  (ScienceDirect 403). tool.yaml `platform.kinematic_type` 은 enum만 두고 성능 주장은 안 한다.
- 상용 툴(AMAT Reflexion, Ebara, KCTech)의 **플래튼 수·WPH 사양** — 제조사 페이지 403,
  공개 1차 자료 미확보. throughput 관련 필드는 전부 `unverified`.
- 플래튼 평행도/런아웃/진동의 **허용치 수치** — 공개 문헌에서 정량값 미확보.

## 출처
1. "Endpoint Detection Based on Optical Method in Chemical Mechanical Polishing", PMC10673209 / PMID 38004910. https://pmc.ncbi.nlm.nih.gov/articles/PMC10673209/ (오픈액세스, 본문 확인)
2. Y. Shin, J. Jeong, J. Shin, H. Jeong, "Process Temperature Control for Low Dishing in CMP", *Materials* 18(19):4461 (2025), doi:10.3390/ma18194461. https://pmc.ncbi.nlm.nih.gov/articles/PMC12525981/ (오픈액세스, 본문 확인)
3. H. Lee et al., "Approaches to Sustainability in CMP: A Review" (2021), PMC8617369. https://pmc.ncbi.nlm.nih.gov/articles/PMC8617369/ (오픈액세스, 본문 확인)
4. US 6,966,816 B2, "Integrated endpoint detection system with optical and eddy current monitoring", Applied Materials. https://patents.google.com/patent/US6966816B2/en (서지·분류 확인)
5. D. White, J. Melvin, D. Boning, *J. Electrochem. Soc.* 150:G271 (2003), doi:10.1149/1.1560642 (2번 문헌 경유 인용)
6. H.K. Li et al., "Motor Power Signal Analysis for End-Point Detection", *Micromachines* 8(6):177 (2017). https://www.mdpi.com/2072-666X/8/6/177 (서지만 확인, 본문 403)
7. J. Park, J. Han, C. Kim, *Applied Sciences* 10(23):8362 (2020), doi:10.3390/app10238362 (3번 문헌 경유 인용)
8. D. Lee, H. Lee, H. Jeong, *J. Mech. Sci. Technol.* 29:5057 (2015), doi:10.1007/s12206-015-1101-2 (3번 문헌 경유 인용)
9. X. Liao et al., *ECS Solid-State Lett.* 15(4):H118 (2012), doi:10.1149/2.009205esl (3번 문헌 경유 인용)
