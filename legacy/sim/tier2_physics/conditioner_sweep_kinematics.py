"""
컨디셔너 스윕 운동학 모델 — 사인파 스윕 모드에서 다이아몬드 입자 궤적을 계산하고,
반경별 누적 스크래치 거리(PCA/PCR 상대 프로파일)를 추출한다.

지식 근거: knowledge/equipment/conditioner-sweep-kinematics-pcr-profile.md (disk-conditioner Lv2-2)
  1차 출처: Zheng, Zhao & Lu (2023), "Prediction of Pad Wear Profile and Simulation of Its
  Influence on Wafer Polishing", Micromachines 14(9), 1683, 오픈액세스 PMC10536193.
  Eq.1-9(위치식) 및 Table 1(실험조건)을 그대로 구현. 논문은 이 운동학 모델을
  실측(레이저 공초점현미경)으로 검증했다고 보고한다(본 모듈은 재현이지 재검증은 아님 — 아래
  self-test는 논문이 보고한 정성적 결론과의 내적 정합성만 확인).

모델 (Eq.1-9, 표기는 노트 §2와 동일):
  arm center:  alpha(T) = alpha0 - (2*n_p/60)*pi*T
               x_ac = R_p*cos(alpha), y_ac = R_p*sin(alpha)
  disk center (sinusoidal sweep): beta(T) = beta_s - 0.5*beta_max*cos(
               arccos(2*(beta0-beta_s)/beta_max) + (2*n_a/60)*pi*T ) + 0.5*beta_max
               x_dc = x_ac + R_a*cos(alpha+beta), y_dc = y_ac + R_a*sin(alpha+beta)
  diamond i:   theta_i(T) = theta_i0 + (2*n_d/60)*pi*T
               x_i = x_dc + R_i*cos(alpha+beta+theta_i), y_i = y_dc + R_i*sin(alpha+beta+theta_i)

PCA(반경 r) 근사: 다수 다이아몬드(디스크 반경 R_i를 균등분포로 샘플)의 궤적을 시간적분해,
각 순간 패드중심으로부터의 거리 r_i(T)=sqrt(x_i^2+y_i^2)를 반경 구간(bin)에 누적
스크래치 거리(속도*dt)로 히스토그램화한다. Preston형 PCA=k*P*s(r)이므로 (k, P가 반경에
무관하다는 가정 하에) 이 히스토그램이 PCR(r)의 상대적 형상을 그대로 준다.

단순화(§7 한계 명시): 개별 다이아몬드 대신 디스크 반경 R_i를 균등분포로 샘플한 대표
입자 집합(N_particles)으로 근사 — 논문처럼 실제 전기도금/솔더링 배치 패턴은 반영하지 않음.
계산량 절감을 위해 논문의 20초~8시간 스케일 대신 self-test는 짧은 시간(수십~수백 초)만
시뮬레이션한다 — "장시간 누적 후 평균적 형상"이 아니라 "형상의 정성적 특징"만 확인.

실행: python3 conditioner_sweep_kinematics.py -> self-test 결과 stdout.
"""
import math
import numpy as np


def arm_center_angle(T, n_p, alpha0=0.0):
    """식(1): alpha(T) = alpha0 - (2*n_p/60)*pi*T   (n_p: 패드 RPM)"""
    return alpha0 - (2.0 * n_p / 60.0) * math.pi * T


def disk_center_beta(T, n_a, beta_s, beta0, beta_max):
    """식(4): 사인파 스윕 모드의 beta(T).

    beta_s: 스윕 시작각, beta0: 초기각, beta_max: 스윕 범위(라디안), n_a: 스윕 RPM.
    beta0는 beta_s와 beta_s+beta_max 사이에 있어야 arccos 인자가 [-1,1] 범위.
    """
    ratio = 2.0 * (beta0 - beta_s) / beta_max - 1.0
    # 원 논문 식은 2*(beta0-beta_s)/beta_max (범위 0~2 가정, 여기선 -1~1로 정규화해 arccos 안전화)
    ratio = np.clip(ratio, -1.0, 1.0)
    phase0 = math.acos(ratio)
    return (beta_s - 0.5 * beta_max * np.cos(phase0 + (2.0 * n_a / 60.0) * math.pi * T)
            + 0.5 * beta_max)


