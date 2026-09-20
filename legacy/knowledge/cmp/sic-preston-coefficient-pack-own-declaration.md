<!-- V2-SECTION: R2-slurry | 정확도루프 BIAS sic2026_ceria_h2o2_ph_DOE50 2026-09-16 -->
# SiC CMP의 Preston 계수 — 상속된 산화막 Kp를 끊고, 레짐별로 쪼갠 기록

> slurry-chemist Lv3 확장 | 작성일: 2026-09-16 | EVIDENCE-RULES 판정#49
> 선행: [[sic-alumina-concentration-negative-exponent-entegris]]
> [[sic-abrasive-concentration-regime-ruling]] [[ceria-slurry-ce-redox-selectivity]]
> 스코프: slurry-chemist. 대상 팩: `sic_ceria_h2o2`, 신설 `sic_alumina_kmno4`.

## 1. 무엇이 틀려 있었나

`tools/accuracy_gaps.py --next` 최우선 갭:
`sic2026_ceria_h2o2_ph_DOE50: 순위는 맞는데(p=0.002) 절대값 0.01배 계통편향`.

원인을 역추적하니 `sic_ceria_h2o2` 팩에 **`kp_m_per_pa` 자체 선언이 없었다.**
상속 사슬은 `base → oxide_silica → sti_ceria → sic_ceria_h2o2` 이고, 실제로 쓰이던
값 2.2e-13 m²/N 은 `sti_ceria`의 것, 즉 **세리아 슬러리로 깎은 Si 산화막(SiO₂)**
에서 역산된 값이다. 연마입자(세리아)만 같고 **피삭재가 다르다**.

이 저장소의 `sim/pack_meta.py`는 같은 팩을 두고 이미 이렇게 적고 있었다:
"경도가 높아 MRR이 Si 대비 2~3자리 낮다". 즉 문서는 알고 있었고 파라미터만
몰랐다. 판정#48(κ 농도항이 실리카 부모의 20 wt%를 상속)과 **같은 종류의
하이진 결함**이다 — 팩 상속은 편리하지만, 재료계가 바뀌는 경계에서
자기선언을 빠뜨리면 조용히 틀린다.

## 2. 1차 출처

- **Wang et al.**, "Machine Learning-Driven Optimization of Silicon Carbide Chemical
  Mechanical Polishing with Surface Roughness Constraints", ACS Supporting Information
  Table S3 "Original Polish dataset" (figshare:31056549, CC BY-NC 4.0).
  4H-SiC + CeO₂ 2/4/6 wt% + H₂O₂ 2/4/6 vol% + pH 9/10/11, 4.5/5.0/5.5 psi,
  head·platen 60/80 rpm, 50조건 완전 DOE. 이미
  `validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml`에 등록됨.
- **Wei et al. 2026**, Crystals 16, 179, **DOI 10.3390/cryst16030179** (MDPI 오픈액세스,
  `papers/wei2026-cryst16030179-4hsic-fenton-cmp.pdf` 원문 확보).
  4H-SiC C면, 콜로이달 실리카 8 wt%(110 nm) + H₂O₂ 5 wt% + Fe₃O₄ 0.03 wt%, pH 9,
  34.5 kPa, 패드·웨이퍼 각 50 rpm, 60 min → 최대 **701 nm/h**(Table 3 + 본문).
- **Wang W., Liu W., Song Z. 2021**, ECS J. Solid State Sci. Technol. 10, 074004,
  **DOI 10.1149/2162-8777/ac12de**. 4H-SiC Si면, Al₂O₃ + KMnO₄, pH 2, 6 psi, 90 rpm
  → **1.4 µm/h**. ⚠ 원문 미확보 — 리뷰 DOI 10.3390/mi13101752 §2 본문에 인쇄된
  수치를 옮긴 **2차 인용(E5)**.
- **Chen G. et al. 2015**, Appl. Surf. Sci. 359, 664-668,
  **DOI 10.1016/j.apsusc.2015.10.158**. 6H-SiC Si면, CeO₂ + KMnO₄, pH 2, 4 psi, 90 rpm
  → **1.089 µm/h**. ⚠ 같은 리뷰 경유 2차 인용(E5), 원문 미확보.
- **US20220315802A1** (Entegris / U. Florida) Table 1. SiC CMP, KMnO₄ 4 wt% + 질산염,
  pH 2.3, Al₂O₃ 0.1~5.0 wt%, 1 psi/60 rpm → **1.2~5.8 µm/h**. Google Patents 전문 무료.

## 3. 같은 "SiC CMP"에서 실측이 130배 갈린다

Preston 정규화(P×V로 나눠 비교)를 하지 않은 원 MRR만 늘어놔도 층이 보인다.

