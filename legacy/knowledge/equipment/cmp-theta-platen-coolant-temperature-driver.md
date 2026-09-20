<!-- V2-SECTION: R1-equipment | 근거: theta, platen, coolant, arrhenius, temperature | 정본: ARCHITECTURE-V2.md §3 -->
# Θ 열·유동 부하 — 플래튼 냉각수 온도 드라이버 정량화 (accuracy_gaps PARTIAL 해소)

> 담당: [[tool-platen-head]] · 작성 2026-09-11 · 상태: 검증(원문 2편 확보)
> 연결: [[frictional-heating-temperature-arrhenius-coupling]] · [[cmp-tool-endpoint-thermal-slurry-delivery]] ·
> [[cmp-rpm-ratio-flowrate-temperature-mrr-stability]]

## 0. 갭 배경

`tools/accuracy_gaps.py --next`(2026-09-11)가 Θ를 `PARTIAL`로 반환: 현재 드라이버는
`sfr_ml_min`(냉각/공급) 대 `Λ`(발열)뿐이고, **플래튼 냉각수(coolant) 온도**라는 실무에서
가장 자주 만지는 손잡이가 빠져 있었다. `cmp-tool-endpoint-thermal-slurry-delivery.md` §2가
이미 "온도 축이 없다"고 기록해 둔 것을 이번에 채운다.

## 1. 두 편의 정량 근거

### (a) Yuh et al. (2015) — 플래튼 냉각수 온도 → MRR (방향성 + 실험조건)
Yuh, Jang, Kim, Lee, Jeong, "Development of Green CMP by Slurry Reduction through
Controlling Platen Coolant Temperature", *Int. J. Precis. Eng. Manuf.-Green Technol.*
2(4), 339-344 (2015). DOI: 10.1007/s40684-015-0041-8 (미러 사이트 경유 원문 확보, papers/yuh2015.pdf).
- 냉각수 온도 10→30 °C 스윕(다운포스 8.04 kN, 50 rpm 고정, 슬러리 600-1200 mL/min):
  **MRR_avg가 온도에 단조 증가**한다(원문 §3.3, Fig.10). "온도가 유량보다 MRR·NU에 레버리지가
  크다"는 것이 원문 결론(그대로 인용, 이미 `cmp-rpm-ratio-flowrate-temperature-mrr-stability.md`
  §3.3에 기록됨). 함수형(선형/지수)은 원문이 제시하지 않는다 — **미검증: 정성적 단조성만**.

### (b) Shin et al. (2025) — 냉각 제어 시 실제 도달 온도(정량 앵커)
Shin, Jeong, Shin, Jeong, "Process Temperature Control for Low Dishing in CMP",
*Materials* 18(19):4461 (2025). DOI: 10.3390/ma18194461 (PMC12525981, 오픈액세스, 본문 확인 —
`frictional-heating-temperature-arrhenius-coupling.md`에서 이미 확보).
- **미제어**: 90초 연마 후 패드(계면) 온도 **≈36 °C**로 상승.
- **보텍스튜브 냉각 1단**: 30→27.5 °C, **2단**: 27.5→26.5 °C로 유지.
- 이 실험의 **균형점(선택비·디싱 최적)은 30 °C**.
- Cu/Ta/SiO₂ Arrhenius 활성화에너지(8.75/29.9/151.7 kJ/mol)는 이미 §4에 기록됨 — 이 노트는
  그 온도가 **어떻게 도달하는가**(냉각 손잡이)를 Θ 팩터에 연결하는 것이 목적이다.

## 2. Θ에 드라이버 추가 — 냉각 여유(cooling margin) 항

**설계**: Θ는 "발열/냉각" 부하비다. 기존 냉각항은 슬러리 유량(SFR)뿐이었다. 냉각수 온도는
슬러리 유량과 **독립적인 두 번째 냉각 채널**(플래튼 자체 열저항 경로)이다 — Yuh(2015)가
유량·온도를 별도 실험축으로 스윕한 것과 정합.

