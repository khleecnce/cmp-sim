<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: chemistry, passivation, pourbaix, slurry, 선택비 | 정본: ARCHITECTURE-V2.md §3 -->
# Cu CMP 3단계 공정(벌크·소프트랜딩·배리어)과 단계별 슬러리 요구 (film-cu Lv1-1)

> film-cu Lv1-1 | 작성일: 2026-09-08
> 선행: [[surface-chemistry-cu-w-pourbaix-passivation]] (Pourbaix·BTA 부동태 메커니즘 원리 —
> 이 노트는 "왜 억제제가 작동하는가"를 재도출하지 않고 그 노트를 인용만 한다)
> [[pattern-dependent-dishing-erosion]] (패턴밀도·선폭에 따른 dishing/erosion 물리, Lv2-1에서 심화)
> 스코프: 3단계 공정 **구조**와 단계별 슬러리 **요구조건**의 "무엇·왜"에 집중. 배리어(Ta/TaN) CMP의
> 상세 화학(선택비 메커니즘 등)은 Lv2-2로 미루고, 여기서는 배리어 단계가 별도 슬러리·공정창을
> 필요로 한다는 사실만 개괄한다.

## 1. 왜 한 번에 안 밀고 여러 단계로 나누는가

Cu damascene CMP는 목표까지 한 가지 압력·슬러리로 밀면 안 된다. 이유는 두 가지 물리가 충돌하기
때문이다: (1) 벌크 제거는 처리량을 위해 빨라야 하지만, (2) 배리어 근처에서는 얇아진 Cu가 과도한
화학적 용해·기계적 압력에 노출되면 dishing이 급격히 커진다. 이 두 요구를 하나의 슬러리·압력으로
동시에 만족시킬 수 없어 업계는 압력·슬러리·화학을 단계적으로 바꾸는 다단계(통상 2~4 플라텐)
공정을 쓴다. 이 노트에서 "3단계"로 개념화하는 것은 **벌크 제거 → 소프트랜딩(브레이크스루) →
배리어 제거**의 3개 기능적 구간이며, 실제 툴 구현은 플라텐 개수에 따라 이보다 더 세분될 수 있다
(§3, §7 참조).

## 2. 1차 출처

- **특허 US 2009/0057264 A1** (Applied Materials, Inc., 발명자 David H. Mai, Stephen Jew,
  Shih-Haur Walters Shen, Zhihong Wang; 출원 2008-08-29, 공개 2009-03-05), "High Throughput Low
  Topography Copper CMP Process." Google Patents에서 명세서·청구항 원문을 직접 확인(캡차 없이
  접근 가능). 이 노트의 정량 수치(다운포스, 제거속도, 처리량, 슬러리 성분)는 전부 이 특허
  명세서의 인용문에서 가져왔다.
- Pan, Li, Wijekoon, Tsai, Redeker (Applied Materials) / Park, Tugbawa, Boning (MIT), "Copper CMP
  and Process Control," *CMP-MIC Conference* (1999년 2월 11-12일 발표) — 원문 PDF 확보
  (`papers/boning-copper-cmp-process-control.pdf`, 직접 텍스트 추출·읽음). **DOI 없음** —
  1999년 컨퍼런스 프로시딩이며 Crossref API로 조회했으나 미등재 확인(2026-09-08). 이하 §6에서
  "Pan 1999"로 표기.
- (정황 근거, 원문 미확보) "Friction based endpoint technique for barrier polish during copper
  CMP," 2011, DOI: 10.1109/wmed.2011.5767272 — 다단계 공정에서 배리어 전환 시점에 엔드포인트
  검출이 왜 필요한지를 뒷받침하는 제목·DOI만 확인, 본문은 읽지 못해 정량 수치는 인용하지 않음.
- Park, Tugbawa, Yoon, Boning, Chung, Muralidhar, Hymes, Gotkis, Alamgir, Walesa, Shumway, Wu,
  Zhang, Kistler, Hawkins (MIT/SEMATECH/IPEC-Planar/Rodel/Cabot), "Pattern and Process Dependencies
  in Copper Damascene Chemical Mechanical Polishing Processes," *VMIC* (1998) — 원문 PDF 확보
  (`papers/park1998-vmic-cu-damascene.pdf`, 직접 텍스트 추출·읽음). **DOI 없음**(동일 사유). 이하
  §6에서 "Park 1998"로 표기.

## 3. 3단계의 정의와 공정 파라미터 (US2009/0057264A1 명세서 인용)

특허가 기술하는 구체 실시예(1번 플라텐에서 2단계, 2번 플라텐에서 3단계째 진행)를 표로 정리:

