"""시간축 시뮬레이션 계약 — 층 전이·반경별 endpoint·출력값 연속성."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.engine import Recipe
from sim.timeline import Layer, run_timeline


def _sti():
    return [Layer("TEOS", 500, "sti_ceria"),
            Layer("SiN", 80, None),
            Layer("Si", 775000, None, stop=True)]


def test_thickness_monotone_and_conserved():
    r = run_timeline(_sti(), Recipe(pack="sti_ceria"), total_s=60, dt_s=2)
    prev = None
    for f in r.frames:
        cur = f.remaining_nm[0][0]
        if prev is not None:
            assert cur <= prev + 1e-9
        prev = cur
    # 60s × 283 nm/min ≈ 283 nm 제거 — 오차 5% 이내
    removed = 500 - r.frames[-1].remaining_nm[0][0]
    assert abs(removed - r.frames[0].mean_mrr * 60 / 60) / removed < 0.05


def test_layer_transition_uses_selectivity_not_zero():
    """SiN에 팩이 없어도 선택비(60)로 느려진 MRR — 0이 아니고 원래 MRR도 아님."""
    r = run_timeline(_sti(), Recipe(pack="sti_ceria"), total_s=180, dt_s=3)
    assert r.endpoint_s is not None
    after = [f for f in r.frames if f.t_s > r.endpoint_s + 3]
    assert after, "endpoint 이후 프레임이 있어야"
    m = after[-1].mean_mrr
    assert 0 < m < r.frames[0].mean_mrr / 30
    assert after[-1].remaining_nm[1][0] < 80  # SiN이 조금은 깎임
    assert any("선택비" in n for n in r.notes)


def test_radius_dependent_endpoint_with_zone_pressure():
    """엣지 압력↑ → 엣지가 먼저 뚫린다. 전반경 endpoint > 최초 돌파."""
    r = run_timeline(_sti(), Recipe(pack="sti_ceria", zone_pressures_psi=[2.6, 3.0, 3.6],
                                    zone_edges_norm=[0.5, 0.85, 1.0]), total_s=180, dt_s=2)
    first = r.layer_breakthrough_s["TEOS"]
    assert first is not None and r.endpoint_s is not None
    assert r.endpoint_s > first
    # 최초 돌파 시점에 엣지는 층1, 중심은 층0
    f = next(f for f in r.frames if f.t_s >= first)
    assert f.exposed_layer[-1] == 1 and f.exposed_layer[0] == 0


def test_outputs_persist_across_transition():
    """층이 바뀌어도 온도·μ가 None으로 사라지지 않는다 (장비 조건은 그대로)."""
    r = run_timeline(_sti(), Recipe(pack="sti_ceria"), total_s=180, dt_s=3)
    assert all(f.outputs["pad_temp_c"] is not None for f in r.frames)
    assert all(f.outputs["cof"] is not None for f in r.frames)


def test_stop_layer_never_removed():
    r = run_timeline(_sti(), Recipe(pack="sti_ceria"), total_s=600, dt_s=5)
    assert all(f.remaining_nm[2][i] == 775000 for f in r.frames for i in (0, -1))


def test_empty_or_unmodeled_first_layer_raises():
    with pytest.raises(ValueError):
        run_timeline([], Recipe(pack="sti_ceria"), total_s=10)
    with pytest.raises(ValueError):
        run_timeline([Layer("X", 100, None)], Recipe(pack="sti_ceria"), total_s=10)


def test_no_false_selectivity_note_on_substrate():
    """film → Si(stop) 직행 스택: 기판에 선택비 근사 노트가 찍히면 거짓이다."""
    r = run_timeline([Layer("HDP", 300, "sti_ceria"), Layer("Si", 775000, None, stop=True)],
                     Recipe(pack="sti_ceria"), total_s=120, dt_s=2)
    assert r.endpoint_s is not None
    assert not any("선택비" in n for n in r.notes)
    assert all(f.remaining_nm[1][0] == 775000 for f in r.frames)


def test_frame_cap():
    r = run_timeline(_sti(), Recipe(pack="sti_ceria"), total_s=10000, dt_s=0.5)
    assert len(r.frames) <= 401
    assert any("제한" in n for n in r.notes)
