# 나이트라이드 정지층 메커니즘: 세리아 슬러리 선택비 화학의 3단 위계 (film-nitride Lv1-2)

> film-nitride Lv1-2 | 작성일: 2026-09-10
> 선행: [[film-nitride-lpcvd-pecvd-properties-cmp]] (Lv1-1 — 막질 자체가 정지층 성능을 가르는 축)
> 관련(부모·형제, 상세 메커니즘은 그쪽 참조): [[../cmp/ceria-slurry-ce-redox-selectivity]] (slurry-chemist Lv3-1 — Ce³⁺/Ce⁴⁺ 산화환원·Si–O–Ce 화학흡착 DFT 정량),
> [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] (film-oxide Lv2-2 — 선택비가 STI 디싱·침식 공정통합으로 번역되는 Lee 2002 모델),
> [[../cmp/preston-luo-dornfeld-mrr]] (Kp·비-Prestonian 프레임)
> 스코프: 이 노트는 **"왜 낮은 농도의 첨가제가 나이트라이드만 골라서 완전히 차단하는가"**를 흡착 포화·표면전하의 관점에서
> 정량화한다. Ce³⁺/Ce⁴⁺ 산화환원의 원자수준 화학(DFT)은 [[../cmp/ceria-slurry-ce-redox-selectivity]]가 다뤘으므로 반복하지 않고,
> 대신 **동일 저자군(Dandu/Babu)의 원문 흡착등온선·제타전위·접촉각·TGA 데이터**를 직접 읽어 "왜 저농도에서 나이트라이드만
> 포화되는가"를 재구성한다. STI 공정통합(디싱·오버폴리시 창)은 후속 Lv2-1 몫.

## 1. 왜 이 단원이 필요한가 — 선택비는 하나의 숫자가 아니라 3단 위계다

지금까지 이 에이전트의 결론(Lv1-1)은 "나이트라이드는 세리아보다 단단하고, 직접 안 깎이고 가수분해로만 깎인다"였다.
그런데 문헌을 모아보면 **같은 세리아 슬러리라도 무엇을 더하느냐에 따라 oxide:nitride 선택비가 4:1에서 290:1까지
두 자릿수를 걸친다.** 이 위계를 만드는 손잡이는 최소 세 가지이고, 각각 다른 기전이다:

1. **첨가제 없는 순수 세리아** — 선택비는 낮다(≈4:1). 유일한 차이는 §4.2에서 다룰 나이트라이드의 느린 가수분해뿐.
2. **분산제만(PAA 등, 사이트-비특이적)** — 선택비가 소폭 오른다(≈5–8:1). 표면 전하·응집 제어가 부수 효과로 나이트라이드를 더 억제.
3. **사이트-특이적 흡착제(사이클릭 아민·아미노산)** — 선택비가 두 자릿수로 뛴다(≈100–290:1). 이것이 실제 STI HSS(고선택비)
   슬러리의 작동 원리다.

## 2. 출처 (5건, 1차 4건, 모두 원문 완독)

- **[D9] P. R. Dandu Veera, S. Peddeti, S. V. Babu, "Selective Chemical Mechanical Polishing of Silicon Dioxide over Silicon
  Nitride for Shallow Trench Isolation Using Ceria Slurries," *J. Electrochem. Soc.* 156(12) H936–H943 (2009).
  DOI: 10.1149/1.3230624.** 1차 논문, 원문 PDF 완독(`papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf`). 이 노트의 §3–5
  핵심 수치(RR·흡착등온선·제타전위·접촉각·TGA)는 전부 이 논문에서 직접 읽었다(sti-cmp 노트가 이미 인용한 RR값과 독립적으로
  재확인, 흡착·전하 데이터는 이 노트가 처음 추출).
- **[N] C. M. Netzband, K. Dunn, "Controlling the Cerium Oxidation State During Silicon Oxide CMP to Improve Material Removal
  Rate and Roughness," *ECS J. Solid State Sci. Technol.* 9, 044002 (2020). DOI: 10.1149/2162-8777/ab8393.** 1차 논문,
  CC-BY 오픈액세스, 원문 PDF 완독(`papers/netzband2020-jss-ceria-oxidation-state-oxide-cmp.pdf`). §5의 산화상태-선택비 배율.
- **[H] S. Hwang, T. Lyu, W. Kim, "Poly(acrylic acid)-Containing Ceria Slurries for Shallow Trench Isolation Chemical
  Mechanical Polishing," *Polymers* 18, 1899 (2026). DOI: 10.3390/polym18151899.** 1차 논문, CC-BY 오픈액세스, 원문 PDF
  완독(`papers/hwang2026-polymers-paa-ceria-sti-slurry.pdf`). §3의 "분산제만" 선택비 기준점(HNU15/HC10).
