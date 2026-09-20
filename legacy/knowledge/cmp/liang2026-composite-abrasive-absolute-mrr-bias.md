# 판정#57 — liang2026 4H-SiC 복합연마입자 절대 MRR 3.97배 편향

작성: 2026-09-18 · 담당: 정확도루프(성장엔진) · 대상 팩: `sic_ceria_h2o2`
관련: [[sic-preston-coefficient-pack-own-declaration]],
[[sic-kmno4-alumina-absolute-mrr-patent-vs-papers]]

## 0. 출처

- Liang, Juan; Zhang, Yan; et al., "Chemical mechanical polishing on silicon
  carbide using developed ceria composite abrasives and their synergistic
  polishing mechanism", Nano Research (2026), doi:10.26599/NR.2026.94909100 —
  Tsinghua University Press, CC-BY. 로컬 PDF 확보(`papers/nr2026-ceria-composite-abrasive-sic-cmp.pdf`).
  §2.3 본문 인쇄값만 사용(그래프 판독 아님).
- Wang et al., figshare:31056549 (ACS SI Table S3, CC BY-NC 4.0) — 이 팩의
  Kp 앵커점(S3-27) 및 pH 항 캘리브레이션(pH 9~11) 출처.
- Su, Y. et al., Procedia Engineering(2011) — `su2011_procengr_6hsic_alumina_abrasive_conc`
  held-out 데이터셋 출처(6H-SiC + 알루미나).
- 방법론은 판정#55, `knowledge/cmp/sic-kmno4-alumina-absolute-mrr-patent-vs-papers.md`
  에서 그대로 가져왔다(k* 정규화 정의).

## 1. 무엇이 문제였나

`tools/accuracy_gaps.py` 최상위(점수 50) 갭:

    BIAS | liang2026_4hsic_ceria_composite_h2o2_conc
         | 순위는 맞는데(ρ=+1.000, p=0.042) 절대값 3.97배 계통편향

갭 랭커의 처방은 "Kp 또는 ref 조건을 데이터셋에 맞추거나 팩을 분리"다. 그런데
판정#55 가 정확히 같은 처방을 받고 실행해 보니 **원자료 쪽이 이상치**였던
전례가 있다(`entegris2022...` 23.04배 편향 — Kp를 올렸으면 held-out 이 17배
더 나빠질 뻔했다). 이번에도 같은 도구(k* 정규화)로 먼저 확인한다.

이 데이터셋 자체는 이미 등록 시점(2026-09-16)에 계 경계를 상세히 신고해
뒀다: 연마입자가 순수 세리아가 아니라 **CuxO-CeO2/Al2O3 복합**(질량 대부분
알루미나), **pH 7 중성**(팩 기준 pH 10, Wang DOE 캘리브레이션 범위는 9~11),
CuxO **Fenton-유사 촉매** 존재, 농도축 최대 9 wt%(Wang DOE 캘리브레이션
범위는 2~6 wt%). scope_note 는 "절대 MRR 대조는 의미가 없고 방향성만
테스트 대상"이라고 이미 선언했다 — 이번 회차는 그 선언을 `rank_only` 로
하네스에 실제로 반영할지, 아니면 Kp 를 손댈지를 실행해서 정한다.

## 2. Q1 — Preston 정규화 k* 대조: 원자료가 이상치인가?

