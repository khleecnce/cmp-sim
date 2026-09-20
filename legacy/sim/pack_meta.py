"""슬러리 팩의 사람이 읽는 이름 — 내부 ID와 UI 표시를 분리한다.

사용자 지시(2026-09-11): "슬러리 팩 고르는거 좀더 큰 범위로 해. 이름도 슬러리
구분잘되도록 바꿔. 예를 들면 W 슬러리 연마매커니즘 xxx사용 이런식으로.
지금처럼 sic_ceria_h2o2 이러면 보기도안좋고 너무 국부적이야"

왜 파일명(내부 ID)을 안 바꾸는가:
  `sic_ceria_h2o2` 같은 stem 은 YAML 파일명, 검증 데이터셋의 pack 필드,
  테스트, ledger 기록, 크론 로그에 전부 박혀 있다. 이름을 바꾸면 과거 QA 기록과
  held-out 매칭이 끊긴다. 그래서 **표시 이름만 따로 둔다.**

어떻게 고르는가 — 사용자가 슬러리를 고를 때 실제로 묻는 순서:
  ① 무슨 막을 깎나 (Target film)      ← 가장 먼저 좁혀지는 축
  ② 어떤 메커니즘으로 깎나            ← 같은 막이어도 이게 다르면 다른 슬러리
  ③ 무슨 연마입자·케미컬을 쓰나        ← 실제 제품 구분
세 가지를 한 줄에 담는다: "W 플러그 — 산화·용해 (Fe(NO3)3 산화제 + 알루미나)"

`family` 는 '큰 범위' 요구에 대응한다. 슬러리 종류는 수백 가지이므로 팩 5개를
평면 나열하면 안 되고, 막질군으로 묶어 접근해야 한다.
"""
from __future__ import annotations

from typing import Any, Dict, List

# family: 막질 대분류 — UI에서 1차로 좁히는 축
#   label:    선택 목록에 보이는 한 줄 (막 — 메커니즘 (케미컬))
#   short:    좁은 화면·배지용 축약
#   film:     깎는 대상
#   mechanism: 제거가 일어나는 물리/화학 경로
#   chem:     연마입자 + 핵심 케미컬
#   note:     이 팩을 고를 때 알아야 할 한 가지 (적용 한계 위주)
PACK_META: Dict[str, Dict[str, Any]] = {
    "oxide_silica": {
        "family": "Oxide (SiO₂)",
        "label": "산화막 — 기계적 마모 (콜로이달 실리카)",
        "short": "Oxide / Silica",
        "film": "oxide",
        "film_label": "TEOS · PETEOS 산화막",
        "mechanism": "Preston형 기계적 마모. 화학은 pH로 표면 연화만 거든다",
        "chem": "콜로이달 실리카, pH 10~11",
        "note": "가장 검증된 기준 조건. 다른 팩의 비교 기준선으로 쓴다.",
    },
    "sti_ceria": {
        "family": "Oxide (SiO₂)",
        "label": "STI 산화막 — 화학적 결합 절단 (세리아, 고선택비)",
        "short": "STI / Ceria",
        "film": "oxide",
        "film_label": "STI 산화막 (질화막 스톱퍼 위)",
        "mechanism": "Si-O-Ce 화학결합(chemical tooth) — 실리카의 기계 마모와 다르다",
        "chem": "세리아(CeO₂) + 음이온 첨가제",
        "note": "같은 산화막이라도 실리카 팩과 메커니즘이 다르다. oxide:nitride 선택비가 목적.",
    },
    "cu_h2o2_bta": {
        "family": "Metal — Cu",
        "label": "구리 — 산화막 형성·제거 (H₂O₂ 산화제 + BTA 억제제)",
        "short": "Cu / H₂O₂+BTA",
        "film": "Cu",
        "film_label": "Cu 배선",
        "mechanism": "산화제가 표면을 산화시키고 연마가 걷어낸다. BTA가 오목부를 보호해 디싱을 막는다",
        "chem": "H₂O₂ 산화제, BTA 억제제, 실리카/알루미나",
        "note": "억제제 농도가 MRR과 디싱을 동시에 지배한다. 산화막 팩과 근본적으로 다른 계.",
    },
    "w_fe_oxidizer": {
        "family": "Metal — W",
        "label": "텅스텐 플러그 — 산화·용해 (Fe계 산화제 + 알루미나)",
        "short": "W / Fe-oxidizer",
        "film": "W",
        "film_label": "W 플러그 · 배리어",
        "mechanism": "Fe³⁺가 W를 산화·용해시키고 연마입자가 산화층을 제거 (Kaufman 모델)",
        "chem": "Fe(NO₃)₃ 계 산화제, 알루미나",
        "note": "리세스·코어링이 주 결함. 산화제 농도 의존성이 Cu보다 가파르다.",
    },
    "sic_alumina_kmno4": {
        "family": "Compound — SiC",
        "label": "SiC — 산성 강산화 연마 (과망간산칼륨 + 알루미나)",
        "short": "SiC / KMnO4+Al2O3",
        "film": "SiC",
        "film_label": "4H·6H-SiC 웨이퍼",
        "mechanism": "강산화제(KMnO₄)가 산성 조건에서 SiC를 빠르게 산화하고 경질 알루미나가 걷어낸다. 알칼리 세리아/H₂O₂ 계보다 MRR이 두 자리 높다",
        "chem": "과망간산칼륨(KMnO₄) 산화제, 알루미나, pH 2 부근",
        "note": "⚠ 같은 SiC라도 알칼리 세리아 계와 제거 속도가 100배 가까이 다르다. 산성·강산화 레시피에만 쓸 것.",
    },
    "sic_ceria_h2o2": {
        "family": "Compound — SiC",
        "label": "4H-SiC — 알칼리 산화 연마 (세리아 + H₂O₂)",
        "short": "SiC / Ceria+H₂O₂",
        "film": "SiC",
        "film_label": "4H-SiC 웨이퍼 (Si면)",
        "mechanism": "H₂O₂가 SiC를 산화해 연질 SiOx를 만들고 세리아가 제거. 경도가 높아 MRR이 Si 대비 2~3자리 낮다",
        "chem": "세리아 + H₂O₂, 알칼리 pH",
        "note": "⚠ Si 반도체용이 아니다. 화합물 반도체 전용 — Si 산화막/Cu/W에 쓰지 말 것.",
    },
}