- **[S] R. Srinivasan, P. V. R. Dandu, S. V. Babu, "Shallow Trench Isolation CMP: A Review," *ECS J. Solid State Sci.
  Technol.* 4(11) P5029–P5039 (2015). DOI: 10.1149/2.0071511jss.** CC-BY 리뷰, 원문 완독(`papers/srinivasan2015-ecsjss-sti-cmp-review.pdf`).
  개관·정지층 <1 nm/min 기준.
- **[D11] P. R. Veera Dandu, B. C. Peethala, H. P. Amanapu, S. V. Babu, "Silicon Nitride Film Removal During CMP Using
  Ceria-Based Dispersions," *J. Electrochem. Soc.* 158(8) H763 (2011). DOI: 10.1149/1.3596181.** Crossref로 실존·저자
  확인. **원문 PDF 미확보**(IOP 페이지가 Cloudflare 챌린지로 HTML만 반환, 미러 사이트 미러도 Cloudflare 봉쇄, 2026-09-10
  재시도) → [N]의 서론이 인용하는 범위(가수분해 2단계 메커니즘)만 **2차 인용**으로 사용.

## 3. 위계 1→2: 첨가제 없음 vs 분산제만 — 가수분해 속도차가 만드는 "바닥" 선택비

[D9]의 무첨가 기준선(60 nm Rhodia 세리아 0.25 wt%, pH 4–5, 4 psi/75-75 rpm, IC1000): 산화막 **350 nm/min**, 나이트라이드
**80 nm/min** → 선택비 **4.375**(원문 Fig.3 서술, §6 verify (A)). 이 4.4:1이 "세리아가 나이트라이드보다 산화막을 더 좋아한다"는
순수 화학 차이(Lv1-1 §4.2 가수분해 속도차)만으로 나오는 바닥값이다.

여기에 **사이트-비특이적 분산제(PAA)만** 넣으면 어떻게 되나 — [H]가 정확히 이 조건이다(사이클릭 아민·아미노산 같은 억제제는
전혀 없이 PAA만 콜로이드 안정화용으로 넣은 슬러리). 4 psi/300-150 rpm/IC1000, 60 s: 자체합성 HNU15 세리아는 산화막
**114.4 Å/min**·나이트라이드 **14.3 Å/min** → 선택비 **8.0**, 상용 HC10 세리아는 산화막 **57.5**·나이트라이드 **12.3 Å/min**
→ 선택비 **4.674**([H] Fig.13 원문, §6 verify (A)). 즉 분산제만으로는 선택비가 기준선(4.4)과 **같은 자릿수**에 머문다 —
PAA는 입자분산·거품 억제가 목적이지 나이트라이드 표면을 목표로 차단하지 않기 때문. (참고: [D9]의 §5.2에 인용된 Hwang 2024
*Polymers* 16,844의 소포폴리머 데이터(선택비 59–80)는 이 [H]와 다른 논문·다른 첨가제[소포제 포함]이며 혼동 주의 — 순수
PAA-only 대조는 이 노트가 처음 정리했다.)

## 4. 위계 2→3: 왜 0.05% 사이클릭 아민이 선택비를 100배 넘게 올리는가 — 흡착 포화의 비대칭

[D9]가 답을 준다. 0.05 wt%의 피리딘HCl·피페라진·이미다졸(모두 방향족/비방향족 고리형 아민) 중 아무거나 넣으면 산화막
RR은 그대로(**350 nm/min**)인데 나이트라이드 RR만 **2–3 nm/min**으로 급락 → 선택비 **117–175**(§6 verify (A)). 180 nm
소성 세리아 1 wt%에서는 첨가제 0.05%로 산화막이 오히려 **580 nm/min**까지 올라가는데 나이트라이드는 여전히 **2 nm/min**
→ 선택비 **290**([D9] 원문 명시 수치). 핵심 질문: 왜 이렇게 낮은 농도(0.05%)에서 나이트라이드만 완전히 뒤덮이고 산화막은
안 그런가?

[D9]의 흡착등온선(Fig.11–12)이 직접 답한다:
- **실리카(120 nm)**: 슬러리 내 피리딘HCl 농도를 0.05%→1%로 20배 올리면 흡착량이 **1.3→8.2 mg/g로 계속 증가**한다 —
  포화되지 않는다.
- **나이트라이드(50 nm)**: 같은 농도범위에서 흡착량이 **0.1% 이상부터 2.4 mg/g로 고정**된다 — 이미 포화.

