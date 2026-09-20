"""cmp_lubrication_regime.py 엔진 등록 회귀 — WaferResult 진단 필드 3종 (S12).

노트 knowledge/physics/cmp-lubrication-regimes.md §5 수치(전형 CMP 조건, self-test
11/11 PASS)를 그대로 재현한다. MRR 경로와 독립인 진단 필드라 mrr_nm_per_min은 건드리지 않는다.
"""
import cmp_lubrication_regime as CLR

from sim.engine import Recipe, simulate


def test_note_typical_condition_sommerfeld():
    # 노트 §5: μ=1e-3, U≈0.75 m/s, p=3psi(≈20684 Pa), δeff=Ra=5e-6 → So≈7.25e-3
    mu, U, p, Ra = 1e-3, 0.75, 3.0 * 6894.76, 5e-6
    so = CLR.cmp_sommerfeld(mu, U, p, Ra)
    assert abs(so - 7.25e-3) / 7.25e-3 < 0.05
    assert CLR.regime_from_lambda(so) == "boundary"


def test_simulate_fills_lubrication_fields():
    res = simulate(Recipe(pressure_psi=3.0, rpm_wafer=60, rpm_platen=55))
    assert res.lubrication_regime is not None
    assert res.cmp_sommerfeld_number is not None
    assert res.cof_stribeck_estimate is not None
    assert res.cmp_sommerfeld_number > 0
    assert res.cof_stribeck_estimate > 0
    # MRR 경로는 이 진단과 무관하게 그대로여야 한다
    assert res.mrr_nm_per_min.shape == res.radius_m.shape


def test_higher_pressure_lowers_sommerfeld():
    # So = μU/(p·δeff) — 분모에 p가 있으니 압력↑ → So↓ (노트 §2 정의식)
    lo = simulate(Recipe(pressure_psi=3.0, rpm_wafer=60, rpm_platen=55))
    hi = simulate(Recipe(pressure_psi=20.0, rpm_wafer=60, rpm_platen=55))
    assert hi.cmp_sommerfeld_number < lo.cmp_sommerfeld_number
