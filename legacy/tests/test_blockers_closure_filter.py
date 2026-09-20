"""blockers.py 가 영구 종결된 칸을 병목으로 내놓지 않는지 고정한다.

왜 이 테스트가 있는가 (2026-09-20, 판정#79)
──────────────────────────────────────────
`validation/C2-CLOSURES.yaml` 에 등록된 칸은 EVIDENCE-RULES 3회차 규칙으로
**영구 종결**된 것이다 — "고치면 격자가 오른다"가 성립하지 않는다.
그런데 `blockers.py` 는 종결 원장을 전혀 읽지 않아, 판정#79 로
`delta/cu_alkaline_benzenesulfonic` 을 종결한 **직후에도** 그 칸을 1위 병목으로
계속 출력했다. 그대로 두면 다음 회차 작업자가 그 순위를 보고 **4회차를 돈다**
— 즉 도구가 규칙 위반을 유도한다.

이 테스트가 고정하는 계약:
  (1) 기본 실행은 유효 종결 칸을 cells 에서 뺀다.
  (2) include_closed=True 는 그 칸을 되살리고 closed=True 로 표시한다.
  (3) 종결되지 않은 미충족 칸은 두 모드 모두에서 보인다(과잉 필터 방지).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.blockers import analyze              # noqa: E402
from tools.completion import c2_closures        # noqa: E402


def _cellset(cells):
    return {(c["factor"], c["pack"]) for c in cells}


def _valid_closures():
    return {k for k, v in c2_closures().items() if v.get("valid")}


def test_valid_closures_are_hidden_by_default():
    valid = _valid_closures()
    assert valid, "종결 원장이 비었다 — 이 테스트의 전제가 깨졌다"
    _, cells = analyze()
    leaked = valid.intersection(_cellset(cells))
    assert not leaked, f"영구 종결 칸이 병목으로 새어 나왔다: {sorted(leaked)}"


def test_include_closed_restores_them_and_marks_them():
    valid = _valid_closures()
    _, cells = analyze(include_closed=True)
    by = {(c["factor"], c["pack"]): c for c in cells}
    restored = valid.intersection(set(by))
    assert restored, "include_closed 로도 종결 칸이 하나도 안 보인다"
    for k in restored:
        assert by[k]["closed"] is True, f"{k}: closed 플래그가 안 붙었다"
        assert by[k]["closure_judgments"], f"{k}: 판정 번호가 비었다"


def test_judgment_79_delta_cell_specifically_closed():
    """판정#79 가 실제로 이 도구에 반영됐는지 — 회귀의 원점을 직접 못 박는다."""
    k = ("delta", "cu_alkaline_benzenesulfonic")
    cl = c2_closures().get(k)
    assert cl and cl["valid"], f"판정#79 종결 등록이 유효하지 않다: {cl}"
    assert "판정#79" in cl["judgments"], cl["judgments"]
    _, cells = analyze()
    assert k not in _cellset(cells)


def test_open_cells_still_visible():
    """과잉 필터 방지 — 종결되지 않은 미충족 칸은 계속 보여야 한다."""
    valid = _valid_closures()
    _, with_closed = analyze(include_closed=True)
    open_cells = _cellset(with_closed).difference(valid)
    _, default = analyze()
    assert open_cells.issubset(_cellset(default)), "종결 안 된 칸이 함께 필터됐다"
