# 산성 KMnO4/알루미나 SiC CMP 의 절대 MRR — 특허 실시예 vs 논문 3편 (판정#55)

작성: 2026-09-16 · 담당: 정확도루프(성장엔진) · 대상 팩: `sic_alumina_kmno4`
관련: [[sic-ceria-abrasive-concentration-sign-reversal-ruling]],
[[sic-alumina-concentration-negative-exponent-entegris]],
[[sic-preston-coefficient-pack-own-declaration]]

## 1. 무엇이 문제였나

`tools/accuracy_gaps.py` 가 여러 회차에 걸쳐 같은 항목을 최상위 갭으로 올렸다:

    BIAS | entegris2022_us20220315802a1_sic_alumina_conc
         | 순위는 맞는데(p=0.008) 절대값 23.04배 계통편향

갭 랭커의 처방은 "팩 Kp 를 데이터셋 조건에 맞추거나 팩을 분리하라"다. 그런데
팩 분리는 **이미 판정#49-B 에서 했다**(`sic_ceria_h2o2` → `sic_alumina_kmno4`).
분리 후에도 23배가 남았다는 것은, 이 편향의 원인이 "한 팩에 두 레짐이 섞였다"가
아니라 **둘 중 하나가 절대값에서 이상치**라는 뜻이다. 어느 쪽인지 갈라야 한다.

## 2. 판정 방법 — Preston 정규화로 장비 조건을 걷어낸다

특허와 논문은 압력·회전수가 서로 다르다(특허 1 psi/60 rpm vs 논문 4~6 psi/90 rpm).
Preston 관계 MRR = Kp·P·V 에서 절대 MRR 을 그대로 비교하면 이 차이가 섞인다.
그래서 **정규화 상수**를 정의해 비교한다:

    k* ≡ MRR[nm/min] / (P[Pa] · rpm_platen)

k* 는 Preston 계수에 비례하는 양이고(선속도 V ∝ rpm), 같은 재료계·같은 화학이면
문헌끼리 같은 자릿수여야 한다. 단위는 임의(문헌 간 비교용 상대량)다.

비교 대상은 **재료계가 일치하는 것만** 골랐다 — 4H/6H-SiC + 알루미나(또는 세리아)
연마입자 + **KMnO4 산화제 + 산성 pH**:

| 출처 | 계 | 조건 | 실측 MRR | k* | 등급 |
|------|-----|------|----------|-----|------|
| Gong et al. 2024, doi:10.3390/ma17030679 Table 2 (L25, n=25, MDPI CC-BY, 로컬 전문 XML) | 4H-SiC(0001) Si면, Al2O3 500 nm, KMnO4 1~5 wt%, pH 2~6 | 4 psi, platen 90 rpm | 0.46~0.83 μm/h (중앙 0.705) | **4.735e-06** | E3(인쇄표, 1차) |
| Wang W. et al. 2021, doi:10.1149/2162-8777/ac12de | 4H-SiC Si면, Al2O3 + KMnO4, pH 2 | 6 psi, 90 rpm | 1.4 μm/h | **6.267e-06** | E5(리뷰 doi:10.3390/mi13101752 §2 경유 2차인용) |
| Chen G. et al. 2015, doi:10.1016/j.apsusc.2015.10.158 | 6H-SiC Si면, CeO2 + KMnO4, pH 2 | 4 psi, 90 rpm | 1.089 μm/h | **7.312e-06** | E5(2차인용) |
| **US20220315802A1 Table 1**(Entegris/U.Florida, n=5) | SiC, Al2O3 나노 0.1~5 wt%, KMnO4 4 wt% + 질산염, pH 2.3 | 1 psi, 60 rpm | 1.2~5.8 μm/h (중앙 4.5) | **1.813e-04** | E3(특허 실시예, 검증 없음) |

## 3. 결과 — 논문 3편은 모이고 특허만 떨어져 있다

- 논문 3편의 k* 는 **4.735e-06 ~ 7.312e-06**, 즉 서로 **1.54배** 안에 있다.
  연마입자가 알루미나(Gong·Wang)와 세리아(Chen)로 갈리고 폴리타입도 4H/6H 로
  갈리는데도 이 정도로 모인다.
- 이 특허는 **1.813e-04** 로, 논문 최대값의 **24.8배**, 최소값의 **38.3배**다.
- 특허의 **가장 느린 조건**(1.2 μm/h, Al2O3 5 wt%)조차 논문 최대값의 **6.6배**다.
  즉 특허 표 전체가 논문 구간 밖에 있고, 표 안의 산포로 설명되지 않는다.