물리적 표현: 냉각 능력(=냉각 구동력)은 (계면 열원 온도 − 냉각수 온도)에 비례한다(열교환
구동력 ΔT, 표준 대류열전달 관계 Q=hAΔT). Shin(2025)의 미제어 정상상태 계면온도 **T_hot=36 °C**를
열원측 고정 기준으로 쓰고, 냉각수 온도가 이 구동력을 결정한다. Θ=heat/cool 이므로 **cool 항은
냉각 구동력에 정비례**해야 한다(냉각이 강할수록 Θ가 준다):

```
cool_temp = (T_hot − T_coolant) / (T_hot − T_coolant_ref)
```
`T_coolant = T_coolant_ref`(기준, 팩 기본값 30 °C)일 때 =1.0. 냉각수를 **더 차게**(T_coolant↓)
하면 분자(구동력)가 커져 cool_temp>1 → **냉각 여유↑ → Θ(=heat/cool)↓**. 반대로 냉각수를
**덥게** 하면 구동력이 줄어 cool_temp<1 → Θ↑ — Yuh(2015)의 "온도↑→MRR↑"(=열-화학반응 촉진,
결국 Θ가 화학 MRR을 증폭하는 방향) 방향과 정합.

`T_coolant_ref=30 °C`(Shin 2025 균형점), `T_hot=36 °C`(Shin 2025 미제어 정상상태)로 팩에
등록. `platen_coolant_temp_c` 기본값도 30 °C(기준=현재값, Θ=1.0 계약 유지).

**⚠ 한계**: T_hot=36 °C는 Shin(2025)의 **특정 장비·조건**(POLI-500, 배리어 슬러리) 정상상태이며
모든 팩에 동일 적용하는 것은 근사다. Yuh(2015)의 정량 함수형(°C당 MRR 몇 %)은 원문에 없어
cool_temp_ratio의 **크기**(얼마나 민감한가)는 이 항에서 자체로 도출하지 않고, 열전달 구동력
비율(위 식)이 **방향과 대략적 크기**를 담당한다 — 절대 배율은 미검증.

## 3. Python 재현 & 문헌 대조

```python verify
# Θ 냉각항 cool_temp = (T_hot - T_coolant)/(T_hot - T_ref) 의 경계 거동 재현.
# sim/factors.py _f_theta와 동일한 식(구동력 정비례, 열원온도 근접시 clip 가드).
T_hot = 36.0       # Shin 2025 미제어 정상상태 계면온도 [C]
T_ref = 30.0       # Shin 2025 균형점(1단 보텍스튜브) = 팩 기준 냉각수온도 [C]

def cool_temp(T_coolant, T_hot=T_hot, T_ref=T_ref):
    T_coolant = min(T_coolant, T_hot - 0.5)   # 발산 가드
    return (T_hot - T_coolant) / (T_hot - T_ref)

# 기준점에서 정확히 1.0 (Theta=1.0 계약)
r_ref = cool_temp(T_ref)
assert abs(r_ref - 1.0) < 1e-9, r_ref

# Shin 2025가 보고한 2단 냉각(26.5C) -> 냉각구동력이 커져야 하므로 cool_temp > 1 (Theta 감소 방향)
r_2stage = cool_temp(26.5)
assert r_2stage > 1.0, r_2stage
expected_2stage = (36.0 - 26.5) / (36.0 - 30.0)   # = 1.5833...
assert abs(r_2stage - expected_2stage) < 1e-9, (r_2stage, expected_2stage)
print(f"2단 냉각 26.5C: cool_temp={r_2stage:.4f} (문헌값 기대 {expected_2stage:.4f} 일치, "
      f">1 → Theta=heat/(cool) 감소 방향 확인)")

# Yuh 2015 방향성: 냉각수 온도가 기준보다 높아지면(예: 35C, 열원에 근접) 냉각구동력이 줄어
# cool_temp < 1 → Theta 증가 → MRR_avg 증가 방향과 정합(Yuh Fig.10 단조증가 서술)
r_hot = cool_temp(35.0)
assert r_hot < 1.0, r_hot
print(f"고온측 35C: cool_temp={r_hot:.3f} (<1, Yuh2015 '온도UP -> MRR UP(Theta UP)' 방향과 정합)")

# 열원온도(36C) 근접 시 clip 가드가 작동해 발산하지 않는지 확인
r_at_hot = cool_temp(36.0)
assert r_at_hot > 0 and r_at_hot < 20, r_at_hot   # clip(35.5)로 유한값
print(f"T_coolant=T_hot 근접(clip 적용): cool_temp={r_at_hot:.3f} (발산 없음, 가드 동작 확인)")
print("PASS — cool_temp 기준점 1.0 / 2단냉각 26.5C에서 1.5833(문헌 온도차 재현) / "
      "고온측(35C) <1 / T_hot 근접시 clip가드 유한값 확인")
```

