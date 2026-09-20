#!/usr/bin/env python3
"""주장 검증기 — 노트의 "문헌값/재현" 주장을 기계가 실제로 확인한다.

왜 (2026-09-05 사용자 지시 "할루시네이션 전혀 없도록 설계해"):
  LLM은 그럴듯한 숫자와 출처를 지어낸다. 사람이 읽어서는 못 잡는다.
  실측: 노트 22편의 "문헌값 일치" 주장 77건 중 같은 줄에 출처가 있는 건 1건(1%).
  대책은 "조심하라"는 지시가 아니라 **주장을 실행 가능하게 만들고 기계가 실행하는 것**이다.

검증 4종:
  1. 출처 실존   — DOI/PMC/arXiv를 실제 API로 조회. 지어낸 문헌은 여기서 죽는다.
  2. 코드 재현   — ```python verify 블록을 실제로 실행. assert 실패 = 반려.
  3. 수치 추적   — 수치 주장에 출처 앵커가 붙어 있는가.
  4. 코드 역추적 — sim/ 상수가 어느 노트의 어느 주장에서 왔는가.

사용:
  python3 tools/verify_claims.py --all           # 전체
  python3 tools/verify_claims.py --offline       # 네트워크 없이(코드·앵커만)
  python3 tools/verify_claims.py knowledge/x.md
  python3 tools/verify_claims.py --trace sim/tier1_empirical/preston.py
"""
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"
CACHE = ROOT / "agents" / ".source_cache.json"

# 출처 식별자
DOI = re.compile(
    r"(?:doi\.org/|doi:\s*)(10\.\d{4,9}/(?:\(\d{1,4}\)|[^\s\)\]\},;\"'*_`<])+)",
    re.I)
PMC = re.compile(r"PMC(\d{5,})")
ARXIV = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", re.I)
PATENT = re.compile(r"(?:patents\.google\.com/patent/)?\b((?:US|EP|JP|KR|CN)\d{6,}[A-Z]?\d?)\b")

# 검증 코드 블록: ```python verify ... ```
VERIFY_BLOCK = re.compile(r"```python\s+verify\s*\n(.*?)```", re.S)

# 수치 주장: 숫자+단위가 있는 줄
UNIT = (r"nm/min|nm|µm|um|mm|cm|m/s|m|kPa|MPa|GPa|Pa|psi|mV|V|kT|%|°C|K|"
        r"rpm|min|h|s|mL/min|wt%|mol/L|M\b")
NUM_CLAIM = re.compile(rf"\d+(?:\.\d+)?(?:e-?\d+)?\s*(?:{UNIT})")
# 출처 앵커: (Author 2024) / [^src] / doi / PMC / 특허번호 / [[노트링크]]
ANCHOR = re.compile(
    r"\([A-Z][A-Za-z\-]+(?:\s+et\s+al\.?)?[^)]{0,40}(?:19|20)\d{2}[^)]*\)"
    r"|\[\^[a-z0-9\-]+\]|doi|PMC\d|arxiv|patent|(?:US|EP|JP|KR|CN)\d{6,}"
    r"|\[\[[^\]]+\]\]", re.I)
# 검증 주장 키워드
CLAIM_KW = re.compile(r"문헌값|재현|대조|일치|수렴|검증")
# 정직한 미검증 선언 — 이게 있으면 앵커 없어도 통과(정직성 보상)
HONEST = re.compile(r"미검증|추정|확인 못|불명|출처 불명|2차 인용|앵커 대조값|오더만")


def load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text())
        except Exception:
            return {}
    return {}


def save_cache(c: dict):
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(c, ensure_ascii=False, indent=1))


def fetch(url: str, timeout=10) -> tuple:
    """(ok, 제목 또는 오류)"""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "fab-sim-verify/1.0 (research; contact via repo)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, type(e).__name__


