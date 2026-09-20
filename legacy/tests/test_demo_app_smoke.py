"""sim/demo_app.py smoke test — 예외 없이 로드되고 세 탭(Preston MRR v0,
WIWNU x 패턴밀도 결합 맵, 캘리브레이션)이 렌더링되는지만 확인한다. UI 로직 자체의 회귀는
각 계산 모듈(tests/test_wiwnu_pattern_combined.py 등)이 이미 담당한다. 캘리브레이션
탭 자체의 회귀는 tests/test_demo_app_calibration_tab.py 가 담당한다."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "sim" / "demo_app.py")


def test_demo_app_loads_without_exception():
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert len(at.exception) == 0
    assert len(at.tabs) == 3
