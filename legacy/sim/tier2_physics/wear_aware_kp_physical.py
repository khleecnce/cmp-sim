"""
패드 마모(glazing) 시간축 MRR 드리프트를, gw_preston_link.py가 정상상태에서 역산한
물리적 Preston 분해(MRR = alpha_removal * n_contacts * V)로 재계산해, pad_wear_glazing.py의
ad-hoc 공식(MRR = c_w * p_r)과 "형태"가 일치하는지 검증하는 다리(bridge) 모듈.

배경 (두 기존 모듈의 간극):
  - gw_preston_link.py (Lv3-2, 정상상태): MRR = alpha_removal * n_contacts(P) * V.
    n_contacts(P)는 연속 GW 모델(gw_pressure_solve.local_contact_state)에서 나오고,
    alpha_removal은 문헌 캘리브레이션(Kp_lit=1e-13, P_ref=20.7kPa, STI 254.05 nm/min)에서
    역산된 상수. Yang et al. 2024 Eq.20(지식노트 gw-nominal-vs-local-pressure.md §3)의
    "MRR의 1차 경로 = 접촉점수 증가"라는 결론을 그대로 따른 물리적으로 더 근거있는 공식.
  - pad_wear_glazing.py (Lv3-1, 시간축): MRR(t) = c_w * p_r(t). c_w는 코드 주석에 명시된 대로
    "물리적 캘리브레이션 아님"인 self-test용 임의 상수. 접촉점수가 아니라 실접촉압력 p_r을
    직접 스케일한다 — gw_preston_link.py의 물리적 그림과 공식이 다르다.

이 모듈이 하는 일 (새 물리 지식 도입 없음, 기존 두 모듈의 재사용/재조합만):
  1) pad_wear_glazing.py의 이산 asperity 시뮬레이션 루프를 "동일 함수들을 그대로 재사용해"
     재현하면서, 각 시점 t의 접촉점수 n_contacts_discrete(heights, d) = sum(heights > d)를
     추가로 기록한다. (pad_wear_glazing.simulate_pad_wear()의 반환값에는 heights 이력이 없어
     n_contacts(t)를 사후에 뽑아낼 수 없으므로, 동일 seed/파라미터로 동일 로직을 다시 돌리되
     원본의 sample_heights/solve_separation_discrete/total_load_discrete/total_area_discrete/
     wear_step_borucki를 전부 import해 재사용한다 — 물리 로직 재구현 없음.)
  2) gw_preston_link.calibrate_alpha_removal()로 역산된 alpha_removal(및 그 self-test와 동일
     V_ref=0.8 m/s, preston.py/gw_preston_link.py에 이미 있는 오더값)로
     MRR_physical(t) = alpha_removal * n_contacts(t) * V_ref 를 계산한다.
  3) 같은 마모 시나리오에서 ad-hoc MRR(t)=c_w*p_r(t)와 물리기반 MRR_physical(t)를 나란히 놓고,
     절대 스케일은 다를 수 있으므로(둘 다 서로 다른 임의/역산 상수가 곱해져 있음) t=0값으로
     정규화한 상대감쇠곡선을 비교한다 — 정성적 형태(단조감쇠, 상관계수)가 일치하는지가 검증
     대상이지, 절대값 일치가 아니다.

주의(스코프): alpha_removal이 정상상태(P 고정, 마모 없음) 캘리브레이션 점에서 나온 상수를
시간축(마모 진행 중) 시나리오에 그대로 적용하는 것은 근사다 — "화학/재료 lump 상수는
마모 상태와 무관하게 일정하다"는 암묵 가정이 깔려 있으며, 이 가정 자체는 이 모듈에서 검증하지
않는다(명시).

────────────────────────────────────────────────────────────────────
⚠️ 불일치 발견 (self-test 실행 결과, 2026-09-05) — 숫자 조작 없이 정직 기록
────────────────────────────────────────────────────────────────────
당초 기대("두 공식 모두 시간에 따라 단조 비증가/비감소로 감쇠하고 정규화 곡선의 상관계수가
높을 것")는 실제 수치 실행 결과 **반증되었다**:

  - n_contacts(t)는 감소가 아니라 **증가**한다 (예: n[0]=3033 -> n[-1]=3564, 40스텝, +17.5%).
    따라서 MRR_physical(t) = alpha_removal * n_contacts(t) * V도 함께 **증가**한다
    (감쇠는커녕 역방향).
  - ad-hoc MRR(t) = c_w * p_r(t)는 pad_wear_glazing.py 자체 self-test대로 여전히 단조
    **감소**한다(p_r 감소).
  - 두 정규화 곡선의 Pearson 상관계수는 +0.9는커녕 **corr ≈ -0.998** (거의 완벽한 역상관).

원인 추정: 이 시나리오는 **명목압력 P_app을 고정한 채 asperity 집단 자체가 마모로 줄어드는**
설정이다(gw_preston_link.py의 n_contacts(P) 선형성 결론은 반대로 "집단을 고정하고 P를
바꿀 때" 성립한 결과였음 — 서로 다른 독립변수를 바꾼 두 실험). 힘평형 W(d)=P_app*A_n을
유지해야 하므로, 집단이 마모로 얇아지면(평균 높이 하락, t=0→39: 2.99e-7→2.93e-7 m, 약 -2%)
같은 총하중을 지지하기 위해 분리거리 d가 그보다 더 빠르게 내려간다(5.63e-7→5.16e-7 m,
약 -8.3%) — 그 결과 d를 넘는(=접촉하는) asperity 개수 n은 오히려 늘어나고, 개별 접촉당
평균압력(p_r=W/A_r)은 낮아진다. 즉 **"고정하중 하에서 표면이 마모로 평탄화(glazing)되면
접촉점 수는 늘고 접촉당 압력은 준다"는, GW 이론상 자기무모순은 아니지만 당초 가정과는
반대 방향의 결과**다. n과 p_r이 강하게(거의 -1) 역상관인 것 자체는 "총하중 보존"이라는
동일 물리제약의 양면이라는 점에서 오히려 깨끗한 결과이나, 이는 gw_preston_link.py의
"MRR = alpha_removal*n(P)*V" 공식을 **압력을 고정하고 집단이 변하는 시간축 시나리오에
그대로 외삽하면 정성적으로 틀린 방향(MRR 증가)을 예측한다**는 것을 의미한다 — 이 공식은
"압력을 바꿀 때"의 관계식이지 "집단이 마모될 때"의 관계식으로 검증된 적이 없었다는
스코프 한계가 이번에 드러난 것. 아래 self-test는 이 결과를 있는 그대로 반영해 FAIL을
출력하도록 두었다(assert 완화·수치 조작 없음 — 거짓 PASS 금지 원칙).

실행: python3 wear_aware_kp_physical.py -> self-test 결과 stdout.
"""
from __future__ import annotations

