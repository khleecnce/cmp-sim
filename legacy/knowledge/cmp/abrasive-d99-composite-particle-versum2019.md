<!-- V2-SECTION: R2-slurry | 작성 2026-09-09 | 정본: ARCHITECTURE-V2.md §3 -->
# 세리아-코팅 실리카 복합입자의 D50/D99 실측값과 산화막 제거율 상관 — Δ 팩터 abrasive_d99_nm 확보

> 에이전트: slurry-abrasive Lv2-1 | 작성일: 2026-09-09
> [[lpc-scratch-density-tail-correlation]] [[particle-wafer-interaction-mechanical-chemical-balance]]
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]

## 1. 왜 필요한가
정확도루프 UNMODELED delta 갭(score=100)의 선행 조건은 "각 팩에 `abrasive_d99_nm` 확보"였다
([[lpc-scratch-density-tail-correlation]] §4). 이 노트는 그 선행 조건을 처리한다: D99 실측값을
1차 문헌(특허)에서 확보하고, D99가 커질수록 산화막 제거율이 어떻게 변하는지(방향·오더)를
정량화한다.

## 2. 1차 문헌 — US 2019/0127607 A1 (Versum Materials US, LLC)
**"Composite Particles, Method of Fabrication, and Applications Thereof", 출원인 Versum
Materials US, LLC, 공개일 2019-05-02, 공개번호 US 2019/0127607 A1.**
USPTO 특허출원공개공보(무료 공개, patents.google.com에서 원문 PDF 직접 다운로드).
`papers/us20190127607a1-versum-ceria-coated-silica-d99.pdf`, `papers/INDEX.json` 등록.
[0007]: "Most of the ceria used in CMP industry are manufactured from calcinations-wet milling
process. The resulted ceria has sharp edges and very wide size distribution. It also has very
large 'large particle count' (LPC). All of these are believed to be responsible for defects and
low yields, especially scratch after the wafer is polished." — 세리아 계열 STI/ILD 산화막 CMP를
직접 다루며, [[lpc-scratch-density-tail-correlation]]과 같은 정성 문제의식(LPC→스크래치)을 공유.

### 2.1 실측 D50·D99 (Example 1, Table I — 원문 그대로)
4종의 세리아-코팅 실리카 복합입자(JGC & C Corporation, 일본 제조)를 DC(Disc Centrifuge) 또는
DLS로 측정:

| 입자 | D50 (nm) | D99 (nm) | D99−D50 (nm) | D50/(D99−D50) |
|---|---|---|---|---|
| A | 156.1 | 302.6 | 146.5 | 1.07 |
| B | 117.2 | 182.7 | 65.5 | 1.79 |
| C | 210.7 | 316.7 | 106.0 | 1.99 |
| D | 88.7 | 158.5 | 69.8 | 1.27 |

원문 정의([0031],[0015]): "D99 is a particle size that 99 wt.% of particles fall under and
under, and D50 is a particle size that 50 wt.% of particles fall on and under." — D99는
Remsen 2006이 다룬 LPC(임계 직경 이상 개수)와 다른 축이지만(누적분포 백분위수 vs 절대 개수),
[[lpc-scratch-density-tail-correlation]] §3-1에서 이미 짚은 근사 관계(둘 다 "꼬리")를 이 문헌이
실측으로 뒷받침한다 — 입자 D는 D99가 가장 좁고(158.5 nm) 입자 A가 가장 넓다(302.6 nm),
즉 D99 자체가 분포 폭(D99−D50)과 함께 움직이는 실측 사례.

### 2.2 산화막 제거율 vs 입도분포 (Example 2, Table II — 원문 그대로)
Mirra polisher(Applied Materials), 3.7 psi, platen 87 rpm, head 93 rpm, slurry flow
200 mL/min, in-situ conditioning 6 lb downforce. 각 입자를 0.185 wt% 농도로 단독 슬러리화
(0.14 wt% ammonium polyacrylate, pH 5.45).

| 입자 | HDP oxide RR (Å/min) | TEOS RR (Å/min) | TEOS/HDP 비 |
|---|---|---|---|
| A (D99=302.6) | 2041 | 1311 | 0.64 |
| B (D99=182.7) | 1807 | 1828 | 1.01 |
| C (D99=316.7) | 2299 | 2223 | 0.97 |
| D (D99=158.5) | 1158 | 875 | 0.76 |

[0121]: "Particle A with larger particle size distribution appeared to provide much higher
removal rates for HDP silicon dioxide films compared to a similar sized particle with narrower
particle size distribution." [0122]: "Particle D with smaller particle size similarly appeared
to provide higher removal rates for HDP silicon dioxide films compared to TEOS films."