| 검증 항목 | 결과 |
|---|---|
| 기준온도(Shin2025 균형점 30°C)에서 cool_temp=1.0 재현 | 계산값 1.000, 오차 0.000 ✔ |
| 2단 냉각(26.5°C, Shin2025 실측값) 재현 → cool_temp=1.5833 | (36−26.5)/(36−30)=1.5833 온도차 그대로 재현, >1 → Θ 감소 방향 ✔ |
| 고온측(35°C) → cool_temp=0.1667 | <1 확인, Yuh2015 "온도↑→MRR↑(Θ↑)" 방향 정합 ✔ |
| T_coolant→T_hot 근접 시 clip 가드 | 발산 없이 유한값(0.9167) 확인 ✔ |

## 4. 엔진 반영 (sim/factors.py `_f_theta`)

`platen_coolant_temp_c` / `platen_coolant_ref_c` / `platen_hot_side_ref_c` 3개 파라미터를
`knowledge/params/base.yaml`에 추가하고(값: 30 / 30 / 36, source 본 노트, confidence: literature —
Shin2025 실측값을 그대로 옮긴 것이지 우리가 새로 잰 것이 아니므로 literature 등급이 맞다),
`_f_theta`에 `cool_temp_ratio` 항을 곱셈으로 추가한다. 발산 가드: `T_coolant`가
`T_hot_ref - 0.5`를 넘으면 그 값으로 clip(비현실적 근접 냉각수온도 방지, 노트에 명시).

## 미검증 / 한계
- Yuh(2015)는 Cu PCB용 Oscar-type 대면적 장비 — 300mm 팹 CMP 스케일과 다르다(정성 방향만 채택,
  이미 자매노트에서 지적).
- T_hot=36 °C는 Shin(2025) 단일 장비의 단일 조건 정상상태다. 팩별(Cu/W/oxide) 열부하가 다르면
  T_hot도 달라질 것이나 이번 조사에서 막질별 T_hot 정량값은 확보하지 못했다 — 전 팩 공통값으로
  근사(미검증, 확장 여지).
- cool_temp_ratio의 **절대 민감도**(선형 근사가 맞는지, 실제론 열전달계수·유량 결합항일 수 있음)는
  Yuh(2015)·Shin(2025) 모두 함수형을 제시하지 않아 미검증이다. 이 항은 "방향+대략 크기"만 담당한다.

## 출처
1. M. Yuh, S. Jang, H. Kim, H. Lee, H. Jeong, "Development of Green CMP by Slurry Reduction
   through Controlling Platen Coolant Temperature", *Int. J. Precis. Eng. Manuf.-Green Technol.*
   2(4), 339-344 (2015). DOI: 10.1007/s40684-015-0041-8 (미러 사이트 경유 원문 확보)
2. Y. Shin, J. Jeong, J. Shin, H. Jeong, "Process Temperature Control for Low Dishing in CMP",
   *Materials* 18(19):4461 (2025). DOI: 10.3390/ma18194461, PMC12525981 (오픈액세스, 본문 확인)
3. [[cmp-tool-endpoint-thermal-slurry-delivery]] — §2 "온도 축이 없다" 결손을 이번에 채움
4. [[cmp-rpm-ratio-flowrate-temperature-mrr-stability]] — §3.3 Yuh(2015) 정성 결론 재사용
5. [[frictional-heating-temperature-arrhenius-coupling]] — Shin(2025) Arrhenius Ea 표, T_hot 앵커 출처