import numpy as np

import pad_wear_glazing as pwg
import gw_preston_link as link


# gw_preston_link.py self-test와 동일한 문헌 캘리브레이션 지점 (동일 상수 재사용, 신규 물리값 도입 없음)
P_REF_PA = 20.7e3
V_REF_MPS = 0.8
KP_LIT = 1e-13


def n_contacts_discrete(heights, d):
    """분리거리 d에서 접촉 중인(=heights > d) asperity 개수. pad_wear_glazing.py의
    total_load_discrete/total_area_discrete와 동일한 delta=heights-d 판정 로직을
    접촉점수 카운트로 재구성한 것(코드 중복 아님 — 그쪽엔 개수 카운트 함수가 없었음)."""
    return int(np.sum(heights > d))


def get_alpha_removal():
    """gw_preston_link.py의 문헌 캘리브레이션 역산을 그대로 재사용."""
    return link.calibrate_alpha_removal(P_REF_PA, V_REF_MPS, KP_LIT)


def simulate_pad_wear_with_contacts(
    n_asperity=20000,
    beta=1.0 / 0.3e-6,
    R=5e-6,
    E_star=1e9,
    P_app=20e3,
    A_n=1e-4,
    c_w=1e-8,
    C1=2e-6,
    n_steps=40,
    dt=1.0,
    seed=42,
):
    """pad_wear_glazing.simulate_pad_wear()와 동일한 로직/파라미터(동일 기본값·동일 seed)로
    이산 마모 루프를 다시 돌리되, 매 스텝 n_contacts_discrete(heights, d)도 함께 기록한다.

    pad_wear_glazing.simulate_pad_wear()를 감싸는 대신 루프를 다시 여는 이유: 원 함수가
    반환하는 dict에는 매 스텝의 heights 배열이 없어 사후에 접촉점수를 뽑아낼 수 없다.
    대신 원 함수가 사용하는 개별 빌딩블록 함수(sample_heights, solve_separation_discrete,
    total_load_discrete, total_area_discrete, wear_step_borucki)를 전부 그대로 import해
    재사용한다 — 동일 seed·동일 기본 인자이므로 여기서 나오는 t/MRR_adhoc/p_r/mean_height/d
    시퀀스는 pad_wear_glazing.simulate_pad_wear()의 반환값과 수치적으로 동일해야 한다
    (self-test에서 이 등가성도 확인한다).
    """
    rng = np.random.default_rng(seed)
    heights = pwg.sample_heights(n_asperity, beta, rng)
    W_target = P_app * A_n

    t_arr, mrr_adhoc_arr, pr_arr, meanh_arr, d_arr, n_arr = [], [], [], [], [], []

    for step in range(n_steps):
        t = step * dt
        d = pwg.solve_separation_discrete(
            heights, W_target, E_star, R, d_bracket=(-5.0 / beta, float(heights.max()))
        )
        W = pwg.total_load_discrete(heights, d, E_star, R)
        A_r = pwg.total_area_discrete(heights, d, R)
        p_r = W / A_r if A_r > 0 else float("nan")
        mrr_adhoc = c_w * p_r
        n = n_contacts_discrete(heights, d)

        t_arr.append(t)
        mrr_adhoc_arr.append(mrr_adhoc)
        pr_arr.append(p_r)
        meanh_arr.append(float(heights.mean()))
        d_arr.append(d)
        n_arr.append(n)

        heights = pwg.wear_step_borucki(heights, d, C1, dt)

    return {
        "t": np.array(t_arr, dtype=float),
        "MRR_adhoc": np.array(mrr_adhoc_arr, dtype=float),
        "p_r": np.array(pr_arr, dtype=float),
        "mean_height": np.array(meanh_arr, dtype=float),
        "d": np.array(d_arr, dtype=float),
        "n_contacts": np.array(n_arr, dtype=float),
    }


