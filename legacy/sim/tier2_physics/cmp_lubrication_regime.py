"""
CMP 윤활 레짐 판별 재현 — Sommerfeld 수 · λ ratio · 유체역학 길이스케일.

지식 근거: knowledge/physics/cmp-lubrication-regimes.md
  - CMP Sommerfeld 수: So = μ·U/(p·δeff),  δeff = α·Ra + (1-α)·δgroove
      출처: Philipossian et al., US20110076924A1 "Method of determining the
      lubrication mechanism in CMP" (Google Patents, 공개). 및 Wu & Liao (2016)
      IntechOpen ch.52631 (오픈액세스).
  - λ ratio(막두께비) 레짐 경계: λ<1 boundary, 1~3 mixed, >3 full-film
      (Bhushan, Introduction to Tribology 2013; tribonet.org — 2차 인용, 경계값은 관례).
  - CMP COF 오더: oxide CMP ~0.23–0.40 (boundary), Physics of the COF in CMP
      (ResearchGate 315672761 스니펫, 2차 인용).

핵심 논증(§ hydrodynamic 길이스케일):
  유체역학 부양 길이 ℓ_hd = μ·U/p 는 CMP 전형조건에서 ~수십 nm 로,
  패드 거칠기 Ra(~µm)보다 2~3 오더 작다 → λ = h_film/σ ≪ 1 → boundary/mixed.
  또한 δeff ≈ σ 일 때 So ≈ ℓ_hd/σ ≈ λ 로, So 와 λ가 같은 오더임을 보인다.

실행: python3 cmp_lubrication_regime.py  → self-test 결과(PASS/FAIL 카운트).
"""
import math
import numpy as np

PSI = 6894.76  # 1 psi [Pa]


# ---------------------------------------------------------------------------
# 1. Sommerfeld 수 & 유효막두께
# ---------------------------------------------------------------------------
def delta_eff(Ra, delta_groove, alpha):
    """유효 유체두께 δeff = α·Ra + (1-α)·δgroove.
    Ra: 패드 raised 영역 평균거칠기[m], δgroove: groove 깊이[m],
    alpha: raised(접촉) 면적 / 전체 표면적 비율(0~1).
    (Philipossian US20110076924A1. groove 가중항 관례는 문헌마다 상이 — 미검증)"""
    return alpha * Ra + (1.0 - alpha) * delta_groove


def cmp_sommerfeld(mu, U, p, d_eff):
    """CMP Sommerfeld 수 So = μ·U/(p·δeff). 무차원.
    mu:슬러리점도[Pa·s], U:상대속도[m/s], p:압력[Pa], d_eff:유효막두께[m]."""
    return mu * U / (p * d_eff)


def hydrodynamic_length(mu, U, p):
    """유체역학 특성길이 ℓ_hd = μ·U/p [m]. So = ℓ_hd/δeff 의 분자."""
    return mu * U / p


# ---------------------------------------------------------------------------
# 2. λ ratio (막두께비) 와 레짐 판별
# ---------------------------------------------------------------------------
def lambda_ratio(h_film, sigma):
    """λ = h_film/σ.  h_film:최소유체막두께[m], σ:합성 RMS 거칠기[m]."""
    return h_film / sigma


def regime_from_lambda(lam):
    """λ 기준 레짐 판별(경계값은 관례, 미검증).
    λ<1: boundary,  1≤λ<3: mixed,  λ≥3: hydrodynamic(full-film)."""
    if lam < 1.0:
        return "boundary"
    if lam < 3.0:
        return "mixed"
    return "hydrodynamic"


