"""백테스트 하네스 — 공개 문헌 실험 데이터로 FabSim 예측을 검증한다.

왜 이것이 지금 가장 중요한가 (POSITIONING.md §5):
  FabSim의 파라미터는 대부분 문헌 역산치(confidence: estimated)이고 실측 검증은 0건이다.
  투자자·심사위원의 첫 질문은 "예측 정확도가 몇 %냐"이고, 지금 답이 없다.
  고객 없이, 혼자, 이번 달에 만들 수 있는 유일한 진짜 증거가 이것이다.

## 무엇을 재는가 — 절대 오차가 아니라 순위

우리가 파는 것은 "데모 대체"가 아니라 "데모 횟수 감축"이다(POSITIONING.md §3):
후보 조성 20개를 다 깎는 대신 계산으로 5개를 골라낸다.

  → 필요한 것은 **순위 정확도**이지 절대 정확도가 아니다.
  → A가 B보다 나은지만 맞히면 스크리닝 도구로 쓸모가 있다.

이건 목표를 낮춘 게 아니다. 순위는 계통오차(모든 예측이 일정 배수만큼 빗나감)에
불변이라서, 절대값을 못 맞혀도 순위는 맞을 수 있다. **달성 가능한 목표로 정확히
조준한 것**이고, 동시에 고객의 실제 질문에 맞는 지표다.

주 지표:
  - Spearman ρ  : 순위 상관 (−1~1). 스크리닝 유용성의 직접 척도
  - Kendall τ   : 쌍별 순위 일치. "두 조건 중 어느 쪽이 나은가"를 몇 % 맞히나
  - pairwise accuracy : τ를 (1+τ)/2로 환산한 직관적 승률
보조 지표(참고용, 주장 근거로 쓰지 말 것):
  - MAPE, 상대 스케일 인자(계통 편향 크기)

## 데이터셋 규약

datasets/*.yaml 한 파일 = 한 논문의 한 DOE. 반드시 포함:
  - source: 논문 서지 + DOI/URL (없으면 등록 거부)
  - conditions[]: 각 조건의 입력(압력·rpm·조성 등)과 실측 출력
  - 실측값은 논문에 인쇄된 숫자만. **그래프에서 눈으로 읽은 값은 read_method: digitized로
    반드시 표기한다.** 이 구분을 흐리면 검증 자체가 오염된다.

## 정직성 규약

- 데이터가 없으면 없다고 출력한다. 합성 데이터로 채우고 "검증했다"고 말하지 않는다.
- held-out 개념: 우리 팩 파라미터를 특정 논문에서 뽑았다면 그 논문으로 검증하면
  안 된다. 각 데이터셋에 `used_for_calibration: true/false`를 명시한다.
- 결과가 나쁘면 그것도 결과다. 어느 항이 틀렸는지가 다음 작업 목록이 된다.
"""
from __future__ import annotations

import sys
import itertools
import random
import datetime as _dt
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import yaml

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sim.engine import Recipe, simulate  # noqa: E402
import sim.models  # noqa: E402,F401  (모델 등록)

DATASET_DIR = Path(__file__).resolve().parent / "datasets"


