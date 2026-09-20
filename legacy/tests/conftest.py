"""pytest 공통 설정 — sim/ 하위 모듈을 각 파일이 직접 실행될 때와 동일한 방식으로 import 가능하게 한다.

sim/tier1_empirical/preston.py는 내부에서 `from kinematics import ...` (동일 폴더 기준
bare import)를 쓰고, process_time.py는 `from preston import mrr_profile`을 쓴다.
이는 `python sim/tier1_empirical/preston.py`로 직접 실행할 때 스크립트 폴더가
sys.path에 자동으로 들어가기 때문에 동작한다. pytest로 import할 때도 동일하게
동작하도록 각 모듈 폴더를 sys.path에 추가한다 (모듈 파일 자체는 수정하지 않음).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT / "sim" / "tier1_empirical", ROOT / "sim" / "tier2_physics",
          ROOT / "sim" / "integration"):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)