| 단계 | 목적 | 다운포스(psi) | 제거속도(Å/min) | 종료조건 |
|---|---|---|---|---|
| ① 벌크 Cu 제거 | 두꺼운 오버버든 Cu를 빠르게 제거 | ~1.8 ("about 1 psi and 2 psi... about 1.8 psi") | ~9000 ("about 9000 Å/min") | Cu 잔막 ~2000Å 시점(RTPC 검출) |
| (전이: rate quench) | 패드 위 Cu²⁺ 부산물 농도를 낮춰 억제제 효과 회복 | ~0.5 ("reduced to about 0.5 psi") | — (슬러리·린스 유량 증가로 농도만 낮춤) | 시간 기반(고정) |
| ② 소프트랜딩 | 배리어 노출 시점까지 저속·저압으로 브레이크스루 | ~1.3 ("about 1.0 psi and 1.6 psi... about 1.3 psi") | 1500-2500, 대표값 ~1800 ("about 1800 Å/min") | 1차 브레이크스루(FullScan 검출) |
| ③ 잔류 Cu 제거(2번째 플라텐) | 웨이퍼 전면 잔류 Cu 완전 제거, 결함성능 확보 | ≤0.3 ("less than or equal to about 0.3 psi") | ~2000(Cu 기준) | 완전 제거 + 저압 오버폴리시(20초, "A 20 second overpolish process was performed") |
| (④ 배리어 제거) | Ta/TaN 제거, Cu:배리어:oxide 선택비 확보 | 미기재(별도 스테이션) | 미기재 | — Lv2-2에서 상세 |

특허 원문: "Following the residual conductive material removal step 316, a barrier polish may be
performed... on the third CMP station 132" — 배리어 제거가 잔류 Cu 제거 이후 **별도 스테이션**에서
수행됨을 명시하지만, 배리어 슬러리 조성·제거속도·압력은 이 특허에 구체적으로 기재되어 있지
않다. **미검증(이 특허 범위 밖)** — Lv2-2에서 배리어 슬러리 논문을 별도로 확보해야 한다.

## 4. 왜 다운포스를 계단식으로 낮추는가 — 전기화학적 근거

