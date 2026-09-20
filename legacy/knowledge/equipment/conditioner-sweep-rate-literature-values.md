<!-- V2-SECTION: R4-disk | 근거: conditioner, sweep, cpm, 컨디셔너, 스윕 | 정본: ARCHITECTURE-V2.md §3 -->
# 컨디셔너 스윕 왕복수(sweep rate, cpm) — 1차 문헌 실측 레시피값 수집

> disk-kinematics 파라미터 앵커 노트 | 작성일: 2026-09-11
> 선행: [[conditioner-sweep-kinematics-pcr-profile]] (Zheng 2023 운동학 4중회전 모델, 하중·RPM만 표로 제시),
> [[disk-sweep-recipe-flattening-baisie2010]] (세그먼트 체류시간 프로파일 최적화),
> [[conditioner-sweep-algorithm-trajectory-density]] (반환점 밀도발산).
> 이 노트의 질문 하나: **`cond_sweep_cpm`에 넣을 숫자가 실제 문헌 레시피에 있는가, 있다면 몇인가.**

## 1. 왜 이 단원이 필요한가 — 기존 노트의 공백

[[conditioner-sweep-kinematics-pcr-profile]]는 스윕 **운동학**(β(T) 사인파 궤적식, Eq.4)은 완전히
확보했지만, 그 식에 들어가는 `n_a`(스윕 속도)의 값은 Zheng et al. Table 1 한 줄(19 RPM)뿐이었다.
[[disk-sweep-recipe-flattening-baisie2010]]은 세그먼트 **체류시간 비율**(무차원)만 다루고 절대
왕복수는 다루지 않는다. 그 결과 `cond_sweep_cpm = 10.0`은 "상용 툴 범위의 대표값 추정"으로
`unverified` 상태였다.

이 노트는 **fab-sim `papers/` 코퍼스 190편 전수 grep + 신규 확보 2편**으로 "분당 왕복수"가
명시적 수치로 적힌 실험 레시피만 뽑아 표로 만든다. 추정·환산 없이 원문 표현 그대로 인용한다.

## 2. 1차 출처 — 스윕 왕복수가 숫자로 명시된 레시피 (원문 표현 그대로)

