"""랜딩 페이지(demo.html)가 주장하는 숫자를 실제 아티팩트에서 산출한다.

배경: demo.html 은 전에 숫자를 손으로 박아 넣었고, 아무 테스트도 검사하지
않아서 실제 코드/데이터와 조용히 어긋났다(예: material systems 5→6,
held-out datasets 21→20, pytest 675→실측치, corpus fulltext 1,510→1,527).
이 모듈이 유일한 출처다 — demo.html 은 {{FABSIM_*}} 토큰만 담고,
sim.api.demo_landing() 이 landing_facts() 로 치환한다.

원칙: 아티팩트가 없으면(배포 슬림 빌드 등) 그 항목만 "—" 로 떨어뜨린다.
절대로 예전 하드코딩 값을 폴백으로 쓰지 않는다 — 그게 이 모듈이 고치려는 결함이다.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

_MISSING = "—"

ROOT = Path(__file__).resolve().parent.parent

# 팩 이름 → 랜딩 페이지용 표시 라벨. 새 팩이 추가돼도 매핑이 없으면
# 팩 이름을 그대로 보여준다(지어내지 않는다) — 그래서 개수는 절대 드리프트하지 않고,
# 라벨만 "예쁘지 않은 상태"로 정직하게 드러난다.
_MATERIAL_LABELS = {
    "oxide_silica": "TEOS/silica",
    "sti_ceria": "STI ceria",
    "cu_h2o2_bta": "Cu/H₂O₂/BTA",
    "w_fe_oxidizer": "W/Fe-oxidizer",
    "sic_ceria_h2o2": "SiC/ceria/H₂O₂",
    "sic_alumina_kmno4": "SiC/alumina/KMnO₄",
}


def _material_facts() -> Dict[str, str]:
    # source: sim/params.py::available_packs() (knowledge/params/*.yaml stems)
    try:
        from sim.params import available_packs

        packs = [p for p in available_packs() if p != "base"]
    except Exception:
        return {"FABSIM_MATERIAL_COUNT": _MISSING, "FABSIM_MATERIAL_LIST": _MISSING}
    labels = [_MATERIAL_LABELS.get(p, p) for p in sorted(packs)]
    return {
        "FABSIM_MATERIAL_COUNT": str(len(packs)),
        "FABSIM_MATERIAL_LIST": ", ".join(labels),
    }


def _dataset_facts() -> Dict[str, str]:
    # source: validation/datasets/*.yaml (excluding _TEMPLATE.yaml); held-out
    # means not used_for_calibration
    try:
        import yaml

        ds_dir = ROOT / "validation" / "datasets"
        if not ds_dir.exists():
            raise FileNotFoundError(ds_dir)
        files = [f for f in ds_dir.glob("*.yaml") if f.stem != "_TEMPLATE"]
        heldout = 0
        for f in files:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            if not d.get("used_for_calibration"):
                heldout += 1
        return {"FABSIM_HELDOUT_COUNT": str(heldout)}
    except Exception:
        return {"FABSIM_HELDOUT_COUNT": _MISSING}


def _accuracy_facts() -> Dict[str, str]:
    # source: validation/loop_ledger.jsonl, last line, "accuracy" block
    try:
        import json

        path = ROOT / "validation" / "loop_ledger.jsonl"
        last = None
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    last = line
        if last is None:
            raise ValueError("empty ledger")
        row = json.loads(last)
        acc = row["accuracy"]
        rho = round(acc["rho_significant"], 2)
        rho_s = f"{'+' if rho >= 0 else ''}{rho:.2f}"
        out = {
            "FABSIM_SIG_N": str(acc["significant_n"]),
            "FABSIM_RHO": rho_s,
        }
        return out
    except Exception:
        return {"FABSIM_SIG_N": _MISSING, "FABSIM_RHO": _MISSING}


@lru_cache(maxsize=1)
def _pytest_count(root: str) -> str:
    """pytest 개수는 **테스트 트리를 직접 수집해서** 센다.

    ⚠ 이전 구현은 validation/loop_ledger.jsonl 의 tests.summary 에서 읽었는데,
    그 원장은 별도 크론(정확도루프)이 append 할 때만 갱신되므로 **뒤처진다** —
    2026-09-17 실측으로 원장 951 vs 실제 1012 (61건 차이) 였다. 손유지 상수를
    '뒤처지는 아티팩트'로 바꾼 것은 드리프트를 못 고친 것이므로 수집으로 교체한다.

    수집은 실측 0.6s 이고 lru_cache 로 프로세스당 1회만 돈다. 실패하면
    (테스트 트리가 없는 슬림 배포 등) 옛 값을 꾸며내지 않고 '—' 로 떨어뜨린다.
    """
    import subprocess
    import sys

    root_path = Path(root)
    if not (root_path / "tests").exists():
        return _MISSING
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--collect-only", "-p", "no:cacheprovider"],
            cwd=root, capture_output=True, text=True, timeout=120,
        )
    except Exception:
        return _MISSING
    m = re.search(r"(\d+)\s+tests?\s+collected", proc.stdout)
    return m.group(1) if m else _MISSING


def _cells_facts() -> Dict[str, str]:
    # source: validation/completion_last.json (tools/completion.py::check() output)
    # "estimated" cells = cells closed via the C2(b) 검증된 한계 route + cells
    # still failing C2 — both carry confidence < literature.
    try:
        import json

        path = ROOT / "validation" / "completion_last.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        estimated = len(data.get("closed") or []) + len(data.get("fails") or [])
        return {
            "FABSIM_CELLS_ESTIMATED": str(estimated),
            "FABSIM_CELLS_TOTAL": str(data["cells_total"]),
        }
    except Exception:
        return {"FABSIM_CELLS_ESTIMATED": _MISSING, "FABSIM_CELLS_TOTAL": _MISSING}


def _corpus_facts() -> Dict[str, str]:
    # source: data/corpus/corpus.sqlite (documents table) — may be absent in slim builds
    try:
        import sqlite3

        path = ROOT / "data" / "corpus" / "corpus.sqlite"
        if not path.exists():
            raise FileNotFoundError(path)
        con = sqlite3.connect(str(path))
        try:
            total = con.execute("select count(*) from documents").fetchone()[0]
            fulltext = con.execute(
                "select count(*) from documents where fulltext_path is not null and fulltext_path != ''"
            ).fetchone()[0]
        finally:
            con.close()
        return {
            "FABSIM_CORPUS_TOTAL": f"{total:,}",
            "FABSIM_CORPUS_FULLTEXT": f"{fulltext:,}",
        }
    except Exception:
        return {"FABSIM_CORPUS_TOTAL": _MISSING, "FABSIM_CORPUS_FULLTEXT": _MISSING}


def _python_facts() -> Dict[str, str]:
    # source: running interpreter itself (sys.version_info) — this IS the deployed
    # Python, not a claim about it, so it can't drift from reality.
    import sys

    return {"FABSIM_PYTHON_VERSION": f"{sys.version_info.major}.{sys.version_info.minor}"}


def landing_facts() -> Dict[str, str]:
    """랜딩 페이지가 주장하는 숫자를 전부 실제 아티팩트에서 산출한다.

    각 하위 함수가 자기 아티팩트를 못 찾으면 해당 키만 "—" 로 떨어뜨리고
    나머지는 정상 계산된다(부분 실패가 전체를 죽이지 않는다).
    """
    out: Dict[str, str] = {}
    out.update(_python_facts())
    out.update(_material_facts())
    out.update(_dataset_facts())
    out.update(_accuracy_facts())
    out.update(_cells_facts())
    out.update(_corpus_facts())
    out["FABSIM_PYTEST_COUNT"] = _pytest_count(str(ROOT))
    return out
