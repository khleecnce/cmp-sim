"""병합 파라미터 (Merged Factors) — ARCHITECTURE-V2.md §2의 구현.

왜 이게 필요한가
────────────────
입력 필드가 468개다. "무엇이 결과를 어떻게 바꾸는지" 파악이 불가능하다.
연관 인자를 물리적으로 묶어 **10개 파라미터**로 만들고, 각 파라미터가
①결과를 어떻게 바꾸는가 ②그걸 바꾸려면 무엇을 만져야 하는가를 동시에 답하게 한다.

분리 규칙 (사용자 확정, 2026-09-08)
────────────────────────────────
- **장비축(Λ Π Θ Γ)과 소모품축(κ χ ψ τ Δ S)을 섞지 않는다.** 장비는 부하를 가하고,
  소모품은 그 부하에 반응한다. 섞으면 "슬러리를 바꿔야 하나 RPM을 올려야 하나"에
  답할 수 없다 — 그 비교가 이 도구의 존재 이유다.
- **웨이퍼는 팩터가 아니다.** 대상막질이자 기준선이지 조절 손잡이가 아니다.

설계 계약 (어기면 V1의 실패가 반복된다)
──────────────────────────────────
1. **모든 팩터는 기준 조건에서 정확히 1.0.** 절대값을 쓰면 Kp에 이미 반영된 효과를
   두 번 센다 — 2026-09-06 Cu MRR 20배 붕괴가 그 사고였다.
2. **파라미터가 없으면 조용히 1.0을 쓰지 않고 `status='unmodeled'`로 신고한다.**
   조용한 1.0은 "화학을 반영했다"는 거짓말이 된다.
3. **각 팩터는 자기 drivers(어느 입력에서 왔나)를 신고한다.** 이게 있어야
   "κ를 올리려면 무엇을 만지나"에 기계가 답한다.
4. 팩터를 붙였으면 스캔해 응답 곡선을 눈으로 확인한다. 단위테스트 통과는 증거가 아니다
   (Langmuir θ가 1mM에서 0.97로 포화해 2mM/5mM이 구분 안 됐던 전례).
"""
from __future__ import annotations

import inspect
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # 순환 import 방지 — engine이 factors를 쓴다
    from sim.engine import ResolvedRecipe

# ─────────────────────────────────────────────────────────── 축 정의
AXIS_EQUIPMENT = "equipment"
AXIS_CONSUMABLE = "consumable"

#: 팩터 → (기호, 이름, 축, 어느 파트가 driver인가)
#: `parts`는 UI에서 "이걸 바꾸려면 어느 탭을 열어야 하나"로 쓰인다.
FACTOR_SPEC = {
    # ── 장비축 — 소모품과 묶지 않는다
    "lambda": ("Λ", "기계 부하 강도", AXIS_EQUIPMENT, ["tool"]),
    "pi":     ("Π", "반경 하중 분포", AXIS_EQUIPMENT, ["tool"]),
    "theta":  ("Θ", "열·유동 부하",   AXIS_EQUIPMENT, ["tool"]),
    "gamma":  ("Γ", "컨디셔닝 부하",  AXIS_EQUIPMENT, ["tool"]),
    # ── 소모품축 — 슬러리·패드·디스크가 함께 결정
    "kappa":  ("κ", "접촉 강도",     AXIS_CONSUMABLE, ["slurry", "pad", "disk"]),
    "chi":    ("χ", "화학 반응성",   AXIS_CONSUMABLE, ["slurry"]),
    "psi":    ("ψ", "표면 보호도",   AXIS_CONSUMABLE, ["slurry"]),
    "tau":    ("τ", "슬러리 전달",   AXIS_CONSUMABLE, ["slurry", "pad", "disk"]),
    "delta":  ("Δ", "손상 유발도",   AXIS_CONSUMABLE, ["slurry", "pad", "disk"]),
    "stab":   ("S", "시간 안정성",   AXIS_CONSUMABLE, ["slurry", "pad", "disk"]),
}

#: 팩터가 MRR에 곱해지는가, 아니면 진단 전용인가.
#: ⚠ 여기에 넣는 순간 이중 계상 위험이 생긴다 — 기준 1.0 계약을 반드시 확인할 것.
#: τ는 결합이 매우 약하다(지수 0.07) — 그래도 넣는 이유는 사용자가 그루브를
#: 바꿨을 때 "아무 반응 없음"과 "약하게 반응함"을 구분해야 하기 때문이다.
#: 실측이 말하는 것은 '효과 없음'이 아니라 '효과가 작음'이다.
MRR_COUPLED = {"chi", "psi", "kappa", "tau"}

# ══════════════════════════════════════════════════════════════════════
# 드라이버의 **극한 의미** 선언 — 검사기가 변수 뜻을 추측하지 않게 한다.
#
# 왜 여기(모델)에 두는가:
#   "이 변수가 0 이면 제거가 멈추는가?"는 검사 도구가 판단할 문제가 아니라
#   모델이 주장하는 물리다. 검사기에 물질별 예외표를 두면 그건 절차가 아니라
#   사례 모음이 된다. 모델이 선언하고 검사기는 그 선언과 실제 거동을 대조만 한다.
#
#   AGENT      — 이것이 없으면 메커니즘 자체가 성립하지 않는다 → 팩터는 0 이어야 한다.
#                (제거를 수행하는 주체. 예: 제거를 일으키는 매개가 사라진 경우)
#   MODULATOR  — 0 이어도 메커니즘은 남는다 → 팩터는 유한한 양수여야 한다.
#                (이미 있는 경로의 세기를 조절할 뿐인 인자)
#   INTENSIVE  — **0 이 '없음'을 뜻하지 않는 변수** → 0 극한 검사를 적용하지 않는다.
#                세기 변수(강도·상태를 나타내는 척도)가 여기 속한다. 이런 변수는
#                양이 아니라 상태를 가리키므로 "0 = 부재"라는 전제가 성립하지 않고,
#                0 은 정의역의 한쪽 끝(극단적인 상태)일 뿐이다. 대신 이들에게는
#                **정의역과 유효 구간**을 확인해야 하며, 구간 밖에서 항이 조용히
#                외삽되지 않는지가 검사 대상이다(0 에서의 값이 아니라).
#
#                ⚠ 세기 변수를 편의상 MODULATOR 로 선언하면 안 된다. 그러면 검사기가
#                  "0 에서 양수면 통과"라고 판정하는데, 그 통과는 아무 물리도 보증하지
#                  않는다 — 애초에 0 이 물어볼 만한 조건이 아니기 때문이다.
#                  잘못된 안심은 침묵보다 나쁘다.
#
#   미선언은 통과가 아니라 **결함**이다. 새 드라이버를 붙이면서 극한에서 무슨 일이
#   일어나는지 말하지 않았다는 뜻이고, 그 상태로는 극한 검사가 침묵한다.
#
# 판정 방법(물질명 없이):
#   ① 이 변수의 0 이 "그것이 없는 상태"를 뜻하는가?
#      아니면 → INTENSIVE (0 극한 대신 유효 구간을 검사)
#   ② 0 으로 두었을 때, 남은 입력만으로 표면에서 재료가 떨어져 나갈 경로가
#      하나라도 있는가? 있으면 MODULATOR, 없으면 AGENT.
LIMIT_ROLE: Dict[str, str] = {
    # ── AGENT: 없으면 메커니즘 소멸 ────────────────────────────────
    "abrasive_wt_pct": "AGENT",          # 하중을 전달할 매개가 없다
    "abrasive_size_nm": "AGENT",         # 크기 0 = 입자 부재와 같다
    "asperity_density_per_m2": "AGENT",  # 접촉점이 없으면 하중 전달 경로가 없다
    "pressure_psi": "AGENT",             # 하중 없이 마모 없다
    "relative_velocity_m_s": "AGENT",    # 상대 운동 없이 마모 없다

    # ── MODULATOR: 0 이어도 다른 경로가 남는다 ─────────────────────
    "groove_width_um": "MODULATOR",
    "groove_depth_mm": "MODULATOR",
    "groove_pitch_mm": "MODULATOR",
    "pad_porosity_pct": "MODULATOR",     # 그루브·간극이 이송을 대신한다
    "slurry_viscosity_pa_s": "MODULATOR",
    "inhibitor_mM": "MODULATOR",         # 억제가 없으면 오히려 제거가 는다
    # chelator_M=0(착화제 없음)은 ①"없는 상태"가 명확하고, ②그 상태에서도
    # χ(반응성)·ψ 억제제(inhibitor_mM) 경로가 남아 재료가 떨어져 나간다 —
    # inhibitor_mM과 같은 구조(보호제 부재=억제 해제=제거 증가, 소멸 아님).
    # 판정#95(EVIDENCE-RULES): chelator_M=0에서 ψ가 1을 넘는 것도 이 방향과
    # 정합 — "메커니즘 소멸"이 아니라 "보호 해제로 인한 상대적 증가"다.
    "chelator_M": "MODULATOR",
    # promoter_M=0(촉진 착화제 없음)도 ①없는 상태가 명확하고, ②
    # _carboxylate_promoter_term의 phi(기계 바닥)가 C=0에서도 유한 양수로
    # 남아 순수 기계적 연마 경로가 죽지 않는다(chemistry.py 주석: "phi가
    # 하는 일: 착화제가 0이어도 제거가 0이 되지 않는다").
    "promoter_M": "MODULATOR",
    "oxidizer_wt_pct": "MODULATOR",      # C=0 에서도 기계적 바닥값이 남는 계가 있다
    "ce3_fraction": "MODULATOR",         # 활성점 0 이어도 입자는 단단한 산화물이다
    "dispersant_type": "MODULATOR",
    "shield_additive_wt_pct": "MODULATOR",  # 첨가제 0 = 억제 없음(배수 1.0), 제거는 남는다
    "time_s": "MODULATOR",

    # ── INTENSIVE: 0 이 '없음'이 아닌 세기 변수 ─────────────────────
    # 이들에게 "0 에서 어떻게 되는가"는 물어볼 수 없는 질문이다. pH 0 은 산이
    # 사라진 상태가 아니라 극단적으로 강한 산성 상태이고, 경도 0 은 재료가
    # 없는 게 아니라 흐르는 상태다. 따라서 0 극한 대신 **유효 구간**을 본다.
    #
    # ⚠ 특히 pH 는 산성/염기성에서 표면 전하 부호가 뒤집히므로 **단일 곡선으로
    #   전 구간을 덮을 수 없다.** 같은 값이라도 어느 쪽 영역인지에 따라 다른
    #   메커니즘이 지배하고, 한쪽에서 유도한 곡선을 반대쪽에 쓰면 순위까지
    #   틀린다. 항을 고를 때 재료 쌍의 등전점 관계로 분기해야 하며, 유도 구간
    #   밖으로 외삽하지 않는 것이 이 변수의 검사 항목이다.
    "slurry_ph": "INTENSIVE",
    "pad_hardness_shore_d": "INTENSIVE",
    "temperature_c": "INTENSIVE",
}

# ══════════════════════════════════════════════════════════════════════
# 범주형 드라이버의 "없음"에 해당하는 값 (2026-09-20, EVIDENCE-RULES 판정#95)
#
# 왜 필요한가: LIMIT_ROLE 은 "0 에서 무엇을 기대하는가"를 말하지만, 범주형
# 드라이버(문자열 값)에는 애초에 "0"이 없다. 검사기가 "그럼 어느 값이
# 없음인가"를 추측하면 그건 절차가 아니라 검사기가 물리를 대신 판단하는
# 것이다. 그래서 모델이 직접 선언한다 — chemistry._dispersant_protection_term
# 이 이미 "dispersant_ref_type 이 없으면 'NONE'(분산제 없음)을 기준으로
# 삼는다"고 코드 docstring에 명시하고 있으므로, 그 관례를 여기 옮겨 적을
# 뿐이지 새로 지어내는 것이 아니다.
#
# 여기 없는 범주형 드라이버는 검사기가 극한 검사를 수행할 수 없다는 뜻이고,
# 그 상태는 결함으로 보고돼야 한다(경고로 조용히 넘기지 않는다).
CATEGORICAL_ABSENT: Dict[str, str] = {
    "dispersant_type": "NONE",
}


@dataclass
class Factor:
    """병합 파라미터 하나. 값 + 근거 + 무엇을 만지면 바뀌는가."""
    key: str
    symbol: str
    name: str
    axis: str
    parts: List[str]
    value: Optional[float] = None          # 기준 조건 대비 배수 (기준=1.0)
    status: str = "unmodeled"              # modeled | partial | unmodeled
    drivers: Dict[str, float] = field(default_factory=dict)   # 입력 필드 → 현재값
    terms: Dict[str, float] = field(default_factory=dict)     # 항별 기여
    confidence: str = "unverified"         # verified | literature | estimated | unverified
    sources: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    # 입력 키 → 그 입력의 항이 **의도적으로 꺼진** 이유 (2026-09-20 신설).
    #
    # 왜 필요한가: 이 파일의 여러 항은 "이 레짐은 관측이 없다"며 스스로 None 을
    # 돌려주고 notes 에 이유를 적는다(예: _ph_cu_acidic_term 의 알칼리×억제제
    # 레짐). 그 구간에서 MRR 이 평평한 것은 **"변하지 않는다는 예측"이 아니라
    # "예측하지 않는다는 선언"**이다. 그런데 하류 도구(tools/response_map.py)는
    # 숫자만 보므로 이 둘을 구분하지 못하고, 평평한 구간과 살아 있는 구간이
    # 이어져 만든 인공 골짜기를 문헌 정점과 대조해 CONFLICT 로 신고했다
    # (2026-09-20 cu_h2o2_bta/pH, score 120 최우선 갭). 모델이 침묵한 구간을
    # 근거로 "모델이 틀린 방향을 가리킨다"고 채점하면 없는 결함을 고치게 된다.
    #
    # notes 문자열을 정규식으로 긁지 않고 구조화해 두는 이유도 같다 — 문구가
    # 바뀌면 조용히 탐지가 꺼진다.
    gated: Dict[str, str] = field(default_factory=dict)

    @property
    def mrr_coupled(self) -> bool:
        return self.key in MRR_COUPLED

    def describe(self) -> str:
        if self.status == "unmodeled":
            return (f"{self.symbol} {self.name}: 미모델링 — "
                    f"필요 파라미터가 팩에 없다. '영향 없음'이 아니다.")
        parts = ", ".join(f"{k}×{v:.3f}" for k, v in self.terms.items())
        tail = f" = {parts}" if parts else ""
        return f"{self.symbol} {self.name}: {self.value:.3f}{tail} [{self.confidence}]"

    def to_dict(self) -> Dict:
        return {
            "key": self.key, "symbol": self.symbol, "name": self.name,
            "axis": self.axis, "parts": self.parts,
            "value": self.value, "status": self.status,
            "drivers": self.drivers, "terms": self.terms,
            "confidence": self.confidence, "sources": self.sources,
            "notes": self.notes, "mrr_coupled": self.mrr_coupled,
            "gated": self.gated,
        }


def _new(key: str) -> Factor:
    sym, name, axis, parts = FACTOR_SPEC[key]
    return Factor(key=key, symbol=sym, name=name, axis=axis, parts=list(parts))


# 근거 등급 서열 — **높은 것부터**. 이 목록이 단일 원천이다.
# ⚠ 같은 서열을 다른 모듈에 손으로 다시 적지 마라. tools/completion.py 가
#   자기 표를 따로 들고 있다가 "measured" 를 빠뜨려, 최상급에 가까운 실측
#   등급을 0점(unverified 취급)으로 읽고 이미 확보된 값의 문헌을 다시 찾으라고
#   회차를 오유도한 적이 있다(2026-09-16). 소비자는 이 상수를 import 하라.
_CONF_ORDER = ["verified", "measured", "literature", "estimated", "unverified"]


def _worst_conf(*confs: str) -> str:
    """여러 근거를 합칠 때 신뢰도는 가장 약한 것을 따른다."""
    order = _CONF_ORDER
    idx = max((order.index(c) if c in order else len(order) - 1) for c in confs) \
        if confs else len(order) - 1
    return order[min(idx, len(order) - 1)]


def _pack_conf(pack, *keys: str) -> str:
    """주어진 키들의 근거 등급 중 가장 약한 것.

    ⚠ 키가 하나도 없으면 "unverified" 를 돌려준다 — 이것은 하한이 아니라
    **"근거를 물어볼 대상이 없다"**는 뜻이다. 선언되지 않은 것을 통과시키면
    미선언이 통과로 읽힌다.
    """
    confs = []
    for k in keys:
        if pack.has(k):
            try:
                confs.append(pack.param(k).confidence or "unverified")
            except Exception:
                confs.append("unverified")
    return _worst_conf(*confs) if confs else "unverified"


# ═══════════════════════════════════════════════════ 장비축 (Equipment)

def _f_lambda(rr: "ResolvedRecipe") -> Factor:
    """Λ 기계 부하 강도 = P·V (Preston 곱, 단위면적 마찰일률).

    Preston MRR = Kp·P·V 에서 Kp를 뺀 나머지 전부. 장비가 웨이퍼에 가하는
    기계적 부하를 단일 숫자로 압축한 것이다.

    기준: 팩의 pressure_psi × (그 조건의 상대속도). 기준 조건에서 1.0.
    """
    f = _new("lambda")
    P = float(rr.pressure_psi)
    # 상대속도 대표값: 웨이퍼 중심(r=r_cc)에서의 전형 상대속도.
    # 회전 CMP의 상대속도는 Rs=1일 때 반경 무관하게 ω_p·r_cc 이다
    # (knowledge/physics/cmp-kinematics-rotary.md — verify PASS).
    omega_p = float(rr.rpm_platen) * 2.0 * math.pi / 60.0
    V = omega_p * float(rr.center_offset_m)
    f.drivers = {
        "pressure_psi": P,
        "rpm_platen": float(rr.rpm_platen),
        "rpm_wafer": float(rr.rpm_wafer),
        "center_offset_m": float(rr.center_offset_m),
    }
    pk = rr.pack
    P_ref = float(pk.get_or("lambda_ref_pressure_psi", P))
    rpm_ref = float(pk.get_or("lambda_ref_rpm_platen", float(rr.rpm_platen)))
    rcc_ref = float(pk.get_or("lambda_ref_center_offset_m", float(rr.center_offset_m)))
    V_ref = rpm_ref * 2.0 * math.pi / 60.0 * rcc_ref
    denom = P_ref * V_ref
    if denom <= 0:
        f.notes.append("⚠ 기준 P·V가 0 이하 — Λ 계산 불가")
        return f
    f.value = (P * V) / denom
    f.terms = {"P": P / P_ref if P_ref else 1.0, "V": V / V_ref if V_ref else 1.0}
    f.status = "modeled"
    f.confidence = _pack_conf(pk, "pressure_psi", "rpm_platen", "center_offset_m")
    f.sources = ["knowledge/physics/cmp-kinematics-rotary.md",
                 "knowledge/cmp/preston-luo-dornfeld-mrr.md"]
    f.notes.append(f"P·V = {P*V:.4g} psi·m/s (기준 대비 {f.value:.3f}배)")
    if not pk.has("lambda_ref_pressure_psi"):
        f.notes.append("⚠ lambda_ref_* 가 팩에 없어 기준=현재 조건으로 폴백 "
                       "— Λ이 항상 1.0이 되어 비교 기능이 죽는다. 팩에 기준을 명시하라.")
    return f


def _f_pi(rr: "ResolvedRecipe") -> Factor:
    """Π 반경 하중 분포 — 존압력·리테이너링이 만드는 P(r) 형상.

    Λ이 '얼마나 세게'라면 Π는 '어디를 세게'다. TTV/WIWNU를 지배하는 축이고,
    Λ과 직교해야 한다(전체를 키우면 Λ, 기울기를 바꾸면 Π).

    정의: 정규화 P(r)/P̄ 의 엣지/센터 비. 균일하면 1.0.
    """
    f = _new("pi")
    zp = rr.zone_pressures_psi
    amp = float(rr.edge_pressure_amp or 0.0)
    f.drivers = {"edge_pressure_amp": amp}
    if zp:
        for i, v in enumerate(zp):
            f.drivers[f"zone_pressures_psi[{i}]"] = float(v)
    if not zp and amp == 0.0:
        f.value = 1.0
        f.status = "modeled"
        f.terms = {"uniform": 1.0}
        f.confidence = "verified"   # 균일은 정의상 참
        f.sources = ["knowledge/equipment/cmp-multizone-carrier-radial-response.md"]
        f.notes.append("균일 압력 — Π=1.0 (존압력·엣지집중 없음)")
        return f
    if zp:
        mean = sum(float(v) for v in zp) / len(zp)
        if mean <= 0:
            f.notes.append("⚠ 존 평균 압력이 0 이하 — Π 계산 불가")
            return f
        f.value = float(zp[-1]) / mean          # 최외곽 존 / 평균
        f.terms = {"edge_zone_ratio": f.value}
        f.status = "modeled"
        f.confidence = "literature"
        f.sources = ["knowledge/equipment/cmp-multizone-carrier-radial-response.md"]
        f.notes.append(f"최외곽 존/평균 = {f.value:.3f} (>1 엣지강조, <1 엣지완화)")
    else:
        f.value = 1.0 + amp
        f.terms = {"edge_amp": f.value}
        f.status = "partial"
        f.confidence = "estimated"
        f.notes.append(f"엣지 압력 집중 진폭 {amp:g} 만 반영 — 존압력 없음")
    if not rr.pack.has("retaining_ring_pressure_psi"):
        f.notes.append("⚠ 리테이닝 링 압력이 팩에 없다 — 엣지 프로파일의 주요 축이 빠졌다. "
                       "담당 tool-platen-head.")
    return f


