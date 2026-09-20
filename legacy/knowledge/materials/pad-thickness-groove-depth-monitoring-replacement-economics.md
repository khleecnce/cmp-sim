<!-- V2-SECTION: R4-disk | 공동: R3-pad | 분배완료 2026-09-08 | 근거: breakin, conditioning, 컨디셔너 | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 두께·그루브 깊이 모니터링과 교체 기준(경제성 포함)

> pad-lifecycle Lv2-2 | 작성일: 2026-09-07
> [[pad-glazing-mechanism-mrr-decay]] [[pad-conditioning-wear-regeneration-balance]]
> [[pad-breakin-asperity-mrr-runup]] 상호링크.
> Lv2-1 노트는 glazing을 "접촉점 수·반경의 시간의존 변화 → MRR 감소"로 정량화했다. 이 노트는
> 한 단계 더 나아가 **패드가 물리적으로 다 닳았다는 것을 실측으로 어떻게 아는가(두께·그루브
> 깊이 모니터링)**와 **그 실측값을 언제 교체 결정으로 바꾸는가(경제성 포함)**를 다룬다.

## 1. 왜 "그루브 깊이"가 별도의 교체 기준인가

Lv2-1의 glazing은 asperity 스케일(μm)의 마모·소성변형이고 MRR로 관찰된다. 반면 그루브는
그보다 훨씬 큰 스케일(수백 μm~mm)의 기계 가공 구조로, 슬러리를 웨이퍼 아래로 수송하고
연마 부산물을 배출하는 통로다. 컨디셔닝이 패드 표면 전체를 깎아내리는 이상 그루브도 함께
얕아지고, 그루브가 슬러리 유체역학을 유지 못 할 만큼 얕아지면(극단적으로는 평평해지면)
asperity 상태와 무관하게 패드 수명이 끝난다 — Son & Lee(2024, 원문은 Applied Sciences
2021년 게재)의 실험 정의를 그대로 쓰면 "usage duration of the polishing pad until the
groove of the polishing pad had worn out, or when an abrupt change in the MRR and WIWNU
occurred"이다. 즉 그루브 깊이는 glazing과는 **독립적인 두 번째 실패 모드**이고, 두께
모니터링은 그 진행 정도를 직접 재는 방법이다.

## 2. 1차 출처 정량 데이터: Son & Lee (2021) — 컨디셔닝 방식이 그루브 마모·패드 수명에 미치는 영향

**출처**: Jungyu Son, Hyunseop Lee, "Contact-Area-Changeable CMP Conditioning for Enhancing
Pad Lifetime", *Applied Sciences* 11(8), 3521 (2021), doi.org/10.3390/app11083521 (MDPI
오픈액세스 CC-BY). `.venv/bin/python tools/find_open_access.py --title`로 DOI 확인(Unpaywall
"publishedVersion"/"cc-by"). ⚠ MDPI 서버가 Akamai 봇 차단으로 curl/WebFetch 직접 접근을
거부해 `r.jina.ai` 리더 프록시로 HTML 전문(표 1~4 포함)을 확보·직접 읽었다 — PDF 파일 자체는
`papers/`에 저장하지 못했다(다운로드 시도는 HTML 오류 페이지만 반환됨, 텍스트는 확보).

실험조건: KONI 하드 폴리우레탄 패드(KPX Chemical), 실리카 슬러리(TSO-12, Soulbrain), 200 mm
SiO2 웨이퍼, 웨이퍼압 34.3 kPa, 플래튼 93 rpm·헤드 87 rpm. 패드 두께 프로파일은
PMS(Pad Measurement System, G&P Technology, 분해능 0.1 μm, 재현성 <2%(1σ))로 컨디셔닝
전후 직접 측정. 두 조건 비교: Case I(기존 풀컨택트 컨디셔너) vs Case II(내측 컨디셔너만
사용해 웨이퍼-패드 접촉 구간의 마모를 줄인 분할 컨디셔너).

| 항목 | Case I (기존) | Case II (분할 컨디셔너) |
|---|---|---|
| 평균 패드 컷레이트 | 43.4 μm/h | 22.2 μm/h |
| MRR 변화 | 401.3→221.0 nm/min (16 h간 −44.9%) | 387.7→359.0 nm/min (20 h간 −7.4%) |
| WIWNU | 12 h까지 3% 이내, 이후 급증 | 20 h까지 3% 이내 유지 |
| 그루브 상태(SEM 단면, Fig.17) | 16 h 후 그루브 완전 소멸, 웨이퍼 파손으로 실험 중단 | 20 h 후에도 그루브 잔존 |