def check_source(kind: str, ident: str, cache: dict) -> tuple:
    """출처가 실존하는가. (ok, 설명)"""
    key = f"{kind}:{ident}"
    if key in cache:
        c = cache[key]
        return c["ok"], c["msg"]

    if kind == "doi":
        ok, data = fetch(f"https://api.crossref.org/works/{urllib.parse.quote(ident)}")
        msg = (data["message"].get("title", [""])[0][:90] if ok
               else f"Crossref 미등록 ({data})")
        if not ok:
            # 폴백: 학위논문·리포지토리·데이터셋 DOI는 Crossref가 아니라 DataCite에 등록된다
            # (2026-09-13 slurry-colloid: UAlberta ERA 논문 10.7939/... 가 404로 잘못 반려됨)
            ok2, d2 = fetch(f"https://api.datacite.org/dois/{urllib.parse.quote(ident)}")
            if ok2:
                try:
                    ok = True
                    msg = (d2["data"]["attributes"]["titles"][0]["title"][:90]
                           + " [DataCite]")
                except Exception:
                    ok, msg = True, "DataCite 등록 확인(제목 파싱 실패)"
    elif kind == "pmc":
        ok, data = fetch(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            f"?db=pmc&id={ident}&retmode=json")
        if ok:
            res = data.get("result", {})
            rec = res.get(ident, {})
            ok = bool(rec) and "error" not in rec
            msg = rec.get("title", "")[:90] if ok else "PMC 미등록"
        else:
            msg = f"조회 실패 ({data})"
    elif kind == "arxiv":
        try:
            req = urllib.request.Request(
                f"http://export.arxiv.org/api/query?id_list={ident}",
                headers={"User-Agent": "fab-sim-verify/1.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read().decode()
            ok = "<entry>" in body and "<title>" in body
            m = re.search(r"<entry>.*?<title>(.*?)</title>", body, re.S)
            msg = (m.group(1).strip()[:90] if ok and m else "arXiv 미등록")
        except Exception as e:
            ok, msg = False, type(e).__name__
    else:  # patent — 형식만 검사(무료 조회 API가 불안정)
        return True, "형식 확인(내용 미조회)"

    cache[key] = {"ok": ok, "msg": msg}
    time.sleep(0.35)          # API 예의
    return ok, msg


def run_verify_blocks(path: Path) -> list:
    """노트의 ```python verify 블록을 실제로 실행한다. 실패 = 주장이 거짓."""
    text = path.read_text()
    blocks = VERIFY_BLOCK.findall(text)
    out = []
    for i, code in enumerate(blocks, 1):
        r = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT, capture_output=True, text=True, timeout=120)
        ok = r.returncode == 0
        err = (r.stderr.strip().splitlines() or [""])[-1][:160]
        out.append({"n": i, "ok": ok, "err": err,
                    "out": r.stdout.strip()[-200:]})
    return out


def check_note(path: Path, cache: dict, offline: bool) -> dict:
    text = path.read_text()
    lines = text.splitlines()
    res = {"sources": [], "blocks": [], "untraced": [], "path": path}

    # 1. 출처 실존
    if not offline:
        for kind, rx in (("doi", DOI), ("pmc", PMC), ("arxiv", ARXIV),
                         ("patent", PATENT)):
            for ident in sorted(set(rx.findall(text))):
                ident = ident.rstrip(".,;")
                ok, msg = check_source(kind, ident, cache)
                res["sources"].append((kind, ident, ok, msg))

    # 2. 코드 재현
    res["blocks"] = run_verify_blocks(path)

    # 3. 수치 추적 — 검증 주장 + 수치가 있는데 출처 앵커가 없는 줄
    #    단, verify 블록 내부는 제외한다(그 블록이 곧 증명이다).
    blk_ranges = []
    for m in VERIFY_BLOCK.finditer(text):
        blk_ranges.append((text[:m.start()].count("\n") + 1,
                           text[:m.end()].count("\n") + 1))
    # 검증 코드가 통과한 노트는 그 코드가 커버하는 수치를 신뢰한다
    verified_nums = set()
    if res["blocks"] and all(b["ok"] for b in res["blocks"]):
        for a, b in blk_ranges:
            for ln in lines[a - 1:b]:
                verified_nums.update(re.findall(r"\d+(?:\.\d+)?", ln))

    def in_block(i):
        return any(a <= i <= b for a, b in blk_ranges)

    for i, ln in enumerate(lines, 1):
        if in_block(i):
            continue
        if not (CLAIM_KW.search(ln) and NUM_CLAIM.search(ln)):
            continue
        if ANCHOR.search(ln) or HONEST.search(ln):
            continue
        # verify 블록이 이미 assert한 수치면 통과 (단위 붙은 수치 기준)
        nums = set(re.findall(r"(\d+(?:\.\d+)?)(?:e-?\d+)?\s*(?:" + UNIT + ")", ln))
        if nums and nums <= verified_nums:
            continue
        # 앞뒤 2줄 안에 앵커가 있으면 통과(문단 단위 인용 허용)
        ctx = "\n".join(lines[max(0, i - 3):i + 2])
        if ANCHOR.search(ctx) or HONEST.search(ctx):
            continue
        res["untraced"].append((i, ln.strip()[:110]))
    return res


def trace_constant(target: Path) -> list:
    """sim/ 파일의 상수가 어느 노트에서 왔는지 역추적."""
    text = target.read_text()
    out = []
    for m in re.finditer(r"^([A-Z_][A-Z0-9_]{2,})\s*=\s*([-\d.e+]+)", text, re.M):
        name, val = m.group(1), m.group(2)
        line_no = text[:m.start()].count("\n") + 1
        ctx = "\n".join(text.splitlines()[max(0, line_no - 4):line_no + 2])
        note = re.search(r"knowledge/([a-z0-9_\-]+/[a-z0-9_\-]+)|\[\[([^\]]+)\]\]", ctx)
        honest = bool(HONEST.search(ctx))
        out.append({"name": name, "val": val, "line": line_no,
                    "note": (note.group(1) or note.group(2)) if note else None,
                    "honest": honest})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--offline", action="store_true", help="네트워크 조회 생략")
    ap.add_argument("--trace", help="sim/ 파일 상수 역추적")
    a = ap.parse_args()

    if a.trace:
        rows = trace_constant(Path(a.trace))
        print(f"■ 상수 역추적 — {a.trace}")
        bad = 0
        for r in rows:
            src = r["note"] or ("(미검증 선언됨)" if r["honest"] else "❌ 근거 없음")
            if not r["note"] and not r["honest"]:
                bad += 1
            print(f"  L{r['line']:<4} {r['name']:<22} = {r['val']:<12} ← {src}")
        print(f"\n근거 없는 상수 {bad}건" if bad else "\n모든 상수에 근거 또는 미검증 선언 있음")
        return 1 if bad else 0

    # `_`로 시작하는 파일은 형식 정본(_SCHEMA.md 등)이지 지식 노트가 아니다 —
    # check_knowledge.py 와 같은 규칙으로 제외한다(그쪽은 이미 제외 중이었다).
    # 이 어긋남 때문에 _SCHEMA.md 가 "검증 코드 블록 없음"으로 영구 반려 상태였다.
    targets = ([p for p in KNOWLEDGE.rglob("*.md")
                if p.name != "INDEX.md" and not p.name.startswith("_")]
               if a.all else [Path(p) for p in a.paths])
    if not targets:
        print("검사할 노트가 없다")
        return 1

    cache = load_cache()
    fail = 0
    tot_src = bad_src = tot_blk = bad_blk = tot_untr = 0

    for p in sorted(targets):
        r = check_note(p, cache, a.offline)
        rel = p.relative_to(KNOWLEDGE) if KNOWLEDGE in p.parents else p
        probs = []

        for kind, ident, ok, msg in r["sources"]:
            tot_src += 1
            if not ok:
                bad_src += 1
                probs.append(f"❌ 출처 실존 안 함: {kind}:{ident} — {msg}")

        for b in r["blocks"]:
            tot_blk += 1
            if not b["ok"]:
                bad_blk += 1
                probs.append(f"❌ 검증 코드 #{b['n']} 실패: {b['err']}")

        for ln, txt in r["untraced"]:
            tot_untr += 1
            probs.append(f"⚠ L{ln} 출처 없는 수치 주장: {txt}")

        if not r["blocks"]:
            probs.append("⚠ 검증 코드 블록 없음 (```python verify) "
                         "— 수식·수치 주장을 기계가 확인할 방법이 없다")

        if probs:
            fail += 1
            print(f"✗ {rel}")
            for x in probs[:6]:
                print(f"    {x}")
            if len(probs) > 6:
                print(f"    … 외 {len(probs)-6}건")
        else:
            nb = len(r["blocks"])
            ns = len(r["sources"])
            print(f"✓ {rel}  (출처 {ns}건 실존 · 코드 {nb}블록 통과)")

    save_cache(cache)
    print(f"\n{len(targets)-fail}/{len(targets)} 통과")
    print(f"출처 {tot_src}건 중 실존 안 함 {bad_src} · "
          f"검증코드 {tot_blk}블록 중 실패 {bad_blk} · 출처없는 수치주장 {tot_untr}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
