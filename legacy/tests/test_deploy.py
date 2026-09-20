"""배포 산출물 계약 — 패키징이 깨지면 여기서 걸린다."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_pack_dir_resolution_prefers_repo():
    """개발 중에는 knowledge/params 를 본다(에이전트가 노트와 함께 갱신하는 정본)."""
    from sim.params import _PACK_DIR
    assert _PACK_DIR.name == "params"
    assert _PACK_DIR.exists(), f"팩 디렉토리 없음: {_PACK_DIR}"


def test_pack_dir_env_override(monkeypatch, tmp_path):
    """고객이 자기 팩 디렉토리를 지정할 수 있어야 한다(온프레미스 요구).

    ⚠ importlib.reload(sim.params)는 금지다. 다른 모듈이 이미 import한
    ParamMissing 등의 클래스 객체가 갈려서 `except ParamMissing`이 안 걸린다
    (2026-09-06 전체 실행에서 test_missing_param_raises_not_guesses가 이걸로 깨졌다).
    해석 함수만 직접 호출해 검증한다.
    """
    import sim.params as P
    monkeypatch.setattr(P, "_ENV_DIR", str(tmp_path))
    assert P._resolve_pack_dir() == tmp_path
    monkeypatch.setattr(P, "_ENV_DIR", None)
    assert P._resolve_pack_dir().name == "params"


def test_entry_points_declared():
    """fabsim / fabsim-studio 명령이 pyproject에 선언되어 있어야 한다."""
    txt = (ROOT / "pyproject.toml").read_text()
    assert 'fabsim = "sim.cli:main"' in txt
    assert 'fabsim-studio = "sim.launch:main"' in txt


def test_cli_runs_as_module():
    """설치본에서 `python -m sim.cli`가 동작하는가."""
    r = subprocess.run([sys.executable, "-m", "sim.cli", "--list-models"],
                       cwd=ROOT, capture_output=True, text=True, timeout=90)
    assert r.returncode == 0, r.stderr[-500:]
    assert "tier2.gw_physical_kp" in r.stdout


def test_dockerfile_excludes_research_material():
    """연구 노트·논문·에이전트는 배포 이미지에 들어가면 안 된다.

    저작권(논문 PDF)과 영업비밀(에이전트 조직·조사 범위) 둘 다의 문제다.
    """
    df = (ROOT / "Dockerfile").read_text()
    assert "COPY knowledge/params/" in df, "물성 팩은 포함되어야 한다"
    for bad in ("COPY papers", "COPY agents", "COPY knowledge/ "):
        assert bad not in df, f"배포 이미지에 {bad} 가 들어있다"
    di = (ROOT / ".dockerignore").read_text()
    assert "papers/" in di and "agents/" in di


def test_dockerfile_runs_nonroot():
    df = (ROOT / "Dockerfile").read_text()
    assert "USER fabsim" in df, "컨테이너를 root로 실행하면 안 된다"


@pytest.mark.parametrize("mod", ["sim.launch", "sim.cli"])
def test_deploy_modules_import(mod):
    __import__(mod)


def test_api_catalog_shape():
    """웹 UI가 화면을 그리는 데 필요한 필드가 다 오는가."""
    pytest.importorskip("fastapi")
    from sim.api import catalog
    c = catalog()
    assert len(c["slots"]) == 6
    for s in c["slots"]:
        assert s["impls"], f"{s['id']} 슬롯에 구현이 없다"
        for im in s["impls"]:
            assert im["status"] in ("verified", "sourced", "warn", "unsourced")
    assert any(p["id"] == "cu_h2o2_bta" for p in c["packs"])


def test_api_simulate_reports_limits():
    """API 결과가 '못 내는 값'을 명시하는가 — 배포본에서도 정직해야 한다."""
    pytest.importorskip("fastapi")
    from sim.api import api_simulate, SimRequest
    d = api_simulate(SimRequest(pack="oxide_silica", initial_thickness_nm=1000))
    assert d["not_computed"], "미산출 항목을 보고하지 않는다"
    assert "dishing" in d["not_computed"]
    assert len(d["trace"]) == 6
    assert "definition" in d["metrics"]


def test_api_rejects_unknown_slot():
    pytest.importorskip("fastapi")
    from fastapi import HTTPException
    from sim.api import api_simulate, SimRequest
    with pytest.raises(HTTPException):
        api_simulate(SimRequest(slots={"kp": "does_not_exist"}))


def test_web_ui_has_no_external_deps():
    """오프라인 고객망에서 떠야 한다 — CDN 링크가 있으면 안 된다."""
    html = (ROOT / "sim" / "web" / "index.html").read_text()
    for bad in ("cdn.", "https://unpkg", "googleapis", "jsdelivr"):
        assert bad not in html, f"외부 의존 발견: {bad}"