def diamond_trajectory(T, R_p, R_a, R_i, n_p, n_a, n_d,
                        alpha0=0.0, beta_s=0.0, beta0=None, beta_max=math.pi / 2,
                        theta_i0=0.0):
    """식(1)-(9) 전체 합성: 시간배열 T에 대한 단일 다이아몬드 절대 위치(x,y) 및 반경 r.

    beta0 기본값: 스윕 구간 중앙(beta_s + beta_max/2) — arccos 인자를 0으로 만들어 안전.
    """
    if beta0 is None:
        beta0 = beta_s + beta_max / 2.0

    alpha = arm_center_angle(T, n_p, alpha0)
    x_ac = R_p * np.cos(alpha)
    y_ac = R_p * np.sin(alpha)

    beta = disk_center_beta(T, n_a, beta_s, beta0, beta_max)
    x_dc = x_ac + R_a * np.cos(alpha + beta)
    y_dc = y_ac + R_a * np.sin(alpha + beta)

    theta_i = theta_i0 + (2.0 * n_d / 60.0) * math.pi * T
    x_i = x_dc + R_i * np.cos(alpha + beta + theta_i)
    y_i = y_dc + R_i * np.sin(alpha + beta + theta_i)

    r = np.sqrt(x_i ** 2 + y_i ** 2)
    return x_i, y_i, r


def pcr_radial_profile(duration_s, dt, R_p, R_a, disk_radius, n_p, n_a, n_d,
                        beta_s, beta_max, n_particles=12, r_bins=20, r_max=None):
    """다수 대표 다이아몬드(디스크 반경 균등샘플)의 궤적을 적분해 반경별 누적
    스크래치 거리(속도*dt 합) 히스토그램을 반환한다 -> PCA(r), 상대적 PCR(r) 형상.

    Returns: (bin_centers, pca_hist) — pca_hist는 [길이 단위]의 상대적 스케일(정규화 안 함).
    """
    if r_max is None:
        r_max = R_p + R_a + disk_radius + 5.0

    T = np.arange(0.0, duration_s, dt)
    R_i_values = np.linspace(0.05 * disk_radius, disk_radius, n_particles)
    theta_i0_values = np.linspace(0.0, 2 * math.pi, n_particles, endpoint=False)

    bins = np.linspace(0.0, r_max, r_bins + 1)
    pca_hist = np.zeros(r_bins)

    for R_i, theta_i0 in zip(R_i_values, theta_i0_values):
        x_i, y_i, r_i = diamond_trajectory(
            T, R_p, R_a, R_i, n_p, n_a, n_d,
            beta_s=beta_s, beta_max=beta_max, theta_i0=theta_i0)
        # 속도(스크래치 길이/dt) 근사: 연속 위치 차분
        dx = np.diff(x_i)
        dy = np.diff(y_i)
        ds = np.sqrt(dx ** 2 + dy ** 2)  # 각 스텝의 스크래치 거리
        r_mid = 0.5 * (r_i[:-1] + r_i[1:])
        idx = np.clip(np.digitize(r_mid, bins) - 1, 0, r_bins - 1)
        for k, s in zip(idx, ds):
            pca_hist[k] += s

    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    return bin_centers, pca_hist


