# 나이트라이드 직접 CMP — 정지층이 아니라 제거 대상일 때 (하드마스크·SAC 게이트) (film-nitride Lv2-2)

> film-nitride Lv2-2 | 작성일: 2026-09-11
> 선행(같은 에이전트): [[film-nitride-lpcvd-pecvd-properties-cmp]] (Lv1-1 — LPCVD/PECVD 물성·경도서열·가수분해 제거기전),
> [[film-nitride-selectivity-ceria-chemistry]] (Lv1-2 — 세리아 선택비 3단 위계, 사이트차단 첨가제로 나이트라이드를 **못 깎게** 만드는 화학),
> [[../cmp/sti-nitride-loss-erosion-overpolish-window]] (Lv2-1 — 정지층으로 살아남은 나이트라이드의 침식·손실 예산)
> 관련: [[preston-luo-dornfeld-mrr]] (Kp·Prestonian/비-Prestonian), [[../cmp/ceria-slurry-ce-redox-selectivity]] (Ce³⁺/Ce⁴⁺ 산화상태)
> 스코프: 이번 단원까지의 Lv1/Lv2-1은 전부 "나이트라이드가 **멈추는 막**"이었다(정지층·선택비·손실예산).
> 이 노트는 반대 극단 — 나이트라이드를 **실제로 깎아 없애야 하는** CMP 공정(하드마스크 스트립, SAC/RMG 게이트,
> FinFET 핀캡)을 다루고, 정지층 대비 요구 MRR·선택비 방향·결함 관점이 어떻게 뒤집히는지 정리한다.

## 1. 왜 "반대"인가 — 같은 세리아 슬러리로 나이트라이드를 빨리 깎기

Lv1-2에서 확립한 상은 "세리아+사이트차단 첨가제 → 나이트라이드 완전 차단(RR↓), 선택비 100~290:1(옥사이드>나이트라이드)"이었다.
그런데 첨단 로직 공정에는 나이트라이드를 **정지 없이 통째로 벗겨내야** 하는 CMP 단계가 최소 두 곳 있다:

1. **SAC(Self-Aligned Contact) / RMG(replacement metal gate) 모듈** — 게이트 위에 정렬마진용 SiN 캡을 덮고 남은
   오버버든을 CMP로 제거한다. 이 공정은 문헌에서 **"Reverse STI"** 라 불린다(Alety 2017, 아래 §2 [A]) — STI가
   "옥사이드를 깎고 나이트라이드에서 멈추는" 공정이라면, 이건 "나이트라이드를 깎고 다른 층(옥사이드/금속)에서
   멈추는" 거울상 공정이기 때문이다.
2. **FinFET 핀캡(fin cap) 하드마스크 제거** — 핀 형성 후 SiN 캡을 웨트/드라이 에치 대신 **폴리싱으로 제거**하는
   특허가 존재한다(US8895444B2, 아래 §2 [P1]).

두 경우 모두 목표는 Lv1-2/Lv2-1과 정반대다: **나이트라이드 RR을 높이고**(수백 nm/min급), 옥사이드/실리콘 쪽에서
멈추도록 선택비를 나이트라이드 우위로 뒤집는다("reverse selectivity").

## 2. 출처 (4건, 1차 3건 — 논문 1건 원문 완독·특허 2건 명세서 확인)

- **[A] S. R. Alety, K. V. Sagi, S. V. Babu, "Role of Ce³⁺ Ions in Achieving High Silicon Nitride Polish Rates,"
  *ECS J. Solid State Sci. Technol.* 6(12) P898–P903 (2017). DOI: 10.1149/2.0351712jss** — 1차 논문, CC-BY-NC-ND
  오픈액세스, 원문 완독(`papers/dandu2017-jss-ce3-high-nitride-polish-rate.pdf`, 표제와 달리 제1저자는 Alety —
  파일명은 형제 그룹 관행을 따름). SAC "Reverse STI" 모듈 개념도(Fig.1)와 Ce³⁺ 첨가 나이트라이드 직접 CMP 데이터.
