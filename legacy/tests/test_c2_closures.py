"""C2 종결 원장(validation/C2-CLOSURES.yaml)의 계약.

이 원장은 "문헌이 구조적으로 없어 3회차 규칙으로 영구 종결한 칸"만 담는다.
느슨해지는 경로이므로 오히려 계약을 더 세게 건다 —
  ① 등록된 모든 칸은 검증(valid)을 통과해야 한다(판정 실존 + 종결 선언 + 노트 존재)
  ② 원장은 값도 confidence 도 바꾸지 않는다(칸의 confidence 는 여전히 < literature)
  ③ 모든 종결에는 재오픈 조건이 있어야 한다(영구 봉인 금지)
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.completion import CONF_RANK, MIN_CONF, c2_closures, grid  # noqa: E402


@pytest.fixture(scope="module")
def g():
    return grid()


def test_all_registered_closures_are_valid():
    cl = c2_closures()
    assert cl, "종결 원장이 비어 있다 — 파일 경로/파싱 확인"
    bad = {k: v["invalid"] for k, v in cl.items() if not v["valid"]}
    assert not bad, f"검증 실패한 종결 등록: {bad}"


def test_closures_do_not_touch_values(g):
    """원장에 올라간 칸은 여전히 confidence < literature 여야 한다.
    (올라갔다고 등급이 올라가면 그건 오염이다.)"""
    for (factor, pack), meta in c2_closures().items():
        c = g[factor][pack]
        assert CONF_RANK.get(c.get("confidence", ""), 0) < CONF_RANK[MIN_CONF], (
            f"{factor}/{pack} 는 이미 {c.get('confidence')} 다 — 원장에서 빼라"
        )


def test_every_closure_has_reopen_condition():
    for k, meta in c2_closures().items():
        assert str(meta.get("reopen_if", "")).strip(), f"{k}: reopen_if 없음 — 영구 봉인 금지"
        assert str(meta.get("reason", "")).strip(), f"{k}: reason 없음"


def test_fake_judgment_number_is_rejected(tmp_path, monkeypatch):
    """존재하지 않는 판정 번호를 적으면 종결로 인정되지 않는다 — grep 우회 방지."""
    import tools.completion as C
    rows = C._evidence_rule_rows()
    assert "판정#22" in rows and "종결" in rows["판정#22-종결"]
    assert "판정#9999" not in rows