저자 결론(원문): 불균일 마모(웨이퍼-패드 접촉 구간에 집중된 국소 과다마모)가 그루브
소멸·MRR 급락·WIWNU 급증을 **동시에** 일으키는 원인이며, 접촉면적을 줄인 컨디셔닝으로
마모를 균일화하면 패드 수명을 20시간 이상으로 늘릴 수 있다(Case II는 실험을 20 h에서
자발 종료했을 뿐 그루브가 남아 있었으므로 **실제 수명은 20 h보다 길 수 있다** — 논문은
이 이상의 값을 보고하지 않음, 미검증).

## 3. 그루브 깊이·패드 두께 인시츄/엑스시츄 모니터링 방법 — 특허 조사

공개 문헌에서 실제 두께·그루브 깊이를 재는 방법을 정리한다(모두 미국 특허, 회사 자금
아닌 개인 조사, Google Patents에서 확인).

- **US7198546B2** (LSI Logic Corp., 출원 2004-06-29·등록 2007-04-03), "Method to monitor
  pad wear in CMP processing": 접촉식(스타일러스가 패드에 닿아 그루브를 지날 때 드래그
  변화 감지)과 비접촉식(전자기 임피던스·레이저 반사·초음파 두께계) 두 계열을 청구한다.
  신품 그루브는 "on the order of 50 mils wide and 50 mils deep"(≈1.27 mm×1.27 mm)이고,
  "패드가 완전히 소진되면 패드는 평평해진다"(그루브 깊이 → 0)를 종료 기준으로 삼는다.
  명시적 교체 임계값 수치는 청구항에 없음(미검증).
- **US6951503B1** (Lam Research → Applied Materials 양도, 출원 2004-06-28·등록
  2005-10-04), "System and method for in-situ measuring and monitoring CMP polishing pad
  thickness": 와전류센서(ECS) 한 쌍을 패드 양면에 대고 차동측정 Δd=(d1−d1′)+(d2−d2′)로
  패드 자체의 정렬 오차를 상쇄한다. "패드의 한 부위라도 약 100 μm 마모되면" 검출 가능하다고
  명시(=분해능 지표이지 교체임계값은 아님). 교체 기준은 "CMP 결과가 미리 정한 성능 수준
  아래로 떨어지면 교체"로 서술 — 두께 자체보다 **성능 프록시**를 우선한다.
- **US20130217306A1** (TSMC, 출원 2012-02-16·공개 2013-08-22, **2015년 응답기한 미준수로
  포기(abandoned)** — 등록 안 됨, 공개공보로서만 인용): 음향 트랜스듀서로 패드에 펄스를
  쏘아 반사파의 도달시간 또는 위상차로 그루브 깊이를 잰다. "측정된 그루브 깊이가 미리 정한
  값보다 작으면 패드가 소진된 것"이라고만 서술하고 구체적 수치는 공개하지 않음(미검증).
- **US20120225612A1**(원출원인 개인, 이후 Micron Technology에 양도, 우선권 2006-04-06·
  공개 2012-09-06), "Method of Manufacture of Constant Groove Depth Pads": 일반적인 패드
  두께 T1 ≈ 50–80 mil(1.3–2.0 mm), 초기 그루브 깊이 D1 ≈ 30–50 mil(0.75–1.25 mm)이라는
  **업계 통상값**을 배경기술로 제시하고, 그루브 하부에 충전재를 넣어 마모가 진행돼도
  깊이가 D2로 거의 유지되게 하는 구조를 제안한다(패드 마모 자체는 여전히 진행, 예시값
  "약 0.25 μm/wafer"). 이 노트가 확보한 유일한 "정상 패드의 그루브 깊이 범위" 수치다.

## 4. 경제성: 패드 소모품 비용과 교체 기준의 연결

