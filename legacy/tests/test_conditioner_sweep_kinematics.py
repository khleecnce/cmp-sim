"""conditioner_sweep_kinematics.py 회귀 테스트 — _self_test()의 5항목을 pytest화."""
import math
import numpy as np

import conditioner_sweep_kinematics as csk


def test_static_position_invariant():
    T = np.linspace(0, 100, 50)
    x, y, r = csk.diamond_trajectory(T, R_p=150.0, R_a=80.0, R_i=40.0,
                                      n_p=0.0, n_a=0.0, n_d=0.0,
                                      beta_s=0.0, beta_max=math.pi / 3)
    assert np.allclose(x, x[0])
    assert np.allclose(y, y[0])


def test_table1_conditions_trajectory_bounded():
    T2 = np.arange(0, 20, 0.01)
    x2, y2, r2 = csk.diamond_trajectory(T2, R_p=190.0, R_a=115.0, R_i=52.0,
                                         n_p=100.0, n_a=19.0, n_d=73.0,
                                         beta_s=math.radians(20), beta_max=math.radians(60))
    r_max = 190.0 + 115.0 + 52.0
    r_min = max(0.0, 190.0 - 115.0 - 52.0)
    assert np.all(r2 <= r_max + 1e-6)
    assert np.all(r2 >= r_min - 1e-6)


def test_sweep_speed_phase_scaling():
    n_a1, n_a2 = 10.0, 20.0
    beta_s, beta0, beta_max = 0.0, math.pi / 6, math.pi / 3
    Tc = np.array([3.0])
    b1 = csk.disk_center_beta(Tc, n_a1, beta_s, beta0, beta_max)
    b2_half = csk.disk_center_beta(Tc / 2.0 * (n_a2 / n_a1), n_a2, beta_s, beta0, beta_max)
    assert np.allclose(b1, b2_half, atol=1e-9)


def test_pca_zero_outside_reach():
    """도달불가 반경에서 PCA=0 (TEST-AUDIT §3-A #5, §4-2 공허통과 버그 수정).

    기존 r_bins=25/기본 r_max에서는 bin 중심 최대가 354.8mm < 도달반경(357mm)+5mm라
    outside_mask가 항상 비어 `(not any) or ...` 구조 때문에 이 테스트가 실제로는
    아무것도 검증하지 않고 있었다(TEST-AUDIT §4-2). r_max를 도달반경보다 명백히
    크게 늘려 도달불가 bin이 실제로 생기게 하고, mask가 비지 않음을 먼저 assert해
    "공허 통과"를 원천 차단한 뒤 그 bin들의 PCA=0을 확인한다.
    """
    R_p, R_a, R_i = 190.0, 115.0, 52.0
    r_reach_max = R_p + R_a + R_i
    bin_centers, pca = csk.pcr_radial_profile(
        duration_s=8.0, dt=0.005, R_p=R_p, R_a=R_a, disk_radius=R_i,
        n_p=100.0, n_a=19.0, n_d=73.0,
        beta_s=math.radians(5), beta_max=math.radians(40),
        n_particles=10, r_bins=40, r_max=r_reach_max * 1.3)
    outside_mask = bin_centers > r_reach_max + 5.0
    assert np.any(outside_mask), "도달불가 반경 bin이 없음 — r_max/r_bins 조정 확인"
    assert np.allclose(pca[outside_mask], 0.0)


def test_pca_profile_has_nonzero_coverage():
    """PCA 비영값 반경대가 디스크중심 궤적의 기하 도달범위와 일치 (TEST-AUDIT §3-A #5).

    disk_center 거리(코사인법칙): dc_r(beta) = sqrt(R_p^2+R_a^2+2*R_p*R_a*cos(beta)),
    beta in [beta_s, beta_s+beta_max]. dc_r는 beta에 대해 단조감소이므로 범위는
    양끝 beta에서 결정. diamond가 R_i로 빠르게(n_d=73rpm) 원주운동하며 스크래치를
    남기므로, PCA가 비영인 반경대는 [min(dc_r)-R_i, max(dc_r)+R_i] (bin폭 여유 포함)
    를 벗어나지 않아야 한다 — 임의 5% 임계값 대신 이 기하 조건으로 대조한다.
    """
    R_p, R_a, R_i = 190.0, 115.0, 52.0
    beta_s, beta_max = math.radians(5), math.radians(40)
    betas = np.array([beta_s, beta_s + beta_max])
    dc_r = np.sqrt(R_p ** 2 + R_a ** 2 + 2 * R_p * R_a * np.cos(betas))
    r_lo, r_hi = dc_r.min() - R_i, dc_r.max() + R_i

    bin_centers, pca = csk.pcr_radial_profile(
        duration_s=8.0, dt=0.005, R_p=R_p, R_a=R_a, disk_radius=R_i,
        n_p=100.0, n_a=19.0, n_d=73.0,
        beta_s=beta_s, beta_max=beta_max,
        n_particles=10, r_bins=25)
    assert np.count_nonzero(pca) > 0
    bw = bin_centers[1] - bin_centers[0]
    nz = bin_centers[pca > 0]
    assert nz.min() >= r_lo - bw, f"{nz.min()} < {r_lo - bw}"
    assert nz.max() <= r_hi + bw, f"{nz.max()} > {r_hi + bw}"