def mrr_physical_series(n_contacts_arr, V_mps=V_REF_MPS, alpha_removal=None):
    """MRR_physical(t) = alpha_removal * n_contacts(t) * V. alpha_removal 미지정 시
    문헌 캘리브레이션(get_alpha_removal())을 사용."""
    if alpha_removal is None:
        alpha_removal = get_alpha_removal()
    return alpha_removal * np.asarray(n_contacts_arr, dtype=float) * V_mps


def compare_adhoc_vs_physical(pad_wear_kwargs: dict | None = None) -> dict:
    """같은 마모 시나리오에서 ad-hoc MRR(t)=c_w*p_r(t)와 물리기반 MRR_physical(t)를 계산하고,
    t=0으로 정규화한 상대감쇠곡선의 상관계수를 구한다.
    """
    kwargs = pad_wear_kwargs or {}
    r = simulate_pad_wear_with_contacts(**kwargs)
    alpha_removal = get_alpha_removal()
    mrr_physical = mrr_physical_series(r["n_contacts"], V_REF_MPS, alpha_removal)
    mrr_adhoc = r["MRR_adhoc"]

    norm_adhoc = mrr_adhoc / mrr_adhoc[0]
    norm_physical = mrr_physical / mrr_physical[0]
    corr = float(np.corrcoef(norm_adhoc, norm_physical)[0, 1])

    return {
        "t": r["t"],
        "n_contacts": r["n_contacts"],
        "mrr_adhoc": mrr_adhoc,
        "mrr_physical": mrr_physical,
        "norm_adhoc": norm_adhoc,
        "norm_physical": norm_physical,
        "corr": corr,
        "alpha_removal": alpha_removal,
    }