# ── 순위 지표 (scipy 없이 직접 구현: 의존성 최소화 + 계산이 투명해야 한다) ──
def spearman_rho(x: List[float], y: List[float]) -> float:
    """순위 상관. 동점은 평균 순위로 처리한다."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = float(np.mean(rx)), float(np.mean(ry))
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def kendall_tau(x: List[float], y: List[float]) -> float:
    """쌍별 순위 일치도. 스크리닝에서 가장 직관적인 지표."""
    n = len(x)
    con = dis = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx, dy = x[i] - x[j], y[i] - y[j]
            s = dx * dy
            if s > 0:
                con += 1
            elif s < 0:
                dis += 1
    tot = con + dis
    return (con - dis) / tot if tot else float("nan")


@dataclass
class BacktestResult:
    dataset: str
    n: int
    spearman: float
    kendall: float
    pairwise_accuracy: float          # (1+τ)/2 — "둘 중 나은 쪽" 적중률
    mape_pct: Optional[float]         # 참고용
    scale_factor: Optional[float]     # 계통 편향: 실측/예측 중앙값
    in_scope: bool = True             # 팩이 이 재료계를 실제로 다루는가
    used_for_calibration: bool = False
    # 절대값 판정에서만 빼는 경우 — 순위는 그대로 쓴다(제거가 아니다).
    # outlier_rules.py 의 C3(rank_only)과 같은 성격이며, 데이터셋 자신이
    # `rank_only: true` + `rank_only_ruling:` 로 **근거를 적었을 때만** 켜진다.
    rank_only: bool = False
    rank_only_ruling: str = ""
    calibration_contact: bool = False  # 이 데이터셋에서 팩 파라미터를 뽑은 이력(부분 오염) 신고 여부
    source: str = ""
    notes: List[str] = field(default_factory=list)
    p_value: Optional[float] = None   # 순열검정 — 우연히 이만큼 맞을 확률
    # 원자료 — 오차 분해(계통편향 vs 형상오차)에 필요하다.
    # 요약 지표만 남기면 "배율을 맞춘 뒤에도 남는 어긋남"을 사후에 잴 수 없다.
    observed: List[float] = field(default_factory=list)
    predicted: List[float] = field(default_factory=list)
    # 이상치 판정(tools/outlier_rules.py)이 **규칙으로** 판정하려면 조건 입력이
    # 필요하다. 이게 없으면 "정의역 밖(C2)"을 전혀 가릴 수 없고, 모든 점이
    # "설명 불가(C5)"로 떨어져 규칙이 작동하는 척만 하게 된다 — 실제로 그랬다.
    pack: str = ""
    rows: List[dict] = field(default_factory=list)

    #: 유의 판정 기준. n=3은 최소 p가 0.167이라 **구조적으로** 이 문턱을 넘을 수 없다.
    P_THRESHOLD = 0.05

    @property
    def significant(self) -> bool:
        return self.p_value is not None and self.p_value < self.P_THRESHOLD

    def verdict(self) -> str:
        if not self.in_scope:
            return "범위밖(팩이 이 재료계를 안 다룸)"
        if np.isnan(self.spearman):
            return "판정불가(분산 없음)"
        if self.used_for_calibration:
            return "참고용(캘리브레이션에 쓴 데이터 — 검증 아님)"
        if self.rank_only:
            # 절대값은 이 데이터셋 자체가 다른 문헌과 어긋난다는 판정이 있다.
            # 순위 판정은 그대로 이어서 낸다 — 아래 로직을 막지 않는다.
            pass
        # ⚠ 유의성을 먼저 본다. ρ가 아무리 높아도 우연과 구분이 안 되면
        #   '사용 가능'이라 말할 수 없다 — n=3의 ρ=1.000이 정확히 그 경우다.
        if not self.significant:
            p = f"p={self.p_value:.3f}" if self.p_value is not None else "p=?"
            return f"유의하지 않음({p}, n={self.n}) — 우연과 구분 불가"
        if self.spearman >= 0.8:
            return "스크리닝 사용 가능"
        if self.spearman >= 0.5:
            return "부분적 — 개선 필요"
        return "스크리닝 불가"

    def line(self) -> str:
        m = f"{self.mape_pct:.1f}%" if self.mape_pct is not None else "—"
        p = f"p={self.p_value:.3f}" if self.p_value is not None else "p=—"
        flag = " [순위전용]" if self.rank_only else ""
        return (f"{self.dataset:34s} n={self.n:3d}  ρ={self.spearman:+.3f}  "
                f"τ={self.kendall:+.3f}  {p:>9s}  "
                f"MAPE={m:>7s}  {self.verdict()}{flag}")


def perm_p_value(rho: float, n: int, iters: int = 20000,
                 seed: int = 0) -> Optional[float]:
    """관측 ρ 이상이 **무작위 순열에서** 나올 확률 (단측 정확/몬테카를로 순열검정).

    ⚠ 왜 이게 반드시 필요한가 (2026-09-08에 실제로 잡은 함정):
      n=3에서 ρ=+1.000은 **완벽한 예측처럼 보이지만 p=0.167이다** — 6가지 순열 중
      하나라 우연히 맞을 확률이 6분의 1이다. 그런 데이터셋 여러 개가 held-out
      평균에 들어가 ρ=+0.481을 만들었고, 백테스트는 그걸 "IR·사업계획서에 쓸 수
      있는 유일한 정량 근거"라고 출력하고 있었다. 투자자 앞에 들고 갈 숫자가
      동전 던지기였다는 뜻이다.

      n=3 → 최소 p=0.167, n=4 → 0.042. **즉 n≤3짜리는 아무리 완벽해도 단독으로
      유의할 수 없다.** 조건 수가 적은 데이터셋은 '증거'가 아니라 '정황'이다.
    """
    if n < 3 or np.isnan(rho):
        return None
    base = list(range(n))
    if n <= 8:                      # 정확검정 (8! = 40320)
        total = hit = 0
        for q in itertools.permutations(base):
            total += 1
            if spearman_rho(base, list(q)) >= rho - 1e-9:
                hit += 1
        return hit / total
    rng = random.Random(seed)       # 몬테카를로
    hit = 0
    for _ in range(iters):
        q = base[:]
        rng.shuffle(q)
        if spearman_rho(base, q) >= rho - 1e-9:
            hit += 1
    return hit / iters


def _recipe_from(cond: Dict, pack: str) -> Recipe:
    """데이터셋의 조건 dict → Recipe.

    ⚠ `overrides:` 블록이 조성 변수(산화제 wt%, 입자 크기, pH 등)를 모델에 전달하는
    유일한 통로다. 이게 없으면 조성만 바꾼 DOE에서 모델이 **모든 조건에 같은 값**을
    뱉는다 — 2026-09-06 실제 발생: carbide L9 9조건 전부 752.02 nm/min으로 동일했고,
    Spearman이 nan(분산 0)으로 나왔다. 그때 "화학층이 조성을 구분 못 한다"고
    오진할 뻔했는데, 실제로는 조성이 애초에 입력되지 않았다.
    """
    kw = {k: cond[k] for k in
          ("pressure_psi", "rpm_wafer", "rpm_platen", "time_s",
           "wafer_radius_m", "kp_m_per_pa", "n_points")
          if k in cond}
    ov = dict(cond.get("overrides") or {})
    return Recipe(pack=cond.get("pack", pack), pack_overrides=ov, **kw)


def run_dataset(path: Path, model: str = "tier2.gw_physical_kp") -> BacktestResult:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    pack = raw.get("pack", "oxide_silica")
    conds = raw.get("conditions") or []
    notes: List[str] = []

    # ── 커버리지 검사 ────────────────────────────────────────
    # 팩이 다루는 재료계 밖의 데이터로 재면 그건 모델 검증이 아니라 외삽 실패다.
    # 2026-09-06: 초경합금·Mo·SiC·석영유리를 전부 oxide_silica 팩으로 돌려놓고
    # "모델이 못 맞힌다"고 결론낼 뻔했다. 실리콘 반도체 CMP 데이터가 하나도 없었다.
    in_scope = bool(raw.get("in_scope", True))
    if not in_scope:
        notes.append(
            f"⚠ 이 데이터셋은 팩 '{pack}'의 재료계 밖이다 — 결과는 모델 성능이 아니라 "
            "외삽 한계를 보여준다. held-out 집계에서 제외한다.")

    obs, pred = [], []
    for c in conds:
        if "mrr_nm_per_min" not in c:
            continue
        res = simulate(_recipe_from(c, pack), model=model)
        pred.append(float(np.mean(res.mrr_nm_per_min)))
        obs.append(float(c["mrr_nm_per_min"]))

    # ── 데이터셋 자체의 건강 검사 ────────────────────────────
    # 예측 분산이 0이면 "모델이 못 맞힌다"가 아니라 "입력이 안 들어갔다"일 수 있다.
    # 이 둘을 구분하지 못하면 멀쩡한 모델을 폐기하거나 고장난 데이터를 신뢰하게 된다.
    if len(set(round(p, 9) for p in pred)) == 1 and len(pred) > 1:
        varied = sorted({k for c in conds for k in (c.get("overrides") or {})})
        notes.append(
            "⚠⚠ 예측값이 전 조건 동일 — 모델 성능 문제가 아니라 **입력이 안 들어간 것**이다. "
            + (f"overrides로 전달된 변수: {varied}. 이 변수들이 엔진에 연결돼 있는지 "
               "`--sensitivity`로 확인하라."
               if varied else
               "이 데이터셋은 `overrides:` 블록이 비어 있다. 논문의 조성 변수를 "
               "overrides로 옮기지 않으면 압력·rpm만 모델에 전달된다."))

    has_contact = bool(raw.get("calibration_contact"))

    # ── 절대값 순위전용 판정 ─────────────────────────────────
    # ⚠ 이 플래그는 "안 맞는 데이터를 빼는" 스위치가 아니다. 켜려면 데이터셋에
    #   `rank_only_ruling:` 로 **왜 절대값을 못 쓰는지의 근거**를 적어야 하고,
    #   근거가 없으면 켜지지 않는다(아래 경고). outlier_rules.py C3 과 같은 취급:
    #   순위는 그대로 집계하고 절대값 판정에서만 뺀다.
    rank_only = bool(raw.get("rank_only", False))
    rank_only_ruling = str(raw.get("rank_only_ruling", "") or "").strip()
    if rank_only and not rank_only_ruling:
        notes.append("⚠ rank_only: true 인데 rank_only_ruling(근거)이 없다 — "
                     "근거 없는 절대값 면제는 인정하지 않는다. 플래그를 무시한다.")
        rank_only = False
    elif rank_only:
        notes.append("순위전용 판정: " + rank_only_ruling.split("\n")[0][:160])
    if len(obs) < 3:
        notes.append(f"조건 {len(obs)}개 — 순위 지표는 3개 이상 필요")
        return BacktestResult(path.stem, len(obs), float("nan"), float("nan"),
                              float("nan"), None, None, in_scope,
                              bool(raw.get("used_for_calibration", False)),
                              rank_only, rank_only_ruling,
                              has_contact, raw.get("source", ""), notes)

    rho = spearman_rho(pred, obs)
    tau = kendall_tau(pred, obs)
    mape = float(np.mean([abs(p - o) / o for p, o in zip(pred, obs) if o])) * 100
    scale = float(np.median([o / p for p, o in zip(pred, obs) if p]))
    if scale < 0.5 or scale > 2.0:
        notes.append(f"⚠ 계통 편향 {scale:.2f}배 — 절대값은 신뢰 불가. "
                     "순위 지표만 근거로 쓸 것."
                     + (" (판정 완료: 원자료 쪽 이상치 — rank_only)" if rank_only else ""))
    digit = sum(1 for c in conds if c.get("read_method") == "digitized")
    if digit:
        notes.append(f"{digit}/{len(conds)} 조건이 그래프 판독값(digitized) — 오차 포함")

    return BacktestResult(path.stem, len(obs), rho, tau, (1 + tau) / 2,
                          mape, scale, in_scope,
                          bool(raw.get("used_for_calibration", False)),
                          rank_only, rank_only_ruling,
                          has_contact, raw.get("source", ""), notes,
                          p_value=perm_p_value(rho, len(obs)),
                          observed=[float(x) for x in obs],
                          predicted=[float(x) for x in pred],
                          pack=str(raw.get("pack", "")),
                          rows=[dict(c) for c in conds])


def run_all(model: str = "tier2.gw_physical_kp") -> List[BacktestResult]:
    if not DATASET_DIR.exists():
        return []
    # _로 시작하는 파일은 템플릿/예시 — 절대 집계하지 않는다.
    # 템플릿의 예시 숫자가 "검증 결과 ρ=1.000"으로 출력된 적이 있다(2026-09-06).
    # 가짜 데이터가 실적으로 둔갑하는 경로는 원천 차단한다.
    paths = [p for p in sorted(DATASET_DIR.glob("*.yaml"))
             if not p.stem.startswith("_")]
    return [run_dataset(p, model) for p in paths]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="결과를 validation/RESULTS.md 에 기록한다(손으로 쓴 값이 묵는 것을 막는다)")
    args = ap.parse_args()

    buf: List[str] = []

    def emit(s: str = "") -> None:
        print(s)
        buf.append(s)

    results = run_all()
    if not results:
        print("데이터셋이 없다. validation/datasets/*.yaml 을 추가하라.")
        print("템플릿: validation/datasets/_TEMPLATE.yaml")
        return 1

    emit("=" * 100)
    emit("FabSim 백테스트 — 공개 문헌 실측 대비 (주 지표: 순위)")
    emit("=" * 100)
    for r in results:
        emit(r.line())
        for n in r.notes:
            emit(f"    · {n}")

    held = [r for r in results if not r.used_for_calibration
            and r.in_scope and not np.isnan(r.spearman)]
    out_of_scope = [r for r in results if not r.in_scope]
    emit("-" * 100)
    if held:
        sig = [r for r in held if r.significant]
        weak = [r for r in held if not r.significant]
        rho = float(np.mean([r.spearman for r in held]))
        acc = float(np.mean([r.pairwise_accuracy for r in held]))
        emit(f"held-out {len(held)}개 전체 평균: ρ={rho:+.3f}, 쌍별 적중률 {acc*100:.1f}%")

        # ⚠ 전체 평균을 근거로 쓰면 안 된다. n=3짜리 ρ=1.000이 섞여 평균을
        #   부풀리는데, 그건 6분의 1 확률로 우연히 나오는 값이다.
        if sig:
            srho = float(np.mean([r.spearman for r in sig]))
            sacc = float(np.mean([r.pairwise_accuracy for r in sig]))
            ntot = sum(r.n for r in sig)
            emit(f"  └ 그중 **통계적으로 유의한 것만** ({len(sig)}개, 총 {ntot}조건): "
                  f"ρ={srho:+.3f}, 쌍별 적중률 {sacc*100:.1f}%")
            emit("→ 외부에 제시할 수 있는 숫자는 이 줄뿐이다 "
                  "(p<0.05, 순열검정).")
            for r in sig:
                emit(f"     · {r.dataset} (n={r.n}, ρ={r.spearman:+.3f}, "
                      f"p={r.p_value:.4f})")

            # ⚠ 위 숫자에는 calibration_contact(팩 파라미터를 이 데이터셋에서
            #   일부 뽑은 부분오염) 신고 데이터셋이 섞여 있을 수 있다. 유리한 쪽만
            #   보이면 안 되므로, 그런 접촉이 전혀 없는 데이터셋만 모은 값도 같이 낸다.
            clean = [r for r in sig if not r.calibration_contact]
            if clean:
                crho = float(np.mean([r.spearman for r in clean]))
                emit(f"  └ 그중 **calibration_contact가 전혀 없는(무접촉/clean) 것만** "
                      f"({len(clean)}개): ρ={crho:+.3f}")
            else:
                emit("  └ ⚠ calibration_contact가 없는 유의 데이터셋이 하나도 없다 "
                      "— 위 숫자 전부가 부분오염 신고를 포함한다.")
        else:
            emit("→ ⚠ 유의한 데이터셋이 하나도 없다. 아직 '검증했다'고 말할 수 없다.")
        if weak:
            emit(f"  └ 유의하지 않음 {len(weak)}개 — 평균에서 빼고 봐야 한다: "
                  + ", ".join(f"{r.dataset}(n={r.n})" for r in weak))
            emit("     n=3은 최소 p가 0.167이라 **구조적으로** 유의할 수 없다. "
                  "조건 수를 늘리거나 여러 데이터셋을 합쳐야 한다.")
        # 절대값 사용 금지 경고 — 계통 편향이 큰 데이터셋이 다수다
        biased = [r for r in held if r.scale_factor is not None
                  and (r.scale_factor < 0.5 or r.scale_factor > 2.0)
                  and not r.rank_only]
        ro = [r for r in held if r.rank_only]
        if ro:
            emit(f"  └ 순위전용 {len(ro)}개(절대값 판정 면제, 근거 기록됨): "
                 + ", ".join(r.dataset for r in ro))
        if biased:
            emit(f"  └ ⚠ 계통 편향 2배 초과 {len(biased)}/{len(held)}개 — "
                  "**절대 MRR은 어디에도 쓰지 마라.** 순위 전용이다.")
    else:
        emit("held-out(범위 내) 데이터셋이 없다 — 아직 '검증했다'고 말할 수 없다.")
    if out_of_scope:
        emit()
        emit(f"범위 밖 {len(out_of_scope)}개(참고용, 집계 제외): "
              + ", ".join(r.dataset for r in out_of_scope))
        emit("→ 이들은 모델 성능이 아니라 '팩 커버리지 밖 외삽'을 보여준다. "
             "실리콘 반도체 CMP 데이터가 필요하다.")

    if args.write:
        # ⚠ 이 파일은 **손으로 쓰지 마라.** 손으로 쓴 값은 묵어도 아무도 모른다.
        #   실제로 2026-09-06 자 수치가 8일 동안 남아 있었고, 그것을 읽은 외부
        #   검토자가 이미 고친 결함을 살아 있는 것으로 보고했다.
        #   측정값을 적는 문서는 측정기가 쓴다.
        out = Path(__file__).resolve().parent / "RESULTS.md"
        stamp = _dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             cwd=_ROOT, capture_output=True, text=True)
        head_sha = rev.stdout.strip() or "(git 정보 없음)"
        out.write_text(
            f"<!-- 자동 생성 — 손으로 고치지 마라.\n"
            f"     재생성: python validation/backtest.py --write -->\n\n"
            f"# 백테스트 결과\n\n"
            f"- 측정 시각: {stamp}\n"
            f"- 코드 리비전: `{head_sha}`\n\n"
            f"```\n" + "\n".join(buf) + "\n```\n",
            encoding="utf-8")
        print(f"\n→ {out} 기록됨 (리비전 {head_sha})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