# UI에서 보여줄 family 순서 (Si 주력 공정 먼저, 화합물 반도체 뒤)
FAMILY_ORDER: List[str] = ["Oxide (SiO₂)", "Metal — Cu", "Metal — W", "Compound — SiC"]

# 슬러리가 아닌 팩 — 선택 목록에서 제외한다.
# base 는 장비·패드·접촉역학 공통값이라 "슬러리 고르기"에 뜨면 안 된다.
NON_SLURRY = {"base"}


def pack_label(pack_id: str) -> str:
    """선택 목록에 보일 한 줄. 메타가 없으면 ID를 그대로 돌려준다."""
    m = PACK_META.get(pack_id)
    return m["label"] if m else pack_id


def pack_meta(pack_id: str) -> Dict[str, Any]:
    """팩 하나의 표시 메타. 미등록 팩도 최소 형태로 채워 UI가 깨지지 않게 한다."""
    m = PACK_META.get(pack_id)
    if m:
        return {"id": pack_id, **m}
    return {
        "id": pack_id,
        "family": "기타",
        "label": pack_id,
        "short": pack_id,
        "film": "",
        "film_label": "",
        "mechanism": "",
        "chem": "",
        "note": "표시 메타 미등록 — knowledge/params 에 팩이 추가되면 sim/pack_meta.py 에도 넣는다.",
    }


def grouped(pack_ids: List[str]) -> List[Dict[str, Any]]:
    """막질군 → 팩 목록으로 묶어 돌려준다. UI가 2단 선택을 만들 수 있게.

    `base` 는 장비·패드 공통값이지 슬러리가 아니므로 선택 목록에서 뺀다
    (실제로 '기타' 항목으로 떠서 슬러리처럼 보였다).
    """
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for pid in pack_ids:
        if pid in NON_SLURRY:
            continue
        meta = pack_meta(pid)
        buckets.setdefault(meta["family"], []).append(meta)
    out = []
    for fam in FAMILY_ORDER:
        if fam in buckets:
            out.append({"family": fam, "packs": buckets.pop(fam)})
    for fam in sorted(buckets):          # 미등록 family 는 뒤에 알파벳순
        out.append({"family": fam, "packs": buckets[fam]})
    return out
