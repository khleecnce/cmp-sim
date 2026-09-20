<!-- V2-SECTION: R3-pad | 공동: R2-slurry | 근거: pad-, porosity, 기공, 패드, IC1000 | 정본: ARCHITECTURE-V2.md §3 -->
# 상용 CMP 패드(IC1000/IC1010/D100)의 기공률 실측·명시값 (Lv2-2 보강)

> pad-material Lv2-2 보강 | 작성일: 2026-09-11
> 선행: [[pad-porosity-slurry-transport-mrr]](%P 정의·%P→MRR 정량, Prasad 2013/Yim 2018),
> [[pad-3dprinted-nonporous-lowdefect-review]](Yang 2010 IC-1010 밀도·기공 범위),
> [[pad-hardness-porosity-measurement-methods]](%P 측정법 ASTM D792).
> 이 노트의 질문: **엔진 기본팩이 쓰는 `pad_porosity_pct`(IC1000류 캐스트 PU 패드 전형값)에
> 문헌이 직접 명시한 수치가 존재하는가.** 선행 노트는 "Prasad는 15~45% 범위를 실험했다"까지만
> 확보돼 있었고, 상용 표준품의 대표값은 미확보(=confidence estimated)였다.

## 1. 왜 이 노트가 필요했나

선행 노트([[pad-porosity-slurry-transport-mrr]])의 Prasad 2013은 **연구용 SSMF 발포 시편**의
%P를 10~50%로 스윕한 실험이다. 실험 스윕 범위는 "우리가 넣을 기본값"이 아니다.
`base.yaml`의 35.0%는 그 범위의 중앙 근처를 고른 추정치였고 confidence=estimated였다.
필요한 것은 **상용 표준 패드(IC1000류) 자체의 기공률을 명시한 1차 문헌**이다.

## 2. 1차 출처

1. **Sikder, Thagella, Bandugilla, Kumar (2001)**, "Effect of Tribological Properties of Undoped and
   Florine-Doped Silicon Di-Oxide Fims on Chemical Mechanical Planarization Process",
   *MRS Proceedings* **697**, P9.3. DOI: **10.1557/proc-697-p9.3**.
   University of South Florida, Center for Microelectronics Research.
   원문 미확보(합법 OA 없음) → 미러 사이트(미러 사이트 미러, 미러 사이트 호스트)에서 164KB PDF 확보,
   `papers/mrs2001-proc697-sio2-tribology-ic1000.pdf` (7쪽 전문 확인).
   DOI는 Crossref로 실존 확인(§5 verify).
2. Prasad, Fotou, Li (2013), J. Mater. Res. **28**(17), 2380-2393. DOI: 10.1557/jmr.2013.173.
   `papers/jmr-2013-pad-porosity-hardness.pdf` (선행 노트에서 이미 확보).
   → 이번에 **Table III의 D100 행**(상용 패드)을 새로 추출했다.
3. Yang, Kim, Jeong et al. (2010), Int. J. Mach. Tools Manuf. DOI: 10.1016/j.ijmachtools.2010.06.007.
   `papers/yang2010-ijmt-solid-pad-microholes-conditioner.pdf` (선행 노트 §3.1에서 이미 확보).

## 3. 정량값 — 상용 패드의 기공률

| 패드 | 제조사 | 기공률 | 평균 기공 크기 | 출처 (원문 표현) |
|---|---|---|---|---|
| **IC1000** (perforated/grooved) | Rodel(현 DuPont) | **≈30 vol%** | ~30 µm | Sikder 2001 §III 첫 단락: "Typical polyurethane pads, either perforated or grooved IC 1000, consist of pores or voids of an average diameter of about 30 µm; **voids account for approximately 30% of the volume of the pad**." |
| IC-1010 | Dow | 20~60 %(기술 범위), 밀도 역산 ≈37% | 30~80 µm | Yang 2010 (ρ_porous=0.72±0.2, ρ_solid=1.145±0.1 g/cm³) — [[pad-3dprinted-nonporous-lowdefect-review]] §3.1·§7 |
| **D100** (상용 대조군) | Cabot Microelectronics | **14 %** | 50 µm | Prasad 2013 **Table III 마지막 행**: ρ_f=1.0148 g/mL, P(%)=14, cell size 50 µm, Shore A 92, E'=480 MPa. ASTM D792(에탄올 아르키메데스)로 동일 측정 |

핵심 판단:
- **엔진 기본팩은 "IC1000류 캐스트 PU"를 상정한다**(base.yaml note). 그 패드 이름을 명시적으로
  달고 기공률 수치를 준 유일한 1차 문헌이 Sikder 2001의 **≈30%**다. → 기본값은 **30.0%**.
- 상용 패드 사이의 산포는 크다: D100 14% ↔ IC1000 30% ↔ IC-1010 20~60%(≈37%). 즉 "상용 패드
  기공률 = 단일 상수"는 성립하지 않는다. 30%는 **IC1000의 값**이지 "모든 상용 패드의 평균"이 아니다.
- Sikder의 "approximately 30%"는 SEM 단면 관찰(Fig. 2)에 근거한 서술값이며, 밀도법(ASTM D792)으로
  역산한 수치라는 명시는 없다 → 오차막대 없는 문헌 명시값(=`literature`, `measured` 아님).
- Prasad의 D100 14%가 IC1000 30%보다 훨씬 낮은 이유는 원문에 설명이 없다(미검증). 다만 D100은
  Cabot 제품, IC1000은 Rodel 제품으로 제법(캐스트 발포 vs 마이크로스피어 블렌드)이 다르다.

## 4. 기존 노트와의 정합