- **[P1] US8895444B2, GLOBALFOUNDRIES Inc., "Hard mask removal method" (출원 2013-03-13, 등록 2014-11-25)** —
  1차 특허, 명세서 확인(freepatentsonline·Google Patents 미러 대조). FinFET 핀캡 SiN을 3단계 CMP
  (옥사이드 씨닝→stop-on-nitride→**stop-on-silicon**)로 제거하는 방법 청구.
- **[P2] US9558959B2, "Polishing compositions and methods for selectively polishing silicon nitride over silicon
  oxide films" (Cabot Microelectronics 계열, 등록 2017)** — 1차 특허, 명세서 확인. 음이온성 연마재+카르복실기
  첨가제로 SiN을 옥사이드보다 빨리 깎는 상용 슬러리 조성과 Table 1 정량 데이터.
- **[D10] P. R. Veera Dandu, V. K. Devarapalli, S. V. Babu, "Reverse selectivity – High silicon nitride and low
  silicon dioxide removal rates using ceria abrasive-based dispersions," *J. Colloid Interface Sci.* 347, 267–273
  (2010). DOI: 10.1016/j.jcis.2010.03.071** — Crossref로 실존·저자·권호 확인. **원문 PDF 미확보**(퍼블리셔 접근권
  없음) → "reverse selectivity" 용어의 원출처로만 인용, 메커니즘 서술은 [A]가 이 논문을 인용한 대목([A] 참고문헌
  4번) 경유 **2차 인용**으로 표기.
- 보조: [[film-nitride-selectivity-ceria-chemistry]]의 Dandu 2009([D9], DOI 10.1149/1.3230624) — 이번 노트의
  대조군(정지층 방향 선택비)으로 재사용.

## 3. SAC/Reverse-STI 모듈 — Ce³⁺ 이온으로 나이트라이드 RR을 30배 끌어올리기

[A]의 Fig.1(Reverse STI 개념도): 게이트 위 SiN 캡을 증착하면 항상 오버버든이 남고, 이를 고선택비로 벗겨내야
콘택 정렬마진이 확보된다. 실험 조건은 PECVD SiN 500 nm·열산화막 2000 nm·오산화질화막(SiON) 200 nm, 세리아
0.1 wt%(140 nm), IC1000 패드, 4 psi/87–93 rpm.

| 조건 | 나이트라이드 RR | 옥사이드 RR | 방향 | 출처 |
|---|---|---|---|---|
| 세리아만, pH4 (첨가제 없음) | ~10 nm/min | ~250 nm/min | 옥사이드 우위(정지층 방향) | [A] Fig.2 |
| +1.2 mM Ce(NO₃)₃, pH4 | ~210 nm/min | ~110 nm/min | **역전 시작** | [A] Fig.2 |
| +2.3 mM Ce(NO₃)₃, pH4 | ~300 nm/min(4 psi)·~360 nm/min(5 psi) | ~80 nm/min(4 psi) | **나이트라이드 우위** | [A] Fig.2, 4, 결론 |
| +2.3 mM Ce(NO₃)₃, pH7 | ~220 nm/min | ~250 nm/min | 거의 동률 | [A] Fig.2 |

Ce³⁺ 농도를 11.5 mM까지 올려도 RR은 더 안 오른다(포화, [A] 결론). 압력을 1→5 psi로 올리면 RR·마찰계수(COF)·
온도가 **거의 선형으로 증가**해(Prestonian) 5 psi에서 RR ~360 nm/min에 도달한다([A] Fig.4). 이는 Lv1-1에서
Mariscal이 정지층 저속 영역(첨가제 없는 낮은 RR)의 SiN 연마를 **"highly chemically-limited"·비-Prestonian**
이라 부른 것과 대비된다 — **같은 재료(SiN)라도 화학(Ce³⁺ 산화 촉매)이 속도결정단계를 바꾸면, 저속 영역(화학-제한)
에서 고속 영역(기계-제한에 가까움, Prestonian)으로 레짐이 이동**한다는 뜻이다(§6에서 정량 재현).

