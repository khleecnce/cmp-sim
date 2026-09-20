"""qa_loop 감사기의 papers/ 탐색 범위 회귀 테스트.

배경 (2026-09-15, Max워커): 특허 원문 HTML 475건이 `papers/patents/` 하위에 있는데
`_paper_texts()`/`_all_paper_names()`가 `PAPERS.glob("*")`(최상위만)를 써서 전혀 보지
못했다. 그 결과 F2(출처 원문 미확보) 플래그가 실제보다 10건 과다 집계되고, 확보돼
있는 특허 8건에 대해 F1(원문 값 대조)이 아예 실행되지 않았다. 여기서 고정하는 계약:

  1. papers/ 하위 디렉터리의 텍스트 파일도 발견된다.
  2. img/·optical_constants/ 는 본문이 아니므로 제외된다.
  3. 최상위 파일이 동명의 하위 파일보다 우선한다(중복 시 결정적).
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_qa_loop(papers_dir: Path):
    spec = importlib.util.spec_from_file_location("qa_loop_under_test", ROOT / "tools" / "qa_loop.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.PAPERS = papers_dir
    return mod


@pytest.fixture
def fake_papers(tmp_path):
    p = tmp_path / "papers"
    (p / "patents").mkdir(parents=True)
    (p / "img" / "seo2001").mkdir(parents=True)
    (p / "optical_constants").mkdir()
    (p / "toplevel2020-study.txt").write_text("removal rate 123.4 nm/min", encoding="utf-8")
    (p / "somepaper.pdf").write_bytes(b"%PDF-1.4 binary")
    (p / "patents" / "US9200180B2.html").write_text("<p>polishing rate 4567 A/min</p>", encoding="utf-8")
    (p / "patents" / "TW202115224A.html").write_text("<p>rate 88 nm/min</p>", encoding="utf-8")
    (p / "img" / "seo2001" / "fig3.txt").write_text("SHOULD NOT BE INDEXED", encoding="utf-8")
    (p / "optical_constants" / "si.txt").write_text("SHOULD NOT BE INDEXED", encoding="utf-8")
    return p


def test_subdirectory_texts_are_discovered(fake_papers):
    q = _load_qa_loop(fake_papers)
    texts = q._paper_texts()
    assert "US9200180B2.html" in texts, "papers/patents/ 하위 특허 원문이 감사기에 보여야 한다"
    assert "TW202115224A.html" in texts
    assert "toplevel2020-study.txt" in texts, "최상위 파일은 계속 보여야 한다(회귀 방지)"


def test_image_and_optical_dirs_are_excluded(fake_papers):
    q = _load_qa_loop(fake_papers)
    texts = q._paper_texts()
    names = q._all_paper_names()
    assert "fig3.txt" not in texts and "fig3.txt" not in names
    assert "si.txt" not in texts and "si.txt" not in names


def test_all_paper_names_includes_binaries_and_subdirs(fake_papers):
    q = _load_qa_loop(fake_papers)
    names = q._all_paper_names()
    assert "somepaper.pdf" in names, "텍스트 미추출 PDF도 파일명 폴백용으로 남아야 한다"
    assert "US9200180B2.html" in names


def test_toplevel_wins_on_duplicate_name(fake_papers):
    (fake_papers / "dup.txt").write_text("TOP", encoding="utf-8")
    (fake_papers / "patents" / "dup.txt").write_text("SUB", encoding="utf-8")
    q = _load_qa_loop(fake_papers)
    assert q._paper_texts()["dup.txt"] == "TOP"


def test_patent_source_now_resolves_to_file(fake_papers):
    """F2가 사라지는 실제 경로 — 특허번호 출처가 하위 HTML에 매칭되어야 한다."""
    q = _load_qa_loop(fake_papers)
    papers = q._paper_texts()
    sf = q._find_source_file("US9200180B2 Example 5 table", papers, {}, "us9200180b2_cu_h2o2_series",
                             q._all_paper_names())
    assert sf == "US9200180B2.html"


def test_real_repo_patents_dir_is_visible_if_present():
    """실제 저장소: papers/patents/ 가 있으면(로컬 개발환경) 감사기가 봐야 한다.

    papers/patents/ 는 .gitignore 대상이라 CI에는 없다 — 없으면 스킵한다.
    """
    real = ROOT / "papers" / "patents"
    if not real.is_dir() or not any(real.glob("*.html")):
        pytest.skip("papers/patents/ 없음(CI 또는 미확보 환경)")
    q = _load_qa_loop(ROOT / "papers")
    sample = next(real.glob("*.html")).name
    assert sample in q._paper_texts()