def _f_theta(rr: "ResolvedRecipe") -> Factor:
    """Θ 열·유동 부하 — 마찰 발열과 슬러리 냉각/공급의 균형.

    발열은 두 독립 채널의 곱이다: Λ(웨이퍼-패드 마찰, 기존)과 리테이닝 링 압력(링-패드 마찰,
    Lee/Guo/Jeong 2012, doi:10.1007/s12541-012-0004-8, knowledge/physics/cmp-theta-retaining-
    ring-pressure-heat-channel.md — Table 1 총마찰력 선형회귀 R²>0.99). 냉각은 세 독립 채널로
    이루어진다: ①슬러리 유량(SFR, 대류 물질교환) ②플래튼 냉각수 온도(열전달 구동력 ΔT)
    ③플래튼 회전속도(회전 대류냉각, von Karman 회전원판 Nu∝Re^0.5 — Harmand et al. 2013,
    doi:10.1016/j.ijthermalsci.2012.11.009, knowledge/physics/cmp-theta-rotation-convective-
    cooling-driver.md). rpm_platen은 Λ의 발열(V=ω·r_cc, 선형)에도 쓰이지만 냉각 쪽에서는
    제곱근으로 스케일링돼 순net 효과는 완화될 뿐 상쇄되지 않는다(같은 노트 §2).
    Yuh 2015(doi:10.1007/s40684-015-0041-8)가 SFR·온도를 독립 실험축으로 스윕했다
    (knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md §1).
    온도는 Arrhenius로 화학속도를, 유량은 신선 슬러리 공급을 지배한다.

    ⚠ 회전 냉각 채널은 전체 냉각의 일부만 차지한다(2026-09-13 정정): White 2003 원문 열저항
    네트워크(정상상태 검증판은 sim/tier2_physics/cmp_theta_steady_state_heat_balance.py,
    frictional-heating-temperature-arrhenius-coupling.md §8.2/§8.4)에 따르면 냉각은
    G_slurry(엔탈피 수송, 회전무관)+G_pad(전도, 회전무관)+G_air(회전 대류, √Ω)의 병렬합이고
    Shin 2025 중앙 케이스 분해가 슬러리 74%/패드 19%/공기 7%임을 준다. 과거에는 cool_rotation
    전체를 √Ω로 스케일해 이 7% 채널의 효과를 냉각 전체(100%)에 적용했다 — 회전 냉각 효과를
    심하게 과대평가한 것이다(§8.4 "정정 후보"로 기록되어 있었음). 지금은 가중평균
    (1-W_AIR_FRACTION)·1.0 + W_AIR_FRACTION·√Ω로 그 7%만 반영한다. W_AIR_FRACTION=0.07은
    단일 케이스(Shin 2025 중앙값)에서 나온 근사치이고 범위는 6~8%다(§8.4 최소/최대 케이스) —
    구조적 결측(§8.5: 웨이퍼/헤드 경로 미모델링, L_pad 유효길이, h_air CMP 실측, 완전 열교환
    가정)이 전혀 닫히지 않았으므로 confidence는 여전히 estimated다.

    ⚠ 절대 온도가 아니라 **기준 대비 부하비**다. 실제 ΔT 예측은
    knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md 의
    모델이 담당하고, 여기서는 팩터로 압축만 한다.
    """
    f = _new("theta")
    pk = rr.pack
    if not pk.has("sfr_ml_min"):
        f.notes.append("⚠ Θ 미모델링: SFR(슬러리 유량)이 팩·레시피에 없다. "
                       "유량은 실제 툴에서 가장 자주 만지는 손잡이인데 엔진에 통로가 없다. "
                       "담당 tool-platen-head.")
        f.drivers = {}
        return f
    sfr = float(pk.get("sfr_ml_min"))
    sfr_ref = float(pk.get_or("sfr_ref_ml_min", sfr))
    lam = _f_lambda(rr)
    f.drivers = {"sfr_ml_min": sfr}
    f.drivers.update(lam.drivers)
    if sfr_ref <= 0 or lam.value is None:
        f.notes.append("⚠ 기준 SFR 또는 Λ 결측 — Θ 계산 불가")
        return f
    cool_sfr = sfr / sfr_ref
    cool_temp = 1.0   # 냉각수 온도 항 없으면 기준으로 폴백 (조용히 1.0 = 기존 partial 계약 유지)
    if pk.has("platen_coolant_temp_c") and pk.has("platen_hot_side_ref_c"):
        T_coolant = float(pk.get("platen_coolant_temp_c"))
        T_ref = float(pk.get_or("platen_coolant_ref_c", T_coolant))
        T_hot = float(pk.get("platen_hot_side_ref_c"))
        # 발산 가드: 냉각수온도가 열원온도에 근접하면 clip
        # (knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md §4)
        T_coolant_clip = min(T_coolant, T_hot - 0.5)
        driving_ref = T_hot - T_ref          # 기준 냉각 구동력(항상 >0, Recipe 검증 불필요)
        driving_now = T_hot - T_coolant_clip  # 이번 런 냉각 구동력 — 냉각수 찰수록 커짐(냉각효과↑)
        if driving_ref > 0:
            cool_temp = driving_now / driving_ref
        f.drivers["platen_coolant_temp_c"] = T_coolant
    # 회전 대류냉각 채널 — von Karman 회전원판 Nu∝Re_r^0.5 (층류, 지수 b=0.5 문헌 일치,
    # knowledge/physics/cmp-theta-rotation-convective-cooling-driver.md §1-2).
    # 새 파라미터 없이 Λ와 같은 lambda_ref_rpm_platen을 재사용(같은 회전축, 이중기준 방지).
    #
    # ⚠ 정정(2026-09-13): 이 회전 채널(G_air)은 전체 냉각 컨덕턴스(G_slurry+G_pad+G_air)의
    # 일부(W_AIR_FRACTION)만 차지한다 — frictional-heating-temperature-arrhenius-coupling.md
    # §8.4 Shin 2025 "중앙 케이스" 정상상태 열저항 네트워크 분해: 슬러리 74% / 패드 19% /
    # 공기 7%. 나머지 두 채널(G_slurry, G_pad)은 회전수와 무관(§8.2)한데도 과거 코드는
    # √Ω 스케일을 냉각 전체에 곱해 회전 냉각 효과를 심하게 과대평가했다(§8.4 "정정 후보").
    # 가중평균으로 고친다: 안 변하는 (1-W_AIR_FRACTION) 채널은 1.0, 공기 채널만 √Ω.
    # W_AIR_FRACTION은 단일 케이스(Shin 2025 중앙값)에서 나온 근사치이며 범위는 6~8%다
    # (§8.4 표의 최소/최대 케이스). 구조적 결측(§8.5)이 해소된 게 아니므로 confidence는
    # estimated로 유지한다.
    W_AIR_FRACTION = 0.07
    rpm_platen = float(rr.rpm_platen)
    rpm_ref = float(pk.get_or("lambda_ref_rpm_platen", rpm_platen or 1.0))
    rotation_ratio = math.sqrt(rpm_platen / rpm_ref) if rpm_ref > 0 else 1.0
    cool_rotation = (1.0 - W_AIR_FRACTION) * 1.0 + W_AIR_FRACTION * rotation_ratio
    # 리테이닝 링 압력 — 웨이퍼-패드 마찰(Λ)과 독립인 추가 발열원(Lee/Guo/Jeong 2012 Table 1,
    # knowledge/physics/cmp-theta-retaining-ring-pressure-heat-channel.md). 총 마찰력 F_wafer+F_ring이
    # RR압력에 선형(R²>0.99)이라는 실측을 기준 대비 배수로 압축한다. 없으면 1.0 폴백(기존 partial 계약 유지).
    heat_ring = 1.0
    if pk.has("retaining_ring_pressure_psi"):
        rr_psi = float(pk.get("retaining_ring_pressure_psi"))
        rr_ref = float(pk.get_or("retaining_ring_ref_psi", rr_psi))
        # Lee/Guo/Jeong 2012 Table 1 정규화 회귀계수 (기준 5psi=1.0):
        # a_norm=0.6145/(0.6145+0.07692*5)=0.6145/0.9991, b_norm=0.07692/0.9991
        A_COEF, B_COEF = 0.6145, 0.07692
        denom_ref = A_COEF + B_COEF * rr_ref
        if denom_ref > 0:
            heat_ring = (A_COEF + B_COEF * rr_psi) / denom_ref
        f.drivers["retaining_ring_pressure_psi"] = rr_psi
    # 부하비 = 발열(Λ×ring) / [냉각(SFR) × 냉각(온도) × 냉각(회전대류)]. 기준 조건에서 1.0.
    f.value = (lam.value * heat_ring) / (cool_sfr * cool_temp * cool_rotation)
    f.terms = {"heat(Λ)": lam.value, "heat(ring)": heat_ring, "cool(SFR)": cool_sfr,
               "cool(coolant_temp)": cool_temp, "cool(rotation)": cool_rotation}
    # 완전성 판정: SFR은 진입 가드에서 이미 필수(없으면 조기 return). 나머지 4채널
    # (heat(ring)/cool(coolant_temp)/cool(rotation)/heat(Λ))이 전부 실제 팩 파라미터로
    # 구동되면(문헌 4건: Lee/Guo/Jeong 2012, Yuh 2015, Harmand 2013, frictional-heating
    # coupling 노트) modeled — kappa/chi와 동일하게 "필요 항 전부 있으면 modeled" 규칙을
    # 적용한다. 이전 3회차(bcc2e5a/84c8e36/7382ab3)가 드라이버를 다 채웠는데도 이 줄이
    # 무조건 partial을 리턴해 accuracy_gaps가 영원히 PARTIAL을 반환하던 버그를 수정.
    have_all_channels = (
        pk.has("platen_coolant_temp_c") and pk.has("platen_hot_side_ref_c")
        and pk.has("retaining_ring_pressure_psi") and lam.value is not None
    )
    f.status = "modeled" if have_all_channels else "partial"
    # 등급 하한 판정 (2026-09-13) — 근거 없는 리터럴을 걷어낸다.
    #   이 팩터의 가장 약한 고리는 무엇인가? 결합 관계(마찰일 → 온도 상승)는
    #   에너지 보존에서 나오고 계수는 문헌 노트에 근거가 있다. 즉 드라이버보다
    #   약한 별도 요소가 없다. 그러므로 하한을 두지 않고 드라이버 등급을 따른다.
    #   ⚠ 채널이 덜 갖춰진 상태(partial)는 등급이 아니라 status 가 말한다 —
    #     둘을 섞으면 문헌을 채워도 등급이 안 오르는 구조가 된다(실제로 그랬다).
    f.confidence = _pack_conf(pk, "sfr_ml_min")
    f.sources = ["knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md",
                 "knowledge/equipment/cmp-rpm-ratio-flowrate-temperature-mrr-stability.md",
                 "knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md",
                 "knowledge/physics/cmp-theta-rotation-convective-cooling-driver.md",
                 "knowledge/physics/cmp-theta-retaining-ring-pressure-heat-channel.md"]
    f.notes.append("⚠ 발열/냉각을 1차 비례로 압축했다 — 실제 열저항·체류시간은 "
                   "미반영. 절대 ΔT는 별도 열모델이 담당한다.")
    if not pk.has("sfr_ref_ml_min"):
        f.notes.append("⚠ sfr_ref_ml_min 없어 기준=현재값 폴백 — SFR 변화가 Θ에 안 잡힌다.")
    if "platen_coolant_temp_c" not in f.drivers:
        f.notes.append("⚠ platen_coolant_temp_c 없어 냉각수온도 항 1.0 폴백 — "
                       "cmp-theta-platen-coolant-temperature-driver.md §2 참조, 담당 tool-platen-head.")
    if "retaining_ring_pressure_psi" not in f.drivers:
        f.notes.append("⚠ retaining_ring_pressure_psi 없어 링 발열 항 1.0 폴백 — "
                       "cmp-theta-retaining-ring-pressure-heat-channel.md §3 참조, 담당 tool-platen-head.")
    return f


# Γ 하한사유(2) 조건부 톨러런스 — aging 배수 A=pcr_now/pcr_ref 가 1에서 이만큼 벗어날 때만
# τ(2차 인용 앵커) 사유로 estimated 하한을 건다. 기준조건(t=t_ref)에서는 A≡1이라 τ와 무관함이
# knowledge/equipment/gamma-conditioning-load-confidence-basis.md §3 verify로 증명됨(5팩, τ×10·×0.1).
# 0.01은 "A가 1%만 벗어나도 τ가 결과를 지배한다"는 뜻의 문턱이지 문헌값이 아니다(추정 아님, 정의).
GAMMA_AGING_CONF_TOL = 0.01


def _f_gamma(rr: "ResolvedRecipe") -> Factor:
    """Γ 컨디셔닝 부하 — 디스크가 패드에 가하는 단위시간 절삭일 (Preston형).

    Zheng et al.(2023) Eq.11: PCR = Kp·P·v_rel. v_rel(디스크-패드 상대속도)의
    지배항은 disk-rpm-load-radius-pcr.md §4가 유도·검증한 **디스크 중심 속도
    ω_p·r_cc**다 — 이 항은 디스크 자전비(Rs=ω_disk/ω_pad)와 무관하게 정확하고,
    같은 문헌조건(Rs=0.73)에서 디스크 전체 평균 v/(ω_p·r_cc)는 1.0004(0.04%
    편차)로 사실상 완전히 지배적이다(§7 verify). r_cc는 레시피가 아니라 스윕
    기구 형상(같은 장비)이므로 F·v 비율에서 상쇄돼, v 항을 rpm_platen(같은
    플래튼) 비율만으로 근사할 수 있다 — Λ이 이미 쓰는 것과 동일 근사(§7 참조).

    **cond_sweep_cpm(스윕 왕복수 n_a)은 v_rel 식에 나타나지 않는다** — 반경별
    궤적밀도·체류시간 분포(어디를 깎는가)를 결정하는 별개 축이다
    (conditioner-sweep-algorithm-trajectory-density.md,
    conditioner-sweep-kinematics-pcr-profile.md). Γ는 반경 무관 스칼라(총
    절삭 부하)이므로 sweep_cpm을 곱하지 않는다 — 곱하면 서로 다른 물리량
    (회전 상대속도 vs 왕복수)을 이중 계상하는 것이었다(2026-09-11 정정, 이전
    버전은 force×sweep×duty로 sweep을 속도 대리항처럼 썼다).

    confidence 하한 3사유 — 2026-09-14 판정(knowledge/equipment/
    gamma-conditioning-load-confidence-basis.md, EVIDENCE-RULES 판정#22):
    (1) **해소** — 디스크 내 상대속도의 Rs 보정은 총량 스칼라에 대해 폐형식
    상계 ⟨|v|⟩/(ω_p r_cc) = 1 + μ²/8 + μ⁴/192 (면적 가중)로 묶이고, 확보한 문헌
    범위(|1−Rs| ≤ 0.75, R_disk/r_cc ≤ 0.63) 전체에서 스윕평균 편차 <1%(산업 조건
    <0.2%)다(노트 §2). 에지 peak-to-peak 14.4%(disk-rpm-load-radius-pcr.md §4)는
    **반경별 분포**의 몫이지 Γ(스칼라)의 결측이 아니다. disk RPM 드라이버 부재는
    등급을 제한하지 않는다.
    (2) **조건부** — 컨디셔너 PCR 시간적 소진은 `cond_disk_usage_hours`가 있으면
    sim/tier2_physics/conditioner_pcr_decay.py의 `pcr_decay()`(TAU_AGING_HOURS≈27.4h,
    Entegris 2차인용 앵커 50h→16% 역산, 판정#14 미확보 종결)로 반영된다. 이 함수는
    **비율** A = pcr_now/pcr_ref 만 쓰므로 t = t_ref 에서는 τ와 무관하게 A ≡ 1 —
    5팩 기준조건(t=t_ref=0)의 Γ는 τ를 10배·1/10배로 바꿔도 불변임을 노트 §3 verify가
    증명했다. 따라서 2차 인용 앵커는 |A−1| > GAMMA_AGING_CONF_TOL 일 때만 estimated
    하한 사유가 되고, 그때 notes에 이유를 남긴다(판정#14를 뒤집는 것이 아니라
    "그 앵커가 기준조건 등급을 제한하지 않는다"는 별개 사실).
    (3) **스코프 축소 종결(3회차, 2026-09-15) — 재탐색 금지, 4회차 없음.** 임계하중
    (critical downforce) 아래에서는 절삭이 안 일어난다는 비선형이 F 선형항에
    미반영이다. 구형 팁 Hertz+Tabor로 유도한 P_c = π³R²(1.65Y)³/(6E*²)에 IC1000
    물성(Saka 2008: E_p 0.5 GPa, H_p 0.05 GPa)을 넣으면, 중심 사례(R=15 µm 가정,
    작동 그릿 10%)는 그릿당 하중이 P_c의 ~40배(임계 downforce ≈0.10 lbf)로 운전점
    4 lbf에서 멀지만, 마모 팁 반경 R을 기하 상한(D/2=90 µm)으로 밀면 1.1배, 작동
    그릿 18,000개까지 겹치면 0.28배로 **부호까지 뒤집힌다**. 임계 downforce
    범위(0.02~14 lbf)가 운전점을 가로지르므로 하한 유지(노트 §4). 3회차에 걸쳐
    (마모 그릿 팁 반경 R 실측, IC1000 항복강도 직접 실측 Y)를 겨냥한 문헌 탐색을
    반복했으나(3회차에 Wei 2010 UA 학위논문을 처음 식별·확보했지만 furrow 단면적·
    UTS 대용값뿐이라 부적격), 이 코퍼스에서 두 값의 1차 문헌은 나오지 않는다는
    결론이 확정됐다 — **"임계하중 비선형은 실재하나 이 계에서 정량화할 1차 문헌이
    없다"는 영구 확정**(노트 §4.7, EVIDENCE-RULES 판정#22-종결). ⚠ 임계 아래에서는
    선형 F항이 과대추정이다.

    **S(stab)와의 결합(2026-09-14)**: 같은 `aging(pcr_decay)` 배수 A(t_disk)가 S의 컨디셔닝 강도
    G = duty/100·A 에도 들어간다(knowledge/materials/pad-steady-state-glazing-conditioning-balance.md
    §3). Γ은 A를 절삭 **부하**로, S는 정상상태 **조도** R_ss=k_c G/(k_g+k_c G)로 변환한다 —
    한 함수를 공유하므로 드레서 마모의 이중 정의가 없고, 드레서 사용량↑ → Γ↓·S↓ 가 같은 부호다.
    PHM2016 실장비(드레서 사용량 vs MRR 저속군 ρ=−0.696)는 이 경로의 순위 검증이다(S 쪽 verify).

    ⚠ 여기는 **장비 설정**(하중·회전속도·duty)만 담는다. 디스크의 형상(그릿
    밀도·돌출)은 소모품이므로 κ/τ 쪽으로 간다. 이 분리를 지켜야 "디스크를
    바꿀까 컨디셔너 세팅을 바꿀까"에 답할 수 있다.
    """
    f = _new("gamma")
    pk = rr.pack
    needed = ["cond_downforce_lbf", "cond_duty_pct"]
    have = [k for k in needed if pk.has(k)]
    if not have:
        f.notes.append("⚠ Γ 미모델링: 컨디셔너 하중·duty 중 어느 것도 팩에 없다. "
                       "패드 절삭률(PCR)이 MRR 안정성을 지배하는데 통로가 없다. "
                       "담당 disk-conditioner.")
        return f
    F = float(pk.get_or("cond_downforce_lbf", 0.0))
    duty = float(pk.get_or("cond_duty_pct", 100.0))
    omega_p = float(rr.rpm_platen)
    f.drivers = {"cond_downforce_lbf": F, "rpm_platen": omega_p, "cond_duty_pct": duty}
    if pk.has("cond_sweep_cpm"):
        # 진단용 로깅만 — Γ 크기에는 곱하지 않는다(위 docstring 참조).
        f.drivers["cond_sweep_cpm(coverage_only,not_multiplied)"] = float(
            pk.get_or("cond_sweep_cpm", 0.0))
    F_ref = float(pk.get_or("cond_ref_downforce_lbf", F or 1.0))
    omega_ref = float(pk.get_or("lambda_ref_rpm_platen", omega_p or 1.0))
    duty_ref = float(pk.get_or("cond_ref_duty_pct", duty or 100.0))

    pcr_now = 1.0
    pcr_ref = 1.0
    if pk.has("cond_disk_usage_hours"):
        import conditioner_pcr_decay as CPD   # sim/tier2_physics (1바이트도 수정 안 함)
        t_hours = float(pk.get("cond_disk_usage_hours"))
        t_ref_hours = float(pk.get_or("cond_ref_disk_usage_hours", 0.0))
        pcr_now = CPD.pcr_decay(t_hours, 1.0, CPD.TAU_AGING_HOURS)
        pcr_ref = CPD.pcr_decay(t_ref_hours, 1.0, CPD.TAU_AGING_HOURS)
        f.drivers["cond_disk_usage_hours"] = t_hours

    denom = F_ref * omega_ref * duty_ref * pcr_ref
    if denom <= 0:
        f.notes.append("⚠ 기준 컨디셔닝 부하가 0 — Γ 계산 불가")
        return f
    f.value = (F * omega_p * duty * pcr_now) / denom
    f.terms = {"force": F / F_ref if F_ref else 1.0,
               "velocity(rpm_platen)": omega_p / omega_ref if omega_ref else 1.0,
               "duty": duty / duty_ref if duty_ref else 1.0,
               "aging(pcr_decay)": pcr_now / pcr_ref if pcr_ref else 1.0}
    f.status = "modeled" if len(have) == len(needed) else "partial"
    # 등급 판정 (2026-09-14, 노트 gamma-conditioning-load-confidence-basis.md §5) —
    #   드라이버 등급 위에 두 종류의 하한을 건다. 값(f.value)은 건드리지 않는다.
    #   · 사유(3) 임계하중 비선형: **스코프 축소 종결(3회차, §4.7)** → 무조건 estimated
    #     확정(하한이 아니라 확정값). 마모 그릿 팁 반경·IC1000 항복강도 직접값 모두
    #     이 코퍼스에 없다고 3회차 규칙으로 종결됐다 — 후속 재탐색 금지, 4회차 없음.
    #   · 사유(2) τ 2차 인용 앵커(판정#14): 기준조건에서는 A≡1이라 무관 → |A−1| >
    #     GAMMA_AGING_CONF_TOL 일 때만 하한(조건부). 사유(3)과 독립이라 이 조건부
    #     하한만 별도로 남겨 두었다.
    #   · 사유(1) Rs 보정: 해소(총량 스칼라 한정) — 하한 사유에서 제외.
    aging_ratio = f.terms["aging(pcr_decay)"]
    driver_keys = [*have, "rpm_platen"]
    if pk.has("cond_disk_usage_hours"):
        driver_keys.append("cond_disk_usage_hours")
    driver_conf = _pack_conf(pk, *driver_keys)
    f.confidence = _worst_conf(driver_conf, "estimated")          # 사유(3) 스코프 축소 종결(확정 하한)
    if abs(aging_ratio - 1.0) > GAMMA_AGING_CONF_TOL:
        f.confidence = _worst_conf(f.confidence, "estimated")    # 사유(2) 조건부 하한
        f.notes.append(
            f"⚠ aging 배수 A={aging_ratio:.4f}(|A−1|>{GAMMA_AGING_CONF_TOL:g}) — 이 배수의 크기는 "
            "TAU_AGING_HOURS≈27.4h(Entegris 백서가 재인용한 Palmgren 2004, 원문 미확보, "
            "EVIDENCE-RULES 판정#14)에 걸려 있어 estimated 하한(조건부). 기준조건(t=t_ref)에서는 "
            "A≡1이라 이 사유는 등급을 건드리지 않는다(gamma-conditioning-load-confidence-basis.md §3).")
    f.sources = ["knowledge/equipment/conditioner-disk-pad-cutting-model.md",
                 "knowledge/equipment/disk-rpm-load-radius-pcr.md",
                 "knowledge/equipment/gamma-conditioning-load-confidence-basis.md"]
    if f.status == "partial":
        missing = [k for k in needed if k not in have]
        f.notes.append(f"⚠ 부분 모델링 — 결측: {', '.join(missing)}")
    f.notes.append("⚠ force×velocity(rpm_platen)×duty 곱 형태는 절삭일률의 1차 근사다 — "
                   "임계하중(critical downforce) 아래에서는 절삭이 안 일어난다는 비선형이 "
                   "미반영(estimated 확정 사유 — 스코프 축소 종결, 3회차 재탐색 완료·재탐색 금지). "
                   "Hertz+Tabor 유도 P_c는 마모 팁 반경 R²에 걸리는데 R·IC1000 항복강도 직접값 "
                   "모두 이 코퍼스에서 못 낸다고 확정돼 임계 downforce가 0.02~14 lbf 범위로 운전점 "
                   "4 lbf를 가로지른다 — 임계 아래에서는 선형 F항이 과대추정이다"
                   "(gamma-conditioning-load-confidence-basis.md §4, §4.7).")
    f.notes.append("velocity 항은 rpm_platen(패드 RPM)만 쓴다 — 디스크 자전비(Rs) 보정은 총량 스칼라에 "
                   "대해 1+μ²/8+μ⁴/192(면적 가중 폐형식)로 묶이고 문헌 범위(|1−Rs|≤0.75, "
                   "R_disk/r_cc≤0.63)에서 스윕평균 <1%라 등급 사유에서 제외(해소, "
                   "gamma-conditioning-load-confidence-basis.md §2). 디스크 에지 peak-to-peak 14.4%는 "
                   "반경별 분포 모듈의 몫이다(disk-rpm-load-radius-pcr.md §4).")
    f.notes.append("⚠ cond_sweep_cpm은 Γ 크기에 곱하지 않는다 — 문헌(disk-rpm-load-radius-pcr.md, "
                   "conditioner-sweep-algorithm-trajectory-density.md)에 따르면 스윕 왕복수는 "
                   "v_rel 식에 없고 반경별 궤적밀도(공간분포)만 결정한다. 총 절삭 부하가 아니다.")
    if not pk.has("cond_disk_usage_hours"):
        f.notes.append("⚠ cond_disk_usage_hours 없음 — 디스크 신품 가정(aging 배수=1.0), "
                       "PCR 시간적 소진(conditioner-disk-pad-cutting-model.md §3) 미반영.")
    return f


