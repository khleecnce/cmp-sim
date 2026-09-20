<!-- V2-SECTION: R2-slurry | 공동: R3-pad | 분배완료 2026-09-08 | 근거: 슬러리, 입자 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 구조 — 발포체·groove·subpad (Lv1-2)

> process-integrator [[cmp-tool-architecture]], pad-mechanic [[pad-viscoelasticity-dma]] 상호링크.
> Phase 0 GW 접촉모델(Lv2-1)의 "패드 표면이 실제로 어떤 기하구조인가" 사전지식.

## 1. IC1000류 상부패드 — 경질 미세다공 폴리우레탄

**출처: Pureon(구 Rodel→Rohm and Haas→Cabot→Entegris 계보) 공식 데이터시트,
IC1000™/IC1010™ Datasheet, 2024-04-09, https://pureon.com/wp-content/uploads/2024/04/IC1000_datasheet_en_2024-04-09.pdf**

| 항목 | IC1000™ | IC1010™ |
|---|---|---|
| 기재 | Urethane (경질 미세다공 PU) | Urethane |
| 압축률 (Compressibility) | 2.25% | 2.25% |
| 경도 (Shore D) | 60 | 60 |
| 두께 | 50 mils (~1.27mm) | 80 mils (~2.03mm) |

- 두 제품 모두 Shore D 60(동일 경도)이지만 두께가 다름 — **두께 차이는 주로 groove 깊이 여유·서브패드
  적층 시 전체 스택 압축 응답을 튜닝하는 데 쓰임** (얇은 IC1000은 더 rigid한 로컬 응답, 두꺼운 IC1010은
  글로벌 컴플라이언스가 약간 더 큼 — 정성적 추론, 정량 비교는 미검증).
- "micro-porous"(미세다공): 발포 공정으로 형성된 닫힌 셀(closed-cell) 기공이 슬러리를 국소적으로
  보유·재분배하는 역할. 기공 크기 분포 자체의 정량값은 이 데이터시트에 없음 → **미검증(추가 조사 필요)**.
- Shore D 60은 pad-mechanic Lv1-1 노트에서 언급한 상용 패드 범위(60–90, US Patent 10391606)의
  하한부에 해당 — 상대적으로 유연한 축에 속하는 CMP 하드패드.
- 적용 공정: W(텅스텐)/Cu/ILD/STI/폴리실리콘 — 즉 IC1000이 다양한 재료계에 범용으로 쓰이는
  "표준" 하드패드임을 확인. ⚠ 이전 판본은 여기에 "Lv2-1 preston.py가 참조한 STI 254 nm/min
  문헌값과 동일 패드 계열"이라 적었으나, **그 254.05 nm/min은 2차 인용**이고
  ([[../cmp/preston-luo-dornfeld-mrr]] §3 코드 주석이 "*2차 인용*"으로 명시) 그 출처가
  IC1000 패드를 썼다는 서술은 어디에도 확인되지 않는다 — **패드 계열 동일성 주장은 근거가
  없으므로** 본 판본에서 철회한다. 데이터시트가 실제로 보증하는 것은 "적용 공정 목록에 STI가 있다"까지다.

## 2. K-groove 패턴

Pureon 데이터시트에 "K groove", "K cross section" 도식 명시(수치 치수는 비공개).
K-groove는 CMP 업계에서 오목한 동심원+방사형 조합 홈 패턴 중 하나로, 슬러리를 웨이퍼 중심에서
가장자리로, 그리고 방사 방향으로 순환시켜 (1) 슬러리 재보급 (2) 연마 부산물·마모입자 배출
(3) 국소 발열 냉각의 3기능을 동시에 수행한다.

**출처: A numerical study on slurry flow with CMP pad grooves, Kim et al., Wear (2020),
ScienceDirect S0167931720302252 (초록 기준 — 원문 유료, 초록만 확인)** — circular groove와
circular+radial groove를 비교한 CFD 연구가 존재한다는 사실만 확인, 정량 결과는 **미검증**
(페이월로 본문 미확인).

## 3. 2층 적층 구조 (Stacked pad: 상부패드 + subpad)

**출처: Zheng, Zhao, Lu (2023), "Prediction of Pad Wear Profile and Simulation of Its Influence
on Wafer Polishing", Micromachines 14(9), 1683, PMC10536193 (오픈액세스 CC-BY),
DOI: 10.3390/mi14091683**

- 실제 산업 CMP 플랫폼(Hwatsing Universal-300-Plus, 12인치) 구조 확인: 폴리싱 헤드가 웨이퍼를
  잡고 패드 위에 가압, 패드는 platen에 접착(glued), 헤드 내부에 다중 동심 압력존, 리테이닝링이
  웨이퍼 이탈 방지, 컨디셔너 디스크가 sweep arm에 고정되어 왕복 운동하며 패드 표면 asperity 재생.
