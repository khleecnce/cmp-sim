"""파라미터 팩 로더 — 물리 상수를 코드에서 데이터로 분리한다.

왜 이 파일이 있나 (2026-09-06 사용자 지시):
  "시뮬레이션툴이야 껍데기고 그 안에는 학습내용이 잘 머지되어서 있어야되는거 아니야?
   그 내용만 바꾸면 각각 다른 시뮬레이션을 할수있도록 설계해"

  그 전까지 knowledge/*.md 36편은 코드에서 **주석**이었다. 실제로 파일을 읽는 코드가
  한 줄도 없었고, 물리 상수는 24개 모듈에 하드코딩돼 있었다(_E_STAR=1e9, sigma0=8.112e-6,
  T_HALF_HOURS=48.0 ...). 그래서 "Cu 슬러리로 바꿔서 돌려봐"가 코드 수정 없이는 불가능했다.

  이 파일이 그 축을 뒤집는다. 물리 상수는 knowledge/params/*.yaml 이 소유하고,
  엔진은 팩 이름만 받아 읽는다. **팩을 바꾸면 다른 시뮬레이션이 된다.**

설계 원칙
  1. **없는 값은 없다고 말한다.** get()은 기본값을 지어내지 않고 KeyError를 던진다.
     조용한 기본값은 곧 할루시네이션이다 — 사용자가 Cu 팩을 돌렸는데 산화막 Kp가
     조용히 쓰이면 그 결과는 거짓말이다.
  2. **모든 값은 출처를 달고 다닌다.** value뿐 아니라 source(지식노트)·confidence를
     함께 싣는다. WaferResult.provenance로 흘러나가 "이 숫자가 어디서 왔나"에 답한다.
  3. **팩은 상속된다.** base 필드로 공통 팩(장비·패드)을 깔고 막질별로 덮어쓴다.
     같은 툴에서 막만 바꾸는 게 실제 실험 방식이라서.
  4. 팩은 knowledge/params/ 에 산다 — 지식베이스의 일부지 코드가 아니다.
     학습 에이전트가 노트를 쓰면서 같은 자리에 수치를 갱신할 수 있어야 한다.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

_ENV_DIR = os.environ.get("FABSIM_PACK_DIR")


def _resolve_pack_dir() -> Path:
    """팩 위치 해석. 개발(저장소)과 배포(설치본) 양쪽에서 동작해야 한다.

    우선순위:
      1. FABSIM_PACK_DIR 환경변수 — 고객이 자기 팩 디렉토리를 지정하는 통로
      2. knowledge/params/  — 저장소 레이아웃(개발). 에이전트가 노트와 함께 갱신한다.
      3. sim/params/        — 설치 패키지에 동봉된 사본(배포). 연구 노트는 빠지고
                              런타임에 필요한 이 값들만 따라간다.
    """
    if _ENV_DIR:
        return Path(_ENV_DIR).expanduser()
    here = Path(__file__).resolve().parent
    repo = here.parent / "knowledge" / "params"
    if repo.is_dir():
        return repo
    return here / "params"


_PACK_DIR = _resolve_pack_dir()


class ParamMissing(KeyError):
    """팩에 없는 파라미터를 요구했다. 기본값으로 때우지 않고 여기서 멈춘다."""


@dataclass
class Param:
    """값 하나 + 그 값이 어디서 왔는지."""
    key: str
    value: Any
    unit: str = ""
    source: str = ""          # knowledge/ 노트 경로 또는 문헌
    confidence: str = "unknown"   # verified | literature | estimated | unverified
    note: str = ""
    owner: str = ""           # 이 값을 선언한 팩 이름 (상속된 값과 자기 값을 구분)

    def __repr__(self) -> str:  # 디버깅 시 출처가 같이 보이게
        return f"Param({self.key}={self.value}{' ' + self.unit if self.unit else ''}, {self.confidence})"


@dataclass
class ParamPack:
    """한 시뮬레이션 조건을 정의하는 물리 상수 묶음."""
    name: str
    description: str = ""
    params: Dict[str, Param] = field(default_factory=dict)
    lineage: List[str] = field(default_factory=list)   # 상속 체인 (base → ... → self)

    # ── 읽기 ────────────────────────────────────────────────
    def get(self, key: str) -> Any:
        """값을 꺼낸다. 없으면 KeyError — 지어내지 않는다."""
        if key not in self.params:
            raise ParamMissing(
                f"팩 '{self.name}'에 '{key}'가 없다. "
                f"보유: {sorted(self.params)}. "
                f"knowledge/params/{self.name}.yaml 에 출처와 함께 추가하라."
            )
        return self.params[key].value

    def get_or(self, key: str, default: Any) -> Any:
        """기본값 허용 — 물리 상수가 **아닌** 편의 값에만 써라."""
        return self.params[key].value if key in self.params else default

    def has(self, key: str) -> bool:
        return key in self.params

    def has_own(self, key: str) -> bool:
        """이 팩이 **직접 선언한** 값인가 (상속된 값이면 False).

        왜 필요한가: 상속은 "같은 물리를 공유한다"는 뜻이다. 그런데 막질·연마입자를
        바꾼 팩은 물리 자체가 달라지므로, 부모의 재료 상수를 조용히 물려받으면
        "남의 재료로 계산한 숫자"가 이 팩의 결과로 나온다. 재료 고유 상수를 쓰는
        항은 그 값이 자기 선언인지 확인한 뒤에만 활성화해야 한다.
        """
        p = self.params.get(key)
        return p is not None and p.owner == self.name

    def param(self, key: str) -> Param:
        if key not in self.params:
            raise ParamMissing(f"팩 '{self.name}'에 '{key}' 없음")
        return self.params[key]

    def provenance(self, keys: Optional[List[str]] = None) -> Dict[str, Dict[str, str]]:
        """쓰인 값들의 출처 표. WaferResult에 실려 나간다."""
        ks = keys if keys is not None else sorted(self.params)
        out = {}
        for k in ks:
            if k in self.params:
                p = self.params[k]
                out[k] = {"value": p.value, "unit": p.unit,
                          "source": p.source, "confidence": p.confidence}
        return out

    def unverified(self) -> List[str]:
        """검증 안 된 값 목록 — 결과에 경고로 딸려 나가야 한다."""
        return sorted(k for k, p in self.params.items()
                      if p.confidence in ("estimated", "unverified", "unknown"))


# ── 로딩 ────────────────────────────────────────────────────
def _coerce_number(v: Any) -> Any:
    """YAML 1.1의 함정: '1.0e11'은 float이 아니라 **문자열**로 파싱된다.

    지수 표기에 부호가 없으면(1.0e11, 5e-6이 아니라 1.0e11) YAML 1.1 정규식이
    숫자로 인정하지 않는다. 그대로 두면 eta='1.0e11'이 numpy 곱셈에 들어가
    `can't multiply sequence by non-int` 같은 엉뚱한 자리에서 터진다.
    실제로 이 프로젝트에서 그렇게 터졌다 — 그래서 로더가 여기서 정규화한다.
    """
    if isinstance(v, str):
        s = v.strip()
        try:
            return int(s) if s.lstrip("+-").isdigit() else float(s)
        except ValueError:
            return v          # 진짜 문자열(막질명·슬러리명 등)
    return v


def _parse_params(raw: Optional[Dict[str, Any]]) -> Dict[str, Param]:
    out: Dict[str, Param] = {}
    for key, v in (raw or {}).items():
        if isinstance(v, dict) and "value" in v:
            out[key] = Param(key=key, value=_coerce_number(v["value"]), unit=v.get("unit", ""),
                             source=v.get("source", ""), note=v.get("note", ""),
                             confidence=v.get("confidence", "unknown"))
        else:
            # 축약형: key: 3.0  — 출처 없음이 명시적으로 드러나도록 unverified
            out[key] = Param(key=key, value=_coerce_number(v), confidence="unverified",
                             note="축약형 정의 — 출처 없음")
    return out


def load_pack(name: str, _seen: Optional[List[str]] = None) -> ParamPack:
    """knowledge/params/<name>.yaml 을 읽는다. base가 있으면 재귀 병합."""
    _seen = list(_seen or [])
    if name in _seen:
        raise ValueError(f"팩 상속 순환: {' → '.join(_seen + [name])}")
    path = _PACK_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"파라미터 팩 '{name}' 없음: {path}\n사용 가능: {available_packs()}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    params: Dict[str, Param] = {}
    lineage: List[str] = []
    base = raw.get("base")
    if base:
        parent = load_pack(base, _seen + [name])
        params.update(parent.params)      # 부모를 깔고
        lineage = parent.lineage
    params.update(_parse_params(raw.get("params")))   # 자식이 덮어쓴다
    # 이 팩이 직접 선언한 값에 소유자를 새긴다 — 상속된 값과 구분하기 위함.
    # (부모에서 온 Param 은 부모 이름을 그대로 달고 있다)
    for key in _parse_params(raw.get("params")):
        params[key].owner = name
    return ParamPack(name=name, description=raw.get("description", ""),
                     params=params, lineage=lineage + [name])


def available_packs() -> List[str]:
    if not _PACK_DIR.exists():
        return []
    return sorted(p.stem for p in _PACK_DIR.glob("*.yaml"))


if __name__ == "__main__":
    for n in available_packs():
        p = load_pack(n)
        print(f"{n:20s} 상속={' → '.join(p.lineage):35s} 값 {len(p.params):2d}개  "
              f"미검증 {len(p.unverified())}개")
