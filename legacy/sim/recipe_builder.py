"""구성요소 스키마 → 레시피 변환.

왜: 실무자는 "세리아 1차 60nm, 함량 1.5wt%, BTA 5mM, pH 4" 로 생각하고,
엔진은 kp_m_per_pa·abrasive_size_nm·inhibitor_mM·slurry_ph 로 계산한다.
이 파일이 그 사이를 잇는다.

핵심 원칙 — **연결되지 않은 것은 조용히 버리지 않는다.**
사용자가 "함량 20wt%"를 입력했는데 엔진에 함량 축이 없으면, 그 사실을 결과에
띄운다. 입력이 무시됐는데 그럴듯한 숫자가 나오는 것이 최악이다.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
COMP_DIR = ROOT / "knowledge" / "components"


def load_schemas() -> Dict[str, dict]:
    import yaml
    out = {}
    for f in sorted(COMP_DIR.glob("*.yaml")):
        d = yaml.safe_load(f.read_text()) or {}
        out[d.get("component", f.stem)] = d
    return out


def field_index() -> Dict[str, dict]:
    """'slurry.abrasive.type' → 필드 정의."""
    idx = {}
    for cname, spec in load_schemas().items():
        for g in spec.get("groups", []):
            for fl in g.get("fields", []):
                idx[f"{cname}.{g['id']}.{fl['key']}"] = {
                    **fl, "_component": cname, "_group": g["id"],
                    "_group_label": g.get("label", g["id"]),
                    "_owner": g.get("owner", spec.get("owner")),
                }
    return idx


def to_overrides(values: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """구성요소 값 → (팩 오버라이드, 경고 목록).

    values: {"slurry.abrasive.primary_size_nm": 60, "slurry.ph_control.ph": 4, ...}
    반환:   ({"abrasive_size_nm": 60, "slurry_ph": 4}, ["⚠ 함량 20wt%는 ..."])
    """
    idx = field_index()
    over: Dict[str, Any] = {}
    warn: List[str] = []
    for path, val in values.items():
        if val in (None, ""):
            continue
        fl = idx.get(path)
        if fl is None:
            warn.append(f"⚠ 알 수 없는 항목 '{path}' — 무시했다")
            continue
        mt = fl.get("maps_to")
        if mt and fl.get("status") in ("wired", "partial"):
            over[mt] = val
        else:
            lbl = fl.get("label", fl["key"])
            own = fl.get("_owner", "?")
            warn.append(
                f"⚠ [{fl['_group_label']}] {lbl} = {val} → **시뮬레이터에 반영되지 않았다.** "
                f"연결식이 아직 없다(담당 {own}). 결과는 이 입력과 무관하다."
            )
    return over, warn


def coverage() -> Dict[str, Any]:
    """무엇이 연결됐고 무엇이 안 됐나 — UI가 '빈 곳'을 보여주는 근거."""
    idx = field_index()
    by_comp: Dict[str, Dict[str, int]] = {}
    for p, fl in idx.items():
        c = fl["_component"]
        d = by_comp.setdefault(c, {"wired": 0, "partial": 0, "not_wired": 0})
        d[fl.get("status", "not_wired")] = d.get(fl.get("status", "not_wired"), 0) + 1
    return {"total_fields": len(idx), "by_component": by_comp}


if __name__ == "__main__":
    ov, wn = to_overrides({
        "slurry.abrasive.primary_size_nm": 60,
        "slurry.abrasive.content_wt_pct": 20,      # 미연결 — 경고 나와야 함
        "slurry.ph_control.ph": 4.0,
        "slurry.inhibitor.cu_inhibitor_mM": 5,
    })
    print("오버라이드:", ov)
    for w in wn:
        print(w)
    print("\n커버리지:", coverage())
