"""
트라이볼로지 기초 재현 — Archard 마모식 · Hersey/Sommerfeld 수 · Stribeck 곡선.

지식 근거: knowledge/physics/tribology-friction-wear-stribeck.md
  - Archard: J.F. Archard (1953) J. Appl. Phys. 24, 981.  V = k·W·L/H
    (2차 검증: DoITPoMS 'Wear' TLP, Cambridge; Encyclopedia MDPI "Archard's Law" 2024)
  - Stribeck/Hersey: STLE Lubrication Fundamentals (2022); tribonet.org.
  - CMP Sommerfeld: Wu & Liao (2016) IntechOpen ch.52631; Philipossian CMP Stribeck.

목적:
  1) Archard 식의 스케일링(V ∝ W, V ∝ L, V ∝ 1/H)을 수치로 재현.
  2) 문헌 예시 마모계수 k로 마모부피 절대값이 오더상 타당한지 대조.
  3) Hersey 수 η·N/P 계산 sanity check(단위/오더).
  4) Stribeck 곡선을 단순 mixed-lubrication 모델로 정성 재현 —
     µ 최소점이 boundary→hydrodynamic 전이 사이에 존재함을 확인.

실행: python3 tribology_basics.py  → self-test 결과 stdout (PASS/FAIL 카운트).
"""
import math
import numpy as np


# ---------------------------------------------------------------------------
# 1. Archard 마모식
# ---------------------------------------------------------------------------
def archard_wear_volume(k, W, L, H):
    """마모부피 V = k·W·L/H.
    k: 무차원 마모계수, W: 수직하중[N], L: 미끄럼거리[m], H: 연질재 경도[Pa].
    반환: 마모부피[m^3].
    """
    return k * W * L / H


def archard_wear_depth(k, P, L, H):
    """마모깊이(면적당). V/A = k·(W/A)·L/H = k·P·L/H.  P=명목압력[Pa].
    반환: 마모깊이[m].  (Preston 식 dot h = Kp·P·V 와 구조 동일 — Kp≈k/H)"""
    return k * P * L / H


# ---------------------------------------------------------------------------
# 2. Hersey / Sommerfeld 수
# ---------------------------------------------------------------------------
def hersey_number(eta, N, P):
    """Hersey 수 = η·N/P.  η:점도[Pa·s], N:속도(회전수 1/s 또는 선속도), P:단위길이당 하중.
    관례에 따라 차원이 달라지므로(무차원이 아닐 수 있음) 오더 확인용."""
    return eta * N / P


def cmp_sommerfeld(eta, V, P, delta_eff):
    """CMP Sommerfeld 수 So = η·V/(P·δeff).  무차원.
    η:슬러리점도[Pa·s], V:상대속도[m/s], P:압력[Pa], δeff:유효막두께[m].
    (Wu&Liao 2016; 일부 문헌은 So=ηVP/δeff로 표기 — 차원상 η V/(P δeff)를 채택)."""
    return eta * V / (P * delta_eff)