# ---------------------------------------------------------------------------
# 3. 정성 Stribeck COF(So) — boundary 상수 + 유체 재상승
# ---------------------------------------------------------------------------
def cof_stribeck(So, mu_bl=0.30, c_hydro=8.0, alpha_tr=40.0, floor=0.002):
    """정성 COF 모델. boundary(저 So)에서 COF≈mu_bl 상수(문헌 oxide CMP 0.23~0.40),
    So↑ 시 접촉분율 f=exp(-alpha_tr·So) 감소로 급락, 유체전단 c_hydro·So 로 재상승.
    COF = f·mu_bl + (1-f)·c_hydro·So + floor."""
    f = math.exp(-alpha_tr * So)
    return f * mu_bl + (1.0 - f) * c_hydro * So + floor


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------
def _tests():
    results = []

    def check(name, cond, detail=""):
        results.append((name, cond, detail))

    # --- 전형 CMP 조건 ---
    mu = 1e-3          # 물기반 슬러리 점도 [Pa·s]
    U = 0.75           # 상대속도 [m/s] (0.5~1 m/s 대표)
    p = 3.0 * PSI      # 3 psi ≈ 20.7 kPa
    Ra = 5e-6          # 패드 raised 거칠기 ~5 µm
    sigma = 5e-6       # 합성 RMS 거칠기 ~ Ra 오더

    # δeff ≈ Ra 근사(groove 가중 무시)로 So 계산
    So = cmp_sommerfeld(mu, U, p, Ra)
    check("CMP So 오더(boundary/mixed, 1e-4~1e-1)",
          1e-4 < So < 1e-1, f"So={So:.3e}")

    # 유체역학 길이 ℓ_hd = μU/p ≪ Ra 여야 (접촉불가 → boundary)
    ell = hydrodynamic_length(mu, U, p)
    check("ℓ_hd = μU/p ≪ Ra (2오더+ 작음 → 부양 불가)",
          ell < Ra / 50.0, f"ℓ_hd={ell*1e9:.1f} nm, Ra={Ra*1e6:.1f} µm")

    # So == ℓ_hd/δeff 항등식 (δeff=Ra)
    check("항등식 So == ℓ_hd/Ra",
          math.isclose(So, ell / Ra, rel_tol=1e-12),
          f"ℓ_hd/Ra={ell/Ra:.3e}")

    # λ ≈ So (δeff≈σ, h_film≈ℓ_hd 근사) → 같은 오더
    lam = lambda_ratio(ell, sigma)
    check("λ ≈ So 같은 오더(δeff≈σ 가정)",
          0.2 < lam / So < 5.0, f"λ={lam:.3e}, So={So:.3e}")
    check("λ<1 → boundary 판별", regime_from_lambda(lam) == "boundary",
          f"λ={lam:.3e} → {regime_from_lambda(lam)}")

    # --- δeff 전체식: α 스윕에서 So 단조감소(δeff 증가) ---
    dg = 250e-6
    So_a05 = cmp_sommerfeld(mu, U, p, delta_eff(Ra, dg, 0.05))
    So_a50 = cmp_sommerfeld(mu, U, p, delta_eff(Ra, dg, 0.50))
    check("δeff 전체식: α↑(접촉면적↑) → δeff↓ → So↑",
          So_a50 > So_a05,
          f"So(α=.05)={So_a05:.2e}, So(α=.5)={So_a50:.2e}")

    # --- 레짐 경계 판별 sanity ---
    check("regime: λ=0.5→boundary", regime_from_lambda(0.5) == "boundary")
    check("regime: λ=2→mixed", regime_from_lambda(2.0) == "mixed")
    check("regime: λ=5→hydrodynamic", regime_from_lambda(5.0) == "hydrodynamic")

    # --- Stribeck COF: boundary 상수 & 최소점 존재 ---
    Ss = np.logspace(-4, 0, 4000)
    cof = np.array([cof_stribeck(s) for s in Ss])
    imin = int(np.argmin(cof))
    check("Stribeck COF 최소점 내부 존재(J자)",
          0 < imin < len(Ss) - 1,
          f"min COF={cof[imin]:.3f} @ So={Ss[imin]:.3e}")
    # 전형 CMP So(~7e-3)에서 COF가 boundary 문헌오더(0.23~0.40) 근처
    cof_cmp = cof_stribeck(So)
    check("전형 So에서 COF ≈ boundary 오더(0.2~0.4)",
          0.20 < cof_cmp < 0.42, f"COF(So={So:.2e})={cof_cmp:.3f}")

    # 출력
    npass = sum(1 for _, c, _ in results if c)
    for name, cond, detail in results:
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
              + (f"  ({detail})" if detail else ""))
    print(f"\n{npass}/{len(results)} PASS")

    # 참고 출력(레짐 요약표)
    print("\n[참고] 전형 CMP 레짐 판별:")
    print(f"  So={So:.2e}, ℓ_hd={ell*1e9:.1f} nm, Ra={Ra*1e6:.1f} µm, "
          f"λ={lam:.2e} → {regime_from_lambda(lam)} (COF~{cof_cmp:.2f})")
    return npass == len(results)


if __name__ == "__main__":
    ok = _tests()
    raise SystemExit(0 if ok else 1)
