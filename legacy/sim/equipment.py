"""장비팩 로더 — 컨디셔너 디스크 등 '장비' 축을 화학 팩과 분리해 로드한다.

왜 분리했나 (백로그 ㉺, validation/S12-RESIDUAL-JUDGMENT.md §2-2):
  컨디셔너 디스크 사양(그릿 크기·밀도·배열·돌출)은 화학 팩(knowledge/params/*.yaml)이
  선언할 값이 아니다. knowledge/params/base.yaml의 pad_asperity_radius_m note가 이미
  "R은 소재 물성이 아니라 **컨디셔닝(디스크 grit·하중)이 만드는 기하량**"이라고
  명시했다. 화학 팩에 디스크 필드를 넣으면 "Cu 화학을 바꿨는데 디스크 사양이 같이
  바뀌는" 잘못된 결합이 생긴다 — 그래서 장비 축을 별도 팩·별도 로더로 둔다.

Param/ParamPack, _parse_params는 sim.params 것을 그대로 쓴다 — 복제하지 않는다.
없는 값은 여기서도 지어내지 않는다: ParamPack.get()의 KeyError(ParamMissing) 그대로.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

import yaml

from sim.params import Param, ParamPack, ParamMissing, _parse_params  # noqa: F401 (재사용)

_ENV_DIR = os.environ.get("FABSIM_EQUIPMENT_DIR")


def _resolve_equipment_dir() -> Path:
    """장비팩 위치 해석. sim/params.py::_resolve_pack_dir()와 같은 3단 우선순위.

    1. FABSIM_EQUIPMENT_DIR 환경변수 — 고객이 자기 장비팩 디렉토리를 지정하는 통로
    2. knowledge/equipment/packs/  — 저장소 레이아웃(개발)
    3. sim/equipment_packs/        — 배포 사본. 디렉토리가 없으면 없는 것으로 처리한다.
    """
    if _ENV_DIR:
        return Path(_ENV_DIR).expanduser()
    here = Path(__file__).resolve().parent
    repo = here.parent / "knowledge" / "equipment" / "packs"
    if repo.is_dir():
        return repo
    return here / "equipment_packs"


_EQUIPMENT_DIR = _resolve_equipment_dir()


def load_equipment_pack(name: str) -> ParamPack:
    """knowledge/equipment/packs/<name>.yaml 을 읽는다.

    화학 팩(sim.params.load_pack)과 달리 base: 상속은 쓰지 않는다 — 지금 있는
    디스크 팩들은 캐리어 직경별 별개 제품값(3M E187 260mm/360mm)이라 공유할
    부모가 없다. 값 조회는 ParamPack.get()의 KeyError(ParamMissing) 그대로 —
    없는 값을 지어내지 않는다.
    """
    path = _EQUIPMENT_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"장비팩 '{name}' 없음: {path}\n사용 가능: {available_equipment_packs()}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    params = _parse_params(raw.get("params"))
    for p in params.values():
        p.owner = name
    return ParamPack(name=name, description=raw.get("description", ""),
                     params=params, lineage=[name])


def available_equipment_packs() -> List[str]:
    if not _EQUIPMENT_DIR.exists():
        return []
    return sorted(p.stem for p in _EQUIPMENT_DIR.glob("*.yaml"))


if __name__ == "__main__":
    for n in available_equipment_packs():
        p = load_equipment_pack(n)
        print(f"{n:20s} 값 {len(p.params):2d}개")