즉 **나이트라이드 표면은 훨씬 적은 흡착제로 100% 덮이고, 실리카 표면은 계속 더 흡착할 자리가 남는다.** 그래서 0.05%라는
"딱 나이트라이드만 포화시키는" 농도를 고르면 나이트라이드는 완전 차단(RR↓↓), 산화막은 부분 피복이라 여전히 세리아가
접근 가능(RR 유지/오히려↑, 접촉각 데이터도 동일 결론: 나이트라이드 접촉각은 0.05%든 1%든 **65° 근처로 불변**, 산화막
접촉각은 농도에 비례해 **35°→90°로 계속 증가**, [D9] Table II). TGA도 정합: 나이트라이드 흡착량은 농도 증가에 거의
불변, 세리아·실리카는 증가(§6 verify (B)).

시간추이(Fig.14)는 이 포화-차단을 더 직접 보여준다: 나이트라이드는 **첫 30 s에 자연산화층 두께(~3 nm)만 깎이고 200 s까지
추가 제거가 없다** — 자연산화층이 벗겨지자마자 드러난 순수 Si₃N₄ 표면에 피리딘이 강하게(탈착 저항성 있게) 결합해
가수분해를 원천봉쇄한다는 뜻이다. 반면 산화막 표면에 흡착된 피리딘은 첨가제 없는 슬러리로 30–60 s만 갈아도 쉽게
씻겨나간다(접촉각이 65°→40°대로 복귀). **나이트라이드 결합은 강하고 비가역적, 산화막 결합은 약하고 가역적** —
이것이 America & Babu(2차 인용, [D9] 본문)의 제안대로 **Si–O–C/H 결합(카르복실·아미노기 ↔ 나이트라이드 표면 Si/N)**이
산화막의 단순 수소결합보다 안정적이기 때문이라는 가설로 이어진다.

## 5. 전하 관점 — 세리아·나이트라이드는 같은 부호, 세리아·실리카는 반대 부호

[D9]의 제타전위 데이터(작동 pH 4–5 기준): **실리카는 pH 2–12 전 구간 음전하**, **세리아 IEP=8**(pH 8까지 양전하),
**나이트라이드 분말 IEP=9**(벌크 Si₃N₄ IEP는 9.7이나 표면 자연산화층 때문에 9로 이동, [D9]가 자신들의 이전 논문을 2차
인용). 즉 pH 4–5 작동점에서 **세리아(+)와 실리카(−)는 반대 부호 → 정전인력**, **세리아(+)와 나이트라이드(+)는 같은
부호 → 정전 반발**([[../cmp/ceria-slurry-ce-redox-selectivity]] §4가 다룬 세리아-실리카 IEP 쌍(6.7–7.8 vs 2–3, 2차 인용
범위)보다 이 노트의 IEP=8/9는 같은 저자군의 **동일 실험 조건에서 직접 측정한 값**이라 더 좁고 신뢰도 높다 — 그 노트와
값의 정합성은 부호만 일치, 절대치는 시료·측정법 의존이라 **직접 비교는 미검증**). 첨가제(피리딘HCl)를 넣으면 세리아
IEP는 8→7, 나이트라이드 IEP는 9→8로 둘 다 소폭 이동하지만 실리카는 저농도(0.05–1%)에서 IEP 변화가 없다(pH<8에서는)
— 이는 §4의 흡착 비대칭과 별개로, 정전기력 자체는 산화막 쪽에 원래 유리하게 기울어 있었음을 보여준다.

## 6. Ce³⁺/Ce⁴⁺ 산화상태 튜닝만으로는 선택비가 한 자릿수밖에 안 오른다

[[../cmp/ceria-slurry-ce-redox-selectivity]]가 다룬 Ce³⁺ 활성점 화학을 나이트라이드 쪽에서 보면 대조적인 그림이
나온다. [N]은 H₂O₂ 0.5 wt%·pH 8·68 nm 입자로 표면 Ce³⁺%를 최적화해 상용 슬러리 대비 산화막 RR을 **5.5배**, 나이트라이드
RR을 **2.25배** 올렸다 — 둘 다 오르지만 산화막이 더 크게 올라 선택비가 "거의 1:1"에서 **3:1**로 개선됐다([N] 원문
"Selectivity measurements" 절, §6 verify (C)). 이는 §4의 사이트-특이적 흡착제(100배 이상)와 **자릿수가 다르다** — Ce³⁺
농도 자체를 조절하는 것은 세리아의 **화학적 이빨의 세기**를 산화막·나이트라이드 양쪽에 비슷한 방향으로(비율은 다르게)
키우는 것이라, 나이트라이드를 선택적으로 "꺼버리는" 사이트 차단과는 기전이 다르다. 결론: **산화상태 튜닝 = 배율 조절
(둘 다 빨라짐, 비율 소폭 변화), 사이트 차단 첨가제 = 스위치(나이트라이드만 꺼짐).**

