"""시간축 시뮬레이션 (Polish Timeline) — 연마 중 두께 변화, 다층 스택 전이.

사용자 지시 (2026-09-08):
  "장비 연마중 데이터 표시 필요 - 실시간 두께 변화 데이터 시각화 (웨이퍼 옆면을
   보여줘서 웨이퍼 스택별로 연마가 어떻게 되는지 확인할 수 있도록) - 온도, 마찰
   (carrier current 등) 표시 필요"

무엇을 하나
──────────
엔진(engine.simulate)은 단발 계산이다: MRR(r) 하나 × 시간 = 제거량. 스택도 없고
시간 중간 상태도 없다. 이 모듈은 그 위에 **시간 스텝 루프**를 얹는다:
  1. 웨이퍼 스택(위→아래 층 목록)을 받는다.
  2. 매 스텝, 현재 노출된 층의 팩으로 simulate()를 호출해 MRR(r)을 얻는다.
  3. 반경별로 제거량을 누적한다. 어떤 반경에서 현재 층이 다 깎이면 그 반경은
     다음 층으로 넘어간다 — **반경마다 층 전이 시점이 다르다**(WIWNU가 있으므로).
  4. 스텝마다 장비 출력값(온도·μ·토크)을 기록해 시계열로 돌려준다.

정직한 한계 (notes에 실린다)
──────────────────────────
- 층 전이 시 MRR은 즉시 바뀐다고 본다. 실제로는 혼합 접촉 구간(두 층이 동시 노출)에서
  중간값이 되고, 정지층(SiN)에서는 선택비로 느려진다. 선택비는 팩의
  oxide_nitride_selectivity 같은 값을 쓰되, 그 값이 없으면 전이 후 층의 팩이 없다고
  보고 **그 반경의 연마를 멈춘다**(모르는 층을 지어내 깎지 않는다).
- 패드 온도는 정상상태 상한(equipment_outputs)이지 과도응답이 아니다. 연마 초기
  온도 상승 곡선은 미모델링이며 시계열은 조건이 바뀔 때만 변한다.
- 시간 스텝 안에서 조건은 고정이다. 멀티스텝 레시피(압력 변경)는 steps로 준다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from sim.engine import Recipe, simulate
from sim.params import load_pack


@dataclass
class Layer:
    name: str                      # "TEOS", "SiN", "Cu" ...
    thickness_nm: float
    pack: Optional[str]            # 이 층을 깎을 때 쓰는 팩. None = 모델 없음
    stop: bool = False             # 정지층 — 여기서 멈춘다 (기판 등)
    color: str = "#7fb3ff"         # UI 단면도 색


@dataclass
class TimelineFrame:
    t_s: float
    exposed_layer: List[int]       # 반경 격자별 현재 노출 층 인덱스
    remaining_nm: List[List[float]]   # [층][반경] 남은 두께
    mrr_nm_min: List[float]        # 반경별 현재 MRR
    mean_mrr: float
    outputs: Dict[str, Optional[float]]   # 온도·μ·토크·전류
    notes: List[str] = field(default_factory=list)


@dataclass
class TimelineResult:
    radius_mm: List[float]
    layers: List[Dict[str, Any]]
    frames: List[TimelineFrame]
    endpoint_s: Optional[float]    # 첫 층이 전 반경에서 다 깎인 시각 (없으면 None)
    layer_breakthrough_s: Dict[str, Optional[float]]   # 층별 최초 돌파 시각(가장 빠른 반경)
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "radius_mm": self.radius_mm, "layers": self.layers,
            "endpoint_s": self.endpoint_s,
            "layer_breakthrough_s": self.layer_breakthrough_s,
            "notes": self.notes,
            "frames": [{
                "t_s": f.t_s, "exposed_layer": f.exposed_layer,
                "remaining_nm": f.remaining_nm, "mrr_nm_min": f.mrr_nm_min,
                "mean_mrr": f.mean_mrr, "outputs": f.outputs, "notes": f.notes,
            } for f in self.frames],
        }


def _outputs_of(res) -> Dict[str, Optional[float]]:
    eq = res.equipment_outputs or {}
    def g(k):
        o = eq.get(k)
        return None if (o is None or o.value is None) else float(o.value)
    return {"pad_temp_c": g("pad_temp_c"), "cof": g("cof"),
            "platen_torque_nm": g("platen_torque_nm"),
            "carrier_current_a": g("carrier_current_a"),
            "friction_power_w": g("friction_power_w")}


def run_timeline(layers: List[Layer], recipe_base: Recipe,
                 total_s: float, dt_s: float = 2.0,
                 selectivity_key: str = "oxide_nitride_selectivity",
                 max_frames: int = 400) -> TimelineResult:
    """스택을 시간축으로 연마한다.

    recipe_base: 압력·rpm 등 공정 조건. pack은 층마다 바뀌므로 여기 값은 무시된다.
    """
    notes: List[str] = []
    if not layers:
        raise ValueError("스택이 비어 있다")
    dt_s = max(float(dt_s), 0.1)
    n_steps = int(np.ceil(total_s / dt_s))
    if n_steps > max_frames:
        dt_s = total_s / max_frames
        n_steps = max_frames
        notes.append(f"스텝을 {max_frames}개로 제한 — dt={dt_s:.2f}s")

    # 층별 MRR(r) 캐시 — 같은 층은 조건이 같으면 MRR이 같다 (시간 무관)
    mrr_cache: Dict[int, Optional[np.ndarray]] = {}
    res_cache: Dict[int, Any] = {}
    radius = None

    def mrr_for(li: int):
        if li in mrr_cache:
            return mrr_cache[li]
        L = layers[li]
        if L.pack is None or L.stop:
            mrr_cache[li] = None
            return None
        rec = Recipe(**{**recipe_base.__dict__, "pack": L.pack})
        try:
            res = simulate(rec)
        except Exception as e:
            notes.append(f"⚠ 층 '{L.name}' 팩 '{L.pack}' 시뮬 실패: {type(e).__name__}: {e} — "
                         "이 층은 깎이지 않는다.")
            mrr_cache[li] = None
            return None
        res_cache[li] = res
        mrr_cache[li] = res.mrr_nm_per_min.copy()
        return mrr_cache[li]

    # 첫 층으로 반경 격자 확정
    first = mrr_for(0)
    if first is None:
        raise ValueError(f"첫 층 '{layers[0].name}'에 연마 모델이 없다 (pack={layers[0].pack})")
    radius = res_cache[0].radius_m
    n_r = len(radius)

    # 선택비: 층 i → i+1 전이 시, 다음 층 팩이 없으면 이전 층 팩의 selectivity로 느려진 값
    def transitional_mrr(li_prev: int, li_next: int) -> Optional[np.ndarray]:
        m = mrr_for(li_next)
        if m is not None:
            return m
        # 다음 층에 모델이 없다. 이전 층 팩에 선택비가 있으면 그걸로 근사.
        prev = layers[li_prev]
        if prev.pack:
            try:
                pk = load_pack(prev.pack)
                if pk.has(selectivity_key):
                    sel = float(pk.get(selectivity_key))
                    if sel > 0:
                        base = mrr_for(li_prev)
                        if base is not None:
                            notes.append(
                                f"층 '{layers[li_next].name}'에 팩이 없어 이전 층 팩의 "
                                f"{selectivity_key}={sel:g}로 MRR/{sel:g} 근사 — "
                                "⚠ 정지층 연마 모델이 아니라 선택비 나눗셈이다.")
                            m2 = base / sel
                            mrr_cache[li_next] = m2
                            return m2
            except Exception:
                pass
        return None

    remaining = np.array([[L.thickness_nm] * n_r for L in layers], dtype=float)
    exposed = np.zeros(n_r, dtype=int)
    frames: List[TimelineFrame] = []
    breakthrough: Dict[str, Optional[float]] = {L.name: None for L in layers}
    endpoint = None

    def snapshot(t):
        cur_mrr = np.zeros(n_r)
        for i in range(n_r):
            li = int(exposed[i])
            m = mrr_cache.get(li)
            cur_mrr[i] = 0.0 if m is None else float(m[i])
        # 출력값은 '가장 많이 노출된 층'의 결과에서 가져온다. 그 층에 시뮬 결과가
        # 없으면(선택비 근사 층) 직전에 결과가 있던 층의 값을 쓴다 — 장비 조건은
        # 같으므로 온도·μ는 그대로다. None으로 비우면 "층 바뀌자 온도 사라짐"이 된다.
        dom = int(np.bincount(exposed).argmax())
        src = dom
        while src >= 0 and src not in res_cache:
            src -= 1
        outs = _outputs_of(res_cache[src]) if src >= 0 else \
            {"pad_temp_c": None, "cof": None, "platen_torque_nm": None,
             "carrier_current_a": None, "friction_power_w": None}
        frames.append(TimelineFrame(
            t_s=round(t, 3), exposed_layer=exposed.tolist(),
            remaining_nm=[np.maximum(remaining[k], 0).round(2).tolist()
                          for k in range(len(layers))],
            mrr_nm_min=cur_mrr.round(3).tolist(),
            mean_mrr=float(cur_mrr.mean()), outputs=outs))

    snapshot(0.0)
    t = 0.0
    for _ in range(n_steps):
        t += dt_s
        for i in range(n_r):
            li = int(exposed[i])
            if layers[li].stop:
                continue
            m = mrr_cache.get(li)
            if m is None:
                m = mrr_for(li)
            if m is None:
                continue
            budget = float(m[i]) * dt_s / 60.0     # 이 스텝에 깎을 수 있는 nm
            while budget > 1e-9 and li < len(layers) and not layers[li].stop:
                take = min(budget, remaining[li, i])
                remaining[li, i] -= take
                budget -= take
                if remaining[li, i] <= 1e-9:
                    # 이 반경에서 층 li 돌파
                    if breakthrough[layers[li].name] is None:
                        breakthrough[layers[li].name] = round(t, 3)
                    if li + 1 >= len(layers):
                        break
                    # 정지층은 선택비 근사를 시도하지 않는다 — 시도하면 "기판에
                    # selectivity 근사" 같은 거짓 노트가 남는다 (NPW 담당이 발견).
                    if layers[li + 1].stop:
                        li += 1
                        exposed[i] = li
                        break
                    nm = transitional_mrr(li, li + 1)
                    li += 1
                    exposed[i] = li
                    if nm is None:
                        break
                    # 남은 budget은 다음 층 MRR 비율로 환산
                    ratio = float(nm[i]) / max(float(m[i]), 1e-12)
                    budget *= ratio
                    m = nm
        if endpoint is None and np.all(exposed >= 1):
            endpoint = round(t, 3)
        snapshot(t)

    if endpoint is None:
        notes.append(f"{total_s:g}s 안에 첫 층이 전 반경에서 다 깎이지 않았다 — "
                     "endpoint 없음. 시간을 늘리거나 조건을 올려라.")
    else:
        fastest = min(v for v in breakthrough.values() if v is not None)
        notes.append(f"첫 층 돌파: 가장 빠른 반경 {fastest:g}s, 전 반경 {endpoint:g}s "
                     f"(차이 {endpoint - fastest:g}s = 오버폴리시 필요량의 근거).")
    notes.append("⚠ 층 전이는 즉시 전환 근사 — 혼합 접촉 구간·정지층 물리는 미모델링.")
    notes.append("⚠ 온도·μ는 정상상태 값 — 연마 초기 과도응답은 미모델링.")

    return TimelineResult(
        radius_mm=(radius * 1000).round(2).tolist(),
        layers=[{"name": L.name, "thickness_nm": L.thickness_nm, "pack": L.pack,
                 "stop": L.stop, "color": L.color} for L in layers],
        frames=frames, endpoint_s=endpoint,
        layer_breakthrough_s=breakthrough, notes=notes)