**출처**: US5595527A (Texas Instruments Inc., 출원 1995-06-07·등록 1997-01-21), "Application
of semiconductor IC fabrication techniques to the manufacturing of a conditioning head for
pad conditioning during chemical-mechanical polish": 배경기술 서술에서 "polishing pads ...
as much as five dollars per product wafer run"이라 하고, "multilevel interconnect systems
each wafer can use five or six CMP steps ... cost for polishing pads alone $25 to $30 per
wafer"라고 명시한다. 1997년 특허라 **최근 15년 우선 원칙에서 벗어난 고전급 자료**이며
달러 가치 자체는 30년 가까이 지나 그대로 쓸 수 없지만(미검증·물가 미보정), **CMP 스텝당
패드비용이 대략 고정되어 있고 웨이퍼당 비용은 스텝 수에 비례한다**는 구조적 관계는 이
노트가 확인할 수 있는 유일한 1차 경제성 근거다. 이보다 최신이고 정량적인 CoO 논문
("Pad surface management as a strategy to reduce the cost of ownership for CMP", IEEE ASMC
2010, doi.org/10.1109/asmc.2010.5551459)은 Unpaywall/OpenAlex에 OA 사본이 없고 미러 사이트
전 미러가 응답하지 않아(2026-09-07 재확인, 이전 회차 메모와 동일 증상) **미확보**로
남긴다 — 이 회차는 초록 이하 수준도 인용하지 않는다(정직성 원칙).

패드비용 자체의 최신 수치가 없으므로, 이 노트는 §2의 Son & Lee(2021) 실측(마모율·수명
비)과 §4의 구조적 관계(비용 ∝ 1/수명)를 결합해 **이 노트에서 직접 계산한** 경제성
추정치를 제시한다(문헌이 보고한 수치가 아니라 이 노트의 산술 추정임을 명확히 표시):
Case II가 Case I 대비 관찰된 실험 종료 시점 기준 수명비 20/16=1.25배만 늘었다고 보수적으로
가정하면 패드당 웨이퍼 처리량 증가로 웨이퍼당 소모품비가 약 20% 감소하고, 컷레이트 역수비
43.4/22.2≈1.95배까지 실제로 수명이 늘어난다고 낙관적으로 가정하면 약 49% 감소한다(§5
verify (D) 계산). 이 범위는 앞서 검색 스니펫에서 나온 "패드 수명 10~20% 개선 시 CoO
수백만원~10~15% 절감" 류의 업계 서술과 오더 수준으로는 부합하지만, 그 스니펫 자체는
1차 출처를 확보하지 못해 이 노트에는 인용하지 않는다(확인 못함).

## 5. 정량 재현 (python verify)

재현 요약(한 줄): (Son & Lee 2021, doi.org/10.3390/app11083521) Case I/II 컷레이트비
43.4/22.2 μm/h≈1.95배는 MRR 감소율비(44.9%/7.4%≈6.1배)보다 훨씬 작아 국소 불균일마모의
비선형 영향을 재확인하고, 그루브 소멸 시점 누적마모량(694 μm)은 (US20120225612A1) 통상
초기 그루브 깊이 하한(750 μm)의 93%로 물리적으로 정합하며, (US6951503B1) 100 μm 분해능은
두 조건 모두 그루브 소멸(16 h/20 h)보다 훨씬 이른 2.3 h/4.5 h 시점에 마모를 검출할 수 있다.