**문헌값 대조(정량):** Gong 2024(doi:10.3390/ma17030679) 실측 중앙값 11.753 nm/min
(@4 psi·90 rpm) → k*=4.735e-06 vs 이 특허(US20220315802A1) Table 1 중앙값 75.0 nm/min
(@1 psi·60 rpm) → k*=1.813e-04, 비 **38.3배**.
Wang 2021(doi:10.1149/2162-8777/ac12de) 23.333 nm/min(@6 psi·90 rpm) → k*=6.267e-06,
특허 대비 **28.9배**.
Chen 2015(doi:10.1016/j.apsusc.2015.10.158) 18.150 nm/min(@4 psi·90 rpm) → k*=7.312e-06,
특허 대비 **24.8배** — 논문 3편 중 가장 관대한 대조값이다.
논문 3편끼리의 대조는 **1.54배**(doi:10.3390/ma17030679 ↔ doi:10.1016/j.apsusc.2015.10.158)에 그친다.

**하나를 맞추면 셋이 틀어진다.** 팩 Kp 를 23.04배 올려 이 특허를 맞추면,
같은 팩의 held-out 인 Gong 2024(n=25)의 계통편향이 현재 1.336배(양호)에서
**0.058배(17.2배 과대예측)** 로 뒤집힌다. 실제 백테스트 실행값으로 확인했다.

## 4. 판정 (EVIDENCE-RULES)

특허 실시예와 논문 실측은 둘 다 **E3(교란 있는 실측)** 이다. 등급이 같으므로
§서열 파괴 규칙대로 **재현가능성·독립 확인 수**로 깬다:

> 서로 독립적으로 일치하는 문헌 3편 > 검증 없이 인쇄된 특허 실시예 1건.

따라서:

1. **팩 `sic_alumina_kmno4` 의 Kp 는 논문 쪽에 고정한다** — 값·근거 모두 불변이다
   (이미 Wang 2021 기준 4.9872e-15). 이번 회차에 팩은 한 글자도 바꾸지 않았다.
2. 이 데이터셋의 **절대값 판정만 면제**한다(`rank_only: true` + 근거 문자열 필수).
   `tools/outlier_rules.py` 의 **C3(rank_only)** 와 같은 취급이다 — 제거가 아니다.
3. **순위는 그대로 집계한다.** ρ=+1.000, p=0.008 은 유지된다. Spearman 은 Kp
   스케일에 불변이고, 이 특허는 이 팩의 **유일한 조성 1축 스윕**(0.1→5 wt%, n=5)
   이라 `abrasive_conc_exponent = -0.406` 의 근거로 계속 필요하다.

⚠ 이것은 "안 맞아서 뺀 것"이 아니다. 뺀 것은 데이터가 아니라 **절대값 판정**이고,
근거는 지표 개선이 아니라 §3 의 독립 문헌 3편 정규화 일치다. 플래그를 켜려면
데이터셋에 `rank_only_ruling:` 로 근거를 적어야 하며, 없으면 백테스트가
경고를 내고 플래그를 무시한다(`validation/backtest.py`).

## 5. 새로 도출한 지식

- **정규화 상수 k* = MRR/(P·rpm) 는 문헌 간 절대 MRR 이상치 판정의 실용 도구다.**
  같은 재료계·같은 산화제라면 압력·rpm 이 2~6배 달라도 k* 가 1.5배 안에 모인다는
  것을 SiC/KMnO4 계 3편에서 확인했다. 이 폭(≈1.5배)이 앞으로 "문헌 간 정상 산포"의
  기준선이 된다 — 그 밖으로 한 자릿수 이상 벗어나면 Kp 갭이 아니라 원자료를 의심한다.