# ═══════════════════════════════════════════════════ 소모품축 (Consumable)

def _f_kappa(rr: "ResolvedRecipe") -> Factor:
    """κ 접촉 강도 = 활성 입자 수 × 입자당 압입 깊이.

    **세 파트가 함께 결정하는 대표 팩터다.**
      - 슬러리: 입경 R, 함량 → 접촉 입자 수
      - 패드:   경도 H, 탄성률 → 입자당 하중과 압입
      - 디스크: asperity 밀도 → 실접촉 면적

    물리: δ_p = F/(2πR·H) 이고 제거 단면 A_f ∝ δ_p^1.5 ⟹ **MRR ∝ H^-1.5**
    (knowledge/cmp/particle-wafer-interaction-... §4, verify PASS).

    ⚠ 화학적 연화(χ)도 같은 H를 통해 들어간다. **두 번 세지 않도록** κ는
    '기계적 경도'만, χ는 '화학이 만든 경도 변화분'만 담당한다.
    """
    f = _new("kappa")
    pk = rr.pack
    terms: Dict[str, float] = {}
    srcs: List[str] = []

    # ① 슬러리: 입자 함량 → 접촉 입자 수 (1차: 선형)
    if pk.has("abrasive_wt_pct"):
        c = float(pk.get("abrasive_wt_pct"))
        f.drivers["abrasive_wt_pct"] = c
        c_ref = float(pk.get_or("abrasive_ref_wt_pct", c))
        # ⚠ 입자 부재 판정이 기준점 판정보다 **먼저**다 (입경 항과 같은 이유).
        #   c=0 을 조건에서 제외하면 항이 **아예 만들어지지 않아** 곱셈에서
        #   1.0 처럼 취급된다 — "입자가 없는데 제거율은 그대로"라는 뜻이 된다.
        #   침묵이 '효과 없음'으로 읽히는 이 패턴이 극한 검사를 무력화했다
        #   (2026-09-13). 하중을 전달할 매개가 없으면 제거 경로가 없으므로
        #   0 을 **명시적으로 계상**한다(LIMIT_ROLE: AGENT).
        if c <= 0:
            terms["conc"] = 0.0
            f.notes.append(
                "연마입자 함량 0 — 하중을 표면으로 전달할 매개가 없어 제거 경로가 "
                "성립하지 않는다. 항을 0 으로 계상한다(빈 항으로 두면 '효과 없음'과 "
                "구분되지 않는다).")
        elif c_ref > 0 and c > 0:
            # Li et al. 2021(doi:10.1149/2162-8777/ac3e44)이 인용한 두 극한 모델:
            #   표면적 지배  R ∝ C0^(1/3)
            #   압입 지배    R ∝ C0^(4/3)
            # 이 두 값 자체는 2차 인용(E5)이라 어느 쪽인지 미확정이었으나, US9499721B2
            # (Cabot, 콜로이달 실리카 TEOS, E1 직접 실측 24점, TABLE 18)의 전역
            # 로그-로그 회귀가 n≈0.30을 줘 표면적 극한(1/3) 쪽으로 판정됐다
            # (EVIDENCE-RULES.md — E1이 E5를 이긴다;
            # knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md §5).
            # 기본값 1/3을 유지하고, 팩이 명시하면 그걸 따른다.
            # ⚠ 같은 데이터가 국소 지수 붕괴(0.5→1.0wt%에서 0.56, 2.5→3.0wt%에서 0.11)를
            # 보여 순수 거듭제곱 자체는 고농도 포화를 구조적으로 표현 못 한다 — 지수값
            # 판정과는 별개 문제이며 함수형 교체는 이 결함 해소 범위 밖(같은 노트 §8 참조).
            n = float(pk.get_or("abrasive_conc_exponent", 1.0 / 3.0))
            # ── 지수를 이론에서 유도해 본다 ─────────────────────────
            # 팩이 적어넣은 지수는 '그 슬러리에서 회귀한 값'이라 다른 조건으로
            # 외삽할 근거가 없다. 물성이 갖춰진 팩은 χ·α·공급형태로부터 지수를
            # **계산**한다(sim/abrasive_mechanics.py 의 3인자 분해).
            try:
                from sim.regime_adapter import exponents_for
                _ex = exponents_for(pk, getattr(rr, "pressure_psi", None))
                if _ex.get("derived") and _ex.get("n_conc") is not None:
                    n = float(_ex["n_conc"])          # type: ignore[arg-type]
                    f.notes.append(
                        f"농도 지수 n={n:+.3f} 를 **이론에서 유도**했다 "
                        f"(등급 {_ex['confidence']}). " +
                        str(_ex["regime"].explain()))  # type: ignore[union-attr]
                _nts = _ex.get("notes")
                for _nt in (list(_nts) if isinstance(_nts, list) else [])[:4]:
                    if str(_nt).startswith("⚠"):
                        f.notes.append(str(_nt))
            except Exception as _e:      # 유도가 실패해도 기존 경로는 살아야 한다
                f.notes.append(f"⚠ 지수 유도 시도 실패({_e!r}) — 팩 선언값을 쓴다.")
            terms["conc"] = (c / c_ref) ** n
            srcs.append("knowledge/cmp/abrasive-size-concentration-"
                        "ph-K-additive-mrr-quantitative.md")
            srcs.append("knowledge/cmp/abrasive-concentration-mrr-saturation-"
                        "contact-probability.md")
            f.notes.append(f"⚠ 농도 지수 n={n:.3f} — 표면적 극한(1/3)은 US9499721B2 E1 실측 "
                           "전역회귀(n≈0.30)로 압입 극한(4/3)보다 우세하다고 판정됐다(같은 "
                           "데이터가 국소 지수는 0.56→0.11로 붕괴 — 순수 거듭제곱은 고농도 "
                           "포화를 못 담는다는 별개의 구조적 한계는 남아있음).")
            # Luo-Dornfeld 포화: 7 wt% 이상에서 RR 불변이 관측된 계가 있다.
            sat = pk.get_or("abrasive_saturation_wt_pct", None)
            if sat is not None and c > float(sat):
                f.notes.append(f"⚠ 입자 함량 {c:g} wt%가 포화농도 {float(sat):g} wt%를 "
                               "넘었다 — 실제로는 더 넣어도 MRR이 안 오른다"
                               "(Luo-Dornfeld 포화영역). 현재 항은 계속 증가시키므로 "
                               "이 구간 예측은 과대평가다.")

    # ② 슬러리: 입경 → 입자당 압입 (δ_p ∝ 1/R)
    if pk.has("abrasive_size_nm"):
        d = float(pk.get("abrasive_size_nm"))
        f.drivers["abrasive_size_nm"] = d
        d_ref = float(pk.get_or("abrasive_ref_size_nm", d))
        # ⚠ 입자 부재 판정이 기준점 판정보다 **먼저**다.
        #   기준점이 없으면 d_ref 는 본값으로 폴백하므로, d=0 일 때 d_ref 도 0 이
        #   되어 아래 d_ref>0 분기가 전부 빠진다 — 항이 사라져 '효과 없음(1.0)'
        #   으로 읽힌다. "입자가 없다"는 사실은 기준점을 아는지와 무관하므로
        #   순서를 뒤집는다.
        if d <= 0:
            terms["size"] = 0.0
            f.notes.append(
                "입자 크기 0 — 크기가 없는 입자는 입자가 아니다. 압입 깊이가 "
                "정의되지 않으므로 항을 0 으로 계상한다.")
        elif d_ref > 0:
            # ⚠ 입경 방향의 지수는 **문헌이 확정하지 못했다.**
            # Li et al. 2021은 40→80→130 nm에서 MRR이 80 nm에 정점을 갖는다고
            # 정성 서술하지만(압입지배→표면적지배 전환), 원문 Eq.3-4의 지수·부호가
            # OCR로 뒤섞여 노트조차 입경 방향을 assert하지 않았다.
            # 그러므로 **지수를 지어내지 않는다.** 팩이 명시할 때만 적용한다.
            # 2026-09-13: Li et al. 2021 Eq.3-4를 pdfplumber 벡터좌표로 재추출해
            # 지수·부호가 확정됐다(knowledge/cmp/abrasive-size-concentration-ph-K-additive-
            # mrr-quantitative.md §4 2026-09-13 정정). 팩이 정점형 3파라미터
            # (abrasive_size_peak_nm·abrasive_size_exp_below_peak·abrasive_size_exp_above_peak)를
            # 명시하면 piecewise 곡선을 쓴다 — 단일 멱함수보다 우선한다(정점 거동을 담기
            # 때문). 없으면 기존 단일지수/null 경로로 폴백한다.
            peak_nm = pk.get_or("abrasive_size_peak_nm", None)
            exp_below = pk.get_or("abrasive_size_exp_below_peak", None)
            exp_above = pk.get_or("abrasive_size_exp_above_peak", None)
            if peak_nm is not None and exp_below is not None and exp_above is not None:
                peak_nm = float(peak_nm)
                exp_below = float(exp_below)
                exp_above = float(exp_above)

                def _piecewise_curve(x: float) -> float:
                    # 정점에서 두 식이 연속이 되도록 peak**exp_below를 앵커로 삼는다.
                    if x <= peak_nm:
                        return x ** exp_below
                    return (peak_nm ** exp_below) * (x / peak_nm) ** exp_above

                c_d, c_ref = _piecewise_curve(d), _piecewise_curve(d_ref)
                if c_ref > 0:
                    terms["size"] = c_d / c_ref
                    srcs.append("knowledge/cmp/abrasive-size-concentration-"
                                "ph-K-additive-mrr-quantitative.md §4")
                    f.notes.append(
                        f"입경 정점형 반영: peak={peak_nm:g}nm 기준 d={d:g}nm(지수 "
                        f"{'below' if d<=peak_nm else 'above'}={exp_below if d<=peak_nm else exp_above:g}), "
                        f"d_ref={d_ref:g}nm. Li et al. 2021 Eq.3-4(압입 지배 φ^{exp_below:.3g}, "
                        f"표면적 지배 φ^{exp_above:.3g})를 벡터좌표 재추출로 확정한 값 — "
                        "이 계(콜로이달 실리카/SiO2)에 한정, 정점 위치·지수의 타 화학종 "
                        "일반화는 미검증.")
                n_size = None  # 아래 단일지수 분기를 건너뛴다
            else:
                n_size = pk.get_or("abrasive_size_exponent", None)
            if peak_nm is not None and exp_below is not None and exp_above is not None:
                pass
            elif n_size is None:
                f.notes.append(
                    "⚠ 입경 항 미적용: 지수(abrasive_size_exponent)가 팩에 없다. "
                    "문헌은 정점형(~80nm 최대)이라고만 서술하고 지수를 확정하지 "
                    "못했으므로 임의값을 쓰지 않는다 — 입경을 바꿔도 κ가 변하지 "
                    "않는다는 뜻이다. 단조 지수를 넣으면 정점 거동을 놓친다.")
            elif float(n_size) == 0.0:
                # 지수 0은 "모른다"가 아니라 "효과가 없다"는 **검증된 결론**이다.
                # 값은 1.0이라 무반응이지만, 근거가 있으므로 항으로 계상한다
                # (미모델링과 구분되어야 한다 — EVIDENCE-RULES.md 판정 #1).
                terms["size"] = 1.0
                srcs.append("knowledge/cmp/abrasive-size-null-result-"
                            "force-partition-theory.md")
                f.notes.append(
                    "입경 지수 0 — **검증된 영(null) 결과**. 교란(입자 형상)을 제거한 "
                    "부분집합에서 입경-MRR 상관이 비유의(ρ≈0.03~0.15)하고, Chen "
                    "단층모델의 면밀도 d⁻²×압입 d⁺² 상쇄가 같은 결론을 준다. "
                    "'지수 미확정'이 아니라 '이 계에서 입경은 지배인자가 아님'이다. "
                    "적용 범위 밖(응집체 비율 높은 슬러리)에는 형상 팩터가 따로 필요하다.")
            else:
                terms["size"] = (d / d_ref) ** float(n_size)
                srcs.append("knowledge/cmp/abrasive-size-concentration-"
                            "ph-K-additive-mrr-quantitative.md")
                f.notes.append(
                    f"⚠ 입경 지수 {float(n_size):g}는 팩이 지정한 값이다. 문헌은 "
                    "정점형(40→80nm 증가, 80→130nm 감소)이라 단조 멱함수로는 "
                    "한쪽 구간만 맞는다 — 적용 범위를 확인하라.")

    # ③ 패드: 경도 → MRR ∝ H^-1.5
    if pk.has("pad_hardness_shore_d"):
        h = float(pk.get("pad_hardness_shore_d"))
        f.drivers["pad_hardness_shore_d"] = h
        h_ref = float(pk.get_or("pad_ref_hardness_shore_d", h))
        if h_ref > 0 and h > 0:
            terms["pad_hardness"] = (h / h_ref) ** (-1.5)
            srcs.append("knowledge/materials/pad-hardness-porosity-"
                        "measurement-methods.md")
            f.notes.append("⚠ Shore D는 경도의 대리지표다. H^-1.5의 H는 압입경도"
                           "(GPa)인데 Shore D↔GPa 환산이 비선형이라 순위는 맞아도 "
                           "절대값은 캘리브레이션이 필요하다. Qi/Joyce/Boyce 2003"
                           "(DOI:10.5254/1.3547752, 위 노트 §8)이 범용 탄성체용 "
                           "Shore D→탄성률 해석해(eq.11)를 주지만 confidence는 "
                           "못 올린다 — ①62D 앵커점에서 FEA 대비 49% 편향만 확인"
                           "됐고 60D에서의 편향 크기는 모름, ②범용 가황고무 대상"
                           "(폴리우레탄 미검증), ③애초에 그 논문의 E는 압입경도가 "
                           "아니라 단축인장 탄성률이라 물리량 자체가 다르다.")

    # ④ 디스크: asperity 밀도 → 실접촉 면적
    if pk.has("asperity_density_per_m2"):
        n_a = float(pk.get("asperity_density_per_m2"))
        f.drivers["asperity_density_per_m2"] = n_a
        n_ref = float(pk.get_or("asperity_ref_density_per_m2", n_a))
        if n_a <= 0:
            # 같은 순서 규칙 — 접촉점이 하나도 없으면 하중을 웨이퍼로 전달할
            # 경로 자체가 없다(LIMIT_ROLE: AGENT). 기준점을 아는지와 무관하다.
            terms["asperity"] = 0.0
            f.notes.append(
                "asperity 밀도 0 — 접촉점이 없으면 하중 전달 경로가 없다. "
                "항을 0 으로 계상한다.")
        elif n_ref > 0:
            terms["asperity"] = (n_a / n_ref) ** 0.5
            srcs.append("knowledge/physics/gw-contact.md")
            f.notes.append("⚠ asperity 밀도 지수 0.5는 GW 접촉에서 실접촉면적이 "
                           "밀도의 제곱근에 가깝게 증가한다는 근사다 — 미검증.")

    if not terms:
        f.notes.insert(0, "⚠ κ 미모델링: 입자 함량·입경·패드 경도·asperity 밀도가 "
                          "전부 팩에 없다. 소모품을 바꿔도 결과가 안 변한다 "
                          "— 이것이 V1의 핵심 결함이었다.")
        return f

    val = 1.0
    for v in terms.values():
        val *= v
    f.value = val
    f.terms = terms
    # 네 항이 다 있어야 modeled. 하나라도 빠지면 partial.
    f.status = "modeled" if len(terms) >= 4 else "partial"
    # 등급 하한 판정 (2026-09-13) — 리터럴 "estimated" 를 걷어내고 실제 약한 고리를 읽는다.
    #   이 팩터의 가장 약한 고리는 드라이버가 아니라 **결합 지수**일 수 있다.
    #   그런데 그 지수들은 이미 팩에 등급과 함께 선언돼 있다 — 그러면 리터럴을 박을
    #   이유가 없다. 선언된 등급을 읽으면 문헌을 확보했을 때 등급이 실제로 오른다.
    #   (리터럴 하한은 문헌을 아무리 채워도 칸이 안 오르게 만들어 며칠을 정체시켰다)
    f.confidence = _worst_conf(
        _pack_conf(pk, "abrasive_wt_pct", "abrasive_size_nm",
                   "pad_hardness_shore_d", "asperity_density_per_m2"),
        _pack_conf(pk, "abrasive_conc_exponent", "abrasive_size_exponent",
                   "abrasive_size_exp_below_peak", "abrasive_size_exp_above_peak"))
    f.sources = sorted(set(srcs))
    if f.status == "partial":
        f.notes.append(f"⚠ 부분 모델링 — 반영된 항 {len(terms)}/4: "
                       f"{', '.join(terms)}")
    return f


def _ph_peak_term(pack, notes: List[str]) -> Optional[float]:
    """pH → MRR, **정점형(peaked)** 거동.

    왜 별도 항인가:
      chemistry.py의 `_ph_softening_term`은 경도비를 pH의 **단조 선형**으로 본다.
      그런데 실측은 정점형이다 — Li et al. 2021 (doi:10.1149/2162-8777/ac3e44, Fig.1,
      20 wt% 실리카·K⁺ 0.25 M·SiO₂ 막):

          pH 10.0 → 1551 Å/min
          pH 11.0 → 1727 Å/min   ← 정점
          pH 12.5 → 1407 Å/min

      메커니즘도 두 갈래다: pH↑는 Si-O-Si 가수분해로 표면을 연화시켜 MRR을 올리지만
      (10→11, +11.3%), 과잉 OH⁻는 입자·표면을 동시에 강한 음전하로 만들어 정전 반발이
      기계적 접촉을 막아 MRR을 떨어뜨린다(11→12.5, −18.5%).

      **단조 모델을 쓰면 pH 12.5를 과대평가한다.** 소재 개발자가 pH를 올려보는
      시뮬레이션에서 이건 틀린 방향을 가리키는 것이라 그냥 부정확한 정도가 아니다.

    형태: 정점에서 1차 미분이 0인 가장 단순한 형태로 2차 감쇠를 쓴다.
        f(pH) = 1 - a·(pH - pH_peak)²
      계수 a는 실측 두 점(10.0, 12.5)에서 비대칭이므로 양쪽을 따로 맞춘다.
      ⚠ 2차 형태 자체는 문헌이 제시한 게 아니라 3점을 지나는 최소 가정이다.
    """
    if not (pack.has("slurry_ph") and pack.has("ph_peak") and pack.has("ph_ref")):
        return None
    ph = float(pack.get("slurry_ph"))
    ph_pk = float(pack.get("ph_peak"))
    ph_ref = float(pack.get("ph_ref"))

    # 실측 3점에서 뽑은 양쪽 곡률. 팩이 덮어쓸 수 있게 열어둔다.
    # 좌: (11.0 - 10.0)=1.0 떨어질 때 1727→1551 = 0.898 ⟹ a_lo = 0.102
    # 우: (12.5 - 11.0)=1.5 떨어질 때 1727→1407 = 0.815 ⟹ a_hi = 0.185/2.25 = 0.0823
    a_lo = float(pack.get_or("ph_curvature_low", 0.102))
    a_hi = float(pack.get_or("ph_curvature_high", 0.0823))

    # ── 산성 영역(pH ≲ 6.0) 골(valley) 로그이차 가지 ─────────────────────
    # 2026-09-10 (오전) RESPONSE_DEAD 대응으로 멱함수(단조 감소, n=5, pH6.0 반등 제외)를
    # 넣었으나 tools/response_map.py 재판정 결과 RESPONSE_CONFLICT로 전환됐다 — 문헌
    # (cn109609035b n=7, pH2.0~6.0)은 **골**(pH~5 부근 최소 후 pH6.0 반등)인데 멱함수는
    # 단조 감소만 표현해 방향이 계속 달랐다. knowledge/cmp/silica-cmp-ph-acidic-repulsion-
    # choi-power-law.md §3(2026-09-10 저녁 갱신)에 따라 cn109609035b **7점 전체**(반등점
    # 포함)에 log(MRR) = a·pH² + b·pH + c 2차 회귀를 다시 적합했다 — 이 로그공간 2차식
    # 자체가 골(아래로 볼록) 형태를 갖는다. 피팅 구간(pH 2.0~6.0) **안에서만** 쓴다 —
    # 밖으로 나가면 급격히 발산해(pH 9 외삽 시 실측 대비 압도적 과대) 비물리적이므로,
    # 전환 경계 위(6.0~9.0, Choi 2004가 서술한 전환 pH)는 골 값(pH6.0)에서 염기 정점식
    # 값(pH9.0)까지 로그-선형 보간한다(데이터 없음 — 미검증 전이).
    ph_acid_max = float(pack.get_or("ph_acid_transition", 6.0))     # cn109609035b 데이터 상한
    ph_trans_hi = float(pack.get_or("ph_transition_upper", 9.0))    # Choi 2004 서술 전환점
    # cn109609035b 7점(pH2.0~6.0, 반등 포함) log(mrr)=a·pH²+b·pH+c 최소제곱 계수.
    # knowledge/cmp/silica-cmp-ph-acidic-repulsion-choi-power-law.md §3 verify 블록에서
    # 동일 계수를 재현·assert한다 — 여기 상수를 바꾸면 그 노트도 갱신해야 한다.
    ph_acid_a2 = float(pack.get_or("ph_acid_quad_a", 0.336472))
    ph_acid_b2 = float(pack.get_or("ph_acid_quad_b", -3.228411))
    ph_acid_c2 = float(pack.get_or("ph_acid_quad_c", 7.349046))

    def _quad(x: float) -> float:
        d = x - ph_pk
        a = a_lo if d < 0 else a_hi
        return max(1.0 - a * d * d, 0.05)   # 물리적으로 0 이하가 될 수 없다

    def _acid_raw(x: float) -> float:
        """cn109609035b 로그이차 골 피팅 — pH 2.0~6.0 보간 전용(외삽 금지, 호출측이 클램프)."""
        return math.exp(ph_acid_a2 * x * x + ph_acid_b2 * x + ph_acid_c2)

    def _rel(x: float) -> float:
        if x <= ph_acid_max:
            x_eff = max(x, 1.5)                         # 조사범위(pH≥2) 밖 발산 방지
            anchor = _quad(ph_acid_max)                  # 염기 정점식 경계값(6.0)
            ratio = _acid_raw(x_eff) / _acid_raw(ph_acid_max)   # 경계에서 1 → 연속
            return anchor * ratio
        if x <= ph_trans_hi:
            # 전이구간(6.0~9.0): 데이터 없음 — 로그-선형 보간(외삽 아님, 양끝 고정 보간)
            lo_v = max(_quad(ph_acid_max), 1e-6)
            hi_v = max(_quad(ph_trans_hi), 1e-6)
            t = (x - ph_acid_max) / (ph_trans_hi - ph_acid_max)
            return math.exp(math.log(lo_v) + t * (math.log(hi_v) - math.log(lo_v)))
        return _quad(x)

    cur, ref = _rel(ph), _rel(ph_ref)
    if ref <= 0:
        return None
    notes.append(
        f"pH {ph:g} (정점 {ph_pk:g}, 기준 {ph_ref:g}) → 상대 {cur/ref:.3f}. "
        "실측 3점(Li 2021 Fig.1) 기반 정점형(pH≳9.0), "
        f"산성(pH≤{ph_acid_max:g})은 골 형태 로그이차(cn109609035b n=7, 반등 포함 피팅). "
        "⚠ 염기 정점식은 3점을 지나는 최소 가정, 산성 골 로그이차는 n=7 피팅 — 둘 다 문헌 폐형식은 아니다. "
        f"⚠ {ph_acid_max:g}~{ph_trans_hi:g} 전환구간은 데이터 없어 로그-선형 보간(미검증 외삽).")
    if ph < ph_acid_max:
        notes.append(f"⚠ pH {ph:g}는 골 로그이차 보간 구간 — n=7(pH 2.0~6.0, 반등 포함) 피팅, "
                     "log-MSE 0.356, 개별점 최대 ±37%(pH5.0) 편차(원인 미상).")
    if ph_acid_max < ph < ph_trans_hi:
        notes.append(f"⚠ pH {ph:g}는 전환구간(데이터 없음) — 로그-선형 보간값이다.")
    if ph > 12.5 or ph < 10.0:
        notes.append(f"⚠ pH {ph:g}는 실측 범위(10.0~12.5) 밖이다 — 외삽이다.")
    return cur / ref