k* ≡ MRR[nm/min] / (P[Pa]·rpm) (판정#55 정의 그대로, 장비조건 걷어낸 상대량).

| 출처 | 조건 | 실측 MRR | k* |
|------|------|----------|-----|
| Liang 2026, abrasive 1 wt%(H2O2 8%, pH7) | 4.3511 psi, 90 rpm | 3.809 nm/min | 1.411e-06 |
| Liang 2026, abrasive 5 wt%(기준 조성) | 4.3511 psi, 90 rpm | 8.974 nm/min | 3.324e-06 |
| Liang 2026, abrasive 9 wt% | 4.3511 psi, 90 rpm | 10.358 nm/min | 3.836e-06 |
| Liang 2026, H2O2 10 wt% | 4.3511 psi, 90 rpm | 9.513 nm/min | 3.523e-06 |
| **Wang figshare:31056549 S3-27(Kp 앵커점)** | 4.5 psi, 60 rpm | 3.309 nm/min | **1.777e-06** |
| Wang DOE50 전체(n=50) | 다양 | — | 중앙 1.862e-06, 범위 6.593e-07~6.593e-06(10배) |

**결과: Liang 4점의 k*(1.41e-06~3.84e-06)는 Wang DOE50 전체 산포(10배 범위) 안에
완전히 들어가고, Kp 앵커점(1.777e-06) 대비로도 0.79~2.16배 — 판정#55가 세운
"동일 재료계 정상 산포 ≈1.5배" 기준의 살짝 밖이지만 한 자릿수 근처에도
못 미친다.** 즉 **원자료의 날 것 속도(raw rate)는 이상치가 아니다** —
같은 자릿수의 정상적인 SiC CMP 속도다. 판정#55의 특허 사례(38배 이상)와는
질적으로 다르다.

**문헌값 대조(정량):** Liang et al. 2026(doi:10.26599/NR.2026.94909100) 기준 조성(5 wt%, H2O2 8 wt%, pH7) 실측 8.974 nm/min(@4.3511 psi·90 rpm) → k*=3.324e-06 vs Wang DOE(figshare:31056549) 앵커점(S3-27) 실측 3.309 nm/min(@4.5 psi·60 rpm) → k*=1.777e-06, 비 1.87배 — 판정#55가
세운 문헌 간 정상산포(1.5배)에 근접하고, 그 판정이 이상치로 판정한 특허
사례(24.8~38.3배)와는 두 자릿수 차이로 질적으로 다르다.

그렇다면 3.97배는 어디서 나오는가 — Kp(스케일 상수)가 아니라 **함수형태
(pH 항)의 외삽**에서 나온다는 것을 §3에서 직접 확인했다.

## 3. 3.97배의 원인 — pH 항을 캘리브레이션 범위(9~11) 밖(7)으로 외삽

팩의 `ph_softening_per_unit`(0.2787)은 Wang DOE 의 **pH 9~11** 구간에서
역산됐다(sic_ceria_h2o2.yaml 자체 선언). Liang 2026 은 pH **7** — 범위 최소값보다
2 단위 낮다. 같은 연마입자·산화제 농도를 pH만 바꿔 넣어 보면:

| pH | 5 wt% 예측 (nm/min) | 실측 8.974 대비 obs/pred |
|----|---------------------|--------------------------|
| 10 (팩 기준, Wang 캘리브레이션 중심) | 5.6543 | 1.587배 |
| 9 (Wang 캘리브레이션 최소값) | 3.9105 | 2.295배 |
| **7 (Liang 실제값, 캘리브레이션 범위 밖)** | **2.2727** | **3.949배** |

pH 를 캘리브레이션 범위 안(9~10)으로 두면 편향이 1.6~2.3배로 떨어진다 —
판정#55 기준(~1.5배)에 근접한다. 범위 밖(7)으로 나갈수록 단조적으로
악화된다. 즉 **모델이 틀린 게 아니라, 캘리브레이션 안 된 정의역으로
외삽했을 때 나는 오차**다. 여기에 더해 (a) CuxO Fenton-유사 촉매 경로가
이 팩의 화학층에 아예 없고, (b) 연마입자 농도 9 wt%가 Wang DOE 캘리브레이션
최대치(6 wt%)를 넘는다 — 둘 다 같은 방향(모델이 실측보다 낮게 예측)으로
작용해 3.97배까지 벌어진다.

## 4. Q2 — Kp 를 조정하면 다른 데이터셋이 어떻게 되는가 (실행 결과)

처방대로 Kp 를 3.97배 올려 Liang 을 맞추는 실험을 **실행**했다
(현재 1.4144e-15 → 가상값 5.6131e-15):

| 데이터셋 | 현재 Kp 계통편향 | Kp×3.97 후 계통편향 |
|----------|------------------|----------------------|
| liang2026 (목표) | 3.969배 | 1.000배 (맞춰짐) |
| sic2026_ceria_h2o2_ph_DOE50 (n=50, 캘리브레이션 데이터) | **0.957배(양호)** | **0.241배(4.1배 과대예측으로 반전)** |
| su2011_procengr_6hsic_alumina_abrasive_conc (n=3, held-out) | **1.078배(양호)** | **0.272배(3.7배 과대예측으로 반전)** |

**하나(Liang, 캘리브레이션에 쓰이지 않은 held-out)를 맞추면 캘리브레이션
데이터 자체(DOE50, n=50)와 다른 held-out(su2011, n=3)이 둘 다 3.7~4배
반대방향으로 틀어진다.** 이 팩의 Kp 는 이미 두 독립 계열(Wang DOE 자체 +
su2011 held-out)에서 정합이 확인된 값이므로, Liang 하나 때문에 건드리면
안 된다 — 판정#55 §3의 "하나를 맞추면 셋이 틀어진다"와 같은 패턴이다.

## 5. 판정

1. **팩 `sic_ceria_h2o2`의 Kp(1.4144e-15)는 불변.** 이번 회차에 팩 파일은
   한 글자도 바꾸지 않았다.
2. 이 데이터셋의 **절대값 판정만 면제**한다(`rank_only: true` +
   `rank_only_ruling:`). 근거는 §2~§4: 원자료 raw rate 는 정상 범위이고,
   편향은 캘리브레이션 정의역(pH 9~11, 연마입자 ≤6 wt%) 밖으로의 외삽 +
   미모델링 Fenton 촉매 경로에서 나온다 — Kp 스케일 결함이 아니다.
3. **순위는 그대로 집계한다.** ρ=+1.000, p=0.042 유지. 이 데이터셋은
   abrasive_conc_exponent 부호(+0.227, 판정#52)의 교차확인 근거로 계속
   쓰인다 — calibration_contact 신고는 이미 데이터셋에 있다.

⚠ 이것은 "안 맞아서 뺀 것"이 아니다. 절대값 판정만 면제했고, 근거는 §4의
반사실 실험(Kp 조정 시 다른 두 데이터셋이 반대로 틀어짐)과 §3의 정의역
외삽 확인이다.

## 6. 새로 확인한 지식

- 판정#55의 k* 정상산포(~1.5배) 기준이 **이번에도 유효했다** — 다만 이번
  사례는 "원자료 이상치"가 아니라 "정상 원자료 + 함수형태 외삽 오차"라는
  다른 종류의 원인으로 판명났다. k* 하나만으로는 이 둘을 못 가른다 —
  raw rate 대조(§2)로 "Kp 문제 아님"을 확인한 뒤, 조건별 재예측(§3)으로
  "그럼 무엇이 원인인가"를 추가로 확인해야 했다.
- **캘리브레이션 정의역 밖 예측은 데이터셋 자체가 아니라 팩 파라미터
  노트에 정의역을 명시해 두는 것이 다음 회차의 시간을 아낀다** — 이번에
  `ph_softening_per_unit` 의 유효 범위(pH 9~11)가 어디에도 숫자로
  적혀 있지 않아 처음부터 다시 역산해야 했다.

## 7. 한계 (정직하게)

- pH 항의 함수형태 자체(1 - k·ΔpH 선형)가 pH 9~11 의 좁은 구간에서
  역산됐으므로, pH 7 에서의 "정답" 형태가 선형인지 여부는 **미검증**이다 —
  §3 의 표는 "범위 밖으로 갈수록 나빠진다"는 방향성만 보여준다.
- CuxO Fenton 경로가 편향에 정량적으로 얼마나 기여하는지는 **분리하지
  못했다**(pH 외삽과 뒤섞여 있다) — 이 논문만으로는 두 효과를 못 가른다.
- Liang 2026 은 CC-BY 오픈액세스 1차 출처(로컬 PDF 확보, §2.3 본문
  인쇄값)이므로 출처 등급 자체는 문제 없다.

## 8. 재현 (verify)

```python verify
import sys
sys.path.insert(0, ".")
from sim.engine import Recipe, simulate
import sim.models
import numpy as np
import yaml

def kstar(mrr_nm_per_min, p_psi, rpm):
    """Preston 정규화 상수 k* = MRR / (P[Pa] * rpm). 문헌 간 상대 비교용."""
    return mrr_nm_per_min / (p_psi * 6894.76 * rpm)

# ── §2: Liang 4점의 raw k* 가 Wang DOE50 산포 안에 있는가 ──────────────
liang = [3.8090, 8.9742, 10.3578, 9.5127]
k_liang = [kstar(m, 4.3511, 90) for m in liang]

d = yaml.safe_load(open("validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml"))
k_wang = [kstar(c["mrr_nm_per_min"], c["pressure_psi"], c["rpm_platen"])
          for c in d["conditions"]]
assert len(k_wang) == 50, len(k_wang)

k_wang_center = kstar(3.3087, 4.5, 60)  # S3-27, Kp 앵커점
assert 1.7e-06 < k_wang_center < 1.9e-06, k_wang_center

# Liang 의 raw k* 는 전부 Wang DOE50 전체 범위(min~max) 안에 있다
assert min(k_wang) <= min(k_liang) and max(k_liang) <= max(k_wang), \
    (min(k_wang), min(k_liang), max(k_liang), max(k_wang))

# Kp 앵커점 대비 Liang 비율은 한 자릿수 안(<3배)이다 — 판정#55 이상치(38배)와 질적으로 다르다
ratios = [k / k_wang_center for k in k_liang]
assert max(ratios) < 3.0, ratios

# ── §3: pH 를 캘리브레이션 범위 안으로 되돌리면 편향이 줄어든다 ─────────
def pred(abrasive, oxidizer, ph, p_psi=4.3511, rpm=90):
    r = Recipe(pack="sic_ceria_h2o2", pack_overrides={
        "abrasive_wt_pct": abrasive, "oxidizer_wt_pct": oxidizer,
        "slurry_ph": ph, "sfr_ml_min": 30,
    }, pressure_psi=p_psi, rpm_wafer=rpm, rpm_platen=rpm)
    res = simulate(r, model="tier2.gw_physical_kp")
    return float(np.mean(res.mrr_nm_per_min))

obs_5wt = 8.9742
bias_ph7 = obs_5wt / pred(5, 8, 7)
bias_ph9 = obs_5wt / pred(5, 8, 9)
bias_ph10 = obs_5wt / pred(5, 8, 10)

assert 3.9 < bias_ph7 < 4.0, bias_ph7      # 실제 조건(범위 밖) — 갭 랭커가 잡은 3.97배와 일치
assert 2.2 < bias_ph9 < 2.4, bias_ph9      # 캘리브레이션 최소값
assert 1.5 < bias_ph10 < 1.7, bias_ph10    # 팩 기준(캘리브레이션 중심)
assert bias_ph7 > bias_ph9 > bias_ph10     # 범위 밖으로 갈수록 단조 악화

# ── §4: Kp 를 3.97배 올려 Liang 을 맞추면 다른 데이터셋이 반대로 틀어진다 ─
def scale_with_kp(path, kp_override):
    raw = yaml.safe_load(open(path))
    obs, pred_ = [], []
    for c in raw["conditions"]:
        if "mrr_nm_per_min" not in c:
            continue
        ov = dict(c.get("overrides") or {})
        r = Recipe(pack=raw["pack"], pack_overrides=ov,
                   pressure_psi=c.get("pressure_psi"), rpm_wafer=c.get("rpm_wafer"),
                   rpm_platen=c.get("rpm_platen"), kp_m_per_pa=kp_override)
        res = simulate(r, model="tier2.gw_physical_kp")
        pred_.append(float(np.mean(res.mrr_nm_per_min)))
        obs.append(float(c["mrr_nm_per_min"]))
    return float(np.median([o / p for o, p in zip(obs, pred_) if p]))

current_kp = 1.4144e-15
factor = bias_ph7  # ≈3.969, Liang 을 맞추는 데 필요한 배율
new_kp = current_kp * factor

s_doe50_before = scale_with_kp("validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml", current_kp)
s_doe50_after = scale_with_kp("validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml", new_kp)
s_su2011_before = scale_with_kp("validation/datasets/su2011_procengr_6hsic_alumina_abrasive_conc.yaml", current_kp)
s_su2011_after = scale_with_kp("validation/datasets/su2011_procengr_6hsic_alumina_abrasive_conc.yaml", new_kp)

assert 0.9 < s_doe50_before < 1.05, s_doe50_before      # 현재: 양호
assert s_doe50_after < 0.3, s_doe50_after               # Kp 올리면: 3배 이상 과대예측으로 반전
assert 0.95 < s_su2011_before < 1.2, s_su2011_before    # 현재: 양호
assert s_su2011_after < 0.35, s_su2011_after            # Kp 올리면: 반전
```