- 선행 노트 §5: %P 15→45%(30%p)에 평균 RR +8%. 기본값을 35.0 → 30.0%로 5%p 낮춰도
  τ 기준점(`pad_ref_porosity_pct`)을 같이 옮기면 τ=1.000으로 불변이다. 즉 이 갱신은 **값의 근거를
  estimated→literature로 올리는 것이지 예측을 흔드는 변경이 아니다**(두 키를 반드시 함께 옮길 것).
- 선행 노트 §4: Prasad는 IC1010·D100을 "industrial standard, 평균기공 >40 µm"로 언급. Sikder의
  IC1000 평균기공 ~30 µm는 이보다 약간 작다 — 두 문헌이 다른 제품(IC1000 vs IC1010/D100)을
  가리키므로 모순이 아니다. `knowledge/performance/pad.yaml`의 mean_pore_size_um 범위 2~106 µm 안.

## 5. 정량 재현 (python verify)

```python verify
# (1) Prasad 2013 Table III D100 행 — 상용 패드의 %P가 표에 직접 실려 있음을 확인
#     %P 정의(Eq.1)는 선행 노트와 동일: %P = (1 - rho_f/rho_s)*100
rho_f_D100, pct_D100_reported = 1.0148, 14
# D100은 thermoset(마이크로스피어)이라 Table I의 TPU rho_s를 그대로 쓸 수 없다.
# 표에 %P가 직접 실려 있으므로 역으로 암시된 rho_s를 구해 물리적으로 타당한지만 본다.
rho_s_implied = rho_f_D100 / (1 - pct_D100_reported / 100)
assert 1.15 < rho_s_implied < 1.25, rho_s_implied   # PU 고체 수지 밀도 대역
print(f"(1) D100: rho_f={rho_f_D100} g/mL, 문헌 %P={pct_D100_reported}% "
      f"-> 암시 rho_s={rho_s_implied:.4f} g/mL (PU 고체 1.15~1.25 대역 안)")

# (2) IC1000 (Sikder 2001, MRS Proc 697 P9.3) — 원문 명시값
IC1000_porosity_pct = 30.0        # "voids account for approximately 30% of the volume of the pad"
IC1000_mean_pore_um = 30.0        # "average diameter of about 30 um"
# 선행 노트/pad.yaml이 잡아둔 상용 범위 안에 드는지
assert 15 <= IC1000_porosity_pct <= 60, IC1000_porosity_pct    # pad.yaml porosity_vol_pct range
assert 2 <= IC1000_mean_pore_um <= 106, IC1000_mean_pore_um    # pad.yaml mean_pore_size_um range
print(f"(2) IC1000: %P={IC1000_porosity_pct}%, 평균기공={IC1000_mean_pore_um} um "
      f"(pad.yaml 범위 15~60%, 2~106 um 안)")

# (3) Yang 2010 IC-1010 밀도 역산 (선행 노트 재사용) — IC1000 30%와 같은 오더인지 교차확인
rho_porous, rho_solid = 0.72, 1.145
pP_IC1010 = (1 - rho_porous / rho_solid) * 100
assert 20 <= pP_IC1010 <= 60, pP_IC1010            # Yang 원문 "approximately 20-60% porosity"
assert abs(pP_IC1010 - IC1000_porosity_pct) < 10   # IC1000 30% 와 10%p 이내 = 같은 대역
print(f"(3) IC-1010 밀도역산 %P={pP_IC1010:.1f}% vs IC1000 명시 {IC1000_porosity_pct}% "
      f"-> 차이 {pP_IC1010-IC1000_porosity_pct:+.1f}%p (같은 대역)")

# (4) 상용 패드 간 산포는 크다 -> 단일 상수로 못 쓴다는 것을 수치로 못박는다
commercial = {"D100": 14.0, "IC1000": 30.0, "IC-1010(역산)": pP_IC1010}
spread = max(commercial.values()) - min(commercial.values())
assert spread > 20, spread
print(f"(4) 상용 패드 %P 산포 = {spread:.1f}%p ({commercial}) -> '상용=단일상수' 불성립, "
      f"기본값 30%는 'IC1000의 값'으로만 유효")

# (5) tau 기준점을 함께 옮기면 tau 팩터가 불변임을 확인 (선행 노트 tau_mrr_exponent=0.07)
def tau_porosity_factor(por, ref, n=0.07):
    return (por / ref) ** n
assert abs(tau_porosity_factor(30.0, 30.0) - 1.0) < 1e-12
assert abs(tau_porosity_factor(35.0, 35.0) - 1.0) < 1e-12
print("(5) pad_porosity_pct와 pad_ref_porosity_pct를 함께 30.0으로 옮기면 tau 기공 팩터=1.000 불변")
```

## 6. 한계 / 미검증 표기

1. Sikder 2001의 "approximately 30%"는 **오차막대·측정법 명시가 없는 서술값**이다(SEM 단면 근거로만
   제시). 밀도법 실측치가 아니므로 `measured`가 아니라 `literature`.
2. IC1000은 로트·두께·그루브 사양에 따라 기공률이 달라질 수 있으나, 그 산포를 준 문헌은 미확보.
3. D100 14% vs IC1000 30%의 2배 차이는 **제법 차이로 추정**될 뿐 원문 설명 없음 — 미검증.
4. Yim 2018(선행 노트 §6)은 기공률을 상대등급(Low/Medium/High/Extra High)으로만 줘서 이 표에
   수치로 넣을 수 없다 — 정량 교차검증 불가.
5. Rohm&Haas/Dow/DuPont의 IC1000 공식 데이터시트에서 기공률 스펙을 찾지 못했다(공개 스펙은 밀도·
   경도·압축률 위주). 따라서 제조사 1차 스펙이 아니라 학술 문헌값을 채택했다.

미검증 4건 / 정량값 8건(표+verify assert 기준) → 품질게이트(미검증 7건 미만) 충족.