def _ph_ceria_electrostatic_term(pack, notes: List[str]) -> Optional[float]:
    """세리아 슬러리의 pH → MRR — **정전 인력 창(window)** 거동.

    실리카 슬러리의 pH 정점(11.0)과는 **메커니즘도, 방향도 다르다.**
    실리카 팩의 `_ph_peak_term`을 세리아에 상속시켜 쓰면 pH 10에서 최대라고
    예측하는데, 실측은 정반대다:

      Dandu 2009 (doi:10.1149/1.3230624, Fig.2a, SiO₂ / 0.25 wt% 세리아 60 nm / 4 psi):
          pH 2.0 →   4.3 nm/min
          pH 3.0 →  95.3
          pH 3.5 → 276.3
          pH 4.0 → 347.4  ┐
          pH 5.0 → 344.3  │ 플래토 (~350)
          pH 5.5 → 350.4  ┘
          pH 6.0 →  99.3  ← 급락
          pH 8.0 →  69.4
          pH 10  →  64.3

    물리 (knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4, verify PASS):
      표면전하 부호 = sign(IEP − pH). 세리아 IEP ≈ 6.8, 실리카 IEP ≈ 2.5.
      **두 IEP 사이(2.5 < pH < 6.8)에서만** 세리아(+)·실리카(−)가 반대부호라
      정전 인력이 입자를 웨이퍼로 끌어당겨 Si-O-Ce 결합을 촉진한다. 그 창 밖에서는
      같은 부호로 반발한다 → MRR 급락. pH 6 부근은 세리아 IEP에 근접해 제타≈0,
      응집까지 겹친다.

    구현: 창 안에서 플래토, 양 끝에서 IEP까지 시그모이드 감쇠. 창 밖 잔류값은
    실측(pH 8~10에서 정점의 ~19%)에서 뽑는다.
      ⚠ 시그모이드 폭·잔류율은 Dandu 한 편의 실측 3구간에서 역산한 값이다.
        형태 자체가 문헌 폐형식은 아니다 — 순위·창 위치는 물리(IEP)가 주고,
        기울기는 캘리브레이션 대상이다.

    ⚠⚠ 알려진 반례 — 숨기지 않는다 (2026-09-08 백테스트):
      Netzband & Dunn 2020 (doi:10.1149/2162-8777/ab8393, 열산화막, 1 wt% 세리아,
      2.25 cm² 벤치탑 쿠폰)은 pH 4→19.8, 6→11.3, 8→20.0, 10→21.3 nm/min으로
      **pH 10이 최고**다. 이 모델은 pH 10을 잔류 18%로 예측하므로 그 데이터셋에서
      ρ=−0.80이 나온다. 이 모델을 넣기 전 dandu2009는 ρ=−0.525였고 넣은 뒤
      +0.933이 됐다 — 한쪽을 맞추면 다른 쪽이 깨지는 **진짜 상충**이다.

      왜 다른가(가설, 미검증): Netzband의 전체 MRR 폭은 11~21(2배)인 반면 Dandu는
      4~350(80배)이다. Netzband는 쿠폰 실험이라 접촉 압력·슬러리 교체가 양산
      폴리셔와 다르고, 1 wt%는 0.25 wt%보다 입자가 4배 많아 정전 반발이 있어도
      기계 접촉이 유지될 수 있다. 즉 정전 창은 **저농도·양산 스케일에서 지배적**이고
      고농도·쿠폰에서는 부차적일 수 있다. 이걸 농도 의존 창 깊이로 넣으려면
      두 논문 사이를 잇는 중간 농도 데이터가 필요하다 — 지금은 없다.

      선택: 양산 스케일(사용자의 실제 사용 조건)을 맞추는 Dandu를 따른다.
      Netzband 조건(고농도·쿠폰)에서는 이 모델이 틀릴 수 있음을 notes로 신고한다.
    """
    if str(pack.get_or("abrasive", "")) != "ceria":
        return None
    if not (pack.has("slurry_ph") and pack.has("abrasive_iep_ph")):
        return None

    # ── 적용 범위 판정 ────────────────────────────────────────────────
    # 이 항의 물리는 "연마입자와 **웨이퍼 표면**이 반대 부호일 때 정전 인력이
    # 붙는다"이다. 즉 창의 두 경계는 입자 IEP 와 **그 막질의** IEP 다. 따라서
    # 막질이 바뀌면 창 자체가 다른 곳으로 옮겨간다 — 같은 곡선을 쓸 수 없다.
    #
    # 그런데 wafer_iep_ph 는 base 팩에서 상속되기 때문에, 막질을 바꾼 팩이
    # 자기 IEP 를 선언하지 않으면 **다른 막질의 IEP 로 계산된 창**이 조용히
    # 적용된다. 이때 나오는 숫자는 "이 막질의 pH 응답"이 아니라 남의 것이다.
    # 조용히 틀린 값을 내느니 항을 건너뛰고 그 사실을 신고한다.
    #
    # 판정: 막질을 선언한 팩은 그 막질의 IEP 도 **자기 팩에서** 선언해야 한다.
    #       (상속된 값은 어느 막질 것인지 알 수 없으므로 근거로 인정하지 않는다)
    film = str(pack.get_or("film", "") or "")
    if film and not pack.has_own("wafer_iep_ph"):
        notes.append(
            f"⚠ pH 창 항 건너뜀 — 막질 '{film}' 의 등전점(wafer_iep_ph)이 이 팩에 "
            "선언되지 않았다. 이 항의 창 경계는 입자 IEP 와 **막질 IEP** 로 정해지므로 "
            "상속된 IEP(다른 막질의 값)로 계산하면 창 위치가 틀린다. "
            "이 막질의 IEP 를 팩에 명시하면 항이 활성화된다. "
            "지금은 pH 효과가 Kp 에 뭉뚱그려진 상태 — pH 를 바꿔도 안 변한다.")
        return None

    ph = float(pack.get("slurry_ph"))
    iep_ceria = float(pack.get("abrasive_iep_ph"))            # ~6.8
    iep_wafer = float(pack.get_or("wafer_iep_ph", 2.5))       # 실리카 산화막
    ph_ref = float(pack.get_or("ph_ref", ph))

    # 실측 역산 파라미터 — 팩이 덮어쓸 수 있다.
    # ⚠ 창 밖 잔류값은 **양쪽이 다르다** — 물리가 다르기 때문이다:
    #   산성 쪽(pH<2.5): 둘 다 (+)이나 실리카는 IEP 직하라 거의 무전하 → 인력도
    #     반발도 약하고 세리아 자체가 용출 → 거의 0 (실측 1%).
    #   염기 쪽(pH>6.8): 둘 다 (−) 강반발이지만 Si-O-Ce chemical tooth는 살아 있어
    #     기계적 접촉만으로도 일부 제거 → ~18% 잔류.
    #   단일 잔류값으로는 이 둘을 동시에 못 맞춘다(격자탐색 log-err 5.3 vs 0.02).
    res_lo = float(pack.get_or("ph_window_residual_acid", 0.01))
    res_hi = float(pack.get_or("ph_window_residual_base", 0.18))
    k_lo = float(pack.get_or("ph_window_k_low", 5.0))
    k_hi = float(pack.get_or("ph_window_k_high", 10.0))
    mid_lo = float(pack.get_or("ph_window_mid_low", iep_wafer + 0.7))     # 3.2
    mid_hi = float(pack.get_or("ph_window_mid_high", iep_ceria - 1.0))    # 5.8

    def _win(x: float) -> float:
        lo = 1.0 / (1.0 + math.exp(-k_lo * (x - mid_lo)))
        hi = 1.0 / (1.0 + math.exp(k_hi * (x - mid_hi)))
        return res_lo * (1.0 - lo) + res_hi * (1.0 - hi) * lo + lo * hi

    cur, ref = _win(ph), _win(ph_ref)
    if ref <= 0:
        return None
    notes.append(
        f"세리아 정전 창: pH {ph:g} (창 {iep_wafer:g}~{iep_ceria:g}, 기준 {ph_ref:g}) "
        f"→ 상대 {cur/ref:.3f}. 창 안에서 세리아(+)·실리카(−) 인력, 밖에서 반발. "
        "⚠ 창 위치는 IEP 물리, 기울기·잔류율은 Dandu 2009 실측 역산 — 미검증.")
    if ph >= iep_ceria - 0.5:
        notes.append(f"⚠ pH {ph:g}는 세리아 IEP({iep_ceria:g}) 근접 — 제타≈0, "
                     "응집·스크래치 위험(Δ↑). 분산제 없이는 실무 부적합.")
    return cur / ref


def _ph_cu_acidic_term(pack, notes: List[str],
                       gated: Optional[Dict[str, str]] = None) -> Optional[float]:
    """pH → MRR, **금속 Cu 산성역**의 산화제 매개 로그선형 항.

    근거 노트: knowledge/cmp/cu-cmp-ph-mechanism.md
    1차 출처: US20080090500A1 (PPG Industries Ohio; Hellring·Li·Auger,
              우선일 2002-08-05) TABLE 4.

    왜 텅스텐 항을 빌려 쓰면 안 되는가 — 메커니즘이 다르다.
      W 는 금속 자신의 산화 반쪽반응이 H⁺ 를 포함해 Nernst 로 pH 가 직접 들어온다.
      Cu 는 다르다: Cu → Cu²⁺ + 2e⁻ 에 H⁺ 가 없어 dE/dpH = 0 이다
      (Pourbaix 에서 Cu²⁺/Cu 경계가 수평선). 따라서 pH 는 **산화제 쪽**으로만
      들어온다:
          H₂O₂ + 2H⁺ + 2e⁻ → 2H₂O,  dE/dpH = −59 mV
      즉 셀 전위의 pH 기울기는 전부 산화제에서 나온다. 산화제가 없으면
      이 경로 자체가 없다.

    형태: f(pH) = exp(−k·(pH − pH_ref)).
      함수형의 근거는 (a) 산화제 Nernst 가 pH 에 선형이고 (b) 속도가 전위에
      지수 반응(Tafel)한다는 표준 구조다.
      ⚠ 그러나 Tafel 로 k 를 **독립 유도하면** b ≈ 0.954 V/decade 가 나와
        전형값(0.06~0.12)의 약 10배로 어긋난다. 즉 **함수형은 물리이고
        계수 크기는 경험값**이다. 이 사실을 숨기지 않는다 —
        confidence 는 literature 이며 verified 가 아니다.

    k = 0.1428 /pH : 실리카 2/3/4 wt% 세 계열을 각자 pH 4 값으로 정규화한
      12점 pooled 최소자승. 계열별 k = 0.1360 / 0.1496 / 0.1427
      (R² = 0.968 / 0.999 / 0.956), 산포 ±4.8 %.
      pooled R² = 0.9537, 12점 최대 재현오차 7.26 %.
      검산: f(3)=1.1535, f(4)=1.0000, f(5)=0.8669, f(6)=0.7516.

    ⚠ 적용 게이트 — 팩이 `cu_ph_acid_k` 를 선언할 때만 켜진다. 깨지는 지점:
      · pH > 6  : 전체 곡선은 정점형이 아니라 **V자**다. pH 6~6.5 에서 최소이고
                  알칼리에서 재증가한다(Du & Desai 2003 DOI 10.1557/PROC-767-F6.6
                  '최소 pH 6'; Ilie & Ipate 2017 DOI 10.3390/lubricants5020015
                  '최소 pH 6.5'). 골을 넘으면 부호가 뒤집히므로 외삽 금지.
      · pH < 3  : 최저 관측점이 pH 3. 삼중점 pH 4.14 아래는 완전 용해영역.
      · 연마입자 < 2 wt% : 0 wt% 행이 비단조(259/106/176/151), 1 wt% 는 R²=0.594.
                  pH 는 부동태막 성질을 바꿀 뿐 **그 막을 벗길 기계력이 없으면**
                  MRR 로 번역되지 않는다. 항을 켜지 않는다.
      · BTA 없음 : k 가 2.33배(US9200180B2 TABLE 4, k=0.3329, R²=0.9971).
                  별도 레짐이다. 두 값을 평균내지 않았다 —
                  ⚠ BTA 유무와 pH 구간이 얽혀 어느 쪽이 주원인인지 이 데이터로
                    분리 불가(식별 불가로 기록).
      · 산화제 없음 : 대응쌍 미확보 → 미확인. 기본값 '적용 안 함'.
    """
    def _gate(reason: str) -> None:
        """이 pH 에서 **예측을 포기한다**는 선언을 구조화해 남긴다(판정#94).

        notes 에만 적으면 하류 도구는 '평평한 예측'과 '예측 없음'을 구분하지
        못한다 — 실제로 tools/response_map.py 가 그 둘을 섞어 없는 골짜기를
        만들고 CONFLICT(score 120)를 찍고 있었다.
        """
        if gated is not None:
            gated["slurry_ph"] = reason

    if not (pack.has("slurry_ph") and pack.has("cu_ph_acid_k")
            and pack.has("ph_ref")):
        return None

    # 기계 경로 게이트 — pH 는 막을 바꿀 뿐, 벗길 입자가 있어야 MRR 이 된다.
    #
    # ⚠ 이 게이트의 근거는 **산성 레짐 데이터**(US20080090500A1, 실리카 2/3/4 wt%)
    #   에서만 나왔다. 알칼리 레짐의 계수를 준 US9200180B2 TABLE 4 는 실리카
    #   10 wt% 단일 농도라 저농도에서 pH 항이 성립하는지 **관측이 없다**.
    #   그래서 여기서 하는 일은 "저농도에서 pH 효과가 없다"는 주장이 아니라
    #   "저농도는 어느 레짐에서도 검증되지 않았다"는 **범위 선언**이다.
    #
    # ⚠ 이 경계에서 예측이 불연속으로 뛴다(실측: 1.5 wt% 39.6 → 2.0 wt% 13.4,
    #   3배 절벽). 물리적 절벽이 아니라 항이 켜지고 꺼지는 데서 오는 인공물이므로,
    #   경계 아래 조건은 **예측값을 쓰지 말고 범위 밖으로 처리**해야 한다
    #   (이상치 규칙 C2 — 모델이 선언한 게이트 밖). 검증 집계에 넣으면 모델이
    #   아니라 게이트를 채점하게 된다.
    #
    # ⚠ 이 절벽을 없애려고 게이트를 넓히지 마라. 그것은 물리를 버리고 데이터를
    #   삼키는 일이다. 저농도를 예측하려면 그 영역의 항을 새로 유도해야 하고,
    #   그 전까지는 범위 밖으로 남기는 것이 정직하다.
    if pack.has("abrasive_wt_pct"):
        try:
            wt = float(pack.get("abrasive_wt_pct"))
        except (TypeError, ValueError):
            wt = None
        if wt is not None and wt < 2.0:
            _gate(f"연마입자 {wt:g} wt% < 2 wt% — pH 가 바꾼 막을 벗길 "
                  "기계 경로가 근거 표에서 검증되지 않았다(범위 선언).")
            notes.append(
                f"Cu 산성역 pH 항 미적용: 연마입자 {wt:g} wt% < 2 wt%. "
                "근거 표에서 저농도 행은 비단조(0 wt%)이거나 설명력이 낮다"
                "(1 wt%, R²=0.594) — pH 가 바꾼 막을 벗길 기계 경로가 부족하다.")
            return None

    ph = float(pack.get("slurry_ph"))
    ph_ref = float(pack.get("ph_ref"))

    # ── 레짐 좌표 판정 (2026-09-15) ────────────────────────────
    # k 가 계열마다 2.33배 갈리는데, 얽힌 두 축(pH 구간 × 억제제 유무)을
    # 데이터로 분리할 수 없다(대각선 2칸만 관측). 그래서 **평균내지 않고**
    # 레짐 좌표로 둔다 — 각 레짐이 자기 데이터에서만 계수를 갖는다.
    #
    #   레짐 1 (산성 · 억제제 유) k=0.1428  US20080090500A1 T4, 12점 R²=0.954
    #   레짐 2 (알칼리 · 억제제 무) k=0.3329  US9200180B2 T4,     5점 R²=0.997
    #   레짐 3 (산성 · 억제제 무)  관측 없음 → **항을 켜지 않는다**
    #   레짐 4 (알칼리 · 억제제 유) 관측 없음 → **항을 켜지 않는다**
    #
    # ⚠ 빈 레짐에 이웃 계수를 넣지 않는다. 그 순간 두 효과가 한 계수에
    #   뭉쳐 그 데이터셋의 지문이 되고, 겉보기 성능은 오히려 좋아져서
    #   들키지 않는다. 관측이 없으면 **신고하고 비활성화**한다.
    #
    # ⚠ 자유도를 늘리지 않는다: 계수 2개는 각각 12점·5점에서 나왔고,
    #   레짐 판정은 데이터가 아니라 **조건**(골 위치, 억제제 선언)이 한다.
    #
    # 부등식 근거(R2, tools/route_cu_alkaline.py): pH 는 산화제 경로(A)와
    # 부동태 경로(B)로 들어오는데, 억제제가 이미 표면을 덮고 있으면 B 의
    # 한계효과가 작아진다 → k(억제제 무) > k(억제제 유). 관측이 이와 모순되지
    # 않는다(0.3329 > 0.1428). 다만 이는 **부호만** 확정할 뿐 원인 분리는 아니다.
    VALLEY_PH = 6.25          # 골 위치: 문헌 두 값(6.0, 6.5)의 중간
    alkaline = ph > VALLEY_PH
    has_inhibitor = False
    if pack.has("inhibitor_mM"):
        try:
            has_inhibitor = float(pack.get("inhibitor_mM")) > 0.0
        except (TypeError, ValueError):
            has_inhibitor = False

    if alkaline and not has_inhibitor:
        if not pack.has("cu_ph_alkaline_k"):
            _gate(f"pH {ph:g} 알칼리 × 억제제 없음 레짐인데 팩에 "
                  "`cu_ph_alkaline_k` 가 없다 — 산성역 계수를 빌리면 부호가 반대라 "
                  "예측하지 않는다.")
            notes.append(
                f"⚠ pH {ph:g}는 알칼리 가지(골 {VALLEY_PH} 초과)이고 억제제가 "
                "없는 레짐인데 `cu_ph_alkaline_k`가 팩에 없다 — 항을 켜지 "
                "않는다. 산성역 계수를 빌려 쓰면 부호가 반대다.")
            return None
        k = float(pack.get("cu_ph_alkaline_k"))
        k_ref = float(pack.get_or("cu_ph_alkaline_ref", VALLEY_PH))
        val = math.exp(-k * (ph - k_ref))
        notes.append(
            f"Cu 알칼리역 pH: pH {ph:g} (기준 {k_ref:g}) → 상대 {val:.3f}. "
            f"k={k:g}/pH — US9200180B2 TABLE 4 Ex.15~19, 5점 R²=0.9971. "
            "레짐: 알칼리 × 억제제 없음. ⚠ 이 계열은 V자의 재상승을 보이지 "
            "않고 pH 9.9 까지 단조 감소한다 — 조성마다 재상승 지점이 다르다.")
        return val

    if alkaline and has_inhibitor:
        _gate(f"pH {ph:g} 알칼리 × 억제제 존재 레짐은 **관측이 없다** — "
              "어느 계수도 이 조건에서 검증된 적이 없어 예측하지 않는다. "
              "필요 데이터: 같은 조성에서 억제제 농도 2수준 × 골 양쪽 pH 3점 이상 "
              "제거율 표.")
        notes.append(
            f"⚠ pH {ph:g} 알칼리 + 억제제 존재 레짐은 **관측이 없다**. "
            "산성역 계수(k=0.1428)도 억제제 없는 알칼리 계수(k=0.3329)도 "
            "이 조건에서 검증된 적이 없으므로 항을 켜지 않는다. "
            "이 레짐을 채우려면: 같은 조성에서 억제제 농도를 두 수준으로 두고 "
            "pH 를 골 양쪽으로 3점 이상 스윕한 제거율 표가 필요하다(R8).")
        return None

    if not alkaline and not has_inhibitor:
        _gate(f"pH {ph:g} 산성 × 억제제 없음 레짐은 **관측이 없다** — "
              "산성역 계수는 억제제가 있는 계열(BTA 1 mM)에서 나왔다.")
        notes.append(
            f"⚠ pH {ph:g} 산성 + 억제제 없음 레짐은 **관측이 없다**. "
            "산성역 계수는 억제제가 있는 계열(BTA 1 mM)에서 나왔다. "
            "항을 켜지 않는다 — 억제제 유무는 pH 민감도를 바꾼다(R2 부등식).")
        return None

    # 레짐 1 — 산성 × 억제제 유 (원 관측)
    k = float(pack.get("cu_ph_acid_k"))
    val = math.exp(-k * (ph - ph_ref))
    notes.append(
        f"Cu 산성역 pH: pH {ph:g} (기준 {ph_ref:g}) → 상대 {val:.3f}. "
        f"산화제(H₂O₂) 환원 전위 경로 — dE/dpH=−59 mV, k={k:g}/pH "
        "(US20080090500A1 TABLE 4, 3계열 12점 pooled, R²=0.954, 산포 ±4.8%). "
        "레짐: 산성 × 억제제 존재. "
        "⚠ 함수형은 물리(Nernst+Tafel)이나 계수 크기는 경험값 — "
        "Tafel 독립 유도 시 b≈0.954 V/dec 로 전형값의 10배라 어긋난다.")
    if not (3.0 <= ph <= 6.0):
        notes.append(
            f"⚠ pH {ph:g}는 근거 구간(3~6) 밖이다 — 외삽이다. "
            "Cu 의 pH-MRR 은 V자이고 pH 6~6.5 에서 골을 지나 알칼리에서 "
            "재증가하므로, 골 너머는 **부호가 반대**라 특히 신뢰할 수 없다.")
    return val


