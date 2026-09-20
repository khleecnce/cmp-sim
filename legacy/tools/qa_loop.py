#!/usr/bin/env python3
"""모델 QA 루프 — 학습 중 만들어진 모델을 매 회차 검증하고, 퇴보를 막고, 가짜 데이터를 걸러낸다.

사용자 지시 (2026-09-08):
  "학습 중 지속적으로 만들어진 모델을 검증해. 루프를 통해서 QA 모델의 성능 검증 해.
   루프가 일정이상 진행되면 가짜 데이터를 걸러내"

세 가지 일
──────────
1. LEDGER  — 매 실행의 백테스트 성적을 `validation/ledger.jsonl`에 남긴다(커밋 해시·시각·
             유의 ρ·데이터셋별 결과). 시간에 따라 모델이 나아지는지/퇴보하는지 보인다.
2. GATE    — 직전 커밋 대비 **퇴보**를 잡는다. 유의 데이터셋의 ρ가 떨어지거나, 유의하던
             데이터셋이 유의하지 않게 되면 FAIL. 크론은 FAIL이면 그 커밋을 되돌린다.
             (테스트 통과는 계약이 안 깨졌다는 뜻이지 예측이 나아졌다는 뜻이 아니다.)
3. AUDIT   — 데이터셋의 **실측값이 출처에 실제로 있는지** 대조한다. 확보한 논문 원문
             (papers/*.xml, *.txt, papers/patents/*.html 등 하위 포함)에서 각 mrr 값(또는 그 원단위)을 찾는다. 못 찾는 값이 많은
             데이터셋은 QUARANTINE(격리) 후보다. 루프가 일정 횟수 이상 돈 뒤(기본 20회차,
             즉 데이터셋이 충분히 쌓인 뒤)에는 격리 데이터셋을 집계에서 자동 제외한다.

"가짜 데이터"의 정의 (기계가 잡을 수 있는 것만)
───────────────────────────────────────────
  F1. 출처 원문에 없는 숫자        — papers/ 원문 대조 실패율 > 50%
  F2. 출처 파일 자체가 없음        — DOI/특허번호가 papers/INDEX.json·datasets에 없음
  F3. 통계적으로 부자연스러움      — 조건 간 MRR 값이 정확히 등차/등비, 또는 유효숫자가
                                     전부 같은 자리(0.0/5.0으로 끝남) → 손으로 지어낸 패턴
  F4. 자기 채점                    — used_for_calibration 누락인데 팩 source가 같은 문헌
  F5. 모델에 지나치게 잘 맞음      — ρ=1.000, MAPE<5%인데 digitized (그래프 판독이 이 정도로
                                     맞을 수 없다 → 예측값을 보고 적었을 가능성)
사람이 넣은 정직한 데이터도 F3에 걸릴 수 있다 — 그래서 격리는 삭제가 아니라 **집계 제외 +
플래그**이고, 해제는 사람이 원문을 확인하고 `audit_verified: true`를 파일에 적는 것으로 한다.

명령
────
  qa_loop.py run            — 백테스트 + 원장 기록 + 게이트 판정 + 감사 (크론용, exit 1 = FAIL)
  qa_loop.py audit          — 감사만 (데이터셋별 F1~F5 플래그)
  qa_loop.py history [-n N] — 원장 추세
  qa_loop.py quarantine     — 현재 격리 목록
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "validation"))

LEDGER = ROOT / "validation" / "ledger.jsonl"
QUAR = ROOT / "validation" / "quarantine.json"
DS_DIR = ROOT / "validation" / "datasets"
PAPERS = ROOT / "papers"

QUARANTINE_AFTER_RUNS = 20      # 루프가 이만큼 돈 뒤부터 격리를 집계에 자동 적용
RHO_DROP_TOL = 0.05             # 유의 데이터셋 ρ가 이만큼 넘게 떨어지면 퇴보
FAIL_MISSING_RATIO = 0.5        # F1: 원문 대조 실패율
FETCH = False                   # run --fetch 시 누락 원문 자동 확보


# ───────────────────────────────────────────────── 원장
def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                       text=True).strip()
    except Exception:
        return "?"


def _load_ledger() -> List[Dict]:
    if not LEDGER.exists():
        return []
    return [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]


def run_backtest() -> Dict:
    import backtest
    res = backtest.run_all()
    quar = load_quarantine()
    n_runs = len(_load_ledger())
    apply_quar = n_runs >= QUARANTINE_AFTER_RUNS
    rows, sig = [], []
    for r in res:
        row = {"dataset": r.dataset, "n": r.n, "rho": round(r.spearman, 4),
               "p": None if r.p_value is None else round(r.p_value, 4),
               "mape": None if r.mape_pct is None else round(r.mape_pct, 1),
               "scale": None if r.scale_factor is None else round(r.scale_factor, 3),
               "in_scope": r.in_scope, "calib": r.used_for_calibration,
               "quarantined": r.dataset in quar}
        rows.append(row)
        usable = r.in_scope and not r.used_for_calibration and r.significant
        if apply_quar and r.dataset in quar:
            usable = False
        row["significant"] = bool(usable)
        if usable:
            sig.append(r.spearman)
    return {
        "ts": time.time(), "commit": _git_head(), "run_index": n_runs + 1,
        "n_datasets": len(rows), "n_significant": len(sig),
        "mean_rho_significant": round(sum(sig) / len(sig), 4) if sig else None,
        "quarantine_applied": apply_quar, "rows": rows,
    }


def append_ledger(entry: Dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ───────────────────────────────────────────────── 게이트
def gate(cur: Dict, prev: Optional[Dict]) -> Dict:
    """퇴보 판정. prev가 없으면 통과(첫 회차)."""
    if not prev:
        return {"status": "PASS", "reasons": ["첫 회차 — 기준선 기록"]}
    reasons, fail = [], False
    pm = {r["dataset"]: r for r in prev["rows"]}
    for r in cur["rows"]:
        p = pm.get(r["dataset"])
        if not p:
            reasons.append(f"+ 신규 데이터셋 {r['dataset']} (n={r['n']}, ρ={r['rho']:+.3f}, p={r['p']})")
            continue
        if p["significant"] and not r["significant"]:
            fail = True
            reasons.append(f"✗ {r['dataset']}: 유의→비유의 (p {p['p']}→{r['p']})")
        elif p["significant"] and r["significant"] and (p["rho"] - r["rho"]) > RHO_DROP_TOL:
            fail = True
            reasons.append(f"✗ {r['dataset']}: ρ {p['rho']:+.3f}→{r['rho']:+.3f} (Δ{r['rho']-p['rho']:+.3f})")
        elif r["significant"] and not p["significant"]:
            reasons.append(f"✓ {r['dataset']}: 비유의→유의 (ρ={r['rho']:+.3f})")
        elif r["significant"] and (r["rho"] - p["rho"]) > RHO_DROP_TOL:
            reasons.append(f"✓ {r['dataset']}: ρ {p['rho']:+.3f}→{r['rho']:+.3f}")
    a, b = prev.get("mean_rho_significant"), cur.get("mean_rho_significant")
    if a is not None and b is not None:
        reasons.append(f"유의 평균 ρ {a:+.3f} → {b:+.3f}")
        if b < a - RHO_DROP_TOL:
            fail = True
            reasons.append("✗ 유의 평균 ρ 퇴보")
    for r in cur["rows"]:
        if r["dataset"] not in pm:
            continue
    return {"status": "FAIL" if fail else "PASS", "reasons": reasons}


# ───────────────────────────────────────────────── 감사 (가짜 데이터)
# papers/ 하위에서 원문으로 취급하지 않는 디렉터리(그림 스캔·광학상수 표 등)
_PAPER_SKIP_DIRS = {"img", "optical_constants"}


def _paper_files() -> List[Path]:
    """papers/ **및 그 하위 디렉터리**의 파일 목록.

    2026-09-15 수정: 종전 `PAPERS.glob("*")`는 최상위만 봤다. 특허 원문 HTML은
    `papers/patents/` 아래에 475건 있는데 감사기가 이를 전혀 보지 못해
    F2(출처 원문 미확보)가 실제보다 과다 집계됐다(10→20건 관측, 모델 변경 아님).
    `img/`·`optical_constants/`는 본문 텍스트가 아니므로 제외한다.
    """
    out: List[Path] = []
    for f in PAPERS.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(PAPERS)
        if rel.parts and rel.parts[0] in _PAPER_SKIP_DIRS:
            continue
        out.append(f)
    return out


def _paper_texts() -> Dict[str, str]:
    """papers/(하위 포함) 안의 원문 텍스트를 (파일명→텍스트)로. 큰 파일은 앞 2MB만.

    최상위 파일이 같은 이름의 하위 파일보다 우선한다(중복 시 결정적 동작).
    """
    out: Dict[str, str] = {}
    for f in sorted(_paper_files(), key=lambda x: (len(x.relative_to(PAPERS).parts), str(x))):
        if f.suffix.lower() not in (".xml", ".txt", ".md", ".html"):
            continue
        if f.name in out:
            continue
        try:
            out[f.name] = f.read_text(encoding="utf-8", errors="ignore")[:2_000_000]
        except Exception:
            pass
    return out


def _numbers_in(text: str) -> set:
    """원문 속 숫자 집합. 천단위 쉼표(6,204)·공백을 제거해 6204로도 넣는다."""
    raw = re.findall(r"(?<![\d.])\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\d.])\d+(?:\.\d+)?(?![\d.])", text)
    out = set()
    for r in raw:
        out.add(r)
        out.add(r.replace(",", ""))
    return out


def _source_ids(src: str) -> List[str]:
    ids = re.findall(r"10\.\d{4,9}/[^\s\"'<>\)]+", src)
    ids += re.findall(r"\b(?:US|TW|KR|JP|EP|WO)\s?\d{4,}[A-Z]?\d?\b", src, flags=re.I)
    ids += re.findall(r"PMC\d+", src)
    ids += re.findall(r"figshare[:/]\s?\d+", src, flags=re.I)
    return [i.rstrip(".,;") for i in ids]


def _all_paper_names() -> List[str]:
    """papers/(하위 포함) 안의 모든 파일명(텍스트 추출 여부 무관) — 파일명 토큰 폴백용."""
    return [f.name for f in _paper_files()]


def _find_source_file(src: str, papers: Dict[str, str], index: Dict,
                       stem: str = "", all_names: Optional[List[str]] = None) -> Optional[str]:
    ids = _source_ids(src)
    for name in papers:
        for i in ids:
            if i.replace("/", "_") in name or i in name or i.lower().replace(" ", "") in name.lower():
                return name
    # INDEX.json 매핑 (doi → 파일)
    for i in ids:
        for k, v in (index or {}).items():
            if isinstance(v, dict):
                blob = json.dumps(v)
                if i in blob or i in k:
                    fn = v.get("file") or v.get("filename") or v.get("path") or v.get("pdf") or v.get("pdf_local")
                    if fn and Path(fn).name in papers:
                        return Path(fn).name
    # 파일명 토큰 폴백 — ID가 파일명에 없을 때. **ID 자체가 있는데** 매칭에
    # 실패한 경우에만 시도한다(ID가 전혀 없으면 stem이 "저자연도" 형식인지도
    # 불확실해 오매칭 위험이 커진다 — 예: "sic2026_..."의 "sic"를 저자로 오인해
    # 무관한 "...4hsic..." 파일에 매칭될 뻔했다). 저자 소문자 토큰(4자 이상,
    # 오인식 방지로 짧은 접두사(us/tw/cn 등)는 제외) + 19xx/20xx 연도가 **둘 다**
    # papers/ 파일명에 있어야 매칭.
    if ids and all_names:
        m = re.match(r"^([a-z]{4,})(19\d{2}|20\d{2})", stem.lower())
        if m:
            author, year = m.group(1), m.group(2)
            for name in all_names:
                lname = name.lower()
                if author in lname and year in lname:
                    return name
    return None


def _try_fetch_source(src: str) -> Optional[str]:
    """누락 원문을 확보해 papers/에 캐시한다. 특허 → Google Patents 본문(무료),
    DOI → PMC(무료, XML). 실패하면 None — 지어내지 않는다."""
    import urllib.request
    ua = {"User-Agent": "Mozilla/5.0 (fab-sim qa_loop)"}
    for i in _source_ids(src):
        i_clean = i.replace(" ", "")
        try:
            if re.match(r"(?i)^(US|TW|KR|JP|EP|WO)\d", i_clean):
                url = f"https://patents.google.com/patent/{i_clean.upper()}/en"
                html = urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=25).read().decode("utf-8", "ignore")
                txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
                txt = re.sub(r"<[^>]+>", " ", txt)
                if len(txt) > 5000:
                    fn = f"{i_clean.upper()}.txt"
                    (PAPERS / fn).write_text(txt, encoding="utf-8")
                    return fn
            elif i_clean.upper().startswith("PMC"):
                u = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{i_clean.upper()}/unicode"
                xml = urllib.request.urlopen(urllib.request.Request(u, headers=ua), timeout=25).read().decode("utf-8", "ignore")
                if len(xml) > 5000:
                    fn = f"{i_clean.upper()}.xml"
                    (PAPERS / fn).write_text(xml, encoding="utf-8")
                    return fn
            elif i_clean.startswith("10."):
                q = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v0.1/?ids={i_clean}&format=json"
                j = json.loads(urllib.request.urlopen(urllib.request.Request(q, headers=ua), timeout=20).read())
                pmc = (j.get("records") or [{}])[0].get("pmcid")
                if pmc:
                    u = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmc}/unicode"
                    xml = urllib.request.urlopen(urllib.request.Request(u, headers=ua), timeout=25).read().decode("utf-8", "ignore")
                    if len(xml) > 5000:
                        fn = f"{pmc}.xml"
                        (PAPERS / fn).write_text(xml, encoding="utf-8")
                        return fn
        except Exception:
            continue
    return None


def _pack_sources() -> Dict[str, Dict[str, Dict[str, str]]]:
    """팩 YAML을 파싱해 파라미터별 source/note **문자열 값만** 모은다.

    yaml.safe_load를 쓰므로 주석(#)은 파싱 단계에서 이미 사라진다 — F4가 주석에
    적힌 "held-out은 다른 문헌으로 한다" 같은 선언까지 자기채점으로 오탐하는
    문제를 구조적으로 없앤다. 반환: {팩이름: {파라미터이름: {"source"/"note": 문자열}}}
    """
    out: Dict[str, Dict[str, Dict[str, str]]] = {}
    for f in (ROOT / "knowledge" / "params").glob("*.yaml"):
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        params = d.get("params") or {}
        fields: Dict[str, Dict[str, str]] = {}
        for pname, pval in params.items():
            if not isinstance(pval, dict):
                continue
            texts = {}
            for key in ("source", "note"):
                v = pval.get(key)
                if isinstance(v, str) and v.strip():
                    texts[key] = v
            if texts:
                fields[pname] = texts
        out[f.stem] = fields
    return out


def audit_dataset(path: Path, papers: Dict[str, str], index: Dict,
                  pack_src: Dict[str, Dict[str, Dict[str, str]]],
                  last_rows: Dict[str, Dict], all_names: Optional[List[str]] = None) -> Dict:
    d = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    conds = d.get("conditions") or []
    flags, info = [], {}
    src = str(d.get("source", ""))
    if d.get("audit_verified"):
        return {"dataset": path.stem, "flags": [], "verified_by_human": True, "info": {}}

    # F2 출처 파일
    sf = _find_source_file(src, papers, index, path.stem, all_names)
    if sf is None and FETCH and _source_ids(src):
        sf = _try_fetch_source(src)
        if sf:
            papers[sf] = (PAPERS / sf).read_text(encoding="utf-8", errors="ignore")[:2_000_000]
            info["fetched"] = True
    info["source_file"] = sf
    if not _source_ids(src):
        flags.append("F2:출처에 DOI/특허번호 없음")
    elif sf is None:
        flags.append("F2:출처 원문 미확보(papers/) — 자동 확보 실패(유료/봉쇄), 사람이 넣어야 함")

    # F1 원문 대조 — mrr 값 또는 그 흔한 변환(Å/min = nm×10, Å/30s 등)을 찾는다
    # sf는 papers/ 파일명 토큰 폴백으로도 찾을 수 있어(PDF만 있고 텍스트 미추출)
    # 항상 papers(텍스트 딕셔너리)에 있는 건 아니다 — 없으면 대조를 생략한다.
    if sf and sf in papers:
        nums = _numbers_in(papers[sf])
        miss = 0
        for c in conds:
            v = c.get("mrr_nm_per_min")
            if v is None:
                continue
            cands = {f"{v:g}", f"{v*10:g}", f"{v/10:g}", f"{v:.0f}", f"{v*10:.0f}",
                     f"{v/2:g}", f"{v*60:g}", f"{v:.1f}"}
            if not (cands & nums):
                miss += 1
        info["values_not_in_source"] = f"{miss}/{len(conds)}"
        if conds and miss / len(conds) > FAIL_MISSING_RATIO:
            flags.append(f"F1:실측값 {miss}/{len(conds)}이 출처 원문에 없음")
    elif sf:
        info["values_not_in_source"] = "텍스트 미추출(PDF만 있음) — 원문대조 생략"

    # F3 부자연스러운 패턴
    vals = [float(c["mrr_nm_per_min"]) for c in conds if c.get("mrr_nm_per_min") is not None]
    if len(vals) >= 4:
        diffs = [round(b - a, 6) for a, b in zip(vals, vals[1:])]
        if len(set(diffs)) == 1 and diffs[0] != 0:
            flags.append("F3:MRR이 정확한 등차수열")
        ratios = [round(b / a, 6) for a, b in zip(vals, vals[1:]) if a]
        if len(ratios) == len(diffs) and len(set(ratios)) == 1:
            flags.append("F3:MRR이 정확한 등비수열")
        all_table = all(c.get("read_method") == "table" for c in conds)
        if not all_table and len(vals) >= 6 and all(v % 5 == 0 for v in vals):
            flags.append("F3:전 조건이 5의 배수 — 그래프 판독값답지 않음(어림수)")
        if len(set(vals)) == 1:
            flags.append("F3:전 조건 동일값")

    # F4 자기 채점 — 팩 파라미터의 source/note(파싱된 값, 주석 제외)에서 같은
    # 문헌 ID가 나오면 히트. calibration_contact에 신고돼 있으면 "미신고 자기채점"이
    # 아니라 "신고된 부분오염"(C4)으로 격하한다 — 격리 유발 soft flag 집계 제외.
    pk = d.get("pack")
    if pk and not d.get("used_for_calibration") and pk in pack_src:
        contacts = {(c.get("pack"), c.get("param")) for c in (d.get("calibration_contact") or [])}
        seen_params = set()
        for param_key, fields in pack_src[pk].items():
            if param_key in seen_params:
                continue
            for field_name, text in fields.items():
                hit = next((i for i in _source_ids(src) if i and i in text), None)
                if hit:
                    seen_params.add(param_key)
                    if (pk, param_key) in contacts:
                        flags.append(
                            f"C4:신고된 부분오염 — 팩 {pk}의 파라미터 {param_key}({field_name})가 "
                            f"같은 문헌({hit})에서 도출(calibration_contact 신고됨)")
                    else:
                        flags.append(
                            f"F4:팩 {pk}의 파라미터 {param_key}({field_name})가 같은 문헌({hit})에서 "
                            "도출 — used_for_calibration 누락")
                    break

    # F5 지나치게 잘 맞음
    r = last_rows.get(path.stem)
    if r and conds:
        digit = sum(1 for c in conds if c.get("read_method") == "digitized")
        if r["rho"] >= 0.999 and r.get("mape") is not None and r["mape"] < 5 and digit == len(conds):
            flags.append(f"F5:digitized인데 ρ=1.000·MAPE {r['mape']}% — 예측을 보고 적었을 가능성")
    return {"dataset": path.stem, "flags": flags, "verified_by_human": False, "info": info}


def audit_all(last_rows: Dict[str, Dict]) -> List[Dict]:
    papers = _paper_texts()
    index = {}
    ip = PAPERS / "INDEX.json"
    if ip.exists():
        try:
            index = json.loads(ip.read_text(encoding="utf-8"))
        except Exception:
            index = {}
    pack_src = _pack_sources()
    all_names = _all_paper_names()
    out = []
    for f in sorted(DS_DIR.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        out.append(audit_dataset(f, papers, index, pack_src, last_rows, all_names))
    return out


def load_quarantine() -> Dict[str, Dict]:
    if QUAR.exists():
        return json.loads(QUAR.read_text(encoding="utf-8"))
    return {}


def update_quarantine(audits: List[Dict]) -> Dict[str, Dict]:
    """F1/F5는 즉시 격리 후보, F2·F3·F4는 2개 이상 겹칠 때. 사람이 verified 하면 해제."""
    q = load_quarantine()
    present = {a["dataset"] for a in audits}
    for stale in [k for k in q if k not in present]:
        q.pop(stale)                      # 파일이 삭제된 데이터셋은 격리 목록에서도 뺀다
    for a in audits:
        name = a["dataset"]
        if a["verified_by_human"]:
            q.pop(name, None)
            continue
        hard = [f for f in a["flags"] if f.startswith(("F1", "F5"))]
        soft = [f for f in a["flags"] if f.startswith(("F3", "F4"))]
        f2 = any(f.startswith("F2") for f in a["flags"])
        # F2(원문 없음)는 단독으론 격리하지 않는다 — 유료 논문이 많아 정직한 데이터도 걸린다.
        # F2 + 패턴 이상(F3)이 겹치면 "확인할 수 없는데 모양도 이상함" → 격리.
        if hard or len(soft) >= 2 or (f2 and soft):
            q[name] = {"flags": a["flags"], "since": q.get(name, {}).get("since", time.time()),
                       "how_to_clear": "원문에서 값 확인 후 데이터셋 파일에 audit_verified: true 추가"}
        else:
            q.pop(name, None)
    QUAR.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    return q


# ───────────────────────────────────────────────── 명령
def cmd_run(a) -> int:
    global FETCH; FETCH = bool(getattr(a, "fetch", False))
    prev = _load_ledger()
    cur = run_backtest()
    g = gate(cur, prev[-1] if prev else None)
    cur["gate"] = g["status"]
    last_rows = {r["dataset"]: r for r in cur["rows"]}
    audits = audit_all(last_rows)
    q = update_quarantine(audits)
    cur["quarantine"] = sorted(q.keys())
    append_ledger(cur)

    print(f"QA 루프 #{cur['run_index']}  commit {cur['commit']}  게이트 {g['status']}")
    print(f"  유의 데이터셋 {cur['n_significant']}/{cur['n_datasets']}  유의 평균 ρ = {cur['mean_rho_significant']}")
    for r in g["reasons"]:
        print("  ", r)
    flagged = [x for x in audits if x["flags"]]
    print(f"\n감사: {len(audits)}개 데이터셋, 플래그 {len(flagged)}개, 격리 {len(q)}개"
          f" (격리 집계 적용: {'예' if cur['quarantine_applied'] else f'아니오 — {QUARANTINE_AFTER_RUNS}회차부터'})")
    for x in flagged:
        tag = "🔒격리" if x["dataset"] in q else "⚠"
        print(f"  {tag} {x['dataset']}: " + " | ".join(x["flags"]))
    if a.strict and g["status"] == "FAIL":
        return 1
    return 0


def cmd_audit(a) -> int:
    global FETCH; FETCH = bool(getattr(a, "fetch", False))
    led = _load_ledger()
    last_rows = {r["dataset"]: r for r in led[-1]["rows"]} if led else {}
    audits = audit_all(last_rows)
    for x in audits:
        s = "✓ human-verified" if x["verified_by_human"] else (" | ".join(x["flags"]) or "clean")
        extra = f"  [{x['info'].get('source_file','-')}, 원문미확인 {x['info'].get('values_not_in_source','-')}]" if x["info"] else ""
        print(f"{x['dataset']:45} {s}{extra}")
    if a.json:
        print(json.dumps(audits, ensure_ascii=False, indent=2))
    return 0


def cmd_history(a) -> int:
    led = _load_ledger()[-a.n:]
    if not led:
        print("원장 없음 — `qa_loop.py run`을 먼저")
        return 0
    print(f"{'#':>4} {'commit':8} {'시각':16} {'유의':>5} {'ρ_sig':>7} {'gate':5} 격리")
    for e in led:
        t = time.strftime("%m-%d %H:%M", time.localtime(e["ts"]))
        rho = "—" if e["mean_rho_significant"] is None else f"{e['mean_rho_significant']:+.3f}"
        print(f"{e['run_index']:>4} {e['commit']:8} {t:16} {e['n_significant']:>2}/{e['n_datasets']:<2} {rho:>7} {e.get('gate','-'):5} {len(e.get('quarantine',[]))}")
    return 0


def cmd_quarantine(a) -> int:
    q = load_quarantine()
    if not q:
        print("격리 없음")
    for k, v in q.items():
        print(f"🔒 {k}\n   " + "\n   ".join(v["flags"]) + f"\n   해제: {v['how_to_clear']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--strict", action="store_true", help="FAIL이면 exit 1"); r.add_argument("--fetch", action="store_true", help="누락 원문 자동 확보 시도")
    au = sub.add_parser("audit"); au.add_argument("--json", action="store_true"); au.add_argument("--fetch", action="store_true")
    h = sub.add_parser("history"); h.add_argument("-n", type=int, default=20)
    sub.add_parser("quarantine")
    a = ap.parse_args()
    return {"run": cmd_run, "audit": cmd_audit, "history": cmd_history, "quarantine": cmd_quarantine}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