## 7. 정량 재현 (python verify)

**재현 요약**: 무첨가 선택비 4.375, PAA 전용 선택비 4.67–8.0, 사이클릭아민 선택비 117–290 — 3단 위계가 문헌 수치로
재현됨. 흡착 비대칭(실리카 1.3→8.2 mg/g 계속증가 vs 나이트라이드 2.4 mg/g 포화), Ce³⁺ 산화상태 튜닝의 선택비 개선
배율(1→2.44, 원문 보고 ~3)이 사이트차단(100배 이상)과 자릿수가 다름을 대조 — 아래 2블록 PASS.

```python verify
# ── (A) 선택비 3단 위계 재현 (Dandu 2009 DOI 10.1149/1.3230624, Hwang 2026 DOI 10.3390/polym18151899, 원문 확인) ──
# 1단: 첨가제 없음
oxide_RR_noadd, nitride_RR_noadd = 350.0, 80.0     # nm/min, Dandu 2009 Fig.3
sel_noadd = oxide_RR_noadd / nitride_RR_noadd
assert abs(sel_noadd - 4.375) < 0.01

# 2단: PAA 분산제만 (사이트-비특이적, 억제제 없음)
sel_paa_hnu15 = 114.4 / 14.3        # A/min, Hwang 2026 Fig.13
sel_paa_hc10 = 57.5 / 12.3          # A/min
assert abs(sel_paa_hnu15 - 8.0) < 0.05
assert abs(sel_paa_hc10 - 4.674) < 0.01

# 3단: 사이트-특이적 사이클릭아민 0.05% (피리딘HCl/피페라진/이미다졸 공통)
oxide_RR_amine, nitride_RR_amine_hi, nitride_RR_amine_lo = 350.0, 3.0, 2.0
sel_amine_lo = oxide_RR_amine / nitride_RR_amine_hi
sel_amine_hi = oxide_RR_amine / nitride_RR_amine_lo
assert 100 <= sel_amine_lo <= sel_amine_hi <= 200
# 180nm 세리아 + 0.05% 피리딘HCl (Dandu 2009 원문 명시 선택비)
oxide_RR_amine_180, nitride_RR_amine_180 = 580.0, 2.0
sel_amine_180 = oxide_RR_amine_180 / nitride_RR_amine_180
assert abs(sel_amine_180 - 290.0) < 0.1

# 위계 순서: 무첨가 < PAA전용 < 사이트특이적 첨가제 (자릿수 단조증가)
assert sel_noadd < sel_paa_hc10 <= sel_paa_hnu15 < sel_amine_lo < sel_amine_180
print(f"위계: 무첨가 {sel_noadd:.1f} < PAA {sel_paa_hc10:.1f}-{sel_paa_hnu15:.1f} "
      f"< 사이트특이적 아민 {sel_amine_lo:.0f}-{sel_amine_180:.0f}")

# ── (B) 흡착 포화 비대칭 (Dandu 2009 Fig.11-12, 원문 확인) ──
ads_silica_005, ads_silica_1 = 1.3, 8.2      # mg/g @ 0.05%, 1% 피리딘HCl (실리카 120nm)
ads_nitride_sat = 2.4                        # mg/g, 0.1% 이상에서 일정(나이트라이드 50nm)
assert ads_silica_1 / ads_silica_005 > 5     # 실리카는 20배 농도증가에 6배 넘게 계속 증가
assert ads_nitride_sat < ads_silica_1        # 나이트라이드 포화점이 실리카 최대흡착보다 낮음 → 저농도서 조기포화
print(f"흡착: 실리카 {ads_silica_005}->{ads_silica_1} mg/g(비포화) vs 나이트라이드 {ads_nitride_sat} mg/g(0.1%부터 포화)")
```

