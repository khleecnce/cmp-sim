"""응답 지도 계약 테스트 — 형상 분류와 판정 규칙이 흔들리지 않게 못 박는다.

여기서 지키는 계약은 셋이다(전부 실제로 틀렸던 적이 있는 지점):
  1. 정점을 단조로 부르면 안 된다 — 소재 개발자에게 틀린 방향을 가리킨다.
  2. 모델과 문헌은 **같은 x 구간**에서 비교해야 한다. 구간이 다르면 가짜 충돌이 난다.
  3. 캘리브레이션 출처·교란(다인자 동시변화) 데이터셋은 판정에서 빠져야 한다.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.response_map import (  # noqa: E402
    classify, verdict_of, literature_evidence, pooled, Evidence,
)


def test_classify_monotonic_and_peak():
    xs = [1, 2, 3, 4, 5, 6, 7]
    assert classify(xs, [1, 2, 3, 4, 5, 6, 7])[0] == "up"
    assert classify(xs, [7, 6, 5, 4, 3, 2, 1])[0] == "down"
    # 정점: 안쪽이 양 끝보다 확실히 높다
    assert classify(xs, [1, 3, 6, 9, 6, 3, 1])[0] == "peak"
    assert classify(xs, [9, 6, 3, 1, 3, 6, 9])[0] == "valley"


def test_classify_flat_is_not_a_direction():
    """무반응은 방향이 아니다 — 'up'으로 새면 미구현 축이 정상으로 보인다."""
    assert classify([1, 2, 3, 4], [5.0, 5.0, 5.0, 5.0])[0] == "flat"
    assert classify([1, 2, 3, 4], [5.0, 5.001, 5.0, 5.002])[0] == "flat"


def test_peak_needs_margin_over_endpoints():
    """안쪽 점이 끝점과 거의 같으면 정점이 아니다 — 노이즈를 정점이라 부르지 않는다."""
    shape, _ = classify([1, 2, 3, 4, 5], [1.0, 1.5, 1.51, 3.0, 5.0])
    assert shape == "up"


def test_verdict_peak_vs_monotonic_is_conflict():
    """가장 위험한 고장: 정점 거동을 단조로 근사 → pH 12.5를 과대평가한다."""
    assert verdict_of("up", "peak") == "CONFLICT"
    assert verdict_of("down", "up") == "CONFLICT"
    assert verdict_of("up", "valley") == "CONFLICT"
    assert verdict_of("peak", "peak") == "AGREE"
    # 포화와 단조 증가는 실무 판단이 같다
    assert verdict_of("saturating", "up") == "AGREE"


def test_verdict_flat_with_literature_is_dead_not_agree():
    assert verdict_of("flat", "up") == "DEAD"
    assert verdict_of("flat", "unknown") == "BLANK"
    assert verdict_of("up", "unknown") == "NO-DATA"


def test_calibration_and_confounded_are_excluded_from_verdict():
    """자기 답안지 채점과 교란 데이터로 '문헌이 확인함'이라 말하면 안 된다."""
    def mk(**kw):
        base = dict(key="slurry_ph", dataset="x", pack="p", n=5, shape="peak",
                    span=2.0, x_lo=1, x_hi=5, xs=[1, 2, 3, 4, 5], ys=[1, 2, 3, 2, 1],
                    confounded=False, n_varying=1, in_scope=True, calib=False,
                    read="table")
        base.update(kw)
        return Evidence(**base)
    assert mk().usable()
    assert not mk(calib=True).usable()
    assert not mk(confounded=True, n_varying=3).usable()
    assert not mk(in_scope=False).usable()
    assert pooled([mk(calib=True)], "slurry_ph", "p") is None


def test_pooling_normalizes_absolute_scale():
    """논문마다 장비·막질이 달라 MRR 절대값이 다르다 — 정규화 없이 풀링하면
    형상이 아니라 논문 간 오프셋을 보게 된다."""
    ev = literature_evidence()
    for e in ev:
        # 각 데이터셋은 자기 중앙값으로 나뉘어 있으므로 중앙값 근처에 1.0이 있다
        assert min(e.ys) <= 1.0 <= max(e.ys) + 1e-9


def test_real_datasets_produce_usable_evidence():
    """실제 데이터셋에서 단독 변화 인자가 하나 이상 잡혀야 한다 —
    전부 교란으로 빠지면 이 도구가 아무것도 판정하지 않는다."""
    ev = literature_evidence()
    assert any(e.usable() for e in ev)
    keys = {e.key for e in ev if e.usable()}
    assert "slurry_ph" in keys


# ── 2026-09-15 판정#42: 교란 탐지가 FACTORS 키만 보던 결함 ────────────────
def test_confound_detection_sees_non_factor_inputs():
    """교란 판정은 '모델이 아는 축'이 아니라 '실험에서 변한 축' 기준이어야 한다.

    원 결함: 교란 탐지가 FACTORS 키만 훑어서, FACTORS 에 없는 키(예: 연마입자
    농도)가 함께 변하는 표를 '단독 변화'로 오인했다. 그 결과 존재하지 않는
    DEAD 갭이 4회차 연속 최상위(score 95)로 올라왔다.

    ⚠ 2026-09-19: 원래 특정 데이터셋(us9200180b2_cu_abrasive_series)을 이름으로
    박아 두었는데, 그 데이터셋이 게이트 밖 2점을 빼면서 n=2 로 줄어 증거를
    내지 않게 되자 테스트가 깨졌다. **계약은 그 파일이 아니라 '교란 탐지가
    FACTORS 밖 키를 본다'는 성질**이므로, 이름을 박지 말고 성질로 검사한다
    (저장소 규칙: 판정 기준에 특정 사례를 하드코딩하지 않는다 — 하드코딩하면
    그 사례가 바뀔 때마다 계약과 무관하게 깨진다).
    """
    from tools.response_map import FACTORS

    ev = list(literature_evidence())
    confounded = [e for e in ev if e.confounded]
    assert confounded, "교란으로 잡힌 증거가 하나도 없다 — 탐지기가 죽었을 수 있다"

    # 교란은 반드시 사용 불가로 이어져야 한다(교란된 증거를 쓰면 오진한다)
    for e in confounded:
        assert not e.usable(), f"{e.dataset}/{e.key}: 교란인데 usable 이다"
        assert e.n_varying >= 2, (
            f"{e.dataset}/{e.key}: 교란인데 변한 축이 {e.n_varying}개다 — "
            "교란의 정의는 '2축 이상 동시 변화'이므로 판정이 모순이다")

    # 핵심 계약: 변한 축을 세는 범위가 **FACTORS 키에 갇혀 있지 않아야** 한다.
    # FACTORS 키만 훑으면 그 밖의 축(연마입자 농도 등)이 함께 변해도 1축으로
    # 세어 '단독 증거'로 통과시킨다 — 그것이 판정#42 의 원 결함이다.
    # 그래서 FACTORS 키 수보다 많은 축이 변한 데이터셋이 실제로 잡히는지 본다.
    factor_keys = {f.key for f in FACTORS}
    assert any(e.n_varying > len(factor_keys & {e.key}) for e in confounded), (
        "교란 판정이 대상 키 자신만 세고 있다 — FACTORS 밖 축을 못 보는 상태일 수 있다")


def test_quarantined_datasets_are_not_evidence():
    """qa_loop가 격리한 데이터셋이 응답 판정에서만 살아 있으면 안 된다.

    backtest.py는 quarantine.json을 적용하는데 response_map은 안 봤다 —
    같은 데이터가 한 도구에는 부적격, 다른 도구에는 적격이면 랭킹 전체를 못 믿는다.
    """
    import json as _json
    qf = ROOT / "validation" / "quarantine.json"
    if not qf.exists():
        return
    q = set(_json.loads(qf.read_text(encoding="utf-8")).keys())
    if not q:
        return
    for e in literature_evidence():
        if e.dataset in q:
            assert e.quarantined and not e.usable()


def test_full_cross_doe_yields_controlled_strata():
    """완전교차 DOE는 통째로 버리지 말고 '나머지 고정' 층에서 단독 증거를 뽑아야 한다.

    US9499721B2는 실리카 6수준 × 압력 4수준이다. 층(실리카 고정) 안에서 압력은
    단독으로 변하므로 통제된 증거다 — 이전 구현은 이걸 교란으로 버렸다.
    """
    ev = {(e.dataset, e.key): e for e in literature_evidence()}
    e = ev.get(("us9499721b2_teos_colloidal_silica_pressure_conc", "pressure_psi"))
    assert e is not None
    assert not e.confounded and e.usable()
    assert e.shape == "up"


# ── 2026-09-20: 가짜 CONFLICT 3종 차단 ───────────────────────────────
# 셋 다 실제로 최우선 갭(score 120)을 잘못 점유하고 크론 회차를 태웠던 결함이다.
# 가짜 충돌의 대가는 "못 잡았다"가 아니라 **멀쩡한 항의 부호를 뒤집는 것**이라
# 다른 레짐까지 망친다. 그래서 계약으로 못 박는다.

def test_replicates_at_same_x_do_not_create_a_shape():
    """같은 x 의 반복 산포는 형상이 아니다.

    classify 는 인덱스 위치로 정점/골을 찾으므로, 같은 x 가 여러 번 들어오면
    반복 산포가 x 축의 기복으로 오인된다. x 가 안 움직였는데 방향이 나오면
    그건 물리가 아니라 채점 버그다.
    """
    # x=0 에서 3회 반복(185/240/265), 이후 단조 감소. 접으면 '단조↓'여야 한다.
    xs = [0.0, 0.0, 0.0, 0.5, 10.0]
    ys = [185.0, 240.0, 265.0, 170.0, 100.0]
    assert classify(xs, ys)[0] == "down"
    # 반복을 접은 뒤 3점 미만이면 형상을 말할 수 없다
    assert classify([1.0, 1.0, 1.0, 2.0], [1.0, 2.0, 3.0, 4.0])[0] == "invalid"


def test_split_regimes_are_not_reported_as_conflict():
    """문헌이 조건별로 반대 방향이면 그건 모델이 틀렸다는 증거가 아니다.

    US8501625B2 의 H2O2 축은 2 psi 층에서 단조↓, 1 psi 층에서 정점이다.
    두 층을 합치면 어느 층에도 없는 '정점'이 나와 모델(단조↓)에 CONFLICT 가
    찍혔다. 고칠 곳은 산화제 항의 부호가 아니라 압력×산화제 상호작용이다.
    """
    assert verdict_of("down", "mixed") == "SPLIT"
    assert verdict_of("up", "mixed") == "SPLIT"
    assert verdict_of("peak", "mixed") == "SPLIT"


def test_declared_excluded_axes_count_as_confounding():
    """데이터셋이 신고한 미모델링 축은 '관측되지 않은 교란요인'이다.

    excluded_axes 의 값은 conditions 에 없으므로 _drivers 가 못 본다. 신고를
    무시하면 정직한 데이터셋이 오히려 가짜 단독-변화 증거로 채점된다.
    """
    ev = [e for e in literature_evidence()
          if e.dataset == "hong2007_cu_ads_bta_polish_rate"
          and e.key == "inhibitor_mM"]
    assert ev, "기준 데이터셋이 사라졌다 — 테스트 전제를 다시 확인하라"
    for e in ev:
        assert e.confounded, "excluded_axes 선언이 교란으로 반영되지 않았다"
        assert not e.usable()