```python verify
# ── (A) Son & Lee 2021, Appl. Sci. 11, 3521, doi.org/10.3390/app11083521 — 원문 수치 그대로
cutI, cutII = 43.4, 22.2          # μm/h, 실측 평균 패드 컷레이트
tI, tII = 16.0, 20.0              # h, 그루브 소멸/실험 종료 시점
mrrI0, mrrI1 = 401.3, 221.0       # nm/min
mrrII0, mrrII1 = 387.7, 359.0     # nm/min

dropI = 1 - mrrI1 / mrrI0
dropII = 1 - mrrII1 / mrrII0
print(f"MRR 감소율: Case I {dropI*100:.1f}%, Case II {dropII*100:.1f}%")
assert abs(dropI - 0.449) < 0.005, "Case I MRR 감소율이 원문 44.9%와 다름"
assert abs(dropII - 0.074) < 0.005, "Case II MRR 감소율이 원문 7.4%와 다름"

ratio_cut = cutI / cutII
ratio_mrr_drop = dropI / dropII
print(f"컷레이트비 {ratio_cut:.2f}배, MRR감소율비 {ratio_mrr_drop:.2f}배")
assert 1.8 < ratio_cut < 2.1, "컷레이트비가 약 2배 범위를 벗어남"
assert ratio_mrr_drop > 5, "MRR 감소율비가 컷레이트비보다 훨씬 커야(불균일마모의 비선형 영향)"

# ── (B) 그루브 소멸 시점 누적마모량 vs US20120225612A1 통상 초기 그루브 깊이(0.75–1.25 mm)
cum_I = cutI * tI    # μm, Case I: 16 h 시점 그루브 완전 소멸(원문 SEM Fig.17b)
cum_II = cutII * tII  # μm, Case II: 20 h 시점 그루브 잔존(원문 SEM Fig.17c)
groove_lo, groove_hi = 750.0, 1250.0   # μm, US20120225612A1 "30-50 mil(0.75-1.25 mm)"
print(f"그루브 소멸 시점 누적마모: Case I {cum_I:.0f} μm, Case II {cum_II:.0f} μm "
      f"(통상 초기 그루브 깊이 {groove_lo:.0f}-{groove_hi:.0f} μm)")
assert 0.5 * groove_lo < cum_I < 1.3 * groove_lo, \
    "Case I 누적마모량이 통상 그루브 깊이 하한과 물리적으로 정합하지 않음"
assert cum_II < groove_lo, "Case II는 20h에도 그루브가 남아야 하므로 누적마모가 하한보다 작아야 함"
# 서로 다른 패드/컨디셔너 조합이라 정확히 같을 이유는 없다 — 근접성만 확인(미검증 수준의 정합)

# ── (C) US6951503B1 분해능(100 μm)으로 그루브 소멸보다 얼마나 일찍 마모를 검출할 수 있는가
detect_thresh = 100.0  # μm, "worn down by as little as about 100 micron"
t_detect_I = detect_thresh / cutI
t_detect_II = detect_thresh / cutII
print(f"100 μm 검출 소요시간: Case I {t_detect_I:.2f} h, Case II {t_detect_II:.2f} h "
      f"(그루브 소멸 {tI:.0f}/{tII:.0f} h보다 훨씬 이름)")
assert t_detect_I < tI * 0.2 and t_detect_II < tII * 0.3, \
    "와전류센서 분해능이 그루브 소멸 시점보다 충분히 이르게 마모를 잡아내지 못함"

# ── (D) 경제성: 패드 수명비 → 웨이퍼당 소모품비 감소율 (이 노트의 산술 추정, 문헌 수치 아님)
lifetime_ratio_conservative = tII / tI          # 실험이 실제로 관찰한 하한(20/16)
lifetime_ratio_optimistic = cutI / cutII        # 컷레이트 역수로 추정한 상한(43.4/22.2)
cost_cut_conservative = 1 - 1 / lifetime_ratio_conservative
cost_cut_optimistic = 1 - 1 / lifetime_ratio_optimistic
print(f"웨이퍼당 소모품비 절감 추정: 보수 {cost_cut_conservative*100:.0f}% "
      f"(수명비 {lifetime_ratio_conservative:.2f}배) ~ 낙관 {cost_cut_optimistic*100:.0f}% "
      f"(수명비 {lifetime_ratio_optimistic:.2f}배)")
assert 0.15 < cost_cut_conservative < 0.25
assert 0.4 < cost_cut_optimistic < 0.55
# US5595527A(1997)의 "$25-30/wafer, 스텝당 $5" 구조적 관계(비용 ∝ 스텝수, 스텝당비용 고정)만
# 확인용으로 재현한다 — 달러 절대값은 30년 전 것이라 이 verify에 넣지 않는다(미검증)
cost_per_step, steps_lo, steps_hi = 5.0, 5, 6
assert 25.0 <= cost_per_step * steps_lo <= cost_per_step * steps_hi <= 30.0

print("PASS: (A)~(D) 전부 문헌 수치 재현/대조 및 노트 자체 추정 계산 통과")
```

## 6. 부모·형제 노트와의 연결

- [[pad-glazing-mechanism-mrr-decay]] §2는 접촉점 수·반경(μm 스케일)의 시간의존 변화로
  MRR 감소를 설명했다. 이 노트의 그루브 깊이(mm 스케일)는 **같은 컨디셔닝 마모 공정이
  만들어내는 별개 실패 모드**다 — Son & Lee(2021)의 Case I은 두 실패 모드(불균일 접촉에
  의한 MRR 급락과 그루브 물리적 소멸)가 같은 16 h 부근에서 동시에 나타난 사례로, glazing과
  그루브 마모가 독립이 아니라 국소 과다마모라는 공통 원인에서 함께 나올 수 있음을 보여준다
  (완전한 인과분리는 이 논문만으로 불가, 미검증).
