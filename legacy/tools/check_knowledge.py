#!/usr/bin/env python3
"""지식노트 품질 게이트 — 병렬 학습에서 졸작이 섞이는 것을 막는다.

배경(2026-09-04 사용자 지시: "품질중심이지"):
  FabSim 학습을 병렬로 돌려 기간을 단축하되, 속도 때문에 노트가 얕아지면
  의미가 없다. 사람 눈으로 5개를 매번 검수할 수 없으므로 코드가 자른다.

기준은 기존 합격 노트(hertz-gw-contact-mechanics.md,
preston-luo-dornfeld-mrr.md)에서 역산했다. 그 둘이 통과해야 기준이 정당하다.

사용:
  python check_knowledge.py knowledge/materials/새노트.md
  python check_knowledge.py --all          # 전체 회귀 검사
종료코드 0=통과, 1=미달(위반 항목 출력)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path.home() / 'fab-sim'
KNOWLEDGE = ROOT / 'knowledge'

MIN_LINES = 40           # 합격 노트 최소가 51줄 — 여유를 두되 스텁은 거른다
MIN_CITATIONS = 3        # 연도 표기 인용 최소 3건
MIN_SECTIONS = 3         # ## 절 최소 3개
MIN_LINKS = 1            # [[상호링크]] 최소 1개 — 고립 노트 방지

YEAR = re.compile(r'(?:\((?:19|20)\d{2}\)|(?:19|20)\d{2}-\d{2}|'
                  r'(?:et al\.?|,)\s*(?:19|20)\d{2}\b|'
                  r'\*[^*]+\*\s*\(?(?:19|20)\d{2})')
URL = re.compile(r'https?://|doi[:.]|arxiv|PMC\d+|\.(?:org|edu|jp|com)\b', re.I)
WIKILINK = re.compile(r'\[\[[^\]]+\]\]')
SECTION = re.compile(r'^##\s+', re.M)
# "검증했다"고 주장하려면 근거가 함께 있어야 한다.
VERIFY_CLAIM = re.compile(r'재현|검증|문헌값|sanity|대조')
# 정직성 표지: 확인 못 한 것을 확인 못 했다고 쓰는가
HONESTY = re.compile(r'미검증|추정|확인 못|불명|출처 불명|2차 인용')
# 1차 출처 식별자 — 리뷰/초록 2차 인용과 구분한다.
PRIMARY = re.compile(r'doi\.org/10\.|doi:\s*10\.|PMC\d{5,}|arxiv\.org/abs/'
                     r'|patents\.google|US\d{7,}|JP\d{6,}|KR\d{6,}', re.I)
# 정량 재현 — "문헌값/재현/대조" 근처에 단위 붙은 수치가 실제로 있는가.
QUANT = re.compile(
    r'(?:재현|검증|문헌값|대조|sanity)[^\n]{0,160}?'
    r'\d+(?:\.\d+)?\s*(?:nm|µm|um|mm|m|Pa|kPa|MPa|GPa|mV|kT|%|°C|K|rpm|m/s|'
    r'nm/min|min|h|s|배|자릿수)'
    r'|\d+(?:\.\d+)?\s*(?:nm|µm|um|mm|Pa|kPa|MPa|GPa|mV|kT|%|nm/min)'
    r'[^\n]{0,160}?(?:재현|문헌값|대조|일치|수렴)')
MAX_UNVERIFIED = 6   # 이 이상이면서 정량값의 절반을 넘으면 반려


def check(path: Path) -> list[str]:
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    bad: list[str] = []

    if len(lines) < MIN_LINES:
        bad.append(f'분량 부족: {len(lines)}줄 < {MIN_LINES}줄 (스텁 의심)')

    cites = len(YEAR.findall(text))
    urls = len(URL.findall(text))
    if cites < MIN_CITATIONS and urls < MIN_CITATIONS:
        bad.append(f'출처 부족: 연도인용 {cites}건 / URL·DOI {urls}건 '
                   f'(둘 중 하나가 {MIN_CITATIONS}건 이상이어야 함)')

    if len(SECTION.findall(text)) < MIN_SECTIONS:
        bad.append(f'구조 부족: ## 절 {len(SECTION.findall(text))}개 < {MIN_SECTIONS}개')

    if len(WIKILINK.findall(text)) < MIN_LINKS:
        bad.append('상호링크 없음: [[다른노트]] 최소 1개 — 고립된 노트는 지식베이스가 아니다')

    if not VERIFY_CLAIM.search(text):
        bad.append('검증 흔적 없음: 수식/수치를 문헌값과 대조한 서술이 없다')

    if not HONESTY.search(text):
        bad.append('정직성 표지 없음: 확인하지 못한 항목을 "미검증/추정"으로 '
                   '명시하지 않았다 (전부 확신하는 노트는 신뢰할 수 없다)')

    # ── 품질 우선 원칙 (2026-09-05 사용자: "빨리하는 것 중요. 하지만 품질 우선")
    # 속도를 위해 병렬 배차를 켜는 대신, 게이트를 이만큼 조인다.

    # (1) 1차 출처: 2차 인용(리뷰·초록)만으로 쌓은 노트를 거른다.
    if not PRIMARY.search(text):
        bad.append('1차 출처 없음: DOI/PMC/arXiv/특허번호 중 최소 1건이 필요하다 '
                   '(리뷰·초록·2차 인용만으로는 파라미터를 신뢰할 수 없다)')

    # (2) 정량 재현: "검증했다"는 서술만 있고 숫자가 없으면 검증이 아니다.
    if not QUANT.search(text):
        bad.append('정량 재현 없음: 문헌값과 대조한 구체적 수치(단위 포함)가 없다 '
                   '— "검증했다"는 서술만으로는 통과시키지 않는다')

    # (3) 미검증 과다: 핵심 수치 대부분이 미검증이면 노트가 아니라 메모다.
    n_un = len(re.findall(r'미검증', text))
    n_num = len(re.findall(r'\d+(?:\.\d+)?\s*(?:nm|µm|um|mm|m|Pa|kPa|MPa|GPa|'
                           r'mV|kT|%|°C|K|rpm|m/s|min|h|s)\b', text))
    if n_un > MAX_UNVERIFIED and n_un > n_num * 0.5:
        bad.append(f'미검증 과다: 미검증 {n_un}건 vs 정량값 {n_num}건 '
                   f'— 절반 이상이 미검증이면 후속 단원에서 쓸 수 없다')

    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='*')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()

    # '_'로 시작하는 파일은 지식 노트가 아니라 형식 규약·감사 메모다
    # (_SCHEMA.md 등). 노트 게이트(인용 3건·검증 흔적)를 적용할 대상이 아니다.
    targets = ([p for p in KNOWLEDGE.rglob('*.md')
                if p.name != 'INDEX.md' and not p.name.startswith('_')]
               if a.all else [Path(p) for p in a.paths])
    if not targets:
        print('검사할 노트가 없다')
        return 1

    failed = 0
    for p in targets:
        if not p.exists():
            print(f'✗ {p} — 파일 없음')
            failed += 1
            continue
        bad = check(p)
        rel = p.relative_to(KNOWLEDGE) if KNOWLEDGE in p.parents else p
        if bad:
            failed += 1
            print(f'✗ {rel}')
            for b in bad:
                print(f'    - {b}')
        else:
            print(f'✓ {rel}')

    print(f'\n{len(targets) - failed}/{len(targets)} 통과')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