# ───────────────────────────── self-test ─────────────────────────────
def _self_test():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    # --- 0) 등가성 확인: 새 루프가 원본 simulate_pad_wear()와 동일 seed/파라미터에서
    #        t/MRR_adhoc/p_r/mean_height/d를 수치적으로 동일하게 재현하는지 (재구현 아님 증거) ---
    r_orig = pwg.simulate_pad_wear(n_steps=30)
    r_new = simulate_pad_wear_with_contacts(n_steps=30)
    # MRR 키 이름이 다르므로(MRR_adhoc vs MRR) 별도 비교, 나머지는 동일 키
    mrr_diff = float(np.max(np.abs(r_new["MRR_adhoc"] - r_orig["MRR"]) / (np.abs(r_orig["MRR"]) + 1e-300)))
    other_diff = max(
        float(np.max(np.abs(r_new[k] - r_orig[k]) / (np.abs(r_orig[k]) + 1e-300)))
        for k in ("t", "p_r", "mean_height", "d")
    )
    max_rel_diff = max(mrr_diff, other_diff)
    chk("동일 seed/파라미터에서 새 루프가 pad_wear_glazing.simulate_pad_wear()와 수치적으로 동일 재현",
        max_rel_diff < 1e-12, f"max_rel_diff={max_rel_diff:.3e}")

    # --- 1) n_contacts(t) 단조 비증가 ---
    r = simulate_pad_wear_with_contacts(n_steps=40)
    n = r["n_contacts"]
    diffs_n = np.diff(n)
    ok1 = bool(np.all(diffs_n <= 0))
    chk("n_contacts(t) 단조 비증가 (마모로 접촉점 소실)", ok1,
        f"n[0]={n[0]:.0f} -> n[-1]={n[-1]:.0f}, max_increase={diffs_n.max():.3f}")

    # --- 2) MRR_physical(t) 단조 비증가 ---
    alpha_removal = get_alpha_removal()
    mrr_phys = mrr_physical_series(n, V_REF_MPS, alpha_removal)
    diffs_mrr = np.diff(mrr_phys)
    ok2 = bool(np.all(diffs_mrr <= 0))
    total_decay_pct = (mrr_phys[0] - mrr_phys[-1]) / mrr_phys[0] * 100
    chk("MRR_physical(t) = alpha_removal*n_contacts(t)*V 단조 비증가", ok2,
        f"MRR_physical[0]={mrr_phys[0]:.4e} -> [-1]={mrr_phys[-1]:.4e} m/s, 감쇠={total_decay_pct:.2f}%")

    # --- 3) 정규화 상대감쇠곡선 상관계수 > 0.9 ---
    # 임계값 0.9 근거: 두 공식이 서로 다른 미시량(p_r vs n_contacts)에 기반하므로 완전 일치(=1.0)는
    # 기대하지 않으나, 둘 다 "asperity 마모로 접촉이 줄어든다"는 동일 물리 과정의 서로 다른 관측량이므로
    # 강한 양의 상관은 기대된다 — Pearson r>0.9는 "형태가 정성적으로 같다"는 판정에 흔히 쓰이는 보수적
    # 기준(완전선형은 아니지만 같은 추세). 만약 실패하면 assert를 낮추지 않고 아래에 불일치로 기록한다.
    cmp = compare_adhoc_vs_physical(pad_wear_kwargs={"n_steps": 40})
    corr = cmp["corr"]
    ok3 = bool(corr > 0.9)
    chk("정규화 상대감쇠곡선 상관계수 > 0.9 (ad-hoc MRR=c_w*p_r vs 물리기반 MRR=alpha_removal*n*V)",
        ok3, f"corr={corr:.6f}")

    # --- 4) 회귀성: C1=0(마모 없음) 극한에서 n_contacts(t)가 상수(변화 없음) ---
    r0 = simulate_pad_wear_with_contacts(n_steps=40, C1=0.0)
    n0 = r0["n_contacts"]
    n0_spread = (n0.max() - n0.min()) / n0.mean() if n0.mean() > 0 else float("nan")
    ok4 = bool(n0_spread < 1e-9)
    chk("C1=0(마모 없음) 극한에서 n_contacts(t) 상수(회귀성 검증)", ok4,
        f"n0[0]={n0[0]:.0f}, n0[-1]={n0[-1]:.0f}, spread={n0_spread:.3e}")

    print(f"\nalpha_removal(재사용, gw_preston_link.py 역산값) = {alpha_removal:.6e} m^3/(s*contact*(m/s))")
    print(f"n_contacts: {n[0]:.0f} -> {n[-1]:.0f} (마모 {40}스텝)")
    print(f"상관계수(정규화 상대감쇠곡선, ad-hoc vs 물리기반) = {corr:.6f}")

    if not (ok1 and ok2 and ok3):
        print("\n[불일치 발견] n_contacts(t)/MRR_physical(t)는 실제로 단조 '증가'하고(감소 아님), "
              "정규화 곡선 상관계수는 +0.9는커녕 corr≈-0.998(거의 완벽한 역상관)이다. 파일 상단 "
              "docstring의 '불일치 발견' 절에 원인 추정을 정직하게 기록함(요약: 명목압력 P_app을 "
              "고정한 채 asperity 집단이 마모로 줄면, 같은 하중을 지지하려고 분리거리 d가 평균높이보다 "
              "더 빨리 내려가 접촉점수 n은 늘고 접촉당 평균압력 p_r은 준다 — gw_preston_link.py의 "
              "n(P) 관계식은 '압력을 바꿀 때'만 검증됐고 '집단이 마모될 때'는 검증 범위 밖이었음이 "
              "이번에 드러남). assert 기준은 낮추지 않았고, 실패는 실패로 둔다.")

    print(f"\n{'ALL PASS' if ok else 'SOME FAILED'}")
    return ok


if __name__ == "__main__":
    import sys
    print("=== wear_aware_kp_physical.py self-test ===")
    success = _self_test()
    sys.exit(0 if success else 1)