- [[pad-conditioning-wear-regeneration-balance]] §1의 "Cut Rate < Wear Rate → severe
  glazing"이라는 Lawing(2004)의 정성적 기준에 비해, 이 노트 §2의 패드 컷레이트(43.4 vs
  22.2 μm/h)는 **정량적 시간축 마모율**이라 sim/의 시간의존 Kp 보정(Lv3-2 예정)에 직접
  대입 가능한 형태다.
- [[pad-breakin-asperity-mrr-runup]]이 다루는 초기 수십 분 스케일의 asperity 재편과 달리,
  이 노트의 그루브 마모는 수십 시간 스케일이다 — 같은 패드의 수명 주기 안에서 시간축이
  최소 asperity(분) < glazing(수 분~수십 분) < 그루브(수 시간~수십 시간)로 3단 분리된다는
  것이 이 세 노트를 합쳐 보이는 그림이다(이 3단 분리 자체는 이 노트가 처음 명시적으로
  정리한 것이라 교차검증된 문헌 근거는 없음, 미검증).

## 7. 미검증·한계 표기 (정직성)

- Son & Lee(2021) 원문 PDF 파일은 확보하지 못했다(MDPI 서버 Akamai 차단) — `r.jina.ai`
  리더가 반환한 HTML→마크다운 변환 텍스트로 본문·표 전체를 읽었으나, 그래프(Fig.7~16)의
  구체 수치는 본문 서술과 표(Table 1~4)로만 확인했고 그래프 자체는 판독하지 못했다.
- US20130217306A1은 등록되지 않고 포기된 출원이다 — 청구항이 특허로 확정된 적이 없다.
  US7198546B2·US6951503B1·US5595527A는 등록특허다.
- §4의 경제성 절감률(20~49%)은 **이 노트가 두 출처를 조합해 계산한 추정치**이지 어느
  논문도 이 숫자 자체를 보고하지 않았다 — "패드 수명 X% 개선 → 소모품비 X% 절감"이라는
  비례관계 자체가 처리량·가동률 등 다른 변수를 무시한 1차 근사임을 명시한다.
- "Pad surface management..." (IEEE ASMC 2010, doi.org/10.1109/asmc.2010.5551459) 등
  이번 회차에 OA·미러 사이트 모두 실패한 유료 논문은 인용하지 않았다(확인 못함).
- US20120225612A1의 "0.25 μm/wafer" 마모율은 그 특허의 특정 얕은 그루브(≈250 μm) 설계
  예시 값이라 일반 패드에 그대로 적용할 수 없다(불명, 조건부 수치).

## 8. 출처 요약 (한 줄 형식)
- Jungyu Son, Hyunseop Lee (2021), "Contact-Area-Changeable CMP Conditioning for Enhancing Pad Lifetime", *Applied Sciences* 11(8), 3521, doi.org/10.3390/app11083521 — OA 전문(HTML) 확보·직접 읽음(1차).
- US7198546B2, LSI Logic Corp., "Method to monitor pad wear in CMP processing" (출원 2004, 등록 2007) — 등록특허, Google Patents 전문 확인(1차).
- US6951503B1, Lam Research Corp. (Applied Materials 양도), "System and method for in-situ measuring and monitoring CMP polishing pad thickness" (출원 2004, 등록 2005) — 등록특허, Google Patents 전문 확인(1차).
- US20130217306A1, TSMC, "CMP Groove Depth and Conditioning Disk Monitoring" (출원 2012, 공개 2013, 포기됨) — 공개특허출원, Google Patents 전문 확인(1차, 미등록).
- US20120225612A1, Micron Technology, "Method of Manufacture of Constant Groove Depth Pads" (우선권 2006, 공개 2012) — 등록특허, Google Patents 전문 확인(1차).
- US5595527A, Texas Instruments Inc., "Application of semiconductor IC fabrication techniques ... conditioning head ..." (출원 1995, 등록 1997) — 등록특허, Google Patents 전문 확인(1차, 고전급 경제성 배경기술).