**메커니즘([A] XPS·제타전위 근거)**: Ce³⁺ 이온이 나이트라이드 표층을 실온·수계에서 **산화질화물(oxynitride,
Si–O–N)로 전환**시키고, 이 산화질화물을 세리아 연마재가 빠르게 벗겨낸다(오산화질화막 자체 RR은 ceria만으로도
65 nm/min, Ce³⁺ 첨가 시 200 nm 막이 ~20 s만에 전부 벗겨져 RR **>600 nm/min**로 추정 — 즉 최소 9배 이상 가속).
전환-제거가 반복되며 전체 RR은 **전환(산화) 단계가 율속**이다([A] 결론). FeCl₃(110 nm/min)·Co(NO₃)₂(70 nm/min)도
같은 산화촉매 역할을 하지만 Ce³⁺(300 nm/min)만큼 효과적이지 않다 — 즉 이 가속은 세리아 특유가 아니라 **다가
양이온 산화촉매 일반의 효과이되 Ce³⁺가 가장 강하다**([A] Discussion).

## 4. FinFET 핀캡 제거 — 에치 대신 CMP를 쓰는 이유

[P1](US8895444B2)은 핀 형성 후 SiN 캡을 제거하는 표준 방법이 **습식/건식 에치**였고, 이것이 "핀 표면 손상
→ 불균일한 핀 프로파일"을 유발한다고 명시한다(명세서 배경기술). 대안으로 제시하는 3단계 CMP:

1. 실리카 기반 슬러리로 옥사이드 씨닝(평탄화)
2. 세리아 기반 슬러리로 **stop-on-nitride** — 옥사이드를 핀캡 상면까지 제거
3. 세리아 기반 슬러리로 **stop-on-silicon** — 핀캡(SiN)을 **완전히 제거**하고 옥사이드를 핀 상면까지 낮춤

3단계가 이 노트의 핵심이다: 여기서 나이트라이드는 **더 이상 정지층이 아니라 제거 대상**이고, 다음 정지 기준면은
**실리콘(핀)**이다. 즉 같은 웨이퍼 안에서 나이트라이드가 (2)단계에서는 "정지 목표"였다가 (3)단계에서는
"제거 목표"로 역할이 바뀐다 — 공정 스텝마다 선택비의 방향 자체가 바뀌는 사례([P1] 청구항 1·3).

## 5. 상용 리버스선택비 슬러리 화학 — 전하 반발로 옥사이드를 밀어내기

[P2](US9558959B2)는 §3의 Ce³⁺/산화질화 경로와는 다른 화학으로 같은 목적(나이트라이드 우위 선택비)을 달성한다:
**음이온성(음전하) 연마재 + 카르복실기(carboxyl/carboxylate) 함유 나이트라이드 촉진제**. 명세서 Table 1(정규화
RR, 8인치 웨이퍼, Applied Materials Mirra, 3 psi):

| 첨가제 | 나이트라이드 RR(정규화) | TEOS RR(정규화) | SiN:TEOS |
|---|---|---|---|
| 없음(대조군) | 1.000 | 0.063 | 16 |
| 질산 | 5.716 | 0.867 | 7 |
| 아세트산 | 11.182 | 0.630 | 18 |
| **프로피온산** | 10.966 | **0.114** | **97** |
| 말론산 | 8.920 | 0.713 | 13 |

카르복실기 첨가제는 나이트라이드 RR을 대조군 대비 **8~11배** 올리면서(질산·황산 등 비-카르복실기 산은 4.6~5.7배로
덜 효과적) TEOS RR은 40 Å/min 미만으로 억제한다. 명세서 설명: 음이온성 연마재가 역시 음전하인 TEOS 표면과
**정전 반발**해 TEOS RR을 낮게 유지하는 반면, 카르복실기 첨가제는 나이트라이드 표면과 유리하게 상호작용해
가수분해·제거를 가속한다. 다만 이 효과가 관능기 하나로 단순화되지는 않는다 — **말론산(디카르복실산)은 나이트라이드
RR을 8.9배 올리면서도 TEOS RR을 0.713까지 더 크게 끌어올려**, 결과 선택비(13:1)가 오히려 대조군(16:1)보다
낮아진다(§6 코드 재현). 즉 카르복실기 개수·구조가 나이트라이드-옥사이드 선택성을 세밀하게 좌우하며, "카르복실기가
있으면 무조건 선택비 개선"이라 단순화할 수 없다. §3의 Ce³⁺ 경로(양이온 산화촉매, 산화질화물 경유)와 §5의
카르복실기 경로(음이온 연마재, 전하반발로 옥사이드만 억제)는 **화학적으로 서로 다른 두 개의 "역선택비" 레버**다 —
Lv1-2에서 정지층 선택비가 "사이트차단(스위치)"과 "산화상태 튜닝(배율조절)"으로 갈렸던 것과 평행한 이원성이다.

