"""미전달 축 감사의 '신규 vs 기록된 부채' 구분을 고정한다.

이 테스트가 존재하는 이유 (2026-09-20)
──────────────────────────────────────
최적화 루프가 매 회차 "🔴 라벨에만 있고 모델에 전달되지 않는 축 3건 — 물리를
고치기 전에 이것을 먼저 고쳐라"를 **최상위 판정**으로 올렸다. 그런데 3건 전부
데이터셋이 `excluded_axes:` 로 사유와 함께 이미 선언하고 판정으로 종결한
미모델링 축 부채였다. 신규 결함이 하나도 없는데 매 회차가 같은 진단을
되풀이했고, 그동안 **진짜 신규 결함이 있었다면 이 3건에 가려 보이지 않았다**.

물리 위생 검사는 같은 문제를 `validation/adjudicated_violations.yaml` 로 이미
해결해 두었다("신규 0 · 판정종결 2"). 이 검사도 같은 구분을 가져야 한다.

⚠ 이것은 **면제가 아니다.** 📖 로 표시된 데이터셋의 순위·절대값 지표는 여전히
구조적으로 달성 불가능하고, 성능 근거로 쓰면 안 된다. 바뀌는 것은 다음 회차가
'새로 생긴 것'과 '이미 기록된 것'을 구분할 수 있다는 점뿐이다.
"""
import pathlib
import sys
import tempfile
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.label_vs_input_audit import scan  # noqa: E402


def _scan_body(body: str):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "ds.yaml"
        p.write_text(body, encoding="utf-8")
        return scan(p)

# 라벨 3종이 모델 입력 2종으로 뭉치는 합성 데이터셋. 뭉치게 만드는 축
# (surfactant_ppm)은 LABEL_TO_KEY 에 없으므로 구조 검사에서만 걸린다.
# ⚠ dedent 를 **먼저** 한다 — 들여쓰기 0 의 선언 블록을 들여쓴 자리에 끼우면
#   공통 접두사가 무너져 YAML 이 깨진다.
_BODY = textwrap.dedent("""
    source: 합성 데이터 (테스트용)
    in_scope: true
    pack: w_fe_oxidizer
    {decl}
    conditions:
      - label: "계면활성제 없음"
        pressure_psi: 3.0
        mrr_nm_per_min: 100.0
        overrides: {{oxidizer_wt_pct: 1.0, sfr_ml_min: 200.0}}
      - label: "계면활성제 250 ppm"
        pressure_psi: 3.0
        mrr_nm_per_min: 140.0
        overrides: {{oxidizer_wt_pct: 1.0, sfr_ml_min: 200.0}}
      - label: "계면활성제 2000 ppm"
        pressure_psi: 3.0
        mrr_nm_per_min: 60.0
        overrides: {{oxidizer_wt_pct: 2.0, sfr_ml_min: 200.0}}
""")

_DECL = textwrap.dedent("""
    excluded_axes:
      surfactant_ppm: >
        계면활성제 흡착 억제 항이 이 팩에 없다. 세 조건 중 둘이 모델에는
        같은 입력으로 들어가 순위 지표를 구조적으로 누른다.
""").strip()


def test_undeclared_structural_defect_is_new():
    """선언 없는 구조 결함은 '신규'(🔴)로 나와야 한다."""
    probs = [p for p in _scan_body(_BODY.format(decl="")) if "고유 입력" in p]
    assert probs, "구조 검사가 뭉친 입력을 놓쳤다"
    assert probs[0].startswith("🔴"), probs[0]
    assert not probs[0].startswith("🔴📖"), \
        "선언이 없는데 기록된 부채로 표시됐다 — 진짜 결함이 조용해진다"


def test_declared_structural_defect_is_recorded_debt():
    """`excluded_axes:` 로 사유와 함께 선언하면 📖(기록된 부채)로 나온다."""
    probs = [p for p in _scan_body(_BODY.format(decl=_DECL)) if "고유 입력" in p]
    assert probs, "선언했다고 결함 자체가 사라지면 안 된다 — 면제가 아니라 기록이다"
    assert probs[0].startswith("🔴📖"), probs[0]


def test_declaration_does_not_silence_the_defect():
    """선언은 심각도를 낮추지 않는다 — 여전히 🔴 이고 문구가 그대로다."""
    probs = [p for p in _scan_body(_BODY.format(decl=_DECL)) if "고유 입력" in p]
    assert "구조적으로" in probs[0] and "달성 불가능" in probs[0], probs[0]


def test_optimize_loop_parses_recorded_count():
    """optimize_loop 이 '신규 N · 기록된 부채 M' 을 읽어 구분한다."""
    import re
    line = "결함 3건 (신규 0 · 기록된 부채 3) — 고치기 전에는 ..."
    assert int(re.search(r"결함\s+(\d+)건", line).group(1)) == 3
    assert int(re.search(r"기록된 부채\s+(\d+)", line).group(1)) == 3
