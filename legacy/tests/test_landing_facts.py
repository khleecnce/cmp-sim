"""sim/web_facts.py + demo_landing() 렌더의 회귀 방지 테스트.

demo.html 의 숫자는 전에 손으로 박혀 있었고, 실제 코드/데이터와 조용히
어긋났었다(material systems 5→6, held-out datasets 21→20, pytest 675→실측,
corpus full text 1,510→1,527, Python 3.11→3.9). 이 테스트는 (a) 토큰이
전부 치환됐는지, (b) 치환된 값이 아티팩트와 실제로 일치하는지, (c) 옛
드리프트 값이 다시 나타나면 실패하는지, (d) 아티팩트가 없어도 안 죽는지를 검사한다.
"""
import json
import re
import sqlite3

import pytest

from sim.api import demo_landing
from sim.web_facts import landing_facts

pytestmark = pytest.mark.filterwarnings("ignore")


def _rendered_body() -> str:
    return demo_landing().body.decode("utf-8")


def test_no_unreplaced_tokens():
    body = _rendered_body()
    assert "{{" not in body
    assert "}}" not in body


def test_material_count_matches_available_packs():
    from sim.params import available_packs

    packs = [p for p in available_packs() if p != "base"]
    facts = landing_facts()
    assert facts["FABSIM_MATERIAL_COUNT"] == str(len(packs))
    body = _rendered_body()
    assert f"<b>{len(packs)}</b><span>material systems:" in body
    # 표시 라벨 개수가 실제 팩 개수와 1:1 대응해야 한다 — 목록이 손유지로
    # 따로 드리프트하지 않았는지 확인.
    list_str = facts["FABSIM_MATERIAL_LIST"]
    assert len(list_str.split(", ")) == len(packs)