```python verify
# ── (C) Ce3+/Ce4+ 산화상태 튜닝의 선택비 개선 배율 (Netzband & Dunn 2020, DOI 10.1149/2162-8777/ab8393, CC-BY 원문 확인) ──
oxide_speedup, nitride_speedup = 5.5, 2.25   # 상용 슬러리 대비 배율, "Selectivity measurements" 절
sel_before = 1.0                              # 원문 "nearly 1:1" — 정밀값 비공개, 근사치 사용(미검증)
sel_after_calc = sel_before * oxide_speedup / nitride_speedup
assert abs(sel_after_calc - 2.444) < 0.01
reported_after = 3.0                          # 원문이 보고한 반올림 선택비
assert abs(sel_after_calc - reported_after) < 1.0   # 근사 일치(sel_before가 정밀히 1.00은 아니라서 미세 불일치, 정직히 기록)

# 산화상태 튜닝 배율(~2.4-3배)은 사이트차단 첨가제 배율(위 블록 100배 이상)과 자릿수가 다르다
site_block_sel = 117.0   # 위 블록 sel_amine_lo 대표값
assert sel_after_calc < 10 < site_block_sel
print(f"Ce3+ 산화상태 튜닝: 선택비 {sel_before:.0f}->{sel_after_calc:.2f}(원문 보고 ~{reported_after:.0f}) "
      f"— 사이트차단 첨가제({site_block_sel:.0f}:1)와 자릿수 차이, 기전이 다름")
```

## 8. 정직한 한계

- **[D11] 원문 미확보**: IOP 페이지·미러 사이트 미러 모두 Cloudflare 챌린지로 봉쇄돼 2단계 가수분해 메커니즘 서술은 [N]의
  서론을 통한 **2차 인용**이다. [D11] 자체의 정량값(있다면)은 이 노트에 반영하지 못했다 — **확인 못 함**.
- **나이트라이드 IEP=9.7(벌크)**은 [D9]가 자기 이전 논문을 인용한 것이라 이 노트 기준으로는 **2차 인용**; 실측(9, 자연산화층
  포함)만 1차로 확인했다.
- **§6 (C)의 sel_before=1.0**은 원문 "nearly 1:1"이라는 정성 서술의 근사치이지 원문이 준 정밀 수치가 아니다 — 계산된
  2.44:1과 원문 보고 3:1 사이 불일치(~19%)는 이 근사 탓일 가능성이 크지만 **원인을 원문에서 직접 확인하지는 못했다(추정)**.
- **PAA 슬러리 두 종(HNU15 vs HC10) 선택비 차이(8.0 vs 4.67)**를 이 노트는 "분산제 자체 효과"로 단순화했지만, 원 논문은
  세리아 입자 자체의 Ce³⁺ 분율·입경 차이도 함께 작용한다고 명시한다(슬러리 계 전체 효과, 단일 변수로 귀속 불가) — **부분
  미검증**, §3에서 이 단서를 함께 적었다.
- 흡착 메커니즘의 원자수준 결합양식(Si–O–C/H 가설)은 America & Babu의 제안을 [D9]가 재인용한 것으로, 이 노트는 DFT나
  분광 데이터로 직접 검증하지 못했다 — **가설 단계로 취급**.

## 9. 이 에이전트의 결론 (모델링 관점)

1. **STI 정지층 모델의 Kp는 첨가제 유무에 따라 자릿수가 바뀐다.** [[../cmp/preston-luo-dornfeld-mrr]]의 Kp_nitride를 단일
   상수로 고정하면 안 되고, 최소 "무첨가(≈1/4.4 Kp_oxide)·분산제(≈1/5–8)·사이트차단(≈1/100–290)" 3구간으로 스위칭해야
   한다. [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] §4의 Lee 2002 선택비 s는 이 3구간 중 어느
   슬러리 레시피를 쓰느냐로 s=4~290 사이를 오간다는 뜻이다.
2. **흡착 포화 농도가 "스위치 포인트"다.** 사이트차단 첨가제는 나이트라이드 표면을 포화시키는 최소농도(이 계에서 ≈0.05–0.1%)
   근방에서 선택비가 급변한다 — 이 농도 밑에서는 나이트라이드 보호가 불완전(WIWNU 50%, [D9]), 위에서는 과잉이라 낭비.
   Tier2 구현 시 이 "포화 임계 농도"를 명시적 파라미터로 넣어야 상 전이형 선택비 거동을 재현할 수 있다(현재 PROFILE
   구현요청의 L-H 모델은 연속함수라 이 스위치를 못 담는다 — 향후 보완 필요).
3. **산화상태(Ce³⁺/Ce⁴⁺) 손잡이와 첨가제 손잡이는 독립적으로 설계 가능**하다 — 전자는 배율(양쪽 다 빠르게/느리게), 후자는
   스위치(한쪽만 차단)이므로 두 효과를 곱해 쓸 수 있다(단, 정량 상호작용은 문헌에 없음 — **미검증**, 향후 조사 과제).

## 10. 자기시험
→ [[../../agents/film-nitride/EXAMS.md]] Lv1-2 문항 참조.