| 계 | 산화제 / pH | 연마입자 | 실측 MRR | 출처 |
|---|---|---|---|---|
| 알칼리 세리아 | H₂O₂ / pH 9~11 | CeO₂ 나노 | 0.12~0.96 µm/h | Wang ACS SI S3 |
| 알칼리 실리카+Fenton | H₂O₂+Fe₃O₄ / pH 9 | SiO₂ 110 nm | 0.70 µm/h | DOI 10.3390/cryst16030179 |
| 알칼리 알루미나 | 미상 / pH 9 | Al₂O₃ 마이크론 | 0.045~0.070 µm/h | DOI 10.1016/j.proeng.2011.11.2673 |
| **산성 강산화** | KMnO₄ / pH 2 | CeO₂ | 1.089 µm/h | DOI 10.1016/j.apsusc.2015.10.158 |
| **산성 강산화** | KMnO₄ / pH 2 | Al₂O₃ | 1.4 µm/h | DOI 10.1149/2162-8777/ac12de |
| **산성 강산화(특허)** | KMnO₄ / pH 2.3 | Al₂O₃ | 1.2~5.8 µm/h | US20220315802A1 T1 |

EVIDENCE-RULES §"그래도 안 갈리면 스코프를 쪼개라"의 전형이다. 하나의 Kp로
덮으면 어느 쪽도 맞지 않는다. 그래서 **팩을 둘로 나눴다**:
알칼리 세리아/H₂O₂ = `sic_ceria_h2o2`, 산성 KMnO₄/알루미나 = 신설 `sic_alumina_kmno4`
(base 상속).

## 4. Kp 역산 — 기준 조건에서 풀었다

기준 조건의 정의는 "팩이 선언한 모든 ref와 일치해 무차원 팩터가 1.0이 되는 점"이다.

```python verify
# ── 1) sic_ceria_h2o2: Wang ACS SI Table S3 의 DOE 중심점 S3-27 에서 역산
#    (CeO2 4 wt% = abrasive_ref_wt_pct, H2O2 4 vol% = oxidizer_ref_wt_pct,
#     pH 10 = ph_ref/ph_softening_ref → 조성축 배수 전부 1.0)
kp_old = 2.2e-13            # 상속되던 sti_ceria(Si 산화막) 값, m^2/N
pred_old = 514.6539         # 그 Kp로 S3-27을 엔진에 넣은 예측, nm/min (실행 확인값)
obs = 3.3087                # Wang ACS SI Table S3 S3-27 실측 198.52 nm/h / 60
kp_new = kp_old * obs / pred_old
assert abs(kp_new - 1.4144e-15) / 1.4144e-15 < 1e-3, f"{kp_new:.5e}"
# 산화막 Kp 대비 몇 배나 작은가 -- pack_meta 의 "Si 대비 2~3자리 낮다"와 대조
ratio = kp_old / kp_new
assert 100 < ratio < 1000, f"자릿수 주장과 불일치: {ratio:.0f}배"
print(f"sic_ceria_h2o2 Kp = {kp_new:.4e} m^2/N (산화막 Kp의 1/{ratio:.0f})")

# ── 2) 독립 확인: Wei 2026 (다른 논문, 같은 4H-SiC + H2O2 알칼리)
#    엔진 실행 예측 1.43 nm/min vs 실측 701 nm/h
obs_wei = 701.0 / 60.0
pred_wei = 1.43
assert abs(obs_wei - 11.683) < 0.01
r = pred_wei / obs_wei
# 8배 과소예측 -- "일치"라고 부르지 않는다. 연마입자가 실리카이고 C면이며
# Fenton 촉매가 있다. 자릿수(1자리 이내)만 맞는다는 주장만 assert 한다.
assert 0.05 < r < 0.5, f"자릿수도 안 맞음: {r:.3f}"
# 옛 Kp 였다면 같은 조건에서 몇 배 틀렸을까
r_old = r * (kp_old / kp_new)
assert r_old > 10, "옛 Kp가 더 나았다면 이 변경은 틀린 것이다"
print(f"Wei2026 대조: 새 Kp {r:.2f}배 vs 옛 Kp {r_old:.0f}배 — 개선 방향 확인")

# ── 3) sic_alumina_kmno4: 논문 2편이 서로 독립적으로 일치, 특허만 이상치
#    Preston 정규화 MRR/(P*V) 로 비교한다. V ∝ rpm 이므로 비례상수는 소거된다.
def norm(mrr_um_h, psi, rpm):
    return mrr_um_h / (psi * rpm)
wang2021 = norm(1.4,   6.0, 90)    # DOI 10.1149/2162-8777/ac12de
chen2015 = norm(1.089, 4.0, 90)    # DOI 10.1016/j.apsusc.2015.10.158
entegris = norm(4.5,   1.0, 60)    # US20220315802A1 Table 1 3행
# 논문 2편은 서로 1.2배 이내 -- 독립 확인으로 쓸 수 있다
assert abs(wang2021 / chen2015 - 1.0) < 0.25, f"{wang2021/chen2015:.2f}"
# 특허는 논문 대비 한 자릿수 이상 높다 -- 이상치로 판정한 근거
assert entegris / wang2021 > 10, f"{entegris/wang2021:.1f}"
print(f"정규화 MRR: Wang2021 {wang2021:.5f}, Chen2015 {chen2015:.5f}, "
      f"특허 {entegris:.5f} (논문 대비 {entegris/wang2021:.0f}배)")
```

