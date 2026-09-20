"""팩 YAML에 선언됐지만 sim/ 어디에서도 읽지 않는 '고아 키'를 기계로 고정한다.

배경 — 왜 이 게이트가 필요한가
-------------------------------
판정#54(2026-09-16)가 `cof_boundary`·`cof_hydro_coeff`·`cof_transition_alpha`
3키가 base.yaml에 선언돼 있으면서 엔진이 **읽지 않는 dead code**임을 적발했다.
증상이 숨어 있던 이유는 모듈 기본인자와 팩 값이 **우연히 같아서**였다 —
팩 값을 3배 흔들어도 출력이 비트 단위로 불변이었다.

그것은 1회성 사고가 아니라 **구조적 고장 방식**이다. 2026-09-17 전수 스캔 결과
고유 파라미터 키 132개 중 **7개**가 sim/ 어디에도 나타나지 않았고, 그 중 5개는
`literature`·`verified` 등급을 달고 있었다. 등급이 높다는 것은 "1차 출처로 검증된
값"이라는 뜻인데, 아무도 읽지 않으면 그 검증은 **모델에 도달하지 않는다**.
더 나쁜 것은 note가 코드에 대해 사실과 다른 주장을 하던 2건이었다(같은 회차에 정정).

이 테스트는 값을 판단하지 않는다. 다만 **고아 키가 조용히 늘어나는 것**을 막는다.
새 키를 팩에 넣고 배선을 잊으면 여기서 FAIL한다.

해소 방법 (둘 중 하나, 침묵은 안 된다)
  (a) 키를 실제로 읽도록 배선한다 — 이게 대개 옳다.
  (b) 아직 배선할 수 없으면 아래 _KNOWN_ORPHANS에 **사유와 함께** 등록한다.
      사유는 "나중에"가 아니라 무엇이 선행조건인지 구체적으로 적는다.
"""
from __future__ import annotations

import pathlib
import re

from sim.params import available_packs, load_pack

# 키 → 고아인 사유. 사유 없이 추가하는 것을 막으려 문자열을 필수로 한다.
# ⚠ 이 목록을 늘리는 것은 부채를 늘리는 것이다. 배선이 가능하면 배선하라.
_KNOWN_ORPHANS = {
    "pad_wear_half_life_h":
        "1차 출처 확보 실패(knowledge/pad/pad-material-gw-effective-modulus-"
        "asperity-distribution.md §5). pad-material 에이전트가 '손대지 말라'를 "
        "명시 권고했고 EVIDENCE-RULES 판정#40이 이를 채택. 값이 estimated라 "
        "배선하면 근거 없는 수치가 MRR 경로에 들어간다 — 의도적 미배선.",
    "dishing_sensitivity":
        "팩 note가 스스로 '⚠ 미연결'을 선언. dishing 정량에는 금속:산화막 MRR 비가 "
        "필요한데 두 팩을 동시에 로드하는 다막질 모델이 아직 없다(S6 대기).",
    "pad_sigma0_m":
        "소비처 conditioner_asperity_distribution 모듈이 S12 전수판정에서 영구 "
        "스킵 확정(validation/S12-RESIDUAL-JUDGMENT.md) — 블로커는 A0(문헌 fit "
        "파라미터라 공개 정량값 없음). 모듈이 등록되면 이 키가 그 입력이 된다.",
    "hamaker_j":
        "소비처 sim/tier2_physics/dlvo_colloid.py 는 self-test에서 A를 인자로 받아 "
        "쓰고 팩을 조회하지 않는다. 엔진의 DLVO 진단은 정성 판정(IEP 거리)만 하고 "
        "V_T(h) 정량 곡선을 내지 않는다 — 이온세기·zeta 실측값이 팩에 없어서다. "
        "정량 곡선을 내려면 그 두 값이 먼저 필요하다.",
    "ph_mrr_at_peak_rel":
        "χ의 pH 항은 정점 위치·연화 기울기로 형상을 만들고 '정점에서의 MRR 비'를 "
        "따로 곱하지 않는다(곱하면 Kp와 이중계상). 이 키는 노트 verify 블록이 "
        "assert하는 문헌 재현값의 보관처다 — 모델 입력이 아니라 근거 기록.",
    "relative_velocity_ref_mps":
        "Λ의 속도 기준은 rpm·기하에서 운동학으로 직접 계산한다(lambda_ref_rpm_* 경유). "
        "이 키는 그 계산의 오더 확인용 문헌 대표값(0.5~1 m/s)이라 입력이 아니다.",
    "cond_ref_sweep_cpm":
        "Γ의 기준 분모는 downforce·rpm·duty·disk_usage 4개로 구성되고 sweep_cpm은 "
        "설계상 Γ 크기에 곱하지 않는다(sim/factors.py 주석: 커버리지 축이라 절삭 "
        "부하와 물리량이 다름). 따라서 그 짝인 기준값도 쓰이지 않는 것이 정상.",
}


def _sim_source_tokens() -> set[str]:
    src = []
    for p in pathlib.Path(__file__).resolve().parent.parent.joinpath("sim").rglob("*.py"):
        src.append(p.read_text(encoding="utf-8", errors="ignore"))
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", "\n".join(src)))


def _orphan_keys() -> dict[str, list[str]]:
    toks = _sim_source_tokens()
    owners: dict[str, list[str]] = {}
    for pk in available_packs():
        for k in load_pack(pk).params:
            owners.setdefault(k, []).append(pk)
    return {k: v for k, v in owners.items() if k not in toks}


def test_no_new_orphan_pack_keys():
    """sim/ 어디에서도 읽지 않는 팩 키가 새로 생기면 FAIL."""
    orphans = _orphan_keys()
    unexpected = sorted(set(orphans) - set(_KNOWN_ORPHANS))
    assert not unexpected, (
        "팩에 선언됐지만 sim/ 어디에서도 읽지 않는 키가 새로 생겼다: "
        f"{unexpected}. 배선하거나, 배선 불가 사유를 _KNOWN_ORPHANS에 적어라. "
        "(판정#54 — 선언만 하고 읽지 않으면 그 값의 confidence 등급은 모델에 도달하지 않는다)"
    )


def test_known_orphans_are_still_orphans():
    """배선이 끝난 키가 목록에 남아 있으면 목록이 낡은 것이다 — 함께 FAIL시킨다."""
    orphans = _orphan_keys()
    stale = sorted(set(_KNOWN_ORPHANS) - set(orphans))
    assert not stale, (
        f"이제 실제로 읽히는데 고아 목록에 남아 있는 키: {stale}. "
        "_KNOWN_ORPHANS에서 지워라 — 낡은 면제는 다음 고아를 숨긴다."
    )


def test_every_known_orphan_has_a_reason():
    """사유 없는 면제 등록을 막는다 — '나중에'는 사유가 아니다."""
    for key, reason in _KNOWN_ORPHANS.items():
        assert isinstance(reason, str) and len(reason.strip()) >= 40, (
            f"{key}: 면제 사유가 비었거나 너무 짧다 — 무엇이 선행조건인지 구체적으로 적어라"
        )


def test_orphan_count_does_not_grow():
    """총량 고정 — 개별 이름을 바꿔 가며 부채를 늘리는 우회를 막는다."""
    assert len(_orphan_keys()) <= len(_KNOWN_ORPHANS) == 7
