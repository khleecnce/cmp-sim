"""EVIDENCE-RULES.md 판정표에 없는 판정번호를 코드/노트/테스트가 근거로 인용하면
FAIL — 판정#64(φ 산화제 농도 보간)·판정#72(글리신 억제항) 원장 누락 사고(둘 다
2026-09-19 복구, #64는 판정#69-종결의 부수 발견으로 지목됨)의 동형 재발 차단.

번호 표기가 두 갈래로 갈린다:

1. **접미사형**: `판정#49-B`(레짐 분리 하위판정)·`판정#69-종결`(종결 표시) — 번호
   뒤에 `-`로 시작하는 꼬리표가 붙는다. 정규식 `판정#(\\d+)`는 숫자만 캡처하고
   `-`이후는 매치에 안 잡히므로, 기반 번호(49·69)가 원장에 있으면 접미사와
   무관하게 통과한다 — 별도 분기 없이 정규식 선택 자체로 성립한다.
2. **분할행형**: `24A`·`24B`·`24C` — EVIDENCE-RULES.md 판정표 자체가 "24"를 단일
   행이 아니라 24A/24B/24C 세 행으로 쪼개 등록했다(원장 확인: bare "24" 행은
   존재하지 않음). 그런데 저장소 전체 40여 곳이 이 셋을 묶어 **"판정#24"로
   총칭**하는 것이 기존(이 회차 이전부터의) 관례다 — 오타가 아니라 확립된 용법.
   그래서 두 단계로 판정한다: (a) 번호에 글자가 **직접 붙은** 형태(`24A`)는
   원장에 그 정확한 행이 있어야 통과, (b) 순수 숫자만인 형태(`24`)는 그 숫자를
   베이스로 하는 행이 하나라도(단독 행이든 분할행 계열이든) 원장에 있으면 통과.
   이렇게 나누는 이유: 그래야 `24D`처럼 실제로 없는 분할행을 총칭 축약과
   구분해서 여전히 잡아낼 수 있다.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()
LEDGER_FILE = REPO_ROOT / "EVIDENCE-RULES.md"

SCAN_DIRS = ["sim", "knowledge", "tests", "tools", "validation"]
SCAN_EXTS = {".py", ".md", ".yaml", ".yml", ".json"}
EXCLUDE_DIR_NAMES = {".venv", "build", "dist", "papers", "_knowledge_audit"}

# 번호 뒤 글자가 하이픈 없이 바로 붙은 것(24A)까지 하나의 참조로 캡처한다.
# `-B`·`-종결`처럼 하이픈이 낀 접미사는 \d+ 가 하이픈 앞에서 멈추므로 그냥 숫자만 남는다.
REF_RE = re.compile(r"판정#(\d+[A-Za-z]?)")
TABLE_ROW_RE = re.compile(r"^\|\s*(\d+[A-Za-z]?)\s*\|")


def _is_excluded_dir(rel_parts) -> bool:
    for part in rel_parts:
        if part in EXCLUDE_DIR_NAMES:
            return True
        if part.startswith(".night_") or part.endswith(".egg-info"):
            return True
    return False


def _iter_scan_files():
    for name in SCAN_DIRS:
        base = REPO_ROOT / name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in SCAN_EXTS:
                continue
            resolved = path.resolve()
            if resolved == THIS_FILE:
                continue
            rel_parts = resolved.relative_to(REPO_ROOT).parts[:-1]
            if _is_excluded_dir(rel_parts):
                continue
            yield resolved
    for path in REPO_ROOT.glob("*.md"):
        resolved = path.resolve()
        if resolved == LEDGER_FILE.resolve():
            continue
        yield resolved


def _parse_ledger():
    """원장 행 id 전체(문자 그대로, 예 '24A')와 그 베이스 숫자 집합을 함께 반환한다."""
    full_ids = set()
    base_numbers = set()
    for line in LEDGER_FILE.read_text(encoding="utf-8").splitlines():
        m = TABLE_ROW_RE.match(line)
        if m:
            row_id = m.group(1)
            full_ids.add(row_id)
            base_numbers.add(int(re.match(r"\d+", row_id).group(0)))
    return full_ids, base_numbers


def _is_known_reference(ref: str, full_ids: set, base_numbers: set) -> bool:
    if re.match(r"^\d+[A-Za-z]$", ref):
        return ref in full_ids
    return int(ref) in base_numbers


def _iter_references():
    for path in _iter_scan_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in REF_RE.finditer(line):
                if " not in " in line[m.end():]:
                    # 존재하지 않는 번호를 의도적으로 리터럴로 적어 파서의 부재-판정을
                    # 검증하는 네거티브 테스트(예: tests/test_c2_closures.py 의
                    # `assert "판정#9999" not in rows`) — 실제 인용이 아니므로 제외.
                    continue
                yield m.group(1), path, lineno


def test_no_dangling_evidence_references():
    full_ids, base_numbers = _parse_ledger()
    assert full_ids, (
        "EVIDENCE-RULES.md 판정표에서 행을 하나도 못 읽었다 — 표 파서가 깨졌을 가능성"
    )

    missing = [
        (ref, path.relative_to(REPO_ROOT), lineno)
        for ref, path, lineno in _iter_references()
        if not _is_known_reference(ref, full_ids, base_numbers)
    ]

    if missing:
        lines = [f"판정#{ref} — 참조 위치 {p}:{ln}" for ref, p, ln in sorted(missing)]
        pytest.fail(
            "EVIDENCE-RULES.md 판정표에 없는 판정번호가 참조되고 있다 "
            "(원장 행 누락 또는 오타):\n" + "\n".join(lines)
        )


def test_ledger_numbers_with_no_referrers_are_informational_only():
    """원장에 있는데 아무데서도 참조 안 되는 번호는 정상 상황 — FAIL 시키지 않는다.

    참조가 나중에 추가되거나(다른 회차 작업), 판정이 단독으로 완결돼 후속 인용이
    없을 수 있다 — 이 자체는 결함이 아니다. 정보 출력만 한다.
    """
    full_ids, _base_numbers = _parse_ledger()
    referenced = {ref for ref, _path, _lineno in _iter_references()}
    # 총칭("24")과 분할행("24A") 둘 다 "참조됨"으로 인정하려면 베이스 숫자로 정규화해 비교한다.
    referenced_bases = {re.match(r"\d+", r).group(0) for r in referenced}
    ledger_bases = {re.match(r"\d+", fid).group(0) for fid in full_ids}

    unreferenced = sorted(int(b) for b in (ledger_bases - referenced_bases))
    print(f"\n[정보] 원장에는 있으나 어디서도 참조되지 않은 판정번호(베이스 기준) "
          f"{len(unreferenced)}건: {unreferenced}")