## 6. 정량 재현 (python verify)

```python verify
# Alety 2017 [A] Fig.2: Ce3+ 첨가에 따른 SiN/옥사이드 RR 역전 (pH4, 0.1wt% ceria, 4psi)
RR_SiN_no_additive   = 10.0    # nm/min, 첨가제 없음
RR_ox_no_additive    = 250.0
RR_SiN_2p3mM         = 300.0   # +2.3 mM Ce(NO3)3
RR_ox_2p3mM          = 80.0

sel_no_additive = RR_ox_no_additive / RR_SiN_no_additive   # 옥사이드 우위(정지층 방향)
sel_with_Ce3    = RR_SiN_2p3mM / RR_ox_2p3mM                # 나이트라이드 우위(역전)

print(f"첨가제 없음: 옥사이드/나이트라이드 = {sel_no_additive:.1f}:1 (정지층 방향)")
print(f"Ce3+ 2.3mM: 나이트라이드/옥사이드 = {sel_with_Ce3:.2f}:1 (역전)")

# 주장1: 첨가제 없을 때는 옥사이드가 20배 이상 빠르다(정지층 레짐, Lv1-2와 정합)
assert sel_no_additive >= 20
# 주장2: Ce3+ 첨가로 방향이 뒤집힌다(나이트라이드가 더 빨라짐)
assert sel_with_Ce3 > 1.0
# 주장3: 나이트라이드 RR 자체는 Ce3+로 30배 가까이 증가
rr_gain = RR_SiN_2p3mM / RR_SiN_no_additive
print(f"나이트라이드 RR 증가량 = {rr_gain:.0f}배")
assert 20 < rr_gain < 40, "Ce3+ 산화촉매 효과가 문헌 서술(2~3자릿수 가속)과 정합해야 함"

# 오산화질화막(SiON) RR: ceria만 65 nm/min -> Ce3+ 첨가 시 >=600 nm/min (하한, 200nm 막이 20s내 전부 제거)
RR_SiON_ceria_only = 65.0
RR_SiON_with_Ce3_lower_bound = 600.0
sion_gain_lower_bound = RR_SiON_with_Ce3_lower_bound / RR_SiON_ceria_only
print(f"SiON RR 가속(하한) = {sion_gain_lower_bound:.1f}배")
assert sion_gain_lower_bound > 9.0, "산화질화물 경유 시 제거가 SiN 직접 제거보다 훨씬 빨라야 기전 성립"
```

```python verify
# US9558959B2 [P2] Table 1: 카르복실기 첨가제의 정규화 선택비 재현
additives = {
    "none":     (1.000, 0.063),
    "nitric":   (5.716, 0.867),
    "acetic":   (11.182, 0.630),
    "propionic":(10.966, 0.114),
    "malonic":  (8.920, 0.713),
}
sel = {k: rr_sin / rr_teos for k, (rr_sin, rr_teos) in additives.items()}
for k, v in sel.items():
    print(f"{k}: SiN:TEOS = {v:.1f}:1")

# 주장1: 프로피온산이 표 중 최고 선택비(~97:1)를 낸다
assert 90 < sel["propionic"] < 100
# 주장2: 카르복실기 첨가제 중에서도 아세트산·프로피온산은 대조군(16:1)보다 선택비가 높지만,
# 말론산(디카르복실산)은 나이트라이드 RR도 올리는 동시에 TEOS RR을 더 크게 올려(0.713) 선택비가 오히려
# 대조군보다 낮다(13:1) — "카르복실기=항상 선택비 개선"이 아니라 관능기 개수·구조에 따라 달라짐을 보여줌.
for k in ("acetic", "propionic"):
    assert sel[k] > sel["none"], f"{k} 선택비가 대조군보다 낮으면 안 됨"
assert sel["malonic"] < sel["none"], "말론산은 예외적으로 선택비가 대조군보다 낮아야 함(표 그대로)"
# 주장3: 카르복실기 없는 질산은 카르복실기 첨가제들보다 나이트라이드 가속 배율이 작다(명세서 서술)
assert additives["nitric"][0] < additives["propionic"][0]
print("카르복실기 첨가제가 비-카르복실기 산보다 나이트라이드 RR을 더 크게 올림 — 명세서 서술과 정합")
```