def _ph_w_acidic_term(pack, notes: List[str]) -> Optional[float]:
    """pH → MRR, **금속 W 산성역**의 산화제 매개 로그선형 항.

    근거 노트: knowledge/cmp/w-cmp-ph-acidic-oxidizer-mediated-stojadinovic.md
    1차 출처: Stojadinović, Bouvet, Mischler (2016), J. Bio- Tribo-Corros. 2:8,
              doi:10.1007/s40735-016-0041-4, Table 1.

    왜 별도 항인가 — 실리카 산화막의 `_ph_peak_term`(정점형)이나 세리아의 IEP 창을
    금속 W 에 빌려 쓰면 메커니즘이 달라 부호까지 틀린다. W 에서 pH 는 표면 연화도
    정전 상호작용도 아니고 **산화(WO₃ 생성) 구동력**을 통해 들어온다:
        W + 3H₂O → WO₃ + 6H⁺ + 6e⁻,  E_rev = −0.119 − 0.059·pH
    pH 5→2 에서 구동 전위가 177 mV 커지고(논문 서술 180 mV), 그만큼 MRR 이 오른다.

    형태: f(pH) = exp(−k·(pH − pH_ref)).  Nernst 로 구동력이 pH 에 선형이고
    속도가 구동력에 지수적(Tafel)이라는 표준 구조를 따른 것이지 임의 곡선맞춤이 아니다.
    k = 0.1163 /pH 는 Table 1 의 산화제 존재 3조건 비(1.429/1.533/1.300)를 로그평균해
    Δ pH = 3 으로 나눈 값이다. 이 k 로 되돌린 예측 오차는 −0.8 % / −7.6 % / +9.0 %.

    ⚠ 적용 게이트 — 팩이 `w_ph_acid_k` 를 선언할 때만 켜진다. **산화제가 없는 W 계는
    부호가 반대다**(Table 1 0 % KIO₃: pH5 40 → pH2 25 Å/min, 비 0.625). 산화제 없는
    레짐에 이 항을 적용하면 방향이 틀린다 — 그 레짐은 의도적으로 스코프 밖이다.
    ⚠ 알칼리역(pH>7)은 용해 지배로 부호가 또 반대다(Xu 2022, doi:10.3390/mi13050762,
    pH 7→12 에서 6.69→13.67 µm/h 증가) — 미모델링. 실무 W 슬러리는 산성이다.
    ⚠ 2점 할선(pH 2, 5)이므로 그 밖은 외삽이다 — 벗어나면 notes 에 경고를 남긴다.
    """
    if not (pack.has("slurry_ph") and pack.has("w_ph_acid_k") and pack.has("ph_ref")):
        return None
    ph = float(pack.get("slurry_ph"))
    ph_ref = float(pack.get("ph_ref"))
    k = float(pack.get("w_ph_acid_k"))
    val = math.exp(-k * (ph - ph_ref))
    notes.append(
        f"W 산성역 pH: pH {ph:g} (기준 {ph_ref:g}) → 상대 {val:.3f}. "
        f"산화(WO₃) 구동력 경로 — Nernst dE/dpH=−59 mV, k={k:g}/pH "
        "(Stojadinović 2016 Table 1, 산화제 존재 3조건 로그평균). "
        "⚠ 개별 조건 재현오차 −0.8~+9.0 %, k 산포 ±22 % — 지수형 가정은 미검증.")
    if not (2.0 <= ph <= 5.0):
        notes.append(f"⚠ pH {ph:g}는 근거 구간(2~5) 밖이다 — 외삽이다. "
                     "pH>7 은 용해 지배로 부호가 반대라 특히 신뢰할 수 없다.")
    return val


def _ph_sic_kmno4_acidic_term(pack, notes: List[str]) -> Optional[float]:
    """pH → MRR, **SiC × 산성 KMnO4** 계의 산화력 감쇠 + 기계 하한 항.

    근거 노트: knowledge/cmp/sic-kmno4-acidic-ph-decay-chen2020.md
    1차 출처: Chen G., Du C., Ni Z., Liu Y., Zhao Y. (2020),
              Russ. J. Appl. Chem. 93(6) 832-837, doi:10.1134/S1070427220060099, Fig. 1(a).
              (2 wt% Al2O3 나노입자 + 0.05 M KMnO4, 6H-SiC Si면, 4 psi, 90/90 rpm)

    왜 별도 항인가 — 이 계에서 pH 는 세리아 IEP 창(정전 상호작용)도 실리카 정점형도
    아니고 **MnO4- 의 산화력**을 통해 들어온다. 산성에서 MnO4- + 4H+ + 3e- → MnO2 +
    2H2O 의 전위가 Nernst 로 pH 와 함께 떨어지므로 MRR 이 pH 증가와 함께 감소한다.
    Chen 2020 Fig.1 은 pH 2→10 에서 Si 면·C 면 모두 **단조 감소**를 보인다 — 알칼리
    쪽에서 오히려 오르는 실리카/세리아 계와 부호가 반대다.

    형태: f(pH) = g(pH)/g(pH_ref),  g(pH) = φ + (1-φ)·exp(-k·(pH - pH_anchor)).
    φ 는 **화학이 꺼져도 남는 기계 경로**(연마입자 압흔)다 — 산화력이 떨어져도 MRR 이
    0 으로 가지 않고 평탄해지는 관측(pH 6~10 에서 거의 수평)을 담는다. 단순 지수만
    쓰면 pH 10 을 3 배 넘게 과소예측한다.
    기준점 나눗셈 덕에 pH = pH_ref 에서 항상 1.0 이다(Kp 이중 계상 방지).

    ⚠ 적용 게이트 — 팩이 `sic_kmno4_ph_acid_k` 를 **직접 선언**할 때만 켜진다.
    ⚠ 근거 구간은 pH 2~10 이다. 그 밖은 외삽이며 notes 에 경고를 남긴다.
    ⚠ 계수는 그래프 판독(digitized)에서 나왔다 — 눈금 간격 역산으로 인쇄 최대값
      1554 nm/h 를 -0.6 % 로 재현했지만 개별 막대는 판독오차를 갖는다.
    """
    if not (pack.has("slurry_ph") and pack.has("sic_kmno4_ph_acid_k")
            and pack.has("ph_ref")):
        return None
    ph = float(pack.get("slurry_ph"))
    ph_ref = float(pack.get("ph_ref"))
    k = float(pack.get("sic_kmno4_ph_acid_k"))
    anchor = float(pack.get_or("sic_kmno4_ph_anchor", 2.0))
    floor = float(pack.get_or("sic_kmno4_ph_floor", 0.0))

    # ── 산화제 농도에 따른 기계 하한 φ 보간 (판정#64, 2026-09-18)
    # φ 는 "산화력이 꺼져도 남는 removal" 이다. 산화제가 진해지면 알칼리 쪽에서도
    # 산화가 완전히 꺼지지 않아 관측되는 평탄부가 **위로 올라간다**. 두 실측 앵커:
    #   · Chen 2020(0.05 M ≈ 0.79 wt% KMnO4, 6H Si면): pH2→10 3.56배 감소 → φ=0.268
    #   · Wang 2021(6.5 wt% KMnO4, 4H Si면): pH2 1.4 → pH12 1.1 µm/h → φ=0.785
    # 두 앵커를 log(농도)로 선형보간한다. 앵커 4개가 전부 선언될 때만 켜지고,
    # 아니면 위의 정적 floor 를 그대로 쓴다(하위호환).
    # ⚠ 앵커가 2점뿐이라 형상은 미검증 — 보간값 자체는 estimated 다.
    _fl_note = ""
    _anc = ("sic_kmno4_ph_floor_lo_wt", "sic_kmno4_ph_floor_lo",
            "sic_kmno4_ph_floor_hi_wt", "sic_kmno4_ph_floor_hi")
    if all(pack.has(a) for a in _anc) and pack.has("oxidizer_wt_pct"):
        c_lo = float(pack.get("sic_kmno4_ph_floor_lo_wt"))
        f_lo = float(pack.get("sic_kmno4_ph_floor_lo"))
        c_hi = float(pack.get("sic_kmno4_ph_floor_hi_wt"))
        f_hi = float(pack.get("sic_kmno4_ph_floor_hi"))
        c = float(pack.get("oxidizer_wt_pct"))
        if c_lo > 0 and c_hi > 0 and c > 0 and c_hi != c_lo:
            t = (math.log(c) - math.log(c_lo)) / (math.log(c_hi) - math.log(c_lo))
            t_cl = min(max(t, 0.0), 1.0)          # 앵커 밖은 외삽하지 않고 고정
            floor = f_lo + t_cl * (f_hi - f_lo)
            _fl_note = (f" φ 는 산화제 {c:g} wt% 에서 앵커 보간값 "
                        f"({c_lo:g}→{f_lo:g}, {c_hi:g}→{f_hi:g} wt%, log 선형)")
            if not (0.0 <= t <= 1.0):
                _fl_note += " ⚠ 앵커 구간 밖이라 끝값으로 고정"
    floor = min(max(floor, 0.0), 1.0)

    def g(x: float) -> float:
        return floor + (1.0 - floor) * math.exp(-k * (x - anchor))

    ref = g(ph_ref)
    if ref <= 0:
        return None
    val = g(ph) / ref
    notes.append(
        f"SiC×산성 KMnO4 pH: pH {ph:g} (기준 {ph_ref:g}) → 상대 {val:.3f}. "
        f"MnO4- 산화력 감쇠 경로 — k={k:g}/pH, 기계 하한 φ={floor:g} "
        "(Chen 2020 doi:10.1134/S1070427220060099 Fig.1a 판독 5점 적합, "
        "재현오차 -2.4~+2.6 %)." + _fl_note +
        " ⚠ k 는 그래프 판독 기반이라 estimated.")
    if not (2.0 <= ph <= 10.0):
        notes.append(f"⚠ pH {ph:g}는 근거 구간(2~10) 밖이다 — 외삽이다.")
    return val


