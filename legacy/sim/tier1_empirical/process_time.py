"""
공정시간(time) 적분 — Preston MRR 프로파일 → 제거두께/엔드포인트 시간 v0.

담당 에이전트: process-integrator
근거 지식노트: knowledge/cmp/preston-luo-dornfeld-mrr.md

────────────────────────────────────────────────────────────────────
범위
────────────────────────────────────────────────────────────────────
이 모듈은 시간(time) 축만 추가한다. 유량(flow rate)은 슬러리 물질전달/화학
지식이 아직 축적되지 않아(knowledge/에 근거 노트 없음) 이번 범위에서 명시적으로
제외한다 — 유량은 슬러리 화학 지식 축적 후 별도 구현.

새 물리 가정 없음: preston.py의 mrr_profile()/wafer_avg_mrr()이 이미 검증한
정상상태 Preston MRR을 그대로 시간에 대해 선형 적분한다
(제거두께 = MRR * t). preston.py/kinematics.py는 수정하지 않고 import만 한다.

────────────────────────────────────────────────────────────────────
검증 결과 (2026-09-04 실행, 이 파일 하단 self-test)
────────────────────────────────────────────────────────────────────
1) 선형성: removed_thickness(t)가 t에 정확히 비례 (t=60s 대비 t=120s → 2배,
   상대오차 < 1e-9).
2) endpoint_time 역관계: MRR을 2배로 하면 동일 목표두께 도달시간이 정확히 1/2
   (상대오차 < 1e-9).
3) wiwnu_percent가 preston.py의 mrr_profile(Rs=1, 균일압력) 결과에 대해 0%에
   근접(<1e-9%) — preston.py self-test 3번(Rs=1 완전 평탄)과 정합.
4) wiwnu_percent가 preston.py의 mrr_profile(Rs=50/60rpm) 결과에 대해 알려진
   오더(0.4% 근방, edge/center=1.00391)와 일관됨을 출력으로 확인.
"""
from __future__ import annotations

import numpy as np

from preston import mrr_profile  # 동일 폴더 tier1_empirical 모듈, 수정 없이 import


def removed_thickness(rs, mrr, t_sec: float) -> np.ndarray:
    """반경별 제거두께 [m] = mrr(r) * t_sec (Preston 정상상태 MRR의 단순 시간적분).

    rs: 반경 배열 [m] (반환값 shape 정합을 위해 받되 계산에는 쓰이지 않음).
    mrr: 반경별 MRR [m/s] (preston.mrr_profile 등의 출력).
    """
    del rs  # 반환 shape을 mrr과 맞추기 위한 시그니처용, 계산에는 불필요
    return np.asarray(mrr, dtype=float) * t_sec


def endpoint_time(target_thickness_m: float, mrr_at_ref: float) -> float:
    """목표두께 도달까지 걸리는 시간 [s] = target_thickness_m / mrr_at_ref.

    mrr_at_ref [m/s]는 보통 웨이퍼 평균 MRR — 어떤 MRR을 기준으로 할지는
    호출부가 결정한다(이 함수는 단순 나눗셈만 한다).
    """
    return float(target_thickness_m) / float(mrr_at_ref)


def wiwnu_percent(mrr_or_thickness_array) -> float:
    """(max-min)/mean * 100 — demo_app.py의 인라인 WIWNU 계산을 그대로 승격."""
    arr = np.asarray(mrr_or_thickness_array, dtype=float)
    return (arr.max() - arr.min()) / arr.mean() * 100.0


# ───────────────────────────── self-test ─────────────────────────────
def _selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    R_w, r_cc = 0.150, 0.200
    kp = 1.0e-13

    # 1) 선형성: t=120s가 t=60s의 정확히 2배
    rs, mrr = mrr_profile(R_w, r_cc, 60.0, 60.0, 20.7e3, kp)
    th_60 = removed_thickness(rs, mrr, 60.0)
    th_120 = removed_thickness(rs, mrr, 120.0)
    ratio = float(np.max(np.abs(th_120 / th_60 - 2.0)))
    chk("removed_thickness linear in t (120s = 2x 60s)", ratio < 1e-9,
        f"max|ratio-2|={ratio:.2e}")

    # 2) endpoint_time 역관계: MRR 2배 -> 시간 1/2
    target = 100e-9  # 100 nm
    mrr_ref = mrr.mean()
    t_base = endpoint_time(target, mrr_ref)
    t_double = endpoint_time(target, 2.0 * mrr_ref)
    chk("endpoint_time halves when MRR doubles",
        abs(t_double / t_base - 0.5) < 1e-9, f"ratio={t_double/t_base:.9f}")

    # 3) Rs=1(균일압력) -> WIWNU ~ 0%
    rs1, mrr1 = mrr_profile(R_w, r_cc, 60.0, 60.0, 20.7e3, kp)
    w1 = wiwnu_percent(mrr1)
    chk("Rs=1 uniform pressure -> WIWNU ~ 0%", w1 < 1e-9, f"WIWNU={w1:.2e}%")

    # 4) Rs=50/60 -> WIWNU 오더 확인(정확값 assert 없이 출력만)
    rs2, mrr2 = mrr_profile(R_w, r_cc, 50.0, 60.0, 20.7e3, kp)
    w2 = wiwnu_percent(mrr2)
    print(f"[INFO] Rs=50/60 WIWNU(프로파일 기준) = {w2:.4f}% "
          f"(참고: kinematics.py/preston.py 교차검증 edge/center=1.00391, 0.4% 근방 예상)")
    chk("Rs=50/60 WIWNU is a small positive percent (order check only)",
        0.0 < w2 < 5.0, f"WIWNU={w2:.4f}%")

    print("\nOVERALL:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys
    print("=== Process time integration v0 self-test ===")
    sys.exit(0 if _selftest() else 1)