## 7. 정지층 vs 직접제거 — 요구치가 뒤집히는 표

| 항목 | 정지층 응용(STI, Lv1-2/Lv2-1) | 직접 제거 응용(SAC/핀캡, 이 노트) |
|---|---|---|
| 목표 나이트라이드 RR | 최소화(문헌 2–3 nm/min, [D9]) | 최대화(수백 nm/min, [A] 300–360) |
| 선택비 방향 | 옥사이드≫나이트라이드(100–290:1, Lv1-2) | 나이트라이드≥옥사이드(3.75:1~97:1, §3·§5) |
| 다음 정지 기준면 | 나이트라이드 자체(정지 목표) | 그 아래 옥사이드/실리콘/금속([P1] stop-on-silicon) |
| 결함 관심사 | 나이트라이드 침식·손실예산 소진([[../cmp/sti-nitride-loss-erosion-overpolish-window]]) | 핀/게이트 손상 균일도([P1]: 에치 대비 "폴리싱이 핀 프로파일을 덜 해친다"는 주장), 게이트 주변 옥사이드 손실("oxide loss or erosion around the gate", POP/SAC 공정 서술 — 미검증: 정량 수치는 확인 못 함) |
| 마찰·열 부하 | 상대적으로 낮음(느린 RR) | COF 0.14→0.58, 온도 40→60 ℃로 급등([A] Fig.3) — 스크래치·열손상 리스크 증가 방향이나 [A]는 결함밀도를 직접 측정하지 않음(**미검증**) |
| 대표 화학 레버 | 사이트차단 첨가제(스위치)·Ce³⁺/⁴⁺ 산화상태(배율조절), Lv1-2 | Ce³⁺ 산화촉매(양이온, 산화질화물 경유)·카르복실기+음이온연마재(전하반발), §3·§5 |

이 표에서 가장 중요한 관찰은 **"세리아 슬러리"라는 한 단어가 두 응용에서 정반대 설계 목표를 갖는다**는 점이다.
같은 세리아 입자라도 Ce³⁺ 첨가·pH·첨가제 종류에 따라 나이트라이드를 완전히 막을 수도(Lv1-2), 30배 가속할 수도(§3)
있다 — CMP 슬러리 설계는 "이 막을 깎을 것인가 남길 것인가"라는 공정 의도에 따라 완전히 다른 화학을 쓴다.

## 8. 이 에이전트의 결론 (모델링 관점)

1. **Kp는 응용에 따라 부호가 아니라 자릿수 자체가 바뀐다**: [[preston-luo-dornfeld-mrr]]의 $K_p$를 나이트라이드에
   적용할 때, "정지층 SiN"과 "직접제거 SiN"을 같은 재료 상수로 취급하면 안 된다. 화학 첨가제(Ce³⁺ 유무·카르복실기
   유무)가 유효 $K_p$를 1~2자릿수 이동시키는 스위치 역할을 한다(§3·§5).
2. **레짐 전이가 Prestonian성 자체를 바꾼다**: Lv1-1/Mariscal은 저속(첨가제 없는) SiN 연마를 화학-제한·비-Prestonian
   이라 했지만, Ce³⁺ 고속 레짐([A])은 압력에 거의 선형 응답한다. 하나의 재료에 대해 "이 막은 비-Prestonian이다"라고
   고정하면 틀릴 수 있다 — **레짐(첨가제 조성)이 Prestonian 여부를 정한다**.
3. **공정 스텝 체인 모델이 필요**: [P1]의 3단계 CMP처럼 한 공정 흐름 안에서 나이트라이드의 역할이 "정지 목표"→
   "제거 목표"로 바뀐다. 시뮬레이터가 스텝별로 슬러리·목표막을 다시 지정할 수 있어야 이런 체인을 재현할 수 있다.

## 9. 자기시험
→ [[../../agents/film-nitride/EXAMS.md]] Lv2-2 문항 참조.