### 2.3 Dishing/over-polish 민감도 vs 분포폭 (Example 3, Fig.3 — 원문 서술)
[0129]-[0130]: 트렌치 손실률/블랭킷 제거율(over-polish sensitivity)을 D50/(D90−D50)의 함수로
플롯. "smaller particles (such as particle D with size distribution of D50/(D90−D50)=1.27)
yields lower over-polish sensitivity. Moreover, as the particle size increases, the dishing for
larger 100 micron features become even worse." — 즉 **분포가 넓을수록(D99/D90 tail이 클수록)
패턴 dishing 민감도가 커진다** — 정성적으로만 서술, 원문에 표는 없고 그래프(Fig.3)만 있어
수치 좌표는 **미확보**(그래프 판독 불가, PDF 텍스트 추출로는 축값 없음).

## 3. sim/factors.py `_f_delta`에 대한 시사점
1. **abrasive_d99_nm 실측값 확보**: 158.5~316.7 nm 범위(세리아-코팅 실리카 복합입자, STI/ILD
   oxide CMP). 단, 이 값은 **원문 입자 자체의 D99이지 현재 5개 팩(cu_h2o2_bta, oxide_silica,
   sic_ceria_h2o2, sti_ceria, w_fe_oxidizer)이 실제로 쓰는 슬러리의 D99가 아니다** — Versum
   특허의 실시예 입자를 팩에 그대로 이식하면 조성 오귀속이다. **팩에 값을 채우지 않는다.**
   대신 이 노트는 "D99가 물리적으로 어떤 오더(수백 nm)이고 어떻게 측정되는지"를 확립해
   향후 각 팩의 실제 슬러리 스펙(제조사 문서)을 찾을 때 대조 기준으로 쓴다.
2. **D99 증가 → MRR 증가 방향 확인(oxide, 정량 재확인)**: Table II 4점을 D99 오름차순으로
   나열하면 D(158.5nm,1158)→B(182.7nm,1807)→A(302.6nm,2041)→C(316.7nm,2299) Å/min로
   **완전 단조 증가**(4/4 순서 일치, n=4로는 강한 신호). 단 구간별 기울기가 균일하지 않다 —
   D→B 구간(D99 +24.2nm)에서 RR이 +649 Å/min 뛰는데, A→C 구간(D99 +14.1nm)에서는
   +258 Å/min만 늘어 **같은 D99 증분에 대한 RR 반응이 일정하지 않다**(선형이 아니거나,
   조성 교란변수가 섞여 있다 — 코팅 두께·1차입자 개수 등 원문이 통제하지 않은 변수).
   → 방향(단조 증가)은 n=4로 확인됐으나 **함수형(선형/거듭제곱 등)은 이 데이터로 특정 불가**
   → **미검증**: D99-MRR 정량 함수형.
3. **Δ(손상)와 MRR(제거율)이 같은 방향으로 움직인다는 시사점**: D99가 큰 입자일수록 MRR도
   높고(§3-2) 스크래치 위험도 커진다는 것이 [[lpc-scratch-density-tail-correlation]]과
   합쳐지면 — **Δ와 λ(MRR 관련 팩터)가 완전히 독립적인 축이 아니라 상관될 수 있다**는 뜻이다.
   현재 `sim/factors.py`가 Δ를 별도 팩터로 분리한 설계 자체는 유지하되(스크래치는 사용자가
   따로 관리하는 리스크 축), "D99를 올리면 MRR도 오르고 Δ도 오른다"는 트레이드오프를 팩
   파라미터 문서에 명시할 필요 — **구현 요청 아님, 다음 단원(Cal-1)의 문서화 과제로 남김**.
4. **Δ 팩터 형태(선형 vs 거듭제곱)는 이 문헌으로 결정 불가**: Table II/III에 스크래치 카운트
   자체가 없다(dishing만 있음) — [[lpc-scratch-density-tail-correlation]] Table V의 결론(선형)을
   뒤집거나 보강하지 못한다. 형태 재검토 구현요청은 그대로 유지.

## 4. 수식 재현 (sanity check)

