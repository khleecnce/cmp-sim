"""데이터셋 YAML이 인용하는 knowledge/ 노트 경로가 실제로 존재하는지 검사.

2026-09-18 실제 사고(판정#58 수거 중 적발): `rank_only_ruling` 본문이
"상세: knowledge/cmp/cu-us9200180b2-absolute-mrr-domain-extrapolation.md"
라고 적었는데 그런 파일은 없었다(실제 노트명은 다름). 판정 근거 문자열은
사람이 나중에 따라가 읽으라고 있는 것이라, 죽은 링크는 근거가 없는 것과
실질적으로 같다 — 그런데 어떤 게이트도 이걸 잡지 않았다.

verify_claims.py 는 노트 **안의** DOI 실존을 보고, check_knowledge.py 는
노트 자체를 본다. 데이터셋 YAML → 노트 방향의 링크는 사각지대였다.
"""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "validation" / "datasets"

# 본문 어디에 있든 knowledge/... .md 로 보이는 토큰을 전부 뽑는다.
PAT = re.compile(r"knowledge/[A-Za-z0-9_./-]+\.md")


def _dataset_files():
    return sorted(DS.glob("*.yaml"))


def test_datasets_exist():
    assert _dataset_files(), "데이터셋이 하나도 없다 — 경로 가정이 깨졌다"


@pytest.mark.parametrize("path", _dataset_files(), ids=lambda p: p.stem)
def test_referenced_knowledge_notes_exist(path):
    try:
        d = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:  # 파싱 실패는 다른 테스트의 몫
        pytest.skip(f"YAML 파싱 실패: {e}")

    def walk(v):
        if isinstance(v, str):
            yield v
        elif isinstance(v, dict):
            for x in v.values():
                yield from walk(x)
        elif isinstance(v, list):
            for x in v:
                yield from walk(x)

    missing = []
    for text in walk(d):
        for ref in PAT.findall(text):
            if not (ROOT / ref).exists():
                missing.append(ref)
    assert not missing, (
        f"{path.name} 이 존재하지 않는 노트를 인용한다: {sorted(set(missing))}. "
        "판정 근거 문자열의 링크가 죽어 있으면 근거를 따라갈 수 없다 — "
        "파일명을 고치거나 노트를 만들어라."
    )