①→②→③으로 갈수록 다운포스와 제거속도가 급격히 낮아지는 이유는 순수히 기계적이지 않다.
벌크 단계에서는 두꺼운 Cu 막 아래 배리어가 아직 멀리 있어 국소적 과연마가 문제되지 않으므로
높은 산화제-기계적 제거 속도(높은 MRR)를 밀어붙일 수 있다. 그러나 Cu 막이 얇아지고 배리어에
근접할수록, (a) 트렌치 내부 Cu와 field 영역 Cu 사이의 국소 두께 편차가 곧바로 dishing으로
직결되고, (b) 패드 위에 누적된 Cu²⁺ 부산물이 [[surface-chemistry-cu-w-pourbaix-passivation]]에서
다룬 부동태(passivation) 평형을 교란해 BTA 억제제의 효과를 떨어뜨린다(특허 원문: rate quench
공정의 목적이 "reduce the copper ion concentration on the polishing pad... preserving passivation
agent effectiveness"). 그래서 소프트랜딩 직전에 슬러리·린스 유량을 늘려 패드 위 Cu 이온 농도를
씻어내는 "rate quench" 전이 스텝을 넣는다 — 이는 기계적 변수(다운포스)만이 아니라 **국소
전기화학 평형을 재설정**하는 스텝이라는 점이 핵심이다.

## 5. 슬러리 조성 — 단계별로 왜 다른가

특허 원문: "The bulk copper removal process and the soft landing process may require the use of
two distinct slurries or the same slurry. The process includes the bulk removal of a copper layer
using a first CMP slurry formulation having oxidizing agent, passivating agent, abrasive and
solvent, and the soft polishing and over-polishing using a formulation including the first CMP
slurry formulation and at least one additional additive."

즉 두 슬러리는 완전히 다른 화학이 아니라 **같은 베이스(산화제+억제제+연마재+용매)에 소프트랜딩용
첨가제를 추가**한 구성으로 기술된다.

- **산화제(oxidizer)**: "hydrogen peroxide" — H₂O₂가 Cu⁰를 Cu²⁺로 산화시켜 기계적 제거를 돕는
  주 산화제로 명시됨. 벌크 단계는 이 산화 반응 속도가 최대화되어야 고MRR이 나온다.
- **부동태화제(passivating agent, 억제제)**: "compounds having a nitrogen atom (N), such as
  organic compounds having an azole group. Examples of suitable compounds include benzotriazole
  (BTA), mercaptobenzotriazole, 5-methyl-1-benzotriazole (TTA)" — [[surface-chemistry-cu-w-pourbaix-passivation]]
  §의 BTA 부동태 메커니즘과 동일 계열. 소프트랜딩용 첨가 성분이 이 계열 억제제의 **추가 투입**일
  가능성이 높다고 특허는 시사하나, 정확히 무엇이 추가되는지(억제제 농도 증가인지 별도 화합물인지)는
  본문에 구체적으로 특정되어 있지 않다 — **미검증**.
- **연마재(abrasive)**: "colloidal silica, alumina, and/or cerria [ceria]" — 세 종류를 선택지로
  제시할 뿐, 벌크/소프트랜딩 단계별로 어느 것이 우선되는지는 특정하지 않는다 — **미검증**.

## 6. 실측: 다단계 공정이 dishing/erosion을 줄인다는 정량 근거 (Pan 1999, Park 1998)

Pan 1999(3-플라텐 양산 공정, 알루미나 연마재 슬러리 사용 명시)는 100 µm 폭 트렌치에서 오버폴리시
비율에 따른 디싱을 실측했다: "an optimum overpolish results in approx. 500 Å dishing over a 100 µm
trench." 또한 공정관리가 부실할 경우의 상한도 서술한다: "The copper loss in a poorly controlled
CMP process could easily reach 50% of the targeted thickness" (목표 Cu 두께 5000 Å 기준). 5 µm
피치·90% 밀도 라인/스페이스 어레이에서는 40% 오버폴리시 시 "the oxide erosion is the main
contributor to the total copper loss, which reaches almost 70% of a nominal 5000 Å thick copper
interconnect" — 즉 광폭 트렌치(dishing 지배)보다 고밀도 어레이(erosion 지배)가 훨씬 큰 두께손실
비율을 보인다는 것이 이 논문의 핵심 관찰이며, [[pattern-dependent-dishing-erosion]]의 패턴밀도
의존성 논의와 직결된다.

Park 1998(단일단계 vs 3단계 다운포스 램프다운 비교 실험, Table 1b: M=5→2→2 psi 3단계 vs
S=3 psi 단일단계, 동일 오버폴리시 시간)은 "the multistep process results in appreciably better
performance than the single step process"라고 결론짓는다 — 다만 이 비교의 정확한 디싱·erosion
수치는 본문 그래프에만 있고 텍스트로 기재되어 있지 않아 **정성적 결론만 재현 가능, 정량 비교는
미검증**으로 남긴다.

```python verify
# Pan et al. 1999, CMP-MIC "Copper CMP and Process Control"
# (papers/boning-copper-cmp-process-control.pdf, 본문 인용 수치)
target_cu_thickness_A = 5000.0  # 논문이 명시한 하위 배선레벨 목표 Cu 두께

# 100um 폭 트렌치, "최적 오버폴리시" 조건 실측 디싱량
optimum_dishing_A = 500.0
optimum_loss_frac = optimum_dishing_A / target_cu_thickness_A
print(f"최적OP 디싱 {optimum_dishing_A}A / 목표두께 {target_cu_thickness_A}A = {optimum_loss_frac:.1%}")
assert abs(optimum_loss_frac - 0.10) < 0.02, "최적 오버폴리시 손실비율이 문헌 서술(약 10%)과 다름"

# 공정관리 미흡시("poorly controlled") 문헌이 명시한 상한: 목표두께의 50%까지 손실 가능
poor_control_loss_frac = 0.50
poor_control_loss_A = poor_control_loss_frac * target_cu_thickness_A
print(f"공정관리 미흡시 Cu 손실 상한: {poor_control_loss_A:.0f}A ({poor_control_loss_frac:.0%})")
assert poor_control_loss_A == 2500.0

# 5um pitch, 90% 밀도 라인/스페이스 어레이, 40% 오버폴리시: 총 손실이 목표두께의 "거의 70%"
dense_array_op40_loss_frac = 0.70
dense_array_loss_A = dense_array_op40_loss_frac * target_cu_thickness_A
print(f"90%밀도 어레이 40%OP: 총 Cu 손실 {dense_array_loss_A:.0f}A (={dense_array_op40_loss_frac:.0%})")
assert abs(dense_array_loss_A - 3500.0) < 1.0

# 고밀도(erosion지배) 구조가 광폭트렌치 최적OP(dishing지배)보다 손실비율이 커야 한다는
# 논문의 정성적 핵심주장(§ EXPERIMENTAL RESULTS ON ARRAYS OF LINE AND SPACE) 재현
assert dense_array_op40_loss_frac > optimum_loss_frac, \
    "erosion 지배 고밀도 구조의 두께손실 비율이 dishing 지배 최적OP보다 커야 함"
print("OK: Pan 1999 실측 서술치로부터 Cu 두께손실 비율 재현, erosion>dishing 방향성 확인")
```

## 7. verify block — 3단계 다운포스·제거속도 단조성, 처리량 개선폭 재현

```python verify
# US 2009/0057264 A1 (Applied Materials, 공개 2009-03-05) 명세서 인용값
downforce_psi = {"bulk": 1.8, "rate_quench": 0.5, "soft_landing": 1.3, "residual_clear": 0.3}
rate_A_min = {"bulk": 9000.0, "soft_landing": 1800.0}

# 다운포스: 벌크 -> 소프트랜딩 -> 잔류제거 순으로 정상상태 값이 감소해야 함("소프트랜딩" 개념 자체)
assert downforce_psi["bulk"] > downforce_psi["soft_landing"] > downforce_psi["residual_clear"], \
    "다운포스가 벌크->소프트랜딩->잔류제거로 갈수록 감소해야 함"
# rate quench는 정상상태가 아닌 순간적 전이 구간으로, 소프트랜딩 정상값보다도 더 낮게 내려감
assert downforce_psi["rate_quench"] < downforce_psi["soft_landing"]

# 제거속도: 벌크 대비 소프트랜딩이 대략 1/5 수준으로 급감(문헌 대표값 9000 -> 1800 A/min)
ratio = rate_A_min["soft_landing"] / rate_A_min["bulk"]
print(f"소프트랜딩/벌크 제거속도 비 = {ratio:.2%}")
assert 0.15 < ratio < 0.25, "소프트랜딩 제거속도가 벌크의 약 1/5 근방이어야 함(문헌 수치 기준)"

# 처리량(throughput) 개선폭: 고처리량 공정 41-43 WPH vs 표준 공정 30-33 WPH
high_wph = (41.0, 43.0)
std_wph = (30.0, 33.0)
gain_conservative = (high_wph[0] - std_wph[1]) / std_wph[1] * 100  # 보수적 추정(하한 대 상한)
gain_optimistic = (high_wph[1] - std_wph[0]) / std_wph[0] * 100    # 낙관적 추정(상한 대 하한)
print(f"처리량 개선폭: +{gain_conservative:.1f}% ~ +{gain_optimistic:.1f}%")
assert 20 < gain_conservative < 30
assert 40 < gain_optimistic < 50
print("OK: 3단계 다운포스/제거속도 단조감소 및 처리량 개선폭(약 24~43%) 문헌 수치 재현")
```

## 8. 한계와 확인 못한 부분 (정직 표기)

- 이 특허(US2009/0057264A1)는 **구리 CMP 2개 플라텐 + 배리어 별도 스테이션** 구조를 기술하지만,
  "3단계 = 벌크·소프트랜딩·배리어"라는 이 노트의 개념적 3분류는 논문 저자들이 명시적으로 그렇게
  이름 붙인 것이 아니라, film-cu 커리큘럼 항목명에 맞춰 **재구성**한 것이다. 실제 툴 구현은
  4스텝(벌크/rate quench/소프트랜딩/잔류Cu제거) + 배리어 별도 스테이션으로 더 세분화되어 있다는
  점을 명시해 둔다.
- 배리어 제거 단계의 슬러리 조성·제거속도·다운포스는 이 특허에 구체적으로 기재되어 있지 않다
  (§3 표의 ④행). Lv2-2("배리어 CMP와 선택비")에서 별도 1차 출처를 확보해야 한다.
- 소프트랜딩 슬러리에 "추가되는 첨가제(at least one additional additive)"가 정확히 무엇인지
  (BTA 농도 증가인지, 별도 화합물인지)는 이 특허 명세서에 특정되어 있지 않다 — 미검증.
- Park 1998의 다단계 vs 단일단계 비교는 정성적 결론("appreciably better performance")만 텍스트로
  확인했고, 정량적 디싱·erosion 수치는 그래프(Fig.3-8)에만 있어 PDF 텍스트 추출로는 확보하지
  못했다 — 미검증.
- 이 노트가 인용한 세 문헌 모두(특허 1건, 컨퍼런스 프로시딩 2건) 동료심사 저널 논문이 아니다.
  특허는 청구항 확보를 위해 넓은 범위의 수치(예: "1500 Å/min for tungsten") — 즉 이 특허가 다루는
  범위가 구리 CMP만이 아니라 텅스텐 CMP까지 포괄하는 일반 특허라는 점에 유의. 본 노트는 구리
  관련 수치만 인용했다.

## 9. 자기시험
→ [[../../agents/film-cu/EXAMS.md]] Lv1-1 문항 참조.