# ---------------------------------------------------------------------------
# 3. Stribeck 곡선 (정성 모델)
# ---------------------------------------------------------------------------
def stribeck_cof(H_num, mu_bl=0.15, mu_hydro_floor=0.001, c_hydro=0.02):
    """정성적 Stribeck 모델. H_num = Hersey/Sommerfeld 수(무차원 가정).
    - boundary(저 H): 접촉비율 높음 -> COF ~ mu_bl 상수
    - mixed: 막이 접촉을 부분 분리 -> COF 급감
    - hydrodynamic(고 H): 완전분리, 점성전단 -> COF = c_hydro*H (다시 완만 상승)
    접촉분율 f = exp(-alpha*H) 로 boundary->film 전이를 근사.
    COF = f*mu_bl + (1-f)*(c_hydro*H) + mu_hydro_floor
    """
    alpha = 50.0  # 전이 급격도(정성 파라미터)
    f = math.exp(-alpha * H_num)          # 접촉분율(고체-고체)
    cof_solid = f * mu_bl
    cof_fluid = (1.0 - f) * (c_hydro * H_num) + mu_hydro_floor
    return cof_solid + cof_fluid


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------
def _tests():
    results = []

    def check(name, cond, detail=""):
        results.append((name, cond, detail))

    # --- Archard 스케일링 ---
    k, W, L, H = 1e-3, 10.0, 100.0, 1e9   # 강철류 H~1GPa 오더
    V0 = archard_wear_volume(k, W, L, H)
    check("Archard V∝W (2배 하중->2배 부피)",
          math.isclose(archard_wear_volume(k, 2*W, L, H), 2*V0),
          f"V0={V0:.3e} m^3")
    check("Archard V∝L (3배 거리->3배 부피)",
          math.isclose(archard_wear_volume(k, W, 3*L, H), 3*V0))
    check("Archard V∝1/H (경도2배->부피 절반)",
          math.isclose(archard_wear_volume(k, W, L, 2*H), 0.5*V0))

    # --- Archard 절대값 오더 대조 (문헌 예시) ---
    # 예시: 연강 pin-on-disk, k~1e-3(비윤활 금속-금속, Archard 1953 표 오더),
    # W=10N, H=1.8GPa(연강 비커스 ~180HV≈1.8GPa), L=1000m
    # V = 1e-3*10*1000/1.8e9 = 5.56e-9 m^3 = 5.6 mm^3 (1km 미끄럼당) -> 물리적 타당
    V_ex = archard_wear_volume(1e-3, 10.0, 1000.0, 1.8e9)
    check("Archard 오더(연강 예시 V~mm^3 스케일: 1e-9~1e-7 m^3)",
          1e-9 < V_ex < 1e-7, f"V_ex={V_ex:.3e} m^3 = {V_ex*1e9:.2f} mm^3")

    # 마모깊이<->Preston 구조 동일성: dot h/ (P V) = k/H 상수여야
    P, Vslide, t = 3e4, 1.0, 60.0   # 3e4 Pa(~4.3psi), 1 m/s, 60s -> L=60m
    depth = archard_wear_depth(1e-3, P, Vslide*t, 1.8e9)
    Kp_equiv = 1e-3 / 1.8e9          # k/H
    depth_preston = Kp_equiv * P * (Vslide*t)
    check("Archard 깊이 == Preston형 Kp·P·L (Kp=k/H)",
          math.isclose(depth, depth_preston), f"depth={depth:.3e} m")

    # --- Hersey/Sommerfeld 오더 ---
    # CMP 전형: η=1e-3 Pa·s(물기반 슬러리), V=1 m/s, P=3e4 Pa, δeff=5e-6 m(패드 Ra 오더)
    So = cmp_sommerfeld(1e-3, 1.0, 3e4, 5e-6)
    check("CMP Sommerfeld 오더(~1e-3, mixed 영역)",
          1e-4 < So < 1e-1, f"So={So:.3e}")

    # --- Stribeck 최소점 존재 확인 ---
    Hs = np.logspace(-4, 0, 4000)         # Hersey/Sommerfeld 수 스윕
    cof = np.array([stribeck_cof(h) for h in Hs])
    imin = int(np.argmin(cof))
    check("Stribeck COF 최소점이 내부(양끝 아님)에 존재",
          0 < imin < len(Hs) - 1,
          f"min COF={cof[imin]:.4f} @ H={Hs[imin]:.3e}")
    check("Stribeck: boundary COF > 최소 COF (좌측 높음)",
          cof[0] > cof[imin], f"cof[0]={cof[0]:.3f}")
    check("Stribeck: hydrodynamic COF > 최소 COF (우측 재상승)",
          cof[-1] > cof[imin], f"cof[-1]={cof[-1]:.3f}")
    check("Stribeck boundary COF ~ mu_bl(0.15) 근처",
          abs(cof[0] - 0.15) < 0.02, f"cof[0]={cof[0]:.4f}")

    # 출력
    npass = sum(1 for _, c, _ in results if c)
    for name, cond, detail in results:
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
              + (f"  ({detail})" if detail else ""))
    print(f"\n{npass}/{len(results)} PASS")
    return npass == len(results)


if __name__ == "__main__":
    ok = _tests()
    raise SystemExit(0 if ok else 1)