```python verify
# US 2019/0127607 A1 (Versum Materials), Table I & Table II 실측값 그대로
# 입자 A/B/C/D의 D99(nm)와 HDP oxide 제거율(Å/min)
d99_nm = {"A": 302.6, "B": 182.7, "C": 316.7, "D": 158.5}
hdp_rr = {"A": 2041, "B": 1807, "C": 2299, "D": 1158}

# 1) 방향성 계약: D99 최대(C)의 RR이 D99 최소(D)의 RR보다 커야 한다
d_min_key = min(d99_nm, key=d99_nm.get)   # D
d_max_key = max(d99_nm, key=d99_nm.get)   # C
assert d_min_key == "D" and d_max_key == "C", "원문 Table I 값 재확인 필요"
rr_at_min_d99 = hdp_rr[d_min_key]
rr_at_max_d99 = hdp_rr[d_max_key]
assert rr_at_max_d99 > rr_at_min_d99, (
    f"D99 최대({d99_nm[d_max_key]}nm)의 RR({rr_at_max_d99})이 "
    f"D99 최소({d99_nm[d_min_key]}nm)의 RR({rr_at_min_d99})보다 커야 한다 (원문 [0121] 방향)"
)
ratio_d99 = d99_nm[d_max_key] / d99_nm[d_min_key]
ratio_rr = rr_at_max_d99 / rr_at_min_d99
print(f"D99 비 (C/D) = {ratio_d99:.2f}, HDP RR 비 (C/D) = {ratio_rr:.2f}")

# 2) 완전 단조성 확인 — 4점 전부 D99 순서와 RR 순서가 일치하는지 (n=4, 강한 신호)
d99_sorted = sorted(d99_nm.items(), key=lambda kv: kv[1])
rr_in_d99_order = [hdp_rr[k] for k, _ in d99_sorted]
is_monotonic = all(rr_in_d99_order[i] <= rr_in_d99_order[i + 1]
                    for i in range(len(rr_in_d99_order) - 1))
print(f"D99 오름차순 정렬: {[k for k, v in d99_sorted]}, RR 순서: {rr_in_d99_order}")
assert is_monotonic, (
    "원문 Table I/II 4점이 D99-RR 완전 단조 증가라는 것이 이 노트의 §3-2 핵심 주장이다 — "
    "재계산 결과가 이를 깨면 노트를 다시 써야 한다."
)

# 3) 비선형성(기울기 불균일) 확인 — 구간별 D99 증분 대비 RR 증분이 다른지
gaps = []
for i in range(len(d99_sorted) - 1):
    k0, d0 = d99_sorted[i]
    k1, d1 = d99_sorted[i + 1]
    d_delta = d1 - d0
    rr_delta = hdp_rr[k1] - hdp_rr[k0]
    slope = rr_delta / d_delta
    gaps.append(slope)
    print(f"{k0}->{k1}: ΔD99={d_delta:.1f}nm, ΔRR={rr_delta}Å/min, 기울기={slope:.1f} (Å/min)/nm")
slope_ratio = max(gaps) / min(gaps)
assert slope_ratio > 1.3, (
    f"구간별 기울기가 거의 균일하면({slope_ratio:.2f}배 차이) 선형 근사가 성립한다는 뜻인데 "
    "이 노트는 '균일하지 않다'고 주장한다 — 재확인 필요."
)
print(f"구간별 기울기 최대/최소 비 = {slope_ratio:.2f} — 균일하지 않음(비선형 신호)")
```

## 4.1 정량 재현 결과 요약
위 verify 블록을 실행하면 D99 최대 입자 C(316.7 nm)의 HDP oxide 제거율 2299 Å/min이
D99 최소 입자 D(158.5 nm)의 1158 Å/min과 대조되어 **재현 결과 RR 비(C/D) = 1.99배,
D99 비(C/D) = 2.00배로 원문 Table I·II 문헌값과 정확히 일치**(같은 표에서 그대로 계산한
것이므로 일치가 당연 — 독립 재현이 아니라 표 내적 일관성 확인이고 모델 정확도는
**미검증**이다). 구간별 기울기는
D→B 26.8 (Å/min)/nm, B→A 1.95 (Å/min)/nm, A→C 18.3 (Å/min)/nm로 **최대/최소 비 13.7배**
차이가 나 선형 근사가 성립하지 않음을 문헌값 자체로 확인했다.

## 5. 한계·후속 (정직한 미검증 표기)
- ⚠ **미검증**: D99-MRR 정량 함수형(§3-2, n=4·교란변수로 회귀 불가) — Cal-1 단원 이전엔
  함수식화하지 않는다.
- ⚠ **미검증**: Example 3 dishing-분포폭 관계는 원문에 수치표가 없고 그래프 서술만 있어
  좌표를 확보하지 못함(1차 미확보, 그래프 판독 불가로 2차 인용 대체도 불가 — 정성 서술만 인용).
- **팩에 값 미기입**: 이 특허의 D99 실측값(158.5~316.7 nm)은 특정 실시예 입자의 값이며
  cu_h2o2_bta/oxide_silica/sic_ceria_h2o2/sti_ceria/w_fe_oxidizer 5개 팩 각각의 실제 조성과
  다르므로 그대로 이식하지 않는다. 팩 파라미터 확보는 각 팩의 화학종에 맞는 제조사 스펙시트
  탐색이 필요(다음 단원 과제, 여전히 선행 미해결).
- 스코프 준수: `tools/scope.py --agent slurry-abrasive --check` 통과(특허, weight 1.0),
  focus(입자 물성) 내 — 제형 자체는 다루지 않음.

## 6. 다음 단원
Lv2-1의 나머지(경도·형상·Hertz 압입)는 미이수. D99 팩 파라미터 자체 확보(제조사 스펙시트,
Cabot/Fujimi/Versum 실제 판매 제품 스펙)가 다음 우선순위 — 이 노트는 "물리적으로 D99가
어떤 오더인지, 어떻게 정의되는지"의 기준점만 세웠다.