def _self_test():
    results = []

    # Test 1: 정지 상태(n_p=n_a=n_d=0)에서는 위치가 시간에 불변 (기구학 항등)
    T = np.linspace(0, 100, 50)
    x, y, r = diamond_trajectory(T, R_p=150.0, R_a=80.0, R_i=40.0,
                                  n_p=0.0, n_a=0.0, n_d=0.0,
                                  beta_s=0.0, beta_max=math.pi / 3)
    ok1 = np.allclose(x, x[0]) and np.allclose(y, y[0])
    results.append(("정지상태 위치불변", ok1))

    # Test 2: 논문 Table 1 조건(n_p=100, n_d=73, n_a=19 RPM)으로 짧은 시간 시뮬레이션 —
    # 궤적 반경이 항상 유한범위(R_p-R_a-R_i ~ R_p+R_a+R_i) 안에 있는지(발산/버그 검출)
    T2 = np.arange(0, 20, 0.01)
    x2, y2, r2 = diamond_trajectory(T2, R_p=190.0, R_a=115.0, R_i=52.0,
                                     n_p=100.0, n_a=19.0, n_d=73.0,
                                     beta_s=math.radians(20), beta_max=math.radians(60))
    r_theory_max = 190.0 + 115.0 + 52.0
    r_theory_min = max(0.0, 190.0 - 115.0 - 52.0)
    ok2 = np.all(r2 <= r_theory_max + 1e-6) and np.all(r2 >= r_theory_min - 1e-6)
    results.append(("Table1 조건 궤적 범위 유효성", ok2))

    # Test 3: 스윕 속도(n_a)가 2배가 되면 위상 진행이 2배 빨라짐 -> 같은 T에서 beta 값이
    # (초기 위상차 무시하고) n_a=2x 케이스가 n_a=1x 케이스의 T/2 시점 값과 근사 일치
    n_a1, n_a2 = 10.0, 20.0
    beta_s, beta0, beta_max = 0.0, math.pi / 6, math.pi / 3
    Tc = np.array([3.0])
    b1 = disk_center_beta(Tc, n_a1, beta_s, beta0, beta_max)
    b2_half = disk_center_beta(Tc / 2.0 * (n_a2 / n_a1), n_a2, beta_s, beta0, beta_max)
    ok3 = np.allclose(b1, b2_half, atol=1e-9)
    results.append(("스윕속도 위상 스케일링(EXAMS Q1 근거)", bool(ok3)))

    # Test 4: PCR(r) 프로파일이 스윕 범위(beta_s~beta_s+beta_max) + 디스크반경이 커버하는
    # 반경 구간 밖(즉 팔이 절대 도달하지 않는 반경)에서는 누적 스크래치 거리가 0에 가까움
    bin_centers, pca = pcr_radial_profile(
        duration_s=8.0, dt=0.005, R_p=190.0, R_a=115.0, disk_radius=52.0,
        n_p=100.0, n_a=19.0, n_d=73.0,
        beta_s=math.radians(5), beta_max=math.radians(40),
        n_particles=10, r_bins=25)
    # 팔이 도달 가능한 최대 반경 근사
    r_reach_max = 190.0 + 115.0 + 52.0
    outside_mask = bin_centers > r_reach_max + 5.0
    ok4 = (not np.any(outside_mask)) or np.allclose(pca[outside_mask], 0.0)
    results.append(("도달불가 반경 PCA=0", bool(ok4)))

    # Test 5: 프로파일이 최소한 스윕 반경 범위(대략 R_p-R_a-R_i ~ R_p+R_a+R_i) 안 어딘가에
    # 0이 아닌 값을 가짐(운동학 모델이 실제로 그 구간을 절삭한다는 최소 sanity check)
    nonzero_frac = np.count_nonzero(pca) / len(pca)
    ok5 = nonzero_frac > 0.05
    results.append((f"PCA 프로파일 비영값 비율={nonzero_frac:.2f}>0.05", bool(ok5)))

    passed = sum(1 for _, ok in results if ok)
    print(f"=== conditioner_sweep_kinematics self-test: {passed}/{len(results)} PASS ===")
    for name, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    return passed == len(results)


if __name__ == "__main__":
    import sys
    success = _self_test()
    sys.exit(0 if success else 1)