| # | 출처 | 툴/패드 | 원문 표현 | 값 (cpm) | PDF 확보 |
|---|---|---|---|---|---|
| 1 | **Menk et al. (2010)**, "Real-Time Control System for Improved CMP Pad Profiles", MRS Proc. 1249, E02-02, DOI 10.1557/PROC-1249-E02-02. Applied Materials. | AMAT 300 mm ILD, platen 93 rpm, carrier 87 rpm, 컨디셔너 head 95 rpm / 9 lb | "The sweep rate was **19 sweeps per minute**, with a sweep range of 1.7 to 14.7 inches divided into 13 equidistant zones." | **19** | `papers/menk2010-real-time-control-pad-profiles.pdf` (기존) |
| 2 | **Zheng, Zhao & Lu (2023)**, *Micromachines* 14(9), 1683, PMC10536193 (OA). Tsinghua. | Hwatsing Universal-300-Plus 12인치, 패드 100 RPM, 디스크 73 RPM, 4 lbf | Table 1: "Conditioner arm sweep speed **19 RPM**", sweep mode Sinusoidal, range radial 83~308 mm | **19** | `papers/mi14091683-fulltext.xml` (기존) |
| 3 | **Kim & Kang (2011)**, *Int. J. Machine Tools & Manuf.* 51, 565–568, DOI 10.1016/j.ijmachtools.2011.02.008 | 300 mm 산화막, platen 93 rpm, head 87 rpm, 컨디셔너 6 lb | "…head speed of 87 rpm, **sweep speed of 15 times/min**, and slurry flow rate of 150 ml/min" | **15** | `papers/kim-kang2011-ijmtm-cvd-diamond-coated-conditioner.pdf` (기존) |
| 4 | **McAllister et al. (2019)**, *Micromachines* 10(4), 258, DOI 10.3390/mi10040258 (CC-BY) | IC1000 K-groove, platen 87 / 디스크 60 RPM, ABT·EHWA 디스크 | "the conditioner swept across the pad **13 times per minutes**" (break-in 및 in-situ 동일 레시피) | **13** | `papers/mcallister2019-conditioner-type-microtexture-sio2-micromachines.pdf` (기존) |
| 5 | **McAllister (2019) 학위논문** (Univ. of Arizona), Ch. 5 (Saesol 4DNS80AMC1, IC-1000 XY-groove, platen 80 / 디스크 70 RPM, 6.75 lbf) | | "the conditioner swept across the pad **13 times per minutes**" | **13** | `papers/mcallister2019-dissertation-ua.pdf` (기존) |
| 6 | 같은 학위논문, 다른 장 (3M PB32A **브러시** 컨디셔너, 66→361 mm, 1.4 kgf, platen 50 / 디스크 95 RPM) | | "sweeping from 66 to 361 millimeters from the pad center **11 times per minute**" | **11** | 동상 |
| 7 | 같은 학위논문, 또 다른 장 (Shinhan CCH212 CVD 디스크, platen 63 / 디스크 95 RPM, 5.7 lbf) | | "with the conditioner sweeping across the pad **10 times per minutes**" | **10** | 동상 |
| 8 | **Liao (2014) 학위논문** (Univ. of Arizona), Ch.4·Ch.7 등 4개 실험 (Araca APD-800, IC1000/IC1010, 3M A2810 및 MMC TRD 디스크, 26.7~44.5 N) | | "The disc rotated at 95 rpm and swept **10 times per minute** across the radius of the pad." (4회 반복 등장) | **10** | `papers/liao2014-dissertation-ua-consumables.pdf` (기존) |
| 9 | **Mariscal et al. (2020)**, *ECS J. Solid State Sci. Technol.*, DOI 10.1149/2162-8777/ab89bc | STI CMP, 6 lbf | "The conditioner rotated at 95 RPM while sweeping **10 times per minute** across the pad surface" | **10** | `papers/mariscal2020-jss-sio2-si3n4-sti-kinetic.pdf` (기존) |
| 10 | **(MEE 2016)** 그루브 폭–체류시간 논문 (`papers/mee-2016-mu-groove-width-residence-time.pdf`), 25.8 N, 95 RPM | | "swept across the pad surface **10 times per minute**. The same rotational velocity and **oscillation frequency** were used for in-situ conditioning." | **10** | 기존 |
| 11 | **Son & Lee (2021)**, "Contact-Area-Changeable CMP Conditioning for Enhancing Pad Lifetime", *Appl. Sci.* 11(8), 3521, DOI 10.3390/app11083521 (CC-BY). 한양대. | 국산 swing-arm, platen 93 rpm, 컨디셔너 101 rpm, 4 kgf, 스윙 50→370 mm | Table 1: "**Sweep per minute (sweep/min) 9**" | **9** | `papers/son2021-contact-area-changeable-app11083521.pdf` (기존) |
| 12 | **(ASPEN 2022)** ex-situ 컨디셔닝 디지털트윈 (`papers/aspen2022-exsitu-conditioning-digitaltwin.pdf`), POLI-500(G&P), platen 93 / head 87 rpm | | Table 1: "Conditioning **Sweep cycle [cyc/min] 9**", Rotation speed 101 rpm, Down force 0.7 psi | **9** | 기존 |
| 13 | **Sorooshian (2005) 학위논문** (Univ. of Arizona) — **랩 소형기** IC-1000 flat, 100-grit, 0.5 PSI, 디스크 30 RPM | | "…rotational velocity of 30 RPM and **disk sweep frequency of 20 per minute**" | (20) | `papers/sorooshian2005-dissertation-ua.pdf` (기존) |
| 14 | 같은 학위논문, 325-grit ring-type, 0.5 PSI, 디스크 20 RPM | | "…rotational velocity of 20 RPM and **disk sweep frequency of 30 per minute**" | (30) | 동상 |

**단위 해석 주의(중요):** #1은 "sweeps per minute", #3~#12는 "times per minute" / "sweep per minute" /
"cyc/min"로 모두 **분당 왕복 횟수**를 뜻한다. #2만 표기가 "sweep speed 19 **RPM**"인데, 같은 논문
§2 Eq.(4)에서 n_a는 β(T)=β_s − ½β_max·cos(… + 2n_a/60·πT) + ½β_max 의 각진동수로 들어간다 —
cos 인자가 (2n_a/60)πT이므로 주기는 60/n_a 초, 즉 **분당 n_a회 완전 왕복**이다. 따라서 #2의
"19 RPM"은 #1의 "19 sweeps per minute"와 **같은 물리량**이다(§4 verify에서 식으로 확인).
Zheng et al.의 툴(Hwatsing)과 Menk et al.의 툴(AMAT)이 독립적으로 19를 쓴 것은 우연으로 보이지만,
어쨌든 두 값은 같은 축 위에 있다.

