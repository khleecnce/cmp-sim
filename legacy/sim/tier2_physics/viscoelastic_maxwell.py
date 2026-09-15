"""
Maxwell 점탄성 모델 — CMP 패드 저장/손실 탄성률 수치 재현 (Lv1-1 sanity check)

이론적 배경: knowledge/materials/pad-viscoelasticity-dma.md §3
출처: Wikipedia "Dynamic mechanical analysis" §Frequency sweep (Maxwell model 수식),
      원 출처 개념은 J.D. Ferry, Viscoelastic Properties of Polymers (Wiley 1980) 표준.

Maxwell 모델(스프링 E + 대시팟 η 직렬, 이완시간 τ0 = η/E)의 정현파 응답:
    E''(ω) = E * τ0*ω / (τ0^2 * ω^2 + 1)   [손실탄성률]
    E'(ω)  = E * τ0^2*ω^2 / (τ0^2*ω^2 + 1)  [저장탄성률]

이 모듈은 CMP 공정변수(MRR/WIWNU) 계산에는 아직 쓰이지 않는다 — 순수 지식 재현/검증 목적의
Lv1 sanity check이며, 향후 Lv2-1 GW 접촉모델에서 패드 유효강성 개념을 도입할 때 자연스럽게
연결된다 (예: 저주파=완전이완=고무질 거동, 고주파=CMP 공정 시간축에서 무시 가능한 순간탄성 거동).
"""
import numpy as np


def maxwell_storage_loss(omega, E, tau0):
    """Maxwell 모델의 저장탄성률 E'(omega), 손실탄성률 E''(omega) 계산.

    Parameters
    ----------
    omega : array_like
        각주파수 [rad/s]
    E : float
        스프링 탄성계수 [Pa 또는 임의 단위, 여기선 무차원 비교용 1.0]
    tau0 : float
        Maxwell 이완시간 [s] = eta/E

    Returns
    -------
    (E_storage, E_loss) : tuple of ndarray
    """
    omega = np.asarray(omega, dtype=float)
    denom = (tau0 ** 2) * (omega ** 2) + 1.0
    E_loss = E * tau0 * omega / denom
    E_storage = E * (tau0 ** 2) * (omega ** 2) / denom
    return E_storage, E_loss


def tan_delta(E_storage, E_loss):
    """손실계수 tan(delta) = E''/E'. E_storage=0인 경우(omega=0)는 정의역 밖 → inf 반환."""
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(E_storage > 0, E_loss / np.where(E_storage == 0, np.nan, E_storage), np.inf)
    return result


def _self_test():
    """5개 문헌 정성 거동을 수치로 검증. 전부 PASS해야 노트 §3 주장이 성립."""
    E = 1.0  # 무차원 스프링 계수
    tau0 = 1.0  # 무차원 이완시간 [s]
    results = []

    # 1) omega -> 0 (저주파, 완전 이완): E' -> 0, E'' -> 0 (액체적 거동, 저장 없음)
    Es_low, El_low = maxwell_storage_loss([1e-6], E, tau0)
    ok1 = Es_low[0] < 1e-6 and El_low[0] < 1e-5
    results.append(("저주파 극한 E'->0", ok1, f"E'={Es_low[0]:.3e}"))

    # 2) omega -> inf (고주파, 순간탄성): E' -> E, E'' -> 0
    Es_high, El_high = maxwell_storage_loss([1e6], E, tau0)
    ok2 = abs(Es_high[0] - E) < 1e-5 and El_high[0] < 1e-5
    results.append(("고주파 극한 E'->E", ok2, f"E'={Es_high[0]:.6f} (목표 {E})"))

    # 3) omega = 1/tau0 (피크): 해석적으로 E''_max = E/2 at omega=1/tau0 (dE''/domega=0 도함수로 유도)
    omega_peak = 1.0 / tau0
    Es_pk, El_pk = maxwell_storage_loss([omega_peak], E, tau0)
    analytic_peak = E / 2.0
    ok3 = abs(El_pk[0] - analytic_peak) < 1e-10
    results.append(("E'' 피크값 = E/2 @ omega=1/tau0", ok3, f"E''={El_pk[0]:.10f} (해석값 {analytic_peak})"))

    # 4) 피크 위치가 실제로 최대인지 광범위 스캔으로 확인 (수치 미분 없이 grid search)
    omega_scan = np.logspace(-3, 3, 100001) / tau0
    _, El_scan = maxwell_storage_loss(omega_scan, E, tau0)
    idx_max = np.argmax(El_scan)
    omega_at_max = omega_scan[idx_max]
    ok4 = abs(omega_at_max - omega_peak) / omega_peak < 1e-3
    results.append(("grid search 최대점 = 1/tau0", ok4, f"omega_max={omega_at_max:.6f} (목표 {omega_peak})"))

    # 5) tan(delta): omega<<1/tau0 에서 tan(delta) 매우 큼(점성 지배), omega>>1/tau0 에서 tan(delta)->0(탄성 지배)
    td_low = tan_delta(Es_low, El_low)[0]
    td_high = tan_delta(Es_high, El_high)[0]
    ok5 = td_low > 100 and td_high < 1e-4
    results.append(("tan(delta): 저주파>>1, 고주파->0", ok5, f"tan_low={td_low:.2f}, tan_high={td_high:.2e}"))

    n_pass = sum(1 for _, ok, _ in results if ok)
    print(f"=== viscoelastic_maxwell.py self-test: {n_pass}/{len(results)} PASS ===")
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name} — {detail}")
    return n_pass == len(results)


if __name__ == "__main__":
    _self_test()
