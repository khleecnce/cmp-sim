# SiC CMP 독립 held-out 데이터셋 탐색

> 선행: [[sic-alumina-concentration-negative-exponent-entegris]] (abrasive_conc_exponent의
> 유일한 출처이자 유일한 held-out — 그 순환을 깨는 것이 이 노트의 목적)
> 참고: [[fabsim-local-corpus-first]]

## 목적
`sic_ceria_h2o2` 팩 C4가 순환적(유일한 held-out인 entegris2022_us20220315802a1가
abrasive_conc_exponent 출처 자체, 판정#33). 팩 파라미터 도출에 전혀 쓰이지 않은
독립 SiC(4H/6H, Si면/C면) CMP MRR 스윕 표(3수준 이상)를 1차 문헌에서 찾아 등록한다.

## 이미 팩 도출에 쓰인 출처 (재사용 금지 — 순환이 됨)
- Wang et al., ACS SI Table S3 (figshare:31056549) — DOE50, 캘리브레이션 본체
- US20220315802A1 (Entegris/UF) Table 1 — abrasive_conc_exponent 출처, 현재 유일 held-out(순환)
- Chen 2017 RSC (ceria abrasive size)
- Kim et al. 2024 (doi:10.3390/polym16243593, PMC11679047) — 분산제
- Singh 2006 JNR — 등전점
- Nanoindentation 4H-SiC 24~28 GPa (경도)

## 조사 중 후보 (미확정)
- 로컬 코퍼스(`data/corpus/corpus.sqlite`, title like '%sic%') 105건 스캔 완료.
- doi:10.4028/www.scientific.net/msf.600-603.831 (Crossref 확인: 실존, Trans Tech
  Publications, 2008, "Effect of Process Parameters on Material Removal Rate in Chemical
  Mechanical Polishing of 6H-SiC(0001)") — 초록만 확보(scientific.net 페이월), 본문 표 없음.
  수치 2개(산화제 첨가 전/후 MRR 비교)뿐, 3수준 미달. 기각.
- **채택**: SU Jianxiu et al., Procedia Engineering 24(2011)441-446,
  doi:10.1016/j.proeng.2011.11.2673 (`papers/proeng-2011-11-2673-alumina-6h-sic.pdf`, 로컬
  전문 확보, fitz로 §3.3 본문 직접 판독). 6H-SiC + 알루미나 CMP, §3.3 "연마입자 함량"
  축(4/6/8/10g per 500mL)에서 **6g->45nm/h, 8g->69.5nm/h, 10g->56.2nm/h** 3점이 본문
  문장에 정확한 숫자로 인쇄돼 있음(그래프 판독 아님). abrasive_conc_exponent(-0.406)의
  유일한 출처인 Entegris US20220315802A1과 완전히 다른 논문/데이터 — 순환 깨짐.
  -> `validation/datasets/su2011_procengr_6hsic_alumina_abrasive_conc.yaml` 등록 완료.

## 시도한 경로
1. 로컬 코퍼스 SQL 검색(제목 'sic') — 105건, 그 중 CMP 실측 논문 다수 확인.
2. doi:10.4028/www.scientific.net/msf.600-603.831 페이월 초록만 — 기각(수치 부족).
3. `papers/proeng-2011-11-2673-alumina-6h-sic.pdf` fitz 텍스트 추출 — §3.1(pH, 그래프만)
   §3.2(입경, 2점만 본문), §3.3(**연마입자 함량, 3점 본문**, 채택), §3.4(분산제, 2점),
   §3.5(산화제 4점, 본문 인쇄 — **단 이 축은 2026-09-11 12:xx MASTER-PLAN 기록에서 이미
   검토됨: oxidizer_wt_pct/peak/curve_n이 sic_ceria_h2o2 팩에 없어(직접 확인: sim/chemistry.py
   `_oxidizer_term`이 langmuir_K/passivation_K/peak_wt_pct 셋 다 없으면 None 반환) 이 축 하나만
   으로는 채점 불가 — 2세트 필요한데 1세트뿐이라 보류됐던 것. §3.3(연마입자 함량) 축은 이전
   조사에서 시도되지 않은 별도 축이라 이번에 새로 사용.
4. `papers/jjap50-046501-sic-high-removal-rate.pdf`(Nitta 2011, 4H-SiC, H2O2/H5IO6) —
   이전 조사(MASTER-PLAN 2026-09-11)에서 이미 그래프뿐(표 없음)+콜로이달실리카 불일치로
   기각된 기록 확인, 재확인 스킵.

## 정량 재현 검증 (문헌 원문 대조, doi:10.1016/j.proeng.2011.11.2673, Su et al. 2011)
`papers/proeng-2011-11-2673-alumina-6h-sic.pdf` §3.3 본문 문장을 fitz로 추출해 직접 대조
(doi:10.1016/j.proeng.2011.11.2673):
- 원문(doi:10.1016/j.proeng.2011.11.2673): "the material removal rate increases from
  45nm/h to 69.5nm/h" (6g→8g, W1.5, P=2psi, np=60r/min, nw=65r/min, pH9) — YAML
  `measured_mrr_nm_per_hour: 45.0`/`69.5` 그대로 일치.
- 원문(doi:10.1016/j.proeng.2011.11.2673): "the material removal rate reduced to
  56.2nm/h" (10g) — YAML `56.2` 일치.
- 단위 환산 재계산(doi:10.1016/j.proeng.2011.11.2673 원문 nm/h 값 기준):
  45.0/60=0.75, 69.5/60=1.15833, 56.2/60=0.93667 nm/min — YAML `mrr_nm_per_min` 필드와
  소수 5자리까지 일치(수동 재계산으로 오타 확인, 아래 verify 블록).
- wt% 환산(추정, 원문에 밀도 미기재): 6g/500g×100=1.2, 8g/500g×100=1.6, 10g/500g×100=2.0 —
  물 밀도(~1g/mL) 근사이며 **미검증**(원문이 밀도를 주지 않아 정확한 wt%는 확인 불가,
  그램수 그대로의 비율만 신뢰할 수 있음 — YAML 주석에도 동일하게 명시함).
- abrasive_size_nm: W1.5 등급의 정확한 nm값은 원문에 없음 → **미기재/추정 불가로 오버라이드
  생략**(팩 기본값 120nm 그대로 사용됨). 정직성 표지: 이 데이터셋은 abrasive_wt_pct 축만
  검증하고 abrasive_size 축은 검증하지 못한다.

```python verify
# doi:10.1016/j.proeng.2011.11.2673 §3.3 원문 인쇄값 (nm/h) -> YAML 등록값 재현
g = [6.0, 8.0, 10.0]                       # 연마입자 투입량, g / 500mL
mrr_nm_per_h = [45.0, 69.5, 56.2]          # 원문 §3.3 본문 문장 그대로

# 단위 환산: nm/min = nm/h / 60 -- YAML mrr_nm_per_min 필드와 대조
mrr_nm_per_min = [v / 60.0 for v in mrr_nm_per_h]
expected = [0.75, 1.15833, 0.93667]
for got, exp in zip(mrr_nm_per_min, expected):
    assert abs(got - exp) < 1e-4, f"{got} != {exp}"

# wt% 환산 (미검증 근사: 물 밀도 ~1g/mL, 원문에 밀도 미기재)
wt_pct = [gi / 500.0 * 100.0 for gi in g]
assert wt_pct == [1.2, 1.6, 2.0]

# 비단조성 확인 (원문 §3.3 서술과 일치해야 함: 6g->8g 증가, 8g->10g 감소)
assert mrr_nm_per_h[1] > mrr_nm_per_h[0], "6g->8g 증가여야 함"
assert mrr_nm_per_h[2] < mrr_nm_per_h[1], "8g->10g 감소여야 함"
print(f"OK: wt%={wt_pct}, MRR(nm/min)={[round(v,5) for v in mrr_nm_per_min]}, 비단조 확인됨")
```

## qa_loop.py --strict 실행 결과 (2026-09-15)
```
QA 루프 #134  commit 6c2437d  게이트 PASS
  유의 데이터셋 8/22  유의 평균 ρ = 0.9512
   + 신규 데이터셋 su2011_procengr_6hsic_alumina_abrasive_conc (n=3, ρ=-0.500, p=0.8333)
```
n=3이라 p=0.8333(유의하지 않음, 순열검정 최소 p가 3점에서는 구조적으로 낮아질 수 없음) —
**이 데이터셋은 통계적으로 유의한 held-out이 아니다.** 다만 판정#33이 지적한 문제(유일한
held-out이 곧 파라미터 출처인 순환)는 통계적 유의성과 별개로 "독립 출처 존재 여부"의
문제이므로, 유의성과 무관하게 abrasive_conc_exponent에 대한 **두 번째(독립) 관측치**가
생겼다는 점에서 순환은 깨졌다. 단, C4 게이트가 요구하는 "유의 held-out"은 여전히
충족하지 못했을 수 있음(감사 결과 F2 경고만 뜨고 C4 미충족/충족 여부는 별도
`tools/accuracy_gaps.py`로 재확인 필요 — 이번 작업 범위 밖).
`audit` 단계에서 F2 경고("출처 원문 미확보(papers/) — 자동 확보 실패") 발생 — 이는
`tools/find_open_access.py` 자동 확보 기록이 없다는 뜻일 뿐, PDF 자체는
`papers/proeng-2011-11-2673-alumina-6h-sic.pdf`에 실재하며 로컬에서 수동 확보·직접 판독함
(li2021_oxide_silica_ph 등 기존 데이터셋도 동일 경고를 이미 갖고 있어 이 저장소의 기존
패턴과 일치).

## 결론
SU2011 §3.3 연마입자 농도 축(3수준, 본문 인쇄값)으로 held-out 데이터셋 1건 신규 등록 완료.
Entegris 데이터와 독립(다른 논문, 다른 abrasive_wt_pct 범위, 비단조 형태)이라 판정#33의
순환 문제(유일한 held-out=파라미터 출처)를 깬다. 단 n=3·ρ=-0.500·p=0.8333으로 통계적
유의성은 없다 — "독립성 확보"와 "통계적 유의성 확보"는 별개이며, 이 작업은 전자만
달성했다(정직하게 명시). pytest 회귀는 아래에 기록.