**#13·#14 제외 이유:** Sorooshian의 두 값(20, 30 cpm)은 100 mm 웨이퍼급 랩 폴리셔에서 0.5 PSI,
디스크 20~30 RPM으로 돌린 조건이다. 스트로크 길이가 300 mm 상용기(#1 스윕범위 330 mm, #11 320 mm)와
자릿수가 다르므로 **같은 모집단으로 섞지 않는다**. 표에는 정직하게 남기되 §3 대표값 산정에서는
제외한다(제외 사실 자체가 §4 verify에서 assert로 고정됨).

## 3. 정량 종합 — 300 mm 상용 CMP 툴의 스윕 왕복수 분포

#1~#12(300 mm/200 mm 상용 폴리셔, 12개 레시피)만 모으면:

```
9, 9, 10, 10, 10, 10, 11, 13, 13, 15, 19, 19   (cpm)
```

- 범위: **9 ~ 19 cpm** (배율 2.1배)
- 중앙값: **10.5 cpm**, 최빈값: **10 cpm** (4/12 = 33%)
- 산술평균: 12.3 cpm

즉 fab-sim 현재값 **10.0 cpm은 이 12개 실측 레시피의 최빈값이자 중앙값 근처**다. 값 자체는
바꿀 필요가 없고, 근거 등급만 `unverified` → `literature`로 올릴 수 있다.

**왜 이 범위인가 (물리적 정합성 확인, 본 노트의 해석 — 어느 출처도 직접 이렇게 말하지 않음):**
스윕 1왕복에 걸리는 시간 60/N초 동안 패든 여러 바퀴 돈다. 패드 93~100 RPM에서 10 cpm이면
왕복 1회당 패드 회전은 약 9~10회 — 즉 **디스크가 반경방향으로 한 번 지나갈 때 패드의 전 원주가
9~10번 그 밑을 통과**한다. 이보다 스윕이 빠르면(N↑) 원주방향 커버리지가 성기고, 느리면(N↓)
반경방향 dwell 불균일이 커진다. 9~19 cpm은 이 두 요구의 절충 구간으로 읽힌다.

**#2 Zheng의 8시간 컨디셔닝이면 왕복 9,120회** (=8·3600/(60/19)) — PCR(r) 적산이 이 정도 반복
위에서 평균화된 결과라는 뜻이고, [[conditioner-sweep-kinematics-pcr-profile]] §3의 "격자 적산"이
통계적으로 수렴할 근거가 된다.

## 4. 정량 재현 (python verify)

```python verify
import statistics as st

# --- (a) §2 표의 원문 인용값. 상용 300/200mm 툴만(#1~#12), 랩 소형기(#13,#14)는 분리 ---
prod = [
    ("Menk2010 AMAT ILD",                 19),  # "19 sweeps per minute"
    ("Zheng2023 Hwatsing Table1",         19),  # "Conditioner arm sweep speed 19 RPM"
    ("KimKang2011 IJMTM",                 15),  # "sweep speed of 15 times/min"
    ("McAllister2019 Micromachines",      13),  # "13 times per minutes"
    ("McAllister2019 diss Saesol",        13),
    ("McAllister2019 diss 3M PB32A brush",11),
    ("McAllister2019 diss Shinhan CVD",   10),
    ("Liao2014 diss Araca APD-800",       10),  # 4개 실험에서 반복 등장
    ("Mariscal2020 JSS STI",              10),
    ("MEE2016 groove width",              10),
    ("Son&Lee2021 AppSci Table1",          9),  # "Sweep per minute (sweep/min) 9"
    ("ASPEN2022 POLI-500 Table1",          9),  # "Sweep cycle [cyc/min] 9"
]
lab = [("Sorooshian2005 100-grit", 20), ("Sorooshian2005 325-grit", 30)]  # 랩 소형기 — 제외

vals = [v for _, v in prod]
assert len(vals) == 12, f"상용 레시피 12건이어야 함, 실제 {len(vals)}"
lo, hi = min(vals), max(vals)
med, mode = st.median(vals), st.mode(vals)
assert (lo, hi) == (9, 19), f"문헌 범위는 9~19 cpm이어야 함, 실제 {lo}~{hi}"
assert mode == 10, f"최빈값은 10 cpm이어야 함, 실제 {mode}"
assert med == 10.5, f"중앙값은 10.5 cpm이어야 함, 실제 {med}"
assert vals.count(10) == 4, "10 cpm이 4건(Shinhan/Liao/Mariscal/MEE2016)이어야 함"
print(f"상용 12건: 범위 {lo}~{hi} cpm, 중앙값 {med}, 최빈값 {mode}, 평균 {st.mean(vals):.1f}")

# fab-sim 현재값 10.0이 이 분포 안에 있고 최빈값과 일치하는지 — 제안값 유지 근거
FABSIM = 10.0
assert lo <= FABSIM <= hi and FABSIM == mode
# 문헌 범위 폭(배율)이 2배 남짓임을 고정 — 이보다 넓어지면 "대표값 1개" 전략 재검토 필요
assert hi / lo < 2.5, f"문헌 범위 배율 {hi/lo:.1f}배 — 단일 대표값 타당성 재검토"

# 랩 소형기는 별도 모집단: 상용 최댓값보다 크다(섞으면 안 되는 이유를 수치로 고정)
assert min(v for _, v in lab) >= hi, "랩 소형기 값이 상용 범위와 겹치면 §2의 분리 논거를 수정해야 함"

# --- (b) Zheng Eq.(4) "19 RPM"이 Menk "19 sweeps/min"과 같은 물리량인지 식으로 확인 ---
# β(T) = β_s − ½β_max·cos( arccos(2(β0−β_s)/β_max) + (2·n_a/60)·π·T ) + ½β_max
# cos 인자가 2π만큼 증가하면 1왕복(=1주기). 그 T가 60/n_a 초인지 본다.
import numpy as np
n_a = 19.0
beta_s, beta_max, beta_0 = 0.0, 0.5, 0.0            # rad, 임의(주기 판정에 무관)
phase0 = np.arccos(2 * (beta_0 - beta_s) / beta_max) if abs(2*(beta_0-beta_s)/beta_max) <= 1 else 0.0
beta = lambda T: beta_s - 0.5*beta_max*np.cos(phase0 + (2*n_a/60)*np.pi*T) + 0.5*beta_max
period_s = 60.0 / n_a
assert abs(beta(0.0) - beta(period_s)) < 1e-12, "60/n_a초 후 스윕 위치가 원점으로 복귀해야 함"
# 한 주기 안에서 스윕이 양쪽 반환점을 정확히 한 번씩 찍는가 (진폭 = β_max)
Tg = np.linspace(0, period_s, 20001)
bg = beta(Tg)
assert abs((bg.max() - bg.min()) - beta_max) < 1e-6, "한 주기에 전체 스윕 범위 β_max를 왕복해야 함"
# 절반 주기에서는 아직 한쪽 끝만 다녀온 상태 — 주기가 60/n_a의 절반이 아님을 배제
bh = beta(np.linspace(0, period_s/2, 10001))
assert (bh.max() - bh.min()) < beta_max - 1e-6, "반주기가 이미 전 범위를 덮으면 주기 정의가 틀린 것"
# 1분 = 정확히 n_a 주기
assert abs((2*n_a/60)*np.pi*60.0 - n_a*2*np.pi) < 1e-9
print(f"Zheng Eq.4: n_a={n_a} RPM -> 주기 {period_s:.3f} s, 분당 {60/period_s:.0f}회 왕복 (= Menk 표기와 동일 축)")

# --- (c) 스윕 1왕복당 패드 회전수 (§3 물리적 정합성 논의의 수치 근거) ---
for name, n_sweep, platen_rpm in [("Menk2010", 19, 93), ("Son&Lee2021", 9, 93),
                                  ("Zheng2023", 19, 100), ("Liao2014", 10, 93)]:
    rev_per_sweep = platen_rpm / n_sweep
    print(f"  {name}: 스윕 1왕복당 패드 {rev_per_sweep:.1f}회전")
    assert 4 < rev_per_sweep < 12, f"{name}: 왕복당 패드회전 {rev_per_sweep:.1f} — 4~12 구간 밖"

# --- (d) Zheng 8시간 컨디셔닝의 총 왕복수 (PCR 적산의 통계 수렴 근거) ---
total_sweeps = 8 * 3600 / (60 / 19)
assert abs(total_sweeps - 9120) < 1, total_sweeps
print(f"Zheng 8h 컨디셔닝 총 왕복수: {total_sweeps:.0f}회")
```

문헌 재현 대조: Zheng et al. (2023) Table 1의 문헌값(sweep speed 19 rpm)으로 계산한 스윕 주기 3.158 s 는 (Menk et al. 2010) 원문 "19 sweeps per minute"이 함의하는 주기 3.158 s 와 일치했다(상대오차 < 1e-12).
두 논문은 서로 다른 툴(Hwatsing Universal-300-Plus vs AMAT)·다른 표기("RPM" vs "sweeps per minute")를
쓰지만 같은 물리량을 가리킨다. 같은 조건에서 스윕 1왕복당 패드 회전은 Zheng(패드 100 rpm) 5.3회,
Menk(platen 93 rpm) 4.9회다.

실행 결과: 상용 12건 범위 9~19 cpm, 중앙값 10.5, 최빈값 10(4/12), 평균 12.3. Zheng Eq.(4)의
n_a=19 RPM은 주기 3.158 s = 분당 19회 왕복으로 Menk의 "19 sweeps per minute"와 정확히 동일
축임을 식으로 확인했다(단위 혼동이 없음). 스윕 1왕복당 패드 회전수는 4.9~10.3회 구간에
전부 들어간다. Zheng 8시간 조건의 총 왕복수는 9,120회.

## 5. fab-sim `cond_sweep_cpm` 제안

- **값: 10.0 cpm 유지**(변경 없음), **confidence: `unverified` → `literature`**.
- 근거: §2 표 #7·#8·#9·#10 네 건이 정확히 "10 times per minute"으로 명시. 12건 상용 레시피의
  최빈값(4/12)이자 중앙값(10.5)에 가장 가까운 정수.
- 민감도 참고: 문헌 범위 9~19 cpm은 **2.1배** 폭이다. PCR(r) 프로파일 형상이 스윕 왕복수에
  민감하다면 이 2배가 그대로 불확실성으로 들어간다 — 시뮬레이터에서 `cond_sweep_cpm`을
  9~19로 스윕하는 민감도 테스트를 권한다(값 자체는 문헌 등급이지만 **범위는 넓다**).

## 6. 한계·미검증 (정직 기록)

- **9~19 cpm의 "어느 값이 왜 좋은가"를 논한 1차 문헌은 못 찾았다.** 모든 출처가 스윕 왕복수를
  실험 조건 표에 적을 뿐, 왕복수를 독립변수로 바꿔가며 PCR/MRR을 측정한 논문은 확보하지
  못했다(Baisie 2010은 세그먼트 **체류시간 비율**을, Zheng 2023은 **스윕 모드·범위**를 바꿨을 뿐
  왕복수 자체는 고정). 따라서 §3의 "9~19는 두 요구의 절충"은 **본 노트의 해석이며 미검증**.
- **장비 특허 경로 실패**: patents.google.com 검색(`CMP conditioner sweep oscillation cycles per
  minute`)에서 US7004825(Lam, oscillation mechanics), US5904615(swing arm), US6273797(IBM wedge),
  US12459078(AMAT) 등이 나왔으나 **실시예에 분당 왕복 횟수를 숫자로 적은 특허는 확인하지
  못했다** — 특허는 스윕 기구·제어 방식을 청구할 뿐 레시피 수치는 회피하는 경향으로 보인다
  (추정, 전수 확인 아님).
- **Menk et al. 2010 원문 PDF 재확보 실패**: link.springer.com이 봇 차단(HTML 셸 반환)이라
  이번 회차에 새로 받지 못했다. 다행히 `papers/menk2010-real-time-control-pad-profiles.pdf`가
  이전 회차에 확보되어 있어 **원문 문장을 직접 인용**했다(검색 스니펫 의존 아님).
- **Khanna et al. (2019)**, "Methodology for pad conditioning sweep optimization for advanced nodes",
  *Microelectron. Eng.* (`papers/khanna2019-sweep-optimization-advanced-nodes.pdf`, 확보됨)는
  제목상 이 단원의 정확한 후속이지만, 본문에서 스윕 **왕복수**는 명시하지 않고 zone별 dwell
  프로파일만 다룬다(platen 99 / carrier 77 RPM, 3.0 psi, 300 ml/min은 확인). AMAT 사내
  시뮬레이터 결과라 수치표가 제한적 — **왕복수 추출 실패**.
- 표 #5~#7은 같은 학위논문의 서로 다른 장이므로 통계적으로 완전히 독립인 12건은 아니다
  (독립 연구그룹 기준으로는 AMAT·Tsinghua·한양대(Kim&Kang)·Arizona·Korea(Son/ASPEN) 5그룹).
  §4 verify의 중앙값·최빈값은 이 중복을 보정하지 않은 단순 통계다.

## 관련 노트
[[conditioner-sweep-kinematics-pcr-profile]] · [[disk-sweep-recipe-flattening-baisie2010]] ·
[[conditioner-sweep-algorithm-trajectory-density]] · [[conditioner-disk-pad-cutting-model]] ·
[[disk-rpm-load-radius-pcr]]