판정: 같은 E3~E5 등급이면 **독립 확인 수**로 깬다(EVIDENCE-RULES §4). 서로 다른
연구팀의 논문 2편이 정규화 기준 1.2배 이내로 일치하고 특허 하나만 29배 높으므로,
`sic_alumina_kmno4`의 Kp는 **논문 쪽(Wang 2021)에서 역산**했다:
엔진 실행 예측 675.04 nm/min이 실측 23.333 nm/min이 되도록 풀어 **4.9872e-15 m²/N**.

## 5. 새로 도출한 지식

1. **팩 상속 사슬이 재료계 경계를 넘을 때 Kp는 반드시 자기선언해야 한다.**
   `kp_m_per_pa`는 다른 파라미터와 달리 "그 재료를 그 메커니즘으로 깎을 때의
   비례상수"라 피삭재가 바뀌면 의미가 없어진다. 그런데 상속은 조용히 성공한다.
   → `sim/params.py`에 "재료계 전환 키(film)가 오버라이드된 팩은 Kp도
   자기선언해야 한다"는 검사를 넣을 것을 제안한다(구현 요청, §7).
2. **SiC CMP는 단일 계가 아니다.** 산화제 강도(H₂O₂ vs KMnO₄)와 pH가 Preston
   정규화 MRR을 100배 가른다. "SiC 슬러리" 하나로 모델링하면 안 된다.
3. **특허 실시예 수치는 논문과 같은 등급으로 취급하면 안 된다.** 이번 건에서
   특허(US20220315802A1)만 29배 높았고, 독립 논문 2편은 서로 1.2배 이내였다.
   특허는 방향(순위) 근거로는 쓰되 절대값 앵커로는 논문 뒤에 둔다.

## 6. 미검증·한계 (덮지 않고 적는다)

- Wang 2021·Chen 2015 **원문 미확보**(ECS·Elsevier 유료). 수치는 오픈액세스 리뷰
  DOI 10.3390/mi13101752 §2 본문 인쇄값을 옮긴 2차 인용이다.
- `sic_alumina_kmno4` Kp 역산 시 **Wang 2021의 알루미나 농도를 0.5 wt%로 가정**했다
  (리뷰가 농도를 적지 않음). 실제 농도가 다르면 농도항 배수만큼 Kp가 틀린다.
- `sic_ceria_h2o2` Kp는 **자기 캘리브레이션**이다(같은 DOE가 `ph_softening_per_unit`
  출처이기도 하다). 이 팩의 절대 MRR은 held-out으로 검증된 적이 없다.
- Wei 2026 대조에서 남은 **8배 과소예측**의 원인은 미상이다. C면/Si면 이방성
  (같은 리뷰 §2: C면이 Si면의 2~3배), 실리카 vs 세리아 연마입자, Fenton 촉매가
  뒤섞여 있어 단일 원인으로 귀속할 수 없다.
- US20220315802A1 데이터셋은 새 팩에서도 **23배 계통편향**이 남는다. 이는 위
  이상치 판정의 직접적 귀결이며, 그 데이터셋은 held-out(순위 ρ=+1.000, p=0.008)
  으로만 쓴다.

## 7. 구현 요청 (소프트웨어 부문)

- **무엇을**: `sim/params.py` 로드 시 경고 — 팩이 `film`을 자기선언(오버라이드)했는데
  `kp_m_per_pa`를 자기선언하지 않았으면 WARN. 입출력: 팩 이름 → 경고 목록.
- **근거 노트**: 이 문서 §1, §5-1.
- **검증에 쓸 값**: 이번 수정 전 `sic_ceria_h2o2`가 정확히 이 상태였다(film=sic_4h
  자기선언, Kp 상속) — 회귀 테스트로 쓸 수 있다.
- **우선순위**: 중. 같은 결함이 판정#48·#49로 두 번 반복됐다.