def test_heldout_count_matches_dataset_files():
    import yaml

    from sim.web_facts import ROOT

    ds_dir = ROOT / "validation" / "datasets"
    files = [f for f in ds_dir.glob("*.yaml") if f.stem != "_TEMPLATE"]
    heldout = sum(
        1 for f in files
        if not (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("used_for_calibration")
    )
    facts = landing_facts()
    assert facts["FABSIM_HELDOUT_COUNT"] == str(heldout)


def test_accuracy_facts_match_loop_ledger():
    from sim.web_facts import ROOT

    last = None
    with (ROOT / "validation" / "loop_ledger.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                last = line
    row = json.loads(last)
    facts = landing_facts()
    assert facts["FABSIM_SIG_N"] == str(row["accuracy"]["significant_n"])
    rho = round(row["accuracy"]["rho_significant"], 2)
    assert facts["FABSIM_RHO"] == f"+{rho:.2f}"


def test_cells_facts_match_completion_last():
    from sim.web_facts import ROOT

    data = json.loads((ROOT / "validation" / "completion_last.json").read_text(encoding="utf-8"))
    facts = landing_facts()
    assert facts["FABSIM_CELLS_TOTAL"] == str(data["cells_total"])
    assert facts["FABSIM_CELLS_ESTIMATED"] == str(
        len(data.get("closed") or []) + len(data.get("fails") or [])
    )


def test_corpus_facts_match_sqlite():
    """⚠ 이 테스트는 data/corpus/corpus.sqlite 가 있을 때만 의미가 있다.

    그 파일은 .gitignore(33행)에 있어 **커밋되지 않는다**. 따라서
    `.githooks/pre-push` 가 HEAD 를 임시 디렉토리에 git archive 해서 돌리는
    클린 트리에는 DB 가 존재하지 않고, connect() 는 빈 파일을 새로 만든 뒤
    'no such table: documents' 로 죽는다 — 즉 이 테스트는 클린 트리에서
    **구조적으로 통과할 수 없었고**, 그 결과 모든 크론의 push 가 막혀 있었다
    (2026-09-18 발견). DB 가 없으면 검사할 대상 자체가 없으므로 skip 한다.
    """
    from sim.web_facts import ROOT

    db = ROOT / "data" / "corpus" / "corpus.sqlite"
    if not db.exists():
        pytest.skip(f"코퍼스 DB 없음(.gitignore 대상): {db} — 클린 트리에서는 검사 대상이 없다")
    con = sqlite3.connect(str(db))
    try:
        total = con.execute("select count(*) from documents").fetchone()[0]
        fulltext = con.execute(
            "select count(*) from documents where fulltext_path is not null and fulltext_path != ''"
        ).fetchone()[0]
    finally:
        con.close()
    facts = landing_facts()
    assert facts["FABSIM_CORPUS_TOTAL"] == f"{total:,}"
    assert facts["FABSIM_CORPUS_FULLTEXT"] == f"{fulltext:,}"


def test_python_version_matches_runtime():
    import sys

    facts = landing_facts()
    assert facts["FABSIM_PYTHON_VERSION"] == f"{sys.version_info.major}.{sys.version_info.minor}"


def test_stale_drifted_values_do_not_reappear():
    """어제까지 손유지되던 틀린 값들 — 다시 나타나면 드리프트 재발."""
    body = _rendered_body()
    for stale in ("675 tests", "of 50", "1,510", "Python 3.11"):
        assert stale not in body, f"stale drifted value {stale!r} reappeared in demo.html render"


def test_landing_facts_survives_missing_artifacts(monkeypatch, tmp_path):
    """배포 슬림 빌드에는 corpus.sqlite / validation 아티팩트가 없을 수 있다 —
    죽지 않고 '—' 로 떨어져야 하며, 옛 하드코딩 값으로 폴백해서는 안 된다."""
    empty_root = tmp_path / "empty_root"
    empty_root.mkdir()
    monkeypatch.setattr("sim.web_facts.ROOT", empty_root)

    facts = landing_facts()

    assert facts["FABSIM_HELDOUT_COUNT"] == "—"
    assert facts["FABSIM_SIG_N"] == "—"
    assert facts["FABSIM_RHO"] == "—"
    assert facts["FABSIM_PYTEST_COUNT"] == "—"
    assert facts["FABSIM_CELLS_ESTIMATED"] == "—"
    assert facts["FABSIM_CELLS_TOTAL"] == "—"
    assert facts["FABSIM_CORPUS_TOTAL"] == "—"
    assert facts["FABSIM_CORPUS_FULLTEXT"] == "—"
    # 예전 하드코딩 값이 폴백으로 슬쩍 들어오면 안 된다.
    for stale in ("21", "675", "1,510", "50"):
        assert facts["FABSIM_HELDOUT_COUNT"] != stale
        assert facts["FABSIM_PYTEST_COUNT"] != stale


def test_demo_landing_renders_with_missing_artifacts(monkeypatch, tmp_path):
    empty_root = tmp_path / "empty_root2"
    empty_root.mkdir()
    monkeypatch.setattr("sim.web_facts.ROOT", empty_root)

    body = _rendered_body()
    assert "{{" not in body
    assert "—" in body


def test_pytest_count_is_collected_not_read_from_lagging_ledger():
    """pytest 개수는 **테스트 트리 수집**으로 세야 한다 — 원장에서 읽으면 뒤처진다.

    2026-09-17 실측: 최초 구현이 validation/loop_ledger.jsonl 의 tests.summary
    (951)에서 읽었는데 실제 수집값은 1012 였다(61건 차이). 원장은 별도 크론이
    append 할 때만 갱신되므로, 손유지 상수를 '뒤처지는 아티팩트'로 바꾼 것은
    드리프트를 고친 것이 아니다. 이 테스트가 그 회귀를 막는다.
    """
    from sim.web_facts import ROOT, landing_facts as _lf

    # (1) 산출값이 지금 이 트리의 실제 수집 개수와 일치한다.
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--collect-only", "-p", "no:cacheprovider"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=180,
    )
    m = re.search(r"(\d+)\s+tests?\s+collected", proc.stdout)
    assert m, f"collect-only 출력에서 개수를 못 읽음: {proc.stdout[-500:]}"
    assert _lf()["FABSIM_PYTEST_COUNT"] == m.group(1)

    # (2) 원장의 tests.summary 와 갈릴 때 원장 쪽을 따라가지 않는다.
    last = None
    with (ROOT / "validation" / "loop_ledger.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                last = line.strip()
    ledger_n = re.match(r"(\d+)\s+passed", json.loads(last).get("tests", {}).get("summary", ""))
    if ledger_n and ledger_n.group(1) != m.group(1):
        assert _lf()["FABSIM_PYTEST_COUNT"] != ledger_n.group(1), (
            "원장의 뒤처진 pytest 개수를 그대로 싣고 있다 — 수집값을 써야 한다"
        )