- 컨디셔닝은 반경별로 다른 컷레이트(cut rate)를 만들어 **패드 마모 프로파일이 불균일**해짐 —
  이 논문은 운동학 모델(Preston 식 기반, 다이아몬드 입자별 총 스크래치 거리 적산)로 패드
  마모 프로파일을 예측하고 실측과 대조해 좋은 일치를 확인했다(정량값은 사내 실험조건 의존이라
  본 노트에는 미기재, 방법론만 채택).
- **핵심 발견 (설계에 직결)**: 정적 모델에서 "패드 표면 불균일(마모로 인한 요철)이 있으면
  pad-wafer 접촉응력에 국소 집중이 생기고, 이는 헤드의 다중 압력존 제어를 어렵게 만든다"
  — 즉 Lv1-2에서 배운 groove/subpad 구조와 무관하게, **마모 자체가 새로운 압력 비균일 원인**이 됨.
  disk-conditioner 에이전트의 Phase 0 항목("디스크: 컨디셔닝-패드마모 모델")과 직결되는 선행 지식.
- 리테이닝링이 있으면 웨이퍼 edge profile이 개선된다는 정성적 결과 — edge effect가 순수 운동학
  ([[cmp-kinematics-rotary]]에서 이미 확인한 시간평균 1.0039 edge/center)뿐 아니라 **기계적
  구속(리테이닝링)에도 좌우됨**을 시사. WIWNU v0 모델(현재 sim/tier1_empirical/process_time.py)은
  이 리테이닝링 효과를 아직 반영하지 않음 — 향후 보강 후보로 기록.

## 4. Subpad 존재의 근거 — Suba IV 사례

**출처: McAllister et al. (2019), "Effect of Conditioner Type and Downforce, and Pad Surface
Micro-Texture on SiO2 Chemical Mechanical Planarization Performance", Micromachines 10(4), 258,
PMC6523751 (오픈액세스 CC-BY), DOI: 10.3390/mi10040258**

- 실험 조건에 명시: "brand-new IC1000 K-grooved pads **with Suba IV sub-pad**" — 즉 상용 CMP
  세팅에서 IC1000(경질 상부패드)+Suba IV(연질 서브패드)의 2층 구조가 실제 사용됨을 1차 문헌으로 확인.
  이는 pad-mechanic EXAMS.md Q3에서 이미 정성 추론했던 "경질 상부패드+연질 서브패드 적층"
  가설을 실측 실험 논문으로 뒷받침하는 근거.
- 정량 공정조건도 확인: 폴리싱 압력 4 PSI(≈27.6 kPa), platen/carrier RPM 87/38(**Rs=38/87≈0.437,
  ω_w≠ω_p — kinematics.py의 등속조건과 다른 비대칭 사례**), 슬러리 Fujimi COMPOL-EX3(콜로이드
  실리카 32.5nm, pH9.5), 컨디셔닝 disc가 13회/분 sweep, 컨디셔닝 downforce 0.9~2.7 kgf.
- 컨디셔너 타입·downforce가 패드 표면 마이크로텍스처(요철 형상)를 바꾸고, 이것이 COF·RR과
  상관되지만 이 논문은 **"COF와 RR이 상관관계 없음"을 명시적으로 보고** — 즉 마찰계수만으로
  MRR을 예측하는 단순 모델은 이 실험 조건에서 실패함을 확인. Preston식(P·V 선형)이 왜 "실험적
  근사"에 그치는지의 또 다른 실측 근거.

## 5. Lv1-2 종합 — Lv2-1(GW 접촉모델) 착수 전 체크리스트

1. 상부패드는 경질(Shore D 60) 미세다공 PU, 두께 mm 단위 — GW 모델에서 "거친 표면의 모재"로 다룰 층.
2. Groove는 slurry 이송·부산물 배출용 기하 구조 — GW 접촉모델에서는 groove를 뺀 "랜드 영역
   (land area)"만 asperity 접촉 대상으로 삼아야 함(면적 보정 인자 필요, 다음 단원에서 도입).
3. Subpad(Suba IV류, 연질)는 상부패드보다 훨씬 낮은 강성으로 웨이퍼 스케일(mm~cm)의 글로벌 휨에
   순응 — GW 모델은 보통 **국소(µm 스케일) asperity 접촉**만 다루므로, subpad 효과는 별도의
   "글로벌 컴플라이언스" 항으로 Lv2-2 이후에 결합해야 함(지금 병합하면 스케일 혼동).
4. 실측 컨디셔닝 조건(sweep 패턴·RPM·downforce)이 패드 표면 상태를 계속 변화시킨다는 것은,
   GW 모델의 입력 파라미터(asperity 밀도·평균곡률·표준편차)가 **시불변 상수가 아니라 컨디셔닝
   이력의 함수**임을 뜻함 — v0 GW 구현 시엔 우선 정적 파라미터로 고정하고, disk-conditioner
   에이전트 지식이 쌓이면 동적으로 갱신하는 것으로 범위를 명확히 유보.

