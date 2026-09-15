"""
접촉 통계(η_c, A_f)에서 Preston 계수 K_p를 상대 보정하는 훅. 새 물리모델이 아니라
GW 솔버 출력(η_c, A_f)을 기존 K_p0에 곱하는 단순 스케일링 인터페이스만 제공한다.

지식 근거: knowledge/materials/disk-design-pad-roughness-asperity-relation.md
(disk-design Lv2-2) §2.3, §3.4(b). Sun (2009) PhD dissertation, Univ. of Arizona,
http://hdl.handle.net/10150/194898, Ch.7.2 Fig.7.14/7.15 판독값(CMC EPIC D100-1/D100-2,
IC1000 k-groove 패드 × Type A(덜 공격적)/Type B(≈3배 cut rate) 디스크). 저자 Eq.7.14가
η_c/A_f를 평균 실접촉압력에 비례하는 대리지표로 쓰고, 세 패드 조합 모두 공격적 디스크(B)의
η_c/A_f가 더 크다(저자 결론, MRR 방향과 일치)는 것만 노트가 검증했다.

PROVISIONAL 경고: preston_coefficient_contact_scaling의 "K_p ∝ η_c/A_f" 단순 비례식은
노트 §3.4(b)/§5가 확인한 유일한 정성적 관계(η_c/A_f가 클수록 K_p/MRR도 크다는 방향성)를
가장 단순한 선형 형태로 옮긴 것일 뿐이다. 비례상수가 1인지, 지수가 정확히 1인지는
어느 출처도 회귀하지 않았다 — 이 선형가정 자체가 미검증(PROVISIONAL)이며, 캘리브레이션
없이 정량 예측에 쓰면 안 된다.

실행: python3 disk_preston_contact_decomposition.py -> self-test 결과 stdout.
"""


def eta_over_af(eta_c, a_f):
    """η_c/A_f 계산 (Sun 2009 Ch.7.2 Eq.7.14 정의) — 접촉점당 평균 실접촉압력에
    비례하는 대리지표. a_f<=0이면 물리적으로 무의미하므로 ValueError."""
    if a_f <= 0:
        raise ValueError(f"a_f는 양수여야 한다(A_f<=0은 접촉 없음/미정의): {a_f}")
    return eta_c / a_f


def preston_coefficient_contact_scaling(eta_af, eta_af_ref, kp0):
    """K_p = kp0 * (eta_af / eta_af_ref).

    노트(§3.4(b), §5)가 검증한 것은 "η_c/A_f가 클수록 K_p/MRR도 크다"는 방향성뿐이다.
    이 함수의 단순 비례(비례상수=1, 지수=1) 가정은 어느 문헌도 회귀하지 않은
    PROVISIONAL 작업가설이며, 캘리브레이션 전에는 정량 예측에 쓰지 않는다.
    """
    return kp0 * (eta_af / eta_af_ref)


def fragment_contact_separation(a_f_measured, a_f_intrinsic):
    """파편(비지지 flat) 접촉 기여도를 분리하는 인터페이스만 제공.

    초과분 = a_f_measured - a_f_intrinsic, 음수면 0으로 clamp(파편 기여가 없다는 뜻).
    A_f는 정의상 항상 >=0이어야 하므로 음수 입력은 ValueError. 분리 계수 자체는
    노트에 없으므로(McAllister 2019, Liao 2014의 정성적 해석만 있음, 노트 §3.4 (a) 서술)
    단순 차감 이상의 모델은 만들지 않는다.
    """
    if a_f_measured < 0 or a_f_intrinsic < 0:
        raise ValueError(
            f"A_f는 음수일 수 없다: a_f_measured={a_f_measured}, a_f_intrinsic={a_f_intrinsic}"
        )
    return max(0.0, a_f_measured - a_f_intrinsic)


def disk_preston_contact_scaling(eta_c, a_f, eta_c_ref, a_f_ref, kp0):
    """eta_over_af + preston_coefficient_contact_scaling을 조합한 종합 함수.

    PROVISIONAL(§3.4(b), §5): scale_factor·kp_scaled는 미검증 선형가정에 의존한다.
    """
    eta_af = eta_over_af(eta_c, a_f)
    eta_af_ref = eta_over_af(eta_c_ref, a_f_ref)
    scale_factor = eta_af / eta_af_ref
    kp_scaled = preston_coefficient_contact_scaling(eta_af, eta_af_ref, kp0)
    return {
        "eta_af": eta_af,
        "eta_af_ref": eta_af_ref,
        "scale_factor": scale_factor,
        "kp_scaled": kp_scaled,
    }


if __name__ == "__main__":
    # Sun 2009 §2.3 표 3개 패드 조합, D100-1 A->B self-test
    r_a = eta_over_af(237, 5.6e-4)
    r_b = eta_over_af(58, 0.55e-4)
    print(f"D100-1 eta_c/A_f: A={r_a:.2e}  B={r_b:.2e}  B/A={r_b / r_a:.2f}")
    assert abs(r_a - 4.23e5) / 4.23e5 < 0.05
    assert abs(r_b - 1.05e6) / 1.05e6 < 0.05
    assert abs((r_b / r_a) - 2.48) / 2.48 < 0.10

    result = disk_preston_contact_scaling(58, 0.55e-4, 237, 5.6e-4, kp0=1.0)
    print(result)
    assert abs(result["kp_scaled"] - 2.48) / 2.48 < 0.10
    print("OK: disk_preston_contact_decomposition self-test 통과")