- **특허 실시예 MRR 은 계통적으로 낙관적일 수 있다.** 이 저장소에서 두 번째 사례다
  (판정#49-A 에서도 같은 특허가 130배 이상치로 잡혔다). 특허 수치를 **순위 근거**로
  쓰는 것과 **절대값 근거**로 쓰는 것을 분리해야 한다.

## 6. 한계 (정직하게)

- Wang 2021·Chen 2015 는 **원문 미확보**다. 리뷰(doi:10.3390/mi13101752 §2)에
  인쇄된 값을 옮긴 **2차 인용(E5)** 이다. 다만 판정의 무게는 1차 전문을 확보한
  Gong 2024(k*=4.735e-06, n=25)가 특허와 **38배** 벌어진다는 사실 하나로도 유지된다
  — 2차 인용 2편을 빼도 결론이 바뀌지 않는다.
- 특허가 왜 높은지의 **원인은 모른다**. 하소 알루미나(0.5~5 μm) 추가 조성이
  실제로 그만큼 빠를 가능성을 배제하지 못한다(특허 본문은 염소산염·과염소산염
  추가로 25~30% 향상을 주장하는데, 25~30%는 24배를 설명하지 못한다). 원인 미상으로
  남긴다.
- k* 는 패드·컨디셔닝·슬러리 유량을 걷어내지 못한다. 특허는 이들 조건을 표에
  인쇄하지 않았다(Google Patents·FreePatentsOnline 전문 양쪽에서 확인 — 두 판본 모두
  Table 1 의 장비 조건 행이 없다). **미검증** 요인으로 남는다.

## 7. 재현 (verify)

```python verify
import math
import yaml
import numpy as np

def kstar(mrr_nm_per_min, p_psi, rpm):
    """Preston 정규화 상수 k* = MRR / (P[Pa] * rpm). 문헌 간 상대 비교용."""
    return mrr_nm_per_min / (p_psi * 6894.76 * rpm)

# ── 문헌값(상수로 박는다) ───────────────────────────────────
# Gong et al. 2024, doi:10.3390/ma17030679, Table 2 — 로컬 데이터셋에서 읽는다
g = [c["mrr_nm_per_min"] for c in
     yaml.safe_load(open("validation/datasets/gong2024_4hsic_alumina_kmno4_L25.yaml"))["conditions"]]
assert len(g) == 25, len(g)
k_gong = kstar(float(np.median(g)), 4.0, 90)

# Wang W. et al. 2021, doi:10.1149/2162-8777/ac12de — 1.4 um/h @ 6 psi, 90 rpm (2차인용)
k_wang = kstar(1400.0 / 60.0, 6.0, 90)
# Chen G. et al. 2015, doi:10.1016/j.apsusc.2015.10.158 — 1.089 um/h @ 4 psi, 90 rpm (2차인용)
k_chen = kstar(1089.0 / 60.0, 4.0, 90)

# US20220315802A1 Table 1 — 로컬 데이터셋에서 읽는다
e = [c["mrr_nm_per_min"] for c in
     yaml.safe_load(open("validation/datasets/entegris2022_us20220315802a1_sic_alumina_conc.yaml"))["conditions"]]
assert len(e) == 5, len(e)
k_pat = kstar(float(np.median(e)), 1.0, 60)

# ① 논문 3편은 1.6배 안에 모인다
papers = [k_gong, k_wang, k_chen]
spread = max(papers) / min(papers)
assert 1.0 < spread < 1.6, spread

# ② 특허는 논문 최대값보다 한 자릿수 이상 높다
assert k_pat / max(papers) > 10.0, k_pat / max(papers)
assert 24.0 < k_pat / max(papers) < 26.0, k_pat / max(papers)
assert 38.0 < k_pat / min(papers) < 39.0, k_pat / min(papers)

# ③ 특허의 가장 느린 조건조차 논문 최대값보다 빠르다 (표 내 산포로 설명 불가)
k_pat_slowest = kstar(min(e), 1.0, 60)
assert k_pat_slowest / max(papers) > 6.0, k_pat_slowest / max(papers)

# ④ 특허에 Kp 를 맞추면 Gong 편향이 뒤집힌다 (백테스트 실측 배수로 확인)
bias_gong_now = 1.336        # 실행값: validation/backtest.py, obs/pred 중앙값
bias_patent_now = 23.04      # 실행값: 같은 출처
bias_gong_after = bias_gong_now / bias_patent_now
assert bias_gong_after < 0.06, bias_gong_after      # 17배 과대예측으로 전환
assert 1.0 / bias_gong_after > 17.0

# ⑤ 데이터셋이 판정을 근거와 함께 신고하고 있는가 (근거 없는 면제 금지)
raw = yaml.safe_load(open("validation/datasets/entegris2022_us20220315802a1_sic_alumina_conc.yaml"))
assert raw.get("rank_only") is True
assert len(str(raw.get("rank_only_ruling", ""))) > 200
assert raw.get("used_for_calibration") is False

print(f"k* Gong={k_gong:.4g} Wang={k_wang:.4g} Chen={k_chen:.4g} | 특허={k_pat:.4g}")
print(f"논문 3편 산포 {spread:.2f}배 / 특허는 논문 최대 대비 {k_pat/max(papers):.1f}배")
```

## 8. 출처

- Gong J., Wang W., Liu W., Song Z., *Polishing Mechanism of CMP 4H-SiC Crystal
  Substrate (0001) Si Surface Based on an Alumina (Al2O3) Abrasive*, Materials
  17(3) 679 (2024). **doi:10.3390/ma17030679** (MDPI CC-BY, 전문 XML 로컬 확보:
  `data/corpus/fulltext/doi_10.3390_ma17030679.xml`)
- Wang W., Liu W., Song Z., ECS J. Solid State Sci. Technol. 10 (2021) 074004.
  **doi:10.1149/2162-8777/ac12de** — ⚠ 원문 미확보, 리뷰 경유 2차 인용
- Chen G. et al., Appl. Surf. Sci. 359 (2015) 664-668.
  **doi:10.1016/j.apsusc.2015.10.158** — ⚠ 원문 미확보, 2차 인용
- 리뷰: *Recent Advances In Silicon Carbide Chemical Mechanical Polishing
  Technologies*, Micromachines 13 (2022) 1752. **doi:10.3390/mi13101752** §2
  (MDPI CC-BY, 로컬 전문 확보)
- 특허: **US20220315802A1** (Entegris Inc / University of Florida Research
  Foundation), Table 1. Google Patents / FreePatentsOnline 전문 확인.