## 6. 검증 — 데이터시트 수치 재현과 인용 정합성 감사 (2026-09-15 부채상환)

이 노트는 `check_knowledge.py`는 통과했으나 `verify_claims.py`에서 **검증 코드 블록 없음**으로
반려 상태였다(22편 중 21편이 같은 상태였던 그 부채). 아래 블록이 ①단위 환산 ②이 노트를
`source:`로 지목하는 팩 파라미터의 정합성을 기계로 잠근다.

**감사 결과(중요)**: `knowledge/params/base.yaml::groove_depth_mm = 0.76`(= 30 mil)이
이 노트를 `source:`로 지목하고 confidence `literature`를 달고 있었는데, **이 노트는 §2에서
"K-groove 수치 치수는 비공개", §7 목록에서 "K-groove 정확한 치수(깊이·폭·피치)"를
**근거 미보유**로 명시**하고 있다 — 즉 팩이 이 노트가 갖고 있지 않은 수치의 근거로 이 노트를
인용하고 있다. 노트를 고쳐 수치를 만들어 내는 것은 할루시네이션이므로 하지 않는다.
대신 아래 assert가 **그 불일치를 사실로 고정**하고, 올바른 1차 출처를 가진
[[pad-groove-geometry-contact-area-flow-resistance]](Rosales-Yeomans 2005 IC1000 3종,
깊이 400 µm 실측 / Zhao 2022 깊이 1.2 mm 최적점)로 `source:` 재지정이 필요함을 신고한다.
이것은 이 노트가 아니라 팩 YAML의 결함이므로 담당(pad-structure)에게 이관한다.

```python verify
# ── ① 데이터시트 단위 환산 재현 (Pureon IC1000/IC1010 2024-04-09) ──
MIL_TO_M = 25.4e-6                      # 1 mil = 1/1000 inch = 25.4 µm
ic1000_m = 50 * MIL_TO_M
ic1010_m = 80 * MIL_TO_M
assert abs(ic1000_m - 1.27e-3) < 1e-9, f"IC1000 50mil 환산 {ic1000_m}"
assert abs(ic1010_m - 2.03e-3) < 1e-5, f"IC1010 80mil 환산 {ic1010_m}"   # 2.032e-3 ≈ 2.03e-3
assert abs(ic1010_m / ic1000_m - 1.6) < 1e-12, "두께비 80/50 = 1.6 — 경도(Shore D 60)는 동일"

# ── ② 이 노트를 source로 지목하는 팩 파라미터 감사 ──
# 노트가 실제로 담고 있는 정량값은 데이터시트 3종(압축률·Shore D·두께)뿐이다.
import re, pathlib
note = pathlib.Path("knowledge/materials/pad-structure-groove-subpad.md").read_text()
assert "수치 치수는 비공개" in note, "§2가 K-groove 치수 비공개를 명시해야 한다"
assert "K-groove 정확한 치수" in note, "§7 목록에 K-groove 치수가 있어야 한다"

base = pathlib.Path("knowledge/params/base.yaml").read_text()
# 이 노트를 source로 쓰는 블록의 키 이름을 모은다
keys = re.findall(
    r"^  (\w+):\n(?:(?:    .*\n|\s*\n)*?)    source: knowledge/materials/pad-structure-groove-subpad\.md",
    base, re.M)
print("이 노트를 근거로 인용하는 팩 키:", keys)

SUPPORTED = {"pad_thickness_m"}          # 데이터시트가 실제로 보증하는 값
for k in keys:
    if k in SUPPORTED:
        continue
    # 노트가 근거 미보유로 선언한 축(groove 치수)을 이 노트 근거로 쓰고 있으면 결함
    assert "groove" in k, f"예상 못 한 인용 키 {k} — 감사 범위를 넓혀야 한다"
    print(f"⚠ 출처 불일치: base.yaml::{k} 가 이 노트를 인용하지만 "
          f"이 노트는 groove 치수의 근거를 갖고 있지 않다 → pad-structure 이관")

# 불일치가 실제로 존재함을 고정한다(해소되면 이 assert가 깨져 재판정을 강제한다)
assert any("groove" in k for k in keys), \
    "groove 치수 인용이 해소됐다면 이 절의 감사 기록을 갱신하라"
print("감사 완료 — 데이터시트 환산 2건 재현, 출처 불일치 1건 신고")
```

## 7. 근거 미보유 목록 (갱신 2026-09-15)
- IC1000 실제 기공 크기·기공률 정량값 (데이터시트 비공개)
- K-groove 정확한 치수(깊이·폭·피치)
- Circular vs circular+radial groove의 CFD 정량 비교 결과 (페이월)
- IC1000/IC1010 두께 차이가 실제 컴플라이언스에 미치는 정량적 영향