def _f_chi(rr: "ResolvedRecipe") -> Factor:
    """χ 화학 반응성 — 표면 연화·산화가 만드는 MRR 배수.

    기존 sim/chemistry.py를 승계하되, pH는 **정점형 항으로 교체**한다
    (단조 연화항은 pH 11 위를 과대평가한다 — `_ph_peak_term` docstring 참조).
    억제 항은 여기가 아니라 ψ가 가져간다 — 방향이 반대이고, 사용자가
    "함량 변화에 따른 성능 변화"를 볼 때 촉진과 억제를 분리해 봐야 한다.

    pH 항 선택 원칙 — **has_own 우선** (EVIDENCE-RULES.md 판정#34,
    validation/C4-SIC-PACK-DIAGNOSIS.md §2.3·§2.4에서 진단):
      "팩이 어떤 pH 메커니즘의 계수를 **직접 선언**(`has_own`)했다면, 상속만
      받은 다른 메커니즘보다 우선한다." 자기 재료계에서 역산한 계수가 남의
      재료계에서 물려받은 계수보다 그 재료를 잘 기술하기 때문이다. 아래
      `candidates`를 1차 패스에서 own 계수 기준으로 훑고, 아무도 own이
      아니면(=지금까지의 4팩이 전부 여기 해당) 2차 패스에서 기존 우선순위
      (세리아 IEP 창 → W 산성역 → 실리카 정점 → 연화 폴백)로 그대로
      떨어진다 — 그래서 기존 4팩의 분기 선택은 이 변경으로 바뀌지 않는다.
      (sic_ceria_h2o2는 세리아 IEP 창의 `abrasive_iep_ph`를 sti_ceria에서
      상속만 받았을 뿐 직접 선언한 적이 없는데, 이 분기가 최우선이라 자기
      이름으로 직접 역산해 선언한 `ph_softening_per_unit`이 가려지고 있었다.)

    2차 패스(own이 아무도 없을 때) 추가 규칙 — **소유 조상의 연마입자 검사**
    (EVIDENCE-RULES.md 판정#59): 아무도 own이 아니면 기존 우선순위로 처음
    적용 가능한 후보를 쓰지만, 그 전에 "이 고유 계수를 실제로 선언한 조상
    팩의 `abrasive`가 이 팩의 `abrasive`와 다른가"를 확인한다. 다르면 후보를
    건너뛴다 — 안 그러면 "own은 아무도 없지만 상속된 계수가 남의 재료
    곡선"인 경우를 그대로 적용하게 된다(sic_alumina_kmno4가 abrasive를
    alumina로 자기선언한 뒤에도 폴백이 오이드_silica 소유 ph_peak(정점 pH=11,
    실리카 전용)로 떨어져 산성 알루미나/KMnO4계에 실리카 곡선을 씌우던 사고가
    실측으로 확인됐다). own 계수는 이 검사를 항상 통과한다(자기 재료가 자기
    계수를 쓴 것이므로 불일치가 있을 수 없다) — 그래서 5팩(cu_h2o2_bta·
    oxide_silica·sic_ceria_h2o2·sti_ceria·w_fe_oxidizer)은 전부 1차 패스에서
    이미 선택이 끝나 이 검사에 닿지 않고, 분기 선택은 바뀌지 않는다. 모든
    후보가 재료 불일치로 막히면 pH 항 없이(terms에서 빠진 채) notes에 왜
    막혔는지 남긴다 — 조용히 다른 재료 곡선으로 떨어지지 않는다.
    """
    from sim.params import load_pack
    from sim.chemistry import (_oxidizer_term, _ceria_term, _ph_softening_term,
                               _carboxylate_promoter_term)
    f = _new("chi")
    pk = rr.pack
    notes: List[str] = []
    terms: Dict[str, float] = {}

    # pH 항 후보 — **재료계별로 다르다.** 메커니즘이 다른 재료에 같은 항을 쓰면
    # 부호까지 틀린다(실리카 IEP 2.5 vs 세리아 6.8 → 정전 상호작용이 반대 방향).
    #   세리아: IEP 창 모델 (Dandu 2009)
    #   W 산성역: 산화 구동력 경로 (Stojadinović 2016)
    #   실리카: 정점형 (Li 2021), 없으면 단조 연화 폴백
    # 각 튜플은 (분기명, 항함수, 이 팩에서 적용 가능한가, 이 메커니즘을
    # 식별하는 "고유 계수" 키) — 마지막 항목(has_own 여부 판정용)은 팩이
    # 실제로 그 재료계에서 역산해 선언하는 계수이지, ph_ref처럼 여러
    # 메커니즘이 공유하는 기준점이 아니다.
    is_ceria = str(pk.get_or("abrasive", "")) == "ceria"
    candidates = [
        ("ph_ceria_window", _ph_ceria_electrostatic_term,
         is_ceria and pk.has("abrasive_iep_ph"), "abrasive_iep_ph"),
        ("ph_w_acidic", _ph_w_acidic_term,
         pk.has("w_ph_acid_k"), "w_ph_acid_k"),
        ("ph_cu_acidic", _ph_cu_acidic_term,
         pk.has("cu_ph_acid_k"), "cu_ph_acid_k"),
        ("ph_sic_kmno4_acidic", _ph_sic_kmno4_acidic_term,
         pk.has("sic_kmno4_ph_acid_k"), "sic_kmno4_ph_acid_k"),
        ("ph_peak", _ph_peak_term,
         pk.has("ph_peak") and pk.has("ph_ref"), "ph_peak"),
        ("ph_softening", _ph_softening_term,
         pk.has("ph_softening_per_unit") and pk.has("ph_softening_ref"),
         "ph_softening_per_unit"),
    ]
    chosen = None
    # 1차 패스: 적용 가능하고, 그 메커니즘의 고유 계수를 팩이 **직접
    # 선언**(has_own)한 첫 후보를 고른다(우선순위는 후보 나열 순서 그대로).
    for name, fn, applicable, own_key in candidates:
        if applicable and pk.has_own(own_key):
            chosen = (name, fn)
            break
    if chosen is None:
        # 2차 패스: own이 아무도 없으면(상속값만 있거나 아예 없으면) 원래
        # 우선순위로 처음 "적용 가능하고 + 소유 조상의 연마입자가 이 팩과
        # 같은" 후보를 쓴다(판정#59, 위 docstring 참조). own_key는 매
        # candidates 항목의 applicable 조건에 이미 포함돼 있으므로 여기서
        # applicable=True면 pk.has(own_key)도 항상 True다.
        for name, fn, applicable, own_key in candidates:
            if not applicable:
                continue
            if pk.has_own(own_key):
                chosen = (name, fn)
                break
            owner_name = pk.param(own_key).owner
            owner_abrasive = None
            if owner_name != pk.name:
                try:
                    owner_abrasive = load_pack(owner_name).get_or("abrasive", None)
                except Exception:
                    owner_abrasive = None
            this_abrasive = pk.get_or("abrasive", None)
            if owner_abrasive and this_abrasive and owner_abrasive != this_abrasive:
                notes.append(
                    f"⚠ pH 분기 '{name}'의 고유 계수 '{own_key}'는 {owner_name} 팩"
                    f"(연마입자={owner_abrasive})이 소유한 상속값인데 이 팩의 연마"
                    f"입자는 {this_abrasive}다 — 재료가 달라 이 분기를 쓰지 않는다"
                    f"(판정#59).")
                continue
            chosen = (name, fn)
            break
    ph_terms = [chosen] if chosen is not None else []
    if chosen is None:
        notes.append(
            "⚠ pH 항 미모델링: 상속된 pH 메커니즘 후보가 전부 다른 연마입자가 "
            "소유한 계수라 재료 불일치로 막혔다 — 이 팩 고유의 pH 계수가 "
            "확보될 때까지 갭으로 남긴다(판정#59).")

    # 항이 스스로 "이 조건은 관측이 없어 예측하지 않는다"고 신고하면(gated)
    # 그 선언을 Factor 에 그대로 실어 보낸다 — 하류 도구가 '평평한 예측'과
    # '예측 없음'을 구분할 수 있어야 한다(판정#94).
    gate_decl: Dict[str, str] = {}
    for name, fn in ([("oxidizer", _oxidizer_term),
                      ("ceria_tooth", _ceria_term),
                      ("carboxylate_promoter", _carboxylate_promoter_term)]
                     + ph_terms):
        # try/except TypeError 를 쓰지 않는다 — 항 **내부**에서 난 TypeError 까지
        # 삼켜 조용히 재실행하게 된다. 시그니처를 보고 고른다.
        if "gated" in inspect.signature(fn).parameters:
            v = fn(pk, notes, gate_decl)
        else:
            v = fn(pk, notes)
        if v is not None:
            terms[name] = v
    f.gated.update(gate_decl)
    for k in ("oxidizer_wt_pct", "slurry_ph", "ce3_fraction",
              "booster_mM", "chelator_mM", "promoter_M"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    if "oxidizer" not in terms and (pk.has("oxidizer_wt_pct")
                                     or pk.has("oxidizer_ref_wt_pct")) and not any(
            pk.has(k) for k in ("oxidizer_langmuir_K", "oxidizer_passivation_K",
                                "oxidizer_peak_wt_pct")):
        notes.append(
            "⚠ 산화제 농도(oxidizer_wt_pct/oxidizer_ref_wt_pct)가 팩에 선언돼 "
            "있으나 형상 파라미터(oxidizer_langmuir_K/oxidizer_passivation_K/"
            "oxidizer_peak_wt_pct)가 하나도 없어 χ가 산화제 변화에 조용히 "
            "반응하지 않는다 — 이번 회차는 이 누락을 경고만 하고 모델링하지 "
            "않는다(값·status·confidence 불변, validation/C4-SIC-PACK-"
            "DIAGNOSIS.md §2.2).")
    if not terms:
        f.notes.append("⚠ χ 미모델링: 산화제·pH·세리아 파라미터가 팩에 없다. "
                       "화학 효과는 Kp에 뭉뚱그려진 상태 — 조성을 바꿔도 안 변한다.")
        f.notes.extend(notes)
        return f
    val = 1.0
    for v in terms.values():
        val *= v
    f.value = val
    f.terms = terms
    f.status = "modeled" if len(terms) >= 2 else "partial"
    # 등급 하한 판정 (2026-09-13): κ 와 같은 규칙 — 화학 항의 형상 파라미터도
    # 팩에 등급과 함께 선언돼 있으므로 리터럴 대신 그것을 읽는다.
    # 산화제 형상 파라미터 등급 소스 — 팩이 Langmuir 경로(oxidizer_langmuir_K
    # 촉진형 또는 oxidizer_passivation_K 억제형, 판정#20)를 쓰면 그 키에서
    # 등급을 읽는다. 레거시 (n, C_peak)는 판정#19로 비활성화됐으므로 Langmuir
    # 경로를 쓰는 팩에서는 등급 계산에서 제외한다(안 그러면 비활성 키의
    # estimated 등급이 계속 발목을 잡는다). 둘 다 없는 팩은
    # 기존 그대로 (n, C_peak)를 읽는다 — 하위호환, 동작 불변.
    # 2026-09-16 보강: **실제로 켜진 항의 등급만** 읽는다. 산화제 항이 꺼져 있는데
    # (종 게이트로 차단됐거나 형상 파라미터가 비어) 그 키의 등급을 등급 하한에
    # 반영하면, 쓰지도 않는 상수 때문에 χ 전체가 강등된다 — 실제로
    # sic_alumina_kmno4 가 부모의 H2O2 K(estimated)를 상속만 하고 쓰지는 않는데
    # χ 가 estimated 로 떨어졌다. 등급은 계산에 들어간 값의 성질이어야 한다.
    if "oxidizer" not in terms:
        oxidizer_shape_keys = ()
    elif pk.has("oxidizer_langmuir_K"):
        oxidizer_shape_keys = ("oxidizer_langmuir_K",)
    elif pk.has("oxidizer_passivation_K"):
        oxidizer_shape_keys = ("oxidizer_passivation_K",)
    else:
        oxidizer_shape_keys = ("oxidizer_curve_n", "oxidizer_peak_wt_pct")
    # 촉진 항도 실제로 켜졌을 때만 등급 하한에 넣는다(산화제 키와 같은 규칙,
    # 2026-09-16 보강 참조) — 종 게이트로 꺼진 팩에서 남의 상수가 χ를 강등하면
    # 계산에 안 들어간 값이 등급을 정하는 것이 된다.
    promoter_shape_keys = (("promoter_exponent_m", "promoter_floor_phi", "promoter_M")
                           if "carboxylate_promoter" in terms else ())
    f.confidence = _worst_conf(
        _pack_conf(pk, "oxidizer_wt_pct", "slurry_ph", "ce3_fraction"),
        _pack_conf(pk, *oxidizer_shape_keys, *promoter_shape_keys, "ph_peak",
                   "ceria_tooth_gain", "w_ph_acid_k", "sic_kmno4_ph_acid_k"))
    f.sources = ["knowledge/cmp/ceria-slurry-ce-redox-selectivity.md",
                 "knowledge/cmp/particle-wafer-interaction-"
                 "mechanical-chemical-balance.md"]
    f.notes.extend(notes)
    if len(terms) > 1:
        f.notes.append("⚠ 화학 항들을 독립으로 보고 곱했다 — pH-흡착, 산화제-세리아 "
                       "산화환원 커플링은 미모델링.")
    if not pk.has("booster_mM"):
        f.notes.append("⚠ R/R booster(glycine 등)가 팩에 없다 — 막질별 선택비를 만드는 "
                       "주요 축인데 통로가 없다. 담당 R2-slurry.")
    return f


def _f_psi(rr: "ResolvedRecipe") -> Factor:
    """ψ 표면 보호도 — 표면 흡착 보호(adsorption shield)가 만드는 제거 억제 배수 (≤1).

    χ와 분리한 이유: 사용자가 배합을 조정할 때 "촉진을 올릴까 억제를 낮출까"는
    서로 다른 결정이다. 하나의 화학 배수로 뭉치면 그 판단이 사라진다.
    디싱/에로전은 이 항이 지배한다.

    ψ 정의 (2026-09-14 확장, COMPLETION.md "축별 완성 경로"): "금속 부동태"가 아니라
    **표면 흡착 보호** — 어떤 화학종이 (막 또는 입자) 표면에 흡착해 연마입자의 접근이나
    표면 반응을 막는 모든 경로. 세 갈래를 같은 형식으로 다룬다:

    ① 금속계 부식억제제 (Cu-BTA, W-피콜린산): `inhibitor_mM` + Langmuir K →
       `chemistry._inhibitor_term` (기존 그대로, 이 함수의 앞 절반. 변경 없음).
    ② 산화막/세리아계 **첨가제 농도축** — 이번 확장의 본체.
       근거 노트: knowledge/cmp/psi-adsorption-shield-oxide-systems.md,
                 knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md
         θ(C) = (K·C)^n / (1 + (K·C)^n)             협동(Hill) 흡착 피복률; n=1이면 Langmuir
         ψ    = exp(−k·[θ(C) − θ(C_ref)])            기준농도 정규화 → C=C_ref에서 항등적 1.0
       파라미터(팩, 첨가제×막질 쌍 고유 → `has_own` 자기선언일 때만 활성):
         shield_additive_wt_pct (드라이버), shield_ref_wt_pct, shield_langmuir_K,
         shield_hill_n, shield_strength_k [+ shield_nitride_* 는 STI 선택비 진단용]
       문헌 역산:
         · sti_ceria — Park et al. 2003 JJAP 42, 5420 (doi:10.1143/jjap.42.5420) Fig.3
           세리아 1 wt% + 음이온 계면활성제 0~0.8 wt% 9점: SiO₂ K=1.295/wt%, n=4.62, k=3.0
           (0.8 wt%에서 산화막 RR 1/5 = 원문 텍스트 정박점 재현); Si₃N₄ K=14.02/wt%,
           n=4.62, k=3.4 (임계농도 C₅₀=0.071 wt% ≈ 원문 0.08 wt%). 두 K의 비 10.8배가
           선택비 창(0.08~0.4 wt%)의 기원 — S(C)/S(ref) = exp(−k_N·Δθ_N + k_O·Δθ_O).
         · oxide_silica — **검증된 영(null)**: Penta et al. 2013 Appl. Surf. Sci. 283, 986
           (doi:10.1016/j.apsusc.2013.07.057) "None of the surfactants studied adsorbs on an
           oxide surface and, hence, does not suppress the oxide RR" (SDS·DBSA·DP·SLS, 10 wt%
           콜로이달 실리카, pH 2~10); US10526508B2 Table 1·2 PEG 0~1.4 wt%에서 산화막 RR
           30~50 Å/min 무단조(Spearman ρ=+0.45). → K_oxide=0 ⇒ θ≡0 ⇒ ψ≡1.0 을 **항으로
           계상**한다(모름이 아니라 효과 없음). 양이온 폴리머(PDADMAC·poly(vinylimidazolium))는
           반대로 2 ppm에서 이미 98% 억제(US9758697B2 Table 1: 6242→116 Å/min)라 K를 식별할
           수 없는 스위치형 — 이 팩의 첨가제 클래스가 아니므로 미모델링을 notes로 신고.
         · sic_ceria_h2o2 — **문헌 없음**. SiC 위 첨가제 농도-RR 스윕이 코퍼스·검색 어디에도
           없다. 부모(sti_ceria)의 K는 첨가제×SiO₂ 쌍의 상수라 상속 사용 금지(`has_own`) →
           항을 만들지 않고 status=partial + 사유.
    ③ 분산제 종류 이산 룩업 (Li 2021 PVA/PVP): `chemistry._dispersant_protection_term`.
       ②와 곱한다(독립 가정 — 커플링 미모델링을 notes에 명시).

    한계 (보고서 그대로): (a) 산화막 쪽 k는 (K,n,k) 묶음으로만 식별된다 — 셋을 따로
    옮기지 마라(노트 §5.5). 등급 estimated. (b) K는 화학종·pH·연마입자마다 다르다 —
    Dandu 2009 pyridine계에 Park K를 대입하면 4배 어긋난다(부호·순서만 일치). (c) 아미노산
    (proline 등)은 Prasad & Ramanathan 2006이 흡착량–억제 상관을 반증했으므로 이 폐형식
    대상이 아니다(America 2004 Table I 이산 룩업만). (d) 온도 의존 K(T) 없음.
    """
    from sim.chemistry import (_inhibitor_term, _dispersant_protection_term,
                               _chelator_suppression_term)
    f = _new("psi")
    pk = rr.pack
    notes: List[str] = []
    v = _inhibitor_term(pk, notes)
    for k in ("inhibitor_mM", "surfactant_ppm"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    if v is not None:
        # ── 착화제(글리신) 농도축 억제 — 억제제 항과 독립 가정으로 곱한다 ──
        # 근거: knowledge/cmp/psi-glycine-chelator-suppression-cu-jani2025.md
        # (Jani 2025 doi:10.1149/2162-8777/adc59e Table I×II 통제쌍 2건 +
        #  회귀 [glycine]=-440.91, p=4.08e-7). 종 게이트가 안 맞으면 None.
        terms_metal = {"inhibitor": v}
        v_chel = _chelator_suppression_term(pk, notes)
        if v_chel is not None:
            terms_metal["chelator_suppression"] = v_chel
            v = v * v_chel
            if pk.has("chelator_M"):
                try:
                    f.drivers["chelator_M"] = float(pk.get("chelator_M"))
                except (TypeError, ValueError):
                    pass
        # ── 정의 위반 검사 (EVIDENCE-RULES 판정#95) ─────────────────
        # ψ 는 "표면 보호가 만드는 제거 **억제** 배수"로 정의된다 — 즉 ≤ 1.
        # 1을 넘으면 "보호제를 넣었더니 더 깎인다"는 뜻이라 정의와 모순이다.
        #
        # ⚠ 이 검사는 반드시 **최종 v**(억제제 항 × 착화제 항)에 걸려야 한다.
        # 2026-09-20 이전에는 착화제 항을 곱하기 **전의** v 에만 걸려 있어서,
        # 억제제 항 자체는 1 이하인데 착화제 항이 곱해져 최종값만 1을 넘는
        # 경우를 놓쳤다(예: chelator_M=0 → inhibitor=1.0 · chelator_suppression
        # =1.223 → 최종 ψ=1.223. 범위 검사([0,5])도 통과해 어느 게이트도
        # 못 잡던 사각지대였다).
        #
        # 어떻게 1을 넘는가: 이 항은 기준 농도 대비 **상대값**이다
        # (Kp 가 이미 기준 슬러리에서 역산됐으므로 절대값을 곱하면 이중 계상).
        # 그런데 검증 조건이 기준보다 **낮은** 농도(예: 억제제·착화제 0)면
        # 상대값이 1을 넘는다. 이것은 보호제를 뺀 만큼 덜 보호받는다는
        # 뜻이라 물리적으로 옳지만, ψ 라는 **이름과 정의**에는 맞지 않는다.
        #
        # 조용히 통과시키면 ψ=18 같은 값이 MRR 을 18배 부풀린다
        # (실측: 억제제 0 조건에서 예측 9085 vs 실측 19.2).
        # 값을 자르지 않는다 — 자르면 물리를 숨기는 것이다. 대신 **신고**한다.
        if v > 1.0 + 1e-9:
            notes.append(
                f"⚠ ψ={v:.3f} > 1 — 정의(표면 보호 ≤1) 위반. 기준 농도보다 "
                "억제제·착화제가 적은 조건이라 상대값이 1을 넘었다. 이 팩의 "
                "inhibitor_ref_mM 또는 chelator_ref_M 이 검증 조건 범위의 "
                "하단이 아니라 중간에 있다는 뜻이다. 기준점을 범위 하단(보통 0)"
                "으로 옮기거나, 억제 항을 ψ 가 아니라 별도 팩터로 분리해야 한다.")
        f.value = v
        f.terms = terms_metal
        f.status = "modeled"
        # 등급 하한 판정 (2026-09-13): 억제 항의 약한 고리는 흡착-제거 변환 계수다.
        # 그 계수도 팩 선언값이므로 리터럴 대신 읽는다.
        _confs_psi = [_pack_conf(pk, "inhibitor_mM"),
                      _pack_conf(pk, "inhibitor_strength_k", "inhibitor_ref_mM")]
        if v_chel is not None:
            _confs_psi.append(_pack_conf(pk, "chelator_suppression_a"))
        f.confidence = _worst_conf(*_confs_psi)
        f.sources = ["knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md",
                     "knowledge/cmp/inhibitor-chelator-adsorption-isotherm-passivation.md"]
        f.notes.extend(notes)
        if not pk.has("surfactant_ppm"):
            f.notes.append("⚠ surfactant가 미연결 — 계면활성제도 피복을 통해 억제에 "
                           "기여하는데 통로가 없다.")
        return f

    # ═══ 산화막/세리아 계 — 표면 흡착 보호 (2026-09-14) ═══════════════════
    terms: Dict[str, float] = {}
    confs: List[str] = []
    srcs: List[str] = []
    shield_declared_but_inactive = False

    # ── ② 첨가제 농도축 (Hill 흡착 → 지수감쇠 잔여율, 기준농도 정규화) ──
    def _theta(C: float, K: float, n: float) -> float:
        """협동 흡착 피복률. K=0(흡착 안 함) 또는 C≤0 이면 0."""
        if C <= 0.0 or K <= 0.0:
            return 0.0
        x = (K * C) ** n
        return x / (1.0 + x)

    if pk.has("shield_additive_wt_pct"):
        try:
            C_add = float(pk.get("shield_additive_wt_pct"))
        except (TypeError, ValueError):
            C_add = 0.0
        if C_add < 0.0:
            f.notes.append(f"⚠ shield_additive_wt_pct={C_add} < 0 — 0으로 절단")
            C_add = 0.0
        f.drivers["shield_additive_wt_pct"] = C_add
        # 흡착상수는 첨가제×막질 쌍의 고유 물성 — 상속값이면 남의 재료로 계산한 숫자다.
        if not pk.has_own("shield_langmuir_K"):
            shield_declared_but_inactive = True
            f.notes.append(
                "⚠ ψ 흡착 보호 농도축 비활성: shield_langmuir_K 가 이 팩의 자기선언이 "
                "아니다(상속). 흡착상수는 첨가제×막질 쌍 고유 물성이라 부모 값을 쓰지 않는다 — "
                "이 막질에서 첨가제 농도-RR 스윕 문헌이 확보되면 자기선언으로 활성화된다. "
                "그때까지 첨가제 농도는 결과에 영향을 주지 않는다(partial).")
        elif not pk.has("shield_ref_wt_pct"):
            shield_declared_but_inactive = True
            f.notes.append(
                "⚠ ψ 흡착 보호 농도축 비활성: shield_ref_wt_pct(기준 농도)가 없다 — "
                "기준 없이 절대 잔여율을 곱하면 Kp 이중 계상이므로 항을 만들지 않는다.")
        else:
            K = float(pk.get("shield_langmuir_K"))
            n_h = float(pk.get_or("shield_hill_n", 1.0))
            k_s = float(pk.get_or("shield_strength_k", 1.0))
            C_ref = float(pk.get("shield_ref_wt_pct"))
            th_c, th_r = _theta(C_add, K, n_h), _theta(C_ref, K, n_h)
            val = math.exp(-k_s * (th_c - th_r))
            terms["adsorption_shield"] = val
            confs.append(_pack_conf(pk, "shield_additive_wt_pct", "shield_ref_wt_pct"))
            confs.append(_pack_conf(pk, "shield_langmuir_K", "shield_hill_n",
                                    "shield_strength_k"))
            srcs.append("knowledge/cmp/psi-adsorption-shield-oxide-systems.md")
            srcs.append("knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md §5")
            if K <= 0.0:
                f.notes.append(
                    "ψ 흡착 보호(농도축): 검증된 영 — 이 팩의 첨가제 클래스는 대상 막에 "
                    "흡착하지 않아(K=0) 농도와 무관하게 배수 1.000. '모름'이 아니라 "
                    "'효과 없음'(Penta 2013 doi:10.1016/j.apsusc.2013.07.057; US10526508B2 "
                    "Table 2). 양이온 폴리머는 다른 클래스(스위치형 억제) — 미모델링.")
            else:
                f.notes.append(
                    f"ψ 흡착 보호(농도축): C={C_add:g} wt% (기준 {C_ref:g}) → θ={th_c:.3f} "
                    f"(기준 θ={th_r:.3f}), Hill K={K:g}/wt% n={n_h:g} k={k_s:g} → 배수 {val:.3f} "
                    "(Park 2003 doi:10.1143/jjap.42.5420 Fig.3 역산)")
                if th_c > 0.9:
                    f.notes.append(
                        f"⚠ θ={th_c:.3f} 포화 구간 — 순위는 유지되나(지수감쇠) 절대값은 "
                        "Park 2003 관측 창(≤0.8 wt%) 밖 외삽.")
            # STI 선택비 진단 — 질화막 쪽 상수가 자기선언일 때만
            if pk.has_own("shield_nitride_langmuir_K") and K > 0.0:
                K_n = float(pk.get("shield_nitride_langmuir_K"))
                n_n = float(pk.get_or("shield_nitride_hill_n", n_h))
                k_n = float(pk.get_or("shield_nitride_strength_k", k_s))
                nit = math.exp(-k_n * (_theta(C_add, K_n, n_n) - _theta(C_ref, K_n, n_n)))
                sel_ratio = val / nit if nit > 0 else float("inf")
                f.notes.append(
                    f"STI 선택비 진단: 질화막 배수 {nit:.3f} → oxide:nitride 선택비 "
                    f"{sel_ratio:.2f}배(기준 대비). Park 2003 계(무첨가 S₀=4.8)라면 "
                    f"S≈{4.8 * sel_ratio:.1f}. 질화막 임계농도 C₅₀={1.0 / K_n:.3f} wt%. "
                    "(진단 출력 — 엔진 MRR에는 산화막 배수만 곱한다)")

    # ── ③ 분산제 종류 이산 룩업 (Li 2021) ──
    dnotes: List[str] = []
    dv = _dispersant_protection_term(pk, dnotes)
    if pk.has("dispersant_type"):
        try:
            f.drivers["dispersant_type"] = pk.get("dispersant_type")
        except (TypeError, ValueError):
            pass
    if dv is not None:
        terms["dispersant"] = dv
        confs.append(_pack_conf(pk, "dispersant_type"))
        srcs.append("knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md §6")
        f.notes.extend(dnotes)

    # ── χ 선점 판정 (2026-09-19, 판정#70) ─────────────────────────────
    # ψ 가 비는 이유는 두 가지가 전혀 다르다:
    #   (a) 아무도 안 쟀다 → 진짜 미모델링(unmodeled). 숨기면 안 된다.
    #   (b) 메커니즘은 실재하고 계량도 됐지만 **χ 가 같은 θ(C) 를 이미 전담**한다
    #       → ψ 에 다시 곱하면 이중계상. 이때 옳은 값은 항등원 1.0 이다.
    # 근거: knowledge/slurry/psi-cu-alkaline-h2o2-passivation.md §3·§6(c)
    #   — 같은 θ(C) 를 ψ 에도 곱하면 US9200180B2 Ex.5-7 실측 대비 오차가
    #     단일항보다 커짐을 수치로 확인(노트 verify 블록 (c)).
    # has_own 게이트: 상속만 받은 팩이 조용히 partial 이 되면 진짜 미모델링을
    #   가린다 — **자기 own 계수로 χ 를 이미 가동 중인 팩만** 이 분기를 탄다.
    if not terms:
        _chi_own = [k for k in ("oxidizer_passivation_K", "cu_ph_alkaline_k")
                    if pk.has_own(k)]
        if _chi_own:
            f.value = 1.0
            f.terms = {"owned_by_chi": 1.0}
            f.status = "partial"
            f.confidence = "literature"
            f.sources = ["knowledge/slurry/psi-cu-alkaline-h2o2-passivation.md",
                         "knowledge/cmp/chi-oxidizer-cu-h2o2-reparameterization.md"]
            f.notes.append(
                "ψ=1.000 (항등원): 이 팩의 표면 보호 메커니즘(H2O2/pH 유도 Cu 부동태화)은 "
                "실재하고 1차 문헌으로 계량됐으나(US9200180B2 [0077]·[0111]·TABLE 4), "
                f"χ 가 자기선언 계수 {'·'.join(_chi_own)} 로 같은 물리량 θ(C) 를 이미 "
                "전담 모델링한다 — ψ 에 같은 θ(C) 를 다시 곱하면 이중계상이다"
                "(knowledge/slurry/psi-cu-alkaline-h2o2-passivation.md §6c 수치 증명). "
                "이 계 문헌에 ψ 가 독립으로 가져갈 흡착 화학종이 없다(§4: 억제제 없음, "
                "벤젠술폰산은 Ta 착화제·산화제로 부호 반대, 분산제 라벨 없음) — "
                "새 독립 흡착종이 확보될 때까지 항등원이 맞다.")
            f.notes.extend(notes)
            f.notes.extend(dnotes)
            return f
    if not terms:
        f.notes.append("⚠ ψ 미모델링: 억제제 파라미터(inhibitor_mM + 흡착상수)도, "
                       "첨가제 농도축(shield_*)도, 분산제 파라미터(dispersant_type)도 팩에 "
                       "없다. 표면 흡착 보호를 시뮬레이션할 수 없다.")
        f.notes.extend(notes)
        f.notes.extend(dnotes)
        return f

    val_total = 1.0
    for t in terms.values():
        val_total *= t
    f.value = val_total
    f.terms = terms
    # 농도축이 살아 있어야 modeled — 분산제 이산 룩업만으로는 "얼마나 넣느냐"에 답할 수
    # 없으므로 partial. 문헌이 없어 항을 못 만든 팩(sic)이 여기에 해당한다.
    f.status = "modeled" if "adsorption_shield" in terms else "partial"
    f.confidence = _worst_conf(*confs)
    f.sources = srcs
    f.notes.append("ψ 정의 확장: 표면 흡착 보호(passivation/adsorption shield) — "
                   "이 팩은 금속 부동태가 아니라 첨가제/분산제 흡착 경로")
    if shield_declared_but_inactive and "adsorption_shield" not in terms:
        f.notes.append("⚠ 첨가제 농도축 부재 사유: 이 막질·첨가제 쌍의 농도-RR 문헌 없음 "
                       "(knowledge/cmp/psi-adsorption-shield-oxide-systems.md §6).")
    if len(terms) > 1:
        f.notes.append("⚠ 흡착 보호 항(농도축·분산제 종류)을 독립으로 보고 곱했다 — "
                       "같은 표면 자리를 두 종이 경쟁하는 커플링은 미모델링.")
    return f


def _f_tau(rr: "ResolvedRecipe") -> Factor:
    """τ 슬러리 전달 — 접촉부에 도달하는 신선 슬러리 유효분율.

    ⚠⚠ 이 팩터의 가장 중요한 사실: **"슬러리를 더 많이 나르면 MRR이 비례해서
    오른다"는 직관은 실측으로 기각됐다.**

    근거 ①  Prasad 2013 (doi:10.1557/jmr.2013.173, III.D.3, Mirra 툴 TEOS):
      동일 수지경도·유사 기공크기에서 기공률 %P만 15%→45%로 30%p 올렸는데
      평균 RR 증가는 **단 8%**("nominal increase", 원문 표현). 저자 스스로
      "기공=슬러리 저장소이므로 비례 증가"를 기대했다가 빗나갔다고 적었다.

    근거 ②  Mu et al. 2016 (doi:10.1016/j.mee.2016.02.035, Table 3):
      그루브 폭 → 슬러리 이용효율 η (3 PSI 기준)
          300 µm → η 9.9%
          600 µm → η 13.4%   (+35% 상대)
          900 µm → η 12.8%   (정체·미세 감소)
      **단조가 아니다.** 600 µm 부근에서 꺾인다. 넓힐수록 좋다는 가정은
      틀렸다 — V_groove와 V_total이 함께 커져 q_actual 비율이 안 변하기 때문이다
      (저류 부피가 과하면 정체 슬러리가 늘어난다).

    그래서 이 구현은 두 가지를 지킨다:
      1. η는 **실측 3점 보간**으로 낸다(단조 멱함수 금지 — 정체 구간을 놓친다).
      2. η→MRR 결합은 **매우 약하게** 들어간다. 지수는 Prasad 데이터에서 역산:
         보유용량 3배(15→45%)에 RR 1.08배 ⟹ n = ln(1.08)/ln(3) ≈ 0.07.
         ⚠ 이건 기공률 실험에서 뽑아 그루브 축에 적용한 **교차 대입**이라
         미검증이다. 순위(전달이 나아지면 조금 낫다)만 신뢰하고 크기는
         캘리브레이션 대상이다.

    τ가 진짜로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다.
    Prasad III.D.2: 기공 2 µm 패드는 중심이 슬러리 기아로 처지고 엣지가 올라
    엣지-중심 RR 차이가 200 nm/min을 넘었다. 그 프로파일 결합은 아직 미구현이며
    이 사실을 notes에 싣는다.
    """
    f = _new("tau")
    pk = rr.pack
    # ⚠ 2026-09-13 EVIDENCE-RULES §3회차 규칙 적용 — groove_depth_mm·groove_pitch_mm은
    # 드라이버 수집 대상에서 제외한다(스코프 축소, "가짜 완성"이 아니라 "정직한 스코프").
    # 근거: knowledge/materials/pad-groove-geometry-contact-area-flow-resistance.md §5.
    # Wei/Kao 2011(doi:10.1016/j.wear.2010.10.057) Fig.7이 깊이→RR 배수를 담고 있지만
    # 그래프 이미지(곡선 440개, page.curves 벡터라 색상-범례 매칭 불가 — 실측 시도함,
    # 2026-09-12/13 두 차례 실패)로만 존재해 "기준 대비 배수" 형태 숫자를 텍스트로 낼 수 없다.
    # Kim 2005·Guo 2012도 같은 사유로 배수 미확보(EVIDENCE-RULES §3회차 규칙: 3회 초과 보류
    # 금지 → null 결론/스코프 축소로 반드시 종결). 여기서는 "groove_depth_mm·groove_pitch_mm은
    # 현재 코퍼스로 τ에 편입 불가"를 스코프 축소로 확정한다 — 지어낸 지수보다 정직한 배제가 낫다.
    # slurry_viscosity_pa_s도 τ 결합 문헌(Prasad/Mu)에 정량 관계가 없어 같은 이유로 제외한다
    # (roughness 모델 sim/engine.py에서 별도로 쓰이므로 그쪽 배선은 유지).
    for k in ("groove_width_um", "pad_porosity_pct"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    if not f.drivers:
        f.notes.append("⚠ τ 미모델링: 그루브 폭·기공률이 팩에 없다.")
        return f

    # ── TR(턴오버비) — Philipossian 2004 실측, 그루브 폭·압력·폴리시 시간 ──
    #
    # 2026-09-14 교체: 기존 η(이용효율) 항을 제거하고 TR 항으로 갈아끼운다.
    # 근거: knowledge/cmp/slurry-turnover-ratio-mrt-preston-constant.md §4.
    #   η = q_actual/q_total, q_actual = V_total/MRT  ⟹  **η·MRT = V_total/q_total**
    #   즉 η와 MRT는 같은 실측(반응기 저류부피 V_total)의 두 얼굴이라 **종속**이다.
    #   둘을 곱으로 병치하면 그루브 폭 효과를 두 번 센다(실측 6점에서 η·MRT가
    #   V_total/q_total과 2% 이내 일치 — 같은 노트 §7 verify).
    #   등급 판정: η 항의 지수 0.07은 Prasad 기공률 실험 → 그루브 축 교차대입(E4),
    #   TR 항은 ILD oxide + 콜로이달 실리카 직접 실측 폐형식(E2). E2 > E4 → TR 채택.
    #   방향 독립 확인: Kao 2011(doi:10.1016/j.wear.2010.10.057) "removal rate was
    #   reduced by increasing the groove width" — 다른 그룹·기법이 같은 방향(§4-1).
    #
    # TR = MRT / t_polish,  f_TR = 1 − a·TR,  a = (1 − 370/500)/1.13 = 0.2301
    #   (Philipossian 2004 doi:10.1149/1.1731539 본문: TR=1.13에서 370 Å vs TR=0에서
    #    500 Å = 26% 감소). 기준 조건 대비 배수로만 쓴다 — 절대 손실률을 주장하지 않는다.
    ETA_W = [300.0, 600.0, 900.0]                      # µm, Mu 2016 Table 1
    MRT_3PSI = [9.2, 10.6, 13.9]                       # s, Mu 2016 Table 3
    MRT_5PSI = [8.3, 9.3, 12.7]                        # s, 같은 표
    terms: Dict[str, float] = {}
    srcs: List[str] = []

    def _interp(xs: List[float], ys: List[float], x: float) -> float:
        """구간 밖은 끝값 고정 — 실측이 없는 곳으로 외삽하지 않는다."""
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        for i in range(len(xs) - 1):
            if xs[i] <= x <= xs[i + 1]:
                t = (x - xs[i]) / (xs[i + 1] - xs[i])
                return ys[i] + t * (ys[i + 1] - ys[i])
        return ys[-1]

    def _mrt(width_um: float, psi: float) -> float:
        m3 = _interp(ETA_W, MRT_3PSI, width_um)
        m5 = _interp(ETA_W, MRT_5PSI, width_um)
        # 압력 3~5 PSI 사이만 선형 보간, 밖은 끝값 고정(외삽 금지)
        if psi <= 3.0:
            return m3
        if psi >= 5.0:
            return m5
        return m3 + (psi - 3.0) / 2.0 * (m5 - m3)

    w = pk.get_or("groove_width_um", None)
    w_ref = pk.get_or("groove_ref_width_um", None)
    if w is not None and w_ref is not None:
        a_tr = float(pk.get_or("tr_preston_slope", 0.2301))
        t_pol = float(getattr(rr, "time_s", 0.0) or 0.0)
        t_ref = float(pk.get_or("tau_ref_polish_time_s", t_pol or 1.0))
        # ⚠ 압력 축은 τ에 **넣지 않는다**(2026-09-14 스코프 판정).
        #   Mu 2016은 MRT의 압력 의존을 실측했다(3→5 PSI에서 MRT 비 0.902/0.877/0.914,
        #   슬러리 필름이 얇아져 반응기 부피가 줄기 때문). 물리적으로 실재하는 효과다.
        #   그런데 이걸 τ에 배선하면 **엔진의 Preston 압력 선형성 계약이 깨진다**
        #   (tests/test_engine.py::test_preston_linearity_in_pressure_and_time).
        #   P는 이미 Preston 본항이 지배적으로 담고 있고, MRT 경로의 추가 기여는
        #   30 s 폴리시·2 PSI 스윙에서 약 1.1%에 불과하다(계산: W=600에서
        #   MRT 10.6→9.3 s ⟹ f_TR 0.9187→0.9287). 오더가 두 자릿수 차이나는
        #   부차 경로 때문에 엔진 전역 계약을 깨는 것은 이득보다 위험이 크다.
        #   그래서 MRT는 **기준 압력에서 평가**하고, 배제한 효과의 크기를 위에 남긴다
        #   (EVIDENCE-RULES §3회차 규칙의 "스코프 축소로 종결"과 같은 처리 —
        #   "못 찾았다"가 아니라 "찾았으나 의도적으로 뺐다"이다).
        psi_ref = float(pk.get_or("tau_ref_pressure_psi", 3.0))
        if t_pol > 0 and t_ref > 0:
            mrt_cur = _mrt(float(w), psi_ref)
            mrt_ref = _mrt(float(w_ref), psi_ref)
            # f_TR은 TR > 1/a = 4.35 에서 음수가 되는 명백한 비물리가 있다 — 클램프.
            f_cur = max(1.0 - a_tr * (mrt_cur / t_pol), 0.05)
            f_ref = max(1.0 - a_tr * (mrt_ref / t_ref), 0.05)
            if f_ref > 0:
                terms["turnover"] = f_cur / f_ref
                srcs.append("knowledge/cmp/slurry-turnover-ratio-"
                            "mrt-preston-constant.md §2,§3")
                f.drivers["time_s"] = t_pol
                f.notes.append(
                    f"그루브 폭 {float(w):g} µm({psi_ref:g} PSI 기준) → 슬러리 MRT={mrt_cur:.1f} s, "
                    f"폴리시 {t_pol:g} s에서 턴오버비 TR={mrt_cur / t_pol:.3f} "
                    f"→ Preston 배수 {f_cur:.3f} (기준 {f_ref:.3f}). "
                    "⚠ 폴리시 시간이 짧을수록 물→슬러리 치환 과도기 비중이 커져 "
                    "평균 MRR이 떨어진다(Philipossian 2004 doi:10.1149/1.1731539).")
                if float(w) < ETA_W[0] or float(w) > ETA_W[-1]:
                    f.notes.append(
                        f"⚠ 그루브 폭 {float(w):g} µm는 MRT 실측 범위"
                        f"({ETA_W[0]:g}~{ETA_W[-1]:g} µm) 밖 — 끝값 고정(외삽하지 않는다). "
                        "1.2 mm 초과 구간은 Hong 2012의 반대 방향 레짐일 수 있다(노트 §4-1).")
                f.notes.append(
                    "⚠ MRT의 압력 의존(Mu 2016 실측, 3→5 PSI에서 MRT 약 0.90배)은 τ에 "
                    "배선하지 않았다 — Preston 압력 선형성 계약을 지키기 위한 의도적 "
                    "스코프 축소다. 배제한 크기는 30 s·2 PSI 스윙에서 약 1.1%.")
        else:
            f.notes.append("⚠ τ turnover 항 미적용: 폴리시 시간(time_s)이 0 이하다.")

    # ── 기공률 → 보유용량 (Prasad 2013: 매우 약한 효과) ────────────
    #
    # 함수형 선택의 근거 — 왜 멱함수가 아니라 아핀(affine)인가:
    #   실측은 %P 15→45(3배)에 RR +8% 다. 즉 기공률은 메커니즘을 **만드는** 인자가
    #   아니라 이미 존재하는 이송을 미세 조절하는 인자다(LIMIT_ROLE: MODULATOR).
    #   그런데 (P/P_ref)^n 은 P→0 에서 항상 0 으로 간다 — "기공이 없으면 제거율 0"
    #   이라는 뜻이고, 이는 실측과도 기전과도 어긋난다. 무공극 패드에서도 그루브와
    #   패드-웨이퍼 간극이 슬러리를 나르므로 이송이 사라지지 않는다.
    #   멱함수는 관측 구간(15~45%)에서만 맞고 그 밖에서 비물리적으로 소멸하는,
    #   외삽하면 안 되는 형태였다.
    #
    #   그래서 "기공이 나르는 몫"과 "기공 없이도 나르는 몫"을 분리한다. 단,
    #   분리는 **절대 기공률**로 해야 한다 — (P/P_ref) 로 쓰면 같은 두 조건의
    #   예측 비가 기준점에 따라 달라진다(기준 15% 에서 1.08, 45% 에서 1.03).
    #   물리량의 비가 "어디를 기준으로 삼았는가"에 의존하면 그건 물리가 아니다.
    #
    #       g(P) = P_floor + (P − P_floor)·s          (이송 능력, 임의 단위)
    #       f(P) = g(P) / g(P_ref)                    (기준 대비 배수)
    #
    #   여기서 P_floor 는 "기공이 0 이어도 남는 이송"을 기공률 단위로 환산한
    #   등가값이다. 두 실측점만 있으면 닫힌 형태로 풀린다:
    #       g(45)/g(15) = 1.08  →  (45 + k) / (15 + k) = 1.08,  k = P_floor/s
    #       k = (45 − 1.08·15) / (1.08 − 1) = 360
    #   즉 그루브·간극이 담당하는 이송은 기공률 360% 에 해당하는 크기다 —
    #   기공 경로가 전체의 4% 남짓(15/(15+360))이라는 뜻이고, "기공률을 3배로
    #   늘려도 8% 밖에 안 오른다"는 실측과 정확히 같은 말이다.
    #
    #   이 형태는 (a) P=0 에서 유한하고 (b) P=P_ref 에서 정확히 1 이며
    #   (c) 두 조건의 비가 기준점 선택과 무관하다.
    por = pk.get_or("pad_porosity_pct", None)
    por_ref = pk.get_or("pad_ref_porosity_pct", None)
    if por is not None and por_ref is not None and float(por_ref) > 0:
        k_por = float(pk.get_or("porosity_transport_floor_pct", 360.0))
        g_cur = float(por) + k_por
        g_ref = float(por_ref) + k_por
        if g_ref > 0:
            terms["porosity"] = max(g_cur, 0.0) / g_ref
            srcs.append("knowledge/materials/pad-porosity-slurry-transport-mrr.md §5")
            f.notes.append(
                f"기공률 {float(por):g}% (기준 {float(por_ref):g}%). "
                "⚠ 실측상 기공률 15→45%(3배)에도 RR은 8%만 올랐다 — 비례 가정은 "
                f"기각됐다(Prasad 2013). 기공 외 이송(그루브·간극)을 기공률 등가 "
                f"{k_por:g}% 로 두어 두 실측점을 정확히 재현한다. 기공 경로 기여는 "
                f"{float(por) / g_cur * 100:.1f}% 뿐이다.")

    if not terms:
        f.notes.append(
            "⚠ τ 입력은 있으나 **엔진에 연결되지 않았다** — 기준값"
            "(groove_ref_width_um / pad_ref_porosity_pct)이 팩에 없어 배수를 낼 수 "
            "없다. 조용히 1.0을 쓰면 '그루브를 반영했다'는 거짓말이 된다.")
        f.notes.append(f"현재 입력값: {f.drivers}")
        return f

    val = 1.0
    for v in terms.values():
        val *= v
    f.value = val
    f.terms = terms
    # 2026-09-13 스코프 축소 이후: 드라이버 수집 대상이 groove_width_um·pad_porosity_pct
    # 둘뿐이라(위 EVIDENCE-RULES §3회차 규칙 주석 참고), 그 둘이 전부 term으로 반영되면
    # 이 팩터는 "제한된 범위 안에서 완전 모델링"이다 — partial과는 다르다. 스코프를 줄인
    # 것과 입력을 놓친 것을 혼동하지 않는다.
    # status: 소모품/패드 드라이버(groove_width_um·pad_porosity_pct)가 전부 term으로
    # 반영됐는지로 판정한다. time_s는 2026-09-14 TR 채널이 새로 끌어온 **레시피** 드라이버라
    # 별도 항을 만들지 않는다(turnover 항 안에 이미 들어간다) — 개수 비교에서 제외한다.
    _consumable_drivers = [k for k in f.drivers if k != "time_s"]
    f.status = "modeled" if len(terms) >= len(_consumable_drivers) else "partial"
    # τ 등급 (2026-09-14 재판정, 노트 §9).
    # 이전에는 결합 지수 tau_mrr_exponent=0.07(기공률→그루브 교차대입, E4)이 가장 약한
    # 고리라 τ 전체를 unverified로 하한했다. 그 항을 TR(E2, 대상계 직접 실측 폐형식)로
    # 교체했으므로 그 하한 근거가 사라졌다. 남은 두 항은
    #   turnover — Philipossian 2004(ILD oxide 실측 2점) + Mu 2016(MRT 실측 6점)  E2
    #   porosity — Prasad 2013(기공률 축 **직접** 실측 2점)                        E2
    # 이므로 드라이버 등급을 그대로 쓴다. verified로 올리지 않는 이유: a=0.2301이
    # 2점 유도라 곡률 미검증, MRT 표가 IC1000 200 mm 한정(노트 §6).
    _driver_conf = _pack_conf(pk, "groove_width_um", "pad_porosity_pct")
    f.confidence = str(pk.get_or("tau_exponent_confidence", _driver_conf))
    f.sources = sorted(set(srcs))
    f.notes.append(
        f"⚠ τ 등급={f.confidence}: 결합 형식이 전부 대상계 실측 폐형식(E2)으로 교체됐다 — "
        "TR 항은 ILD oxide 실측(Philipossian 2004), 기공률 항은 기공률 축 직접 실측"
        "(Prasad 2013). 종속이던 η 항은 제거했다(이중 계상, 노트 §4). "
        "verified가 아닌 이유는 TR 기울기 a=0.2301이 2점 유도라 곡률이 미검증이기 때문이다.")
    f.notes.append(
        "⚠ τ가 실제로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다. "
        "기공 2 µm 패드에서 중심이 슬러리 기아로 처지고 엣지-중심 RR 차이가 "
        "200 nm/min을 넘었다(Prasad 2013 III.D.2). 이 프로파일 결합은 미구현 — "
        "담당 R3-pad × R2-slurry.")
    return f


def _f_delta(rr: "ResolvedRecipe") -> Factor:
    """Δ 손상 유발도 — 스크래치·결함 발생 경향 (진단 전용, MRR에 곱하지 않는다).

    종합 노트: knowledge/cmp/delta-damage-model-synthesis.md (2026-09-14, 기확보 노트 8편 종합).

    관계식
        Δ = (D99 / D99_ref)^n × (1 + a)         기준 조건(D99 = D99_ref, a = 0)에서 정확히 1.0
        ① 꼬리 항  — 스크래치는 평균 입경이 아니라 **대입자 꼬리(D99)** 가 만든다. 임계 초과
           입자 개수축에서는 선형(Remsen 2006 Table V, doi:10.1149/1.2184036)이고, 대표 직경
           D99 축으로 옮기면 완만한 거듭제곱이 된다. n = 팩의 `damage_exponent`:
           세리아 1.44(Hitachi US8439995B2 4점 로그-로그 회귀, R²=0.997, literature) /
           텅스텐 2.54(Egan & Kim 2019 doi:10.1149/2.0311905jss 배수 2점 기하평균, literature) /
           구리 2.54(텅스텐→구리 전이, estimated) / 실리카 1.44(세리아→실리카 입자 전이, literature).
        ② 응집 항  — Basim & Moudgil 2002(doi:10.1006/jcis.2002.8352) Table 1: NaCl 0.2 M(CCC
           미달)에서 **평균 입경 불변**인데 AFM Rmax 25→50 nm(×2). D99가 못 잡는 일시적 응집
           경로가 D99 항과 독립으로 존재한다 → `1 + aggregate_ratio`, a=1이 그 논문의 불안정화
           정도. 단일점(n=1) 기반이라 계수 2.0의 화학종 외삽은 미검증. 팩에 선언될 때만 항으로
           계상(미선언 = 이 경로 미조사, 0 = 무영향).
    진단 출력(배수 아님, notes로만 — status/confidence/value에 영향 없음)
        ③ 임계 위치  D99 / d_c, d_c = `scratch_threshold_nm`(680 nm, Remsen 2006; Kwon 2023 700 nm;
           Eusner 2009 응집체 610/762 nm 수렴). 계단 항으로 넣지 않는 이유: 임계 아래에서도
           카운트가 0이 아니고 5팩 다수가 임계 아래라 기준 1.0 계약과 충돌한다.
        ④ 치수 상한  2a_max = D99·√(H_p,max/H_film), δ_max = (D99/2)·(H_p,max/H_film)
           (Saka 2008 doi:10.1016/j.cirp.2008.03.098 식(14)(15) / Eusner 2009 doi:10.1149/1.3121964
           식(10)(11), Table IV 6칸 재현). 압력·패드 토포그래피에 무관하고 패드 **최대** 경도
           `pad_asperity_hardness_max_pa`(0.31 GPa)와 막 경도 `film_bulk_hardness_pa`가 정한다.
           한 팩 안에서 막 경도는 상수라 기준 대비 비가 항상 1 — 드라이버가 될 수 없다.
    넣지 않은 항
        · 입자/막 경도비 배수 — 개수와 입자 경도의 정량 관계를 준 문헌이 없고, 실리카 입자(7.3 GPa)는
          SiO₂ 막(≈9~10 GPa)보다 무르므로 단조 배수는 실리카 팩에서 틀린 방향을 가리킨다.
        · 제타전위·이온강도 → 응집도 유도 — 팩에 실측 입력이 없어(oxide_silica.yaml "지어내지 않음")
          aggregate_ratio는 선언 입력으로만 둔다.
        · LPC 개수축(Fujifilm US10907074 800,000/wt% @0.2 µm) — 입력 축 미신설.
    D99 없는 팩(cu_h2o2_bta·oxide_silica·w_fe_oxidizer)의 D99는 **D50 × D99/D50 일반비 5.00**
    (Levitronix/Silco 2008, 2차 자료) 유도값이며 직접 측정값이 아니다 → estimated(EVIDENCE-RULES
    판정#16: 일반비가 Hitachi 실측 대응쌍에서 30~60% 괴리로 재현되지 않음). what-if를 D50 배수로
    넣으면 Δ는 일반비 선택에 불변이다.
    한계
        · 절대 스크래치 개수는 예측하지 않는다(문헌 slope가 계마다 자릿수 차이). 팩 간 Δ 비교 금지 —
          같은 Δ라도 손상의 절대 심각도는 ④가 보이듯 막 경도가 정한다(Cu δ_max 65 nm vs W 3 nm).
        · n은 재료 상수가 아니라 "D99가 d_c의 어느 쪽에 있는가"의 함수다(종합 노트 §6-1: 로그정규
          꼬리의 국소 지수가 Hitachi 3점에서 8.4→4.6→0.7로 단조 감소, 문헌 상수 n은 그 할선). D99를
          임계를 가로질러 크게 흔들면 상수 n은 임계 아래 과소·위 과대 예측한다.
        · 2026-09-13 스코프 축소: abrasive_size_nm(평균 입경)은 드라이버가 아니다 — 평균 입경(50~150 nm)은
          임계(680 nm)보다 훨씬 작아 그 자체로는 무의미(Remsen 2006 §2.2).
    """
    f = _new("delta")
    pk = rr.pack
    # 2026-09-13 스코프 축소(EVIDENCE-RULES 패턴, τ와 동일): abrasive_size_nm(평균 입경)은
    # 드라이버 수집 대상에서 뺐다. lpc-scratch-density-tail-correlation.md §3이 "D99는 LPC의
    # 근사 대리변수이지 평균 입경과 동일 개념이 아니다"를 명시하고, Remsen 2006 실측(§2.2)이
    # 평균 입경(50~150nm)은 스크래치 임계(680nm)보다 훨씬 작아 그 자체로는 무의미함을 보였다
    # — 즉 abrasive_size_nm을 Δ의 "입력"으로 추적하는 것 자체가 잘못된 신호였다. Δ가 실제로
    # 받는 입력은 d99(꼬리 대표값)와 aggregate_ratio(콜로이드 불안정화) 둘뿐이다.
    for k in ("abrasive_d99_nm", "aggregate_ratio"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    if not pk.has("abrasive_d99_nm"):
        f.notes.append(
            "⚠ Δ 미모델링: 대입자 tail(abrasive_d99_nm)이 팩에 없다. "
            "스크래치는 평균 입경이 아니라 꼬리가 만든다 — D50만으로는 예측 불가. "
            "담당 R2-slurry × defect. 실무에서 가장 자주 문제되는 축인데 통로가 없다.")
        return f
    d99 = float(pk.get("abrasive_d99_nm"))
    d99_ref = float(pk.get_or("abrasive_ref_d99_nm", d99))
    if d99_ref <= 0:
        return f
    # 스크래치 깊이 ∝ 입자 크기, 발생률은 그보다 가파르다. 지수는 knowledge/params/base.yaml
    # 의 damage_exponent(1.44, US8439995B2 회귀)가 기본값이고 화학종별 팩이 덮어쓴다 —
    # 코드에 리터럴로 박지 않는다(EVIDENCE-RULES 판정#12).
    n = float(pk.get("damage_exponent"))
    d99_term = (d99 / d99_ref) ** n
    terms = {"d99": d99_term}
    # aggregate_ratio 항 — 팩에 실제로 선언됐을 때만 term으로 카운트한다(τ와 동일 규칙).
    # 기본값 0.0은 "이 팩에 대해 이 경로가 조사되지 않았다"는 뜻이지 "발동한 항이 1.0으로
    # 확인됐다"는 뜻이 아니다 — 이 구분이 없으면 조사 안 된 팩도 항상 "aggregate"가 term에
    # 잡혀 상태 판정(len(terms)==len(drivers))이 항상 거짓으로 나온다.
    if pk.has("aggregate_ratio"):
        agg_ratio = float(pk.get("aggregate_ratio"))
        terms["aggregate"] = 1.0 + agg_ratio
    else:
        agg_ratio = 0.0
    agg_term = 1.0 + agg_ratio
    val = d99_term * agg_term
    f.value = val
    f.terms = terms
    # 2026-09-13: 남은 드라이버(d99, +선언 시 aggregate_ratio)가 전부 term으로 반영되면
    # "제한된 범위 안에서 완전 모델링"이다(τ와 동일 논리) — abrasive_size_nm을 스코프에서
    # 뺀 것이지, 실제 입력을 놓친 게 아니다.
    f.status = "modeled" if len(terms) == len(f.drivers) else "partial"
    # ⚠ Δ의 confidence는 τ와 동일 원리: 드라이버(D99)와 **지수 근거** 중 나쁜 쪽을 쓴다.
    # 지수는 이제 코드 상수가 아니라 damage_exponent 파라미터 자체가 confidence를 달고
    # 다닌다(base.yaml literature, 팩별로 literature/estimated로 재선언) — τ처럼 별도
    # "_exponent_confidence" 키를 만들 필요가 없다.
    _driver_conf = _pack_conf(pk, "abrasive_d99_nm", "abrasive_ref_d99_nm")
    _exp_conf = pk.param("damage_exponent").confidence
    f.confidence = _worst_conf(_driver_conf, _exp_conf)
    f.sources = ["knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md",
                 "knowledge/cmp/lpc-scratch-density-tail-correlation.md",
                 "knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism.md"]
    f.notes.append(f"손상 지수 n={n:g}(등급={_exp_conf}) — 2026-09-14 판정(EVIDENCE-RULES #12): "
                   "이전 코드 기본값 n=3.0은 출처 없는 가정값(E6, 채택 금지)이었다. "
                   "US8439995B2(Hitachi, 세리아 D99-스크래치 4점 실측) 로그-로그 회귀 "
                   "n≈1.44(R²=0.997, E3)로 교체했다 — knowledge/cmp/"
                   "abrasive-d99-scratch-hitachi-us8439995.md §3. 교차확증: "
                   "lpc-scratch-density-tail-correlation.md(Remsen 2006, fumed silica)도 "
                   "선형(n≈1 근방)을 지지해 같은 방향(n=3.0보다 훨씬 완만)으로 수렴한다. "
                   "순위(큰 입자가 더 긁는다)는 물론 절대 배수도 이제 문헌 근거가 있으나, "
                   "표본이 작아(세리아 1개 화학종, 실질 독립 3점) confidence 상한은 "
                   "literature — verified로는 올리지 않는다.")
    if agg_ratio != 0.0:
        f.notes.append(f"⚠ aggregate_ratio={agg_ratio:g} 항 발동(×{agg_term:.3f}) — "
                       "Basim&Moudgil 2002 NaCl 0.2M 단일 데이터점(n=1) 기반, 화학종/조건 "
                       "외삽 미검증. knowledge/slurry/colloidal-destabilization-lpc-"
                       "defect-mechanism.md §3.")
    f.sources.append("knowledge/cmp/delta-damage-model-synthesis.md")
    f.notes.extend(_delta_diagnostics(pk, d99))
    return f


def _delta_diagnostics(pk, d99_nm: float) -> List[str]:
    """Δ 진단 출력 ③④ — 배수가 아니라 절대 위치·치수. value/terms/status/confidence를 건드리지 않는다.

    ③ 임계 위치: D99 / scratch_threshold_nm (Remsen 2006 680 nm, 실리카 등가).
    ④ 치수 상한: 2a_max = D99·√(H_p,max/H_film), δ_max = (D99/2)·(H_p,max/H_film)
       (Eusner 2009 식(10)(11); Saka 2008 식(14)(15)). 압력 무관 — 패드 최대 경도와 막 경도만.
    상수가 팩에 없으면 그 줄을 내지 않는다(조용한 기본값 금지 — 진단이 빠졌음이 곧 신호).
    """
    out: List[str] = []
    try:
        d_c = float(pk.get("scratch_threshold_nm"))
    except Exception:
        d_c = 0.0
    if d_c > 0:
        pos = d99_nm / d_c
        where = "아래" if pos < 0.9 else ("근처(가장 민감한 위치)" if pos <= 1.1 else "위")
        out.append(f"Δ 진단③ D99/d_c = {pos:.2f} — 꼬리가 스크래치 임계 {d_c:g} nm(Remsen 2006, "
                   f"Kwon 2023·Eusner 2009 교차) {where}. 배수에는 안 들어간다(위치 진단).")
    try:
        h_p = float(pk.get("pad_asperity_hardness_max_pa"))
        h_f = float(pk.get("film_bulk_hardness_pa"))
    except Exception:
        h_p = h_f = 0.0
    if h_p > 0 and h_f > 0:
        r = d99_nm / 2.0
        a_max = r * math.sqrt(h_p / h_f)
        d_max = r * (h_p / h_f)
        out.append(f"Δ 진단④ 스크래치 치수 상한(압력 무관): 폭 2a_max≈{2*a_max:.0f} nm, "
                   f"깊이 δ_max≈{d_max:.1f} nm — Eusner 2009 식(10)(11), H_p,max={h_p/1e9:.2f} GPa, "
                   f"H_film={h_f/1e9:.1f} GPa. Δ 배수가 같아도 절대 심각도는 막 경도가 정한다.")
    return out


def _stab_balance(k_g: float, k_c: float, G: float) -> float:
    """정상상태 패드 조도 R_ss = k_c·G/(k_g + k_c·G)  (식 3, 균형 노트 §1)."""
    return k_c * G / (k_g + k_c * G)


def _stab_value(k_g: float, k_c: float, G: float, G_ref: float,
                t_min: float, t_ref_min: float) -> tuple[float, str]:
    """S 값과 어느 분기(in-situ 균형 / ex-situ 감쇠)인지 돌려준다 — 균형 노트 식 (5a)/(5b).

    G>0  : in-situ. 시정수 1/(k_g+k_c G)≈0.24 min ≪ 연마시간이라 직전 웨이퍼에서 이미
           정상상태 → S = R_ss(G)/R_ss(G_ref), 시간 무관.
    G==0 : ex-situ/무컨디셔닝 프로토콜(웨이퍼마다 R(0)=1) → S = exp(−k_g (clamp(t,1,10) − t_ref)).
           Jeong 2024 관측범위(1~10 min) 밖은 clamp(외삽 금지, 기존 계약 유지).
    """
    if G > 0.0:
        return _stab_balance(k_g, k_c, G) / _stab_balance(k_g, k_c, G_ref), "steady_state"
    t_c = min(max(t_min, 1.0), 10.0)
    return math.exp(-k_g * (t_c - t_ref_min)), "no_conditioning_decay"


def _f_stab(rr: "ResolvedRecipe") -> Factor:
    """S 안정성 — 글레이징률 vs 컨디셔닝 재생률의 균형이 정하는 정상상태 패드 조도.

    모델 (knowledge/materials/pad-steady-state-glazing-conditioning-balance.md §1):
        dR/dt = −k_g·R + k_c·G·(1 − R),   G = (duty/100)·A(t_disk),  A = exp(−t_disk/τ_aging)
        R_ss  = k_c·G / (k_g + k_c·G)
        S     = R_ss(G) / R_ss(G_ref)                       (G > 0, in-situ 균형; 시간 무관)
        S     = exp(−k_g·(clamp(t,1,10 min) − 1 min))       (G = 0, 무컨디셔닝 — Jeong 2024 특수해)
    기준 조건(cond_ref_duty_pct=100, cond_ref_disk_usage_hours=0)에서 정확히 1.0.

    파라미터 (base.yaml, 팩 5개 공통 — 패드 재질 성질):
      k_g = 0.02796 /min  Jeong et al. 2024 (doi:10.3390/ma17081817) Fig.9 pooled 로그회귀
                          (a=1.1478, b=−0.1109)의 10 min 손실 22.25%를 지수형으로 이식. 10 min 값은
                          기존 로그감쇠와 동일(회귀 테스트), 중간점 R²는 exp 0.77 > log 0.64.
      k_c = 4.08 /min     Jeong et al. 2022 ASPEN (doi:10.3850/978-981-18-6021-8_or-12-0224) Table 1
                          3 psi → 30 s 완전 회복 + Jeong 2024 복원 허용폭 ±13% → ln(1/0.13)/0.5.
      A(t_disk)           Γ과 같은 함수(sim/tier2_physics/conditioner_pcr_decay.pcr_decay, τ=27.4 h)
                          — 드레서 마모가 Γ(절삭 부하)와 S(정상상태 조도)에 한 번씩, 같은 부호로 들어간다.

    검증 (같은 노트 §4 verify):
      · duty=0, t=10 min → 0.7775 = 기존 로그감쇠 값(1e−9 이내).
      · PHM2016 실장비 477 웨이퍼(validation/raw/phm2016): S 순위 vs MRR 순위 저속군 ρ=+0.696
        (원변수 드레서 사용량 −0.696의 부호 반전), 사용량→시간 배율 0.02/0.05/0.1 전부 동일 —
        데이터가 은닉 배율로 스케일돼 있어 **순위만** 검증(절대값 금지, README).

    등급 판정(리터럴 하한이 아니라 계산): 비-실리카 팩의 k_g는 코퍼스에 없다(EVIDENCE-RULES
    판정#9 종결 — 재탐색 금지). 그 불확실성이 이번 런에 실제로 미치는 폭을 잰다: k_g를
    stab_glaze_rate_uncertainty_x(=5, Lawing 2004 fumed/colloidal)배로 바꿔 S를 재계산해
    |ΔS| < 0.03(제품 오차 목표)이면 k_g는 약한 고리가 아니므로 k_c·A·duty 등급(literature)을 따르고,
    넘으면 estimated. 기준점(G=G_ref)에서는 k_g가 식에서 상쇄돼 ΔS=0 — 실리카가 아니어도
    in-situ 기준 운전점의 S는 문헌 등급이다. 무컨디셔닝(duty=0) 구간은 판정#9대로 실리카만 literature.

    한계(문헌이 지지하지 않아 뺀 항, 노트 §6):
      · k_g 압력 지수(2 psi 0.0223 / 5 psi 0.0392 — 2점) 미도입, ±40% 밴드로만 기록. 압력은 Λ의 축.
      · G에 컨디셔너 하중·속도(F·v) 미포함 — k_c 도출 조건(0.7 psi·101 rpm)→기준(4 lbf·55 rpm) 환산
        지수 없음. 하중·속도의 S 반응은 미모델링(Γ이 부하로만 담는다).
      · 그릿 밀도·형상 → k_c(Kwon 2013 37/23/19 µm/h)는 팩에 그릿 키가 없어 미연결.
      · 수십시간 패드 수명(Son & Lee 2021)은 컨디셔너 구조 변수 부재로 판정#8 유지.
      · ε=0.13은 접촉수 기준 — k_c 자릿수(1.3~6 /min)만 확실, 4.08은 그 안의 한 점.
    """
    f = _new("stab")
    pk = rr.pack
    t_min = rr.time_s / 60.0
    f.drivers["time_s"] = rr.time_s

    needed = ["stab_glaze_rate_per_min", "stab_cond_recovery_rate_per_min"]
    if not all(pk.has(k) for k in needed):
        # 균형 파라미터가 없으면 무컨디셔닝 로그감쇠 특수해로 후퇴한다 (기존 계약 그대로).
        a_fit, b_fit = 1.1478, -0.1109
        t_c = min(max(t_min, 1.0), 10.0)
        f.value = (a_fit + b_fit * math.log(t_c)) / a_fit
        f.terms = {"time_min_log_decay": f.value}
        f.status = "partial"
        abrasive = str(pk.get_or("abrasive", "")).lower()
        f.confidence = "literature" if abrasive == "silica" else "estimated"
        f.sources.append("knowledge/materials/pad-glazing-mechanism-mrr-decay.md")
        f.notes.append("⚠ stab_glaze_rate/stab_cond_recovery_rate 없음 — 컨디셔닝 균형 미모델링, "
                       "Jeong 2024 무컨디셔닝 로그감쇠만 적용.")
        return f

    k_g = float(pk.get("stab_glaze_rate_per_min"))
    k_c = float(pk.get("stab_cond_recovery_rate_per_min"))
    t_ref_min = float(pk.get_or("stab_ref_time_s", 60.0)) / 60.0
    duty = float(pk.get_or("cond_duty_pct", 100.0))
    duty_ref = float(pk.get_or("cond_ref_duty_pct", duty or 100.0))
    f.drivers["cond_duty_pct"] = duty

    A_now = A_ref = 1.0
    if pk.has("cond_disk_usage_hours"):
        import conditioner_pcr_decay as CPD   # sim/tier2_physics — Γ과 같은 함수, 수정 없음
        t_h = float(pk.get("cond_disk_usage_hours"))
        t_ref_h = float(pk.get_or("cond_ref_disk_usage_hours", 0.0))
        A_now = CPD.pcr_decay(t_h, 1.0, CPD.TAU_AGING_HOURS)
        A_ref = CPD.pcr_decay(t_ref_h, 1.0, CPD.TAU_AGING_HOURS)
        f.drivers["cond_disk_usage_hours"] = t_h

    G = (duty / 100.0) * A_now
    G_ref = (duty_ref / 100.0) * A_ref
    if G_ref <= 0.0:
        f.notes.append("⚠ 기준 컨디셔닝 강도 G_ref=0 — 균형 기준점을 정의할 수 없어 S 계산 불가")
        return f

    val, branch = _stab_value(k_g, k_c, G, G_ref, t_min, t_ref_min)
    f.value = val
    f.terms = {branch: val,
               "R_ss(G)": _stab_balance(k_g, k_c, G) if G > 0 else 0.0,
               "R_ss(G_ref)": _stab_balance(k_g, k_c, G_ref),
               "conditioning_strength_G": G,
               "dresser_wear_A": A_now / A_ref if A_ref else 1.0}
    f.status = "modeled"

    # ── 등급: k_g 불확실성이 이번 운전점에서 실제로 미치는 폭으로 판정 ──
    # 등급 하한 판정 (2026-09-14) — 이 하한은 **정당하다**. 근거를 남긴다.
    #   가장 약한 고리는 드라이버(duty·사용시간)가 아니라 **글레이징 속도 k_g**다.
    #   k_g의 유일한 정량 앵커는 실리카/IC1000 계 로그감쇠(Jeong 2024)이고, 다른
    #   연마입자계의 k_g는 코퍼스에 없다 — 즉 재료 전이(E4)라 드라이버가 전부
    #   문헌값이어도 S 배수의 크기를 문헌이 보증하지 않는다.
    #   단, 하한을 무조건 걸지는 않는다: 이 운전점에서 k_g를 ×x 흔들어도
    #   |ΔS|<0.03이면 k_g 불확실성이 결과를 지배하지 않으므로 드라이버 등급을 그대로
    #   쓴다(실리카계는 앵커 계이므로 애초에 전이가 아니다).
    #   해제 조건: 해당 연마입자계의 k_g를 문헌/실측으로 확보해 팩에 선언.
    x = float(pk.get_or("stab_glaze_rate_uncertainty_x", 5.0))
    val_hi, _ = _stab_value(k_g * x, k_c, G, G_ref, t_min, t_ref_min)
    band = abs(val_hi - val)
    f.terms["k_g_band_dS"] = band
    abrasive = str(pk.get_or("abrasive", "")).lower()
    base_conf = _pack_conf(pk, *needed, "cond_duty_pct",
                           *(["cond_disk_usage_hours"] if pk.has("cond_disk_usage_hours") else []))
    if abrasive == "silica" or band < 0.03:
        f.confidence = base_conf
    else:
        f.confidence = _worst_conf(base_conf, "estimated")
        f.notes.append(
            f"⚠ k_g는 실리카/IC1000 값이고 이 팩({abrasive or '미상'})의 k_g는 코퍼스에 없다"
            f"(판정#9). 이 운전점에서 k_g×{x:g} 밴드가 |ΔS|={band:.3f}(>0.03)라 estimated.")
    f.sources = [
        "knowledge/materials/pad-steady-state-glazing-conditioning-balance.md",
        "knowledge/materials/pad-glazing-mechanism-mrr-decay.md",
        "knowledge/equipment/disk-insitu-exsitu-conditioning-mrr-stability.md",
        "knowledge/equipment/conditioner-disk-pad-cutting-model.md",
        "Jeong et al. 2024, Materials 17(8) 1817, doi:10.3390/ma17081817 (PMC11051262) Fig.9",
        "Jeong et al. 2022, ASPEN 2022 pp.568-570, doi:10.3850/978-981-18-6021-8_or-12-0224 Table 1",
    ]
    if branch == "no_conditioning_decay":
        f.notes.append("duty=0 → 웨이퍼마다 ex-situ 재생 프로토콜(R(0)=1)로 해석: Jeong 2024 무컨디셔닝 "
                       "감쇠 특수해. 장시간 무컨디셔닝 연속 운전(G→0⁺, R_ss→0)과는 다른 프로토콜이다.")
        if t_min > 10.0:
            f.notes.append(f"⚠ time_s={rr.time_s:.0f}s({t_min:.1f} min)가 관측범위(1~10 min) 초과 — "
                           "t=10 min 값으로 clamp(외삽 아님, 과소추정 가능).")
        if t_min < 1.0:
            f.notes.append(f"⚠ time_s={rr.time_s:.0f}s가 관측 최솟값(1 min) 미만 — t=1 min 값으로 clamp.")
    else:
        f.notes.append(f"in-situ 균형: 시정수 1/(k_g+k_c·G)={1/(k_g+k_c*G):.2f} min ≪ 연마시간이라 "
                       "정상상태 — S는 time_s에 무관하고 duty·드레서 마모만 본다.")
    if not pk.has("cond_disk_usage_hours"):
        f.notes.append("⚠ cond_disk_usage_hours 없음 — 디스크 신품 가정(A=1.0).")
    f.notes.append("⚠ 미모델링: 컨디셔너 하중·속도의 S 반응(k_c 환산 지수 없음), 그릿 밀도→k_c, "
                   "수십시간 패드 수명(컨디셔너 구조 변수 부재, 판정#8). 균형 노트 §6.")
    return f


# ═══════════════════════════════════════════════════ 집계

_BUILDERS = {
    "lambda": _f_lambda, "pi": _f_pi, "theta": _f_theta, "gamma": _f_gamma,
    "kappa": _f_kappa, "chi": _f_chi, "psi": _f_psi,
    "tau": _f_tau, "delta": _f_delta, "stab": _f_stab,
}


def compute_factors(rr: "ResolvedRecipe") -> Dict[str, Factor]:
    """레시피 하나에서 10개 병합 파라미터를 전부 계산한다.

    실패한 팩터는 예외를 던지지 않고 status='unmodeled'로 돌아온다 —
    미모델링을 숨기지 않는 것이 이 층의 핵심 계약이다.
    """
    out: Dict[str, Factor] = {}
    for key, fn in _BUILDERS.items():
        try:
            out[key] = fn(rr)
        except Exception as e:      # 팩터 하나가 죽어도 나머지는 봐야 한다
            f = _new(key)
            f.notes.append(f"⚠ 계산 중 예외: {type(e).__name__}: {e}")
            out[key] = f
    return out


def mrr_multiplier(factors: Dict[str, Factor]) -> tuple[float, List[str]]:
    """MRR에 곱해질 총 배수와 그 근거 문구.

    ⚠ MRR_COUPLED에 든 팩터만 곱한다. 기준 조건에서 각 팩터가 1.0이므로
    총 배수도 1.0이어야 한다 — 이 성질은 테스트로 고정돼 있다.
    """
    mult = 1.0
    notes: List[str] = []
    for key in sorted(MRR_COUPLED):
        f = factors.get(key)
        if f is None:
            continue
        if f.status == "unmodeled" or f.value is None:
            notes.append(f"[{f.symbol} {f.name}] 미모델링 — MRR에 반영 안 됨")
            continue
        mult *= f.value
        notes.append(f"[{f.symbol} {f.name}] ×{f.value:.4f} ({f.status}, {f.confidence})")
    return mult, notes


def coverage(factors: Dict[str, Factor]) -> Dict[str, object]:
    """팩터 커버리지 — 얼마나 많은 축이 실제로 살아 있는가.

    V2의 완주 판정(§3)이 읽는 값이다. '노트 몇 편'이 아니라 이 숫자가 진도다.
    """
    modeled = [k for k, f in factors.items() if f.status == "modeled"]
    partial = [k for k, f in factors.items() if f.status == "partial"]
    unmodeled = [k for k, f in factors.items() if f.status == "unmodeled"]
    return {
        "total": len(factors),
        "modeled": sorted(modeled),
        "partial": sorted(partial),
        "unmodeled": sorted(unmodeled),
        "score": round((len(modeled) + 0.5 * len(partial)) / max(len(factors), 1), 3),
    }
